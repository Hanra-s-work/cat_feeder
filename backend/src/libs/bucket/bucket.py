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
# FILE: bucket.py
# CREATION DATE: 11-10-2025
# LAST Modified: 17:56:8 09-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of providing a boiled down interface for interracting with an s3 bucket.
# // AR
# +==== END CatFeeder =================+
"""

from __future__ import annotations

from typing import List, Union, Dict, Any, Optional,  cast
import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from display_tty import Disp, initialise_logger
from .bucket_class_aliases import S3ObjectLike,  S3BucketLike,  S3ServiceResourceLike
from . import bucket_constants as CONST
from ..core import FinalClass


class Bucket(metaclass=FinalClass):
    """
    Class to manage interaction with an S3-compatible bucket like MinIO.

    Attributes:
        disp (Disp): Logger instance for debugging and error reporting.
        connection (Optional[S3ServiceResourceLike]): Active S3 connection resource.
        debug (bool): Debug mode flag.
        success (int): Numeric success code.
        error (int): Numeric error code.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    # --- Instance tracker to avoid creating unnecessary duplicate instances ---
    _initialization_attempted: bool = False
    _initialization_failed: bool = False

    def __init__(self, error: int = 84, success: int = 0, auto_connect: bool = True, debug: bool = False) -> None:
        """Initialize the Bucket instance.

        Args:
            error (int, optional): Numeric error code. Defaults to 84.
            success (int, optional): Numeric success code. Defaults to 0.
            auto_connect (bool, optional): If True, automatically connect to S3. Defaults to True.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.debug: bool = debug
        self.error: int = error
        self.success: int = success
        # ----------------------- The connector address  -----------------------
        # boto3 S3 resource when connected
        self.connection: Optional[S3ServiceResourceLike] = None
        self._is_connected: bool = False

        # Auto-connect if requested (for RuntimeManager compatibility)
        if auto_connect:
            self._auto_connect()

        self.disp.log_debug("Initialised")

    def _auto_connect(self) -> None:
        """Automatically connect to S3 service.

        Called during __init__ when auto_connect=True.
        Tracks connection attempts to provide better error messages.
        """
        Bucket._initialization_attempted = True
        try:
            if self.connect() != self.success:
                Bucket._initialization_failed = True
                msg = "Failed to connect to S3/MinIO service."
                self.disp.log_error(msg)
                # Don't raise here - allow the instance to exist but mark as failed
            else:
                self._is_connected = True
        except (BotoCoreError, ClientError, ConnectionError, RuntimeError) as e:
            Bucket._initialization_failed = True
            self.disp.log_error(f"Connection failed: {e}")
            # Don't raise here - allow graceful degradation

    def __del__(self) -> None:
        """Best-effort cleanup invoked when the instance is garbage-collected.

        This releases the S3 connection resource.
        """
        if self.connection is not None:
            try:
                self.disconnect()
            except (BotoCoreError, ClientError, ConnectionError, RuntimeError, AttributeError):
                pass  # Suppress errors in destructor
            self.connection = None

    def _ensure_connected(self) -> None:
        """Ensure the Bucket instance is connected to S3.

        If connection was never attempted, try to auto-connect.
        If connection was attempted but failed, try to reconnect once.

        Raises:
            RuntimeError: If connection has failed and cannot be re-established.
        """
        if self._is_connected and self.is_connected():
            return

        if not Bucket._initialization_attempted:
            self.disp.log_debug(
                "Attempting lazy connection", "_ensure_connected")
            self._auto_connect()
        elif not self._is_connected:
            # Try to reconnect once
            self.disp.log_debug("Attempting to reconnect", "_ensure_connected")
            if self.connect() == self.success:
                self._is_connected = True
                Bucket._initialization_failed = False
            else:
                raise RuntimeError(
                    "Bucket connection failed. Cannot perform operations without active S3 connection."
                )

    def connect(self) -> int:
        """
        Connect to the S3-compatible service (MinIO, Cellar, AWS S3, etc.).

        Returns:
            int: success or error code.
        """
        try:
            # Build endpoint URL - ensure it includes protocol scheme
            endpoint_url = CONST.BUCKET_HOST

            # Add protocol if not present
            if not endpoint_url.startswith(('http://', 'https://')):
                endpoint_url = f"http://{endpoint_url}"

            # Add port only if specified
            if CONST.BUCKET_PORT:
                endpoint_url = f"{endpoint_url}:{CONST.BUCKET_PORT}"

            # Create S3 service resource
            resource = boto3.resource(
                CONST.BUCKET_RESSOURCE_TYPE,
                endpoint_url=endpoint_url,
                aws_access_key_id=CONST.BUCKET_USER,
                aws_secret_access_key=CONST.BUCKET_PASSWORD,
                config=Config(signature_version=CONST.BUCKET_SIGNATURE_VERSION)
            )
            self.connection = cast(S3ServiceResourceLike, resource)
            # Check connection by listing buckets
            conn = self.connection
            assert conn is not None
            conn.meta.client.list_buckets()
            self.disp.log_info(
                "Connection to S3-compatible service successful.")
            return self.success
        except (BotoCoreError, ClientError) as e:
            self.disp.log_error(
                f"Failed to connect to S3-compatible service: {str(e)}"
            )
            return self.error

    def is_connected(self) -> bool:
        """
        Check if the connection to the S3-compatible service is active.

        Returns:
            bool: True if connected, False otherwise.
        """
        if self.connection is None:
            self.disp.log_error("No connection object found.")
            return False

        try:
            # Attempt to list buckets as a simple test of the connection
            self.connection.meta.client.list_buckets()
            self.disp.log_info("Connection is active.")
            return True
        except (BotoCoreError, ClientError, ConnectionError) as e:
            self.disp.log_error(
                f"Connection check failed: {str(e)}"
            )
            return False

    def disconnect(self) -> int:
        """
        Disconnect from the S3-compatible service by setting the connection to None.

        Returns:
            int: success or error code.
        """
        if self.connection is None:
            self.disp.log_warning(
                "No active connection to disconnect."
            )
            return self.error

        # Setting to None is safe and should not raise; log and return success
        self.connection = None
        self.disp.log_info(
            "Disconnected from the S3-compatible service."
        )
        return self.success

    def get_bucket_names(self) -> Union[List[str], int]:
        """
        Retrieve a list of all bucket names.

        Returns:
            Union[List[str], int]: A list of bucket names or error code.
        """
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            buckets = [bucket.name for bucket in self.connection.buckets.all()]
            return buckets
        except (BotoCoreError, ClientError, ConnectionError) as e:
            self.disp.log_error(
                f"Error fetching bucket names: {str(e)}"
            )
            return self.error

    def create_bucket(self, bucket_name: str) -> int:
        """
        Create a new bucket.

        Args:
            bucket_name (str): Name of the bucket to create.

        Returns:
            int: success or error code.
        """
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            self.connection.create_bucket(Bucket=bucket_name)
            self.disp.log_info(
                f"Bucket '{bucket_name}' created successfully."
            )
            return self.success
        except (BotoCoreError, ClientError, ConnectionError) as e:
            self.disp.log_error(
                f"Failed to create bucket '{bucket_name}': {str(e)}"
            )
            return self.error

    def upload_file(self, bucket_name: str, file_path: str, key_name: Optional[str] = None) -> int:
        """
        Upload a file to the specified bucket.

        Args:
            bucket_name (str): Name of the target bucket.
            file_path (str): Path of the file to upload.
            key_name (Optional[str]): Name to save the file as in the bucket. Defaults to the file path name.

        Returns:
            int: success or error code.
        """
        key_name = key_name or file_path
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            bucket: S3BucketLike = self.connection.Bucket(
                bucket_name)  # type: ignore[assignment]
            bucket.upload_file(file_path, key_name)
            msg = f"File '{file_path}' uploaded to bucket "
            msg += f"'{bucket_name}' as '{key_name}'."
            self.disp.log_info(msg)
            return self.success
        except (BotoCoreError, ClientError, ConnectionError) as e:
            msg = f"Failed to upload file '{file_path}' to bucket "
            msg += f"'{bucket_name}': {str(e)}"
            self.disp.log_error(msg)
            return self.error

    def upload_stream(self, bucket_name: str, data: bytes, key_name: Optional[str] = None) -> int:
        """Upload a file to the specified bucket from a byte stream.

        Args:
            bucket_name (str): Name of the target bucket.
            data (bytes): The file content as bytes.
            key_name (Optional[str]): Name to save the file as in the bucket. Defaults to a generated name if not provided.

        Returns:
            int: success or error code.
        """
        if key_name is None:
            self.disp.log_error(
                "key_name must be provided for stream uploads")
            return self.error
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            bucket: S3BucketLike = self.connection.Bucket(
                bucket_name)  # type: ignore[assignment]
            bucket.put_object(Key=key_name, Body=data)
            msg = f"File stream uploaded to bucket '{bucket_name}' as '{key_name}' ({len(data)} bytes)."
            self.disp.log_info(msg)
            return self.success
        except (BotoCoreError, ClientError, ConnectionError, RuntimeError) as e:
            msg = f"Failed to upload file stream to bucket '{bucket_name}' as '{key_name}': {str(e)}"
            self.disp.log_error(msg)
            return self.error

    def download_file(self, bucket_name: str, key_name: str, destination_path: Optional[str] = None) -> int:
        """
        Download a file from the specified bucket.

        Args:
            bucket_name (str): Name of the target bucket.
            key_name (str): Name of the file to download.
            destination_path (Optional[str]): Local path where the file will be saved. Defaults to the key_name if not provided.

        Returns:
            int: success or error code.
        """
        destination_path = destination_path or key_name
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            bucket: S3BucketLike = self.connection.Bucket(
                bucket_name)  # type: ignore[assignment]
            bucket.download_file(key_name, destination_path)
            msg = f"File '{key_name}' downloaded from bucket "
            msg += f"'{bucket_name}' to '{destination_path}'."
            self.disp.log_info(msg)
            return self.success
        except (BotoCoreError, ClientError, ConnectionError) as e:
            msg = f"Failed to download file '{key_name}'"
            msg += f" from bucket '{bucket_name}': {str(e)}"
            self.disp.log_error(msg)
            return self.error

    def download_stream(self, bucket_name: str, key_name: str) -> Union[bytes, int]:
        """Download a file from the specified bucket and return it as a byte stream.

        Args:
            bucket_name (str): Name of the target bucket.
            key_name (str): Name of the file to download.

        Returns:
            Union[bytes, int]: File content as bytes or error code.
        """
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            bucket: S3BucketLike = self.connection.Bucket(
                bucket_name)  # type: ignore[assignment]
            obj: S3ObjectLike = bucket.Object(
                key_name)  # type: ignore[assignment]
            file_data = obj.get()['Body'].read()
            msg = f"File '{key_name}' downloaded from bucket "
            msg += f"'{bucket_name}' as stream ({len(file_data)} bytes)."
            self.disp.log_info(msg)
            return file_data
        except (BotoCoreError, ClientError, ConnectionError, RuntimeError) as e:
            msg = f"Failed to download file '{key_name}' from bucket "
            msg += f"'{bucket_name}' as stream: {str(e)}"
            self.disp.log_error(msg)
            return self.error

    def delete_file(self, bucket_name: str, key_name: str) -> int:
        """
        Delete a file from the specified bucket.

        Args:
            bucket_name (str): Name of the bucket.
            key_name (str): Name of the file to delete.

        Returns:
            int: success or error code.
        """
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            bucket: S3BucketLike = self.connection.Bucket(
                bucket_name)  # type: ignore[assignment]
            bucket.Object(key_name).delete()
            self.disp.log_info(
                f"File '{key_name}' deleted from bucket '{bucket_name}'."
            )
            return self.success
        except (BotoCoreError, ClientError, ConnectionError) as e:
            msg = f"Failed to delete file '{key_name}' from bucket "
            msg += f"'{bucket_name}': {str(e)}"
            self.disp.log_error(msg)
            return self.error

    def delete_bucket(self, bucket_name: str) -> int:
        """
        Delete a bucket.

        Args:
            bucket_name (str): Name of the bucket to delete.

        Returns:
            int: success or error code.
        """
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            bucket: S3BucketLike = self.connection.Bucket(
                bucket_name)  # type: ignore[assignment]
            bucket.delete()
            self.disp.log_info(
                f"Bucket '{bucket_name}' deleted successfully."
            )
            return self.success
        except (BotoCoreError, ClientError, ConnectionError) as e:
            self.disp.log_error(
                f"Failed to delete bucket '{bucket_name}': {str(e)}"
            )
            return self.error

    def get_bucket_files(self, bucket_name: str) -> Union[List[str], int]:
        """
        List all files in the specified bucket.

        Args:
            bucket_name (str): Name of the bucket.

        Returns:
            Union[List[str], int]: List of file names or error code.
        """
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            files: List[str] = []
            bucket: S3BucketLike = self.connection.Bucket(
                bucket_name)  # type: ignore[assignment]
            for obj in bucket.objects.all():
                files.append(obj.key)
            return files
        except (BotoCoreError, ClientError, ConnectionError) as e:
            msg = f"Failed to retrieve files from bucket '{bucket_name}'"
            msg += f": {str(e)}"
            self.disp.log_error(msg)
            return self.error

    def get_bucket_file(self, bucket_name: str, key_name: str) -> Union[Dict[str, Any], int]:
        """
        Get information about a specific file in the bucket.

        Args:
            bucket_name (str): Name of the bucket.
            key_name (str): Name of the file.

        Returns:
            Union[Dict[str, Any], int]: File metadata (path and size) or error code.
        """
        try:
            self._ensure_connected()
            if self.connection is None:
                raise ConnectionError("No connection established.")
            bucket: S3BucketLike = self.connection.Bucket(
                bucket_name)  # type: ignore[assignment]
            obj: S3ObjectLike = bucket.Object(
                key_name)  # type: ignore[assignment]
            return {'file_path': key_name, 'file_size': obj.content_length}
        except (BotoCoreError, ClientError, ConnectionError, RuntimeError) as e:
            msg = f"Failed to get file '{key_name}' "
            msg += f"from bucket '{bucket_name}': {str(e)}"
            self.disp.log_error(msg)
            return self.error
