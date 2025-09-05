from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PydanticClass(BaseModel):
    """A test Pydantic class with various field types."""

    # Required fields
    name: str = Field(description="The name of the item")
    count: int = Field(default=0, description="Counter value")

    # Optional fields
    description: str | None = Field(default=None, description="Optional description")
    tags: list[str] = Field(default_factory=list, description="List of tags")

    # Field with validators
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )

    model_config = {"arbitrary_types_allowed": True}
