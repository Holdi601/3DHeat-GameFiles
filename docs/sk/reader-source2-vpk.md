---
title: "Source 2 `.vpk`"
nav_order: 6
lang: "sk"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Vypisuje a rozbaľuje** archívy VPK od Valve, verzie 1 a 2, vrátane rozdelených archívov a dát uložených vo vnútri súboru adresára. Každú položku možno overiť jej vlastným CRC. Toto je jediný kontajnerový formát tu, ktorého dodávateľ ho dokumentuje. Hry: Counter-Strike 2, Dota 2, Half-Life: Alyx a ďalšie na Source 2.

Zdroj: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Príkazy: `identify`, `list`, `extract`.

## Rozloženie {#layout}

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

- Tri vnorené slučky, každá končí prázdnym reťazcom, takže čítačka, ktorá očakáva počet, žiadny nenájde. Cesty sa ukladajú raz pre skupinu a skladajú sa zo všetkých troch častí. Jediná medzera znamená „žiadny priečinok“ alebo „žiadna prípona“.
- Každý záznam končí `0xFFFF`. To sa kontroluje, takže čítačka, ktorá stratila miesto, sa okamžite zastaví („the directory is not being read at the right offset“).
- **Rozdelené archívy:** `pak01_dir.vpk` drží adresár a dáta sú v `pak01_000.vpk`, `pak01_001.vpk`... vybrané podľa indexu archívu položky.
- **Index archívu `0x7FFF`** znamená, že bajty sú v samotnom súbore adresára, za stromom. Keby ho čítačka brala ako skutočný index, hľadala by `pak01_32767.vpk`.
- **Predbežné načítanie (preload):** malé súbory sa ukladajú celé v adresári. Dĺžka 0 potom nie je chyba.

## Príkazy {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` vypíše verziu, počet položiek a prvý súbor `.nav`. `list` ukáže každú položku ako `stored`, lebo VPK nekomprimuje. `extract` zapíše bajty bez kontroly CRC. V Pythone `VpkArchive(path).verify(name)` porovná bajty položky s CRC, ktoré zaznamenal adresár.

## Navigačná sieť {#the-navigation-mesh}

Mapa ukladá svoju **navigačnú sieť** (`maps/<map>.nav`) vedľa skompilovanej geometrie. Pre heatmapu pozícií hráčov je to ďaleko užitočnejšie z oboch, lebo navigačná sieť *je* pochôdzna podlaha, už vypočítaná a tisícinová veľkosť. Test na nainštalovanej hre overuje, že `.nav` zverejnenej mapy začína magickým číslom navigačnej siete Source `CE FA ED FE`.

## Overené {#verified}

Každá položka vzorkovaná naprieč zverejnenými mapovými archívmi hry prišla bajt po bajte presná podľa svojho CRC a každý mapový archív sa dá naparsovať.
Testy na nainštalovanej hre opakujú kontrolu CRC na 25 náhodných položkách z každého mapového archívu, až štyroch.

## Nie je implementované {#not-implemented}

- Dekódovanie skompilovaných aktív Source 2 (`.vmdl_c`, `.vtex_c`). Sú to rozdelené binárne súbory s vlastnou štruktúrou, rovnaká práca ako formáty sietí Unreal a Frostbite. Samostatný nástroj 3DHeat CS2 spracúva geometriu máp CS2.
- Dekódovanie navigačnej siete CS2. Jej formát je verzia 36 a líši sa od všeobecne dokumentovaného formátu Source 1. Jej bajty sú štruktúrované, nie komprimované (entropia 6,2, 31 % núl), ale len 3 % jej slov sa čítajú ako súradnice, takže rozloženie nie je zrejmé a zatiaľ nebolo vypracované.
