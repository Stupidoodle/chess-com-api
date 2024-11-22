# Testing Guide

This guide covers all aspects of testing the Chess.com API client, including unit tests, integration tests, and test
automation.

## Testing Setup

### Prerequisites

The testing framework uses:

- pytest: Main testing framework
- pytest-asyncio: For testing async code
- pytest-cov: For coverage reporting
- pytest-mock: For mocking

```bash
# Install development dependencies including test requirements
pip install -e ".[dev]"
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py

# Run specific test function
pytest tests/test_client.py::test_get_player
```

### Running with Coverage

```bash
# Run tests with coverage report
pytest --cov=chess_com_api

# Generate HTML coverage report
pytest --cov=chess_com_api --cov-report=html

# Generate XML coverage report (for CI/CD)
pytest --cov=chess_com_api --cov-report=xml
```

### Test Categories

```bash
# Run only unit tests
pytest tests -m "not integration"

# Run only integration tests
pytest tests -m integration

# Run slow tests
pytest tests -m slow
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from chess_com_api import ChessComClient
from chess_com_api.exceptions import NotFoundError


@pytest.mark.asyncio
async def test_get_player():
    async with ChessComClient() as client:
        # Arrange
        username = "hikaru"

        # Act
        player = await client.get_player(username)

        # Assert
        assert player.username == username
        assert player.title == "GM"
```

### Test Fixtures

```python
# conftest.py
import pytest
from chess_com_api import ChessComClient


@pytest.fixture
async def client():
    """Create test client instance."""
    async with ChessComClient(max_retries=3) as client:
        yield client


@pytest.fixture
def player_data():
    """Sample player data."""
    return {
        "username": "hikaru",
        "title": "GM",
        "player_id": 15448422,
        "status": "premium",
        "joined": 1389043258,
        "last_online": 1732135306
    }


# Using fixtures in tests
@pytest.mark.asyncio
async def test_get_player_stats(client, player_data):
    player = await client.get_player(player_data["username"])
    assert player.username == player_data["username"]
```

### Mocking External Calls

```python
import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_get_player_with_mock(mocker):
    # Mock the _make_request method
    mock_response = {
        "username": "hikaru",
        "title": "GM",
        "status": "premium"
    }

    mock_request = AsyncMock(return_value=mock_response)

    async with ChessComClient() as client:
        mocker.patch.object(client, '_make_request', mock_request)

        player = await client.get_player("hikaru")

        assert player.username == "hikaru"
        assert player.title == "GM"
        mock_request.assert_called_once()
```

### Testing Error Cases

```python
@pytest.mark.asyncio
async def test_get_player_not_found():
    async with ChessComClient() as client:
        with pytest.raises(NotFoundError) as exc_info:
            await client.get_player("nonexistent_user")

        assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_input():
    async with ChessComClient() as client:
        with pytest.raises(ValueError):
            await client.get_player("")
```

### Testing Rate Limiting

```python
@pytest.mark.asyncio
async def test_rate_limiting():
    async with ChessComClient() as client:
        # Make multiple concurrent requests
        usernames = ["hikaru", "magnuscarlsen", "fabianocaruana"]
        tasks = [client.get_player(username) for username in usernames]

        # Should complete without rate limit errors
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert all(not isinstance(r, Exception) for r in results)
```

## Integration Testing

### Real API Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_player_workflow():
    async with ChessComClient() as client:
        # Get player profile
        player = await client.get_player("hikaru")

        # Get player stats
        stats = await client.get_player_stats("hikaru")

        # Get recent games
        games = await client.get_player_current_games("hikaru")

        # Verify complete workflow
        assert player.username == "hikaru"
        assert stats.chess_blitz is not None
        assert isinstance(games, list)
```

### Long-Running Tests

```python
@pytest.mark.slow
@pytest.mark.asyncio
async def test_tournament_completion():
    async with ChessComClient() as client:
        tournament = await client.get_tournament("some-tournament-id")
        await tournament.fetch_rounds(client=client)

        for round_info in tournament.rounds:
            await round_info.fetch_groups(client=client)
            # Verify round data
```

## Test Organization

### Directory Structure

```plaintext
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_client.py        # Client tests
├── test_integration.py   # Integration tests
├── test_models.py        # Model tests
└── data/                 # Test data
    ├── player_data.json
    ├── game_data.json
    └── tournament_data.json
```

### Test Categories

```python
# Unit tests
@pytest.mark.unit
def test_model_creation():
    pass


# Integration tests
@pytest.mark.integration
async def test_api_interaction():
    pass


# Slow tests
@pytest.mark.slow
async def test_bulk_operation():
    pass
```

## Test Data Management

### Loading Test Data

```python
import json
from pathlib import Path


def load_test_data(filename: str):
    data_path = Path(__file__).parent / "data" / filename
    with open(data_path, "r") as f:
        return json.load(f)


# Usage in tests
def test_with_data():
    data = load_test_data("player_data.json")
    # Use test data
```

### Test Data Generation

```python
import random


def generate_test_username():
    return f"test_user_{random.randint(1000, 9999)}"


def generate_test_game_data():
    return {
        "url": f"https://chess.com/game/{random.randint(1000, 9999)}",
        "pgn": "1. e4 e5 2. Nf3 Nc6",
        "time_control": "300+2",
        "end_time": int(time.time())
    }
```

## Performance Testing

### Load Testing

```python
@pytest.mark.performance
async def test_concurrent_requests():
    async with ChessComClient() as client:
        start_time = time.time()

        # Make 100 concurrent requests
        tasks = [
            client.get_player(f"user_{i}")
            for i in range(100)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration = end_time - start_time

        # Log performance metrics
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_count = len(results) - success_count

        print(f"Duration: {duration:.2f}s")
        print(f"Success Rate: {(success_count / len(results)) * 100:.1f}%")
        print(f"Error Count: {error_count}")
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/tests.yml
name: Tests

on: [ push, pull_request ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ "3.8", "3.9", "3.10", "3.11", "3.12" ]

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest --cov=chess_com_api --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on state from other tests
   ```python
   @pytest.fixture(autouse=True)
   async def cleanup():
       # Setup
       yield
       # Cleanup
   ```

2. **Descriptive Names**: Use clear test names that describe the scenario
   ```python
   async def test_get_player_returns_correct_title_for_grandmaster():
       pass
   ```

3. **Test Data**: Use meaningful test data
   ```python
   test_data = {
       "username": "hikaru",  # Known GM
       "title": "GM",
       "status": "premium"
   }
   ```

4. **Error Cases**: Test both success and failure cases
   ```python
   async def test_get_player_raises_not_found_for_nonexistent_user():
       pass
   ```

5. **Async Testing**: Always use proper async test decorators
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       pass
   ```

## See Also

- [Project Setup Guide](project-setup.md)
- [Contributing Guide](../contributing.md)
- [API Reference](../api/client.md)