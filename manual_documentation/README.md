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
-- FILE: README.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 13:44:45 02-12-2025
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: The doxygen handwritten readme of the project.
-- // AR
-- +==== END AsperBackend =================+
-->
# Asperguide Backend Manual Documentation

This directory contains comprehensive architectural documentation for the Asperguide Backend, organized to match the actual source code structure in `backend/src/`.

## 📚 Documentation Structure

### Architecture Overview

| File | Description |
|------|-------------|
| **[00_ARCHITECTURE.md](00_ARCHITECTURE.md)** | System architecture, design patterns, and module interactions |

### Project Structure

| File | Description |
|------|-------------|
| **[project_structure.md](project_structure/project_structure.md)** | Directory structure, entry points, assets, dependencies |
| **[server_main.md](project_structure/server_main.md)** | Entry point and CLI arguments |

### Module Documentation (maps to `backend/src/libs/`)

| Module | Description | Documentation |
|--------|-------------|---------------|
| **server.py** | Main Server orchestration | [server/server.md](server/server.md) |
| **boilerplates/** | Request/Response handlers | [boilerplates/boilerplates.md](boilerplates/boilerplates.md) |
| **bucket/** | S3 storage (MinIO) | [bucket/bucket.md](bucket/bucket.md) |
| **core/** | RuntimeManager, Singletons | [core/core.md](core/core.md) |
| **crons/** | Background tasks | [crons/crons.md](crons/crons.md) |
| **docs/** | API documentation | [docs/docs.md](docs/docs.md) |
| **e_mail/** | Email management | [e_mail/e_mail.md](e_mail/e_mail.md) |
| **endpoint_manager/** | Endpoint registration | [endpoint_manager/endpoint_manager.md](endpoint_manager/endpoint_manager.md) |
| **fffamily/** | FFmpeg utilities | [fffamily/fffamily.md](fffamily/fffamily.md) |
| **http_codes/** | HTTP status codes | [http_codes/http_codes.md](http_codes/http_codes.md) |
| **path_manager/** | Route management | [path_manager/path_manager.md](path_manager/path_manager.md) |
| **redis/** | Redis caching | [redis/redis.md](redis/redis.md) |
| **server_header/** | CORS, security headers | [server_header/server_header.md](server_header/server_header.md) |
| **sql/** | Database (MySQL) | [sql/sql.md](sql/sql.md) |
| **utils/** | OAuth, passwords, etc. | [utils/utils.md](utils/utils.md) |

### Additional Documentation

| File | Description |
|------|-------------|
| **[QUICK_START.md](QUICK_START.md)** | Quick start guide for development |
| **[DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)** | Documentation overview |

## 🎯 Purpose

This documentation serves multiple purposes:

1. **Onboarding**: Help new developers understand the system architecture
2. **Reference**: Provide detailed class and interaction diagrams
3. **Design Documentation**: Explain design patterns and architectural decisions
4. **Doxygen Integration**: Integrated into the main Doxygen-generated documentation

## 🔧 How to Use

### For Developers

1. **Start with the Overview**: Read [00_OVERVIEW.md](00_OVERVIEW.md) to understand the big picture
2. **Dive into Layers**: Explore specific layers based on your work area
3. **Reference Diagrams**: Use PlantUML diagrams to understand component interactions

### For Doxygen Generation

These files are automatically included in the Doxygen-generated documentation:

```bash
# Generate documentation
cd doxygen_generation
doxygen Doxyfile

# View in browser
cd documentation/html
python3 -m http.server 8000
# Open http://localhost:8000
```

The PlantUML diagrams will be rendered as images in the HTML output.

## 📊 Diagram Format: PlantUML

All diagrams use **PlantUML** syntax for the following reasons:

✅ **Advantages:**

- Text-based (perfect for version control)
- Native Doxygen support
- AI-friendly (easy to generate and modify)
- Renders to SVG/PNG automatically
- Consistent with Doxygen's automatic UML diagrams

### Diagram Types Used

1. **Component Diagrams**: System architecture and module relationships
2. **Class Diagrams**: Class structure and inheritance
3. **Sequence Diagrams**: Interaction flows and message passing
4. **Deployment Diagrams**: Service initialization and dependencies

## 🏗️ Architecture Layers

The backend follows a **layered architecture**:

```text
┌─────────────────────────────────────┐
│       Entry Point Layer             │  server_main.py
├─────────────────────────────────────┤
│       Application Layer             │  Server, PathManager, EndpointManager
├─────────────────────────────────────┤
│       Service Layer                 │  BackgroundTasks, OAuth, MailManagement
├─────────────────────────────────────┤
│       Data Layer                    │  SQL, Redis, Bucket (S3)
├─────────────────────────────────────┤
│       Core Layer                    │  RuntimeManager, FinalSingleton
├─────────────────────────────────────┤
│       Utility Layer                 │  Boilerplates, HttpCodes, Passwords
└─────────────────────────────────────┘
```

## 🔑 Key Design Patterns

### 1. Service Locator Pattern

**Implementation**: `RuntimeManager`

- Centralized service container
- Lazy initialization
- Thread-safe singleton management

### 2. Final Singleton Pattern

**Implementation**: `FinalSingleton` base class

- Prevents direct instantiation
- Enforces RuntimeManager usage
- Thread-safe creation

### 3. Path Registration Pattern

**Implementation**: `PathManager`

- Deferred route registration
- Decouples endpoints from FastAPI
- Enables route introspection

### 4. Boilerplate Pattern

**Implementation**: `BoilerplateResponses` / `BoilerplateIncoming`

- Standardized request/response handling
- Consistent error formats
- Validation decorators

## 📖 Reading Guide

### For Backend Developers

1. Start: `00_OVERVIEW.md` → `01_CORE.md`
2. Then: `02_DATA_LAYER.md` for database/caching
3. Then: `03_APPLICATION_LAYER.md` for endpoint management

### For Frontend Developers

1. Start: `00_OVERVIEW.md` (high-level only)
2. Focus: `03_APPLICATION_LAYER.md` → EndpointManager
3. Reference: API documentation at `/docs` endpoint

### For DevOps Engineers

1. Start: `00_OVERVIEW.md` → Architecture Diagram
2. Focus: Service initialization sequence
3. Reference: Docker configuration and deployment

### For QA/Testing

1. Start: `00_OVERVIEW.md` → Testing Strategy
2. Reference: Testing sections in each layer document
3. Focus: Mock implementations and test patterns

## 🛠️ Maintenance

### Adding New Documentation

When adding new modules:

1. Create new `.md` file following naming convention
2. Include PlantUML diagrams for:
   - Class structure
   - Interaction flows
   - Integration points
3. Link from related documents
4. Update this README

### Updating Diagrams

PlantUML diagrams can be edited directly in the `.md` files:

```markdown
@startuml
' Edit diagram here
@enduml
```

After editing, regenerate Doxygen documentation to see rendered diagrams.

## 🔗 Links

- **Main Doxygen Docs**: `../doxygen_generation/documentation/html/index.html` (after generation)
- **Source Code**: `../backend/src/libs/`
- **API Documentation**: `http://localhost:5000/docs` (when server running)
- **PlantUML Documentation**: <https://plantuml.com/>

## 📝 Document Conventions

### Headers

- Use `{#anchor_name}` for Doxygen anchors
- Use hierarchical numbering for sections

### Code Blocks

- Use language-specific syntax highlighting
- Include explanatory comments
- Provide context before/after code

### Diagrams

- Always include `!theme plain` for consistency
- Add notes for complex interactions
- Use meaningful component names

### Links

- Use relative links for local files
- Use Doxygen `\ref` for cross-references
- Always verify links after generation

## 🤝 Contributing

When contributing to this documentation:

1. **Accuracy**: Ensure diagrams match actual code
2. **Clarity**: Write for multiple audiences (junior devs to architects)
3. **Completeness**: Cover common use cases and edge cases
4. **Consistency**: Follow existing formatting and style
5. **Testing**: Generate Doxygen to verify rendering

## 📅 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-02 | Initial comprehensive documentation created |

---

**Questions?** Check the [Overview](00_OVERVIEW.md) or consult the generated Doxygen documentation.
