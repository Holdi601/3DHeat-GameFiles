---
title: "Forza autók"
nav_order: 6
lang: "hu"
source: forza-cars.md
source_hash: "e1b48f2525db"
nav_exclude: true
search_exclude: true
---
# Forza autók: `cars` {#forza-cars-cars}

Egy telepített Forza minden autóját a játék saját, alacsony részletességű modelljével egyetlen
fájlba írja a megtekintő Versenyelemzés fülének (minden megtett körhöz egy autót rajzol), így minden
rögzített autó a saját alakjában, valódi méretében jelenik meg.

![cars --help](../assets/img/cars-help.svg)

## Lépésről lépésre {#step-by-step}

1. **Futtasd** a játékkal, amely telepítve van (az a Steam-könyvtárakban és a
   `C:\XboxGames` mappában található):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Vagy add meg a játék mappáját:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza mappa>" -o forza.h3dcars
   ```

2. **Töltsd be a megtekintőbe**: a nézetbeállításokban a **Autófájl betöltése...** gombot, vagy húzd a
   fájlt a versenyfülre; a böngészőben marad. Azok a körök, amelyeknek a rajtszáma szerepel a
   fájlban, ekkor pontosan azzal az autóval jelennek meg (lásd a megtekintő
   [verseny-visszajátszás dokumentációját](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Futtasd újra**, amikor a játékba új autók kerülnek. Másodpercekig tart, és körülbelül 5 MB-ot ír.

## Kapcsolók {#options}

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars`, vagy a `$HEAT3D_LEVELS/forza/forza.h3dcars`, ha az be van állítva | az írandó fájl |
| `--game FOLDER` | a megtalált telepített játék | a játék mappája |

## Mi van a fájlban {#what-is-in-the-file}

Minden `media/Cars` alatti autó-archívumhoz: a benne lévő `ProxyLOD` modell (kb. 900
háromszög), az autó rajtszáma a telemetria szerint, márkája, modelljelzése és gyártási éve az
archívum nevéből, valamint a kerekei és hátsó lámpái. Az alakzatok méterben vannak, 1:1 arányban az
autóval. Az olyan archívumot, amelyben nincs ilyen modell (például forgalmi díszlet), név szerint
megnevezi és kihagyja.

A fájl a 3DHeat megtekintőnek készült; elrendezése annak, aki máshol olvassa
([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Rész | Elrendezés |
|---|---|
| teljes fájl | gzip-tömörítve |
| azonosító | a 8 bájt `H3DCARS1` |
| fejléc hossza | little-endian u32 |
| fejléc | UTF-8 JSON: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| kitöltés | szóközök a 4 bájt többszöröséig |
| adat | autónként: a csúcspontok három-három i16 értékként (milliméterben; x jobbra, y felfelé, z előre), majd a háromszögek három-három u16 értékként |

Minden `cars` bejegyzés: `key`, `ordinals` (az autó számai a telemetria szerint), `make`, `model`,
`year`, `height` és `length` (m), `wheels` (kerekenként `[x, y, z, sugár]`, m), `lights`
(hátsó lámpa pontjai `[x, y, z]`, m), valamint `vertexAt`, `vertices`, `faceAt`, `faces` (bájteltolás
az adat elejétől, és darabszámok).

A fájl a játék tartalmát hordozza: ahhoz a géphez készült, amelyen létrejött, nem arra, hogy
továbbadják ([Szabályok és licencek](rules-and-licences.md)).
