---
title: "Source 2 VPK"
nav_order: 6
lang: "da"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Viser og udpakker** Valves VPK-arkiver, version 1 og 2, inklusive delte
arkiver og data, der ligger inde i katalogfilen. Hver post kan kontrolleres
mod sin egen CRC. Dette er det ene containerformat her, hvis leverandør dokumenterer
det. Spil: Counter-Strike 2, Dota 2, Half-Life: Alyx og andre på Source 2.

Kilde: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Kommandoer: `identify`, `list`, `extract`.

## Opbygning {#layout}

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

- Tre indlejrede løkker, som hver slutter på en tom streng, så en læser, der forventer et antal,
  finder ingen. Stier gemmes én gang pr. gruppe og sættes sammen af alle tre
  dele. Et enkelt mellemrum betyder "ingen mappe" eller "ingen endelse".
- Hver post slutter med `0xFFFF`. Det kontrolleres, så en læser, der har mistet
  sin plads, stopper med det samme ("the directory is not being read at the right offset").
- **Delte arkiver:** `pak01_dir.vpk` indeholder kataloget, og dataene ligger i
  `pak01_000.vpk`, `pak01_001.vpk`... valgt efter postens arkivindeks.
- **Arkivindeks `0x7FFF`** betyder, at bytene ligger i selve katalogfilen,
  efter træet. Læses det som et rigtigt indeks, sender det en læser på jagt efter
  `pak01_32767.vpk`.
- **Preload:** små filer gemmes hele i kataloget. En længde på 0 er så ikke en fejl.

## Kommandoer {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` skriver versionen, antallet af poster og den første `.nav`-fil. `list`
viser hver post som `stored`, fordi VPK ikke komprimerer. `extract` skriver bytene
uden at kontrollere CRC'en. I Python sammenligner `VpkArchive(path).verify(name)`
en posts bytes med den CRC, kataloget har registreret.

## Navigationsmeshet {#the-navigation-mesh}

Et kort leverer sit **navigationsmesh** (`maps/<map>.nav`) ved siden af den kompilerede
geometri. Til et varmekort over spillerpositioner er det det nyttigste af de to med god
margin, for navmeshet *er* det begængelige gulv, allerede beregnet og en tusindedel
af størrelsen. Den installerede-spil-test kontrollerer, at et udleveret korts
`.nav` starter med Source-navigationsmagien `CE FA ED FE`.

## Verificeret {#verified}

Hver post, der blev stikprøvet på tværs af et spils udleverede kortarkiver, kom tilbage
byte for byte korrekt mod sin CRC, og hvert kortarkiv kan læses.
Testene med installeret spil gentager CRC-kontrollen på 25 tilfældige poster fra hvert af
op til fire kortarkiver.

## Ikke implementeret {#not-implemented}

- Dekodning af Source 2's kompilerede aktiver (`.vmdl_c`, `.vtex_c`). De er chunkede
  binærfiler med deres eget format, det samme slags opgave som Unreal- og Frostbite-meshformaterne. Det
  separate 3DHeat CS2-værktøj håndterer CS2-kortgeometri.
- Dekodning af CS2-navmeshet. Dets format er version 36 og adskiller sig fra det
  bredt dokumenterede Source 1-format. Dets bytes er struktureret og ikke komprimeret
  (entropi 6,2, 31 % nuller), men kun 3 % af dets ord læses som koordinater, så
  opbygningen er ikke den oplagte og er endnu ikke fundet ud af.
