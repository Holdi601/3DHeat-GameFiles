---
title: "Prehliadanie archívov: `identify`, `list`, `extract`, `meshes`"
nav_order: 3
lang: "sk"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Prehliadanie archívov: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Hry balia svoje súbory do veľkých škatúľ, ktoré sa volajú **archívy**. Tieto príkazy pozrú na štítok škatule, vypíšu, čo je vo vnútri, a jednu vec z nej vyberú.

Pred exportom niečoho z neznámej hry si pozrite, čo obsahuje. Tieto štyri príkazy čítajú súbor a povedia vám, čo to je a čo obsahuje; nič nezapisujú, okrem jednej položky, o ktorú požiadate príkazom `extract`.

![identify, list a extract spustené nad malým zip súborom](../assets/img/inspect-archives.svg)

*Beh nad syntetickým zip súborom usporiadaným ako úroveň BeamNG.drive.*

## Postup krok za krokom {#step-by-step}

1. **Opýtajte sa, čo je súbor.** `identify` číta bajty, nie príponu:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Vypíše formát (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle alebo `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` alebo `.modelbin`, BeamNG `.cdae`/`.ter`, zip), jeho verziu, koľko položiek obsahuje a či je zašifrovaný.

2. **Vypíšte, čo je vnútri.** `list` vypíše jeden riadok na položku: veľkosť, kompresiu, cestu. Zúžte ho pomocou `--filter`, obmedzte pomocou `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Vyberte jednu položku.** `extract` zapíše jednu položku (do priečinka, v ktorom ste, pokiaľ `--out` neurčí inak) podľa cesty, ktorú vypísal `list` (alebo `#12`, podľa čísla, v `.minizip` bez mien):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` vypíše a skontroluje siete v `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Možnosti {#options}

| Príkaz | Možnosť | Význam |
|---|---|---|
| `identify` | `<file>` | ľubovoľný súbor |
| `list` | `<archive>` | `.pak`, `.utoc` (alebo `.ucas` vedľa neho), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | len cesty obsahujúce TEXT |
| | `--limit N` | najviac N riadkov |
| | `--key HEX` | kľúč AES-256 (64 hexadecimálnych číslic), ktorý už máte; len zašifrovaný `.pak` ho potrebuje |
| `extract` | `<archive> <path>` | archív a cesta položky tak, ako ju vypíše `list` |
| | `--out FILE` | kam ju zapísať (predvolene meno položky) |
| | `--key HEX` | ako pri `list` |
| `meshes` | `<file>`, `--limit N` | Unity `SerializedFile`; najviac N sietí |

Nástroj žiadne kľúče nepridáva ani neobnovuje: zašifrovaný archív sa otvorí len s kľúčom, ktorý mu dáte. Súbor, ktorý nevie prečítať, odmietne jedným riadkom s návratovým kódom 1. Každý príkaz a návratový kód je na [Príkazy](commands.md); ako sa číta každý formát, je v [Čítačky archívov](archive-readers.md).
