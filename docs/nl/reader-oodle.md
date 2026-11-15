---
title: Oodle
nav_order: 3
lang: "nl"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: gevonden, niet meegeleverd {#oodle-found-not-bundled}

Het meeste uitgeleverde Unreal-materiaal, en sommige Frostbite-payloads, zijn gecomprimeerd met **Oodle** (RAD Game Tools, nu Epic). Oodle is eigen software. Er is geen vrij verspreidbare build en geen Python-implementatie, en `oo2core_*.dll` is in licentie gegeven aan het product dat het meelevert. Daarom **zoekt dit hulpmiddel een kopie die al op jouw computer staat, en laadt die**. Het levert er nooit zelf een mee. FModel en UModel werken op dezelfde manier.

Bron: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Waar het zoekt {#where-it-looks}

Het eerste bestand dat bestaat, wint. Dit is de volgorde:

1. Een expliciet pad dat de aanroeper meegeeft (Python-API).
2. `HEAT3D_OODLE`: een pad naar de DLL, of naar een map die er één bevat.
3. Een ondiepe zoektocht, één map diep, van
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - de `steamapps\common` van elke Steam-bibliotheek

   Voor elke submap `<game>` wordt gekeken in `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` en `<game>\Engine\Binaries\Win64`.

Bestandsnamen die worden geprobeerd, nieuwste eerst: `oo2core_9_win64.dll` tot `oo2core_3_win64.dll`. Het formaat is achterwaarts compatibel, dus een oudere bibliotheek werkt meestal ook.

Het zoeken op alle schijven, recursief, is bewust **niet** gedaan, want dat zou minuten duren. Vindt het niets, stel dan `HEAT3D_OODLE` in:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Een map werkt net zo goed als het bestand zelf: de DLL-namen hierboven worden erin geprobeerd.

Een installatie van Unreal Engine heeft er één onder `Engine\Binaries\ThirdParty\Oodle`. Voor een ontwikkelaar is dat de netste bron. Veel spellen zetten er één naast hun uitvoerbaar bestand. Unreal 5-spellen linken Oodle vaak statisch en leveren geen DLL mee, dus de gevonden kopie kan bij een ander spel horen dan het archief dat gelezen wordt. Het formaat is in beide gevallen hetzelfde.

## Hoe het wordt aangeroepen {#how-it-is-called}

`OodleLZ_Decompress` wordt via `ctypes` aangeroepen, met de verwachte uitvoerlengte (de archiefindex kent die altijd, en Oodle kan haar niet afleiden). Het decoderen is beveiligd tegen vreemde invoer (de invoer is niet te vertrouwen), er is geen CRC-controle (de eigen SHA-1 van de pak dekt de bytes al af), en het draait zonder threads. Een resultaat van de verkeerde lengte is een fout. De bibliotheek wordt één keer per run geladen.

## Als er geen is {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Een item dat niet gedecomprimeerd kan worden, is een fout. Het is nooit plausibel onzin.

De loader werkt alleen op Windows (hij zoekt naar `*_win64.dll`). Bibliotheken voor Linux en macOS worden niet gezocht.
