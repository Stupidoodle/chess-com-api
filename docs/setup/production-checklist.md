# Production Deployment Checklist

This guide provides a comprehensive checklist for deploying applications using the Chess.com API client in production
environments.

## Pre-Deployment Checklist

### 1. Environment Configuration

#### Client Configuration

```python
import aiohttp
from chess_com_api import ChessComClient
import ssl

def create_production_client():
    # SSL Configuration
    ssl_context = ssl.create_default_context()
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    # Connection Configuration
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=100,               # Connection pool size
        ttl_dns_cache=300,       # DNS cache TTL
        use_dns_cache=True,      # Enable DNS caching
        force_close=False        # Keep connections alive
    )
    
    # Timeout Configuration
    timeout = aiohttp.ClientTimeout(
        total=30,        # Total timeout
        connect=10,      # Connection timeout
        sock_read=10,    # Socket read timeout
        sock_connect=10  # Socket connect timeout
    )
    
    # Create session
    session = aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={
            "User-Agent": "YourApp/1.0 (contact@example.com)"
        }
    )
    
    return ChessComClient(session=session)
```

#### Environment Variables

```bash
# Required Variables
export CHESS_COM_USER_AGENT="YourApp/1.0 (contact@example.com)"
export CHESS_COM_MAX_RETRIES=3
export CHESS_COM_TIMEOUT=30
export CHESS_COM_RATE_LIMIT=300

# Logging Configuration
export CHESS_COM_LOG_LEVEL=INFO
export CHESS_COM_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
export CHESS_COM_LOG_FILE="/var/log/chess_com_api.log"

# Monitoring Configuration
export CHESS_COM_ENABLE_METRICS=true
export CHESS_COM_METRICS_PORT=9090
```

### 2. Logging Setup

#### Logging Configuration

```python
import logging
import logging.handlers
import os

def setup_production_logging():
    # Create logger
    logger = logging.getLogger("chess_com_api")
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        os.getenv("CHESS_COM_LOG_FILE", "chess_com_api.log"),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### 3. Error Handling

#### Production Error Handler

```python
class ProductionErrorHandler:
    def __init__(self, logger):
        self.logger = logger
        self.error_counts = defaultdict(int)
    
    async def handle(self, operation, *args, **kwargs):
        try:
            return await operation(*args, **kwargs)
        except NotFoundError as e:
            self.logger.warning(f"Resource not found: {e}")
            self.error_counts["not_found"] += 1
            raise
        except RateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {e}")
            self.error_counts["rate_limit"] += 1
            raise
        except Exception as e:
            self.logger.exception("Unexpected error")
            self.error_counts["unexpected"] += 1
            raise
```

### 4. Monitoring Setup

#### Metrics Collection

```python
from prometheus_client import Counter, Histogram
import time

class MetricsCollector:
    def __init__(self):
        self.request_count = Counter(
            'chess_com_api_requests_total',
            'Total requests made to Chess.com API'
        )
        self.error_count = Counter(
            'chess_com_api_errors_total',
            'Total errors encountered',
            ['error_type']
        )
        self.request_duration = Histogram(
            'chess_com_api_request_duration_seconds',
            'Request duration in seconds',
            ['endpoint']
        )
    
    def track_request(self, endpoint: str):
        self.request_count.inc()
        start_time = time.time()
        
        def track_duration():
            duration = time.time() - start_time
            self.request_duration.labels(endpoint=endpoint).observe(duration)
        
        return track_duration
```

## Deployment Checklist

### 1. Application Configuration

- [ ] Set appropriate environment variables
- [ ] Configure logging
- [ ] Set up error handling
- [ ] Configure monitoring
- [ ] Set up health checks
- [ ] Configure rate limiting
- [ ] Set up connection pooling
- [ ] Configure timeouts
- [ ] Set up SSL/TLS

### 2. Performance Configuration

- [ ] Configure connection pooling
- [ ] Set appropriate batch sizes
- [ ] Configure concurrent requests
- [ ] Set up caching if needed
- [ ] Configure retry strategies
- [ ] Set up circuit breakers
- [ ] Configure request timeouts
- [ ] Set up DNS caching

### 3. Monitoring and Logging

- [ ] Set up application logging
- [ ] Configure error tracking
- [ ] Set up performance monitoring
- [ ] Configure health checks
- [ ] Set up alerting
- [ ] Configure metrics collection
- [ ] Set up log rotation
- [ ] Configure audit logging

### 4. Security Configuration

- [ ] Configure SSL/TLS
- [ ] Set up secure headers
- [ ] Configure timeouts
- [ ] Set up rate limiting
- [ ] Configure input validation
- [ ] Set up error handling
- [ ] Configure logging (no sensitive data)
- [ ] Set up monitoring

## Production Best Practices

### 1. Resource Management

```python
class ResourceManager:
    def __init__(self):
        self.clients = weakref.WeakSet()
    
    async def get_client(self):
        client = await create_production_client()
        self.clients.add(client)
        return client
    
    async def cleanup(self):
        for client in self.clients:
            await client.close()
```

### 2. Health Checks

```python
async def health_check():
    async with ChessComClient() as client:
        try:
            # Test API connectivity
            await client.get_player("hikaru")
            return True
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            return False
```

### 3. Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "closed"
    
    async def execute(self, operation):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await operation()
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise e
```

## Deployment Steps

1. **Pre-Deployment**
    - [ ] Review configuration
    - [ ] Check dependencies
    - [ ] Run tests
    - [ ] Review logging
    - [ ] Check monitoring

2. **Deployment**
    - [ ] Deploy configuration
    - [ ] Start application
    - [ ] Check logs
    - [ ] Verify metrics
    - [ ] Test health checks

3. **Post-Deployment**
    - [ ] Monitor performance
    - [ ] Check error rates
    - [ ] Verify logging
    - [ ] Test alerts
    - [ ] Review metrics

## Common Production Issues

### 1. Connection Management

- Rate limiting issues
- Connection timeouts
- DNS resolution problems
- SSL/TLS errors

### 2. Resource Usage

- Memory leaks
- High CPU usage
- Network congestion
- Disk space issues

### 3. Error Handling

- Unhandled exceptions
- API errors
- Timeout issues
- Rate limit errors

## Monitoring Tips

1. **Key Metrics to Monitor**
    - Request rates
    - Error rates
    - Response times
    - Resource usage

2. **Alerting Thresholds**
    - Error rate > 5%
    - Response time > 2s
    - Rate limit hits
    - Resource exhaustion

## See Also

- [Performance Tuning Guide](performance-guide.md)
- [Error Handling Guide](../user-guide/error-handling.md)
- [Security Guide](security-guide.md)
- [API Reference](../api/client.md)