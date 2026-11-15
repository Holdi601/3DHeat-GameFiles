---
title: "Pregled arhivov"
nav_order: 3
lang: "sl"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Pregled arhivov: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Igra svoje datoteke pakira v velike škatle, imenovane **arhivi**. Ti ukazi pogledajo nalepko škatle, izpišejo, kaj je v njej, in izvlečejo eno stvar.

Preden izvozite karkoli iz neznane igre, si oglejte, kaj ponuja. Ti štirje ukazi berejo datoteko in vam povejo, kaj je in kaj vsebuje. Ne zapišejo ničesar, razen enega vnosa, ki ga zahtevate z `extract`.

![identify, list in extract na majhnem zipu](../assets/img/inspect-archives.svg)

*Zagon na sintetičnem zipu, zgrajenem kot nivo BeamNG.drive.*

## Korak za korakom {#step-by-step}

1. **Vprašajte, kaj je datoteka.** `identify` prebere bajte, ne pripone:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Imenuje obliko (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle ali `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` ali `.modelbin`, BeamNG `.cdae`/`.ter`, zip), njeno različico, koliko vnosov vsebuje in ali je šifrirana.

2. **Izpišite, kaj je notri.** `list` izpiše po eno vrstico na vnos: velikost, stiskanje, pot. Zožite ga z `--filter`, omejite pa z `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Izvlecite en vnos.** `extract` zapiše en vnos (v mapo, v kateri ste, razen če `--out` pove drugače) po poti, ki jo je izpisal `list` (ali `#12`, po številki, v `.minizip` brez imen):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` izpiše in preveri mreže v `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Možnosti {#options}

| Ukaz | Možnost | Pomen |
|---|---|---|
| `identify` | `<file>` | katera koli datoteka |
| `list` | `<archive>` | `.pak`, `.utoc` (ali `.ucas` ob njej), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | samo poti, ki vsebujejo TEXT |
| | `--limit N` | največ N vrstic |
| | `--key HEX` | ključ AES-256 (64 šestnajstiških številk), ki ga že imate; samo šifrirana `.pak` ga potrebuje |
| `extract` | `<archive> <path>` | arhiv in pot vnosa, kot jo izpiše `list` |
| | `--out FILE` | kam ga zapisati (privzeto: ime datoteke vnosa) |
| | `--key HEX` | kot pri `list` |
| `meshes` | `<file>`, `--limit N` | `SerializedFile` iz Unityja; največ N mrež |

Orodje ne vsebuje ključev in jih ne izračuna: šifriran arhiv se odpre samo s ključem, ki ga podate. Datoteka, ki je ne more prebrati, je zavrnjena v eni vrstici z izhodno kodo 1. Vsak ukaz in vsaka izhodna koda sta na [Ukazi](commands.md). Kako se bere vsaka oblika, je pod [Bralniki arhivov](archive-readers.md).
