import functools
from typing import overload

import click

from romq.app import nes as nes_app

type Renderable = nes_app.RomInfo | nes_app.SearchResult | Exception


@overload
def render(data: nes_app.RomInfo) -> str: ...


@overload
def render(data: nes_app.SearchResult) -> str: ...


@overload
def render(data: Exception) -> str: ...


def render(data: Renderable) -> str:
    return _render(data)


@functools.singledispatch
def _render(data: Renderable) -> str:
    raise NotImplementedError(f"No renderer for {type(data)}")


@_render.register
def _render_error(data: Exception) -> str:  # pyright: ignore[reportUnusedFunction]
    return click.style(f"{data}", fg="bright_red")


@_render.register
def _render_rom_info(data: nes_app.RomInfo) -> str:  # pyright: ignore[reportUnusedFunction]
    rows: list[str] = [click.style(f"ROM: {data.filepath}", fg="bright_cyan")]

    metadata = data.metadata
    raw_rows = (
        ("Format", metadata.rom_format.describe()),
        ("Console", metadata.console_type.describe()),
        ("TV System", metadata.tv_system.describe()),
        ("Mapper", str(metadata.mapper_id)),
        ("Submapper", str(metadata.submapper_id)),
        ("Mirroring", metadata.mirroring.describe()),
        ("Trainer", str(metadata.has_trainer)),
        ("Alternate NT", str(metadata.has_alternate_nt)),
        ("Battery-backed", str(metadata.has_battery)),
        ("PRG ROM", str(metadata.prg_rom_size)),
        ("CHR ROM", str(metadata.chr_rom_size)),
        ("PRG RAM", str(metadata.prg_ram_size)),
        ("PRG NVRAM", str(metadata.prg_nvram_size)),
        ("CHR RAM", str(metadata.chr_ram_size)),
        ("CHR NVRAM", str(metadata.chr_nvram_size)),
    )

    max_label_len = max(len(label) for label, _ in raw_rows)
    label_width = max_label_len + 2

    for label, value in raw_rows:
        styled_label = click.style(
            f"  {label:<{label_width}}",
            fg="bright_black",
        )
        styled_value = click.style(
            f"{value}",
            fg="bright_white",
        )
        rows.append(" ".join((styled_label, styled_value)))

    return "\n".join(rows)


@_render.register
def _render_search_result(data: nes_app.SearchResult) -> str:  # pyright: ignore[reportUnusedFunction]
    rows: list[str] = []

    for match in data.matches:
        rows.append(click.style(str(match.filepath), fg="bright_green"))

        metadata = match.metadata
        rows.append(
            click.style(
                (
                    f"  [{metadata.rom_format.describe()}"
                    f" | {metadata.tv_system.describe()}"
                    f" | Mapper {metadata.mapper_id}"
                    f" | {metadata.mirroring.describe()}"
                    f" | PRG {metadata.prg_rom_size}"
                    f" | CHR {metadata.chr_rom_size}]"
                ),
                fg="bright_black",
            )
        )

    for failure in data.failures:
        rows.append(
            click.style(f"{failure.filepath}", fg="bright_red")
            + click.style(f"\n  {failure.error}", fg="red")
        )

    rows.append(
        click.style(
            (
                f"ROM matches: {len(data.matches)}"
                f", Errors: {len(data.failures)}"
            ),
            fg="bright_white",
        )
    )

    return "\n".join(rows)
