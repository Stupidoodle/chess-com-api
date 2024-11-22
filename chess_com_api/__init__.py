"""Chess.com API Client.

~~~~~~~~~~~~~~~~~~

A modern, fully typed, asynchronous Python wrapper for the Chess.com API.

Basic usage:

    >>> import asyncio
    >>> from chess_com_api import ChessComClient
    >>>
    >>> async def main():
    ...     async with ChessComClient() as client:
    ...         player = await client.get_player("hikaru")
    ...         print(f"Title: {player.title}")
    ...
    >>> asyncio.run(main())
    Title: GM

:copyright: (c) 2024 by [Bryan Tran].
:license: MIT, see LICENSE for more details.
"""

from chess_com_api._version import __version__
from chess_com_api.client import ChessComClient
from chess_com_api.exceptions import (
    ChessComAPIError,
    GoneError,
    NotFoundError,
    RateLimitError,
    RedirectError,
    ValidationError,
)
from chess_com_api.models import (
    Board,
    Club,
    Country,
    DailyGame,
    DailyPuzzle,
    Game,
    Leaderboard,
    Match,
    Player,
    PlayerMatches,
    PlayerStats,
    PlayerTournaments,
    Round,
    Streamer,
    Tournament,
    UserClub,
)

__all__ = [
    "__version__",
    "ChessComClient",
    "ChessComAPIError",
    "GoneError",
    "NotFoundError",
    "RateLimitError",
    "RedirectError",
    "ValidationError",
    "Board",
    "Club",
    "Country",
    "DailyGame",
    "DailyPuzzle",
    "Game",
    "Leaderboard",
    "Match",
    "Player",
    "PlayerMatches",
    "PlayerStats",
    "PlayerTournaments",
    "Round",
    "Streamer",
    "Tournament",
    "UserClub",
]
