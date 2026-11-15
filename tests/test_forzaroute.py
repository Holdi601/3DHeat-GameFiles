"""
Races: the game's routes, matching a lap to one, and what a route adds to and
takes from the world. Synthetic files; nothing here needs the game.
"""

from __future__ import annotations

import struct
import zipfile
from pathlib import Path

import numpy as np

from heat3d_gamefiles import forzaroute
from heat3d_gamefiles.forzaplacement import (
    EVENT_PART,
    LAYER_PART,
    VENUE_PART,
    _Hidden,
    fallback_colour,
    layer_of,
    routes_of,
    world_part,
)
from heat3d_gamefiles.forzaroute import (
    Route,
    defined_routes,
    instance_models,
    match,
    read_definition,
    read_route,
    read_routes,
    route_assets,
)


def owt(points) -> bytes:
    """An AI route file: the header, then a 56-byte node per point."""
    head = bytearray(forzaroute.NODES_AT)
    head[0:4] = forzaroute.MAGIC
    struct.pack_into("<I", head, forzaroute.COUNT_AT, len(points))
    body = b"".join(struct.pack("<3f", *p) + bytes(forzaroute.NODE - 12) for p in points)
    return bytes(head) + body + bytes(24)


def loop(cx, cz, radius, n=200):
    angle = np.linspace(0, 2 * np.pi, n)
    return np.stack([cx + radius * np.cos(angle), np.full(n, 100.0), cz + radius * np.sin(angle)], axis=1)


class TestRoutes:
    def test_nodes_are_positions(self):
        route = read_route(owt([(1, 2, 3), (4, 5, 6)]), 7)
        assert route.id == 7
        assert route.points.tolist() == [[1, 2, 3], [4, 5, 6]]

    def test_unreadable_nodes_are_dropped(self):
        route = read_route(owt([(1, 2, 3), (float("nan"), 0, 0), (1e30, 0, 0), (4, 5, 6)]))
        assert len(route.points) == 2

    def test_not_a_route_file(self):
        try:
            read_route(b"nope" + bytes(200))
        except ValueError:
            return
        raise AssertionError("read a file that is not a route")

    def test_routes_are_found_beside_the_track(self, tmp_path):
        track = tmp_path / "media" / "Tracks" / "Map"
        track.mkdir(parents=True)
        ai = tmp_path / "media" / "OpenWorld" / "Map" / "AITracks"
        ai.mkdir(parents=True)
        (ai / "Route41.owt").write_bytes(owt(loop(0, 0, 100)))
        (ai / "Route41.nav").write_bytes(b"other")
        assert [r.id for r in read_routes(track)] == [41]

    def test_the_lap_finds_its_own_route(self):
        lap = loop(0, 0, 100, 900) + np.random.default_rng(1).normal(0, 2, (900, 3))
        routes = [Route(1, loop(0, 0, 100)), Route(2, loop(0, 0, 160)), Route(3, loop(500, 0, 100))]
        found, fit = match(lap, routes)
        assert found.id == 1 and fit < 10

    def test_a_sprint_on_part_of_a_long_route_is_not_that_route(self):
        lap = loop(0, 0, 100)[:40]
        found, _fit = match(lap, [Route(1, loop(0, 0, 100))])
        assert found is None


DEFINITION = """<Route>
  <CookedHiddenAssets trackversion="1"><Instances><Entry idx="5" /></Instances></CookedHiddenAssets>
  <HiddenAssets>
    <Transform guid="AAAA-1" value="1 0 0 0 0 1 0 0 0 0 1 0 10 20 30 1" cooked="true" />
    <Transform guid="bbbb-2" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1" cooked="true" />
  </HiddenAssets>
  <RouteAssets>
    <Instance Version="8">
      <Name value="g1" shortname="wall" />
      <Model value="tracks\\map\\scene\\models\\barriers\\festival\\wall_a\\wall_a.model" />
      <Transform value="0 0 2 0 0 1 0 0 -1 0 0 0 100 5 -200 1" />
      <Material value="3" />
    </Instance>
    <Instance Version="8">
      <Name value="g2" shortname="crowd" />
      <Model value="tracks\\map\\scene\\models\\crowd_proxies\\for_race_grand.model" />
      <Transform value="1 0 0 0 0 1 0 0 0 0 1 0 1 1 1 1" />
    </Instance>
    <Instance Version="8">
      <Name value="g3" shortname="spline" />
      <Model value="tracks\\map\\scene\\0000-1111.splinecol" />
      <Transform value="1 0 0 0 0 1 0 0 0 0 1 0 1 1 1 1" />
    </Instance>
  </RouteAssets>
</Route>"""


class TestRouteDefinitions:
    def test_added_models_become_placements(self):
        assets = read_definition(DEFINITION, 6)
        assert assets.id == 6 and list(assets.models) == ["wall_a"]
        row = assets.models["wall_a"][0]
        # Rows of the transform are the axes, scaled, then the position.
        assert row[0:3].tolist() == [100, 5, -200]
        assert row[3:6].tolist() == [0, 0, 1]
        assert row[6:9].tolist() == [0, 1, 0]
        assert row[9:12].tolist() == [2, 1, 1]
        assert row[12] == 3
        assert assets.kinds["wall_a"] == "barriers"

    def test_spectators_and_collision_are_counted_not_drawn(self):
        assets = read_definition(DEFINITION)
        assert assets.markers == {"crowd_proxies": 1, "splinecol": 1}
        assert assets.copies == 1

    def test_hidden_assets_keep_their_position_and_id(self):
        assets = read_definition(DEFINITION)
        assert assets.hidden.tolist() == [[10, 20, 30], [0, 0, 0]]
        assert assets.hidden_ids == ["aaaa-1", "bbbb-2"]

    def test_definitions_are_found_and_read_from_their_zip(self, tmp_path):
        track = tmp_path / "media" / "Tracks" / "Map"
        track.mkdir(parents=True)
        gs = tmp_path / "media" / "Stripped" / "gs" / "map"
        gs.mkdir(parents=True)
        with zipfile.ZipFile(gs / "routedefinitions.zip", "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("route6_map.rtd", DEFINITION)
            z.writestr("readme.txt", "x")
        assert defined_routes(track) == {6: "route6_map.rtd"}
        assert route_assets(track, 6).copies == 1
        assert route_assets(track, 7) is None

    def test_instance_ids_name_their_model(self, tmp_path):
        (tmp_path / "AssetManifest.xml").write_text(
            "<Models>\n"
            '  <Model Name="a.modelbin" >\n'
            '    <Mesh Name="n/a" Source="tracks\\map\\scene\\models\\plots\\lawn_a\\lawn_a.max" />\n'
            '    <Instance Id="BBBB-2" Ribbon="0" Index="1" />\n'
            "  </Model>\n</Models>\n",
            encoding="utf-8",
        )
        assert instance_models(tmp_path, ["bbbb-2", "cccc-3"]) == {"bbbb-2": "lawn_a"}


class TestLayers:
    def test_the_free_roam_world_has_no_layer(self):
        for name in ("c200_props_do.pgeo", "c50_buildings_do_119.pgeo", "c100_bushes_ulc.pgeo", "c100_signs_a.pgeo"):
            assert layer_of(name) == "", name

    def test_switched_on_layers_are_named(self):
        assert layer_of("c200_props_do_rt_0_discount_board_xp_a_054.pgeo") == "rt_0_discount_board_xp_a"
        assert layer_of("c200_barriers_do_rt_0.pgeo") == "rt_0"
        assert layer_of("c100_bushes_rt_1_ulc.pgeo") == "rt_1"
        assert layer_of("c200_props_do__tag_drift_zone_04_.pgeo") == "tag_drift_zone_04"
        assert layer_of("c100_evolving_world_do.pgeo") == "evolving_world"

    def test_a_race_layer_names_its_routes(self):
        layer = layer_of("x\\c300_crowdtemplate_cwd_rt_x1023_x2201.pgeo")
        assert layer == "rt_x1023_x2201"
        assert routes_of(layer) == {1023, 2201}
        assert routes_of("rt_0") == set()

    def test_layer_parts_take_their_category_colour(self):
        assert fallback_colour(EVENT_PART.format("barriers")) == fallback_colour("structure:barriers")
        assert fallback_colour(LAYER_PART.format("props")) == fallback_colour("structure:props")


class TestWorldModels:
    def test_a_venue_and_a_plinth_are_ground(self):
        assert world_part("plots", "plt_stadium_01_a") == VENUE_PART
        assert world_part("plinths", "plnth_plaza_01") == "ground:plinths"
        assert world_part("models", "tunnel_floor_01_a") == "ground:plinths"

    def test_bridges_and_the_rest(self):
        assert world_part("hda_infrastructure", "ps_bridge_tool_bridge_0_0_ab") == "structure:bridges"
        assert world_part("rocks", "roc_comp_a") == "structure:rocks"

    def test_what_is_not_drawn(self):
        assert world_part("hda_cables", "cbl_generate_cables_x") is None
        assert world_part("hda_buildings", "pb_generate_modular_building_roof") is None
        assert world_part("models", "ocean_vista") is None
        assert world_part("collision", "occ_shl_x") is None


class TestHidden:
    def test_a_copy_where_a_hidden_one_stands_is_it(self):
        hidden = _Hidden(np.array([[-1000.31, 50.91, -2000.4], [1, 2, 3]]))
        near = hidden.near(np.array([[-1000.36, 50.95, -2000.35], [-1000.6, 50.91, -2000.4], [1.04, 2, 3]]))
        assert near.tolist() == [True, False, True]

    def test_nothing_hidden(self):
        hidden = _Hidden(np.zeros((0, 3)))
        assert len(hidden) == 0
        assert not hidden.near(np.zeros((2, 3))).any()


def test_course_files_name_two_courses_of_one_name_apart(tmp_path):
    import time

    from heat3d_gamefiles.cli import _course_files

    first = tmp_path / "Ring (course_100_200_to_105_200)"
    later = tmp_path / "Ring (course_-300_-400_to_-300_-400)"
    other = tmp_path / "Other (course_1_2_to_3_4)"
    for folder in (first, later, other):
        folder.mkdir()
        time.sleep(0.05)
    courses = sorted([first, later, other])
    targets = {c.name: t.name for c, t in _course_files(courses, tmp_path / "out")}
    # Recorded first keeps the name, though it sorts second.
    assert targets[first.name] == "ring.glb"
    assert targets[later.name] == "ring_m300_m400.glb"
    assert targets[other.name] == "other.glb"


def test_course_format_is_read_from_the_file(tmp_path):
    from heat3d_gamefiles.cli import COURSE_FORMAT, course_format
    from heat3d_gamefiles.glb import write_glb

    positions = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 1]], dtype=np.float32)
    faces = np.array([[0, 1, 2]], dtype=np.int32)
    old = write_glb(tmp_path / "old.glb", positions, faces)
    new = write_glb(tmp_path / "new.glb", positions, faces, extras={"course_format": COURSE_FORMAT})
    assert course_format(old) == 0
    assert course_format(new) == COURSE_FORMAT
    assert course_format(tmp_path / "missing.glb") == 0
