"""
A simple in-memory registry to hold large tabular payloads so we don't pass them
through the LLM context. Store data and reference it by a short key in tool calls.
"""
from __future__ import annotations
from typing import Dict, Optional
import uuid

# Module-level in-memory store (process lifetime)
_REGISTRY: Dict[str, str] = {}


def register_data(data: str) -> str:
    """Store data and return a unique key."""
    key = f"data:{uuid.uuid4().hex}"
    _REGISTRY[key] = data
    return key


def get_data(key: str) -> Optional[str]:
    """Retrieve data by key, or None if missing."""
    return _REGISTRY.get(key)


def delete_data(key: str) -> None:
    _REGISTRY.pop(key, None)


def clear() -> None:
    _REGISTRY.clear()

