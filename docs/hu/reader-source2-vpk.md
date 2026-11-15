---
title: "Source 2 `.vpk`"
nav_order: 6
lang: "hu"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Listázza és kicsomagolja** a Valve VPK archívumait, az 1-es és 2-es verziót, beleértve a
felosztott archívumokat és a könyvtárfájlban tárolt adatokat. Minden bejegyzés ellenőrizhető a saját
CRC-jével. Ez az egyetlen konténerformátum itt, amelyet a gyártója dokumentál. Játékok: Counter-Strike 2,
Dota 2, Half-Life: Alyx, és más Source 2-es játékok.

Forrás: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Parancsok: `identify`, `list`, `extract`.

## Elrendezés {#layout}

```
u32 magic 0x55AA1234, u32 version (1 or 2), u32 tree size
  (version 2: 16 more header bytes; header 12 or 28 bytes)
directory tree:
  extension        "vmdl_c", then "vtex_c", ..., then ""
    path           "maps/example_map", then ""
      file name    "world_layer0", then ""
        u32 crc, u16 preload size, u16 archive index, u32 offset, u32 length, u16 0xFFFF
        [preload bytes]
```

- Három egymásba ágyazott ciklus, mindegyik üres sztringgel zárul, így az olvasó, amely darabszámot
  vár, nem talál semmit. Az útvonalak csoportonként egyszer tárolódnak, és mind a három részből
  állnak össze. Egyetlen szóköz azt jelenti, hogy nincs mappa vagy kiterjesztés.
- Minden rekord `0xFFFF`-fel zárul. Ezt ellenőrzi, így az olvasó, amely elvesztette a helyét, azonnal
  megáll ("the directory is not being read at the right offset").
- **Felosztott archívumok:** a `pak01_dir.vpk` tartalmazza a könyvtárat, az adat pedig a
  `pak01_000.vpk`, `pak01_001.vpk`... fájlokban van, a bejegyzés archívumindexe alapján kiválasztva.
- **`0x7FFF` archívumindex** azt jelenti, hogy a bájtok maga a könyvtárfájlban vannak, a fa után. Ha
  valódi indexként olvassa, az olvasó a `pak01_32767.vpk` fájlt keresi.
- **Előtöltés:** a kis fájlok egészben tárolódnak a könyvtárban. Ekkor a 0 hosszúság nem hiba.

## Parancsok {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

Az `identify` kiírja a verziót, a bejegyzések számát és az első `.nav` fájlt. A `list` minden
bejegyzést `stored`-ként mutat, mert a VPK nem tömörít. Az `extract` ellenőrzés nélkül írja ki a
bájtokat. Pythonban a `VpkArchive(path).verify(name)` összeveti egy bejegyzés bájtjait a könyvtárban
rögzített CRC-vel.

## A navigációs háló {#the-navigation-mesh}

Egy pálya a fordított geometria mellett a **navigációs hálóját** (`maps/<map>.nav`) is szállítja. Játékos
pozíciók hőtérképéhez messze a hasznosabb a kettő közül, mert a navigációs háló *maga a járható talaj*,
már kiszámítva, és ezredakkora méretben. A telepített játékon futó teszt ellenőrzi, hogy egy szállított
pálya `.nav` fájlja a Source navigációs mágikus számmal, `CE FA ED FE`-vel kezdődik.

## Ellenőrizve {#verified}

Egy játék szállított pályaarchívumainak minden mintavételezett bejegyzése bájtra pontosan megegyezett a
CRC-jével, és minden pályaarchívum feldolgozható.
A telepített játékon futó tesztek megismétlik a CRC-ellenőrzést, a 25 véletlen bejegyzésen mindegyik
legfeljebb négy pályaarchívumból.

## Nincs megvalósítva {#not-implemented}

- A Source 2 fordított eszközeinek (`.vmdl_c`, `.vtex_c`) dekódolása. Ezek saját darabolt bináris
  fájlok, ugyanolyan feladat, mint az Unreal- és Frostbite-mesh formátumok. A külön 3DHeat CS2 eszköz
  kezeli a CS2 pálya geometriáját.
- A CS2 navigációs háló dekódolása. Formátuma a 36-os verzió, és eltér a széles körben dokumentált
  Source 1-es formátumtól. Bájtjai szerkezetesek, nem tömörítettek (entrópia 6,2, 31% nulla), de csak
  a szavak 3%-a olvasható koordinátaként, így az elrendezés nem a kézenfekvő, és még nincs
  kikövetkeztetve.
