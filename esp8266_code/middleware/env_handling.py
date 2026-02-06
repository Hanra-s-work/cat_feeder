r""" 
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
# FILE: env_handling.py
# CREATION DATE: 07-02-2026
# LAST Modified: 0:35:3 07-02-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the middleware file in charge of loading and parsing the .env file to prevent users from pushing hardcoded information in the script.
# // AR
# +==== END CatFeeder =================+
"""

import os
import glob

# Manually load .env file (no external dependencies needed)


def load_env_file(filepath='../.env'):
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    env_vars[key] = value
                    # Also set in environment for PlatformIO
                    os.environ[key] = value
    return env_vars


if __name__ == "__main__":
    # Load environment variables
    env_vars = load_env_file()

    # Find all .hpp files in the include folder
    include_dir = os.path.join(os.path.dirname(__file__), '..', 'include')
    hpp_files = glob.glob(os.path.join(include_dir, '*.hpp'))

    # Replace placeholders in .hpp files
    for hpp_file in hpp_files:
        with open(hpp_file, 'r', encoding="utf-8") as f:
            content = f.read()

        for key, value in env_vars.items():
            placeholder = f'[{key}]'
            content = content.replace(placeholder, value)

        with open(hpp_file, 'w', encoding="utf-8") as f:
            f.write(content)
