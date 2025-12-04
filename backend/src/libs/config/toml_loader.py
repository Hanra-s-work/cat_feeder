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
# FILE: toml_loader.py
# CREATION DATE: 04-12-2025
# LAST Modified: 8:6:18 04-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Centralized configuration management with intelligent path discovery
# // AR
# +==== END CatFeeder =================+
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from display_tty import Disp, initialise_logger

if sys.version_info >= (3, 11):
    try:
        import tomllib as tomli
    except ImportError as e:
        raise ImportError(
            "Python 3.11+ should have tomllib in stdlib. Something is wrong with your Python installation."
        ) from e
else:
    try:
        import tomli
    except ImportError as e:
        raise ImportError(
            "No TOML library found. Install tomli for Python < 3.11: pip install tomli"
        ) from e


class TOMLLoader:
    """
    Singleton configuration loader with smart path resolution.

    Loads config.toml files once and caches them for application lifecycle.
    Supports dynamic path discovery and multiple configuration sources.
    """

    _instance: Optional['TOMLLoader'] = None
    _initialized: bool = False

    debug: bool = False
    disp: Disp = initialise_logger(__qualname__, False)

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, debug: Optional[bool] = None) -> None:
        """Initialize the TOMLLoader singleton."""
        # ------------------------ Only initialize once ------------------------
        if TOMLLoader._initialized:
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

        # ------------------ Cache for loaded configurations  ------------------
        self._config_toml: Optional[Dict[str, Any]] = None
        self._project_root: Optional[Path] = None

        # ------------------- Mark the class as initialised  -------------------
        TOMLLoader._initialized = True
        # ------------------ Confirm initialisation complete  ------------------
        self.disp.log_info("Initialised")

    def _find_project_root(self) -> Path:
        """Find project root by looking for marker files/directories."""
        if self._project_root is not None:
            return self._project_root

        current = Path(__file__).resolve().parent
        cwd = Path.cwd().resolve()
        search_paths = [cwd, current]

        markers = [
            'docker-compose.yaml',
            'requirements.txt',
            'backend',
            '.git',
            'config.toml',
            '.env'
        ]

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

    def _search_directory_for_file(self, directory: Path, filename: str, current_depth: int, max_depth: int) -> Optional[Path]:
        """
        Recursively search directory for file up to max_depth.

        Args:
            directory: Directory to search in
            filename: Name of file to find
            current_depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            Path to found file or None if not found
        """
        if current_depth > max_depth:
            return None

        target = directory / filename
        if target.exists() and target.is_file():
            return target

        if current_depth < max_depth:
            try:
                for subdir in directory.iterdir():
                    if subdir.is_dir() and not subdir.name.startswith('.'):
                        result = self._search_directory_for_file(
                            subdir, filename, current_depth + 1, max_depth)
                        if result:
                            return result
            except PermissionError:
                pass

        return None

    def _find_file(self, filename: str, max_depth: int = 3) -> Optional[Path]:
        """
        Find a file by searching dynamically in directory tree.

        Args:
            filename: Name of file to find
            max_depth: Maximum directory levels to search (default: 3)

        Returns:
            Path to found file or None if not found
        """
        root = self._find_project_root()
        return self._search_directory_for_file(root, filename, 0, max_depth)

    def load_toml(self, force_reload: bool = False, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load config.toml file and return as dictionary.

        Args:
            force_reload: Force reload even if cached (default: False)
            custom_path: Custom path to config file (default: None)

        Returns:
            Dictionary containing parsed TOML configuration

        Raises:
            FileNotFoundError: If config.toml not found
            OSError: If file cannot be read
            IOError: If file read operation fails
        """
        if self._config_toml is not None and not force_reload:
            return self._config_toml

        config_path = None

        if custom_path:
            config_path = Path(custom_path)
        else:
            if '--config' in sys.argv:
                try:
                    idx = sys.argv.index('--config')
                    if idx + 1 < len(sys.argv):
                        config_path = Path(sys.argv[idx + 1])
                except (ValueError, IndexError):
                    pass

            if config_path is None:
                env_config = os.environ.get('CONFIG_FILE')
                if env_config:
                    config_path = Path(env_config)

            if config_path is None:
                config_path = self._find_file('config.toml')

        if config_path is None or not config_path.exists():
            error_message = f"config.toml not found in {os.getcwd()}"
            self.disp.log_critical(error_message)
            raise FileNotFoundError(
                "config.toml not found. Searched in project root and subdirectories. "
                "Set CONFIG_FILE environment variable or pass custom_path to specify location."
            )

        try:
            with open(config_path, 'rb') as f:
                self._config_toml = tomli.load(f)
        except (OSError, IOError) as e:
            self.disp.log_warning(f"{e}", "load_config_toml")
            raise

        return self._config_toml

    def load_config_toml(self, force_reload: bool = False, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Alias function for the load_toml function.
        Load config.toml file and return as dictionary.

        Args:
            force_reload: Force reload even if cached (default: False)
            custom_path: Custom path to config file (default: None)

        Returns:
            Dictionary containing parsed TOML configuration

        Raises:
            FileNotFoundError: If config.toml not found
            OSError: If file cannot be read
            IOError: If file read operation fails
        """
        return self.load_toml(force_reload, custom_path)

    def get_toml_value(self, *keys: str, default: Any = None) -> Any:
        """
        Get a value from config.toml using nested keys.

        Args:
            *keys: Nested keys to traverse (e.g., 'database', 'host')
            default: Default value if key not found (default: None)

        Returns:
            Value at specified key path or default if not found
        """
        config = self.load_config_toml()

        result = config
        for key in keys:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return default

        return result

    def get_config_value(self, *keys: str, default: Any = None) -> Any:
        """
        Alias function of get_toml_value
        Get a value from config.toml using nested keys.

        Args:
            *keys: Nested keys to traverse (e.g., 'database', 'host')
            default: Default value if key not found (default: None)

        Returns:
            Value at specified key path or default if not found
        """
        return self.get_config_value(*keys, default)

    def clear_cache(self) -> None:
        """Clear cached configuration."""
        self._config_toml = None
        self._project_root = None

    def get_project_root(self) -> Path:
        """Get the project root directory."""
        return self._find_project_root()

    def _ensure_loaded(self) -> None:
        """Make sure tha the internal toml file is loaded and ready to be used

        Raises:
            RuntimeError: If the internal toml configuration could not be loaded.
        """
        error_message: str = "No toml configuration loaded"
        if not self._config_toml:
            try:
                self.load_toml()
            except (FileNotFoundError, OSError, IOError) as e:
                self.disp.log_error(error_message)
                raise RuntimeError(error_message) from e
            if not self._config_toml:
                self.disp.log_error(error_message)
                raise RuntimeError(error_message)

    def get_toml_variable(self, section: str, key: str, default=None, *, toml_conf: Optional[Dict[str, Optional[str]]] = None) -> Any:
        """
        Get the value of a configuration variable from the TOML file.

        Args:
            section (str): The section of the TOML file to search in.
            key (str): The key within the section to fetch.
            default: The default value to return if the key is not found. Defaults to None.
            toml_conf (dict, optional): The loaded TOML configuration as a dictionary. Defaults to None.

        Returns:
            str: The value of the configuration variable, or the default value if the key is not found.

        Raises:
            KeyError: If the section is not found in the TOML configuration.
            RuntimeError: If the internally determined toml file has not been loaded and not alternate configuration is specified.
        """
        if not toml_conf:
            self._ensure_loaded()
            current_section = self._config_toml
        else:
            current_section = toml_conf
        try:
            keys = section.split('.')

            for k in keys:
                if k in current_section:
                    current_section = current_section[k]
                else:
                    error_message: str = f"Section '{section}' not found in TOML configuration."
                    self.disp.log_error(error_message)
                    raise KeyError(error_message)

            if key in current_section:
                msg = f"current_section[{key}] = {current_section[key]} : "
                msg += f"{type(current_section[key])}"
                self.disp.log_debug(msg)
                if current_section[key] == "none":
                    self.disp.log_debug(
                        "The value none has been converted to None."
                    )
                    return None
                return current_section[key]
            if default is None:
                msg = f"Key '{key}' not found in section '{section}' "
                msg += "of TOML configuration."
                self.disp.log_error(msg)
                raise KeyError(msg)
            return default

        except KeyError as e:
            self.disp.log_warning(f"{e}")
            return default


def load_config() -> Dict[str, Any]:
    """
    Load config.toml (cached).

    Returns:
        Dictionary containing parsed TOML configuration

    Raises:
        FileNotFoundError: If config.toml not found
    """
    loader = TOMLLoader()
    return loader.load_config_toml()


def get_config(*keys: str, default: Any = None) -> Any:
    """
    Get config.toml value using nested keys.

    Args:
        *keys: Nested keys to traverse (e.g., 'database', 'host')
        default: Default value if key not found (default: None)

    Returns:
        Value at specified key path or default if not found
    """
    loader = TOMLLoader()
    return loader.get_config_value(*keys, default=default)


def get_project_root() -> Path:
    """Get the project root directory."""
    loader = TOMLLoader()
    return loader.get_project_root()
