from pathlib import Path

import pytest

from romq.app import nes as nes_app
from romq.core.nes.parser import errors as parser_errors

from tests.app.utils import (
    create_7zipfile,
    create_empty_7zipfile,
    create_empty_zipfile,
    create_file,
    create_zipfile,
)

_ROM1_HEADER = b"NES\x1a\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
_ROM1_INFO = nes_app.RomInfo(
    filepath=Path(),
    metadata=nes_app.RomMetadata(
        prg_rom_size=16384,
        chr_rom_size=8192,
        prg_ram_size=0,
        prg_nvram_size=0,
        chr_ram_size=0,
        chr_nvram_size=0,
        mapper_id=0,
        submapper_id=0,
        rom_format=nes_app.RomFormat.INES,
        mirroring=nes_app.Mirroring.HORIZONTAL,
        console_type=nes_app.ConsoleType.NES,
        tv_system=nes_app.TvSystem.NTSC,
        has_battery=False,
        has_trainer=False,
        has_alternate_nt=False,
    ),
)

_ROM2_HEADER = b"NES\x1a\x08\x00\x21\x08\x20\x00\x00\x07\x00\x00\x00\x01"
_ROM2_INFO = nes_app.RomInfo(
    filepath=Path(),
    metadata=nes_app.RomMetadata(
        prg_rom_size=131072,
        chr_rom_size=0,
        prg_ram_size=0,
        prg_nvram_size=0,
        chr_ram_size=8192,
        chr_nvram_size=0,
        mapper_id=2,
        submapper_id=2,
        rom_format=nes_app.RomFormat.INES_20,
        mirroring=nes_app.Mirroring.VERTICAL,
        console_type=nes_app.ConsoleType.NES,
        tv_system=nes_app.TvSystem.NTSC,
        has_battery=False,
        has_trainer=False,
        has_alternate_nt=False,
    ),
)


@pytest.mark.app
def test_search_roms__dir_not_exists(tmp_dir: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"No such directory"):
        _ = nes_app.search_roms(tmp_dir.joinpath("notexist.nes"))


@pytest.mark.app
def test_search_roms__not_directory(tmp_dir: Path) -> None:
    filepath = create_file(tmp_dir, b"")
    with pytest.raises(
        NotADirectoryError,
        match="Directory name is invalid",
    ):
        _ = nes_app.search_roms(filepath)


@pytest.mark.app
def test_search_roms__empty_dir(tmp_dir: Path) -> None:
    result = nes_app.search_roms(tmp_dir)
    assert len(result.matches) == 0
    assert len(result.failures) == 0


@pytest.mark.app
def test_search_roms__match_any(tmp_dir: Path) -> None:
    rom_path = create_file(tmp_dir, _ROM1_HEADER)

    zip_rom_path = create_zipfile(tmp_dir, _ROM2_HEADER)
    _empty_zip_path = create_empty_zipfile(tmp_dir)

    sevenzip_rom_path = create_7zipfile(tmp_dir, _ROM1_HEADER)
    _empty_7zip_path = create_empty_7zipfile(tmp_dir)

    _not_rom_path = create_file(tmp_dir, b"NES\x1a")
    bad_rom_path = create_file(
        tmp_dir,
        b"NES\x1a\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00",
    )

    expected_matches = {
        rom_path: _ROM1_INFO.metadata,
        zip_rom_path: _ROM2_INFO.metadata,
        sevenzip_rom_path: _ROM1_INFO.metadata,
    }
    expected_errors = {
        bad_rom_path: nes_app.InspectionFailure(
            bad_rom_path,
            parser_errors.UnknownRomError("Unknown ROM format bits: 0x03"),
        )
    }

    result = nes_app.search_roms(tmp_dir)

    assert len(result.matches) == len(expected_matches)
    assert all(
        expected_matches[match.filepath] == match.metadata
        for match in result.matches
    )

    assert len(result.failures) == len(expected_errors)
    for error in result.failures:
        expected = expected_errors[error.filepath]
        assert error.filepath == expected.filepath
        assert error.error.__class__ is expected.error.__class__
        assert str(error.error) == str(expected.error)


@pytest.mark.app
def test_search_roms__match_filter(tmp_dir: Path) -> None:
    ines_horiz_path = create_file(tmp_dir, _ROM1_HEADER)
    _ = create_zipfile(tmp_dir, _ROM2_HEADER)

    result = nes_app.search_roms(
        tmp_dir,
        query=nes_app.SearchQuery(
            mapper_id=_ROM1_INFO.metadata.mapper_id,
            submapper_id=_ROM1_INFO.metadata.submapper_id,
            rom_format=_ROM1_INFO.metadata.rom_format,
            mirroring=_ROM1_INFO.metadata.mirroring,
            console_type=_ROM1_INFO.metadata.console_type,
            tv_system=_ROM1_INFO.metadata.tv_system,
            has_battery=_ROM1_INFO.metadata.has_battery,
            has_trainer=_ROM1_INFO.metadata.has_trainer,
            has_alternate_nt=_ROM1_INFO.metadata.has_alternate_nt,
        ),
    )

    assert len(result.failures) == 0
    assert len(result.matches) == 1

    match = result.matches[0]
    assert match.filepath == ines_horiz_path
    assert match.metadata == _ROM1_INFO.metadata


@pytest.mark.app
def test_search_roms__match_predicate(tmp_dir: Path) -> None:
    _ = create_file(tmp_dir, _ROM1_HEADER)
    ines20_vert_path = create_zipfile(tmp_dir, _ROM2_HEADER)

    result = nes_app.search_roms(
        tmp_dir,
        predicate=lambda ri: (
            ri.rom_format is nes_app.RomFormat.INES_20
            and ri.mirroring is nes_app.Mirroring.VERTICAL
        ),
    )

    assert len(result.failures) == 0
    assert len(result.matches) == 1

    match = result.matches[0]
    assert match.filepath == ines20_vert_path
    assert match.metadata == _ROM2_INFO.metadata


@pytest.mark.app
def test_search_roms__predicate_overrides_filter_args(tmp_dir: Path) -> None:
    _ = create_file(tmp_dir, _ROM1_HEADER)
    vert_ines20_path = create_zipfile(tmp_dir, _ROM2_HEADER)

    result = nes_app.search_roms(
        tmp_dir,
        query=nes_app.SearchQuery(
            rom_format=nes_app.RomFormat.INES,
            mirroring=nes_app.Mirroring.HORIZONTAL,
        ),
        predicate=lambda ri: (
            ri.rom_format is nes_app.RomFormat.INES_20
            and ri.mirroring is nes_app.Mirroring.VERTICAL
        ),
    )

    assert len(result.failures) == 0
    assert len(result.matches) == 1

    match = result.matches[0]
    assert match.filepath == vert_ines20_path
    assert match.metadata == _ROM2_INFO.metadata


@pytest.mark.app
def test_search_roms__match_nothing(tmp_dir: Path) -> None:
    _ = create_file(tmp_dir, _ROM1_HEADER)

    result = nes_app.search_roms(
        tmp_dir,
        query=nes_app.SearchQuery(
            console_type=nes_app.ConsoleType.VS_UNISYSTEM,
        ),
    )

    assert len(result.failures) == 0
    assert len(result.matches) == 0
