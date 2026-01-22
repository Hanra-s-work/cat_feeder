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
# FILE: favicon_helpers.py
# CREATION DATE: 12-01-2026
# LAST Modified: 22:17:14 12-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of containing the functions that will help the favicon classes in the different processes.
# // AR
# +==== END CatFeeder =================+
"""

from typing import List, Dict, Any, Union, Optional, TYPE_CHECKING
from pathlib import Path
from display_tty import Disp, initialise_logger
from ..config.env_loader import EnvLoader
from ..image_reducer import image_reducer_constants as IR_CONST
from ..http_codes import HttpDataTypes
from . import favicon_constants as FAV_CONST

if TYPE_CHECKING:
    from ..sql import SQL

FAVICON_HELPER_DISP: Disp = initialise_logger(
    class_name="FaviconHelperDisp", debug=EnvLoader().debug
)


def reducer_type_to_data_type(reducer_type: IR_CONST.FileFormat, *, disp: Disp = FAVICON_HELPER_DISP) -> HttpDataTypes:
    """Convert an ImageReducer FileFormat to an HttpDataTypes value.

    Args:
        reducer_type (IR_CONST.FileFormat): The image reducer file format.

    Returns:
        HttpDataTypes: The corresponding HTTP data type.
    """
    disp.log_debug(
        f"Converting reducer type '{reducer_type}' to HTTP data type."
    )
    if reducer_type == IR_CONST.FileFormat.PNG:
        disp.log_debug("Matched PNG format.")
        return HttpDataTypes.PNG
    if reducer_type == IR_CONST.FileFormat.JPEG:
        disp.log_debug("Matched JPEG format.")
        return HttpDataTypes.JPEG
    if reducer_type == IR_CONST.FileFormat.WEBP:
        disp.log_debug("Matched WEBP format.")
        return HttpDataTypes.WEBP
    if reducer_type == IR_CONST.FileFormat.SVG:
        disp.log_debug("Matched SVG format.")
        return HttpDataTypes.SVG
    disp.log_debug("No matching format found. Defaulting to OCTET_STREAM.")
    return HttpDataTypes.OCTET_STREAM


def generate_image_path(filename: str, file_id: str) -> str:
    """Generate the full image path for a favicon in the bucket.

    Args:
        filename (str): The filename of the image.
        file_id (str): The unique identifier for the favicon.

    Returns:
        str: The full path to the image in the bucket.
    """
    file_format = Path(filename).name.rsplit(
        ".", maxsplit=1
    )[-1]  # Sanitize the filename
    return str(Path(FAV_CONST.FAVICON_BUCKET_FOLDER_USER) / f"{file_id}.{file_format}")


def list_from_table(sql: "SQL", table: str, *, title: str = "_list_from_table", disp: Disp = FAVICON_HELPER_DISP) -> List[Dict[str, Any]]:
    """Retrieve all rows from `table` using the provided SQL helper.

    This wraps the low-level SQL `get_data_from_table` call and returns a
    list of dictionaries. On SQL failure the function logs the error and
    returns an empty list.

    Args:
        sql (SQL): SQL helper instance with `get_data_from_table`.
        table (str): Table name to query.
        title (str): Optional logging title.
        disp (Disp): Optional display logger.

    Returns:
        List[Dict[str, Any]]: The list of rows (possibly empty on error).
    """
    disp.log_debug(
        f"Gathering the list of entries from table '{table}'", title
    )
    resp = sql.get_data_from_table(
        table=table,
        column="*"
    )
    if isinstance(resp, int):
        disp.log_error(
            f"Failed to gather data for table '{table}'", title
        )
        disp.log_error(
            "Returning []", title
        )
        return []
    disp.log_debug(
        f"Data gathered for table '{table}':\n{resp}", title
    )
    return resp


def extract_line_from_id(data_list: List[Dict[str, Any]], entry_id: Optional[Union[int, str]], *, disp: Disp = FAVICON_HELPER_DISP) -> Dict[str, Any]:
    """Extract a line from a list of dictionaries based on the 'id' key.

    Args:
        data_list (List[Dict[str, Any]]): The list of dictionaries to search.
        entry_id (Union[int,str]): The id to search for.
        disp (Disp, optional): The display logger to use.

    Returns:
        Dict[str, Any]: The dictionary with the matching id. If no matching
        entry is found the function returns a dictionary containing only the
        `'id'` key with the original `entry_id` value (e.g. `{'id': entry_id}`).
    """
    if not entry_id:
        disp.log_debug(
            "No entry_id provided, returning empty dictionary.", "extract_line_from_id"
        )
        return {'id': entry_id}
    disp.log_debug(
        f"Extracting entry with id '{entry_id}' from data list.", "extract_line_from_id"
    )
    entry_id_str: str = str(entry_id)
    for entry in data_list:
        if str(entry.get("id")) == entry_id_str:
            disp.log_debug(
                f"Entry found: {entry}", "extract_line_from_id"
            )
            return entry
    disp.log_debug(
        f"No entry found with id '{entry_id}'. Returning empty dictionary.", "extract_line_from_id"
    )
    return {'id': entry_id}


def get_from_table(sql: "SQL", table: str, item_id: Union[int, str], *, title: str = "get_from_table", disp: Disp = FAVICON_HELPER_DISP) -> Dict[str, Any]:
    """Retrieve a single row by id from `table`.

    Args:
        sql (SQL): SQL helper instance.
        table (str): Table name to query.
        item_id (Union[int, str]): The id value to look up.
        title (str): Optional logging title.
        disp (Disp): Optional display logger.

    Returns:
        Dict[str, Any]: The found row as a dictionary. If the SQL call fails
        the function returns a dict with `{'id': id}`. If the query succeeds
        but no rows are found it returns an empty dict.
    """
    disp.log_debug(
        f"Gathering a single entry from table '{table}'", title
    )
    resp = sql.get_data_from_table(
        table=table,
        column="*",
        where=f"id={item_id}",
        beautify=True
    )
    if isinstance(resp, int):
        disp.log_error(
            f"Failed to gather data for table '{table}'", title
        )
        disp.log_error(
            "Returning empty dictionary", title
        )
        return {'id': id}
    if len(resp) == 0:
        disp.log_debug(
            f"No entries found in table '{table}'. Returning empty dictionary.", title
        )
        return {}
    disp.log_debug(
        f"Data gathered for table '{table}':\n{resp[0]}", title
    )
    return resp[0]


def is_hex_colour_valid(colour: str) -> bool:
    """Check if a string is a valid hex colour code.

    Args:
        colour (str): The colour string to validate.
    Returns:
        bool: True if valid hex colour, False otherwise.
    """
    if isinstance(colour, str):
        return bool(FAV_CONST.FAVICON_HEX_COLOUR_RE.fullmatch(colour))
    return False


def pad_hex_colour(colour: str, with_alpha: bool = True) -> str:
    """
    Normalize a hex colour to full form.

    - #RGB      → #RRGGBB
    - #RGBA     → #RRGGBBAA
    - #RRGGBB   → #RRGGBB or #RRGGBBFF
    - #RRGGBBAA → unchanged

    Args:
        colour (str): Hex colour
        with_alpha (bool): If True, ensure alpha channel exists

    Returns:
        str: Normalized hex colour
    """
    if not is_hex_colour_valid(colour):
        return colour

    hex_part = colour[1:]

    if len(hex_part) in (3, 4):
        # Expand shorthand
        hex_part = ''.join(c * 2 for c in hex_part)

    if len(hex_part) == 6 and with_alpha:
        hex_part += 'FF'  # fully opaque

    return '#' + hex_part.upper()


def unpad_hex_colour(colour: str) -> str:
    """
    Compress a hex colour to shorthand when safe.

    - #RRGGBB   → #RGB
    - #RRGGBBAA → #RGBA
    - Otherwise unchanged
    """
    if not is_hex_colour_valid(colour):
        return colour

    hex_part = colour[1:]

    if len(hex_part) not in (6, 8):
        return colour

    step = 2
    compressed = []

    for i in range(0, len(hex_part), step):
        pair = hex_part[i:i + 2]
        if pair[0] != pair[1]:
            return colour
        compressed.append(pair[0])

    return '#' + ''.join(compressed).upper()
