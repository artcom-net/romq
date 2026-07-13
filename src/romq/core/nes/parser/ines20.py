from typing import NamedTuple

from romq.core.nes.parser.common import (
    CHR_BANK_SIZE,
    PRG_BANK_SIZE,
    Flags6,
    Flags7,
    RawHeader,
)
from romq.core.nes.parser.errors import ParseError
from romq.core.nes.parser.models import RomMetadata, TvSystem

_EXPONENT_SIZE_FLAGS = 0x0F


def parse(
    raw_header: RawHeader,
    flags6: Flags6,
    flags7: Flags7,
) -> RomMetadata:
    flags8 = _parse_flags8(raw_header.flags8)
    flags9 = _parse_flags9(raw_header.flags9)
    flags10 = _parse_flags10(raw_header.flags10)
    flags11 = _parse_flags11(raw_header.flags11)
    flags12 = _parse_flags12(raw_header.flags12)
    # TODO: also parse 13-15

    mapper_id = (
        flags8.mapper_id_msb << 8
        | flags7.mapper_id_msb << 4
        | flags6.mapper_id_lsb
    )

    prg_rom_size = _calculate_rom_size(
        raw_header.prg_rom_banks_lsb, flags9.prg_rom_banks_msb, PRG_BANK_SIZE
    )
    chr_rom_size = _calculate_rom_size(
        raw_header.chr_rom_banks_lsb, flags9.chr_rom_banks_msb, CHR_BANK_SIZE
    )

    prg_ram_size = _calculate_ram_size(flags10.prg_ram_shift)
    prg_nvram_size = _calculate_ram_size(flags10.prg_nvram_shift)

    chr_ram_size = _calculate_ram_size(flags11.chr_ram_shift)
    chr_nvram_size = _calculate_ram_size(flags11.chr_nvram_shift)

    return RomMetadata(
        prg_rom_size=prg_rom_size,
        chr_rom_size=chr_rom_size,
        prg_ram_size=prg_ram_size,
        prg_nvram_size=prg_nvram_size,
        chr_ram_size=chr_ram_size,
        chr_nvram_size=chr_nvram_size,
        mapper_id=mapper_id,
        submapper_id=flags8.submapper_id,
        rom_format=flags7.rom_format,
        mirroring=flags6.mirroring,
        console_type=flags7.console_type,
        tv_system=flags12.tv_system,
        has_battery=flags6.has_battery,
        has_trainer=flags6.has_trainer,
        has_alternate_nt=flags6.has_alternate_nt,
    )


class _Flags8(NamedTuple):
    mapper_id_msb: int
    submapper_id: int


class _Flags9(NamedTuple):
    prg_rom_banks_msb: int
    chr_rom_banks_msb: int


class _Flags10(NamedTuple):
    prg_ram_shift: int
    prg_nvram_shift: int


class _Flags11(NamedTuple):
    chr_ram_shift: int
    chr_nvram_shift: int


class _Flags12(NamedTuple):
    tv_system: TvSystem


def _parse_flags8(flags: int) -> _Flags8:
    return _Flags8(
        mapper_id_msb=flags & 0x0F, submapper_id=(flags & 0xF0) >> 4
    )


def _parse_flags9(flags: int) -> _Flags9:
    return _Flags9(
        prg_rom_banks_msb=flags & 0x0F, chr_rom_banks_msb=(flags & 0xF0) >> 4
    )


def _parse_flags10(flags: int) -> _Flags10:
    return _Flags10(
        prg_ram_shift=flags & 0x0F, prg_nvram_shift=(flags & 0xF0) >> 4
    )


def _parse_flags11(flags: int) -> _Flags11:
    return _Flags11(
        chr_ram_shift=flags & 0x0F, chr_nvram_shift=(flags & 0xF0) >> 4
    )


def _parse_flags12(flags: int) -> _Flags12:
    match flags & 3:
        case 0:
            tv_system = TvSystem.NTSC
        case 1:
            tv_system = TvSystem.PAL
        case 2:
            tv_system = TvSystem.MULTIPLE_REGION
        case 3:
            tv_system = TvSystem.DENDY
        case _:
            # Impossible case
            raise ParseError("Unknown TV system bits")

    return _Flags12(tv_system=tv_system)


def _calculate_rom_size(
    rom_size_lsb: int,
    rom_size_msb: int,
    bank_size: int,
) -> int:
    if rom_size_msb == _EXPONENT_SIZE_FLAGS:
        """
            ++++----------- Header byte 9 D3..D0
            |||| ++++-++++- Header byte 4
          D~BA98 7654 3210
            --------------
            1111 EEEE EEMM
                 |||| ||++- Multiplier, actual value is MM*2+1 (1,3,5,7)
                 ++++-++--- Exponent (2^E), 0-63

        The actual PRG-ROM size is 2^E *(MM*2+1) bytes.
        """
        return (1 << (rom_size_lsb >> 2)) * (((rom_size_lsb & 3) * 2) + 1)
    return (rom_size_msb << 8 | rom_size_lsb) * bank_size


def _calculate_ram_size(shift_bits: int) -> int:
    return 64 << shift_bits if shift_bits else 0
