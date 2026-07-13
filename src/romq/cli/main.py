from typing import Any, override

import click

from romq import __version__
from romq.app import errors as app_errors
from romq.cli.commands.nes import nes_group
from romq.cli.render import Renderable, render
from romq.cli.statuses import ES_ERROR, ES_INTERNAL_ERROR


class _MainGroup(click.Group):
    def __init__(self, *args, **kwargs) -> None:  # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]
        self.add_command(nes_group)

    @override
    def invoke(self, ctx: click.Context) -> Any:  # pyright: ignore[reportExplicitAny, reportAny]
        try:
            return super().invoke(ctx)  # pyright: ignore[reportAny]
        except click.ClickException, click.Abort, click.exceptions.Exit:
            raise
        except (OSError, app_errors.RomqError) as error:
            status = ES_ERROR
            click.echo(render(error), err=True)
        except Exception as error:
            status = ES_INTERNAL_ERROR
            click.echo(render(error), err=True)

        raise click.exceptions.Exit(status)


@click.group(
    "romq",
    cls=_MainGroup,
    help=(
        "A CLI utility for inspecting ROM metadata and searching directories"
        " for ROM files based on specific criteria."
    ),
    context_settings={"help_option_names": ["-h", "--help"], "color": True},
)
@click.version_option(message=f"%(prog)s {__version__}")
def main() -> None:
    pass


@main.result_callback()
def _process_result(result: Renderable) -> None:  # pyright: ignore[reportUnusedFunction]
    click.echo(render(result))
