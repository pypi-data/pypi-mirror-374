from typing import Unpack

import loguru

from liblaf.grapes._config import config
from liblaf.grapes.logging.filters import make_filter


def jsonl_handler(
    **kwargs: Unpack["loguru.FileHandlerConfig"],
) -> "loguru.FileHandlerConfig":
    if "sink" not in kwargs and config.logging.file is not None:
        kwargs["sink"] = config.logging.file
    kwargs["filter"] = make_filter(kwargs.get("filter"))
    kwargs.setdefault("serialize", True)
    kwargs.setdefault("mode", "w")
    return kwargs
