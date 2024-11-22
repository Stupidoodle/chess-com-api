# Chess.com API Client

[![PyPI version](https://badge.fury.io/py/chess-com-api.svg)](https://badge.fury.io/py/chess-com-api)
[![Python versions](https://img.shields.io/pypi/pyversions/chess-com-api.svg)](https://pypi.org/project/chess-com-api/)
[![Documentation Status](https://readthedocs.org/projects/chess-com-api/badge/?version=latest)](https://chess-com-api.readthedocs.io/en/latest/?badge=latest)
[![GitHub Actions](https://github.com/Stupidoodle/chess-com-api/workflows/CI/badge.svg)](https://github.com/Stupidoodle/chess-com-api/actions)
[![Coverage](https://codecov.io/gh/Stupidoodle/chess-com-api/branch/main/graph/badge.svg)](https://codecov.io/gh/Stupidoodle/chess-com-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, fully typed, asynchronous Python wrapper for the Chess.com API.

## Features

- 🚀 **Fully Async**: Built with `aiohttp` for high-performance async operations
- 📦 **Type Safety**: Complete type hints and runtime type checking
- 🛡️ **Robust Error Handling**: Comprehensive error types and automatic retries
- 🔄 **Rate Limiting**: Built-in rate limit handling with smart backoff
- 📚 **Rich Data Models**: Intuitive object-oriented interface to API data
- ✨ **Modern Python**: Supports Python 3.8+
- 📈 **Production Ready**: Thoroughly tested and production hardened

## Installation

```bash
pip install chess-com-api
```

## Quick Start

```python
import asyncio
from chess_com_api import ChessComClient

async def main():
    async with ChessComClient() as client:
        # Get player profile
        player = await client.get_player("hikaru")
        print(f"Title: {player.title}")
        print(f"Rating: {player.rating}")
        
        # Get recent games
        games = await client.get_player_current_games("hikaru")
        for game in games:
            print(f"Game URL: {game.url}")
            print(f"Time Control: {game.time_control}")

asyncio.run(main())
```

## Advanced Usage

### Custom Session Configuration

```python
import aiohttp
from chess_com_api import ChessComClient

async def main():
    # Configure custom timeout and headers
    timeout = aiohttp.ClientTimeout(total=60)
    session = aiohttp.ClientSession(
        timeout=timeout,
        headers={"User-Agent": "MyApp/1.0"}
    )
    
    client = ChessComClient(
        session=session,
        max_retries=5,
        rate_limit=100
    )
    
    try:
        # Your code here
        pass
    finally:
        await client.close()

asyncio.run(main())
```

### Error Handling

```python
from chess_com_api.exceptions import NotFoundError, RateLimitError

async def get_player_info(username: str):
    try:
        async with ChessComClient() as client:
            player = await client.get_player(username)
            return player
    except NotFoundError:
        print(f"Player {username} not found")
    except RateLimitError:
        print("Rate limit exceeded, please try again later")
    except Exception as e:
        print(f"An error occurred: {e}")
```

## Documentation

For full documentation, please visit [chess-com-api.readthedocs.io](https://chess-com-api.readthedocs.io/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Install development dependencies (`pip install -e ".[dev]"`)
4. Make your changes
5. Run tests (`pytest`)
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

Please make sure to update tests as appropriate and follow the existing code style.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Chess.com for providing the public API
- The Python community for valuable feedback and contributions

## Support

If you encounter any problems or have any questions, please [open an issue](https://github.com/Stupidoodle/chess-com-api/issues/new/choose) on GitHub.