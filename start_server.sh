#!/bin/bash
# 
# +==== BEGIN CatFeeder =================+
# LOGO: 
# ..............(..../\\
# ...............)..(.')
# ..............(../..)
# ...............\\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: start_server.sh
# CREATION DATE: 28-09-2025
# LAST Modified: 14:21:56 04-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The server starter
# // AR
# +==== END CatFeeder =================+
# 
SYSTEM_ENV_LOCATION=${1:-"$(pwd)"}
SYSTEM_ENV_NAME=${2:-"server_env"}
shift 2
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
    --debug $@

deactivate
