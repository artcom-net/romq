import contextlib
import re
from collections.abc import Generator
from types import ModuleType
from unittest.mock import MagicMock, create_autospec

import pytest

_ANSI_ESCAPE_REGEXP = re.compile(r"\x1b\[[0-9;]*m")


def clear_ansi_escape(value: str) -> str:
    return _ANSI_ESCAPE_REGEXP.sub("", value)


@contextlib.contextmanager
def mock_app_func(
    module: ModuleType,
    func_name: str,
    monkeypatch: pytest.MonkeyPatch,
    return_value: object | Exception,
) -> Generator[MagicMock]:
    func = getattr(module, func_name)  # pyright: ignore[reportAny]
    if isinstance(return_value, Exception):
        mock = create_autospec(func, side_effect=return_value)  # pyright: ignore[reportAny]
    else:
        mock = create_autospec(func, return_value=return_value)  # pyright: ignore[reportAny]

    with monkeypatch.context() as patcher:
        patcher.setattr(module, func_name, mock)  # pyright: ignore[reportAny]
        yield mock
