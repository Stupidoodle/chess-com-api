# Basic Usage

This guide covers the fundamental operations you can perform with the Chess.com API Client.

## Client Setup

The most basic way to use the client is with a context manager:

```python
import asyncio
from chess_com_api import ChessComClient

async def main():
    async with ChessComClient() as client:
        # Your code here
        pass

asyncio.run(main())
```

## Player Operations

### Getting Player Profile

```python
async def get_player_info(username: str):
    async with ChessComClient() as client:
        player = await client.get_player(username)
        
        print(f"Username: {player.username}")
        print(f"Title: {player.title}")
        print(f"Status: {player.status}")
        print(f"Followers: {player.followers}")
        print(f"Country: {player.country}")
        print(f"Joined: {player.joined}")
```

### Getting Player Statistics

```python
async def get_player_ratings(username: str):
    async with ChessComClient() as client:
        stats = await client.get_player_stats(username)
        
        # Accessing different game modes
        blitz = stats.chess_blitz["last"]
        rapid = stats.chess_rapid["last"]
        bullet = stats.chess_bullet["last"]
        
        print(f"Blitz Rating: {blitz['rating']}")
        print(f"Rapid Rating: {rapid['rating']}")
        print(f"Bullet Rating: {bullet['rating']}")
```

### Getting Player's Current Games

```python
async def get_ongoing_games(username: str):
    async with ChessComClient() as client:
        games = await client.get_player_current_games(username)
        
        for game in games:
            print("\nGame Details:")
            print(f"URL: {game.url}")
            print(f"White: {game.white.username}")
            print(f"Black: {game.black.username}")
            print(f"Time Control: {game.time_control}")
```

## Game History

### Getting Archived Games

```python
async def get_monthly_games(username: str, year: int, month: int):
    async with ChessComClient() as client:
        games = await client.get_archived_games(username, year, month)
        
        for game in games:
            print("\nGame:")
            print(f"Result: {game.white.result} - {game.black.result}")
            print(f"PGN: {game.pgn}")
```

### Downloading PGN Files

```python
async def download_monthly_pgn(username: str, year: int, month: int):
    async with ChessComClient() as client:
        await client.download_archived_games_pgn(
            file_name=f"{username}_{year}_{month}.pgn",
            username=username,
            year=year,
            month=month
        )
```

## Tournament Information

### Getting Tournament Details

```python
async def get_tournament_details(url_id: str):
    async with ChessComClient() as client:
        tournament = await client.get_tournament(url_id)
        
        print(f"Name: {tournament.name}")
        print(f"Status: {tournament.status}")
        print(f"Type: {tournament.settings.type}")
        print(f"Time Control: {tournament.settings.time_control}")
```

### Getting Tournament Rounds

```python
async def get_tournament_round_info(url_id: str, round_num: int):
    async with ChessComClient() as client:
        round_info = await client.get_tournament_round(url_id, round_num)
        
        print(f"Players: {len(round_info.players)}")
        print(f"Groups: {len(round_info.groups)}")
```

## Club Operations

### Getting Club Information

```python
async def get_club_info(url_id: str):
    async with ChessComClient() as client:
        club = await client.get_club(url_id)
        
        print(f"Name: {club.name}")
        print(f"Members: {club.members_count}")
        print(f"Description: {club.description}")
```

### Getting Club Members

```python
async def get_club_members(url_id: str):
    async with ChessComClient() as client:
        members = await client.get_club_members(url_id)
        
        print("Weekly Members:")
        for member in members["weekly"]:
            print(f"- {member}")
```

## Puzzle Operations

### Getting Daily Puzzle

```python
async def get_todays_puzzle():
    async with ChessComClient() as client:
        puzzle = await client.get_daily_puzzle()
        
        print(f"Title: {puzzle.title}")
        print(f"FEN: {puzzle.fen}")
        print(f"PGN: {puzzle.pgn}")
```

### Getting Random Puzzle

```python
async def get_random_puzzle():
    async with ChessComClient() as client:
        puzzle = await client.get_random_puzzle()
        
        print(f"Title: {puzzle.title}")
        print(f"FEN: {puzzle.fen}")
        print(f"PGN: {puzzle.pgn}")
```

## Error Handling

Always handle potential errors in your applications:

```python
from chess_com_api.exceptions import (
    NotFoundError,
    RateLimitError,
    ValidationError
)

async def safe_operation():
    try:
        async with ChessComClient() as client:
            return await client.get_player("username")
    except NotFoundError:
        print("Player not found")
    except RateLimitError:
        print("Rate limit exceeded")
    except ValidationError:
        print("Invalid input")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Working with Data Models

All responses are converted to convenient Python objects:

```python
async def work_with_models():
    async with ChessComClient() as client:
        player = await client.get_player("hikaru")
        
        # Access attributes directly
        print(player.username)  # string
        print(player.joined)    # datetime
        print(player.status)    # string
        
        # Models are immutable for safety
        player.username = "new"  # Raises AttributeError
```

## Next Steps

- Check out [Advanced Usage](advanced-usage.md) for more complex scenarios
- Learn about [Rate Limiting](rate-limiting.md) for high-volume applications
- See [Error Handling](error-handling.md) for detailed error management