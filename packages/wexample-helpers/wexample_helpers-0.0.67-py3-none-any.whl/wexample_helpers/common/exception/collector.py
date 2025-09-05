from __future__ import annotations

import inspect
from types import TracebackType

from wexample_helpers.enums.debug_path_style import DebugPathStyle

from .frame import ExceptionFrame


class TraceCollector:
    """Collects frames from current stack or from an exception traceback."""

    @staticmethod
    def from_traceback(
        traceback: TracebackType,
        *,
        path_style: DebugPathStyle = DebugPathStyle.FULL,
        paths_map: dict[str, str] | None = None,
    ) -> list[ExceptionFrame]:
        frames: list[ExceptionFrame] = []
        current = traceback
        while current is not None:
            frame = current.tb_frame
            code = None
            if frame.f_code.co_filename != "<string>":
                try:
                    with open(frame.f_code.co_filename) as f:
                        lines = f.readlines()
                        if 0 <= current.tb_lineno - 1 < len(lines):
                            code = lines[current.tb_lineno - 1]
                except (OSError, IndexError):
                    pass

            frames.append(
                ExceptionFrame(
                    filename=frame.f_code.co_filename,
                    lineno=current.tb_lineno,
                    function=frame.f_code.co_name,
                    code=code,
                    path_style=path_style,
                    paths_map=paths_map,
                )
            )
            current = current.tb_next
        return frames

    @staticmethod
    def from_stack(
        *,
        skip_frames: int | None = None,
        path_style: DebugPathStyle = DebugPathStyle.FULL,
        paths_map: dict[str, str] | None = None,
    ) -> list[ExceptionFrame]:
        frames: list[ExceptionFrame] = []
        for frame in inspect.stack()[
            (skip_frames + 1 if skip_frames is not None else 0) :
        ]:
            frames.append(
                ExceptionFrame(
                    filename=frame.filename,
                    lineno=frame.lineno,
                    function=frame.function,
                    code=frame.code_context[0] if frame.code_context else None,
                    path_style=path_style,
                    paths_map=paths_map,
                )
            )
        frames.reverse()
        return frames
