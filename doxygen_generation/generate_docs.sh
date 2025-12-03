#!/bin/bash

# Asperguide Backend - Documentation Generation Script
# This script generates the complete Doxygen documentation with PlantUML diagrams
# using a Docker container with all tools pre-installed

set -e  # Exit on error

echo "=========================================="
echo "  Asperguide Backend Documentation"
echo "=========================================="
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Docker container configuration
CONTAINER_NAME="asperguide_doxygen"
CONTAINER_IMAGE="doxygen/doxygen:latest"  # Or your custom image
DOCKERFILE_DIR="$(dirname "$0")"

# Paths
DOXYGEN_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$DOXYGEN_DIR/.." && pwd)"
OUTPUT_DIR="$DOXYGEN_DIR/documentation"

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"
echo -e "${BLUE}Doxygen config: $DOXYGEN_DIR${NC}"
echo -e "${BLUE}Output directory: $OUTPUT_DIR${NC}"
echo

# Check if Docker is available
echo "Step 1: Checking for Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found!${NC}"
    echo "Please install Docker to generate documentation."
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check if Dockerfile exists
echo
echo "Step 2: Checking for Dockerfile..."
if [ -f "$DOCKERFILE_DIR/Dockerfile" ]; then
    echo -e "${GREEN}✓ Dockerfile found${NC}"
    USE_CUSTOM_IMAGE=true
    CONTAINER_IMAGE="asperguide/doxygen:latest"
else
    echo -e "${YELLOW}⚠ No Dockerfile found, using public doxygen image${NC}"
    USE_CUSTOM_IMAGE=false
fi

# Build custom image if Dockerfile exists
if [ "$USE_CUSTOM_IMAGE" = true ]; then
    echo
    echo "Step 3: Building Docker image..."
    cd "$DOCKERFILE_DIR"
    docker build -t "$CONTAINER_IMAGE" . || {
        echo -e "${RED}✗ Failed to build Docker image${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo
    echo "Step 3: Pulling Docker image..."
    docker pull "$CONTAINER_IMAGE" || {
        echo -e "${RED}✗ Failed to pull Docker image${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Docker image ready${NC}"
fi

# Clean up any existing container
echo
echo "Step 4: Cleaning up previous containers..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate documentation
echo
echo "Step 5: Generating documentation..."
echo "This may take a few minutes..."
echo

# Run Doxygen in container
docker run --rm \
    --name "$CONTAINER_NAME" \
    -v "$PROJECT_ROOT:/workspace:ro" \
    -v "$OUTPUT_DIR:/output" \
    -w /workspace/doxygen_generation \
    "$CONTAINER_IMAGE" \
    doxygen Doxyfile

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
    echo "To view the documentation:"
    echo "  cd $OUTPUT_DIR/html"
    echo "  python3 -m http.server 8000"
    echo "  Then open: http://localhost:8000"
    echo
    
    # Set permissions
    chmod -R a+r "$OUTPUT_DIR"
    
    # Step 6: Optional - Start local server
    echo
    read -p "Do you want to start a local web server to view the docs? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$OUTPUT_DIR/html"
        echo -e "${BLUE}Starting web server on http://localhost:8000${NC}"
        echo "Press Ctrl+C to stop the server"
        python3 -m http.server 8000
    fi
else
    echo -e "${RED}✗ Documentation generation failed${NC}"
    exit 1
fi
