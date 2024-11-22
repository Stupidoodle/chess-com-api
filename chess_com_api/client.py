# chess_com_api/client.py

from __future__ import annotations

import aiohttp

from .exceptions import *
from .models import *


class ChessComClient:
    """Asynchronous client for the Chess.com API."""

    BASE_URL = "https://api.chess.com/pub"

    def __init__(
            self,
            session: Optional[aiohttp.ClientSession] = None,
            timeout: int = 30,
            max_retries: int = 3,
            rate_limit: int = 300
    ):
        """Initialize the Chess.com API client."""
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = session or aiohttp.ClientSession(timeout=self.timeout)
        self.max_retries = max_retries
        self._rate_limit = asyncio.Semaphore(rate_limit)
        self._headers = {
            "Accept": "application/json",
            "User-Agent": "ChessComAPI-Python/2.0"
        }

    async def close(self):
        """Close the client session."""
        await self.session.close()

    async def _make_request(
            self,
            endpoint: str,
            params: Optional[Dict] = None,
            bytestream: Optional[bool] = False,
    ) -> Dict | bytes:
        url = f"{self.BASE_URL}{endpoint}"
        retry_intervals = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]  # Adaptive retry intervals

        async with self._rate_limit:  # Enforce concurrency
            for attempt in range(self.max_retries):
                try:
                    async with self.session.get(
                            url, params=params, headers=self._headers, timeout=self.timeout
                    ) as response:
                        if response.status == 200:
                            return await response.json() if not bytestream else await response.content.read()

                        if response.status == 429:  # Rate limit hit
                            retry_time = retry_intervals[min(attempt, len(retry_intervals) - 1)]
                            print(f"Rate limit hit. Retrying in {retry_time:.2f} seconds...")
                            await asyncio.sleep(retry_time)
                            continue  # Retry after backoff

                        if response.status == 404:
                            data = await response.json()
                            raise NotFoundError(f"Resource not found: {data.get('message', 'Unknown error')}")

                        if response.status in (301, 304):
                            raise RedirectError(f"Resource moved or not modified: {url}")
                        if response.status == 410:
                            raise GoneError(f"Resource is no longer available: {url}")

                        if 500 <= response.status < 600:  # Server error
                            backoff_time = min(2 ** attempt, 10)
                            print(f"Server error {response.status}. Retrying in {backoff_time} seconds...")
                            await asyncio.sleep(backoff_time)
                            continue

                        raise ChessComAPIError(f"API request failed with status {response.status}")

                except NotFoundError:
                    # Do not retry for NotFoundError
                    raise

                except asyncio.TimeoutError:
                    backoff_time = min(2 ** attempt, 10)
                    print(f"Timeout. Retrying in {backoff_time} seconds...")
                    if attempt == self.max_retries - 1:
                        raise ChessComAPIError("Request timed out")
                    await asyncio.sleep(backoff_time)

                except Exception as e:
                    backoff_time = min(2 ** attempt, 10)
                    print(f"Unexpected error: {e}. Retrying in {backoff_time} seconds...")
                    if attempt == self.max_retries - 1:
                        raise ChessComAPIError(f"Request failed after retries: {e}")
                    await asyncio.sleep(backoff_time)

    # Player endpoints
    async def get_player(self, username: str) -> Player:
        if not username.strip():
            raise ValueError("Username cannot be empty")
        data = await self._make_request(f"/player/{username}")
        return Player.from_dict(data)

    async def get_titled_players(self, title: str) -> List[str]:
        """Get list of titled players."""
        data = await self._make_request(f"/titled/{title}")
        return data["players"]

    async def get_player_stats(self, username: str) -> PlayerStats:
        """Get player statistics."""
        data = await self._make_request(f"/player/{username}/stats")
        return PlayerStats.from_dict(data)

    async def get_player_current_games(self, username: str) -> List[Game]:
        """Get player's current games."""
        data = await self._make_request(f"/player/{username}/games")
        return [Game.from_dict(game) for game in data["games"]]

    async def get_player_to_move_games(self, username: str) -> List[DailyGame]:
        """Get player's games where it's their turn."""
        data = await self._make_request(f"/player/{username}/games/to-move")
        return [DailyGame.from_dict(game) for game in data["games"]]

    async def get_player_game_archives(self, username: str) -> List[str]:
        """Get URLs of player's game archives."""
        data = await self._make_request(f"/player/{username}/games/archives")
        return data["archives"]

    async def get_archived_games(self, username: str, year: int, month: int) -> List[Game]:
        """Get player's archived games for a specific month."""
        data = await self._make_request(f"/player/{username}/games/{year}/{month}")
        return [Game.from_dict(game) for game in data["games"]]

    async def download_archived_games_pgn(self, file_name: str, username: str, year: int, month: int) -> None:
        """Download player's multi-game PGN for a specific month."""
        data = await self._make_request(f"/player/{username}/games/{year}/{month}/pgn", bytestream=True)
        with open(file_name, "wb") as f:
            f.write(data)

    async def get_player_clubs(self, username: str) -> List[UserClub]:
        """Get player's clubs."""
        data = await self._make_request(f"/player/{username}/clubs")
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

    # TODO: Implement ClubMembers class
    async def get_club_members(self, url_id: str) -> Dict[str, List[str]]:
        """Get club members."""
        return await self._make_request(f"/club/{url_id}/members")

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

    async def get_tournament_round_group(self, url_id: str, round_num: int, group_num: int) -> Group:
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

    async def get_live_match_board(self, match_id: str, board_num: int) -> Board:
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
        return [Streamer.from_dict(s) for s in data.get("streamers", [])]

    async def get_leaderboards(self) -> Leaderboard:
        """Get Chess.com leaderboards."""
        data = await self._make_request("/leaderboards")
        return Leaderboard.from_dict(data)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
