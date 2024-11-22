# chess_com_api/exceptions.py

class ChessComAPIError(Exception):
    """Base exception for Chess.com API errors."""
    pass


class RateLimitError(ChessComAPIError):
    """Raised when API rate limit is exceeded."""
    pass


class NotFoundError(ChessComAPIError):
    """Raised when requested resource is not found."""
    pass


class ValidationError(ChessComAPIError):
    """Raised when input validation fails."""
    pass


class RedirectError(ChessComAPIError):
    """Raised when a redirect is encountered."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(
            f"Redirect to {url} was encountered. Please try again later."
        )


class GoneError(ChessComAPIError):
    """Raised when a resource is no longer available."""
    pass
