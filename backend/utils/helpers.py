import uuid
from datetime import datetime
from typing import Any, Dict


# Generate a random UUID.
# Useful for unique identifiers like room IDs or user IDs.
# Returns a string version of UUID4.

def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())

# Get the current UNIX timestamp.
# Useful for logging, token generation, and time tracking.
# Returns integer seconds since epoch.

def timestamp() -> int:
    """Get current timestamp"""
    return int(datetime.now().timestamp())

# Convert seconds into human-readable duration.
# Handles seconds, minutes, and hours formatting.
# Example: 65 → "1m 5s", 3700 → "1h 1m".

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

# Safely retrieve nested dictionary values.
# Walks through keys step by step, avoids KeyError.
# Returns default value if key path doesn’t exist.

def safe_get(dictionary: Dict, *keys, default: Any = None) -> Any:
    """Safely get nested dictionary values"""
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current