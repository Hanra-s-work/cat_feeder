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
# CREATION DATE: 11-10-2025
# LAST Modified: 20:58:55 22-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# 
# This file raises:
#     ArchitectureNotSupported: This means that the architecure you are running this file on is unknown to it.
#     PackageNotSupported: This class informs the user that the system architecture they are using is not supported by this script
#     PackageNotInstalled: This class informs the user that the ff dependency(ies) they required does not exist.
#     NotImplementedError: This class inform the user that a required operation is not implemented and thus not completable.
#     ValueError: This is used for any error that does not fit into any specific class.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of downloading and extracting the FFmpeg binaries for the current system.
# // AR
# +==== END CatFeeder =================+
"""
import os
import sys
import math
import struct
import shutil
import zipfile
import tarfile
import platform
from typing import Union, Callable
from pathlib import Path as PPath
from pydub import AudioSegment, playback
import requests
from .ff_exceptions import ArchitectureNotSupported, PackageNotInstalled, PackageNotSupported
from . import ff_constants as CONST
from ..core import FinalClass


class FFMPEGDownloader(metaclass=FinalClass):
    """
        The class in charge of downloading and extracting the FFmpeg binaries for the current system.
        This class is there so that ffmpeg (and it's familly binaries) ca be run without requiring the user to install it.

    Raises:
        ArchitectureNotSupported: This means that the architecure you are running this file on is unknown to it.
        PackageNotSupported: This class informs the user that the system architecture they are using is not supported by this script
        PackageNotInstalled: This class informs the user that the ff dependency(ies) they required does not exist.
        NotImplementedError: This class inform the user that a required operation is not implemented and thus not completable.
        ValueError: This is used for any error that does not fit into any specific class.
        RuntimeError: Any error that was unexpected and caused the program to stop.
    """

    available_binaries: list = [CONST.FFMPEG_KEY,
                                CONST.FFPROBE_KEY, CONST.FFPLAY_KEY]

    def __init__(self, cwd: str = os.getcwd(), query_timeout: int = 10, success: int = 0, error: int = 84, debug: bool = False):
        self.cwd: str = cwd
        self.error: int = error
        self.debug: bool = debug
        self.success: int = success
        self.file_url: Union[str, None] = None
        self.file_path: Union[str, None] = None
        self.fold_path: Union[str, None] = None
        self.query_timeout: int = query_timeout
        self.new_folder_path: Union[str, None] = None
        self.extracted_folder: Union[str, None] = None
        self.system: str = self.get_system_name()
        self.architecture: str = self.get_platform()
        self.available_binaries: list = FFMPEGDownloader.available_binaries

    @staticmethod
    def process_file_path(*args: Union[str, PPath], cwd: Union[str, PPath, None] = None) -> str:
        """_summary_
            This is a rebind function of the process_file_path defined globaly
        """
        return CONST.process_file_path(
            *args, cwd=cwd
        )

    @staticmethod
    def generate_audio_sample(tone: int) -> AudioSegment:
        """
        Generates a pure tone audio sample using the pydub library.

        Args:
            tone (int): Frequency of the tone in Hz.

        Returns:
            AudioSegment: The generated audio segment.
        """
        print(f"Generating audio sample for tone {tone} Hz")
        sample_rate = 44100  # Hz
        frequency = tone  # Hz
        duration = 3.0  # seconds

        # Generate samples manually
        num_samples = int(sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / sample_rate
            # Generate a sine wave
            sample_value = 0.5 * math.sin(2 * math.pi * frequency * t)
            # Convert to 16-bit integer
            waveform_integer = int(sample_value * 32767)
            samples.append(waveform_integer)

        # Pack the waveform integers into a byte array
        raw_audio_data = struct.pack("<" + "h" * len(samples), *samples)

        # Create the AudioSegment
        audio_segment = AudioSegment(
            raw_audio_data,
            frame_rate=sample_rate,
            sample_width=2,  # 16-bit audio is 2 bytes
            channels=1  # Mono audio
        )
        print("Audio sample generated")
        return audio_segment

    @staticmethod
    def play_audio_sample(audio_segment: AudioSegment) -> None:
        """
        Plays an audio sample using the pydub library.

        Args:
            audio_segment (AudioSegment): The audio segment to play.
        """
        print("Playing audio sample")
        playback.play(audio_segment)
        print("Audio sample played")

    @staticmethod
    def save_audio_sample(audio_segment: AudioSegment, file_path: str) -> None:
        """
            Saves an audio sample to a file using the pydub library.

        Args:
            audio_segment (AudioSegment): _description_
            file_path (str): _description_

        Returns:
            _type_: _description_
        """
        print(f"Saving audio sample to {file_path}")
        audio_segment.export(file_path, format="wav")
        print(f"Audio sample saved to {file_path}")

    @staticmethod
    def _extract_package(file_path: str, destination: str) -> None:
        """_summary_

        Args:
            file_path (_type_): _description_
            destination (_type_): _description_

        Raises:
            NotImplementedError: _description_
            ValueError: _description_
        """
        print(f"Extracting {file_path} to {destination}")
        if file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(destination)
        elif file_path.endswith(".tar.xz"):
            with tarfile.open(file_path, 'r:xz') as tar_ref:
                tar_ref.extractall(destination)
        elif file_path.endswith(".7z"):
            # Handling 7z files
            raise NotImplementedError("7z extraction not implemented")
        else:
            raise ValueError("Unsupported file format")
        print("Extraction complete")

    @staticmethod
    def get_system_name() -> str:
        """_summary_

        Raises:
            ArchitectureNotSupported: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_

        Returns:
            str: _description_
        """
        return platform.system().lower()

    @staticmethod
    def get_platform() -> str:
        """_summary_

        Raises:
            NotImplementedError: _description_
            ValueError: _description_

        Returns:
            str: _description_
        """
        return platform.architecture()[0]

    @staticmethod
    def _create_path_if_not_exists(path: str) -> None:
        """_summary_

        Args:
            path (_type_): _description_

        Raises:
            NotImplementedError: _description_
            ValueError: _description_
        """
        if not os.path.exists(path):
            print(f"Creating directory: {path}")
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def _download_file(file_url: str, file_path: str, query_timeout: int = 10) -> None:
        """_summary_

        Args:
            file_url (_type_): _description_
            file_path (_type_): _description_

        Raises:
            PackageNotInstalled: _description_
        """
        print(f"Downloading FFmpeg from {file_url}")
        response_data = requests.get(file_url, timeout=query_timeout)
        if response_data.status_code != 200:
            raise PackageNotInstalled("Could not download the package")
        print(f"Saving to {file_path}")
        with open(file_path, "wb") as file_descriptor:
            file_descriptor.write(response_data.content)
        print("Download complete")

    @staticmethod
    def _grant_executable_rights(file_path: Union[str, None] = None) -> None:
        """_summary_

        Args:
            file_path (str, optional): _description_. Defaults to None.
        """
        if file_path is None:
            return
        print(f"Giving executable rights to {file_path}")
        if os.path.exists(file_path):
            os.chmod(file_path, 0o755)
            print(f"Executable rights granted to {file_path}")
        else:
            print(f"{file_path} does not exist, could not grant executable rights")

    @staticmethod
    def _rename_extracted_folder(old_name: str, new_name: str) -> None:
        """_summary_

        Args:
            old_name (str): _description_
            new_name (str): _description_
        """

        if os.path.exists(old_name):
            print(f"Renaming {old_name} to {new_name}")
            shutil.move(old_name, new_name)

    @staticmethod
    def get_ff_family_path(download_if_not_present: bool = True, cwd: str = os.getcwd(), query_timeout: int = 10,  success: int = 0, error: int = 1, debug: bool = False) -> str:
        """_summary_
            The general path for ff related libraries

        Args:
            download_if_not_present (bool, optional): _description_. Defaults to True.
            cwd (str, optional): _description_. Defaults to os.getcwd().
            query_timeout (int, optional): _description_. Defaults to 10.
            success (int, optional): _description_. Defaults to 0.
            error (int, optional): _description_. Defaults to 1.
            debug (bool, optional): _description_. Defaults to False.

        Raises:
            PackageNotSupported: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_
            ArchitectureNotSupported: _description_
            PackageNotSupported: _description_
            RuntimeError: _description_

        Returns:
            str: _description_
        """
        system = FFMPEGDownloader.get_system_name()
        if system not in ("windows", "linux", "darwin"):
            raise PackageNotSupported("Unsupported system")
        precompiled_ffmpeg = os.path.join(cwd, "ffmpeg", system)
        precompiled_ffprobe = os.path.join(cwd, "ffprobe", system)
        precompiled_ffplay = os.path.join(cwd, "ffplay", system)
        if not os.path.isdir(precompiled_ffmpeg) or not os.path.isdir(precompiled_ffprobe) or not os.path.isdir(precompiled_ffplay):
            if not download_if_not_present:
                raise PackageNotInstalled("FF_family not found")
            print("FF_family not found in precompiled paths, setting up")
            fdi = FFMPEGDownloader(
                cwd=cwd,
                query_timeout=query_timeout,
                success=success,
                error=error,
                debug=debug
            )
            status = fdi.main()
            if status != 0:
                raise RuntimeError("FF_family could not be installed")
        if os.path.exists(cwd) and os.path.isdir(cwd):
            return cwd
        raise PackageNotInstalled("FF_family not found")

    @staticmethod
    def get_ffmpeg_binary_path(download_if_not_present: bool = True, cwd: str = os.getcwd(), query_timeout: int = 10,  success: int = 0, error: int = 1, debug: bool = False) -> str:
        """_summary_

        Args:
            download_if_not_present (bool, optional): _description_. Defaults to True.
            cwd (str, optional): _description_. Defaults to os.getcwd().
            query_timeout (int, optional): _description_. Defaults to 10.
            success (int, optional): _description_. Defaults to 0.
            error (int, optional): _description_. Defaults to 1.
            debug (bool, optional): _description_. Defaults to False.

        Raises:
            PackageNotSupported: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_

        Returns:
            str: _description_
        """
        system = FFMPEGDownloader.get_system_name()
        ffmpeg_system_path = FFMPEGDownloader.get_ff_family_path(
            download_if_not_present=download_if_not_present,
            cwd=cwd,
            query_timeout=query_timeout,
            success=success,
            error=error,
            debug=debug
        )
        ffmpeg_precompiled_path = os.path.join(
            ffmpeg_system_path, "ffmpeg", system
        )
        path = None
        if system == "windows":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffmpeg.exe"
            )
        elif system == "linux":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffmpeg"
            )
            FFMPEGDownloader._grant_executable_rights(path)
        elif system == "darwin":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffmpeg"
            )
            FFMPEGDownloader._grant_executable_rights(path)
        else:
            raise PackageNotSupported("Unsupported OS")
        print(f"FFmpeg path = '{path}'")
        if os.path.exists(path):
            if os.path.isfile(path):
                return path
            raise PackageNotSupported("Path is not a file")
        raise PackageNotInstalled("ffmpeg is not properly installed")

    @staticmethod
    def get_ffplay_binary_path(download_if_not_present: bool = True, cwd: str = os.getcwd(), query_timeout: int = 10,  success: int = 0, error: int = 1, debug: bool = False) -> str:
        """_summary_

        Args:
            download_if_not_present (bool, optional): _description_. Defaults to True.
            cwd (str, optional): _description_. Defaults to os.getcwd().
            query_timeout (int, optional): _description_. Defaults to 10.
            success (int, optional): _description_. Defaults to 0.
            error (int, optional): _description_. Defaults to 1.
            debug (bool, optional): _description_. Defaults to False.

        Raises:
            PackageNotSupported: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_

        Returns:
            str: _description_
        """
        system = FFMPEGDownloader.get_system_name()
        ffmpeg_system_path = FFMPEGDownloader.get_ff_family_path(
            download_if_not_present=download_if_not_present,
            cwd=cwd,
            query_timeout=query_timeout,
            success=success,
            error=error,
            debug=debug
        )
        ffmpeg_precompiled_path = os.path.join(
            ffmpeg_system_path, "ffplay", system
        )
        path = None
        if system == "windows":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffplay.exe"
            )
        elif system == "linux":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffplay"
            )
            FFMPEGDownloader._grant_executable_rights(path)
        elif system == "darwin":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffplay"
            )
            FFMPEGDownloader._grant_executable_rights(path)
        else:
            raise PackageNotSupported("Unsupported OS")
        print(f"FFplay path = '{path}'")
        if os.path.exists(path):
            if os.path.isfile(path):
                return path
            raise PackageNotSupported("Path is not a file")
        raise PackageNotInstalled("ffplay is not properly installed")

    @staticmethod
    def get_ffprobe_binary_path(download_if_not_present: bool = True, cwd: str = os.getcwd(), query_timeout: int = 10,  success: int = 0, error: int = 1, debug: bool = False) -> str:
        """_summary_

        Args:
            download_if_not_present (bool, optional): _description_. Defaults to True.
            cwd (str, optional): _description_. Defaults to os.getcwd().
            query_timeout (int, optional): _description_. Defaults to 10.
            success (int, optional): _description_. Defaults to 0.
            error (int, optional): _description_. Defaults to 1.
            debug (bool, optional): _description_. Defaults to False.

        Raises:
            PackageNotSupported: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_

        Returns:
            str: _description_
        """
        system = FFMPEGDownloader.get_system_name()
        ffmpeg_system_path = FFMPEGDownloader.get_ff_family_path(
            download_if_not_present=download_if_not_present,
            cwd=cwd,
            query_timeout=query_timeout,
            success=success,
            error=error,
            debug=debug
        )
        ffmpeg_precompiled_path = os.path.join(
            ffmpeg_system_path, "ffprobe", system
        )
        path = None
        if system == "windows":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffprobe.exe"
            )
        elif system == "linux":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffprobe"
            )
            FFMPEGDownloader._grant_executable_rights(path)
        elif system == "darwin":
            path = os.path.join(
                ffmpeg_precompiled_path,
                "ffprobe"
            )
            FFMPEGDownloader._grant_executable_rights(path)
        else:
            raise PackageNotSupported("Unsupported OS")
        print(f"FFprobe path = '{path}'")
        if os.path.exists(path):
            if os.path.isfile(path):
                return path
            raise PackageNotSupported("Path is not a file")
        raise PackageNotInstalled("ffprobe is not properly installed")

    @staticmethod
    def add_ff_family_to_path(ffmpeg_path: Union[str, None] = None, ffplay_path: Union[str, None] = None, ffprobe_path: Union[str, None] = None, download_if_not_present: bool = True, cwd: str = os.getcwd(), query_timeout: int = 10,  success: int = 0, error: int = 1, debug: bool = False) -> None:
        """_summary_
            Add the FF family to the system path.

        Args:
            ffmpeg_path (str, optional): _description_. Defaults to None.
            ffplay_path (str, optional): _description_. Defaults to None.
            ffprobe_path (str, optional): _description_. Defaults to None.
            download_if_not_present (bool, optional): _description_. Defaults to True.
            cwd (str, optional): _description_. Defaults to os.getcwd().
            query_timeout (int, optional): _description_. Defaults to 10.
            success (int, optional): _description_. Defaults to 0.
            error (int, optional): _description_. Defaults to 1.
            debug (bool, optional): _description_. Defaults to False.
        """
        if ffmpeg_path is None:
            try:
                print("Getting ffmpeg path")
                ffmpeg_path = FFMPEGDownloader.get_ffmpeg_binary_path(
                    download_if_not_present=download_if_not_present,
                    cwd=cwd,
                    query_timeout=query_timeout,
                    success=success,
                    error=error,
                    debug=debug
                )
            except (PackageNotSupported, PackageNotSupported, PackageNotInstalled) as e:
                print(f"Failed to expose ffmpeg, error: {e}")
        if ffplay_path is None:
            try:
                print("Getting ffplay path")
                ffplay_path = FFMPEGDownloader.get_ffplay_binary_path(
                    download_if_not_present=download_if_not_present,
                    cwd=cwd,
                    query_timeout=query_timeout,
                    success=success,
                    error=error,
                    debug=debug
                )
            except (PackageNotSupported, PackageNotSupported, PackageNotInstalled) as e:
                print(f"Failed to expose ffplay, error: {e}")
        if ffprobe_path is None:
            try:
                print("Getting ffprobe path")
                ffprobe_path = FFMPEGDownloader.get_ffprobe_binary_path(
                    download_if_not_present=download_if_not_present,
                    cwd=cwd,
                    query_timeout=query_timeout,
                    success=success,
                    error=error,
                    debug=debug
                )
            except (PackageNotSupported, PackageNotSupported, PackageNotInstalled) as e:
                print(f"Failed to expose ffprobe, error: {e}")
        msg = "Converting the direct paths (which include the binaries at the end) into system paths (which only include the directories containing the binaries)"
        print(msg)
        if ffmpeg_path:
            ffmpeg_path = os.path.abspath(os.path.dirname(ffmpeg_path))
        if ffplay_path:
            ffplay_path = os.path.abspath(os.path.dirname(ffplay_path))
        if ffprobe_path:
            ffprobe_path = os.path.abspath(os.path.dirname(ffprobe_path))
        print("Adding FF family to PATH")
        for ff_path in [ffmpeg_path, ffplay_path, ffprobe_path]:
            if not ff_path:
                print("Path not defined, skipping")
                continue
            if ff_path not in os.environ["PATH"]:
                print(f"Adding {ff_path} to PATH")
                os.environ["PATH"] = ff_path + os.pathsep + os.environ["PATH"]
                print(f"Added {ff_path} to PATH")
            else:
                print(f"{ff_path} is already in PATH")
            if ff_path not in sys.path:
                print(f"Adding {ff_path} to sys.path")
                sys.path.append(ff_path)
                print(f"Added {ff_path} to sys.path")
            else:
                print(f"{ff_path} is already in sys.path")

    def _clean_platform_name(self) -> None:
        """_summary_

        Raises:
            NotImplementedError: _description_
            ValueError: _description_
        """
        msg = "Current system (before filtering): "
        msg += f"{self.system} {self.architecture}"
        print(msg)

        if "bit" in self.architecture:
            self.architecture = self.architecture.replace("bit", "")
        elif "x" in self.architecture:
            self.architecture = self.architecture.replace("x", "")

        msg = "Current system (after filtering): "
        msg += f"{self.system} {self.architecture}"
        print(msg)

    def _get_correct_download_and_file_path(self, binary_name: str = CONST.FFMPEG_KEY) -> None:
        """_summary_

        Args:
            binary_name (str, optional): _description_. Defaults to FFMPEG_KEY.

        Raises:
            ArchitectureNotSupported: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_
        """
        if binary_name not in CONST.BUNDLE_DOWNLOAD:
            raise PackageNotSupported("Unknown binary choice" + binary_name)
        if self.system in CONST.BUNDLE_DOWNLOAD[binary_name]:
            if self.architecture in CONST.BUNDLE_DOWNLOAD[binary_name][self.system]:
                tmp_path: Union[str, Callable] = CONST.BUNDLE_DOWNLOAD[binary_name][
                    self.system][self.architecture][CONST.FILE_PATH_TOKEN]
                if callable(tmp_path):
                    self.file_path = str(tmp_path(cwd=self.cwd))
                else:
                    self.file_path = tmp_path
                self.file_url = CONST.BUNDLE_DOWNLOAD[binary_name][
                    self.system
                ][self.architecture][CONST.FILE_URL_TOKEN]
            else:
                raise ArchitectureNotSupported("Unknown architecture")
        else:
            raise PackageNotSupported("Unknown system")

    def _get_all_binaries(self) -> None:
        """_summary_

        Raises:
            PackageNotSupported: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_
        """
        for binary in self.available_binaries:
            print(f"Downloading {binary}")
            self._get_correct_download_and_file_path(binary)
            if self.file_path:
                self.fold_path = os.path.dirname(self.file_path)
            else:
                self.fold_path = os.path.dirname(__file__)
            self._create_path_if_not_exists(self.fold_path)
            if self.file_path and os.path.exists(self.file_path):
                print(f"{binary} already downloaded")
                continue
            if not self.file_url or not self.file_path:
                print(f"{binary} contains corrupted data, skipping")
                continue
            self._download_file(
                self.file_url,
                self.file_path,
                self.query_timeout
            )

    def _install_all_binaries(self) -> None:
        """_summary_
            This is the function that will install all the FF_family binaries if they are already downloaded.
        """
        for binary in self.available_binaries:
            print(f"Installing {binary}")
            self._get_correct_download_and_file_path(binary)
            if not self.file_path:
                print(
                    f"{binary} filepath is empty, the binary meta data appears to be corrupted, skipping")
                continue
            self.fold_path = os.path.dirname(self.file_path)
            extract_to = os.path.join(
                self.cwd,
                binary
            )
            final_name = os.path.join(
                extract_to,
                self.system
            )
            if os.path.isdir(final_name):
                print(f"{binary} already installed")
                continue
            if binary == CONST.FFPLAY_KEY:
                extract_to = os.path.join(
                    extract_to,
                    self.system
                )
            self._create_path_if_not_exists(extract_to)
            self._extract_package(self.file_path, extract_to)
            self.extracted_folder = os.listdir(extract_to)[0]
            new_folder_path = os.path.join(
                self.cwd,
                binary,
                self.system
            )
            old_folder_path = os.path.join(
                extract_to,
                self.extracted_folder
            )
            if binary != CONST.FFPLAY_KEY:
                self._rename_extracted_folder(
                    old_folder_path,
                    new_folder_path
                )
            print(f"{binary} installed")

    def main(self, audio_segment_node: Union[AudioSegment, None] = None) -> int:
        """_summary_
            The function in charge of downloading and extracting the FF_family binaries for the current system.

        Raises:
            PackageNotInstalled: _description_
            PackageNotSupported: _description_
            PackageNotInstalled: _description_

        Returns:
            int: _description_
        """
        try:
            found_path = self.get_ff_family_path(download_if_not_present=False)
            print(f"FF_family already installed at {found_path}")
            ffmpeg_path = self.get_ffmpeg_binary_path(
                download_if_not_present=False,
                cwd=self.cwd,
                query_timeout=self.query_timeout,
                success=self.success,
                error=self.error,
                debug=self.debug
            )
            ffplay_path = self.get_ffplay_binary_path(
                download_if_not_present=False,
                cwd=self.cwd,
                query_timeout=self.query_timeout,
                success=self.success,
                error=self.error,
                debug=self.debug
            )
            ffprobe_path = self.get_ffprobe_binary_path(
                download_if_not_present=False,
                cwd=self.cwd,
                query_timeout=self.query_timeout,
                success=self.success,
                error=self.error,
                debug=self.debug
            )
            print("Updating pydub ffmpeg path")
            if audio_segment_node is not None:
                audio_segment_node.ffmpeg = ffmpeg_path
            AudioSegment.ffmpeg = ffmpeg_path
            self.add_ff_family_to_path(
                ffmpeg_path, ffplay_path, ffprobe_path, download_if_not_present=False
            )
            print("FF_family already installed and ready to use!")
            return self.success
        except PackageNotInstalled:
            print("FFmpeg not found. Installing...")
        except PackageNotSupported as e:
            raise RuntimeError(
                "FFmpeg cannot be installed on this device because the system is unknown to this script."
            ) from e
        self._clean_platform_name()
        self._get_all_binaries()
        self._install_all_binaries()
        ffmpeg_path = self.get_ffmpeg_binary_path(
            download_if_not_present=False,
            cwd=self.cwd,
            query_timeout=self.query_timeout,
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        ffplay_path = self.get_ffplay_binary_path(
            download_if_not_present=False,
            cwd=self.cwd,
            query_timeout=self.query_timeout,
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        ffprobe_path = self.get_ffprobe_binary_path(
            download_if_not_present=False,
            cwd=self.cwd,
            query_timeout=self.query_timeout,
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        print(f"FFmpeg installed at {ffmpeg_path}")
        print(f"FFplay installed at {ffplay_path}")
        print(f"FFprobe installed at {ffprobe_path}")
        if audio_segment_node is not None:
            audio_segment_node.ffmpeg = ffmpeg_path
        AudioSegment.ffmpeg = ffmpeg_path
        self.add_ff_family_to_path(
            ffmpeg_path, ffplay_path, ffprobe_path, download_if_not_present=False
        )
        print("FF_family installed and ready to use!")
        return self.success


if __name__ == "__main__":
    FDI = FFMPEGDownloader()
    FDI.main()
    AUDIO_WAVE = 440
    AUDIO_SAMPLE_PATH = f"./{AUDIO_WAVE}.wav"
    AUDIO_SAMPLE = FDI.generate_audio_sample(AUDIO_WAVE)
    FDI.save_audio_sample(AUDIO_SAMPLE, AUDIO_SAMPLE_PATH)
    FDI.play_audio_sample(AUDIO_SAMPLE)
