# Player Data Examples

This guide provides practical examples for working with player data using the Chess.com API client.

## Basic Player Information

### Getting Player Profile

```python
import asyncio
from chess_com_api import ChessComClient


async def get_player_info():
    async with ChessComClient() as client:
        player = await client.get_player("hikaru")

        print(f"Username: {player.username}")
        print(f"Title: {player.title}")
        print(f"Country: {player.country}")
        print(f"Followers: {player.followers}")
        print(f"Joined: {player.joined.strftime('%Y-%m-%d')}")

        if player.is_streamer:
            print(f"Twitch: {player.twitch_url}")


asyncio.run(get_player_info())
```

### Getting Multiple Players

```python
async def get_multiple_players(usernames: list[str]):
    async with ChessComClient() as client:
        players = []
        for username in usernames:
            try:
                player = await client.get_player(username)
                players.append(player)
                print(f"Found {player.username} ({player.title or 'Untitled'})")
            except Exception as e:
                print(f"Error fetching {username}: {e}")
        return players


# Usage
usernames = ["hikaru", "magnuscarlsen", "fabianocaruana"]
players = asyncio.run(get_multiple_players(usernames))
```

## Rating Information

### Complete Player Stats

```python
async def analyze_player_ratings(username: str):
    async with ChessComClient() as client:
        stats = await client.get_player_stats(username)

        # Extract ratings for each time control
        ratings = {
            "Blitz": stats.chess_blitz["last"]["rating"] if stats.chess_blitz else None,
            "Rapid": stats.chess_rapid["last"]["rating"] if stats.chess_rapid else None,
            "Bullet": stats.chess_bullet["last"]["rating"] if stats.chess_bullet else None
        }

        # Print ratings
        for time_control, rating in ratings.items():
            if rating:
                print(f"{time_control}: {rating}")

        # Check best ratings
        if stats.chess_blitz and "best" in stats.chess_blitz:
            best_blitz = stats.chess_blitz["best"]["rating"]
            print(f"Best Blitz Rating: {best_blitz}")
```

### Rating Comparison

```python
async def compare_players(player1: str, player2: str):
    async with ChessComClient() as client:
        # Get both players' stats concurrently
        stats1, stats2 = await asyncio.gather(
            client.get_player_stats(player1),
            client.get_player_stats(player2)
        )

        # Compare blitz ratings
        blitz1 = stats1.chess_blitz["last"]["rating"] if stats1.chess_blitz else 0
        blitz2 = stats2.chess_blitz["last"]["rating"] if stats2.chess_blitz else 0

        print(f"{player1} Blitz: {blitz1}")
        print(f"{player2} Blitz: {blitz2}")
        print(f"Difference: {abs(blitz1 - blitz2)}")
```

## Game History

### Recent Games Analysis

```python
async def analyze_recent_games(username: str):
    async with ChessComClient() as client:
        games = await client.get_player_current_games(username)

        stats = {
            "total": len(games),
            "white": 0,
            "black": 0,
            "time_controls": {}
        }

        for game in games:
            # Count games by color
            if game.white.username.lower() == username.lower():
                stats["white"] += 1
            else:
                stats["black"] += 1

            # Count games by time control
            stats["time_controls"][game.time_class] =
                stats["time_controls"].get(game.time_class, 0) + 1

        print(f"Total active games: {stats['total']}")
        print(f"Playing White: {stats['white']}")
        print(f"Playing Black: {stats['black']}")
        print("\nGames by time control:")
        for tc, count in stats["time_controls"].items():
            print(f"{tc.title()}: {count}")
```

### Monthly Games Archive

```python
from datetime import datetime, timedelta


async def get_monthly_games(username: str, year: int, month: int):
    async with ChessComClient() as client:
        games = await client.get_archived_games(username, year, month)

        results = {"wins": 0, "losses": 0, "draws": 0}

        for game in games:
            player_color = "white" if game.white.username.lower() == username.lower() else "black"
            player = game.white if player_color == "white" else game.black

            if player.result == "win":
                results["wins"] += 1
            elif player.result == "lose":
                results["losses"] += 1
            else:
                results["draws"] += 1

        total_games = sum(results.values())
        if total_games > 0:
            win_rate = (results["wins"] / total_games) * 100
            print(f"Games played in {year}-{month:02d}: {total_games}")
            print(f"Wins: {results['wins']}")
            print(f"Losses: {results['losses']}")
            print(f"Draws: {results['draws']}")
            print(f"Win rate: {win_rate:.1f}%")
```

## Advanced Analysis

### Rating Progress Tracker

```python
async def track_rating_progress(username: str, months: int = 12):
    async with ChessComClient() as client:
        # Get archives for the last N months
        archives = await client.get_player_game_archives(username)
        recent_archives = archives[-months:]

        ratings_over_time = []

        for archive_url in recent_archives:
            # Extract year and month from URL
            year = int(archive_url.split('/')[-2])
            month = int(archive_url.split('/')[-1])

            try:
                games = await client.get_archived_games(username, year, month)
                if games:
                    # Get ratings from each game
                    for game in games:
                        if game.white.username.lower() == username.lower():
                            rating = game.white.rating
                        else:
                            rating = game.black.rating

                        ratings_over_time.append({
                            'date': game.end_time,
                            'rating': rating,
                            'time_class': game.time_class
                        })
            except Exception as e:
                print(f"Error fetching games for {year}-{month}: {e}")
                continue

        # Analyze rating progression
        if ratings_over_time:
            for time_class in set(r['time_class'] for r in ratings_over_time):
                tc_ratings = [r for r in ratings_over_time if r['time_class'] == time_class]
                if tc_ratings:
                    first_rating = tc_ratings[0]['rating']
                    last_rating = tc_ratings[-1]['rating']
                    change = last_rating - first_rating

                    print(f"\n{time_class.title()} Rating Progress:")
                    print(f"Starting: {first_rating}")
                    print(f"Current: {last_rating}")
                    print(f"Change: {change:+d}")
```

### Performance Analysis

```python
async def analyze_performance(username: str, year: int, month: int):
    async with ChessComClient() as client:
        games = await client.get_archived_games(username, year, month)

        performance = {
            'time_controls': {},
            'colors': {'white': 0, 'black': 0},
            'average_rating': 0,
            'total_games': len(games)
        }

        total_rating = 0
        rating_count = 0

        for game in games:
            # Track time controls
            tc = game.time_class
            if tc not in performance['time_controls']:
                performance['time_controls'][tc] = {
                    'games': 0, 'wins': 0, 'losses': 0, 'draws': 0
                }

            performance['time_controls'][tc]['games'] += 1

            # Track colors
            color = 'white' if game.white.username.lower() == username.lower() else 'black'
            performance['colors'][color] += 1

            # Track results
            player = game.white if color == 'white' else game.black
            if player.result == 'win':
                performance['time_controls'][tc]['wins'] += 1
            elif player.result == 'lose':
                performance['time_controls'][tc]['losses'] += 1
            else:
                performance['time_controls'][tc]['draws'] += 1

            # Track ratings
            total_rating += player.rating
            rating_count += 1

        if rating_count > 0:
            performance['average_rating'] = total_rating / rating_count

        # Print analysis
        print(f"Performance Analysis for {year}-{month}")
        print(f"Total Games: {performance['total_games']}")
        print(f"Average Rating: {performance['average_rating']:.0f}")
        print("\nResults by Time Control:")
        for tc, results in performance['time_controls'].items():
            win_rate = (results['wins'] / results['games']) * 100
            print(f"\n{tc.title()}:")
            print(f"Games: {results['games']}")
            print(f"W/L/D: {results['wins']}/{results['losses']}/{results['draws']}")
            print(f"Win Rate: {win_rate:.1f}%")
```

## See Also

- [Game Analysis Examples](game-analysis.md) - Examples for analyzing games
- [Tournament Integration](tournament-integration.md) - Tournament-related examples
- [Basic Usage Guide](../user-guide/basic-usage.md) - Getting started guide