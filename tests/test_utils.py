"""Tests for the `utils` module."""

from datetime import datetime

from chess_com_api.utils import format_timestamp


def test_format_timestamp() -> None:
    """Test the `format_timestamp` function.

    This function verifies the behavior of `format_timestamp` by checking whether it
    correctly converts a valid timestamp to a `datetime` object and appropriately
    handles a `None` input without raising an error.

    :return: None
    """
    now = int(datetime.now().timestamp())
    formatted = format_timestamp(now)

    assert isinstance(formatted, datetime)
    assert format_timestamp(None) is None
