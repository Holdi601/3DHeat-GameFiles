"""
The cars of an installed Forza, as one small file the viewer can draw.

Each car is an ordinary ZIP under `media/Cars`. Besides the detailed parts it
holds `Scene/ProxyLOD.modelbin`, the game's own stand-in for the whole car seen
from afar: a closed shell of a few hundred to a few thousand triangles, with the
wheel arches cut out and no wheels. That is the car at reduced quality, and
nothing here has to reduce anything.

What else the viewer needs comes from the same archive:

- the car's number, the one the telemetry calls `carOrdinal`, from the name of
  `Scene/animations/Mojo/clip/carclips_<number>.clipd`. It matched the archive of
  all 253 cars in a lap library whose folders state number and name;
- where the wheels are, from `Locators.xml`, and the tail lights the same way;
- the make and year, from the archive's name: `BMW_E36M3_97`.

No file says how big the wheels are in metres that this reader can trust (the
wheel models are scaled by the car's parts), and the shell has to stand on the
road. So the radius is measured off the shell: see `wheel_radius`.

The car axes are the game's: x to the car's right, y up, z forward.

The file
--------
A gzip of: the 8 bytes `H3DCARS1`, a little-endian u32 with the length of a UTF-8
JSON header, the header, padding with spaces to a multiple of 4, then each car's
vertices as three i16 per vertex in millimetres and its triangles as three u16.
The header says where each car's data begins, counted from the first byte after
the header's padding.

The result holds the game's own shapes. It is for the machine it was made on: it
is not something to pass around, and nothing in this package ships one.
"""

from __future__ import annotations

import gzip
import json
import re
import struct
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from .forzatech import UnsupportedForza, read_geometry, read_model

MAGIC = b"H3DCARS1"
FORMAT_VERSION = 1

PROXY = "scene/proxylod.modelbin"
LOCATORS = "locators.xml"

#: What the telemetry's `game` says for laps of this reader's games.
GAME = "forza-horizon"

#: The first part of an archive's name, and the make it stands for.
MAKES = {
    "343": "AMG Transport Dynamics", "AC": "Alumicraft", "ACU": "Acura", "AH": "Austin-Healey",
    "ALF": "Alfa Romeo", "APO": "Apollo", "ARI": "Ariel", "AST": "Aston Martin", "AUD": "Audi",
    "AZM": "Autozam", "BAC": "BAC", "BEN": "Bentley", "BMW": "BMW", "BUI": "Buick", "CAD": "Cadillac",
    "CAN": "Can-Am", "CHE": "Chevrolet", "CHR": "Chrysler", "CIT": "Citroen", "DAT": "Datsun",
    "DEL": "DeLorean", "DET": "De Tomaso", "DOD": "Dodge", "EUN": "Eunos", "EXO": "Exomotive",
    "FER": "Ferrari", "FIA": "Fiat", "FOR": "Ford", "FUN": "Funco", "GIN": "Ginetta",
    "GMA": "Gordon Murray", "GMC": "GMC", "HEN": "Hennessey", "HOL": "Holden", "HON": "Honda",
    "HYU": "Hyundai", "JAG": "Jaguar", "JEE": "Jeep", "JIM": "Jimco", "KOE": "Koenigsegg", "KTM": "KTM",
    "LAM": "Lamborghini", "LAN": "Lancia", "LEX": "Lexus", "LIN": "Lincoln", "LOT": "Lotus",
    "LR": "Land Rover", "LUC": "Lucid", "MAS": "Maserati", "MAZ": "Mazda", "MCL": "McLaren",
    "MER": "Mercedes", "MEY": "Meyers", "MG": "MG", "MIN": "MINI", "MIT": "Mitsubishi", "NIS": "Nissan",
    "NOB": "Noble", "OPE": "Opel", "PAG": "Pagani", "PEE": "Peel", "PEN": "Penhall", "PEU": "Peugeot",
    "PLY": "Plymouth", "POL": "Polaris", "PON": "Pontiac", "POR": "Porsche", "RAD": "Radical", "RAM": "Ram",
    "REL": "Reliant", "REN": "Renault", "RIM": "Rimac", "RIV": "Rivian", "RJ": "RJ Anderson", "SAL": "Saleen",
    "SHE": "Shelby", "SIE": "SIERRA", "SUB": "Subaru", "SUN": "Sunbeam", "TOY": "Toyota", "TVR": "TVR",
    "ULT": "Ultima", "VAU": "Vauxhall", "VIP": "SRT", "VOL": "Volvo", "VW": "Volkswagen", "WUL": "Wuling",
    "ZEN": "Zenvo",
}

#: A car's wheels, in the order the viewer keeps them: FL, FR, RL, RR.
WHEELS = ("wheelLF", "wheelRF", "wheelLR", "wheelRR")
LIGHTS = ("taillightL", "taillightR")

#: The radius a wheel can have, as shares of the car's length.
WHEEL_OF_LENGTH = (0.07, 0.095)

CLIPS = re.compile(r"carclips_(\d+)", re.I)
LOCATOR = re.compile(
    r'<Name value="carLocator_(\w+)"/>.*?value\._41="(-?[\d.]+)" value\._42="(-?[\d.]+)" value\._43="(-?[\d.]+)"',
    re.S,
)


@dataclass
class Car:
    """One car, ready to write."""

    key: str
    ordinals: list[int]
    make: str
    model: str
    year: int | None
    positions: "object"
    faces: "object"
    #: x, y, z of the hub and the radius, for each of `WHEELS`, in metres.
    wheels: list[list[float]] = field(default_factory=list)
    #: x, y, z of each tail light the archive places.
    lights: list[list[float]] = field(default_factory=list)

    @property
    def ground(self) -> float:
        """The road's height in the car's axes, from the wheels."""
        return sum(w[1] - w[3] for w in self.wheels) / len(self.wheels)

    @property
    def height(self) -> float:
        """The roof over the road, metres."""
        return float(self.positions[:, 1].max()) - self.ground


def name_parts(stem: str, *, this_year: int = 2030) -> tuple[str, str, int | None]:
    """The make, the model tag and the year in an archive's name."""
    parts = stem.split("_")
    make = MAKES.get(parts[0].upper(), parts[0])
    year: int | None = None
    rest = parts[1:]
    if rest and re.fullmatch(r"\d{2}", rest[-1]):
        two = int(rest[-1])
        year = 2000 + two if 2000 + two <= this_year else 1900 + two
        rest = rest[:-1]
    return make, "_".join(rest), year


def locators(text: str) -> dict[str, list[float]]:
    """The named points of a `Locators.xml`, first of each name."""
    found: dict[str, list[float]] = {}
    for match in LOCATOR.finditer(text):
        found.setdefault(match.group(1), [float(match.group(k)) for k in (2, 3, 4)])
    return found


def wheel_radius(positions, hub) -> float:
    """
    A wheel's radius, from the arch cut round it in the shell.

    The arch's lip is the nearest point of the shell's outer skin above the hub,
    in the plane the wheel turns in. A road car's wheel fills it: within 2 cm of
    the real radius on the road cars this was checked against. An off-road car's
    arch has room for the travel as well, so the lip is held to what a wheel can
    be on a car of this length; that bound also stands in where the shell has no
    arch to measure. Checked against 14 cars of known tyre size, from a microcar
    to a six-wheeler: within 5 cm, and the two furthest are lifted trucks.
    """
    import numpy as np

    length = float(np.ptp(positions[:, 2]))
    least, most = WHEEL_OF_LENGTH[0] * length, WHEEL_OF_LENGTH[1] * length
    side = np.sign(hub[0]) or 1.0
    up = positions[:, 1] - hub[1]
    along = positions[:, 2] - hub[2]
    skin = (positions[:, 0] * side > abs(hub[0]) * 0.85) & (up > 0) & (np.abs(along) < up * 0.7)
    reach = np.hypot(up[skin], along[skin])
    reach = reach[reach > 0.1]
    return float(np.clip(reach.min(), least, most)) if len(reach) else least


def read_car(archive: str | Path) -> Car | None:
    """A car archive's stand-in, or None for an archive without one (traffic props)."""
    import numpy as np

    archive = Path(archive)
    with zipfile.ZipFile(archive) as z:
        names = {name.lower(): name for name in z.namelist()}
        if PROXY not in names:
            return None
        geometry = read_geometry(read_model("ProxyLOD.modelbin", z.read(names[PROXY])), lod=None)
        ordinals = sorted({int(m.group(1)) for m in (CLIPS.search(n) for n in names) if m})
        placed = locators(z.read(names[LOCATORS]).decode("utf-8", "replace")) if LOCATORS in names else {}
    positions = np.asarray(geometry.positions, dtype=np.float64)
    if not len(geometry.faces):
        return None
    if all(w in placed for w in WHEELS):
        wheels = [[*placed[w], wheel_radius(positions, placed[w])] for w in WHEELS]
    else:
        # No locators: the wheels where a car's would be, from the shell's size.
        lo, hi = positions.min(axis=0), positions.max(axis=0)
        length = hi[2] - lo[2]
        ahead, behind = hi[2] - 0.2 * length, lo[2] + 0.2 * length
        across = 0.42 * (hi[0] - lo[0])
        radius = WHEEL_OF_LENGTH[0] * length
        wheels = [
            [x, lo[1] + radius, z, radius]
            for z in (ahead, behind)
            for x in (-across, across)
        ]
    # Each shell has a lump hanging under its floor, through the road on most cars.
    road = sum(w[1] - w[3] for w in wheels) / 4
    faces = np.asarray(geometry.faces, dtype=np.int64)
    kept = faces[positions[faces, 1].max(axis=1) >= road]
    if len(kept):
        faces = kept
    if len(positions) > 0xFFFF + 1:
        raise UnsupportedForza(f"{archive.stem} has more vertices than the file's indices reach")
    make, model, year = name_parts(archive.stem)
    return Car(
        key=archive.stem,
        ordinals=ordinals,
        make=make,
        model=model,
        year=year,
        positions=positions,
        faces=faces,
        wheels=wheels,
        lights=[placed[light] for light in LIGHTS if light in placed],
    )


def write_pack(cars: list[Car], path: str | Path, *, game: str = GAME, source: str = "") -> int:
    """Write the file described above; returns its size in bytes."""
    import numpy as np

    entries = []
    chunks: list[bytes] = []
    at = 0
    for car in cars:
        vertices = np.clip(np.rint(car.positions * 1000.0), -32768, 32767).astype("<i2").tobytes()
        if car.faces.max() > 0xFFFF:
            raise UnsupportedForza(f"{car.key} has more vertices than the file's indices reach")
        faces = car.faces.astype("<u2").tobytes()
        entries.append(
            {
                "key": car.key,
                "ordinals": car.ordinals,
                "make": car.make,
                "model": car.model,
                "year": car.year,
                "height": round(car.height, 3),
                "length": round(float(np.ptp(car.positions[:, 2])), 3),
                "wheels": [[round(float(v), 4) for v in w] for w in car.wheels],
                "lights": [[round(float(v), 4) for v in p] for p in car.lights],
                "vertexAt": at,
                "vertices": len(car.positions),
                "faceAt": at + len(vertices),
                "faces": len(car.faces),
            }
        )
        chunks += [vertices, faces]
        at += len(vertices) + len(faces)
    header = json.dumps(
        {"format": "heat3d-cars", "version": FORMAT_VERSION, "game": game, "source": source, "cars": entries},
        separators=(",", ":"),
    ).encode("utf-8")
    prefix = MAGIC + struct.pack("<I", len(header)) + header
    prefix += b" " * (-len(prefix) % 4)
    packed = gzip.compress(prefix + b"".join(chunks), 6)
    Path(path).write_bytes(packed)
    return len(packed)


def read_pack(path: str | Path) -> tuple[dict, bytes]:
    """The header and data of a written file."""
    raw = gzip.decompress(Path(path).read_bytes())
    if raw[:8] != MAGIC:
        raise UnsupportedForza(f"{path} is not a car file")
    (length,) = struct.unpack_from("<I", raw, 8)
    start = 12 + length
    header = json.loads(raw[12:start])
    return header, raw[start + (-start % 4) :]


def cars_of_game(game: str | Path) -> list[Path]:
    """Every car archive of an installed game."""
    for folder in ("media/Cars", "media/cars"):
        base = Path(game) / folder
        if base.is_dir():
            return sorted(p for p in base.iterdir() if p.suffix.lower() == ".zip")
    return []
