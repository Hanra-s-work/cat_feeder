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
# FILE: start_compose.sh
# CREATION DATE: 16-10-2025
# LAST Modified: 1:32:55 26-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Wrapper script that forwards to the actual implementation in docker/utils/start_compose.sh
# // AR
# +==== END AsperBackend =================+
# 
#
# @file start_compose.sh
# @brief Convenience wrapper to launch docker/utils/start_compose.sh from the repository root.
#
# This script allows users to run start_compose.sh from the repository root directory
# while the actual implementation lives in docker/utils/. All command-line arguments
# are forwarded to the actual script.
#
# @author Asperguide
# @date 2025-10-16
#
# Usage:
#   ./start_compose.sh [arguments...]
#
# Notes:
#  - This script must be run from the repository root
#  - All arguments are passed through to docker/utils/start_compose.sh

if [ ! -f "docker/utils/start_compose.sh" ]; then
	echo "Error: docker/utils/start_compose.sh not found." >&2
	echo "Please ensure you are running this script from the repository root." >&2
	exit 1
fi

# Forward all arguments to the actual implementation
./docker/utils/start_compose.sh "$@"
