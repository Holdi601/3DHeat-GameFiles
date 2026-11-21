"""The standalone app's description of GameFiles: tasks, checks, no maps (no game files used)."""

from __future__ import annotations

import json

import pytest

from heat3d_gamefiles import standalone_spec
from heat3d_gamefiles.app import entry, update


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "appdata"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "appdata"))
    monkeypatch.setenv("HEAT3D_LEVELS", str(tmp_path / "levels"))
    monkeypatch.setenv("HEAT3D_NO_UPDATE", "1")
    update.AUTO_THIS_RUN = False


def test_tasks_run_the_tools_own_verbs(tmp_path):
    spec = standalone_spec.SPEC
    tasks = {t.id: t for t in spec.tasks}
    assert tasks["ue-map"].argv({"game": "G", "map": "M"}, tmp_path) == ["heat3d-gamefiles", "ue-map", "G", "M"]
    assert tasks["ue-maps"].argv({"game": "G"}, tmp_path) == ["heat3d-gamefiles", "ue-maps", "G"]
    for t in spec.tasks:
        assert t.argv({i.key: "x" for i in t.inputs}, tmp_path)[0] in spec.tools


def test_check_and_status(capsys):
    spec = standalone_spec.SPEC
    assert entry.main(spec, ["--check", "--json"]) == 0
    ids = [c["id"] for c in json.loads(capsys.readouterr().out)["checks"]]
    assert ids == ["oodle", "disk"]
    assert entry.main(spec, ["status", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["games"] == []


def test_a_tool_runs_through_the_app(tmp_path, capsys):
    f = tmp_path / "x.bin"
    f.write_bytes(b"\0" * 16)
    assert entry.main(standalone_spec.SPEC, ["heat3d-gamefiles", "identify", str(f)]) == 0
    assert capsys.readouterr().out.strip()


def test_update_startup_asks_through_the_app(monkeypatch, capsys):
    import heat3d_update

    t = heat3d_update.target()
    assert t.tool_id == "heat3d-gamefiles" and t.repo == "Holdi601/3DHeat-GameFiles"
    seen = []
    monkeypatch.setattr(update, "startup", lambda target, ask=None: seen.append((target.tool_id, ask)))
    heat3d_update.startup("heat3d_gamefiles", ask=False)
    assert seen == [("heat3d-gamefiles", False)]
