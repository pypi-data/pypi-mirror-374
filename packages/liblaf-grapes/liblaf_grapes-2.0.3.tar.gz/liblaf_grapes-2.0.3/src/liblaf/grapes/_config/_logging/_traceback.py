import importlib
import types
from collections.abc import Iterable

import pydantic
from environs import env

from liblaf.grapes._config._base import BaseModel


def _show_locals_default() -> bool:
    return env.bool("RICH_TRACEBACK_SHOW_LOCALS", True)


def _suppress_default() -> list[str | types.ModuleType]:
    packages: list[str] = ["liblaf.cherries", "pydantic"]
    suppress: list[str | types.ModuleType] = []
    for package in packages:
        try:
            module: types.ModuleType = importlib.import_module(package)
        except ImportError:
            pass
        else:
            suppress.append(module)
    return suppress


class ConfigLoggingTraceback(BaseModel):
    """.

    References:
        1. [`rich.traceback.Traceback.from_exception`](https://rich.readthedocs.io/en/stable/reference/traceback.html#rich.traceback.Traceback.from_exception)
    """

    width: int | None = pydantic.Field(default=None)
    """Number of characters used to traceback."""

    code_width: int | None = pydantic.Field(default=None)
    """Number of code characters used to traceback."""

    extra_lines: int = pydantic.Field(default=3)
    """Additional lines of code to render."""

    show_locals: int = pydantic.Field(default_factory=_show_locals_default)
    """Enable display of local variables."""

    suppress: Iterable[str | types.ModuleType] = pydantic.Field(
        default_factory=_suppress_default
    )
    """Optional sequence of modules or paths to exclude from traceback."""
