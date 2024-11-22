# Project Setup and Configuration

This guide covers the complete setup process for both users and developers of the Chess.com API client.

## Development Environment Setup

### Prerequisites

1. Python Environment

```bash
# Install Python 3.8 or higher
python --version  # Should be 3.8+

# Install pip (if not included)
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

2. Git Setup

```bash
# Install git
git --version

# Configure git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Project Setup

1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Stupidoodle/chess-com-api.git
cd chess-com-api

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

2. Install Dependencies

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Configuration

### Development Tools

1. Configure Code Formatting

```bash
# Create a .style.yapf file (if customizing)
[style]
based_on_style = google
column_limit = 100
indent_width = 4
```

2. Configure Testing

```bash
# Create pytest.ini if it doesn't exist
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = --verbose --cov=chess_com_api --cov-report=term-missing
```

3. Configure Type Checking

```bash
# Create mypy.ini if customizing
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
check_untyped_defs = True
```

### IDE Setup

#### VS Code

```jsonc
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

#### PyCharm

- Open PyCharm
- File → Open → Select project directory
- File → Settings → Project → Python Interpreter
- Add Interpreter → Virtual Environment → Existing → Select `venv/bin/python`
- Enable pytest: Settings → Tools → Python Integrated Tools → Default test runner

## Development Workflow

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Development Cycle

```bash
# Make changes
# Run tests
pytest

# Format code
black .
isort .

# Check types
mypy chess_com_api tests

# Run linter
ruff check .

# Run all checks
tox
```

### 3. Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## Building and Publishing

### Building the Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build package
python -m build
```

### Running Tests

```bash
# Run all tests
tox

# Run specific environment
tox -e py39

# Run with coverage
pytest --cov=chess_com_api --cov-report=html
```

### Publishing to PyPI

```bash
# Build
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Environment Variables

Optional environment variables for development:

```bash
# Development Configuration
export CHESS_COM_DEV_MODE=1
export CHESS_COM_LOG_LEVEL=DEBUG

# Testing Configuration
export CHESS_COM_TEST_USERNAME=testuser
export CHESS_COM_TEST_TOURNAMENT=test-tournament-id

# Documentation
export CHESS_COM_DOCS_DEPLOY_KEY=your-key
```

## Common Issues and Solutions

### Virtual Environment Issues

```bash
# If venv creation fails
python -m pip install --upgrade virtualenv
virtualenv venv

# If activation fails on Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Dependency Issues

```bash
# If dependencies conflict
pip install --upgrade pip
pip install -e ".[dev]" --no-deps
pip install -r requirements-dev.txt

# Clear pip cache if needed
pip cache purge
```

### Testing Issues

```bash
# If tests fail due to event loop
pytest --asyncio-mode=auto

# If coverage reports fail
coverage erase
coverage run -m pytest
coverage html
```

## Project Structure

```plaintext
chess_com_api/
├── __init__.py          # Package initialization
├── client.py            # Main client implementation
├── exceptions.py        # Custom exceptions
├── models.py            # Data models
└── py.typed            # Type hints marker

tests/                   # Test directory
├── __init__.py
├── conftest.py         # Test configuration
├── test_client.py      # Client tests
├── test_integration.py # Integration tests
└── test_models.py      # Model tests

docs/                   # Documentation
├── api/                # API documentation
├── examples/           # Usage examples
└── user-guide/         # User guides

.github/                # GitHub configuration
├── workflows/          # GitHub Actions
└── ISSUE_TEMPLATE/     # Issue templates
```

## Next Steps

- Check the [Contributing Guide](../contributing.md) for contribution guidelines
- Review the [Testing Guide](testing-guide.md) for testing information
- See the [Security Guide](security-guide.md) for security best practices