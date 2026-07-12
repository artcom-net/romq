import contextlib
import io
import zipfile
from collections.abc import Generator
from pathlib import Path
from typing import Protocol, final, override

import py7zr

import romq.app.io.errors as io_errors
from romq.app.io.types import PathType


@contextlib.contextmanager
def open_rom(
    filepath: PathType,
    rom_extension: str,
) -> Generator[_BinaryStream]:
    file_path = Path(filepath)
    if not file_path.is_file():
        raise FileNotFoundError(f"No such file: {file_path}")

    with file_path.open("rb") as file:
        if zipfile.is_zipfile(file):
            with _extract_zip_stream(file, rom_extension) as rom_stream:
                yield rom_stream
        elif py7zr.is_7zfile(file):
            with _extract_7zip_stream(file, rom_extension) as rom_stream:
                yield rom_stream
        else:
            yield file


@contextlib.contextmanager
def _extract_zip_stream(
    file: io.BufferedReader,
    rom_extension: str,
) -> Generator[_BinaryStream]:
    # TODO: return pair (stream + filename) instead of single stream
    try:
        with zipfile.ZipFile(file) as zip_file:
            for filename in zip_file.namelist():
                if filename.endswith(rom_extension):
                    break
            else:
                raise io_errors.ArchiveMissingRom(
                    f"Archive doesn't contain ROM: *{rom_extension}"
                )

            with zip_file.open(filename) as stream:
                yield stream

    except (zipfile.BadZipFile, zipfile.LargeZipFile) as error:
        raise io_errors.ArchiveError(str(error)) from error


@contextlib.contextmanager
def _extract_7zip_stream(
    file: io.BufferedReader,
    rom_extension: str,
) -> Generator[_BinaryStream]:
    try:
        with py7zr.SevenZipFile(file, "r") as archive:
            for filename in archive.namelist():
                if filename.endswith(rom_extension):
                    break
            else:
                raise io_errors.ArchiveMissingRom(
                    f"Archive doesn't contain ROM: *{rom_extension}"
                )

            factory = _MemoryIOFactory()
            archive.extract(targets=[filename], factory=factory)
            yield factory.stream

    except py7zr.Bad7zFile as error:
        raise io_errors.ArchiveError(str(error)) from error


class _BinaryStream(Protocol):
    def read(self, n: int = -1, /) -> bytes: ...
    def seek(self, offset: int, whence: int = 0, /) -> int: ...
    def tell(self) -> int: ...


@final
class _MemoryIO(py7zr.Py7zIO):
    def __init__(self):
        self._buffer = io.BytesIO()

    @property
    def buffer(self) -> io.BytesIO:
        return self._buffer

    @override
    def write(self, s: bytes | bytearray) -> int:
        return self._buffer.write(s)

    @override
    def read(self, size: int | None = None) -> bytes:
        return self._buffer.read(size)

    @override
    def seek(self, offset: int, whence: int = 0) -> int:
        return self._buffer.seek(offset, whence)

    @override
    def flush(self) -> None:
        return

    @override
    def size(self) -> int:
        return self._buffer.getbuffer().nbytes


class _MemoryIOFactory(py7zr.WriterFactory):
    def __init__(self):
        self._memory_io: _MemoryIO | None = None

    @override
    def create(self, filename: str) -> py7zr.Py7zIO:
        self._memory_io = _MemoryIO()
        return self._memory_io

    @property
    def stream(self) -> io.BytesIO:
        if not self._memory_io:
            raise ValueError("Internal buffer not exists")
        return self._memory_io.buffer
