# cloud-storage-mocker

Mocker library of
[Google Cloud Storage Python client](https://github.com/googleapis/python-storage)
with local filesystem mounting.


## Install

For package users:

```shell
pip install cloud-storage-mocker
```

For package developers:

```shell
git clone git@github.com:odashi/cloud-storage-mocker
cd cloud-storage-mocker
python -m venv venv
source venv/bin/activate
pip install -e '.[dev]'
```


## How the package works


### Basic usage

This library provides `patch` context manager, which replaces following classes on the
[`google-cloud-storage`](https://github.com/googleapis/python-storage) package:

- `Client`
- `Bucket`
- `Blob`

`patch` takes a list of `Mount` objects, which represent mappings between bucket names
and directories on the local filesystem.
Each `Mount` has Boolean configs `readable` and `writable` to control read/write
permissions to the mounted buckets.

A canonical use-case of this package is writing unit tests to check the behavior of the
code that works with Google Cloud Storage:

```python
import pathlib

import google.cloud.storage  # type: ignore[import]

from cloud_storage_mocker import BlobMetadata, Mount
from cloud_storage_mocker import patch as gcs_patch


def test_something(tmp_path: pathlib.Path) -> None:
    # Creates two temporary directories for readable/writable buckets.
    src_dir = tmp_path / "src"
    dest_dir = tmp_path / "dest"
    src_dir.mkdir()
    dest_dir.mkdir()

    # A sample file on the readable bucket.
    (src_dir / "hello.txt").write_text("Hello.")
    # Optionally, object metadata can also be specified by the file beside the
    # content, suffixed by ".__metadata__".
    (src_dir / "hello.txt.__metadata__").write_text(
        BlobMetadata(content_type="text/plain").dump_json()
    )

    # Mounts directories. Empty list is allowed if no actual access is required.
    with gcs_patch(
        [
            Mount("readable", src_dir, readable=True),
            Mount("writable", dest_dir, writable=True),
        ],
    ):
        client = google.cloud.storage.Client()

        # Reads a blob.
        blob = client.bucket("readable").blob("hello.txt")
        assert blob.download_as_text() == "Hello."
        # Metadata is available after downloading the content.
        assert blob.content_type == "text/plain"

        # Writes a blob.
        blob = client.bucket("writable").blob("world.txt")
        blob.upload_from_string("World.")

    # Checks if the file is written appropriately.
    assert (dest_dir / "world.txt").read_text() == "World."
```


## Patched methods/properties

Methods listed below have specialized behavior to mount the local filesystem.

Other methods are mapped to `MagicMock`.

```
Client()

Client.bucket()

Bucket()

Bucket.blob()

Blob()

# Blob properties (download only)
Blob.cache_control
Blob.content_disposition
Blob.content_encoding
Blob.content_language
Blob.content_type

Blob.download_to_file()
Blob.download_to_filename()
Blob.download_as_bytes()
Blob.download_as_string()
Blob.download_as_text()
Blob.upload_from_file()
Blob.upload_from_filename()
Blob.upload_from_string()
```


## Caution

This library is basically provided for writing unit tests.
DO NOT use this library on any code on the production.
