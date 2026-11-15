---
title: "ForzaTech"
nav_order: 7
lang: "sl"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, vzorci, postavitve {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon teče na ForzaTech, lastnem pogonu podjetja Turn 10. Ti bralniki vzamejo progo iz njenih arhivov do postavljenih, teksturiranih trikotnikov. Do njih pridemo prek `course`, `courses` in `terrain` (glejte [Forza Horizon](course-forza-horizon.md)). `identify` prepozna `.minizip` in goli `.modelbin`, `list` in `extract` pa vzameta `.minizip` po imenih v `ChunkContentsMiniZip<n>.txt` ob njem ali po številki vnosa (`#12`).

| Format | Modul |
|---|---|
| arhivi `.minizip` in njihovi seznami imen | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modeli in teren `.modelbin` | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| vzorci tekstur `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| datoteke postavitev `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` in zgoščene vrednosti tekstur materialov | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| ploščice terena po mestu | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza veliko vsebine hrani tudi v običajnih arhivih ZIP pod `media\`. Python-ov `zipfile` jih odpre, `forzatech.models_in_archive()` pa našteje njihove vnose `.modelbin`. Geometrija proge je v arhivih `.minizip`.

## `.minizip`: arhiv brez imen {#minizip-an-archive-with-no-names}

Proga ima štiri arhive `GeoChunk<n>.minizip`, za odprt svet vsak po deset in več gigabajtov, s stotinami tisoč vnosi. **Arhivi ne shranjujejo nobenih imen**: ne tabele imen ne glave na vnos, samo zaporedno številko. Imena so v `ChunkContentsMiniZip<n>.txt` ob vsakem arhivu, po ena vrstica na vnos v vrstnem redu vnosov (`<build path>zipcache\pc\<path>|<bundle>`). Ta parnost je edini način, kako zahtevati datoteko. Vse do `zipcache\pc\` se odstrani, iskanja pa ne upoštevajo velikosti črk.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Trije podrobnosti v kazalu še vedno dajo izhod, če se napačno preberejo. Bralnik vse tri pravilno obravnava:

| Podrobnost | Kaj naredi nepazljiv bralnik | Kako izgleda |
|---|---|---|
| osnova segmenta je **64-bitna** | prebere jo kot u32 in polnilo | pravilna za prvih 4 GB, nato šum prave dolžine |
| osnova je **poravnana na 8 bajtov** | prezre polnilno besedo za tabelo paketov | v arhivih s sodim številom paketov vsak vnos zahteva kodek, ki ne obstaja |
| shranjena dolžina vnosa je razmik do naslednjega vnosa (ali osnove naslednjega segmenta) **minus njegovo polnilo** (biti zastavic 12-13) | uporabi celoten razmik | LZ4 jo zavrne v celoti |

Kodeki so nižjih pet bitov zastavic: `0x00` shranjeno, `0x08` surov deflate, `0x1F` blok LZ4. Vsak drug je zavrnjen. Vsak vnos se mora razširiti natanko v velikost, ki jo navaja, sicer je zavrnjen. Kazalo (okoli 5 MB) se prebere enkrat, podatki pa se berejo s premikanjem.

Glava se preveri: magična številka, glava dolga 32 bajtov in število segmentov, ki se ujema z `ceil(entries / per segment)`.

**Preverjeno:** vzorčeni vnosi čez vse arhive vsake karte, vsak se razširi natanko na svojo navedeno dolžino pod vsemi tremi kodeki.

## `.modelbin`: vsebnik chunkov {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Navedena velikost datoteke mora biti enaka pravi velikosti.
- **Veriga:** vsak chunk se začne tam, kjer je končal prejšnji, zaokrožen navzgor na 4 bajte. Nič v datoteki tega ne pove, zato je to dokaz: zapis, prebran pri napačnem koraku, tega ne proizvede. Velja za vseh 252 vzorčenih modelov.
- Datoteka `PGZP`, podana bralniku modelov, je označena kot "a ForzaTech .minizip archive, not a model" in napotena na `minizip.py`, namesto da bi bila zavrnjena nejasno.

Geometrijo dajo ti chunki:

| Chunk | Vsebina |
|---|---|
| `VLay` | postavitev oglišč: imena atributov, nato elementi (u16 indeks imena, u16 kanal, medpomnilnik, format DXGI, odmik); število elementov je u16 |
| `VerB` | medpomnilnik oglišč za 16-bajtno glavo (število, velikost, u16 korak, u16 atributi, format) |
| `IndB` | medpomnilnik indeksov, enaka glava |
| `Mesh` | en podmesh: material, maska stopnje podrobnosti, obseg indeksov, postavitev, medpomnilnik, korak, tabela variant in škatla položaja na koncu |
| `MatI` | primerek materiala: njegova pot `.materialbin` in zgoščene vrednosti tekstur |

### Položaji in škatla {#positions-and-the-box}

Položaji so `R16G16B16A16_SNORM` (format 13): štirje predznačeni shorti na oglišče. `position = short / 32767 * scale + bias`, pri čemer sta scale in bias zadnjih 32 bajtov chunka `Mesh` (dva float4). Bias je v **svetovnih koordinatah igre**, zato pristane ploščica terena tam, kamor jo igra postavi, brez transformacije primerka. Zato je dovolj en lok telemetrije, da zahtevate kos zemljevida. Vsak podmesh modela nosi isto škatlo (preverjeno na 860 primerkih).

### Postavitev oglišč {#the-vertex-layout}

En medpomnilnik položajev pokrije vsa oglišča. Drugi atributi so razdeljeni na zaporedne skupine oglišč, vsaka s svojim medpomnilnikom in svojo postavitvijo: cesta blizu križišča nosi tri nabore UV in dve tangenti, breg ob njej samo normalo. Vsak drug atribut je štiri bajte. Katera postavitev opisuje kateri medpomnilnik, se vzame iz podmeshov, ki rišejo iz njega, ker postavitve in medpomnilniki nista v istem vrstnem redu (enako, zamaknjeno za ena ali permutirano, odvisno od modela).

| Format DXGI | Koda | Za kaj |
|---|---|---|
| R16G16B16A16_SNORM | 13 | položaj (četrti short je x normale) |
| R16G16_SNORM | 37 | normalna y, z |
| R16G16_UNORM | 35 | par UV (kanal = kateri nabor) |
| R8G8B8A8_UNORM | 28 | barva ali uteži mešanja |
| R10G10B10A2_UNORM | 24 | tangenta (ni dekodirana) |
| R16_UINT | 57 | indeksi |

**Normala je razcepljena.** `NORMAL` hrani y in z. x je četrti short položaja, ki je izgledal kot polnilo. Čez stotine tisoč oglišč terena korelira s +0,92 z x normale trikotnika in z ničimer drugim. Z njim je 96 % oglišč na pobočju znotraj 18° od izračunane normale. Vsaka kodirava z dvema komponentama brez njega (oktaedrična v vseh 48 razporeditvah vmes) je pravilno dobila y in z, x pa napačno.

Drugi formati položajev ali indeksov so **zavrnjeni** ("only 13 (four shorts, scaled) is implemented"; "only unsigned shorts are implemented").

### Podmeshi {#submeshes}

Zapis `Mesh` je v standardni obliki dolg 238 bajtov. Daljši zapisi nosijo daljšo tabelo **variant** materialov na začetku, 238 + 8 x count - 4 bajte, in vsako polje za njo se premakne nazaj za natanko toliko. Krajši (218 bajtov, nekateri tereni) ohranijo odmike. Vsak vnos variante je `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. Maska stopnje podrobnosti je u16, en bit na stopnjo od bita 1.

Nič se ne zaupa samo. Obsegi indeksov morajo natanko pokriti medpomnilnik indeksov, vsako `index count` mora biti enako 3 x `triangles`, korak, ki ga podmesh navede, pa mora biti korak njegovega medpomnilnika. Tabela, ki ne uspe, je zavrnjena v celoti, ker je označevanje trikotnikov iz napačno prebranih polj slabše od tega, da ni označeno. Med tisoči vzorčenih podmeshev vsak, katerega indeks medpomnilnika je v območju, prestane preverjanje.

### Materiali in zgoščene vrednosti tekstur {#materials-and-texture-hashes}

`MatI` svoj material poimenuje s potjo `Game:...\x.materialbin`, najdeno z iskanjem po chunku. Njegove teksture so zapisi `u32 slot, u32, u32 hash`, razmaknjeni za 33 bajtov in neporavnani, zato se chunk preiskuje na vsakem bajtnem odmiku za besedami, ki so znane zgoščene vrednosti tekstur. Te pridejo iz `AssetManifest.xml` proge (`<Texture Source="...\name.swatch" SourceHash="...">`, prebrano do `</Textures>`). Reža `0x88B483AA` je osnovna barva standardnega senčilnika. Kako se nato izbere barvna tekstura, je na [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: vzorci tekstur {#pb-texture-swatches}

Vzorec je isti vsebnik `burG` kot model: 96-bajtna glava `HCXT` na bajtu 44, nato en chunk slikovnih pik. Glava hrani GUID teksture (tistega v njenem imenu datoteke), širino in višino, število mipov ter **kodo formata na bajtu 72** (ForzaTechova lastna številčenje). Bajt 84 hrani število bajtov slikovnih pik.

| Koda | Format | Prepoznano kot |
|---|---|---|
| 0 | BC1, pol bajta na piksel | dekodira se v rdeč in bel robnik (šum pod BC4) |
| 9 | BC7, en bajt na piksel | dekodira se v ploščico terena, na kateri je vidna proga |
| 13 | RGBA8, štirje bajti na piksel | navadna |
| drugo | zavrnjeno | "texture format N has not been identified; refusing to guess" |

Formati so bili določeni z dekodiranjem pravih datotek na vse načine, ki jih dopušča velikost podatkov. Bajt 47, ki ga je prejšnja različica vzela za format, je v vseh vzorčenih teksturah 4. Dekodira se samo zgornji mip datoteke. Vsaka ločljivost je svoj vnos `<name>_<guid>_quality<n>.pb`, kakovost 1 najmanjša do 5 največja. Pri teksturah terena sta dve največji v drugem arhivu kot preostale.
Dekodiranje gre prek dekoderja BCn v Pillow, prek ustvarjene glave DDS.

## Datoteke postavitev (.pgeo) {#placement-files-pgeo}

Ena datoteka na kategorijo na prostorsko celico: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Sama pot pove kvadrat celice in kategorijo, zato se datoteke lahko filtrirajo, ne da bi jih odprli.

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

Kako je odločeno vsako polje:

| Polje | Odločeno z |
|---|---|
| položaj je fiksna vejica 16.16, ne ulomek škatle | zaporedne ograje so točno 4.000 m narazen (dolžina modela) |
| predznak-velikost, ne dvojiški komplement | dvojiški komplement je negativne koordinate postavil desetine kilometrov stran od zemljevida; z bitom 31 kot predznakom se vsak zapis vsake kategorije vzorca pristane znotraj škatle svoje datoteke |
| vektorji so osi modela same | konec vsake ograje pristane na začetku naslednje: 93,5 % znotraj 5 cm, mediana 0,000 m |
| bajt 60 je varianta | pet kopij ene table se bere 0, 2, 2, 3, 4, medtem ko vsaka ograja bere 0 |

Samo imena, ki se končajo z `_3D`, so zapisi modelov. Tabela variant pred njimi navaja imena brez pripone in, prebrana kot zapisi, pristanejo v neskončnosti. Kandidatni zapis je sprejet samo, če njegovo število ustreza datoteki, primerki z neskončnimi števili pa so izpuščeni.

## Ni implementirano {#not-implemented}

- Formati oglišč in indeksov razen zgoraj navedenih (zavrnjeni).
- Formati tekstur razen 0, 9, 13 (zavrnjeni).
- Tangente (preskočene, niso uporabljene).
- Plasti materialov senčilnika terena. Talna tekstura je interpretacija zemljevidov ploščic (glejte [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
