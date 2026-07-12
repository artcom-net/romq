from typing import NamedTuple

from romq.core.nes.parser.common import (
    CHR_BANK_SIZE,
    PRG_BANK_SIZE,
    PRG_RAM_BANK_SIZE,
    Flags6,
    Flags7,
    RawHeader,
)
from romq.core.nes.parser.models import RomMetadata, TvSystem


def parse(
    raw_header: RawHeader,
    flags6: Flags6,
    flags7: Flags7,
) -> RomMetadata:
    flags9 = _parse_flags9(raw_header.flags9)

    return RomMetadata(
        prg_rom_size=raw_header.prg_rom_banks_lsb * PRG_BANK_SIZE,
        chr_rom_size=raw_header.chr_rom_banks_lsb * CHR_BANK_SIZE,
        prg_ram_size=raw_header.flags8 * PRG_RAM_BANK_SIZE,
        prg_nvram_size=0,
        chr_ram_size=0,
        chr_nvram_size=0,
        mapper_id=flags7.mapper_id_msb << 4 | flags6.mapper_id_lsb,
        submapper_id=0,
        rom_format=flags7.rom_format,
        mirroring=flags6.mirroring,
        console_type=flags7.console_type,
        tv_system=flags9.tv_system,
        has_battery=flags6.has_battery,
        has_trainer=flags6.has_trainer,
        has_alternate_nt=flags6.has_alternate_nt,
    )


class _Flags9(NamedTuple):
    tv_system: TvSystem
    reserved_bits: int


def _parse_flags9(flags: int) -> _Flags9:
    return _Flags9(
        tv_system=TvSystem.PAL if flags & 1 else TvSystem.NTSC,
        reserved_bits=flags & 0xFE,
    )
