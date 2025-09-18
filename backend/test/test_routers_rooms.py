import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from unittest.mock import AsyncMock, patch

from app.main import app # your FastAPI app entrypoint


@pytest.mark.asyncio
async def test_get_room_info_success():
    mock_room = {"room_id": "room1", "sid": "sid123", "num_participants": 2}
    with patch("routers.rooms.livekit_service.get_room", new=AsyncMock(return_value=mock_room)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/rooms/room1/info")
    assert response.status_code == 200
    assert response.json() == mock_room


@pytest.mark.asyncio
async def test_get_room_info_not_found():
    with patch("routers.rooms.livekit_service.get_room", new=AsyncMock(return_value=None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/rooms/missing/info")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_get_room_participants_success():
    mock_participants = [{"identity": "user1"}, {"identity": "user2"}]
    with patch("routers.rooms.livekit_service.list_participants", new=AsyncMock(return_value=mock_participants)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/rooms/room1/participants")
    assert response.status_code == 200
    assert response.json() == {"participants": mock_participants}


@pytest.mark.asyncio
async def test_get_room_stats_success():
    mock_stats = {"room_info": {"room_id": "room1"}, "participant_count": 3}
    with patch("routers.rooms.livekit_service.get_room_stats", new=AsyncMock(return_value=mock_stats)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/rooms/room1/stats")
    assert response.status_code == 200
    assert response.json() == mock_stats


@pytest.mark.asyncio
async def test_close_room_success():
    with patch("routers.rooms.livekit_service.close_room", new=AsyncMock(return_value=True)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.delete("/rooms/room1")
    assert response.status_code == 200
    assert response.json() == {"message": "Room closed successfully"}


@pytest.mark.asyncio
async def test_close_room_failure():
    with patch("routers.rooms.livekit_service.close_room", new=AsyncMock(return_value=False)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.delete("/rooms/room1")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Failed to close room"


@pytest.mark.asyncio
async def test_mute_participant_success():
    with patch("routers.rooms.livekit_service.mute_participant", new=AsyncMock(return_value=True)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/rooms/room1/mute", params={"participant_identity": "user1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Participant muted successfully"}


@pytest.mark.asyncio
async def test_mute_participant_failure():
    with patch("routers.rooms.livekit_service.mute_participant", new=AsyncMock(return_value=False)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/rooms/room1/mute", params={"participant_identity": "user1"})
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Failed to mute participant"


@pytest.mark.asyncio
async def test_remove_participant_success():
    with patch("routers.rooms.livekit_service.remove_participant", new=AsyncMock(return_value=True)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/rooms/room1/remove", params={"participant_identity": "user1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Participant removed successfully"}


@pytest.mark.asyncio
async def test_remove_participant_failure():
    with patch("routers.rooms.livekit_service.remove_participant", new=AsyncMock(return_value=False)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/rooms/room1/remove", params={"participant_identity": "user1"})
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Failed to remove participant"


@pytest.mark.asyncio
async def test_send_data_to_room_success():
    with patch("routers.rooms.livekit_service.send_data_to_participants", new=AsyncMock(return_value=True)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/rooms/room1/send-data", params={"data": "hello"})
    assert response.status_code == 200
    assert response.json() == {"message": "Data sent successfully"}


@pytest.mark.asyncio
async def test_send_data_to_room_failure():
    with patch("routers.rooms.livekit_service.send_data_to_participants", new=AsyncMock(return_value=False)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/rooms/room1/send-data", params={"data": "hello"})
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Failed to send data"
