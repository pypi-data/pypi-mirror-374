from __future__ import annotations

from collections.abc import Iterable

from .frame import ExceptionFrame


class TraceFormatter:
    """Formats a sequence of ExceptionFrame objects into a human-readable string."""

    def format(self, frames: Iterable[ExceptionFrame]) -> str:
        return "\n".join(str(frame) for frame in frames)
