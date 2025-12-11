""" 
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
# FILE: conftest.py
# CREATION DATE: 11-12-2025
# LAST Modified: 1:59:1 11-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of checking the logging library.
# // AR
# +==== END CatFeeder =================+
"""
import importlib.util
import os
import sys
import types
import pytest

# At import time, ensure the project's backend `src` directory is available
# on sys.path so tests can import `libs.*` during collection.
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", ".."))
backend_src = os.path.join(project_root, "src")
if backend_src not in sys.path:
    sys.path.insert(0, backend_src)

# Provide a minimal dummy `display_tty` module so imports succeed in tests.
disp_mod = types.ModuleType("display_tty")


class DummyDisp:
    def __init__(self, *a, **k):
        pass

    def update_disp_debug(self, *a, **k):
        pass

    def log_debug(self, *a, **k):
        pass

    def log_info(self, *a, **k):
        pass

    def log_warning(self, *a, **k):
        pass

    def log_error(self, *a, **k):
        pass

    def disp_print_debug(self, *a, **k):
        pass


def initialise_logger(name, flag=False):
    return DummyDisp()


disp_mod.Disp = DummyDisp
disp_mod.initialise_logger = initialise_logger
sys.modules.setdefault("display_tty", disp_mod)

# Create a lightweight synthetic `libs` package so importing
# `libs.sql.<module>` doesn't execute the real `backend/src/libs/__init__.py`.

sql_dir = os.path.join(project_root, "src", "libs", "sql")
libs_pkg = types.ModuleType("libs")
libs_sql_pkg = types.ModuleType("libs.sql")
# Provide __path__ on the package so import machinery can find submodules
libs_sql_pkg.__path__ = [sql_dir]
sys.modules.setdefault("libs", libs_pkg)
sys.modules.setdefault("libs.sql", libs_sql_pkg)


@pytest.fixture(autouse=True)
def noop_fixture():
    """A no-op autouse fixture kept for symmetry with earlier implementations."""
    yield
