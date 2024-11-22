# Rate Limiting

This guide explains Chess.com's rate limiting policy and how to handle parallel requests effectively using our client
library.

## Understanding Chess.com's Rate Limiting

Chess.com's API has a fairly liberal rate limiting policy:

- **Serial Requests**: No rate limit when making requests serially (waiting for each response before making the next
  request)
- **Parallel Requests**: May receive `429 Too Many Requests` responses when making concurrent requests
- **Application Blocking**: Possible for abnormal or suspicious activity

## Client Configuration

The client includes built-in handling for parallel requests:

```python
from chess_com_api import ChessComClient

# Default configuration optimized for most use cases
client = ChessComClient(
    rate_limit=300,     # Maximum concurrent requests
    max_retries=3       # Default retries for simple requests
)
```

## Handling Bulk Operations

For operations that involve fetching multiple resources (like country clubs), you might need more retries:

```python
# For bulk operations
client = ChessComClient(
    rate_limit=300,
    max_retries=50     # Increased retries for bulk operations
)
```

### Practical Implementation

Here's a proven implementation for fetching multiple resources in parallel:

```python
import asyncio
from typing import List, Optional
from chess_com_api.exceptions import RateLimitError

class BulkFetcher:
    async def fetch_clubs(self, client: ChessComClient, club_urls: List[str]) -> List[Club]:
        seen_club_ids = set()
        fetched_clubs = []

        async def fetch_club(club_url: str) -> Optional[Club]:
            club_id = club_url.split("/")[-1]
            if club_id in seen_club_ids:
                return None  # Skip duplicates
            
            try:
                print(f"Fetching club with ID: {club_id}")
                club = await client.get_club(url_id=club_id)
                seen_club_ids.add(club_id)
                return club
            except RateLimitError:
                print(f"Rate limit hit while fetching club {club_id}. Retrying...")
                await asyncio.sleep(2)  # Fixed backoff
                return await fetch_club(club_url)  # Retry with built-in mechanism
            except Exception as e:
                print(f"Error fetching club {club_id}: {e}")
                return None

        # Execute fetches concurrently
        tasks = [fetch_club(url) for url in club_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if isinstance(result, Club):
                print(f"Fetched club: {result.name}")
                fetched_clubs.append(result)
            elif isinstance(result, Exception):
                print(f"Failed to fetch club: {result}")

        return fetched_clubs

# Usage example
async def get_country_clubs(country_code: str):
    client = ChessComClient(max_retries=50)  # Increased retries for bulk operation
    try:
        country_clubs = await client.get_country_clubs(country_code)
        fetcher = BulkFetcher()
        clubs = await fetcher.fetch_clubs(client, country_clubs.club_urls)
        print(f"Successfully fetched {len(clubs)} clubs")
        return clubs
    finally:
        await client.close()
```

## Best Practices

1. **Adjust Retries Based on Operation**
    - Use default 3 retries for simple operations
    - Increase to 50 retries for bulk operations (e.g., country clubs)
    - Consider the operation's scope when setting retries

2. **Implement Smart Backoff**
   ```python
   async def smart_backoff(attempt: int) -> None:
       base_delay = 2
       max_delay = 30
       delay = min(base_delay * (2 ** attempt), max_delay)
       await asyncio.sleep(delay)
   ```

3. **Track and Log Operations**
   ```python
   class OperationTracker:
       def __init__(self):
           self.start_time = time.time()
           self.success_count = 0
           self.error_count = 0
           self.retry_count = 0

       def log_progress(self):
           elapsed = time.time() - self.start_time
           print(f"Progress: {self.success_count} successful, "
                 f"{self.error_count} failed, "
                 f"{self.retry_count} retries, "
                 f"elapsed time: {elapsed:.2f}s")
   ```

4. **Handle Different Resource Types**
   ```python
   async def bulk_fetch(
       client: ChessComClient,
       urls: List[str],
       fetch_func: Callable,
       max_retries: int = 50
   ):
       client.max_retries = max_retries
       results = []
       
       for url in urls:
           try:
               result = await fetch_func(url)
               results.append(result)
           except RateLimitError:
               print(f"Rate limit hit for {url}")
               await asyncio.sleep(2)
               # Retry with existing mechanism
               results.append(await fetch_func(url))
           except Exception as e:
               print(f"Error fetching {url}: {e}")
               
       return results
   ```

## Practical Tips

1. **Set Appropriate User-Agent**
   ```python
   headers = {
       "User-Agent": "MyApp/1.0 (contact@example.com)"
   }
   session = aiohttp.ClientSession(headers=headers)
   client = ChessComClient(session=session)
   ```

2. **Monitor Long Operations**
   ```python
   async def monitored_bulk_operation(urls: List[str]):
       start_time = time.time()
       results = []
       
       for i, url in enumerate(urls, 1):
           result = await fetch_resource(url)
           results.append(result)
           
           if i % 10 == 0:  # Log progress every 10 items
               elapsed = time.time() - start_time
               print(f"Processed {i}/{len(urls)} items in {elapsed:.2f}s")
               
       return results
   ```

3. **Handle Session Lifecycle**
   ```python
   async def safe_bulk_operation():
       async with ChessComClient(max_retries=50) as client:
           try:
               return await client.get_country_clubs("US")
           except Exception as e:
               print(f"Operation failed: {e}")
               return None
   ```

## Common Scenarios

1. **Fetching Country Clubs**
    - Expect operation to take 1+ minutes
    - Use 50 retries for reliability
    - Implement progress tracking

2. **Tournament Data**
    - Similar to country clubs
    - May require multiple nested requests
    - Consider implementing caching

3. **Player Games**
    - Usually faster than club operations
    - Standard retry configuration usually sufficient
    - Consider pagination if available

Remember that Chess.com's rate limiting is primarily focused on parallel request management rather than strict request
counts. The key is to handle `429` responses gracefully and implement appropriate retry mechanisms.