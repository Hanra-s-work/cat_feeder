<!-- 
-- +==== BEGIN AsperBackend =================+
-- LOGO: 
-- ..........####...####..........
-- ......###.....#.#########......
-- ....##........#.###########....
-- ...#..........#.############...
-- ...#..........#.#####.######...
-- ..#.....##....#.###..#...####..
-- .#.....#.##...#.##..##########.
-- #.....##########....##...######
-- #.....#...##..#.##..####.######
-- .#...##....##.#.##..###..#####.
-- ..#.##......#.#.####...######..
-- ..#...........#.#############..
-- ..#...........#.#############..
-- ...##.........#.############...
-- ......#.......#.#########......
-- .......#......#.########.......
-- .........#####...#####.........
-- /STOP
-- PROJECT: AsperBackend
-- FILE: bucket.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 15:26:37 02-12-2025
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: The overview of the bucket module.
-- // AR
-- +==== END AsperBackend =================+
-->
# Bucket Module Documentation

## Overview

The Bucket module provides a simplified, robust interface for interacting with S3-compatible object storage services such as MinIO, AWS S3, and Cellar. Built on top of the `boto3` library, it abstracts away the complexity of direct S3 API calls while providing comprehensive error handling, automatic connection management, and clean logging.

### Key Features

- **S3-Compatible**: Works with AWS S3, MinIO, Cellar, and any S3-compatible service
- **Connection Management**: Automatic connection initialization and health checking
- **Error Handling**: Comprehensive exception handling with detailed logging
- **Type Safety**: Strongly typed with Protocol-based type hints
- **Singleton Pattern**: Uses `FinalClass` metaclass to prevent subclassing
- **Lazy Connection**: Supports both auto-connect and lazy connection patterns

## Architecture

@startuml{bucket_architecture.puml}

The Bucket class acts as a facade over the boto3 S3 resource, providing simplified methods for common operations while ensuring connections are maintained and errors are properly handled.

## Class: Bucket

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `disp` | `Disp` | Logger instance for debugging and error reporting |
| `connection` | `Optional[S3ServiceResourceLike]` | Active S3 connection resource |
| `debug` | `bool` | Debug mode flag for verbose logging |
| `success` | `int` | Numeric success code (default: 0) |
| `error` | `int` | Numeric error code (default: 84) |
| `_is_connected` | `bool` | Internal connection state tracker |
| `_initialization_attempted` | `bool` | Class-level tracker for connection attempts |
| `_initialization_failed` | `bool` | Class-level tracker for connection failures |

### Constructor

```python
def __init__(
    self,
    error: int = 84,
    success: int = 0,
    auto_connect: bool = True,
    debug: bool = False
) -> None:
```

**Parameters:**

- `error` (int): Numeric error code to return on failures
- `success` (int): Numeric success code to return on success
- `auto_connect` (bool): If True, automatically establishes S3 connection during initialization
- `debug` (bool): Enable debug logging

**Example:**

```python
from backend.src.libs.bucket import Bucket

# Auto-connect mode (default)
bucket = Bucket(debug=True)

# Manual connection mode
bucket = Bucket(auto_connect=False)
bucket.connect()
```

## Connection Management

### connect()

Establishes connection to the S3-compatible service using credentials from environment variables.

```python
def connect(self) -> int:
```

**Returns:** `success` code on successful connection, `error` code on failure

**Configuration (Environment Variables):**

- `BUCKET_HOST`: S3 service host (e.g., "localhost", "s3.amazonaws.com")
- `BUCKET_PORT`: S3 service port (optional, e.g., "9000" for MinIO)
- `BUCKET_USER`: Access key ID
- `BUCKET_PASSWORD`: Secret access key
- `BUCKET_SIGNATURE_VERSION`: Signature version (default: "s3v4")

**Example:**

```python
bucket = Bucket(auto_connect=False)
result = bucket.connect()
if result == bucket.success:
    print("Connected successfully")
```

**Flow:**

@startuml{bucket_operations.puml}

### is_connected()

Verifies if the connection to the S3 service is active by attempting to list buckets.

```python
def is_connected(self) -> bool:
```

**Returns:** `True` if connected and operational, `False` otherwise

**Example:**

```python
if bucket.is_connected():
    print("Connection is active")
else:
    print("Connection lost or not established")
```

### disconnect()

Closes the connection to the S3 service by setting the connection object to None.

```python
def disconnect(self) -> int:
```

**Returns:** `success` code on successful disconnection, `error` code if no connection exists

**Example:**

```python
bucket.disconnect()
```

### _ensure_connected() (Internal)

Internal method that ensures a valid connection exists before performing operations. Automatically called by all operation methods.

- If never connected, attempts lazy connection
- If connection lost, attempts to reconnect once
- Raises `RuntimeError` if connection cannot be established

## Bucket Operations

### get_bucket_names()

Retrieves a list of all bucket names in the S3 service.

```python
def get_bucket_names(self) -> Union[List[str], int]:
```

**Returns:** List of bucket names as strings, or `error` code on failure

**Example:**

```python
buckets = bucket.get_bucket_names()
if isinstance(buckets, list):
    for bucket_name in buckets:
        print(f"Bucket: {bucket_name}")
```

### create_bucket()

Creates a new bucket with the specified name.

```python
def create_bucket(self, bucket_name: str) -> int:
```

**Parameters:**

- `bucket_name` (str): Name of the bucket to create

**Returns:** `success` code on creation, `error` code on failure

**Example:**

```python
result = bucket.create_bucket("my-application-data")
if result == bucket.success:
    print("Bucket created successfully")
```

### delete_bucket()

Deletes an existing bucket. The bucket must be empty before deletion.

```python
def delete_bucket(self, bucket_name: str) -> int:
```

**Parameters:**

- `bucket_name` (str): Name of the bucket to delete

**Returns:** `success` code on deletion, `error` code on failure

**Example:**

```python
result = bucket.delete_bucket("old-bucket")
```

## File Operations

### upload_file()

Uploads a file from the local filesystem to a specified bucket.

@startuml{bucket_upload_flow.puml}

```python
def upload_file(
    self,
    bucket_name: str,
    file_path: str,
    key_name: Optional[str] = None
) -> int:
```

**Parameters:**

- `bucket_name` (str): Target bucket name
- `file_path` (str): Local path to the file to upload
- `key_name` (Optional[str]): Name to save the file as in the bucket. If None, uses the file_path

**Returns:** `success` code on upload, `error` code on failure

**Example:**

```python
# Upload with automatic key name
result = bucket.upload_file("media", "/tmp/image.jpg")

# Upload with custom key name
result = bucket.upload_file(
    bucket_name="media",
    file_path="/tmp/image.jpg",
    key_name="uploads/2025/image.jpg"
)
```

### download_file()

Downloads a file from a bucket to the local filesystem.

```python
def download_file(
    self,
    bucket_name: str,
    key_name: str,
    destination_path: str
) -> int:
```

**Parameters:**

- `bucket_name` (str): Source bucket name
- `key_name` (str): Name/path of the file in the bucket
- `destination_path` (str): Local path where the file will be saved

**Returns:** `success` code on download, `error` code on failure

**Example:**

```python
result = bucket.download_file(
    bucket_name="media",
    key_name="uploads/2025/image.jpg",
    destination_path="/tmp/downloaded_image.jpg"
)
```

### delete_file()

Deletes a file from the specified bucket.

```python
def delete_file(self, bucket_name: str, key_name: str) -> int:
```

**Parameters:**

- `bucket_name` (str): Bucket containing the file
- `key_name` (str): Name/path of the file to delete

**Returns:** `success` code on deletion, `error` code on failure

**Example:**

```python
result = bucket.delete_file("media", "uploads/2025/old_image.jpg")
```

### get_bucket_files()

Lists all files in a specified bucket.

```python
def get_bucket_files(self, bucket_name: str) -> Union[List[str], int]:
```

**Parameters:**

- `bucket_name` (str): Name of the bucket to list

**Returns:** List of file keys as strings, or `error` code on failure

**Example:**

```python
files = bucket.get_bucket_files("media")
if isinstance(files, list):
    print(f"Found {len(files)} files:")
    for file_key in files:
        print(f"  - {file_key}")
```

### get_bucket_file()

Retrieves metadata about a specific file in a bucket.

```python
def get_bucket_file(
    self,
    bucket_name: str,
    key_name: str
) -> Union[Dict[str, Any], int]:
```

**Parameters:**

- `bucket_name` (str): Bucket containing the file
- `key_name` (str): Name/path of the file

**Returns:** Dictionary with file metadata (`file_path`, `file_size`), or `error` code on failure

**Example:**

```python
file_info = bucket.get_bucket_file("media", "uploads/2025/image.jpg")
if isinstance(file_info, dict):
    print(f"File: {file_info['file_path']}")
    print(f"Size: {file_info['file_size']} bytes")
```

## Error Handling

The Bucket module uses a comprehensive error handling strategy:

1. **Return Codes**: Methods return numeric codes (`success` or `error`) for operations
2. **Exceptions**: Catches boto3 exceptions (`BotoCoreError`, `ClientError`) and standard exceptions (`ConnectionError`, `RuntimeError`)
3. **Logging**: All errors are logged via the `display_tty` logger with detailed context
4. **Graceful Degradation**: Connection failures don't crash the application; instances can exist in a disconnected state

### Common Error Scenarios

```python
# Connection failure
bucket = Bucket()
if not bucket.is_connected():
    print("Failed to establish connection - check credentials and network")

# File upload failure
result = bucket.upload_file("nonexistent-bucket", "/tmp/file.txt")
if result == bucket.error:
    print("Upload failed - check bucket name and file path")

# List operation failure
files = bucket.get_bucket_files("my-bucket")
if isinstance(files, int) and files == bucket.error:
    print("Failed to list files - bucket may not exist or be inaccessible")
```

## Configuration

The Bucket module uses environment variables for configuration. These should be defined in your `.env` file:

```bash
# Required
BUCKET_HOST=localhost
BUCKET_USER=minioadmin
BUCKET_PASSWORD=minioadmin

# Optional
BUCKET_PORT=9000
BUCKET_SIGNATURE_VERSION=s3v4
```

### Docker Compose Example

```yaml
services:
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  backend:
    build: .
    environment:
      BUCKET_HOST: minio
      BUCKET_PORT: 9000
      BUCKET_USER: minioadmin
      BUCKET_PASSWORD: minioadmin
```

## Complete Usage Example

```python
from backend.src.libs.bucket import Bucket

# Initialize with auto-connect
bucket = Bucket(debug=True)

# Verify connection
if not bucket.is_connected():
    print("Connection failed!")
    exit(1)

# Create a bucket
if bucket.create_bucket("application-storage") == bucket.success:
    print("Bucket created")

# Upload files
bucket.upload_file(
    bucket_name="application-storage",
    file_path="/tmp/data.json",
    key_name="config/data.json"
)

# List all files
files = bucket.get_bucket_files("application-storage")
if isinstance(files, list):
    print(f"Files in bucket: {files}")

# Get file metadata
file_info = bucket.get_bucket_file("application-storage", "config/data.json")
if isinstance(file_info, dict):
    print(f"File size: {file_info['file_size']} bytes")

# Download file
bucket.download_file(
    bucket_name="application-storage",
    key_name="config/data.json",
    destination_path="/tmp/downloaded_data.json"
)

# Delete file
bucket.delete_file("application-storage", "config/data.json")

# Clean up
bucket.disconnect()
```

## Integration with RuntimeManager

The Bucket class is designed to integrate with the RuntimeManager system for centralized lifecycle management:

```python
from backend.src.libs.core import RuntimeManager

# RuntimeManager automatically initializes Bucket with auto_connect=True
runtime = RuntimeManager()

# Access the bucket instance
bucket = runtime.bucket

# Use bucket operations
bucket.upload_file("my-bucket", "/tmp/file.txt", "uploads/file.txt")
```

## Type Safety

The module uses Protocol-based type hints for better static type checking without requiring boto3 stubs:

- `S3ServiceResourceLike`: The main S3 service resource
- `S3BucketLike`: Bucket resource with file operations
- `S3ObjectLike`: Individual S3 object with metadata
- `S3ObjectsCollectionLike`: Collection of objects for iteration
- `S3BucketsCollectionLike`: Collection of buckets for iteration

These lightweight protocols describe only the subset of boto3's API that the Bucket wrapper actually uses.

## Best Practices

1. **Use Auto-Connect**: Let the Bucket class handle connection automatically unless you have specific initialization requirements
2. **Check Return Codes**: Always check return codes for operations that return integers
3. **Type Check Returns**: Use `isinstance()` to distinguish between successful list returns and error codes
4. **Enable Debug Mode**: Use `debug=True` during development for detailed logging
5. **Environment Variables**: Keep credentials in environment variables, never in code
6. **Connection Lifecycle**: Let the RuntimeManager handle bucket lifecycle when possible
7. **Error Handling**: Wrap operations in try-except blocks when precise error handling is needed

## See Also

- [Core Module Documentation](../core/core.md) - RuntimeManager integration
- [Redis Module Documentation](../redis/redis.md) - Similar pattern for Redis connections
- [SQL Module Documentation](../sql/sql.md) - Database connection management
