"""Asynchronous client for the Chess.com API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

import aiohttp

from .exceptions import ChessComAPIError, GoneError, NotFoundError, RedirectError
from .models import (
    Board,
    BoardGame,
    Club,
    ClubMatches,
    Country,
    CountryClubs,
    DailyGame,
    DailyPuzzle,
    Game,
    GameArchive,
    Group,
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChessComClient:
    """Asynchronous client for the Chess.com API."""

    BASE_URL = "https://api.chess.com/pub"

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit: int = 300,
    ) -> None:
        """Initialize the Chess.com API client."""
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = session or aiohttp.ClientSession(timeout=self.timeout)
        self.max_retries = max_retries
        self._rate_limit = asyncio.Semaphore(rate_limit)
        self._headers: Dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "ChessComAPI-Python/2.0",
        }

    async def close(self) -> None:
        """Close the client session."""
        await self.session.close()

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        bytestream: bool = False,
    ) -> dict[str, Any] | bytes | None:
        """Make an API request to the specified endpoint with retry logic.

        :param endpoint: The API endpoint relative to the base URL.
        :type endpoint: str
        :param params: Optional parameters to be included in the request.
        :type params: Optional[Dict[str, Any]]
        :param bytestream: Flag to determine if the response should be treated as binary
            data. Default is False.
        :type bytestream: bool
        :return: The API response, either as a dictionary (if JSON)
            or as bytes (if bytestream).
        :rtype: Union[Dict[str, Any], bytes]
        """
        url = f"{self.BASE_URL}{endpoint}"
        retry_intervals = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]

        async with self._rate_limit:
            for attempt in range(self.max_retries):
                try:
                    return await self._attempt_request(url, params, bytestream)
                except (asyncio.TimeoutError, ChessComAPIError) as e:
                    await self._handle_retry_error(e, attempt, retry_intervals)
                except Exception as e:
                    await self._handle_unexpected_error(e, attempt, retry_intervals)
            return None

    async def _attempt_request(
        self, url: str, params: Optional[Dict[str, Any]], bytestream: bool
    ) -> Union[Dict[str, Any], bytes]:
        """Attempt a single API request."""
        async with self.session.get(
            url, params=params, headers=self._headers, timeout=self.timeout
        ) as response:
            if response.status == 200:
                return await self._handle_successful_response(response, bytestream)
            else:
                await self._handle_http_error(response)
                raise ChessComAPIError(
                    f"Request failed with status code {response.status}"
                )

    @staticmethod
    async def _handle_successful_response(
        response: aiohttp.ClientResponse, bytestream: bool
    ) -> Union[Dict[str, Any], bytes]:
        """Handle a successful HTTP response."""
        return (
            await response.json() if not bytestream else await response.content.read()
        )

    @staticmethod
    async def _handle_http_error(response: aiohttp.ClientResponse) -> None:
        """Handle various HTTP error responses."""
        if response.status == 429:
            raise ChessComAPIError("Rate limit hit")
        if response.status == 404:
            data = await response.json()
            raise NotFoundError(
                f"Resource not found: {data.get('message', 'Unknown error')}"
            )
        if response.status in (301, 304):
            raise RedirectError(f"Resource moved or not modified: {response.url}")
        if response.status == 410:
            raise GoneError(f"Resource is no longer available: {response.url}")
        if 500 <= response.status < 600:
            raise ChessComAPIError(f"Server error {response.status}")

    async def _handle_retry_error(
        self,
        error: Union[asyncio.TimeoutError, ChessComAPIError],
        attempt: int,
        retry_intervals: List[float],
    ) -> None:
        """Handle errors that should trigger a retry."""
        backoff_time = retry_intervals[min(attempt, len(retry_intervals) - 1)]
        if isinstance(error, asyncio.TimeoutError):
            print(f"Timeout. Retrying in {backoff_time:.2f} seconds...")
        else:
            print(f"{error}. Retrying in {backoff_time:.2f} seconds...")
        if attempt == self.max_retries - 1:
            raise ChessComAPIError("Max retries reached") from error
        if isinstance(error, (GoneError, NotFoundError)):
            raise error from error
        await asyncio.sleep(backoff_time)

    async def _handle_unexpected_error(
        self, error: Exception, attempt: int, retry_intervals: List[float]
    ) -> None:
        """Handle unexpected errors."""
        backoff_time = retry_intervals[min(attempt, len(retry_intervals) - 1)]
        print(f"Unexpected error: {error}. Retrying in {backoff_time:.2f} seconds...")
        if attempt == self.max_retries - 1:
            raise ChessComAPIError(
                f"Unexpected error after retries: {error}"
            ) from error
        await asyncio.sleep(backoff_time)

    # Player endpoints
    async def get_player(self, username: str) -> Player:
        """Retrieve player information by username.

        This method fetches player data from a remote service and returns a Player
        instance. It raises a ValueError if the username is empty.

        :param username: The username of the player to retrieve.
        :type username: str
        :return: A Player instance containing the player's information.
        :rtype: Player
        """
        if not username.strip():
            raise ValueError("Username cannot be empty")
        data = await self._make_request(f"/player/{username}")
        return Player.from_dict(data)

    async def get_titled_players(self, title: str) -> List[str]:
        """Get list of titled players."""
        data = await self._make_request(f"/titled/{title}")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /titled endpoint")
        if not isinstance(data["players"], list):
            raise ChessComAPIError("Unexpected response from /titled endpoint")
        return data["players"]

    async def get_player_stats(self, username: str) -> PlayerStats:
        """Get player statistics."""
        data = await self._make_request(f"/player/{username}/stats")
        return PlayerStats.from_dict(data)

    async def get_player_current_games(self, username: str) -> List[Game]:
        """Get player's current games."""
        data = await self._make_request(f"/player/{username}/games")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /player/games endpoint")
        return [Game.from_dict(game) for game in data["games"]]

    async def get_player_to_move_games(self, username: str) -> List[DailyGame]:
        """Get player's games where it's their turn."""
        data = await self._make_request(f"/player/{username}/games/to-move")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /player/games endpoint")
        return [DailyGame.from_dict(game) for game in data["games"]]

    async def get_player_game_archives(self, username: str) -> GameArchive:
        """Get URLs of player's game archives."""
        data = await self._make_request(f"/player/{username}/games/archives")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /player/games endpoint")
        return GameArchive.from_dict(
            data=data,
        )

    async def get_archived_games(
        self, username: str, year: int, month: str
    ) -> List[BoardGame]:
        """Get player's archived games for a specific month."""
        data = await self._make_request(f"/player/{username}/games/{year}/{month}")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /player/games endpoint")
        if not isinstance(data["games"], list):
            raise ChessComAPIError("Unexpected response from /player/games endpoint")
        return [BoardGame.from_dict(game) for game in data["games"]]

    async def download_archived_games_pgn(
        self, file_name: str, username: str, year: int, month: int
    ) -> None:
        """Download player's multi-game PGN for a specific month."""
        data = await self._make_request(
            f"/player/{username}/games/{year}/{month}/pgn", bytestream=True
        )
        if not isinstance(data, bytes):
            raise ChessComAPIError("Unexpected response from /player/games endpoint")
        with open(file_name, "wb") as f:
            f.write(data)

    async def get_game(
        self,
        username: str,
        game_id: Union[str, int],
        year: Optional[int] = None,
        month: Optional[str] = None,
    ) -> Optional[Game]:
        """Get game from player's archives via game ID/URL."""
        if isinstance(game_id, str):
            game_id = int(game_id.split("/")[-1])
        if not year or not month:
            logging.info("Depending on the amounts of games, this may take a while.")
        archive = await self.get_player_game_archives(username)
        return await archive.get_game(
            client=self, game_id=game_id, year=year, month=month
        )

    async def get_player_clubs(self, username: str) -> List[UserClub]:
        """Get player's clubs."""
        data = await self._make_request(f"/player/{username}/clubs")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /player/clubs endpoint")
        return [UserClub.from_dict(club) for club in data.get("clubs", [])]

    async def get_player_matches(self, username: str) -> PlayerMatches:
        """Get player's team matches."""
        data = await self._make_request(f"/player/{username}/matches")
        return PlayerMatches.from_dict(data)

    async def get_player_tournaments(self, username: str) -> PlayerTournaments:
        """Get player's tournaments."""
        data = await self._make_request(f"/player/{username}/tournaments")
        return PlayerTournaments.from_dict(data)

    # Club endpoints
    async def get_club(self, url_id: str) -> Club:
        """Get club details."""
        data = await self._make_request(f"/club/{url_id}")
        return Club.from_dict(data)

    async def get_club_members(self, url_id: str) -> Dict[str, List[str]]:
        """Get club members."""
        data = await self._make_request(f"/club/{url_id}/members")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /club/members endpoint")
        return data

    async def get_club_matches(self, url_id: str) -> ClubMatches:
        """Get club matches."""
        data = await self._make_request(f"/club/{url_id}/matches")
        return ClubMatches.from_dict(data)

    # Tournament endpoints
    async def get_tournament(self, url_id: str) -> Tournament:
        """Get tournament details."""
        data = await self._make_request(f"/tournament/{url_id}")
        return Tournament.from_dict(data)

    async def get_tournament_round(self, url_id: str, round_num: int) -> Round:
        """Get tournament round details."""
        data = await self._make_request(f"/tournament/{url_id}/{round_num}")
        return Round.from_dict(data)

    async def get_tournament_round_group(
        self, url_id: str, round_num: int, group_num: int
    ) -> Group:
        """Get tournament round group details."""
        data = await self._make_request(f"/tournament/{url_id}/{round_num}/{group_num}")
        return Group.from_dict(data)

    # Match endpoints
    async def get_match(self, match_id: int) -> Match:
        """Get team match details."""
        data = await self._make_request(f"/match/{match_id}")
        return Match.from_dict(data)

    async def get_match_board(self, match_id: int, board_num: int) -> Board:
        """Get team match board details."""
        data = await self._make_request(f"/match/{match_id}/{board_num}")
        return Board.from_dict(data)

    async def get_live_match(self, match_id: str) -> Match:
        """Get live team match details."""
        data = await self._make_request(f"/match/live/{match_id}")
        return Match.from_dict(data)

    async def get_live_match_board(self, match_id: int, board_num: int) -> Board:
        """Get live team match board details."""
        data = await self._make_request(f"/match/live/{match_id}/{board_num}")
        return Board.from_dict(data)

    # Country endpoints
    async def get_country(self, iso_code: str) -> Country:
        """Get country details."""
        data = await self._make_request(f"/country/{iso_code}")
        return Country.from_dict(data)

    async def get_country_players(self, iso_code: str) -> List[str]:
        """Get country players."""
        data = await self._make_request(f"/country/{iso_code}/players")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /country/players endpoint")
        if not isinstance(data["players"], list):
            raise ChessComAPIError("Unexpected response from /country/players endpoint")
        return data["players"]

    async def get_country_clubs(self, iso_code: str) -> CountryClubs:
        """Get country clubs."""
        data = await self._make_request(f"/country/{iso_code}/clubs")
        return CountryClubs.from_dict(data)

    # Puzzle endpoints
    async def get_daily_puzzle(self) -> DailyPuzzle:
        """Get daily puzzle."""
        data = await self._make_request("/puzzle")
        return DailyPuzzle.from_dict(data)

    async def get_random_puzzle(self) -> DailyPuzzle:
        """Get random puzzle."""
        data = await self._make_request("/puzzle/random")
        return DailyPuzzle.from_dict(data)

    # Miscellaneous endpoints
    async def get_streamers(self) -> List[Streamer]:
        """Get Chess.com streamers."""
        data = await self._make_request("/streamers")
        if not isinstance(data, dict):
            raise ChessComAPIError("Unexpected response from /streamers endpoint")
        return [Streamer.from_dict(s) for s in data.get("streamers", [])]

    async def get_leaderboards(self) -> Leaderboard:
        """Get Chess.com leaderboards."""
        data = await self._make_request("/leaderboards")
        return Leaderboard.from_dict(data)

    async def __aenter__(self) -> ChessComClient:
        """Enter the asynchronous context.

        This method is used to handle the initialization when entering an asynchronous
        context using the 'async with' statement. It returns the coroutine object itself
        for further operations within the context.

        :return: The coroutine object itself for further operations within the context.
        :rtype: Coroutine
        """
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        """Clean up the resources used by the asynchronous context manager.

        This method is called when exiting the async context. It ensures that any
        resources that were acquired by the context manager are properly released.

        :param exc_type: The exception type if an exception occurred, else None.
        :type exc_type: type | None
        :param exc_val: The exception instance if an exception occurred, else None.
        :type exc_val: BaseException | None
        :param exc_tb: The traceback if an exception occurred, else None.
        :type exc_tb: traceback | None
        :return: False if the exception should be propagated, else None.
        :rtype: bool | None
        """
        await self.close()
        if exc_type is not None:
            # Log or handle specific exceptions here if needed
            return False  # Propagate the exception
        return True  # Suppress exceptions if no exception occurred
