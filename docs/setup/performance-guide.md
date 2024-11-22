# Performance Tuning Guide

This guide covers optimization strategies and best practices for achieving optimal performance with the Chess.com API
client.

## Connection Optimization

### Connection Pooling

Configure connection pooling for optimal performance:

```python
import aiohttp
from chess_com_api import ChessComClient

async def create_optimized_client():
    connector = aiohttp.TCPConnector(
        limit=100,               # Maximum concurrent connections
        ttl_dns_cache=300,       # DNS cache TTL in seconds
        use_dns_cache=True,      # Enable DNS caching
        force_close=False,       # Keep connections alive
        enable_cleanup_closed=True
    )
    
    timeout = aiohttp.ClientTimeout(
        total=30,        # Total request timeout
        connect=10,      # Connection timeout
        sock_read=10,    # Socket read timeout
        sock_connect=10  # Socket connect timeout
    )
    
    session = aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    )
    
    return ChessComClient(session=session)
```

### DNS Optimization

```python
import socket

# Configure custom DNS resolver
resolver = aiohttp.AsyncResolver(
    nameservers=["8.8.8.8", "8.8.4.4"]
)

connector = aiohttp.TCPConnector(
    resolver=resolver,
    family=socket.AF_INET  # IPv4 only for consistent performance
)
```

## Concurrent Operations

### Batch Processing

Process multiple requests efficiently:

```python
import asyncio
from typing import List, Optional

async def batch_process(
    usernames: List[str],
    batch_size: int = 50
) -> List[Optional[dict]]:
    """Process usernames in batches."""
    results = []
    
    async with ChessComClient() as client:
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            tasks = [
                client.get_player(username)
                for username in batch
            ]
            
            # Process batch
            batch_results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )
            
            # Handle results
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(None)
                else:
                    results.append(result)
            
            # Add small delay between batches
            await asyncio.sleep(0.1)
    
    return results
```

### Concurrent Request Management

```python
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar('T')

@dataclass
class RequestManager(Generic[T]):
    """Manage concurrent request execution."""
    
    max_concurrent: int = 50
    timeout: float = 30.0
    
    async def execute(
        self,
        client: ChessComClient,
        operations: List[T]
    ) -> List[Optional[T]]:
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def controlled_request(operation: T) -> Optional[T]:
            async with semaphore:
                try:
                    return await asyncio.wait_for(
                        operation,
                        timeout=self.timeout
                    )
                except asyncio.TimeoutError:
                    return None
                except Exception as e:
                    print(f"Error processing request: {e}")
                    return None
        
        return await asyncio.gather(
            *[controlled_request(op) for op in operations]
        )

# Usage
async def get_multiple_players(usernames: List[str]):
    async with ChessComClient() as client:
        manager = RequestManager[dict](max_concurrent=50)
        operations = [
            client.get_player(username)
            for username in usernames
        ]
        results = await manager.execute(client, operations)
        return results
```

## Memory Optimization

### Generator-based Processing

Use generators for large datasets:

```python
async def process_large_dataset(usernames: List[str]):
    async def player_generator():
        async with ChessComClient() as client:
            for username in usernames:
                try:
                    player = await client.get_player(username)
                    yield player
                except Exception as e:
                    print(f"Error processing {username}: {e}")
                    continue
    
    async for player in player_generator():
        # Process each player with minimal memory usage
        process_player(player)
```

### Memory-Efficient Bulk Operations

```python
from itertools import islice

async def memory_efficient_processing(
    usernames: List[str],
    chunk_size: int = 1000
):
    def chunks(data: List[str], size: int):
        iterator = iter(data)
        return iter(lambda: list(islice(iterator, size)), [])
    
    results = []
    async with ChessComClient() as client:
        for chunk in chunks(usernames, chunk_size):
            chunk_results = await batch_process(chunk)
            
            # Process results immediately to free memory
            for result in chunk_results:
                if result:
                    process_and_store(result)
            
            # Clear chunk results
            chunk_results = None
            
            # Allow garbage collection
            await asyncio.sleep(0)
```

## Cache Optimization

### Simple Cache Implementation

```python
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CacheEntry:
    data: Any
    timestamp: float
    ttl: float

class APICache:
    def __init__(self, default_ttl: float = 300):
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry.timestamp < entry.ttl:
                return entry.data
            del self.cache[key]
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None
    ) -> None:
        self.cache[key] = CacheEntry(
            data=value,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl
        )
    
    def cleanup(self) -> None:
        now = time.time()
        expired = [
            key for key, entry in self.cache.items()
            if now - entry.timestamp >= entry.ttl
        ]
        for key in expired:
            del self.cache[key]

# Usage with client
class CachedChessComClient(ChessComClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = APICache()
    
    async def get_player(self, username: str):
        cache_key = f"player:{username}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        result = await super().get_player(username)
        self.cache.set(cache_key, result)
        return result
```

## Performance Monitoring

### Request Timing

```python
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class PerformanceMetrics:
    total_requests: int = 0
    total_errors: int = 0
    response_times: List[float] = field(default_factory=list)
    endpoint_times: Dict[str, List[float]] = field(default_factory=dict)
    
    @property
    def average_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def add_timing(self, endpoint: str, duration: float):
        self.total_requests += 1
        self.response_times.append(duration)
        
        if endpoint not in self.endpoint_times:
            self.endpoint_times[endpoint] = []
        self.endpoint_times[endpoint].append(duration)
    
    def print_stats(self):
        print(f"Total Requests: {self.total_requests}")
        print(f"Total Errors: {self.total_errors}")
        print(f"Average Response Time: {self.average_response_time:.3f}s")
        
        print("\nEndpoint Statistics:")
        for endpoint, times in self.endpoint_times.items():
            avg_time = sum(times) / len(times)
            print(f"{endpoint}: {avg_time:.3f}s average")

class MonitoredChessComClient(ChessComClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = PerformanceMetrics()
    
    @asynccontextmanager
    async def _timed_request(self, endpoint: str):
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.metrics.add_timing(endpoint, duration)
    
    async def get_player(self, username: str):
        async with self._timed_request(f"get_player:{username}"):
            return await super().get_player(username)
```

## Best Practices

### 1. Connection Management

- Reuse client instances
- Configure appropriate timeouts
- Use connection pooling
- Enable keep-alive when appropriate

### 2. Concurrency

- Use appropriate batch sizes
- Implement rate limiting
- Handle errors gracefully
- Monitor memory usage

### 3. Memory Management

- Process large datasets in chunks
- Use generators for streaming
- Clear unused references
- Monitor memory usage

### 4. Caching

- Cache frequently accessed data
- Implement TTL for cache entries
- Regular cache cleanup
- Monitor cache hit rates

### 5. Error Handling

- Implement retries with backoff
- Handle timeouts appropriately
- Log errors for monitoring
- Monitor error rates

## Performance Checklist

1. **Client Configuration**
    - [ ] Configure connection pooling
    - [ ] Set appropriate timeouts
    - [ ] Enable DNS caching
    - [ ] Configure retry strategy

2. **Request Optimization**
    - [ ] Batch similar requests
    - [ ] Implement concurrent processing
    - [ ] Use connection pooling
    - [ ] Enable keep-alive when appropriate

3. **Memory Management**
    - [ ] Process large datasets in chunks
    - [ ] Clear unused references
    - [ ] Monitor memory usage
    - [ ] Use generators for large datasets

4. **Error Handling**
    - [ ] Implement retry strategy
    - [ ] Handle timeouts
    - [ ] Log errors appropriately
    - [ ] Monitor error rates

5. **Monitoring**
    - [ ] Track request times
    - [ ] Monitor error rates
    - [ ] Track memory usage
    - [ ] Monitor cache performance

## See Also

- [Basic Usage Guide](../user-guide/basic-usage.md)
- [Advanced Usage Guide](../user-guide/advanced-usage.md)
- [Error Handling Guide](../user-guide/error-handling.md)
- [API Reference](../api/client.md)