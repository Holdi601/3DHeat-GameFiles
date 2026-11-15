"""The game readers in their own repositories: found and run as commands, never imported."""

from __future__ import annotations

import subprocess
import sys

from heat3d_gamefiles import cli, external


def test_a_missing_tool_says_where_to_get_it(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(external, "ROOT", tmp_path)
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr("importlib.util.find_spec", lambda _: None)
    monkeypatch.delenv("HEAT3D_FORZA_MAPS", raising=False)
    assert cli.main(["cars"]) == 2
    err = capsys.readouterr().err
    assert "3DHeat-Ext-Forza" in err and "heat3d-forza-maps" in err


def test_old_verbs_run_the_game_tool_with_the_same_arguments(monkeypatch):
    calls = []
    monkeypatch.setattr("shutil.which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(subprocess, "run", lambda args, **kw: calls.append(args) or subprocess.CompletedProcess(args, 0))
    assert cli.main(["level", "some level", "-o", "x.glb", "--navmesh"]) == 0
    assert cli.main(["enfusion-worlds", "--install", "here"]) == 0
    assert cli.main(["course", "lap.json", "--game", "beamng", "--margin", "50"]) == 0
    assert calls == [
        ["/bin/heat3d-battlefield-maps", "level", "some level", "-o", "x.glb", "--navmesh"],
        ["/bin/heat3d-reforger-maps", "enfusion-worlds", "--install", "here"],
        ["/bin/heat3d-beamng-maps", "course", "lap.json", "--game", "beamng", "--margin", "50"],
    ]


def test_a_source_folder_beside_gamefiles_is_found(tmp_path, monkeypatch):
    folder = tmp_path / "ext" / "reforger-maps" / "heat3d_ext_reforger"
    folder.mkdir(parents=True)
    (folder / "__init__.py").write_text("")
    monkeypatch.setattr(external, "ROOT", tmp_path / "gamefiles")
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.delenv("HEAT3D_REFORGER_MAPS", raising=False)
    tool = external.TOOLS["reforger"]
    assert tool.source() == folder.parent
    assert tool.found() == [sys.executable, "-m", "heat3d_ext_reforger"]


def test_a_game_with_no_course_reader_is_refused_plainly(capsys):
    assert cli.main(["course", "lap.json", "--game", "iracing"]) == 1
    assert "no course export for this lap" in capsys.readouterr().err
