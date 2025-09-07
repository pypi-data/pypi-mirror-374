"""
SiftDB HTTP Client Implementation

Provides a Python client for interacting with SiftDB HTTP API server.
"""

import json
import requests
from typing import List, Optional, Union
from urllib.parse import urljoin

from .models import (
    SearchRequest, SearchResponse, SearchResult,
    ImportRequest, ImportResponse,
    CollectionListResponse, CollectionInfo,
    HealthResponse, ErrorResponse
)


class SiftDBException(Exception):
    """Exception raised by SiftDB client operations."""
    pass


class SiftDBClient:
    """
    SiftDB HTTP API Client
    
    A Python client for interacting with SiftDB HTTP API server.
    Provides methods for searching, importing, and managing collections.
    
    Args:
        base_url: Base URL of the SiftDB server (e.g., "http://localhost:8080")
        timeout: Request timeout in seconds (default: 30)
        default_collection: Default collection path to use for operations
    """
    
    def __init__(self, base_url: str = "http://localhost:8080", timeout: int = 30, default_collection: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.default_collection = default_collection
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, json_data: Optional[dict] = None) -> Union[dict, List]:
        """Make HTTP request to SiftDB server."""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'} if json_data else None
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.content else {"error": f"HTTP {response.status_code}"}
                raise SiftDBException(f"Server error ({response.status_code}): {error_data.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise SiftDBException(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise SiftDBException(f"Invalid JSON response: {str(e)}")
    
    def health(self) -> HealthResponse:
        """
        Check server health status.
        
        Returns:
            HealthResponse with server status and version information
            
        Raises:
            SiftDBException: If the request fails
        """
        data = self._make_request('GET', '/')
        return HealthResponse(
            status=data['status'],
            version=data['version']
        )
    
    def search(
        self, 
        query: str, 
        collection: Optional[str] = None,
        path_filter: Optional[str] = None,
        regex: bool = False,
        limit: int = 1000
    ) -> SearchResponse:
        """
        Search for text in a SiftDB collection.
        
        Args:
            query: Search query string
            collection: Collection path (uses default if not specified)
            path_filter: Optional glob pattern to filter file paths
            regex: Whether to treat query as a regex pattern
            limit: Maximum number of results to return
            
        Returns:
            SearchResponse containing search results and metadata
            
        Raises:
            SiftDBException: If the search fails
        """
        request_data = {
            "query": query,
            "regex": regex,
            "limit": limit
        }
        
        if collection or self.default_collection:
            request_data["collection"] = collection or self.default_collection
            
        if path_filter:
            request_data["path_filter"] = path_filter
            
        data = self._make_request('POST', '/search', request_data)
        
        results = [
            SearchResult(
                file_path=r['file_path'],
                line_number=r['line_number'],
                line_content=r['line_content']
            )
            for r in data['results']
        ]
        
        return SearchResponse(
            query=data['query'],
            total_matches=data['total_matches'],
            results=results,
            duration_ms=data['duration_ms']
        )
    
    def import_files(
        self,
        source_path: str,
        collection: Optional[str] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> ImportResponse:
        """
        Import files from filesystem into a SiftDB collection.
        
        Args:
            source_path: Path to source directory or file to import
            collection: Collection path (uses default if not specified)
            include_patterns: Optional list of glob patterns for files to include
            exclude_patterns: Optional list of glob patterns for files to exclude
            
        Returns:
            ImportResponse containing import statistics
            
        Raises:
            SiftDBException: If the import fails
        """
        request_data = {
            "source_path": source_path,
            "include_patterns": include_patterns or [],
            "exclude_patterns": exclude_patterns or []
        }
        
        if collection or self.default_collection:
            request_data["collection"] = collection or self.default_collection
            
        data = self._make_request('POST', '/import', request_data)
        
        return ImportResponse(
            message=data['message'],
            files_ingested=data['files_ingested'],
            files_skipped=data['files_skipped'],
            errors=data['errors'],
            duration_ms=data['duration_ms']
        )
    
    def list_collections(self) -> CollectionListResponse:
        """
        List available SiftDB collections.
        
        Returns:
            CollectionListResponse containing collection information
            
        Raises:
            SiftDBException: If the request fails
        """
        data = self._make_request('GET', '/collections')
        
        collections = [
            CollectionInfo(
                name=c['name'],
                path=c['path'],
                total_files=c['total_files'],
                total_size_bytes=c['total_size_bytes']
            )
            for c in data['collections']
        ]
        
        return CollectionListResponse(collections=collections)
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
