# Authentication

The Chess.com API primarily uses public endpoints that don't require authentication. However, this guide covers best
practices for working with the API and setting up your client properly.

## User Agent Configuration

While authentication isn't required, it's good practice to identify your application:

```python
import aiohttp
from chess_com_api import ChessComClient

async def main():
    headers = {
        "User-Agent": "MyApp/1.0 (contact@example.com)"
    }
    
    session = aiohttp.ClientSession(headers=headers)
    client = ChessComClient(session=session)
    
    try:
        # Your code here
        pass
    finally:
        await client.close()
```

## Rate Limiting

The Chess.com API has rate limits that you need to respect:

- Default limit: 100 requests per minute
- Bursts of up to 10 concurrent requests

The client handles these limits automatically, but you can customize them:

```python
client = ChessComClient(
    rate_limit=100,  # Maximum requests per minute
    max_retries=3    # Number of retries on rate limit
)
```

## Custom Session Configuration

You can customize the session for more advanced use cases:

```python
import aiohttp
import ssl

async def create_custom_client():
    # Create custom SSL context
    ssl_context = ssl.create_default_context()
    
    # Configure timeouts
    timeout = aiohttp.ClientTimeout(
        total=30,
        connect=10,
        sock_read=10
    )
    
    # Create session with custom configuration
    session = aiohttp.ClientSession(
        headers={
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json"
        },
        timeout=timeout,
        connector=aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=50  # Connection pool limit
        )
    )
    
    return ChessComClient(session=session)
```

## Proxy Support

If you need to use a proxy:

```python
async def create_proxy_client():
    connector = aiohttp.TCPConnector(
        ssl=False,  # Disable SSL verification if needed
        limit=50
    )
    
    session = aiohttp.ClientSession(
        connector=connector,
        trust_env=True  # Use environment proxy settings
    )
    
    return ChessComClient(session=session)
```

## Environment Variables

You can use environment variables for configuration:

```python
import os
from chess_com_api import ChessComClient

async def create_configured_client():
    headers = {
        "User-Agent": os.getenv("CHESS_COM_USER_AGENT", "MyApp/1.0"),
    }
    
    rate_limit = int(os.getenv("CHESS_COM_RATE_LIMIT", "100"))
    max_retries = int(os.getenv("CHESS_COM_MAX_RETRIES", "3"))
    
    session = aiohttp.ClientSession(headers=headers)
    return ChessComClient(
        session=session,
        rate_limit=rate_limit,
        max_retries=max_retries
    )
```

## Best Practices

1. **Always set a User-Agent**:
   ```python
   headers = {"User-Agent": "MyApp/1.0 (contact@example.com)"}
   ```

2. **Handle session lifecycle**:
   ```python
   async with ChessComClient() as client:
       # Your code here
       pass  # Session automatically closed
   ```

3. **Configure timeouts**:
   ```python
   timeout = aiohttp.ClientTimeout(total=30)
   session = aiohttp.ClientSession(timeout=timeout)
   ```

4. **Use retry mechanism**:
   ```python
   client = ChessComClient(max_retries=3)
   ```

5. **Handle rate limits gracefully**:
   ```python
   from chess_com_api.exceptions import RateLimitError
   
   try:
       result = await client.get_player("username")
   except RateLimitError:
       # Wait or notify user
       pass
   ```

## Security Considerations

1. **SSL Verification**:
    - Always verify SSL certificates in production
    - Only disable SSL verification for development/testing

2. **Proxy Usage**:
    - Use secure proxies when needed
    - Be careful with proxy authentication credentials

3. **Rate Limiting**:
    - Respect the API's rate limits
    - Implement backoff strategies for concurrent requests

## Next Steps

Now that you understand authentication and configuration, check out:

- [Basic Usage](../user-guide/basic-usage.md) for common operations
- [Advanced Usage](../user-guide/advanced-usage.md) for complex scenarios
- [Rate Limiting](../user-guide/rate-limiting.md) for detailed rate limit handling