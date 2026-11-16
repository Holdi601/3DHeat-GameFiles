---
title: Command reference
nav_order: 3
---

# Command reference

This page is generated from the program's own `--help` by `tools/gen_docs_reference.py`;
do not edit it by hand. The other pages explain each command step by step.

## `python -m heat3d_gamefiles`

```text
usage: heat3d_gamefiles [-h]
                        {identify,list,extract,meshes,course,courses,races,cars,terrain,levels,level,enfusion-worlds,enfusion-world,ue-maps,ue-map} ...

Read level data out of shipped game archives.

positional arguments:
  {identify,list,extract,meshes,course,courses,races,cars,terrain,levels,level,enfusion-worlds,enfusion-world,ue-maps,ue-map}
    identify            say what a file is
    list                list what is inside an archive
    extract             write one entry to disk
    meshes              list the meshes in a Unity container
    course              export the ground around a lap (by the Forza, BeamNG.drive or
                        AC Rally tool)
    courses             every course in a recorded lap library (heat3d-forza-maps)
    races               every race an installed Forza defines (heat3d-forza-maps)
    cars                every car of an installed Forza at low detail (heat3d-forza-
                        maps)
    terrain             a piece of Forza terrain by world coordinates (heat3d-forza-
                        maps)
    levels              the levels of an installed Frostbite game (heat3d-battlefield-
                        maps)
    level               a Frostbite level as one .glb (heat3d-battlefield-maps)
    enfusion-worlds     the worlds of an installed Arma Reforger (heat3d-reforger-
                        maps)
    enfusion-world      an Arma Reforger world as one .glb (heat3d-reforger-maps)
    ue-maps             list the World Partition maps of an Unreal 5 game
    ue-map              export an Unreal 5 World Partition map: landscape, HLOD
                        structures, water

options:
  -h, --help            show this help message and exit

Encrypted archives need a key you already hold; this tool has none and recovers none.
It reads the files of your own installation and ships nothing from a game.
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

Run by [`heat3d-forza-maps`](https://holdi601.github.io/3DHeat-Ext-Forza/cli-reference.html), [`heat3d-beamng-maps`](https://holdi601.github.io/3DHeat-Ext-BeamNG/cli-reference.html), [`heat3d-acrally-maps`](https://holdi601.github.io/3DHeat-Ext-ACRally/cli-reference.html) with the same arguments; see its command reference.

## `courses`

Run by [`heat3d-forza-maps`](https://holdi601.github.io/3DHeat-Ext-Forza/cli-reference.html) with the same arguments; see its command reference.

## `races`

Run by [`heat3d-forza-maps`](https://holdi601.github.io/3DHeat-Ext-Forza/cli-reference.html) with the same arguments; see its command reference.

## `cars`

Run by [`heat3d-forza-maps`](https://holdi601.github.io/3DHeat-Ext-Forza/cli-reference.html) with the same arguments; see its command reference.

## `terrain`

Run by [`heat3d-forza-maps`](https://holdi601.github.io/3DHeat-Ext-Forza/cli-reference.html) with the same arguments; see its command reference.

## `levels`

Run by [`heat3d-battlefield-maps`](https://holdi601.github.io/3DHeat-Ext-Battlefield/cli-reference.html) with the same arguments; see its command reference.

## `level`

Run by [`heat3d-battlefield-maps`](https://holdi601.github.io/3DHeat-Ext-Battlefield/cli-reference.html) with the same arguments; see its command reference.

## `enfusion-worlds`

Run by [`heat3d-reforger-maps`](https://holdi601.github.io/3DHeat-Ext-Reforger/cli-reference.html) with the same arguments; see its command reference.

## `enfusion-world`

Run by [`heat3d-reforger-maps`](https://holdi601.github.io/3DHeat-Ext-Reforger/cli-reference.html) with the same arguments; see its command reference.

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
  -o, --out OUT         the .glb (default: <map>.glb, in $HEAT3D_LEVELS/<game> when
                        that is set)
  --ground-spacing METRES
                        the landscape's vertex spacing in the file, rounded to its own
                        grid (default 2)
  --no-structures       leave out the HLOD buildings and props
  --no-water            leave out the water bodies
```
