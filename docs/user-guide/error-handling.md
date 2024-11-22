# Error Handling

This guide covers error handling in the Chess.com API Client, including common error types, best practices, and example
implementations.

## Exception Hierarchy

The client defines several custom exceptions:

```python
from chess_com_api.exceptions import (
    ChessComAPIError,      # Base exception
    NotFoundError,         # Resource not found (404)
    RateLimitError,        # Rate limit exceeded (429)
    ValidationError,       # Invalid input
    RedirectError,         # Resource moved (301, 304)
    GoneError             # Resource no longer available (410)
)
```

## Basic Error Handling

### Simple Try/Except Pattern

```python
from chess_com_api import ChessComClient
from chess_com_api.exceptions import NotFoundError, RateLimitError

async def get_player_safely(username: str):
    try:
        async with ChessComClient() as client:
            return await client.get_player(username)
    except NotFoundError:
        print(f"Player {username} not found")
        return None
    except RateLimitError:
        print("Rate limit exceeded, please try again later")
        return None
    except ChessComAPIError as e:
        print(f"API error occurred: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Context-Specific Error Handling

```python
async def handle_tournament_operations(tournament_id: str):
    try:
        async with ChessComClient() as client:
            tournament = await client.get_tournament(tournament_id)
            
            try:
                # Fetch tournament rounds
                rounds = await asyncio.gather(
                    *[client.get_tournament_round(tournament_id, i) 
                      for i in range(1, tournament.round_count + 1)]
                )
                return tournament, rounds
            except NotFoundError:
                print("Some tournament rounds not found")
                return tournament, None
                
    except GoneError:
        print("Tournament has been deleted or archived")
    except ValidationError as e:
        print(f"Invalid tournament ID: {e}")
```

## Advanced Error Handling

### Custom Error Handler

```python
from dataclasses import dataclass
from typing import Optional, Callable, Any
import logging

@dataclass
class ErrorHandler:
    logger: logging.Logger
    notify_func: Optional[Callable[[Exception], Any]] = None
    
    async def handle(self, operation: Callable, *args, **kwargs):
        try:
            return await operation(*args, **kwargs)
        except NotFoundError as e:
            self.logger.warning(f"Resource not found: {e}")
            if self.notify_func:
                await self.notify_func(e)
            return None
        except RateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {e}")
            if self.notify_func:
                await self.notify_func(e)
            raise
        except ChessComAPIError as e:
            self.logger.error(f"API error: {e}")
            if self.notify_func:
                await self.notify_func(e)
            raise
        except Exception as e:
            self.logger.exception("Unexpected error occurred")
            if self.notify_func:
                await self.notify_func(e)
            raise

# Usage
logger = logging.getLogger("chess_com_api")
async def notify_admin(error: Exception):
    # Implement notification logic
    pass

handler = ErrorHandler(logger, notify_admin)

async def safe_operation():
    async with ChessComClient() as client:
        return await handler.handle(
            client.get_player, "username"
        )
```

### Retry Handler

```python
class RetryHandler:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        logger: Optional[logging.Logger] = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.logger = logger or logging.getLogger(__name__)

    async def execute(
        self,
        operation: Callable,
        *args,
        retry_on: tuple = (RateLimitError,),
        **kwargs
    ):
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except retry_on as e:
                last_exception = e
                if attempt == self.max_retries - 1:
                    self.logger.error(
                        f"Max retries ({self.max_retries}) exceeded"
                    )
                    raise
                
                delay = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )
                self.logger.warning(
                    f"Attempt {attempt + 1} failed, "
                    f"retrying in {delay} seconds..."
                )
                await asyncio.sleep(delay)
            except Exception as e:
                self.logger.exception("Unhandled error occurred")
                raise

# Usage
retry_handler = RetryHandler(max_retries=5)

async def fetch_with_retry():
    async with ChessComClient() as client:
        return await retry_handler.execute(
            client.get_player,
            "username",
            retry_on=(RateLimitError, ConnectionError)
        )
```

## Error Recovery Strategies

### Graceful Degradation

```python
async def get_player_profile(username: str):
    """Fetch player profile with fallback to basic info."""
    async with ChessComClient() as client:
        try:
            # Try to get full profile
            player = await client.get_player(username)
            stats = await client.get_player_stats(username)
            return {
                "profile": player,
                "stats": stats
            }
        except NotFoundError:
            return None
        except RateLimitError:
            # Fall back to basic profile only
            try:
                return {
                    "profile": await client.get_player(username),
                    "stats": None
                }
            except Exception:
                return None
```

### Bulk Operation Recovery

```python
async def bulk_fetch_with_recovery(urls: List[str]):
    """Fetch multiple resources with partial success handling."""
    results = []
    failed = []
    
    async with ChessComClient() as client:
        for url in urls:
            try:
                result = await client.get_club(url)
                results.append(result)
            except Exception as e:
                failed.append((url, str(e)))
                continue
    
    if failed:
        # Log failures but continue with partial success
        logging.warning(
            f"Failed to fetch {len(failed)} out of {len(urls)} resources"
        )
        for url, error in failed:
            logging.error(f"Failed to fetch {url}: {error}")
    
    return results, failed
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

    async def execute(self, operation: Callable, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await operation(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise e

# Usage
breaker = CircuitBreaker()
async def safe_api_call():
    async with ChessComClient() as client:
        return await breaker.execute(
            client.get_player, "username"
        )
```

## Best Practices

1. **Always Use Context Managers**
   ```python
   # Good
   async with ChessComClient() as client:
       result = await client.get_player("username")
   
   # Bad
   client = ChessComClient()
   result = await client.get_player("username")
   # Resource leak if error occurs before close
   ```

2. **Implement Proper Logging**
   ```python
   import logging

   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger("chess_com_api")
   ```

3. **Use Type Hints and Exception Types**
   ```python
   from typing import Optional
   from chess_com_api.models import Player

   async def get_player(
       username: str
   ) -> Optional[Player]:
       try:
           async with ChessComClient() as client:
               return await client.get_player(username)
       except NotFoundError:
           return None
   ```

4. **Handle Resource Cleanup**
   ```python
   from contextlib import asynccontextmanager

   @asynccontextmanager
   async def managed_client():
       client = ChessComClient()
       try:
           yield client
       finally:
           await client.close()
   ```

## Common Error Scenarios

### Network Issues

```python
import aiohttp

async def handle_network_errors():
    try:
        async with ChessComClient() as client:
            return await client.get_player("username")
    except aiohttp.ClientError as e:
        logging.error(f"Network error: {e}")
        return None
```

### Invalid Input

```python
async def handle_invalid_input(username: str):
    try:
        if not username or not isinstance(username, str):
            raise ValidationError("Username must be a non-empty string")

        async with ChessComClient() as client:
            return await client.get_player(username)
    except ValidationError as e:
        logging.error(f"Invalid input: {e}")
        return None
```

### Resource Not Found

```python
async def handle_missing_resource():
    try:
        async with ChessComClient() as client:
            return await client.get_player("nonexistent_user")
    except NotFoundError:
        # Log but don't raise - expected scenario
        logging.info("Resource not found")
        return None
    except Exception as e:
        # Log and raise - unexpected scenario
        logging.error(f"Unexpected error: {e}")
        raise
```

## Next Steps

- Review [Rate Limiting](rate-limiting.md) for handling request limits
- Check [Advanced Usage](advanced-usage.md) for more complex scenarios
- See the [API Reference](../api/client.md) for detailed method documentation