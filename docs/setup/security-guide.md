# Security Best Practices

This guide covers security best practices for using the Chess.com API client in your applications.

## Client Configuration

### Secure Session Setup

Always configure your client with secure defaults:

```python
import ssl
import aiohttp
from chess_com_api import ChessComClient


async def create_secure_client():
    # Create secure SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Configure connection pooling with secure defaults
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        force_close=True,  # Don't reuse connections
        enable_cleanup_closed=True,  # Clean up closed connections
        verify_ssl=True  # Always verify SSL certificates
    )

    # Configure secure timeouts
    timeout = aiohttp.ClientTimeout(
        total=30,  # Total timeout
        connect=10,  # Connection timeout
        sock_connect=10  # Socket connect timeout
    )

    # Set secure headers
    headers = {
        "User-Agent": "MyApp/1.0 (contact@example.com)",
        "Accept": "application/json"
    }

    session = aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=headers
    )

    return ChessComClient(session=session)
```

## Network Security

### SSL/TLS Configuration

Always use secure TLS settings:

```python
def create_ssl_context():
    ssl_context = ssl.create_default_context()

    # Set minimum TLS version
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Set secure cipher suites
    ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20')

    # Enable hostname verification
    ssl_context.check_hostname = True

    # Enable certificate verification
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    return ssl_context
```

### Request/Response Validation

```python
from typing import Any, Dict
from chess_com_api.exceptions import ValidationError


def validate_response(data: Dict[str, Any]) -> None:
    """Validate API response data."""
    required_fields = ["username", "url", "player_id"]

    # Check required fields
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    # Validate data types
    if not isinstance(data["username"], str):
        raise ValidationError("Username must be a string")
    if not isinstance(data["player_id"], int):
        raise ValidationError("Player ID must be an integer")


async def safe_request(client: ChessComClient, username: str):
    """Make a request with validation."""
    # Validate input
    if not username or not isinstance(username, str):
        raise ValidationError("Invalid username")

    # Make request
    response = await client.get_player(username)

    # Validate response
    validate_response(response.dict())

    return response
```

## Data Handling

### Input Sanitization

```python
import re
from typing import Optional


def sanitize_username(username: str) -> Optional[str]:
    """Sanitize username input."""
    # Remove whitespace
    username = username.strip()

    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return None

    # Convert to lowercase
    username = username.lower()

    # Limit length
    max_length = 50
    if len(username) > max_length:
        return None

    return username


async def safe_get_player(client: ChessComClient, username: str):
    """Get player with input sanitization."""
    clean_username = sanitize_username(username)
    if not clean_username:
        raise ValidationError("Invalid username")

    return await client.get_player(clean_username)
```

### Rate Limiting Protection

```python
class RateLimitProtection:
    def __init__(self, max_requests: int = 300, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []

    def is_rate_limited(self) -> bool:
        """Check if current requests exceed rate limit."""
        now = time.time()

        # Remove old requests
        self.requests = [
            req_time for req_time in self.requests
            if now - req_time < self.window_seconds
        ]

        return len(self.requests) >= self.max_requests

    def add_request(self):
        """Record a new request."""
        self.requests.append(time.time())


# Usage
rate_limiter = RateLimitProtection()


async def protected_request(client: ChessComClient, username: str):
    if rate_limiter.is_rate_limited():
        raise RateLimitError("Rate limit exceeded")

    try:
        result = await client.get_player(username)
        rate_limiter.add_request()
        return result
    except Exception as e:
        # Log error but don't expose internal details
        logging.error(f"Error in protected_request: {e}")
        raise
```

## Error Handling

### Secure Error Handling

```python
import logging
from typing import Optional

class SecureErrorHandler:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def handle_operation(self, operation, *args, **kwargs):
        try:
            return await operation(*args, **kwargs)
        except NotFoundError:
            # Safe to expose to users
            raise
        except ValidationError as e:
            # Log and sanitize error message
            self.logger.warning(f"Validation error: {e}")
            raise ValidationError("Invalid input provided")
        except Exception as e:
            # Log the full error but return a generic message
            self.logger.error(f"Unexpected error: {e}")
            raise ChessComAPIError(
                "An unexpected error occurred. Please try again later."
            )

# Usage
error_handler = SecureErrorHandler()

async def safe_operation():
    return await error_handler.handle_operation(
        client.get_player,
        "username"
    )
```

## Logging and Monitoring

### Secure Logging

```python
import logging
from typing import Any, Dict


class SecureLogger:
    def __init__(self):
        self.logger = logging.getLogger("chess_com_api")
        self._setup_logger()

    def _setup_logger(self):
        """Configure secure logging."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Log to file with restricted permissions
        handler = logging.FileHandler(
            'chess_com_api.log',
            mode='a',
            encoding='utf-8'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Set appropriate log level
        self.logger.setLevel(logging.INFO)

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data before logging."""
        sanitized = data.copy()

        # Remove potentially sensitive fields
        sensitive_fields = ['token', 'password', 'api_key']
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '[REDACTED]'

        return sanitized

    def log_request(self, method: str, url: str, data: Dict[str, Any]):
        """Log API request safely."""
        sanitized_data = self._sanitize_data(data)
        self.logger.info(
            f"API Request - Method: {method}, URL: {url}, "
            f"Data: {sanitized_data}"
        )

    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error safely."""
        sanitized_context = self._sanitize_data(context)
        self.logger.error(
            f"API Error - Type: {type(error).__name__}, "
            f"Context: {sanitized_context}"
        )


# Usage
secure_logger = SecureLogger()
```

## Production Deployment

### Environment Variables

```python
import os
from typing import Optional


class SecurityConfig:
    @staticmethod
    def get_user_agent() -> str:
        return os.getenv(
            'CHESS_COM_USER_AGENT',
            'ChessComAPI-Python/1.0'
        )

    @staticmethod
    def get_max_retries() -> int:
        return int(os.getenv('CHESS_COM_MAX_RETRIES', '3'))

    @staticmethod
    def get_timeout() -> int:
        return int(os.getenv('CHESS_COM_TIMEOUT', '30'))

    @staticmethod
    def get_proxy_url() -> Optional[str]:
        return os.getenv('CHESS_COM_PROXY_URL')


# Usage
config = SecurityConfig()
client = ChessComClient(
    user_agent=config.get_user_agent(),
    max_retries=config.get_max_retries(),
    timeout=config.get_timeout()
)
```

### Production Client Factory

```python
class SecureClientFactory:
    @staticmethod
    async def create_client(
            environment: str = "production"
    ) -> ChessComClient:
        """Create a properly configured client for the environment."""
        if environment not in ["development", "staging", "production"]:
            raise ValueError("Invalid environment")

        # Load environment-specific configuration
        config = SecurityConfig()

        # Create secure SSL context
        ssl_context = create_ssl_context()

        # Configure connection pooling
        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=100,
            force_close=environment == "production"
        )

        # Configure timeouts
        timeout = aiohttp.ClientTimeout(
            total=config.get_timeout(),
            connect=10
        )

        # Create session with secure defaults
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": config.get_user_agent()
            }
        )

        return ChessComClient(
            session=session,
            max_retries=config.get_max_retries()
        )


# Usage
client = await SecureClientFactory.create_client("production")
```

## Security Checklist

1. **Client Configuration**
    - [ ] Use TLS 1.2 or higher
    - [ ] Configure secure timeouts
    - [ ] Set appropriate headers
    - [ ] Enable SSL verification

2. **Input Validation**
    - [ ] Sanitize all input
    - [ ] Validate data types
    - [ ] Check input lengths
    - [ ] Use parameterized queries

3. **Error Handling**
    - [ ] Catch all exceptions
    - [ ] Log errors securely
    - [ ] Return safe error messages
    - [ ] Implement rate limiting

4. **Logging**
    - [ ] Use secure logging
    - [ ] Sanitize logged data
    - [ ] Implement proper log rotation
    - [ ] Set appropriate log levels

5. **Deployment**
    - [ ] Use environment variables
    - [ ] Set secure defaults
    - [ ] Implement monitoring
    - [ ] Regular security updates

## Best Practices

1. Always validate input and output
2. Use proper error handling
3. Implement rate limiting
4. Log securely
5. Keep dependencies updated
6. Use environment variables for configuration
7. Implement proper monitoring
8. Regular security audits

## See Also

- [Project Setup Guide](project-setup.md)
- [Error Handling Guide](../user-guide/error-handling.md)
- [API Reference](../api/client.md)