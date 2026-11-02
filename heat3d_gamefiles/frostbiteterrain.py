"""
A Frostbite level's terrain: the heightfield its streaming tree points at.

The terrain of a level is one resource, the **TerrainStreamingTree**, and a few
hundred chunks it names. The resource holds the terrain's raster trees and, at
its end, the quadtree of streaming nodes; each node names the chunk its rasters
are stored in. Nothing of this is documented, and every step below was measured
on a shipped level and then checked against something independent of it.

The resource
------------
::

    header          34 bytes; little-endian; the node count at 25
    raster trees    each a type byte and a u32 length, then that many bytes,
                    until a type byte of 0xFF
    streaming nodes the quadtree, depth first, to the last byte

The heightfield is raster tree 0. Its header gives the samples per side of a
node's height page (265) and the height range (1,280 m) at +5 and +21; its first
node record, at +76, carries the terrain's bounding box (an 8,192 m square in
the level checked). Tree 0 itself holds only the nodes' bounding boxes and a
min/max pyramid per node — 16 x 16 cells, row-major, each cell the min and max
of the four below it, which closes on every level of it — not the heights.

A streaming node is::

    u32 size, GUID         its chunk
    u8 has-second [u32 size, GUID]   an optional second chunk (colour)
    u8 flags               bit 0: the chunk starts with a height page
    u8 has-children        then four children: (0,0), (1,0), (1,1), (0,1)

The parse consumes the resource to its last byte, which is the check that the
record layout is right.

The height page
---------------
The first `265 x 265` unsigned 16-bit words of a flagged node's chunk, row by
row, height = word x 1,280 / 65,535 metres. Columns run along world x and rows
along world z, from the node's low corner, with a border of four samples on each
side: sample `4 + 256 k / span` is at `k` metres into the node. Every way of
reading it was checked, not chosen:

- neighbouring nodes share nine columns exactly — the last nine of one are the
  first nine of the next — so the stride is 256;
- a child's samples at every other position equal its parent's exactly with a
  border of four and with no other border (a mismatch of 90 to 700 units
  otherwise), which also fixes the child order;
- of the eight ways the terrain square could lie on the world (two axes, two
  signs each), only x along x and z along z, unflipped, puts the level's placed
  objects on it: half of 3,000 copies have their origin within 2.2 m of the
  surface, against 11 m and more for every other way.

The word for the lowest point of the level decodes to the bounding box's lowest
height to the centimetre (2,148 x 1,280 / 65,535 = 41.95 m).

What the rest of a node's chunk holds — 72 x 72 BC4 mask pages, BC7 colour — is
not read here.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field

import numpy as np

from .frostbite import UnsupportedFrostbite

#: The res type, as bundle manifests give it.
STREAMING_TREE = 0x22FE8AC8

HEADER = 34
HEIGHTFIELD = 0
END = 0xFF

#: Samples a height page has outside the node on each side, measured.
BORDER = 4


@dataclass
class Node:
    depth: int
    ix: int
    iz: int
    size: int
    chunk: bytes
    flags: int
    second: bytes | None = None


@dataclass
class TerrainTree:
    samples: int
    height_range: float
    #: x0, z0, x1, z1 of the terrain square, in world metres.
    square: tuple[float, float, float, float]
    nodes: list[Node] = field(default_factory=list)

    @property
    def stride(self) -> int:
        return self.samples - 2 * BORDER - 1

    def height_nodes(self) -> dict[tuple[int, int, int], Node]:
        need = self.samples * self.samples * 2
        return {
            (n.depth, n.ix, n.iz): n for n in self.nodes if n.flags & 1 and n.size >= need
        }


def read_tree(res: bytes, name: str = "terrain") -> TerrainTree:
    """The heightfield's parameters and the streaming quadtree of a terrain."""
    if len(res) < HEADER + 5:
        raise UnsupportedFrostbite(f"{name}: too short for a terrain streaming tree")
    (declared,) = struct.unpack_from("<I", res, 25)

    at = HEADER
    heightfield = None
    while at < len(res):
        kind = res[at]
        if kind == END:
            at += 1
            break
        if at + 5 > len(res):
            raise UnsupportedFrostbite(f"{name}: a raster tree header runs past the end")
        (length,) = struct.unpack_from("<I", res, at + 1)
        if kind == HEIGHTFIELD:
            heightfield = at
        at += 5 + length
    else:
        raise UnsupportedFrostbite(f"{name}: the raster trees do not end")
    if heightfield is None:
        raise UnsupportedFrostbite(f"{name}: no heightfield tree")

    (samples,) = struct.unpack_from("<I", res, heightfield + 5)
    (height_range,) = struct.unpack_from("<f", res, heightfield + 21)
    box = struct.unpack_from("<6f", res, heightfield + 77)
    stride = samples - 2 * BORDER - 1
    if stride <= 0 or stride & (stride - 1):
        raise UnsupportedFrostbite(
            f"{name}: {samples} samples a side is not a power of two plus a border"
        )
    tree = TerrainTree(samples, height_range, (box[0], box[2], box[3], box[5]))

    def node(at: int, depth: int, ix: int, iz: int) -> int:
        size = struct.unpack_from("<I", res, at)[0]
        chunk = res[at + 4 : at + 20]
        at += 20
        second = None
        if res[at]:
            second = res[at + 5 : at + 21]
            at += 21
        else:
            at += 1
        flags, children = res[at], res[at + 1]
        at += 2
        tree.nodes.append(Node(depth, ix, iz, size, chunk, flags, second))
        if children:
            for dx, dz in ((0, 0), (1, 0), (1, 1), (0, 1)):
                at = node(at, depth + 1, 2 * ix + dx, 2 * iz + dz)
        return at

    try:
        end = node(at, 0, 0, 0)
    except (struct.error, IndexError, RecursionError) as exc:
        raise UnsupportedFrostbite(f"{name}: the node quadtree does not parse") from exc
    if end != len(res) or len(tree.nodes) != declared:
        raise UnsupportedFrostbite(
            f"{name}: the node quadtree ends at {end} of {len(res)} with "
            f"{len(tree.nodes)} of {declared} nodes"
        )
    return tree


def height_page(tree: TerrainTree, chunk: bytes) -> np.ndarray:
    """A node's height page in metres, (samples, samples), rows along z."""
    count = tree.samples * tree.samples
    if len(chunk) < 2 * count:
        raise UnsupportedFrostbite("a height chunk is shorter than its page")
    words = np.frombuffer(chunk, dtype="<u2", count=count).reshape(tree.samples, tree.samples)
    return words.astype(np.float32) * np.float32(tree.height_range / 65535.0)


@dataclass
class Ground:
    positions: np.ndarray
    faces: np.ndarray
    #: (depth, finest spacing used) per piece, for the summary.
    pieces: int = 0


def build_ground(tree: TerrainTree, read_chunk, spacing: float = 2.0) -> Ground:
    """
    The terrain as triangles, each part of it from the finest node that has
    heights there, sampled no finer than `spacing` metres.

    A node whose four children all have heights hands over to them; one whose
    children have heights for only some quadrants draws the others itself.
    Pieces of different resolution meet with small steps along their edges;
    nothing stitches them.
    """
    heights = tree.height_nodes()
    x0, z0, x1, z1 = tree.square
    side = x1 - x0
    stride = tree.stride
    points: list[np.ndarray] = []
    faces: list[np.ndarray] = []
    base = 0
    pages: dict[tuple[int, int, int], np.ndarray] = {}

    def page(key):
        if key not in pages:
            pages[key] = height_page(tree, read_chunk(heights[key].chunk))
        return pages[key]

    def emit(key, lo_r, lo_c, count):
        """`count` x `count` cells of node `key` from sample (lo_r, lo_c)."""
        nonlocal base
        depth, ix, iz = key
        span = side / (1 << depth)
        cell = span / stride
        step = max(1, int(round(spacing / cell)))
        while count % step:
            step -= 1
        idx = np.arange(0, count + 1, step)
        rows = BORDER + lo_r + idx
        cols = BORDER + lo_c + idx
        grid = page(key)[np.ix_(rows, cols)]
        xs = x0 + ix * span + (lo_c + idx) * cell
        zs = z0 + iz * span + (lo_r + idx) * cell
        gx, gz = np.meshgrid(xs, zs)
        n = len(idx)
        points.append(np.stack([gx.ravel(), grid.ravel(), gz.ravel()], 1).astype(np.float32))
        r, c = np.meshgrid(np.arange(n - 1), np.arange(n - 1), indexing="ij")
        a = (r * n + c).ravel()
        b, d, e = a + 1, a + n, a + n + 1
        # Counter-clockwise seen from above with y up and z towards the viewer.
        faces.append(np.concatenate([np.stack([a, d, b], 1), np.stack([b, d, e], 1)]) + base)
        base += n * n

    def walk(key):
        depth, ix, iz = key
        children = [(depth + 1, 2 * ix + dx, 2 * iz + dz) for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1))]
        if not any(child in heights for child in children):
            emit(key, 0, 0, stride)
            return
        half = stride // 2
        for (cd, cx, cz) in children:
            if (cd, cx, cz) in heights:
                walk((cd, cx, cz))
            else:
                emit(key, (cz - 2 * iz) * half, (cx - 2 * ix) * half, half)

    roots = sorted(k for k in heights if not any(
        (k[0] - s, k[1] >> s, k[2] >> s) in heights for s in range(1, k[0] + 1)
    ))
    if not roots:
        raise UnsupportedFrostbite("no streaming node carries a height page")
    for key in roots:
        walk(key)
    return Ground(np.concatenate(points), np.concatenate(faces), len(points))


def sample_heights(tree: TerrainTree, read_chunk, x: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Bilinear terrain height at world (x, z) from the finest node; NaN outside."""
    heights = tree.height_nodes()
    x0, z0, x1, z1 = tree.square
    side = x1 - x0
    out = np.full(len(x), np.nan)
    pages: dict = {}
    depths = sorted({k[0] for k in heights}, reverse=True)
    for depth in depths:
        span = side / (1 << depth)
        ix = np.floor((x - x0) / span).astype(int)
        iz = np.floor((z - z0) / span).astype(int)
        todo = np.isnan(out) & (x >= x0) & (x < x1) & (z >= z0) & (z < z1)
        for i in np.nonzero(todo)[0]:
            key = (depth, ix[i], iz[i])
            if key not in heights:
                continue
            if key not in pages:
                pages[key] = height_page(tree, read_chunk(heights[key].chunk))
            c = BORDER + (x[i] - x0 - ix[i] * span) / span * tree.stride
            r = BORDER + (z[i] - z0 - iz[i] * span) / span * tree.stride
            c0, r0 = int(c), int(r)
            fc, fr = c - c0, r - r0
            p = pages[key]
            out[i] = (
                p[r0, c0] * (1 - fc) * (1 - fr) + p[r0, c0 + 1] * fc * (1 - fr)
                + p[r0 + 1, c0] * (1 - fc) * fr + p[r0 + 1, c0 + 1] * fc * fr
            )
    return out
