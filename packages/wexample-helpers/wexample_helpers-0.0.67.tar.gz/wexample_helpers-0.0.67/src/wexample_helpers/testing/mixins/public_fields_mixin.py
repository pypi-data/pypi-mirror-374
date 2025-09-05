from __future__ import annotations

from .base_mixin import BaseMixin


class PublicFieldsMixin(BaseMixin):
    """Mixin providing public fields template."""

    name: str
    tags: list[str]
    description: str | None
    version: str = "1.0.0"
