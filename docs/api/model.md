# Models Reference

This document details all data models used in the Chess.com API client. All models are implemented as immutable
dataclasses with proper type hints.

## Player Models

### Player

Represents a Chess.com player profile.

```python
@dataclass(frozen=True)
class Player:
    username: str
    player_id: int
    title: Optional[str]
    status: str
    name: Optional[str]
    avatar: Optional[str]
    location: Optional[str]
    country: Optional[str]
    joined: datetime
    last_online: datetime
    followers: int
    is_streamer: Optional[bool] = False
    twitch_url: Optional[str] = None
    verified: Optional[bool] = False
```

#### Attributes

- `username`: Player's username
- `player_id`: Unique player identifier
- `title`: Chess title (GM, IM, FM, etc.) if any
- `status`: Account status (basic, premium, etc.)
- `name`: Player's real name (if provided)
- `avatar`: URL to player's avatar
- `location`: Player's location (if provided)
- `country`: Player's country code
- `joined`: Account creation date
- `last_online`: Last activity timestamp
- `followers`: Number of followers
- `is_streamer`: Whether player is a Chess.com streamer
- `twitch_url`: Player's Twitch URL if applicable
- `verified`: Account verification status

#### Example Usage

```python
player = await client.get_player("hikaru")
print(f"Title: {player.title}")
print(f"Joined: {player.joined.strftime('%Y-%m-%d')}")
```

### PlayerStats

Represents a player's statistics across different game types.

```python
@dataclass(frozen=True)
class PlayerStats:
    chess_daily: Optional[Dict[str, Any]]
    chess_rapid: Optional[Dict[str, Any]]
    chess_bullet: Optional[Dict[str, Any]]
    chess_blitz: Optional[Dict[str, Any]]
    fide: Optional[int]
    tactics: Optional[Dict[str, Any]]
    lessons: Optional[Dict[str, Any]]
    puzzle_rush: Optional[Dict[str, Any]]
```

#### Attributes

Each game type contains rating information:

- `last`: Last rating details
- `best`: Best rating achieved
- `record`: Win/loss record

#### Example Usage

```python
stats = await client.get_player_stats("hikaru")
blitz_rating = stats.chess_blitz["last"]["rating"]
best_bullet = stats.chess_bullet["best"]["rating"]
```

## Game Models

### Game

Represents a chess game.

```python
@dataclass(frozen=True)
class Game:
    url: str
    pgn: str
    time_control: str
    time_class: str
    rated: bool
    fen: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    rules: str
    white: GamePlayer
    black: GamePlayer
```

#### Attributes

- `url`: Game URL
- `pgn`: Game PGN notation
- `time_control`: Time control format
- `time_class`: Game time class (bullet, blitz, rapid, etc.)
- `rated`: Whether game is rated
- `fen`: Current position in FEN notation
- `start_time`: Game start timestamp
- `end_time`: Game end timestamp
- `rules`: Game ruleset
- `white`: White player information
- `black`: Black player information

### GamePlayer

Represents a player in a specific game.

```python
@dataclass(frozen=True)
class GamePlayer:
    username: str
    rating: int
    result: str
    user: Optional[Player] = None
```

## Tournament Models

### Tournament

Represents a Chess.com tournament.

```python
@dataclass(frozen=True)
class Tournament:
    name: str
    url: str
    description: str
    creator: str
    status: str
    finish_time: Optional[datetime]
    settings: TournamentSettings
    players: List[str]
    rounds: Optional[List[Round]] = None
```

### TournamentSettings

```python
@dataclass(frozen=True)
class TournamentSettings:
    type: str
    rules: str
    time_control: str
    time_class: str
    rated: bool
    start_time: datetime
    registration_cut_off: datetime
    advanced: Dict[str, Any]
```

### Round

```python
@dataclass(frozen=True)
class Round:
    players: List[str]
    games: List[Game]
    group_urls: List[str]
    groups: Optional[List[Group]] = None
```

## Club Models

### Club

Represents a Chess.com club.

```python
@dataclass(frozen=True)
class Club:
    id: str
    name: str
    description: str
    country: str
    created_at: datetime
    last_activity: datetime
    members_count: int
    admin_usernames: List[str]
    visibility: str
    join_request: str
```

### UserClub

Represents a club from a player's perspective.

```python
@dataclass(frozen=True)
class UserClub:
    name: str
    url: str
    joined: datetime
```

## Match Models

### Match

Represents a team match.

```python
@dataclass(frozen=True)
class Match:
    name: str
    url: str
    start_time: datetime
    status: str
    boards: List[Board]
```

### Board

```python
@dataclass(frozen=True)
class Board:
    board_number: int
    games: List[Game]
```

## Country Models

### Country

```python
@dataclass(frozen=True)
class Country:
    code: str
    name: str
```

### CountryClubs

```python
@dataclass(frozen=True)
class CountryClubs:
    club_urls: List[str]
    clubs: Optional[List[Club]] = None

    async def fetch_clubs(self, client: ChessComClient) -> List[Club]:
        """Fetch detailed club information."""
        pass
```

## Puzzle Models

### DailyPuzzle

```python
@dataclass(frozen=True)
class DailyPuzzle:
    title: str
    url: str
    pgn: str
    fen: str
    rating: int
    themes: List[str]
```

## Utility Models

### Streamer

```python
@dataclass(frozen=True)
class Streamer:
    username: str
    avatar: str
    twitch_url: str
    is_live: bool
```

### Leaderboard

```python
@dataclass(frozen=True)
class Leaderboard:
    daily: List[Dict[str, Any]]
    live_rapid: List[Dict[str, Any]]
    live_blitz: List[Dict[str, Any]]
    live_bullet: List[Dict[str, Any]]
    tactics: List[Dict[str, Any]]
```

## Model Utilities

### Fetch Methods

Many models include fetch methods to load related data:

```python
async def fetch_user(self, client: ChessComClient) -> Player:
    """Fetch full player details."""
    pass


async def fetch_clubs(self, client: ChessComClient) -> List[Club]:
    """Fetch detailed club information."""
    pass
```

### Factory Methods

Models include factory methods for creation from API data:

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> Self:
    """Create instance from API response data."""
    pass
```

## Best Practices

1. Always use type hints when working with models:
   ```python
   async def process_player(player: Player) -> None:
       pass
   ```

2. Use pattern matching for type-safe code:
   ```python
   match game.time_class:
       case "bullet":
           process_bullet_game(game)
       case "blitz":
           process_blitz_game(game)
       case _:
           process_other_game(game)
   ```

3. Handle optional fields appropriately:
   ```python
   if player.title is not None:
       print(f"Title: {player.title}")
   ```

4. Use fetch methods for related data:
   ```python
   game = await client.get_game(game_id)
   await game.white.fetch_user(client)
   await game.black.fetch_user(client)
   ```

## See Also

- [Client Reference](client.md) - API client documentation
- [Exceptions Reference](exceptions.md) - Error types documentation
- [Basic Usage](../user-guide/basic-usage.md) - Getting started guide