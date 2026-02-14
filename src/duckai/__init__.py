"""DuckAI - DuckDuckGo AI API Client"""

__version__ = "0.1.0"
__author__ = "DuckAI"

from .client import DuckAIClient
from .models import Message, Conversation

__all__ = ["DuckAIClient", "Message", "Conversation"]
