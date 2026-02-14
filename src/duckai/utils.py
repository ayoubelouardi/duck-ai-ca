"""Utility functions for DuckAI"""

import re
import json
from typing import Any, Dict, Optional


def clean_text(text: str) -> str:
    """Clean and normalize text input"""
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse Server-Sent Events (SSE) line

    SSE format: data: {...json...}
    """
    if line.startswith("data: "):
        data = line[6:]  # Remove "data: " prefix
        if data == "[DONE]":
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    return None


def format_response(text: str) -> str:
    """Format AI response for display"""
    # Remove any markdown code block markers if needed
    return text.strip()


def print_stream_chunk(chunk: str, end: str = ""):
    """Print streaming chunk without newline"""
    print(chunk, end=end, flush=True)
