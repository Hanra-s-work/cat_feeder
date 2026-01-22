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
# FILE: downloader.py
# CREATION DATE: 16-01-2026
# LAST Modified: 23:55:24 16-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The code in charge of downloading the tyni tex binaries and exposing them to the PATH.
# // AR
# +==== END CatFeeder =================+
"""
import os
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, Tuple, Optional, Union

import hashlib
import requests
from display_tty import Disp, initialise_logger

from ..core import FinalClass
from ..utils import CONST

DOWNLOAD_PATH: Union[str, Path] = CONST.ASSETS_DIRECTORY / "tinytex"


class TinyTeXInstaller(metaclass=FinalClass):
    """
    Downloads and installs TinyTeX locally in the current directory.
    Handles cross-platform archive selection, SHA256 verification,
    extraction, and exposes the bin folder to Python via PATH.

    Usage:
        installer = TinyTeXInstaller(flavour="TinyTeX-1")
        bin_path = installer.install()
    """

    disp: Disp = initialise_logger(__qualname__, CONST.DEBUG)

    _instance: Optional["TinyTeXInstaller"] = None

    # Predefined URLs + SHA256 hashes for each OS and scheme
    RELEASES: Dict[str, Dict[str, Tuple[str, str]]] = {
        "windows": {
            "TinyTeX-0": (
                "https://github.com/rstudio/tinytex-releases/releases/download/v2026.01/TinyTeX-0-v2026.01.zip",
                "2ecc48c2e25387b4736f63fdcbe7fddeb8027e8da3bcbf4f3149e3affe926722"
            ),
            "TinyTeX-1": (
                "https://github.com/rstudio/tinytex-releases/releases/download/v2026.01/TinyTeX-1-v2026.01.zip",
                "807d2600e9bf7171a3785416ad2e9d2cf18aeabc6cb56f533ad43d2819d37b8d"
            )
        },
        "linux": {
            "TinyTeX-0": (
                "https://github.com/rstudio/tinytex-releases/releases/download/v2026.01/TinyTeX-0-v2026.01.tar.gz",
                "5b1cc012e4c033ef7748023d67ae6709b1db65b738edd2c69e82bedf297ba4cd"
            ),
            "TinyTeX-1": (
                "https://github.com/rstudio/tinytex-releases/releases/download/v2026.01/TinyTeX-1-v2026.01.tar.gz",
                "91c7e636c900d70f3731149c1b54ede26a5c10212b0bd1b7694c1b0d898ec37a"
            ),
        },
        "darwin": {  # macOS
            "TinyTeX-0": (
                "https://github.com/rstudio/tinytex-releases/releases/download/v2026.01/TinyTeX-0-v2026.01.tgz",
                "638a817a448f896b81de8219896a20c306fd484067136f3febdf12c03bb49605"
            ),
            "TinyTeX-1": (
                "https://github.com/rstudio/tinytex-releases/releases/download/v2026.01/TinyTeX-1-v2026.01.tgz",
                "1eec5125d45b73c3112399afa7c2c3595803b17c762bfd97180c86656d183706"
            ),
        },
    }

    def __new__(cls, *args, **kwargs) -> "TinyTeXInstaller":
        if cls._instance is None:
            cls._instance = super(TinyTeXInstaller, cls).__new__(cls)
        return cls._instance

    def __init__(self, flavour: str = "TinyTeX-1", install_dir_name: Union[str, Path] = DOWNLOAD_PATH, *, timeout_seconds: int = 300) -> None:
        self.disp.log_debug("Initialising...")
        self.flavour: str = flavour
        self.install_dir_name: Union[str, Path] = install_dir_name
        self.os_key: str = self.detect_os()
        self.timeout: int = timeout_seconds

        if self.flavour not in self.RELEASES[self.os_key]:
            raise ValueError(
                f"flavour '{flavour}' not available for OS '{self.os_key}'"
            )

        self.url, self.sha256 = self.RELEASES[self.os_key][self.flavour]
        self.disp.log_debug("Initialised.")

    def __call__(self) -> str:
        return self.install()

    @staticmethod
    def detect_os() -> str:
        """Detect the current operating system."""
        if sys.platform.startswith("win"):
            return "windows"
        if sys.platform.startswith("linux"):
            return "linux"
        if sys.platform.startswith("darwin"):
            return "darwin"
        raise RuntimeError(f"Unsupported OS: {sys.platform}")

    def _download_file(self, url: str, dest_path: str) -> None:
        """Download a file from a URL to a local destination.

        Args:
            url (str): The URL to download from.
            dest_path (str): The local file path to save the downloaded file.
        """
        self.disp.log_info(f"Downloading {url} ...")
        with requests.get(url, stream=True, timeout=self.timeout) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        self.disp.log_info(f"Downloaded to {dest_path}")

    def _verify_sha256(self, file_path: str, expected_hash: str) -> None:
        """Verify the SHA256 hash of a file.

        Args:
            file_path (str): Path to the file to verify.
            expected_hash (str): Expected SHA256 hash string.

        Raises:
            ValueError: If the hash does not match.
        """
        self.disp.log_info(f"Verifying SHA256 for {file_path} ...")
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        actual_hash = h.hexdigest()
        if actual_hash != expected_hash:
            self.disp.log_error(
                f"SHA256 mismatch: {actual_hash} != {expected_hash}"
            )
            raise ValueError(
                f"SHA256 mismatch: {actual_hash} != {expected_hash}"
            )
        self.disp.log_info("SHA256 verified")

    def _extract_archive(self, archive_path: str, dest_dir: str) -> None:
        self.disp.log_info(f"Extracting {archive_path} → {dest_dir}")
        if archive_path.endswith(".zip"):
            self.disp.log_debug("Detected ZIP archive.")
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(dest_dir)
        elif archive_path.endswith((".tar.gz", ".tgz")):
            self.disp.log_debug("Detected TAR.GZ archive.")
            with tarfile.open(archive_path, "r:gz") as tf:
                tf.extractall(dest_dir)
        else:
            self.disp.log_error("Unknown archive format.")
            raise ValueError(f"Unknown archive format: {archive_path}")

    def install(self) -> str:
        """Install TinyTeX locally and expose its bin folder. Returns the bin path."""
        self.disp.log_info("Starting TinyTeX installation...")
        cwd = os.getcwd()
        install_dir = os.path.join(cwd, self.install_dir_name)
        self.disp.log_debug(f"Installation directory: {install_dir}")
        os.makedirs(install_dir, exist_ok=True)

        archive_path = os.path.join(install_dir, os.path.basename(self.url))
        self.disp.log_debug(f"Archive path: {archive_path}")

        if not os.path.exists(archive_path):
            self.disp.log_info(
                f"{archive_path} does not exist, downloading...")
            self._download_file(self.url, archive_path)
            self.disp.log_debug("Download complete, verifying...")
            self._verify_sha256(archive_path, self.sha256)
        else:
            self.disp.log_info(
                f"{archive_path} already exists, skipping download.")
            self._verify_sha256(archive_path, self.sha256)

        self._extract_archive(archive_path, install_dir)

        # Find bin folder
        bin_path: Optional[str] = None
        for root, dirs, _ in os.walk(install_dir):
            if "bin" in dirs:
                bin_path = os.path.join(root, "bin")
                break
        self.disp.log_debug(f"Bin path: {bin_path}")

        if bin_path is None:
            raise RuntimeError(
                "Could not find TinyTeX 'bin' directory after extraction")

        # Expose path
        os.environ["PATH"] = f"{bin_path}{os.pathsep}{os.environ.get('PATH', '')}"
        sys.path.insert(0, bin_path)
        self.disp.log_info(f"TinyTeX bin available at: {bin_path}")

        return bin_path


# === USAGE EXAMPLE ===
if __name__ == "__main__":
    installer = TinyTeXInstaller(flavour="TinyTeX-1")
    bin_dir = installer.install()
    print("You can now run pdflatex, xelatex, lualatex from Python or Pandoc.")
