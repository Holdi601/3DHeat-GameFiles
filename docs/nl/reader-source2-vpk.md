---
title: Source 2 `.vpk`
nav_order: 6
lang: "nl"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Toont en pakt uit** de VPK-archieven van Valve, versie 1 en 2, inclusief gesplitste archieven en data die in het mapbestand is opgeslagen. Elk item kan worden gecontroleerd tegen zijn eigen CRC. Dit is het enige containerformaat hier waarvan de leverancier de opbouw documenteert. Spellen: Counter-Strike 2, Dota 2, Half-Life: Alyx, en andere op Source 2.

Bron: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Commando's: `identify`, `list`, `extract`.

## Opbouw {#layout}

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

- Drie geneste lussen, die elk eindigen op een lege tekenreeks, zodat een lezer die een aantal verwacht er geen vindt. Paden worden één keer per groep opgeslagen en uit alle drie delen samengesteld. Een enkele spatie betekent "geen map" of "geen extensie".
- Elk record eindigt op `0xFFFF`. Dat wordt gecontroleerd, zodat een lezer die zijn plaats kwijt is meteen stopt ("the directory is not being read at the right offset").
- **Gesplitste archieven:** `pak01_dir.vpk` bevat de map, en de data staat in `pak01_000.vpk`, `pak01_001.vpk`... Welk bestand het is, wordt bepaald door de archiefindex van het item.
- **Archiefindex `0x7FFF`** betekent dat de bytes in het mapbestand zelf staan, na de boom. Een lezer die dat als echte index leest, zoekt naar `pak01_32767.vpk`.
- **Preload:** kleine bestanden worden helemaal in de map opgeslagen. Een lengte van 0 is dan geen fout.

## Commando's {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` drukt de versie, het aantal items en het eerste `.nav`-bestand af. `list` toont elk item als `stored`, omdat VPK niet comprimeert. `extract` schrijft de bytes zonder de CRC te controleren. In Python vergelijkt `VpkArchive(path).verify(name)` de bytes van een item met de CRC die de map had vastgelegd.

## Het navigatienetwerk {#the-navigation-mesh}

Een kaart levert zijn **navigatienetwerk** (`maps/<map>.nav`) mee naast de gecompileerde geometrie. Voor een heatmap van spelerposities is dat met een flink verschil het nuttigste van de twee. Het navigatienetwerk *is* de begaanbare vloer, al berekend, en een duizendste zo groot. De test op een geïnstalleerd spel controleert dat de `.nav` van een uitgeleverde kaart begint met de Source-navigatiemagic `CE FA ED FE`.

## Gecontroleerd {#verified}

Elk item dat is bemonsterd uit de kaartarchieven van een spel, kwam byte voor byte overeen met zijn CRC, en elk kaartarchief wordt correct gelezen. De tests op geïnstalleerde spellen herhalen de CRC-controle op 25 willekeurige items uit elk van maximaal vier kaartarchieven.

## Niet geïmplementeerd {#not-implemented}

- Het decoderen van de gecompileerde assets van Source 2 (`.vmdl_c`, `.vtex_c`). Dat zijn gechunkte binaries met een eigen formaat, hetzelfde soort werk als de Unreal- en Frostbite-meshformaten. De aparte 3DHeat CS2-tool verwerkt de CS2-kaartgeometrie.
- Het decoderen van het CS2-navigatienetwerk. Het formaat is versie 36 en wijkt af van het wijd gedocumenteerde Source 1-formaat. De bytes zijn gestructureerd en niet gecomprimeerd (entropy 6.2, 31% nullen), maar slechts 3% van de woorden leest als coördinaten. De opbouw is dus niet de voor de hand liggende, en is nog niet uitgewerkt.
