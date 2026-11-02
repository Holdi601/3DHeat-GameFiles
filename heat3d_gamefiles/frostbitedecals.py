"""
Frostbite terrain decals: the roads, asphalt, concrete aprons and painted
markings the game draws over the terrain, and a ground texture baked from them.

The TerrainDecals res
---------------------
One res per terrain (type 0x15E1F32E). Nothing about it is documented; every
field below was measured on a level's 10 MB res and checked as noted::

    +16          slot count n (55), then n 16-byte slots
    20 + 16n     record count (926)
    records      variable length, one per draw batch, back to back
    vertices     32 bytes each: x, z (f32), 8 packed bytes, u, v (f32),
                 r, g, b, a (f16)
    the rest     u32 indices, which only count up within each batch; the
                 batches are plain triangle lists and are drawn from the
                 vertices directly

A record begins with 156 bytes of fixed fields — at +32 its first vertex, at
+36 its triangle count, at +44 its texture tiling in metres — then its vertex
range in bytes at +156 (offset, size), then a tail of variable length naming,
among other things, the batch's textures by their asset's partition GUID: a
colour map (`_cv`), an opacity map (`_op`, its red channel), normal and
occlusion maps, or for painted markings a channel mask (`_rgb`).

The checks that hold the reading together:

- the records' vertex ranges follow each other without gap or overlap and
  cover the vertex block exactly — 926 of 926 records, 265,794 vertices;
- each record's first vertex times 32 is its byte offset, and its triangle
  count times 96 its byte size;
- the vertex block's start is where world-mapped batches have u = x and v = z
  in the same vertex, which is how their textures are laid on the ground; of
  the starts that score so, a whole vertex either way splits every triangle
  across its neighbours, which the triangles' size gives away, and a whole
  triangle earlier begins in record bytes, whose "colours" are not 0 to 1;
- triangles drawn from the vertices so read are compact decals — painted
  letters, strips of road line, patches of asphalt; read one slot later they
  are slivers reaching across the map.

The texture coordinates are either the world position (a tiling surface,
asphalt or concrete, the texture repeating every tiling-metres) or 0 to 1
across the decal (a line, a letter, a tyre track). Records are drawn in file
order, later ones over earlier ones.

What is not read: the materials' colour parameters. A marking drawn through a
channel mask (`_rgb`) has its paint colour in the material, so it is baked in
a neutral colour — white for lines and letters, dark for outlines and wear.
"""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass, field

import numpy as np

from .frostbite import UnsupportedFrostbite

TERRAIN_DECALS = 0x15E1F32E

VERTEX = np.dtype(
    [("x", "<f4"), ("z", "<f4"), ("packed", "<u8"), ("u", "<f4"), ("v", "<f4"), ("rgba", "<f2", 4)]
)
_CORE = 156


@dataclass
class Batch:
    first: int
    triangles: int
    tiling: float
    textures: list[str] = field(default_factory=list)

    def texture(self, suffix: str) -> str | None:
        for name in self.textures:
            if name.lower().endswith(suffix):
                return name
        return None


@dataclass
class Decals:
    vertices: np.ndarray
    batches: list[Batch]


def read_decals(res: bytes, texture_guids: dict[bytes, str], name: str = "decals") -> Decals:
    """
    The batches and vertices of a TerrainDecals res. `texture_guids` maps a
    texture asset's partition GUID to its name.
    """
    if len(res) < 24:
        raise UnsupportedFrostbite(f"{name}: too short for terrain decals")
    (slots,) = struct.unpack_from("<I", res, 16)
    at = 20 + 16 * slots
    if at + 4 > len(res):
        raise UnsupportedFrostbite(f"{name}: {slots} slots run past the end")
    (count,) = struct.unpack_from("<I", res, at)
    at += 4

    starts: list[int] = []
    first = 0
    offset = 0
    limit = len(res)
    for k in range(count):
        found = None
        for s in range(at, min(at + 8192, limit - _CORE - 8)):
            f, n = struct.unpack_from("<II", res, s + 32)
            if f != first or n == 0:
                continue
            o, size = struct.unpack_from("<II", res, s + _CORE)
            if o == offset and size == 96 * n:
                found = s
                break
        if found is None:
            raise UnsupportedFrostbite(
                f"{name}: record {k} of {count} is not where the previous one says"
            )
        starts.append(found)
        n = struct.unpack_from("<I", res, found + 36)[0]
        first += 3 * n
        offset += 96 * n
        at = found + _CORE + 8
    total = first

    # The vertex block: after the last record, where world-mapped batches
    # carry their own position as texture coordinates.
    scores = []
    for start in range(at, min(at + 4096, len(res) - 32 * total) + 1):
        block = np.frombuffer(res, dtype=VERTEX, count=min(total, 1024), offset=start)
        with np.errstate(all="ignore"):
            real = (np.abs(block["x"]) > 1) & (np.abs(block["x"]) < 1e5) & (np.abs(block["z"]) < 1e5)
            scores.append((np.mean(real & (block["u"] == block["x"]) & (block["v"] == block["z"])), start))
    top = max(scores)[0] if scores else 0
    if top < 0.01:
        raise UnsupportedFrostbite(f"{name}: no vertex block where one should start")
    # A start a whole vertex earlier or later scores as well, but then every
    # triangle takes a corner from its neighbour: the true start is the one
    # whose triangles are smallest.
    def spread(start: int) -> float:
        n = min(total, 3 * 3000) // 3 * 3
        block = np.frombuffer(res, dtype=VERTEX, count=n, offset=start)
        with np.errstate(all="ignore"):
            p = np.stack([block["x"], block["z"]], 1).astype(np.float64).reshape(-1, 3, 2)
            edge = np.linalg.norm(p - np.roll(p, 1, axis=1), axis=2).max(axis=1)
        return float(np.nanmedian(edge)) if np.isfinite(edge).any() else np.inf

    good = [start for score, start in scores if score >= 0.9 * top]
    phase = min({g % 96 for g in good}, key=lambda r: spread(min(g for g in good if g % 96 == r)))

    # Within that phase a start a whole triangle off is still compact; the
    # block starts at the earliest one whose first vertices are vertices —
    # colour and opacity between 0 and 1, finite positions — not record bytes.
    def plausible(start: int) -> bool:
        head = np.frombuffer(res, dtype=VERTEX, count=3, offset=start)
        with np.errstate(all="ignore"):
            rgba = head["rgba"].astype(np.float32)
            return bool(
                np.isfinite(rgba).all() and (rgba >= 0).all() and (rgba <= 1).all()
                and (np.abs(head["x"]) < 1e5).all() and (np.abs(head["z"]) < 1e5).all()
            )

    first_start = next(
        (g for g in range(min(g for g in good if g % 96 == phase) % 96 + at - at % 96, at + 4097, 96)
         if g >= at and plausible(g)),
        None,
    )
    if first_start is None:
        raise UnsupportedFrostbite(f"{name}: no vertex block where one should start")
    best = (top, first_start)
    vertices = np.frombuffer(res, dtype=VERTEX, count=total, offset=best[1]).copy()

    batches: list[Batch] = []
    for k, s in enumerate(starts):
        f, n = struct.unpack_from("<II", res, s + 32)
        (tiling,) = struct.unpack_from("<f", res, s + 44)
        end = starts[k + 1] if k + 1 < len(starts) else best[1]
        tail = res[s + _CORE + 8 : end]
        names = []
        for p in range(0, max(0, len(tail) - 15)):
            hit = texture_guids.get(tail[p : p + 16])
            if hit and hit not in names:
                names.append(hit)
        batches.append(Batch(f, n, tiling if tiling > 0 else 1.0, names))
    return Decals(vertices, batches)


#: How a marking drawn through a channel mask is painted, for want of the
#: material's own colour: (pattern, colour, strength). Wear and tyre marks
#: are a faint darkening, an outline a dark one, anything else white paint.
MASK_PAINT = (
    (re.compile(r"wear|track|dirt|patch", re.I), (0.25, 0.23, 0.20), 0.35),
    (re.compile(r"outline", re.I), (0.15, 0.15, 0.15), 1.0),
    (re.compile(r"", re.I), (0.92, 0.92, 0.90), 1.0),
)


@dataclass
class Layer:
    """One batch ready to draw: its colour (image or flat) and opacity."""

    colour: np.ndarray | None
    flat: tuple[float, float, float] | None
    opacity: np.ndarray | None
    world: bool
    tiling: float


def bake(
    decals: Decals,
    layers: list[Layer | None],
    base: np.ndarray,
    origin: tuple[float, float],
    metres: float,
) -> np.ndarray:
    """
    Composite every batch over `base` (H x W x 3, floats 0..1), whose pixel
    (row r, column c) is centred on world x = origin[0] + (c + 0.5) * metres,
    z = origin[1] + (r + 0.5) * metres.
    """
    out = base.copy()
    h, w = out.shape[:2]
    v = decals.vertices
    for batch, layer in zip(decals.batches, layers):
        if layer is None:
            continue
        tri = v[batch.first : batch.first + 3 * batch.triangles].reshape(-1, 3)
        px = (tri["x"] - origin[0]) / metres - 0.5
        pz = (tri["z"] - origin[1]) / metres - 0.5
        lo_c = np.floor(px.min(1)).astype(int)
        hi_c = np.ceil(px.max(1)).astype(int)
        lo_r = np.floor(pz.min(1)).astype(int)
        hi_r = np.ceil(pz.max(1)).astype(int)
        inside = (hi_c >= 0) & (lo_c < w) & (hi_r >= 0) & (lo_r < h)
        for t in np.nonzero(inside)[0]:
            c0, c1 = max(lo_c[t], 0), min(hi_c[t], w - 1)
            r0, r1 = max(lo_r[t], 0), min(hi_r[t], h - 1)
            if c1 < c0 or r1 < r0:
                continue
            cs, rs = np.meshgrid(np.arange(c0, c1 + 1), np.arange(r0, r1 + 1))
            (ax, bx, cx), (az, bz, cz) = px[t], pz[t]
            den = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
            if abs(den) < 1e-12:
                continue
            w0 = ((bz - cz) * (cs - cx) + (cx - bx) * (rs - cz)) / den
            w1 = ((cz - az) * (cs - cx) + (ax - cx) * (rs - cz)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not m.any():
                continue
            k = tri[t]
            u = w0 * k["u"][0] + w1 * k["u"][1] + w2 * k["u"][2]
            vv = w0 * k["v"][0] + w1 * k["v"][1] + w2 * k["v"][2]
            alpha = (
                w0 * float(k["rgba"][0][3]) + w1 * float(k["rgba"][1][3]) + w2 * float(k["rgba"][2][3])
            )
            if layer.world:
                u, vv = u / layer.tiling, vv / layer.tiling
            u, vv, alpha = u[m] % 1.0, vv[m] % 1.0, np.clip(np.broadcast_to(alpha, m.shape)[m], 0, 1)
            if layer.opacity is not None:
                oh, ow = layer.opacity.shape
                alpha = alpha * layer.opacity[(vv * oh).astype(int).clip(0, oh - 1), (u * ow).astype(int).clip(0, ow - 1)]
            if layer.colour is not None:
                ch, cw = layer.colour.shape[:2]
                colour = layer.colour[(vv * ch).astype(int).clip(0, ch - 1), (u * cw).astype(int).clip(0, cw - 1)]
            else:
                colour = np.broadcast_to(np.array(layer.flat), (len(u), 3))
            target = out[r0 : r1 + 1, c0 : c1 + 1]
            target[m] = target[m] * (1 - alpha[:, None]) + colour * alpha[:, None]
    return out
