---
title: BeamNG files
parent: Archive readers
nav_order: 8
---

# BeamNG files: level archives, `.ter`, `.cdae`, `.dae`

BeamNG.drive ships plain zip archives, so there is no container to reverse
engineer. The work is in reading a level **the way the game does**: mounting the
archives into one file system, following the scene files, and decoding the
terrain and the compiled shapes. These readers are reached through the
[BeamNG.drive](course-beamng.md) course export. `identify` also names a level
zip, a `.cdae` and a `.ter`, and `list` and `extract` take any of the zips.

Sources: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## The mounted file system

`Files.of_install(game)` builds one case-insensitive index over
`gameengine.zip`, the `content` zips (except vehicles and sounds), and the user's
mods (`mods\*.zip`, `mods\unpacked\*`, and a user `levels` folder). Later
additions override earlier ones, as in the game. Lookups ignore case because the
levels' own references do not agree with the archives on it (`.DAE` for a
`.dae`). Details are on [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` finds a path the way the game does: as given, relative to the file
that named it, `x.png` as `x.dds`, `x.dae` as `x.cdae` (preferred), and through a
`x.png.link` JSON file whose `path` points into `/assets`.

## Scene files

| Source | Format | Read |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | one JSON object per line, or a single JSON array or map | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | the same classes, for older levels without `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript or JSON | children placed relative to the prefab, up to 8 levels deep |
| `levels\<name>\forest\*.forest4.json` | one instance per line | typed by `TSForestItemData` records in `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | the level's title (translation keys are ignored) |

**Transforms.** `rotationMatrix` is nine numbers whose **rows** are the object's
own axes in the world. Guardrail sections chained along a road run along row 0
(92%), and the up row tilts with the road's slope. Older prefabs give
`rotation = "x y z degrees"`, a right-handed turn by that angle (92% of rail
chains line up with it, 19% with the opposite sense). Scale multiplies the rows,
and `position` (or `pos`) is the last row. A prefab child's transform is
composed with the prefab's. The prefab's `groupPosition` is an editor pivot and is
**not** subtracted: a trolley prefab sits on the ground only without it.

TorqueScript numbers are read with a tolerant pattern, because some shipped
prefabs write values such as `-0.99563-0.0` without a space.

## Terrain: `.ter`

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Height in metres: `position.z + h * maxHeight / 65535`, with `position`,
  `squareSize` and `maxHeight` from the `TerrainBlock` (defaults 0, 1 and 2048).
- Rows run along +y. Grid point (i, j) is at
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Layer 255 is a hole.

Checked: road nodes lie on the terrain to 1-2 cm (median) on three levels.
`h / 32`, or the other axis order, misses by tens to hundreds of metres.

## Materials

Every `*.materials.json` outside `levels\`, plus the current level's, indexed by
`mapTo`, `name` and key:

| Class | Fields used |
|---|---|
| `Material`, `CustomMaterial` | colour map (`baseColorMap`, `colorMap` or `diffuseMap`, first stage), colour factor, opacity map and factor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | base map and `diffuseSize`, detail map, size and strength, macro map, size and strength, `groundmodelName`, `annotation` |

Images are decoded with Pillow (DDS, PNG and so on), using a reduced-size draft
where possible, and cached per size. An unreadable texture falls back to flat
colour.

## Compiled shapes: `.cdae`

`.cdae` is the game's own cache of every Collada file, written as MessagePack. Its
layout is **documented by BeamNG**
(documentation.beamng.com/modding/file_formats/cdae/) and the reader follows it:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

What is read: bounds, nodes, objects, details (levels of detail), default node
rotations (`Quat16`) and translations, every mesh's vertices, UVs, normals,
colours, primitives and indices, and the material names. Material names are found
at the end of the stream, because an animated prop's sequences come before them
in a form that is not documented.

Two things the documentation does not spell out, settled against the `.dae`
files the shapes were built from:

- **Node rotations are Torque's.** A `Quat16` read the textbook way rotates the
  wrong way round. Its matrix has to be **transposed**. With that, every node's
  world bounds match the Collada to the millimetre. Without it, they are 38 cm out
  in the median.
- **Units and axes are already applied.** A Collada file authored in centimetres
  or Y-up comes out of the cache in metres, Z-up.

Levels of detail are the `details` with a non-negative size, largest first.
Negative sizes are collision and line-of-sight meshes, never drawn. Objects named
`colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` or `imposter`
are never drawn. Only standard and sorted meshes are drawn. Skinned meshes
(characters, vehicles) and decal meshes are not. Triangle strips and fans are
unrolled, and faces are re-wound to agree with the stored normals, which Torque's
own winding does not promise.

Checked: 6,000 of the 6,002 shipped shapes read. The two others are an older
version.

## Collada fallback: `.dae`

For shapes with no `.cdae` (mods, and the odd shape whose cache is older), the
Collada file is read the way Torque's importer reads it, into the same structure:

- Levels of detail from Torque's naming: a mesh node's trailing number is the
  pixel size it is drawn from (`barrier75`, `barrier40`). A negative number, or a
  `collision`/`Colmesh`/`LOS`/`nulldetail` name, is never drawn. A shape without
  the convention is one level.
- Units from `<unit meter>`, and Y-up turned to Z-up.
- UVs flipped to the cache's convention (v runs down the image).

Checked against the game's own `.cdae` of the same files: 594 of 600 bounds within
1 cm, 583 with the same triangle count, 94% of materials' UVs identical. The
installed-game test requires 90% of up to 60 shape pairs from the shared art
archive to agree within 1 cm.

## Not read

- Ground cover (procedural grass), and anything generated at run time.
- Animated sequences and skinning.
- Vehicles and sounds (never mounted).
