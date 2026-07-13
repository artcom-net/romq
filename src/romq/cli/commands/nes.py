import click

from romq.app import nes as nes_app

nes_group = click.Group("nes", help="NES ROM inspection and search utilities")


@nes_group.command(
    "inspect",
    help="Display metadata for a single NES ROM file or an archive (ZIP/7z).",
)
@click.argument("rom_path")
def _inspect_rom(rom_path: str) -> nes_app.RomInfo:  # pyright: ignore[reportUnusedFunction]
    return nes_app.inspect_rom(rom_path)


@nes_group.command(
    "search",
    help="Search NES ROMs in a directory using hardware and format filters.",
)
@click.argument("root_dir")
@click.option(
    "-m",
    "--mapper-id",
    type=click.INT,
    help="Mapper ID (e.g., 0, 1, 4)",
)
@click.option(
    "-s",
    "--submapper-id",
    type=click.INT,
    help="Submapper ID",
)
@click.option(
    "-f",
    "--rom-format",
    type=click.Choice(
        (nes_app.RomFormat.INES, nes_app.RomFormat.INES_20),
        case_sensitive=False,
    ),
    help="iNES format version (1.0 or 2.0)",
)
@click.option(
    "-r",
    "--mirroring",
    type=click.Choice(nes_app.Mirroring, case_sensitive=False),
    help="Mirroring mode",
)
@click.option(
    "-c",
    "--console",
    type=click.Choice(nes_app.ConsoleType, case_sensitive=False),
    help="Console type",
)
@click.option(
    "-v",
    "--tv-system",
    type=click.Choice(nes_app.TvSystem, case_sensitive=False),
    help="TV system",
)
@click.option(
    "--battery/--no-battery",
    "has_battery",
    is_flag=True,
    default=None,
    help="Battery-backed RAM",
)
@click.option(
    "--trainer/--no-trainer",
    "has_trainer",
    is_flag=True,
    default=None,
    help="Trainer present",
)
@click.option(
    "--alt-nt/--no-alt-nt",
    "has_alternate_nt",
    is_flag=True,
    default=None,
    help="Alternate nametable layout",
)
def _search_roms(  # pyright: ignore[reportUnusedFunction]  # noqa: PLR0913
    root_dir: str,
    mapper_id: int | None,
    submapper_id: int | None,
    rom_format: nes_app.RomFormat | None,
    mirroring: nes_app.Mirroring | None,
    console: nes_app.ConsoleType | None,
    tv_system: nes_app.TvSystem | None,
    has_battery: bool | None,
    has_trainer: bool | None,
    has_alternate_nt: bool | None,
) -> nes_app.SearchResult:
    return nes_app.search_roms(
        root_dir,
        query=nes_app.SearchQuery(
            mapper_id=mapper_id,
            submapper_id=submapper_id,
            rom_format=rom_format,
            mirroring=mirroring,
            console_type=console,
            tv_system=tv_system,
            has_battery=has_battery,
            has_trainer=has_trainer,
            has_alternate_nt=has_alternate_nt,
        ),
    )
