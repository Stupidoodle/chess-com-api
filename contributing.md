# Contributing to Chess.com API Client

First off, thank you for considering contributing to the Chess.com API Client! It's
people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By
participating, you are expected to uphold this code. Please report unacceptable behavior
to [bryan.tran.xyz@gmail.com].

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please
check [the issue list](https://github.com/Stupidoodle/chess-com-api/issues) as you might
find out that you don't need to create one. When you are creating a bug report, please
include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include Python version and package version information

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide the
following information:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

1. Fork the repository and create your branch from `main`.
2. Set up your development environment:
   ```bash
   # Clone your fork
   git clone https://github.com/Stupidoodle/chess-com-api.git
   cd chess-com-api

   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows

   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. Make your changes:
    * Write your code
    * Add or update tests as needed
    * Update documentation as needed

4. Follow the coding standards:
    * Use [Black](https://black.readthedocs.io/) for code formatting
    * Use [isort](https://pycqa.github.io/isort/) for import sorting
    * Follow [PEP 484](https://www.python.org/dev/peps/pep-0484/) for type hints
    * Run the linting tools:
      ```bash
      # Format code
      black .
      isort .
 
      # Run linters
      ruff check .
      mypy chess_com_api tests
      ```

5. Run the tests:
   ```bash
   pytest
   ```

6. Create your Pull Request:
    * Submit it to the `main` branch
    * Write a clear title and description
    * Reference any relevant issues
    * Make sure all tests pass in CI

## Development Setup

### Prerequisites

* Python 3.8 or higher
* pip
* git

### Environment Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/Stupidoodle/chess-com-api.git
   cd chess-com-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chess_com_api

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::test_get_player
```

### Building Documentation

The documentation is built using MkDocs (AI Generated so not accurate):

```bash
# Install documentation dependencies
pip install -e ".[dev]"

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Making a Release

1. Update version number in `chess_com_api/_version.py`
2. Update CHANGELOG.md
3. Create a new git tag:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```
4. GitHub Actions will automatically build and publish to PyPI

## Code Style Guide

### Python Style

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use type hints for all function arguments and return values
* Document all public methods and classes using docstrings
* Keep lines under 100 characters
* Use meaningful variable names

### Docstring Format

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """Short description of function.

    Longer description of function if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this error is raised
    """
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

## Questions?

Feel free to open an issue or contact the maintainers if you have any questions about
contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT
License.