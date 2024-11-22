# Migration Guide

This guide helps you migrate between different versions of the Chess.com API client. It documents all breaking changes,
deprecations, and new features for each version.

## Upgrading to 1.0.0

### Breaking Changes

1. Async/Await Support

```python
# Old code (0.x)
client = ChessComClient()
player = client.get_player("hikaru")
client.close()

# New code (1.0.0)
async with ChessComClient() as client:
    player = await client.get_player("hikaru")
```

2. Type Hints

```python
# Old code (0.x)
def get_player(username):
    pass


# New code (1.0.0)
async def get_player(self, username: str) -> Player:
    pass
```

3. Exception Hierarchy

```python
# Old code (0.x)
try:
    player = client.get_player("username")
except ChessComError:
    pass

# New code (1.0.0)
try:
    player = await client.get_player("username")
except NotFoundError:
    # Handle specific error
    pass
except ChessComAPIError:
    # Handle general API error
    pass
```

### New Features

1. Rate Limiting

```python
# Configure rate limiting
client = ChessComClient(
    rate_limit=300,  # Maximum concurrent requests
    max_retries=3  # Number of retries
)
```

2. Custom Session Configuration

```python
import aiohttp

session = aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=30),
    headers={"User-Agent": "MyApp/1.0"}
)
client = ChessComClient(session=session)
```

3. Model Properties

```python
# Access typed properties
player = await client.get_player("hikaru")
print(player.title)  # Type: Optional[str]
print(player.rating)  # Type: int
```

### Deprecations

1. Synchronous Methods

```python
# Deprecated (0.x)
client.get_player_sync("username")

# New approach (1.0.0)
import asyncio

asyncio.run(client.get_player("username"))
```

2. Direct Property Access

```python
# Deprecated (0.x)
player._data["title"]

# New approach (1.0.0)
player.title  # Use typed properties
```

### Migration Steps

1. Update Dependencies

```bash
# Update to the latest version
pip install --upgrade chess-com-api

# For development
pip install --upgrade chess-com-api[dev]
```

2. Update Imports

```python
# Old imports (0.x)
from chess_com_api import ChessComClient, ChessComError

# New imports (1.0.0)
from chess_com_api import (
    ChessComClient,
    ChessComAPIError,
    NotFoundError,
    Player
)
```

3. Update Client Usage

```python
# Old code (0.x)
client = ChessComClient()
try:
    player = client.get_player("username")
finally:
    client.close()

# New code (1.0.0)
async with ChessComClient() as client:
    try:
        player = await client.get_player("username")
    except NotFoundError:
        # Handle error
        pass
```

4. Update Type Hints

```python
# Add type hints to your functions
async def get_player_info(username: str) -> Optional[Player]:
    async with ChessComClient() as client:
        try:
            return await client.get_player(username)
        except NotFoundError:
            return None
```

### Code Examples

1. Handling Multiple Requests

```python
# Old code (0.x)
results = []
for username in usernames:
    try:
        player = client.get_player(username)
        results.append(player)
    except ChessComError:
        continue

# New code (1.0.0)
async with ChessComClient() as client:
    tasks = [
        client.get_player(username)
        for username in usernames
    ]
    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )
```

2. Custom Error Handling

```python
# Old code (0.x)
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ChessComError as e:
            logging.error(f"API error: {e}")
            raise

    return wrapper


# New code (1.0.0)
from functools import wraps


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NotFoundError as e:
            logging.warning(f"Resource not found: {e}")
            raise
        except ChessComAPIError as e:
            logging.error(f"API error: {e}")
            raise

    return wrapper
```

3. Data Processing

```python
# Old code (0.x)
def process_games(username):
    games = client.get_player_games(username)
    return [game.get("url") for game in games]


# New code (1.0.0)
async def process_games(username: str) -> List[str]:
    async with ChessComClient() as client:
        games = await client.get_player_games(username)
        return [game.url for game in games]
```

### Testing Updates

1. Update Test Fixtures

```python
# Old tests (0.x)
def test_get_player(client):
    player = client.get_player("hikaru")
    assert player["username"] == "hikaru"


# New tests (1.0.0)
@pytest.mark.asyncio
async def test_get_player(client):
    player = await client.get_player("hikaru")
    assert player.username == "hikaru"
```

2. Update Mock Usage

```python
# Old mocks (0.x)
def test_with_mock(mocker):
    mocker.patch("chess_com_api.client.get_player")


# New mocks (1.0.0)
@pytest.mark.asyncio
async def test_with_mock(mocker):
    mock = mocker.patch("chess_com_api.client._make_request")
    mock.return_value = {"username": "hikaru"}
```

## Configuration Updates

### Environment Variables

```bash
# Old environment variables (0.x)
CHESS_COM_TIMEOUT=30
CHESS_COM_RETRY=3

# New environment variables (1.0.0)
CHESS_COM_TIMEOUT=30
CHESS_COM_MAX_RETRIES=3
CHESS_COM_RATE_LIMIT=300
```

### Logging Configuration

```python
# Old logging (0.x)
logging.basicConfig(level=logging.INFO)

# New logging (1.0.0)
import logging.config

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO"
        }
    },
    "loggers": {
        "chess_com_api": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    }
})
```

## Best Practices

1. Always use async/await with proper error handling
2. Implement proper type hints
3. Use context managers for client lifecycle
4. Handle rate limiting appropriately
5. Update tests to use pytest-asyncio
6. Use modern Python features (3.8+)

## Troubleshooting

### Common Issues

1. Async/Await Errors

```python
# Error: Async call in non-async function
# Solution: Add async/await
async def main():
    async with ChessComClient() as client:
        return await client.get_player("username")


result = asyncio.run(main())
```

2. Type Hint Issues

```python
# Error: Type hint incompatibility
# Solution: Add proper type hints
from typing import Optional, List


async def get_players(
        usernames: List[str]
) -> List[Optional[Player]]:
    pass
```

### Verification Steps

1. Check all async/await usage
2. Verify type hints
3. Update error handling
4. Update tests
5. Check configuration
6. Update dependencies

## See Also

- [API Reference](../api/client.md)
- [Project Setup](project-setup.md)
- [Testing Guide](testing-guide.md)