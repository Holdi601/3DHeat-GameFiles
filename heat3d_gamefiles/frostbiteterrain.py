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

The colormap
------------
A node's second chunk ends with its **colormap**: four BC7 pages of 132 x 132
(128 and a border of two), 17,424 bytes each, one per quadrant of the node, in
the order (low x, high z), (high x, high z), (high x, low z), (low x, low z).
Before them come whole 72 x 72 BC4 mask pages (2,592 bytes each), none in the
play area's nodes, so the chunk is `69,696 + 2,592 k` bytes long. Raster tree
4's header names the 132-texel tile and its border of two.

Evidence: the order was fitted, not chosen. Against the edges of each
quadrant's own heightfield (roads, building pads), every page of the nodes with
features matches one quadrant, unflipped, at 0.3 to 0.54 where the next best
placement is below 0.2; and stitched by that order, a level's pages join
without a seam into the roads, water and built-up areas of the test level. The engine
uses the colormap as an overlay on its splatted surface layers: it is
near-neutral, 107 to 113 in sRGB.

A level whose second chunks have another layout has no colormap read: in one,
they are whole numbers of 4,356-byte units, uncompressed 66 x 66 mask pages,
and one of them, ten times 69,696 bytes long, fits the rule above by
coincidence and is skipped.

The masks
---------
Raster tree 1 is the masks' quadtree: a 59-byte header (the page's side at
0: 72 for BC4 pages, 66 for uncompressed ones), then one group per node,
depth first: u16, u16 record count, u32 page count, 33-byte records (u16
layer, u16 hash, the quadrant's box, two flag bytes, an 85-bit presence
pyramid), a zero byte; a group without records is 7 bytes in all. A group's records are its node's quadrants, layer by
layer, each layer's quadrants in `CELL_ORDER`. A record with the second flag
set covers its quadrant whole; one without it has a page; a quadrant without
a record of a layer its group names is empty of that layer; the first flag
is clear exactly when the layer goes on in the quadrant's own group. The
page count is the number of records with a page, in every group of the three
levels checked. A streaming node's pages follow its height page, a 4,358-byte
16-bit section and a 67 x 67 eight-bit raster; its second chunk holds the
pages of its quadrants' groups one level down, quadrants in the colormap's
order, then the colormap. A page is 64 x 64 texels of its quadrant, rows
along z and columns along x, with a border copied from the neighbours: 4
texels on BC4 pages of 72 x 72, 1 on uncompressed 8-bit pages of 66 x 66.
Proof: every border predicted between neighbouring pages of one layer is
exactly equal - within nodes, across nodes and in second chunks - in all
three levels (4,783, 4,145 and 2,193 borders in one; no prediction fails),
and the borders facing a full quadrant are exactly 255, those facing an
empty one exactly 0 (2,042 of 2,050).
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
    #: Every raster tree's body, by type: 0 the heightfield, 1 the masks.
    rasters: dict[int, bytes] = field(default_factory=dict)

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
    rasters: dict[int, bytes] = {}
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
        rasters.setdefault(kind, res[at + 5 : at + 5 + length])
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
    tree = TerrainTree(samples, height_range, (box[0], box[2], box[3], box[5]), rasters=rasters)

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


#: A colormap: four BC7 pages of 132 x 132, 17,424 bytes each.
COLOUR_PAGE = 17_424
COLOUR_PAGES = 4 * COLOUR_PAGE
#: A BC4 mask page of 72 x 72, as the bytes before the colormap come.
MASK_PAGE = 2_592
#: Which quadrant (x, z) of its node each colormap page covers, in order.
COLOUR_QUADRANTS = ((0, 1), (1, 1), (1, 0), (0, 0))


@dataclass
class Colormap:
    """The terrain's colormap, stitched: RGB, rows along z, columns along x."""

    image: np.ndarray
    #: World x, z of the image's low corner, and metres a texel.
    origin: tuple[float, float]
    metres: float

    def sample(self, gx: np.ndarray, gz: np.ndarray) -> np.ndarray:
        """Colours 0..1 at world points; NaN where the colormap has none."""
        h, w = self.image.shape[:2]
        c = np.floor((gx - self.origin[0]) / self.metres).astype(np.int64)
        r = np.floor((gz - self.origin[1]) / self.metres).astype(np.int64)
        inside = (c >= 0) & (c < w) & (r >= 0) & (r < h)
        out = np.full(gx.shape + (3,), np.nan, dtype=np.float32)
        pixels = self.image[r[inside], c[inside]]
        known = pixels[:, 3] > 0
        rgb = np.full((int(inside.sum()), 3), np.nan, dtype=np.float32)
        rgb[known] = pixels[known, :3] / 255.0
        out[inside] = rgb
        return out


def read_colormap(tree: TerrainTree, read_chunk, has_chunk) -> Colormap | None:
    """
    Every node's colormap pages, stitched at the finest pages' resolution;
    finer nodes over coarser ones. None when no node's second chunk has the
    layout described above.

    A second chunk holds the mask pages of its node's quadrants' groups and
    then, when the node has one, the colormap: the mask tree says how many
    bytes the pages take, and the colormap is the four pages after them. In
    some levels four more pages of another raster (one flat colour in the
    level checked) follow it in the coarser nodes. Where the mask tree is not
    read, a chunk is taken for one when what comes before its last 69,696
    bytes is whole BC4 mask pages.
    """
    from PIL import Image

    try:
        tile, groups = mask_groups(tree)
    except UnsupportedFrostbite:
        tile, groups = 0, {}
    known = tile in (66, 72) and bool(groups)
    pages = []
    x0, z0, x1, _z1 = tree.square
    for node in tree.nodes:
        if node.second is None or not has_chunk(node.second):
            continue
        chunk = read_chunk(node.second)
        if known:
            start = _child_page_count(tree, groups, node) * _page_bytes(tile)
            rest = len(chunk) - start
            if rest < COLOUR_PAGES or rest % COLOUR_PAGES:
                continue
            pages.append((node, chunk[start : start + COLOUR_PAGES]))
            continue
        if len(chunk) < COLOUR_PAGES or (len(chunk) - COLOUR_PAGES) % MASK_PAGE:
            continue
        if len(chunk) > COLOUR_PAGES and len(chunk) % COLOUR_PAGES == 0:
            continue  # as many colormaps' worth as mask pages: another layout
        pages.append((node, chunk[len(chunk) - COLOUR_PAGES :]))
    if not pages:
        return None
    span = lambda node: (x1 - x0) / 2**node.depth
    finest = max(node.depth for node, _ in pages)
    metres = span(next(n for n, _ in pages if n.depth == finest)) / 2 / 128
    lo_x = min(x0 + n.ix * span(n) for n, _ in pages)
    lo_z = min(z0 + n.iz * span(n) for n, _ in pages)
    hi_x = max(x0 + (n.ix + 1) * span(n) for n, _ in pages)
    hi_z = max(z0 + (n.iz + 1) * span(n) for n, _ in pages)
    w = int(round((hi_x - lo_x) / metres))
    h = int(round((hi_z - lo_z) / metres))
    image = np.zeros((h, w, 4), dtype=np.uint8)
    for node, data in sorted(pages, key=lambda item: item[0].depth):
        half = span(node) / 2
        side = int(round(half / metres))
        for k, (qx, qz) in enumerate(COLOUR_QUADRANTS):
            page = Image.frombytes("RGBA", (132, 132), data[k * COLOUR_PAGE : (k + 1) * COLOUR_PAGE], "bcn", 7)
            rgb = np.asarray(page.crop((2, 2, 130, 130)).convert("RGB").resize((side, side)))
            c = int(round((x0 + node.ix * span(node) + qx * half - lo_x) / metres))
            r = int(round((z0 + node.iz * span(node) + qz * half - lo_z) / metres))
            image[r : r + side, c : c + side, :3] = rgb
            image[r : r + side, c : c + side, 3] = 255
    return Colormap(image, (lo_x, lo_z), metres)


#: The masks' raster tree.
MASKS = 1
#: Its body: a header of 59 bytes (a u32 at 0, the page's side: 72 BC4 or 66
#: uncompressed), then one group per node of the mask quadtree, depth first:
#: u16, u16 record count, u32 page count, the records, a zero byte.
MASK_HEADER = 59
#: A group without records is 7 bytes long.
EMPTY_GROUP = 7
#: A record: u16 layer, u16 hash, the quadrant's box (four floats), two flag
#: bytes and an 85-bit presence pyramid.
LAYER_RECORD = 33
#: Where a node's own pages start in its chunk, after the height page: a
#: 4,358-byte 16-bit section and a 67 x 67 eight-bit raster come first.
MASK_START = 4_358 + 4_489
#: Order of a node's four quadrants, as records and pages list them: (x, z).
CELL_ORDER = ((0, 0), (1, 0), (1, 1), (0, 1))


@dataclass
class LayerRecord:
    layer: int
    box: tuple[float, float, float, float]
    #: No page: the layer covers the quadrant whole.
    full: bool
    #: The layer goes on in the quadrant's own group, one level down.
    deeper: bool
    bits: int


@dataclass
class MaskGroup:
    pages: int
    records: list[LayerRecord]


def node_box(tree: TerrainTree, node: Node) -> tuple[float, float, float, float]:
    x0, z0, x1, _z1 = tree.square
    span = (x1 - x0) / 2**node.depth
    return (x0 + node.ix * span, z0 + node.iz * span, x0 + (node.ix + 1) * span, z0 + (node.iz + 1) * span)


def mask_groups(tree: TerrainTree) -> tuple[int, dict[tuple[float, float, float, float], MaskGroup]]:
    """The page side and every group of the mask tree, by the box its records tile."""
    body = tree.rasters.get(MASKS, b"")
    if len(body) < MASK_HEADER:
        return 0, {}
    (tile,) = struct.unpack_from("<I", body, 0)
    groups = {}
    at = MASK_HEADER
    while at + 8 <= len(body):
        _first, count, pages = struct.unpack_from("<HHI", body, at)
        if count == 0:
            at += EMPTY_GROUP
            continue
        at += 8
        if at + count * LAYER_RECORD > len(body):
            raise UnsupportedFrostbite("a mask group runs past its raster tree")
        records = []
        for _ in range(count):
            layer, _hash = struct.unpack_from("<HH", body, at)
            box = struct.unpack_from("<4f", body, at + 4)
            records.append(
                LayerRecord(layer, box, body[at + 21] == 1, body[at + 20] == 0, int.from_bytes(body[at + 22 : at + 33], "little"))
            )
            at += LAYER_RECORD
        at += 1
        if records:
            # The node whose quadrants these are: twice a quadrant's side, on
            # the quadtree's grid (a group need not name every quadrant).
            x0, z0 = tree.square[:2]
            r = records[0].box
            side = 2 * (r[2] - r[0])
            nx = x0 + np.floor((r[0] - x0) / side + 1e-6) * side
            nz = z0 + np.floor((r[1] - z0) / side + 1e-6) * side
            key = (nx, nz, nx + side, nz + side)
            if key in groups:
                raise UnsupportedFrostbite("two mask groups describe one node, a layout the reader does not know")
            groups[key] = MaskGroup(pages, records)
    return tile, groups


def _child_quadrants(tree: TerrainTree, node: Node) -> list[tuple[float, float, float, float]]:
    """A node's four quadrants' boxes, in the colormap's order."""
    x0, z0, x1, _ = node_box(tree, node)
    half = (x1 - x0) / 2
    return [(x0 + qx * half, z0 + qz * half, x0 + (qx + 1) * half, z0 + (qz + 1) * half) for qx, qz in COLOUR_QUADRANTS]


def _child_page_count(tree: TerrainTree, groups: dict, node: Node) -> int:
    """The mask pages a node's second chunk holds: its quadrants' groups' pages."""
    return sum(groups[box].pages for box in _child_quadrants(tree, node) if box in groups)


def _page_bytes(tile: int) -> int:
    return 2_592 if tile == 72 else tile * tile


def _decode_page(tile: int, data: bytes) -> np.ndarray:
    if tile == 72:
        from PIL import Image

        return np.asarray(Image.frombytes("L", (72, 72), data, "bcn", 4))
    return np.frombuffer(data, np.uint8).reshape(tile, tile)


@dataclass
class LayerMasks:
    """
    The painted layers' masks, as quadrant tiles: per layer, (depth, box,
    64 x 64 texels or a constant 0 / 255). Painted coarse to fine, so a
    finer group overrides its parent's quadrant.
    """

    tiles: dict[int, list[tuple[int, tuple[float, float, float, float], np.ndarray | int]]]

    def raster(self, layer: int, origin: tuple[float, float], metres: float, shape: tuple[int, int]) -> np.ndarray:
        """The layer over a grid of `shape` from `origin`, 0..1; NaN where no group says."""
        h, w = shape
        out = np.full(shape, np.nan, dtype=np.float32)
        for _depth, (x0, z0, x1, z1), image in sorted(self.tiles.get(layer, []), key=lambda t: t[0]):
            c0 = int(np.floor((x0 - origin[0]) / metres))
            r0 = int(np.floor((z0 - origin[1]) / metres))
            c1 = int(np.ceil((x1 - origin[0]) / metres))
            r1 = int(np.ceil((z1 - origin[1]) / metres))
            cc0, rr0, cc1, rr1 = max(c0, 0), max(r0, 0), min(c1, w), min(r1, h)
            if cc1 <= cc0 or rr1 <= rr0:
                continue
            if isinstance(image, int):
                out[rr0:rr1, cc0:cc1] = image / 255.0
                continue
            # Texel centres of the tile at the grid's cell centres.
            cols = ((origin[0] + (np.arange(cc0, cc1) + 0.5) * metres - x0) / (x1 - x0) * 64).astype(np.int64).clip(0, 63)
            rows = ((origin[1] + (np.arange(rr0, rr1) + 0.5) * metres - z0) / (z1 - z0) * 64).astype(np.int64).clip(0, 63)
            out[rr0:rr1, cc0:cc1] = image[np.ix_(rows, cols)] / 255.0
        return out


def read_masks(tree: TerrainTree, read_chunk, has_chunk) -> LayerMasks | None:
    """
    Every painted layer's mask, placed. A streaming node's own group lists
    its four quadrants' records, layer by layer, each layer's quadrants in
    `CELL_ORDER`; a record without the full flag has the next page of the
    node's chunk (after `MASK_START` when the chunk starts with a height
    page, from its start when not), one with it covers the quadrant whole,
    and a quadrant without a record of a layer the group names is empty of
    it. A node's second chunk holds the pages of its four quadrants' groups
    one level down, quadrants in the colormap's order. A page is the
    quadrant's 64 x 64 texels, rows along z and columns along x, and a
    border copied from the neighbours (4 texels on BC4 pages of 72, 1 on
    uncompressed ones of 66).

    Placing is checked as it reads: two neighbouring pages of a layer must
    carry each other's edge texels in their borders. Some levels keep more
    in their nodes' chunks than this layout knows, and their pages land in
    the wrong place; when fewer than `BORDERS_AGREE` of the borders agree,
    the masks are refused rather than drawn wrong.
    """
    tile, groups = mask_groups(tree)
    if not groups or tile not in (66, 72):
        return None
    size = _page_bytes(tile)
    border = (tile - 64) // 2
    tiles: dict[int, list] = {}
    edges: dict[tuple, tuple[np.ndarray, np.ndarray]] = {}
    x_origin, z_origin = tree.square[:2]

    def place(box, group: MaskGroup, data: bytes, at: int, depth: int) -> int:
        named: dict[int, set] = {}
        x0, z0, x1, z1 = box
        half = (x1 - x0) / 2
        for record in group.records:
            qx = int(round((record.box[0] - x0) / half))
            qz = int(round((record.box[1] - z0) / half))
            named.setdefault(record.layer, set()).add((qx, qz))
            if record.full:
                tiles.setdefault(record.layer, []).append((depth, record.box, 255))
                continue
            if at + size > len(data):
                raise UnsupportedFrostbite("a mask page runs past its chunk")
            page = _decode_page(tile, data[at : at + size])
            at += size
            # Kept by its cell on its depth's grid, for the border check.
            side = record.box[2] - record.box[0]
            cell = (side, record.layer, round((record.box[0] - x_origin) / side), round((record.box[1] - z_origin) / side))
            edges[cell] = page
            tiles.setdefault(record.layer, []).append((depth, record.box, page[border : border + 64, border : border + 64]))
        for layer, present in named.items():
            for qx, qz in CELL_ORDER:
                if (qx, qz) not in present:
                    quad = (x0 + qx * half, z0 + qz * half, x0 + (qx + 1) * half, z0 + (qz + 1) * half)
                    tiles[layer].append((depth, quad, 0))
        return at

    for node in tree.nodes:
        box = node_box(tree, node)
        group = groups.get(box)
        if group is not None and group.pages:
            data = read_chunk(node.chunk) if has_chunk(node.chunk) else b""
            start = 265 * 265 * 2 + MASK_START if node.flags & 1 else 0
            if len(data) < start + group.pages * size:
                continue
            place(box, group, data, start, node.depth)
        if node.second is None or not has_chunk(node.second):
            continue
        children = [(child, groups[child]) for child in _child_quadrants(tree, node) if child in groups]
        need = sum(g.pages for _, g in children)
        if not need:
            continue
        data = read_chunk(node.second)
        if len(data) < need * size:
            continue
        at = 0
        for child, group in children:
            at = place(child, group, data, at, node.depth + 1)
    agree, compared = _borders_agree(edges, 2 * border)
    if compared and agree < BORDERS_AGREE * compared:
        raise UnsupportedFrostbite(
            f"the layer masks' pages do not fit together ({agree:,} of {compared:,} borders agree), "
            "so this level keeps more in its chunks than the reader knows"
        )
    return LayerMasks(tiles) if tiles else None


#: The share of neighbouring pages' borders that must agree for the masks to be used.
BORDERS_AGREE = 0.99


def _borders_agree(pages: dict[tuple, np.ndarray], overlap: int) -> tuple[int, int]:
    """Of the neighbouring pages that are not both flat, how many share their borders exactly."""
    agree = compared = 0
    for (side, layer, cx, cz), page in pages.items():
        for far, near, other in (
            (page[-overlap:], lambda q: q[:overlap], (side, layer, cx, cz + 1)),
            (page[:, -overlap:], lambda q: q[:, :overlap], (side, layer, cx + 1, cz)),
        ):
            neighbour = pages.get(other)
            if neighbour is None:
                continue
            strip = near(neighbour)
            if far.min() == far.max() and strip.min() == strip.max():
                continue
            compared += 1
            agree += bool(np.array_equal(far, strip))
    return agree, compared


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
