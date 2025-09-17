import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.transfer_service import TransferService
from services.llm_service import llm_service
from services import livekit_service

@pytest.mark.asyncio
async def test_initiate_warm_transfer_success():
    transfer_service = TransferService()

    # Mock DB session and query results
    mock_db = MagicMock()
    mock_call = MagicMock()
    mock_call.id = "call1"
    mock_call.transcript = "Test transcript"
    mock_call.caller_name = "John"
    mock_call.caller_phone = "123"
    mock_call.duration_seconds = 120
    mock_call.call_reason = "Support"
    mock_call.status = "active"
    mock_call.summary = None
    mock_call.room_id = "room1"
    mock_call.agent_a_id = "agent1"

    mock_from_agent = MagicMock()
    mock_from_agent.id = "agent1"
    mock_from_agent.name = "Alice"
    mock_from_agent.status = "available"
    mock_from_agent.skills = ["skill1"]
    mock_from_agent.max_concurrent_calls = 2

    mock_to_agent = MagicMock()
    mock_to_agent.id = "agent2"
    mock_to_agent.name = "Bob"
    mock_to_agent.status = "available"
    mock_to_agent.skills = ["skill1", "skill2"]
    mock_to_agent.max_concurrent_calls = 2

    # Setup DB mocks
    mock_db.query().filter().first.side_effect = [mock_call, mock_from_agent, mock_to_agent]
    mock_db.query().filter().count.return_value = 0   # ✅ simulate no active calls

    # Mock LLM service
    async def mock_generate_call_summary(**kwargs):
        return "Test Summary"

    async def mock_generate_transfer_context(**kwargs):
        return "Transfer Context"

    llm_service.generate_call_summary = mock_generate_call_summary
    llm_service.generate_transfer_context = mock_generate_transfer_context

    # Mock LiveKit service
    livekit_service.generate_room_id = lambda x: "transfer_room_1"
    livekit_service.create_room = AsyncMock(return_value={"sid": "room_sid"})
    livekit_service.generate_access_token = lambda **kwargs: "token"

    # Run the service
    result = await transfer_service.initiate_warm_transfer(
        "call1", "agent1", "agent2", "Reason", db=mock_db
    )

    assert result["success"] is True
    assert result["summary"] == "Test Summary"
    assert result["transfer_context"] == "Transfer Context"
    assert "transfer_id" in result



@pytest.mark.asyncio
async def test_cancel_transfer_success():
    transfer_service = TransferService()
    mock_db = MagicMock()

    from app.database import Call, Agent, Transfer

    mock_transfer = Transfer(
        id="transfer1",
        transfer_room_id="room1",
        call_id="call1",
        from_agent_id="agent1",
        to_agent_id="agent2"
    )

    mock_from_agent = Agent(id="agent1", name="Alice", status="busy", skills=[], max_concurrent_calls=2)
    mock_to_agent = Agent(id="agent2", name="Bob", status="available", skills=[], max_concurrent_calls=2)
    mock_call = Call(id="call1", room_id="room1", status="transferring", agent_a_id="agent1", agent_b_id=None)

    mock_db.query().filter().first.side_effect = [mock_transfer, mock_call, mock_from_agent, mock_to_agent]

    # ✅ Patch the singleton livekit_service, not the class
    with patch("services.livekit_service.livekit_service.close_room", new_callable=AsyncMock) as mock_close:
        mock_close.return_value = None

    result = await transfer_service.cancel_transfer("transfer1", db=mock_db)

    assert result["success"] is True
    assert result["message"] == "Transfer cancelled"