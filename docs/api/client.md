# Client API Reference

The `ChessComClient` class is the main interface for interacting with the Chess.com API. This document provides detailed
information about all available methods and their usage.

## ChessComClient

### Constructor

```python
def __init__(
    self,
    session: Optional[aiohttp.ClientSession] = None,
    timeout: int = 30,
    max_retries: int = 3,
    rate_limit: int = 300
) -> None
```

Creates a new Chess.com API client instance.

#### Parameters

- `session` (Optional[aiohttp.ClientSession]): Custom aiohttp session. If not provided, a new session will be created.
- `timeout` (int): Request timeout in seconds. Default: 30
- `max_retries` (int): Maximum number of retry attempts. Default: 3
- `rate_limit` (int): Maximum concurrent requests. Default: 300

#### Example

```python
import aiohttp
from chess_com_api import ChessComClient

# Basic usage
client = ChessComClient()

# Custom configuration
session = aiohttp.ClientSession(
    headers={"User-Agent": "MyApp/1.0"}
)
client = ChessComClient(
    session=session,
    timeout=60,
    max_retries=5
)
```

### Player Methods

#### get_player

```python
async def get_player(self, username: str) -> Player
```

Get profile information for a player.

#### Parameters

- `username` (str): The username of the player

#### Returns

- `Player`: Player profile information

#### Raises

- `NotFoundError`: If the player doesn't exist
- `ValidationError`: If the username is invalid

#### Example

```python
player = await client.get_player("hikaru")
print(f"Title: {player.title}")
print(f"Rating: {player.rating}")
```

#### get_player_stats

```python
async def get_player_stats(self, username: str) -> PlayerStats
```

Get statistics for a player.

#### Parameters

- `username` (str): The username of the player

#### Returns

- `PlayerStats`: Player statistics including ratings for different game types

#### Example

```python
stats = await client.get_player_stats("hikaru")
blitz_rating = stats.chess_blitz["last"]["rating"]
```

#### get_player_current_games

```python
async def get_player_current_games(self, username: str) -> List[Game]
```

Get a player's current games.

#### Parameters

- `username` (str): The username of the player

#### Returns

- `List[Game]`: List of current games

#### Example

```python
games = await client.get_player_current_games("hikaru")
for game in games:
    print(f"Game URL: {game.url}")
```

#### get_player_to_move_games

```python
async def get_player_to_move_games(self, username: str) -> List[DailyGame]
```

Get a player's games where it's their turn to move.

#### Parameters

- `username` (str): The username of the player

#### Returns

- `List[DailyGame]`: List of games where it's the player's turn

### Tournament Methods

#### get_tournament

```python
async def get_tournament(self, url_id: str) -> Tournament
```

Get tournament details.

#### Parameters

- `url_id` (str): The tournament's URL identifier

#### Returns

- `Tournament`: Tournament information

#### Example

```python
tournament = await client.get_tournament("tournament-id")
print(f"Name: {tournament.name}")
```

#### get_tournament_round

```python
async def get_tournament_round(
    self,
    url_id: str,
    round_num: int
) -> Round
```

Get details for a specific tournament round.

#### Parameters

- `url_id` (str): The tournament's URL identifier
- `round_num` (int): The round number

#### Returns

- `Round`: Round information

### Club Methods

#### get_club

```python
async def get_club(self, url_id: str) -> Club
```

Get club details.

#### Parameters

- `url_id` (str): The club's URL identifier

#### Returns

- `Club`: Club information

#### Example

```python
club = await client.get_club("chess-com-developer-community")
print(f"Members: {club.members_count}")
```

#### get_club_members

```python
async def get_club_members(self, url_id: str) -> Dict[str, List[str]]
```

Get club members.

#### Parameters

- `url_id` (str): The club's URL identifier

#### Returns

- `Dict[str, List[str]]`: Dictionary of member lists by category

### Country Methods

#### get_country

```python
async def get_country(self, iso_code: str) -> Country
```

Get country details.

#### Parameters

- `iso_code` (str): The country's ISO code

#### Returns

- `Country`: Country information

#### Example

```python
country = await client.get_country("US")
print(f"Name: {country.name}")
```

#### get_country_players

```python
async def get_country_players(self, iso_code: str) -> List[str]
```

Get players from a specific country.

#### Parameters

- `iso_code` (str): The country's ISO code

#### Returns

- `List[str]`: List of player usernames

#### get_country_clubs

```python
async def get_country_clubs(self, iso_code: str) -> CountryClubs
```

Get clubs from a specific country.

#### Parameters

- `iso_code` (str): The country's ISO code

#### Returns

- `CountryClubs`: Country clubs information

### Match Methods

#### get_match

```python
async def get_match(self, match_id: int) -> Match
```

Get team match details.

#### Parameters

- `match_id` (int): The match identifier

#### Returns

- `Match`: Match information

#### get_match_board

```python
async def get_match_board(
    self,
    match_id: int,
    board_num: int
) -> Board
```

Get team match board details.

#### Parameters

- `match_id` (int): The match identifier
- `board_num` (int): The board number

#### Returns

- `Board`: Board information

### Puzzle Methods

#### get_daily_puzzle

```python
async def get_daily_puzzle(self) -> DailyPuzzle
```

Get the daily puzzle.

#### Returns

- `DailyPuzzle`: Daily puzzle information

#### Example

```python
puzzle = await client.get_daily_puzzle()
print(f"Title: {puzzle.title}")
print(f"FEN: {puzzle.fen}")
```

#### get_random_puzzle

```python
async def get_random_puzzle(self) -> DailyPuzzle
```

Get a random puzzle.

#### Returns

- `DailyPuzzle`: Random puzzle information

### Streamer Methods

#### get_streamers

```python
async def get_streamers(self) -> List[Streamer]
```

Get Chess.com streamers.

#### Returns

- `List[Streamer]`: List of Chess.com streamers

### Leaderboard Methods

#### get_leaderboards

```python
async def get_leaderboards(self) -> Leaderboard
```

Get Chess.com leaderboards.

#### Returns

- `Leaderboard`: Leaderboard information for various game types

### Helper Methods

#### close

```python
async def close(self) -> None
```

Close the client session.

#### Example

```python
await client.close()
```

### Context Manager Support

The client supports the async context manager protocol:

```python
async with ChessComClient() as client:
    player = await client.get_player("hikaru")
```

## Error Handling

All methods may raise the following exceptions:

- `NotFoundError`: Resource not found
- `RateLimitError`: Rate limit exceeded
- `ValidationError`: Invalid input parameters
- `RedirectError`: Resource moved
- `GoneError`: Resource no longer available
- `ChessComAPIError`: Base class for all API errors

Example error handling:

```python
try:
    player = await client.get_player("username")
except NotFoundError:
    print("Player not found")
except RateLimitError:
    print("Rate limit exceeded")
except ChessComAPIError as e:
    print(f"API error: {e}")
```

## Best Practices

1. Always use the context manager when possible:
   ```python
   async with ChessComClient() as client:
       # Your code here
       pass
   ```

2. Set appropriate timeouts for your use case:
   ```python
   client = ChessComClient(timeout=60)  # Longer timeout for bulk operations
   ```

3. Handle rate limits properly:
   ```python
   client = ChessComClient(max_retries=50)  # More retries for bulk operations
   ```

4. Set a descriptive User-Agent:
   ```python
   session = aiohttp.ClientSession(
       headers={"User-Agent": "MyApp/1.0 (contact@example.com)"}
   )
   client = ChessComClient(session=session)
   ```

## See Also

- [Models Reference](models.md) - Data model documentation
- [Exceptions Reference](exceptions.md) - Error types documentation
- [Rate Limiting Guide](../user-guide/rate-limiting.md) - Detailed rate limiting information