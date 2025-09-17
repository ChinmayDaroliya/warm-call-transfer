import jwt
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings


# Generate a signed JWT token.
# Adds subject, issue time, and expiry into payload.
# Supports extra claims and custom expiration.


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """Create a JWT access token"""
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode = {
        "exp": expire,
        "sub": subject,
        "iat": datetime.utcnow()
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

# Validate and decode a JWT token.
# Returns payload if valid, otherwise None.
# Handles expired or tampered tokens gracefully.

def verify_access_token(token: str) -> Optional[dict]:
    """Verify a JWT access token"""
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        return None