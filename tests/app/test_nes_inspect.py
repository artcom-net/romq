import functools
import re
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

import romq.app.io.file as file_io
from romq.app import errors as app_errors
from romq.app import nes as nes_app

from tests.app.utils import (
    create_7zipfile,
    create_empty_7zipfile,
    create_empty_zipfile,
    create_file,
    create_zipfile,
)

# pyright: reportUnnecessaryTypeIgnoreComment=false

_ROM_HEADER = b"NES\x1a\x01\x01\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00"


@pytest.mark.app
@pytest.mark.parametrize(
    "romfile_factory",
    (create_file, create_zipfile, create_7zipfile),
)
def test_inspect_rom__success(
    tmp_dir: Path,
    romfile_factory: Callable[[Path, bytes], Path],
) -> None:
    rom_path = romfile_factory(tmp_dir, _ROM_HEADER)
    expected_rom_info = nes_app.RomInfo(
        filepath=rom_path,
        metadata=nes_app.RomMetadata(
            prg_rom_size=16384,
            chr_rom_size=8192,
            prg_ram_size=0,
            prg_nvram_size=0,
            chr_ram_size=0,
            chr_nvram_size=0,
            mapper_id=0,
            submapper_id=0,
            rom_format=nes_app.RomFormat.INES_20,
            mirroring=nes_app.Mirroring.HORIZONTAL,
            console_type=nes_app.ConsoleType.NES,
            tv_system=nes_app.TvSystem.NTSC,
            has_battery=False,
            has_trainer=False,
            has_alternate_nt=False,
        ),
    )

    assert nes_app.inspect_rom(rom_path) == expected_rom_info


@pytest.mark.app
def test_inspect_rom__file_not_exist(tmp_dir: Path) -> None:
    rom_path = tmp_dir.joinpath("test_inspect_rom__file_not_exist.nes")
    with pytest.raises(FileNotFoundError):
        _ = nes_app.inspect_rom(rom_path)


@pytest.mark.app
@pytest.mark.parametrize(
    "header,error_regexp",
    (
        (
            b"",
            "ROM header is too small",
        ),
        (
            b"NES\x00\x01\x01\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00",
            "Invalid iNES header ID",
        ),
        (
            b"NES\x1a\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00",
            "Archaic iNES format is not supported",
        ),
        (
            b"NES\x1a\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00",
            "Unknown ROM format bits: 0x03",
        ),
    ),
)
def test_inspect_rom__invalid_rom_header(
    tmp_dir: Path,
    header: bytes,
    error_regexp: str,
) -> None:
    rom_path = tmp_dir.joinpath("test_inspect_rom__expected_failures.nes")
    _ = rom_path.write_bytes(header)

    with pytest.raises(app_errors.RomInspectError, match=error_regexp):
        _ = nes_app.inspect_rom(rom_path)


@pytest.mark.app
@pytest.mark.parametrize(
    "romfile_factory",
    (
        create_empty_zipfile,
        create_empty_7zipfile,
        functools.partial(create_zipfile, content=_ROM_HEADER, suffix=".exe"),
        functools.partial(create_7zipfile, content=_ROM_HEADER, suffix=".exe"),
    ),
)
def test_inspect_rom__missing_rom_in_archive(
    tmp_dir: Path,
    romfile_factory: Callable[[Path], Path],
) -> None:
    rom_path = romfile_factory(tmp_dir)

    with pytest.raises(
        app_errors.RomIOError,
        match=re.escape("Archive doesn't contain ROM: *.nes"),
    ):
        _ = nes_app.inspect_rom(rom_path)


@pytest.mark.app
@pytest.mark.parametrize(
    "patcher_args,archive_suffix,error",
    (
        ((file_io.zipfile, "is_zipfile"), ".zip", "File is not a zip file"),  # pyright: ignore[reportPrivateImportUsage, reportPrivateLocalImportUsage]
        ((file_io.py7zr, "is_7zfile"), ".7z", "not a 7z file"),  # pyright: ignore[reportPrivateImportUsage, reportPrivateLocalImportUsage]
    ),
)
def test_inspect_rom__broken_archive(
    monkeypatch: pytest.MonkeyPatch,
    tmp_dir: Path,
    patcher_args: tuple[ModuleType, str],
    archive_suffix: str,
    error: str,
) -> None:
    # TODO: replace on manual creating broken files
    with monkeypatch.context() as patcher:
        patcher.setattr(*patcher_args, lambda _: True)  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
        bad_archive_path = create_file(tmp_dir, b"", suffix=archive_suffix)

        with pytest.raises(app_errors.RomIOError, match=error):
            _ = nes_app.inspect_rom(bad_archive_path)
