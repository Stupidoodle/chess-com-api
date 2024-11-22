---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:

1. Create client with '...'
2. Call method '....'
3. Use parameters '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Code example**

```python
# Minimal code example that reproduces the issue
import asyncio
from chess_com_api import ChessComClient


async def main():
    async with ChessComClient() as client:
        # Your code here
        pass


asyncio.run(main())
```

**Environment (please complete the following information):**

- OS: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.11.2]
- Package version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.