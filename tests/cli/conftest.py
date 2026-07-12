import click.testing
import pytest


@pytest.fixture(autouse=True)
def freeze_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COLUMNS", "80")


@pytest.fixture(params=("-h", "--help"))
def help_option(request: pytest.FixtureRequest) -> str:
    return request.param  # pyright: ignore[reportAny]


@pytest.fixture
def cli_runner() -> click.testing.CliRunner:
    return click.testing.CliRunner()
