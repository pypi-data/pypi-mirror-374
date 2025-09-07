from collections.abc import Callable, Mapping
from typing import Any, Literal, TypedDict

import pydantic

type EncHook = Callable[[Any], Any]


type IncEx = (
    set[int] | set[str] | Mapping[int, "IncEx | bool"] | Mapping[str, "IncEx | bool"]
)


class PydanticModelDumpOptions(TypedDict, total=False):
    mode: Literal["json", "python"]
    include: IncEx | None
    exclude: IncEx | None
    context: Any | None
    by_alias: bool | None
    exclude_unset: bool
    exclude_defaults: bool
    exclude_none: bool
    round_trip: bool
    warnings: bool | Literal["none", "warn", "error"]
    fallback: Callable[[Any], Any] | None
    serialize_as_any: bool


def enc_hook(
    obj: Any, /, *, pydantic_options: PydanticModelDumpOptions | None = None
) -> Any:
    if isinstance(obj, pydantic.BaseModel):
        pydantic_options = pydantic_options or {}
        return obj.model_dump(**pydantic_options)
    return obj
