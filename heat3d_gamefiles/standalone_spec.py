"""
The standalone app's description of this tool (app/spec.py). GameFiles reads
engine formats of whichever game it is pointed at, so it has no install of its
own to find and no fixed list of maps: the window offers its commands as tasks
(an Unreal 5 game's World Partition maps, one of them as a level, what a file
is, what an archive holds), and checks the Oodle library some archives need.
`python -m heat3d_gamefiles.standalone_spec` runs the app from a checkout; the
release executables run the same.
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import __version__
from .app.spec import Check, Input, Spec, Task

TOOL = "heat3d-gamefiles"


def _checks(found: dict, levels: Path) -> list[Check]:
    from .oodle import find_oodle

    if sys.platform != "win32":
        return [Check("oodle", "Oodle library (from a game or engine on this machine)", False,
                      "the Oodle library is a Windows DLL; archives with Oodle-compressed blocks are read on Windows")]
    lib = find_oodle()
    return [Check(
        "oodle", "Oodle library (from a game or engine on this machine)", lib is not None,
        str(lib) if lib else "not found; only Oodle-compressed archives need it. Set HEAT3D_OODLE to an "
        "oo2core_*_win64.dll from a game or engine installed on this machine.",
    )]


def _apply_source(release) -> str:
    """A checkout or source copy updates the way it always did (heat3d_update in the repository root)."""
    root = str(Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.append(root)
    import heat3d_update

    return heat3d_update.apply(release)


SPEC = Spec(
    id="heat3d-gamefiles",
    name="3DHeat GameFiles",
    repo="Holdi601/3DHeat-GameFiles",
    version=__version__,
    tools={TOOL: "heat3d_gamefiles.cli:main"},
    default_tool=TOOL,
    description="engine-format readers: Unreal 5 maps as 3DHeat levels, and what game archives hold",
    module="heat3d_gamefiles.standalone_spec",
    games=[],
    checks=_checks,
    tasks=[
        Task(
            "ue-maps", "List an Unreal 5 game's maps",
            [Input("game", "The game's folder (the one holding its Content\\Paks)", "folder")],
            lambda v, levels: [TOOL, "ue-maps", v["game"]],
            help="every World Partition map the game's containers hold",
        ),
        Task(
            "ue-map", "Export an Unreal 5 map",
            [Input("game", "The game's folder (the one holding its Content\\Paks)", "folder"),
             Input("map", "The map's name, as the list shows it", "text")],
            lambda v, levels: [TOOL, "ue-map", v["game"], v["map"]],
            help="landscape, HLOD structures and water as one .glb, into <levels>/<game>",
        ),
        Task(
            "identify", "Say what a file is",
            [Input("path", "A game file", "file")],
            lambda v, levels: [TOOL, "identify", v["path"]],
        ),
        Task(
            "list", "List what an archive holds",
            [Input("path", "An archive (.pak, .utoc, _dir.vpk, .minizip, .zip)", "file")],
            lambda v, levels: [TOOL, "list", v["path"]],
        ),
    ],
    min_free_gb=2.0,
    notice="Not affiliated with or endorsed by any game's makers or publishers.",
)

if __name__ == "__main__":
    from .app.entry import main

    raise SystemExit(main(SPEC, apply_source=_apply_source))
