---
title: "Source 2 `.vpk`"
nav_order: 6
lang: "cs"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Vypisuje a rozbaluje** archivy VPK od Valve, verze 1 a 2, včetně rozdělených archivů a dat uložených uvnitř souboru adresáře. Každou položku lze ověřit proti jejímu vlastnímu CRC. Je to jediný kontejnerový formát zde, jehož výrobce ho dokumentuje. Hry: Counter-Strike 2, Dota 2, Half-Life: Alyx a další na Source 2.

Zdroj: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Příkazy: `identify`, `list`, `extract`.

## Rozložení {#layout}

```
u32 magic 0x55AA1234, u32 version (1 or 2), u32 tree size
  (version 2: 16 more header bytes; header 12 or 28 bytes)
directory tree:
  extension        "vmdl_c", then "vtex_c", ..., then ""
    path           "maps/example_map", then ""
      file name    "world_layer0", then ""
        u32 crc, u16 preload size, u16 archive index, u32 offset, u32 length, u16 0xFFFF
        [preload bytes]
```

- Tři vnořené smyčky, každá končí prázdným řetězcem, takže čtečka, která čeká počet, žádný nenajde. Cesty se ukládají jednou pro každou skupinu a skládají se ze všech tří částí. Jediná mezera znamená „žádná složka“ nebo „žádná přípona“.
- Každý záznam končí `0xFFFF`. To se kontroluje, takže čtečka, která ztratila místo, se hned zastaví („the directory is not being read at the right offset“).
- **Rozdělené archivy:** `pak01_dir.vpk` drží adresář a data jsou v `pak01_000.vpk`, `pak01_001.vpk`… vybraných podle indexu archivu položky.
- **Index archivu `0x7FFF`** znamená, že bajty jsou v samotném souboru adresáře, za stromem. Čtečka, která by ho četla jako skutečný index, by hledala `pak01_32767.vpk`.
- **Preload:** malé soubory se ukládají celé přímo v adresáři. Délka 0 pak není chyba.

## Příkazy {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` vypíše verzi, počet položek a první soubor `.nav`. `list` ukáže každou položku jako `stored`, protože VPK nekomprimuje. `extract` zapíše bajty bez kontroly CRC. V Pythonu `VpkArchive(path).verify(name)` porovná bajty položky s CRC, které si zapsal adresář.

## Navigační síť {#the-navigation-mesh}

Mapa dodává svou **navigační síť** (`maps/<map>.nav`) vedle zkompilované geometrie. Pro tepelnou mapu pozic hráčů je o hodně užitečnější ze dvou, protože navigační síť *je* průchozí podlaha, už spočítaná a tisíckrát menší. Test na nainstalované hře kontroluje, že `.nav` dodané mapy začíná magickými bajty navigace Source `CE FA ED FE`.

## Ověřeno {#verified}

Každá položka vzorkovaná napříč dodanými mapovými archivy hry se vrátila bajt po bajtu shodná se svým CRC a každý mapový archiv se načetl.
Testy na nainstalované hře opakují kontrolu CRC na 25 náhodných položkách z každého z až čtyř mapových archivů.

## Neimplementováno {#not-implemented}

- Dekódování zkompilovaných assetů Source 2 (`.vmdl_c`, `.vtex_c`). Jsou to blokově členěná binární data vlastního druhu, stejná práce jako u formátů meshů Unreal a Frostbite. Samostatný nástroj 3DHeat pro CS2 zpracovává geometrii map CS2.
- Dekódování navigační sítě CS2. Její formát je verze 36 a liší se od široce dokumentovaného formátu Source 1. Její bajty jsou strukturované, ne komprimované (entropie 6,2, 31 % nul), ale jen 3 % jejích slov se čte jako souřadnice. Rozložení tedy není zřejmé a zatím nebylo vyřešeno.
