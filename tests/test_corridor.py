"""
The band either side of the driving that an export keeps.

For a circuit it and the bounding box are nearly the same thing; for a sprint
the box is ten times larger, and every square metre of it outside the band is
hillside decoded, textured and written for nothing.
"""

from __future__ import annotations

import numpy as np
import pytest

from heat3d_gamefiles.corridor import Corridor



def straight(length=1000.0, step=5.0):
    """Driving due east along z = 0."""
    x = np.arange(0.0, length + step, step)
    return np.stack([x, np.zeros_like(x), np.zeros_like(x)], axis=1)


class TestTheBand:
    def test_within_the_margin_is_in_and_beyond_it_is_out(self):
        band = Corridor(straight(), 80.0)
        inside = band.contains(np.array([[500.0, 0.0], [500.0, 70.0], [500.0, -70.0]]))
        outside = band.contains(np.array([[500.0, 100.0], [500.0, -100.0], [1200.0, 0.0]]))
        assert inside.all() and not outside.any()

    def test_three_dimensional_points_are_read_in_the_ground_plane(self):
        band = Corridor(straight(), 80.0)
        assert band.contains(np.array([[500.0, 999.0, 10.0]])).all()

    def test_its_area_is_the_line_times_twice_the_margin(self):
        band = Corridor(straight(), 80.0)
        # 1 km of line, 160 m wide, plus the rounded ends; the grid adds a cell.
        assert 1000 * 160 <= band.area <= 1000 * 160 + np.pi * 88**2 + 1000 * 16

    def test_a_box_touches_it_or_does_not(self):
        band = Corridor(straight(), 80.0)
        assert band.touches((400.0, -10.0), (600.0, 10.0))
        assert not band.touches((400.0, 200.0), (600.0, 400.0))
        assert not band.touches((5000.0, 0.0), (5100.0, 10.0))

    def test_a_big_triangle_across_the_band_is_kept_by_its_middle(self):
        """Every corner outside, the band running through it: a hole if dropped."""
        band = Corridor(straight(), 20.0)
        points = np.array([[450.0, 0.0, -200.0], [550.0, 0.0, -200.0], [500.0, 0.0, 200.0]])
        assert band.triangles(points, np.array([[0, 1, 2]])).all()

    def test_samples_a_little_apart_are_joined(self):
        """Forty metres between samples, a ten-metre band: the middle is still in."""
        band = Corridor(np.array([[0.0, 0.0, 0.0], [40.0, 0.0, 0.0]]), 10.0)
        assert band.contains(np.array([[20.0, 0.0]])).all()

    def test_the_seam_between_two_laps_is_not_driving(self):
        """The finish of one sprint and the start of the next are not a road."""
        band = Corridor(np.array([[0.0, 0.0, 0.0], [3000.0, 0.0, 0.0]]), 80.0)
        assert not band.contains(np.array([[1500.0, 0.0]])).any()
        assert band.contains(np.array([[0.0, 0.0], [3000.0, 0.0]])).all()

    def test_no_driving_is_an_error(self):
        with pytest.raises(ValueError):
            Corridor(np.zeros((0, 3)), 80.0)
