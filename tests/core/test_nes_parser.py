from io import BytesIO, StringIO
from typing import Any, final

import pytest

from romq.core.nes import parser as nes_parser


@final
class _NoSeekableStream:
    __slots__ = ("_stream",)

    def __init__(self, data: bytes):
        self._stream = BytesIO(data)

    def read(self, n: int = -1, /) -> bytes:
        return self._stream.read(n)


@final
class _NoReadableStream:
    __slots__ = ("_stream",)

    def __init__(self, data: bytes):
        self._stream = BytesIO(data)

    def seek(self, _offset: int, _whence: int = 0, /) -> int:
        return 0

    def tell(self) -> int:
        return 0


@pytest.mark.core
@pytest.mark.parametrize(
    "stream",
    (
        BytesIO(b"NES\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
        BytesIO(b"NES\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
    ),
)  # fmt: skip
def test_is_rom__valid_header(stream: BytesIO) -> None:
    orig_pos = stream.tell()
    assert nes_parser.is_rom(stream) is True
    assert stream.tell() == orig_pos


@pytest.mark.core
@pytest.mark.parametrize(
    "stream",
    (
        BytesIO(),
        BytesIO(b"NES\x1a"),
        BytesIO(b"NES\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
    ),
)
def test_is_rom__invalid_header(stream: BytesIO) -> None:
    orig_pos = stream.tell()
    assert nes_parser.is_rom(stream) is False
    assert stream.tell() == orig_pos


@pytest.mark.core
@pytest.mark.parametrize(
    "stream,expected",
    (
        # iNES 1.0 basic
        (
            BytesIO(b"NES\x1a\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=16384,
                chr_rom_size=8192,
                prg_ram_size=0,
                prg_nvram_size=0,
                chr_ram_size=0,
                chr_nvram_size=0,
                mapper_id=0,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES,
                mirroring=nes_parser.Mirroring.HORIZONTAL,
                console_type=nes_parser.ConsoleType.NES,
                tv_system=nes_parser.TvSystem.NTSC,
                has_battery=False,
                has_trainer=False,
                has_alternate_nt=False,
            )
        ),
        # iNES 1.0 max mapper, x2 PRG/CHR banks
        (
            BytesIO(b"NES\x1a\x02\x02\xf0\xf0\x00\x00\x00\x00\x00\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=32768,
                chr_rom_size=16384,
                prg_ram_size=0,
                prg_nvram_size=0,
                chr_ram_size=0,
                chr_nvram_size=0,
                mapper_id=255,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES,
                mirroring=nes_parser.Mirroring.HORIZONTAL,
                console_type=nes_parser.ConsoleType.NES,
                tv_system=nes_parser.TvSystem.NTSC,
                has_battery=False,
                has_trainer=False,
                has_alternate_nt=False,
            )
        ),
        # iNES 1.0 battery, trainer, vertical
        (
            BytesIO(b"NES\x1a\x01\x01\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=16384,
                chr_rom_size=8192,
                prg_ram_size=0,
                prg_nvram_size=0,
                chr_ram_size=0,
                chr_nvram_size=0,
                mapper_id=0,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES,
                mirroring=nes_parser.Mirroring.VERTICAL,
                console_type=nes_parser.ConsoleType.NES,
                tv_system=nes_parser.TvSystem.NTSC,
                has_battery=True,
                has_trainer=True,
                has_alternate_nt=False,
            )
        ),
        # iNES 2.0 basic
        (
            BytesIO(b"NES\x1a\x01\x01\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=16384,
                chr_rom_size=8192,
                prg_ram_size=0,
                prg_nvram_size=0,
                chr_ram_size=0,
                chr_nvram_size=0,
                mapper_id=0,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES_20,
                mirroring=nes_parser.Mirroring.HORIZONTAL,
                console_type=nes_parser.ConsoleType.NES,
                tv_system=nes_parser.TvSystem.NTSC,
                has_battery=False,
                has_trainer=False,
                has_alternate_nt=False,
            )
        ),
        # iNES 2.0 max mapper / submapper
        (
            BytesIO(b"NES\x1a\x01\x01\xf0\xf8\xff\x00\x00\x00\x00\x00\x00\x00"),
                nes_parser.RomMetadata(
                    prg_rom_size=16384,
                    chr_rom_size=8192,
                    prg_ram_size=0,
                    prg_nvram_size=0,
                    chr_ram_size=0,
                    chr_nvram_size=0,
                    mapper_id=4095,
                    submapper_id=15,
                    rom_format=nes_parser.RomFormat.INES_20,
                    mirroring=nes_parser.Mirroring.HORIZONTAL,
                    console_type=nes_parser.ConsoleType.NES,
                    tv_system=nes_parser.TvSystem.NTSC,
                    has_battery=False,
                    has_trainer=False,
                    has_alternate_nt=False,
            )
        ),
        # iNES 2.0 mapper 4, PRG RAM 8K
        (
            BytesIO(b"NES\x1a\x08\x10\x40\x08\x00\x00\x07\x00\x00\x00\x00\x00"),
                nes_parser.RomMetadata(
                    prg_rom_size=131072,
                    chr_rom_size=131072,
                    prg_ram_size=8192,
                    prg_nvram_size=0,
                    chr_ram_size=0,
                    chr_nvram_size=0,
                    mapper_id=4,
                    submapper_id=0,
                    rom_format=nes_parser.RomFormat.INES_20,
                    mirroring=nes_parser.Mirroring.HORIZONTAL,
                    console_type=nes_parser.ConsoleType.NES,
                    tv_system=nes_parser.TvSystem.NTSC,
                    has_battery=False,
                    has_trainer=False,
                    has_alternate_nt=False,
            )
        ),
        # iNES 2.0 mapper 2, submapper 2, CHR RAM, vertical
        (
            BytesIO(b"NES\x1a\x08\x00\x21\x08\x20\x00\x00\x07\x00\x00\x00\x00"),
                nes_parser.RomMetadata(
                    prg_rom_size=131072,
                    chr_rom_size=0,
                    prg_ram_size=0,
                    prg_nvram_size=0,
                    chr_ram_size=8192,
                    chr_nvram_size=0,
                    mapper_id=2,
                    submapper_id=2,
                    rom_format=nes_parser.RomFormat.INES_20,
                    mirroring=nes_parser.Mirroring.VERTICAL,
                    console_type=nes_parser.ConsoleType.NES,
                    tv_system=nes_parser.TvSystem.NTSC,
                    has_battery=False,
                    has_trainer=False,
                    has_alternate_nt=False,
            )
        ),
        # iNES 2.0 VS Unisystem, PAL, battery, trainer, alt NT layout
        (
            BytesIO(b"NES\x1a\x01\x01\x0e\x09\x00\x00\x00\x00\x01\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=16384,
                chr_rom_size=8192,
                prg_ram_size=0,
                prg_nvram_size=0,
                chr_ram_size=0,
                chr_nvram_size=0,
                mapper_id=0,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES_20,
                mirroring=nes_parser.Mirroring.HORIZONTAL,
                console_type=nes_parser.ConsoleType.VS_UNISYSTEM,
                tv_system=nes_parser.TvSystem.PAL,
                has_battery=True,
                has_trainer=True,
                has_alternate_nt=True,
            )
        ),
        # iNES 2.0 large PRG ROM (512K), CHR NVRAM, battery
        (
            BytesIO(b"NES\x1a\x20\x00\x42\x08\x00\x00\x00\x70\x00\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=524288,
                chr_rom_size=0,
                prg_ram_size=0,
                prg_nvram_size=0,
                chr_ram_size=0,
                chr_nvram_size=8192,
                mapper_id=4,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES_20,
                mirroring=nes_parser.Mirroring.HORIZONTAL,
                console_type=nes_parser.ConsoleType.NES,
                tv_system=nes_parser.TvSystem.NTSC,
                has_battery=True,
                has_trainer=False,
                has_alternate_nt=False,
            )
        ),
        # iNES 2.0 Dendy
        (
            BytesIO(b"NES\x1a\x01\x01\x00\x08\x00\x00\x00\x00\x03\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=16384,
                chr_rom_size=8192,
                prg_ram_size=0,
                prg_nvram_size=0,
                chr_ram_size=0,
                chr_nvram_size=0,
                mapper_id=0,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES_20,
                mirroring=nes_parser.Mirroring.HORIZONTAL,
                console_type=nes_parser.ConsoleType.NES,
                tv_system=nes_parser.TvSystem.DENDY,
                has_battery=False,
                has_trainer=False,
                has_alternate_nt=False,
            )
        ),
        # iNES 2.0 Exponent PRG size
        (
            BytesIO(b"NES\x1a\x51\x01\x00\x08\x00\x0f\x00\x00\x00\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=3145728,
                chr_rom_size=8192,
                prg_ram_size=0,
                prg_nvram_size=0,
                chr_ram_size=0,
                chr_nvram_size=0,
                mapper_id=0,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES_20,
                mirroring=nes_parser.Mirroring.HORIZONTAL,
                console_type=nes_parser.ConsoleType.NES,
                tv_system=nes_parser.TvSystem.NTSC,
                has_battery=False,
                has_trainer=False,
                has_alternate_nt=False,
            )
        ),
        # 12. iNES 2.0 PRG NVRAM, battery
        (
            BytesIO(b"NES\x1a\x01\x01\x02\x08\x00\x00\x70\x00\x00\x00\x00\x00"),
            nes_parser.RomMetadata(
                prg_rom_size=16384,
                chr_rom_size=8192,
                prg_ram_size=0,
                prg_nvram_size=8192,
                chr_ram_size=0,
                chr_nvram_size=0,
                mapper_id=0,
                submapper_id=0,
                rom_format=nes_parser.RomFormat.INES_20,
                mirroring=nes_parser.Mirroring.HORIZONTAL,
                console_type=nes_parser.ConsoleType.NES,
                tv_system=nes_parser.TvSystem.NTSC,
                has_battery=True,
                has_trainer=False,
                has_alternate_nt=False,
            )
        ),
    )
)  # fmt: skip
# TODO: Split ines 1.0 / 2.0
def test_parse_stream__valid_header(
    stream: BytesIO,
    expected: nes_parser.RomMetadata,
) -> None:
    orig_pos = stream.tell()
    assert nes_parser.parse_stream(stream) == expected
    assert stream.tell() == orig_pos


@pytest.mark.core
@pytest.mark.parametrize(
    "stream,error_type,message_regexp",
    (
        (
            BytesIO(b""),
            nes_parser.errors.HeaderParseError,
            r"ROM header is too small",
        ),
        (
            BytesIO(b"NES\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            nes_parser.errors.HeaderParseError,
            r"ROM header is too small",
        ),
        (
            BytesIO(b"NES\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            nes_parser.errors.InvalidHeaderError,
            r"Invalid iNES header ID",
        ),
        (
            BytesIO(b"NES\x1a\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00"),
            nes_parser.errors.UnsupportedRomError,
            r"Archaic iNES format is not supported",
        ),
        (
            BytesIO(b"NES\x1a\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00"),
            nes_parser.errors.UnknownRomError,
            r"Unknown ROM format bits: 0x03",
        ),
    ),
)  # fmt: skip
def test_parse_stream__invalid_header(
    stream: BytesIO,
    error_type: type[nes_parser.errors.ParseError],
    message_regexp: str,
) -> None:
    orig_pos = stream.tell()

    with pytest.raises(error_type, match=message_regexp):
        _ = nes_parser.parse_stream(stream)

    assert stream.tell() == orig_pos


@pytest.mark.core
@pytest.mark.parametrize(
    "stream,error_type,message_regexp",
    (
        (
            StringIO("4e45531a010102080000700000000000"),
            TypeError,
            r"bytes-like object is required",
        ),
        (
            _NoSeekableStream(
                b"NES\x1a\x01\x01\x00\x08\x00\x00\x00\x00\x03\x00\x00\x00"
            ),
            AttributeError,
            r"object has no attribute 'tell'",
        ),
        (
            _NoReadableStream(
                b"NES\x1a\x01\x01\x00\x08\x00\x00\x00\x00\x03\x00\x00\x00"
            ),
            AttributeError,
            r"object has no attribute 'read'",
        ),
    ),
)
def test_parse_stream__invalid_stream(
    stream: Any,  # pyright: ignore[reportExplicitAny, reportAny]
    error_type: type[Exception],
    message_regexp: str,
) -> None:
    with pytest.raises(error_type, match=message_regexp):
        _ = nes_parser.parse_stream(stream)  # pyright: ignore[reportAny]
