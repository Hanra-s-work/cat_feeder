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
# FILE: ff_constants.py
# CREATION DATE: 19-11-2025
# LAST Modified: 14:50:38 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The constants used by the ff download handler.
# // AR
# +==== END CatFeeder =================+
"""

import os
from typing import Union, Optional
from functools import partial
from pathlib import Path as PPath

#  Function to extract files based on archive type

FFMPEG_KEY = "ffmpeg"
FFPROBE_KEY = "ffprobe"
FFPLAY_KEY = "ffplay"

WINDOWS_KEY = "windows"
LINUX_KEY = "linux"
MAC_KEY = "darwin"

FILE_URL_TOKEN = "file_url"
FILE_PATH_TOKEN = "file_path"
QUERY_TIMEOUT = 10

CWD = os.getcwd()


def process_file_path(*args: Union[str, PPath], cwd: Optional[Union[str, PPath]] = None) -> str:
    """
    Convert a list of elements making up a path to a valid system-specific path.

    Args:
        *args: Path components to join.
        cwd: Optional base directory to prepend to the path.

    Returns:
        str: The compiled path.
    """
    if isinstance(cwd, str):
        path = PPath(cwd, *args)
    else:
        path = PPath(*args)
    return str(path)


BUNDLE_DOWNLOAD = {
    FFMPEG_KEY: {
        WINDOWS_KEY: {
            "i686": {
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.zip",  # 32-bit Windows
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "windows", "ffmpeg-release-i686-static.zip"
                )
            },
            "64": {
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-x86_64-static.zip",  # 64-bit Windows
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "windows", "ffmpeg-release-x86_64-static.zip"
                )
            }
        },
        LINUX_KEY: {
            "i686": {
                # 32-bit Linux (x86)
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffmpeg-release-i686-static.tar.xz"
                )
            },
            "64": {
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",  # 64-bit Linux
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffmpeg-release-x86_64-static.tar.xz"
                )
            },
            "arm64": {
                # 64-bit Linux (arm64)
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffprobe-release-arm64-static.tar.xz"
                )
            }
        },
        MAC_KEY: {
            "i686": {
                FILE_URL_TOKEN: "https://evermeet.cx/ffmpeg/get/zip",  # 32-bit macOS
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffmpeg-latest.zip"
                )
            },
            "64": {
                FILE_URL_TOKEN: "https://evermeet.cx/ffmpeg/get/zip",  # 64-bit macOS
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffmpeg-latest-amd64.zip"
                )
            },
            "arm64": {
                # 64-bit macOS (arm64),
                FILE_URL_TOKEN: "https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/release/ffmpeg.zip",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffmpeg-latest-arm64.zip"
                )
            }
        },
    },
    FFPROBE_KEY: {
        WINDOWS_KEY: {
            "i686": {
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.zip",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "windows", "ffprobe-release-i686-static.zip"
                )
            },
            "64": {
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-x86_64-static.zip",  # 64-bit Windows
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "windows", "ffprobe-release-x86_64-static.zip"
                )
            }
        },
        LINUX_KEY: {
            "i686": {
                # 32-bit Linux (x86)
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffprobe-release-i686-static.tar.xz"
                )
            },
            "64": {
                # 64-bit Linux
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffprobe_x64.tar.xz"
                )
            },
            "arm64": {
                # 64-bit Linux (arm 64)
                FILE_URL_TOKEN: "https://ffmpeg.martin-riedl.de/redirect/latest/linux/arm64/release/ffprobe.zip",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffprobe_arm64.zip"
                )
            },
        },
        MAC_KEY: {
            "i686": {
                FILE_URL_TOKEN: "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip",  # 32-bit macOS
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffprobe-latest.zip"
                )
            },
            "64": {
                FILE_URL_TOKEN: "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip",  # 64-bit macOS
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffprobe-latest-amd64.zip"
                )
            },
            "arm64": {
                # 64-bit macOS (arm64),
                FILE_URL_TOKEN: "https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/release/ffprobe.zip",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffprobe-latest-arm64.zip"
                )
            }
        },
    },
    FFPLAY_KEY: {
        WINDOWS_KEY: {
            "i686": {
                FILE_URL_TOKEN: "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n4.4-32bit-static.zip",  # 32-bit Windows
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "windows", "ffplay-release-i686-static.zip"
                )
            },
            "64": {
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-x86_64-static.zip",  # 64-bit Windows
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "windows", "ffplay-release-x86_64-static.zip"
                )
            }
        },
        LINUX_KEY: {
            "i686": {
                # 32-bit Linux (x86)
                FILE_URL_TOKEN: "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffplay-release-i686-static.tar.xz"
                )
            },
            "64": {
                FILE_URL_TOKEN: "https://ffmpeg.martin-riedl.de/redirect/latest/linux/amd64/release/ffplay.zip",  # 64-bit Linux
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffplay-latest-amd64.zip"
                )
            },
            "arm64": {
                FILE_URL_TOKEN: "https://ffmpeg.martin-riedl.de/redirect/latest/linux/arm64/release/ffplay.zip",  # 64-bit Linux
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "linux", "ffplay-latest-arm64.zip"
                )
            }
        },
        MAC_KEY: {
            "i686": {
                FILE_URL_TOKEN: "https://evermeet.cx/ffmpeg/getrelease/ffplay/zip",  # 32-bit macOS
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffplay-latest.zip"
                )
            },
            "64": {
                FILE_URL_TOKEN: "https://evermeet.cx/ffmpeg/getrelease/ffplay/zip",  # 64-bit macOS
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffplay-latest.zip"
                )
            },
            "arm64": {
                # 64-bit macOS (arm64)
                FILE_URL_TOKEN: "https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/release/ffplay.zip",
                FILE_PATH_TOKEN: partial(
                    process_file_path,
                    "downloads", "macos", "ffplay-latest-arm64.zip"
                )
            }
        }
    }
}
