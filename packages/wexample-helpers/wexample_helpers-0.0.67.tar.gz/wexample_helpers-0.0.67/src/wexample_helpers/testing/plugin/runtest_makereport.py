from __future__ import annotations

import pytest
from wexample_helpers.common.exception.handler import ExceptionHandler
from wexample_helpers.enums.debug_path_style import DebugPathStyle


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call) -> None:
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed and call.excinfo is not None:
        err = call.excinfo.value
        handler = ExceptionHandler()
        formatted = handler.format_exception(
            err,
            path_style=DebugPathStyle.FULL,
            hide_magic_frames=True,
        )
        rep.longrepr = formatted
