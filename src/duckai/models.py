"""Data models for DuckAI"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Message:
    """Represents a chat message"""

    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None
    model: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for API requests"""
        return {"role": self.role, "content": self.content}


@dataclass
class Conversation:
    """Represents a conversation session"""

    id: str
    messages: List[Message]
    model: str
    created_at: datetime

    def add_message(self, role: str, content: str) -> Message:
        """Add a message to the conversation"""
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        return msg

    def to_api_format(self) -> List[dict]:
        """Convert conversation to API format"""
        return [msg.to_dict() for msg in self.messages]
