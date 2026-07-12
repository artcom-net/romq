from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import override

from romq.app.io import PathType
from romq.app.io import errors as io_errors
from romq.app.nes.common import open_rom
from romq.app.nes.models import RomInfo
from romq.core.nes import parser as nes_parser


@dataclass(slots=True, frozen=True, kw_only=True)
class SearchQuery:
    """Criteria for filtering NES ROMs during a directory search.

    Attributes:
        mapper_id: Filter by mapper ID (high and low bits combined).
        submapper_id: Filter by submapper ID.
        rom_format: Filter by ROM format (e.g. iNES, iNES 2.0).
        mirroring: Filter by mirroring type (vertical or horizontal).
        console_type: Filter by console (NES, VS Unisystem, PlayChoice-10).
        tv_system: Filter by TV system (NTSC, PAL, Dendy, Multiple-region).
        has_battery: Filter by presence of battery-backed save memory.
        has_trainer: Filter by presence of a trainer program.
        has_alternate_nt: Filter by presence of alternate nametable layout.
    """

    mapper_id: int | None = None
    submapper_id: int | None = None
    rom_format: nes_parser.RomFormat | None = None
    mirroring: nes_parser.Mirroring | None = None
    console_type: nes_parser.ConsoleType | None = None
    tv_system: nes_parser.TvSystem | None = None
    has_battery: bool | None = None
    has_trainer: bool | None = None
    has_alternate_nt: bool | None = None


@dataclass(slots=True, frozen=True)
class InspectionFailure:
    """A ROM file that could not be inspected.

    Attributes:
        filepath: The path to the source file or archive that failed
            inspection.
        error: The exception raised during inspection.
    """

    filepath: Path
    error: Exception


@dataclass(slots=True, frozen=True)
class SearchResult:
    """Results from searching for NES ROMs in a directory tree.

    Attributes:
        matches: List of ROMs that matched all specified filter criteria.
        failures: List of ROMs that could not be inspected due to errors.
    """

    matches: list[RomInfo]
    failures: list[InspectionFailure]


def search_roms(
    root_dir: PathType,
    query: SearchQuery | None = None,
    predicate: Callable[[nes_parser.RomMetadata], bool] | None = None,
) -> SearchResult:
    """Search a directory tree for NES ROMs matching the given criteria.

    Recursively scans all files under ``root_dir``, identifies NES ROMs
    (including ROMs packaged inside archives (ZIP/7z)), parses their
    headers, and filters them by the provided criteria. The results include
    the path to the source file or archive containing it.

    Files that cannot be read or parsed are recorded as failures rather than
    raising an exception, so all successfully inspected ROMs are returned
    along with the list of failures.

    Args:
        root_dir: String or path-like object to the root directory to search.
        query: A :class:`~romq.app.nes.SearchQuery` object containing
            the filtering criteria.
        predicate: Optional callback function accepting a
            :class:`~romq.app.nes.RomMetadata` and returning ``True`` for
            matches. If provided, all other filter parameters in ``query``
            are ignored.

    Returns:
        A :class:`~romq.app.nes.SearchResult` containing a list of
        :class:`~romq.app.nes.RomInfo` objects and a list of
        :class:`~romq.app.nes.RomInspectFailure` objects.

    Raises:
        OSError: If there is a system-level issue accessing the root directory
            (e.g. directory not found, permission denied, etc.).
    """
    root_dir_path = Path(root_dir)
    if not root_dir_path.exists():
        raise FileNotFoundError(f"No such directory: {root_dir_path}")
    if not root_dir_path.is_dir():
        raise NotADirectoryError(f"Directory name is invalid: {root_dir_path}")

    match_func = _make_predicate(query) if predicate is None else predicate

    matches: list[RomInfo] = []
    errors: list[InspectionFailure] = []

    for filepath in _generate_filepaths(root_dir_path):
        try:
            with open_rom(filepath) as file:
                if not nes_parser.is_rom(file):
                    continue
                rom_metadata = nes_parser.parse_stream(file)
        except io_errors.ArchiveMissingRom:
            continue
        except (
            OSError,
            io_errors.ArchiveError,
            nes_parser.errors.ParseError,
        ) as error:
            errors.append(InspectionFailure(filepath, error))
            continue

        if match_func(rom_metadata):
            matches.append(RomInfo(filepath, rom_metadata))

    return SearchResult(matches, errors)


@dataclass(slots=True, frozen=True, eq=False, init=False)
class _Wildcard:  # noqa: PLW1641
    @override
    def __eq__(self, value: object, /) -> bool:
        return True


_WILDCARD = _Wildcard()


def _make_predicate(
    query: SearchQuery | None,
) -> Callable[[nes_parser.RomMetadata], bool]:
    if not query:
        return lambda _: True

    # fmt: off
    _mapper_id = (
        _WILDCARD if query.mapper_id is None else query.mapper_id
    )
    _submapper_id = (
        _WILDCARD if query.submapper_id is None else query.submapper_id
    )
    _rom_format = (
        _WILDCARD if query.rom_format is None else query.rom_format
    )
    _mirroring = (
        _WILDCARD if query.mirroring is None else query.mirroring
    )
    _console_type = (
        _WILDCARD if query.console_type is None else query.console_type
    )
    _tv_system = (
        _WILDCARD if query.tv_system is None else query.tv_system
    )
    _has_battery = (
        _WILDCARD if query.has_battery is None else query.has_battery
    )
    _has_trainer = (
        _WILDCARD if query.has_trainer is None else query.has_trainer
    )
    _has_alt_nt = (
        _WILDCARD if query.has_alternate_nt is None else query.has_alternate_nt
    )
    # fmt: on

    def match_rom(rom_info: nes_parser.RomMetadata) -> bool:
        return (
            rom_info.mapper_id == _mapper_id
            and rom_info.submapper_id == _submapper_id
            and rom_info.rom_format == _rom_format
            and rom_info.mirroring == _mirroring
            and rom_info.console_type == _console_type
            and rom_info.tv_system == _tv_system
            and rom_info.has_battery == _has_battery
            and rom_info.has_trainer == _has_trainer
            and rom_info.has_alternate_nt == _has_alt_nt
        )

    return match_rom


def _generate_filepaths(root: Path) -> Iterable[Path]:
    for root_dir, _, files in root.walk():
        for file in files:
            yield root_dir.joinpath(file)
