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
# FILE: favicon_admin.py
# CREATION DATE: 05-01-2026
# LAST Modified: 1:39:39 13-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the handler for the admin favicons.
# // AR
# +==== END CatFeeder =================+
"""

from typing import TYPE_CHECKING, Optional, List, Union, Dict, Any

from fastapi import Response, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from display_tty import Disp, initialise_logger

from . import favicon_constants as FAV_CONST
from . import favicon_helpers as FAV_HELPERS
from . import favicon_error_class as FAV_ERR

from ..core import FinalSingleton
from ..core.runtime_manager import RI, RuntimeManager
from ..image_reducer import FileFormat
from ..http_codes import HCI, HttpDataTypes
from ..utils import CONST

if TYPE_CHECKING:
    from ..sql import SQL
    from ..bucket import Bucket
    from ..image_reducer import ImageReducer
    from ..server_header import ServerHeaders
    from ..boilerplates.responses import BoilerplateResponses


class FaviconAdmin(FinalSingleton):

    # --------------------------------------------------------------------------
    # STATIC CLASS VALUES
    # --------------------------------------------------------------------------

    # -------------- Initialise the logger globally in the class. --------------
    disp: Disp = initialise_logger(__qualname__, False)

    # --------------------------------------------------------------------------
    # CONSTRUCTOR & DESTRUCTOR
    # --------------------------------------------------------------------------

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """Initialize the ImageReducer instance with dependencies.

        Keyword Arguments:
            debug: Enable debug logging when True. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.success = success
        self.error = error
        self.disp.log_debug("Initialising...")
        self.runtime_manager: RuntimeManager = RI
        self.boilerplate_response: "BoilerplateResponses" = self.runtime_manager.get(
            "BoilerplateResponses")
        self.server_header: "ServerHeaders" = self.runtime_manager.get(
            "ServerHeaders")
        self.bucket: "Bucket" = self.runtime_manager.get("Bucket")
        self.sql: "SQL" = self.runtime_manager.get("SQL")
        self.image_reducer: Optional["ImageReducer"] = self.runtime_manager.get_if_exists(
            "ImageReducer", None)
        self.disp.log_debug("Initialised")

    def _no_user_id(self, title: str, token: Optional[str] = None) -> Response:
        """Return a standardized response when no user id is provided.

        Logs an error and returns the `user_not_found` response constructed by
        the configured boilerplate response helper.

        Args:
            title (str): Title to include in the response context.
            token (Optional[str]): Optional token related to the request.

        Returns:
            Response: A FastAPI response produced by `BoilerplateResponses`.
        """
        self.disp.log_error("There is no specified user id.")
        return self.boilerplate_response.user_not_found(title, token)

    def _no_data(self, title: str, token: Optional[str] = None) -> Response:
        """Return a 404 JSON response when no favicon data exists.

        Builds a standardized error body using the boilerplate response helper
        and returns an HTTP 404 response with appropriate JSON headers.

        Args:
            title (str): Title to include in the response context.
            token (Optional[str]): Optional token related to the request.

        Returns:
            Response: A FastAPI response with HTTP 404 and JSON body.
        """
        self.disp.log_error("There is no data available.")
        body = self.boilerplate_response.build_response_body(
            title=title,
            message="No icon available",
            resp="No data",
            token=token,
            error=True
        )
        return HCI.not_found(
            content=body,
            content_type=HttpDataTypes.JSON,
            headers=self.server_header.for_json()
        )

    def _populate_ids(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace numeric id fields in a favicon data dict with full records.

        Mutates the provided `data` mapping by replacing `type`, `gender` and
        `season` fields (when present) with the corresponding full records from
        the database.

        Args:
            data (Dict[str, Any]): The raw favicon data containing id fields.

        Returns:
            Dict[str, Any]: The mutated mapping with populated fields.
        """
        data["type"] = self.get_favicon_type(data.get("type", -1))
        data["gender"] = self.get_favicon_gender(data.get("gender", -1))
        data["season"] = self.get_favicon_season(data.get("season", -1))
        return data

    def _process_favicon_type_id(self, ftype: Optional[Union[int, str]] = None) -> Optional[int]:
        """Normalize a favicon type identifier to a numeric id.

        Accepts either an integer id or a string name/id and returns the
        corresponding integer id when found, otherwise `None`.

        Args:
            ftype (Optional[Union[int, str]]): The id or name to resolve.

        Returns:
            Optional[int]: The resolved integer id or `None` if not found.
        """
        if not isinstance(ftype, (int, str)):
            return None
        data = self.list_favicon_type()
        ftype_str = str(ftype)
        for item in data:
            fid = item.get("id")
            if str(fid) == ftype_str:
                return fid
            if item.get("name") == str(ftype):
                return fid
        return None

    def _process_favicon_gender_id(self, gender: Optional[Union[int, str]] = None) -> Optional[int]:
        """Normalize a favicon gender identifier to a numeric id.

        Accepts either an integer id or a string name/id and returns the
        corresponding integer id when found, otherwise `None`.

        Args:
            gender (Optional[Union[int, str]]): The id or name to resolve.

        Returns:
            Optional[int]: The resolved integer id or `None` if not found.
        """
        if not isinstance(gender, (int, str)):
            return None
        data = self.list_favicon_type()
        gender_str = str(gender)
        for item in data:
            gid = item.get("id")
            if str(gid) == gender_str:
                return gid
            if item.get("gender") == str(gender):
                return gid
        return None

    def _process_favicon_season_id(self, ftype: Optional[Union[int, str]] = None) -> Optional[int]:
        """Normalize a favicon season identifier to a numeric id.

        Accepts either an integer id or a string name/id and returns the
        corresponding integer id when found, otherwise `None`.

        Args:
            ftype (Optional[Union[int, str]]): The id or name to resolve.

        Returns:
            Optional[int]: The resolved integer id or `None` if not found.
        """
        if not isinstance(ftype, (int, str)):
            return None
        data = self.list_favicon_type()
        ftype_str = str(ftype)
        for item in data:
            fid = item.get("id")
            if str(fid) == ftype_str:
                return fid
            if item.get("season") == str(ftype):
                return fid
        return None

    def _upload_bytes(self, image_data: bytes, icon_id: int, *, title: str = "_upload_bytes") -> str:
        """Upload image bytes to the configured bucket.

        This is a placeholder for the actual implementation of the image
        upload logic.
        """
        self.image_reducer = self.runtime_manager.get_if_exists(
            "ImageReducer", self.image_reducer)
        if self.image_reducer is None:
            self.disp.log_error(
                "There is no ImageReducer instance available in the runtime manager", title
            )
            raise FAV_ERR.FaviconNoImageReducerError(
                "ImageReducer instance not found in RuntimeManager"
            )
        file_format = self.image_reducer.detect_file_format(
            image_data).name.lower()
        img_path = FAV_HELPERS.generate_image_path(
            f"{icon_id}.{file_format}", str(icon_id)
        )
        bucket_status = self.bucket.upload_stream(
            bucket_name=FAV_CONST.FAVICON_BUCKET_NAME,
            key_name=img_path,
            data=image_data
        )
        if isinstance(bucket_status, int) and bucket_status != self.success:
            err_msg = f"Failed to upload favicon image data to bucket '{FAV_CONST.FAVICON_BUCKET_NAME}' at path '{img_path}'"
            self.disp.log_error(err_msg)
            raise FAV_ERR.FaviconImageUploadError(err_msg)
        return img_path

    def _upload_file(self, image_data: UploadFile, icon_id: int, *, title: str = "_upload_bytes") -> str:
        """Upload an UploadFile to the configured bucket.

        This is a placeholder for the actual implementation of the image
        upload logic.
        """
        self.image_reducer = self.runtime_manager.get_if_exists(
            "ImageReducer", self.image_reducer)
        if self.image_reducer is None:
            self.disp.log_error(
                "There is no ImageReducer instance available in the runtime manager", title
            )
            raise FAV_ERR.FaviconNoImageReducerError(
                "ImageReducer instance not found in RuntimeManager"
            )
        file_data = image_data.file.read()
        file_name = image_data.filename
        image_data.file.close()
        file_format = self.image_reducer.detect_file_format(
            file_data).name.lower()
        img_path = FAV_HELPERS.generate_image_path(
            f"{file_name}.{file_format}", str(icon_id)
        )
        bucket_status = self.bucket.upload_stream(
            bucket_name=FAV_CONST.FAVICON_BUCKET_NAME,
            key_name=img_path,
            data=file_data
        )
        if isinstance(bucket_status, int) and bucket_status != self.success:
            err_msg = f"Failed to upload favicon image data to bucket '{FAV_CONST.FAVICON_BUCKET_NAME}' at path '{img_path}'"
            self.disp.log_error(err_msg)
            raise FAV_ERR.FaviconImageUploadError(err_msg)
        return img_path

    def reducer_type_to_data_type(self, reducer_type: FileFormat) -> HttpDataTypes:
        """(This is a wrapper of the same function in the constants)
        Convert an ImageReducer FileFormat to an HttpDataTypes value.

        Args:
            reducer_type (IR_CONST.FileFormat): The image reducer file format.

        Returns:
            HttpDataTypes: The corresponding HTTP data type.
        """
        return FAV_HELPERS.reducer_type_to_data_type(reducer_type)

    def list_favicon_gender(self) -> List[Dict[str, Any]]:
        """List all favicon genders from the database.

        Returns a list of dictionary records representing available genders.

        Returns:
            List[Dict[str, Any]]: The gender records.
        """
        table: str = FAV_CONST.FAVICON_TABLE_GENDER
        title = "list_favicon_gender:list_from_table"
        return FAV_HELPERS.list_from_table(self.sql, table, title=title, disp=self.disp)

    def list_favicon_season(self) -> List[Dict[str, Any]]:
        """List all favicon seasons from the database.

        Returns a list of dictionary records representing available seasons.

        Returns:
            List[Dict[str, Any]]: The season records.
        """
        table: str = FAV_CONST.FAVICON_TABLE_SEASON
        title = "list_favicon_season:list_from_table"
        return FAV_HELPERS.list_from_table(self.sql, table, title=title, disp=self.disp)

    def list_favicon_type(self) -> List[Dict[str, Any]]:
        """List all favicon types from the database.

        Returns a list of dictionary records representing available types.

        Returns:
            List[Dict[str, Any]]: The type records.
        """
        table: str = FAV_CONST.FAVICON_TABLE_TYPE
        title = "list_favicon_type:list_from_table"
        return FAV_HELPERS.list_from_table(self.sql, table, title=title, disp=self.disp)

    def list_favicons(self) -> List[Dict[str, Any]]:
        """Return list of favicons with resolved type/gender/season fields.

        Fetches raw favicon records from the main table and replaces numeric
        `type`, `gender` and `season` identifiers with full records resolved
        via the helper list/get functions.

        Returns:
            List[Dict[str, Any]]: The favicon records with populated fields.
        """
        table: str = FAV_CONST.FAVICON_TABLE_MAIN
        title = "list_favicons:list_from_table"
        favicon = FAV_HELPERS.list_from_table(
            self.sql, table, title=title, disp=self.disp)
        if len(favicon) == 0:
            self.disp.log_debug("No favicons available.")
            return favicon
        f_type = self.list_favicon_type()
        f_gender = self.list_favicon_gender()
        f_season = self.list_favicon_season()
        for icon in favicon:
            icon["type"] = FAV_HELPERS.extract_line_from_id(
                data_list=f_type, entry_id=icon.get("type", -1), disp=self.disp
            )
            icon["gender"] = FAV_HELPERS.extract_line_from_id(
                data_list=f_gender, entry_id=icon.get("gender", -1), disp=self.disp
            )
            icon["season"] = FAV_HELPERS.extract_line_from_id(
                data_list=f_season, entry_id=icon.get("season", -1), disp=self.disp
            )
        return favicon

    def get_favicon_gender(self, item_id: Union[int, str] = 1) -> Dict[str, Any]:
        """Retrieve a single favicon gender record by id.

        Args:
            item_id (Union[int, str]): The id (or identifier) of the gender.

        Returns:
            Dict[str, Any]: The gender record or an empty dict if not found.
        """
        table: str = FAV_CONST.FAVICON_TABLE_GENDER
        title = "get_favicon_gender:get_from_table"
        return FAV_HELPERS.get_from_table(self.sql, table, item_id, title=title, disp=self.disp)

    def get_favicon_season(self, item_id: Union[int, str] = 1) -> Dict[str, Any]:
        """Retrieve a single favicon season record by id.

        Args:
            item_id (Union[int, str]): The id (or identifier) of the season.

        Returns:
            Dict[str, Any]: The season record or an empty dict if not found.
        """
        table: str = FAV_CONST.FAVICON_TABLE_SEASON
        title = "get_favicon_season:get_from_table"
        return FAV_HELPERS.get_from_table(self.sql, table, item_id, title=title, disp=self.disp)

    def get_favicon_type(self, item_id: Union[int, str] = 1) -> Dict[str, Any]:
        """Retrieve a single favicon type record by id.

        Args:
            item_id (Union[int, str]): The id (or identifier) of the type.

        Returns:
            Dict[str, Any]: The type record or an empty dict if not found.
        """
        table: str = FAV_CONST.FAVICON_TABLE_TYPE
        title = "get_favicon_type:get_from_table"
        return FAV_HELPERS.get_from_table(self.sql, table, item_id, title=title, disp=self.disp)

    def get_favicon(self, favicon_id, *, fetch_image: bool = True, title: str = "list_user_favicon", token: Optional[str] = None) -> Union[FAV_CONST.FaviconData, Response]:
        """Retrieve a favicon record and optionally its binary image.

        Args:
            favicon_id: The id of the favicon to retrieve.
            fetch_image (bool): If True, attempt to download image bytes from the
                configured bucket. If False, return metadata only. Defaults to True.
            title (str): Title used in logging and error responses.
            token (Optional[str]): Optional token used in error responses.

        Returns:
            Union[FAV_CONST.FaviconData, Response]: A `FaviconData` object with
            metadata and optionally `img`/`img_type` populated, or a FastAPI
            `Response` when an error response should be returned.
        """
        table: str = FAV_CONST.FAVICON_TABLE_MAIN
        final_resp: FAV_CONST.FaviconData = FAV_CONST.FaviconData()
        self.disp.log_debug(
            f"Gathering the list of uploaded user icons from table '{table}'"
        )
        sql_resp = self.sql.get_data_from_table(
            table=table,
            column="*",
            where=f"id={favicon_id}"
        )
        if isinstance(sql_resp, int):
            self.disp.log_error(
                f"Failed to gather data for table '{table}'"
            )
            return self._no_data(title, token)
        if len(sql_resp) == 0:
            return final_resp
        final_resp.data = CONST.clean_dict(
            self._populate_ids(
                sql_resp[0].copy()
            ),
            (FAV_CONST.FAVICON_IMAGE_PATH_KEY, ""),
            self.disp
        )
        if sql_resp[0][FAV_CONST.FAVICON_IMAGE_PATH_KEY] is None or sql_resp[0][FAV_CONST.FAVICON_IMAGE_PATH_KEY] == "":
            self.disp.log_error(
                f"There is no image path for icon id='{favicon_id}'"
            )
            return final_resp
        if not fetch_image:
            self.disp.log_debug(
                "Image fetch not requested; returning data without image."
            )
            return final_resp
        self.image_reducer = self.runtime_manager.get_if_exists(
            "ImageReducer", self.image_reducer)
        if self.image_reducer is None:
            self.disp.log_error(
                "There is no ImageReducer instance available in the runtime manager"
            )
            return final_resp
        img_path = sql_resp[0][FAV_CONST.FAVICON_IMAGE_PATH_KEY]
        bucket_resp = self.bucket.download_stream(
            bucket_name=FAV_CONST.FAVICON_BUCKET_NAME,
            key_name=img_path
        )
        if isinstance(bucket_resp, int):
            self.disp.log_error(
                f"Failed to download image data from bucket '{FAV_CONST.FAVICON_BUCKET_NAME}' and path '{img_path}'"
            )
            return final_resp
        final_resp.img = bucket_resp
        final_resp.img_type = self.reducer_type_to_data_type(
            self.image_reducer.detect_file_format(final_resp.img)
        )
        self.disp.log_debug(
            f"Data gathered for table '{table}':\n{final_resp}"
        )
        return final_resp

    def register_gender(self, gender: str, *, title: str = "register_favicon_gender") -> int:
        """Register a new favicon gender into the genders table.

        Args:
            gender (str): The gender label to insert.
            title (str): Logging/response title. Defaults to "register_favicon_gender".

        Returns:
            int: `self.success` on success or an error code from the SQL layer.
        """
        table: str = FAV_CONST.FAVICON_TABLE_GENDER
        self.disp.log_debug(
            f"Registering new favicon gender '{gender}' into table '{table}'", title
        )
        column_clean = ["gender"]
        status = self.sql.insert_data_into_table(
            table=table,
            data=[gender],
            column=column_clean
        )
        if status != self.success:
            self.disp.log_error(
                f"Failed to register new favicon gender '{gender}' into table '{table}'", title
            )
            return status
        self.disp.log_debug(
            f"Registered new favicon gender '{gender}' into table '{table}' successfully", title
        )
        return self.success

    def register_season(self, season: str, parent_season: Optional[int] = None, *, title: str = "register_favicon_season") -> int:
        """Register a new favicon season, optionally with a parent season.

        Args:
            season (str): The season label to insert.
            parent_season (Optional[int]): Optional id of a parent season.
            title (str): Logging/response title. Defaults to "register_favicon_season".

        Returns:
            int: `self.success` on success or an error code from the SQL layer.
        """
        table: str = FAV_CONST.FAVICON_TABLE_SEASON
        self.disp.log_debug(
            f"Registering new favicon season '{season}' with parent '{parent_season}' into table '{table}'", title
        )
        column_clean = ["season"]
        data_clean: List[Union[str, int, float, None]] = [season]
        if isinstance(parent_season, int):
            data = self.get_favicon_season(parent_season)
            if not data or data.get("id") != parent_season or "season" not in data:
                self.disp.log_error(
                    f"Parent season id '{parent_season}' does not exist in table '{table}'", title
                )
                return self.error
            column_clean.append("parent_id")
            data_clean.append(parent_season)
        status = self.sql.insert_data_into_table(
            table=table,
            data=data_clean,
            column=column_clean
        )
        if status != self.success:
            self.disp.log_error(
                f"Failed to register new favicon season '{season}' into table '{table}'", title
            )
            return status
        self.disp.log_debug(
            f"Registered new favicon season '{season}' into table '{table}' successfully", title
        )
        return self.success

    def register_type(self, ftype: str, parent_type: Optional[int] = None, *, title: str = "register_favicon_type") -> int:
        """Register a new favicon type, optionally linked to a parent type.

        Args:
            ftype (str): The type name to insert.
            parent_type (Optional[int]): Optional id of a parent type.
            title (str): Logging/response title. Defaults to "register_favicon_type".

        Returns:
            int: `self.success` on success or an error code from the SQL layer.
        """
        table: str = FAV_CONST.FAVICON_TABLE_TYPE
        self.disp.log_debug(
            f"Registering new favicon type '{ftype}' with parent '{parent_type}' into table '{table}'", title
        )
        column_clean = ["name"]
        data_clean: List[Union[str, int, float, None]] = [ftype]
        if isinstance(parent_type, int):
            data = self.get_favicon_type(parent_type)
            if not data or data.get("id") != parent_type or "name" not in data:
                self.disp.log_error(
                    f"Parent season id '{parent_type}' does not exist in table '{table}'", title
                )
                return self.error
            column_clean.append("parent_id")
            data_clean.append(parent_type)
        status = self.sql.insert_data_into_table(
            table=table,
            data=data_clean,
            column=column_clean
        )
        if status != self.success:
            self.disp.log_error(
                f"Failed to register new favicon type '{ftype}' into table '{table}'", title
            )
            return status
        self.disp.log_debug(
            f"Registered new favicon type '{ftype}' into table '{table}' successfully", title
        )
        return self.success

    def register_icon(
        self,
        name: str,
        price: int = FAV_CONST.FAVICON_DEFAULT_PRICE,
        ftype: Optional[Union[int, str]] = None,
        gender: Optional[Union[int, str]] = None,
        season: Optional[Union[int, str]] = None,
        default_colour: Optional[str] = None,
        image_data: Optional[Union[bytes, UploadFile]] = None,
        source: Optional[str] = None,
        *, title: str = "register_icon"
    ) -> int:
        """Register a new favicon entry and optionally upload its image.

        Args:
            name (str): The display name for the favicon.
            price (int): The price associated with the favicon.
            ftype (Optional[Union[int, str]]): Type id or name to link.
            gender (Optional[Union[int, str]]): Gender id or name to link.
            season (Optional[Union[int, str]]): Season id or name to link.
            default_colour (Optional[str]): Hex colour string for default colour.
            image_data (Optional[Union[bytes, UploadFile]]): Optional image bytes to upload to the bucket.
            source (Optional[str]): Optional source metadata for the icon.
            title (str): Logging/response title.

        Returns:
            int: The id of the newly created favicon.

        Raises:
            FAV_ERR.FaviconDatabaseError: If inserting the favicon metadata or
                retrieving the new id from the database fails.
            FAV_ERR.FaviconNoImageReducerError: If an ImageReducer instance is not
                available in the runtime manager when `image_data` is provided.
            FAV_ERR.FaviconImageUploadError: If uploading image bytes to the
                configured bucket fails.
            FAV_ERR.FaviconImagePathUpdateError: If updating the database with
                the stored image path fails after upload.

        The function inserts the favicon metadata into the main table, resolves
        type/gender/season identifiers, and if `image_data` is provided it will
        upload the image to the configured bucket and update the database with
        the stored image path. Various filesystem/bucket/database errors are
        raised as specialized `FAV_ERR` exceptions or returned as error codes.
        """
        table: str = FAV_CONST.FAVICON_TABLE_MAIN
        self.disp.log_debug(
            f"Registering new favicon '{name}' into table '{table}'", title
        )
        column_clean = ["name", "price"]
        data_clean: List[Union[str, int, float, None]] = [name, price]
        ftype_id = self._process_favicon_type_id(ftype)
        if isinstance(ftype_id, int):
            column_clean.append("type")
            data_clean.append(ftype_id)
        gender_id = self._process_favicon_gender_id(gender)
        if isinstance(gender_id, int):
            column_clean.append("gender")
            data_clean.append(gender_id)
        season_id = self._process_favicon_season_id(season)
        if isinstance(season_id, int):
            column_clean.append("season")
            data_clean.append(season_id)
        if isinstance(default_colour, str) and FAV_HELPERS.is_hex_colour_valid(default_colour):
            padded_colour = FAV_HELPERS.pad_hex_colour(
                default_colour, with_alpha=True
            )
            column_clean.append("default_colour")
            data_clean.append(padded_colour)
        if isinstance(source, str):
            column_clean.append("source")
            data_clean.append(source)
        status = self.sql.insert_data_into_table(
            table=table,
            data=data_clean,
            column=column_clean
        )
        if status != self.success:
            self.disp.log_error(
                f"Failed to register new favicon '{name}' into table '{table}'", title
            )
            raise FAV_ERR.FaviconDatabaseError(
                "Failed to insert new favicon into database"
            )
        self.disp.log_debug(
            f"Registered new favicon '{name}' into table '{table}' successfully", title
        )
        icon_id = self.list_favicons()[-1].get("id")
        if not icon_id:
            self.disp.log_error(
                f"Failed to retrieve the id of the newly registered favicon '{name}'", title
            )
            raise FAV_ERR.FaviconDatabaseError(
                "Could not retrieve newly inserted favicon id"
            )
        self.disp.log_debug(f"New favicon id is '{icon_id}'", title)
        self.disp.log_debug(
            f"type(Image data) = '{type(image_data)}', image_data={image_data}", title
        )
        if isinstance(image_data, bytes):
            self.disp.log_debug("Uploading image from bytes...", title)
            img_path = self._upload_bytes(
                image_data,
                icon_id,
                title=f"{title}:_upload_bytes"
            )
        elif isinstance(image_data, (UploadFile, StarletteUploadFile)):
            self.disp.log_debug("Uploading image from UploadFile...", title)
            img_path = self._upload_file(
                image_data,
                icon_id,
                title=f"{title}:_upload_file"
            )
        else:
            self.disp.log_debug(
                f"Image data is of unsupported type '{type(image_data)}'; skipping upload.", title
            )
            self.disp.log_debug(
                "No image data provided; skipping upload.", title
            )
            return int(icon_id)
        update_status = self.sql.update_data_in_table(
            table=table,
            data=[img_path],
            column=["img_path"],
            where=f"id={icon_id}"
        )
        if update_status != self.success:
            self.disp.log_error(
                f"Failed to update favicon image path in table '{table}' for icon id '{icon_id}'", title
            )
            raise FAV_ERR.FaviconImagePathUpdateError(
                "Failed to update image path in database"
            )
        self.disp.log_debug(
            f"Uploaded favicon image data to bucket '{FAV_CONST.FAVICON_BUCKET_NAME}' at path '{img_path}' successfully", title
        )
        return int(icon_id)

    def register_icon_image(
        self,
        icon_id: int,
        image_data: Optional[Union[bytes, UploadFile]] = None,
        *, title: str = "register_icon"
    ) -> int:
        """Register a new favicon entry and optionally upload its image.

        Args:
            name (str): The display name for the favicon.
            price (int): The price associated with the favicon.
            ftype (Optional[Union[int, str]]): Type id or name to link.
            gender (Optional[Union[int, str]]): Gender id or name to link.
            season (Optional[Union[int, str]]): Season id or name to link.
            default_colour (Optional[str]): Hex colour string for default colour.
            image_data (Optional[Union[bytes, UploadFile]]): Optional image bytes to upload to the bucket.
            source (Optional[str]): Optional source metadata for the icon.
            title (str): Logging/response title.

        Returns:
            int: The id of the newly created favicon.

        Raises:
            FAV_ERR.FaviconDatabaseError: If inserting the favicon metadata or
                retrieving the new id from the database fails.
            FAV_ERR.FaviconNoImageReducerError: If an ImageReducer instance is not
                available in the runtime manager when `image_data` is provided.
            FAV_ERR.FaviconImageUploadError: If uploading image bytes to the
                configured bucket fails.
            FAV_ERR.FaviconImagePathUpdateError: If updating the database with
                the stored image path fails after upload.

        The function inserts the favicon metadata into the main table, resolves
        type/gender/season identifiers, and if `image_data` is provided it will
        upload the image to the configured bucket and update the database with
        the stored image path. Various filesystem/bucket/database errors are
        raised as specialized `FAV_ERR` exceptions or returned as error codes.
        """
        table: str = FAV_CONST.FAVICON_TABLE_MAIN
        self.disp.log_debug(
            f"Registering new favicon image '{icon_id}' into table '{table}'", title
        )
        self.disp.log_debug(
            f"type(Image data) = '{type(image_data)}', image_data={image_data}", title
        )
        if isinstance(image_data, bytes):
            self.disp.log_debug("Uploading image from bytes...", title)
            img_path = self._upload_bytes(
                image_data,
                icon_id,
                title=f"{title}:_upload_bytes"
            )
        elif isinstance(image_data, (UploadFile, StarletteUploadFile)):
            self.disp.log_debug("Uploading image from UploadFile...", title)
            img_path = self._upload_file(
                image_data,
                icon_id,
                title=f"{title}:_upload_file"
            )
        else:
            self.disp.log_debug(
                f"Image data is of unsupported type '{type(image_data)}'; skipping upload.", title
            )
            self.disp.log_debug(
                "No image data provided; skipping upload.", title
            )
            return int(icon_id)
        update_status = self.sql.update_data_in_table(
            table=table,
            data=[img_path],
            column=["img_path"],
            where=f"id={icon_id}"
        )
        if update_status != self.success:
            self.disp.log_error(
                f"Failed to update favicon image path in table '{table}' for icon id '{icon_id}'", title
            )
            raise FAV_ERR.FaviconImagePathUpdateError(
                "Failed to update image path in database"
            )
        self.disp.log_debug(
            f"Uploaded favicon image data to bucket '{FAV_CONST.FAVICON_BUCKET_NAME}' at path '{img_path}' successfully", title
        )
        return int(icon_id)
