from __future__ import annotations

from pydantic import Field

from .pydantic_circular_advanced_service import AdvancedService
from .pydantic_circular_base_kernel import BaseKernel


class AdvancedKernel(BaseKernel):
    """Advanced kernel with additional features."""

    version: str = Field(default="1.0.0")
    features: list[str] = Field(default_factory=list)

    @classmethod
    def get_service_class(cls) -> type[AdvancedService]:
        """Override to use AdvancedService."""
        return AdvancedService
