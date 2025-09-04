from contextlib import suppress
from io import BytesIO
from typing import IO
from typing import Any
from typing import BinaryIO

from amsdal_models.storage.base import Storage
from amsdal_models.storage.errors import StorageError
from amsdal_models.storage.helpers import build_storage_address
from amsdal_models.storage.types import FileProtocol


class DBStorage(Storage):
    """
    In-database storage backend.

    This backend "stores" file bytes within the File model's `data` field itself.
    - save(): reads bytes from the provided content stream and assigns to file.data.
    - open(): returns a BytesIO stream over file.data.
    - url(): returns a non-public placeholder URL (db://<filename>).

    Since bytes are kept on the model, this backend keeps a local copy to prevent
    persistence layer from clearing payload.
    """

    keeps_local_copy = True

    def save(self, file: FileProtocol, content: BinaryIO) -> str:
        data = self._ensure_bytes(content)
        file.data = data
        file.storage_address = build_storage_address(self, file.filename)
        # Do not change the provided filename; collisions are irrelevant for DB storage
        return file.filename

    def open(self, file: FileProtocol, mode: str = 'rb') -> IO[Any]:
        self._validate_mode(mode)
        if file.data is None:
            msg = f"No data present in FileProtocol '{file.filename}' to open"
            raise StorageError(msg)
        # Return a new BytesIO each time to emulate a fresh stream
        return BytesIO(file.data)

    def delete(self, file: FileProtocol) -> None:
        file.data = None

    def exists(self, file: FileProtocol) -> bool:
        return file.data is not None

    def url(self, file: FileProtocol) -> str:
        return f'db://{file.filename}'

    async def asave(self, file: FileProtocol, content: BinaryIO) -> str:
        return self.save(file, content)

    async def aopen(self, file: FileProtocol, mode: str = 'rb') -> IO[Any]:
        return self.open(file, mode)

    async def adelete(self, file: FileProtocol) -> None:
        self.delete(file)

    async def aexists(self, file: FileProtocol) -> bool:
        return self.exists(file)

    async def aurl(self, file: FileProtocol) -> str:
        return self.url(file)

    def _ensure_bytes(self, content: BinaryIO) -> bytes:
        # Try to reset to beginning if possible
        if hasattr(content, 'seek'):
            with suppress(Exception):
                content.seek(0)

        data = content.read()

        if not isinstance(data, bytes | bytearray):
            msg = 'DBStorage.save expected a binary stream returning bytes'
            raise StorageError(msg)
        return bytes(data)

    def _validate_mode(self, mode: str) -> None:
        # We only support reading modes from in-memory bytes
        if 'w' in mode or 'a' in mode or '+' in mode:
            msg = f"DBStorage.open does not support write/append modes: '{mode}'"
            raise StorageError(msg)
