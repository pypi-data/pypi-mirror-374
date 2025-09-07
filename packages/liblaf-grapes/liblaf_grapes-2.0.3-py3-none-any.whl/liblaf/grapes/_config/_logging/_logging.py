import types
from collections.abc import Iterable
from pathlib import Path

import pydantic

from liblaf.grapes._config._base import BaseModel
from liblaf.grapes._config._paths import paths


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

    show_locals: int = pydantic.Field(default=True)
    """Enable display of local variables."""

    suppress: Iterable[str | types.ModuleType] = pydantic.Field(default_factory=list)
    """Optional sequence of modules or paths to exclude from traceback."""


class ConfigLogging(BaseModel):
    file: Path = pydantic.Field(default=paths.log_file)
    level: str | int = pydantic.Field(default="INFO")
    traceback: ConfigLoggingTraceback = pydantic.Field(
        default_factory=ConfigLoggingTraceback
    )
