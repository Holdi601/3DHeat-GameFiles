---
title: ForzaTech
lang: "no"
source: reader-forzatech.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, fargeprøver, plasseringer

Forza Horizon kjører på ForzaTech, Turn 10s egen motor. Disse leserne tar en bane fra arkivene sine og ned til
posisjonerte, tekstuerte trekanter. De nås gjennom `course`, `courses` og `terrain` (se [Forza Horizon](course-forza-horizon.md)).
`identify` gjenkjenner en `.minizip` og en ren `.modelbin`, og `list` og `extract` tar en `.minizip`, etter
navnene i `ChunkContentsMiniZip<n>.txt` ved siden av den, eller etter oppføringsnummer (`#12`).

| Format | Modul |
|---|---|
| `.minizip`-arkiver og deres navnelister | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin`-modeller og terreng | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb`-teksturfargeprøver | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo`-plasseringsfiler | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` og materialteksturhash-er | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| terrengfliser etter sted | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza har også mye av innholdet sitt i vanlige ZIP-arkiver under `media\`. Pythons `zipfile` åpner dem, og
`forzatech.models_in_archive()` lister deres `.modelbin`-oppføringer. Banegeometrien ligger i `.minizip`-arkivene.

## `.minizip`: et arkiv uten navn

En bane leveres med fire `GeoChunk<n>.minizip`-arkiver, titalls gigabyte hver for et åpent kart, med hundretusenvis
av oppføringer. **Arkivene lagrer ingen navn i det hele tatt**: ingen navnetabell og ingen header per oppføring, bare
et ordenstall. Navnene står i `ChunkContentsMiniZip<n>.txt` ved siden av hvert arkiv, én linje per oppføring i
oppføringsrekkefølge (`<build path>zipcache\pc\<path>|<bundle>`). Den paringen er den eneste måten å be om en fil
på. Alt opp til `zipcache\pc\` fjernes, og oppslag ignorerer store og små bokstaver.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tre detaljer i indeksen gir fortsatt utdata når de leses feil. Leseren får alle tre riktige:

| Detalj | Hva en uforsiktig leser gjør | Hvordan det ser ut |
|---|---|---|
| segmentbasen er **64-bits** | leser den som u32 pluss fylling | riktig for de første 4 GB, deretter støy av riktig lengde |
| basen er **8-byte-justert** | ignorerer fyllordet etter bundle-tabellen | i arkiver med et partall bundles peker hver oppføring på en kodek som ikke finnes |
| en oppføring sin lagrede lengde er gapet til neste oppføring (eller neste segments base) **minus sin fylling** (flaggbit 12-13) | bruker hele gapet | LZ4 avviser blokken helt |

Kodeker er de lave fem bitene av flaggene: `0x00` lagret, `0x08` rå deflate, `0x1F` LZ4-blokk. Alle andre avvises.
Hver oppføring må pakkes ut til nøyaktig størrelsen den oppgir, ellers avvises den. Indeksen (ca. 5 MB) leses én gang,
og nyttelaster leses ved å søke.

Headeren kontrolleres: magi, en 32-byte header, og et segmenttall som stemmer med `ceil(entries / per segment)`.

**Verifisert:** oppføringer stikkprøvet fra hvert arkiv i et kart, og hver pakkes ut til nøyaktig sin oppgitte lengde under
alle tre kodekene.

## `.modelbin`: chunk-beholderen

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Den deklarerte filstørrelsen må være lik den virkelige størrelsen.
- **Kjeden**: hver chunk starter der den forrige sluttet, avrundet opp til 4 byte. Ingenting i filen sier dette,
  så det er bevis: en post lest med feil steg produserer det ikke. Det holdt for alle 252 modeller som ble stikkprøvet.
- En `PGZP`-fil gitt til modelleseren blir kalt «a ForzaTech .minizip archive, not a model» og pekt til `minizip.py`,
  i stedet for å avvises tomt.

Geometrien kommer fra disse chunkene:

| Chunk | Inneholder |
|---|---|
| `VLay` | et hjørnepunktoppsett: attributtnavn, deretter elementer (u16-navneindeks, u16-kanal, buffer, DXGI-format, forskyvning); elementtallet er en u16 |
| `VerB` | en hjørnepunktbuffer bak en 16-byte header (antall, størrelse, u16-steg, u16-attributter, format) |
| `IndB` | indeksbufferen, samme header |
| `Mesh` | én undermesh: materiale, detaljnivåmaske, indeksområde, oppsett, buffer, steg, variantstabell, og en posisjonsboks på slutten |
| `MatI` | en materialinstans: dens `.materialbin`-sti og teksturhash-er |

### Posisjoner og boksen

Posisjoner er `R16G16B16A16_SNORM` (format 13): fire fortegnede shorts per hjørnepunkt.
`position = short / 32767 * scale + bias`, der skala og bias er de siste 32 bytene av `Mesh`-chunken (to float4).
Biasen er i **spillets verdenskoordinater**, så en terrengflis havner der spillet plasserer den uten noen
instanstransform. Derfor er et telemetrispor nok til å be om en bit av kartet.
Hver undermesh i en modell bærer samme boks (kontrollert over 860 av dem).

### Hjørnepunktoppsettet

Én posisjonsbuffer dekker alle hjørnepunktene. De andre attributtene er delt i påfølgende hjørnepunktgrupper, hver med
sin egen buffer og sitt eget oppsett: vei nær et kryss bærer tre UV-sett og to tangenter, banken ved siden bare en
normal. Hvert ikke-posisjonsattributt er fire byte. Hvilket oppsett som beskriver hvilken buffer, tas fra undermeshene
som tegner fra den, fordi oppsett og buffere ikke står i samme rekkefølge (samme, rotert med én, eller permutert,
avhengig av modellen).

| DXGI-format | Kode | Brukes til |
|---|---|---|
| R16G16B16A16_SNORM | 13 | posisjon (den fjerde shortet er normalens x) |
| R16G16_SNORM | 37 | normal y, z |
| R16G16_UNORM | 35 | et UV-par (kanal = hvilket sett) |
| R8G8B8A8_UNORM | 28 | farge eller blandevekter |
| R10G10B10A2_UNORM | 24 | tangent (ikke dekodet) |
| R16_UINT | 57 | indekser |

**Normalen er delt.** `NORMAL` holder y og z. X-en er posisjonens fjerde short, som så ut som fylling. Over hundretusenvis
av terrenghjørnepunkter korrelerer den +0,92 med x-en til trekantnormalen og med ingenting annet. Med den ligger 96 % av
skråningshjørnepunktene innen 18° av den beregnede normalen. Hver tokomponent-koding som ble prøvd uten den (oktaedrisk i alle
48 oppsett blant dem) fikk y og z riktige og x feil.

Andre posisjons- eller indeksformater **avvises** («only 13 (four shorts, scaled) is implemented»; «only unsigned shorts are implemented»).

### Undermasker

En `Mesh`-post er 238 byte i standardformen. Lengre poster har en lengre materialvariant-tabell foran, 238 + 8 x antall - 4
byte, og hvert felt etter den flyttes tilbake med nøyaktig så mye. Shorter poster (218 byte, noe terreng) beholder forskyvningene.
Hver variantpost er `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. Detaljnivåmasken er en u16, én bit per nivå
fra bit 1.

Ingenting stoles på alene. Indeksområdene må dekke indeksbufferen nøyaktig, hvert `index count` må være 3 x `triangles`, og
steget en undermesh oppgir, må være dens buffers. En tabell som ikke går opp, avvises helt, fordi å merke trekanter ut fra
feillest felt er verre enn å ikke merke dem. Blant tusenvis av stikkprøvede undermasker består hver én hvis bufferindeks er i
området.

### Materialer og teksturhash-er

En `MatI` navngir sitt materiale med en `Game:...\x.materialbin`-sti, funnet ved å søke i chunken. Dens teksturer er
`u32 slot, u32, u32 hash`-poster, 33 byte fra hverandre og ujusterte, så chunken søkes ved hver bytforskyvning etter ord som
er kjente teksturhash-er. Disse kommer fra sporets `AssetManifest.xml`
(`<Texture Source="...\name.swatch" SourceHash="...">`, lest til `</Textures>`). Slot `0x88B483AA` er standard-shaderens
grunnfarge. Hvordan fargeteksturen så velges, står på [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: teksturfargeprøver

En fargeprøve er den samme `burG`-beholderen som en modell: en 96-byte `HCXT`-header ved byte 44, deretter én chunk med piksler.
Headeren holder teksturens GUID (den i filnavnet), bredde og høyde, antall mip-nivåer, og **formatkoden ved byte 72**
(ForzaTechs egen nummerering). Byte 84 holder antall pikselbyte.

| Kode | Format | Identifisert som |
|---|---|---|
| 0 | BC1, en halv byte per piksel | dekodes til en rød og hvit kantstein (støy under BC4) |
| 9 | BC7, en byte per piksel | dekodes til en terrengflis med banen synlig |
| 13 | RGBA8, fire byte per piksel | enkel |
| annet | avvist | «texture format N has not been identified; refusing to guess» |

Formatene ble identifisert ved å dekode ekte filer på alle måter nyttelastens størrelse tillater. Byte 47, som en tidligere
versjon tok for formatet, er 4 i hver eneste stikkprøvede tekstur. Bare toppmipet i en fil dekodes. Hver oppløsning er sin egen
oppføring, `<name>_<guid>_quality<n>.pb`, kvalitet 1 minst til 5 størst. For terrengkart ligger de to største i et annet arkiv enn
resten. Dekoding går gjennom Pillows BCn-dekoder, via en generert DDS-header.

## Plasseringsfiler (.pgeo)

Én fil per kategori per romlig celle:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Stien alene gir cellens kvadrat og kategori, så filer kan
filtreres uten å åpne dem.

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

Hvordan hvert felt ble avgjort:

| Felt | Avgjort av |
|---|---|
| posisjon er 16.16 fastkomma, ikke en brøkdel av boksen | påfølgende veirekkverk står nøyaktig 4,000 m fra hverandre (modellens lengde) |
| fortegn-og-størrelse, ikke tokomplement | tokomplement plasserte negative koordinater titalls kilometer av kartet; med bit 31 som fortegn havner hver post i hver kategori som ble stikkprøvet innenfor sin fils boks |
| vektorene er modellens egne akser | enden av hvert veirekkverk havner på starten av det neste: 93,5 % innen 5 cm, median 0,000 m |
| byte 60 er varianten | fem kopier av et skilt leses 0, 2, 2, 3, 4 mens hvert veirekkverk leses 0 |

Bare navn som slutter på `_3D`, er modellposter. Variantstabellen foran dem lister navn uten suffikset, og leses
man de som poster, havner de i uendeligheten. En kandidatpost aksepteres bare hvis antallet får plass i filen, og
instanser med ikke-endelige tall fjernes.

## Ikke implementert

- Hjørnepunkt- og indeksformater annet enn de over (avvist).
- Teksturformater annet enn 0, 9, 13 (avvist).
- Tangenter (leses forbi, ikke brukt).
- Terrengshaderens materiallag. Bakketeksturen er en tolkning av flisekartene (se [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
