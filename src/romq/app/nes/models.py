from dataclasses import dataclass
from pathlib import Path

from romq.core.nes import parser as nes_parser


@dataclass(slots=True, frozen=True)
class RomInfo:
    """Information about an NES ROM file.

    Attributes:
        filepath: The path to the source file or archive containing the ROM.
        metadata: The metadata extracted from the ROM.
    """

    filepath: Path
    metadata: nes_parser.RomMetadata
