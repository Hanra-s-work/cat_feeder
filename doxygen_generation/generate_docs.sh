#!/bin/bash
# 
# +==== BEGIN CatFeeder =================+
# LOGO: 
# ..............(..../\
# ...............)..(.')
# ..............(../..)
# ...............\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: generate_docs.sh
# CREATION DATE: 04-12-2025
# LAST Modified: 14:39:57 04-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: An easy script to generate the doxygen documentation based on the local doxygen configuration.
# // AR
# +==== END CatFeeder =================+
# 

# Cat Feeder Backend - Documentation Generation Script
# This script generates the complete Doxygen documentation with PlantUML diagrams
# using a Docker container with all tools pre-installed


set -e  # Exit on error

echo "=========================================="
echo "  Cat Feeder Backend Documentation"
echo "=========================================="
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Docker container configuration
CONTAINER_NAME="cat_feeder_doxygen"
CONTAINER_IMAGE="hanralatalliard/doxygen:latest"
DOCKERFILE_DIR="$(dirname "$0")"

# HTTPD server configuration
DOCS_CONTAINER_NAME="Cat Feeder_docs"
DOCS_IMAGE="httpd:2.4"
HOST_PORT=8080

# Paths
DOXYGEN_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$DOXYGEN_DIR/.." && pwd)"
# Use repository-root `documentation` to match the GitHub Action output location
OUTPUT_DIR="$PROJECT_ROOT/documentation"

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"
echo -e "${BLUE}Doxygen config: $DOXYGEN_DIR${NC}"
echo -e "${BLUE}Output directory: $OUTPUT_DIR${NC}"
echo

# Check if Docker is available
echo "Step 1: Checking for Docker..."
if ! command -v docker &> /dev/null; then
    # Try to detect docker available via sudo (some environments have docker only for root)
    if sudo -n command -v docker &> /dev/null 2>/dev/null; then
        SUDO_CMD="sudo"
    else
        echo -e "${RED}✗ Docker CLI not found in PATH.${NC}"
        echo "Please install Docker or ensure it's available in PATH for this user."
        exit 1
    fi
else
    SUDO_CMD=""
fi

# Helper to run docker commands with optional sudo
run_docker() {
    if [ -n "${SUDO_CMD}" ]; then
        sudo docker "$@"
    else
        docker "$@"
    fi
}

# Check daemon connectivity
if ! run_docker info >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Docker CLI found but daemon not accessible or not running.${NC}"
    echo "Try: sudo systemctl start docker  (or ensure your user is in the docker group)."
    exit 1
fi

echo -e "${GREEN}✓ Docker available${NC}"

# Check if Dockerfile exists
echo
echo "Step 2: Checking for Dockerfile..."
if [ -f "$DOCKERFILE_DIR/Dockerfile" ]; then
    echo -e "${GREEN}✓ Dockerfile found${NC}"
    USE_CUSTOM_IMAGE=true
    # Keep the configured CONTAINER_IMAGE (e.g. your custom 'hanralatalliard/doxygen')
    # We'll try to pull it first and fall back to building the local Dockerfile if pull fails.
else
    echo -e "${YELLOW}⚠ No Dockerfile found, using public doxygen image${NC}"
    USE_CUSTOM_IMAGE=false
fi

# Build or pull Docker image
if [ "$USE_CUSTOM_IMAGE" = true ]; then
    echo
    echo "Step 3: Attempting to pull prebuilt custom image '$CONTAINER_IMAGE'..."
    if run_docker pull "$CONTAINER_IMAGE"; then
        echo -e "${GREEN}✓ Pulled prebuilt image $CONTAINER_IMAGE${NC}"
    else
        echo -e "${YELLOW}⚠ Prebuilt image not available; building locally (this may take a long time)...${NC}"
        cd "$DOCKERFILE_DIR"
        if ! run_docker build -t "$CONTAINER_IMAGE" .; then
            echo -e "${RED}✗ Failed to build Docker image${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Docker image built successfully${NC}"
    fi
else
    echo
    echo "Step 3: Pulling public doxygen image '$CONTAINER_IMAGE'..."
    if ! run_docker pull "$CONTAINER_IMAGE"; then
        echo -e "${RED}✗ Failed to pull Docker image${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker image ready${NC}"
fi

# Clean up any existing container
echo
echo "Step 4: Cleaning up previous containers..."
run_docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate documentation
echo
echo "Step 5: Generating documentation..."
echo "This may take a few minutes..."
echo

# Run Doxygen in container using the same approach as the GitHub Action:
# - mount the repository at /app (read-write)
# - copy the Doxyfile into /app and run doxygen there
# - mount the host output directory at /documentation so generated files are written outside source tree
run_docker run --rm \
    --name "$CONTAINER_NAME" \
    -v "$PROJECT_ROOT":/app:rw \
    -v "$OUTPUT_DIR":/documentation:rw \
    -w /app \
    "$CONTAINER_IMAGE" \
    /bin/bash -c "cp -v doxygen_generation/Doxyfile ./Doxyfile && doxygen ; exit $?"

if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}✓ Documentation generated successfully!${NC}"
    echo
    echo "=========================================="
    echo "  Documentation Generated Successfully!"
    echo "=========================================="
    echo
    echo "HTML Documentation: $OUTPUT_DIR/html/index.html"
    echo
    echo "To view the documentation locally you can use the provided httpd Docker image."
    echo "It will serve files from $OUTPUT_DIR/html on http://localhost:$HOST_PORT"
    echo

    # Reclaim ownership like the workflow (if script was run under sudo)
    if [ "$(id -u)" -eq 0 ]; then
        OWNER="${SUDO_USER:-${USER}}"
        if [ -n "$OWNER" ]; then
            echo "Owning the generated content (replacing root by the original user: $OWNER)"
            chown -Rv "$OWNER:$OWNER" "$OUTPUT_DIR" || true
            echo "Granting all users read-write rights on the files"
            chmod -Rv a+rw "$OUTPUT_DIR" || true
        fi
    else
        # Non-root runs: ensure output is world-readable
        chmod -R a+r "$OUTPUT_DIR" || true
    fi

    # Step 6: Optional - Start httpd Docker server
    echo
    read -p "Start an httpd Docker container to serve the docs on http://localhost:$HOST_PORT? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Ensure Docker daemon is still accessible before starting container
        if ! run_docker info >/dev/null 2>&1; then
            echo -e "${RED}✗ Docker daemon not accessible; cannot start httpd container.${NC}"
            echo "Try: sudo systemctl start docker  (or ensure your user is in the docker group)."
            exit 1
        fi


        echo -e "${BLUE}Starting httpd Docker container binding $OUTPUT_DIR/html -> /usr/local/apache2/htdocs/${NC}"
        echo "Serving at: http://localhost:$HOST_PORT"
        echo "Press Ctrl+C to stop the container (or run: docker stop $DOCS_CONTAINER_NAME)"

        # Remove any previous container with the same name
        run_docker rm -f "$DOCS_CONTAINER_NAME" 2>/dev/null || true

        # Run in the foreground so Ctrl+C stops it; use --rm to cleanup on exit
        run_docker run --rm --name "$DOCS_CONTAINER_NAME" -p ${HOST_PORT}:80 \
            -v "$OUTPUT_DIR/html":/usr/local/apache2/htdocs/:ro \
            "$DOCS_IMAGE"
    fi
else
    echo -e "${RED}✗ Documentation generation failed${NC}"
    exit 1
fi
