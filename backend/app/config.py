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

    # JWT configuration

Settings = Settings()    
    