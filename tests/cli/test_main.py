import textwrap

import click.testing
import pytest

from romq import __version__, cli

_MAIN_HELP = textwrap.dedent(
    """\
Usage: romq [OPTIONS] COMMAND [ARGS]...

  A CLI utility for inspecting ROM metadata and searching directories for ROM
  files based on specific criteria.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  nes  NES ROM inspection and search utilities
"""
)


@pytest.mark.cli
def test_get_version(cli_runner: click.testing.CliRunner) -> None:
    result = cli_runner.invoke(cli.main, ["--version"])
    assert result.exit_code == cli.statuses.ES_SUCCESS
    assert result.stdout == f"romq {__version__}\n"


@pytest.mark.cli
def test_main__help(
    cli_runner: click.testing.CliRunner,
    help_option: str,
) -> None:
    result = cli_runner.invoke(cli.main, [help_option])
    assert result.exit_code == cli.statuses.ES_SUCCESS
    assert result.stdout == _MAIN_HELP


@pytest.mark.cli
def test_main__missing_required_arguments(
    cli_runner: click.testing.CliRunner,
) -> None:
    result = cli_runner.invoke(cli.main, [])
    assert result.exit_code == cli.statuses.ES_USAGE_ERROR
    assert result.stderr == _MAIN_HELP


@pytest.mark.cli
def test_main__invalid_arguments(
    cli_runner: click.testing.CliRunner,
) -> None:
    result = cli_runner.invoke(cli.main, ["invalid_arg"])
    assert result.exit_code == cli.statuses.ES_USAGE_ERROR
    assert "No such command 'invalid_arg'" in result.stderr
