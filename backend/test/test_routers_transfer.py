# test/test_routers_transfer.py
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone
import asyncio

from app.main import app
from app.database import get_db, CallStatus, AgentStatus, TransferStatus
from models.transfer import TransferRequest, TransferResponse, TransferStatusResponse, AgentAvailabilityResponse


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
async def test_initiate_transfer_success(override_get_db):
    request_data = {
        "call_id": "call1",
        "from_agent_id": "agent1",
        "to_agent_id": "agent2",
        "reason": "Specialized assistance needed"
    }

    # Mock the service response - this should match what your service actually returns
    mock_service_response = {
        "success": True,
        "transfer_id": "transfer1",
        "transfer_room_id": "room-transfer1",
        "from_agent_token": "token1",
        "to_agent_token": "token2",
        "summary": "Call summary",
        "transfer_context": "Transfer context",
        "call_room_id": "room-call1",
        "status": "IN_PROGRESS",
        "call_id": "call1",
        "from_agent_id": "agent1",
        "to_agent_id": "agent2",
        "initiated_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "duration_seconds": 0,
        "reason": "Specialized assistance needed"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.initiate_warm_transfer", AsyncMock(return_value=mock_service_response)):
            response = await ac.post("/routers/transfer/initiate", json=request_data)

    assert response.status_code == 200
    body = response.json()
    assert body["transfer_id"] == "transfer1"
    assert body["transfer_room_id"] == "room-transfer1"


@pytest.mark.asyncio
async def test_initiate_transfer_failure(override_get_db):
    request_data = {
        "call_id": "call1",
        "from_agent_id": "agent1",
        "to_agent_id": "agent2"
    }

    mock_service_response = {
        "success": False,
        "error": "Target agent is not available"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.initiate_warm_transfer", AsyncMock(return_value=mock_service_response)):
            response = await ac.post("/routers/transfer/initiate", json=request_data)

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Target agent is not available"


@pytest.mark.asyncio
async def test_complete_transfer_success(override_get_db):
    mock_service_response = {
        "success": True,
        "call_room_id": "room-call1",
        "to_agent_call_token": "token123",
        "transfer_completed_at": datetime.now(timezone.utc).isoformat()
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.complete_warm_transfer", AsyncMock(return_value=mock_service_response)):
            response = await ac.post("/routers/transfer/transfer1/complete")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Transfer completed successfully"
    assert "call_room_id" in body


@pytest.mark.asyncio
async def test_complete_transfer_failure(override_get_db):
    mock_service_response = {
        "success": False,
        "error": "Transfer not found"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.complete_warm_transfer", AsyncMock(return_value=mock_service_response)):
            response = await ac.post("/routers/transfer/transfer1/complete")

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Transfer not found"


@pytest.mark.asyncio
async def test_cancel_transfer_success(override_get_db):
    mock_service_response = {"success": True, "message": "Transfer cancelled"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.cancel_transfer", AsyncMock(return_value=mock_service_response)):
            response = await ac.post("/routers/transfer/transfer1/cancel", json={"reason": "Customer changed mind"})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Transfer cancelled successfully"


@pytest.mark.asyncio
async def test_cancel_transfer_failure(override_get_db):
    mock_service_response = {
        "success": False,
        "error": "Transfer not found"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.cancel_transfer", AsyncMock(return_value=mock_service_response)):
            response = await ac.post("/routers/transfer/transfer1/cancel")

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Transfer not found"


@pytest.mark.asyncio
async def test_get_transfer_status_success(override_get_db):
    mock_service_response = {
        "transfer_id": "transfer1",
        "status": TransferStatus.IN_PROGRESS.value,
        "call_id": "call1",
        "from_agent_id": "agent1",
        "to_agent_id": "agent2",
        "initiated_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "duration_seconds": 0,
        "transfer_room_id": "room-transfer1",
        "summary": "Call summary",
        "reason": "Specialized assistance"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.get_transfer_status", AsyncMock(return_value=mock_service_response)):
            response = await ac.get("/routers/transfer/transfer1/status")

    assert response.status_code == 200
    body = response.json()
    assert body["transfer_id"] == "transfer1"
    assert body["status"] == TransferStatus.IN_PROGRESS.value


@pytest.mark.asyncio
async def test_get_transfer_status_not_found(override_get_db):
    mock_service_response = {"error": "Transfer not found"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.get_transfer_status", AsyncMock(return_value=mock_service_response)):
            response = await ac.get("/routers/transfer/transfer1/status")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Transfer not found"


@pytest.mark.asyncio
async def test_get_available_agents_success(override_get_db):
    mock_service_response = [
        {
            "id": "agent1",
            "name": "Alice",
            "email": "alice@example.com",
            "skills": ["support", "billing"],
            "active_calls": 1,
            "max_calls": 3,
            "availability_capacity": 2
        },
        {
            "id": "agent2",
            "name": "Bob",
            "email": "bob@example.com",
            "skills": ["technical"],
            "active_calls": 0,
            "max_calls": 3,
            "availability_capacity": 3
        }
    ]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.get_agent_availability", AsyncMock(return_value=mock_service_response)):
            response = await ac.get("/routers/transfer/agents/available")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["name"] == "Alice"
    assert body[1]["name"] == "Bob"
    assert body[0]["availability_capacity"] == 2


@pytest.mark.asyncio
async def test_get_active_transfers_success(override_get_db):
    mock_service_response = [
        {
            "call_id": "call1",
            "transfer_room_id": "room-transfer1",
            "from_agent_id": "agent1",
            "to_agent_id": "agent2",
            "status": TransferStatus.IN_PROGRESS.value,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.get_active_transfers", return_value=mock_service_response):
            response = await ac.get("/routers/transfer/active")

    assert response.status_code == 200
    body = response.json()
    assert "active_transfers" in body
    assert len(body["active_transfers"]) == 1
    assert body["active_transfers"][0]["call_id"] == "call1"


@pytest.mark.asyncio
async def test_get_active_transfers_empty(override_get_db):
    mock_service_response = []

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.get_active_transfers", return_value=mock_service_response):
            response = await ac.get("/routers/transfer/active")

    assert response.status_code == 200
    body = response.json()
    assert body["active_transfers"] == []


@pytest.mark.asyncio
async def test_initiate_transfer_server_error(override_get_db):
    request_data = {
        "call_id": "call1",
        "from_agent_id": "agent1",
        "to_agent_id": "agent2"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.initiate_warm_transfer", AsyncMock(side_effect=Exception("Database error"))):
            response = await ac.post("/routers/transfer/initiate", json=request_data)

    assert response.status_code == 500
    body = response.json()
    assert "detail" in body


@pytest.mark.asyncio
async def test_complete_transfer_server_error(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.complete_warm_transfer", AsyncMock(side_effect=Exception("Network error"))):
            response = await ac.post("/routers/transfer/transfer1/complete")

    assert response.status_code == 500
    body = response.json()
    assert "detail" in body


@pytest.mark.asyncio
async def test_cancel_transfer_with_reason(override_get_db):
    mock_service_response = {"success": True, "message": "Transfer cancelled"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.cancel_transfer", AsyncMock(return_value=mock_service_response)):
            response = await ac.post("/routers/transfer/transfer1/cancel?reason=Customer%20changed%20mind")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Transfer cancelled successfully"


@pytest.mark.asyncio
async def test_get_transfer_status_server_error(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.get_transfer_status", AsyncMock(side_effect=Exception("DB connection failed"))):
            response = await ac.get("/routers/transfer/transfer1/status")

    assert response.status_code == 500
    body = response.json()
    assert "detail" in body


@pytest.mark.asyncio
async def test_get_available_agents_server_error(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.transfer.transfer_service.get_agent_availability", AsyncMock(side_effect=Exception("Query failed"))):
            response = await ac.get("/routers/transfer/agents/available")

    assert response.status_code == 500
    body = response.json()
    assert "detail" in body