import functools
import textwrap
from collections.abc import Iterable
from pathlib import Path

import click.testing
import pytest

from romq import cli
from romq.app import nes

from tests.cli.utils import clear_ansi_escape, mock_app_func

_mock_search = functools.partial(mock_app_func, nes, "search_roms")


def _make_search_query(  # noqa: PLR0913
    mapper_id: int | None = None,
    submapper_id: int | None = None,
    rom_format: nes.RomFormat | None = None,
    mirroring: nes.Mirroring | None = None,
    console_type: nes.ConsoleType | None = None,
    tv_system: nes.TvSystem | None = None,
    has_battery: bool | None = None,
    has_trainer: bool | None = None,
    has_alternate_nt: bool | None = None,
) -> nes.SearchQuery:
    return nes.SearchQuery(
        mapper_id=mapper_id,
        submapper_id=submapper_id,
        rom_format=rom_format,
        mirroring=mirroring,
        console_type=console_type,
        tv_system=tv_system,
        has_battery=has_battery,
        has_trainer=has_trainer,
        has_alternate_nt=has_alternate_nt,
    )


@pytest.mark.cli
def test_search_roms__help(
    cli_runner: click.testing.CliRunner,
    help_option: str,
) -> None:
    expected_output = textwrap.dedent(
        """\
        Usage: romq nes search [OPTIONS] ROOT_DIR

          Search NES ROMs in a directory using hardware and format filters.

        Options:
          -m, --mapper-id INTEGER         Mapper ID (e.g., 0, 1, 4)
          -s, --submapper-id INTEGER      Submapper ID
          -f, --rom-format [ines|ines_20]
                                          iNES format version (1.0 or 2.0)
          -r, --mirroring [vertical|horizontal]
                                          Mirroring mode
          -c, --console [nes|vs_unisystem|playchoice_10]
                                          Console type
          -v, --tv-system [ntsc|pal|dendy|multiple_region]
                                          TV system
          --battery / --no-battery        Battery-backed RAM
          --trainer / --no-trainer        Trainer present
          --alt-nt / --no-alt-nt          Alternate nametable layout
          -h, --help                      Show this message and exit.
        """
    )

    result = cli_runner.invoke(cli.main, ["nes", "search", help_option])
    assert result.exit_code == cli.statuses.ES_SUCCESS
    assert result.stdout == expected_output


@pytest.mark.cli
def test_search_roms__missing_required_arguments(
    cli_runner: click.testing.CliRunner,
) -> None:
    result = cli_runner.invoke(cli.main, ["nes", "search"])
    assert result.exit_code == cli.statuses.ES_USAGE_ERROR
    assert "Missing argument 'ROOT_DIR'" in result.stderr


@pytest.mark.cli
@pytest.mark.parametrize(
    "options,search_query",
    (
        # empty
        (
            (),
            _make_search_query(),
        ),
        # mapper
        (
            ("-m", "0"),
            _make_search_query(mapper_id=0),
        ),
        (
            ("--mapper-id", "0"),
            _make_search_query(mapper_id=0),
        ),
        # submapper
        (
            ("-s", "0"),
            _make_search_query(submapper_id=0),
        ),
        (
            ("--submapper-id", "0"),
            _make_search_query(submapper_id=0),
        ),
        # rom format
        (
            ("-f", "ines"),
            _make_search_query(rom_format=nes.RomFormat.INES),
        ),
        (
            ("--rom-format", "ines_20"),
            _make_search_query(rom_format=nes.RomFormat.INES_20),
        ),
        # mirroring
        (
            ("-r", "horizontal"),
            _make_search_query(mirroring=nes.Mirroring.HORIZONTAL),
        ),
        (
            ("--mirroring", "vertical"),
            _make_search_query(mirroring=nes.Mirroring.VERTICAL),
        ),
        # console
        (
            ("-c", "nes"),
            _make_search_query(console_type=nes.ConsoleType.NES),
        ),
        (
            ("--console", "playchoice_10"),
            _make_search_query(console_type=nes.ConsoleType.PLAYCHOICE_10),
        ),
        (
            ("--console", "vs_unisystem"),
            _make_search_query(console_type=nes.ConsoleType.VS_UNISYSTEM),
        ),
        # tv system
        (
            ("-v", "ntsc"),
            _make_search_query(tv_system=nes.TvSystem.NTSC),
        ),
        (
            ("--tv-system", "pal"),
            _make_search_query(tv_system=nes.TvSystem.PAL),
        ),
        (
            ("--tv-system", "multiple_region"),
            _make_search_query(tv_system=nes.TvSystem.MULTIPLE_REGION),
        ),
        (
            ("--tv-system", "dendy"),
            _make_search_query(tv_system=nes.TvSystem.DENDY),
        ),
        # battery
        (
            ("--battery",),
            _make_search_query(has_battery=True),
        ),
        (
            ("--no-battery",),
            _make_search_query(has_battery=False),
        ),
        # trainer
        (
            ("--trainer",),
            _make_search_query(has_trainer=True),
        ),
        (
            ("--no-trainer",),
            _make_search_query(has_trainer=False),
        ),
        # alt NT layout
        (
            ("--alt-nt",),
            _make_search_query(has_alternate_nt=True),
        ),
        (
            ("--no-alt-nt",),
            _make_search_query(has_alternate_nt=False),
        ),
        # all
        (
            (
                "--mapper-id", "4",
                "--submapper-id", "0",
                "--rom-format", "ines_20",
                "--mirroring", "horizontal",
                "--console", "nes",
                "--tv-system", "ntsc",
                "--battery",
                "--trainer",
                "--alt-nt",
            ),
            _make_search_query(
                mapper_id=4,
                submapper_id=0,
                rom_format=nes.RomFormat.INES_20,
                mirroring=nes.Mirroring.HORIZONTAL,
                console_type=nes.ConsoleType.NES,
                tv_system=nes.TvSystem.NTSC,
                has_battery=True,
                has_trainer=True,
                has_alternate_nt=True,
            )
        ),
    )
)  # fmt: skip
def test_search_roms__valid_options(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
    options: Iterable[str],
    search_query: nes.SearchQuery,
) -> None:
    with _mock_search(monkeypatch, nes.SearchResult([], [])) as mock:
        root_dir = "root_dir"
        result = cli_runner.invoke(
            cli.main,
            ["nes", "search", root_dir, *options],
        )

        assert result.exit_code == cli.statuses.ES_SUCCESS
        mock.assert_called_once_with(root_dir, query=search_query)


# ruff: disable[E501]
@pytest.mark.cli
@pytest.mark.parametrize(
    "options,expected_error",
    (
        (
            ("--mapper-id", "a"),
            "Invalid value for '-m' / '--mapper-id': 'a' is not a valid integer",
        ),
        (
            ("--submapper-id", "a"),
            "Invalid value for '-s' / '--submapper-id': 'a' is not a valid integer",
        ),
        (
            ("--rom-format", "archaic_ines"),
            "Invalid value for '-f' / '--rom-format': 'archaic_ines' is not one of 'ines', 'ines_20'",
        ),
        (
            ("--mirroring", "hor"),
            "Invalid value for '-r' / '--mirroring': 'hor' is not one of 'vertical', 'horizontal'",
        ),
        (
            ("--console", "default"),
            "Invalid value for '-c' / '--console': 'default' is not one of 'nes', 'vs_unisystem', 'playchoice_10'.",
        ),
        (
            ("--tv-system", "HD"),
            "Invalid value for '-v' / '--tv-system': 'HD' is not one of 'ntsc', 'pal', 'dendy', 'multiple_region'",
        ),
        (
            ("--battery", "yes"),
            "Got unexpected extra argument (yes)",
        ),
    ),
)
# ruff: enable[E501]
# fmt: skip
def test_search_roms__invalid_options(
    cli_runner: click.testing.CliRunner,
    options: Iterable[str],
    expected_error: str,
) -> None:
    result = cli_runner.invoke(
        cli.main,
        ["nes", "search", "root_dir", *options],
    )
    assert result.exit_code == cli.statuses.ES_USAGE_ERROR
    assert result.stdout == ""
    assert expected_error in result.stderr


@pytest.mark.cli
def test_search_roms__empty_result_output(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
) -> None:
    with _mock_search(monkeypatch, nes.SearchResult([], [])):
        result = cli_runner.invoke(cli.main, ["nes", "search", "root_dir"])

        assert result.exit_code == cli.statuses.ES_SUCCESS
        assert result.stderr == ""
        assert (
            clear_ansi_escape(result.stdout) == "ROM matches: 0, Errors: 0\n"
        )


@pytest.mark.cli
def test_search_roms__mixed_result_output(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
) -> None:
    rom_info1 = nes.RomInfo(
        filepath=Path("rom.nes"),
        metadata=nes.RomMetadata(
            prg_rom_size=16384,
            chr_rom_size=8192,
            prg_ram_size=0,
            prg_nvram_size=0,
            chr_ram_size=0,
            chr_nvram_size=0,
            mapper_id=4,
            submapper_id=0,
            rom_format=nes.RomFormat.INES_20,
            mirroring=nes.Mirroring.HORIZONTAL,
            console_type=nes.ConsoleType.NES,
            tv_system=nes.TvSystem.NTSC,
            has_battery=False,
            has_trainer=True,
            has_alternate_nt=False,
        ),
    )
    rom_info2 = nes.RomInfo(
        filepath=Path("rom2.nes"),
        metadata=nes.RomMetadata(
            prg_rom_size=131072,
            chr_rom_size=0,
            prg_ram_size=0,
            prg_nvram_size=0,
            chr_ram_size=8192,
            chr_nvram_size=0,
            mapper_id=2,
            submapper_id=2,
            rom_format=nes.RomFormat.INES_20,
            mirroring=nes.Mirroring.VERTICAL,
            console_type=nes.ConsoleType.NES,
            tv_system=nes.TvSystem.NTSC,
            has_battery=False,
            has_trainer=False,
            has_alternate_nt=False,
        ),
    )
    search_result = nes.SearchResult(
        matches=[rom_info1, rom_info2],
        failures=[
            nes.InspectionFailure(
                Path("invalid.nes"),
                ValueError("invalid header"),
            ),
        ],
    )
    # ruff: disable[E501]
    expected_output = textwrap.dedent(
        """\
        rom.nes
          [iNES 2.0 | RP2C02 (NTSC NES) | Mapper 4 | Horizontal | PRG 16384 | CHR 8192]
        rom2.nes
          [iNES 2.0 | RP2C02 (NTSC NES) | Mapper 2 | Vertical | PRG 131072 | CHR 0]
        invalid.nes
          invalid header
        ROM matches: 2, Errors: 1
        """
    )
    # ruff: enable[E501]

    with _mock_search(monkeypatch, search_result):
        result = cli_runner.invoke(cli.main, ["nes", "search", "root_dir"])

        assert result.exit_code == cli.statuses.ES_SUCCESS
        assert result.stderr == ""
        assert clear_ansi_escape(result.stdout) == expected_output


@pytest.mark.cli
@pytest.mark.parametrize(
    "error",
    (
        FileNotFoundError("File not found"),
        PermissionError("Cannot access to file"),
        NotADirectoryError("Directory name is invalid"),
    ),
)
def test_search_roms__expected_failure_output(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
    error: Exception,
) -> None:
    with _mock_search(monkeypatch, error):
        result = cli_runner.invoke(cli.main, ["nes", "search", "root_dir"])

        assert result.exit_code == cli.statuses.ES_ERROR
        assert result.stdout == ""
        assert clear_ansi_escape(result.stderr) == f"{error}\n"


@pytest.mark.cli
@pytest.mark.parametrize(
    "error",
    (
        RuntimeError("Something went wrong.."),
        ValueError("Value error"),
        TypeError("Type error"),
        AttributeError("Attribute error"),
    ),
)
def test_search_roms__unexpected_failure_output(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
    error: Exception,
) -> None:
    with _mock_search(monkeypatch, error):
        result = cli_runner.invoke(cli.main, ["nes", "search", "root_dir"])

        assert result.exit_code == cli.statuses.ES_INTERNAL_ERROR
        assert result.stdout == ""
        assert clear_ansi_escape(result.stderr) == f"{error}\n"
