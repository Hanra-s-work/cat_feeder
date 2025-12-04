<!-- 
-- +==== BEGIN CatFeeder =================+
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
-- PROJECT: CatFeeder
-- FILE: server_header.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:25:50 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The structure of the server header module.
-- // AR
-- +==== END CatFeeder =================+
-->
# Server Header Module

## Overview

The server_header module provides standardized HTTP response header generation for FastAPI applications. It implements security best practices, caching strategies, and content-specific header configurations to protect against common web vulnerabilities.

**Location:** `backend/src/libs/server_header/`

**Key Components:**

- `ServerHeaders` - Main header builder class
- `server_header_constants.py` - Header name constants
- Security headers (XSS, CORS, CSP, clickjacking protection)
- Caching strategies per content type

## Architecture

See [server_header_architecture.puml](server_header_architecture.puml) for visual representation.

## Core Class

### ServerHeaders

A final class that generates standardized HTTP headers for different content types with security-first defaults.

**Purpose:** Provides consistent, secure HTTP headers across all API responses with appropriate caching policies.

**Key Features:**

- Comprehensive security headers (MIME sniffing, clickjacking, XSS protection)
- Content-specific caching strategies
- CORS configuration support
- Content-Security-Policy for HTML responses
- Flexible content disposition (inline vs. attachment)
- Custom application identification header

**Constructor:**

```python
ServerHeaders(
    host: str = "0.0.0.0",
    port: int = 5000,
    app_name: str = "Cat Feeder",
    error: int = 84,
    success: int = 0,
    debug: bool = False
)
```

**Parameters:**

- `host` - Server host address
- `port` - Server port number
- `app_name` - Application name (included in `app_sender` header)
- `error` - Error status code
- `success` - Success status code
- `debug` - Enable debug logging

## Security Headers

### Base Security Headers

Applied to **all responses** via `_base_security_headers()`:

| Header | Value | Purpose |
|--------|-------|---------|
| `app_sender` | Application name | Identifies the application |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME type sniffing attacks |
| `X-Frame-Options` | `DENY` | Prevents clickjacking attacks |
| `X-XSS-Protection` | `1; mode=block` | Enables browser XSS filter |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls referrer information leakage |

### Content-Security-Policy (HTML Only)

Applied to HTML responses to control resource loading:

```
default-src 'self';
script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self' data:;
```

**Protection against:**

- Cross-site scripting (XSS)
- Unauthorized resource loading
- Data injection attacks
- Inline script execution (controlled)

## Caching Strategies

The module implements content-specific caching policies optimized for different use cases:

### No-Cache (Dynamic Content)

**Applied to:** JSON, plain text, HTML, XML, forms, streaming

```python
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
```

**Methods:**

- `for_json()` - API responses
- `for_text()` - Plain text
- `for_html()` - HTML pages
- `for_xml()` - XML data
- `for_form_data()` - Form submissions
- `for_streaming()` - Streaming content

### Long-Term Cache (Static Assets)

**Applied to:** CSS, JavaScript

```python
Cache-Control: public, max-age=31536000, immutable
```

**Duration:** 1 year (31536000 seconds)

**Methods:**

- `for_css()` - Stylesheets
- `for_javascript()` - Scripts

**Note:** Assumes versioned/fingerprinted filenames (e.g., `app.v123.js`)

### Medium-Term Cache (Media)

**Applied to:** Images, video, audio

```python
Cache-Control: public, max-age=86400
```

**Duration:** 24 hours (86400 seconds)

**Methods:**

- `for_image()` - Image responses
- `for_video()` - Video streams
- `for_audio()` - Audio files

### Short-Term Cache (Downloads)

**Applied to:** PDF, CSV, downloadable files

```python
Cache-Control: public, max-age=3600
```

**Duration:** 1 hour (3600 seconds)

**Methods:**

- `for_pdf()` - PDF documents
- `for_csv()` - CSV exports
- `for_file()` - Generic file downloads

## Header Generation Methods

### Dynamic Content

```python
# JSON API responses
headers = server_headers.for_json()

# Plain text responses
headers = server_headers.for_text()

# HTML pages
headers = server_headers.for_html()

# XML data
headers = server_headers.for_xml()

# Form data submissions
headers = server_headers.for_form_data()
```

### Static Assets

```python
# CSS stylesheets (1 year cache)
headers = server_headers.for_css()

# JavaScript files (1 year cache)
headers = server_headers.for_javascript()
```

### Media Files

```python
# Images (24 hour cache)
headers = server_headers.for_image()

# Video streams (24 hour cache)
headers = server_headers.for_video()

# Audio files (24 hour cache)
headers = server_headers.for_audio()
```

### Downloadable Files

```python
# Generic file download
headers = server_headers.for_file(filename="report.xlsx")

# PDF documents
headers = server_headers.for_pdf(
    filename="invoice.pdf",
    inline=False  # Force download
)

# CSV exports
headers = server_headers.for_csv(filename="data.csv")
```

### Streaming Content

```python
# Streaming responses (no cache)
headers = server_headers.for_streaming()
```

## Configuration (server_header_constants.py)

Header name constants for consistency:

```python
# Custom headers
HEADER_APP_NAME: str = "app_sender"

# Caching
CACHE_CONTROL: str = "Cache-Control"
PRAGMA: str = "Pragma"
EXPIRES: str = "Expires"

# Content delivery
CONTENT_DISPOSITION: str = "Content-Disposition"
ACCEPT_RANGES: str = "Accept-Ranges"

# Privacy
REFERRER_POLICY: str = "Referrer-Policy"

# Security
CONTENT_SECURITY_POLICY: str = "Content-Security-Policy"
CONTENT_TYPE: str = "X-Content-Type-Options"
FRAME_OPTIONS: str = "X-Frame-Options"
XSS_PROTECTION: str = "X-XSS-Protection"
```

## Usage Examples

### Example 1: JSON API Response

```python
from backend.src.libs.server_header import ServerHeaders
from backend.src.libs.http_codes import HCI, DataTypes

server_headers = ServerHeaders(app_name="MyAPI")

@app.get("/api/users")
def get_users():
    data = {"users": [...]}
    return HCI.ok(
        content=data,
        content_type=DataTypes.JSON,
        headers=server_headers.for_json()
    )
```

### Example 2: File Download with Filename

```python
@app.get("/download/report")
def download_report():
    file_path = "/path/to/report.pdf"
    return HCI.ok(
        content=file_path,
        content_type=DataTypes.PDF,
        headers=server_headers.for_file(filename="monthly-report.pdf")
    )
```

### Example 3: PDF Inline Display

```python
@app.get("/view/invoice/{id}")
def view_invoice(id: int):
    pdf_path = f"/invoices/{id}.pdf"
    return HCI.ok(
        content=pdf_path,
        content_type=DataTypes.PDF,
        headers=server_headers.for_pdf(
            filename=f"invoice-{id}.pdf",
            inline=True  # Display in browser
        )
    )
```

### Example 4: Static CSS with Long Cache

```python
@app.get("/static/styles.v123.css")
def get_stylesheet():
    css_content = "body { margin: 0; }"
    return HCI.ok(
        content=css_content,
        content_type=DataTypes.CSS,
        headers=server_headers.for_css()
    )
```

### Example 5: Image with Medium Cache

```python
@app.get("/images/logo.png")
def get_logo():
    return HCI.ok(
        content="/static/images/logo.png",
        content_type=DataTypes.PNG,
        headers=server_headers.for_image()
    )
```

### Example 6: HTML with CSP

```python
@app.get("/page")
def get_page():
    html = "<html><body><h1>Secure Page</h1></body></html>"
    return HCI.ok(
        content=html,
        content_type=DataTypes.HTML,
        headers=server_headers.for_html()  # Includes CSP
    )
```

### Example 7: CSV Export

```python
@app.get("/export/data")
def export_data():
    csv_data = "Name,Email\nJohn,john@example.com"
    return HCI.ok(
        content=csv_data,
        content_type=DataTypes.CSV,
        headers=server_headers.for_csv(filename="users.csv")
    )
```

### Example 8: Video Streaming

```python
@app.get("/stream/video/{id}")
def stream_video(id: int):
    video_path = f"/videos/{id}.mp4"
    headers = server_headers.for_video()
    headers["Accept-Ranges"] = "bytes"  # Enable seeking
    
    return HCI.ok(
        content=video_path,
        content_type=DataTypes.MP4,
        headers=headers
    )
```

### Example 9: Integration with RuntimeManager

```python
from backend.src.libs.core import RI
from backend.src.libs.server_header import ServerHeaders

# Initialize once in application startup
RI.set(ServerHeaders, host="0.0.0.0", port=8000, app_name="Cat Feeder")

# Use anywhere in the application
@app.get("/api/status")
def get_status():
    server_headers = RI.get(ServerHeaders)
    return HCI.ok(
        content={"status": "healthy"},
        headers=server_headers.for_json()
    )
```

## CORS Configuration

While `ServerHeaders` doesn't directly manage CORS, it's typically used alongside FastAPI's `CORSMiddleware`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ServerHeaders adds additional security on top of CORS
@app.get("/api/data")
def get_data():
    return HCI.ok(
        content={"data": "value"},
        headers=server_headers.for_json()
    )
```

## Security Best Practices

### 1. MIME Sniffing Protection

```python
X-Content-Type-Options: nosniff
```

Prevents browsers from MIME-sniffing content types, reducing XSS attack surface.

### 2. Clickjacking Protection

```python
X-Frame-Options: DENY  # Most responses
X-Frame-Options: SAMEORIGIN  # Images only
```

Prevents embedding in iframes from malicious sites.

### 3. XSS Protection

```python
X-XSS-Protection: 1; mode=block
```

Enables browser's built-in XSS filter (legacy but still useful).

### 4. Content Security Policy

```python
Content-Security-Policy: default-src 'self'; ...
```

Restricts resource loading to trusted sources only.

### 5. Referrer Policy

```python
Referrer-Policy: strict-origin-when-cross-origin
```

Controls how much referrer information is sent with requests.

## Caching Decision Tree

```
Is content dynamic (changes frequently)?
├─ Yes → No cache (for_json, for_text, for_html)
└─ No → Is it a versioned static asset?
    ├─ Yes → Long cache (for_css, for_javascript)
    └─ No → Is it media?
        ├─ Yes → Medium cache (for_image, for_video)
        └─ No → Short cache (for_file, for_pdf)
```

## Content-Disposition Handling

```python
# Force download
headers = server_headers.for_file(filename="report.pdf")
# Content-Disposition: attachment; filename="report.pdf"

# Display inline (browser)
headers = server_headers.for_pdf(filename="doc.pdf", inline=True)
# Content-Disposition: inline; filename="doc.pdf"

# No disposition (let browser decide)
headers = server_headers.for_json()
# No Content-Disposition header
```

## Best Practices

1. **Use appropriate method for content type** - Match caching to content volatility
2. **Always include security headers** - Base headers applied automatically
3. **Version static assets** - Enable long-term caching safely
4. **Set proper filenames** - Improves user experience for downloads
5. **Use inline for viewable content** - PDFs, images can be displayed
6. **Combine with ServerManagement** - Consistent header usage across endpoints
7. **Test CSP policies** - Ensure legitimate resources aren't blocked
8. **Monitor cache hit rates** - Adjust strategies based on analytics

## Integration Points

Typically used with:

```python
# In endpoint handlers
return HCI.ok(
    content=data,
    content_type=DataTypes.JSON,
    headers=server_headers.for_json()  # ← ServerHeaders
)

# In boilerplate responses
class BoilerplateResponses:
    def __init__(self):
        self.server_headers = RI.get(ServerHeaders)
    
    def success_response(self, data):
        return HCI.ok(
            content=data,
            headers=self.server_headers.for_json()
        )
```

## Dependencies

- `display_tty` - Logging functionality
- `backend.src.libs.core` - `FinalClass` metaclass
- `backend.src.libs.server_header.server_header_constants` - Header name constants

## Related Modules

- [HTTP Codes](../http_codes/http_codes.md) - Response generation using these headers
- [Server](../server/server.md) - Server management and CORS configuration
- [Boilerplates](../boilerplates/boilerplates.md) - Standardized response patterns
- [Endpoint Manager](../endpoint_manager/endpoint_manager.md) - Route handling
