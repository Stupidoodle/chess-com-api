"""Custom exceptions for the Chess.com API wrapper.

This module defines custom exception classes used throughout the Chess.com API wrapper
to handle specific error scenarios and provide meaningful error messages.
"""


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
        """Handle URL redirects by storing the URL and initializing the parent class.

        This method initializes the exception with the redirect URL and creates a
        formatted error message.

        :param url: The URL to redirect to.
        :type url: str
        """
        self.url = url
        super().__init__(f"Redirect to {url} was encountered. Please try again later.")


class GoneError(ChessComAPIError):
    """Raised when a resource is no longer available."""

    pass
