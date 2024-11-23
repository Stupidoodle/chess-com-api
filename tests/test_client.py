"""Tests for the Chess.com API client."""

import asyncio
import hashlib
import os
from datetime import datetime
from typing import AsyncGenerator

import pytest

from chess_com_api.client import ChessComClient
from chess_com_api.exceptions import NotFoundError
from chess_com_api.models import (
    Black,
    Board,
    BoardGame,
    Club,
    Game,
    GameArchive,
    Group,
    PlayerMatches,
    PlayerTournaments,
    Round,
    White,
)


def get_file_hash(file_path: str, hash_algorithm: str = "sha256") -> str:
    """Compute the hash of a file with normalized line endings."""
    # Create a hash object
    hash_func = getattr(hashlib, hash_algorithm)()

    # Read the file in binary mode
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):  # Read in 8KB chunks
            # Normalize line endings
            chunk = chunk.replace(b"\r\n", b"\n")  # Convert CRLF to LF
            hash_func.update(chunk)

    return hash_func.hexdigest()  # type: ignore


@pytest.fixture
async def client() -> AsyncGenerator[ChessComClient, None]:
    """Create test client instance."""
    async with ChessComClient(max_retries=50) as client:
        yield client


@pytest.mark.asyncio
async def test_get_player(client: ChessComClient) -> None:
    """Test getting player profile."""
    player = await client.get_player("hikaru")
    assert player.username == "hikaru"
    assert player.title == "GM"
    assert isinstance(player.joined, datetime)


@pytest.mark.asyncio
async def test_get_titled_players(client: ChessComClient) -> None:
    """Test getting player profiles with title."""
    players = await client.get_titled_players("GM")
    assert isinstance(players, list)
    assert "hikaru" in players


@pytest.mark.asyncio
async def test_get_player_to_move_games(client: ChessComClient) -> None:
    """Test getting player's to move games."""
    games = await client.get_player_to_move_games("erik")
    assert isinstance(games, list)
    assert games[0].url.startswith("https://")


@pytest.mark.asyncio
async def test_get_player_stats(client: ChessComClient) -> None:
    """Test getting player statistics."""
    stats = await client.get_player_stats("hikaru")
    assert stats.chess_blitz is not None
    assert stats.chess_rapid is not None


@pytest.mark.asyncio
async def test_download_monthly_pgn(client: ChessComClient) -> None:
    """Test downloading monthly PGN."""
    await client.download_archived_games_pgn("test_file.pgn", "erik", 2009, 10)
    print(get_file_hash("test_file.pgn"))
    assert (
        get_file_hash("test_file.pgn")
        == "436c21bd6fdd07844e0227754190a207a64cf908b6508fffd7f4a52354949377"
    )
    os.remove("test_file.pgn")


@pytest.mark.asyncio
async def test_get_player_matches(client: ChessComClient) -> None:
    """Test getting player matches."""
    matches = await client.get_player_matches("erik")
    assert isinstance(matches, PlayerMatches)
    assert len(matches.finished) > 0
    assert len(matches.in_progress) > 0
    await matches.finished[0].fetch_club(client=client)
    await matches.in_progress[0].fetch_club(client=client)
    assert matches.finished[0].club.name is not None
    assert matches.in_progress[0].club.name is not None
    await matches.finished[0].fetch_board(client=client)
    await matches.in_progress[0].fetch_board(client=client)
    assert isinstance(matches.finished[0].board, Board)
    assert isinstance(matches.in_progress[0].board, Board)
    assert len(matches.finished[0].board.games) > 0
    assert len(matches.in_progress[0].board.games) > 0
    assert isinstance(matches.finished[0].board.games[0], BoardGame)
    assert isinstance(matches.in_progress[0].board.games[0], BoardGame)
    assert isinstance(matches.finished[0].board.games[0].white, White)
    assert isinstance(matches.finished[0].board.games[0].black, Black)
    assert isinstance(matches.in_progress[0].board.games[0].white, White)
    assert isinstance(matches.in_progress[0].board.games[0].black, Black)
    assert matches.finished[0].board.games[0].white.username == "erik"
    assert matches.finished[0].board.games[0].black.username == "Remchess69"
    assert matches.in_progress[0].board.games[0].white.username == "erik"
    assert matches.in_progress[0].board.games[0].black.username == "AdamKytlica"
    if len(matches.registered) > 1:
        await matches.registered[1].fetch_club(client=client)
        assert matches.registered[1].club.name is not None


@pytest.mark.asyncio
async def test_get_player_tournaments(client: ChessComClient) -> None:
    """Test getting player tournaments."""
    tournaments = await client.get_player_tournaments("erik")
    assert isinstance(tournaments, PlayerTournaments)
    assert len(tournaments.finished) > 0
    assert len(tournaments.in_progress) > 0
    await tournaments.finished[0].fetch_tournament(client=client)
    await tournaments.in_progress[0].fetch_tournament(client=client)
    assert tournaments.finished[0].tournament.name is not None
    assert tournaments.in_progress[0].tournament.name is not None
    if len(tournaments.registered) > 1:
        await tournaments.registered[1].fetch_tournament(client=client)
        assert tournaments.registered[1].tournament.name is not None


@pytest.mark.asyncio
async def test_get_player_current_games(client: ChessComClient) -> None:
    """Test getting player's current games."""
    games = await client.get_player_current_games("erik")
    assert isinstance(games, list)
    if games:
        assert all(hasattr(g, "url") for g in games)


@pytest.mark.asyncio
async def test_get_player_game_archives(client: ChessComClient) -> None:
    """Test getting player's game archives."""
    archives = await client.get_player_game_archives("hikaru")
    assert isinstance(archives, GameArchive)
    assert len(archives.archive_urls) > 0


@pytest.mark.asyncio
class TestPlayerGameArchive:
    """Test player game archive."""

    async def test_get_game(self, client: ChessComClient) -> None:
        """Test getting game from URL."""
        game = await client.get_game(
            username="erik", game_id="https://www.chess.com/game/live/1687076816"
        )
        assert isinstance(game, Game)
        assert game.url == "https://www.chess.com/game/live/1687076816"

    async def test_get_game_with_month(self, client: ChessComClient) -> None:
        """Test getting game from URL with month."""
        game = await client.get_game(
            username="erik",
            game_id="1687076816",
            month="08",
        )
        assert isinstance(game, Game)
        assert game.url == "https://www.chess.com/game/live/1687076816"

    async def test_get_game_with_year(self, client: ChessComClient) -> None:
        """Test getting game from URL with year."""
        game = await client.get_game(
            username="erik",
            game_id="1687076816",
            year=2016,
        )
        assert isinstance(game, Game)
        assert game.url == "https://www.chess.com/game/live/1687076816"

    async def test_get_game_with_month_and_year(self, client: ChessComClient) -> None:
        """Test getting game from URL with month and year."""
        game = await client.get_game(
            username="erik",
            game_id="1687076816",
            month="08",
            year=2016,
        )
        assert isinstance(game, Game)
        assert game.url == "https://www.chess.com/game/live/1687076816"

    async def test_download_game_pgn(self, client: ChessComClient) -> None:
        """Test downloading game PGN."""
        await client.download_game_pgn(
            username="erik",
            game_id="https://www.chess.com/game/live/116396973087",
            file_name="test_pgn.pgn",
        )
        assert (
            get_file_hash("test_pgn.pgn")
            == "73f3340fa79614c3688b80aad7cec710896680f1da213f5d057d4898ec1f5dc4"
        )
        os.remove("test_pgn.pgn")

    async def test_download_game_pgn_with_month(self, client: ChessComClient) -> None:
        """Test downloading game PGN with month."""
        await client.download_game_pgn(
            username="erik",
            game_id="116396973087",
            file_name="test_pgn.pgn",
            month="08",
        )
        assert (
            get_file_hash("test_pgn.pgn")
            == "73f3340fa79614c3688b80aad7cec710896680f1da213f5d057d4898ec1f5dc4"
        )
        os.remove("test_pgn.pgn")

    async def test_download_game_pgn_with_year(self, client: ChessComClient) -> None:
        """Test downloading game PGN with year."""
        await client.download_game_pgn(
            username="erik",
            game_id="116396973087",
            file_name="test_pgn.pgn",
            year=2024,
        )
        assert (
            get_file_hash("test_pgn.pgn")
            == "73f3340fa79614c3688b80aad7cec710896680f1da213f5d057d4898ec1f5dc4"
        )
        os.remove("test_pgn.pgn")

    async def test_download_game_pgn_with_month_and_year(
        self, client: ChessComClient
    ) -> None:
        """Test downloading game PGN with month and year."""
        await client.download_game_pgn(
            username="erik",
            game_id="116396973087",
            file_name="test_pgn.pgn",
            month="08",
            year=2024,
        )
        assert (
            get_file_hash("test_pgn.pgn")
            == "73f3340fa79614c3688b80aad7cec710896680f1da213f5d057d4898ec1f5dc4"
        )
        os.remove("test_pgn.pgn")


@pytest.mark.asyncio
async def test_get_archived_games(client: ChessComClient) -> None:
    """Test getting player's archived games."""
    games = await client.get_archived_games("hikaru", 2023, "12")
    assert isinstance(games, list)
    if games:
        assert all(hasattr(g, "url") for g in games)


@pytest.mark.asyncio
async def test_get_player_clubs(client: ChessComClient) -> None:
    """Test getting player's clubs."""
    clubs = await client.get_player_clubs("erik")
    assert isinstance(clubs, list)
    if clubs:
        assert all(hasattr(c, "name") for c in clubs)


@pytest.mark.asyncio
async def test_get_club(client: ChessComClient) -> None:
    """Test getting club details."""
    club = await client.get_club("chess-com-developer-community")
    assert club.name is not None
    assert isinstance(club.members_count, int)


@pytest.mark.asyncio
async def test_get_tournament(client: ChessComClient) -> None:
    """Test getting tournament details."""
    tournament = await client.get_tournament("-33rd-chesscom-quick-knockouts-1401-1600")
    assert tournament.name is not None
    assert tournament.status in ["finished", "in_progress", "registration"]
    await tournament.fetch_rounds(client=client)
    assert len(tournament.rounds) > 0
    assert isinstance(tournament.rounds[0], Round)


@pytest.mark.asyncio
async def test_tournament_round(client: ChessComClient) -> None:
    """Test getting tournament round details."""
    tournament_id = "-33rd-chesscom-quick-knockouts-1401-1600"
    tournament_round = await client.get_tournament_round(tournament_id, 1)
    assert len(tournament_round.players) > 0
    assert len(tournament_round.group_urls) > 0
    await tournament_round.fetch_groups(client=client)
    assert len(tournament_round.groups) > 0
    assert isinstance(tournament_round.groups[0], Group)


@pytest.mark.asyncio
async def test_tournament_round_group(client: ChessComClient) -> None:
    """Test getting tournament round group details."""
    tournament_id = "-33rd-chesscom-quick-knockouts-1401-1600"
    tournament_round_group = await client.get_tournament_round_group(
        tournament_id, 1, 1
    )
    assert len(tournament_round_group.games) > 0
    assert isinstance(tournament_round_group.games[0], Game)


@pytest.mark.asyncio
async def test_get_match(client: ChessComClient) -> None:
    """Test getting match details."""
    match = await client.get_match(12803)
    assert match.url.startswith("https://")
    await match.fetch_boards(client=client)
    assert isinstance(match.boards, list)
    assert len(match.boards) > 0
    assert isinstance(match.boards[0], Board)
    assert len(match.boards[0].games) > 0
    assert isinstance(match.boards[0].games[0], Game)
    assert isinstance(match.boards[0].games[0].white, White)
    assert isinstance(match.boards[0].games[0].black, Black)
    await match.boards[0].games[0].white.fetch_user(client=client)
    await match.boards[0].games[0].black.fetch_user(client=client)
    assert (
        match.boards[0].games[0].white.username == "sorinel"
        and match.boards[0].games[0].black.username == "Kllr"
    )
    assert match.boards[0].games[0].white.user == await client.get_player("sorinel")
    assert match.boards[0].games[0].black.user == await client.get_player("Kllr")
    await match.boards[0].games[0].fetch_white(client=client)
    await match.boards[0].games[0].fetch_black(client=client)
    assert match.boards[0].games[0].white.user == await client.get_player("sorinel")
    assert match.boards[0].games[0].black.user == await client.get_player("Kllr")


@pytest.mark.asyncio
async def test_get_match_board(client: ChessComClient) -> None:
    """Test getting match board."""
    board = await client.get_match_board(12803, 1)
    assert len(board.games) > 0
    assert isinstance(board.games[0], BoardGame)
    assert isinstance(board.games[0].white, White)
    assert isinstance(board.games[0].black, Black)
    await board.games[0].white.fetch_user(client=client)
    await board.games[0].black.fetch_user(client=client)
    assert (
        board.games[0].white.username == "sorinel"
        and board.games[0].black.username == "Kllr"
    )
    assert board.games[0].white.user == await client.get_player("sorinel")
    assert board.games[0].black.user == await client.get_player("Kllr")
    await board.games[0].fetch_white(client=client)
    await board.games[0].fetch_black(client=client)
    assert board.games[0].white.user == await client.get_player("sorinel")
    assert board.games[0].black.user == await client.get_player("Kllr")


@pytest.mark.asyncio
async def test_get_live_match(client: ChessComClient) -> None:
    """Test getting live match details."""
    match = await client.get_live_match("5833")
    assert match.url.startswith("https://")


@pytest.mark.asyncio
async def test_get_live_match_board(client: ChessComClient) -> None:
    """Test getting live match board."""
    board = await client.get_live_match_board(5833, 5)
    assert len(board.games) > 0
    assert isinstance(board.games[0], Game)


@pytest.mark.asyncio
async def test_get_country(client: ChessComClient) -> None:
    """Test getting country details."""
    country = await client.get_country("US")
    assert country.name == "United States"
    assert country.code == "US"


@pytest.mark.asyncio
async def test_get_country_clubs(client: ChessComClient) -> None:
    """Test getting country clubs."""
    country_clubs = await client.get_country_clubs("TV")
    await country_clubs.fetch_clubs(client=client)
    assert len(country_clubs.clubs) > 0
    assert isinstance(country_clubs.clubs[0], Club)


@pytest.mark.asyncio
async def test_get_daily_puzzle(client: ChessComClient) -> None:
    """Test getting daily puzzle."""
    puzzle = await client.get_daily_puzzle()
    assert puzzle.title is not None
    assert puzzle.pgn is not None
    assert puzzle.fen is not None


@pytest.mark.asyncio
async def test_get_streamers(client: ChessComClient) -> None:
    """Test getting Chess.com streamers."""
    streamers = await client.get_streamers()
    assert isinstance(streamers, list)
    if streamers:
        assert all(hasattr(s, "username") for s in streamers)


@pytest.mark.asyncio
async def test_get_leaderboards(client: ChessComClient) -> None:
    """Test getting leaderboards."""
    leaderboards = await client.get_leaderboards()
    assert hasattr(leaderboards, "daily")
    assert hasattr(leaderboards, "live_blitz")
    assert hasattr(leaderboards, "tactics")


@pytest.mark.asyncio
async def test_error_handling(client: ChessComClient) -> None:
    """Test error handling."""
    with pytest.raises(NotFoundError):
        await client.get_player("thisisnotarealuser12345")

    with pytest.raises(ValueError):
        await client.get_player("")


@pytest.mark.asyncio
async def test_rate_limiting(client: ChessComClient) -> None:
    """Test rate limiting functionality."""
    # Make multiple concurrent requests
    tasks = [client.get_player("hikaru") for _ in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check that all requests succeeded
    assert all(not isinstance(r, Exception) for r in results)


def test_client_context_manager() -> None:
    """Test client context manager functionality."""

    async def run() -> None:
        async with ChessComClient() as client:
            player = await client.get_player("hikaru")
            assert player is not None

    asyncio.run(run())
