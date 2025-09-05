from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING

from wexample_helpers.enums.debug_path_style import DebugPathStyle

if TYPE_CHECKING:
    # Backward-compat type alias to new frame class
    from wexample_helpers.common.exception.frame import ExceptionFrame as TraceFrame

from wexample_helpers.common.exception.collector import TraceCollector
from wexample_helpers.common.exception.formatter import TraceFormatter


def trace_print(
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    paths_map: dict | None = None,
    show_internal: bool = False,
) -> None:
    # By default, hide the helper frame (this function) to show user code as the top frame.
    # When show_internal=True, display every frame including helper internals.
    print(
        trace_format(
            trace_get_frames(
                skip_frames=(1 if show_internal is False else None),
                path_style=path_style,
                paths_map=paths_map,
            )
        )
    )


def trace_get_traceback_frames(
    traceback: TracebackType,
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    paths_map: dict | None = None,
) -> list[TraceFrame]:
    """Convert exception traceback frames to TraceFrame objects."""
    return TraceCollector.from_traceback(
        traceback,
        path_style=path_style,
        paths_map=paths_map,
    )


def trace_get_frames(
    skip_frames: int | None = None,
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    paths_map: dict | None = None,
) -> list[TraceFrame]:
    """Convert stack frames to TraceFrame objects."""
    return TraceCollector.from_stack(
        skip_frames=(skip_frames + 1) if (skip_frames is not None) else None,
        path_style=path_style,
        paths_map=paths_map,
    )


def trace_format(traceback_frames: list[TraceFrame]) -> str:
    """Format a list of TraceFrame objects and optional exception information."""
    return TraceFormatter().format(traceback_frames)
