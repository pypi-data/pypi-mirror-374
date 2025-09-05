from __future__ import annotations

import inspect
from typing import ClassVar, Final, NoReturn, get_origin, get_type_hints

from pydantic.fields import FieldInfo
from wexample_helpers.classes.mixin.printable_mixin import PrintableMixin
from wexample_helpers.classes.unique_base_model import UniqueBaseModel


class ExtendedBaseModel(PrintableMixin, UniqueBaseModel):
    def __init_subclass__(cls, **kwargs) -> None:  # type: ignore[override]
        super().__init_subclass__(**kwargs)
        # Only names declared in this class body (avoid inherited ones)
        local_annotations = cls.__dict__.get("__annotations__", {}) or {}
        # Resolve annotations with include_extras=True so ClassVar/Final are visible
        try:
            resolved_hints = get_type_hints(cls, include_extras=True)
        except Exception:
            # Fallback: use local string/raw annotations if resolution fails
            resolved_hints = {}

        for name, raw_anno in local_annotations.items():
            if name.startswith("__"):
                continue
            # Determine the effective annotation (resolved if available)
            anno = resolved_hints.get(name, raw_anno)

            # Robustly skip ClassVar / Final (constants, not model fields), even if anno is a string
            origin = get_origin(anno)
            raw_s = raw_anno if isinstance(raw_anno, str) else ""
            if (
                origin is ClassVar
                or origin is Final
                or raw_s.strip().startswith("ClassVar")
                or raw_s.strip().startswith("Final")
            ):
                continue
            # Skip private attrs and dunder
            if name.startswith("_"):
                continue

            # Only enforce on fields declared in this class body
            default = cls.__dict__.get(name, ...)

            # Must be declared with Field(...)
            if not isinstance(default, FieldInfo):
                raise TypeError(
                    (
                        f"{cls.__name__}.{name}: fields must use Field(..., description=...) — "
                        f"found plain default or missing Field."
                    )
                )

            # Must have a non-empty description
            desc = getattr(default, "description", None)
            if not desc or not str(desc).strip():
                raise TypeError(
                    f"{cls.__name__}.{name}: Field must include a non-empty description"
                )

    @classmethod
    def _raise_not_implemented_error(
        cls,
        method: str | None = None,
        message: str | None = None,
    ) -> NoReturn:
        """Convenience to raise a standardized NotImplementedError.

        Usage in would-be abstract/class methods:

            @classmethod
            def get_example_class(cls):
                cls._raise_not_implemented_error()

        or, from instance methods:

            def do_work(self):
                type(self)._raise_not_implemented_error()

        The method name is inferred from the caller if not provided.
        """
        if method is None:
            try:
                method = inspect.stack()[1].function
            except Exception:
                method = "<unknown>"
        raise NotImplementedError(
            message or f"{cls.__name__}.{method} must be implemented by subclass"
        )

    def __getattr__(self, item):
        try:
            return super().__getattr__(item)
        except AttributeError:
            # Special diagnostic for pydantic initialization issues
            if item == "__pydantic_private__":
                cls_name = type(self).__name__
                msg = (
                    f"{cls_name} is not fully initialized by Pydantic.'.\n"
                    "This typically happens when a mixin defines __init__ and is initialized before BaseModel.\n"
                    "Fix: in your class __init__, call ExtendedBaseModel.__init__(self, **kwargs) first, then your mixins;\n"
                    "or move mixin initialization logic to a post-init hook."
                )
                raise AttributeError(msg) from None

            cls_name = type(self).__name__
            raise AttributeError(f"{cls_name} has no attribute '{item}'") from None
