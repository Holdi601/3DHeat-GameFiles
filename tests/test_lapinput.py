"""
Taking a lap in whatever shape the caller has it.

Four tools in this project write a driven line and they all write it
differently — two route formats, a recorded library's own per-lap files, and the
table the viewer ingests. Converting between them by hand before asking for a
piece of map is exactly the friction this removes, so the tests are mostly about
accepting each one and getting the same answer from all of them.

The one that is not about accepting is the box. It is drawn in the plane and
never in height, and that is not a detail: a lap is a line, and cutting terrain
to a line's altitude range removes the ground under any hill the road climbs.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from heat3d_gamefiles.lapinput import (
    Driven,
    UnreadableLap,
    find_recorded_course,
    read,
    read_file,
    read_folder,
)

#: A few metres of a lap, in the game's own world coordinates.
POINTS = [
    [1184.9712, 461.6221, 3394.9365],
    [1190.1208, 462.07178, 3396.732],
    [1195.1418, 462.50894, 3398.4834],
]


def route_file(path, points=POINTS):
    path.write_text(
        json.dumps(
            {
                "layout": "forza",
                "bounds": {
                    "min": np.min(points, axis=0).tolist(),
                    "max": np.max(points, axis=0).tolist(),
                },
                "positions": points,
            }
        ),
        encoding="utf-8",
    )
    return path


def library_lap(path, points=POINTS):
    """As the recorded library writes one, byte-order mark and all."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "﻿"
        + json.dumps(
            {
                "Course": "course_1200_3400_to_1175_3400",
                "Class": "A",
                "Lap": {
                    "lapSeconds": 47.737,
                    "samples": [
                        {"X": x, "Y": y, "Z": z, "Speed": 60.0} for x, y, z in points
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    return path


class TestEveryShapeOfLap:
    def test_a_route_file(self, tmp_path):
        driven = read_file(route_file(tmp_path / "lap.json"))

        assert np.allclose(driven, POINTS)

    def test_a_lap_from_the_recorded_library(self, tmp_path):
        driven = read_file(library_lap(tmp_path / "47.737s.json"))

        assert np.allclose(driven, POINTS)

    def test_a_recording(self, tmp_path):
        path = tmp_path / "lap.npz"
        np.savez(path, positions=np.array(POINTS), times=np.arange(3.0))

        assert np.allclose(read_file(path), POINTS)

    def test_a_table_with_x_y_and_z(self, tmp_path):
        """The CSV the viewer eats, so a course exported for analysis can be
        handed straight back to ask for the ground under it."""
        path = tmp_path / "samples.csv"
        rows = "\n".join(f"Mapletree,{x},{y},{z},220" for x, y, z in POINTS)
        path.write_text(f"course,x,y,z,speed_kmh\n{rows}\n", encoding="utf-8")

        assert np.allclose(read_file(path), POINTS)

    def test_a_route_file_that_carries_only_its_bounds(self, tmp_path):
        """Two corners are a degenerate line and a perfectly good box, which is
        all the extractor wants."""
        path = tmp_path / "lap.json"
        path.write_text(
            json.dumps({"bounds": {"min": [0, 10, 0], "max": [100, 20, 50]}}),
            encoding="utf-8",
        )

        points = read_file(path)

        assert points.shape == (2, 3)

    def test_a_folder_gathers_every_lap_in_it(self, tmp_path):
        """A course in the recorded library is a tree - class, car, tune, tag -
        and nobody should have to know its shape."""
        library_lap(tmp_path / "A" / "car382" / "tune" / "untagged" / "a.json")
        library_lap(
            tmp_path / "R" / "car4212" / "tune" / "untagged" / "b.json",
            points=[[1400.0, 470.0, 3500.0]] * 3,
        )

        points, laps = read_folder(tmp_path)

        assert laps == 2
        assert len(points) == 6
        assert points[:, 0].max() == pytest.approx(1400.0)

    def test_the_metadata_beside_the_laps_is_not_one(self, tmp_path):
        library_lap(tmp_path / "A" / "car1" / "t" / "untagged" / "a.json")
        (tmp_path / "course.json").write_text(
            json.dumps({"Name": "Mapletree Test Loop", "StartX": 1188.0}), encoding="utf-8"
        )

        _points, laps = read_folder(tmp_path)

        assert laps == 1

    def test_one_unreadable_file_does_not_cost_the_folder(self, tmp_path):
        library_lap(tmp_path / "A" / "car1" / "t" / "untagged" / "good.json")
        (tmp_path / "A" / "broken.json").write_text("not json", encoding="utf-8")

        _points, laps = read_folder(tmp_path)

        assert laps == 1


def labelled_lap(path, game, points=POINTS):
    """A `heat3d-lap` document, which names its game."""
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = np.asarray(points).T.tolist()
    path.write_text(
        json.dumps({"format": "heat3d-lap", "game": game, "channels": dict(zip("xyz", columns))}),
        encoding="utf-8",
    )
    return path


class TestWhichGameAFolderIs:
    def test_the_game_its_laps_name(self, tmp_path):
        labelled_lap(tmp_path / "a.json", "beamng")
        labelled_lap(tmp_path / "b" / "c.json", "beamng")

        assert read(tmp_path).game == "beamng"

    def test_a_file_that_names_no_game_does_not_vote(self, tmp_path):
        labelled_lap(tmp_path / "a.json", "assetto-corsa-rally")
        # Metadata, and a table without its description line: neither says.
        (tmp_path / "course.json").write_text(json.dumps({"Name": "Example Stage"}), encoding="utf-8")
        (tmp_path / "b.csv").write_text("x,y,z\n1,2,3\n4,5,6\n", encoding="utf-8")

        driven = read(tmp_path)

        assert driven.game == "assetto-corsa-rally"
        assert driven.laps == 2

    def test_two_games_are_a_mix_and_say_nothing(self, tmp_path):
        labelled_lap(tmp_path / "a.json", "beamng")
        labelled_lap(tmp_path / "b.json", "assetto-corsa-rally")

        assert read(tmp_path).game is None

    def test_a_folder_where_nothing_names_a_game_has_none(self, tmp_path):
        library_lap(tmp_path / "A" / "car1" / "t" / "untagged" / "a.json")

        assert read(tmp_path).game is None


class TestTheBoxItCuts:
    def test_the_margin_widens_the_plane(self):
        driven = Driven(name="x", positions=np.array(POINTS))

        low, high = driven.box(80.0)

        assert low[0] == pytest.approx(1184.9712 - 80.0)
        assert high[1] == pytest.approx(3398.4834 + 80.0)

    def test_height_is_never_bounded(self):
        """
        A lap is a line. Cutting terrain to its altitude range would remove the
        ground under a hill the road climbs — which on a course with 55 m of
        climb is most of what someone wants to look at.
        """
        driven = Driven(name="x", positions=np.array(POINTS))

        low, high = driven.box(80.0)

        assert len(low) == 2 and len(high) == 2

    def test_the_distance_driven_is_along_the_line(self):
        driven = Driven(
            name="x", positions=np.array([[0.0, 0, 0], [3.0, 0, 4.0], [3.0, 0, 8.0]])
        )

        assert driven.metres == pytest.approx(9.0)


class TestWhenItCannot:
    def test_a_file_that_is_not_a_lap_says_what_it_takes(self, tmp_path):
        path = tmp_path / "notes.md"
        path.write_text("# hello", encoding="utf-8")

        with pytest.raises(UnreadableLap, match="course's name"):
            read_file(path)

    def test_json_without_positions(self, tmp_path):
        path = tmp_path / "other.json"
        path.write_text(json.dumps({"hello": "world"}), encoding="utf-8")

        with pytest.raises(UnreadableLap, match="neither"):
            read_file(path)

    def test_a_recording_missing_its_positions(self, tmp_path):
        path = tmp_path / "lap.npz"
        np.savez(path, times=np.arange(3.0))

        with pytest.raises(UnreadableLap, match="no `positions`"):
            read_file(path)

    def test_an_empty_folder(self, tmp_path):
        with pytest.raises(UnreadableLap, match="no readable laps"):
            read_folder(tmp_path)


class TestLookingACourseUpByName:
    @pytest.fixture
    def shelf(self, tmp_path):
        root = tmp_path / "laps"
        for name in (
            "Mapletree Test Loop (course_1200_3400_to_1175_3400)",
            "Harbour Chase (course_-300_-2200_to_-200_-1200)",
            "Harbour Circuit (course_-150_-2100_to_-150_-2100)",
        ):
            library_lap(root / name / "A" / "car1" / "t" / "untagged" / "a.json")
        return root

    def test_the_coordinates_in_the_folder_name_can_be_ignored(self, shelf):
        found = find_recorded_course("Mapletree Test Loop", shelf)

        assert found.name.startswith("Mapletree Test Loop")

    def test_a_partial_name_works_when_it_is_unambiguous(self, shelf):
        assert find_recorded_course("mapletree", shelf).name.startswith("Mapletree")

    def test_an_ambiguous_name_lists_what_it_matched(self, shelf):
        with pytest.raises(UnreadableLap, match="Harbour Chase, Harbour Circuit"):
            find_recorded_course("harbour", shelf)

    def test_a_name_that_matches_nothing(self, shelf):
        with pytest.raises(UnreadableLap, match="no course"):
            find_recorded_course("Nurburgring", shelf)

    def test_read_takes_a_path_before_a_name(self, tmp_path):
        """A file that exists is that file, even if something in the library
        happens to share its name."""
        path = route_file(tmp_path / "lap.json")

        driven = read(path)

        assert driven.laps == 1
        assert np.allclose(driven.positions, POINTS)

    def test_the_name_loses_the_coordinates_glued_to_it(self, tmp_path):
        folder = tmp_path / "Mapletree Test Loop (course_1200_3400_to_1175_3400)"
        library_lap(folder / "A" / "car1" / "t" / "untagged" / "a.json")

        assert read(folder).name == "Mapletree Test Loop"
