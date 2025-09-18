from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models.call import (
    CallCreateRequest, CallResponse,JoinCallResponse,JoinCallRequest, CallUpdateRequest, callListResponse
)
from app.database import (  
    get_db, Agent, AgentStatus, create_call, Call, CallStatus
)
from services.livekit_service import livekit_service

router = APIRouter()
logger = logging.getLogger(__name__)

# # Create a new call with LiveKit room, assign agent if requested, and return call info.

@router.post("/create", response_model=CallResponse)
async def create_new_call(
    request: CallCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a nwe call and livekit room"""

    try:
        # generate unique room id 
        room_id = livekit_service.generate_room_id("call")

        # create livekit room
        room_info = await livekit_service.create_room(
            room_name = room_id,
            max_participants = 5,
            metadata = {
                "type": "customer_call",
                "caller_name": request.caller_name,
                "priority": request.priority
            }
        )

        # find available agent if requested
        agent_id = None
        if request.assign_agent:
            available_agent = db.query(Agent).filter(Agent.status == AgentStatus.AVAILABLE.value).first()

            if available_agent:
                agent_id = available_agent.id
                available_agent.status = AgentStatus.BUSY.value
                available_agent.current_room_id = room_id

        # create call record in database
        call = create_call(
            db=db,
            room_id = room_id,
            caller_name=request.caller_name,
            caller_phone=request.caller_phone,
            agent_a_id=agent_id,
            call_reason=request.call_reason,
            priority=request.priority
        )

        # generate accesss token for caller
        caller_token = livekit_service.generate_access_token(
            room_name=room_id,
            participant_identity=f"caller_{call.id}",
            participant_name=request.caller_name or "Customer"
        )

        db.commit()

        return CallResponse(
             id=call.id,
                room_id=room_id,
                caller_name=request.caller_name,
                caller_phone=request.caller_phone,
                status=call.status,
                agent_a_id=agent_id,
                agent_b_id=getattr(call, "agent_b_id", None),  # ✅ add this
                access_token=caller_token,
                created_at=call.created_at,
                updated_at=getattr(call, "updated_at", None),
                started_at=getattr(call, "started_at", None),
                ended_at=getattr(call, "ended_at", None),
                duration_seconds=getattr(call, "duration_seconds", None),
                transcript=getattr(call, "transcript", None),
                summary=getattr(call, "summary", None),
                summary_generated_at=getattr(call, "summary_generated_at", None),
                extra_metadata=getattr(call, "extra_metadata", None),
        )

    except Exception as e:
        logger.error(f"Error creating call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Allow agents or participants to join an existing call and get LiveKit access token.

@router.post("/join", response_model=JoinCallResponse)
async def join_existing_call(
        request:JoinCallRequest,
        db: Session = Depends(get_db)
):
    """Join an existing call as an agent or participant"""

    try:
        call = db.query(Call).filter(Call.room_id == request.room_id).first()
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Generate access token
        token = livekit_service.generate_access_token(
            room_name=request.room_id,
            participant_identity=request.participant_identity,
            participant_name=request.participant_name
        )
        
        # If joining as agent, update agent status
        if request.participant_identity.startswith("agent_"):
            agent_id = request.participant_identity.split("_")[1]
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                agent.current_room_id = request.room_id
                agent.status = AgentStatus.BUSY.value
                db.commit()
        
        return JoinCallResponse(
            access_token=token,
            room_id=request.room_id,
            call_status=call.status
        )
    
    except Exception as e:
        logger.error(f"Error joining call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve full details of a specific call by its ID.
 
@router.get("/{call_id}", response_model=CallResponse)
async def get_call_details(
    call_id: str,
    db: Session = Depends(get_db)
):
    """Get details for a specific call"""
    
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return CallResponse.from_orm(call)

# List all calls, optionally filtered by status, with a limit on results.

@router.get("/", response_model=List[callListResponse])
async def list_calls(
    status: Optional[CallStatus] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all calls with optional filtering"""
    
    query = db.query(Call)
    if status:
        query = query.filter(Call.status == status.value)
    
    calls = query.order_by(Call.created_at.desc()).limit(limit).all()
    return [callListResponse.from_orm(call) for call in calls]

# Update the status of a call, record transcript, and free agents if completed.

@router.put("/{call_id}/status")
async def update_call_status(
    call_id: str,
    status_update: CallUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update call status and related information"""
    
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    if status_update.status:
        call.status = status_update.status.value
        
        # If call is completed, update end time and duration
        if status_update.status == CallStatus.COMPLETED:
            call.ended_at = datetime.now()
            if call.started_at:
                call.duration_seconds = int((call.ended_at - call.started_at).total_seconds())
            
            # Free up agents
            if call.agent_a:
                call.agent_a.status = AgentStatus.AVAILABLE.value
                call.agent_a.current_room_id = None
            if call.agent_b:
                call.agent_b.status = AgentStatus.AVAILABLE.value
                call.agent_b.current_room_id = None
    
    if status_update.transcript:
        call.transcript = status_update.transcript
    
    db.commit()
    
    return {"message": "Call updated successfully"}

# End a call, close LiveKit room, update status, and free assigned agents.

@router.delete("/{call_id}")
async def end_call(
    call_id: str,
    db: Session = Depends(get_db)
):
    """End a call and clean up resources"""
    
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    try:
        # Close LiveKit room
        await livekit_service.close_room(call.room_id)
        
        # Update call status
        call.status = CallStatus.COMPLETED.value
        call.ended_at = datetime.now()
        
        # Free up agents
        if call.agent_a:
            call.agent_a.status = AgentStatus.AVAILABLE.value
            call.agent_a.current_room_id = None
        if call.agent_b:
            call.agent_b.status = AgentStatus.AVAILABLE.value
            call.agent_b.current_room_id = None
        
        db.commit()
        
        return {"message": "Call ended successfully"}
        
    except Exception as e:
        logger.error(f"Error ending call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))    