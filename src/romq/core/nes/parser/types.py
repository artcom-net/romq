from typing import Protocol


class ReadableStream(Protocol):
    def read(self, n: int = -1, /) -> bytes: ...


class SeekableStream(Protocol):
    def seek(self, offset: int, whence: int = 0, /) -> int: ...
    def tell(self) -> int: ...


class ReadableSeekableStream(ReadableStream, SeekableStream, Protocol):
    pass
