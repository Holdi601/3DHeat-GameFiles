---
title: ForzaTech
nav_order: 7
lang: "cs"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, vzorníky, umístění {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon běží na ForzaTech, vlastním enginu společnosti Turn 10. Tyto čtečky
vezmou trať z jejích archivů až k umístěným, texturovaným trojúhelníkům. Volají se
přes `course`, `courses` a `terrain` (viz [Forza Horizon](course-forza-horizon.md)).
`identify` rozpozná `.minizip` a samotný `.modelbin`, a `list` a `extract` berou
`.minizip` podle názvů v `ChunkContentsMiniZip<n>.txt` vedle něj, nebo podle čísla
položky (`#12`).

| Formát | Modul |
|---|---|
| archivy `.minizip` a jejich seznamy názvů | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modely a terén `.modelbin` | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| vzorníky textur `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| soubory umístění `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` a hashe textur materiálů | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| dlaždice terénu podle místa | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza také drží velkou část obsahu v obyčejných ZIP archivech pod `media\`.
Pythonový `zipfile` je otevře a `forzatech.models_in_archive()` vypíše jejich
položky `.modelbin`. Geometrie tratí je v archivech `.minizip`.

## `.minizip`: archiv bez názvů {#minizip-an-archive-with-no-names}

Trať dodává čtyři archivy `GeoChunk<n>.minizip`, u otevřeného světa má každý desítky
gigabajtů, se stovkami tisíc položek. **Archivy neukládají žádné názvy**: žádnou
tabulku názvů ani hlavičku u položek, jen pořadové číslo. Názvy jsou v
`ChunkContentsMiniZip<n>.txt` vedle každého archivu, jeden řádek na položku v pořadí
položek (`<build path>zipcache\pc\<path>|<bundle>`). Toto párování je jediný způsob,
jak soubor požádat. Vše až po `zipcache\pc\` se zahodí a hledání nerozlišuje velikost
písmen.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tři detaily v indexu dávají výstup i tehdy, když se čtou špatně. Čtečka všechny tři
zvládá správně:

| Detail | Co udělá neopatrná čtečka | Jak to vypadá |
|---|---|---|
| základ segmentu je **64bitový** | přečte ho jako u32 plus výplň | správné prvních 4 GB, potom šum správné délky |
| základ je **zarovnaný na 8 bajtů** | ignoruje výplňové slovo za tabulkou bundlů | v archivech se sudým počtem bundlů každá položka hlásí kodek, který neexistuje |
| uložená délka položky je mezera k další položce (nebo k základu dalšího segmentu) **mínus její výplň** (bity příznaků 12-13) | použije celou mezeru | LZ4 odmítne blok úplně |

Kodeky jsou pět nejnižších bitů příznaků: `0x00` uloženo, `0x08` syrový deflate,
`0x1F` blok LZ4. Každý jiný se odmítne. Každá položka se musí rozbalit přesně na
velikost, kterou deklaruje, jinak se odmítne. Index (zhruba 5 MB) se načte jednou a
data se čtou hledáním pozice.

Hlavička se kontroluje: magie, hlavička 32 bajtů a počet segmentů, který odpovídá
`ceil(entries / per segment)`.

**Ověřeno:** položky vzorkované napříč každým archivem jedné mapy, každá se rozbalí
přesně na deklarovanou délku pod všemi třemi kodeky.

## `.modelbin`: kontejner chunků {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Deklarovaná velikost souboru se musí rovnat skutečné velikosti.
- **Řetěz:** každý chunk začíná tam, kde skončil předchozí, zaokrouhleno nahoru na 4
  bajty. Nic v souboru to neříká, takže je to důkaz: záznam přečtený špatným krokem
  tento řetěz nevytvoří. Držel u všech 252 vzorkovaných modelů.
- Soubor `PGZP` předaný čtečce modelů se označí jako "a ForzaTech .minizip archive,
  not a model" a nasměruje na `minizip.py`, místo aby se bez vysvětlení odmítl.

Geometrii nesou tyto chunky:

| Chunk | Obsahuje |
|---|---|
| `VLay` | rozložení vrcholů: názvy atributů, potom prvky (u16 index názvu, u16 kanál, buffer, formát DXGI, posun); počet prvků je u16 |
| `VerB` | buffer vrcholů za 16bajtovou hlavičkou (počet, velikost, u16 krok, u16 atributy, formát) |
| `IndB` | buffer indexů, stejná hlavička |
| `Mesh` | jedna podsíť: materiál, maska úrovně detailu, rozsah indexů, rozložení, buffer, krok, tabulka variant a pozice boxu na konci |
| `MatI` | instance materiálu: její cesta `.materialbin` a hashe textur |

### Pozice a box {#positions-and-the-box}

Pozice jsou `R16G16B16A16_SNORM` (formát 13): čtyři znaménkové shorty na vrchol.
`position = short / 32767 * scale + bias`, kde měřítko a posun jsou posledních 32
bajtů chunku `Mesh` (dva float4). Posun je v **světových souřadnicích hry**, takže
dlaždice terénu přistane tam, kam ji hra dává, bez jakékoli transformace instance.
Proto stačí kolo telemetrie, aby si řeklo o kus mapy.
Každá podsíť modelu nese stejný box (zkontrolováno u 860 z nich).

### Rozložení vrcholů {#the-vertex-layout}

Jeden buffer pozic pokrývá každý vrchol. Ostatní atributy jsou rozdělené do
po sobě jdoucích skupin vrcholů, každá s vlastním bufferem a vlastním rozložením:
silnice u křižovatky nese tři sady UV a dvě tangenty, vedlejší břeh jen normálu.
Každý atribut mimo pozice má čtyři bajty. Který rozložení popisuje který buffer, se
bere z podsítí, které z něj kreslí, protože rozložení a buffery nejsou ve stejném
pořadí (stejné, posunuté o jedno, nebo přeházené, podle modelu).

| Formát DXGI | Kód | Použití |
|---|---|---|
| R16G16B16A16_SNORM | 13 | pozice (čtvrtý short je x normály) |
| R16G16_SNORM | 37 | normála y, z |
| R16G16_UNORM | 35 | pár UV (kanál = která sada) |
| R8G8B8A8_UNORM | 28 | barva nebo váhy míchání |
| R10G10B10A2_UNORM | 24 | tangenta (nedekódováno) |
| R16_UINT | 57 | indexy |

**Normála je rozdělená.** `NORMAL` nese y a z. X je čtvrtý short pozice, který
vypadal jako výplň. Přes stovky tisíc vrcholů terénu koreluje s +0,92 s x normály
trojúhelníku a s ničím jiným. S ním je 96 % vrcholů svažitého terénu do 18° od
vypočtené normály. Každé kódování dvou složek zkoušené bez ní (oktaedrické ve všech
48 uspořádáních mezi nimi) dostalo y a z správně a x špatně.

Jiné formáty pozic nebo indexů se **odmítnou** ("only 13 (four shorts, scaled) is
implemented"; "only unsigned shorts are implemented").

### Podsítě {#submeshes}

Záznam `Mesh` má ve standardním tvaru 238 bajtů. Delší nesou na začátku delší
tabulku **variant** materiálů, 238 + 8 x počet - 4 bajty, a každé pole za ní se
posune zpět přesně o tuto hodnotu. Kratší (218 bajtů, některý terén) si drží
posuny. Každá položka varianty je
`u16 0xFFFF, u16 letní materiál, u16 0xFFFF, u16 zimní materiál`. Maska úrovně
detailu je u16, jeden bit na úroveň od bitu 1.

Nic se nevěří samo o sobě. Rozsahy indexů musí přesně pokrýt buffer indexů, každý
počet `index count` se musí rovnat 3 x `triangles` a krok, který podsíť jmenuje,
musí být krok jejího bufferu. Tabulka, která neprojde, se odmítne celá, protože
označovat trojúhelníky z chybně přečtených polí je horší než je neoznačit. Napříč
tisíci vzorkovanými podsítěmi projde každá, jejíž index bufferu je v rozsahu.

### Materiály a hashe textur {#materials-and-texture-hashes}

`MatI` pojmenovává svůj materiál cestou `Game:...\x.materialbin`, nalezenou
hledáním v chunku. Jeho textury jsou záznamy `u32 slot, u32, u32 hash`, 33 bajtů od
sebe a nezarovnané, takže se chunk prohledává na každém bajtovém posunu kvůli
slovům, která jsou známými hashi textur. Ty pocházejí z `AssetManifest.xml` trati
(`<Texture Source="...\name.swatch" SourceHash="...">`, čteno až do
`</Textures>`). Slot `0x88B483AA` je základní barva standardního shaderu. Jak se pak
vybere barevná textura, je na [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: vzorníky textur {#pb-texture-swatches}

Vzorník je stejný kontejner `burG` jako model: hlavička `HCXT` o 96 bajtech od
bajtu 44, potom jeden chunk pixelů. Hlavička nese GUID textury (to v jejím názvu
souboru), šířku a výšku, počet mipů a **kód formátu na bajtu 72** (vlastní číslování
ForzaTech). Bajt 84 nese počet bajtů pixelů.

| Kód | Formát | Určeno jako |
|---|---|---|
| 0 | BC1, půl bajtu na pixel | dekóduje na červenobílou obrubu (pod BC4 šum) |
| 9 | BC7, jeden bajt na pixel | dekóduje na dlaždici terénu, na které je vidět okruh |
| 13 | RGBA8, čtyři bajty na pixel | prostý |
| jiný | odmítnuto | "texture format N has not been identified; refusing to guess" |

Formáty se určily dekódováním skutečných souborů každým způsobem, který velikost
dat dovolí. Bajt 47, který dřívější verze bral za formát, je u každé vzorkované
textury 4. Dekóduje se jen nejvyšší mip souboru. Každé rozlišení je vlastní položka,
`<name>_<guid>_quality<n>.pb`, kvalita 1 nejmenší až 5 největší. U mapy terénu jsou
dvě největší v jiném archivu než zbytek. Dekódování jde přes BCn dekodér Pillow,
přes vygenerovanou hlavičku DDS.

## Soubory umístění (.pgeo) {#placement-files-pgeo}

Jeden soubor na kategorii a prostorovou buňku:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Samotná cesta
udává čtverec buňky a kategorii, takže soubory se dají filtrovat, aniž by se
otevřely.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Jak se určilo každé pole:

| Pole | Určeno podle |
|---|---|
| pozice je pevná řádová čárka 16.16, ne zlomek boxu | za sebou jdoucí svodidla jsou přesně 4,000 m od sebe (délka modelu) |
| znaménko a velikost, ne dvojkový doplněk | dvojkový doplněk dal záporné souřadnice desítky kilometrů mimo mapu; s bitem 31 jako znaménkem každý záznam každé kategorie vzorkované leží uvnitř boxu svého souboru |
| vektory jsou vlastní osy modelu | konec každého svodidla leží na začátku dalšího: 93,5 % do 5 cm, medián 0,000 m |
| bajt 60 je varianta | pět kopií billboardu čte 0, 2, 2, 3, 4, zatímco každé svodidlo čte 0 |

Jen názvy končící `_3D` jsou záznamy modelů. Tabulka variant před nimi jmenuje
názvy bez přípony, a čtené jako záznamy by skončily v nekonečnu. Kandidátní záznam
se přijme jen tehdy, když se jeho počet vejde do souboru, a instance s nekonečnými
čísly se zahodí.

## Neimplementováno {#not-implemented}

- Formáty vrcholů a indexů jiné než uvedené výše (odmítnuto).
- Formáty textur jiné než 0, 9, 13 (odmítnuto).
- Tangenty (přeskočeny, nepoužívají se).
- Vrstvy materiálů shaderu terénu. Barevná textura terénu je interpretace map
  dlaždic (viz [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
