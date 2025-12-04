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
# FILE: import_time.sh
# CREATION DATE: 27-11-2025
# LAST Modified: 4:33:36 27-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This file aims to provide an easy way to track the time the server takes to import the required dependencies.
# // AR
# +==== END CatFeeder =================+
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

IMPORT_LOG="import_time_$(date +%Y-%m-%d_%H-%M-%S).log"

echo "Running server with import timing capture..."
echo "Full output saved to: ${IMPORT_LOG}"
echo "To view only import timing: grep 'import time:' ${IMPORT_LOG}"
echo ""

# Run server with import timing, capture all output
python3 -X importtime ./backend/src/ \
    --host 0.0.0.0 \
    --port 5002 \
    --debug 2>&1 | tee "${IMPORT_LOG}"

echo "Import time data saved to: ${IMPORT_LOG}"
deactivate
