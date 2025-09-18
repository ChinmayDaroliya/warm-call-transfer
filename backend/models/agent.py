from enum import Enum
from pydantic import BaseModel,Field,EmailStr,ConfigDict
from typing import Optional, List
from datetime import datetime

# Enum representing possible statuses of an agent
class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

# Request model for creating a new agent with name, email, and skills
class AgentCreateRequest(BaseModel):
    name: str = Field()
    email: EmailStr = Field()
    skills: List[str] = Field() 

# Request model for updating the agent with name, email, or skills
class AgentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Agent's full name")
    skills: Optional[List[str]] = Field(None, description="List of agent skills")
    max_concurrent_calls: Optional[int] = Field(None, description="maximum concurrent calls agent can handle")

# Request model for updating the current status of an agent (available, busy, offline)
class StatusUpdate(BaseModel):
    status: AgentStatus = Field(..., description="New agent status")

# Response model providing detailed information of a single agent to the frontend
class AgentResponse(BaseModel):
    id: str
    name: str
    email: str
    status: AgentStatus
    current_room_id: str | None = None
    max_concurrent_calls: int
    skills: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # This allows model_validate to read from ORM objects
    }
    # class config:
    #     from_attributes: True

# Response model providing a list of agents with basic info to the frontend
class AgentListResponse(BaseModel):
    id: str
    name: str
    email: str
    status: AgentStatus
    current_room_id: Optional[str]
    skills: List[str]
    
    model_config = {
        "from_attributes": True
    }
    # class config:
    #     from_attributes: True

class AgentStatusUpdate(BaseModel):
    status: AgentStatus = Field(..., description="New agent status")
