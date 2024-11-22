# Game Analysis Examples

This guide provides practical examples for analyzing chess games using the Chess.com API client.

## Current Games Analysis

### Fetching Active Games

```python
import asyncio
from chess_com_api import ChessComClient
from datetime import datetime, timezone


async def get_active_games(username: str):
    async with ChessComClient() as client:
        games = await client.get_player_current_games(username)

        print(f"Active Games for {username}:")
        for game in games:
            # Get opponent's username
            opponent = game.black if game.white.username.lower() == username.lower() else game.white

            # Format duration since game started
            duration = datetime.now(timezone.utc) - game.start_time
            duration_hours = duration.total_seconds() / 3600

            print(f"\nGame URL: {game.url}")
            print(f"Opponent: {opponent.username} ({opponent.rating})")
            print(f"Time Control: {game.time_control}")
            print(f"Game Duration: {duration_hours:.1f} hours")
```

### Games To Move Analysis

```python
async def analyze_games_to_move(username: str):
    async with ChessComClient() as client:
        games = await client.get_player_to_move_games(username)

        stats = {
            "total": len(games),
            "by_time_control": {},
            "by_remaining_time": [],
            "by_color": {"white": 0, "black": 0}
        }

        for game in games:
            # Track games by time control
            tc = game.time_control
            stats["by_time_control"][tc] = stats["by_time_control"].get(tc, 0) + 1

            # Track color distribution
            color = "white" if game.white.username.lower() == username.lower() else "black"
            stats["by_color"][color] += 1

            # Track games by remaining time (for timed games)
            if hasattr(game, "remaining_time"):
                stats["by_remaining_time"].append({
                    "url": game.url,
                    "remaining": game.remaining_time
                })

        # Print analysis
        print(f"Games to Move: {stats['total']}")
        print("\nBy Time Control:")
        for tc, count in stats["by_time_control"].items():
            print(f"{tc}: {count} games")

        print("\nBy Color:")
        print(f"White: {stats['by_color']['white']}")
        print(f"Black: {stats['by_color']['black']}")

        if stats["by_remaining_time"]:
            print("\nLow Time Games (< 1 minute):")
            for game in stats["by_remaining_time"]:
                if game["remaining"] < 60:
                    print(f"Game {game['url']}: {game['remaining']}s remaining")
```

## Historical Game Analysis

### Monthly Games Analysis

```python
async def analyze_monthly_games(username: str, year: int, month: int):
    async with ChessComClient() as client:
        games = await client.get_archived_games(username, year, month)

        analysis = {
            "total_games": len(games),
            "results": {"wins": 0, "losses": 0, "draws": 0},
            "time_controls": {},
            "openings": {},
            "avg_game_length": 0,
            "rating_change": {"start": None, "end": None}
        }

        total_moves = 0

        for game in games:
            # Determine player's color and result
            is_white = game.white.username.lower() == username.lower()
            player = game.white if is_white else game.black
            opponent = game.black if is_white else game.white

            # Track results
            if player.result == "win":
                analysis["results"]["wins"] += 1
            elif player.result == "lose":
                analysis["results"]["losses"] += 1
            else:
                analysis["results"]["draws"] += 1

            # Track time controls
            tc = game.time_control
            if tc not in analysis["time_controls"]:
                analysis["time_controls"][tc] = {
                    "games": 0, "wins": 0, "losses": 0, "draws": 0,
                    "rating_change": 0
                }
            analysis["time_controls"][tc]["games"] += 1

            # Track rating changes
            if analysis["rating_change"]["start"] is None:
                analysis["rating_change"]["start"] = player.rating
            analysis["rating_change"]["end"] = player.rating

            # Count moves from PGN
            moves = len([m for m in game.pgn.split() if not m.startswith("{") and not m.startswith("(")])
            total_moves += moves

            # Extract opening if available
            opening = game.pgn.split("]")[0].split('"')[-2] if "[Opening " in game.pgn else "Unknown"
            analysis["openings"][opening] = analysis["openings"].get(opening, 0) + 1

        # Calculate averages
        if analysis["total_games"] > 0:
            analysis["avg_game_length"] = total_moves / analysis["total_games"]

        # Print analysis
        print(f"Analysis for {year}-{month:02d}")
        print(f"Total Games: {analysis['total_games']}")
        print("\nResults:")
        for result, count in analysis["results"].items():
            percentage = (count / analysis["total_games"]) * 100 if analysis["total_games"] > 0 else 0
            print(f"{result.title()}: {count} ({percentage:.1f}%)")

        print("\nTime Controls:")
        for tc, data in analysis["time_controls"].items():
            win_rate = (data["wins"] / data["games"]) * 100 if data["games"] > 0 else 0
            print(f"\n{tc}:")
            print(f"Games: {data['games']}")
            print(f"Win Rate: {win_rate:.1f}%")

        print("\nMost Common Openings:")
        sorted_openings = sorted(analysis["openings"].items(), key=lambda x: x[1], reverse=True)
        for opening, count in sorted_openings[:5]:
            print(f"{opening}: {count} games")

        if analysis["rating_change"]["start"] and analysis["rating_change"]["end"]:
            rating_change = analysis["rating_change"]["end"] - analysis["rating_change"]["start"]
            print(f"\nRating Change: {rating_change:+d}")

        print(f"\nAverage Game Length: {analysis['avg_game_length']:.1f} moves")
```

### Opening Analysis

```python
from collections import defaultdict


async def analyze_openings(username: str, year: int, month: int):
    async with ChessComClient() as client:
        games = await client.get_archived_games(username, year, month)

        opening_stats = defaultdict(lambda: {
            "total": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "white": 0,
            "black": 0,
            "avg_rating": 0,
            "performance": 0
        })

        for game in games:
            # Extract opening from PGN
            pgn = game.pgn
            opening = next((line.split('"')[1] for line in pgn.split("\n")
                            if line.startswith('[Opening "')), "Unknown")

            # Determine player's color and result
            is_white = game.white.username.lower() == username.lower()
            player = game.white if is_white else game.black
            opponent = game.black if is_white else game.white

            # Update statistics
            stats = opening_stats[opening]
            stats["total"] += 1
            stats["white" if is_white else "black"] += 1

            if player.result == "win":
                stats["wins"] += 1
            elif player.result == "lose":
                stats["losses"] += 1
            else:
                stats["draws"] += 1

            # Update rating statistics
            stats["avg_rating"] = (
                    (stats["avg_rating"] * (stats["total"] - 1) + opponent.rating)
                    / stats["total"]
            )

        # Calculate performance for each opening
        for opening, stats in opening_stats.items():
            if stats["total"] > 0:
                win_rate = (stats["wins"] + stats["draws"] * 0.5) / stats["total"]
                avg_opp_rating = stats["avg_rating"]
                stats["performance"] = avg_opp_rating + 400 * (2 * win_rate - 1)

        # Print analysis
        print(f"Opening Analysis for {username} ({year}-{month:02d})")
        print("\nTop Openings by Games Played:")
        sorted_by_games = sorted(
            opening_stats.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )

        for opening, stats in sorted_by_games[:10]:
            win_rate = (stats["wins"] / stats["total"]) * 100
            print(f"\n{opening}:")
            print(f"Games: {stats['total']}")
            print(f"Results: +{stats['wins']}={stats['draws']}-{stats['losses']}")
            print(f"Win Rate: {win_rate:.1f}%")
            print(f"As White: {stats['white']}, As Black: {stats['black']}")
            print(f"Avg Opponent Rating: {stats['avg_rating']:.0f}")
            print(f"Performance Rating: {stats['performance']:.0f}")
```

### Time Usage Analysis

```python
async def analyze_time_usage(username: str, year: int, month: int):
    async with ChessComClient() as client:
        games = await client.get_archived_games(username, year, month)

        time_data = {
            "blitz": {"games": [], "avg_time_per_move": []},
            "rapid": {"games": [], "avg_time_per_move": []},
            "bullet": {"games": [], "avg_time_per_move": []}
        }

        for game in games:
            # Skip games without timing information
            if not hasattr(game, "clocks"):
                continue

            # Calculate average time per move
            total_time = sum(game.clocks)
            num_moves = len(game.clocks)
            if num_moves > 0:
                avg_time = total_time / num_moves
                time_data[game.time_class]["games"].append(game)
                time_data[game.time_class]["avg_time_per_move"].append(avg_time)

        # Print analysis
        for time_class, data in time_data.items():
            if data["games"]:
                print(f"\n{time_class.title()} Games Analysis:")
                print(f"Total Games: {len(data['games'])}")
                avg_time = sum(data["avg_time_per_move"]) / len(data["games"])
                print(f"Average Time per Move: {avg_time:.1f}s")

                # Time management analysis
                critical_games = [
                    g for g in data["games"]
                    if hasattr(g, "timeouts") and g.timeouts > 0
                ]
                if critical_games:
                    print(f"Games with Time Issues: {len(critical_games)}")
```

## See Also

- [Player Data Examples](player-data.md) - Examples for player analysis
- [Tournament Integration](tournament-integration.md) - Tournament-related examples
- [Basic Usage Guide](../user-guide/basic-usage.md) - Getting started guide