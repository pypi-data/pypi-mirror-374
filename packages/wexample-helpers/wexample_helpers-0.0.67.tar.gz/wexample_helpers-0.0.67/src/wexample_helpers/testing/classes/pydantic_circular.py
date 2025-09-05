from __future__ import annotations

from typing import ForwardRef

from pydantic import BaseModel, Field, PrivateAttr

# Forward references for circular dependencies
KernelRef = ForwardRef("Kernel")
ServiceRef = ForwardRef("Service")


class Service(BaseModel):
    """A service that needs access to its parent kernel."""

    name: str = Field(description="Service name")
    enabled: bool = Field(default=True)

    # Private reference to parent
    _kernel: Kernel | None = PrivateAttr(default=None)

    def initialize(self, kernel: Kernel) -> None:
        """Initialize the service with its parent kernel."""
        self._kernel = kernel

    @property
    def kernel(self) -> Kernel | None:
        """Get the parent kernel."""
        return self._kernel


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


# Update forward references
Service.model_rebuild()
Kernel.model_rebuild()
