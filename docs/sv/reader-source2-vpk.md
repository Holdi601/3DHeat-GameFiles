---
title: Source 2 VPK
nav_order: 6
lang: "sv"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Listar och packar ut** Valves VPK-arkiv, version 1 och 2, inklusive delade arkiv och data som ligger inuti katalogfilen. Varje post kan kontrolleras mot sin egen CRC. Detta är det enda containerformatet här vars leverantör dokumenterar det. Spel: Counter-Strike 2, Dota 2, Half-Life: Alyx och andra på Source 2.

Källa: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Kommandon: `identify`, `list`, `extract`.

## Layout {#layout}

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

- Tre inbäddade loopar, var och en slutar med en tom sträng, så en läsare som väntar sig en räkning hittar ingen. Sökvägar lagras en gång per grupp och sätts ihop igen av alla tre delarna. Ett enda mellanslag betyder ”ingen mapp” eller ”ingen filändelse”.
- Varje post slutar med `0xFFFF`. Det kontrolleras, så en läsare som har tappat bort var den är stannar direkt (”the directory is not being read at the right offset”).
- **Delade arkiv:** `pak01_dir.vpk` innehåller katalogen, och datan ligger i `pak01_000.vpk`, `pak01_001.vpk`... och väljs med postens arkivindex.
- **Arkivindex `0x7FFF`** betyder att byten finns i själva katalogfilen, efter trädet. Läses det som ett riktigt index skickas läsaren och letar efter `pak01_32767.vpk`.
- **Förladdning:** små filer lagras hela i katalogen. En längd på 0 är då inte ett fel.

## Kommandon {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` skriver ut versionen, antalet poster och den första `.nav`-filen. `list` visar varje post som `stored`, eftersom VPK inte komprimerar. `extract` skriver byten utan att kontrollera CRC. I Python jämför `VpkArchive(path).verify(name)` en posts byte med den CRC som katalogen registrerade.

## Navigeringsnätet {#the-navigation-mesh}

En karta levereras med sitt **navigeringsnät** (`maps/<map>.nav`) bredvid den kompilerade geometrin. För en värmekarta över spelarpositioner är det den mest användbara av de två, med stor marginal, eftersom navigeringsnätet *är* det gångbara golvet, redan beräknat och en tusendel av storleken. Testet med installerat spel kontrollerar att en levererad kartas `.nav` börjar med Source-navigeringens magiska bytes `CE FA ED FE`.

## Verifierat {#verified}

Varje post som stickprovskontrollerades i ett spels levererade kartarkiv gav tillbaka exakta byte mot sin CRC, och alla kartarkiv tolkas korrekt.
Testerna med installerat spel upprepar CRC-kontrollen på 25 slumpvalda poster från vart och ett av upp till fyra kartarkiv.

## Inte implementerat {#not-implemented}

- Avkodning av Source 2:s kompilerade tillgångar (`.vmdl_c`, `.vtex_c`). De är egna binärer uppdelade i block, samma sorts jobb som mesh-formaten för Unreal och Frostbite. Det separata 3DHeat-verktyget för CS2 hanterar geometrin för CS2-kartor.
- Avkodning av CS2:s navigeringsnät. Dess format är version 36 och skiljer sig från det allmänt dokumenterade Source 1-formatet. Dess byte är strukturerade snarare än komprimerade (entropi 6.2, 31% nollor), men bara 3% av dess ord läses som koordinater, så layouten är inte den självklara och är ännu inte utredd.
