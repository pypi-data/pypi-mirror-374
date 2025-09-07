"""
SiftDB Python Client Library

A Python client for interacting with SiftDB HTTP API server.
Provides easy-to-use methods for searching, importing, and managing collections.
"""

from .client import SiftDBClient, SiftDBException
from .models import SearchRequest, SearchResponse, ImportRequest, ImportResponse, ErrorResponse

__version__ = "0.2.2"
__all__ = [
    "SiftDBClient",
    "SiftDBException", 
    "SearchRequest", 
    "SearchResponse",
    "ImportRequest",
    "ImportResponse", 
    "ErrorResponse"
]
