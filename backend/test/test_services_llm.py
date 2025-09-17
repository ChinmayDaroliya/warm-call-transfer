import pytest
from unittest.mock import patch, MagicMock
from services.llm_service import LLMService

@pytest.mark.asyncio
async def test_generate_call_summary_success():
    llm = LLMService()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Summary Text"))]

    async def mock_acreate(*args, **kwargs):
        return mock_response

    with patch("openai.ChatCompletion.acreate", new=mock_acreate):
        result = await llm.generate_call_summary("Test transcript")
        assert result == "Summary Text"


@pytest.mark.asyncio
async def test_generate_call_summary_fallback_on_error():
    llm = LLMService()

    # simulate exception in OpenAI call
    async def mock_acreate(*args, **kwargs):
        raise Exception("API Error")

    with patch("openai.ChatCompletion.acreate", new=mock_acreate):
        result = await llm.generate_call_summary("Test transcript")
        assert "Auto-generated fallback" in result


@pytest.mark.asyncio
async def test_create_summary_prompt_structure():
    llm = LLMService()
    prompt = llm.create_summary_prompt(
        transcript="Hello",
        caller_info={"name": "John", "phone": "123"},
        call_duration=125,
        call_reason="Support"
    )
    assert "Caller Information" in prompt
    assert "Call duration" in prompt
    assert "CALL TRANSCRIPT" in prompt


@pytest.mark.asyncio
async def test_generate_transfer_context_success():
    llm = LLMService()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Transfer Message"))]

    async def mock_acreate(*args, **kwargs):
        return mock_response

    with patch("openai.ChatCompletion.acreate", new=mock_acreate):
        result = await llm.generate_transfer_context("Summary Text", "Reason")
        assert result == "Transfer Message"


@pytest.mark.asyncio
async def test_analyze_call_sentiment_success():
    llm = LLMService()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"overall_sentiment":"positive","confidence":0.9,"key_emotions":["happy"],"escalation_risk":"low","summary":"Good call"}'))]

    async def mock_acreate(*args, **kwargs):
        return mock_response

    with patch("openai.ChatCompletion.acreate", new=mock_acreate):
        result = await llm.analyze_call_sentiment("Transcript here")
        assert result["overall_sentiment"] == "positive"
        assert result["confidence"] == 0.9


@pytest.mark.asyncio
async def test_analyze_call_sentiment_fallback():
    llm = LLMService()

    async def mock_acreate(*args, **kwargs):
        raise Exception("API Error")

    with patch("openai.ChatCompletion.acreate", new=mock_acreate):
        result = await llm.analyze_call_sentiment("Transcript here")
        assert result["overall_sentiment"] == "neutral"
        assert "Sentiment analysis unavailable" in result["summary"]
