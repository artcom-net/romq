import tempfile
import zipfile
from pathlib import Path

import py7zr


def create_file(tmp_dir: Path, content: bytes, suffix: str = "") -> Path:
    with tempfile.NamedTemporaryFile(
        dir=tmp_dir,
        suffix=suffix or ".nes",
        delete=False,
    ) as tmpfile:
        _ = tmpfile.write(content)
        return Path(tmpfile.name)


def create_empty_zipfile(tmp_dir: Path) -> Path:
    with (
        tempfile.NamedTemporaryFile(
            dir=tmp_dir,
            suffix=".zip",
            delete=False,
        ) as tmp_zipfile,
        zipfile.ZipFile(tmp_zipfile, "w"),
    ):
        return Path(tmp_zipfile.name)


def create_zipfile(tmp_dir: Path, content: bytes, suffix: str = "") -> Path:
    zip_path = create_empty_zipfile(tmp_dir)
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        file_suffix = suffix or ".nes"
        zip_file.writestr(f"rom{file_suffix}", content)
        return zip_path


def create_empty_7zipfile(tmp_dir: Path) -> Path:
    with (
        tempfile.NamedTemporaryFile(
            dir=tmp_dir,
            suffix=".7z",
            delete=False,
        ) as tmp_7zipfile,
        py7zr.SevenZipFile(tmp_7zipfile.file, "w"),
    ):
        return Path(tmp_7zipfile.name)


def create_7zipfile(tmp_dir: Path, content: bytes, suffix: str = "") -> Path:
    sevenzip_path = create_empty_7zipfile(tmp_dir)
    with py7zr.SevenZipFile(sevenzip_path, "w") as sevenzip_file:
        file_suffix = suffix or ".nes"
        sevenzip_file.writestr(content, f"rom{file_suffix}")
        return sevenzip_path
