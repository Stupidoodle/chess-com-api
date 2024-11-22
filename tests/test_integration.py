# tests/test_integration.py

import asyncio
from unittest.mock import AsyncMock

import aiohttp
import pytest

from chess_com_api.client import ChessComClient
from chess_com_api.exceptions import *
from chess_com_api.models import ClubMatches, Country


@pytest.fixture
async def client():
    async with ChessComClient() as client:
        yield client


@pytest.mark.asyncio
async def test_client_fixture(client):
    assert client is not None
    assert isinstance(client, ChessComClient), "Fixture did not yield a ChessComClient instance"


@pytest.mark.asyncio
class TestPlayerEndpoints:
    async def test_get_player(self, client):
        """Test getting player profile."""
        player = await client.get_player("hikaru")
        assert player.username == "hikaru"
        assert player.title == "GM"
        await player.fetch_country(client=client)
        assert player.country == Country(code="US", name="United States")

    async def test_get_player_stats(self, client):
        """Test getting player statistics."""
        stats = await client.get_player_stats("hikaru")
        assert stats.chess_blitz is not None
        assert "rating" in stats.chess_blitz["last"]

    async def test_player_games(self, client):
        """Test getting player games."""
        games = await client.get_player_current_games("erik")
        for game in games:
            assert game.url.startswith("https://")
            assert game.pgn is not None


@pytest.mark.asyncio
class TestClubEndpoints:
    async def test_get_club(self, client):
        """Test getting club details."""
        club = await client.get_club("chess-com-developer-community")
        assert club.name is not None
        assert club.members_count > 0

    async def test_club_members(self, client):
        """Test getting club members."""
        members = await client.get_club_members("chess-com-developer-community")
        assert "weekly" in members
        assert "monthly" in members
        assert "all_time" in members

    async def test_club_matches(self, client):
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
    async def test_get_country(self, client):
        """Test getting country details."""
        country = await client.get_country("US")
        assert country.name == "United States"
        assert country.code == "US"

    async def test_country_players(self, client):
        """Test getting country players."""
        players = await client.get_country_players("US")
        assert isinstance(players, list)
        assert len(players) > 0


@pytest.mark.asyncio
class TestPuzzleEndpoints:
    async def test_daily_puzzle(self, client):
        """Test getting daily puzzle."""
        puzzle = await client.get_daily_puzzle()
        assert puzzle.title is not None
        assert puzzle.pgn is not None
        assert puzzle.fen is not None

    async def test_random_puzzle(self, client):
        """Test getting random puzzle."""
        puzzle = await client.get_random_puzzle()
        assert puzzle.title is not None
        assert puzzle.pgn is not None


@pytest.mark.asyncio
class TestStreamersEndpoint:
    async def test_get_streamers(self, client):
        """Test getting Chess.com streamers."""
        streamers = await client.get_streamers()
        for streamer in streamers:
            assert streamer.username is not None
            assert streamer.twitch_url is not None


@pytest.mark.asyncio
class TestLeaderboardsEndpoint:
    async def test_get_leaderboards(self, client):
        """Test getting leaderboards."""
        leaderboards = await client.get_leaderboards()
        assert len(leaderboards.daily) > 0
        assert len(leaderboards.live_blitz) > 0
        assert len(leaderboards.tactics) > 0


@pytest.mark.asyncio
class TestErrorHandling:
    async def test_not_found(self, client):
        """Test 404 error handling."""
        with pytest.raises(NotFoundError):
            await client.get_player("thisisnotarealuser12345")

    @pytest.mark.asyncio
    async def test_rate_limit(self, client, monkeypatch):
        """Test rate limit handling."""
        mock_request = AsyncMock(side_effect=RateLimitError("Rate limit exceeded"))
        monkeypatch.setattr(client, "_make_request", mock_request)

        tasks = [client.get_player("hikaru") for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert any(isinstance(r, RateLimitError) for r in results)

    async def test_invalid_input(self, client):
        """Test input validation."""
        with pytest.raises(ValueError):
            await client.get_player("")


@pytest.mark.asyncio
class TestRetryMechanism:
    async def test_retry_success(self, client, mocker):
        """Test successful retry after failure."""
        # Mock the `get` method to fail once and succeed on the second attempt
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value.status = 200
        mock_response.__aenter__.return_value.json = AsyncMock(return_value={
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
                {
                    "type": "twitch",
                    "channel_url": "https://twitch.tv/gmhikaru"
                }
            ]
        })

        mocker.patch.object(client.session, "get", side_effect=[
            aiohttp.ClientError(),
            mock_response
        ])

        result = await client.get_player("hikaru")
        assert result.username == "hikaru"

    async def test_max_retries_exceeded(self, client, mocker):
        """Test max retries exceeded."""
        mocker.patch.object(client.session, 'get',
                            side_effect=aiohttp.ClientError())

        with pytest.raises(ChessComAPIError):
            await client.get_player("hikaru")


@pytest.mark.asyncio
class TestContextManager:
    async def test_context_manager(self):
        """Test client context manager."""
        async with ChessComClient() as client:
            player = await client.get_player("hikaru")
            assert player is not None
