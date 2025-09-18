import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from app.main import app
from app.database import CallStatus,get_db

@pytest.fixture
def override_get_db():
    mock_db = MagicMock()
    yield mock_db

@pytest.fixture(autouse=True)
def override_dependency(override_get_db):
    app.dependency_overrides[get_db] = lambda: override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_new_call_success(override_get_db):
    mock_db = override_get_db

    with patch("routers.calls.create_call") as mock_create_call, \
        patch("routers.calls.livekit_service.create_room", new_callable=AsyncMock) as mock_create_room, \
        patch("routers.calls.livekit_service.generate_room_id", return_value="room123"), \
        patch("routers.calls.livekit_service.generate_access_token", return_value="fake_token"):

        # Mock room creation
        mock_create_room.return_value = {"room": "info"}

        # Mock call creation
        mock_create_call.return_value = MagicMock(
             id="call1",
            room_id="room123",
            caller_name="Alice",
            caller_phone="123456",
            call_reason="Support",
            priority="normal",
            status=CallStatus.ACTIVE.value,
            agent_a_id=None,
            agent_b_id=None,         # ✅ must exist
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            started_at=None,
            ended_at=None,
            duration_seconds=None,
            transcript=None,
            summary=None,
            summary_generated_at=None,
            extra_metadata=None,
        )

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

        # Assertions
        assert response.status_code == 200
        body = response.json()
        assert body["caller_name"] == "Alice"
        assert body["room_id"] == "room123"
        assert "access_token" in body
        assert body["status"] == CallStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_join_existing_call_success(override_get_db):
    mock_db = override_get_db

    with patch("routers.calls.livekit_service.generate_access_token", return_value="fake_token"):
        # Mock DB call
        mock_call = MagicMock(
            id="call1",
            room_id="room123",
            status=CallStatus.ACTIVE.value
        )
        mock_db.query().filter().first.return_value = mock_call

        request_data = {
            "room_id": "room123",
            "participant_identity": "caller_1",
            "participant_name": "Alice"
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/routers/calls/join", json=request_data)

        # Assertions
        assert response.status_code == 200
        body = response.json()
        assert body["room_id"] == "room123"
        assert body["call_status"] == CallStatus.ACTIVE.value
        assert "access_token" in body

