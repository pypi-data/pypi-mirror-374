# SiftDB Python Client

The official Python client library for SiftDB HTTP API.

## Installation

```bash
pip install siftdb
```

## Quick Start

### Basic Usage

```python
from siftdb import SiftDBClient

# Create client instance
client = SiftDBClient(
    base_url="http://localhost:8080",
    default_collection="/path/to/my/collection"
)

# Search for text
results = client.search(
    query="function main",
    path_filter="**/*.py",
    limit=50
)

print(f"Found {results.total_matches} matches in {results.duration_ms}ms")
for hit in results.results:
    print(f"{hit.file_path}:{hit.line_number}: {hit.line_content}")
```

### Context Manager Usage

```python
with SiftDBClient(base_url="http://localhost:8080") as client:
    results = client.search("error handling")
    print(f"Found {len(results.results)} results")
```

### Import Files

```python
# Import files into a collection
import_result = client.import_files(
    source_path="/path/to/source",
    include_patterns=["**/*.py", "**/*.md"],
    exclude_patterns=["**/__pycache__/**", "**/.*"]
)

print(f"Imported {import_result.files_ingested} files")
print(f"Skipped {import_result.files_skipped} files")
if import_result.errors > 0:
    print(f"Encountered {import_result.errors} errors")
```

### List Collections

```python
# List available collections
collections = client.list_collections()
for collection in collections.collections:
    print(f"{collection.name}: {collection.total_files} files, {collection.total_size_bytes} bytes")
```

### Health Check

```python
# Check server health
health = client.health()
print(f"Server status: {health.status}")
print(f"Server version: {health.version}")
```

## API Reference

### Client Configuration

```python
SiftDBClient(
    base_url="http://localhost:8080",  # Server URL
    timeout=30,                        # Request timeout in seconds
    default_collection="/path/to/db"   # Default collection path
)
```

### Search Parameters

```python
client.search(
    query="search text",           # Required: search query
    collection="/path/to/db",      # Optional: override default collection
    path_filter="**/*.py",         # Optional: glob pattern for file filtering
    regex=False,                   # Optional: treat query as regex
    limit=1000                     # Optional: max results
)
```

### Import Parameters

```python
client.import_files(
    source_path="/path/to/source",         # Required: source directory
    collection="/path/to/collection",      # Optional: override default collection
    include_patterns=["**/*.py"],          # Optional: files to include
    exclude_patterns=["**/build/**"]       # Optional: files to exclude
)
```

## Error Handling

```python
from siftdb import SiftDBClient, SiftDBException

try:
    client = SiftDBClient()
    results = client.search("my query")
except SiftDBException as e:
    print(f"SiftDB Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Data Models

### SearchResponse

```python
@dataclass
class SearchResponse:
    query: str                    # Original search query
    total_matches: int           # Total number of matches
    results: List[SearchResult]  # Search results
    duration_ms: float          # Search duration
```

### SearchResult

```python
@dataclass
class SearchResult:
    file_path: str      # File path of the match
    line_number: int    # Line number where match occurred
    line_content: str   # Content of the matching line
```

### ImportResponse

```python
@dataclass
class ImportResponse:
    message: str          # Import completion message
    files_ingested: int   # Number of files imported
    files_skipped: int    # Number of files skipped
    errors: int          # Number of errors encountered
    duration_ms: float   # Import duration
```

## Requirements

- Python 3.8+
- requests >= 2.25.0

## License

MIT
