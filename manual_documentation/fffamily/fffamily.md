<!-- 
-- +==== BEGIN AsperBackend =================+
-- LOGO: 
-- ..........####...####..........
-- ......###.....#.#########......
-- ....##........#.###########....
-- ...#..........#.############...
-- ...#..........#.#####.######...
-- ..#.....##....#.###..#...####..
-- .#.....#.##...#.##..##########.
-- #.....##########....##...######
-- #.....#...##..#.##..####.######
-- .#...##....##.#.##..###..#####.
-- ..#.##......#.#.####...######..
-- ..#...........#.#############..
-- ..#...........#.#############..
-- ...##.........#.############...
-- ......#.......#.#########......
-- .......#......#.########.......
-- .........#####...#####.........
-- /STOP
-- PROJECT: AsperBackend
-- FILE: fffamily.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:42:48 02-12-2025
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: The overview of the module in charge of downloading ff family dependencies that can later be used by the server.
-- // AR
-- +==== END AsperBackend =================+
-->
# FFmpeg Family Module

## Overview

The `fffamily` module provides automated FFmpeg binary management for the AsperBackend application. It handles downloading, extracting, and configuring FFmpeg, FFprobe, and FFplay binaries across different operating systems (Windows, Linux, macOS) and architectures, eliminating the need for manual installation.

## Architecture

![FFmpeg Family Architecture](fffamily_architecture.puml)

## Core Components

### FFMPEGDownloader Class

The `FFMPEGDownloader` class is the main component responsible for managing FFmpeg family binaries. It implements the `FinalClass` metaclass pattern and provides cross-platform binary management.

**Key Features:**

- Automatic binary downloading from official sources
- Multi-platform support (Windows, Linux, macOS)
- Architecture detection (32-bit, 64-bit, ARM)
- Binary extraction and setup
- Executable permissions management (Unix-like systems)
- Path resolution utilities
- Audio sample generation for testing

**Attributes:**

- `available_binaries`: List of supported binaries (ffmpeg, ffprobe, ffplay)
- `cwd`: Current working directory for binary storage
- `system`: Detected operating system name
- `architecture`: Detected system architecture
- `file_url`: Download URL for the binary package
- `file_path`: Local path for downloaded archive
- `fold_path`: Path for extracted binaries

### Supported Platforms

| Platform | Architecture | Status |
|----------|-------------|--------|
| Windows | 32-bit, 64-bit | ✅ Supported |
| Linux | 64-bit, ARM | ✅ Supported |
| macOS | Intel, ARM (M1/M2) | ✅ Supported |

## Configuration

### Constants (ff_constants.py)

The module defines platform-specific download URLs and paths:

```python
# Binary Keys
FFMPEG_KEY = "ffmpeg"
FFPROBE_KEY = "ffprobe"
FFPLAY_KEY = "ffplay"

# Platform Keys
WINDOWS_KEY = "windows"
LINUX_KEY = "linux"
MAC_KEY = "darwin"

# URL Configuration
FILE_URL_TOKEN = "file_url"

# Platform-specific download URLs
FFMPEG_URLS = {
    WINDOWS_KEY: "https://...",
    LINUX_KEY: "https://...",
    MAC_KEY: "https://..."
}
```

### Custom Exceptions (ff_exceptions.py)

The module defines specific exceptions for error handling:

```python
class ArchitectureNotSupported(Exception):
    """System architecture is not supported"""
    pass

class PackageNotInstalled(Exception):
    """FF binary is not installed"""
    pass

class PackageNotSupported(Exception):
    """System platform is not supported"""
    pass
```

## Usage Examples

### Automatic Binary Setup

```python
from backend.src.libs.fffamily import FFMPEGDownloader

# Initialize downloader
downloader = FFMPEGDownloader(
    cwd="/path/to/binary/storage",
    query_timeout=30,
    debug=True
)

# Download and setup all binaries
status = downloader.main()

if status == 0:
    print("FFmpeg family installed successfully")
else:
    print("Installation failed")
```

### Get FFmpeg Binary Path

```python
from backend.src.libs.fffamily import FFMPEGDownloader

# Get path to ffmpeg binary (downloads if not present)
try:
    ffmpeg_path = FFMPEGDownloader.get_ffmpeg_binary_path(
        download_if_not_present=True,
        cwd="/path/to/storage",
        debug=True
    )
    print(f"FFmpeg binary: {ffmpeg_path}")
    
    # Use with subprocess
    import subprocess
    result = subprocess.run(
        [ffmpeg_path, "-version"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
except Exception as e:
    print(f"Error: {e}")
```

### Get All Binary Paths

```python
# Get all three binaries
try:
    ffmpeg_path = FFMPEGDownloader.get_ffmpeg_binary_path()
    ffprobe_path = FFMPEGDownloader.get_ffprobe_binary_path()
    ffplay_path = FFMPEGDownloader.get_ffplay_binary_path()
    
    binaries = {
        "ffmpeg": ffmpeg_path,
        "ffprobe": ffprobe_path,
        "ffplay": ffplay_path
    }
    
    print("Available binaries:")
    for name, path in binaries.items():
        print(f"  {name}: {path}")
        
except Exception as e:
    print(f"Error getting binaries: {e}")
```

### Manual Download Control

```python
# Check if binaries exist without downloading
try:
    family_path = FFMPEGDownloader.get_ff_family_path(
        download_if_not_present=False
    )
    print("Binaries already installed")
    
except PackageNotInstalled:
    print("Binaries not found, downloading...")
    downloader = FFMPEGDownloader(debug=True)
    downloader.main()
```

### Video Processing Example

```python
import subprocess
from backend.src.libs.fffamily import FFMPEGDownloader

# Get ffmpeg path
ffmpeg_path = FFMPEGDownloader.get_ffmpeg_binary_path()

# Convert video format
def convert_video(input_file, output_file, format="mp4"):
    """Convert video to specified format"""
    cmd = [
        ffmpeg_path,
        "-i", input_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        output_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Conversion successful: {output_file}")
    else:
        print(f"Error: {result.stderr}")
    
    return result.returncode

# Usage
status = convert_video("input.avi", "output.mp4")
```

### Audio Processing Example

```python
from backend.src.libs.fffamily import FFMPEGDownloader
from pydub import AudioSegment

# Set FFmpeg path for pydub
AudioSegment.converter = FFMPEGDownloader.get_ffmpeg_binary_path()
AudioSegment.ffprobe = FFMPEGDownloader.get_ffprobe_binary_path()

# Generate test audio sample
tone_segment = FFMPEGDownloader.generate_audio_sample(tone=440)

# Play audio
from pydub.playback import play
play(tone_segment)

# Export audio
tone_segment.export("test_tone.mp3", format="mp3")
```

### Get Media Information

```python
import subprocess
import json
from backend.src.libs.fffamily import FFMPEGDownloader

ffprobe_path = FFMPEGDownloader.get_ffprobe_binary_path()

def get_media_info(file_path):
    """Get detailed media file information"""
    cmd = [
        ffprobe_path,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise RuntimeError(f"FFprobe error: {result.stderr}")

# Usage
info = get_media_info("video.mp4")
print(f"Duration: {info['format']['duration']}s")
print(f"Bitrate: {info['format']['bit_rate']}")
```

## Key Methods

### Static Methods

#### get_ffmpeg_binary_path(download_if_not_present=True, cwd=os.getcwd(), ...)

Returns the path to the ffmpeg binary.

**Parameters:**

- `download_if_not_present` (bool): Download if not found (default: True)
- `cwd` (str): Working directory for storage
- `query_timeout` (int): Download timeout in seconds
- `success` (int): Success return code
- `error` (int): Error return code
- `debug` (bool): Enable debug logging

**Returns:**

- `str`: Absolute path to ffmpeg binary

**Raises:**

- `PackageNotSupported`: Unsupported OS
- `PackageNotInstalled`: Binary not found

#### get_ffprobe_binary_path(...)

Returns the path to the ffprobe binary (same parameters as above).

#### get_ffplay_binary_path(...)

Returns the path to the ffplay binary (same parameters as above).

#### get_ff_family_path(...)

Returns the base directory containing all FF binaries.

**Returns:**

- `str`: Path to directory containing ffmpeg, ffprobe, and ffplay folders

#### get_system_name()

Detects and returns the operating system name.

**Returns:**

- `str`: "windows", "linux", or "darwin"

#### get_platform()

Detects and returns the system architecture.

**Returns:**

- `str`: "32bit", "64bit", or specific ARM architecture

#### generate_audio_sample(tone=440)

Generates a test audio sample at the specified frequency.

**Parameters:**

- `tone` (int): Frequency in Hz (default: 440Hz - A4 note)

**Returns:**

- `AudioSegment`: Pydub audio segment object

#### process_file_path(*args, cwd=None)

Resolves file paths across different operating systems.

**Parameters:**

- `*args`: Path components
- `cwd` (str/PPath): Current working directory

**Returns:**

- `str`: Normalized absolute path

### Instance Methods

#### main()

Main execution method that downloads, extracts, and configures all binaries.

**Returns:**

- `int`: Success (0) or error (84) code

**Process:**

1. Detect system and architecture
2. Determine download URLs
3. Create storage directories
4. Download binary archives
5. Extract archives
6. Set executable permissions (Unix)
7. Organize binaries into correct paths

### Private Helper Methods

#### _download_file(file_url, file_path, query_timeout)

Downloads a file from URL to local path.

#### _create_path_if_not_exists(path)

Creates directory structure if it doesn't exist.

#### _grant_executable_rights(file_path)

Sets executable permissions on Unix-like systems (chmod 755).

#### _rename_extracted_folder(old_name, new_name)

Renames extracted directory to standardized name.

## Platform-Specific Behavior

### Windows

```python
# Binary names
ffmpeg.exe
ffprobe.exe
ffplay.exe

# No permission modification needed
# Automatic download from Windows builds
```

### Linux

```python
# Binary names
ffmpeg
ffprobe
ffplay

# Automatic executable permission setup (chmod 755)
# Download from static Linux builds
```

### macOS

```python
# Binary names
ffmpeg
ffprobe
ffplay

# Automatic executable permission setup
# Universal binaries for Intel and Apple Silicon
```

## Directory Structure

After installation, binaries are organized as follows:

```txt
<cwd>/
├── ffmpeg/
│   ├── windows/
│   │   └── ffmpeg.exe
│   ├── linux/
│   │   └── ffmpeg
│   └── darwin/
│       └── ffmpeg
├── ffprobe/
│   ├── windows/
│   │   └── ffprobe.exe
│   ├── linux/
│   │   └── ffprobe
│   └── darwin/
│       └── ffprobe
└── ffplay/
    ├── windows/
    │   └── ffplay.exe
    ├── linux/
    │   └── ffplay
    └── darwin/
        └── ffplay
```

## Error Handling

### Exception Hierarchy

```python
try:
    ffmpeg_path = FFMPEGDownloader.get_ffmpeg_binary_path()
except ArchitectureNotSupported as e:
    print(f"Architecture not supported: {e}")
except PackageNotSupported as e:
    print(f"Platform not supported: {e}")
except PackageNotInstalled as e:
    print(f"Binary not installed: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
```

### Common Issues

1. **Download Timeout**: Increase `query_timeout` parameter
2. **Permission Denied**: Ensure write access to `cwd`
3. **Architecture Detection Failed**: Check platform.system() output
4. **Extraction Failed**: Verify downloaded archive integrity

## Integration with FastAPI

### Endpoint Example

```python
from fastapi import FastAPI, UploadFile, File
from backend.src.libs.fffamily import FFMPEGDownloader
import subprocess
import os

app = FastAPI()

# Initialize FFmpeg
ffmpeg_path = FFMPEGDownloader.get_ffmpeg_binary_path()

@app.post("/convert-video")
async def convert_video(file: UploadFile = File(...)):
    """Convert uploaded video to MP4"""
    
    # Save uploaded file
    input_path = f"/tmp/{file.filename}"
    output_path = f"/tmp/{os.path.splitext(file.filename)[0]}.mp4"
    
    with open(input_path, "wb") as f:
        f.write(await file.read())
    
    # Convert using FFmpeg
    cmd = [
        ffmpeg_path,
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "fast",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode == 0:
        return {"message": "Conversion successful", "output": output_path}
    else:
        return {"error": result.stderr.decode()}
```

## Performance Considerations

1. **First-Time Setup**: Initial download may take 1-5 minutes depending on connection
2. **Caching**: Binaries are cached locally after first download
3. **Disk Space**: Each platform requires ~50-150MB of storage
4. **Concurrent Access**: Safe for multi-threaded applications

## Dependencies

- `requests`: HTTP downloads
- `platform`: System detection
- `zipfile`/`tarfile`: Archive extraction
- `pydub`: Audio processing
- `pathlib`: Path manipulation
- Core modules (FinalClass)

## Best Practices

1. **Cache Binary Paths**: Store paths in application configuration
2. **Check Before Download**: Use `download_if_not_present=False` to check availability
3. **Set Appropriate Timeouts**: Adjust `query_timeout` based on connection speed
4. **Handle Exceptions**: Always wrap calls in try-except blocks
5. **Use Absolute Paths**: Specify full `cwd` path for reliability

## See Also

- [FFmpeg Official Documentation](https://ffmpeg.org/documentation.html)
- [Pydub Documentation](https://github.com/jiaaro/pydub)
- [Core Module Documentation](../core/core.md)
