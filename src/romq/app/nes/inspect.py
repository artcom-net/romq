from pathlib import Path

from romq.app.errors import RomInspectError
from romq.app.io import PathType
from romq.app.nes.common import open_rom
from romq.app.nes.models import RomInfo
from romq.core.nes import parser as nes_parser


def inspect_rom(rom_path: PathType) -> RomInfo:
    """Inspect an NES ROM file and return its metadata.

    Opens the specified ROM file (plain file, ZIP/7z archive) and returns
    a :class:`~romq.app.nes.RomInfo` with all detected properties.
    If the archive contains multiple ROM files, the first one found with
    the correct extension will be inspected.

    Args:
        rom_path: String or path-like object to the ROM file or a ZIP/7z
            archive containing one.

    Returns:
        A :class:`~romq.app.nes.RomInfo` instance with the ROM metadata.

    Raises:
        :exc:`~romq.app.errors.RomInspectError`: If the file is not a valid
            NES ROM or the header cannot be parsed.
        :exc:`~romq.app.io.errors.ArchiveError`: If the archive is invalid or
            cannot be processed.
        :exc:`~romq.app.io.errors.ArchiveMissingRom`: If the archive contains
            no matching ROM file.
        OSError: If there is a system-level issue accessing the file
            (e.g. file not found, permission denied, or path is not a file).
    """
    filepath = Path(rom_path)
    try:
        with open_rom(filepath) as file:
            metadata = nes_parser.parse_stream(file)
            return RomInfo(filepath=filepath, metadata=metadata)
    except nes_parser.errors.ParseError as error:
        raise RomInspectError(
            f"Failed to parse ROM header: {error}"
        ) from error
