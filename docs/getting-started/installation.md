# Installation

This guide will help you install the Chess.com API Client and set up your development environment.

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Basic Installation

Install the Chess.com API Client using pip:

```bash
pip install chess-com-api
```

## Development Installation

If you plan to contribute to the project or need the latest development version:

```bash
# Clone the repository
git clone https://github.com/Stupidoodle/chess-com-api.git
cd chess-com-api

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install with development dependencies
pip install -e ".[dev]"
```

## Verifying Installation

You can verify your installation by running Python and importing the package:

```python
import chess_com_api
print(chess_com_api.__version__)
```

## Dependencies

The package automatically installs these required dependencies:

- `aiohttp`: For async HTTP requests
- `typing-extensions`: For Python 3.8 compatibility (if needed)

## Optional Dependencies

Development dependencies include:

- `pytest`: For running tests
- `black`: For code formatting
- `mypy`: For type checking
- `ruff`: For linting
- `mkdocs`: For building documentation

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**:
   ```bash
   pip install --upgrade certifi
   ```

2. **Dependency Conflicts**:
   ```bash
   pip install -U chess-com-api --no-deps
   pip install -U aiohttp
   ```

3. **Python Version Issues**:
   Make sure you're using Python 3.8 or higher:
   ```bash
   python --version
   ```

### Platform-Specific Notes

=== "Windows"
```powershell
# If you see "execution policy" errors
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

=== "Linux"
```bash
# If you see permission errors
pip install --user chess-com-api
```

=== "macOS"
```bash
# If using Homebrew Python
python3 -m pip install chess-com-api
```

## Next Steps

After installation, check out the [Quick Start](quickstart.md) guide to begin using the library.