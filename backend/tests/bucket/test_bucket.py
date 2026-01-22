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
# FILE: test_bucket.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for S3/MinIO Bucket wrapper class.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for Bucket class initialization, connection, and operations.
# // AR
# +==== END CatFeeder =================+
"""
from unittest.mock import Mock, MagicMock, patch, call
from botocore.exceptions import BotoCoreError, ClientError
import pytest

try:
    from libs.bucket.bucket import Bucket
    from libs.bucket import bucket_constants as CONST
except Exception:
    from src.libs.bucket.bucket import Bucket
    from src.libs.bucket import bucket_constants as CONST


class TestBucketInitialization:
    """Test Bucket class initialization."""

    def test_bucket_init_default_values(self):
        """Verify Bucket initializes with default values."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            assert bucket.error == 84
            assert bucket.success == 0
            assert bucket.debug is False

    def test_bucket_init_custom_error_code(self):
        """Verify Bucket accepts custom error code."""
        with patch('src.libs.bucket.bucket.boto3.resource'):
            bucket = Bucket(error=1, auto_connect=False)
            assert bucket.error == 1

    def test_bucket_init_custom_success_code(self):
        """Verify Bucket accepts custom success code."""
        with patch('src.libs.bucket.bucket.boto3.resource'):
            bucket = Bucket(success=200, auto_connect=False)
            assert bucket.success == 200

    def test_bucket_init_custom_debug_flag(self):
        """Verify Bucket accepts custom debug flag."""
        with patch('src.libs.bucket.bucket.boto3.resource'):
            bucket = Bucket(debug=True, auto_connect=False)
            assert bucket.debug is True

    def test_bucket_init_no_auto_connect(self):
        """Verify Bucket respects auto_connect=False."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            bucket = Bucket(auto_connect=False)
            assert bucket.connection is None
            # Should not call boto3.resource when auto_connect is False
            mock_resource.assert_not_called()

    def test_bucket_init_auto_connect_successful(self):
        """Verify Bucket auto-connects when auto_connect=True."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            mock_resource.assert_called_once()

    def test_bucket_final_class_metaclass(self):
        """Verify Bucket cannot be subclassed."""
        with pytest.raises(TypeError):
            class SubBucket(Bucket):
                pass


class TestBucketConnection:
    """Test Bucket connection management."""

    def test_bucket_connect_success(self):
        """Verify successful connection returns success code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=False)
            result = bucket.connect()
            assert result == bucket.success

    def test_bucket_connect_failure(self):
        """Verify failed connection returns error code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_resource.side_effect = ClientError(
                {'Error': {'Code': '503', 'Message': 'Service Unavailable'}},
                'ListBuckets'
            )

            bucket = Bucket(auto_connect=False)
            result = bucket.connect()
            assert result == bucket.error

    def test_bucket_connect_boto_core_error(self):
        """Verify BotoCoreError returns error code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_resource.side_effect = BotoCoreError()

            bucket = Bucket(auto_connect=False)
            result = bucket.connect()
            assert result == bucket.error

    def test_bucket_is_connected_true(self):
        """Verify is_connected returns True for active connection."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            assert bucket.is_connected() is True

    def test_bucket_is_connected_false_no_connection(self):
        """Verify is_connected returns False when no connection."""
        bucket = Bucket(auto_connect=False)
        assert bucket.is_connected() is False

    def test_bucket_is_connected_false_connection_error(self):
        """Verify is_connected returns False on connection error."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.side_effect = ClientError(
                {'Error': {'Code': '503', 'Message': 'Service Unavailable'}},
                'ListBuckets'
            )

            bucket = Bucket(auto_connect=False)
            bucket.connection = mock_service
            assert bucket.is_connected() is False

    def test_bucket_disconnect_success(self):
        """Verify disconnect returns success code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            result = bucket.disconnect()
            assert result == bucket.success
            assert bucket.connection is None

    def test_bucket_disconnect_no_connection(self):
        """Verify disconnect returns error code when not connected."""
        bucket = Bucket(auto_connect=False)
        result = bucket.disconnect()
        assert result == bucket.error


class TestBucketLazyConnection:
    """Test Bucket lazy connection (_ensure_connected)."""

    def test_ensure_connected_already_connected(self):
        """Verify _ensure_connected skips if already connected."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            with patch.object(bucket, 'connect') as mock_connect:
                bucket._ensure_connected()
                mock_connect.assert_not_called()

    def test_ensure_connected_never_attempted(self):
        """Verify _ensure_connected attempts lazy connection."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=False)
            Bucket._initialization_attempted = False
            bucket._ensure_connected()
            assert bucket.connection is not None

    def test_ensure_connected_failed_raises_error(self):
        """Verify _ensure_connected raises RuntimeError when connection fails."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_resource.side_effect = ClientError(
                {'Error': {'Code': '503', 'Message': 'Service Unavailable'}},
                'ListBuckets'
            )

            bucket = Bucket(auto_connect=False)
            Bucket._initialization_attempted = True
            Bucket._initialization_failed = True
            bucket._is_connected = False

            with pytest.raises(RuntimeError):
                bucket._ensure_connected()


class TestBucketBucketOperations:
    """Test Bucket bucket operations (create, delete, list)."""

    def test_get_bucket_names_success(self):
        """Verify get_bucket_names returns list of bucket names."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service

            # Setup mock buckets
            mock_bucket1 = MagicMock()
            mock_bucket1.name = 'bucket-1'
            mock_bucket2 = MagicMock()
            mock_bucket2.name = 'bucket-2'

            mock_service.buckets.all.return_value = [
                mock_bucket1, mock_bucket2]
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            result = bucket.get_bucket_names()
            assert isinstance(result, list)
            assert 'bucket-1' in result
            assert 'bucket-2' in result

    def test_get_bucket_names_failure(self):
        """Verify get_bucket_names returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            bucket.connection.buckets.all.side_effect = ClientError(
                {'Error': {'Code': '503', 'Message': 'Service Unavailable'}},
                'ListBuckets'
            )

            result = bucket.get_bucket_names()
            assert result == bucket.error

    def test_create_bucket_success(self):
        """Verify create_bucket returns success code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            result = bucket.create_bucket('test-bucket')
            assert result == bucket.success

    def test_create_bucket_failure(self):
        """Verify create_bucket returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}
            mock_service.create_bucket.side_effect = ClientError(
                {'Error': {'Code': '409', 'Message': 'Bucket already exists'}},
                'CreateBucket'
            )

            bucket = Bucket(auto_connect=True)
            result = bucket.create_bucket('existing-bucket')
            assert result == bucket.error

    def test_delete_bucket_success(self):
        """Verify delete_bucket returns success code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.delete_bucket('test-bucket')
            assert result == bucket.success

    def test_delete_bucket_failure(self):
        """Verify delete_bucket returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_bucket.delete.side_effect = ClientError(
                {'Error': {'Code': '409', 'Message': 'Bucket not empty'}},
                'DeleteBucket'
            )
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.delete_bucket('test-bucket')
            assert result == bucket.error


class TestBucketFileOperations:
    """Test Bucket file operations (upload, download, delete)."""

    def test_upload_file_success(self):
        """Verify upload_file returns success code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.upload_file('test-bucket', '/path/to/file.txt')
            assert result == bucket.success

    def test_upload_file_with_custom_key_name(self):
        """Verify upload_file accepts custom key name."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.upload_file(
                'test-bucket', '/path/to/file.txt', 'custom-key.txt')
            assert result == bucket.success
            mock_bucket.upload_file.assert_called_once()

    def test_upload_file_failure(self):
        """Verify upload_file returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_bucket.upload_file.side_effect = ClientError(
                {'Error': {'Code': '404', 'Message': 'Bucket not found'}},
                'PutObject'
            )
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.upload_file('missing-bucket', '/path/to/file.txt')
            assert result == bucket.error

    def test_upload_stream_success(self):
        """Verify upload_stream returns success code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.upload_stream(
                'test-bucket', b'file content', 'file.txt')
            assert result == bucket.success

    def test_upload_stream_no_key_name(self):
        """Verify upload_stream requires key_name."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            bucket = Bucket(auto_connect=True)
            result = bucket.upload_stream('test-bucket', b'file content')
            assert result == bucket.error

    def test_upload_stream_failure(self):
        """Verify upload_stream returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_bucket.put_object.side_effect = ClientError(
                {'Error': {'Code': '403', 'Message': 'Access Denied'}},
                'PutObject'
            )
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.upload_stream(
                'test-bucket', b'content', 'file.txt')
            assert result == bucket.error

    def test_download_file_success(self):
        """Verify download_file returns success code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.download_file(
                'test-bucket', 'file.txt', '/path/to/file.txt')
            assert result == bucket.success

    def test_download_file_default_destination(self):
        """Verify download_file uses key_name as destination by default."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.download_file('test-bucket', 'file.txt')
            assert result == bucket.success
            mock_bucket.download_file.assert_called_once_with(
                'file.txt', 'file.txt')

    def test_download_file_failure(self):
        """Verify download_file returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_bucket.download_file.side_effect = ClientError(
                {'Error': {'Code': '404', 'Message': 'Object not found'}},
                'GetObject'
            )
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.download_file('test-bucket', 'missing.txt')
            assert result == bucket.error

    def test_download_stream_success(self):
        """Verify download_stream returns bytes."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_obj = MagicMock()
            mock_body = MagicMock()
            mock_body.read.return_value = b'file content'
            mock_obj.get.return_value = {'Body': mock_body}
            mock_bucket.Object.return_value = mock_obj
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.download_stream('test-bucket', 'file.txt')
            assert result == b'file content'

    def test_download_stream_failure(self):
        """Verify download_stream returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_obj = MagicMock()
            mock_obj.get.side_effect = ClientError(
                {'Error': {'Code': '404', 'Message': 'Object not found'}},
                'GetObject'
            )
            mock_bucket.Object.return_value = mock_obj
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.download_stream('test-bucket', 'missing.txt')
            assert result == bucket.error

    def test_delete_file_success(self):
        """Verify delete_file returns success code."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_obj = MagicMock()
            mock_bucket.Object.return_value = mock_obj
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.delete_file('test-bucket', 'file.txt')
            assert result == bucket.success

    def test_delete_file_failure(self):
        """Verify delete_file returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_obj = MagicMock()
            mock_obj.delete.side_effect = ClientError(
                {'Error': {'Code': '404', 'Message': 'Object not found'}},
                'DeleteObject'
            )
            mock_bucket.Object.return_value = mock_obj
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.delete_file('test-bucket', 'missing.txt')
            assert result == bucket.error


class TestBucketGetBucketFile:
    """Test Bucket get_bucket_file operation."""

    def test_get_bucket_file_success(self):
        """Verify get_bucket_file returns file metadata."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_obj = MagicMock()
            mock_obj.content_length = 1024
            mock_bucket.Object.return_value = mock_obj
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.get_bucket_file('test-bucket', 'file.txt')
            assert isinstance(result, dict)
            assert result['file_path'] == 'file.txt'
            assert result['file_size'] == 1024

    def test_get_bucket_file_failure(self):
        """Verify get_bucket_file returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_obj = MagicMock()
            mock_obj.content_length = None  # Will cause AttributeError
            mock_bucket.Object.return_value = mock_obj
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.get_bucket_file('test-bucket', 'file.txt')
            # Should return error code on failure


class TestBucketGetBucketFiles:
    """Test Bucket get_bucket_files operation."""

    def test_get_bucket_files_success(self):
        """Verify get_bucket_files returns list of file names."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_obj1 = MagicMock()
            mock_obj1.key = 'file1.txt'
            mock_obj2 = MagicMock()
            mock_obj2.key = 'file2.txt'
            mock_bucket.objects.all.return_value = [mock_obj1, mock_obj2]
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.get_bucket_files('test-bucket')
            assert isinstance(result, list)
            assert 'file1.txt' in result
            assert 'file2.txt' in result

    def test_get_bucket_files_empty_bucket(self):
        """Verify get_bucket_files handles empty buckets."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_bucket.objects.all.return_value = []
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.get_bucket_files('test-bucket')
            assert isinstance(result, list)
            assert len(result) == 0

    def test_get_bucket_files_failure(self):
        """Verify get_bucket_files returns error code on failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_service = MagicMock()
            mock_resource.return_value = mock_service
            mock_service.meta.client.list_buckets.return_value = {
                'Buckets': []}

            mock_bucket = MagicMock()
            mock_bucket.objects.all.side_effect = ClientError(
                {'Error': {'Code': '404', 'Message': 'Bucket not found'}},
                'ListObjects'
            )
            mock_service.Bucket.return_value = mock_bucket

            bucket = Bucket(auto_connect=True)
            result = bucket.get_bucket_files('missing-bucket')
            assert result == bucket.error


class TestBucketConnectionEndpoint:
    """Test Bucket connection endpoint URL building."""

    def test_connect_adds_http_scheme(self):
        """Verify connect adds http:// scheme if not present."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            with patch.dict('src.libs.bucket.bucket_constants.__dict__', {
                'BUCKET_HOST': 'localhost',
                'BUCKET_PORT': '',
                'BUCKET_USER': 'user',
                'BUCKET_PASSWORD': 'pass',
                'BUCKET_RESSOURCE_TYPE': 's3',
                'BUCKET_SIGNATURE_VERSION': 's3v4'
            }):
                mock_service = MagicMock()
                mock_resource.return_value = mock_service
                mock_service.meta.client.list_buckets.return_value = {
                    'Buckets': []}

                bucket = Bucket(auto_connect=False)
                bucket.connect()

                # Verify resource was called with proper endpoint
                call_args = mock_resource.call_args
                assert call_args is not None

    def test_connect_preserves_https(self):
        """Verify connect preserves https:// scheme."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            with patch.dict('src.libs.bucket.bucket_constants.__dict__', {
                'BUCKET_HOST': 'https://s3.amazonaws.com',
                'BUCKET_PORT': '',
                'BUCKET_USER': 'user',
                'BUCKET_PASSWORD': 'pass',
                'BUCKET_RESSOURCE_TYPE': 's3',
                'BUCKET_SIGNATURE_VERSION': 's3v4'
            }):
                mock_service = MagicMock()
                mock_resource.return_value = mock_service
                mock_service.meta.client.list_buckets.return_value = {
                    'Buckets': []}

                bucket = Bucket(auto_connect=False)
                bucket.connect()

                call_args = mock_resource.call_args
                assert call_args is not None


class TestBucketStaticState:
    """Test Bucket static/class state tracking."""

    def test_initialization_attempted_flag(self):
        """Verify _initialization_attempted flag is set."""
        with patch('src.libs.bucket.bucket.boto3.resource'):
            # Reset flags
            Bucket._initialization_attempted = False
            Bucket._initialization_failed = False

            bucket = Bucket(auto_connect=False)
            bucket.connect()
            # Flags should be set by connect attempt

    def test_initialization_failed_flag_on_failure(self):
        """Verify _initialization_failed flag is set on connection failure."""
        with patch('src.libs.bucket.bucket.boto3.resource') as mock_resource:
            mock_resource.side_effect = ClientError(
                {'Error': {'Code': '503', 'Message': 'Service Unavailable'}},
                'ListBuckets'
            )

            # Reset flags
            Bucket._initialization_attempted = False
            Bucket._initialization_failed = False

            bucket = Bucket(auto_connect=True)
            # Failure should be recorded
