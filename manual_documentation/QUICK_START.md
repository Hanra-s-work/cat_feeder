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
-- FILE: QUICK_START.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 11:4:4 04-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: A handwritten quickstart of the project.
-- // AR
-- +==== END CatFeeder =================+
-->
# Quick Start: Generating Documentation

## Using Docker (Recommended)

The documentation generation uses a Docker container with all tools pre-installed (Doxygen, PlantUML, Graphviz).

Important: Run the provided scripts from the repository root (not from inside `doxygen_generation`).
Also ensure the scripts are executable before running them:

```bash
chmod +x doxygen_generation/generate_docs.sh doxygen_generation/make_documentation.sh
```

### Option 1: Simple Script (recommended)

Run the generator from the repository root:

```bash
./doxygen_generation/generate_docs.sh
```

This script will:

1. Check for Docker
2. Try to pull the prebuilt Doxygen image (`hanralatalliard/doxygen:latest`) and only build locally if the image cannot be pulled
3. Run Doxygen with PlantUML support
4. Optionally start a web server

Important: pulling the prebuilt image is strongly recommended — a pull typically takes 3–4 minutes. Building the Docker image locally (which will compile LaTeX/PDF artifacts) can be very slow — compiling LaTeX from source may take ~4 hours on typical developer machines. Build locally only as a last resort.

### Option 2: Direct Docker Command

If you prefer to run Doxygen directly in a container, run these commands from the repository root (no `cd` required):

```bash
# Build the image (if you have a Dockerfile)
# The generator script uses `hanralatalliard/doxygen:latest` by default.
docker build -t hanralatalliard/doxygen:latest doxygen_generation

# Generate documentation (run from repo root)
docker run --rm \
    -v "$(pwd)":/workspace:ro \
    -v "$(pwd)/documentation":/output:rw \
    -w /workspace/doxygen_generation \
    hanralatalliard/doxygen:latest \
    doxygen Doxyfile

# View the results
# Serve the generated HTML with the `httpd` Docker image (preferred):
docker run --rm --name Cat Feeder_docs -p 8080:80 \
    -v "$(pwd)/documentation/html":/usr/local/apache2/htdocs/:ro \
    httpd:2.4
# Open http://localhost:8080

Note: you may need to prefix `docker` with `sudo` if your user cannot access the Docker daemon (for example: `sudo docker run ...`).
```

### Option 3: Using make_documentation.sh

Run the comprehensive script from the repository root:

```bash
./doxygen_generation/make_documentation.sh
```

This provides more control and debugging options.

## What Gets Generated

```text
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
# Preferred: serve the generated HTML with an httpd Docker container
docker run --rm --name Cat Feeder_docs -p 8080:80 \
    -v "$(pwd)/documentation/html":/usr/local/apache2/htdocs/:ro \
    httpd:2.4
```

Then open: <http://localhost:8080>

Note: you may need to prefix `docker` with `sudo` if your user cannot access the Docker daemon.

### Direct File Access

Simply open `documentation/html/index.html` in your browser.

## Documentation Structure

The main page (`00_ARCHITECTURE.md`) provides:

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

### Port 8080 already in use

```bash
# Use a different host port when starting the httpd container, for example 8081:
docker run --rm --name Cat Feeder_docs -p 8081:80 \
    -v "$(pwd)/documentation/html":/usr/local/apache2/htdocs/:ro \
    httpd:2.4
```

## Container Details

The Docker container includes:

- ✅ Doxygen 1.10+
- ✅ PlantUML (latest)

**Note about live API documentation endpoints**: The live API documentation endpoints (for example `http://localhost:5000/docs`, `http://localhost:5000/redoc`, `http://localhost:5000/rapidpdf`, `http://localhost:5000/scalar`, `http://localhost:5000/editor`, `http://localhost:5000/elements`, `http://localhost:5000/explorer`) are only available when the corresponding documentation endpoints are enabled in your project's `.env` configuration. Ensure the relevant flags or features are turned on in your environment file (see `sample.env` / `tmp.env`) before expecting these routes to be served by the running application.

- ✅ Graphviz (for DOT diagrams)
- ✅ All necessary dependencies

All tools are pre-installed and configured on the PATH.

## Quick Commands

```bash
# Make scripts executable (if not already)
chmod +x doxygen_generation/generate_docs.sh doxygen_generation/make_documentation.sh

# Generate docs (run from repository root)
./doxygen_generation/generate_docs.sh

# Serve the docs locally with httpd (preferred)
docker run --rm --name Cat Feeder_docs -p 8080:80 \
    -v "$(pwd)/documentation/html":/usr/local/apache2/htdocs/:ro \
    httpd:2.4

# Clean output
rm -rf documentation/

# Rebuild from scratch
rm -rf documentation/ && ./doxygen_generation/generate_docs.sh
```

---

 **Need help?** See [00_ARCHITECTURE.md](00_ARCHITECTURE.md) for full details.
