# test/test_routers_agents.py
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from types import SimpleNamespace

from app.main import app
from app.database import get_db, AgentStatus
from models.agent import AgentCreateRequest, AgentUpdateRequest, AgentStatusUpdate, AgentResponse


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
async def test_create_agent_success(override_get_db):
    request_data = {
        "name": "Alice",
        "email": "alice@example.com",
        "skills": ["support"]
    }

    # Create a proper dictionary with all required fields
    mock_agent_data = {
        "id": "agent1",
        "name": "Alice",
        "email": "alice@example.com",
        "status": AgentStatus.AVAILABLE,
        "current_room_id": None,
        "max_concurrent_calls": 3,
        "skills": ["support"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch("routers.agents.db_create_agent", return_value=mock_agent_data):
            # Ensure email uniqueness check returns None
            override_get_db.query.return_value.filter.return_value.first.return_value = None
            response = await ac.post("/routers/agents/", json=request_data)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"
    assert body["status"] == AgentStatus.AVAILABLE.value


@pytest.mark.asyncio
async def test_list_agents(override_get_db):
    mock_db = override_get_db
    mock_agent = SimpleNamespace(
        id="agent1",
        name="Alice",
        email="alice@example.com",
        status=AgentStatus.AVAILABLE.value,
        current_room_id=None,
        skills=["support"],
    )
    mock_db.query().order_by().all.return_value = [mock_agent]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/routers/agents/")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_get_agent_success(override_get_db):
    mock_db = override_get_db
    mock_agent = SimpleNamespace(
        id="agent1",
        name="Alice",
        email="alice@example.com",
        status=AgentStatus.AVAILABLE.value,
        current_room_id=None,
        max_concurrent_calls=3,
        skills=["support"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.query().filter().first.return_value = mock_agent

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/routers/agents/agent1")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "agent1"
    assert body["name"] == "Alice"


@pytest.mark.asyncio
async def test_update_agent_success(override_get_db):
    request_data = {
        "name": "Alice Updated",
        "skills": ["support", "billing"],
        "max_concurrent_calls": 5
    }

    mock_agent = SimpleNamespace(
        id="agent1",
        name="Alice",
        email="alice@example.com",
        skills=["support"],
        max_concurrent_calls=3,
        status=AgentStatus.AVAILABLE.value,
        current_room_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    override_get_db.query().filter().first.return_value = mock_agent

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put("/routers/agents/agent1", json=request_data)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alice Updated"
    assert body["skills"] == ["support", "billing"]


@pytest.mark.asyncio
async def test_update_agent_status_success(override_get_db):
    mock_db = override_get_db
    mock_agent = SimpleNamespace(
        status=AgentStatus.BUSY.value,
        current_room_id="room123"
    )
    mock_db.query().filter().first.return_value = mock_agent

    request_data = {"status": AgentStatus.AVAILABLE.value}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch("/routers/agents/agent1/status", json=request_data)

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Agent status updated successfully"
    assert mock_agent.current_room_id is None


@pytest.mark.asyncio
async def test_delete_agent_success(override_get_db):
    mock_db = override_get_db
    mock_agent = SimpleNamespace(
        status=AgentStatus.AVAILABLE.value
    )
    mock_db.query().filter().first.return_value = mock_agent

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/routers/agents/agent1")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Agent deleted successfully"
