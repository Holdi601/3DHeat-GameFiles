---
title: Source 2 `.vpk`
nav_order: 6
lang: "no"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Lister og pakker ut** Valves VPK-arkiver, versjon 1 og 2, inkludert delte arkiver og
data lagret inne i katalogfilen. Hver oppføring kan sjekkes mot sin egen CRC. Dette er
det ene beholderformatet her som leverandøren selv dokumenterer. Spill: Counter-Strike 2,
Dota 2, Half-Life: Alyx, og andre på Source 2.

Kilde: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Kommandoer: `identify`, `list`, `extract`.

## Oppsett {#layout}

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

- Tre nøstede løkker, hver avsluttet med en tom streng, så en leser som forventer et antall
  finner ingen. Stier lagres én gang per gruppe og settes sammen igjen fra alle tre delene. Et
  enkelt mellomrom betyr "ingen mappe" eller "ingen filendelse".
- Hver post avsluttes med `0xFFFF`. Det sjekkes, så en leser som har mistet plassen sin stopper
  straks ("the directory is not being read at the right offset").
- **Delte arkiver:** `pak01_dir.vpk` holder katalogen, og dataene ligger i `pak01_000.vpk`,
  `pak01_001.vpk` ... valgt etter oppføringens arkivindeks.
- **Arkivindeks `0x7FFF`** betyr at bytene ligger i selve katalogfilen, etter treet. Leser man
  det som en ekte indeks, ledes en leser etter `pak01_32767.vpk`.
- **Forhåndslasting:** små filer lagres hele i katalogen. En lengde på 0 er da ingen feil.

## Kommandoer {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` skriver ut versjonen, antall oppføringer og den første `.nav`-filen. `list` viser
hver oppføring som `stored`, fordi VPK ikke komprimerer. `extract` skriver bytene uten å sjekke
CRC-en. I Python sammenligner `VpkArchive(path).verify(name)` en oppførings bytes med CRC-en
katalogen registrerte.

## Navigasjonsnettet {#the-navigation-mesh}

Et kart leveres med sitt **navigasjonsnett** (`maps/<map>.nav`) ved siden av den kompilerte
geometrien. For et varmekart over spillerposisjoner er det det nyttigste av de to med stor
margin, fordi navigasjonsnettet *er* den begåelige flaten, allerede beregnet, og en tusendel av
størrelsen. Installert-spill-testen sjekker at et leveret kart sin `.nav` starter med Source-
navigasjonsmagien `CE FA ED FE`.

## Verifisert {#verified}

Hver oppføring stikkprøvet på tvers av et spills leverte kartarkiver kom tilbake byte for byte
riktig mot sin CRC, og hvert kartarkiv parser.
Testene mot installerte spill gjentar CRC-sjekken på 25 tilfeldige oppføringer fra hvert av
opptil fire kartarkiver.

## Ikke implementert {#not-implemented}

- Dekoding av Source 2s kompilerte ressurser (`.vmdl_c`, `.vtex_c`). De er chunkede binærfiler
  med sitt eget format, samme type jobb som Unreal- og Frostbite-modellformatene. Det separate
  3DHeat CS2-verktøyet håndterer CS2-kartgeometri.
- Dekoding av CS2-navigasjonsnettet. Formatet er versjon 36 og avviker fra det mye dokumenterte
  Source 1-formatet. Bytene er strukturerte snarere enn komprimerte (entropi 6,2, 31 % nuller),
  men bare 3 % av ordene leses som koordinater, så oppsettet er ikke det åpenbare og er ikke
  utredet ennå.
