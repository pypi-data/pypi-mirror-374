# collepedia/exceptions.py

class CollepediaError(Exception):
    """Base exception class for the Collepedia library."""
    pass

class CollepediaConnectionError(CollepediaError):
    """Raised for network-related errors during feed fetching."""
    pass

class FeedParsingError(CollepediaError):
    """Raised when the RSS/Atom feed is malformed or cannot be parsed."""
    pass
