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
-- FILE: http_codes.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:40:33 02-12-2025
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: The overview of the http module.
-- // AR
-- +==== END AsperBackend =================+
-->
# HTTP Codes Module

## Overview

The http_codes module provides a comprehensive HTTP status code and response management system for FastAPI. It offers a type-safe interface for sending HTTP responses with proper content types, status codes, and headers.

**Location:** `backend/src/libs/http_codes/`

**Key Components:**

- `HttpCodes` - Main response builder class
- `http_constants.py` - HTTP status codes, MIME types, and DataTypes enum
- Global instance `HCI` - Ready-to-use HttpCodes singleton

## Architecture

See [http_codes_architecture.puml](http_codes_architecture.puml) for visual representation.

## Core Classes

### HttpCodes

A final class that standardizes HTTP response creation across all status codes (1xx-5xx).

**Purpose:** Provides consistent, type-safe HTTP responses with proper FastAPI response types based on content type.

**Key Features:**

- 80+ predefined HTTP status code methods
- Automatic response type selection (JSONResponse, HTMLResponse, FileResponse, etc.)
- MIME type validation and normalization
- Support for DataTypes enum, string keys, and raw MIME strings
- Content type detection and processing

**Constructor:**

```python
HttpCodes()  # No parameters needed
```

**Key Methods:**

| Method | Description | Return Type |
|--------|-------------|-------------|
| `send_message_on_status()` | Generic response builder | Response |
| `_package_correctly()` | Select appropriate FastAPI response class | Response subclass |
| `_check_data_type()` | Validate and normalize content type | str (MIME type) |
| `_check_header()` | Validate header mapping | Dict[str, str] |
| `_process_data_content()` | Process content based on type | Any |

### DataTypes Enum

An enumeration of common HTTP content (MIME) types with convenient access methods.

**Purpose:** Provides type-safe content type selection with string-based lookup.

**Features:**

- 100+ MIME types covering common file formats
- Alphabetically sorted members
- Case-insensitive key lookup via `from_key()`
- Support for hyphenated and underscored names

**Usage:**

```python
# Access by enum member
DataTypes.JSON.value  # 'application/json'

# Access by key (case-insensitive)
DataTypes.from_key('json')  # DataTypes.JSON
DataTypes.from_key('HTML')  # DataTypes.HTML
DataTypes.from_key('pdf')   # DataTypes.PDF
```

**Categories:**

| Category | Examples |
|----------|----------|
| Archive | `_7Z`, `GZIP`, `ZIP`, `TAR` |
| Audio | `MP3`, `WAV`, `OGG`, `AAC` |
| Data | `JSON`, `XML`, `CSV`, `YAML` |
| Document | `PDF`, `DOC`, `DOCX`, `ODT` |
| Font | `TTF`, `WOFF`, `WOFF2`, `EOT` |
| Image | `PNG`, `JPEG`, `GIF`, `WEBP`, `SVG` |
| Text | `PLAIN`, `HTML`, `CSS`, `JAVASCRIPT` |
| Video | `MP4`, `WEBM`, `AVI`, `MOV` |
| Special | `OCTET_STREAM`, `FORM_DATA`, `FORM_URLENCODED` |

## HTTP Status Codes

The module supports all standard HTTP status codes organized by category:

### 1xx - Informational

```python
http_codes.continue_(content)                    # 100
http_codes.switching_protocols(content)          # 101
http_codes.processing(content)                   # 102
http_codes.early_hints(content)                  # 103
```

### 2xx - Success

```python
http_codes.ok(content)                           # 200
http_codes.created(content)                      # 201
http_codes.accepted(content)                     # 202
http_codes.no_content()                          # 204
http_codes.reset_content()                       # 205
http_codes.partial_content(content)              # 206
```

### 3xx - Redirection

```python
http_codes.moved_permanently(url)                # 301
http_codes.found(url)                            # 302
http_codes.see_other(url)                        # 303
http_codes.not_modified()                        # 304
http_codes.temporary_redirect(url)               # 307
http_codes.permanent_redirect(url)               # 308
```

### 4xx - Client Errors

```python
http_codes.bad_request(message)                  # 400
http_codes.unauthorized(message)                 # 401
http_codes.forbidden(message)                    # 403
http_codes.not_found(message)                    # 404
http_codes.method_not_allowed(message)           # 405
http_codes.not_acceptable(message)               # 406
http_codes.request_timeout(message)              # 408
http_codes.conflict(message)                     # 409
http_codes.unprocessable_entity(message)         # 422
http_codes.too_many_requests(message)            # 429
```

### 5xx - Server Errors

```python
http_codes.internal_server_error(message)        # 500
http_codes.not_implemented(message)              # 501
http_codes.bad_gateway(message)                  # 502
http_codes.service_unavailable(message)          # 503
http_codes.gateway_timeout(message)              # 504
```

## Configuration (http_constants.py)

### AUTHORISED_STATUSES

List of all valid HTTP status codes:

```python
AUTHORISED_STATUSES: List[int] = [
    100, 101, 102, ...,  # 1xx
    200, 201, 202, ...,  # 2xx
    300, 301, 302, ...,  # 3xx
    400, 401, 403, ...,  # 4xx
    500, 501, 502, ...   # 5xx
]
```

### MIME Type Groups

Constants grouping related MIME types:

```python
FILE_MIME_TYPES: Set[str]          # File-based content
HTML_MIME_TYPES: Set[str]          # HTML/XML/JavaScript
JSON_MIME_TYPES: Set[str]          # JSON variants
PLAIN_TEXT_MIME_TYPES: Set[str]    # Plain text variants
REDIRECT_MIME_TYPES: Set[str]      # Redirect indicator
STREAMING_MIME_TYPES: Set[str]     # Streaming content
UJSON_MIME_TYPES: Set[str]         # UJSON variant
ORJSON_MIME_TYPES: Set[str]        # ORJSON variant
```

### DEFAULT_MESSAGE_TYPE & DEFAULT_MESSAGE_CONTENT

Default values for responses:

```python
DEFAULT_MESSAGE_TYPE: str = "application/json"
DEFAULT_MESSAGE_CONTENT: str = ""
```

## Response Type Selection

The module automatically selects the appropriate FastAPI response class:

| Content Type | FastAPI Response Class | Use Case |
|--------------|------------------------|----------|
| File paths | `FileResponse` | Serving static files |
| HTML/XML/JS | `HTMLResponse` | Web pages, scripts |
| JSON | `JSONResponse` | API responses (default) |
| Plain text | `PlainTextResponse` | Text content |
| Redirect | `RedirectResponse` | URL redirects |
| Streaming | `StreamingResponse` | Large files, media |
| UJSON | `UJSONResponse` | Ultra-fast JSON |
| ORJSON | `ORJSONResponse` | Optimized JSON |
| Other | `Response` | Generic fallback |

## Usage Examples

### Example 1: Simple JSON Response

```python
from backend.src.libs.http_codes import HCI, HttpDataTypes

@app.get("/api/user")
def get_user():
    data = {"id": 123, "name": "John Doe"}
    return HCI.ok(
        content=data,
        content_type=HttpDataTypes.JSON
    )
```

### Example 2: Using DataTypes Enum

```python
from backend.src.libs.http_codes import HCI, DataTypes

@app.get("/api/report")
def get_report():
    return HCI.ok(
        content={"report": "data"},
        content_type=DataTypes.JSON  # Enum member
    )
```

### Example 3: Using String Keys

```python
@app.post("/api/data")
def create_data():
    return HCI.created(
        content={"id": 456},
        content_type="json"  # String key (case-insensitive)
    )
```

### Example 4: Error Responses

```python
@app.get("/api/resource/{id}")
def get_resource(id: int):
    resource = database.get(id)
    if not resource:
        return HCI.not_found(
            content={"error": "Resource not found"},
            content_type="json"
        )
    return HCI.ok(content=resource)
```

### Example 5: File Download

```python
@app.get("/download/report")
def download_report():
    return HCI.ok(
        content="/path/to/report.pdf",
        content_type=DataTypes.PDF,
        headers={"Content-Disposition": 'attachment; filename="report.pdf"'}
    )
```

### Example 6: HTML Response

```python
@app.get("/page")
def get_page():
    html_content = "<html><body><h1>Hello World</h1></body></html>"
    return HCI.ok(
        content=html_content,
        content_type=DataTypes.HTML
    )
```

### Example 7: Redirect

```python
@app.get("/old-path")
def redirect_old_path():
    return HCI.moved_permanently(
        content="https://example.com/new-path",
        content_type="redirect"
    )
```

### Example 8: Custom Status with Headers

```python
@app.post("/api/webhook")
def webhook_handler():
    return HCI.accepted(
        content={"status": "processing"},
        content_type="json",
        headers={"X-Request-ID": "abc123"}
    )
```

### Example 9: Generic Status Code

```python
@app.get("/custom")
def custom_response():
    return HCI.send_message_on_status(
        status=418,  # I'm a teapot
        content={"message": "I'm a teapot"},
        content_type=DataTypes.JSON
    )
```

## Content Type Resolution

The module supports multiple ways to specify content types:

```python
# 1. DataTypes enum member
HCI.ok(content=data, content_type=DataTypes.JSON)

# 2. String key (case-insensitive)
HCI.ok(content=data, content_type="json")
HCI.ok(content=data, content_type="JSON")

# 3. Raw MIME string
HCI.ok(content=data, content_type="application/json")

# 4. Default (if not specified)
HCI.ok(content=data)  # Uses DEFAULT_MESSAGE_TYPE
```

## Error Handling

**Type Validation:**

```python
# Invalid content type raises TypeError
try:
    HCI.ok(content=data, content_type=12345)
except TypeError as e:
    print(f"Invalid data type: {e}")

# Invalid status code raises ValueError
try:
    HCI.send_message_on_status(status=999, content=data)
except ValueError as e:
    print(f"Invalid status code: {e}")
```

**Header Validation:**

```python
# Invalid header format raises TypeError
try:
    HCI.ok(content=data, headers="invalid")
except TypeError as e:
    print(f"Invalid header format: {e}")
```

## Best Practices

1. **Use the global `HCI` instance** - Already instantiated and ready to use
2. **Prefer enum members** - `DataTypes.JSON` is more type-safe than `"json"`
3. **Use specific status methods** - `HCI.not_found()` is clearer than `HCI.send_message_on_status(404)`
4. **Include error details** - Always provide meaningful error messages
5. **Set proper headers** - Use ServerHeaders module for standardized headers
6. **Handle file paths carefully** - Ensure files exist before returning FileResponse
7. **Use streaming for large content** - Prevents memory issues
8. **Validate content type matches content** - Don't send JSON with HTML content type

## Global Instance

The module exports a global `HCI` instance:

```python
from backend.src.libs.http_codes import HCI

# Ready to use immediately
return HCI.ok({"status": "success"})
```

## Dependencies

- `fastapi.responses` - Response classes (JSONResponse, HTMLResponse, etc.)
- `backend.src.libs.core` - `FinalClass` metaclass
- `backend.src.libs.http_codes.http_constants` - Constants and enums

## Related Modules

- [Server Header](../server_header/server_header.md) - Generates standard security headers
- [Boilerplates](../boilerplates/boilerplates.md) - Response boilerplate generation
- [Endpoint Manager](../endpoint_manager/endpoint_manager.md) - Route handling and responses
