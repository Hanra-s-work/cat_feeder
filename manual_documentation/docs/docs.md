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
-- FILE: docs.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 15:21:28 02-12-2025
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: The overview of the documentation structure.
-- // AR
-- +==== END AsperBackend =================+
-->
# Documentation Handler Module

## Overview

The `docs` module provides a unified documentation handler for managing multiple API documentation providers in the AsperBackend FastAPI application. It supports various documentation frameworks including Swagger UI, ReDoc, RapiDoc, Scalar, Stoplight Elements, and more, allowing developers to easily expose and customize API documentation.

## Architecture

![Documentation Architecture](docs_architecture.puml)

## Core Components

### DocumentationHandler Class

The `DocumentationHandler` is the main class responsible for managing API documentation providers. It implements the `FinalClass` metaclass pattern and provides a centralized interface for documentation management.

**Key Features:**

- Multi-provider support (8+ documentation frameworks)
- Custom OpenAPI schema generation
- OAuth2 authentication support for documentation UIs
- Dynamic provider registration
- Centralized configuration management

**Attributes:**

- `providers`: Dictionary mapping provider names to their instances
- `enabled_providers`: Tuple of active documentation providers
- `openapi_url`: URL path for OpenAPI JSON schema
- `api_title`, `api_version`, `api_description`: API metadata
- `runtime_manager`: Shared runtime manager instance

### Supported Documentation Providers

The module supports the following documentation providers through the `DocumentationProvider` enum:

1. **SWAGGER** - Swagger UI (interactive API documentation)
2. **REDOC** - ReDoc (clean, responsive documentation)
3. **RAPIDOC** - RapiDoc (customizable API explorer)
4. **SCALAR** - Scalar (modern API documentation)
5. **ELEMENTS** - Stoplight Elements
6. **EDITOR** - Swagger Editor
7. **EXPLORER** - OpenAPI Explorer
8. **RAPIPDF** - RapiPDF (PDF generation)

### Provider Factory Pattern

The class uses a factory pattern to instantiate providers:

```python
self.provider_factories = {
    DocumentationProvider.SWAGGER: lambda: SwaggerHandler(...),
    DocumentationProvider.REDOC: lambda: RedocHandler(...),
    DocumentationProvider.RAPIDOC: lambda: RapiDocProvider(...),
    # ... other providers
}
```

## Configuration

### Constants (docs_constants.py)

The module uses environment variables and TOML configuration for setup:

```python
# OpenAPI Configuration
OPENAPI_URL = "/openapi.json"
OPENAPI_TITLE = "AsperBackend API"
OPENAPI_VERSION = "1.0.0"
OPENAPI_DESCRIPTION = "Backend server API documentation"

# OAuth2 Configuration
ENABLE_OAUTH2_DOCS = True
OAUTH2_AUTHORIZATION_URL = "..."
OAUTH2_TOKEN_URL = "..."
OAUTH2_SCOPES = {...}

# Default Providers
DEFAULT_PROVIDERS = (
    DocumentationProvider.SWAGGER,
    DocumentationProvider.REDOC,
)
```

## Usage Examples

### Basic Initialization

```python
from backend.src.libs.docs import DocumentationHandler, DocumentationProvider

# Initialize with default providers (Swagger + ReDoc)
docs_handler = DocumentationHandler(
    api_title="My API",
    api_version="1.0.0",
    api_description="My API Description",
    debug=True
)

# Inject documentation endpoints into FastAPI app
docs_handler.inject()
```

### Custom Provider Selection

```python
# Enable specific providers
custom_providers = (
    DocumentationProvider.SWAGGER,
    DocumentationProvider.RAPIDOC,
    DocumentationProvider.SCALAR,
)

docs_handler = DocumentationHandler(
    providers=custom_providers,
    openapi_url="/api/openapi.json",
    debug=False
)

docs_handler.inject()
```

### With OAuth2 Authentication

```python
# Configuration supports OAuth2 for secured documentation
docs_handler = DocumentationHandler(
    providers=(DocumentationProvider.SWAGGER,),
    api_title="Secured API",
    debug=True
)

# OAuth2 redirect handler is automatically registered
# Access at: /docs/oauth2-redirect
docs_handler.inject()
```

### Accessing Documentation

Once injected, documentation is available at provider-specific endpoints:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- RapiDoc: `http://localhost:8000/rapidoc`
- Scalar: `http://localhost:8000/scalar`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Custom OpenAPI Schema

The handler generates a custom OpenAPI schema with additional metadata:

```python
def _get_custom_openapi_schema(self, app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema with metadata"""
    openapi_schema = get_openapi(
        title=self.api_title,
        version=self.api_version,
        description=self.api_description,
        routes=app.routes,
    )
    
    # Add custom logo
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/logo.png"
    }
    
    # Add OAuth2 security schemes
    if ENABLE_OAUTH2_DOCS:
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2": {...},
            "BearerAuth": {...}
        }
    
    return openapi_schema
```

## Key Methods

### inject(providers=None)

Injects documentation endpoints into the FastAPI application.

**Parameters:**

- `providers` (Optional[tuple]): Override default providers

**Returns:**

- `int`: Success (0) or error (84) code

**Usage:**

```python
# Use default providers
docs_handler.inject()

# Override with specific providers
docs_handler.inject(providers=(DocumentationProvider.SWAGGER,))
```

### _initialize_providers()

Internal method that creates instances of enabled documentation providers.

### _custom_openapi_wrapper(request)

Wrapper for the custom OpenAPI endpoint that serves the schema.

### _oauth2_redirect_handler(request)

Handles OAuth2 authentication callbacks for Swagger UI.

## Integration with FastAPI

The documentation handler integrates seamlessly with FastAPI's routing system:

```python
# In your main application setup
from fastapi import FastAPI
from backend.src.libs.docs import DocumentationHandler

app = FastAPI()

# Initialize and inject documentation
docs = DocumentationHandler(
    api_title="AsperBackend API",
    api_version="1.0.0",
    debug=True
)
docs.inject()

# Your API routes...
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Error Handling

The module implements comprehensive error handling:

- Logs initialization steps with debug information
- Validates provider availability before registration
- Handles missing FastAPI instances gracefully
- Reports errors through the `Disp` logging system

## Dependencies

- `fastapi`: Web framework
- `display_tty`: Logging functionality
- Provider-specific modules (swagger, redoc, rapidoc, etc.)
- Core modules (FinalClass, RuntimeControl, ServerHeaders)
- Supporting modules (PathManager, BoilerplateResponses)

## Thread Safety

The `DocumentationHandler` uses the `FinalClass` metaclass to prevent inheritance and the `RuntimeManager` singleton pattern to ensure consistent state across the application.

## Best Practices

1. **Initialize Once**: Create a single `DocumentationHandler` instance per application
2. **Call inject() After App Setup**: Ensure FastAPI app is fully configured before injecting docs
3. **Use Environment Variables**: Configure OAuth2 and API metadata through environment variables
4. **Enable Debug Logging**: Use `debug=True` during development for detailed logs
5. **Select Appropriate Providers**: Choose documentation providers based on your API consumer needs

## See Also

- [Swagger Handler Documentation](swagger/swagger_class.py)
- [ReDoc Handler Documentation](redoc/redoc_class.py)
- [Core Module Documentation](../core/core.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
