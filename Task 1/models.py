from dataclasses import dataclass
from typing import Optional, Literal

ChannelType = Literal["voice", "whatsapp", "chat"]

@dataclass
class MessageResponse:
    response_text: str
    confidence: float
    suggested_action: str
    channel_formatted_response: str
    error: Optional[str] = None
