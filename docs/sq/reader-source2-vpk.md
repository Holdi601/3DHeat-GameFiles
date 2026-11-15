---
title: "Source 2 VPK"
nav_order: 6
lang: "sq"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Liston dhe nxjerr** arkivat VPK të Valve, versionet 1 dhe 2, përfshirë arkivat e ndara
dhe të dhënat e ruajtura brenda skedarit të drejtorisë. Çdo hyrje mund të kontrollohet
me CRC-në e vet. Ky është formati i vetëm i kontejnerit këtu që shitësi e dokumenton.
Lojëra: Counter-Strike 2, Dota 2, Half-Life: Alyx dhe të tjera në Source 2.

Burimi: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Komandat: `identify`, `list`, `extract`.

## Struktura {#layout}

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

- Tri cikle të futur, secili që mbaron me një varg bosh, kështu që një lexues që pret
  një numër nuk gjen asnjë. Rrugët ruhen një herë për grup dhe rindërtohen nga të tria
  pjesët. Një hapësirë e vetme do të thotë "pa dosje" ose "pa shtesë".
- Çdo regjistrim mbaron me `0xFFFF`. Kjo kontrollohet, kështu që një lexues që e ka humbur
  vendin ndalon menjëherë ("the directory is not being read at the right offset").
- **Arkivat e ndara:** `pak01_dir.vpk` mban drejtorinë, dhe të dhënat gjenden në
  `pak01_000.vpk`, `pak01_001.vpk`..., të zgjedhura nga indeksi i arkivit të hyrjes.
- **Indeksi i arkivit `0x7FFF`** do të thotë që bajtet janë në vetë skedarin e drejtorisë,
  pas pemës. Nëse lexohet si indeks i vërtetë, lexuesi shkon të kërkojë
  `pak01_32767.vpk`.
- **Preload:** skedarët e vegjël ruhen të plotë në drejtori. Gjatësia 0 atëherë
  nuk është gabim.

## Komandat {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` printon versionin, numrin e hyrjeve dhe skedarin e parë `.nav`. `list`
tregon çdo hyrje si `stored`, sepse VPK nuk ngjesh. `extract` shkruan
bajtet pa kontrolluar CRC-në. Në Python, `VpkArchive(path).verify(name)`
krahason bajtet e një hyrjeje me CRC-në që regjistroi drejtoria.

## Rrjeta e navigimit {#the-navigation-mesh}

Një hartë sjell **rrjetën e navigimit** (`maps/<map>.nav`) pranë gjeometrisë
së kompiluar. Për një hartë nxehtësie të pozicioneve të lojtarëve ajo është më e dobishmja nga të dyja
me shumë, sepse rrjeta nav *është* dyshemeja ku mund të ecësh, e llogaritur tashmë
dhe një të mijtën e madhësisë. Testi i lojës së instaluar kontrollon që `.nav` i një harte të dërguar
fillon me magic-un e navigimit të Source `CE FA ED FE`.

## E verifikuar {#verified}

Çdo hyrje e marrë si mostër nga arkivat e hartave të një loje erdhi bajt për bajt e saktë
sipas CRC-së, dhe çdo arkiv harte lexohet.
Testet e lojës së instaluar e përsërisin kontrollin e CRC-së në 25 hyrje të rastësishme nga secili prej
deri në katër arkiva hartash.

## Nuk është zbatuar {#not-implemented}

- Dekodimi i aseteve të kompiluara të Source 2 (`.vmdl_c`, `.vtex_c`). Janë
  binarë me copa, të veçantë, i njëjti lloj pune si formatet e rrjetave të Unreal dhe
  Frostbite. Mjeti i veçantë 3DHeat CS2 trajton gjeometrinë e hartave të CS2.
- Dekodimi i rrjetës nav të CS2. Formati i saj është versioni 36 dhe ndryshon nga ai
  i Source 1 që është i dokumentuar gjerësisht. Bajtet e saj janë të strukturuara dhe jo të ngjeshura
  (entropia 6.2, 31% zero), por vetëm 3% e fjalëve të saj lexohen si koordinata, kështu që
  struktura nuk është ajo e dukshmja dhe ende nuk është zbuluar.
