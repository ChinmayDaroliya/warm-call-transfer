# import sqlalchemy tools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import Settings


# create database engine
engine = create_engine(
    Settings.DATABASE_URL,
    echo = Settings.DATABASE_ECHO,
    connect_args={"check_the same_thread":False} if "sqlite" in Settings.DATABASE_URL else {}    
)

# create a session factory
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# base class for models
Base = declarative_base()

# database init function
async def init_db():
    """Initialize all the database tables"""
    Base.metadata.create_all(bind=engine) 

# dependency function to get a session 
def get_db():
    """Yields a database session"""
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()    