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
    JWT_SECRET_KEY:str = ""
    JWT_ALGORITHM:str = ""
    JWT_EXPIRATION_HOURS:int = 24

    # Transfer Configuration
    MAX_TRANSFER_WAIT_TIME:int = 300 #5 minutes in seconds
    MAX_ACTIVE_CALLS_PER_AGENT:int = 3

    # LLM Configuration
    MAX_SUMMARY_TOKENS:int = 500
    SUMMARY_TEMPERATURE:float = 0.3

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
Settings = Settings()    

# validate required settings
# Ensure all critical environment variables and API keys are set before the app starts.
def validate_settings():
    required_settings = [
        ("LIVEKIT_API_KEY", Settings.LIVEKIT_API_KEY),
        ("LIVEKIT_API_SECRET", Settings.LIVEKIT_API_SECRET),
        ("LIVEKIT_WS_URL", Settings.LIVEKIT_WS_URL),
    ]
    
    # Check LLM provider keys
    llm_keys = {
        "openai": Settings.OPENAI_API_KEY
    }

    if not llm_keys.get(Settings.DEFAULT_LLM_PROVIDER):
        raise ValueError(f"API key for {Settings.DEFAULT_LLM_PROVIDER} is required")
    
    missing_settings = [name for name, value in required_settings if not value]

    if missing_settings:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")
    
# validate on import 
try:
    validate_settings()
except ValueError as e:
    print(f"Configuration warning: {e}")
    if not Settings.DEBUG:
        raise