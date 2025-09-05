from __future__ import annotations

import os
from dataclasses import dataclass

from wexample_helpers.enums.debug_path_style import DebugPathStyle
from wexample_helpers.helpers.cli import cli_make_clickable_path


@dataclass(frozen=True)
class ExceptionFrame:
    filename: str
    lineno: int
    function: str
    code: str | None
    path_style: DebugPathStyle = DebugPathStyle.FULL
    paths_map: dict[str, str] | None = None

    def get_formatted_path(self) -> str:
        path = self.filename

        if self.paths_map:
            for prod_path, local_path in self.paths_map.items():
                if path.startswith(prod_path):
                    path = path.replace(prod_path, local_path, 1)
                    break

        if self.path_style == DebugPathStyle.FULL:
            return path
        elif self.path_style == DebugPathStyle.RELATIVE:
            try:
                return os.path.relpath(path)
            except ValueError:
                return path
        else:
            return os.path.basename(path)

    def format(self) -> str:
        formatted_path = self.get_formatted_path()
        path_with_line = f"{formatted_path}:{self.lineno}"

        base = (
            f"\n{'-' * 50}\n"
            f"File     : {cli_make_clickable_path(path_with_line)}\n"
            f"Line     : {self.lineno}\n"
            f"Function : {self.function}"
        )

        if self.code:
            code_section = f"\nCode     : {self.code.strip()}"
            return f"{base}{code_section}"
        return base

    def __str__(self) -> str:  # pragma: no cover – str delegates to format
        return self.format()
