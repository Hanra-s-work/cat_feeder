import pytest
import types
import sys
import os
import importlib.util
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
# FILE: conftest.py
# CREATION DATE: 11-12-2025
# LAST Modified: 14:55:8 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of checking the logging library.
# // AR
# +==== END CatFeeder =================+
"""

# Dynamically determine paths relative to this test file
# Structure: <root>/tests/sql/conftest.py -> go up 2 levels to get <root>
# Works regardless of whether <root> is named "backend", "app", etc.
test_file_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(test_file_dir, "..", ".."))
src_dir = os.path.join(project_root, "src")

# Determine the actual package name from the project root folder name
# This allows the code to work whether it's "backend", "app", or any other name
project_package_name = os.path.basename(project_root)

# Ensure the src directory is available on sys.path for imports
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Provide a minimal dummy `display_tty` module so imports succeed in tests.
disp_mod = types.ModuleType("display_tty")


class DummyDisp:
    """Minimal display/logging mock for testing.

    Provides no-op implementations of all display_tty.Disp methods to
    prevent logging output from cluttering test results.
    """

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

    Args:
        name (str): Logger name (ignored in test mock).
        flag (bool): Debug flag (ignored in test mock).
        **kwargs: Additional keyword arguments (class_name, debug, etc) - ignored in test mock.

    Returns:
        DummyDisp: A no-op display object.
    """
    return DummyDisp()


disp_mod.Disp = DummyDisp
disp_mod.initialise_logger = initialise_logger
sys.modules.setdefault("display_tty", disp_mod)

# Create a lightweight synthetic package module to prevent real module loading
# This blocks the full initialization chain that requires environment variables
# The module name is determined dynamically from the project root folder name
package_mod = types.ModuleType(project_package_name)
package_mod.__path__ = [project_root]
sys.modules.setdefault(project_package_name, package_mod)

# Create a lightweight synthetic `libs` package so importing
# `libs.sql.<module>` doesn't execute the real `<root>/src/libs/__init__.py`.

sql_dir = os.path.join(project_root, "src", "libs", "sql")
utils_dir = os.path.join(project_root, "src", "libs", "utils")
libs_pkg = types.ModuleType("libs")
libs_sql_pkg = types.ModuleType("libs.sql")
libs_utils_pkg = types.ModuleType("libs.utils")

# Provide __path__ on the packages so import machinery can find submodules
libs_sql_pkg.__path__ = [sql_dir]
libs_utils_pkg.__path__ = [utils_dir]
libs_pkg.__path__ = [os.path.join(project_root, "src", "libs")]

sys.modules.setdefault("libs", libs_pkg)
sys.modules.setdefault("libs.sql", libs_sql_pkg)
sys.modules.setdefault("libs.utils", libs_utils_pkg)

# Mock the constants module that sql_connections imports
constants_mod = types.ModuleType("libs.utils.constants")
# Add dummy constants that might be imported
constants_mod.DATABASE_POOL_NAME = "test_pool"
constants_mod.DATABASE_MAX_POOL_CONNECTIONS = 5
constants_mod.DATABASE_RESET_POOL_NODE_CONNECTION = True
constants_mod.DATABASE_COLLATION = "utf8mb4_unicode_ci"
constants_mod.DATABASE_CONNECTION_TIMEOUT = 10
constants_mod.DATABASE_LOCAL_INFILE = False
constants_mod.DATABASE_INIT_COMMAND = ""
constants_mod.DATABASE_DEFAULT_FILE = None
constants_mod.DATABASE_AUTOCOMMIT = False
constants_mod.DATABASE_SSL = False
constants_mod.DATABASE_SSL_KEY = None
constants_mod.DATABASE_SSL_CERT = None
constants_mod.DATABASE_SSL_CA = None
constants_mod.DATABASE_SSL_CIPHER = None
constants_mod.DATABASE_SSL_VERIFY_CERT = False
sys.modules.setdefault("libs.utils.constants", constants_mod)


@pytest.fixture(autouse=True)
def noop_fixture():
    """A no-op autouse fixture kept for symmetry with earlier implementations.

    This fixture is automatically used by all tests in the sql test directory
    but performs no operations. It exists for consistency and potential future
    setup/teardown needs.
    """
    yield
