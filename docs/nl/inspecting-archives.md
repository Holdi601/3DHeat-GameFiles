---
title: Archieven inspecteren
nav_order: 3
lang: "nl"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Archieven inspecteren: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Een spel verpakt zijn bestanden in grote dozen die **archieven** heten. Deze commando's kijken naar het etiket van een doos, tonen wat erin zit, en halen één ding eruit.

Kijk voordat je iets exporteert uit een onbekend spel wat het meelevert. Deze vier commando's lezen een bestand en vertellen wat het is en wat het bevat. Ze schrijven niets, behalve het ene item dat je aan `extract` vraagt.

![identify, list en extract draaien op een klein zip-bestand](../assets/img/inspect-archives.svg)

*Een run op een synthetische zip, opgebouwd als een BeamNG.drive-level.*

## Stap voor stap {#step-by-step}

1. **Vraag wat het bestand is.** `identify` leest de bytes, niet de extensie:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Het noemt het formaat (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity-bundle of `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` of `.modelbin`, BeamNG `.cdae`/`.ter`, zip), de versie, het aantal items en of het versleuteld is.

2. **Lijst wat erin zit.** `list` drukt één regel per item af: grootte, compressie, pad. Beperk het met `--filter`, en begrens het met `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Haal één item eruit.** `extract` schrijft één item (in de map waarin je staat, tenzij `--out` aangeeft waar), op het pad dat `list` heeft afgedrukt (of `#12`, op nummer, in een `.minizip` zonder namen):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` toont en controleert de meshes in een `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Opties {#options}

| Commando | Optie | Betekenis |
|---|---|---|
| `identify` | `<file>` | elk bestand |
| `list` | `<archive>` | `.pak`, `.utoc` (of de `.ucas` ernaast), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | alleen paden die TEXT bevatten |
| | `--limit N` | hoogstens N regels |
| | `--key HEX` | een AES-256-sleutel (64 hexadecimale cijfers) die je al hebt; alleen een versleutelde `.pak` heeft die nodig |
| `extract` | `<archive> <path>` | het archief en het pad van het item, zoals `list` het afdrukt |
| | `--out FILE` | waar het geschreven wordt (standaard: de bestandsnaam van het item) |
| | `--key HEX` | zoals bij `list` |
| `meshes` | `<file>`, `--limit N` | een Unity `SerializedFile`; hoogstens N meshes |

Het hulpmiddel bevat geen sleutels en vindt er geen uit: een versleuteld archief opent alleen met een sleutel die je meegeeft. Een bestand dat het niet kan lezen, wordt in één regel geweigerd met exitcode 1. Elk commando en elke exitcode staat op [Commando's](commands.md). Hoe elk formaat gelezen wordt, staat onder [Archieflezers](archive-readers.md).
