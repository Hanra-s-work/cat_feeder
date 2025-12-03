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
# .........##.##...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: start_server.sh
# CREATION DATE: 28-09-2025
# LAST Modified: 0:31:58 26-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The server starter
# // AR
# +==== END AsperBackend =================+
# 
SYSTEM_ENV_LOCATION=${1:-"$(pwd)"}
SYSTEM_ENV_NAME=${2:-"server_env"}
if [[ -f "${SYSTEM_ENV_LOCATION}/${SYSTEM_ENV_NAME}/bin/activate" ]]; then
    . ${SYSTEM_ENV_LOCATION}/${SYSTEM_ENV_NAME}/bin/activate
elif [[ -f "./server_env/bin/activate" ]]; then
    . ./server_env/bin/activate
else
    make create_environement install_dependencies
    if [[ -f "./server_env/bin/activate" ]]; then
        . ./server_env/bin/activate
    else
        echo "Error: Unable to create or activate environment"
        exit 1
    fi
fi

python3 ./backend/src/ \
    --host 0.0.0.0 \
    --port 5001 \
    --debug

deactivate
