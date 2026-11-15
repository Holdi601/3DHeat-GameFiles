---
title: Vstupy kola
nav_order: 7
lang: "cs"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Vstupy kola {#lap-inputs}

**Soubor kola** je seznam bodů x, y, z: kam auto jelo. Nejrychlejší ručně vytvořený
je CSV z části [5. Tabulka `.csv`](#5-a-csv-table) níže.

Kolo říká exportu trati **kam auto jelo**. Nic dalšího v něm se nepoužívá: rychlost,
ovládání a g-síly patří telemetrické části 3DHeat. Nástroj čte pozice v metrech
světa hry a, pokud to soubor říká, hru a trať.

Zdroj: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Co přijímá `course` {#what-course-accepts}

Formát se pozná podle obsahu souboru, ne podle názvu, s tím, že `.npz` a `.csv` se
poznají podle přípony a všechno ostatní se zkouší jako JSON.

### 1. Dokument `heat3d-lap` (libovolná hra) {#a-heat3d-lap-document-any-game}

Zapisují ho telemetrické záznamníky 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y` a `channels.z` jsou povinné. Řádky, kde některá z těchto
  hodnot není konečné číslo, se zahodí. Ostatní kanály se ignorují.
- `game` rozhoduje o exportu (viz [Příkazy](commands.md#which-game)).
- `track` používá Assetto Corsa Rally, aby nejdřív zkusilo jmenovanou etapu.
- Osy: y je výška. Kola Forzy a AC Rally používají vodorovné osy hry tak, jak je
  zapisuje záznamník. Kola BeamNG se čekají v rámci prohlížeče,
  `(x, z, -y)` světa BeamNG se Z nahoru (viz [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Soubor trasy {#a-route-file}

Zapisují ho `heat3d_capture route` a `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` je seznam `[x, y, z]`. Soubor trasy s `bounds` a bez pozic funguje
také: jeho dva rohy tvoří čáru bez plochy, ale je to použitelný box.

### 3. Soubor kola FH Companion {#an-fh-companion-lap-file}

Soubory jednotlivých kol z nahrané knihovny FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Chybějící `X`, `Y` nebo `Z` se čte jako 0. Soubory se zapisují s značkou pořadí
bajtů, takže všechen JSON se čte jako `utf-8-sig`.

### 4. Záznam `.npz` {#a-npz-recording}

Archiv NumPy s polem `positions` tvaru (n, 3).

### 5. Tabulka `.csv` {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Sloupce pojmenované `x`, `y`, `z` (velká a malá písmena a mezery kolem nich se
  ignorují) jsou povinné. Ostatní sloupce se ignorují.
- Řádky začínající `#` se přeskočí. Pokud **první** řádek je `# {json}`, čtou se z
  něj `game` a `track`.
- Řádky, které nejdou přečíst jako čísla, se přeskočí.

### 6. Složka {#a-folder}

Složka se prohledává **rekurzivně** na soubory `.json`, `.npz` a `.csv` a všechny se
spojí do jedné projeté čáry. Tak se ukládá celá nahraná trať: knihovna FH
Companion vnořuje složky podle třídy, auta, ladění a štítku.

- `course.json` se přeskočí podle jména (jsou to metadata, ne kolo).
- Soubor, který nejde přečíst, se tiše přeskočí. Jeden špatný soubor mezi stovkami
  nezmaří ostatní.
- Konzole hlásí, kolik souborů kol se načetlo (`12 laps, 18,400 samples`).
- Složka dostane hru, kterou jmenují její soubory, když jmenují **jen jednu**.
  Soubor, který žádnou hru nejmenuje (kolo FH Companion, `course.json`, CSV bez
  popisného řádku), se nepočítá, takže jeden z nich mezi nahrávkami hry složce hru
  nevezme. Soubory jmenující dvě různé hry jsou směs a složka nedostane žádnou.
  Složka bez hry se exportuje jako Forza, pokud `--game` neříká jinak.
- Pokud se nic nepřečte: "no readable laps under <folder>".

### 7. Název trati {#a-course-name}

Pokud argument není existujícím souborem nebo složkou, hledá se jako název tratě
v knihovně FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. složka, jejíž název bez přípony ` (course_...)` se rovná názvu (bez ohledu na
   velikost písmen);
2. jinak jediná složka, jejíž název ho obsahuje.

Takže `"Example Circuit"` najde
`Example Circuit (course_1200_3400_to_1175_3400)`, aniž by někdo znal souřadnice.
Více shod je chyba, která je vypíše. Trať nalezená podle názvu nenese hru, takže se
exportuje jako Forza, pokud `--game` neříká jinak.

## Co přijímá `terrain --route` {#what-terrain---route-accepts}

`terrain` potřebuje pole `bounds` souboru trasy (tvar 2 výše),
`{"min": [x, y, z], "max": [x, y, z]}`. Bez `bounds` se zastaví s
"<file> has no bounds; --route takes a route file with "bounds": {...}". Soubor se
čte jako UTF-8 s značkou pořadí bajtů nebo bez ní, stejně jako každé kolo v JSON.
Pokud má soubor také aspoň 10 pozic čitelných podle výše uvedených pravidel, zúží
řez na koridor a řídí detail.

## Jak se kolo používá {#how-the-lap-is-used}

| Použití | Podrobnosti |
|---|---|
| název | jméno souboru, nebo název složky bez ` (course_...)`; stane se výchozím názvem výstupního souboru |
| ujetá vzdálenost | součet mezer mezi po sobě jdoucími vzorky (vypíše se jako `m driven`; u složky sem patří i skoky mezi soubory) |
| box | rozsah x a z, rozšířený o `--margin`; výška se nikdy neomezuje |
| koridor | x a z každého vzorku, viz [Export trati](course-export.md#the-corridor) |
| detail | vzdálenost každé umístěné kopie k nejbližšímu vzorku, viz [Úrovně detailu a rozpočet](detail-budget.md) |

Kolo s méně než dvěma vzorky se odmítne ("holds no driving").

## Chyby {#errors}

| Zpráva | Význam |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | soubor není JSON (a není `.npz` ani `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON jiného tvaru |
| `<file> has no x, y and z columns` | CSV bez těchto hlaviček |
| `<file> has no positions array` | `.npz` bez `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | název, ale žádná knihovna FH Companion |
| `'<name>' matches 3 courses: A, B, C` | buďte konkrétnější |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | jen pro hledání podle názvu a pro `courses` |
