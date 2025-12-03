#!/bin/bash
# 
# +==== BEGIN AsperBackend =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: generate_plantuml_diagrams.sh
# CREATION DATE: 02-12-2025
# LAST Modified: 15:36:34 02-12-2025
# DESCRIPTION: 
# Generate PNG, SVG, and PDF versions of all PlantUML diagrams
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Documentation diagram generation
# // AR
# +==== END AsperBackend =================+
# 

set -e

# Configuration
SUDO=${SUDO:-sudo}
PORT=8082
CONTAINER_NAME=plantuml
IMAGE_NAME=plantuml/plantuml-server:jetty
DOCS_DIR="."
SERVER_URL="http://127.0.0.1:${PORT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PlantUML Diagram Generator - Asperguide Backend          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Stop and remove existing container
echo -e "${YELLOW}[1/5] Stopping existing PlantUML container...${NC}"
if $SUDO docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    $SUDO docker stop $CONTAINER_NAME 2>/dev/null || true
    $SUDO docker container rm $CONTAINER_NAME 2>/dev/null || true
    echo -e "${GREEN}✓ Stopped and removed existing container${NC}"
else
    echo -e "${GREEN}✓ No existing container found${NC}"
fi
echo ""

# Pull latest image
echo -e "${YELLOW}[2/5] Pulling latest PlantUML server image...${NC}"
$SUDO docker pull $IMAGE_NAME
echo -e "${GREEN}✓ Image pulled successfully${NC}"
echo ""

# Start new container
echo -e "${YELLOW}[3/5] Starting PlantUML server container...${NC}"
$SUDO docker run -d -p $PORT:8080 --name $CONTAINER_NAME $IMAGE_NAME
echo -e "${GREEN}✓ Container started on port ${PORT}${NC}"
echo ""

# Wait for server to be ready
echo -e "${YELLOW}[4/5] Waiting for PlantUML server to be ready...${NC}"
for i in {1..30}; do
    if curl -s "${SERVER_URL}/svg/" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Server failed to start within 30 seconds${NC}"
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""

# Generate diagrams
echo -e "${YELLOW}[5/5] Generating diagrams from PlantUML files...${NC}"
echo ""

# Change to docs directory
cd "$DOCS_DIR"

# Find all .puml files
PUML_FILES=$(find . -name "*.puml" -type f | sort)
TOTAL=$(echo "$PUML_FILES" | wc -l)
CURRENT=0
SUCCESS=0
FAILED=0

for file in $PUML_FILES; do
    CURRENT=$((CURRENT + 1))
    dir=$(dirname "$file")
    base=$(basename "$file" .puml)
    
    echo -e "${BLUE}[$CURRENT/$TOTAL]${NC} Processing: ${file}"
    
    # Generate PNG
    if curl -s -X POST --data-binary @"$file" "${SERVER_URL}/png/" -o "$dir/$base.png" 2>/dev/null; then
        echo -e "  ${GREEN}✓ PNG${NC} created"
    else
        echo -e "  ${RED}✗ PNG${NC} failed"
        FAILED=$((FAILED + 1))
        continue
    fi
    
    # Generate SVG
    if curl -s -X POST --data-binary @"$file" "${SERVER_URL}/svg/" -o "$dir/$base.svg" 2>/dev/null; then
        echo -e "  ${GREEN}✓ SVG${NC} created"
    else
        echo -e "  ${RED}✗ SVG${NC} failed"
        FAILED=$((FAILED + 1))
        continue
    fi
    
    # Generate PDF (if supported by server)
    if curl -s -X POST --data-binary @"$file" "${SERVER_URL}/pdf/" -o "$dir/$base.pdf" 2>/dev/null; then
        # Check if PDF is valid (not an error message)
        if file "$dir/$base.pdf" | grep -q "PDF"; then
            echo -e "  ${GREEN}✓ PDF${NC} created"
        else
            echo -e "  ${YELLOW}⚠ PDF${NC} not supported by server"
            rm -f "$dir/$base.pdf"
        fi
    else
        echo -e "  ${YELLOW}⚠ PDF${NC} not supported by server"
    fi
    
    SUCCESS=$((SUCCESS + 1))
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Generation Summary                                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo -e "${GREEN}✓ Successfully processed: ${SUCCESS}/${TOTAL}${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}✗ Failed: ${FAILED}/${TOTAL}${NC}"
fi
echo ""
echo -e "${GREEN}All diagrams have been generated in manual_documentation/${NC}"
echo -e "${YELLOW}PlantUML server is running on ${SERVER_URL}${NC}"
echo -e "${YELLOW}To stop: ${SUDO} docker stop ${CONTAINER_NAME}${NC}"
