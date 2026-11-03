"""
A Frostbite level's navigation mesh: the surfaces its AI soldiers walk on.

Players stand where soldiers can: on the ground, floors, stairs, bridges — not
on container lids, roofs or tank tops, which the navigation mesh leaves out.
That makes it the map of walkable space.

Where it is
-----------
A level ships one partition per agent layer, `<level>/dbt/<level>_navmesh_layer_<n>`.
Each holds two arrays::

    tiles   28 bytes each: u32 0, u32 hash, u32 0, u32 chunk index,
            u16 tile x, u16 tile z, u32 offset, u32 size
    chunks  20 bytes each: chunk GUID, u32 size

A tile's data is `size` bytes at `offset` in chunk `chunk index`; the chunks'
sizes add up to the tiles' exactly (20,677,772 bytes for one level's soldier
layer, in 305 chunks for 9,744 tiles of 16 m).

A tile
------
Little-endian, magic `VAND`, version 7. The layout is Detour's (Recast
Navigation) behind a longer header::

    +8    tile x, tile z
    +24   counts: polygons, vertices, links, detail meshes, detail vertices,
          detail triangles, bounding-volume nodes, off-mesh links, and the
          index of the first off-mesh polygon
    +188  agent height, step, radius (1.8, 0.18, 0.4 m for soldiers)
    +200  the tile's bounding box, six floats
    +232  vertices: x, y, z floats, world coordinates
    then  polygons from the next eight-byte boundary, 32 bytes each: u32,
          six u16 vertex indices, six u16 neighbours, u16 flags, at +30 the
          vertex count and at +31 the area (low six bits) and kind (top two)

After the polygons, packed: links (16 bytes), detail meshes (12: first
detail vertex u32, first detail triangle u32, vertex count u8, triangle count
u8), detail vertices (x, y, z floats), detail triangles (4 bytes: three
indices and flags), bounding-volume nodes (16) and off-mesh links (80). In
every tile of three levels (17,702) these add up to the tile's size exactly,
and the detail meshes number the polygons before the first off-mesh one.

A polygon is flat between its corners; its **detail mesh** carries the
surface's real height over bumps, rocks and steps. A detail triangle's index
below the polygon's vertex count is that polygon corner, otherwise detail
vertex `first + index - corners`. Fanning the polygons instead put 9.3% of one
level's triangles more than half a metre under the terrain.

Kind 0 is ground, kind 2 small steep patches (about 45 degrees, a square
metre each), kind 1 a link between surfaces rather than a surface: its
corners span 125 m of height or more, some lie far outside the tile, some at
the origin. Links are left out.

Checks: every surface polygon's indices are below the tile's vertex count and
its vertices lie inside the tile's bounding box, give or take 4 m (1.2 m is
the most seen) — or the tile is refused.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field

import numpy as np

from .frostbite import UnsupportedFrostbite
from .frostbiteebx import read_partition

MAGIC = b"VAND"
VERTICES = 232
POLYGON = 32
LINK = 1
#: Bytes of each record after the polygons: link, detail mesh, detail vertex,
#: detail triangle, bounding-volume node, off-mesh link.
SIZES = (16, 12, 12, 4, 16, 80)


@dataclass
class NavMesh:
    name: str
    agent: tuple[float, float, float]
    positions: np.ndarray
    faces: np.ndarray
    tiles: int = 0
    refused: int = 0


def read_tile(blob: bytes) -> tuple[tuple[float, float, float], np.ndarray, list[tuple[int, int, int]]]:
    """
    A tile's agent parameters, vertices (the polygons' corners, then the
    detail vertices) and surface triangles: each polygon's detail mesh, or
    the polygon fanned when the tile has none.
    """
    if len(blob) < VERTICES or blob[:4] != MAGIC:
        raise UnsupportedFrostbite("not a navigation tile")
    polygons, vertices, links, meshes, extra, triangles, nodes, offmesh, first_link = struct.unpack_from(
        "<9I", blob, 24
    )
    agent = struct.unpack_from("<3f", blob, 188)
    box = np.array(struct.unpack_from("<6f", blob, 200)).reshape(2, 3)
    end = VERTICES + 12 * vertices
    end += -end % 8  # the polygons start on an eight-byte boundary
    if end + POLYGON * polygons > len(blob):
        raise UnsupportedFrostbite("a navigation tile is shorter than its counts")
    points = np.frombuffer(blob, dtype="<f4", count=3 * vertices, offset=VERTICES).reshape(-1, 3)
    corners = []
    at = end
    for _ in range(polygons):
        count, kind = blob[at + 30], blob[at + 31] >> 6
        indices = list(struct.unpack_from("<6H", blob, at + 4))[: min(count, 6)]
        at += POLYGON
        if kind == LINK or len(indices) < 3:
            corners.append(None)
            continue
        if any(i >= vertices for i in indices):
            raise UnsupportedFrostbite("a navigation polygon names a vertex the tile lacks")
        corners.append(indices)

    counts = (links, meshes, extra, triangles, nodes, offmesh)
    detailed = 0 < meshes == first_link and at + sum(n * k for n, k in zip(counts, SIZES)) == len(blob)
    out: list[tuple[int, int, int]] = []
    if detailed:
        mesh_at = at + 16 * links
        extra_at = mesh_at + 12 * meshes
        triangle_at = extra_at + 12 * extra
        detail = np.frombuffer(blob, dtype="<f4", count=3 * extra, offset=extra_at).reshape(-1, 3)
        for k in range(meshes):
            if k >= len(corners) or corners[k] is None:
                continue
            vertex_base, triangle_base, _count, count = struct.unpack_from("<IIBB", blob, mesh_at + 12 * k)
            own = corners[k]
            for t in range(triangle_base, triangle_base + count):
                if t >= triangles:
                    raise UnsupportedFrostbite("a navigation detail mesh runs past its triangles")
                tri = []
                for i in blob[triangle_at + 4 * t : triangle_at + 4 * t + 3]:
                    if i < len(own):
                        tri.append(own[i])
                    elif vertex_base + i - len(own) < extra:
                        tri.append(vertices + vertex_base + i - len(own))
                    else:
                        raise UnsupportedFrostbite("a navigation detail triangle names a vertex the tile lacks")
                out.append(tuple(tri))
        points = np.concatenate([points, detail])
    else:
        for own in corners:
            if own is not None:
                out.extend((own[0], own[k], own[k + 1]) for k in range(1, len(own) - 1))
    used = points[sorted({i for tri in out for i in tri})][:, [0, 2]]
    slack = 4.0
    if len(used) and not ((used >= box[0, [0, 2]] - slack).all() and (used <= box[1, [0, 2]] + slack).all()):
        raise UnsupportedFrostbite("navigation vertices outside their tile")
    return agent, points.astype(np.float32), out


def layers(level, prefix: str) -> list[str]:
    """The navigation mesh partitions of a level, one per agent layer."""
    return sorted(n for n in level.ebx if n.startswith(prefix) and "_navmesh_layer_" in n)


def read_navmesh(level, name: str) -> NavMesh:
    """Every tile of one layer, as triangles: the polygons' detail meshes."""
    partition = read_partition(level.read(level.ebx[name].location), name)
    arrays = sorted(partition.arrays, key=lambda a: -a.count)
    data = partition.data
    tiles = next((a for a in arrays if a.count and _stride(data, a, 28)), None)
    chunks = next((a for a in arrays if a is not tiles and a.count and _stride(data, a, 20)), None)
    if tiles is None or chunks is None:
        raise UnsupportedFrostbite(f"{name}: no tile and chunk tables")
    guids = [
        (data[chunks.offset + 20 * i : chunks.offset + 20 * i + 16],
         struct.unpack_from("<I", data, chunks.offset + 20 * i + 16)[0])
        for i in range(chunks.count)
    ]
    loaded: dict[int, bytes] = {}
    points, faces = [], []
    base = 0
    agent = (0.0, 0.0, 0.0)
    refused = 0
    for i in range(tiles.count):
        _z, _hash, _z2, chunk, _tx, _tz, offset, size = struct.unpack_from(
            "<IIIIHHII", data, tiles.offset + 28 * i
        )
        if chunk >= len(guids) or not size:
            continue
        if chunk not in loaded:
            guid = guids[chunk][0]
            if guid not in level.chunks:
                raise UnsupportedFrostbite(f"{name}: navigation chunk {chunk} is not in the level")
            loaded[chunk] = level.chunk(guid)
        try:
            agent, vertices, triangles = read_tile(loaded[chunk][offset : offset + size])
        except UnsupportedFrostbite:
            refused += 1
            continue
        faces.extend((base + a, base + b, base + c) for a, b, c in triangles)
        points.append(vertices)
        base += len(vertices)
    if not faces:
        raise UnsupportedFrostbite(f"{name}: no navigation tile read")
    # Only the vertices surfaces use: the links' ends would widen the bounds.
    used, local = np.unique(np.array(faces, dtype=np.int64), return_inverse=True)
    return NavMesh(
        name, agent, np.concatenate(points)[used], local.reshape(-1, 3), tiles.count, refused
    )


def _stride(data: bytes, array, size: int) -> bool:
    """Whether an array's elements are `size` bytes: its successor starts there."""
    return array.offset + array.count * size <= len(data)


def soldier_layer(level, prefix: str) -> NavMesh | None:
    """The layer for the smallest agent — the soldier's — read whole."""
    best = None
    for name in layers(level, prefix):
        try:
            mesh = read_navmesh(level, name)
        except UnsupportedFrostbite:
            continue
        if best is None or mesh.agent[2] < best.agent[2]:
            best = mesh
    return best
