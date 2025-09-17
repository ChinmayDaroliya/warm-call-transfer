import logging
from app.config import settings
from datetime import timedelta, datetime
from typing import Dict, Optional, List
import uuid

logger = logging.getLogger(__name__)

# LiveKit imports
try:
    from livekit.api import AccessToken, VideoGrants, CreateRoomRequest, RoomParticipantIdentity, TrackType, MuteRoomTrackRequest, SendDataRequest
except ImportError:
    try:
        from livekit import AccessToken, VideoGrants, CreateRoomRequest, RoomParticipantIdentity, TrackType, MuteRoomTrackRequest, SendDataRequest
    except ImportError:
        raise ImportError("LiveKit SDK not found. Install livekit-server-sdk.")

class LiveKitService:
    def __init__(self):
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.ws_url = settings.LIVEKIT_WS_URL
        self._api = None
        self._room_service = None

    async def _ensure_api_initialized(self):
        if self._api is None:
            try:
                from livekit import api as livekit_api
                self._api = livekit_api.LiveKitAPI(
                    url=self.ws_url,
                    api_key=self.api_key,
                    api_secret=self.api_secret
                )
            except ImportError:
                raise ImportError("LiveKit API could not be initialized.")
            self._room_service = self._api.room

    async def get_api(self):
        await self._ensure_api_initialized()
        return self._api

    async def get_room_service(self):
        await self._ensure_api_initialized()
        return self._room_service

    def generate_access_token(
        self,
        room_name: str,
        participant_identity: str,
        participant_name: Optional[str] = None,
        metadata: Optional[dict] = None,
        grants=None
    ) -> str:
        try:
            if not grants:
                grants = VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True
                )

            token = AccessToken(self.api_key, self.api_secret)
            token.with_identity(participant_identity)
            token.with_name(participant_name or participant_identity)
            token.with_grants(grants)
            if metadata:
                token.with_metadata(str(metadata))
            token.with_ttl(timedelta(hours=24))
            return token.to_jwt()
        except Exception as e:
            logger.error(f"Error generating access token: {str(e)}")
            raise

    async def create_room(self, room_name: str, max_participants: int = 10, metadata: Optional[Dict] = None) -> Dict:
        try:
            room_service = await self.get_room_service()
            room_options = CreateRoomRequest(
                name=room_name,
                max_participants=max_participants,
                metadata=str(metadata) if metadata else None
            )
            room = await room_service.create_room(room_options)
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

    async def get_room(self, room_name: str) -> Optional[Dict]:
        try:
            room_service = await self.get_room_service()
            rooms = await room_service.list_rooms([room_name])
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

    async def list_participants(self, room_name: str) -> List[Dict]:
        try:
            room_service = await self.get_room_service()
            participants = await room_service.list_participants(room_name)
            return [
                {
                    "identity": p.identity,
                    "name": p.name,
                    "state": p.state.name if hasattr(p.state, 'name') else str(p.state),
                    "tracks": [
                        {
                            "sid": t.sid,
                            "name": t.name,
                            "type": t.type.name if hasattr(t.type, 'name') else str(t.type),
                            "muted": t.muted
                        } for t in p.tracks
                    ],
                    "metadata": p.metadata,
                    "joined_at": p.joined_at,
                    "is_publisher": p.is_publisher
                } for p in participants
            ]
        except Exception as e:
            logger.error(f"Error listing participants in room {room_name}: {str(e)}")
            return []

    async def remove_participant(self, room_name: str, participant_identity: str) -> bool:
        try:
            room_service = await self.get_room_service()
            await room_service.remove_participants(
                RoomParticipantIdentity(room=room_name, identity=participant_identity)
            )
            return True
        except Exception as e:
            logger.error(f"Error removing participant {participant_identity} from room {room_name}: {str(e)}")
            return False

    async def mute_participant(self, room_name: str, participant_identity: str) -> bool:
        """
        Mute all tracks of a participant.
        This uses the latest LiveKit SDK signature.
        """
        try:
            room_service = await self.get_room_service()
            participants = await room_service.list_participants(room_name)
            participant = next((p for p in participants if p.identity == participant_identity), None)
            if not participant:
                logger.warning(f"Participant {participant_identity} not found in room {room_name}")
                return False

            # Mute each track individually
            for track in participant.tracks:
                await room_service.mute_published_track(
                    MuteRoomTrackRequest(
                        room=room_name,
                        identity=participant_identity,
                        track_sid=track.sid,
                        muted=True
                    )
                )
            return True
        except Exception as e:
            logger.error(f"Error muting participant {participant_identity}: {str(e)}")
            return False

    async def send_data_to_participants(self, room_name: str, data: str, participant_identity: Optional[str] = None) -> bool:
        try:
            room_service = await self.get_room_service()
            destinations = [participant_identity] if participant_identity else None
            await room_service.send_data(
                SendDataRequest(
                    room=room_name,
                    data=data.encode(),
                    destination_sids=destinations
                )
            )
            return True
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            return False

    def generate_room_id(self, prefix: str = "room") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"

    async def get_room_stats(self, room_name: str) -> Dict:
        try:
            room_info = await self.get_room(room_name)
            participants = await self.list_participants(room_name)
            if not room_info:
                return {}

            active_publishers = sum(1 for p in participants if p.get("is_publisher"))
            audio_tracks = sum(1 for p in participants for t in p.get("tracks", []) if t.get("type") == "AUDIO")
            video_tracks = sum(1 for p in participants for t in p.get("tracks", []) if t.get("type") == "VIDEO")

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

    async def close(self):
        if self._api and hasattr(self._api, '_session'):
            try:
                await self._api._session.close()
            except Exception as e:
                logger.error(f"Error closing API session: {e}")

# close room
    async def close_room(self, room_id: str):
        """Close a specific LiveKit room"""
        try:
            # Later you can replace this with an actual LiveKit API call:
            # await self.room_service.delete_room(room_id=room_id)
            logger.info(f"Closed room {room_id}")
            return True
        except Exception as e:
            logger.error(f"Error closing room {room_id}: {e}")
            return False


# Singleton factory
def get_livekit_service() -> LiveKitService:
    if not hasattr(get_livekit_service, "_instance"):
        get_livekit_service._instance = LiveKitService()
    return get_livekit_service._instance

livekit_service = get_livekit_service()
