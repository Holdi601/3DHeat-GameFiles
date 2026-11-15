---
title: "Skoðun skjalasafna"
nav_order: 3
lang: "is"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Skoðun skjalasafna: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Leikur pakkar skrám sínum í stóra kassa sem kallast **skjalasöfn** (archives). Þessar
skipanir skoða miðann á kassa, telja upp hvað er í honum og taka eitt út.

Áður en þú flytur nokkuð út úr ókunnum leik skaltu skoða hvað hann sendir með.
Þessar fjórar skipanir (verbs) lesa skrá og segja þér hvað hún er og hvað hún geymir; þær
skrifa ekkert nema þá einu færslu sem þú biður `extract` um.

![identify, list og extract keyrð á litlu zip](../assets/img/inspect-archives.svg)

*Keyrsla á tilbúnu zip sem er sett upp eins og BeamNG.drive borð.*

## Skref fyrir skref {#step-by-step}

1. **Spurðu hvað skráin er.** `identify` les bætin, ekki skráarendinguna:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Það nefnir sniðið (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity-búnt eða
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` eða
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), útgáfu þess, hversu margar færslur það
   geymir og hvort það er dulkóðað.

2. **Teldu upp hvað er inni.** `list` prentar eina línu fyrir hverja færslu: stærð, þjöppun,
   slóð. Þrengdu það með `--filter`, takmarkaðu það með `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Taktu eina færslu út.** `extract` skrifar eina færslu (í möppuna sem þú ert í,
   nema `--out` segi annað), eftir slóðinni sem `list`
   prentaði (eða `#12`, eftir númeri, í `.minizip` án nafna):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` telur upp og athugar netin (meshes) í `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Valkostir {#options}

| Skipun | Valkostur | Merking |
|---|---|---|
| `identify` | `<file>` | hvaða skrá sem er |
| `list` | `<archive>` | `.pak`, `.utoc` (eða `.ucas` við hlið hennar), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | aðeins slóðir sem innihalda TEXT |
| | `--limit N` | í mesta lagi N línur |
| | `--key HEX` | AES-256 lykill (64 sextándastafir) sem þú átt þegar; aðeins dulkóðað `.pak` þarf hann |
| `extract` | `<archive> <path>` | skjalasafnið og slóð færslunnar eins og `list` prentar hana |
| | `--out FILE` | hvert á að skrifa hana (sjálfgefið: skráarnafn færslunnar) |
| | `--key HEX` | eins og fyrir `list` |
| `meshes` | `<file>`, `--limit N` | Unity `SerializedFile`; í mesta lagi N net |

Verkfærið sendir enga lykla með og endurheimtir enga: dulkóðað skjalasafn opnast aðeins með
lykli sem þú gefur. Skrá sem það getur ekki lesið er hafnað í einni línu með útgöngukóðann 1.
Hver skipun og útgöngukóði er á [Skipanir](commands.md); hvernig hvert snið er
lesið er undir [Skjalasafnalesarar](archive-readers.md).
