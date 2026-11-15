---
title: "Skedarët e BeamNG"
nav_order: 8
lang: "sq"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Skedarët e BeamNG: arkivat e niveleve, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive dërgon arkiva zip të thjeshta, prandaj nuk ka kontejner për t'u inxhinieruar
në të kundërt. Puna është të lexosh një nivel **ashtu siç e bën loja**: montimi i
arkivave në një sistem të vetëm skedarësh, ndjekja e skedarëve të skenës, dhe dekodimi i
terrenit dhe i formave të përpiluara. Këta lexues arrihen përmes eksportit të kursit
[BeamNG.drive](course-beamng.md). `identify` emërton gjithashtu një zip niveli,
një `.cdae` dhe një `.ter`, dhe `list` e `extract` marrin cilindo nga zip-et.

Burimet: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Sistemi i montuar i skedarëve {#the-mounted-file-system}

`Files.of_install(game)` ndërton një indeks të vetëm pa dallim shkronjash mbi
`gameengine.zip`, zip-et `content` (përveç automjeteve dhe tingujve), dhe modet e
përdoruesit (`mods\*.zip`, `mods\unpacked\*`, dhe një dosje `levels` e përdoruesit). Shtesat
e mëvonshme mbivendosin ato të mëparshme, si në lojë. Kërkimet injorojnë shkronjat e mëdha e të vogla sepse referencat e vetë
niveleve nuk përputhen me arkivat në këtë (`.DAE` për një
`.dae`). Detajet janë te [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` gjen një shteg ashtu siç e bën loja: siç është dhënë, relativ me skedarin
që e emërtoi, `x.png` si `x.dds`, `x.dae` si `x.cdae` (preferohet), dhe përmes një
skedari JSON `x.png.link` që `path` i tij tregon brenda `/assets`.

## Skedarët e skenës {#scene-files}

| Burimi | Formati | Lexohet |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | një objekt JSON për rresht, ose një varg ose hartë e vetme JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | të njëjtat klasa, për nivelet më të vjetra pa `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript ose JSON | fëmijët e vendosur relative me prefab, deri në 8 nivele thellësi |
| `levels\<name>\forest\*.forest4.json` | një instancë për rresht | të tipizuara nga regjistrat `TSForestItemData` në `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | titulli i nivelit (çelësat e përkthimit injorohen) |

**Transformimet.** `rotationMatrix` janë nëntë numra **rreshtat** e të cilëve janë
akset e vetë objektit në botë. Seksionet e parmakut të vargëzuara përgjatë një rruge shkojnë përgjatë rreshtit 0
(92%), dhe rreshti lart anon me pjerrësinë e rrugës. Prefab-et më të vjetër japin
`rotation = "x y z degrees"`, një kthesë e dorës së djathtë me atë kënd (92% e vargjeve
parmaku përputhen me të, 19% me kahun e kundërt). Shkalla i shumëzon rreshtat,
dhe `position` (ose `pos`) është rreshti i fundit. Transformimi i një fëmije prefab
përbëhet me atë të prefab-it. `groupPosition` i prefab-it është pivot redaktori dhe
**nuk** zbritet: një prefab trolejbusi qëndron në tokë vetëm pa të.

Numrat TorqueScript lexohen me një model tolerant, sepse disa prefab-e të dërguar
shkruajnë vlera si `-0.99563-0.0` pa hapësirë.

## Terreni: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Lartësia në metra: `position.z + h * maxHeight / 65535`, me `position`,
  `squareSize` dhe `maxHeight` nga `TerrainBlock` (parazgjedhjet 0, 1 dhe 2048).
- Rreshtat shkojnë përgjatë +y. Pika e rrjetës (i, j) është te
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Shtresa 255 është vrimë.

Kontrolluar: nyjet e rrugës shtrihen mbi terren brenda 1-2 cm (mediana) në tre nivele.
`h / 32`, ose rendi tjetër i akseve, gabon me dhjetëra deri qindra metra.

## Materialet {#materials}

Çdo `*.materials.json` jashtë `levels\`, plus ato të nivelit aktual, i indeksuar sipas
`mapTo`, `name` dhe çelësit:

| Klasa | Fushat e përdorura |
|---|---|
| `Material`, `CustomMaterial` | harta e ngjyrës (`baseColorMap`, `colorMap` ose `diffuseMap`, faza e parë), faktori i ngjyrës, harta dhe faktori i patejdukshmërisë, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | harta bazë dhe `diffuseSize`, harta e detajit, madhësia dhe forca, harta makro, madhësia dhe forca, `groundmodelName`, `annotation` |

Imazhet dekodohen me Pillow (DDS, PNG e kështu me radhë), duke përdorur një skicë me madhësi të zvogëluar
ku është e mundur, dhe ruhen në cache sipas madhësisë. Një teksturë e palexueshme kthehet te ngjyra e sheshtë.

## Format e përpiluara: `.cdae` {#compiled-shapes-cdae}

`.cdae` është cache i vetë lojës i çdo skedari Collada, i shkruar si MessagePack. Struktura e tij
është **e dokumentuar nga BeamNG**
(documentation.beamng.com/modding/file_formats/cdae/) dhe lexuesi e ndjek:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Çfarë lexohet: kufijtë, nyjet, objektet, detajet (nivelet e detajit), rrotullimet
parazgjedhëse të nyjeve (`Quat16`) dhe translatimet, kulmet, UV-të, normalet,
ngjyrat, primitivat dhe indekset e çdo rrjete, dhe emrat e materialeve. Emrat e materialeve gjenden
në fund të rrjedhës, sepse sekuencat e një objekti të animuar vijnë para tyre
në një formë që nuk është e dokumentuar.

Dy gjëra që dokumentimi nuk i shpjegon, të zgjidhura kundrejt skedarëve `.dae`
nga të cilët u ndërtuan format:

- **Rrotullimet e nyjeve janë të Torque.** Një `Quat16` i lexuar sipas librit rrotullon
  në anën e gabuar. Matrica e tij duhet **transpozuar**. Me këtë, kufijtë e botës të çdo nyjeje
  përputhen me Collada deri në milimetër. Pa të, janë 38 cm gabim
  në mediane.
- **Njësitë dhe akset janë aplikuar tashmë.** Një skedar Collada i krijuar në centimetra
  ose Y-lart del nga cache në metra, Z-lart.

Nivelet e detajit janë `details` me madhësi jo-negative, më e madhja së pari.
Madhësitë negative janë rrjeta përplasjeje dhe vijës së shikimit, nuk vizatohen kurrë. Objektet me emër
`colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` ose `imposter`
nuk vizatohen kurrë. Vizatohen vetëm rrjetat standarde dhe të renditura. Rrjetat me skelet
(personazhe, automjete) dhe rrjetat decal jo. Shiritat dhe ventilatorët e trekëndëshave
shpalosen, dhe faqet rimbështjellohen që të përputhen me normalet e ruajtura, çka mbështjellja
e vetë Torque nuk e premton.

Kontrolluar: pothuajse çdo formë e dërguar lexohet. Dy të tjerat janë një version
më i vjetër.

## Alternativa Collada: `.dae` {#collada-fallback-dae}

Për format pa `.cdae` (modet, dhe forma e rastit cache i së cilës është më i vjetër), skedari
Collada lexohet ashtu siç e lexon importuesi i Torque, në të njëjtën strukturë:

- Nivelet e detajit nga emërtimi i Torque: numri në fund të një nyjeje rrjete është
  madhësia në piksel nga e cila vizatohet (`barrier75`, `barrier40`). Një numër negativ, ose një
  emër `collision`/`Colmesh`/`LOS`/`nulldetail`, nuk vizatohet kurrë. Një formë pa
  konventën është një nivel.
- Njësitë nga `<unit meter>`, dhe Y-lart kthehet në Z-lart.
- UV-të përmbysen sipas konventës së cache (v shkon poshtë imazhit).

Kontrolluar kundrejt `.cdae` të vetë lojës të të njëjtave skedarë: pothuajse të gjithë kufijtë e mostruar brenda
1 cm, 583 me të njëjtin numër trekëndëshash, 94% e UV-ve të materialeve identike. Testi
me lojë të instaluar kërkon që 90% e deri në 60 çifteve formash nga arkivi i përbashkët i artit
të përputhen brenda 1 cm.

## Nuk lexohet {#not-read}

- Mbulesa e tokës (bar procedural), dhe çdo gjë e gjeneruar gjatë ekzekutimit.
- Sekuencat e animuara dhe skinning.
- Automjetet dhe tingujt (nuk montohen kurrë).
