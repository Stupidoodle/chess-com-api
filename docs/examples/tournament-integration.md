# Tournament Integration Examples

This guide provides practical examples for working with Chess.com tournaments using the API client.

## Basic Tournament Operations

### Getting Tournament Details

```python
import asyncio
from chess_com_api import ChessComClient
from datetime import datetime


async def get_tournament_info(tournament_id: str):
    async with ChessComClient() as client:
        try:
            tournament = await client.get_tournament(tournament_id)

            print(f"Tournament: {tournament.name}")
            print(f"Status: {tournament.status}")
            print(f"Type: {tournament.settings.type}")
            print(f"Time Control: {tournament.settings.time_control}")
            print(f"Total Players: {len(tournament.players)}")

            if tournament.finish_time:
                duration = tournament.finish_time - tournament.settings.start_time
                print(f"Duration: {duration.days} days, {duration.seconds // 3600} hours")

            return tournament
        except Exception as e:
            print(f"Error fetching tournament: {e}")
            return None
```

### Tournament Round Analysis

```python
async def analyze_tournament_round(tournament_id: str, round_num: int):
    async with ChessComClient() as client:
        round_info = await client.get_tournament_round(tournament_id, round_num)

        stats = {
            "total_players": len(round_info.players),
            "total_groups": len(round_info.group_urls),
            "games_completed": 0,
            "games_in_progress": 0,
            "results": {"wins_white": 0, "wins_black": 0, "draws": 0}
        }

        # Fetch all groups for the round
        await round_info.fetch_groups(client=client)

        for group in round_info.groups:
            for game in group.games:
                if game.end_time:
                    stats["games_completed"] += 1
                    if game.white.result == "win":
                        stats["results"]["wins_white"] += 1
                    elif game.black.result == "win":
                        stats["results"]["wins_black"] += 1
                    else:
                        stats["results"]["draws"] += 1
                else:
                    stats["games_in_progress"] += 1

        # Print analysis
        print(f"Round {round_num} Analysis:")
        print(f"Total Players: {stats['total_players']}")
        print(f"Total Groups: {stats['total_groups']}")
        print(f"\nGames Status:")
        print(f"Completed: {stats['games_completed']}")
        print(f"In Progress: {stats['games_in_progress']}")

        if stats["games_completed"] > 0:
            print("\nResults:")
            white_win_pct = (stats["results"]["wins_white"] / stats["games_completed"]) * 100
            black_win_pct = (stats["results"]["wins_black"] / stats["games_completed"]) * 100
            draw_pct = (stats["results"]["draws"] / stats["games_completed"]) * 100

            print(f"White Wins: {stats['results']['wins_white']} ({white_win_pct:.1f}%)")
            print(f"Black Wins: {stats['results']['wins_black']} ({black_win_pct:.1f}%)")
            print(f"Draws: {stats['results']['draws']} ({draw_pct:.1f}%)")
```

## Tournament Progress Tracking

### Track Player's Progress

```python
async def track_player_progress(username: str, tournament_id: str):
    async with ChessComClient() as client:
        tournament = await client.get_tournament(tournament_id)

        player_history = {
            "rounds_played": 0,
            "score": 0,
            "games": [],
            "opponents": []
        }

        # Fetch all rounds
        await tournament.fetch_rounds(client=client)

        for round_num, round_info in enumerate(tournament.rounds, 1):
            # Fetch groups for this round
            await round_info.fetch_groups(client=client)

            for group in round_info.groups:
                for game in group.games:
                    if (game.white.username.lower() == username.lower() or
                            game.black.username.lower() == username.lower()):
                        # Found a game with our player
                        is_white = game.white.username.lower() == username.lower()
                        player = game.white if is_white else game.black
                        opponent = game.black if is_white else game.white

                        game_info = {
                            "round": round_num,
                            "opponent": opponent.username,
                            "color": "white" if is_white else "black",
                            "result": player.result,
                            "url": game.url
                        }

                        player_history["games"].append(game_info)
                        player_history["opponents"].append(opponent.username)

                        if game.end_time:
                            player_history["rounds_played"] += 1
                            if player.result == "win":
                                player_history["score"] += 1
                            elif player.result == "draw":
                                player_history["score"] += 0.5

        # Print progress report
        print(f"Tournament Progress for {username}")
        print(f"Rounds Played: {player_history['rounds_played']}")
        print(f"Current Score: {player_history['score']}")

        print("\nGame History:")
        for game in player_history["games"]:
            print(f"\nRound {game['round']}:")
            print(f"vs {game['opponent']} ({game['color']})")
            print(f"Result: {game['result']}")
            print(f"Game URL: {game['url']}")
```

### Tournament Performance Analysis

```python
from collections import defaultdict


async def analyze_tournament_performance(tournament_id: str):
    async with ChessComClient() as client:
        tournament = await client.get_tournament(tournament_id)
        await tournament.fetch_rounds(client=client)

        performance_stats = defaultdict(lambda: {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "rating_performance": [],
            "opponents": []
        })

        for round_info in tournament.rounds:
            await round_info.fetch_groups(client=client)

            for group in round_info.groups:
                for game in group.games:
                    if not game.end_time:
                        continue

                    # Update stats for both players
                    for color in ["white", "black"]:
                        player = getattr(game, color)
                        opponent = game.black if color == "white" else game.white

                        stats = performance_stats[player.username]
                        stats["games_played"] += 1
                        stats["opponents"].append(opponent.username)
                        stats["rating_performance"].append(opponent.rating)

                        if player.result == "win":
                            stats["wins"] += 1
                        elif player.result == "loss":
                            stats["losses"] += 1
                        else:
                            stats["draws"] += 1

        # Print performance analysis
        print(f"Tournament Performance Analysis")
        print("=" * 40)

        for player, stats in performance_stats.items():
            if stats["games_played"] > 0:
                print(f"\nPlayer: {player}")
                print(f"Games Played: {stats['games_played']}")

                win_rate = (stats["wins"] / stats["games_played"]) * 100
                print(f"Record: +{stats['wins']}={stats['draws']}-{stats['losses']}")
                print(f"Win Rate: {win_rate:.1f}%")

                if stats["rating_performance"]:
                    avg_opp_rating = sum(stats["rating_performance"]) / len(stats["rating_performance"])
                    print(f"Average Opponent Rating: {avg_opp_rating:.0f}")

                    # Calculate performance rating
                    score_percentage = (stats["wins"] + stats["draws"] * 0.5) / stats["games_played"]
                    performance = avg_opp_rating + 400 * (2 * score_percentage - 1)
                    print(f"Performance Rating: {performance:.0f}")
```

## Advanced Tournament Operations

### Tournament Pairing Analysis

```python
async def analyze_pairings(tournament_id: str, round_num: int):
    async with ChessComClient() as client:
        round_info = await client.get_tournament_round(tournament_id, round_num)
        await round_info.fetch_groups(client=client)

        pairing_stats = {
            "rating_differences": [],
            "color_alternation": defaultdict(list),
            "rematch_count": 0
        }

        player_history = defaultdict(list)

        for group in round_info.groups:
            for game in group.games:
                # Rating difference analysis
                rating_diff = abs(game.white.rating - game.black.rating)
                pairing_stats["rating_differences"].append(rating_diff)

                # Color tracking
                pairing_stats["color_alternation"][game.white.username].append("white")
                pairing_stats["color_alternation"][game.black.username].append("black")

                # Check for rematches
                white_history = player_history[game.white.username]
                if game.black.username in white_history:
                    pairing_stats["rematch_count"] += 1

                # Update player history
                player_history[game.white.username].append(game.black.username)
                player_history[game.black.username].append(game.white.username)

        # Print analysis
        print(f"Pairing Analysis for Round {round_num}")

        if pairing_stats["rating_differences"]:
            avg_rating_diff = sum(pairing_stats["rating_differences"]) / len(pairing_stats["rating_differences"])
            max_rating_diff = max(pairing_stats["rating_differences"])
            print(f"\nRating Differences:")
            print(f"Average: {avg_rating_diff:.0f}")
            print(f"Maximum: {max_rating_diff}")

        print(f"\nRematches: {pairing_stats['rematch_count']}")

        print("\nColor Distribution:")
        for player, colors in pairing_stats["color_alternation"].items():
            white_count = colors.count("white")
            total = len(colors)
            print(f"{player}: {white_count}/{total} as White")
```

### Tournament State Manager

```python
class TournamentStateManager:
    def __init__(self, client: ChessComClient):
        self.client = client
        self.tournaments = {}
        self.updates = {}

    async def track_tournament(self, tournament_id: str):
        """Start tracking a tournament's state."""
        tournament = await self.client.get_tournament(tournament_id)
        self.tournaments[tournament_id] = tournament
        self.updates[tournament_id] = datetime.now()
        return tournament

    async def check_updates(self, tournament_id: str):
        """Check for tournament updates."""
        if tournament_id not in self.tournaments:
            return await self.track_tournament(tournament_id)

        current = await self.client.get_tournament(tournament_id)
        previous = self.tournaments[tournament_id]

        changes = {
            "status_changed": current.status != previous.status,
            "players_changed": len(current.players) != len(previous.players),
            "new_rounds": len(current.rounds or []) != len(previous.rounds or [])
        }

        self.tournaments[tournament_id] = current
        self.updates[tournament_id] = datetime.now()

        return current, changes


# Usage
async def monitor_tournament(tournament_id: str):
    async with ChessComClient() as client:
        manager = TournamentStateManager(client)

        while True:
            try:
                tournament, changes = await manager.check_updates(tournament_id)

                if any(changes.values()):
                    print(f"\nUpdates detected for {tournament.name}:")
                    if changes["status_changed"]:
                        print(f"Status changed to: {tournament.status}")
                    if changes["players_changed"]:
                        print(f"Player count: {len(tournament.players)}")
                    if changes["new_rounds"]:
                        print(f"Rounds updated: {len(tournament.rounds or [])}")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Error updating tournament: {e}")
                await asyncio.sleep(300)  # Back off on error
```

## See Also

- [Player Data Examples](player-data.md) - Examples for player analysis
- [Game Analysis Examples](game-analysis.md) - Examples for analyzing games
- [Basic Usage Guide](../user-guide/basic-usage.md) - Getting started guide