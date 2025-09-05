from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

RegistrableType = TypeVar("RegistrableType")


class Registry(BaseModel, Generic[RegistrableType]):
    """Generic registry for managing any type of data."""

    _items: dict[str, RegistrableType] = {}
    _fail_if_missing: bool = True
    container: Any

    def register(self, key: str, item: RegistrableType) -> None:
        """Register an item in the registry."""
        self._items[key] = item

    def get(self, key: str, **kwargs) -> RegistrableType | None:
        """
        Retrieve an item by its key.
        Additional kwargs can be used by child classes.
        """
        item = self._items.get(key)
        self._raise_error_if_expected(key, item)

        return item

    def get_all(self) -> dict[str, RegistrableType]:
        """Get all items in the registry."""
        return self._items

    def has(self, key: str) -> bool:
        """Check if an item exists in the registry."""
        return key in self._items

    def all_keys(self) -> list[str]:
        return list(self._items.keys())

    def _raise_error_if_expected(self, key: str, item: Any) -> None:
        if item is None and self._fail_if_missing:
            available_keys = self.all_keys()
            raise KeyError(
                f"Item not found in registry: {key}. Available keys: {available_keys}"
            )
