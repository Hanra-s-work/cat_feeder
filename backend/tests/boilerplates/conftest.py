r"""
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
# FILE: conftest.py
# CREATION DATE: 14-12-2025
# LAST Modified: 14:53:59 19-12-2025
# DESCRIPTION:
# Test configuration for boilerplates tests (path and lightweight mocks).
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Configuration for boilerplates tests to work from multiple locations.
# // AR
# +==== END CatFeeder =================+
"""
import os
import sys
import types
import pytest

# Determine project root relative to this test file
test_file_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(test_file_dir, "..", ".."))
src_dir = os.path.join(project_root, "src")

project_package_name = os.path.basename(project_root)

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Minimal display_tty stub to avoid importing the real logging
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

    def log_critical(self, *a, **k):
        pass

    def disp_print_debug(self, *a, **k):
        pass


def initialise_logger(name=None, flag=False, **kwargs):
    """Create and return a dummy display object for testing.

    Accepts both positional and keyword arguments to be compatible with
    real initialise_logger calls that may use class_name=, debug=, etc.
    """
    return DummyDisp()


disp_mod.Disp = DummyDisp
disp_mod.initialise_logger = initialise_logger
sys.modules.setdefault("display_tty", disp_mod)

# Lightweight project package module to allow imports like 'backend' or project folder name
package_mod = types.ModuleType(project_package_name)
package_mod.__path__ = [project_root]
sys.modules.setdefault(project_package_name, package_mod)

# Create libs package and expose the boilerplates package path
libs_pkg = types.ModuleType("libs")
sys.modules["libs"] = libs_pkg

libs_boilerplates_pkg = types.ModuleType("libs.boilerplates")
libs_boilerplates_pkg.__path__ = [
    os.path.join(src_dir, "libs", "boilerplates")]
sys.modules["libs.boilerplates"] = libs_boilerplates_pkg


@pytest.fixture(autouse=True)
def noop_fixture():
    # placeholder for future setup/teardown
    yield
