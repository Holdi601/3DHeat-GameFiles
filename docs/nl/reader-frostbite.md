---
title: "Frostbite"
nav_order: 5
lang: "nl"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, bundels, meshes en levels {#frostbite-toc-cas-bundles-meshes-and-levels}

**Leest een Battlefield 6-level tot aan zijn terrein, zijn geplaatste meshes en hun kleurkaarten, en schrijft
het als een `.glb`.** Frostbite-spellen (Battlefield, Need for Speed, Dead Space) bewaren hun inhoud in
`.cas`-blobs, beschreven door `.toc`-inhoudsopgaven. De tabel van een level zegt welke bundels het level
laadt, de bundels noemen elk asset, en de assets zeggen welk mesh waar staat.

Bronnen:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabellen, pakketten, payloads),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bundels en hun manifesten),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX-partities),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(hoogteveld),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(texturen en materialen),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(plaatsing en export).
Commando's: `identify`, `levels`, `level` (zie [Commando's](commands.md#levels-and-level-frostbite)).

Niets hier is door het spel gedocumenteerd. Elke indeling hieronder is van de bestanden afgelezen en daarna
tegen alle bestanden gecontroleerd, en elke sectie zegt wat de controle was. Waar de Frosty-modding-tools oudere
versies van een structuur beschrijven, volgen de veldnamen die van hen; er is geen code van hen overgenomen (zie
[Regels en licenties](rules-and-licences.md)).

## De kop die versleuteld lijkt en het niet is {#the-header-that-looks-encrypted-and-is-not}

| Magie (u32, little-endian) | Betekenis | Behandeling |
|---|---|---|
| `0x00CED100` | plain: de boom begint meteen | gelezen |
| `0x01CED100` | signed: een handtekening van 556 bytes, dan de boom **in de helder** | gelezen |
| `0x03CED100` | XOR-verduisterd, met de sleutel in de eigen kop van het bestand | herkend en geweigerd |

De signed-vorm is wat het huidige Battlefield gebruikt. De bytes met hoge entropie na de magie zijn een
handtekening, geen versleuteld materiaal.

## De DbObject-boom {#the-dbobject-tree}

Eén recursieve structuur. Elk veld is een typebyte (de onderste vijf bits het type, bit 7 "anoniem"), een
optionele naam, en een waarde. Containers dragen hun lengte als een variabel geheel getal en eindigen met een
nulbyte. `parse_toc` controleert de lengte van elke container, dus een bestand dat parseert, is begrepen.
`layout.toc` heeft deze vorm.

## Installatiepakketten {#installation-packages}

Elke locatie noemt het **installatiepakket** waartoe zijn blob hoort. Elk pakket nummert zijn blobs vanaf
`cas_01`, dus het blobnummer alleen is dubbelzinnig zodra er meer dan één pakket is geïnstalleerd, en dat is
altijd het geval.

- `layout.toc` somt de pakketten op onder `installManifest.installChunks`, elk met een `persistentIndex` en een
  `installBundle` zoals `Win32/installation/<package>`.
- De blobs van het pakket staan in die map, onder `Data` voor het basisspel of onder `Update/<pack>/Data` voor
  wat later kwam.
- Een locatierecord draagt de volledige 32-bit `persistentIndex`: het lage halfwoord van zijn eerste woord bevat
  het hoge halfwoord, het hoge halfwoord van zijn tweede woord het lage halfwoord; het lage halfwoord van het
  tweede woord is het blobnummer.

Controle: elke locatie in elke binaire tabel van een installatie wordt opgelost naar een aangegeven pakket en valt
binnen de blob die hij noemt. Een eerdere versie nam het eerste `cas_NN.cas` van het juiste nummer. Een derde van
de payloads die die las, zag er dan uit als hoge entropie en werd voor versleuteling gehouden. Het waren de juiste
offsets in het verkeerde bestand. Niets wat gevonden is, is versleuteld.

## De leveltabel {#the-level-table}

De tabel van een level (`levels/<level>/<level>.toc`) is een sectietabel: vijftien big-endian kopwoorden, dan
secties van begin tot eind, waarvan de offsets zowel vermeld als afleidbaar zijn uit twee tellingen.

| Sectie | Inhoud |
|---|---|
| bundels | een hashtabel (één woord per bundel), dan een record van 16 bytes per bundel: sleutel, `0x40000000` \| grootte, 0, offset |
| chunk-hashtabel | één woord per chunk |
| chunks | 16-byte id (de GUID van de chunk **byte-omgekeerd**), dan een woord: `0x80000000` \| 4 x de index van zijn locatie |
| locaties | vier big-endian woorden: pakket (gesplitst), blob, offset, grootte |

De chunk-ids en de locaties staan in **verschillende volgorden**. Ze in bestandsvolgorde lezen koppelt elke chunk aan de bytes van een andere chunk. Die bytes decoderen vaak prima (meestal als geluid), dus het lijkt pas fout als een mesh als ruis verschijnt. Controle: in een level zijn de indexwoorden een permutatie van 0 tot het aantal chunks
min één.

De bundels staan inline na de sectietabel. Elk heeft negen big-endian kopwoorden, dan zijn items: acht bytes
offset en grootte, voorafgegaan door nog acht die pakket en blob noemen wanneer de vlagbyte van het item zijn
bovenste bit heeft. Controle: bij elke bundel eindigt het laatste item precies waar de vlagbytes beginnen.

### Welke tabel is het level {#which-table-is-the-level}

Een level kan meerdere tabellen met dezelfde naam hebben: één in de `Data` van het basisspel, één in elke update
(`Update/<pack>/Data`) die het level levert of wijzigt, en één in elk pakket met hoge resolutie
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Sommige bevatten bundels. Voor een level dat een
update levert, bevat de tabel in het basisspel alleen chunks en geen bundels, en de tabel in de update is het
level; de eerste tabel die gevonden wordt nemen, leverde niets van het level op.

Het level is dus de tabel met de meeste bundels, waarbij een latere laag wint bij gelijkspel (eerst het basisspel,
dan de updates in naamvolgorde), en de tabellen met dezelfde naam zonder bundels zijn **aanvullingen**: hun
chunks worden bij die van het level opgeteld, want ze bevatten de grootste mips van zijn texturen. Een texturkop
noemt die chunk op +164 (zie [Texturen en materialen](#textures-and-materials)). `levels` toont waar elk level
vandaan komt en hoeveel aanvullingen het heeft.

## Bundelmanifesten {#bundle-manifests}

Het eerste item van een bundel is zijn manifest, ongecomprimeerd opgeslagen. Het is het binaire bundelformaat van
eerdere Frostbite-spellen met een nieuwe magie, `0xD68E799D`: tellingen, SHA-1's, ebx- en res-records (naamoffset en
grootte), restypes, metadata en id's, chunk-GUID's, tekenreeksen. De rest van de items van de bundel zijn de ebx,
de res en de chunks, in die volgorde. Controle: de tellingen kloppen met de items bij elke bundel, en de tekenreeksen
beginnen waar de records eindigen.

Restypes zijn hashes. `0x49B156D4` is MeshSet (elke res van dat type heet `..._mesh`), `0x6BDE20BA` Texture,
`0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` leest dit alles voor één level in een paar seconden: een level heeft tientallen bundels en tienduizenden
ebx-, res- en chunk-items.

## Payloadblokken {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Een compressed size van nul betekent opgeslagen, zolang het decomprimeert tot de ongecomprimeerde grootte.

| Methodewoord | Codec |
|---|---|
| `0x0070`, `0x0071` | geen |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), uit de eigen `oo2core`-DLL van het spel) |
| andere, met gelijke groottes | gekopieerd zoals opgeslagen |
| andere | geweigerd |

Gelezen uit het juiste pakket: elke gesamplede payload decodeert.

## EBX-partities {#ebx-partitions}

EBX bevat alles wat geen ruwe data is. Elke partitie is een RIFF-bestand: `EBXD` (de data, uitgelijnd op 16),
`EFIX` (partitie-GUID, type-GUID's en handtekeningen, instantie-, pointer-, import- en type-infooffsets, imports,
en de offsets van de array, de boxed-value en de tekenreeksen), `EBXX` (de arraytabel: offset, aantal, hash,
vlaggen, elementtype). Een pointerveld is acht bytes: nul is null, een oneven waarde is importnummer `value >> 1`,
al het andere is relatief ten opzichte van het veld.

De **typebibliotheek is niet leesbaar**. Het spel levert die in zijn initiële bestandssysteem, dat versleuteld is,
en dit pakket raakt het niet aan. Types worden herkend aan GUID en handtekening, die elke partitie meedraagt, en de
paar types die de levelexport nodig heeft, zijn uit de data afgeleid.

## MeshSet {#meshset}

Een mesh is een MeshSet-res (de beschrijving) en één chunk per detailniveau (de buffers).

| Deel | Indeling |
|---|---|
| prefix | vier woorden: kopgrootte (176 of 192), grootte van het niveaurecord (176 tot 188), grootte van het sectierecord (368), 0 |
| kop | bounding box; zes i64-niveauoffsets; meshtype op `0x6C` (rigid, skinned, composite); aantal niveaus en secties op `0x9C` |
| niveau | secties op `+0x08`; vijf tekenlijsten op `+0x14` (ondoorzichtig, transparant, decal, alleen diepte, schaduw); indexformaat `+0x54` (`0x21` u16, `0x2E` u32), index- en vertexbytes; chunk-GUID op `+0x74` |
| sectie | materiaalnaam; vertexstap; driehoeken, eerste index, vertexoffset (bytes), vertexaantal op `+0x20`; vertexdeclaratie op `+0x64`: 16 x (gebruik, formaat, offset, stream), 16 streamstappen, tellingen |
| chunk | de vertexbuffer, dan de indexbuffer. De streams van een sectie volgen elkaar op, en indices tellen vanaf de eerste vertex van de sectie |

Posities zijn gebruik 1, stream 0, offset 0, als vier halfwaarden of drie floats. Alleen de ondoorzichtige en de
transparante secties worden getekend. Elke sectie met de naam `..._shadow` staat alleen in de schaduwlijst, dus de
lijsten bepalen het.

Controle: elk mesh van een level waarvan de niveaus in chunks zijn opgeslagen, decodeert, en bijna alle hebben 99% of
meer van hun vertices binnen hun aangegeven box; de rest mist die met afrondingsfouten van halve precisie. Een
gedecodeerde kist meet ongeveer een meter, Y omhoog, met normalen die naar buiten wijzen.

## Plaatsing {#placement}

De inhoudspijplijn verzamelt de statische objecten van elk sub-world in een **statische modelgroep**: een array van
leden, één per mesh, elk met zijn instantietransformaties.

| Type (GUID, handtekening) | Indeling |
|---|---|
| lid `ad13064e…`, `0xF861A878` | 224 bytes: `+88` array van transformaties, `+112` de objectblauwdruk (import), `+160` het meshasset (import) |
| transformatie `101dce06…`, `0x5E6D8C37` | 64 bytes: rechts, omhoog, vooruit, translatie, elk een vec3 opgevuld tot 16 |

De partitie van het meshasset heet als zijn MeshSet-res, dus de partitie-GUID van de import geeft het mesh. Een punt
komt op `x·right + y·up + z·forward + translation`. De transformatie van de groep zelf was in elke gecontroleerde
groep de identiteit, en wordt niet toegepast.

Controle: in een level wordt elk lid van elke groep opgelost naar een mesh; de meeste kopieën hebben een rotatie met
determinant 1 tot op een duizendste, de rest is geschaald of gespiegeld. De type-GUID's en handtekeningen zijn in
andere levels hetzelfde. Een spelupdate die de indeling verandert, verandert de handtekening, en de lezer vindt dan
niets in plaats van verkeerd te lezen.

### Objecten die één voor één zijn geplaatst {#objects-placed-one-by-one}

Wat de pijplijn niet kan groeperen - vernietigbare objecten, containers, puin - wordt geplaatst via **objectverwijzingen**
en **prefabverwijzingen** in de partities van het level:

| Type (GUID, handtekening) | Indeling |
|---|---|
| objectverwijzing `a9a6a6ad…`, `0xC4856BEC` | `+32` de transformatie (zoals hierboven), `+112` de objectblauwdruk (import) |
| prefabverwijzing `117c746e…`, `0xDE3FE9B4` | hetzelfde; de blauwdruk is een prefab, een partitie met verdere verwijzingen |

Prefabs zijn genest; een kopie komt op zijn eigen transformatie maal die van zijn ouder (rijvectoren), tot acht
niveaus diep. Een objectblauwdruk wordt getekend als de meshes die hij importeert, met de vernietigde toestanden
(`dc_...`) weggelaten. Een gegroepeerde prefab wordt aangeduid met zijn `..._nongroupable_autogen`-rest, zodat niets
dubbel wordt getekend.

De doorloop begint alleen bij de werelden en lagen van het level. Een partitie waarvan het eerste instantie een
prefab-blauwdruk is (`134919fc…`, `0x0247807D`) is de definitie van een prefab, en een level bewaart er veel onder
zijn eigen map, geplaatst door zijn werelden op andere manieren dan deze verwijzingen; als zo'n prefab als een wereld
wordt gelezen, zet hij zijn inhoud op zijn lokale coördinaten. Dat stapelt honderden kopieën rond de oorsprong van de
wereld, ver onder de grond. Werelden en lagen hebben `a10ebe0f…`, `0xD3D16C3C` als eerste.

Blauwdrukken die uit het spel zijn geplaatst, worden niet gevolgd: ontwikkel- en testassets (`game/dev/`, `test/`), de
set van de eindcinematic van de ronde (`..._gameend_...`: onder de grond geplaatst) en de controller van de sterfcamera
(`.../deathflow/...`, waarvan de gadgets op de oorsprong van de wereld staan). Ze worden herkend aan hun assetpad, niet
aan hun laag: dezelfde laag die de cinematicset bevat, kan ook de echte muren en daken van het level plaatsen. Na beide
regels ligt in de gecontroleerde levels geen kopie meer dan 10 m onder het terrein, en staan kopieën op het terrein waar
het spel ze toont.

**Detailniveaus die als stand-in dienen.** Het laatste detailniveau van een mesh kan overschakelen naar een
verre-weergave-stand-in met een eigen materiaal: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Een
roosterwerk-toren van tienduizenden driehoeken kan eindigen in een silhouet van een paar honderd, wat het budget zou
kiezen en wat van dichtbij een massieve piek is. Een detailniveau dat zo'n materiaal binnenbrengt, dat het fijnste niveau
niet heeft, wordt nooit gekozen; het grofste niveau van het mesh is het laatste echte.

## Terrein {#terrain}

Bron: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Het terrein is een TerrainStreamingTree-res (type `0x22FE8AC8`) en de chunks die hij noemt.

| Deel | Indeling |
|---|---|
| kop | 34 bytes; het aantal knopen op 25 |
| rastebomen | een typebyte en een u32-lengte elk, tot een typebyte `0xFF`. Type 0 is het hoogteveld: samples per zijde op +5 (265), hoogtebereik op +21 (1.280 m), het terreinvierkant in zijn eerste knoprecord op +77 (8.192 m in het gecontroleerde level). Het bevat bounding boxes van knopen en een 16 x 16 min/max-piramide per knoop, niet de hoogtes |
| streaming-knopen | de quadtree, diepte-eerst: chunkgrootte en GUID; een optionele tweede chunk; een vlagbyte (bit 0: de chunk begint met een hoogtepagina); heeft kinderen. Kinderen in de volgorde (0,0), (1,0), (1,1), (0,1) |
| hoogtepagina | de eerste 265 x 265 u16 van de chunk van een gevlagde knoop, rij voor rij; hoogte = waarde x 1.280 / 65.535 m; kolommen langs x, rijen langs z, vanaf de lage hoek van de knoop; een rand van 4 samples, dus 256 cellen per knoop |

Elke stap is afzonderlijk gecontroleerd:

- De parse van de quadtree van knopen verbruikt de res tot zijn laatste byte, met de aangegeven 529 knopen.
- Naburige knopen delen hun negen randkolommen precies, dus de stap is 256.
- De samples van een kind op elke andere positie zijn precies gelijk aan die van zijn ouder met een rand van 4, en
  wijken 90 tot 700 eenheden af met elke andere rand.
- Het laagste woord in het level decodeert tot de laagste hoogte van de bounding box tot op de centimeter.
- Van de acht manieren waarop het vierkant op de wereld kan liggen, zorgen alleen x langs x en z langs z ervoor dat de
  geplaatste objecten erop liggen: de helft van de bemonsterde kopieën binnen ongeveer 2 m, tegenover een veelvoud
  daarvan voor elke andere manier.

De geplaatste objecten meten het resultaat dan. Het laagste punt van elke kopie, tegen het terrein eronder (bilineair,
uit de fijnste knoop):

| Geplaatst | Mediane afstand | Gesigneerde mediaan |
|---|---|---|
| bomen en struiken | ruim onder een meter | net onder het oppervlak |
| rekwisieten | een meter of twee | op het oppervlak |
| rotsen | ongeveer een meter | ongeveer een meter ingezakt |
| gebouwen | meerdere meters (ze staan op funderingen) | licht ingezakt |

Begroeiing wordt alleen op de grond geplaatst, en nergens anders, wat het scherpste punt van controle maakt: de
oorsprongen liggen mediaan 0,07 m van het oppervlak. Gebouwen spreiden zich breed omdat de categorie muren, vloeren en
bouwpakketonderdelen van meerlaagse en ondergrondse constructies bevat. Het terrein 64 m zijwaarts verschuiven
verlaagt het aandeel kopieën binnen 0,5 m van 29% naar 10%.

`level` tekent het hoogteveld als `ground:terrain`, elk deel ervan uit de fijnste knoop met hoogten daar en niet fijner
dan `--ground-spacing` (standaard 4 m: 3,7 miljoen driehoeken voor het gecontroleerde level, waarvan de fijnste knopen
0,5 m zijn). Stukken van verschillende resolutie komen samen met kleine treden; niets egaliseert ze.

De chunk van een knoop bevat ook de pagina's van de laagmaskers na zijn hoogtepagina, en zijn tweede chunk eindigt met de
kleurkaart van de knoop (zie [Terreinlagen](#terrain-layers)).

## Terreinlagen {#terrain-layers}

Het spel schaduwt het terrein bij een speler door oppervlakmaterialen in tegels te splatten, gestuurd door geschilderde
maskers, met een kleurkaart erbovenop, en door decals (wegen, asfaltvlekken, landingsbaanmarkeringen) erbovenop te
tekenen. De eigen beschrijving van Frostbite van het systeem (Widmark, "Terrain in Battlefield 3", GDC 2012) somt de
rasters van het terrein op als het hoogteveld, shadersplatmaskers, een kleurkaart "used as an overlay on top of shader
splatting", fysicamaterialen, een vernietigingsdieptemasker, een albedokaart voor bounce-licht en extra maskerkanalen; de
tegels van een raster dragen een rand voor de renderalgoritmen. De streaming-boom van de gecontroleerde levels heeft zeven
rasterbomen, getypeerd 0, 1, 2, 4, 5, 7 en 8, waarvan de koppen beginnen met hun tegelgrootte: 265 voor het hoogteveld
(type 0) en type 2, 72 of 66 voor de maskers (type 1), 132 met een rand van 2 voor de kleurkaart (type 4), 260 met een rand
van 2 voor type 5.

**De lijst van lagen.** De `....layergraphs`-res van het terrein somt één item van 32 bytes per laag op, in de volgorde waarin
de maskerrecords ze nummeren (34 items, 34 depot-secties en laagindices 0 tot 33 in één level); de id van elk item eindigt
met zijn sectiesleutel in het shaderblok-depot van de layergraph (`....layergraphs_shaderblockdepot`), waarvan het blok de
kaarten van de laag noemt: één `_cv`-kleurkaart, `_nhs`- en `_ao`-kaarten per oppervlak, plus gedeelde detail- en
ruiskaarten. Veel lagen noemen geen kaarten: het zijn bronnen die de layergraph leest. De kleur van een laag is het
gemiddelde van zijn `_cv`-kaart; de tegelschaal wordt niet gevonden. Het terreinasset eindigt met één item van vijf bytes
per laag (een byte, dan een u32-laagindex of -1).

**De maskers.** Rasterboom 1 is de quadtree van de maskers. Zijn inhoud begint met 59 bytes, de zijde van de pagina op 0:
72 waar de pagina's BC4 zijn (72 x 72, 2.592 bytes), 66 waar ze ongecomprimeerd acht-bit zijn (4.356 bytes). Dan volgt één
groep per knoop, diepte-eerst:

| Deel | Indeling |
|---|---|
| groep | u16; u16 recordaantal; u32 paginaaantal; de records; een nulbyte. Een groep zonder records is in totaal 7 bytes |
| record | 33 bytes: u16-laag, u16-hash, de box van het kwadrant (vier floats), twee vlagbytes, een piramide van 85 bits voor aanwezigheid |

De records van een groep zijn de vier kwadranten van zijn knoop, laag voor laag, met de kwadranten van elke laag in de
volgorde (0, 0), (1, 0), (1, 1), (0, 1). Een record met de tweede vlag gezet dekt zijn kwadrant helemaal en heeft geen
pagina; een zonder die vlag heeft de volgende pagina; een kwadrant zonder record voor een laag die zijn groep noemt, is
van die laag leeg; de eerste vlag is precies dan uit wanneer de laag doorloopt in de eigen groep van het kwadrant, één
niveau lager, wat het daar vervangt. Het aantal pagina's is het aantal records met een pagina.

De pagina's: de pagina's van de eigen groep van een streaming-knoop volgen in zijn chunk, na de hoogtepagina, een
16-bits sectie van 4.358 bytes en een raster van 67 x 67 acht-bit (vanaf het begin van de chunk als die geen hoogtepagina
heeft); zijn tweede chunk bevat de pagina's van de groepen van zijn vier kwadranten één niveau lager, de kwadranten in de
volgorde van de kleurkaart, dan de kleurkaart. Een pagina is de 64 x 64 texels van het kwadrant, rijen langs z en kolommen
langs x, met een rand die van de buren is gekopieerd: 4 texels op een BC4-pagina, 1 op een ongecomprimeerde.

De randen bewijzen de plaatsing zonder oordeel: twee pagina's van één laag naast elkaar moeten elkaars randtexels dragen.
`read_masks` controleert dat voor elk paar dat het plaatst, en weigert een level waar minder dan 99% overeenkomt. Ongeveer
een derde van de gecontroleerde levels wordt gelezen, met hun randen die overeenkomen; een paar hebben geen geschilderde
maskers; de rest wordt geweigerd, bijna allemaal door de controle (hun knoopchunks bevatten meer dan deze indeling kent).
De grond van een geweigerd level krijgt de middelste kleur van zijn oppervlakmaterialen, en de export zegt waarom. De randen
die aan een volledig kwadrant grenzen zijn 255, die aan een leeg kwadrant 0.

De 4.358-byte sectie en het raster van 67 x 67 voor de pagina's worden niet gelezen: hun waarden zitten in een smalle hoge
band, zonder kleine waarden en zonder markering.

**De kleur van de grond.** De layergraph mengt de lagen in een gecompileerde shadergraph van maskers, helling, hoogte en
ruis, en die wordt niet gelezen. `--ground-texture` kleurt de grond met een eigen regel, hier als zodanig vermeld:

- lagen waarvan de kleurkaart naar afstand is genoemd, zijn de stand-ins van het verre beeld en worden weggelaten;
- de getextureerde lagen die negen tiende of meer van het terrein bedekken, vormen de basis. Hun maskers zijn bijna overal vol,
  dus waar elk ligt, is de keuze van de shader, niet die van hen: die genoemd naar rots of klif kleuren hellingen steiler dan
  40 graden, die genoemd naar grind kleuren vlak terrein (de andere basislagen als er geen is), en worden tussen 20 en 40 graden
  gemengd door de helling van het hoogteveld (genomen elke 4 m en bilineair uitgespreid over de ingebakken texels: herhaald in
  blokken van 4 m tekende het de rotskleur als harde vlekken);
- elke andere getextureerde laag wordt over de basis gelegd door zijn eigen masker, in laagvolgorde;
- de kleurkaart wordt over het resultaat gelegd zoals de engine het doet, twee keer de kleur van de grond maal de kaart, zodat
  middengrijs er niets aan verandert; waar de kleurkaart geen texels heeft, krijgt de grond de mediane helderheid van de kaart,
  in grijs.

Gecontroleerd tegen de mediane grondkleur van gameplay-frames van drie levels (chroma als rood en blauw ten opzichte van groen):
het ingebakken speelgebied komt op 1,00 / 0,69 tegenover de frames van 1,19 / 0,78 in één, waarvan de graslagen groen zijn
waar de frames droog gras tonen; 1,19 / 0,82 tegenover 1,01 / 1,04 in een andere, waarvan de kleurkaart zelf warm is (1,13 /
0,88); en 1,05 / 0,91 tegenover 0,93 / 0,92 in een derde zonder kleurkaart. De frames zijn belicht en gegradeerd, dus dit meet
de tint, niet de helderheid.

**De kleurkaart.** De tweede chunk van een knoop bevat, na de maskerpagina's van de groepen van zijn kwadranten, vier
BC7-pagina's van 132 x 132 (elk 17.424 bytes), één per kwadrant van de knoop, in de volgorde (lage x, hoge z), (hoge x,
hoge z), (hoge x, lage z), (lage x, lage z). De maskerboom zegt hoeveel bytes de maskerpagina's innemen, dus de kleurkaart
wordt gevonden op aantal en niet op het einde van de chunk: in één level dragen de grovere knopen na de kleurkaart nog vier
van zulke pagina's, een ander raster in één effen kleur, en het lezen van de laatste vier pagina's van de chunk verloor de
kleurkaart over negen tiende van het terrein. Zonder die telling werd de kleurkaart ook gemist in levels met ongecomprimeerde
maskerpagina's, waarvan de pagina's geen geheel aantal BC4-pagina's vormen; de kleurkaart van één level ging van 0,4 naar 0,94
van zijn terrein. De volgorde is gepast: tegen de randen van het hoogteveld van elk kwadrant past elke pagina van de knopen met
kenmerken op één kwadrant, ongedraaid, met 0,3 tot 0,54 waar de volgende beste plaatsing onder 0,2 ligt. Zo aaneengezet, sluiten
de pagina's van een level zonder naad aan op de wegen, het water en de bebouwde gebieden van het testlevel, op 0,5 m per texel
in het speelgebied. Waar de lagen het werk doen, is de kleurkaart bijna neutraal (mediaan 110, 107, 104); elders kan ze volle
kleur dragen. Een level waarvan de tweede chunks alleen ongecomprimeerde maskerpagina's bevatten, heeft geen kleurkaart
gelezen. Een eerdere ronde van deze lezer noemde die pagina's niet geografisch: ze werden tegen de achtergrondkaart gehouden,
die een ander landschap kan zijn, en elke pagina werd op de hele knoop geplaatst in plaats van op een kwadrant.

**De albedo van het bounce-licht** is gezocht en niet gevonden: de chunks van de wortel- en de eerste-niveau-knopen zijn hele
maskerpagina's, en de payload van type 5 is niet gevonden.

**Gaten.** Het terreinasset van een level (res-type `0x1CA38E06`) noemt drie shaders: een standaard oppervlakshader, een
gatenoppervlakshader en een standaard brongshader. Welke laag de gatenshader leest, is niet gevonden, dus het hoogteveld wordt
niet uitgesneden. In een level kan het navigatiemesh op rotsmeshes tientallen meters onder het hoogteveld lopen, waar het spel
het weg had moeten snijden. Gezocht en niet gevonden daar: het masker van een laag, het raster van 67 x 67, een gereserveerde
hoogte (geen hoogtepagina van een level bevat 0 of 65.535) en een knoopvlag (elke knoop onder de wortel heeft vlag 1). Rasterbomen
7 en 8 zijn wat overblijft. Beide zijn run-length-gecodeerd: een byte die gelijk is aan de vorige wordt gevolgd door een aantal
extra kopieën (`ff ff 84` is 134 bytes van 255). Boom 7 (tegel 256, een volledige quadtree van vijf niveaus, vier bits per
sample) decodeert tot bytepaaren met waarden 0 tot 3; boom 8 (tegel 265) tot bytes die vooral 255 zijn, met de andere waarden in
regelmatige reeksen. Geen van beide tegels is nog geplaatst, dus van geen van beide is bekend dat ze de gaten bevatten.

**Decals** worden gelezen en ingebakken; zie [Terreindecals](#terrain-decals).

## Terreindecals {#terrain-decals}

Bron: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Wegen, landingsbanen, betonnen platforms, geschilderde lijnen en letters, bandensporen: de `TerrainDecals`-res (type
`0x15E1F32E`) bevat ze als platte geometrie die het spel over het terrein legt.

| Deel | Indeling |
|---|---|
| kop | op +16 een aantal slots n, dan n slots van 16 bytes, dan het aantal records |
| records | één per tekenbatch, achter elkaar, van wisselende lengte: 156 bytes vaste velden - eerste vertex op +32, aantal driehoeken op +36, texturtegeling in meter op +44 - dan de vertexbytes van de batch (offset, grootte), dan een staart die zijn texturen noemt bij de partitie-GUID's van hun assets |
| vertices | 32 bytes: x, z (f32), 8 gepakte bytes, u, v (f32), r, g, b, a (f16); elke batch is een gewone driehoekslijst |
| indices | u32, vanaf 0 in elke batch; niet nodig |

Controles:

- de vertexbereiken van de records volgen elkaar zonder gat en dekken alle vertices precies, en de eerste vertex × 32 van elk
  record is zijn offset;
- zo gelezen zijn de driehoeken compacte decals (letters, strepen lijn, vlekken); één vertex verder gelezen, zijn het splinters
  over de kaart;
- bijna alle batches noemen texturen in hun staart: een kleurkaart (`_cv`) met een dekkingskaart (`_op`, rood kanaal), of bij
  markeringen een kanaalmasker (`_rgb`).

Na de texture-GUID's draagt de staart de materiaalparameters van de batch, gecodeerd zoals die van een shaderblok (zie Tints
hieronder). De verfkleur van een markering, een bandenspoor of een lijn is de float3 met hash `607e`: een zanderige 0,64,
0,56, 0,48 voor bandensporen in zand, bijna zwart voor teer. Dekkingskaarten zijn meestal formaat 62, één kanaal van 8 bytes per
blok, gelezen als BC4.

Een batch koppelt zijn textuur op één van twee manieren: op wereldpositie (u = x, v = z, de textuur herhaalt zich elke
tegelingsmeter: asfalt, beton, grind) of 0 tot 1 over het decal (een lijn, een letter, een bandenspoor). Records worden getekend
in bestandsvolgorde.

**De bake.** `level --ground-texture M` schildert, onder de omvang van de decals en tegels van hoogstens 4.096 pixels, de
achtergrondkleurkaart (bilineair) en daarna elke batch erover, naar zijn dekking × de vertexalfa. De kleur van de vertices wordt
niet gebruikt: sommige batches hebben zuiver groene of blauwe vertices, wat de markeringen van een level in die kleuren kleurde.
De driehoeken van het hoogteveld daar worden de delen `ground:terrain x<x> z<z>` die de tegel dragen. Elke batch tekent met:

| Batchnamen | Getekend als |
|---|---|
| een kleurkaart (`_cv`) | de kaart, door zijn dekkingskaart |
| een vermenigvuldigkaart (`_mult`) en een dekkingskaart | de verf (wit waar het materiaal er geen noemt) maal de vermenigvuldigkaart, door de dekkingskaart: de versleten middenlijn, randlijnen en drempelbalken van een landingsbaan |
| een kanaalmasker (`_rgb`) | de verf, anders wit voor lijnen en letters, donker voor omtrekken, een zwakke verduistering voor slijtage, bandensporen, vlekken, plassen en natheid, door het masker |
| alleen een dekkingskaart, met een verf | de verf door de dekkingskaart: bandensporen |

Een wegvariatiemasker is geen verf, maar varieert het oppervlak eronder, honderden meters breed, en wordt niet getekend, wat de
verf ook is: wit geschilderd legde het twee bleke rechthoeken van 150 tot 250 m lang op de hellingen van een level. De `_mult`-kaart
wordt opgevat als de eigen slijtage van de verf, niet als een verduistering van de grond eronder: ze is bijna wit, en de vorm van de
lijn zit in de dekkingskaart.

Bijna elke batch wordt getekend, in een paar tegels van 0,5 m per pixel; de export groeit met een paar MB en duurt een paar seconden
langer. Van bovenaf gezien liggen de platforms, taxibanen en het wegennet onder de hekken en gebouwen van de complexen en leiden ze
naar hun poorten.

Als geometrie van hun eigen zouden decals alfa-mengen nodig hebben, wat de schrijver niet meeneemt, en een verschuiving boven een
terrein zou ermee vechten; bakken houdt ze in de eigen kleur van de grond.

## Texturen en materialen {#textures-and-materials}

Bron: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Een Texture-res (type `0x6BDE20BA`) is een kop van 180 bytes: type en pixelformaat op +8, breedte en hoogte op +22, aantal mips
op +30, de chunk-GUID op +40, vijftien mipgroottes op +56. De chunk is de mipketen, het grootste eerst. Sommige chunks missen hun
grootste mips, die in een pakket met hoge resolutie staan, en de lengte van de chunk zegt bij welke mip hij begint. De chunk van dat
pakket wordt genoemd op +164; hij wordt uit de aanvullingen van het level gelezen wanneer een mip die de hoofdchunk mist nodig is,
en zijn lengte plus die van de hoofdchunk is de hele keten.

| Formaat | Gedecodeerd als | Bewijs |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineair) | een kleurvel van een plastic tank decodeert zo; als BC3 zijn dezelfde bytes ruis |
| 61, 60 | BC3 | een kistvel decodeert schoon als BC3, niet als BC1 of BC7 |
| 57, 56, 55 | BC1 | een halve byte per pixel |

De meshasset noemt geen textuur. De koppeling staat in de **shaderblok-depots** van het level (restype `0x73312045`, één per
sub-world), gesleuteld op de acht bytes op +0x130 van het record van een mesh-sectie:

| Deel | Indeling |
|---|---|
| tabel, bij 16 | (sectiesleutel u64, descriptoroffset u64), tot een offset buiten de res valt |
| descriptor | (blokoffset u64, hash u64, bloktgrootte u64) |
| blok | de shaderparameters van de sectie; elke textuur is een record van 49 bytes: een byte, 16 bytes, de partitie-GUID van het textuurasset, zijn instantie-GUID |

De sectiesleutel van de kist staat één keer in elk van de tien depots van de sub-worlds die hem plaatsen, en zijn blok noemt
`t_mil_crate_03_cs` en `_nmt` tussen de gedeelde detailkaarten. Een blok noemt elke textuur die de shader bemonstert, en welke de
kleurkaart is, wordt niet gezegd, dus wordt hij gekozen: een sRGB 2D-textuur waarvan de naam de meeste woorden van de materiaalnaam
bevat (`M_ConcreteWall_01`: concrete, wall), dan die van het mesh, dan een die geen detail-, decal- (`t_de_...`) of schadekaart is, dan
de die het minst door blokken wordt gebruikt. Het blok van een wegbord noemt zijn paneel `t_com_highwaysignage_01_cs` en een decalvel
`t_de_com_highwaysignage_01_ca` met een schild op zijn zij; beide passen op de woorden, en zonder de decalregel won het vel op gebruik en
toonde het bord het schild een kwart gedraaid, door elke texturcoördinatenset die de sectie heeft. Signed distance fields (`..._sdf`),
paletten en kanaalmaskers (`_rgb`) worden nooit gekozen, wat ze ook gemeen hebben (`_rgba`-kaarten wel: de meeste zijn kleur met een alfa,
en ze weglaten verwisselde de eigen kaarten van een hoogspanningsmast en een trap voor onverwante); een vegetatieatlas van een achtergrond
`..._atlas_a_sdf`, als kleur getekend, toonde zwarte en witte sterren voor bomen, een palet van een achtergrondgebouw een confetti van
stalen voor muren, en glasscherven getekend via hun kanaalmasker kwamen cyaan uit. Een sectie waarvan de enige kandidaten gedeelde
detailkaarten zijn, blijft vlak gekleurd.

**Paletten.** De gebouwen van een achtergrond nemen hun kleuren uit een palet van 256 x 256 texels van 16 x 16 stalen: elke vertex
draagt vier bytes (gebruik `0x1E`) waarvan de eerste twee zeggen waar in het palet zijn kleur ligt, x en y van 0 tot 255. `level` tekent
zo'n sectie met het palet als textuur, elke vertex in het midden van zijn staal. Zo getekend, komen de achtergrondblokken van een level
uit als pasteliken muren, terracotta en donkere ramen waar ze wit waren.

**Overlays.** Grote objecten leggen een trimblad via hun eerste texturcoördinaten, en leggen er een overlay overheen via de tweede,
die binnen 0 tot 1 liggen: een uitvouwing van het hele object. De overlay (`..._overlay_cs`, met zijn masker `..._overlay_a`) draagt wat
het object van veraf laat zien, de rode banden en roest van een olietank; getekend met alleen het trimblad, kwamen de tanks van één
level uit als grijze panelen. Een sectie waarvan het blok een overlay met zijn masker noemt, en waarvan de tweede coördinaten zo'n
uitvouwing zijn, wordt getekend met de overlay erdoorheen (36 secties in dat level).

**Tints.** Veel kleurkaarten zijn grijs (hun kanaalgemiddelden liggen binnen 6% van elkaar): de shader schildert ze met kleuren uit de
parameters van het blok. Na zijn texturitems (elk 49 bytes) somt een blok zijn parameters op, elk met een typetag (`f11af825` een float3,
`a5e1f2de` een float4, `c1b1a014` een float, `4a4fc3a1` een geheel getal), de vlagbytes `01 80` voor één waarde, een tweebyte-hash van de
parameternaam, een u32-aantal, de waarde en een id van acht bytes. De namen worden niet opgeslagen. Zeven float3-naamhashes werken als
tints: in één level bevatten er drie een kleur in ongeveer 1 blok van 6 waarvan de kaart grijs is en bijna nooit waar de kaart zijn eigen
kleur heeft, en de andere bevatten de kleuren waarin een grijze kaart wordt geschilderd waar de materiaalnaam dat zegt (de `..._blue`-trim
van een brug: 0,047, 0,098, 0,171 tegenover een neutrale 0,5). Een familie kan meerdere waarden bevatten, één per kanaal van een masker,
de meeste neutraal, en een waarde met een kanaal dat bijna niets is (puur groen op bakstenen gevels) kiest een kanaal van een masker in
plaats van te verven. `level` vermenigvuldigt een grijze kleurkaart, in lineair licht, met de eerste waarde van elke familie die niet
neutraal is en niet zo'n kanaalkiezer, ten opzichte van de neutrale; het resultaat wordt als een eigen textuur bewaard; een kaart met
kleur blijft zoals ze is. De regel is die van de exporter zelf: welk kanaal van een masker welke tint krijgt, wordt niet gelezen. In één
level bracht het het aandeel structuurdriehoeken dat bijna wit getekend werd van 19,4% naar 3,9%.

**Objectvariaties.** Eén mesh wordt in meerdere uiterlijken geplaatst: een magazijnmuur met een rode of blauwe streep en een ander nummer
erop geschilderd, een container in groen of grijs. Elke geplaatste kopie noemt zijn uiterlijk:

| Waar | Veld |
|---|---|
| lid van een statische modelgroep | +32: een array van één pointer per kopie, naar een objectvariatie of null |
| objectverwijzing | +120: een pointer naar een objectvariatie of null |
| objectvariatie (partitie `ov_...`, type `235f2a9c...`) | zijn eerste instantie +32: de u32-naamhash van de variatie |

Het uiterlijk van een sectie in een variatie is het shaderblok dat gesleuteld is op de eigen sleutel van de sectie met de hash van de
variatie opgeteld bij zijn eerste vier bytes, als little-endian u32 (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); een sectie
zonder blok onder die sleutel ziet er in elke variatie hetzelfde uit. De databases met meshvariaties van het level (`meshvariationdb_win32`)
tonen per mesh en variatiehash welke materialen elke variatie raakt, maar niet de sleutels: de regel is uit de sleutels zelf gevonden en geldt
voor elke sectie met varianten die is gecontroleerd (de vier variaties van één muur, elk met drie van zijn secties). Het blok van een variatie
brengt zijn eigen texturen mee, net zo goed als zijn tints: het geschilderde nummer op de muur is een letterblad dat het blok van de variatie
noemt. Een groot deel van de gegroepeerde kopieën wordt in een variatie geplaatst.

Een blok wordt één keer gebakken voor elke set inhoud, en het depotitem voor een sleutel draagt een hash daarvan (de tweede u64 van het
item). Waar een sectie geen blok onder de sleutel van zijn variatie heeft, bereikt de variatie hem toch via een *tweeling*: een andere sectie
waarvan het standaardblok dezelfde inhoud heeft en wel zo'n blok heeft. Zonder tweelingen kan een muur waarvan de lengtes één standaardblok delen,
in twee kleuren uitkomen. Een sectie zonder eigen variant neemt de variant die de meeste van zijn tweelingen hebben.

**Vernietigbare meshes.** Een mesh dat een match kan neerhalen, heeft een vernietigingsasset van zijn eigen naam ernaast
(`.../br_x.destruction` voor `.../br_x_mesh`): de breekbare gebouwen en muren (`br_`) en veel rekwisieten. `level` houdt hun oppervlakken
in eigen delen, genoemd met ` (destructible)`, waarvan de glTF-nodes `{"destructible": true}` dragen. Hun vernietigde toestanden zijn de
meshes `dc_..._part<N>_mesh` ernaast, elk gecentreerd op zijn eigen oorsprong; waar een stuk zit, staat in het vernietigingsasset, dat niet
wordt gelezen, dus de vernietigde toestanden worden niet geëxporteerd.

**Weggelaten.** Secties van placeholder-blokkeermaterialen (`M_Whitebox`: een paar grote ongetextureerde driehoeken die sommige gebouwen naast
hun oppervlakken houden, die uit een level staken als witte vinnen), meshes die voor cinematics zijn gemaakt (een helikopter die geplaatst is
waar zijn scène begint) en verlichtingshulpmiddelen (vlakken die licht blokkeren, nooit getekend). De gegenereerde achtergrondgebouwen van een
level (`..._generated_blueprints_..._mesh`) worden getekend, maar hun muurmaterialen noemen alleen ruiskaarten en hun vertices dragen geen kleur,
dus ze blijven kaal. Bijna elke getekende sectie krijgt een kleurkaart.

**Letterbladen.** Een geschilderd nummer op een muur, of een billboardprint van een kraan, is een eigen sectie waarvan de kleurkaart een blad
is (`_ca`): de alfa van een letter over effen verf, of een print. Zijn eerste texturcoördinaten tegelen het pleisterwerk van de muur over het paneel
(u -0,2 tot 1,7 op één muur), wat het blad bijna twee keer tekent; de vierde set (`0x24`, anders de derde, `0x23`) legt het precies één keer
erop (u -1 tot 0, v 1 tot 2, een paar duizendsten over in de grovere detailniveaus). Waar de eerste set één exemplaar van de afbeelding laat en de
vierde of derde er binnen één ligt, wordt het blad erdoor getekend, naar 0 tot 1 verplaatst. Een blad met alfa wordt 1 cm voor het oppervlak
getekend waarop het geschilderd is, dat onder het blad wordt getekend in de andere kleurkaart van het blok via de eerste set: zonder dat lieten de
lege texels van het blad de binnenkant van de muur zien. De tweede set is de uitvouwing van een object voor zijn overlay en wordt hier niet gebruikt.

**Uitknipkaarten.** Het vierde kanaal van de kleurkaart betekent iets anders naargelang de naam van de kaart. In `_cs`, verreweg het meest
voorkomend (893 van de gekozen kaarten van één level), is het gladheid: 1% van de alfa van een mediane kaart ligt binnen 0,1 van 0 of 1. In
`_cu` (bladeren, gras) en `_ca` (kleur en alfa) is het ondoorzichtigheid: 90% en 87%. Een kleurkaart genoemd `..._cu` of `..._ca` waarvan de alfa
voor ten minste 75% dicht bij 0 of 1 ligt, ten minste 1% onder 0,5 en ten minste 5% boven 0,5, wordt met zijn alfa geschreven, als PNG, en zijn
materiaal als glTF `alphaMode` MASK, `alphaCutoff` 0,5, dubbelzijdig; bladkaarten tonen dan bladeren, niet hun zwarte hoeken. De bladkaart van één
boom heeft helemaal geen alfa (4 van 255 op zijn hoogst): zijn takken worden door geometrie uitgeknipt, en met alleen de eerste twee voorwaarden
was de hele kroon weggesneden.

Texturcoördinaten zijn vertexgebruik `0x21`, twee halfwaarden (formaat 6) of twee floats (formaat 2). Secties dragen tot drie extra sets
(`0x22` tot `0x24`) voor decal- en detaillagen. De coördinaten tegelen: de geribbelde zijkant van een container loopt van -1,6 tot 1,8, de tegels
van de terreinachtergrond liggen geheel buiten 0..1, en in één level valt 23% van de getextureerde driehoeken buiten 0..1. Ze worden geschreven
zoals ze zijn, met een herhalende sampler; de 3DHeat-viewer wikkelt elke herhalende textuur binnen zijn atlas. Een renderer die ze in plaats daarvan
afknipt, smeert de ribben uit tot twee keer hun breedte, verandert een betonnen vloer in strepen langs één as, en geeft de balken van een toren de
randkleur van hun textuur; voor zo'n renderer knipt `--clamped-uvs` elke driehoek langs de lijnen waar zijn textuur zich herhaalt, en verplaatst
elk stuk naar 0..1 (zie [Uitvoerformaat](output-format.md)). Daarna valt 0,03% van de getextureerde driehoeken, waarover een textuur zich meer dan
16 keer herhaalt, buiten, en een driehoek die door het knippen in meer dan 4 stukken zou vallen, wordt in plaats daarvan in de gemiddelde kleur van
zijn textuur getekend: schors herhaalt zich langs elke tak, en geknipt steeg het aantal driehoeken van de bomen van een level van 6,4 naar 24 miljoen.

Het hoogteveld heeft geen eigen kleurkaart die gelezen kan worden. Waar een van de kaarten van de terreinachtergrond het bedekt, wordt het daaruit
gekleurd: de texturcoördinaten van de achtergrond zijn een lineaire functie van wereld-x en -z (99% van zijn vertices binnen 0,001 ervan; de kaart
bedekt een vierkant van 65.536 m, een kwartslag gedraaid), en dezelfde functie geeft die van het hoogteveld. Het level levert de mips van die kaart
vanaf 2.048 px naar beneden, dus het hoogteveld krijgt 32 m per pixel. Zijn donkere rots ligt op het steile terrein: de correlatie van donkerte met
helling is 0,48, en op zijn hoogst 0,34 voor de zeven andere oriëntaties.

De achtergrond van een ander level bestaat uit acht nabije en acht verre tegels rond het speelgebied, elk met zijn eigen textuur die zich over de tegel
herhaalt, en geen daarvan bereikt het hoogteveld. Elke achtergrondtextuur wordt op zich gepast, en wanneer geen ervan het hoogteveld bedekt, neemt het de
gemiddelde kleur die de achtergrond laat zien binnen een kilometer van het terreinvierkant, waarover `--ground-texture` de decals bakt. Een
achtergrondmateriaal is er een waarvan de naam `TerrainBackdrop` bevat, of `BD_` en `Terrain` (`M_BD_<site>_Terrain..._Near`); of een achtergrondmesh
(`bd_..._terrain<site>_04_far_mesh`) draagt een gewoon terreinmateriaal (`M_<region>_Terrain<site>_04_Far`), wat de eerste twee regels in één level
misten en zo het terrein kleurden naar zijn oppervlakken.

Waar geen achtergrondkaart het hoogteveld bedekt, krijgt het echter de middelste kleur van de eigen oppervlakken van het terrein vóór het gemiddelde van
de achtergrond: de `_cv`-kleurkaarten die de shaderblokken van de layergraph noemen (27 in één level: zanden, grinden, gronden, gras, gebarsten beton),
elk gemiddeld, dan de mediaan van elk kanaal, zonder het standaardoppervlak van de engine. Een achtergrond kan een ander landschap zijn: in één level
kleurde zijn gemiddelde (95, 99, 80 in sRGB) de grond van het speelgebied een grijs dat het spel niet toont. Met `--ground-texture` wordt die kleur
vermenigvuldigd met twee keer de kleurkaart, wat middengrijs laat zoals het is, en met de decals erover gebakken, over zowel de omvang van de decals als
die van de kleurkaart.

Tegen het spel: de mediane grondkleur van het ingebakken speelgebied van elk level en van gameplay-frames (rijen 55 tot 72% van het beeld naast de HUD, elk
24 frames; sRGB; de frames zijn belicht en gegradeerd, dus de verhoudingen r/g en b/g zijn de eerlijke vergelijking):

| Level | Frames | Gemiddelde van de achtergrond | Nu |
|---|---|---|---|
| eerste | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| tweede | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| derde | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

De eerste is rechtgezet; de andere twee lagen daarvoor al dichter bij in tint. Eén kleur voor een heel level kan nergens helemaal kloppen; de
maskers wel.

## Navigatiemesh {#navigation-mesh}

Bron: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Een level levert één partitie per agent, `<level>/dbt/<level>_navmesh_layer_<n>`: in één level is laag 0 de soldaat (1,8 m hoog, 0,18 m stap, 0,4 m straal) en
zijn twee andere voertuigen (3,5 en 10 m hoog). Elke partitie bevat twee arrays:

| Array | Element |
|---|---|
| tegels | 28 bytes: u32 0, u32 hash, u32 0, u32 chunk-index, u16 tegel-x, u16 tegel-z, u32 offset, u32 grootte |
| chunks | 20 bytes: de GUID van de chunk, u32 grootte |

Een tegel is `size` bytes op `offset` in chunk `chunk index`, little-endian, en is ingedeeld zoals die van Detour (Recast Navigation), achter een
langere kop:

| Offset | Inhoud |
|---|---|
| 0 | `VAND`, versie 7 |
| 24 | tellingen: polygonen, vertices, links, detailmeshes, detailvertices, detaildriehoeken, bounding-volume-knopen, off-mesh-links, het eerste off-mesh-polygoon |
| 188 | agenthoogte, stap, straal |
| 200 | de bounding box van de tegel, zes floats |
| 232 | vertices: x, y, z floats, wereldcoördinaten |
| volgende 8-bytegrens | polygonen, 32 bytes: u32, zes u16 vertex-indices, zes u16 buren, u16 vlaggen, het vertexaantal op +30, op +31 het gebied (onderste zes bits) en de soort (bovenste twee) |
| daarna, samengepakt | links (16 bytes), detailmeshes (12: eerste detailvertex u32, eerste detaildriehoek u32, vertex- en driehoeksaantal u8), detailvertices (drie floats), detaildriehoeken (drie indices en vlaggen), bounding-volume-knopen (16), off-mesh-links (80) |

In elke tegel van de gecontroleerde levels tellen deze op tot de grootte van de tegel tot op de byte, en de detailmeshes nummeren de polygonen
vóór het eerste off-mesh-polygoon.

Een polygoon is vlak tussen zijn hoeken; zijn **detailmesh** bevat de echte hoogte van het oppervlak over oneffenheden, rotsen en treden, en dat
is wat getekend wordt. Een detaildriehoeksindex onder het aantal hoeken van het polygoon is die hoek, anders detailvertex `first + index - corners`.
Het polygoon zonder detailmesh waaieren zet veel meer driehoeken onder het terrein en maakt lange splinters; met de detailmeshes is er geen langer dan
de diagonaal van een tegel van 16 m plus de stap omhoog langs een helling.

Soort 0 is grond, soort 2 kleine steile vlekken (ongeveer 45 graden, elk een vierkante meter), soort 1 een link tussen oppervlakken: zijn hoeken
overspannen 125 m of meer hoogte en liggen buiten de tegel, sommige op de oorsprong. Links worden weggelaten; de rest wordt getekend door zijn
detailmeshes, of waaierend in een tegel zonder één.

Controles: de grootten van de chunks tellen precies op tot die van de tegels; elke oppervlakvertex ligt binnen de box van zijn tegel, op ongeveer een meter
na; bijna alle driehoeken wijzen omhoog. Een tegel die faalt, wordt geweigerd en geteld, en in dat level faalt er geen.

Wat het navigatiemesh van de soldaat bedekt, van bovenaf gezien in het testlevel: de grond, vloeren, trappen en sommige daken, en niet de toppen van vrachtcontainers.
Het is de kaart van de AI van waar een soldaat kan staan, het dichtst dat de bestanden komen bij waar spelers staan.

## Niet geïmplementeerd {#not-implemented}

- De layergraph van het terrein, die zijn oppervlaklagen mengt (zie [Terreinlagen](#terrain-layers)): de kleur van de grond volgt een eigen regel van
  deze lezer, uit de maskers van de lagen en de helling van het hoogteveld, en levels waarvan de maskerpagina's niet op elkaar passen, krijgen één kleur.
- Kleurparameters van decalmaterialen: markeringen via kanaalmaskers worden in een neutrale kleur geschilderd.
- Objectblauwdrukken die geen meshes zijn (spellogica, effecten, geluiden).
- Vernietigde toestanden van vernietigbare meshes: hun plaatsen staan in het vernietigingsasset, dat niet wordt gelezen.
- De links van het navigatiemesh (sprongen, ladders, overstappen) en zijn voertuiglagen.
- Meshniveaus die inline in de res zijn opgeslagen (10 meshes in een level, gadgets), en de botten en delen van skinned en composite meshes, en normalen (door de schrijver berekend).
- Normaal-, ruwheids- en andere kaarten; alfa anders dan een uitknipkaart (transparant glas en decals worden ondoorzichtig getekend).
- Terreingaten: een gatenshader is genoemd, maar wat hij leest is niet gevonden (zie [Terreinlagen](#terrain-layers)), dus het hoogteveld wordt niet uitgesneden waar het begaanbare grond onder loopt.
- Welke tint bij welk kanaal van het masker van een materiaal hoort: een grijze kleurkaart neemt de eerste tint die niet neutraal is (zie [Texturen en materialen](#textures-and-materials)).
- Effecten (`fx/`-paden) en de kabelmeshes, waarvan de bounding boxes tientallen kilometers lang zijn; ze worden weggelaten en in de samenvatting geteld.
- De XOR-verduisterde tabelvorm.
