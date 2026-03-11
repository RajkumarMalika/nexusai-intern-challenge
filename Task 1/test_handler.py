import pytest
import asyncio
import httpx
from unittest.mock import patch
from openai import RateLimitError

from handler import handle_message
from models import MessageResponse

# Helper to create a realistic OpenAI RateLimitError
def create_rate_limit_error():
    request = httpx.Request("POST", "https://api.openai.com")
    response = httpx.Response(429, request=request)
    return RateLimitError("Rate limit exceeded", response=response, body=None)

@pytest.mark.asyncio
async def test_empty_input():
    """Test Case 1: Empty input should return immediately without calling the API."""
    response = await handle_message("   ", "CUST-123", "chat")
    
    assert response.error == "Input Error: Customer message cannot be empty or whitespace-only."
    assert response.response_text == ""
    assert response.confidence == 0.0

@pytest.mark.asyncio
@patch("handler._call_openai_with_timeout")
async def test_successful_api_call(mock_api_call):
    """Test Case 2: A normal, successful API response."""
    # Define what the fake API should return
    mock_api_call.return_value = {
        "response_text": "I can help with your router.",
        "confidence": 0.95,
        "suggested_action": "Check Router"
    }
    
    response = await handle_message("My internet is down", "CUST-123", "chat")
    
    assert response.error is None
    assert response.response_text == "I can help with your router."
    assert response.confidence == 0.95
    mock_api_call.assert_called_once()

@pytest.mark.asyncio
@patch("handler._call_openai_with_timeout")
async def test_api_timeout(mock_api_call):
    """Test Case 3: The API takes longer than 10 seconds."""
    # Force the mock to raise a TimeoutError
    mock_api_call.side_effect = asyncio.TimeoutError
    
    response = await handle_message("My internet is down", "CUST-123", "voice")
    
    assert response.error == "API Error: Request timed out after 10 seconds."
    assert response.response_text == ""

@pytest.mark.asyncio
@patch("asyncio.sleep") # We mock sleep so the test doesn't actually wait 2 seconds
@patch("handler._call_openai_with_timeout")
async def test_rate_limit_retry_success(mock_api_call, mock_sleep):
    """Test Case 4: API hits a rate limit, retries, and succeeds."""
    
    # side_effect with a list returns the items in sequence per call
    # Call 1: Raise RateLimitError | Call 2: Return successful JSON
    mock_api_call.side_effect = [
        create_rate_limit_error(),
        {
            "response_text": "Thanks for waiting, I have pulled up your bill.",
            "confidence": 0.88,
            "suggested_action": "Transfer to Billing"
        }
    ]
    
    response = await handle_message("Billing issue", "CUST-123", "whatsapp")
    
    # Assertions
    assert response.error is None
    assert "Thanks for waiting" in response.response_text
    
    # Verify the mock was called exactly twice (the initial try + the retry)
    assert mock_api_call.call_count == 2
    # Verify our 2-second sleep was triggered during the retry phase
    mock_sleep.assert_called_once_with(2)
