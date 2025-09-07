import pydantic
import pydantic_settings

from ._base import BaseConfig
from ._joblib import ConfigJoblib
from ._logging import ConfigLogging
from ._pretty import ConfigPretty


class Config(BaseConfig):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="LIBLAF_GRAPES_")

    joblib: ConfigJoblib = pydantic.Field(default_factory=ConfigJoblib)
    logging: ConfigLogging = pydantic.Field(default_factory=ConfigLogging)
    pretty: ConfigPretty = pydantic.Field(default_factory=ConfigPretty)


config = Config()
