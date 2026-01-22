"""
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
# FILE: env_loader.py
# CREATION DATE: 04-12-2025
# LAST Modified: 21:52:55 14-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE:
# Centralized .env management with intelligent path discovery.
# Singleton environment variable loader with smart .env file discovery and caching.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict
from display_tty import Disp, initialise_logger


class EnvLoader:
    """
    Singleton .env file loader with smart path resolution.

    Loads .env files once and caches environment variables for application lifecycle.
    Supports dynamic path discovery and multiple configuration sources.
    """

    _instance: Optional['EnvLoader'] = None
    _initialized: bool = False

    debug: bool = False
    disp: Disp = initialise_logger(__qualname__, False)

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, debug: Optional[bool] = None) -> None:
        """Initialize the EnvLoader singleton."""
        # ------------------------ Only initialize once ------------------------
        if EnvLoader._initialized:
            self.disp.log_debug(
                "An instance already exists, returning early"
            )
            return

        # ------------------ Set the debug status if provided ------------------
        if isinstance(debug, bool):
            self.debug: bool = debug
        self.disp.update_disp_debug(self.debug)

        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(self.debug)
        self.disp.log_info("Initialising...")

        # --------------- Cache for loaded environment variables ---------------
        self._env_vars: Optional[Dict[str, str]] = None
        self._project_root: Optional[Path] = None

        # ------------------- Mark the class as initialised  -------------------
        EnvLoader._initialized = True

        # ------------- Actively load environment file at init -----------------
        try:
            self.load_env_file()
            self.disp.log_info("Environment file loaded successfully")
        except FileNotFoundError:
            self.disp.log_warning("No .env file found, using os.environ only")
            self._env_vars = dict(os.environ)
        except (OSError, IOError) as e:
            self.disp.log_warning(f"Could not load environment file: {e}")
            self._env_vars = dict(os.environ)

        # ------------------ Confirm initialisation complete  ------------------
        self.disp.log_info("Initialised")

    def _find_project_root(self) -> Path:
        """Find project root by looking for marker files/directories."""
        if self._project_root is not None:
            return self._project_root

        current = Path(__file__).resolve().parent
        self.disp.log_debug(f"current={current}")
        cwd = Path.cwd().resolve()
        self.disp.log_debug(f"cwd={cwd}")
        # Check cwd first since it's usually the project root
        search_paths = [cwd, current]
        self.disp.log_debug(f"search_paths={search_paths}")

        markers = [
            'docker-compose.yaml',
            'requirements.txt',
            'backend',
            '.git',
            'config.toml',
            '.env'
        ]
        self.disp.log_debug(f"markers={markers}")

        for start_path in search_paths:
            for level in range(5):  # Increased from 4 to 5 to handle libs/config depth
                check_path = start_path
                for _ in range(level):
                    check_path = check_path.parent

                for marker in markers:
                    marker_path = check_path / marker
                    if marker_path.exists():
                        self._project_root = check_path
                        return self._project_root

        self._project_root = cwd
        return self._project_root

    def _search_directory_for_env(self, directory: Path, current_depth: int, max_depth: int) -> Optional[Path]:
        """
        Recursively search directory for .env file up to max_depth.

        Args:
            directory: Directory to search in
            current_depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            Path to found .env file or None if not found
        """
        if current_depth > max_depth:
            return None

        self.disp.log_debug(
            f"Searching in {directory} at depth {current_depth}")
        for env_name in ['.env', 'tmp.env']:
            target = directory / env_name
            self.disp.log_debug(
                f"Checking {target}: exists={target.exists()}, is_file={target.is_file() if target.exists() else 'N/A'}")
            if target.exists() and target.is_file():
                self.disp.log_debug(f"Found env file: {target}")
                return target

        if current_depth < max_depth:
            try:
                for subdir in directory.iterdir():
                    if subdir.is_dir() and not subdir.name.startswith('.'):
                        result = self._search_directory_for_env(
                            subdir, current_depth + 1, max_depth)
                        if result:
                            return result
            except PermissionError:
                pass

        return None

    def _find_env_file(self, max_depth: int = 5) -> Optional[Path]:
        """
        Find .env file dynamically in directory tree.

        Args:
            max_depth: Maximum directory levels to search (default: 3)

        Returns:
            Path to found .env file or None if not found
        """
        root = self._find_project_root()
        self.disp.log_debug(f"Project root for env search: {root}")
        result = self._search_directory_for_env(root, 0, max_depth)
        self.disp.log_debug(f"Env search result: {result}")
        return result

    def update_debug(self, debug: bool) -> None:
        """
        Update debug status of the loader.

        Args:
            debug: New debug status
        """
        self.debug = debug
        self.disp.update_disp_debug(debug)
        self.disp.log_info(f"Debug mode set to {debug}")

    def load_env_file(self, force_reload: bool = False, merge_os_environ: bool = True, custom_path: Optional[str] = None) -> Dict[str, str]:
        """
        Load .env file and return as dictionary.

        Args:
            force_reload: Force reload even if cached (default: False)
            merge_os_environ: Merge with os.environ variables (default: True)
            custom_path: Custom path to .env file (default: None)

        Returns:
            Dictionary containing environment variables

        Raises:
            FileNotFoundError: If .env file not found
            OSError: If file cannot be read
            IOError: If file read operation fails
        """
        if self._env_vars is not None and not force_reload:
            return self._env_vars

        env_path = None

        if custom_path:
            env_path = Path(custom_path)
        else:
            if '--env' in sys.argv:
                try:
                    idx = sys.argv.index('--env')
                    if idx + 1 < len(sys.argv):
                        env_path = Path(sys.argv[idx + 1])
                except (ValueError, IndexError):
                    pass

            if env_path is None:
                env_env = os.environ.get('ENV_FILE')
                if env_env:
                    env_path = Path(env_env)

            if env_path is None:
                env_path = self._find_env_file()

        if env_path is None or not env_path.exists():
            error_message = f".env file not found in {env_path}"
            self.disp.log_critical(error_message)
            raise FileNotFoundError(
                ".env file not found. Searched in project root and subdirectories. "
                "Set ENV_FILE environment variable or pass custom_path to specify location."
            )

        if merge_os_environ:
            self._env_vars = dict(os.environ)
        else:
            self._env_vars = {}

        try:
            env_file_vars = self._parse_env_file(env_path)
            self._env_vars.update(env_file_vars)
        except (OSError, IOError) as e:
            self.disp.log_warning(f"{e}")
            raise

        return self._env_vars

    def _parse_env_file(self, env_path: Path) -> Dict[str, str]:
        """
        Parse .env file and return as dictionary.

        Args:
            env_path: Path to .env file

        Returns:
            Dictionary of key-value pairs from .env file
        """
        env_vars = {}

        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                if '=' not in line:
                    continue

                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()

                if len(value) >= 2:
                    if (
                        value.startswith('"') and value.endswith('"')
                    ) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        value = value[1:-1]

                env_vars[key] = value

        return env_vars

    def get_env_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a value from .env file.

        Args:
            key: Environment variable key
            default: Default value if key not found (default: None)

        Returns:
            Environment variable value or default if not found
        """
        env_vars = self.load_env_file()
        return env_vars.get(key, default)

    def apply_to_os_environ(self) -> None:
        """Apply loaded .env variables to os.environ."""
        env_vars = self.load_env_file(merge_os_environ=False)
        os.environ.update(env_vars)

    def clear_cache(self) -> None:
        """Clear cached environment variables."""
        self._env_vars = None
        self._project_root = None

    def get_project_root(self) -> Path:
        """Get the project root directory."""
        return self._find_project_root()

    def get_environment_variable(self, variable_name: str) -> str:
        """
        Get the content of an environment variable.

        Args:
            variable_name: Name of the environment variable to retrieve

        Returns:
            Value of the environment variable

        Raises:
            ValueError: If no environment file is loaded
            ValueError: If variable not found in environment
        """
        if self._env_vars is None:
            raise ValueError(
                "No environment file loaded."
            )
        data = self._env_vars.get(variable_name, None)
        if data is None:
            error_msg = f"Variable '{variable_name}' not found in the environment"
            raise ValueError(error_msg)
        return data


# Backwards compatibility - global ENV dictionary
EnvLoader.debug = True
_loader_instance = EnvLoader()
try:
    ENV = _loader_instance.load_env_file()
except FileNotFoundError:
    ENV = {}


def load_env(merge_os_environ: bool = True) -> Dict[str, str]:
    """
    Load .env file (cached).

    Args:
        merge_os_environ: Merge with os.environ variables (default: True)

    Returns:
        Dictionary containing environment variables

    Raises:
        FileNotFoundError: If .env file not found
    """
    loader = EnvLoader()
    return loader.load_env_file(merge_os_environ=merge_os_environ)


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get .env value.

    Args:
        key: Environment variable key
        default: Default value if key not found (default: None)

    Returns:
        Environment variable value or default if not found
    """
    loader = EnvLoader()
    return loader.get_env_value(key, default)


def apply_env() -> None:
    """Apply loaded .env variables to os.environ."""
    loader = EnvLoader()
    loader.apply_to_os_environ()


def get_environment_variable(variable_name: str) -> str:
    """
    Get the content of an environment variable (backwards compatibility).

    Args:
        variable_name: Name of the environment variable to retrieve

    Returns:
        Value of the environment variable

    Raises:
        ValueError: If no environment file is loaded
        ValueError: If variable not found in environment
    """
    loader = EnvLoader()
    return loader.get_environment_variable(variable_name)
