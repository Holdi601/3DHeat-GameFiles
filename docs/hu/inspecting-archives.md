---
title: "Archívumok vizsgálata"
nav_order: 3
lang: "hu"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Archívumok vizsgálata: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

A játékok a fájljaikat nagy dobozokba, úgynevezett **archívumokba** csomagolják. Ezek a parancsok
megnézik a doboz címkéjét, felsorolják, mi van benne, és kivesznek belőle egy dolgot.

Ismeretlen játékból bármit exportálás előtt nézd meg, mit szállít. Ez a négy parancs fájlt olvas, és
megmondja, mi az, és mit tartalmaz; az `extract` által kért egyetlen bejegyzésen kívül semmit nem ír.

![identify, list és extract egy kis zipen futva](../assets/img/inspect-archives.svg)

*Futtatás egy BeamNG.drive pályához hasonlóan felépített, kitalált zipen.*

## Lépésről lépésre {#step-by-step}

1. **Kérdezd meg, mi a fájl.** Az `identify` a bájtokat olvassa, nem a kiterjesztést:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Megmondja a formátumot (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle vagy
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` vagy `.modelbin`, BeamNG
   `.cdae`/`.ter`, zip), a verzióját, azt, hány bejegyzést tartalmaz, és hogy titkosított-e.

2. **Sorold fel, mi van benne.** A `list` soronként egy bejegyzést ír ki: méret, tömörítés,
   útvonal. Szűkítsd a `--filter` kapcsolóval, korlátozd a `--limit` kapcsolóval:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Vegyél ki egy bejegyzést.** Az `extract` egy bejegyzést ír ki (abba a mappába, amelyben
   állsz, hacsak a `--out` nem mondja meg, hová), a `list` által kiírt útvonal alapján (vagy számmal,
   `#12` alakban, a nevek nélküli `.minizip`-ben):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** a `meshes` felsorolja és ellenőrzi a meshfeleket egy `SerializedFile`-ban:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Kapcsolók {#options}

| Parancs | Kapcsoló | Jelentés |
|---|---|---|
| `identify` | `<file>` | bármilyen fájl |
| `list` | `<archive>` | `.pak`, `.utoc` (vagy mellette lévő `.ucas`), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | csak a TEXT-et tartalmazó útvonalak |
| | `--limit N` | legfeljebb N sor |
| | `--key HEX` | egy AES-256 kulcs (64 hexadecimális számjegy), amelyet már birtokolsz; csak a titkosított `.pak` igényli |
| `extract` | `<archive> <path>` | az archívum és a bejegyzés útvonala, ahogy a `list` kiírja |
| | `--out FILE` | hová írja (alapértelmezés: a bejegyzés fájlneve) |
| | `--key HEX` | mint a `list`-nél |
| `meshes` | `<file>`, `--limit N` | egy Unity `SerializedFile`; legfeljebb N mesh |

Az eszköz nem tartalmaz kulcsokat, és nem állít elő egyet sem: a titkosított archívum csak az általad
megadott kulccsal nyílik meg. Amit nem tud beolvasni, azt egy sorban elutasítja, 1-es kilépési
kóddal. Minden parancs és kilépési kód a [Parancsok](commands.md) oldalon található; az egyes
formátumok olvasása az [Archívum-olvasók](archive-readers.md) alatt van.
