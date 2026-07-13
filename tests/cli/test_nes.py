import textwrap

import click.testing
import pytest

from romq import cli

_NES_HELP = textwrap.dedent(
    """\
Usage: romq nes [OPTIONS] COMMAND [ARGS]...

  NES ROM inspection and search utilities

Options:
  -h, --help  Show this message and exit.

Commands:
  inspect  Display metadata for a single NES ROM file or an archive (ZIP/7z).
  search   Search NES ROMs in a directory using hardware and format filters.
"""
)


@pytest.mark.cli
def test_nes__help(
    cli_runner: click.testing.CliRunner,
    help_option: str,
) -> None:
    result = cli_runner.invoke(cli.main, ["nes", help_option])
    assert result.exit_code == cli.statuses.ES_SUCCESS
    assert result.stdout == _NES_HELP


@pytest.mark.cli
def test_nes__missing_required_arguments(
    cli_runner: click.testing.CliRunner,
) -> None:
    result = cli_runner.invoke(cli.main, ["nes"])
    assert result.exit_code == cli.statuses.ES_USAGE_ERROR
    assert result.stderr == _NES_HELP


@pytest.mark.cli
def test_nes__invalid_arguments(
    cli_runner: click.testing.CliRunner,
) -> None:
    result = cli_runner.invoke(cli.main, ["nes", "invalid_arg"])
    assert result.exit_code == cli.statuses.ES_USAGE_ERROR
    assert "No such command 'invalid_arg'" in result.stderr
