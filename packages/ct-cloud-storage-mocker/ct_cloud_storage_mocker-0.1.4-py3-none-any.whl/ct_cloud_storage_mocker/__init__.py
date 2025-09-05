"""cloud_storage_mocker root package."""

try:
    from ct_cloud_storage_mocker import _version

    __version__ = _version.__version__
except Exception:
    __version__ = ""


from ct_cloud_storage_mocker._core import BlobMetadata, Mount, patch

__all__ = [
    "__version__",
    "BlobMetadata",
    "Mount",
    "patch",
]
