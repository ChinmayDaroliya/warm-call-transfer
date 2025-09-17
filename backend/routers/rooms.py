# app/routers/rooms.py
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
from services.livekit_service import livekit_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Route: GET /{room_id}/info
# Purpose: Fetch information about a specific LiveKit room.
# Example: Returns room metadata such as ID, name, creation time, etc

@router.get("/{room_id}/info")
async def get_room_info(room_id: str):
    """Get information about a LiveKit room"""
    
    try:
        room_info = await livekit_service.get_room(room_id)
        if not room_info:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return room_info
        
    except Exception as e:
        logger.error(f"Error getting room info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Route: GET /{room_id}/participants
# Purpose: Retrieve the list of participants currently in a room.
# Example: Returns an array of participant details (IDs, names, status)

@router.get("/{room_id}/participants")
async def get_room_participants(room_id: str):
    """Get list of participants in a LiveKit room"""
    
    try:
        participants = await livekit_service.list_participants(room_id)
        return {"participants": participants}
        
    except Exception as e:
        logger.error(f"Error getting room participants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Route: GET /{room_id}/stats
# Purpose: Get statistics about the room (e.g., active streams, bandwidth).
# Example: Returns analytics/metrics for monitoring usage of the room.

@router.get("/{room_id}/stats")
async def get_room_stats(room_id: str):
    """Get detailed statistics for a LiveKit room"""
    
    try:
        stats = await livekit_service.get_room_stats(room_id)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting room stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Route: DELETE /{room_id}
# Purpose: Close (delete) an active LiveKit room and remove participants.
# Example: Used when ending a meeting or force-closing a session.

@router.delete("/{room_id}")
async def close_room(room_id: str):
    """Close/delete a LiveKit room"""
    
    try:
        success = await livekit_service.close_room(room_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to close room")
        
        return {"message": "Room closed successfully"}
        
    except Exception as e:
        logger.error(f"Error closing room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Route: POST /{room_id}/mute
# Purpose: Mute a specific participant's track (audio/video) inside the room.
# Example: Admin can mute a participant's microphone remotely.

@router.post("/{room_id}/mute")
async def mute_participant(
    room_id: str,
    participant_identity: str,
    track_type: str = "audio"
):
    """Mute a participant in a room"""
    
    try:
        success = await livekit_service.mute_participant(room_id, participant_identity, track_type)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to mute participant")
        
        return {"message": "Participant muted successfully"}
        
    except Exception as e:
        logger.error(f"Error muting participant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Route: POST /{room_id}/remove
# Purpose: Remove (kick) a participant out of a room.
# Example: Used by admin to forcefully remove a disruptive user.

@router.post("/{room_id}/remove")
async def remove_participant(
    room_id: str,
    participant_identity: str
):
    """Remove a participant from a room"""
    
    try:
        success = await livekit_service.remove_participant(room_id, participant_identity)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove participant")
        
        return {"message": "Participant removed successfully"}
        
    except Exception as e:
        logger.error(f"Error removing participant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Route: POST /{room_id}/send-data
# Purpose: Send a custom data message to all participants or a specific participant.
# Example: Used for in-room chat messages, signals, or notifications.

@router.post("/{room_id}/send-data")
async def send_data_to_room(
    room_id: str,
    data: str,
    participant_identity: Optional[str] = None
):
    """Send data message to room participants"""
    
    try:
        success = await livekit_service.send_data_to_participant(room_id, data, participant_identity)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send data")
        
        return {"message": "Data sent successfully"}
        
    except Exception as e:
        logger.error(f"Error sending data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))