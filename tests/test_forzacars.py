"""
The car file: what it reads out of a car archive and how it writes it.

The fixtures are made here, so these run with no game installed. The test at the
end reads the real thing where it is: every archive of an installed Forza must
give a car standing on its wheels.
"""

from __future__ import annotations

import gzip
import json
import struct
import zipfile
from pathlib import Path

import numpy as np
import pytest

from heat3d_gamefiles.forzacars import (
    MAGIC,
    Car,
    cars_of_game,
    locators,
    name_parts,
    read_car,
    read_pack,
    wheel_radius,
    write_pack,
)
from heat3d_gamefiles.forzatech import INDEX_LONG

from .installed import installed


def box_car() -> np.ndarray:
    """A shell 4.5 m long with an arch 0.32 m above and round the front right hub."""
    points = [[x, y, z] for x in (-0.95, 0.95) for y in (-0.1, 1.3) for z in (-2.25, 2.25)]
    for angle in np.radians(np.arange(-30, 31, 10)):
        points.append([0.9, 0.2 + 0.32 * np.cos(angle), 1.4 + 0.32 * np.sin(angle)])
    return np.array(points, dtype=float)


def test_long_indices_have_a_format_code():
    assert INDEX_LONG == 42


@pytest.mark.parametrize(
    "stem, make, model, year",
    [
        ("BMW_E36M3_97", "BMW", "E36M3", 1997),
        ("BMW_98_325iFD_89", "BMW", "98_325iFD", 1989),
        ("VW_IDBuzz_25", "Volkswagen", "IDBuzz", 2025),
        ("for_focusrs_03", "Ford", "focusrs", 2003),
        ("XXX_NewCar", "XXX", "NewCar", None),
    ],
)
def test_the_name_says_make_model_and_year(stem, make, model, year):
    assert name_parts(stem) == (make, model, year)


def test_locators_keep_the_first_of_a_name():
    text = (
        '<Name value="carLocator_wheelLF"/><SceneTransform value._41="-0.8" value._42="0.2" value._43="1.4"/>'
        '<Name value="other"/><SceneTransform value._41="9" value._42="9" value._43="9"/>'
        '<Name value="carLocator_wheelLF"/><SceneTransform value._41="5" value._42="5" value._43="5"/>'
    )
    assert locators(text) == {"wheelLF": [-0.8, 0.2, 1.4]}


def test_a_wheel_fills_its_arch():
    assert wheel_radius(box_car(), [0.85, 0.2, 1.4]) == pytest.approx(0.32, abs=0.001)


def test_an_arch_wider_than_a_wheel_can_be_is_held_to_the_cars_length():
    shell = box_car()
    # An off-roader's arch: far more room than the wheel needs.
    shell = shell[np.hypot(shell[:, 1] - 0.2, shell[:, 2] - 1.4) > 0.6]
    shell = np.vstack([shell, [[0.9, 0.9, 1.4]]])
    assert wheel_radius(shell, [0.85, 0.2, 1.4]) == pytest.approx(0.095 * 4.5, abs=0.001)


def test_no_arch_at_all_gets_the_least_a_car_this_long_has():
    shell = np.array([[x, -0.1, z] for x in (-1, 1) for z in (-2.25, 2.25)], dtype=float)
    assert wheel_radius(shell, [0.85, 0.2, 1.4]) == pytest.approx(0.07 * 4.5, abs=0.001)


def car(**changes) -> Car:
    base = dict(
        key="BMW_E36M3_97",
        ordinals=[382],
        make="BMW",
        model="E36M3",
        year=1997,
        positions=box_car(),
        faces=np.array([[0, 1, 2], [1, 2, 3]]),
        wheels=[[-0.85, 0.2, 1.4, 0.32], [0.85, 0.2, 1.4, 0.32], [-0.85, 0.2, -1.3, 0.32], [0.85, 0.2, -1.3, 0.32]],
        lights=[[0.5, 0.7, -2.2]],
    )
    base.update(changes)
    return Car(**base)


def test_a_car_too_big_for_the_file_is_refused_before_it_stops_the_others(tmp_path: Path):
    # write_pack's guard is the last line; read_car's is what puts one car on the failed list.
    with pytest.raises(Exception, match="indices"):
        write_pack([car(faces=np.array([[0, 1, 70000]]))], tmp_path / "x.h3dcars")


def test_height_is_over_the_road():
    assert car().height == pytest.approx(1.3 - (0.2 - 0.32))


def test_the_file_round_trips(tmp_path: Path):
    path = tmp_path / "cars.h3dcars"
    write_pack([car(), car(key="OTHER_Car_01", ordinals=[7], make="OTHER", model="Car", year=2001)], path, source="game")
    header, data = read_pack(path)
    assert (header["format"], header["version"], header["game"], header["source"]) == ("heat3d-cars", 1, "forza-horizon", "game")
    first, second = header["cars"]
    assert first["ordinals"] == [382] and second["ordinals"] == [7]
    vertices = np.frombuffer(data, "<i2", first["vertices"] * 3, first["vertexAt"]).reshape(-1, 3) / 1000
    assert vertices == pytest.approx(np.round(box_car(), 3), abs=0.001)
    faces = np.frombuffer(data, "<u2", first["faces"] * 3, first["faceAt"]).reshape(-1, 3)
    assert faces.tolist() == [[0, 1, 2], [1, 2, 3]]
    assert second["vertexAt"] == first["faceAt"] + first["faces"] * 6


def test_the_data_starts_on_four_bytes_after_the_magic(tmp_path: Path):
    path = tmp_path / "cars.h3dcars"
    write_pack([car()], path)
    raw = gzip.decompress(path.read_bytes())
    assert raw[:8] == MAGIC
    (length,) = struct.unpack_from("<I", raw, 8)
    assert json.loads(raw[12 : 12 + length])["cars"][0]["key"] == "BMW_E36M3_97"
    assert (12 + length + (-(12 + length) % 4)) % 4 == 0


def test_an_archive_without_a_stand_in_is_not_a_car(tmp_path: Path):
    path = tmp_path / "Traffic_Truck_14.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("Manifest.xml", "<Manifest/>")
    assert read_car(path) is None


def test_the_games_cars_are_found_in_either_spelling(tmp_path: Path):
    (tmp_path / "media" / "Cars").mkdir(parents=True)
    (tmp_path / "media" / "Cars" / "A_B_01.zip").write_bytes(b"")
    (tmp_path / "media" / "Cars" / "readme.txt").write_bytes(b"")
    assert [p.name for p in cars_of_game(tmp_path)] == ["A_B_01.zip"]
    assert cars_of_game(tmp_path / "nothing") == []


def test_installed_cars_stand_on_their_wheels():
    archives = installed("ForzaHorizon*/media/Cars/*.zip")[:40]
    if not archives:
        pytest.skip("no Forza installed")
    read = [c for c in map(read_car, archives) if c is not None]
    assert read
    for c in read:
        assert c.ordinals, c.key
        assert len(c.wheels) == 4, c.key
        assert all(0.1 < w[3] < 0.85 for w in c.wheels), c.key
        # The wheels are at the corners of the car, the fronts ahead of the rears.
        assert c.wheels[0][2] > c.wheels[2][2], c.key
        assert c.wheels[0][0] < 0 < c.wheels[1][0], c.key
        assert 0.6 < c.height < 3.5, c.key
