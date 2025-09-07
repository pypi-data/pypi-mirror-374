import pydantic

from ._base import BaseModel


class ConfigPretty(BaseModel):
    """.

    References:
        1. [wadler_lindig.pformat](https://docs.kidger.site/wadler_lindig/api/#wadler_lindig.pformat)
    """

    width: int | None = pydantic.Field(default=None)
    """a best-effort maximum width to allow. May be exceeded if there are unbroken pieces of text which are wider than this."""

    indent: int = pydantic.Field(default=2)
    """when the contents of a structured type are too large to fit on one line, they will be indented by this amount and placed on separate lines."""

    short_arrays: bool = pydantic.Field(default=True)
    """whether to print a NumPy array / PyTorch tensor / JAX array as a short summary of the form `f32[3,4]` (here indicating a `float32` matrix of shape `(3, 4)`)"""

    hide_defaults: bool = pydantic.Field(default=True)
    """whether to show the default values of dataclass fields."""

    show_type_module: bool = pydantic.Field(default=True)
    """whether to show the name of the module for a type: `somelib.SomeClass` versus `SomeClass`."""

    show_dataclass_module: bool = pydantic.Field(default=False)
    """whether to show the name of the module for a dataclass instance: `somelib.SomeClass()` versus `SomeClass()`."""

    show_function_module: bool = pydantic.Field(default=False)
    """whether to show the name of the module for a function: `<function some_fn>` versus `<function somelib.some_fn>`."""

    respect_pdoc: bool = pydantic.Field(default=True)
