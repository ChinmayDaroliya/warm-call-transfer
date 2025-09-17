import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.database import CallStatus, AgentStatus, get_db


# ---- Override DB dependency ----
@pytest.fixture(autouse=True)
def override_get_db():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    yield mock_db
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_new_call_success(override_get_db):
    mock_db = override_get_db

    with patch("services.livekit_service.livekit_service.create_room", new_callable=AsyncMock) as mock_create_room, \
         patch("services.livekit_service.livekit_service.generate_room_id", return_value="room123"), \
         patch("services.livekit_service.livekit_service.generate_access_token", return_value="fake_token"), \
         patch("app.database.create_call") as mock_create_call:

        mock_create_room.return_value = {"room": "info"}
        mock_create_call.return_value = MagicMock(id="call1", status=CallStatus.ACTIVE.value, created_at="now")

        request_data = {
            "caller_name": "Alice",
            "caller_phone": "123456",
            "call_reason": "Support",
            "priority": "normal",
            "assign_agent": False
        }

        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/routers/calls/create", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "call1"
        response = await ac.post("/routers/calls/create", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "call1"
        assert data["room_id"] == "room123"
        assert data["access_token"] == "fake_token"


@pytest.mark.asyncio
async def test_join_existing_call_success(override_get_db):
    mock_db = override_get_db
    mock_call = MagicMock(id="call1", room_id="room123", status=CallStatus.ACTIVE.value)
    mock_db.query().filter().first.return_value = mock_call

    with patch("services.livekit_service.livekit_service.generate_access_token", return_value="agent_token"):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/routers/calls/join", json={
                "room_id": "room123",
                "participant_identity": "agent_1",
                "participant_name": "Bob"
            })

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "agent_token"
        assert data["room_id"] == "room123"


@pytest.mark.asyncio
async def test_get_call_details_not_found(override_get_db):
    mock_db = override_get_db
    mock_db.query().filter().first.return_value = None

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/routers/calls/nonexistent-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Call not found"


@pytest.mark.asyncio
async def test_end_call_success(override_get_db):
    mock_call = MagicMock(id="call1", room_id="room123", status=CallStatus.ACTIVE.value)
    mock_call.agent_a = MagicMock(status=AgentStatus.BUSY.value)
    mock_call.agent_b = None

    mock_db = override_get_db
    mock_db.query().filter().first.return_value = mock_call

    with patch("services.livekit_service.livekit_service.close_room", new_callable=AsyncMock) as mock_close_room:
        mock_close_room.return_value = True

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete("/routers/calls/call1")

        assert response.status_code == 200
        assert response.json()["message"] == "Call ended successfully"
