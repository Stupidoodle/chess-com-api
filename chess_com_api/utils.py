"""Utility functions."""

from datetime import datetime
from typing import Optional


def format_timestamp(timestamp: Optional[int]) -> Optional[datetime]:
    """Convert Unix timestamp to datetime object."""
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp)
