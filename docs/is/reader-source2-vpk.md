---
title: "Source 2 VPK"
nav_order: 6
lang: "is"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Telur upp og tekur út** VPK-skjalasöfn Valve, útgáfur 1 og 2, þar með talin skipt
skjalasöfn og gögn geymd inni í möppuskránni. Hægt er að athuga hverja færslu
gegn eigin CRC. Þetta er eina gámasniðið hér sem framleiðandinn skjalfestir.
Leikir: Counter-Strike 2, Dota 2, Half-Life: Alyx og aðrir á Source 2.

Frumkóði: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Skipanir: `identify`, `list`, `extract`.

## Uppbygging {#layout}

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

- Þrjár hreiðraðar lykkjur, hver endar á tómum streng, svo lesari sem býst við
  fjölda finnur engan. Slóðir eru geymdar einu sinni í hverjum hópi og settar saman úr öllum
  þremur hlutunum. Eitt bil þýðir „engin mappa“ eða „engin endinga“.
- Sérhver færsla endar á `0xFFFF`. Það er athugað, svo lesari sem hefur misst
  staðinn stoppar strax („the directory is not being read at the right offset“).
- **Skipt skjalasöfn:** `pak01_dir.vpk` geymir möppuna og gögnin eru í
  `pak01_000.vpk`, `pak01_001.vpk`... valin eftir skjalasafnsvísi færslunnar.
- **Skjalasafnsvísir `0x7FFF`** þýðir að bætin eru í möppuskránni sjálfri,
  á eftir trénu. Ef hann er lesinn sem raunverulegur vísir fer lesari að leita að
  `pak01_32767.vpk`.
- **Forhleðsla (preload):** litlar skrár eru geymdar heilar í möppunni. Lengdin 0 er
  þá ekki villa.

## Skipanir {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` prentar útgáfuna, fjölda færslna og fyrstu `.nav` skrána. `list`
sýnir hverja færslu sem `stored`, því VPK þjappar ekki. `extract` skrifar
bætin án þess að athuga CRC. Í Python ber `VpkArchive(path).verify(name)`
bæti færslu saman við CRC sem mappan skráði.

## Leiðsögunetið (navigation mesh) {#the-navigation-mesh}

Kort sendir með **leiðsögunet** (`maps/<map>.nav`) við hlið samsettrar
rúmfræði. Fyrir hitakort af staðsetningum leikmanna er það miklu gagnlegra af
þessu tvennu, því leiðsögunetið *er* gönguflöturinn, þegar reiknaður og
þúsundasti hluti af stærðinni. Prófunin á uppsettum leik athugar að `.nav` útgefins korts
byrji á Source-leiðsögugaldrinum `CE FA ED FE`.

## Staðfest {#verified}

Sérhver færsla sem sýni var tekið af úr kortaskjalasöfnum leiks kom bæti fyrir bæti rétt
gegn CRC, og sérhvert kortaskjalasafn les rétt.
Prófanirnar á uppsettum leik endurtaka CRC-athugunina á 25 handahófskenndum færslum úr hverju
af allt að fjórum kortaskjalasöfnum.

## Ekki útfært {#not-implemented}

- Afkóðun á þýddum gögnum Source 2 (`.vmdl_c`, `.vtex_c`). Þau eru bútuð
  tvíundarsnið út af fyrir sig, sams konar verk og Unreal- og Frostbite-netsniðin.
  Aðskilda 3DHeat CS2 verkfærið sér um rúmfræði CS2-korta.
- Afkóðun á CS2-leiðsögunetinu. Snið þess er útgáfa 36 og er ólíkt hinu víða
  skjalfesta Source 1 sniði. Bæti þess eru byggð upp frekar en þjöppuð
  (entropy 6.2, 31% núll), en aðeins 3% orða þess lesast sem hnit, svo
  uppbyggingin er ekki sú augljósa og hefur ekki verið greind enn.
