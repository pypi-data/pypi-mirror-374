from __future__ import annotations

from wexample_helpers.exception.undefined_exception import ExceptionData


class NotAllowedItemData(ExceptionData):
    """Data model for exceptions related to not allowed items."""

    item_type: str
    item_value: str | None = None
    allowed_values: list[str] = []
    is_missing: bool = False
