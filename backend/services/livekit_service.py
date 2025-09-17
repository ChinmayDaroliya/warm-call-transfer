import logging
from app.config import Settings
from livekit import api, VideoGrants, AccessToken
from datetime import timedelta, datetime
from typing import Dict, Optional, List
import uuid

# creates a logger specific to your module so that when your project grows and has many files,
# you can tell where each log message came from.
logger = logging.getLogger(__name__)

class LiveKitService:
    def __init__(self):
        self.api_key = Settings.LIVEKIT_API_KIT
        self.api_secret = Settings.LIVEKIT_API_SECRET
        self.ws_url = Settings.LIVEKIT_WS_URL

        # LiveKit client used to create and manage rooms
        self.room_service = api.RoomService(
            url = self.ws_url,
            api_key = self.api_key,
            api_secret = self.api_secret
        )

#  Create and return a secure JWT access token for a LiveKit room.
# - Takes room name, participant identity, and optional details.
# - Adds default grants (join, publish, subscribe, send data).
# - Token is valid for 24 hours.
# - Returns the token as a string (JWT).

def generate_access_token(
       self,
       room_name: str,
       participant_identity: str,
       participant_name: str = None,
       metadata: dict = None,
       grants: VideoGrants = None
) -> str:
    """Generate access token for LiveKit room"""
    
    try:
        if not grants:
            grants = VideoGrants(
                room_join = True,
                room = room_name,
                can_publish = True,
                can_subscribe = True,
                can_publish_data = True
            )

        token = AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_identity)
        token.with_name(participant_name or participant_identity)
        token.with_grants(grants)

        if(metadata):
            token.with_metadata(str(metadata))

        # set token expiration 24 hour
        token.with_ttl(timedelta(hours=24))

        return token.to_jwt()
    
    except Exception as e:
        logger.error(f"Error generating acces token: {str(e)}")
        raise

# Create a new LiveKit room with given settings.
# Uses async since it makes a network call to LiveKit server.
# Returns room details as a dictionary.

async def create_room(
    self,
    room_name: str,
    max_participants: int = 10,
    metadata: Dict = None        
) -> Dict:
    """Create a new LiveKit room"""
    try:
        room_options = api.CreateRoomRequest(
            name = room_name,
            max_participants = max_participants,
            metadata = str(metadata) if metadata else None,
            empty_timeout = 30*60, #30 min empty timeour
            departure_timeout = 60 #60 sec departure timeout
        )

        room = await self.room_service.create_room(room_options)

        logger.info(f"Created room: {room.name} with SID: {room.sid}")

        return {
            "room_id": room.name,
            "sid": room.sid,
            "max_participants": room.max_participants,
            "creation_time": room.creation_time,
            "metadata": room.metadata
        }
    
    except Exception as e:
        logger.error(f"Error creating room {room_name}: {str(e)}")
        raise

#  Get details of a LiveKit room by name.
# Returns a dictionary with room info if found, otherwise None.
# Uses async since it calls LiveKit server.

async def get_room(self, room_name: str) -> Optional[Dict]:
    """Get room information"""

    try:
        rooms = await self.room_service.list_rooms([room_name])
        if rooms:
            room = rooms[0]

            return {
                "room_id": room.name,
                "sid": room.sid,
                "num_participants": room.num_participants,
                "max_participants": room.max_participants,
                "creation_time": room.creation_time,
                "metadata": room.metadata
            }

        return None
    
    except Exception as e:
        logger.error(f"Error getting room {room_name}: {str(e)}")
        return None
    
# Get a list of all participants in a given LiveKit room.
# Returns a list of dictionaries with participant details (identity, name, state, tracks, etc.).
# If an error occurs, returns an empty list.

async def list_participants(self, room_name: str) -> List[Dict]:
    """List all participants in a room"""

    try:
        participants = await self.room_service.list_participants(room_name)

        return [
            {
                "identity": p.identity,
                "name": p.name,
                "state": p.state.name,
                "tracks": [
                    {
                        "sid": track.sid,
                        "name": track.name,
                        "type": track.type.name,
                        "muted": track.muted
                    }
                    for track in p.tracks
                ],
                "metadata": p.metadata,
                "joined_at": p.joined_at,
                "is_publisher": p.is_publisher
            }
            for p in participants
        ]

    except Exception as e:
        logger.error(f"Error listing participants in room {room_name}: {str(e)}")
        return []

# Remove a specific participant from a LiveKit room by their identity.
# Returns True if successful, otherwise False if an error occurs.

async def remove_participants(self, room_name: str, participant_identity: str) -> bool:
    """Remove a participant from a room """

    try:
        await self.room_service.remove_participants(
            api.RoomParticipantIdentity(
                room = room_name,
                identity = participant_identity
            )
        )

        logger.info(f"Remove participant {participant_identity} from room {room_name}")
        return True
    
    except Exception as e:
        logger.error(f"Error removing participant {participant_identity} from room {room_name} : {str(e)}")   
        return False
    
# Mute a participant's audio or video track in a LiveKit room.
# - track_type can be "audio" (default) or "video".
# - Returns True if successful, otherwise False on error.  

async def mute_participant(
       self,
       room_name: str,
       participant_identity: str,
       track_type: str = "audio" 
)-> bool:
    """Mute a participant's track"""
    try:
        # convert string to tracktype enum
        track_type_enum = api.TrackType.AUDIO if track_type == "audio" else api.TrackType.VIDEO

        await self.room_service.mute_published_track(
            api.MuteRoomTrackRequest(
                room = room_name,
                identity = participant_identity,
                track_type = track_type_enum,
                muted=True
            )
        )

        logger.info(f"Muted {track_type} for participant {participant_identity} in room {room_name}")
        return True

    except Exception as e:
        logger.error(f"Error muting participant: {str(e)}")
        return False

#  Send a data message to participants in a LiveKit room.
# - If participant_identity is given, message goes only to that participant.
# - If not, message is broadcast to all participants.
# - Returns True if successful, otherwise False.

async def send_data_to_participants(
        self,
        room_name: str,
        data: str,
        participant_idenetity: str = None
)-> bool:
    """Send data message to participants"""  
    try:
        destinations = [participant_idenetity] if participant_idenetity else []

        await self.room_service.send_data(
            api.SendDataRequest(
                room = room_name,
                data = data.encode(),
                destination_sids = destinations
            )
        )

        logger.info(f"Sent data to room {room_name}")
        return True  
    
    except Exception as e:
        logger.error(f"Error sending data: {str(e)}")
        return False
    
#  Generate a unique room ID using:
# - a prefix (default "room"),
# - a random 8-char UUID,
# - and the current timestamp.
# Example: room_ab12cd34_1737171717

def generate_room_id(self , prefix: str = "room")-> str:
    """Generate a unique room ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}" 

#  Get detailed statistics for a LiveKit room.
# - Fetches room info and participants.
# - Counts total participants, active publishers, audio tracks, and video tracks.
# - Returns all stats in a dictionary (empty dict if room not found or error).

async def get_room_stats(self, room_name: str)-> Dict:
    """Get detailed room statistics"""
    try:
        room_info = await self.get_room(room_name)
        participants = await self.list_participants(room_name)

        if not room_info:
            return{}
        
        # calculate stats
        active_publishers = sum(1 for p in participants if p.get("is_publisher"))
        audio_tracks = sum(
            1 for p in participants
            for track in p.get("tracks", [])
            if track.get("type") == "AUDIO"
        )
        video_tracks = sum(
            1 for p in participants
            for track in p.get("tracks", [])
            if track.get("type") == "VIDEO"
        )

        return {
            "room_info": room_info,
            "participant_count": len(participants),
            "active_publishers": active_publishers,
            "audio_tracks": audio_tracks,
            "video_tracks": video_tracks,
            "participants": participants

        }
    
    except Exception as e:
        logger.error(f"Error getting room stats for {room_name}: {str(e)}")
        return {}
        
# create singleton instance
livekit_service = LiveKitService()