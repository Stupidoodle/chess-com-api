"""Tests for the models module."""

from datetime import datetime

from chess_com_api.models import Game, Player, PlayerStats


def test_player_model() -> None:
    """Test Player model."""
    data = {
        "username": "hikaru",
        "player_id": 12345,
        "title": "GM",
        "status": "premium",
        "name": "Hikaru Nakamura",
        "avatar": "https://example.com/avatar.jpg",
        "location": "USA",
        "country": "US",
        "joined": 1234567890,
        "last_online": 1234567890,
        "followers": 100000,
    }

    player = Player.from_dict(data)
    assert player.username == "hikaru"
    assert player.title == "GM"
    assert isinstance(player.joined, datetime)


def test_player_stats_model() -> None:
    """Test PlayerStats model."""
    data = {
        "chess_daily": {"last": {"rating": 2800, "date": 1234567890, "rd": 50}},
        "chess_blitz": {"last": {"rating": 3000, "date": 1234567890, "rd": 50}},
    }

    stats = PlayerStats.from_dict(data)
    assert stats.chess_daily is not None
    assert stats.chess_blitz is not None


def test_game_model() -> None:
    """Test Game model."""
    data = {
        "white": {
            "username": "player1",
            "rating": 1500,
            "result": "repetition",
            "@id": "https://api.example.com/pub/player/player1",
            "uuid": "1234567890",
        },
        "black": {
            "username": "player2",
            "rating": 1600,
            "result": "win",
            "@id": "https://api.example.com/pub/player/player2",
            "uuid": "1234567891",
        },
        "url": "https://example.com/game/18023",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "pgn": "1. e4 e5",
        "time_control": "300+2",
        "time_class": "blitz",
        "rules": "chess",
    }

    game = Game.from_dict(data)
    assert game.url == "https://example.com/game/18023"
    assert game.time_class == "blitz"
    assert game.id == 18023


# Add more model tests...
