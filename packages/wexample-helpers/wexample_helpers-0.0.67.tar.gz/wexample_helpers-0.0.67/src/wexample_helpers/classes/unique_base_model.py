from __future__ import annotations

from pydantic import BaseModel


class UniqueBaseModel(BaseModel):
    """
    Abstract base class that prevents multiple inheritance of BaseModel.

    During the initialization of a subclass, the __init_subclass__ method inspects
    the immediate parent classes to ensure that no more than one class derived from
    BaseModel is present. If multiple BaseModel-derived classes are detected, a
    MultipleBaseModelInheritanceError is raised.

    Why this exists (rationale):
    - Multiple inheritance with several BaseModel-derived parents can lead to
      Method Resolution Order (MRO) ambiguities and subtle bugs in field merging,
      validators, model config and generics (Pydantic v1/v2). These issues are
      often hard to diagnose because they only appear at runtime on specific paths.
    - In team projects, enforcing a single BaseModel ancestor provides a clear rule
      that prevents accidental pattern drift and “magic” behaviour when models
      evolve and mixins get reused.

    Recommended patterns instead of multi-inheritance of BaseModel:
    - Prefer composition or utility mixins that DO NOT inherit from BaseModel.
    - Share validators or constraints via Annotated types / helper functions.
    - Extract common config/logic into standalone helpers or a single shared base.

    This class is abstract and cannot be instantiated directly.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        # Count the number of direct base classes that are subclasses of BaseModel.
        base_model_count = sum(
            1 for base in cls.__bases__ if issubclass(base, BaseModel)
        )
        if base_model_count > 1:
            from wexample_helpers.errors.multiple_base_model_inheritance_error import (
                MultipleBaseModelInheritanceError,
            )

            raise MultipleBaseModelInheritanceError(cls)
