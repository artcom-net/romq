import functools
import textwrap
from pathlib import Path

import click.testing
import pytest

from romq import cli
from romq.app import errors as app_errors
from romq.app import nes

from tests.cli.utils import clear_ansi_escape, mock_app_func

_mock_inspect = functools.partial(mock_app_func, nes, "inspect_rom")

_ROM_INFO = nes.RomInfo(
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


@pytest.mark.cli
def test_inspect_rom__help(
    cli_runner: click.testing.CliRunner,
    help_option: str,
) -> None:
    expected_output = textwrap.dedent(
        """\
        Usage: romq nes inspect [OPTIONS] ROM_PATH

          Display metadata for a single NES ROM file or an archive (ZIP/7z).

        Options:
          -h, --help  Show this message and exit.
        """
    )

    result = cli_runner.invoke(cli.main, ["nes", "inspect", help_option])
    assert result.exit_code == cli.statuses.ES_SUCCESS
    assert result.stdout == expected_output


@pytest.mark.cli
def test_inspect_rom__missing_required_arguments(
    cli_runner: click.testing.CliRunner,
) -> None:
    result = cli_runner.invoke(cli.main, ["nes", "inspect"])
    assert result.exit_code == cli.statuses.ES_USAGE_ERROR
    assert "Missing argument 'ROM_PATH'" in result.stderr


@pytest.mark.cli
def test_inspect_rom__valid_options(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
) -> None:
    with _mock_inspect(monkeypatch, _ROM_INFO) as mock:
        rom_path = "rom.nes"
        result = cli_runner.invoke(
            cli.main,
            ["nes", "inspect", rom_path],
        )
        assert result.exit_code == cli.statuses.ES_SUCCESS
        mock.assert_called_once_with(rom_path)


@pytest.mark.cli
def test_inspect_rom__success_output(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
) -> None:
    expected_output = textwrap.dedent(
        """\
        ROM: rom.nes
          Format           iNES 2.0
          Console          NES
          TV System        RP2C02 (NTSC NES)
          Mapper           4
          Submapper        0
          Mirroring        Horizontal
          Trainer          True
          Alternate NT     False
          Battery-backed   False
          PRG ROM          16384
          CHR ROM          8192
          PRG RAM          0
          PRG NVRAM        0
          CHR RAM          0
          CHR NVRAM        0
        """
    )
    with _mock_inspect(monkeypatch, _ROM_INFO):
        result = cli_runner.invoke(
            cli.main,
            ["nes", "inspect", str(_ROM_INFO.filepath)],
        )
        assert result.exit_code == cli.statuses.ES_SUCCESS
        assert clear_ansi_escape(result.stdout) == expected_output


@pytest.mark.cli
@pytest.mark.parametrize(
    "error",
    (
        FileNotFoundError("File not found"),
        PermissionError("Cannot access to file"),
        app_errors.RomIOError("Archive doesn't contain ROM"),
        app_errors.RomInspectError("Invalid header ID"),
    ),
)
def test_inspect_rom__expected_failure_output(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
    error: Exception,
) -> None:
    with _mock_inspect(monkeypatch, error):
        result = cli_runner.invoke(
            cli.main,
            ["nes", "inspect", "rom.nes"],
        )
        assert result.exit_code == cli.statuses.ES_ERROR
        assert result.stdout == ""
        assert clear_ansi_escape(result.stderr) == f"{error}\n"


@pytest.mark.cli
@pytest.mark.parametrize(
    "error",
    (
        RuntimeError("something went wrong.."),
        ValueError("value error"),
        TypeError("type error"),
        AttributeError("attribute error"),
    ),
)
def test_inspect_rom__unexpected_failure_output(
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: click.testing.CliRunner,
    error: Exception,
) -> None:
    with _mock_inspect(monkeypatch, error):
        result = cli_runner.invoke(
            cli.main,
            ["nes", "inspect", "rom.nes"],
        )
        assert result.exit_code == cli.statuses.ES_INTERNAL_ERROR
        assert result.stdout == ""
        assert clear_ansi_escape(result.stderr) == f"{error}\n"
