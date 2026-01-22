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
# LAST Modified: 6:47:33 12-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Configuration for http_codes tests to work from multiple locations.
# // AR
# +==== END CatFeeder =================+
"""
import os
import sys
import types
import pytest

# Dynamically determine paths relative to this test file
# Structure: <root>/tests/http_codes/conftest.py -> go up 2 levels to get <root>
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

# Also add project_root to allow "src." imports from project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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

# Create a lightweight synthetic package module to prevent full backend module loading
# The module name is determined dynamically from the project root folder name
package_mod = types.ModuleType(project_package_name)
package_mod.__path__ = [project_root]
sys.modules.setdefault(project_package_name, package_mod)

# Create synthetic libs package
libs_pkg = types.ModuleType("libs")
sys.modules["libs"] = libs_pkg

# Create libs.core with FinalClass mock - inject directly without loading files
libs_core_pkg = types.ModuleType("libs.core")


class FinalClass(type):
    """Mock FinalClass metaclass for testing - prevents subclassing."""
    def __init__(cls, name, bases, dct):
        for base in bases:
            if isinstance(base, FinalClass):
                raise TypeError(
                    f"Class '{base.__name__}' is final and cannot be subclassed.")
        super().__init__(name, bases, dct)


# Inject FinalClass directly into the module
libs_core_pkg.FinalClass = FinalClass
sys.modules["libs.core"] = libs_core_pkg

# Create libs.http_codes with proper __path__ for module file discovery
http_codes_dir = os.path.join(src_dir, "libs", "http_codes")
libs_http_codes_pkg = types.ModuleType("libs.http_codes")
libs_http_codes_pkg.__path__ = [http_codes_dir]
sys.modules["libs.http_codes"] = libs_http_codes_pkg


@pytest.fixture(autouse=True)
def noop_fixture():
    """A no-op autouse fixture kept for symmetry with earlier implementations.

    This fixture is automatically used by all tests in the http_codes test directory
    but performs no operations. It exists for consistency and potential future
    setup/teardown needs.
    """
    yield
