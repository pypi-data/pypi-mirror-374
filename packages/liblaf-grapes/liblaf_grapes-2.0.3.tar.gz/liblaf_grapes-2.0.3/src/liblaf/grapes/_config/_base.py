import contextlib
from collections.abc import Generator, Mapping
from typing import Any, Self

import pydantic
import pydantic_settings


class MixinOverrides:
    @contextlib.contextmanager
    def overrides(self, **kwargs) -> Generator[Self]:
        original: dict[str, Any] = {}
        try:
            for k, v in kwargs.items():
                original[k] = getattr(self, k)
                setattr(self, k, v)
            yield self
        finally:
            for k, v in original.items():
                setattr(self, k, v)


class BaseModel(MixinOverrides, pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True, validate_default=True
    )

    def to_dict(self, **kwargs) -> Mapping[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return self.model_dump(**kwargs)


class BaseConfig(MixinOverrides, pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_nested_delimiter="__",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        validate_default=True,
    )
