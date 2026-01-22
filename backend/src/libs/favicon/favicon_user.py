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
# FILE: favicon_user.py
# CREATION DATE: 05-01-2026
# LAST Modified: 11:55:14 12-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the class for handling user favicons.
# // AR
# +==== END CatFeeder =================+
"""

from typing import TYPE_CHECKING, Optional, List, Union, Dict, Any

from fastapi import Response
from display_tty import Disp, initialise_logger

from . import favicon_constants as FAV_CONST
from . import favicon_helpers as FAV_HELPERS
from . import favicon_error_class as FAV_ERR

from ..utils import CONST
from ..core import FinalSingleton
from ..http_codes import HCI, HttpDataTypes
from ..core.runtime_manager import RI, RuntimeManager
from ..image_reducer import IR_ERROR, FileFormat

if TYPE_CHECKING:
    from ..sql import SQL
    from ..bucket import Bucket
    from ..image_reducer import ImageReducer
    from ..server_header import ServerHeaders
    from ..boilerplates.responses import BoilerplateResponses


class FaviconUser(FinalSingleton):

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
        self.disp.log_error("There is no specified user id.")
        return self.boilerplate_response.user_not_found(title, token)

    def _no_data(self, title: str, token: Optional[str] = None) -> Response:
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

    def reducer_type_to_data_type(self, reducer_type: FileFormat) -> HttpDataTypes:
        """(This is a wrapper of the same function in the constants)
        Convert an ImageReducer FileFormat to an HttpDataTypes value.

        Args:
            reducer_type (IR_CONST.FileFormat): The image reducer file format.

        Returns:
            HttpDataTypes: The corresponding HTTP data type.
        """
        return FAV_CONST.reducer_type_to_data_type(reducer_type)

    def list_user_favicons(self, user_id: Optional[int] = None, *, title: str = "list_user_favicon", token: Optional[str] = None) -> Union[List[Dict[str, Any]], Response]:
        table: str = FAV_CONST.FAVICON_USER_OWNED_TABLE
        if user_id is None:
            self.disp.log_error(
                "There is no specified user to search for, returning []"
            )
            return self._no_user_id(title, token)
        self.disp.log_debug(
            f"Gathering the list of uploaded user icons from table '{table}' and user id='{user_id}'"
        )
        resp = self.sql.get_data_from_table(
            table=table,
            column="*",
            where=f"user_id={user_id}"
        )
        if isinstance(resp, int):
            self.disp.log_error(
                f"Failed to gather data for table '{table}' and user id='{user_id}'"
            )
            return self._no_data(title, token)
        self.disp.log_debug(
            f"Data gathered for table '{table}' and user id='{user_id}':\n{resp}"
        )
        return resp

    def list_active_user_favicons(self, user_id: Optional[int] = None, *, title: str = "list_active_user_favicon", token: Optional[str] = None) -> Union[List[Dict[str, Any]], Response]:
        table: str = FAV_CONST.FAVICON_USER_ACTIVE_TABLE
        if user_id is None:
            self.disp.log_error(
                "There is no specified user to search for, returning []"
            )
            return self._no_user_id(title, token)
        self.disp.log_debug(
            f"Gathering the list of uploaded user icons from table '{table}' and user id='{user_id}'"
        )
        resp = self.sql.get_data_from_table(
            table=table,
            column="*",
            where=f"user_id={user_id}"
        )
        if isinstance(resp, int):
            self.disp.log_error(
                f"Failed to gather data for table '{table}' and user id='{user_id}'"
            )
            return self._no_data(title, token)
        self.disp.log_debug(
            f"Data gathered for table '{table}' and user id='{user_id}':\n{resp}"
        )
        return resp

    def get_user_favicon(self, user_id, favicon_id, *, title: str = "list_user_favicon", token: Optional[str] = None) -> Union[FAV_CONST.FaviconData, Response]:
        table: str = FAV_CONST.FAVICON_USER_ACTIVE_TABLE
        final_resp: FAV_CONST.FaviconData = FAV_CONST.FaviconData()
        if user_id is None:
            self.disp.log_error(
                "There is no specified user to search for"
            )
            return self._no_user_id(title, token)
        self.disp.log_debug(
            f"Gathering the list of uploaded user icons from table '{table}' and user id='{user_id}'"
        )
        sql_resp = self.sql.get_data_from_table(
            table=table,
            column="*",
            where=[f"user_id={user_id}", f"icon_id={favicon_id}"]
        )
        if isinstance(sql_resp, int):
            self.disp.log_error(
                f"Failed to gather data for table '{table}' and user id='{user_id}'"
            )
            return self._no_data(title, token)
        if len(sql_resp) == 0:
            return final_resp
        sql_raw_data = self.sql.get_data_from_table(
            table=FAV_CONST.FAVICON_TABLE_MAIN,
            column="*",
            where=f"id={favicon_id}"
        )
        if isinstance(sql_raw_data, int):
            self.disp.log_error(
                f"Failed to gather raw data for table '{FAV_CONST.FAVICON_TABLE_MAIN}' and icon id='{favicon_id}'"
            )
            return self._no_data(title, token)
        if len(sql_raw_data) == 0:
            return final_resp
        final_resp.data = CONST.clean_dict(
            sql_raw_data[0].copy(),
            (FAV_CONST.FAVICON_IMAGE_PATH_KEY, ""),
            self.disp
        )
        if sql_raw_data[0][FAV_CONST.FAVICON_IMAGE_PATH_KEY] is None or sql_raw_data[0][FAV_CONST.FAVICON_IMAGE_PATH_KEY] == "":
            self.disp.log_error(
                f"There is no image path for icon id='{favicon_id}'"
            )
            return final_resp
        img_path = sql_raw_data[0][FAV_CONST.FAVICON_IMAGE_PATH_KEY]
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
        self.image_reducer = self.runtime_manager.get_if_exists(
            "ImageReducer", self.image_reducer)
        if self.image_reducer is None:
            self.disp.log_error(
                "There is no ImageReducer instance available in the runtime manager"
            )
            return final_resp
        final_resp.img_type = self.reducer_type_to_data_type(
            self.image_reducer.detect_file_format(final_resp.img)
        )
        self.disp.log_debug(
            f"Data gathered for table '{table}' and user id='{user_id}':\n{final_resp}"
        )
        return final_resp
