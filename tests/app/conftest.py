import tempfile
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem


@pytest.fixture
def tmp_dir(request: pytest.FixtureRequest, fs: FakeFilesystem) -> Path:
    dir_path = Path(
        tempfile.gettempdir(),
        request.module.__name__,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        request.function.__name__,  # pyright: ignore[reportAny]
    )
    _ = fs.create_dir(dir_path)  # pyright: ignore[reportUnknownMemberType]
    return dir_path
