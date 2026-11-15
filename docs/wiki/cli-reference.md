# Command reference

This page is generated from the program's own `--help` by `tools/gen_docs_reference.py`;
do not edit it by hand. The other pages explain each command step by step.

## `python -m heat3d_gamefiles`

```text
usage: heat3d_gamefiles [-h]
                        {identify,list,extract,meshes,course,courses,races,cars,terrain,levels,level,ue-maps,ue-map,enfusion-worlds,enfusion-world} ...

Read level data out of shipped game archives.

positional arguments:
  {identify,list,extract,meshes,course,courses,races,cars,terrain,levels,level,ue-maps,ue-map,enfusion-worlds,enfusion-world}
    identify            say what a file is
    list                list what is inside an archive
    extract             write one entry to disk
    meshes              list the meshes in a Unity container
    course              export the ground around a lap, working out the rest
    courses             export every course in a recorded lap library, one file each
    races               every race an installed Forza defines: its own assets, venues,
                        and the exports of it
    cars                every car of an installed Forza at low detail, in one file for
                        the viewer
    terrain             cut a piece of Forza terrain out, by world coordinates
    levels              list the levels of an installed Frostbite game
    level               export a Frostbite level: its terrain backdrop and placed
                        meshes
    ue-maps             list the World Partition maps of an Unreal 5 game
    ue-map              export an Unreal 5 World Partition map: landscape, HLOD
                        structures, water
    enfusion-worlds     list the worlds of an installed Arma Reforger
    enfusion-world      export an Arma Reforger world: terrain, its colour, the sea,
                        building boxes

options:
  -h, --help            show this help message and exit

Encrypted archives need a key you already hold; this tool has none and recovers none.
What you point it at is subject to that game's own licence.
```

## `identify`

```text
usage: heat3d_gamefiles identify [-h] path

positional arguments:
  path

options:
  -h, --help  show this help message and exit
```

## `list`

```text
usage: heat3d_gamefiles list [-h] [--filter FILTER] [--limit LIMIT] [--key KEY] path

positional arguments:
  path             an Unreal .pak or IoStore .utoc, a Source 2 .vpk (the _dir.vpk), a
                   ForzaTech .minizip, or a zip

options:
  -h, --help       show this help message and exit
  --filter FILTER  only paths containing this text
  --limit LIMIT
  --key KEY        an AES-256 key in hex (64 digits), if you hold one; only an
                   encrypted .pak needs it
```

## `extract`

```text
usage: heat3d_gamefiles extract [-h] [--out OUT] [--key KEY] path entry

positional arguments:
  path        an Unreal .pak or IoStore .utoc, a Source 2 .vpk (the _dir.vpk), a
              ForzaTech .minizip, or a zip
  entry       the path as list prints it (a .minizip without its manifest: #number)

options:
  -h, --help  show this help message and exit
  --out OUT
  --key KEY   an AES-256 key in hex (64 digits), if you hold one; only an encrypted
              .pak needs it
```

## `meshes`

```text
usage: heat3d_gamefiles meshes [-h] [--limit LIMIT] path

positional arguments:
  path

options:
  -h, --help     show this help message and exit
  --limit LIMIT
```

## `course`

```text
usage: heat3d_gamefiles course [-h] [--texture-size {2048,1024,512}] [--no-textures]
                               [--season {summer,autumn,winter,spring}] [--no-placed]
                               [--trees] [--detail-budget DETAIL_BUDGET] [-o OUT]
                               [--track TRACK] [--margin MARGIN]
                               [--game {forza,beamng,acrally}] [--level LEVEL]
                               [--install INSTALL]
                               lap

positional arguments:
  lap                   a lap or course: a file written by heat3d_capture, a lap or
                        course folder from a recorded library, or just a course's name

options:
  -h, --help            show this help message and exit
  --texture-size {2048,1024,512}
                        ground texture per 512 m tile, in pixels (2048 = 25 cm a
                        pixel)
  --no-textures         flat colours only: a far smaller file, and no ground detail
  --season {summer,autumn,winter,spring}
                        which season's ground maps and model textures to use
  --no-placed           terrain only: leave out kerbs, barriers, tyre walls, signs and
                        buildings
  --trees               also place trees and bushes (many triangles, and they hide the
                        road)
  --detail-budget DETAIL_BUDGET
                        a ceiling on triangles for everything placed; the costliest
                        models drop to coarser levels of detail until it fits, and
                        past that the furthest copies are left out (default: enough to
                        keep every copy, and at least 1,500,000; kerbs always stay at
                        full detail)
  -o, --out OUT         where to write the .glb (default: the course's name)
  --track TRACK         the track folder, if the installed game should not be searched
                        for
  --margin MARGIN       metres of ground to keep either side of the driving (default
                        80)
  --game {forza,beamng,acrally}
                        which game the lap is from (default: what the lap file says,
                        else Forza)
  --level LEVEL         BeamNG, AC Rally: the level or stage, if it should not be
                        found from the lap
  --install INSTALL     BeamNG, AC Rally: the game's folder, if it is not in a Steam
                        library
```

## `courses`

```text
usage: heat3d_gamefiles courses [-h] [--texture-size {2048,1024,512}] [--no-textures]
                                [--season {summer,autumn,winter,spring}] [--no-placed]
                                [--trees] [--detail-budget DETAIL_BUDGET] [-o OUT]
                                [--library LIBRARY] [--only ONLY [ONLY ...]] [--force]
                                [--track TRACK] [--margin MARGIN]

options:
  -h, --help            show this help message and exit
  --texture-size {2048,1024,512}
                        ground texture per 512 m tile, in pixels (2048 = 25 cm a
                        pixel)
  --no-textures         flat colours only: a far smaller file, and no ground detail
  --season {summer,autumn,winter,spring}
                        which season's ground maps and model textures to use
  --no-placed           terrain only: leave out kerbs, barriers, tyre walls, signs and
                        buildings
  --trees               also place trees and bushes (many triangles, and they hide the
                        road)
  --detail-budget DETAIL_BUDGET
                        a ceiling on triangles for everything placed; the costliest
                        models drop to coarser levels of detail until it fits, and
                        past that the furthest copies are left out (default: enough to
                        keep every copy, and at least 1,500,000; kerbs always stay at
                        full detail)
  -o, --out OUT         folder to write into (default ./courses)
  --library LIBRARY     the lap library (default: FH Companion's, under
                        %LOCALAPPDATA%)
  --only ONLY [ONLY ...]
                        just the courses whose names contain these
  --force               export again what is already there
  --track TRACK         the track folder, if not the installed game's
  --margin MARGIN       metres either side of the driving (default 80)
```

## `races`

```text
usage: heat3d_gamefiles races [-h] [-o OUT] [--library LIBRARY] [--track TRACK]
                              [--markdown MARKDOWN]

options:
  -h, --help           show this help message and exit
  -o, --out OUT        the folder `courses` writes to (default ./courses)
  --library LIBRARY    the lap library (default: FH Companion's)
  --track TRACK        the track folder, if not the installed game's
  --markdown MARKDOWN  also write the table here
```

## `cars`

```text
usage: heat3d_gamefiles cars [-h] [-o OUT] [--game GAME]

options:
  -h, --help     show this help message and exit
  -o, --out OUT  the file to write (default ./forza.h3dcars)
  --game GAME    the game's folder, if not the installed one found
```

## `terrain`

```text
usage: heat3d_gamefiles terrain [-h] [--texture-size {2048,1024,512}] [--no-textures]
                                [--season {summer,autumn,winter,spring}] [--no-placed]
                                [--trees] [--detail-budget DETAIL_BUDGET] -o OUT
                                [--box X0 Z0 X1 Z1] [--route ROUTE] [--margin MARGIN]
                                path

positional arguments:
  path                  a track folder under media/Tracks

options:
  -h, --help            show this help message and exit
  --texture-size {2048,1024,512}
                        ground texture per 512 m tile, in pixels (2048 = 25 cm a
                        pixel)
  --no-textures         flat colours only: a far smaller file, and no ground detail
  --season {summer,autumn,winter,spring}
                        which season's ground maps and model textures to use
  --no-placed           terrain only: leave out kerbs, barriers, tyre walls, signs and
                        buildings
  --trees               also place trees and bushes (many triangles, and they hide the
                        road)
  --detail-budget DETAIL_BUDGET
                        a ceiling on triangles for everything placed; the costliest
                        models drop to coarser levels of detail until it fits, and
                        past that the furthest copies are left out (default: enough to
                        keep every copy, and at least 1,500,000; kerbs always stay at
                        full detail)
  -o, --out OUT
  --box X0 Z0 X1 Z1     the region to cut, in the game's metres
  --route ROUTE         a route JSON with "bounds" {"min": [x, y, z], "max": [x, y,
                        z]}, as heat3d_capture route and laps write it; its x and z
                        extent is the region, and its positions, if it has at least
                        10, narrow it to a corridor
  --margin MARGIN       metres to add around a route, so the verge comes with the road
```

## `levels`

```text
usage: heat3d_gamefiles levels [-h] [--install INSTALL]

options:
  -h, --help         show this help message and exit
  --install INSTALL  the game's folder, if not in a Steam library
```

## `level`

```text
usage: heat3d_gamefiles level [-h] [-o OUT] [--install INSTALL]
                              [--detail-budget DETAIL_BUDGET] [--textures [PIXELS]]
                              [--ground-texture [METRES]] [--navmesh] [--by-mesh]
                              [--clamped-uvs] [--ground-spacing METRES] [--skip TEXT]
                              level

positional arguments:
  level                 the level's name as `levels` lists it, or its .toc

options:
  -h, --help            show this help message and exit
  -o, --out OUT         the .glb (default: <level>.glb)
  --install INSTALL     the game's folder, if not in a Steam library
  --detail-budget DETAIL_BUDGET
                        a ceiling on triangles; the costliest meshes drop to coarser
                        levels of detail until it fits (default: every copy at its
                        coarsest, plus a quarter, at least 1,500,000; the terrain
                        stays at full detail)
  --textures [PIXELS]   write each surface's colour map, no larger than PIXELS a side
                        (default 512 when given without a size); without it, flat
                        colours
  --ground-texture [METRES]
                        bake the terrain decals (roads, aprons, markings) into the
                        ground's colour, METRES a pixel (default 0.5 when given
                        without a size), in tiles of at most 4096 pixels
  --navmesh             add the soldiers' walkable surfaces from the level's
                        navigation mesh as the part nav:walkable
  --by-mesh             for finding what a part is: one part per source mesh and
                        material, named '<part> | <mesh> | <material>' (a much larger
                        file)
  --clamped-uvs         for a renderer that cannot repeat a texture: cut every
                        textured triangle into pieces with UVs inside 0..1, and draw
                        the ones that would need more than 4 pieces in their texture's
                        average colour (default: UVs as the game has them, with a
                        repeating sampler)
  --ground-spacing METRES
                        the terrain heightfield's finest spacing (default 4; 0 leaves
                        it out)
  --skip TEXT           leave out static model groups whose partition name contains
                        TEXT (repeatable)
```

## `ue-maps`

```text
usage: heat3d_gamefiles ue-maps [-h] game

positional arguments:
  game        the game's folder, its Content/Paks, or a Steam game folder name (e.g.
              "My Game")

options:
  -h, --help  show this help message and exit
```

## `ue-map`

```text
usage: heat3d_gamefiles ue-map [-h] [-o OUT] [--ground-spacing METRES]
                               [--no-structures] [--no-water]
                               game map

positional arguments:
  game                  the game's folder, its Content/Paks, or a Steam game folder
                        name (e.g. "My Game")
  map                   the map's name as `ue-maps` lists it

options:
  -h, --help            show this help message and exit
  -o, --out OUT         the .glb (default: <map>.glb)
  --ground-spacing METRES
                        the landscape's vertex spacing in the file, rounded to its own
                        grid (default 2)
  --no-structures       leave out the HLOD buildings and props
  --no-water            leave out the water bodies
```

## `enfusion-worlds`

```text
usage: heat3d_gamefiles enfusion-worlds [-h] [--install INSTALL]

options:
  -h, --help         show this help message and exit
  --install INSTALL  the game's folder, if not in a Steam library
```

## `enfusion-world`

```text
usage: heat3d_gamefiles enfusion-world [-h] [-o OUT] [--install INSTALL]
                                       [--ground-spacing METRES]
                                       [--texture-size PIXELS] [--no-structures]
                                       [--trees]
                                       world

positional arguments:
  world                 the world's name as `enfusion-worlds` lists it

options:
  -h, --help            show this help message and exit
  -o, --out OUT         the .glb (default: <world>.glb)
  --install INSTALL     the game's folder, if not in a Steam library
  --ground-spacing METRES
                        terrain vertex spacing in the file (default 2, the terrain's
                        own)
  --texture-size PIXELS
                        the ground colour image's larger side (default 4096; 0 for
                        none)
  --no-structures       leave out the placed models
  --trees               also place trees and other vegetation (as boxes)
```
