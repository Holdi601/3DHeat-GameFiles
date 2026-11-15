"""
Where an export goes when no `-o` names a place.

`HEAT3D_LEVELS`, when set, is one folder for every extraction on this machine:
each game's exports go in a folder of their own under it
(`<HEAT3D_LEVELS>/<game>/...`), so levels, courses and car packs from every
game end up side by side and one backup covers them all. Unset, an export goes
where the command runs, as it always has. An explicit `-o` always wins.
"""

from __future__ import annotations

import os
import re
from pathlib import Path


def home(game: str, *parts: str) -> Path | None:
    """`<HEAT3D_LEVELS>/<game>/<parts>`, or None when the variable is not set."""
    root = os.environ.get("HEAT3D_LEVELS", "").strip()
    return Path(root, game, *parts) if root else None


def default(name: str, game: str, *parts: str) -> Path:
    """`name` under the game's folder in `HEAT3D_LEVELS`, else `name` here."""
    folder = home(game, *parts)
    return folder / name if folder is not None else Path(name)


def game_folder(install: Path | str) -> str:
    """A game's install folder or name as a folder name: `Hell Let Loose - Vietnam` -> `hell-let-loose-vietnam`."""
    return re.sub(r"[^a-z0-9]+", "-", Path(str(install)).name.lower()).strip("-") or "game"
