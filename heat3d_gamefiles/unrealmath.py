"""Unreal's rotations as matrices, shared by the Unreal readers and the games built on them."""

from __future__ import annotations

import math

import numpy as np


def rotator_matrix(pitch: float, yaw: float, roll: float) -> np.ndarray:
    """Unreal's `FRotationMatrix`: rows are the turned axes (row vectors)."""
    p, y, r = (math.radians(v) for v in (pitch, yaw, roll))
    sp, cp, sy, cy, sr, cr = math.sin(p), math.cos(p), math.sin(y), math.cos(y), math.sin(r), math.cos(r)
    return np.array(
        [
            [cp * cy, cp * sy, sp],
            [sr * sp * cy - cr * sy, sr * sp * sy + cr * cy, -sr * cp],
            [-(cr * sp * cy + sr * sy), cy * sr - cr * sp * sy, cr * cp],
        ]
    )
