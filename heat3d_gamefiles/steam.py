"""Where Steam keeps its libraries: the folders listed in `libraryfolders.vdf`, which every
game reader uses to find an install without being told."""

from __future__ import annotations

import re
from pathlib import Path

#: A Steam library's `path` entries in `libraryfolders.vdf`. The file is Valve's
#: own key-value format; one regex is a better trade here than a parser for it.
LIBRARY_PATH = re.compile(r'"path"\s*"([^"]+)"')

#: Where Steam itself lives, which is also a library.
STEAM_DEFAULTS = (
    r"C:\Program Files (x86)\Steam",
    r"C:\Program Files\Steam",
)


def steam_libraries() -> list[Path]:
    """Every Steam library folder this machine knows about."""
    roots: list[Path] = []
    seen: set[str] = set()
    for base in STEAM_DEFAULTS:
        config = Path(base) / "config" / "libraryfolders.vdf"
        if not config.exists():
            continue
        try:
            text = config.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for found in LIBRARY_PATH.finditer(text):
            path = Path(found.group(1).replace("\\\\", "\\"))
            key = str(path).lower()
            if key not in seen:
                seen.add(key)
                roots.append(path)
    return roots
