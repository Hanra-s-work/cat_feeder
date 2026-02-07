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
# LAST Modified: 1:19:55 07-02-2026
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
import shutil

# Import the SCons environment
Import("env")

# Manually load .env file (no external dependencies needed)


def locate_env_file() -> str:
    """
        Locate the environement file (.env) in the current, parent, or grandparent directory.

    Raises:
        FileNotFoundError: If no .env file is found in the current, parent, or grandparent directories.

    Returns:
        str: The path to the located .env file.
    """
    # Check current directory (project root)
    current_dir = os.getcwd()
    env_path = os.path.join(current_dir, '.env')
    if os.path.exists(env_path):
        return env_path

    # Check parent directory
    parent_dir = os.path.dirname(current_dir)
    env_path = os.path.join(parent_dir, '.env')
    if os.path.exists(env_path):
        return env_path

    # Check grandparent directory
    grandparent_dir = os.path.dirname(parent_dir)
    env_path = os.path.join(grandparent_dir, '.env')
    if os.path.exists(env_path):
        return env_path

    raise FileNotFoundError(
        "No .env file found in current, parent, or grandparent directories."
    )


def load_env_file(filepath='../.env'):
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Strip surrounding quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    env_vars[key] = value
                    # Also set in environment for PlatformIO
                    os.environ[key] = value
    return env_vars


def main():
    # Load environment variables
    env_file = locate_env_file()
    print(f"Loading environment variables from .env file '({env_file})'...")
    env_vars = load_env_file(env_file)
    print(f"Loaded environment variables: {env_vars}")

    # Create shadow copies in .pio/modified_include
    modified_include_dir = os.path.join(os.getcwd(), '.pio', 'modified_include')
    os.makedirs(modified_include_dir, exist_ok=True)
    print(f"Creating shadow copies in: {modified_include_dir}")

    include_dir = os.path.join(os.getcwd(), 'include')
    for hpp_file in glob.glob(os.path.join(include_dir, '*.hpp')):
        shutil.copy(hpp_file, modified_include_dir)

    # Modify the shadow copies
    print("Processing shadow .hpp files to replace placeholders...")
    hpp_files = glob.glob(os.path.join(modified_include_dir, '*.hpp'))
    print(f"Found shadow .hpp files: {hpp_files}")

    for hpp_file in hpp_files:
        with open(hpp_file, 'r', encoding="utf-8") as f:
            content = f.read()

        for key, value in env_vars.items():
            placeholder = f'[{key}]'
            content = content.replace(placeholder, value)

        with open(hpp_file, 'w', encoding="utf-8") as f:
            f.write(content)

    # Set the include path to prioritize shadow copies
    print(f"CXXFLAGS before prepend: {env.get('CXXFLAGS', [])}")
    env.Prepend(CXXFLAGS=['-I' + modified_include_dir])
    print(f"Prepended -I flag: -I{modified_include_dir}")
    print(f"CXXFLAGS after prepend: {env['CXXFLAGS']}")


main()
