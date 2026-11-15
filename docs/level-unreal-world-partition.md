---
title: Unreal 5 maps
parent: Whole levels
nav_order: 2
---

# Unreal 5 World Partition maps: `ue-maps` and `ue-map`

**What is it?** A whole map of an Unreal 5 game as one 3D file: the ground, the
buildings and the water. **Why?** So heat from that game has the map under it.
(*World Partition* is how Unreal 5 splits a big map into pieces; *HLOD* is a
simplified stand-in for a group of buildings, the one the game draws far away.)

Exports a whole map of an Unreal 5 game whose maps are cooked as World
Partition cells: the landscape, the map's merged HLOD meshes (its buildings
and props as the game draws them at a distance) and its water bodies. No
editor and no project are needed, only the installed game.

![The steps of a ue-map export](assets/img/ue-map-steps.svg)

## Step by step

1. **List the maps.** `<game>` is the game's folder, its `Content/Paks`, or the
   name of its folder in a Steam library:

   ```
   python -m heat3d_gamefiles ue-maps "<Steam game folder name>"
   python -m heat3d_gamefiles ue-maps "D:\Games\<game>"
   ```

   Every map with cooked World Partition cells is printed with its package path.

2. **Export one** by its name or a unique part of it:

   ```
   python -m heat3d_gamefiles ue-map "<game>" <map> -o map.glb
   ```

3. **Ground only, or coarser:**

   ```
   python -m heat3d_gamefiles ue-map "<game>" <map> --no-structures --no-water
   python -m heat3d_gamefiles ue-map "<game>" <map> --ground-spacing 4
   ```

4. **Open `map.glb`** in the 3DHeat viewer's Background / level panel
   ([loading a level](https://holdi601.github.io/3DHeat/levels.html)).

## Options

| Option | Default | Meaning |
|---|---|---|
| `<game>` | required | the game's folder, its `Content/Paks`, or its Steam folder name |
| `<map>` | required | a name as `ue-maps` prints it, or a unique part of one |
| `-o`, `--out FILE` | `<map>.glb` (in `$HEAT3D_LEVELS/<game>/` when that is set) | the file to write |
| `--ground-spacing METRES` | 2 | the landscape's vertex spacing, rounded to a whole number of its own quads |
| `--no-structures` | | leave the HLOD buildings and props out |
| `--no-water` | | leave the water bodies out |

Content compressed with Oodle needs an Oodle library already on the machine
(see [Oodle](reader-oodle.md)).

## Example output

```text
<map> -> map.glb
  ground      <n> triangles from <n> landscape components; <n> of <n> vertices stored twice disagree
  structure   <n> triangles in <n> HLOD meshes
  water       <n> triangles from <n> water bodies
```

The disagreement count is a self-check: neighbouring landscape components
store their shared edge twice, and the two must match. A 3 km map at 2 m is
about 4.6 million ground triangles.

## The parts

`ground:<map>` (the landscape), `structure:<map>` (the HLOD meshes) and
`water:<map>` (water standing above the ground).

**Units:** this is the one export **not in metres**: Unreal centimetres, with Y
and Z swapped (Y up), the frame the 3DHeat Unreal Exporter writes. Telemetry
from the same game uses the same frame, so it lies on the map.

## How it is read and checked

| Part | Read from | Checked against |
|---|---|---|
| ground | each landscape component's 16-bit heightmap, placed by its section base on the landscape's transform | every vertex stored twice (on a seam or a component edge) must agree; disagreements are counted and printed, not smoothed |
| structure | the map's merged HLOD meshes, built by the engine in world space | a mesh is kept only if the bounds its component caches describe its own vertices |
| water | each water body's mesh, laid on the ground grid, kept where it stands above the ground | water sits a few metres above the ground under it, as a river over its bed does |

The landscape's properties are found by shape, not by slot number (slots move
between engine versions). The structures are the simplified stand-ins, not the
full-detail models. Foliage, decals and landscape materials are not exported;
the ground is untextured and shaded by the viewer. Archive details:
[Unreal 5 IoStore](reader-unreal-iostore.md).

**Terms:** games' licences usually allow personal, non-commercial use and forbid
reverse engineering "to the extent that such actions cannot be prohibited by
law". Reading your own install is your decision under them; the output is for
your own use and is not to be shared.
