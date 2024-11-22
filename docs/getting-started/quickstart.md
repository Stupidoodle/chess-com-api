# Quick Start Guide

This guide will help you get up and running with the Chess.com API Client quickly.

## Basic Usage

Here's a simple example to get started:

```python
import asyncio
from chess_com_api import ChessComClient


async def main():
    async with ChessComClient() as client:
        # Get player profile
        player = await client.get_player("hikaru")
        print(f"Player: {player.username}")
        print(f"Title: {player.title}")
        print(f"Rating: {player.rating}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Common Operations

### Getting Player Statistics

```python
async def get_player_stats(username: str):
    async with ChessComClient() as client:
        stats = await client.get_player_stats(username)

        # Access various game modes
        blitz = stats.chess_blitz
        rapid = stats.chess_rapid
        bullet = stats.chess_bullet

        print(f"Blitz Rating: {blitz['last']['rating']}")
        print(f"Rapid Rating: {rapid['last']['rating']}")
        print(f"Bullet Rating: {bullet['last']['rating']}")
```

### Fetching Recent Games

```python
async def get_recent_games(username: str):
    async with ChessComClient() as client:
        games = await client.get_player_current_games(username)

        for game in games:
            print(f"Game URL: {game.url}")
            print(f"White: {game.white.username}")
            print(f"Black: {game.black.username}")
            print(f"Time Control: {game.time_control}")
            print("---")
```

### Working with Tournaments

```python
async def get_tournament_info(tournament_id: str):
    async with ChessComClient() as client:
        tournament = await client.get_tournament(tournament_id)

        print(f"Tournament: {tournament.name}")
        print(f"Status: {tournament.status}")
        print(f"Time Control: {tournament.settings.time_control}")
```

## Error Handling

Always handle potential errors in your applications:

```python
from chess_com_api.exceptions import NotFoundError, RateLimitError


async def safe_get_player(username: str):
    try:
        async with ChessComClient() as client:
            return await client.get_player(username)
    except NotFoundError:
        print(f"Player {username} not found")
    except RateLimitError:
        print("Rate limit exceeded. Please try again later")
    except Exception as e:
        print(f"An error occurred: {e}")
```

## Rate Limiting

The client handles rate limiting automatically, but you can customize it:

```python
client = ChessComClient(
    rate_limit=100,  # Maximum concurrent requests
    max_retries=3  # Number of retries on failure
)
```

## Working with Multiple Requests

You can make multiple concurrent requests efficiently:

```python
async def get_multiple_players(usernames: List[str]):
    async with ChessComClient() as client:
        tasks = [client.get_player(username) for username in usernames]
        players = await asyncio.gather(*tasks, return_exceptions=True)

        for username, result in zip(usernames, players):
            if isinstance(result, Exception):
                print(f"Error fetching {username}: {result}")
            else:
                print(f"Found {username}: {result.title}")
```

## Next Steps

- Check out the [Authentication](authentication.md) guide for more secure usage
- Visit the [User Guide](../user-guide/basic-usage.md) for detailed information
- See the [Examples](../examples/player-data.md) section for more use cases
- Read the [API Reference](../api/client.md) for complete documentation