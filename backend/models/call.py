from enum import Enum
from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime

# these are enum classes which are fixed value show the status and priority of a call
class CallStatus(str,Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    FAILED = "failed"

class PriorityLevel(str,Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Schema defining the data expected from frontend when creating a new call
class CallCreateRequest(BaseModel):
    caller_name: Optional[str] = Field(None, description="Name of the caller")
    caller_phone: Optional[str] = Field(None, description="Phone number of the caller")
    call_reason: Optional[str] = Field(None, description="Reason for the call")
    priority: PriorityLevel = Field(PriorityLevel.NORMAL, description="Call priority level")
    assign_agent: bool = Field(True, description="Whether to automatically assign an agent")

# Schema for updating an existing call's status or transcript
class CallUpdateRequest(BaseModel):
    status: Optional[CallStatus] = Field(None, description="New call status")
    transcript: Optional[str] = Field(None, description="call transcript text")

# Schema for joining a LiveKit call room, used by both callers and agents
class JoinCallRequest(BaseModel):
    room_id: str = Field(..., description="LiveKit room Id to join")
    participant_identity: str = Field(..., description="Unique identity for the participant")
    participant_name: str = Field(..., description="Display name for the participant")

# Response schema returned by backend with call details for frontend or agent
class CallResponse(BaseModel):
    id: str
    room_id: str
    caller_name: Optional[str]
    caller_phone: Optional[str]
    status: CallStatus
    agent_a_id: Optional[str]
    agent_b_id: Optional[str]
    access_token: Optional[str] = None
    created_at:datetime

    class config:
        from_attributes = True

# Response sent to frontend when a participant successfully joins a call
class JoinCallResponse(BaseModel):
    access_token: str
    room_id: str
    call_status: CallStatus

# Represents a single call item in a list of calls sent to the frontend
class callListResponse(BaseModel):
    id: str
    room_id: str
    caller_name: Optional[str]
    status: CallStatus
    started_at: Optional[datetime]
    duration_seconds: int
    priority: str

    class config:
        from_attributes = True
