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
# FILE: start_compose.sh
# CREATION DATE: 16-10-2025
# LAST Modified: 3:11:10 04-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Wrapper script that forwards to the actual implementation in docker/utils/start_compose.sh
# // AR
# +==== END CatFeeder =================+
# 
#
# @file start_compose.sh
# @brief Convenience wrapper to launch docker/utils/start_compose.sh from the repository root.
#
# This script allows users to run start_compose.sh from the repository root directory
# while the actual implementation lives in docker/utils/. All command-line arguments
# are forwarded to the actual script.
#
# @author Cat Feeder
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
