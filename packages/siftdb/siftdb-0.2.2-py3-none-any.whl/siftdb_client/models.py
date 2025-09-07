"""
Data models for SiftDB API requests and responses.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class SearchRequest:
    """Request model for search operations."""
    query: str
    collection: Optional[str] = None
    path_filter: Optional[str] = None
    regex: bool = False
    limit: int = 1000


@dataclass
class SearchResult:
    """Individual search result."""
    file_path: str
    line_number: int
    line_content: str


@dataclass
class SearchResponse:
    """Response model for search operations."""
    query: str
    total_matches: int
    results: List[SearchResult]
    duration_ms: float


@dataclass
class ImportRequest:
    """Request model for import operations."""
    source_path: str
    collection: Optional[str] = None
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None


@dataclass
class ImportResponse:
    """Response model for import operations."""
    message: str
    files_ingested: int
    files_skipped: int
    errors: int
    duration_ms: float


@dataclass
class CollectionInfo:
    """Information about a SiftDB collection."""
    name: str
    path: str
    total_files: int
    total_size_bytes: int


@dataclass
class CollectionListResponse:
    """Response model for listing collections."""
    collections: List[CollectionInfo]


@dataclass
class ErrorResponse:
    """Error response model."""
    error: str


@dataclass
class HealthResponse:
    """Health check response model."""
    status: str
    version: str
