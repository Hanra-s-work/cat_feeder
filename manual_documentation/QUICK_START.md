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
-- FILE: QUICK_START.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 13:45:6 02-12-2025
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: A handwritten quickstart of the project.
-- // AR
-- +==== END AsperBackend =================+
-->
# Quick Start: Generating Documentation

## Using Docker (Recommended)

The documentation generation uses a Docker container with all tools pre-installed (Doxygen, PlantUML, Graphviz).

### Option 1: Simple Script

```bash
cd doxygen_generation
./generate_docs.sh
```

This script will:

1. Check for Docker
2. Build/pull the Doxygen container image
3. Run Doxygen with PlantUML support
4. Optionally start a web server

### Option 2: Direct Docker Command

```bash
cd doxygen_generation

# Build the image (if you have a Dockerfile)
docker build -t asperguide/doxygen:latest .

# Generate documentation
docker run --rm \
    -v "$(pwd)/..:/workspace:ro" \
    -v "$(pwd)/documentation:/output" \
    -w /workspace/doxygen_generation \
    asperguide/doxygen:latest \
    doxygen Doxyfile

# View the results
cd documentation/html
python3 -m http.server 8000
# Open http://localhost:8000
```

### Option 3: Using make_documentation.sh

If you prefer the existing comprehensive script:

```bash
cd doxygen_generation
./make_documentation.sh
```

This provides more control and debugging options.

## What Gets Generated

```
documentation/
├── html/              # HTML documentation (main output)
│   ├── index.html    # Start here!
│   ├── pages.html    # Manual documentation pages
│   └── ...
├── latex/             # LaTeX/PDF documentation
├── man/               # Man pages
└── xml/               # XML output
```

## Viewing the Documentation

### Local Web Server

```bash
cd documentation/html
python3 -m http.server 8000
```

Then open: <http://localhost:8000>

### Direct File Access

Simply open `documentation/html/index.html` in your browser.

## Documentation Structure

The main page (`00_OVERVIEW.md`) provides:

- Architecture overview
- System layers explanation
- Design patterns
- Links to detailed documentation

### Navigation in Generated Docs

- **Main Page** → Architecture overview
- **Related Pages** → Layer-specific documentation
- **Classes** → Auto-generated API docs
- **Files** → Source code documentation

## PlantUML Diagrams

All diagrams are automatically rendered from the PlantUML code in the markdown files. No manual diagram generation needed!

## Troubleshooting

### Docker not found

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
```

### Permission denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Port 8000 already in use

```bash
# Use a different port
python3 -m http.server 8080
```

## Container Details

The Docker container includes:

- ✅ Doxygen 1.10+
- ✅ PlantUML (latest)
- ✅ Graphviz (for DOT diagrams)
- ✅ All necessary dependencies

All tools are pre-installed and configured on the PATH.

## Quick Commands

```bash
# Generate docs
cd doxygen_generation && ./generate_docs.sh

# View docs
cd documentation/html && python3 -m http.server 8000

# Clean output
rm -rf documentation/

# Rebuild from scratch
rm -rf documentation/ && ./generate_docs.sh
```

---

**Need help?** See [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md) for full details.
