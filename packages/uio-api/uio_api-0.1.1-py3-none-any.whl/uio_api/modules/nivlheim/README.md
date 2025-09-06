# Nivlheim API Client

A Python client for the Nivlheim API with type-safe endpoints and automatic APIKEY authentication.

## Features

- **Type-safe endpoints** using StrEnum
- **Automatic APIKEY authentication** via HTTP headers
- **Flexible client creation** with or without context managers
- **Configuration support** for token storage
- **All Nivlheim API endpoints** supported

## Authentication

Nivlheim uses APIKEY authentication. Tokens are obtained from the Nivlheim web interface and are ephemeral (cannot be refreshed programmatically).

### Obtaining an API Key

1. Visit your Nivlheim instance (e.g., `https://nivlheim.uio.no`)
2. Log in through the web interface
3. Generate an API key in your user settings
4. Copy the API key for use with this client

## Configuration

### Storing API Keys

You can store your Nivlheim API key in several ways:

#### 1. Direct in Code (Not Recommended for Production)

```python
from uio_api.modules.nivlheim import nivlheim_client

client = nivlheim_client(
    url="https://nivlheim.uio.no",
    api_key="your-api-key-here"
)
```

#### 2. Using a File (Recommended)

Store your API key in a file:

```bash
echo "your-api-key-here" > ~/.nivlheim-api-key
chmod 600 ~/.nivlheim-api-key
```

Then use it in your code:

```python
from uio_api.modules.nivlheim import nivlheim_client
from pathlib import Path

client = nivlheim_client(
    url="https://nivlheim.uio.no",
    api_key_file=Path.home() / ".nivlheim-api-key"
)
```

#### 3. Using uio_api Configuration System

Create a configuration file `~/.config/uio_api/config.toml`:

```toml
[nivlheim]
url = "https://nivlheim.uio.no"
api_key = "your-api-key-here"
```

Then use it:

```python
from uio_api.modules.nivlheim import nivlheim_client

client = nivlheim_client()  # Uses config values
```

## Usage Examples

### Basic Usage

```python
from uio_api.modules.nivlheim import nivlheim_client, Endpoint

# Create client
client = nivlheim_client(
    url="https://nivlheim.uio.no",
    api_key_file="~/.nivlheim-api-key"
)

# Without context manager (auto-cleanup)
hosts = client.get(Endpoint.Hostlist, params={"fields": "hostname,lastseen"})

# With context manager
with nivlheim_client(api_key="your-key") as client:
    hosts = client.get(Endpoint.Hostlist, params={"fields": "hostname,lastseen"})
```

### Host Operations

```python
from uio_api.modules.nivlheim import nivlheim_client, Endpoint

with nivlheim_client(api_key="your-key") as client:
    # Get host information
    host_data = client.get(
        Endpoint.Host.with_id("hostname.example.com"),
        params={"fields": "ipAddress,hostname,lastseen,os,kernel"}
    )

    # List all hosts
    all_hosts = client.get(
        Endpoint.Hostlist,
        params={"fields": "hostname,ipAddress,lastseen"}
    )

    # Search hosts by criteria
    recent_hosts = client.get(
        Endpoint.Hostlist,
        params={
            "fields": "hostname,lastseen",
            "lastseen<2h": "",  # Last seen less than 2 hours ago
            "sort": "-lastseen"  # Sort by lastseen descending
        }
    )
```

### File Operations

```python
from uio_api.modules.nivlheim import nivlheim_client, Endpoint

with nivlheim_client(api_key="your-key") as client:
    # Get file content by fileId
    file_data = client.get(
        Endpoint.File,
        params={"fileId": "1234", "fields": "content,filename,hostname"}
    )

    # Get file by filename and hostname
    file_data = client.get(
        Endpoint.File,
        params={
            "filename": "/etc/os-release",
            "hostname": "server.example.com",
            "fields": "content,lastModified"
        }
    )

    # Get file content as plain text
    file_content = client.get(
        Endpoint.File,
        params={"fileId": "1234", "format": "raw"}
    )
```

### Search Operations

```python
from uio_api.modules.nivlheim import nivlheim_client, Endpoint

with nivlheim_client(api_key="your-key") as client:
    # Search for content in files
    search_results = client.get(
        Endpoint.Search,
        params={
            "q": "Fedora",
            "filename": "/etc/redhat-release",
            "fields": "hostname,filename,content"
        }
    )

    # Multi-search with multiple terms and operations
    multi_results = client.get(
        Endpoint.Msearch,
        params={
            "q1": "kernel",
            "f1": "/proc/version",
            "q2": "x86_64",
            "op2": "and",
            "fields": "hostname,ipAddress"
        }
    )

    # Grep across all files
    grep_results = client.get(
        Endpoint.Grep,
        params={"q": "wheel", "limit": "10"}
    )
```

### Status Information

```python
from uio_api.modules.nivlheim import nivlheim_client, Endpoint

with nivlheim_client(api_key="your-key") as client:
    # Get status information
    status = client.get(Endpoint.Status)
    print(f"Status: {status}")
```

## Advanced Configuration

### Custom Timeout

```python
client = nivlheim_client(
    url="https://nivlheim.uio.no",
    api_key="your-key",
    timeout=60.0  # 60 second timeout
)
```

### Error Handling

```python
from uio_api.modules.nivlheim import nivlheim_client, Endpoint
import httpx

try:
    with nivlheim_client(api_key="your-key") as client:
        data = client.get(Endpoint.Hostlist)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("Invalid API key - obtain a new one from the web interface")
    elif e.response.status_code == 404:
        print("Resource not found")
    else:
        print(f"HTTP error: {e}")
except httpx.RequestError as e:
    print(f"Network error: {e}")
```

## API Reference

### Endpoints

- `Endpoint.File` - Retrieve file contents and metadata
- `Endpoint.Host` - Retrieve host metadata and file lists
- `Endpoint.Hostlist` - Generate lists of hosts with criteria
- `Endpoint.Search` - Search files for content
- `Endpoint.Msearch` - Multiple searches with boolean operations
- `Endpoint.Grep` - Search all files and return matching lines
- `Endpoint.Status` - Return status information

### Client Methods

All standard HTTP methods are supported:
- `client.get(path, params=None)` - GET requests
- `client.post(path, json=None)` - POST requests
- `client.put(path, json=None)` - PUT requests
- `client.delete(path)` - DELETE requests

## Notes

- **Token Management**: Nivlheim API keys are ephemeral and cannot be refreshed programmatically. When a token expires, you must obtain a new one from the Nivlheim web interface.

- **Rate Limiting**: Be mindful of API rate limits. The client does not implement automatic retry for rate limit errors.

- **Large Responses**: Some endpoints may return large amounts of data. Consider using pagination parameters where available.
