# import sqlalchemy tools
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

from enum import Enum
import uuid

from app.config import settings

# create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo = settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
  
)

# create a session factory
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# base class for models
Base = declarative_base()

# enums
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

class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class TransferStatus(str, Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Datebase models

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()) )
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    status = Column(String(20), default=AgentStatus.AVAILABLE.value)
    current_room_id = Column(String(255), nullable=True)
    max_concurrent_calls = Column(Integer, default=3)
    skills = Column(JSON, default=list) #list of skills departments
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    calls_as_agent_a = relationship("Call", foreign_keys="Call.agent_a_id", back_populates="agent_a")
    calls_as_agent_b = relationship("Call", foreign_keys="Call.agent_b_id", back_populates="agent_b")
    transfers_initiated = relationship("Transfer", foreign_keys="Transfer.from_agent_id", back_populates="from_agent")
    transfers_received = relationship("Transfer", foreign_keys="Transfer.to_agent_id", back_populates="to_agent")

class Call(Base):
    __tablename__ = "calls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = Column(String(255), nullable=False, unique=True)
    caller_name = Column(String(100), nullable=True)
    caller_phone = Column(String(20), nullable=True)
    status = Column(String(20), default=CallStatus.WAITING.value)

    # Agent Assignments
    agent_a_id = Column(String, ForeignKey("agents.id"), nullable=True)
    agent_b_id = Column(String, ForeignKey("agents.id"), nullable=True)

    # call details
    # started_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)

    # call transcript and summary
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    summary_generated_at = Column(DateTime, nullable=True)

    # additional metadata
    call_reason = Column(String(255), nullable=True)
    priority = Column(String(20), default=PriorityLevel.NORMAL.value)
    extra_metadata = Column(JSON, default=dict)   

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # relationships
    agent_a = relationship("Agent", foreign_keys=[agent_a_id], back_populates="calls_as_agent_a")
    agent_b = relationship("Agent", foreign_keys=[agent_b_id], back_populates="calls_as_agent_b")
    transfers = relationship("Transfer", back_populates="call")

class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(String, primary_key=True, default=lambda:str(uuid.uuid4()))
    call_id = Column(String, ForeignKey("calls.id"), nullable=False)

    # transfer agents
    from_agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    to_agent_id = Column(String, ForeignKey("agents.id"), nullable=False)

    # Transfer details
    status = Column(String(20), default=TransferStatus.INITIATED.value)
    reason = Column(String(500), nullable=True)
    summary_shared = Column(Text, nullable=True)

    # timings
    initiated_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)

    # Room information
    transfer_room_id = Column(String(255), nullable=True) #Room where agents meet

    # Metadata
    extra_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # relationships
    call = relationship("Call", back_populates="transfers")
    from_agent = relationship("Agent", foreign_keys=[from_agent_id], back_populates="transfers_initiated")
    to_agent = relationship("Agent", foreign_keys=[to_agent_id], back_populates="transfers_received")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(String, primary_key=True, default=lambda:str(uuid.uuid4()))
    livekit_room_id = Column(String(255),nullable=False, unique=True )
    name = Column(String(255), nullable=False)

    # room type and status
    room_type = Column(String(50), default="call")
    is_active = Column(Boolean, default=True)

    # participant tracking
    max_participants = Column(Integer, default=10)
    current_participants = Column(JSON, default=list)

    # associated call/ transfer
    call_id = Column(String, ForeignKey("calls.id"), nullable=True)

    # timing
    created_at = Column(DateTime, default=func.now())
    closed_at = Column(DateTime, nullable=True)

    # metadata
    extra_metadata = Column(JSON, default=dict)

# database init function
async def init_db():
    """Initialize all the database tables"""
    Base.metadata.create_all(bind=engine) 

# dependency function to get a session 
def get_db():
    """Yields a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    


# helper function for database operations

def create_agent(db, name: str, email: str, skills: list = None ):
    """Create a new agent"""

    agent = Agent(
        name = name,
        email = email,
        skills = skills or []
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

def create_call(
    db,
    room_id: str,
    caller_name: str = None,
    caller_phone: str = None,
    agent_a_id: str = None,
    call_reason: str = None,
    priority: str = "normal"
):
    """Create a new call"""
    call = Call(
        room_id=room_id,
        caller_name=caller_name,
        caller_phone=caller_phone,
        agent_a_id=agent_a_id,
        call_reason=call_reason,
        priority=priority
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call

def create_transfer(db, call_id: str, from_agent_id: str, to_agent_id: str, reason: str = None):
    """Create a new transfer"""
    transfer = Transfer(
        call_id = call_id,
        from_agent_id = from_agent_id,
        to_agent_id = to_agent_id,
        reason = reason
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer