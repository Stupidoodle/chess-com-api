# Exceptions Reference

This document details all exceptions that can be raised by the Chess.com API client. Understanding these exceptions is
crucial for proper error handling in your applications.

## Exception Hierarchy

```plain
ChessComAPIError
├── RateLimitError
├── NotFoundError
├── ValidationError
├── RedirectError
└── GoneError
```

## Base Exception

### ChessComAPIError

The base exception for all Chess.com API errors.

```python
class ChessComAPIError(Exception):
    """Base exception for Chess.com API errors."""
    pass
```

This is the parent class for all custom exceptions in the library. You can catch this to handle any API-related error:

```python
try:
    player = await client.get_player("username")
except ChessComAPIError as e:
    print(f"An API error occurred: {e}")
```

## Specific Exceptions

### RateLimitError

Raised when parallel requests exceed the API's capacity to handle them.

```python
class RateLimitError(ChessComAPIError):
    """Raised when the API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        self.message = message
        super().__init__(self.message)
```

#### Example Usage

```python
from chess_com_api.exceptions import RateLimitError


async def safe_get_player(username: str):
    try:
        async with ChessComClient() as client:
            return await client.get_player(username)
    except RateLimitError:
        print("Too many requests, please try again later")
        return None
```

#### Common Scenarios

- Making too many parallel requests
- Not waiting for responses before making new requests
- Bulk operations without proper rate limiting

### NotFoundError

Raised when the requested resource doesn't exist.

```python
class NotFoundError(ChessComAPIError):
    """Raised when requested resource is not found."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Resource not found: {message}")
```

#### Example Usage

```python
try:
    player = await client.get_player("nonexistent_user")
except NotFoundError as e:
    print(f"Player not found: {e}")
```

#### Common Scenarios

- Invalid username
- Deleted tournament
- Archived match
- Non-existent club

### ValidationError

Raised when input validation fails.

```python
class ValidationError(ChessComAPIError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Validation error: {message}")
```

#### Example Usage

```python
try:
    if not username.strip():
        raise ValidationError("Username cannot be empty")
    player = await client.get_player(username)
except ValidationError as e:
    print(f"Invalid input: {e}")
```

#### Common Scenarios

- Empty username
- Invalid date format
- Invalid country code
- Malformed tournament ID

### RedirectError

Raised when a resource has moved to a different location.

```python
class RedirectError(ChessComAPIError):
    """Raised when a redirect is encountered."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(
            f"Redirect to {url} was encountered. Please try again later."
        )
```

#### Example Usage

```python
try:
    tournament = await client.get_tournament("old_id")
except RedirectError as e:
    print(f"Tournament moved to: {e.url}")
```

#### Common Scenarios

- Renamed tournaments
- Moved resources
- URL structure changes

### GoneError

Raised when a resource is no longer available.

```python
class GoneError(ChessComAPIError):
    """Raised when a resource is no longer available."""

    def __init__(self, message: str = "Resource is no longer available"):
        self.message = message
        super().__init__(self.message)
```

#### Example Usage

```python
try:
    game = await client.get_archived_games("username", 2020, 1)
except GoneError:
    print("These games are no longer available")
```

#### Common Scenarios

- Deleted games
- Removed tournaments
- Archived content

## Error Handling Best Practices

### 1. Specific to General Exception Handling

Always catch specific exceptions before general ones:

```python
try:
    await client.get_player("username")
except NotFoundError:
    # Handle missing player
    pass
except RateLimitError:
    # Handle rate limiting
    pass
except ChessComAPIError:
    # Handle any other API error
    pass
except Exception:
    # Handle unexpected errors
    pass
```

### 2. Custom Error Handler

Create a reusable error handler:

```python
from typing import Optional, TypeVar, Callable
import logging

T = TypeVar("T")


class ErrorHandler:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    async def handle_operation(
            self,
            operation: Callable[..., T],
            *args,
            **kwargs
    ) -> Optional[T]:
        try:
            return await operation(*args, **kwargs)
        except NotFoundError as e:
            self.logger.warning(f"Resource not found: {e}")
            return None
        except RateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {e}")
            raise
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            return None
        except ChessComAPIError as e:
            self.logger.error(f"API error: {e}")
            raise
        except Exception as e:
            self.logger.exception("Unexpected error")
            raise


# Usage
handler = ErrorHandler()
result = await handler.handle_operation(
    client.get_player,
    "username"
)
```

### 3. Context-Specific Handling

Adapt error handling to the context:

```python
async def get_player_stats_safely(username: str):
    """Get player stats with fallback to basic info."""
    try:
        async with ChessComClient() as client:
            # Try to get full stats
            stats = await client.get_player_stats(username)
            return stats
    except NotFoundError:
        return None
    except RateLimitError:
        # Fall back to basic player info
        try:
            return await client.get_player(username)
        except ChessComAPIError:
            return None
```

### 4. Bulk Operation Error Handling

Handle errors in bulk operations:

```python
async def bulk_fetch_players(usernames: List[str]):
    """Fetch multiple players with error tracking."""
    results = []
    errors = []

    async with ChessComClient() as client:
        for username in usernames:
            try:
                player = await client.get_player(username)
                results.append(player)
            except ChessComAPIError as e:
                errors.append((username, str(e)))

    return results, errors
```

## Common Error Patterns

### Network Issues

```python
import aiohttp

try:
    async with ChessComClient() as client:
        await client.get_player("username")
except aiohttp.ClientError as e:
    print(f"Network error: {e}")
```

### Resource State Errors

```python
try:
    match = await client.get_match(match_id)
except GoneError:
    print("Match has been deleted")
except RedirectError as e:
    print(f"Match moved to: {e.url}")
```

### Input Validation

```python
try:
    if not isinstance(username, str):
        raise ValidationError("Username must be a string")
    if len(username) > 50:
        raise ValidationError("Username too long")
    player = await client.get_player(username)
except ValidationError as e:
    print(f"Invalid input: {e}")
```

## See Also

- [Client Reference](client.md) - API client documentation
- [Models Reference](models.md) - Data models documentation
- [Error Handling Guide](../user-guide/error-handling.md) - Detailed error handling guide