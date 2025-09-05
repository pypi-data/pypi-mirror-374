from __future__ import annotations

import re

CSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
OSC8_RE = re.compile(r"\x1B\]8;;.*?\x1B\\")
