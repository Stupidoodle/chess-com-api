# Chess.com API Client

Welcome to the Chess.com API Client documentation! This library provides a modern, fully typed, asynchronous Python
wrapper for the Chess.com API.

## Features

- 🚀 **Fully Async**: Built with `aiohttp` for high-performance async operations
- 📦 **Type Safety**: Complete type hints and runtime type checking
- 🛡️ **Robust Error Handling**: Comprehensive error types and automatic retries
- 🔄 **Rate Limiting**: Built-in rate limit handling with smart backoff
- 📚 **Rich Data Models**: Intuitive object-oriented interface to API data
- ✨ **Modern Python**: Supports Python 3.8+
- 📈 **Production Ready**: Thoroughly tested and production hardened

## Quick Start

### Installation

```bash
pip install chess-com-api
```

### Basic Usage

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

## Documentation Structure

The documentation is organized into several sections:

- **Getting Started**: Basic installation and setup instructions
- **User Guide**: Detailed usage instructions and best practices
- **API Reference**: Complete API documentation
- **Examples**: Real-world usage examples
- **Contributing**: Guidelines for contributing to the project

## Support

If you encounter any problems or have questions:

1. Check the [Troubleshooting](user-guide/troubleshooting.md) guide
2. Search existing [GitHub Issues](https://github.com/Stupidoodle/chess-com-api/issues)
3. Create a new issue if your problem isn't already reported

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](contributing.md) for details on how to submit pull
requests, report issues, and contribute to the project.

## License

This project is licensed under the MIT License - see
the [LICENSE](https://github.com/Stupidoodle/chess-com-api/blob/main/LICENSE) file for details.

## Acknowledgments

- Chess.com for providing the public API
- The Python community for valuable feedback and contributions