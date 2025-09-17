from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    #server configuration
    HOST: str = "127.0.0.1",
    PORT: int = 8000,
    DEBUG: bool = True

    #CORS Configurations
    ALLOWED_ORIGINS:List[str] = []

    # Database configuration
    DATABASE_URL: str = ""
    DATABASE_ECHO:bool 

    # LiveKit configuration
    LIVEKIT_API_KIT:str = ""
    LIVEKIT_API_SECRET:str = ""
    LIVEKIT_WS_URL: str = ""

    # LLM configuration
    OPENAI_API_KEY:str = ""
    # GROQ_API_KEY:str = ""
    # OPENROUTER_API_KEY = ""
    DEFAULT_LLM_PROVIDER:str = "openai"

    # JWT configuration

    # Transfer Configuration
    MAX_TRANSFER_WAIT_TIME:int = 300 #5 minutes in seconds
    MAX_ACTIVE_CALLS_PER_AGENT:int = 3

    # LLM Configuration
    MAX_SUMMARY_TOKENS:int = 500
    SUMMARY_TEMPERATURE:float = 0.3

# Create settings instance
Settings = Settings()    
    