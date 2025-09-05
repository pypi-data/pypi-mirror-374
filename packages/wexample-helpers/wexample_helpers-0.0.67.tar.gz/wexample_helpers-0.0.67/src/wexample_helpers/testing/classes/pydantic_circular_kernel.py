from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from .pydantic_circular_service import Service


class Kernel(BaseModel):
    """A kernel that creates and manages services."""

    name: str = Field(description="Kernel name")
    debug: bool = Field(default=False)

    # Private service instance
    _service: Service | None = PrivateAttr(default=None)

    def __init__(self, **data) -> None:
        super().__init__(**data)
        # Create and initialize service
        self._service = Service(name=f"{self.name}_service")
        self._service.initialize(self)

    @property
    def service(self) -> Service:
        """Get the managed service."""
        return self._service
