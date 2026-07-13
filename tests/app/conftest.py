import sys
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

    if sys.platform == "linux":
        # # py7zr uses psutil which reads /proc/meminfo
        fs.add_real_file("/proc/meminfo")  # pyright: ignore[reportUnknownMemberType, reportUnusedCallResult]

    return dir_path
