---
title: "Prohlížení archivů: `identify`, `list`, `extract`, `meshes`"
nav_order: 3
lang: "cs"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Prohlížení archivů: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Hra balí své soubory do velkých krabic zvaných **archivy**. Tyto příkazy si prohlédnou štítek krabice, vypíšou, co je uvnitř, a jednu věc z ní vyberou.

Než něco exportujete z neznámé hry, podívejte se, co obsahuje. Tyto čtyři příkazy čtou soubor a říkají vám, co je zač a co drží. Nic nezapisují, kromě jediné položky, kterou si u `extract` vyžádáte.

![příkazy identify, list a extract spuštěné na malém zipu](../assets/img/inspect-archives.svg)

*Běh na syntetickém zipu uspořádaném jako úroveň BeamNG.drive.*

## Postup krok za krokem {#step-by-step}

1. **Zeptejte se, co je to za soubor.** `identify` čte bajty, ne příponu:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Pojmenuje formát (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle nebo `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` nebo `.modelbin`, BeamNG `.cdae`/`.ter`, zip), jeho verzi, počet položek a to, jestli je zašifrovaný.

2. **Vypište, co je uvnitř.** `list` vypíše jeden řádek na položku: velikost, kompresi a cestu. Zúžíte ji pomocí `--filter`, omezíte pomocí `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Vyberte jednu položku.** `extract` zapíše jednu položku (do složky, ve které jste, pokud `--out` neříká jinak), a to podle cesty, kterou vypsal `list` (nebo `#12`, podle čísla, u `.minizip` bez názvů):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` vypíše a zkontroluje meshe v `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Možnosti {#options}

| Příkaz | Možnost | Význam |
|---|---|---|
| `identify` | `<file>` | libovolný soubor |
| `list` | `<archive>` | `.pak`, `.utoc` (nebo `.ucas` vedle něj), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | jen cesty obsahující TEXT |
| | `--limit N` | nejvýše N řádků |
| | `--key HEX` | klíč AES-256 (64 hexadecimálních číslic), který už máte; potřebuje ho jen zašifrovaný `.pak` |
| `extract` | `<archive> <path>` | archiv a cesta položky tak, jak ji vypíše `list` |
| | `--out FILE` | kam ji zapsat (výchozí: název souboru položky) |
| | `--key HEX` | jako u `list` |
| `meshes` | `<file>`, `--limit N` | Unity `SerializedFile`; nejvýše N meshů |

Nástroj žádné klíče nedodává a žádné neobnovuje: zašifrovaný archiv se otevře jen s klíčem, který předáte. Soubor, který nedokáže přečíst, odmítne jedním řádkem s návratovým kódem 1. Každý příkaz a každý návratový kód je na stránce [Příkazy](commands.md). Jak se každý formát čte, je popsáno v [Čtečkách archivů](archive-readers.md).
