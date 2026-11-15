---
title: "Begränsningar och kända brister"
nav_order: 10
lang: "sv"
source: limits-and-known-gaps.md
source_hash: "02df0dd20fc9"
nav_exclude: true
search_exclude: true
---
# Begränsningar och kända brister {#limits-and-known-gaps}

Vad verktyget inte gör, vad det gör bara delvis, och var dess beteende är ojämnt.
De flesta brister är avsiktliga avslag. Att avkoda utan en fil att kontrollera mot
ger utdata som ser rätt ut men inte är det.

## Spel {#games}

| Spel | Banexport | Varför inte, eller hur långt det räcker |
|---|---|---|
| Forza Horizon | ja | markfärgen är en tolkning (se nedan) |
| BeamNG.drive | ja | ingen markvegetation, upprepade modelltexturer plattas ut |
| Assetto Corsa Rally | ja | modeller med platta färger; ännu inte körd på ett varv inspelat i spelet |
| Assetto Corsa EVO | **nej** | allt innehåll ligger i ett paket, obfuskerat med en nyckel, och verktyget återskapar inga nycklar |
| Battlefield 6 (nivåexport, `level`) | ja, en hel nivå | terräng, grupperade och enskilt placerade meshar och deras färgkartor, soldaternas navigeringsmesh, utskuren vegetation; spelområdets markfärg är grov (32 m per pixel, eller en enda genomsnittsfärg); ingen genomskinlighet eller normalkartor; förstörbara meshar taggade, deras förstörda tillstånd exporteras inte |
| Unreal 5 World Partition-spel (kartexport, `ue-map`) | ja, en hel karta | landskapet exakt; byggnader som kartans förenklade HLOD-meshar, inte de fullt detaljerade modellerna; vattenkroppar; ingen växtlighet, dekaler eller markfärg |
| Arma Reforger (världsexport, `enfusion-world`) | ja, en hel värld | terräng i sina egna färger och havet; byggnader, rekvisita och stenar som modellernas lådor, inte deras trianglar; träd på begäran (`--trees`), som lådor; inga sjöar, floder eller underentiteter |
| iRacing | **nej** | banorna levereras i ett skyddat format som inte är ett mål för filutvinning |
| allt annat | **nej** | det finns ingen banläsare; återskapa från spelet med 3DHeat GameCapture, eller analysera varven i visarens flik Racinganalys utan bana |

## Motorer och format {#engines-and-formats}

| Format | Inte implementerat |
|---|---|
| Unreal `.pak` | versioner före 8; index med bara sökvägshashar (namnen kan inte återskapas); poster i indexets överflödeslista (hoppas över); avkodning av `.uasset`/`.umap`-innehåll ur ett pak |
| Unreal IoStore | krypterade behållare (vägras, inget nyckelalternativ); lista en behållare utan katalogindex (den namnger inga filer); versionerade paket; meshar som bara finns i Nanite och meshar som inte är inline; skelettmeshar; egenskaper hos klasser utan schema; instansierade komponenters egenskaper (layouten ändrad i spelets version); spline-meshar och dekalkomponenter |
| Unity | format före 22 (Unity 2019 och äldre); filer med inbäddade typträd; komprimerade meshar; alla klasser utom `Mesh`, så inga transformer, material eller scener; `meshes` på ett paket; `list`/`extract` (använd `meshes`) |
| Frostbite | XOR-maskerade tabeller; terrängens lagergraf (masker lästa i cirka en tredjedel av de kontrollerade nivåerna); objektsmallar som inte är meshar (spellogik, effekter, ljud); meshnivåer lagrade inline; normal- och andra kartor, alfa utom utskärningar; terränghål; typbiblioteket (krypterat i det initiala filsystemet, inte berört); ett kommando för att lista eller extrahera enskilda assets |
| Source 2 | kompilerade assets (`.vmdl_c`, `.vtex_c`); CS2:s navmesh (version 36) |
| ForzaTech | positionsformat utom fyra skalade shorts; indexformat utom u16; texturkoder utom 0, 9, 13; terrängshaderns materiallager; tangenter |
| BeamNG | skinnade meshar och dekalmeshar; animation; procedurell markvegetation; scenerier längs världens kant |
| Unreal-landskap och World Partition-kartor | landskap vars höjdkartor ligger i de cachade cellerna; redigeringslager och hål; Nanite-landskapsmeshar; fullt detaljerade modeller placerade i cellerna; växtlighet; landskapsmaterial |
| Enfusion | modelltrianglar (`.xob`-geometri är komprimerad i en layout som inte läses); `.edds` med pre-DX10-headers; värden för kapslade objekt i världsfiler (hoppas över, räknas); underentiteter; genererade sjöar och floder; `list`/`extract` på en `.pak` |

## Beteende värt att känna till {#behaviour-worth-knowing}

- **Forzas markfärg är inte spelets.** Den inbakade texturen ritas från rutkartorna
  som säger *var* asfalt, kort gräs, ojämn mark och skog finns. Den använder fasta
  färger och skuggning, eftersom terrängshaderns egna materiallager inte avkodas.
- **`--no-textures` tar också bort Forzas kant.** Delningen asfalt/kant använder
  asfaltmasken som följer med de inbakade kartorna. Utan texturer förblir vägremsor
  hela som väg.
- **En budget du anger kan bara överskridas av kantstenar.** Kantstenar (och BeamNG:s
  modeller med körbar yta) förenklas aldrig och utelämnas aldrig, i något spel, så en
  `--detail-budget` som är mindre än vad de kostar överskrids av dem ensamma; allt
  annat utelämnas först. Se [Detaljnivåer och budgeten](detail-budget.md).
- **Alternativ som inte gäller ignoreras tyst**: `--season` för BeamNG och AC Rally,
  `--track` för BeamNG och AC Rally, `--level`/`--install` för Forza.
- **En Battlefield 6-nivås markfärg är grov utanför dess dekaler.** Höjdfältet
  färgas från terrängkulissens färgkarta, 32 m per pixel på den största mipnivå
  nivån levererar, eller, där ingen kulisskarta täcker det, i mellanfärgen för
  terrängens ytmaterial; `--ground-texture` multiplicerar det med terrängens
  färgkarta (på 0,5 m per pixel där nivån har en) och bakar vägar, plattor,
  landningsbanelinjer, däckspår och markeringar in i det, i deras materials
  målarfärg där en sådan är satt och i en neutral där den inte är det; vägens
  variationsmasker utelämnas. Spelet blandar sina ytlager i en shadergraf som inte
  läses; exporten lägger ut lagrens färger efter deras masker och höjdfältets lutning,
  enligt en egen regel, och en nivå vars maskssidor inte passar ihop får en enda färg.
  Varje lager är dess färgkartas medelvärde, inte dess textur. Se
  [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#terrain-layers). Bitar av höjdfältet i olika
  upplösning möts med små steg.
- **En Battlefield 6-färgkarta väljs, den läses inte.** Ett shaderblock anger varje
  textur det samplar utan att säga vilken som är färgen; valet går efter namn (se
  [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#textures-and-materials)) och kan välja ett trim- eller
  detaljark för en yta. Dekalark (`t_de_...`) förlorar mot ytans egen karta; en skylts
  dekal som ritades som sin panel, med dess sköld, vreds en kvarts varv. Distansfält,
  paletter och kanalmasker tas aldrig. Kulissbyggnader ritas i sina paletters färger;
  gråa kartor tar materialets tonning enligt en regel som exportören själv har, eftersom
  parametrarnas namn är hashade, och ett material som målar en grå karta genom en mask
  med flera tonningar får en av dem.
- **Battlefield 6-terränghål skärs inte.** Där en nivås gångbara mark ligger under
  höjdfältet måste spelet ha skurit i terrängen, och exporten gör inte det. Utesluten
  som plats för hålen: terrängens lagermasker (ingen är koncentrerad där), dess
  67 x 67-nodraster, ett reserverat höjdvärde (ingen höjdsida innehåller 0 eller
  65 535), nodernas flaggor (alla lika) och meshar eller assets som skär i marken: det
  som placeras under marken där är berg- och klippmeshar, och inget asset i nivån är
  namngivet för hål, tunnlar eller grottor. Två rastraträd är körlängdsavkodade men
  inte placerade, och är det som återstår (se
  [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#terrain-layers)).
- **En Battlefield 6-objektvariation når en sektion via sina tvillingar.** En
  placerad kopias variation väljer sina sektioners shaderblock med nyckel; där en mesh
  inte har något block för en variation tas varianten av en annan meshs sektion med
  ett identiskt standardblock (se [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#textures-and-materials)).
  Det är exportörens regel; en sektion utan någon tvilling som varierar behåller sitt
  standardutseende.
- **Battlefield 6-lagrade material ritas som sin bas och ett ark.** En väggpanel med
  bokstäver ritas som sin puts med bokstavsarket över sig; materialets övriga lager
  (smutsöverlägg genom sin mask, detalj- och mossKartor) blandas inte in.
- **Navigeringsmeshen är AI:ns, inte spelarnas.** Den täcker det en soldat kan gå
  till: marken, golv och trappor, och vissa tak, men inte varje hög punkt. Länkarna
  mellan ytor (hopp, stegar, övertag) utelämnas.
- **En Battlefield 6-nivå innehåller varje spelläges lager.** Objekt som bara ett läge
  placerar kan överlappa ett annat läges. `--skip` lämnar lager utanför efter namn.
- **`courses` gäller bara Forza**, och plockar bara upp bibliotekets mappar med
  namn på formen `... (course_...)`.
- **BeamNG:s varvram antas** vara visarens ram `(x, z, -y)` som 3DHeat-inspelaren
  skriver. Varv från en annan inspelare i BeamNG:s råa ram skulle inte placeras.
- **`list` och `extract` tar arkiven, inte alla format.** De öppnar en `.pak`, en
  IoStore-`.utoc`, en `.vpk`, en `.minizip` och en zip. En Unity-behållare läses med
  `meshes`, en Frostbite-nivå med `level`, och en `.cdae` eller `.ter` är en fil och
  inte ett arkiv (`identify` namnger den). En `.minizip` utan sin
  `ChunkContentsMiniZip<n>.txt` bredvid listas efter postnummer.
- **Placerade modeller i BeamNG använder upprepande texturer som medelfärger**,
  eftersom `.glb`-samplern klämmer och visaren packar texturer i en atlas.
- **Windows i praktiken.** Steam-sökvägar under `C:\Program Files`,
  `%LOCALAPPDATA%`, `C:\XboxGames`, och en `*_win64.dll` för Oodle. Andra plattformar
  är inte testade.

## Overifierat {#unverified}

- Äldre Python-versioner (verktyget har körts med 3.13).
- Assetto Corsa Rally med ett varv inspelat i spelet. Det har bara testats med
  syntetiska varv i slumpvalda riktningar.
- glTF-visare utom 3DHeat-visaren.
- Om varje spels ram är vänster- eller högerhänt. Exporten behåller varje spels
  telemetriram, så varv och banor passar ihop oavsett.
- Betydelsen av `WaterBlock`:s lokala z = 0 som dess yta (BeamNG).
- Frostbite-placering på andra spel än Battlefield 6, och på Battlefield 6 efter en
  uppdatering som ändrar gruppmedlemmarnas layout. Läsaren hittar då inga grupper och säger det.
- Om en Battlefield 6-export passar ihop med positioner som spelet rapporterar.
  Koordinaterna är spelets egna, som för de andra spelen, men ingen inspelning har
  ännu lagts över en.
