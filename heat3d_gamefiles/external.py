"""
The game readers that live in their own repositories, run as commands.

Each game's reader is a separate project (3DHeat-Ext-Forza, -Battlefield,
-BeamNG, -ACRally, -Reforger), so a problem with one game's terms touches only
that game. GameFiles keeps the engine-format readers they build on, and keeps
its old verbs working by running the game's tool with the arguments it was
given. Nothing of a game tool is imported here; it is only run.

A tool is found as its command on PATH, else as its installed package, else as
its source folder: `HEAT3D_<GAME>_MAPS`, or beside GameFiles (`exporters/ext/
<folder>` in a 3DHeat checkout, or `3DHeat-Ext-<Name>` next to this one).
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

#: This repository's root: where the game tools' folders are looked for beside it.
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Tool:
    key: str
    command: str
    package: str
    folder: str
    repo: str
    game: str

    @property
    def env(self) -> str:
        return f"HEAT3D_{self.key.upper()}_MAPS"

    def source(self) -> Path | None:
        """The tool's source folder, when it is not installed."""
        given = os.environ.get(self.env)
        candidates = [Path(given)] if given else []
        candidates += [ROOT.parent / "ext" / self.folder, ROOT.parent / self.repo]
        return next((c for c in candidates if (c / self.package / "__init__.py").is_file()), None)

    def found(self) -> list[str] | None:
        """How to run it, or None when it is nowhere."""
        import importlib.util
        import shutil

        on_path = shutil.which(self.command)
        if on_path:
            return [on_path]
        if self.source() is not None or importlib.util.find_spec(self.package) is not None:
            return [sys.executable, "-m", self.package]
        return None

    def missing(self) -> str:
        return (
            f"{self.game} is read by its own tool, which is not installed: get it from "
            f"https://github.com/Holdi601/{self.repo} and run `python -m pip install -e .` in its folder "
            f"(it installs the `{self.command}` command); its docs: https://holdi601.github.io/{self.repo}/"
        )

    def run(self, argv: list[str], capture: bool = False) -> subprocess.CompletedProcess | None:
        """Runs the tool with `argv`, in this folder; None when it is not installed."""
        command = self.found()
        if command is None:
            return None
        env = dict(os.environ)
        if command[0] == sys.executable:
            # A source folder: it and this library on the path, the user's folder unchanged.
            paths = [str(p) for p in (self.source(), ROOT) if p is not None]
            env["PYTHONPATH"] = os.pathsep.join(paths + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        env.setdefault("HEAT3D_GAMEFILES", str(ROOT))
        return subprocess.run(
            [*command, *argv], env=env, capture_output=capture, text=capture,
            encoding="utf-8" if capture else None, errors="replace" if capture else None,
        )


TOOLS = {
    t.key: t
    for t in (
        Tool("forza", "heat3d-forza-maps", "heat3d_ext_forza", "forza-maps", "3DHeat-Ext-Forza", "Forza"),
        Tool("battlefield", "heat3d-battlefield-maps", "heat3d_ext_battlefield", "battlefield-maps",
             "3DHeat-Ext-Battlefield", "Battlefield (Frostbite)"),
        Tool("beamng", "heat3d-beamng-maps", "heat3d_ext_beamng", "beamng-maps", "3DHeat-Ext-BeamNG", "BeamNG.drive"),
        Tool("acrally", "heat3d-acrally-maps", "heat3d_ext_acrally", "acrally-maps", "3DHeat-Ext-ACRally",
             "Assetto Corsa Rally"),
        Tool("reforger", "heat3d-reforger-maps", "heat3d_ext_reforger", "reforger-maps", "3DHeat-Ext-Reforger",
             "Arma Reforger (Enfusion)"),
    )
}

#: GameFiles' verbs that are a game tool's now, and whose.
VERBS = {
    "courses": "forza",
    "races": "forza",
    "cars": "forza",
    "terrain": "forza",
    "levels": "battlefield",
    "level": "battlefield",
    "enfusion-worlds": "reforger",
    "enfusion-world": "reforger",
}


def delegate(key: str, argv: list[str]) -> int:
    """Runs a game tool with the user's arguments unchanged; its exit status, or 2 with how to get it."""
    tool = TOOLS[key]
    done = tool.run(argv)
    if done is None:
        print(tool.missing(), file=sys.stderr)
        return 2
    return done.returncode


def identify(path: Path) -> str | None:
    """What an installed game tool says a file is, or None when none knows it."""
    for tool in TOOLS.values():
        done = tool.run(["identify", str(path.resolve())], capture=True)
        if done is not None and done.returncode == 0 and done.stdout.strip():
            return done.stdout.rstrip()
    return None
