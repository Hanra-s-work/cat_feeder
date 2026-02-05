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
# FILE: endpoint_helpers.py
# CREATION DATE: 11-01-2026
# LAST Modified: 14:24:16 02-02-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This file contains helper functions for managing API endpoints.
# // AR
# +==== END CatFeeder =================+
"""

from typing import Union, Dict, List, Any, Tuple, Set
from string import ascii_letters, digits
from random import randint

from decimal import Decimal
from threading import Lock
from datetime import datetime

from fastapi import Request

from display_tty import Disp, initialise_logger
from english_words import get_english_words_set

from . import endpoint_constants as EP_CONST

from ..config.env_loader import EnvLoader

EP_IDISP: Disp = initialise_logger(
    class_name="endpoint_helpers", debug=EnvLoader().debug
)

# Lock to ensure the english words set is loaded only once across threads
_WORDS_LOCK = Lock()


def datetime_to_string(dt: Union[datetime, str], default_message: str = "<unknown_date>", *, disp: Disp = EP_IDISP) -> str:
    """Convert a datetime object to ISO 8601 string format.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        str: The ISO 8601 formatted string representation of the datetime.
    """
    disp.log_debug(f"Converting datetime '{dt}' to string.")
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        return dt.isoformat()
    return default_message


def string_to_datetime(date_str: str, default_datetime: datetime = datetime.min, *, disp: Disp = EP_IDISP) -> datetime:
    """Convert an ISO 8601 string to a datetime object.

    Args:
        date_str (str): The ISO 8601 formatted string to convert.

    Returns:
        datetime: The corresponding datetime object.
    """
    disp.log_debug(f"Converting string '{date_str}' to datetime.")
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return default_datetime


def convert_datetime_instances_to_strings_list(data: Union[List, Tuple, Set], default_message: str = "<unknown_date>", *, disp: Disp = EP_IDISP, depth: int = 0) -> Union[List[Any], Tuple[Any, ...], Set[Any]]:
    """Convert all datetime instances in a dictionary to ISO 8601 string format.

    Args:
        data (dict): The dictionary containing potential datetime instances.
        default_message (str): The message to use if conversion fails. Defaults to '<unknown_date>'.
    Returns:
        dict: The updated dictionary with datetime instances converted to strings.
    """
    disp.log_debug("Converting datetime instances in list/tuples to strings.")
    disp.log_debug(f"Recursion depth: {depth}")
    disp.log_debug(f"Input data: {data}")
    final_list = []
    for key in data:
        if isinstance(key, datetime):
            disp.log_debug(
                f"Converting list/tuple item with datetime value '{key}'."
            )
            final_list.append(datetime_to_string(key, default_message))
        elif isinstance(key, dict):
            disp.log_debug(
                "Recursively converting dictionary item in list/tuple."
            )
            final_list.append(
                convert_datetime_instances_to_strings(
                    key, default_message, disp=disp
                )
            )
        elif isinstance(key, (list, tuple, set)):
            disp.log_debug(
                "Recursively converting list/tuple item in list/tuple."
            )
            final_list.append(
                convert_datetime_instances_to_strings_list(
                    key, default_message, disp=disp
                )
            )
        elif isinstance(key, Decimal):
            disp.log_debug(
                f"Converting list/tuple item with decimal value '{key}' to float."
            )
            final_list.append(convert_decimal_to_float(key, disp=disp))
        elif isinstance(key, bytes):
            disp.log_debug(
                f"Decoding bytes value '{key}' using bytes to str."
            )
            final_list.append(convert_bytes_to_str(key, disp=disp))
        else:
            final_list.append(key)
    disp.log_debug(f"Converted data: {final_list}")
    if isinstance(data, tuple):
        return tuple(final_list)
    if isinstance(data, set):
        return set(final_list)
    return final_list


def convert_datetime_instances_to_strings(data: Dict[str, Any], default_message: str = "<unknown_date>", *, disp: Disp = EP_IDISP, depth: int = 0) -> Dict:
    """Convert all datetime instances in a dictionary to ISO 8601 string format.

    Args:
        data (dict): The dictionary containing potential datetime instances.
        default_message (str): The message to use if conversion fails. Defaults to '<unknown_date>'.
    Returns:
        dict: The updated dictionary with datetime instances converted to strings.
    """
    disp.log_debug("Converting datetime instances in dictionary to strings.")
    disp.log_debug(f"Recursion depth: {depth}")
    disp.log_debug(f"Input data: {data}")
    for key, value in data.items():
        if isinstance(value, datetime):
            disp.log_debug(
                f"Converting key '{key}' with datetime value '{value}'."
            )
            data[key] = datetime_to_string(value, default_message)
        elif isinstance(value, dict):
            disp.log_debug(
                f"Recursively converting dictionary at key '{key}'."
            )
            data[key] = convert_datetime_instances_to_strings(
                value, default_message, disp=disp, depth=depth + 1
            )
        elif isinstance(value, (list, tuple, set)):
            disp.log_debug(
                f"Recursively converting list/tuple at key '{key}'."
            )
            data[key] = convert_datetime_instances_to_strings_list(
                value, default_message, disp=disp, depth=depth + 1
            )
        elif isinstance(value, Decimal):
            disp.log_debug(
                f"Converting key '{key}' with decimal value '{value}' to float."
            )
            data[key] = convert_decimal_to_float(value, disp=disp)
        elif isinstance(value, bytes):
            disp.log_debug(
                f"Decoding bytes value '{value}' using bytes to str."
            )
            data[key] = convert_bytes_to_str(value, disp=disp)
        else:
            disp.log_debug(f"No conversion needed for key '{key}'.")
            data[key] = value
    disp.log_debug(f"Converted data: {data}")
    return data


def convert_decimal_to_float(data: Decimal, *, disp: Disp = EP_IDISP) -> float:
    """Convert a decimal.Decimal to float.

    Args:
        data (decimal.Decimal): The decimal value to convert.

    Returns:
        float: The converted float value.
    """
    disp.log_debug("Converting decimal to float.")
    try:
        return float(data)
    except (ValueError, TypeError) as e:
        disp.log_debug(f"Failed to convert decimal to float: {e}")
        return 0.0


def convert_float_to_decimal(data: Union[float, int], *, disp: Disp = EP_IDISP) -> Decimal:
    """Convert a float to decimal.Decimal.

    Args:
        data (float): The float value to convert.

    Returns:
        decimal.Decimal: The converted decimal value.
    """
    disp.log_debug("Converting float to decimal.")
    try:
        return Decimal(data)
    except (ValueError, TypeError) as e:
        disp.log_debug(f"Failed to convert float to decimal: {e}")
        return Decimal(0)


def convert_bytes_to_str(data: Union[bytes, str], encoding: str = "utf-8", *, disp: Disp = EP_IDISP) -> str:
    """Convert bytes to string using the specified encoding.

    Args:
        data (bytes or str): The data to convert.
        encoding (str): The encoding to use for conversion. Defaults to 'utf-8'.

    Returns:
        str: The converted string.
    """
    disp.log_debug("Converting bytes to string.")
    if isinstance(data, bytes):
        disp.log_debug(f"Decoding bytes data using encoding '{encoding}'.")
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError) as e:
            disp.log_debug(
                f"Failed to decode bytes: {e}; returning default string."
            )
            return "<undecodable_bytes>"
    if not isinstance(data, str):
        disp.log_debug(
            "Data is neither bytes nor string; converting to string using str()."
        )
        return str(data)
    disp.log_debug("Data is already a string; no conversion needed.")
    return data


def convert_str_to_bytes(data: Union[bytes, str], encoding: str = "utf-8", *, disp: Disp = EP_IDISP) -> bytes:
    """Convert string to bytes using the specified encoding.

    Args:
        data (str or bytes): The data to convert.
        encoding (str): The encoding to use for conversion. Defaults to 'utf-8'.

    Returns:
        bytes: The converted bytes.
    """
    disp.log_debug("Converting string to bytes.")
    if isinstance(data, str):
        disp.log_debug(f"Encoding string data using encoding '{encoding}'.")
        try:
            return data.encode(encoding)
        except (UnicodeEncodeError, AttributeError) as e:
            disp.log_debug(
                f"Failed to encode string: {e}; returning default bytes."
            )
            return b"<un-encodable_string>"
    if not isinstance(data, bytes):
        disp.log_debug(
            "Data is neither string nor bytes; converting to bytes using str()."
        )
        return str(data).encode(encoding)
    disp.log_debug("Data is already bytes; no conversion needed.")
    return data


def load_english_words_tuple_if_required(*, disp: Disp = EP_IDISP) -> Tuple[str, ...]:
    """Load the set of English words if not already loaded.

    Returns:
        set: The set of English words.
    """
    if EP_CONST.WORDS:
        disp.log_debug("English words set already loaded.")
        disp.log_debug(f"Number of words loaded: {EP_CONST.WORDS_LENGTH}")
        return EP_CONST.WORDS

    disp.log_debug("English words set not loaded yet; acquiring lock to load.")
    with _WORDS_LOCK:
        if EP_CONST.WORDS:
            disp.log_debug("English words set loaded while waiting for lock.")
            return EP_CONST.WORDS
        disp.log_debug("Loading English words set.")
        EP_CONST.WORDS = tuple(get_english_words_set(['web2']))
        EP_CONST.WORDS_LENGTH = len(EP_CONST.WORDS)
        disp.log_debug(f"Loaded {EP_CONST.WORDS_LENGTH} English words.")
    return EP_CONST.WORDS


def generate_random_name(word_count: int = 4, *, length: int = 12, link_character: str = "-", disp: Disp = EP_IDISP) -> str:
    """Generate a random name composed of words or random characters.

    The function attempts to use a cached tuple of English words loaded via
    :func:`load_english_words_tuple_if_required`. If the word list is empty
    it falls back to using ASCII letters and digits to build random chunks.

    Args:
        word_count (int): Number of chunks/words to join. Defaults to 4.
        length (int): When generating a random-character chunk, the length of that chunk. Defaults to 12.
        link_character (str): Character used to join chunks. Defaults to '-'.
        disp (Disp): Logger instance for debug output.

    Returns:
        str: The generated name composed of `word_count` chunks joined by `link_character`. If falling back to random characters the name is prefixed with an "r" to indicate the fallback mode.
    """
    disp.log_debug(f"Generating random name of length {length}.")
    words_tuple = load_english_words_tuple_if_required(disp=disp)
    word_length = EP_CONST.WORDS_LENGTH
    random_letters: bool = False
    if not words_tuple:
        disp.log_debug(
            "English words sequence is empty; returning default name."
        )
        words_tuple = tuple(ascii_letters + digits)
        word_length = len(words_tuple)
        random_letters = True
    final_name = []
    for _attempt in range(word_count):
        if random_letters:
            name_chunk: str = ""
            for _ in range(length):
                name_chunk += words_tuple[
                    randint(0, word_length - 1)
                ]
            final_name.append(name_chunk)
        else:
            name_chunk = words_tuple[
                randint(0, word_length - 1)
            ]
            final_name.append(name_chunk)
    random_name = str(link_character).join(final_name)
    if random_letters:
        random_name = f"r{random_name}"
    disp.log_debug(f"Generated random name: {random_name}")
    return random_name


async def display_request_content(request: Request, *, disp: Disp = EP_IDISP, title: str = "display_request_content") -> None:
    """Display the content of a FastAPI request for debugging.

    Args:
        request (Request): The FastAPI request object.
        disp (Disp): Logger instance for debug output.
        title (str): Title for logging context.
    """
    padding: str = "-" * 42
    disp.log_debug(padding, title)
    disp.log_debug("Displaying request content for debugging.", title)
    disp.log_debug(padding, title)
    body = await request.body()
    form = await request.form()
    disconnected = await request.is_disconnected()
    disp.log_debug(f"Request body: {body}", title)
    try:
        json_body = await request.json()
        disp.log_debug(f"Request JSON body: {json_body}", title)
    except Exception as e:
        disp.log_debug(f"Failed to parse JSON body: {e}", title)
    disp.log_debug(f"request_content = {request}", title)
    for index, item in enumerate(request.headers.items()):
        disp.log_debug(f"header_item[{index}] = {item}", title)
    disp.log_debug(f"request.app ='{request.app}'", title)
    disp.log_debug(f"request.url = '{request.url}'", title)
    # disp.log_debug(f"request.auth = '{request.auth}'") #Only attempt to log if starlette middleware is registered
    disp.log_debug(f"request.form = '{form}'", title)
    for index, item in enumerate(request.keys()):
        disp.log_debug(f"request.keys[{index}] = '{item}'", title)
    for index, item in enumerate(request.scope.items()):
        disp.log_debug(f"request.scope[{index}] = '{item}'", title)
    disp.log_debug(f"request.state = '{request.state}'", title)
    disp.log_debug(f"request.client = '{request.client}'", title)
    disp.log_debug(f"request.method = '{request.method}'", title)
    disp.log_debug(f"request.values = '{request.values()}'", title)
    for index, item in enumerate(request.cookies.items()):
        disp.log_debug(f"request.cookies[{index}] = {item}", title)
    disp.log_debug(f"request.receive = '{request.receive}'", title)
    # for index, item in enumerate(request.session.items()): #Only attempt to log if starlette middleware is registered
    #     disp.log_debug(f"request.session[{index}] = '{item}'",title)
    disp.log_debug(f"request.base_url = '{request.base_url}'", title)
    for index, item in enumerate(request.query_params.items()):
        disp.log_debug(f"request.query_params[{index}] = {item}", title)
    disp.log_debug(f"request.is_disconnected = '{disconnected}'", title)
    for index, item in enumerate(request.path_params.items()):
        disp.log_debug(f"request.path_params[{index}] = {item}", title)
    disp.log_debug(padding, title)
    disp.log_debug("Finished displaying request content.", title)
    disp.log_debug(padding, title)


def sanitize_response_data(data: Union[List[Any], Dict[Any, Any], Tuple[Any, ...], Set[Any]], *, disp: Disp = EP_IDISP) -> Union[List[Any], Dict[Any, Any], Tuple[Any, ...], Set[Any]]:
    """Sanitize response data by converting datetime instances to strings.

    Args:
        data (list, dict, or tuple): The response data to sanitize.
        disp (Disp): Logger instance for debug output.

    Returns:
        list, dict, or tuple: The sanitized response data.
    """
    disp.log_debug("Sanitizing response data.")
    disp.log_debug("Converting datetime instances in dictionary to strings.")
    disp.log_debug(f"Input data: {data}")
    if isinstance(data, dict):
        return convert_datetime_instances_to_strings(data, disp=disp)
    if isinstance(data, (list, tuple, set)):
        return convert_datetime_instances_to_strings_list(data, disp=disp)
    disp.log_debug(
        "Data is not iterable, checking if specific conversions are needed."
    )
    if isinstance(data, datetime):
        disp.log_debug(
            f"Converting datetime value '{data}' to string."
        )
        return datetime_to_string(data)
    if isinstance(data, Decimal):
        disp.log_debug(
            f"Converting decimal value '{data}' to float."
        )
        return convert_decimal_to_float(data, disp=disp)
    if isinstance(data, bytes):
        disp.log_debug("Decoding bytes data using bytes to str.")
        return convert_bytes_to_str(data, disp=disp)
    disp.log_debug("No conversion needed for data.")
    return data
