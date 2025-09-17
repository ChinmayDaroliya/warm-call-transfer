import logging
from typing import Dict,List
from sqlalchemy.orm import Session
from app.database import (
    Call, Agent, Transfer, CallStatus, AgentStatus, TransferStatus,
    get_db, create_transfer
)
from services.livekit_service import livekit_service
from datetime import datetime
from services.llm_service import llm_service
import asyncio
from app.config import Settings

logger = logging.getLogger(__name__)

class TransferService:
    def __init__(self):
        self.active_transfers = {} #tracks ongoing transfer
        self.transfer_timeouts = {} #tracks transfer timeouts

    # This function manages the entire warm transfer:
    # 1. Get the call and agent details
    # 2. Check if transfer is possible
    # 3. Update the call and agent status in the database
    # 4. Save the transfer record
    # 5. Ask the AI to create a call summary and transfer message
    # 6. Create a special LiveKit room for both agents
    # 7. Generate tokens so agents can join the room
    # 8. Return all transfer details to the frontend
    # If anything fails, mark the transfer as failed

    async def initiate_warm_transfer(
        self,
        call_id: str,
        from_agent_id: str,
        to_agent_id: str,
        reason: str = None,
        db: Session = None
    ) -> Dict :
        """Initiate a warm transfer process"""

        logger.info(f"Initiating warm transfer for call {call_id} from {from_agent_id} to {to_agent_id}")

        try:
            # get call and agents from database
            call = db.query(Call).fliter(Call.id == call_id).first()
            from_agent = db.query(Agent).filter(Agent.id == from_agent_id).first()
            to_agent = db.query(Agent).filter(Agent.id == to_agent_id).first()

            if not call or not from_agent or not to_agent:
                raise ValueError("call or agent not found")
            
            # validate transfer condition
            validate_result = await self._validate_transfer_conditions(
                call, from_agent, to_agent, db
            )

            if not validate_result["valid"]:
                return {"success":False , "error": validate_result["error"]}
            
            # update call status to transferring
            call.status = CallStatus.TRANSFERRING.value
            db.commit()

            # create transfer record
            transfer = create_transfer(
                db=db,
                call_id=call_id,
                from_agent_id=from_agent_id,
                to_agent_id=to_agent_id,
                reason=reason
            )

            # generate call summary using LLM
            summary = await self._generate_transfer_summary(call,db)
            transfer.summary_shared = summary

            # create transfer room for agent-to-agnet conversation
            transfer_room_id = livekit_service.generate_room_id("transfer")
            transfer_room = await livekit_service.create_room(
                room_name = transfer_room_id,
                max_participants = 3,
                metadata = {"type":"transfer", "call_id":call_id, "transfer_id":transfer.id}
            )

            transfer.transfer_room_id = transfer_room_id
            db.commit()

            # generate  access token for both agents
            from_agent_token = livekit_service.generate_access_token(
                room_name = transfer_room_id,
                participant_identity = f"agent_{from_agent.id}",
                participant_name = from_agent.name
            )

            to_agent_token = livekit_service.generate_access_token(
                room_name = transfer_room_id,
                participant_identity = f"agent_{to_agent.id}",
                participant_name = to_agent.name
            )

            # update agent statuses
            to_agent.status = AgentStatus.BUSY.value
            from_agent.status = AgentStatus.BUSY.value
            db.commit()

            # store transfer in active transfers
            self.active_transfers[transfer.id] = {
                "call_id": call_id,
                "transfer_room_id": transfer_room_id,
                "from_agent_id": from_agent_id,
                "to_agent_id": to_agent_id,
                "status": TransferStatus.INITIATED.value,
                "created_at": datetime.now()
            }

            # set timeout for transfer completion
            await self._set_transfer_timeout(transfer.id)

            # generate transfer context for speaking
            transfer_context = await llm_service.generate_transfer_context(
                summary=summary,
                transfer_reason = reason or "Specialized assistance required",
                agent_skills = to_agent.skills
            )

            return {
                "success":True,
                 "transfer_id": transfer.id,
                "transfer_room_id": transfer_room_id,
                "from_agent_token": from_agent_token,
                "to_agent_token": to_agent_token,
                "summary": summary,
                "transfer_context": transfer_context,
                "call_room_id": call.room_id
            }
        
        except Exception as e:
            logger.error(f"Error initiating warm transfer {str(e)}")
            # rollback any changes

            if 'transfer' in locals():
                transfer.status = TransferStatus.FAILED.value
                db.commit()
            return {"success":False, "error":str(e)}    

    # Finalize the warm transfer:
    # move customer from Agent A to Agent B, update call/agent records,
    # close transfer room, cancel timers, and return new call details.

    async def complete_warm_transfer(
            self,
            transfer_id : str,
            db: Session = None
    )->Dict:
        """Complete the warm transfer by moving customer to agent b"""

        logger.info(f"Completing warm transfer {transfer_id}")

        try:
            # get transfer record
            transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
            if not transfer:
                return {"success":False, "error":"Transfer not found"}
            
            call = db.query(Call).filter(Call.id == transfer.call_id).first()
            from_agent = db.query(Agent).filter(Agent.id == transfer.from_agent_id).first()
            to_agent = db.query(Agent).filter(Agent.id == transfer.to_agent_id).first()

            # update call to assign agent b
            call.agent_b_id = transfer.to_agent_id
            call.status = CallStatus.ACTIVE.value

            # generate access token for agent b to join the original call 
            to_agent_call_token = livekit_service.generate_access_token(
                room_name = call.room_id,
                participant_identity = f"agent_{to_agent.id}",
                participant_name = to_agent.name
            )

            # remove agent a from original call room
            await livekit_service.remove_participant(
                room_name = call.room_id,
                participant_identity = f"agent_{from_agent.id}"
            )

            # update transfer status
            transfer.status = TransferStatus.COMPLETED.value
            transfer.completed_at = datetime.now()
            transfer.duration_seconds = int(
                (datetime.now() - transfer.initiated_at).total_seconds()
            )

            # update agent statuses
            from_agent.status = AgentStatus.AVAILABLE.value
            from_agent.current_room_id = None
            to_agent.current_room_id = call.room_id

            db.commit()

            # clean up transfer room
            await livekit_service.close_room(transfer.transfer_room_id)

            # remove from active transfers
            if transfer_id in self.active_transfers:
                del self.active_transfers[transfer_id]

            # cancel timeout
            if transfer_id in self.transfer_timeouts:
                self.transfer_timeouts[transfer_id].cancel()
                del self.transfer_timeouts[transfer_id]

            logger.info(f"Warm transfer {transfer_id} completed successfully")

            return {
                "success": True,
                "call_room_id": call.room_id,
                "to_agent_call_token": to_agent_call_token,
                "transfer_completed_at": transfer.completed_at
            }   
        
        except Exception as e: 
            logger.error(f"Error completing warm transfer : {str(e)}")
            return {"success":False, "error":str(e)}
        
    # Cancel an ongoing transfer:
    # mark transfer as failed, reset agent statuses,
    # clean up transfer room and tracking, and return result.

    async def cancel_transfer(
            self,
            transfer_id: str,
            reason: str = None,
            db:Session = None
    )->Dict:
        """Cancel an ongoing transfer"""

        logger.info(f"Cancelling transfer {transfer_id}")

        try:
            transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
            if not transfer:
                return {"success":False, "error":"Transfer not found"}
            
            # update transfer status
            transfer.status = TransferStatus.FAILED.value
            transfer.completed_at = datetime.now()

            # get related records
            call = db.query(Call).filter(Call.id == transfer.call_id).first()
            from_agent = db.query(Agent).filter(Agent.id == transfer.from_agent_id).first()
            to_agent = db.query(Agent).filter(Agent.id == transfer.to_agent_id).first()

            # reset call ststus
            from_agent.status = AgentStatus.BUSY.value
            to_agent.status = AgentStatus.AVAILABLE.value

            db.commit()

            # clean up transfer room
            if transfer.Transfer_room_id:
                await livekit_service.close_room(transfer.transfer_room_id)

            # clean up tracking
            if transfer_id in self.active_transfers:
                del self.active_transfers[transfer_id]
            
            if transfer_id in self.transfer_timeouts:
                self.transfer_timeouts[transfer_id].cancel()
                del self.transfer_timeouts[transfer_id]
                
            return {"success":True, "message":"Transfer cancelled"}

        except Exception as e:
            logger.error(f"Error cancelling transfer: {str(e)}")
            return {"success":False, "error":str(e)}
    
    # Get the current status and details of a transfer from the database.

    async def get_transfer_status(self, transfer_id: str, db: Session = None) -> Dict:
        """Get current transfer status"""
        
        transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
        if not transfer:
            return {"error": "Transfer not found"}
        
        return {
            "transfer_id": transfer.id,
            "status": transfer.status,
            "call_id": transfer.call_id,
            "from_agent_id": transfer.from_agent_id,
            "to_agent_id": transfer.to_agent_id,
            "initiated_at": transfer.initiated_at,
            "completed_at": transfer.completed_at,
            "duration_seconds": transfer.duration_seconds,
            "transfer_room_id": transfer.transfer_room_id,
            "summary": transfer.summary_shared,
            "reason": transfer.reason
        }
    
    # Validate if a warm transfer is allowed by checking call state,
    # agent availability, and concurrent call limits.

    async def _validate_transfer_conditions(
        self, 
        call: Call, 
        from_agent: Agent, 
        to_agent: Agent,
        db: Session
    ) -> Dict:
        """Validate that transfer can proceed"""
        
        # Check if call is in valid state
        if call.status not in [CallStatus.ACTIVE.value]:
            return {"valid": False, "error": "Call is not in active state"}
        
        # Check if from_agent is actually on the call
        if call.agent_a_id != from_agent.id:
            return {"valid": False, "error": "Agent is not assigned to this call"}
        
        # Check if to_agent is available
        if to_agent.status != AgentStatus.AVAILABLE.value:
            return {"valid": False, "error": "Target agent is not available"}
        
        # Check if agents are different
        if from_agent.id == to_agent.id:
            return {"valid": False, "error": "Cannot transfer to the same agent"}
        
        # Check agent's concurrent call limit
        active_calls = db.query(Call).filter(
            Call.agent_a_id == to_agent.id,
            Call.status.in_([CallStatus.ACTIVE.value, CallStatus.TRANSFERRING.value])
        ).count()
        
        if active_calls >= to_agent.max_concurrent_calls:
            return {"valid": False, "error": "Target agent has reached maximum concurrent calls"}
        
        return {"valid": True}
    
    # Get or create a call summary for transfer:
    # return existing summary, generate a new one if transcript is available,
    # otherwise provide a simple fallback summary.

    async def _generate_transfer_summary(self, call: Call, db: Session) -> str:
        """Generate or retrieve call summary for transfer"""
        
        if call.summary:
            return call.summary
        
        # Generate new summary if transcript exists
        if call.transcript:
            caller_info = {
                "name": call.caller_name,
                "phone": call.caller_phone
            }
            
            summary = await llm_service.generate_call_summary(
                transcript=call.transcript,
                caller_info=caller_info,
                call_duration=call.duration_seconds,
                call_reason=call.call_reason
            )
            
            # Save summary to database
            call.summary = summary
            call.summary_generated_at = datetime.now()
            db.commit()
            
            return summary
        
        # Fallback summary
        return f"Call transfer for {call.caller_name or 'Customer'}. Duration: {call.duration_seconds // 60} minutes. Reason: {call.call_reason or 'General inquiry'}."

    # Set a timeout for warm transfer; auto-cancel if not completed in time.

    async def _set_transfer_timeout(self, transfer_id:str):
        """Set timeout for transfer completion"""

        async def timeout_handler():
            await asyncio.sleep(Settings.MAX_TRANSFER_WAIT_TIME)

            if transfer_id in self.active_transfers:
                logger.warning(f"Transfer {transfer_id} timed out")

                # get database session    
                db = next(get_db())
                try:
                    await self.cancel_transfer(
                        transfer_id=transfer_id,
                        reason="Transfer timed out",
                        db=db
                    )
                finally:
                    db.close()    

        # create and store timeout tasks
        timeout_task = asyncio.create_task(timeout_handler())
        self.transfer_timeouts[transfer_id] = timeout_task

    # Get a list of all currently active transfers.

    def get_active_transfers(self)->List[Dict]:
        """Get list of all active transfers"""
        return list(self.active_transfers.values())

    # Get all available agents with their details and remaining call capacity.

    async def get_agent_availability(self, db: Session) -> List[Dict]:
        """Get list of available agents for transfers"""
        
        available_agents = db.query(Agent).filter(
            Agent.status == AgentStatus.AVAILABLE.value
        ).all()
        
        agent_list = []
        for agent in available_agents:
            # Count current active calls
            active_calls = db.query(Call).filter(
                Call.agent_a_id == agent.id,
                Call.status.in_([CallStatus.ACTIVE.value, CallStatus.TRANSFERRING.value])
            ).count()
            
            agent_list.append({
                "id": agent.id,
                "name": agent.name,
                "email": agent.email,
                "skills": agent.skills,
                "active_calls": active_calls,
                "max_calls": agent.max_concurrent_calls,
                "available_capacity": agent.max_concurrent_calls - active_calls
            })
        
        return agent_list

# Create singleton instance
transfer_service = TransferService()    