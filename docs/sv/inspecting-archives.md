---
title: Titta in i arkiv
nav_order: 3
lang: "sv"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Titta in i arkiv: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Ett spel packar sina filer i stora lådor som kallas **arkiv**. Dessa kommandon
tittar på lådans etikett, listar vad som finns i den och tar ut en sak.

Innan du exporterar något från ett okänt spel, titta på vad det levereras med.
Dessa fyra verb läser en fil och säger vad den är och vad den innehåller; de
skriver ingenting utom den enda post du ber `extract` om.

![identify, list och extract körs på en liten zip-fil](../assets/img/inspect-archives.svg)

*En körning på en syntetisk zip-fil uppbyggd som en nivå i BeamNG.drive.*

## Steg för steg {#step-by-step}

1. **Fråga vad filen är.** `identify` läser bytena, inte filändelsen:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Den anger formatet (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity-bundle eller
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` eller
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), dess version, hur många poster den
   innehåller och om den är krypterad.

2. **Lista vad som finns inuti.** `list` skriver en rad per post: storlek,
   komprimering, sökväg. Begränsa med `--filter`, och ta bort överflödiga rader med `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Ta ut en post.** `extract` skriver en post (till mappen du står i, om inte
   `--out` anger något annat), med den sökväg som `list` skrev ut (eller `#12`, med
   nummer, i en `.minizip` utan namn):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` listar och kontrollerar meshar i en `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Alternativ {#options}

| Verb | Alternativ | Betydelse |
|---|---|---|
| `identify` | `<file>` | valfri fil |
| `list` | `<archive>` | `.pak`, `.utoc` (eller `.ucas` bredvid den), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | bara sökvägar som innehåller TEXT |
| | `--limit N` | högst N rader |
| | `--key HEX` | en AES-256-nyckel (64 hexsiffror) som du redan har; bara en krypterad `.pak` behöver den |
| `extract` | `<archive> <path>` | arkivet och postens sökväg så som `list` skriver ut den |
| | `--out FILE` | var den ska skrivas (standard: postens filnamn) |
| | `--key HEX` | som för `list` |
| `meshes` | `<file>`, `--limit N` | en Unity-`SerializedFile`; högst N meshar |

Verktyget levereras utan nycklar och återskapar inga. Ett krypterat arkiv öppnas
bara med en nyckel som du skickar in. En fil som verktyget inte kan läsa avvisas
med en rad och slutkod 1. Varje verb och slutkod finns i [Kommandon](commands.md);
hur varje format läses finns under [Arkivläsare](archive-readers.md).
