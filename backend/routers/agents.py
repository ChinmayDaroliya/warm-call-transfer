from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db, Agent, AgentStatus,create_agent as db_create_agent
from models.agent import (
    AgentCreateRequest, AgentResponse, AgentUpdateRequest,
    AgentListResponse, AgentStatusUpdate
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Add a new agent to the system after checking email uniqueness.

@router.post("/", response_model=AgentResponse)
async def create_agent(
    request: AgentCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new agent"""
    
    try:
        # Check if email already exists
        existing_agent = db.query(Agent).filter(Agent.email == request.email).first()
        if existing_agent:
            raise HTTPException(status_code=400, detail="Agent with this email already exists")
        
        agent = db_create_agent(
            db=db,
            name=request.name,
            email=request.email,
            skills=request.skills
        )
        
        return AgentResponse.model_validate(agent)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve a list of all agents, optionally filtering by status (available/busy).

@router.get("/", response_model=List[AgentListResponse])
async def list_agents(
    status: Optional[AgentStatus] = None,
    db: Session = Depends(get_db)
):
    """List all agents with optional filtering"""
    
    query = db.query(Agent)
    if status:
        query = query.filter(Agent.status == status.value)
    
    agents = query.order_by(Agent.name).all()
    return [AgentListResponse.from_orm(agent) for agent in agents]

# Fetch full details of a specific agent by their ID.

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Get details for a specific agent"""
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse.from_orm(agent)

# Update agent’s name, skills, or max concurrent calls.

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update agent details"""
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if request.name:
        agent.name = request.name
    if request.skills is not None:
        agent.skills = request.skills
    if request.max_concurrent_calls:
        agent.max_concurrent_calls = request.max_concurrent_calls
    
    db.commit()
    db.refresh(agent)
    
    return AgentResponse.from_orm(agent)

# Change agent’s current status (available, busy) and clear room if available.

@router.patch("/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status_update: AgentStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update agent status"""
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.status = status_update.status.value
    
    # If setting to available, clear current room
    if status_update.status == AgentStatus.AVAILABLE:
        agent.current_room_id = None
    
    db.commit()
    
    return {"message": "Agent status updated successfully"}

# Delete an agent if they are not currently on a call.

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Delete an agent"""
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if agent is currently on a call
    if agent.status == AgentStatus.BUSY:
        raise HTTPException(status_code=400, detail="Cannot delete agent who is currently on a call")
    
    db.delete(agent)
    db.commit()
    
    return {"message": "Agent deleted successfully"}