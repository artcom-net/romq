import enum
from dataclasses import dataclass
from typing import assert_never


class RomFormat(enum.Enum):
    """Rom format type."""

    INES = "INES"
    INES_20 = "INES_20"
    ARCHAIC_INES = "ARCHAIC_INES"

    def describe(self) -> str:
        match self:
            case RomFormat.INES:
                return "iNES"
            case RomFormat.INES_20:
                return "iNES 2.0"
            case RomFormat.ARCHAIC_INES:
                return "Archaic iNES"
            case _:
                assert_never(self)


class Mirroring(enum.Enum):
    """Screen mirroring type."""

    VERTICAL = "VERTICAL"
    HORIZONTAL = "HORIZONTAL"

    def describe(self) -> str:
        match self:
            case Mirroring.VERTICAL:
                return "Vertical"
            case Mirroring.HORIZONTAL:
                return "Horizontal"
            case _:
                assert_never(self)


class ConsoleType(enum.Enum):
    """Target console platform."""

    NES = "NES"
    VS_UNISYSTEM = "VS_UNISYSTEM"
    PLAYCHOICE_10 = "PLAYCHOICE_10"

    def describe(self) -> str:
        match self:
            case ConsoleType.NES:
                return "NES"
            case ConsoleType.VS_UNISYSTEM:
                return "VS Unisystem"
            case ConsoleType.PLAYCHOICE_10:
                return "PlayChoice-10"
            case _:
                assert_never(self)


class TvSystem(enum.Enum):
    """TV system / region variant."""

    NTSC = "NTSC"
    PAL = "PAL"
    DENDY = "DENDY"
    MULTIPLE_REGION = "MULTIPLE_REGION"

    def describe(self) -> str:
        match self:
            case TvSystem.NTSC:
                return "RP2C02 (NTSC NES)"
            case TvSystem.PAL:
                return "RP2C07 (PAL NES)"
            case TvSystem.DENDY:
                return "UA6538 (Dendy)"
            case TvSystem.MULTIPLE_REGION:
                return "Multiple-region"
            case _:
                assert_never(self)


@dataclass(slots=True, frozen=True)
class RomMetadata:
    """Metadata about a NES ROM.

    Attributes:
        prg_rom_size:
            Size of PRG-ROM in bytes.
        chr_rom_size:
            Size of CHR-ROM in bytes (0 if CHR-RAM is used).
        prg_ram_size:
            Size of PRG-RAM in bytes (0 if none).
        prg_nvram_size:
            Size of onboard NVRAM in bytes (0 if none).
        chr_ram_size:
            Size of CHR-RAM in bytes (0 if CHR-ROM is used).
        chr_nvram_size:
            Size of CHR NVRAM in bytes (reserved).
        mapper_id:
            Mapper number. Identifies the CPU/PPU mapper chip.
        submapper_id:
            Submapper number. Used by some mappers for variants.
        rom_format:
            The iNES variant.
        mirroring:
            Screen mirroring type.
        console_type:
            Target platform.
        tv_system:
            TV system / region variant.
        has_battery:
            Whether the ROM uses battery-backed RAM for saves.
        has_trainer:
            Whether the ROM contains a trainer program after the header.
        has_alternate_nt:
            Whether the ROM uses alternate nametable mirroring.
    """

    prg_rom_size: int
    chr_rom_size: int
    prg_ram_size: int
    prg_nvram_size: int
    chr_ram_size: int
    chr_nvram_size: int
    mapper_id: int
    submapper_id: int
    rom_format: RomFormat
    mirroring: Mirroring
    console_type: ConsoleType
    tv_system: TvSystem
    has_battery: bool
    has_trainer: bool
    has_alternate_nt: bool
