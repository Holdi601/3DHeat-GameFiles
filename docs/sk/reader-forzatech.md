---
title: ForzaTech
nav_order: 7
lang: "sk"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, vzorníky, umiestnenia {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon beží na ForzaTech, vlastnom engine studia Turn 10. Tieto čítačky vezmú
trať z jej archívov až k umiestneným, texturovaným trojuholníkom. Dostanete sa k nim
cez `course`, `courses` a `terrain` (pozri [Forza Horizon](course-forza-horizon.md)).
`identify` rozpozná `.minizip` a holý `.modelbin`, a `list` a `extract` berú `.minizip`
podľa názvov v `ChunkContentsMiniZip<n>.txt` vedľa neho alebo podľa čísla položky
(`#12`).

| Formát | Modul |
|---|---|
| archívy `.minizip` a ich zoznamy názvov | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modely a terén `.modelbin` | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| textúrové vzorníky `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| súbory umiestnení `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` a hashe textúr materiálov | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| dlaždice terénu podľa miesta | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza uchováva veľkú časť obsahu aj v obyčajných ZIP archívoch pod `media\`.
Pythonov modul `zipfile` ich otvorí a `forzatech.models_in_archive()` vypíše ich
položky `.modelbin`. Geometria trate je v archívoch `.minizip`.

## `.minizip`: archív bez názvov {#minizip-an-archive-with-no-names}

Trať dodáva štyri `GeoChunk<n>.minizip` archívy, pri otvorenom svete mapy každý
desiatky gigabajtov, so stovkami tisíc položiek. **Archívy neukladajú žiadne názvy**:
žiadnu tabuľku názvov ani hlavičku pri každej položke, len poradové číslo. Názvy sú
v `ChunkContentsMiniZip<n>.txt` vedľa každého archívu, jeden riadok na položku v
poradí položiek (`<build path>zipcache\pc\<path>|<bundle>`). Toto párovanie je jediný
spôsob, ako si súbor vypýtať. Všetko až po `zipcache\pc\` sa zahodí a vyhľadávanie
ignoruje veľkosť písmen.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tri podrobnosti v indexe stále vyprodukujú výstup, aj keď sa čítajú zle. Čítačka
všetky tri spracuje správne:

| Podrobnosť | Čo urobí neopatrná čítačka | Ako to vyzerá |
|---|---|---|
| základňa segmentu je **64-bitová** | číta ju ako u32 plus výplň | správne pre prvé 4 GB, potom šum správnej dĺžky |
| základňa je **zarovnaná na 8 bajtov** | ignoruje výplňové slovo za tabuľkou zväzkov | v archívoch s párnym počtom zväzkov každá položka tvrdí kodek, ktorý neexistuje |
| uložená dĺžka položky je medzera k ďalšej položke (alebo k základni ďalšieho segmentu) **mínus jej výplň** (bity príznakov 12-13) | použije celú medzeru | LZ4 blok bez výhrad odmietne |

Kodeky sú nižších päť bitov príznakov: `0x00` uložené, `0x08` surový deflate,
`0x1F` blok LZ4. Iné sa odmietnu. Každá položka sa musí rozbaliť presne na veľkosť,
ktorú deklaruje, inak sa odmietne. Index (asi 5 MB) sa prečíta raz a užitočné dáta sa
čítajú hľadaním.

Hlavička sa overuje: magické číslo, 32-bajtová hlavička a počet segmentov, ktorý sa
zhoduje s `ceil(entries / per segment)`.

**Overené:** položky vzorkované naprieč každým archívom mapy, každá sa rozbalí presne
na svoju deklarovanú dĺžku pod všetkými tromi kodekmi.

## `.modelbin`: kontajner chunkov {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Deklarovaná veľkosť súboru sa musí rovnať skutočnej veľkosti.
- **Reťaz**: každý chunk začína tam, kde skončil predchádzajúci, zaokrúhlený nahor
  na 4 bajty. Nič v súbore to neuvádza, takže je to dôkaz: záznam čítaný na zlom kroku
  to nevytvorí. Platilo to pre všetkých 252 vzorkovaných modelov.
- Súbor `PGZP` dodaný čítačke modelu sa pomenuje ako „a ForzaTech .minizip archive,
  not a model“ a nasmeruje sa na `minizip.py`, namiesto aby sa odmietol bez vysvetlenia.

Geometria pochádza z týchto chunkov:

| Chunk | Obsahuje |
|---|---|
| `VLay` | rozloženie vrcholov: názvy atribútov, potom prvky (u16 index názvu, u16 kanál, buffer, formát DXGI, offset); počet prvkov je u16 |
| `VerB` | buffer vrcholov za 16-bajtovou hlavičkou (počet, veľkosť, u16 krok, u16 atribúty, formát) |
| `IndB` | buffer indexov, rovnaká hlavička |
| `Mesh` | jedna podsieť: materiál, maska úrovne detailu, rozsah indexov, rozloženie, buffer, krok, tabuľka variantov a box pozície na konci |
| `MatI` | inštancia materiálu: jej cesta `.materialbin` a hashe textúr |

### Pozície a box {#positions-and-the-box}

Pozície sú `R16G16B16A16_SNORM` (formát 13): štyri znamienkové shorty na vrchol.
`position = short / 32767 * scale + bias`, kde scale a bias sú posledných 32 bajtov
chunku `Mesh` (dva float4). Bias je v **svetových súradniciach hry**, takže dlaždica
terénu pristane tam, kam ju hra kladie, bez transformácie inštancie. Preto stačí kolo
telemetrie na vyžiadanie kúska mapy. Každá podsieť modelu nesie ten istý box
(overené na 860 z nich).

### Rozloženie vrcholov {#the-vertex-layout}

Jeden buffer pozícií pokrýva všetky vrcholy. Ostatné atribúty sú rozdelené do po sebe
idúcich skupín vrcholov, každá s vlastným bufferom a vlastným rozložením: cesta pri
križovatke nesie tri sady UV a dve tangenty, breh vedľa nej len normálu. Každý
neposlený atribút má štyri bajty. Ktoré rozloženie popisuje ktorý buffer, sa zistí
z podsietí, ktoré z neho kreslia, lebo rozloženia a buffery nie sú v rovnakom poradí
(rovnaké, posunuté o jedno alebo premiešané podľa modelu).

| Formát DXGI | Kód | Použitie |
|---|---|---|
| R16G16B16A16_SNORM | 13 | pozícia (štvrtý short je x normály) |
| R16G16_SNORM | 37 | normála y, z |
| R16G16_UNORM | 35 | pár UV (kanál = ktorá sada) |
| R8G8B8A8_UNORM | 28 | farba alebo váhy miešania |
| R10G10B10A2_UNORM | 24 | tangenta (nedekóduje sa) |
| R16_UINT | 57 | indexy |

**Normála je rozdelená.** `NORMAL` obsahuje y a z. X je štvrtý short pozície, ktorý
vyzeral ako výplň. Cez stovky tisíc vrcholov terénu koreluje +0,92 s x normály
trojuholníka a s ničím iným. S ním je 96 % vrcholov svahového terénu do 18° od
vypočítanej normály. Každé kódovanie dvoch zložiek vyskúšané bez nej (oktaedrické vo
všetkých 48 usporiadaniach medzi nimi) dostalo y a z správne a x zle.

Iné formáty pozícií alebo indexov sa **odmietnu** („only 13 (four shorts, scaled) is
implemented“; „only unsigned shorts are implemented“).

### Podsiete {#submeshes}

Záznam `Mesh` má 238 bajtov v štandardnej forme. Dlhšie nesú dlhšiu tabuľku
materiálových **variantov** vpredu, 238 + 8 x count - 4 bajty, a každé pole za ňou sa
posunie presne o tú hodnotu. Kratšie (218 bajtov, časť terénu) si ponechajú offsety.
Každá položka variantu je `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`.
Maska úrovne detailu je u16, jeden bit na úroveň od bitu 1.

Nič sa neberie len samo o sebe. Rozsahy indexov musia presne pokryť buffer indexov,
každý `index count` sa musí rovnať 3 x `triangles` a krok, ktorý podsieť uvedie, musí
byť krokom jej bufferu. Tabuľka, ktorá zlyhá, sa odmietne celá, lebo označovanie
trojuholníkov zo zle čítaných polí je horšie ako neoznačovať. Pri tisíckach
vzorkovaných podsietí prejde každá, ktorej index bufferu je v rozsahu.

### Materiály a hashe textúr {#materials-and-texture-hashes}

`MatI` pomenuje svoj materiál cestou `Game:...\x.materialbin`, nájdenou hľadaním v
chunku. Jeho textúry sú záznamy `u32 slot, u32, u32 hash` vzdialené 33 bajtov od seba
a nezarovnané, takže sa chunk prehľadáva na každom bajtovom offsete pre slová, ktoré sú
známe hashe textúr. Tie pochádzajú z `AssetManifest.xml` trate
(`<Texture Source="...\name.swatch" SourceHash="...">`, čítané až po `</Textures>`).
Slot `0x88B483AA` je základná farba štandardného shaderu. Ako sa potom vyberie farebná
textúra, je na stránke [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: textúrové vzorníky {#pb-texture-swatches}

Vzorník je ten istý kontajner `burG` ako model: 96-bajtová hlavička `HCXT` na bajte 44,
potom jeden chunk pixelov. Hlavička obsahuje GUID textúry (to v názve súboru), šírku
a výšku, počet mipov a **kód formátu na bajte 72** (ForzaTech vlastné číslovanie).
Bajt 84 obsahuje počet bajtov pixelov.

| Kód | Formát | Identifikované ako |
|---|---|---|
| 0 | BC1, pol bajtu na pixel | dekóduje sa na červeno-bielý obrubník (pod BC4 šum) |
| 9 | BC7, jeden bajt na pixel | dekóduje sa na dlaždicu terénu s viditeľným okruhom |
| 13 | RGBA8, štyri bajty na pixel | obyčajný |
| iné | odmietnuté | „texture format N has not been identified; refusing to guess“ |

Formáty sa identifikovali dekódovaním skutočných súborov všetkými spôsobmi, aké
veľkosť užitočných dát dovoľuje. Bajt 47, ktorý staršia verzia považovala za formát,
je 4 vo všetkých vzorkovaných textúrach. Dekóduje sa len najvyšší mip súboru. Každé
rozlíšenie je vlastný záznam `<name>_<guid>_quality<n>.pb`, kvalita 1 najmenšia až 5
najväčšia. Pri mapách terénu sú dve najväčšie v inom archíve než zvyšok. Dekódovanie
ide cez BCn dekodér Pillow, cez vygenerovanú hlavičku DDS.

## Súbory umiestnení (.pgeo) {#placement-files-pgeo}

Jeden súbor na kategóriu na každú priestorovú bunku:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Samotná cesta dáva
štvorec bunky a kategóriu, takže súbory sa dajú filtrovať bez ich otvárania.

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

Ako sa rozhodlo o každom poli:

| Pole | Rozhodnuté podľa |
|---|---|
| pozícia je pevná rádová čiarka 16.16, nie zlomok boxu | po sebe idúce zvodidlá sú presne 4,000 m od seba (dĺžka modelu) |
| znamienko a veľkosť, nie dvojkový doplnok | dvojkový doplnok dával záporné súradnice desiatky kilometrov mimo mapy; s bitom 31 ako znamienkom každý záznam každej kategórie vzorkovaný padol do boxu svojho súboru |
| vektory sú vlastné osi modelu | koniec každého zvodidla padne na začiatok ďalšieho: 93,5 % do 5 cm, medián 0,000 m |
| bajt 60 je variant | päť kópií odrazového stĺpika číta 0, 2, 2, 3, 4, kým každé zvodidlo číta 0 |

Modelové záznamy sú len názvy končiace na `_3D`. Tabuľka variantov pred nimi uvádza
názvy bez tejto prípony a čítané ako záznamy by padli do nekonečna. Kandidátsky
záznam sa prijme, len ak jeho počet sa zmestí do súboru, a inštancie s nekonečnými
číslami sa zahodia.

## Nie je implementované {#not-implemented}

- Formáty vrcholov a indexov iné ako vyššie uvedené (odmietnuté).
- Formáty textúr iné ako 0, 9, 13 (odmietnuté).
- Tangenty (preskočené, nepoužité).
- Vrstvy materiálu shaderu terénu. Textúra povrchu je interpretáciou máp dlaždíc
  (pozri [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
