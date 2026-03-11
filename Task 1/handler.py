import asyncio
import json
from openai import AsyncOpenAI, RateLimitError
from dotenv import load_dotenv

from models import MessageResponse, ChannelType
from prompts import get_system_prompt

# Load environment variables if a .env file is present (evaluator use)
load_dotenv()

# The client automatically picks up the OPENAI_API_KEY from the environment
client = AsyncOpenAI()

async def _call_openai_with_timeout(messages: list, timeout: int = 10) -> dict:
    """Helper function to call OpenAI with a strict timeout."""
    response = await asyncio.wait_for(
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
        ),
        timeout=timeout
    )
    return json.loads(response.choices[0].message.content)


async def handle_message(
    customer_message: str, 
    customer_id: str, 
    channel: ChannelType
) -> MessageResponse:
    
    # Requirement (c): Empty or whitespace-only input
    if not customer_message or not customer_message.strip():
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="",
            channel_formatted_response="",
            error="Input Error: Customer message cannot be empty or whitespace-only."
        )

    system_prompt = get_system_prompt(channel)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Customer ID: {customer_id}\nMessage: {customer_message}"}
    ]

    try:
        # Requirements (a) & (b): Timeout and Rate Limit handling
        try:
            data = await _call_openai_with_timeout(messages, timeout=10)
        except RateLimitError:
            # Retry once after 2 seconds
            await asyncio.sleep(2)
            data = await _call_openai_with_timeout(messages, timeout=10)

        response_text = data.get("response_text", "")
        
        # Format the response based on the channel
        if channel == "whatsapp":
            formatted_response = f"*[NovaTel Support]*\n{response_text}"
        elif channel == "voice":
            formatted_response = f"<speak>{response_text}</speak>" 
        else:
            formatted_response = response_text

        return MessageResponse(
            response_text=response_text,
            confidence=float(data.get("confidence", 0.0)),
            suggested_action=data.get("suggested_action", "None"),
            channel_formatted_response=formatted_response,
            error=None
        )

    except asyncio.TimeoutError:
        return MessageResponse(
            response_text="", confidence=0.0, suggested_action="", channel_formatted_response="",
            error="API Error: Request timed out after 10 seconds."
        )
    except RateLimitError:
        return MessageResponse(
            response_text="", confidence=0.0, suggested_action="", channel_formatted_response="",
            error="API Error: Rate limit exceeded after retry."
        )
    except Exception as e:
        return MessageResponse(
            response_text="", confidence=0.0, suggested_action="", channel_formatted_response="",
            error=f"Unexpected Error: {str(e)}"
        )
