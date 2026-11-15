"""
Which of the game's own races a lap was driven on.

A ForzaTech open world ships its race routes as AI driving lines:
`media\\OpenWorld\\<map>\\AITracks\\Route<id>.owt`, one per route, the number in
the name being the route's id. The id is what everything else about a race is
keyed by - the spectator layers placed for one race are named after it
(`crowdtemplate_cwd_rt_x<id>` in the placement files) - so a lap that can be
matched to its route can be given what the game places for that race alone.

The file
--------
::

    "FTWO", u32 version, u32 hash, u32 size, ...
    0x24  u32 node count
    0x60  count x 56 bytes:
              f32 x 3   position (x, y, z), world metres
              f32 x 7   direction, up, distance along the route
              ...       flags and links

Read as 56-byte nodes from 0x60, consecutive positions of every route but a
handful lie a few metres apart along the road. Those few hold extra records
between nodes; their nodes still read as positions, and whatever does not (not
finite, or tens of kilometres off) is dropped rather than trusted.

Matching
--------
A lap matches a route when both are close to each other both ways: the median
distance from the lap's samples to the route, plus the median from the
route's nodes to the lap, under `MATCH` metres. One way alone is not enough -
a short sprint lies on a long route that passes the same road, and a long lap
covers a short route. Over a library of recorded courses, the right route
scores a few metres - the width of the road the line and the lap differ by -
and the next best an order of magnitude or more.
"""

from __future__ import annotations

import re
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

#: Bytes per node, where the nodes begin, and where their count is.
NODE = 56
NODES_AT = 0x60
COUNT_AT = 0x24
MAGIC = b"FTWO"

#: Metres: both medians together under this, or the lap is not that route.
MATCH = 30.0

#: Points each side is thinned to before distances are measured. A library
#: course is tens of thousands of samples nearly on top of one another.
THIN = 1500

_ROUTE_FILE = re.compile(r"^route(\d+)\.owt$", re.I)


@dataclass
class Route:
    id: int
    #: (n, 3) world positions along the route.
    points: np.ndarray

    @property
    def plane(self) -> np.ndarray:
        return self.points[:, [0, 2]]


def read_route(data: bytes, route_id: int = 0) -> Route:
    """One `.owt`: its nodes' positions, the unreadable ones dropped."""
    if len(data) < NODES_AT or data[:4] != MAGIC:
        raise ValueError("not an AI route file")
    (count,) = struct.unpack_from("<I", data, COUNT_AT)
    count = min(count, (len(data) - NODES_AT) // NODE)
    nodes = np.frombuffer(data, dtype="<f4", count=count * NODE // 4, offset=NODES_AT)
    points = nodes.reshape(count, NODE // 4)[:, :3].astype(np.float64)
    with np.errstate(invalid="ignore"):
        ok = np.isfinite(points).all(axis=1) & (np.abs(points) < 100_000).all(axis=1)
    return Route(route_id, points[ok])


def routes_folder(track: str | Path) -> Path:
    """`media\\Tracks\\<map>` to `media\\OpenWorld\\<map>\\AITracks`, whatever the case."""
    track = Path(track)
    media = track.parent.parent
    for world in (media / "OpenWorld" / track.name, media / "openworld" / track.name.lower()):
        if (world / "AITracks").is_dir():
            return world / "AITracks"
    return media / "OpenWorld" / track.name / "AITracks"


def read_routes(track: str | Path) -> list[Route]:
    """Every route of a track's open world, or none if it ships no AI routes."""
    folder = routes_folder(track)
    if not folder.is_dir():
        return []
    out = []
    for path in sorted(folder.iterdir()):
        found = _ROUTE_FILE.match(path.name)
        if not found:
            continue
        try:
            route = read_route(path.read_bytes(), int(found.group(1)))
        except (OSError, ValueError, struct.error):
            continue
        if len(route.points) >= 2:
            out.append(route)
    return out


def _thin(points: np.ndarray) -> np.ndarray:
    return points[:: max(1, len(points) // THIN)]


def _nearest(points: np.ndarray, to: np.ndarray) -> np.ndarray:
    """Distance from each point to the nearest of `to`, in blocks."""
    out = np.empty(len(points))
    for start in range(0, len(points), 512):
        block = points[start : start + 512]
        gap = ((block[:, None, :] - to[None, :, :]) ** 2).sum(axis=2)
        out[start : start + 512] = np.sqrt(gap.min(axis=1))
    return out


def score(lap: np.ndarray, route: np.ndarray) -> float:
    """Median lap-to-route plus median route-to-lap distance, in metres."""
    lap, route = _thin(lap), _thin(route)
    return float(np.median(_nearest(lap, route)) + np.median(_nearest(route, lap)))


def match(positions: np.ndarray, routes: list[Route]) -> tuple[Route | None, float]:
    """
    The route a lap was driven on, and its score; (None, inf) when none is
    within `MATCH`.

    Only routes whose box overlaps the lap's are measured, so a whole map's
    worth costs about a second.
    """
    positions = np.asarray(positions, dtype=np.float64)
    lap = positions[:, [0, 2]] if positions.shape[1] >= 3 else positions[:, :2]
    lap = lap[np.isfinite(lap).all(axis=1)]
    if not len(lap) or not routes:
        return None, float("inf")
    low, high = lap.min(axis=0) - MATCH, lap.max(axis=0) + MATCH
    best, best_score = None, float("inf")
    for route in routes:
        plane = route.plane
        if (plane.max(axis=0) < low).any() or (plane.min(axis=0) > high).any():
            continue
        value = score(lap, plane)
        if value < best_score:
            best, best_score = route, value
    if best_score > MATCH:
        return None, best_score
    return best, best_score


# ---------------------------------------------------------------------------
# A race's own assets
# ---------------------------------------------------------------------------
#
# What the game adds to the world for one race, and takes away from it, is
# written per route in `media\Stripped\gs\<map>\routedefinitions.zip`: one
# `route<id>_<map>.rtd` each, plain XML in a plain zip.
#
# ::
#
#     <Route>
#       <CookedHiddenAssets> ... </CookedHiddenAssets>      instance numbers
#       <HiddenAssets>
#         <Transform guid="..." value="16 floats" />       free-roam objects
#       </HiddenAssets>                                    taken away
#       <RouteAssets>
#         <Instance>
#           <Model value="tracks\<map>\scene\models\<kind>\...\<stem>.model" />
#           <Transform value="16 floats" />                rows: x, y, z axes
#           <Material value="n" />                         (scaled), position
#         </Instance> ...
#       </RouteAssets>
#     </Route>
#
# The transform's rows are the model's axes and its position: the third row is
# the cross product of the first two (checked on a stadium circuit's
# instances), and the fourth is where it stands, in the world's own metres.
# A hidden asset is named by its instance GUID, which the track's
# `AssetManifest.xml` lists under the model it is a copy of; one standing at
# the origin is a model already in world coordinates (a stadium's lawn).

#: Kinds of route asset that are not geometry here: spectators, which the game
#: draws as animated sprites from these markers.
NOT_GEOMETRY = ("crowd_proxies",)


@dataclass
class RouteAssets:
    """One race's own layer, and what it hides of the free-roam world."""

    id: int
    #: stem -> (n, 13) copies, as `forzaplacement.parse_pgeo` gives them:
    #: position, x axis, y axis, scale, variant.
    models: dict[str, np.ndarray]
    #: stem -> its kind, the folder under `scene\models\` (barriers, props...).
    kinds: dict[str, str]
    #: Where each free-roam object the race hides stands, and its instance id.
    hidden: np.ndarray
    hidden_ids: list[str]
    #: kind -> copies that are not drawn geometry (spectator markers, collision).
    markers: dict[str, int]

    @property
    def copies(self) -> int:
        return sum(len(v) for v in self.models.values())


_INSTANCE = re.compile(r"<Instance\b[^>]*>(.*?)</Instance>", re.S)
_MODEL = re.compile(r'<Model value="([^"]+)"')
_TRANSFORM = re.compile(r'<Transform\b[^>]*?value="([^"]+)"')
_MATERIAL = re.compile(r'<Material value="(\d+)"')
_HIDDEN = re.compile(r'<Transform guid="([^"]+)" value="([^"]+)"')


def _instance_row(values: list[float], variant: int) -> np.ndarray | None:
    if len(values) != 16:
        return None
    m = np.array(values, dtype=np.float64).reshape(4, 4)
    scale = np.linalg.norm(m[:3, :3], axis=1)
    if not np.isfinite(m).all() or (scale < 1e-9).any():
        return None
    ax, ay = m[0, :3] / scale[0], m[1, :3] / scale[1]
    return np.concatenate([m[3, :3], ax, ay, scale, [variant]])


def read_definition(text: str, route_id: int = 0) -> RouteAssets:
    """One route definition's added and hidden assets."""
    models: dict[str, list[np.ndarray]] = {}
    kinds: dict[str, str] = {}
    markers: dict[str, int] = {}
    added = text.find("<RouteAssets")
    for found in _INSTANCE.finditer(text, added if added >= 0 else len(text)):
        body = found.group(1)
        model = _MODEL.search(body)
        transform = _TRANSFORM.search(body)
        if not model or not transform:
            continue
        path = model.group(1).replace("/", "\\").lower()
        pieces = path.split("\\")
        stem, _dot, extension = pieces[-1].rpartition(".")
        if not _dot:
            stem, extension = pieces[-1], ""
        kind = pieces[pieces.index("models") + 1] if "models" in pieces[:-1] else (extension or "other")
        if kind in NOT_GEOMETRY or extension != "model":
            label = kind if kind in NOT_GEOMETRY else (extension or "other")
            markers[label] = markers.get(label, 0) + 1
            continue
        material = _MATERIAL.search(body)
        try:
            values = [float(v) for v in transform.group(1).split()]
        except ValueError:
            continue
        row = _instance_row(values, int(material.group(1)) if material else 0)
        if row is None:
            continue
        models.setdefault(stem, []).append(row)
        kinds[stem] = kind
    hidden, ids = [], []
    start = text.find("<HiddenAssets>")
    end = text.find("</HiddenAssets>", start)
    if start >= 0 and end > start:
        for guid, value in _HIDDEN.findall(text, start, end):
            try:
                values = [float(v) for v in value.split()]
            except ValueError:
                continue
            if len(values) == 16:
                hidden.append(values[12:15])
                ids.append(guid.lower())
    return RouteAssets(
        id=route_id,
        models={stem: np.array(rows) for stem, rows in models.items()},
        kinds=kinds,
        hidden=np.array(hidden, dtype=np.float64).reshape(-1, 3),
        hidden_ids=ids,
        markers=markers,
    )


def definitions_archive(track: str | Path) -> Path:
    """`media\\Tracks\\<map>` to `media\\Stripped\\gs\\<map>\\routedefinitions.zip`."""
    track = Path(track)
    media = track.parent.parent
    for gs in (media / "Stripped" / "gs", media / "stripped" / "gs"):
        for name in (track.name.lower(), track.name):
            candidate = gs / name / "routedefinitions.zip"
            if candidate.exists():
                return candidate
    return media / "Stripped" / "gs" / track.name.lower() / "routedefinitions.zip"


_DEFINITION = re.compile(r"^route(\d+)_[^.]*\.rtd$", re.I)


def defined_routes(track: str | Path) -> dict[int, str]:
    """Route id -> its entry in the definitions archive, for every race the game defines."""
    archive = definitions_archive(track)
    if not archive.exists():
        return {}
    with zipfile.ZipFile(archive) as opened:
        out = {}
        for name in opened.namelist():
            found = _DEFINITION.match(name.rsplit("/", 1)[-1])
            if found:
                out[int(found.group(1))] = name
        return out


def route_assets(track: str | Path, route_id: int) -> RouteAssets | None:
    """A race's own assets, or None when the game defines nothing for it."""
    entry = defined_routes(track).get(route_id)
    if entry is None:
        return None
    with zipfile.ZipFile(definitions_archive(track)) as opened:
        text = opened.read(entry).decode("utf-8", "replace")
    return read_definition(text, route_id)


def instance_models(track: str | Path, ids) -> dict[str, str]:
    """
    Instance GUID -> model stem, for the GUIDs asked about, from the track's
    `AssetManifest.xml` (its `<Models>` list: each model's source, then the
    ids of its copies). One pass over the file, a few seconds.
    """
    wanted = {i.lower() for i in ids}
    out: dict[str, str] = {}
    path = Path(track) / "AssetManifest.xml"
    if not wanted or not path.exists():
        return out
    source = re.compile(r'Source="([^"]+)"')
    instance = re.compile(r'<Instance Id="([0-9a-fA-F-]+)"')
    stem = None
    with open(path, encoding="utf-8", errors="replace") as lines:
        for line in lines:
            if "<Mesh " in line:
                found = source.search(line)
                if found:
                    leaf = found.group(1).replace("/", "\\").rsplit("\\", 1)[-1]
                    stem = leaf.rsplit(".", 1)[0].lower()
            elif "<Instance Id=" in line and stem:
                found = instance.search(line)
                if found and found.group(1).lower() in wanted:
                    out[found.group(1).lower()] = stem
                    if len(out) == len(wanted):
                        break
    return out
