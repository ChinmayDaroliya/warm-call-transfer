from pydantic import BaseModel,Field
from typing import Optional,List
from datetime import datetime

# Data model for initiating a call transfer between agents
class TransferRequest(BaseModel):
    call_id: str = Field(..., description="ID of the call to transfer")
    from_agent_id: str = Field(..., description="Id of the agnet initiating the transfer")
    to_agent_id: str = Field(..., description="Id of the agent recieving the transfer")
    reason: Optional[str] = Field(None, description="Reason for the transfer")

# Response model returned to frontend with details of a call transfer, useful for transfer history
class TransferResponse(BaseModel):
    transfer_id: str
    status: str
    call_id: str
    from_agent_id: str
    to_agent_id: str
    initiated_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: int
    transfer_room_id: Optional[str]
    summary: Optional[str]
    reason: Optional[str]

# Response model providing agent details and current availability for frontend display
class AgentAvailabilityResponse(BaseModel):
    id: str
    name: str
    email: str
    skills: List[str]
    active_calls: int
    max_calls: int
    availability_capacity: int 

class TransferStatusResponse(BaseModel):
    transfer_id: str
    status: str
    call_id: str
    from_agent_id: str
    to_agent_id: str
    initiated_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: int
    transfer_room_id: Optional[str]
    summary: Optional[str]
    reason: Optional[str]