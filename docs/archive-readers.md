---
title: Archive readers
nav_order: 6
has_children: true
---

# Archive readers

Underneath the commands are readers for the containers games ship. Their formats
are undocumented, apart from Valve's VPK and BeamNG's `.cdae`, so "supported" has
to mean **verified against real files**, not "did not crash". Every reader checks
itself against something the format guarantees: a hash, a CRC, a chain of offsets
that has to close, a stored bounding box. Where a check fails, the reader refuses
with a message instead of guessing. A wrong mesh looks like a right one until
someone puts it next to the track.

| Reader | Module | Reads | Does not read | Reached from |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versions 8-12: index, entries, Zlib/Gzip/Oodle blocks, AES with a key you supply | versions before 8, path-hash-only indexes, overflow entries, asset contents | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, checked on v8), zen packages, unversioned properties for a few component classes, cooked static meshes, textures, streaming virtual textures | encrypted containers, versioned packages, Nanite-only meshes, other classes' properties | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle blocks through a library already on the machine | anything without such a library; it is never bundled | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22+ (Unity 2020 to 6000), `UnityFS` bundles, uncompressed meshes incl. `.resS` | pre-2020 formats, embedded type trees, compressed meshes, any class but `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc` DbObject trees and binary section tables, installation packages, chunk locations, inline bundles and their manifests, RIFF EBX partitions, MeshSet meshes, the terrain heightfield, BC1/BC3/BC7 textures and their shader blocks, static model group placement | XOR-obfuscated tables, the terrain's near-ground colour and holes, normal maps, alpha other than cut-outs |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versions 1 and 2, split archives, preload data, CRC check | compiled assets (`.vmdl_c`, `.vtex_c`), the CS2 nav mesh format | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, stored), `.modelbin` geometry, `.pb` swatches (BC1, BC7, RGBA), `.pgeo` placements, material texture hashes | other vertex and index formats, other texture formats, terrain shader layers | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` and `extract` (`.minizip`) |
| [BeamNG files](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | the mounted zip file system, scene JSON and TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materials | skinned and decal meshes, animated sequences, procedural ground cover | `course` (BeamNG), `identify` (zips, `.cdae`, `.ter`), `list` and `extract` (zips) |

## Rules every reader follows

- **No keys shipped, none recovered.** An encrypted archive opens only with a key
  you pass in (Unreal `.pak`, `--key`). An encrypted IoStore container is refused.
  Nothing searches an executable for a key or reads another process's memory. See
  [Rules and licences](rules-and-licences.md).
- **No proprietary code bundled.** Oodle is loaded from a game or engine already
  installed on the machine.
- **Refuse rather than guess.** An unknown version, codec, vertex format or
  texture format raises a specific error, such as
  `texture format 42 has not been identified; refusing to guess`.
- **Read-only.** No reader writes into a game folder. Exports go where you say.

## What "verified" meant

The verification figures quoted on these pages come from the module docstrings.
They were measured against installed games while each reader was written. The
synthetic tests (see [Development](development.md)) pin the field layouts. The
installed-game tests repeat some of the checks when the game is on the machine,
and skip otherwise. Figures not covered by a test have not been re-checked since.
