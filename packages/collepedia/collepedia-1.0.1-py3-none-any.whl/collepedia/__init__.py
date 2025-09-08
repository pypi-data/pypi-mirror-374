# collepedia/__init__.py

"""
Collepedia Library
A dedicated client to fetch and manage posts from Collepedia.
"""

__version__ = "1.0.0"

from .client import CollepediaClient, PostEntry
from .exceptions import CollepediaError, CollepediaConnectionError, FeedParsingError

__all__ = [
    "CollepediaClient",
    "PostEntry",
    "CollepediaError",
    "CollepediaConnectionError",
    "FeedParsingError",
]
