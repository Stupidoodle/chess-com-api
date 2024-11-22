# tests/test_utils.py

from datetime import datetime

from chess_com_api.utils import format_timestamp


def test_format_timestamp():
    """Test timestamp formatting."""
    now = int(datetime.now().timestamp())
    formatted = format_timestamp(now)

    assert isinstance(formatted, datetime)
    assert format_timestamp(None) is None
