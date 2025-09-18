from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from services.transfer_service import transfer_service
from models.transfer import (
    TransferRequest, TransferResponse, TransferStatusResponse,
    AgentAvailabilityResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Start a warm transfer: assign agents, create transfer room, generate summary & tokens.

@router.post("/initiate", response_model=TransferResponse)
async def initiate_transfer(
    request: TransferRequest,
    db: Session = Depends(get_db)
):
    """Initiate a warm transfer between agents"""
    
    try:
        result = await transfer_service.initiate_warm_transfer(
            call_id=request.call_id,
            from_agent_id=request.from_agent_id,
            to_agent_id=request.to_agent_id,
            reason=request.reason,
            db=db
        )
        
        # Handle service error responses
        if not result.get("success", True):  # Default to True if key doesn't exist
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        
        return result  # Return the service response directly
    
    except HTTPException:
    # Already handled above, re-raise
        raise    
    except Exception as e:
        logger.error(f"Error initiating transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Complete a transfer: move the customer to the target agent, update statuses, clean up transfer room.

@router.post("/{transfer_id}/complete")
async def complete_transfer(
    transfer_id: str,
    db: Session = Depends(get_db)
):
    """Complete a warm transfer"""
    
    try:
        result = await transfer_service.complete_warm_transfer(transfer_id, db)
        
        # Handle service error responses
        if not result.get("success", True):
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        
        return {"message": "Transfer completed successfully", **result}
    except HTTPException:
    # Already handled above, re-raise
        raise        
    except Exception as e:
        logger.error(f"Error completing transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Cancel a transfer: mark as failed, free agents, close transfer room, remove from active transfers.

@router.post("/{transfer_id}/cancel")
async def cancel_transfer(
    transfer_id: str,
    reason: str = None,
    db: Session = Depends(get_db)
):
    """Cancel an ongoing transfer"""
    
    try:
        result = await transfer_service.cancel_transfer(transfer_id, reason, db)
        
        # Handle service error responses
        if not result.get("success", True):
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        
        return {"message": "Transfer cancelled successfully"}
    
    except HTTPException:
    # Already handled above, re-raise
        raise        
    except Exception as e:
        logger.error(f"Error cancelling transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Retrieve the current status of a specific transfer by its ID.
    
@router.get("/{transfer_id}/status", response_model=TransferStatusResponse)
async def get_transfer_status(
    transfer_id: str,
    db: Session = Depends(get_db)
):
    """Get the status of a transfer"""
    
    try:
        status = await transfer_service.get_transfer_status(transfer_id, db)
        
        # Handle service error responses
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
    
    except HTTPException:
    # Already handled above, re-raise
        raise        
    except Exception as e:
        logger.error(f"Error getting transfer status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# List all agents who are available for new transfers along with their current load.

@router.get("/agents/available", response_model=List[AgentAvailabilityResponse])
async def get_available_agents(
    db: Session = Depends(get_db)
):
    """Get list of available agents for transfer"""
    
    try:
        agents = await transfer_service.get_agent_availability(db)
        return agents
   
    except HTTPException:
    # Already handled above, re-raise
        raise        
    except Exception as e:
        logger.error(f"Error getting available agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# List all transfers that are currently in progress.

@router.get("/active")
async def get_active_transfers():
    """Get list of all active transfers"""
    
    try:
        transfers = transfer_service.get_active_transfers()
        return {"active_transfers": transfers}
   
    except HTTPException:
    # Already handled above, re-raise
        raise        
    except Exception as e:
        logger.error(f"Error getting active transfers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))