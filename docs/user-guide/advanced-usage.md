# Advanced Usage

This guide covers advanced usage patterns and optimization techniques for the Chess.com API Client.

## Concurrent Operations

### Parallel Requests

Using `asyncio.gather` for multiple concurrent requests:

```python
import asyncio
from chess_com_api import ChessComClient

async def get_multiple_players(usernames: list[str]):
    async with ChessComClient() as client:
        # Create tasks for all requests
        tasks = [client.get_player(username) for username in usernames]
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for username, result in zip(usernames, results):
            if isinstance(result, Exception):
                print(f"Error fetching {username}: {result}")
            else:
                print(f"Found {username}: {result.title}")
```

### Controlled Concurrency

Using semaphores to limit concurrent requests:

```python
async def fetch_with_limit(usernames: list[str], max_concurrent: int = 10):
    async with ChessComClient() as client:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(username: str):
            async with semaphore:
                return await client.get_player(username)
        
        tasks = [fetch_with_semaphore(username) for username in usernames]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

## Custom Session Configuration

### Advanced HTTP Settings

Configuring the client with custom HTTP settings:

```python
import aiohttp
import ssl

async def create_advanced_client():
    # Create custom SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers('ECDHE+AESGCM')
    
    # Configure connection pooling
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=50,                # Max simultaneous connections
        ttl_dns_cache=300,       # DNS cache TTL in seconds
        force_close=False,       # Keep connections alive
        enable_cleanup_closed=True
    )
    
    # Configure timeouts
    timeout = aiohttp.ClientTimeout(
        total=60,        # Total timeout
        connect=10,      # Connection timeout
        sock_read=30,    # Socket read timeout
        sock_connect=10  # Socket connect timeout
    )
    
    # Create session with all configurations
    session = aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json"
        },
        raise_for_status=True
    )
    
    return ChessComClient(session=session)
```

## Custom Error Handling

### Retry Logic

Implementing custom retry logic:

```python
import time
from chess_com_api.exceptions import RateLimitError

class RetryHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute(self, operation):
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await operation()
            except RateLimitError as e:
                last_exception = e
                delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Rate limit hit, retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        
        raise last_exception

async def safe_get_player(client: ChessComClient, username: str):
    retry_handler = RetryHandler()
    return await retry_handler.execute(
        lambda: client.get_player(username)
    )
```

## Data Processing

### Batch Processing

Processing large amounts of data efficiently:

```python
from typing import AsyncGenerator
from datetime import datetime, timedelta

async def get_player_game_history(
    client: ChessComClient,
    username: str,
    months: int = 12
) -> AsyncGenerator:
    # Get archive URLs
    archives = await client.get_player_game_archives(username)
    
    # Process recent archives
    recent_archives = archives[-months:] if months > 0 else archives
    
    for archive_url in recent_archives:
        # Extract year and month from URL
        year = int(archive_url.split('/')[-2])
        month = int(archive_url.split('/')[-1])
        
        try:
            games = await client.get_archived_games(username, year, month)
            for game in games:
                yield game
        except Exception as e:
            print(f"Error processing {year}-{month}: {e}")
            continue

# Usage
async def analyze_player_history(username: str):
    async with ChessComClient() as client:
        win_count = 0
        total_games = 0
        
        async for game in get_player_game_history(client, username):
            total_games += 1
            if game.white.username.lower() == username.lower():
                if game.white.result == "win":
                    win_count += 1
            elif game.black.result == "win":
                win_count += 1
        
        win_rate = (win_count / total_games) * 100 if total_games > 0 else 0
        print(f"Win rate over last year: {win_rate:.2f}%")
```

## Caching

### Implementing a Simple Cache

```python
from functools import wraps
from typing import Any, Callable
import time

class SimpleCache:
    def __init__(self, ttl: int = 300):  # TTL in seconds
        self._cache = {}
        self._ttl = ttl
    
    def get(self, key: str) -> Any:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp <= self._ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = (value, time.time())

def cache_decorator(cache: SimpleCache):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator

# Usage
cache = SimpleCache(ttl=300)  # 5 minutes TTL

class CachedChessComClient(ChessComClient):
    @cache_decorator(cache)
    async def get_player(self, username: str):
        return await super().get_player(username)
```

## Custom Data Models

### Extending Base Models

```python
from dataclasses import dataclass
from datetime import datetime
from chess_com_api.models import Player


@dataclass
class EnhancedPlayer(Player):
    def __post_init__(self):
        super().__post_init__()
        self._calculate_membership_duration()

    def _calculate_membership_duration(self):
        self.membership_days = (datetime.now() - self.joined).days

    @property
    def is_premium(self) -> bool:
        return self.status == "premium"

    @property
    def membership_years(self) -> float:
        return self.membership_days / 365.25


# Usage
async def analyze_player_account(username: str):
    async with ChessComClient() as client:
        player_data = await client.get_player(username)
        player = EnhancedPlayer(**player_data.dict())

        print(f"Premium Member: {player.is_premium}")
        print(f"Member for: {player.membership_years:.1f} years")
```

## Performance Monitoring

### Basic Metrics Collection

```python
import time
from contextlib import asynccontextmanager
from typing import Dict, List

class Metrics:
    def __init__(self):
        self.request_times: List[float] = []
        self.error_counts: Dict[str, int] = {}
    
    def add_request_time(self, duration: float):
        self.request_times.append(duration)
    
    def add_error(self, error_type: str):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    @property
    def average_request_time(self) -> float:
        return sum(self.request_times) / len(self.request_times) if self.request_times else 0

class MonitoredChessComClient(ChessComClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = Metrics()
    
    @asynccontextmanager
    async def _timed_request(self):
        start_time = time.time()
        try:
            yield
        except Exception as e:
            self.metrics.add_error(type(e).__name__)
            raise
        finally:
            duration = time.time() - start_time
            self.metrics.add_request_time(duration)
    
    async def get_player(self, username: str):
        async with self._timed_request():
            return await super().get_player(username)

# Usage
async def monitored_operations():
    client = MonitoredChessComClient()
    try:
        await client.get_player("hikaru")
        await client.get_player("magnus")
    finally:
        print(f"Average request time: {client.metrics.average_request_time:.3f}s")
        print(f"Errors: {dict(client.metrics.error_counts)}")
```

## Next Steps

- Learn about [Rate Limiting](rate-limiting.md) for managing API quotas
- Explore [Error Handling](error-handling.md) for robust applications
- Check the [API Reference](../api/client.md) for detailed method documentation