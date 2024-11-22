# tests/test_client.py

import asyncio
import hashlib
import os
from datetime import datetime

import pytest

from chess_com_api.client import ChessComClient
from chess_com_api.exceptions import *
from chess_com_api.models import PlayerMatches, PlayerTournaments, Game, Club, BoardGame, Round, Group


def get_file_hash(file_path, hash_algorithm="sha256"):
    """
    Computes the hash of a file.

    Args:
        file_path (str): Path to the file.
        hash_algorithm (str): Hash algorithm to use ('md5', 'sha1', 'sha256', etc.).

    Returns:
        str: Hexadecimal hash string of the file.
    """
    # Create a hash object
    hash_func = getattr(hashlib, hash_algorithm)()

    # Read the file in chunks to handle large files
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):  # Read in 8KB chunks
            hash_func.update(chunk)

    return hash_func.hexdigest()


@pytest.fixture
async def client():
    """Create test client instance."""
    async with ChessComClient(max_retries=50) as client:
        yield client


@pytest.mark.asyncio
async def test_get_player(client):
    """Test getting player profile."""
    player = await client.get_player("hikaru")
    assert player.username == "hikaru"
    assert player.title == "GM"
    assert isinstance(player.joined, datetime)


@pytest.mark.asyncio
async def test_get_titled_players(client):
    """Test getting player profiles with title."""
    players = await client.get_titled_players("GM")
    assert isinstance(players, list)
    assert "hikaru" in players


@pytest.mark.asyncio
async def test_get_player_to_move_games(client):
    """Test getting player's to move games."""
    games = await client.get_player_to_move_games("erik")
    assert isinstance(games, list)
    assert games[0].url.startswith("https://")


@pytest.mark.asyncio
async def test_get_player_stats(client):
    """Test getting player statistics."""
    stats = await client.get_player_stats("hikaru")
    assert stats.chess_blitz is not None
    assert stats.chess_rapid is not None


@pytest.mark.asyncio
async def test_download_monthly_pgn(client):
    """Test downloading monthly PGN."""
    await client.download_archived_games_pgn("test_file.pgn", "erik", 2009, 10)
    print(get_file_hash("test_file.pgn"))
    assert get_file_hash("test_file.pgn") == "436c21bd6fdd07844e0227754190a207a64cf908b6508fffd7f4a52354949377"
    os.remove("test_file.pgn")


@pytest.mark.asyncio
async def test_get_player_matches(client):
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
    assert matches.finished[0].board.games[0].white.username == "erik"
    assert matches.finished[0].board.games[0].black.username == "Remchess69"
    assert matches.in_progress[0].board.games[0].white.username == "erik"
    assert matches.in_progress[0].board.games[0].black.username == "AdamKytlica"
    if len(matches.registered) > 1:
        await matches.registered[1].fetch_club(client=client)
        assert matches.registered[1].club.name is not None


@pytest.mark.asyncio
async def test_get_player_tournaments(client):
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
async def test_get_player_current_games(client):
    """Test getting player's current games."""
    games = await client.get_player_current_games("erik")
    assert isinstance(games, list)
    if games:
        assert all(hasattr(g, 'url') for g in games)


@pytest.mark.asyncio
async def test_get_player_game_archives(client):
    """Test getting player's game archives."""
    archives = await client.get_player_game_archives("hikaru")
    assert isinstance(archives, list)
    assert len(archives) > 0


@pytest.mark.asyncio
async def test_get_archived_games(client):
    """Test getting player's archived games."""
    games = await client.get_archived_games("hikaru", 2023, 12)
    assert isinstance(games, list)
    if games:
        assert all(hasattr(g, 'url') for g in games)


@pytest.mark.asyncio
async def test_get_player_clubs(client):
    """Test getting player's clubs."""
    clubs = await client.get_player_clubs("erik")
    assert isinstance(clubs, list)
    if clubs:
        assert all(hasattr(c, 'name') for c in clubs)


@pytest.mark.asyncio
async def test_get_club(client):
    """Test getting club details."""
    club = await client.get_club("chess-com-developer-community")
    assert club.name is not None
    assert isinstance(club.members_count, int)


@pytest.mark.asyncio
async def test_get_tournament(client):
    """Test getting tournament details."""
    tournament = await client.get_tournament("-33rd-chesscom-quick-knockouts-1401-1600")
    assert tournament.name is not None
    assert tournament.status in ["finished", "in_progress", "registration"]
    await tournament.fetch_rounds(client=client)
    assert len(tournament.rounds) > 0
    assert isinstance(tournament.rounds[0], Round)


@pytest.mark.asyncio
async def test_tournament_round(client):
    tournament_id = "-33rd-chesscom-quick-knockouts-1401-1600"
    tournament_round = await client.get_tournament_round(tournament_id, 1)
    assert len(tournament_round.players) > 0
    assert len(tournament_round.group_urls) > 0
    await tournament_round.fetch_groups(client=client)
    assert len(tournament_round.groups) > 0
    assert isinstance(tournament_round.groups[0], Group)


@pytest.mark.asyncio
async def test_tournament_round_group(client):
    tournament_id = "-33rd-chesscom-quick-knockouts-1401-1600"
    tournament_round_group = await client.get_tournament_round_group(tournament_id, 1, 1)
    assert len(tournament_round_group.games) > 0
    assert isinstance(tournament_round_group.games[0], Game)


@pytest.mark.asyncio
async def test_get_match(client):
    """Test getting match details."""
    match = await client.get_match(12803)
    assert match.url.startswith("https://")
    await match.fetch_boards(client=client)
    assert len(match.boards) > 0
    assert len(match.boards[0].games) > 0
    assert isinstance(match.boards[0].games[0], Game)
    await match.boards[0].games[0].white.fetch_user(client=client)
    await match.boards[0].games[0].black.fetch_user(client=client)
    assert (
            match.boards[0].games[0].white.username == "sorinel"
            and match.boards[0].games[0].black.username == "Kllr"
    )
    assert match.boards[0].games[0].white.user == await client.get_player("sorinel")
    assert match.boards[0].games[0].black.user == await client.get_player("Kllr")
    match.boards[0].games[0].fetch_white(client=client)
    match.boards[0].games[0].fetch_black(client=client)
    assert match.boards[0].games[0].white.user == await client.get_player("sorinel")
    assert match.boards[0].games[0].black.user == await client.get_player("Kllr")


@pytest.mark.asyncio
async def test_get_match_board(client):
    """Test getting match board."""
    board = await client.get_match_board(12803, 1)
    assert len(board.games) > 0
    assert isinstance(board.games[0], BoardGame)
    await board.games[0].white.fetch_user(client=client)
    await board.games[0].black.fetch_user(client=client)
    assert (
            board.games[0].white.username == "sorinel"
            and board.games[0].black.username == "Kllr"
    )
    assert board.games[0].white.user == await client.get_player("sorinel")
    assert board.games[0].black.user == await client.get_player("Kllr")
    board.games[0].fetch_white(client=client)
    board.games[0].fetch_black(client=client)
    assert board.games[0].white.user == await client.get_player("sorinel")
    assert board.games[0].black.user == await client.get_player("Kllr")


@pytest.mark.asyncio
async def test_get_live_match(client):
    """Test getting live match details."""
    match = await client.get_live_match("5833")
    assert match.url.startswith("https://")


@pytest.mark.asyncio
async def test_get_live_match_board(client):
    """Test getting live match board."""
    board = await client.get_live_match_board(5833, 5)
    assert len(board.games) > 0
    assert isinstance(board.games[0], Game)


@pytest.mark.asyncio
async def test_get_country(client):
    """Test getting country details."""
    country = await client.get_country("US")
    assert country.name == "United States"
    assert country.code == "US"


@pytest.mark.asyncio
async def test_get_country_clubs(client):
    """Test getting country clubs."""
    country_clubs = await client.get_country_clubs("TV")
    await country_clubs.fetch_clubs(client=client)
    assert len(country_clubs.clubs) > 0
    assert isinstance(country_clubs.clubs[0], Club)


@pytest.mark.asyncio
async def test_get_daily_puzzle(client):
    """Test getting daily puzzle."""
    puzzle = await client.get_daily_puzzle()
    assert puzzle.title is not None
    assert puzzle.pgn is not None
    assert puzzle.fen is not None


@pytest.mark.asyncio
async def test_get_streamers(client):
    """Test getting Chess.com streamers."""
    streamers = await client.get_streamers()
    assert isinstance(streamers, list)
    if streamers:
        assert all(hasattr(s, 'username') for s in streamers)


@pytest.mark.asyncio
async def test_get_leaderboards(client):
    """Test getting leaderboards."""
    leaderboards = await client.get_leaderboards()
    assert hasattr(leaderboards, 'daily')
    assert hasattr(leaderboards, 'live_blitz')
    assert hasattr(leaderboards, 'tactics')


@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling."""
    with pytest.raises(NotFoundError):
        await client.get_player("thisisnotarealuser12345")

    with pytest.raises(ValueError):
        await client.get_player("")


@pytest.mark.asyncio
async def test_rate_limiting(client):
    """Test rate limiting functionality."""
    # Make multiple concurrent requests
    tasks = [client.get_player("hikaru") for _ in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check that all requests succeeded
    assert all(not isinstance(r, Exception) for r in results)


def test_client_context_manager():
    """Test client context manager functionality."""

    async def run():
        async with ChessComClient() as client:
            player = await client.get_player("hikaru")
            assert player is not None

    asyncio.run(run())
