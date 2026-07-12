from typing import NamedTuple

from romq.core.nes.parser.models import ConsoleType, Mirroring, RomFormat

_KB = 1024
PRG_BANK_SIZE = 16 * _KB
CHR_BANK_SIZE = 8 * _KB
PRG_RAM_BANK_SIZE = 8 * _KB
CHR_RAM_BANK_SIZE = 8 * _KB


class Flags6(NamedTuple):
    mirroring: Mirroring
    has_battery: bool
    has_trainer: bool
    has_alternate_nt: bool
    mapper_id_lsb: int


class Flags7(NamedTuple):
    console_type: ConsoleType
    rom_format: RomFormat
    mapper_id_msb: int


class RawHeader(NamedTuple):
    id: bytes
    prg_rom_banks_lsb: int
    chr_rom_banks_lsb: int
    flags6: int
    flags7: int
    flags8: int
    flags9: int
    flags10: int
    flags11: int
    flags12: int
    flags13: int
    flags14: int
    flags15: int
