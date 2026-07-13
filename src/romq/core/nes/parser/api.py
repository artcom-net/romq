import contextlib
import struct
from collections.abc import Generator
from typing import assert_never

from romq.core.nes.parser.common import Flags6, Flags7, RawHeader
from romq.core.nes.parser.errors import (
    HeaderParseError,
    InvalidHeaderError,
    UnknownRomError,
    UnsupportedRomError,
)
from romq.core.nes.parser.ines import parse as parse_ines
from romq.core.nes.parser.ines20 import parse as parse_ines20
from romq.core.nes.parser.models import (
    ConsoleType,
    Mirroring,
    RomFormat,
    RomMetadata,
)
from romq.core.nes.parser.types import (
    ReadableSeekableStream,
    ReadableStream,
    SeekableStream,
)

_HEADER_SIZE = 16
_HEADER_ID = b"NES\x1a"
_HEADER_ID_SIZE = len(_HEADER_ID)
_HEADER_STRUCT_SPEC = struct.Struct(
    f">{_HEADER_ID_SIZE}s{_HEADER_SIZE - _HEADER_ID_SIZE}B"
)


def is_rom(stream: ReadableSeekableStream) -> bool:
    """Check whether a stream contains a valid NES ROM.

    Validates only the iNES header for structural correctness. It does
    not verify internal ROM parameters (e.g., PRG or CHR sizes) or
    data integrity.

    The stream position is restored to its original location after the check.

    Args:
        stream: A readable, seekable byte stream positioned at the
            start of a potential ROM file.

    Returns:
        ``True`` if the stream contains a valid iNES header, ``False``
        otherwise.

    """
    with _restore_stream_position(stream):
        try:
            _ = _parse_raw_header(stream)
        except HeaderParseError:
            return False
        return True


def parse_stream(stream: ReadableSeekableStream) -> RomMetadata:
    """Parse a NES ROM header and return its metadata.

    Extracts and validates metadata from the iNES header. This operation
    is header-only and does not read the entire ROM file or verify
    internal data integrity.
    Supports iNES 1.0 and 2.0 formats. Archaic iNES is not supported.

    The stream position is restored to its original location after the check.

    Args:
        stream: A readable, seekable byte stream positioned at the
            start of a NES ROM file.

    Returns:
        A :class:`~romq.core.nes.parser.models.RomMetadata` instance
        with the ROM metadata.

    Raises:
        :exc:`~romq.core.nes.parser.errors.HeaderParseError`: If the header
            is missing or malformed.
        :exc:`~romq.core.nes.parser.errors.InvalidHeaderError`: If the magic
            bytes are invalid.
        :exc:`~romq.core.nes.parser.errors.UnsupportedRomError`: If the ROM
            uses an unsupported format.
        :exc:`~romq.core.nes.parser.errors.UnknownRomError`: If the ROM
            format is unrecognized.

    """
    with _restore_stream_position(stream):
        raw_header = _parse_raw_header(stream)

        flags6 = _parse_flags6(raw_header.flags6)
        flags7 = _parse_flags7(raw_header.flags7)

        match flags7.rom_format:
            case RomFormat.INES:
                rom_info = parse_ines(raw_header, flags6, flags7)
            case RomFormat.INES_20:
                rom_info = parse_ines20(raw_header, flags6, flags7)
            case RomFormat.ARCHAIC_INES:
                raise UnsupportedRomError(
                    "Archaic iNES format is not supported"
                )
            case _:
                assert_never(flags7.rom_format)

        return rom_info


@contextlib.contextmanager
def _restore_stream_position(
    stream: SeekableStream,
) -> Generator[None]:
    orig_pos = stream.tell()
    try:
        yield
    finally:
        _ = stream.seek(orig_pos)


def _parse_raw_header(stream: ReadableStream) -> RawHeader:
    header_bytes = stream.read(_HEADER_SIZE)
    if len(header_bytes) != _HEADER_SIZE:
        raise HeaderParseError("ROM header is too small")

    try:
        header = RawHeader._make(_HEADER_STRUCT_SPEC.unpack(header_bytes))
    except struct.error as error:
        raise HeaderParseError("Invalid header structure") from error

    if header.id != _HEADER_ID:
        raise InvalidHeaderError("Invalid iNES header ID")

    return header


def _parse_flags6(flags: int) -> Flags6:
    return Flags6(
        mirroring=Mirroring.VERTICAL if flags & 1 else Mirroring.HORIZONTAL,
        has_battery=bool(flags & 2),
        has_trainer=bool(flags & 4),
        has_alternate_nt=bool(flags & 8),
        mapper_id_lsb=(flags & 0xF0) >> 4,
    )


def _parse_flags7(flags: int) -> Flags7:
    match flags & 3:
        case 1:
            console_type = ConsoleType.VS_UNISYSTEM
        case 2:
            console_type = ConsoleType.PLAYCHOICE_10
        case _:
            console_type = ConsoleType.NES

    match (flags & 0x0C) >> 2:
        case 0:
            rom_format = RomFormat.INES
        case 1:
            rom_format = RomFormat.ARCHAIC_INES
        case 2:
            rom_format = RomFormat.INES_20
        case format_bits:
            raise UnknownRomError(
                f"Unknown ROM format bits: 0x{format_bits:02X}"
            )

    return Flags7(
        console_type=console_type,
        rom_format=rom_format,
        mapper_id_msb=(flags & 0xF0) >> 4,
    )
