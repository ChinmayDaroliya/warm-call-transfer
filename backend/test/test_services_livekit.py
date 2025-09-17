import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from services.livekit_service import LiveKitService

@pytest.mark.asyncio
async def test_generate_access_token():
    service = LiveKitService()
    token = service.generate_access_token("test_room", "user1")
    assert isinstance(token, str)
    assert len(token) > 0

@pytest.mark.asyncio
async def test_generate_room_id():
    service = LiveKitService()
    room_id = service.generate_room_id("test")
    assert room_id.startswith("test_")
    assert len(room_id) > 10

@pytest.mark.asyncio
async def test_create_room():
    service = LiveKitService()

    # Use a regular object instead of AsyncMock for the room
    mock_room = SimpleNamespace(
        name="room1",
        sid="sid123",
        max_participants=10,
        creation_time="2025-09-18T00:00:00Z",
        metadata=None
    )
    mock_room_service = AsyncMock()
    mock_room_service.create_room.return_value = mock_room

    with patch.object(service, 'get_room_service', return_value=mock_room_service):
        result = await service.create_room("room1", 10)
        assert result["room_id"] == "room1"
        assert result["sid"] == "sid123"

@pytest.mark.asyncio
async def test_get_room():
    service = LiveKitService()

    mock_room = SimpleNamespace(
        name="room1",
        sid="sid123",
        num_participants=5,
        max_participants=10,
        creation_time="2025-09-18T00:00:00Z",
        metadata=None
    )

    mock_room_service = AsyncMock()
    mock_room_service.list_rooms.return_value = [mock_room]

    with patch.object(service, 'get_room_service', return_value=mock_room_service):
        result = await service.get_room("room1")
        assert result["room_id"] == "room1"
        assert result["num_participants"] == 5

@pytest.mark.asyncio
async def test_list_participants():
    service = LiveKitService()

    mock_participant = SimpleNamespace(
        identity="user1",
        name="User One",
        state=SimpleNamespace(name="CONNECTED"),
        tracks=[],
        metadata=None,
        joined_at="2025-09-18T00:00:00Z",
        is_publisher=True
    )

    mock_room_service = AsyncMock()
    mock_room_service.list_participants.return_value = [mock_participant]

    with patch.object(service, 'get_room_service', return_value=mock_room_service):
        participants = await service.list_participants("room1")
        assert len(participants) == 1
        assert participants[0]["identity"] == "user1"

@pytest.mark.asyncio
async def test_remove_participant():
    service = LiveKitService()
    mock_room_service = AsyncMock()
    mock_room_service.remove_participants.return_value = None

    with patch.object(service, 'get_room_service', return_value=mock_room_service):
        result = await service.remove_participant("room1", "user1")
        assert result is True

@pytest.mark.asyncio
async def test_mute_participant():
    service = LiveKitService()
    
    # Mock a track
    mock_track = AsyncMock()
    mock_track.sid = "track1"
    
    # Mock a participant with tracks
    mock_participant = AsyncMock()
    mock_participant.identity = "user1"
    mock_participant.tracks = [mock_track]
    
    # Mock room service
    mock_room_service = AsyncMock()
    mock_room_service.list_participants.return_value = [mock_participant]
    mock_room_service.mute_published_track.return_value = None

    with patch.object(service, 'get_room_service', return_value=mock_room_service):
        result = await service.mute_participant("room1", "user1")
        assert result is True


@pytest.mark.asyncio
async def test_send_data_to_participants():
    service = LiveKitService()
    mock_room_service = AsyncMock()
    mock_room_service.send_data.return_value = None

    with patch.object(service, 'get_room_service', return_value=mock_room_service):
        result = await service.send_data_to_participants("room1", "hello world")
        assert result is True
