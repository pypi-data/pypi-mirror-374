from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .pydantic_circular_service import Service

if TYPE_CHECKING:
    from .pydantic_circular_advanced_kernel import AdvancedKernel
    from .pydantic_circular_base_kernel import BaseKernel


class AdvancedService(Service):
    """Advanced service with additional features."""

    mode: str = Field(default="advanced")
    config: dict = Field(default_factory=dict)

    @property
    def advanced_kernel(self) -> AdvancedKernel | None:
        """Get the parent kernel as AdvancedKernel."""
        return self.kernel  # type: ignore

    @property
    def base_kernel(self) -> BaseKernel | None:
        """Access parent kernel as base type."""
        return self.kernel
