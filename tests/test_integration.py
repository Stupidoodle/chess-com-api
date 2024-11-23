"""Integration tests for the Chess.com API client."""

import asyncio
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock

import aiohttp
import pytest

from chess_com_api.client import ChessComClient
from chess_com_api.exceptions import ChessComAPIError, NotFoundError, RateLimitError
from chess_com_api.models import ClubMatches, Country


@pytest.fixture
async def client() -> AsyncGenerator[ChessComClient, None]:
    """Create and yield an asynchronous ChessComClient fixture.

    This fixture is used to manage the lifecycle of a ChessComClient instance,
    ensuring it is properly initialized and closed when tests are executed.

    :return: An instance of ChessComClient.
    :rtype: ChessComClient
    """
    async with ChessComClient() as client:
        yield client


@pytest.mark.asyncio
async def test_client_fixture(client: ChessComClient) -> None:
    """Test the client fixture for proper instantiation.

    This test verifies that the client fixture is correctly set up and returns an
    instance of ChessComClient.

    :param client: The client fixture to be tested.
    :type client: ChessComClient
    :return: None
    """
    assert client is not None
    assert isinstance(
        client, ChessComClient
    ), "Fixture did not yield a ChessComClient instance"


@pytest.mark.asyncio
class TestPlayerEndpoints:
    """Test endpoints related to players.

    This class contains async test methods to verify the functionality
    of various player-related API endpoints.

    :ivar client: The API client to interact with player endpoints.
    :type client: APIClient
    """

    async def test_get_player(self, client: ChessComClient) -> None:
        """Test getting player profile."""
        player = await client.get_player("hikaru")
        assert player.username == "hikaru"
        assert player.title == "GM"
        await player.fetch_country(client=client)
        assert player.country == Country(code="US", name="United States")

    async def test_get_player_stats(self, client: ChessComClient) -> None:
        """Test getting player statistics."""
        stats = await client.get_player_stats("hikaru")
        assert stats.chess_blitz is not None
        assert "rating" in stats.chess_blitz["last"]

    async def test_player_games(self, client: ChessComClient) -> None:
        """Test getting player games."""
        games = await client.get_player_current_games("erik")
        for game in games:
            assert game.url.startswith("https://")
            assert game.pgn is not None


@pytest.mark.asyncio
class TestClubEndpoints:
    """Class for testing endpoints related to clubs using asynchronous calls.

    This class contains methods to test various endpoints related to clubs. Each test
    method performs an asynchronous call to the corresponding club endpoint and asserts
    the validity of the fetched data.

    :ivar attribute1: Description of attribute1.
    :type attribute1: type
    :ivar attribute2: Description of attribute2.
    :type attribute2: type
    """

    async def test_get_club(self, client: ChessComClient) -> None:
        """Test getting club details."""
        club = await client.get_club("chess-com-developer-community")
        assert club.name is not None
        assert club.members_count > 0

    async def test_club_members(self, client: ChessComClient) -> None:
        """Test getting club members."""
        members = await client.get_club_members("team-usa")
        assert "weekly" in members
        assert "monthly" in members
        assert "all_time" in members

    async def test_club_matches(self, client: ChessComClient) -> None:
        """Test getting club matches."""
        matches = await client.get_club_matches("chess-com-developer-community")
        assert isinstance(matches, ClubMatches)
        assert len(matches.finished) > 0
        await matches.finished[0].fetch_match(client=client)
        assert matches.finished[0].match.url.startswith("https://")
        await matches.finished[0].fetch_opponent(client=client)
        assert matches.finished[0].opponent.name is not None
        if len(matches.in_progress) > 1:
            await matches.in_progress[0].fetch_match(client=client)
            assert matches.in_progress[0].match.url.startswith("https://")
            await matches.in_progress[0].fetch_opponent(client=client)
            assert matches.in_progress[0].opponent.name is not None
        if len(matches.registered) > 1:
            await matches.registered[1].fetch_match(client=client)
            assert matches.registered[1].match.url.startswith("https://")
            await matches.registered[1].fetch_opponent(client=client)
            assert matches.registered[1].opponent.name is not None


@pytest.mark.asyncio
class TestCountryEndpoints:
    """Test the endpoints for country-related functionalities in the API.

    This test class includes asynchronous methods to ensure that the country
    endpoints in the API are functioning correctly. It validates the retrieval of
    country details and the list of players from a specified country using the
    provided API client.

    """

    async def test_get_country(self, client: ChessComClient) -> None:
        """Test getting country details."""
        country = await client.get_country("US")
        assert country.name == "United States"
        assert country.code == "US"

    async def test_country_players(self, client: ChessComClient) -> None:
        """Test getting country players."""
        players = await client.get_country_players("US")
        assert isinstance(players, list)
        assert len(players) > 0


@pytest.mark.asyncio
class TestPuzzleEndpoints:
    """Test suite for puzzle-related endpoints.

    A set of asynchronous test methods to ensure that puzzle endpoints are
    functioning as expected.

    :ivar client: The test client to interact with puzzle endpoints.
    :type client: Any
    """

    async def test_daily_puzzle(self, client: ChessComClient) -> None:
        """Test getting daily puzzle."""
        puzzle = await client.get_daily_puzzle()
        assert puzzle.title is not None
        assert puzzle.pgn is not None
        assert puzzle.fen is not None

    async def test_random_puzzle(self, client: ChessComClient) -> None:
        """Test getting random puzzle."""
        puzzle = await client.get_random_puzzle()
        assert puzzle.title is not None
        assert puzzle.pgn is not None


@pytest.mark.asyncio
class TestStreamersEndpoint:
    """Contains test cases for the streamers endpoint.

    This class uses pytest to test the functionality of the streamers endpoint. It
    verifies that the `get_streamers` method retrieves streamers correctly.

    :ivar client: The HTTP client used to interact with the API.
    :type client: HttpClient
    """

    async def test_get_streamers(self, client: ChessComClient) -> None:
        """Test getting Chess.com streamers."""
        streamers = await client.get_streamers()
        for streamer in streamers:
            assert streamer.username is not None
            assert streamer.twitch_url is not None


@pytest.mark.asyncio
class TestLeaderboardsEndpoint:
    """Class for testing the Leaderboards endpoint.

    This class contains asynchronous test methods to verify the functionality
    of the Leaderboards endpoint. It ensures that the endpoint returns valid data
    for daily, live blitz, and tactics leaderboards.

    :ivar client: The client fixture used for making requests to the endpoint.
    :type client: TestClient
    """

    async def test_get_leaderboards(self, client: ChessComClient) -> None:
        """Test getting leaderboards."""
        leaderboards = await client.get_leaderboards()
        assert len(leaderboards.daily) > 0
        assert len(leaderboards.live_blitz) > 0
        assert len(leaderboards.tactics) > 0


@pytest.mark.asyncio
class TestErrorHandling:
    """Test suite for error handling in client operations.

    This class contains asynchronous tests for handling various errors in client
    operations. It includes tests for 404 errors, rate limit errors, and input
    validation errors.
    """

    async def test_not_found(self, client: ChessComClient) -> None:
        """Test 404 error handling."""
        with pytest.raises(NotFoundError):
            await client.get_player("thisisnotarealuser12345")

    async def test_rate_limit(self, client: ChessComClient, monkeypatch: Any) -> None:
        """Test rate limit handling."""
        mock_request = AsyncMock(side_effect=RateLimitError("Rate limit exceeded"))
        monkeypatch.setattr(client, "_make_request", mock_request)

        tasks = [client.get_player("hikaru") for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert any(isinstance(r, RateLimitError) for r in results)

    async def test_invalid_input(self, client: ChessComClient) -> None:
        """Test input validation."""
        with pytest.raises(ValueError):
            await client.get_player("")


@pytest.mark.asyncio
class TestRetryMechanism:
    """Test the retry mechanism of the client.

    This class contains tests that verify the client's ability to successfully
    retry requests upon failure, as well as handling cases where the maximum
    number of retries is exceeded.
    """

    async def test_retry_success(self, client: ChessComClient, mocker: Any) -> None:
        """Test successful retry after failure."""
        # Mock the `get` method to fail once and succeed on the second attempt
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value.status = 200
        mock_response.__aenter__.return_value.json = AsyncMock(
            return_value={
                "avatar": "https://images.chesscomfiles.com/uploads/v1/user/15448422.88c010c1.200x200o.3c5619f5441e.png",
                "player_id": 15448422,
                "@id": "https://api.chess.com/pub/player/hikaru",
                "url": "https://www.chess.com/member/Hikaru",
                "name": "Hikaru Nakamura",
                "username": "hikaru",
                "title": "GM",
                "followers": 1225729,
                "country": "https://api.chess.com/pub/country/US",
                "location": "Florida",
                "last_online": 1732135306,
                "joined": 1389043258,
                "status": "premium",
                "is_streamer": True,
                "twitch_url": "https://twitch.tv/gmhikaru",
                "verified": False,
                "league": "Legend",
                "streaming_platforms": [
                    {"type": "twitch", "channel_url": "https://twitch.tv/gmhikaru"}
                ],
            }
        )

        mocker.patch.object(
            client.session, "get", side_effect=[aiohttp.ClientError(), mock_response]
        )

        result = await client.get_player("hikaru")
        assert result.username == "hikaru"

    async def test_max_retries_exceeded(
        self, client: ChessComClient, mocker: Any
    ) -> None:
        """Test max retries exceeded."""
        mocker.patch.object(client.session, "get", side_effect=aiohttp.ClientError())

        with pytest.raises(ChessComAPIError):
            await client.get_player("hikaru")


@pytest.mark.asyncio
class TestContextManager:
    """Represents test cases for the ChessComClient context manager.

    Provides functionality to test that the ChessComClient context manager properly
    initializes and provides access to client methods within an asynchronous context.
    """

    async def test_context_manager(self) -> None:
        """Test client context manager."""
        async with ChessComClient() as client:
            player = await client.get_player("hikaru")
            assert player is not None
