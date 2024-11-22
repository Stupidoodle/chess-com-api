# Frequently Asked Questions

This document addresses common questions and concerns about using the Chess.com API client.

## General Questions

### What Python versions are supported?

The client supports Python 3.8 and higher. We recommend using the latest stable Python version for optimal performance
and security.

### Is this an official Chess.com package?

No, this is an unofficial Python wrapper for the Chess.com API. While we follow Chess.com's API guidelines and best
practices, this is a community-maintained project.

### Do I need authentication to use this client?

No, Chess.com's public API doesn't require authentication. However, you should always set a proper User-Agent header to
identify your application.

## Technical Questions

### How do I handle rate limiting?

The client handles rate limiting automatically with built-in retry mechanisms. You can configure the behavior:

```python
client = ChessComClient(
    rate_limit=300,  # Maximum concurrent requests
    max_retries=3    # Number of retries
)
```

### Why am I getting connection errors?

Common causes include:

1. Network connectivity issues
2. Rate limiting
3. Invalid requests

Example handling:

```python
try:
    async with ChessComClient() as client:
        player = await client.get_player("username")
except aiohttp.ClientError as e:
    print(f"Connection error: {e}")
```

### How do I optimize performance for bulk operations?

For bulk operations:

1. Use concurrent requests with `asyncio.gather()`
2. Implement proper error handling
3. Consider using the bulk fetch utilities

Example:

```python
async def fetch_multiple_players(usernames: List[str]):
    async with ChessComClient() as client:
        tasks = [client.get_player(username) for username in usernames]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

## Common Issues

### "RuntimeError: Event loop is closed"

This typically occurs when not properly handling async/await. Solution:

```python
import asyncio

async def main():
    async with ChessComClient() as client:
        return await client.get_player("username")

# Correct way to run
result = asyncio.run(main())
```

### "SSL Certificate Verification Failed"

This can occur in certain environments. Solution:

```python
import ssl
import aiohttp

ssl_context = ssl.create_default_context()
connector = aiohttp.TCPConnector(ssl=ssl_context)
session = aiohttp.ClientSession(connector=connector)
client = ChessComClient(session=session)
```

### Memory Usage in Long-Running Applications

For long-running applications, manage resources properly:

```python
async def efficient_processing():
    async with ChessComClient() as client:
        # Process in batches
        batch_size = 100
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            await process_batch(client, batch)
            # Allow garbage collection
            await asyncio.sleep(0)
```

## Best Practices

### Proper Exception Handling

Always handle specific exceptions:

```python
from chess_com_api.exceptions import (
    NotFoundError,
    RateLimitError,
    ChessComAPIError
)

try:
    result = await client.get_player("username")
except NotFoundError:
    # Handle missing resource
    pass
except RateLimitError:
    # Handle rate limiting
    pass
except ChessComAPIError:
    # Handle other API errors
    pass
```

### Resource Cleanup

Always use context managers:

```python
async with ChessComClient() as client:
    # Your code here
    pass  # Resources automatically cleaned up
```

### Type Checking

Use type hints and verify with mypy:

```python
from typing import List, Optional
from chess_com_api.models import Player

async def get_players(
    usernames: List[str]
) -> List[Optional[Player]]:
    async with ChessComClient() as client:
        results = []
        for username in usernames:
            try:
                player = await client.get_player(username)
                results.append(player)
            except NotFoundError:
                results.append(None)
        return results
```

## Deployment Questions

### How do I configure logging in production?

Use structured logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chess_com_api.log'),
        logging.StreamHandler()
    ]
)
```

### How do I monitor API usage?

Implement custom metrics:

```python
from dataclasses import dataclass, field
from typing import Dict
import time

@dataclass
class APIMetrics:
    request_count: int = 0
    error_count: int = 0
    response_times: Dict[str, float] = field(default_factory=dict)

metrics = APIMetrics()

async def monitored_request(client: ChessComClient, username: str):
    start_time = time.time()
    try:
        result = await client.get_player(username)
        metrics.request_count += 1
        metrics.response_times[username] = time.time() - start_time
        return result
    except Exception:
        metrics.error_count += 1
        raise
```

## Contributing Questions

### How do I run tests?

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=chess_com_api
```

### How do I submit changes?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

See the [Contributing Guide](../contributing.md) for detailed instructions.

## Support and Help

### Where can I get help?

1. Create an issue on GitHub
2. Check existing documentation
3. Look for similar issues in closed GitHub issues

### How do I report security issues?

Please refer to our [Security Policy](../../SECURITY.md) for reporting security issues.

## See Also

- [Basic Usage Guide](basic-usage.md)
- [Advanced Usage Guide](advanced-usage.md)
- [API Reference](../api/client.md)
- [Contributing Guide](../contributing.md)