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
# FILE: rebuild_from_scratch.sh
# CREATION DATE: 16-10-2025
# LAST Modified: 1:28:8 26-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Wrapper script that forwards to the actual implementation in docker/utils/rebuild_from_scratch.sh
# // AR
# +==== END AsperBackend =================+
# 
#
# @file rebuild_from_scratch.sh
# @brief Convenience wrapper to launch docker/utils/rebuild_from_scratch.sh from the repository root.
#
# This script allows users to run rebuild_from_scratch.sh from the repository root directory
# while the actual implementation lives in docker/utils/. All command-line arguments
# are forwarded to the actual script.
#
# WARNING: This is a destructive script that removes ALL Docker volumes system-wide.
# See docker/utils/rebuild_from_scratch.sh for details.
#
# @author Asperguide
# @date 2025-10-16
#
# Usage:
#   ./rebuild_from_scratch.sh [arguments...]
#
# Notes:
#  - This script must be run from the repository root
#  - All arguments are passed through to docker/utils/rebuild_from_scratch.sh

if [ ! -f "docker/utils/rebuild_from_scratch.sh" ]; then
	echo "Error: docker/utils/rebuild_from_scratch.sh not found." >&2
	echo "Please ensure you are running this script from the repository root." >&2
	exit 1
fi

# Forward all arguments to the actual implementation
./docker/utils/rebuild_from_scratch.sh "$@"
