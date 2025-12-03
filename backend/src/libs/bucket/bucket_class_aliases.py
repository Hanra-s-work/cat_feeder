""" 
# +==== BEGIN AsperBackend =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: bucket_class_aliases.py
# CREATION DATE: 19-11-2025
# LAST Modified: 7:35:6 02-12-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# Protocol aliases for the S3 bucket wrapper.
#
# These lightweight ``typing.Protocol`` classes describe only the subset of the boto3 S3 interface that the bucket wrapper relies on.
# They allow static type checking without introducing optional stub packages or a hard dependency on external type distributions.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Class aliases used to help with typing for the bucket wrapper.
# // AR
# +==== END AsperBackend =================+
"""

from typing import Protocol, Any, Iterable


class S3ObjectLike(Protocol):
    """Minimal shape of an object stored in a bucket.

    Only the attributes and methods actually accessed by the
    wrapper are declared here.
    """
    @property
    def content_length(self) -> int:
        """Return the byte size of the object's content."""
        raise NotImplementedError

    def delete(self) -> Any:
        """Delete the object from its parent bucket."""
        raise NotImplementedError

    @property
    def key(self) -> str:
        """Return the object key (its unique path within the bucket)."""
        raise NotImplementedError


class S3ObjectsCollectionLike(Protocol):
    """Iterable collection façade exposing ``all()`` to enumerate objects."""

    def all(self) -> Iterable[S3ObjectLike]:
        """Return an iterable over all objects in the collection."""
        raise NotImplementedError


class S3BucketLike(Protocol):
    """Minimal bucket interface used for file/object operations."""

    def upload_file(self, Filename: str, Key: str) -> Any:
        """Upload a local file specified by ``Filename`` to this bucket under ``Key``."""
        raise NotImplementedError

    def download_file(self, Key: str, Filename: str) -> Any:
        """Download the object at ``Key`` into the local file path ``Filename``."""
        raise NotImplementedError

    def delete(self) -> Any:
        """Delete the bucket itself (must be empty)."""
        raise NotImplementedError

    def Object(self, key: str) -> S3ObjectLike:
        """Return an object handle for the given key inside this bucket."""
        raise NotImplementedError

    @property
    def objects(self) -> S3ObjectsCollectionLike:
        """Return a collection façade exposing enumeration of bucket objects."""
        raise NotImplementedError


class S3BucketsCollectionLike(Protocol):
    """Collection façade for listing bucket resources."""

    def all(self) -> Iterable[Any]:
        """Return an iterable over all available bucket resources (each with ``.name``)."""
        raise NotImplementedError  # Buckets with `.name`


class S3ServiceResourceLike(Protocol):
    """Top-level S3 service resource surface used by the wrapper.

    Provides bucket lookup, bucket creation and metadata client
    access for connectivity checks.
    """
    buckets: S3BucketsCollectionLike
    meta: Any  # has `.client.list_buckets()`

    def Bucket(self, name: str) -> S3BucketLike:
        """Return a bucket handle for the given name."""
        raise NotImplementedError

    def create_bucket(self, *, Bucket: str, **kwargs: Any) -> Any:
        """Create a new bucket named ``Bucket`` with optional configuration ``kwargs``."""
        raise NotImplementedError
