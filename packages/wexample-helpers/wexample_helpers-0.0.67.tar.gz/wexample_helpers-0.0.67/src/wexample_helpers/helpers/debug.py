from __future__ import annotations

from typing import Any

from wexample_helpers.common.debug.debug_breakpoint import DebugBreakpoint
from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.common.debug.debug_dump_class import DebugDumpClass
from wexample_helpers.enums.debug_path_style import DebugPathStyle
from wexample_helpers.helpers.trace import trace_print


def debug_trace(
    path_style: DebugPathStyle = DebugPathStyle.FULL, paths_map: dict | None = None
) -> None:
    # Delegate to trace helpers that use the new exception/trace classes
    trace_print(
        path_style=path_style,
        paths_map=paths_map,
    )


def debug_trace_and_die(
    message: str = None,
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    paths_map: dict | None = None,
) -> None:
    if message:
        print(message)
    debug_trace(
        path_style=path_style,
        paths_map=paths_map,
    )
    exit(1)


def debug_dump(obj: Any, max_depth: int = 100) -> None:
    DebugDump(obj, max_depth).execute()


def debug_dump_and_die(*args, **kwargs) -> None:
    debug_dump(*args, **kwargs)
    exit()


def debug_class_info(cls_or_obj, title: str = None) -> None:
    """
    Print detailed information about a class or object with improved hierarchy visualization.
    """
    target_class = cls_or_obj if isinstance(cls_or_obj, type) else type(cls_or_obj)
    dumper = DebugDumpClass(target_class)

    if title:
        print(f"\n=== {title} ===")

    dumper.execute()


def debug_breakpoint(message: str = None) -> None:
    DebugBreakpoint(message).execute()


def dd(*args, **kwargs) -> None:
    debug_dump_and_die(*args, **kwargs)
