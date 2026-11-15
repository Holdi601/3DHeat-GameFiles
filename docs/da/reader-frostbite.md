---
title: "Frostbite"
nav_order: 5
lang: "da"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, bundles, meshes og baner {#frostbite-toc-cas-bundles-meshes-and-levels}

**Læser en Battlefield 6-bane ned til dens terræn, dens placerede meshes og deres farvekort, og skriver den som en `.glb`.** Frostbite-spil (Battlefield, Need for Speed, Dead Space) gemmer deres indhold i `.cas`-blobs, beskrevet af `.toc`-indholdsfortegnelser. En banes tabel siger hvilke bundles banen indlæser, bundlerne navngiver hvert asset, og assets'ene siger hvilket mesh der står hvor.

Kilder:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabeller, pakker, payloads),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bundles og deres manifester),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX-partitioner),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(højdefelt),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(teksturer og materialer),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(placering og eksport).
Kommandoer: `identify`, `levels`, `level` (se [Kommandoer](commands.md#levels-and-level-frostbite)).

Intet her er dokumenteret af spillet. Hver layout nedenfor er læst ud af filerne og derefter holdt op mod alle filerne, og hvert afsnit siger hvad kontrollen var. Hvor Frosty-modding-værktøjerne beskriver ældre versioner af en struktur, følger feltnavnene deres; der er ikke taget kode fra dem (se [Regler og licenser](rules-and-licences.md)).

## Headeren der ser krypteret ud og ikke er det {#the-header-that-looks-encrypted-and-is-not}

| Magi (u32, little-endian) | Betydning | Håndteret |
|---|---|---|
| `0x00CED100` | plain: træet begynder med det samme | læses |
| `0x01CED100` | signed: en 556 byte lang signatur, derefter træet **i klartekst** | læses |
| `0x03CED100` | XOR-obfuskeret, med nøglen i filens egen header | genkendt og afvist |

Den signerede form er det nuværende Battlefield leverer. De højentropi-bytes efter magien er en signatur, ikke chiffertekst.

## DbObject-træet {#the-dbobject-tree}

En rekursiv struktur. Hvert felt er en typebyte (de nederste fem bits er typen, bit 7 er "anonym"), et valgfrit navn og en værdi. Containere bærer deres længde som et variabelt heltal og slutter med en nulbyte. `parse_toc` kontrollerer hver containers længde, så en fil der parser, er forstået. `layout.toc` er i denne form.

## Installationspakker {#installation-packages}

Hver placering navngiver den **installationspakke** dens blob hører til. Hver pakke nummererer sine blobs fra `cas_01`, så blobnummeret alene er tvetydigt så snart mere end én pakke er installeret, hvilket altid er tilfældet.

- `layout.toc` lister pakkerne under `installManifest.installChunks`, hver med en `persistentIndex` og en `installBundle` som `Win32/installation/<package>`.
- Pakkens blobs ligger i den mappe, under `Data` for basisspillet eller under `Update/<pack>/Data` for det der kom senere.
- En placeringspost bærer den fulde 32-bit `persistentIndex`: den lave halvdel af dens første ord holder den høje halvdel, den høje halvdel af dets andet ord den lave halvdel; den lave halvdel af det andet ord er blobnummeret.

Kontrol: hver placering i hver binær tabel i en installation løses til en erklæret pakke og ligger inden for den blob den navngiver. En tidligere version tog den første `cas_NN.cas` med det rigtige nummer. En tredjedel af payloads den læste så ud som højentropi og blev taget for kryptering. De var de rigtige forskydninger i den forkerte fil. Intet fundet er krypteret.

## Banetabellen {#the-level-table}

En banes tabel (`levels/<level>/<level>.toc`) er en sektionstabel: femten big-endian header-ord, derefter sektioner lagt ende til ende, hvis forskydninger både er angivet og kan udledes af to tal.

| Sektion | Indhold |
|---|---|
| bundles | en hash-tabel (et ord hver), derefter en 16-byte post pr. bundle: nøgle, `0x40000000` \| størrelse, 0, forskydning |
| chunk-hash-tabel | et ord pr. chunk |
| chunks | 16-byte id (chunkens GUID **byte-vendt**), derefter et ord: `0x80000000` \| 4 x indekset for dens placering |
| placeringer | fire big-endian ord: pakke (delt), blob, forskydning, størrelse |

Chunk-id'erne og placeringerne står i **forskellige rækkefølger**. Læses de i filrækkefølge, parrer man hver chunk med en anden chunks bytes, og de dekoder perfekt (mest som lyd), og de ser derfor ikke forkerte ud før et mesh kommer ud som støj. Kontrol: i en bane er indeksordene en permutation af 0 til chunk-antallet minus én.

Bundlerne ligger inline efter sektionstabellen. Hver er ni big-endian header-ord, derefter sine poster: otte bytes forskydning og størrelse, og foran dem yderligere otte der navngiver pakke og blob, når postens flag-byte har sin øverste bit sat. Kontrol: på hver bundle slutter den sidste post præcis hvor flag-bytes begynder.

### Which table is the level {#which-table-is-the-level}

Et niveau kan have flere tabeller med samme navn: én i basisspillets `Data`, én i hver opdatering (`Update/<pack>/Data`) der leverer eller ændrer det, og én i hver pakke med høj opløsning (`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Kun nogle af dem har bundles. For en bane en opdatering leverer, har tabellen i basisspillet kun chunks og ingen bundles, og tabellen i opdateringen er banen; at tage den første tabel der blev fundet, eksporterede ingenting af den.

Så banen er tabellen med flest bundles, hvor et senere lag vinder et uafgjort (basisspillet først, derefter opdateringerne i navnerækkefølge), og tabellerne med samme navn uden bundles er dens **supplementer**: deres chunks lægges til banens, for de indeholder de største mips af dens teksturer. En teksturheader navngiver den chunk ved +164 (se [Teksturer og materialer](#textures-and-materials)). `levels` udskriver hvor hver bane kommer fra, og hvor mange supplementer den har.

## Bundle-manifester {#bundle-manifests}

En bundles første post er dens manifest, gemt ukomprimeret. Det er det binære bundle-format fra tidligere Frostbite-spil med en ny magi, `0xD68E799D`: antal, SHA-1'er, ebx- og res-poster (navneforskydning og størrelse), res-typer, metadata og id'er, chunk-GUID'er, strenge. Bundlens øvrige poster er ebx, res og chunks i den rækkefølge. Kontrol: antallene passer med posterne på hver bundle, og strengene begynder hvor postene slutter.

Ressourcetyper er hashes. `0x49B156D4` er MeshSet (hver res af den type hedder `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` læser alt dette for én bane, på få sekunder: en bane har titalls bundles og titusindvis af ebx, res og chunks.

## Payload-blokke {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

En komprimeret størrelse på nul betyder lagret, så længe den dekomprimerer til det samme.

| Metodeord | Kodek |
|---|---|
| `0x0070`, `0x0071` | ingen |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), fra spillets egen `oo2core`-DLL) |
| andet, med lige store størrelser | kopieret som lagret |
| andet | afvist |

Læst fra den rigtige pakke dekoderer hver samplet payload.

## EBX-partitioner {#ebx-partitions}

EBX indeholder alt der ikke er rå data. Hver partition er en RIFF-fil: `EBXD` (data, justeret til 16), `EFIX` (partitions-GUID, type-GUID'er og signaturer, instans, pointer-, import- og type-info-forskydninger, imports, og forskydningerne for arrays, boxede værdier og strenge), `EBXX` (array-tabellen: forskydning, antal, hash, flag, elementtype). Et pointerfelt er otte bytes: nul er null, en ulige værdi er import nummer `value >> 1`, alt andet er relativt til feltet.

**Typebiblioteket kan ikke læses.** Spillet leverer det i sit initielle filsystem, som er krypteret, og denne pakke rører det ikke. Typer kendes på GUID og signatur, som hver partition bærer, og de få typer baneeksporten har brug for, er lagt ud fra dataene.

## MeshSet {#meshset}

Et mesh er en MeshSet-res (beskrivelsen) og én chunk pr. detaljeniveau (bufferne).

| Del | Layout |
|---|---|
| præfiks | fire ord: header-størrelse (176 eller 192), niveau-postens størrelse (176 til 188), sektionspostens størrelse (368), 0 |
| header | bounding box; seks i64 niveauforskydninger; mesh-type ved `0x6C` (rigid, skinned, composite); niveau- og sektionsantal ved `0x9C` |
| niveau | sektioner ved `+0x08`; fem tegnelister ved `+0x14` (opaque, transparent, decal, depth only, shadow); indeksformat `+0x54` (`0x21` u16, `0x2E` u32), indeks- og vertexbytes; chunk-GUID ved `+0x74` |
| sektion | materialenavn; vertex-stride; trekanter, første indeks, vertex-forskydning (bytes), vertex-antal ved `+0x20`; vertex-deklaration ved `+0x64`: 16 x (usage, format, offset, stream), 16 stream-strides, antal |
| chunk | vertex-bufferen, derefter indeks-bufferen. En sektions streams følger hinanden, og indeks tæller fra sektionens første vertex |

Positioner er usage 1, stream 0, offset 0, som fire halvtal eller tre floats. Kun de opaque og transparent sektioner tegnes. Hver sektion navngivet `..._shadow` er i shadow-listen og kun der, så listerne afgør.

Kontrol: hvert mesh i en bane, hvis niveauer ligger i chunks, afkodes, og næsten alle har 99 % eller mere af deres vertices inden for deres erklærede boks; resten misser med afrundinger af halvflydende tal. Et afkodet kasse måler omkring en meter, Y op, med normaler der peger udad.

## Placering {#placement}

Indholdspipelinen samler et undermiljøs statiske objekter i en **statisk modelgruppe**: et array af medlemmer, ét pr. mesh, hver med sine instanstransformationer.

| Type (GUID, signatur) | Layout |
|---|---|
| medlem `ad13064e…`, `0xF861A878` | 224 byte: `+88` array af transformationer, `+112` objekt-blueprint (import), `+160` mesh-asset (import) |
| transformation `101dce06…`, `0x5E6D8C37` | 64 byte: højre, op, frem, translation, hver en vec3 polstret til 16 |

Mesh-assetets partition er navngivet som dens MeshSet-res, så importens partitions-GUID giver meshet. Et punkt lander ved `x·right + y·up + z·forward + translation`. Gruppens egen transformation var identitet i hver gruppe i de kontrollerede baner, og anvendes ikke.

Kontrol: i en bane løses hvert medlem i hver gruppe til et mesh; de fleste kopier har en rotation med determinant 1 inden for en tusindedel, de øvrige er skaleret eller spejlet. Type-GUID'erne og signaturerne er de samme i andre baner. En spilopdatering der ændrer layoutet, ændrer signaturen, og læseren finder så intet i stedet for at læse forkert.

### Objekter placeret enkeltvis {#objects-placed-one-by-one}

Det pipelinen ikke kan gruppere — ødelæggelige objekter, containere, affald — placeres via **objektreferencer** og **prefab-referencer** i banens partitioner:

| Type (GUID, signatur) | Layout |
|---|---|
| objektreference `a9a6a6ad…`, `0xC4856BEC` | `+32` transformationen (som ovenfor), `+112` objekt-blueprint (import) |
| prefab-reference `117c746e…`, `0xDE3FE9B4` | det samme; blueprintet er en prefab, en partition med flere referencer |

Prefabs indlejres; en kopi lander ved sin egen transformation ganget med sin forælders (rækkevektorer), ned til otte niveauer. Et objekt-blueprint tegnes som de meshes det importerer, undtagen de ødelagte tilstande (`dc_...`). En gruppet prefab refereres som sin `..._nongroupable_autogen`-rest, så intet tegnes to gange.

Gennemgangen starter kun fra banens verdener og lag. En partition hvis første instans er et prefab-blueprint (`134919fc…`, `0x0247807D`) er en prefabs definition, og en bane gemmer mange under sin egen mappe, placeret af sine verdener på andre måder end disse referencer; gennemgås den som om den var en verden, lægger en prefab sit indhold ved sine lokale koordinater. Det hober hundredvis af kopier omkring verdenens origin, langt under jorden. Verdener og lag har `a10ebe0f…`, `0xD3D16C3C` først.

Blueprints der er taget ud af spillet, følges ikke: udviklings- og testaktiver (`game/dev/`, `test/`), rundeslutnings-filmens sæt (`..._gameend_...`: placeret under jorden) og dødskameraets controller (`.../deathflow/...`, hvis gadgets står i verdenens origin). De genkendes på deres asset-sti, ikke deres lag: det samme lag der holder filmsættet kan placere en banes rigtige vægge og tage. Efter begge regler ligger ingen kopi i de kontrollerede baner mere end 10 m under terrænet, og kopier står på terrænet hvor spillet viser dem.

**Detaljeniveauer der træder i stedet.** Et meshs sidste detaljeniveau kan skifte til en afstandsvisning med et materiale af sin egen: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Et gitterårntårn med titusindvis af trekanter kan ende i en silhuet på nogle få hundrede, som budgettet ville vælge, og som tæt på er en massiv pig. Et detaljeniveau der indfører et sådant materiale, et det fineste niveau ikke har, vælges aldrig; meshets groveste er det sidste rigtige.

## Terræn {#terrain}

Kilde: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Terrænet er en TerrainStreamingTree-res (type `0x22FE8AC8`) og de chunks den navngiver.

| Del | Layout |
|---|---|
| header | 34 byte; nodeantallet ved 25 |
| rastertræer | en typebyte og en u32-længde hver, indtil en typebyte `0xFF`. Type 0 er højdefeltet: prøver pr. side ved +5 (265), højdeinterval ved +21 (1.280 m), terrænkvadratet i dens første nodepost ved +77 (8.192 m i den kontrollerede bane). Den holder nodernes bounding boxes og en 16 x 16 min/max-pyramide pr. node, ikke højderne |
| streaming-noder | quadtræet, først i dybden: chunk-størrelse og GUID; en valgfri anden chunk; en flag-byte (bit 0: chunken begynder med en højdeside); har-børn. Børn i rækkefølgen (0,0), (1,0), (1,1), (0,1) |
| højdeside | de første 265 x 265 u16 af en flaget nodes chunk, række for række; højde = værdi x 1.280 / 65.535 m; kolonner langs x, rækker langs z, fra nodens lave hjørne; en kant på 4 prøver, så 256 celler pr. node |

Hvert trin er kontrolleret for sig:

- Nodequadtræets parse forbruger resen til den sidste byte, med de erklærede 529 noder.
- Nabonoder deler præcis deres ni kantkolonner, så stride er 256.
- Et barns prøver på hver anden position er lig med forældrens præcis med en kant på 4, og 90 til 700 enheder fra med enhver anden kant.
- Det laveste ord i banen afkodes til bounding boxens laveste højde til centimeteren.
- Af de otte måder kvadratet kunne ligge på verdenen, er det kun x langs x og z langs z der lægger de placerede objekter på det: halvdelen af de samplede kopier inden for omkring 2 m, mod flere gange det for alle andre måder.

De placerede objekter måler så resultatet. Det laveste punkt af hver kopi, mod terrænet under den (bilineært, fra den fineste node):

| Placeret | Medianafstand | Signeret median |
|---|---|---|
| træer og buske | godt under en meter | lige under overfladen |
| rekvisitter | en meter eller to | på overfladen |
| klipper | omkring en meter | sunket ned med omkring en meter |
| bygninger | flere meter (de står på fundamenter) | let sunket ned |

Vegetation placeres på jorden og intet andet sted, hvilket gør det til den skarpeste kontrol: dens origins ligger i median 0,07 m fra overfladen. Bygninger spreder sig meget, fordi kategorien holder vægge, gulve og sæt-stykker til flerdelte og underjordiske konstruktioner. At flytte terrænet 64 m sideværts reducerer andelen af kopier inden for 0,5 m fra 29 % til 10 %.

`level` tegner højdefeltet som `ground:terrain`, hver del af det fra den fineste node med højder dér og ikke finere end `--ground-spacing` (4 m som standard: 3,7 millioner trekanter for den kontrollerede bane, hvis fineste noder er 0,5 m). Dele med forskellig opløsning mødes med små trin; intet syer dem sammen.

En nodes chunk holder også siderne af lagmaskerne efter dens højdeside, og dens anden chunk ender med nodens farvekort (se [Terrænlag](#terrain-layers)).

## Terrain layers {#terrain-layers}

Spillet skygger terrænet tæt på en spiller ved at splatte tilt-overfladematerialer med malede masker, med et farvekort over dem, og tegne dekaler (veje, asfaltpletter, startbanemarkeringer) ovenpå. Frostbites egen beskrivelse af systemet (Widmark, "Terrain in Battlefield 3", GDC 2012) lister terrænets rastre som højdefeltet, shader-splatmasker, et farvekort "used as an overlay on top of shader splatting", fysikmaterialer, en ødelæggelsesdybdemaske, et albedokort til bounce-lys og ekstra maskekanaler; en rasters fliser bærer en kant til renderingsalgoritmerne. Den streamingtræ der tilhører de kontrollerede baner, har syv rastertræer, typet 0, 1, 2, 4, 5, 7 og 8, hvis headere begynder med deres flisestørrelse: 265 for højdefeltet (type 0) og type 2, 72 eller 66 for maskerne (type 1), 132 med en kant på 2 for farvekortet (type 4), 260 med en kant på 2 for type 5.

**Lagslisten.** Terrænets `....layergraphs`-res lister en 32-byte post pr. lag, i den rækkefølge maskepostene nummererer dem (34 poster, 34 depotsektioner og lagindeks 0 til 33 i én bane); hver posts id slutter med dens sektionsnøgle i lagdiagrammets shaderblok-depot (`....layergraphs_shaderblockdepot`), hvis blok navngiver lagets kort: ét `_cv`-farvekort, `_nhs`- og `_ao`-kort pr. overflade, plus delte detalje- og støjkort. Mange lag navngiver ingen kort: de er kilder lagdiagrammet læser. Et lags farve er middelværdien af dets `_cv`-kort; skalaen for flisningen findes ikke. Terrænasset slutter med en fembyte-post pr. lag (en byte, derefter et u32-lagindeks eller -1).

**Maskerne.** Rastertræ 1 er maskernes quadtræ. Dets krop begynder med 59 byte, sidelængden af siden ved 0: 72 hvor siderne er BC4 (72 x 72, 2.592 byte), 66 hvor de er ukomprimeret otte-bit (4.356 byte). Derefter kommer en gruppe pr. node, først i dybden:

| Del | Layout |
|---|---|
| gruppe | u16; u16 postantal; u32 sideantal; posterne; en nulbyte. En gruppe uden poster er 7 byte i alt |
| post | 33 byte: u16 lag, u16 hash, kvadrantens boks (fire floats), to flag-bytes, en 85-bit tilstedeværelsespyramide |

En gruppes poster er dens nodes fire kvadranter, lag for lag, hvert lags kvadranter i rækkefølgen (0, 0), (1, 0), (1, 1), (0, 1). En post med det andet flag sat dækker sin kvadrant hel og har ingen side; en uden den har den næste side; en kvadrant uden en post for et lag dens gruppe nævner, er tom for det lag; det første flag er kun klart når laget fortsætter i kvadrantens egen gruppe, et niveau ned, og erstatter det dér. Sideantallet er antallet af poster med en side.

Siderne: en streaming-nodes egne gruppes sider følger i dens chunk, højdesiden, en 4.358 byte lang 16-bit-sektion og en 67 x 67 otte-bit-raster (fra chunkens start når den ikke har en højdeside); dens anden chunk holder siderne for sine fire kvadranters grupper et niveau ned, kvadranterne i farvekortets rækkefølge, og så farvekortet. En side er kvadrantens 64 x 64 texels, rækker langs z og kolonner langs x, med en kant kopieret fra naboerne: 4 texels på en BC4-side, 1 på en ukomprimeret.

Kanterne beviser placeringen uden skøn: to sider af samme lag ved siden af hinanden skal have hinandens kant-texels. `read_masks` kontrollerer det for hvert par den placerer, og afviser en bane hvor færre end 99 % er enige. Omkring en tredjedel af de kontrollerede baner læses, med deres kanter enige; nogle har ingen malede masker; resten afvises, næsten alle af kontrollen (deres nodes chunks holder mere end dette layout kender). En afvist banes jord tager middelfarven af dens overfladematerialer, og eksporten siger hvorfor. Kanterne mod en fuld kvadrant er 255 og dem mod en tom 0.

Den 4.358 byte lange sektion og 67 x 67-rasteren før siderne læses ikke: deres værdier ligger i et smalt højt bånd, uden små værdier og uden sentinel.

**Jordens farve.** Lagdiagrammet blander lagene i et kompileret shader-diagram af masker, hældning, højde og støj, og det læses ikke. `--ground-texture` farver jorden efter en regel af sin egen, sagt her som sådan:

- lag hvis farvekort er navngivet for afstand er de fjerne views stand-ins og udelades;
- de teksturerede lag der dækker ni tiendedele af terrænet eller mere, er grundlaget. Deres masker er fyldt næsten overalt, så hvor hvert ligger, er shaderens valg, ikke deres: dem navngivet for klippe eller klint farver skråninger over 40 grader, dem navngivet for grus farver fladt terræn (de andre grundlagslag når ingen er), blandet mellem 20 og 40 grader efter højdefeltets hældning (taget hver 4 m og spredt bilinært over de bagte texels: gentaget i 4 m-blokke tegnede den klippefarven som hårdkantede pletter);
- hvert andet teksturet lag lægges over grundlaget efter sin egen maske, i lagrækkefølge;
- farvekortet lægges over resultatet som motoren gør det, to gange jordens farve ganget med kortet, så mellemgråt lader den være som den er; hvor farvekortet ikke har texels, tager jorden kortets medianlysstyrke, i gråt.

Kontrolleret mod medianfarven på jorden i spilframes fra tre baner (kroma som rød og blå over grøn): det bagte spilleområde kommer til 1,00 / 0,69 mod framenes 1,19 / 0,78 i én, hvis græslag er grønne hvor framene viser tør græs; 1,19 / 0,82 mod 1,01 / 1,04 i en anden, hvis farvekort i sig selv er varmt (1,13 / 0,88); og 1,05 / 0,91 mod 0,93 / 0,92 i en tredje uden farvekort. Framene er belyst og gradueret, så dette måler nuancen, ikke lysstyrken.

**Farvekortet.** En nodes anden chunk holder, efter siderne af dens kvadranters grupper, fire BC7-sider på 132 x 132 (17.424 byte hver), én pr. kvadrant i nodens, i rækkefølgen (lav x, høj z), (høj x, høj z), (høj x, lav z), (lav x, lav z). Maskerne fortæller hvor mange byte mask-siderne fylder, så farvekortet findes ved antal, ikke ved chunkens slutning: i en bane har de grovere noder fire flere sådanne sider efter det, en anden raster i en flad farve, og at læse chunkens sidste fire sider mistede farvekortet over ni tiendedele af terrænet. Uden den tælling var farvekortet også væk i baner med ukomprimerede masker, hvis sider ikke er et helt antal BC4-sider; en banes farvekort gik fra 0,4 til 0,94 af dens terræn. Rækkefølgen blev fittet: mod kanterne af hver kvadrants højdefelt matcher hver side for noder med detaljer en kvadrant, ikke vendt, med 0,3 til 0,54 hvor den næste bedste placering er under 0,2. Sammensyet af den lægger en banes sider sig uden søm ind i vejene, vandet og bebyggelserne på testbanen, ved 0,5 m pr. texel i spilleområdet. Hvor lagene gør arbejdet, er farvekortet næsten neutralt (median 110, 107, 104); andetsteds kan det bære fuld farve. En bane hvis anden chunks kun holder ukomprimerede masker-sider, får ingen farvekort læst. En tidligere runde af denne læser kaldte disse sider ikke-geografiske: den matchede dem mod baggrundskortet, som kan være et helt andet landskab, og placerede hver side over hele sin node i stedet for en kvadrant.

**Den bagudrettede bounce-lys-albedo** blev søgt efter og ikke fundet: rod- og første-niveau-nodernes chunks er hele maskesider, og type 5's payload er ikke lokaliseret.

**Huller.** Et banes terrænasset (res-type `0x1CA38E06`) navngiver tre shadere: en standard overfladeshader, en hul-overfladeshader og en standard kildeshader. Hvilket lag hul-shaderen læser, er ikke fundet, så højdefeltet skæres ikke. I en bane kan navigationsmeshet køre på klippemeshes titalls meter under højdefeltet, hvor spillet må have skåret dem væk. Der ledt efter og ikke fundet: et lags maske, rasteren 67 x 67, en reserveret højde (ingen højdeside i banen holder 0 eller 65.535) og et nodeflag (hver node under roden har flag 1). Rastertræ 7 og 8 er det der er tilbage. Begge er længdekodet: en byte lig med den før den efterfølges af et antal yderligere kopier (`ff ff 84` er 134 byte af 255). Træ 7 (flise 256, et fuldt quadtræ med fem niveauer, fire bit pr. prøve) afkodes til bytepar med værdierne 0 til 3; træ 8 (flise 265) til bytes overvejende 255, med dets øvrige værdier i regelmæssige serier. Ingen af deres flise er endnu placeret, så ingen af dem vides at indeholde hullerne.

**Dekaler** læses og bages; se [Terrændekaler](#terrain-decals).

## Terrain decals {#terrain-decals}

Kilde: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Veje, startbaner, betonplatforme, malede linjer og bogstaver, dækspor: `TerrainDecals`-res'en (type `0x15E1F32E`) holder dem som flad geometri, spillet lægger hen over terrænet.

| Del | Layout |
|---|---|
| header | ved +16 et slot-antal n, derefter n 16-byte slots, derefter postantallet |
| poster | én pr. tegnebatch, lagt ende til ende, i varierende længde: 156 byte faste felter — første vertex ved +32, trekantantal ved +36, teksturflisning i meter ved +44 — derefter batchens vertexbytes (forskydning, størrelse), og så en hale der navngiver dens teksturer med deres assets' partitions-GUID'er |
| vertices | 32 byte: x, z (f32), 8 pakkede bytes, u, v (f32), r, g, b, a (f16); hver batch en almindelig trekantsliste |
| indekser | u32, talt fra 0 i hver batch; ikke nødvendige |

Kontroller:

- postenes vertexintervaller følger hinanden uden huller og dækker alle vertices præcis, og hver posts første vertex x 32 er dens forskydning;
- læst sådan er trekanterne kompakte dekaler (bogstaver, linjestrimler, pletter); læst med én vertex forskudt, er de flader der løber hen over kortet;
- næsten alle batches navngiver teksturer i deres hale: et farvekort (`_cv`) med et opacitetskort (`_op`, rød kanal), eller for markeringer et kanalmaske (`_rgb`).

Efter tekstur-GUID'erne bærer halen batchens materialeparametre, kodet som en shaderbloks er (se Tints nedenfor). Malingsfarven på en markering, et dækspor eller en linje er float3-en med hashen `607e`: en sandfarvet 0,64, 0,56, 0,48 for dækspor i sand, næsten sort for tjære. Opacitetskort er for det meste format 62, en kanal med 8 byte pr. blok, læst som BC4.

En batch afbilder sin tekstur enten efter verdensposition (u = x, v = z, teksturen gentages hver tilflisnings-meter: asfalt, beton, grus) eller 0 til 1 på tværs af dekalen (en linje, et bogstav, et dækspor). Poster tegnes i filrækkefølge.

**Bagningen.** `level --ground-texture M` maler, under dekalernes udstrækning og fliser på højst 4.096 pixels, baggrundens farvekort (bilineært) og derefter hver batch over det efter sin opacitet × vertex-alfaen. Vertexfarverne bruges ikke: nogle batches' vertices er rent grønne eller blå, hvilket farvede en banes markeringer i de farver. Højdefeltets trekanter dér bliver til `ground:terrain x<x> z<z>`-dele der bærer flisen. Hver batch tegnes med:

| Batchen navngiver | Tegnes som |
|---|---|
| et farvekort (`_cv`) | kortet, efter dets opacitetskort |
| et multiplikationskort (`_mult`) og et opacitetskort | malingen (hvid hvor materialet ikke navngiver nogen) ganget med multiplikationskortet, efter opacitetskortet: en startbanes slidte midterlinje, kantlinjer og tærskelstriber |
| et kanalmaske (`_rgb`) | malingen, ellers hvid for linjer og bogstaver, mørk for konturer, en svag mørkfarvning for slid, dækspor, pletter, vandpytter og fugtighed, efter masken |
| et opacitetskort alene, med en maling | malingen efter opacitetskortet: dækspor |

En vejvariationsmaske er ikke maling, men varierer overfladen under den, hundredvis af meter på tværs, og tegnes ikke, uanset sin maling: malet hvid lagde den to bleg rektangler på 150 til 250 m længde på en banes skråninger. `_mult`-kortet tages som malingens eget slid, ikke som en mørkfarvning af jorden under den: det er næsten hvidt, og linjens form ligger i opacitetskortet.

Næsten hver batch tegnes, ind i nogle få fliser ved 0,5 m pr. pixel; eksporten vokser med nogle få MB og tager nogle få sekunder længere. Set oppefra ligger flyvepladsernes, taxibanernes og vejnettets områder under sammensatte hegn og bygninger og fører ind i deres porte.

Tegnet som geometri i stedet ville dekaler kræve alfa-blanding, som skriveren ikke bærer, og en forskydning over et terræn ville de z-fightes med; bagning holder dem i jordens egne farver.

## Textures and materials {#textures-and-materials}

Kilde: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

En Texture-res (type `0x6BDE20BA`) er en 180 byte lang header: type og pixelformat ved +8, bredde og højde ved +22, mip-antal ved +30, chunk-GUID'en ved +40, femten mip-størrelser ved +56. Chunken er mip-kæden, største først. Nogle chunks mangler deres største mips, som leveres i en pakke med høj opløsning, og chunkens længde siger hvilken mip den begynder ved. Den pakkes chunk navngives ved +164; den læses fra banens [supplementer](#which-table-is-the-level), når en mip som hovedchunken mangler ønskes, og dens længde plus hovedchunkens er hele kæden.

| Format | Afkodet som | Belæg |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineær) | et plastiktanks farveark afkodes som én; som BC3 er de samme bytes støj |
| 61, 60 | BC3 | et kasse-ark afkodes rent som BC3, ikke som BC1 eller BC7 |
| 57, 56, 55 | BC1 | en halv byte pr. pixel |

Mesh-assetet navngiver ingen tekstur. Forbindelsen ligger i banens **shaderblok-depoter** (res-type `0x73312045`, ét pr. undermiljø), nøglet med otte bytes ved +0x130 i et meshsektions post:

| Del | Layout |
|---|---|
| tabel, ved 16 | (sektionsnøgle u64, deskriptorforskydning u64), indtil en forskydning falder uden for resen |
| deskriptor | (blokforskydning u64, hash u64, blokstørrelse u64) |
| blok | sektionens shader-parametre; hver tekstur er en 49 byte post: en byte, 16 byte, teksturassetets partitions-GUID, dens instans-GUID |

Kassens sektionsnøgle optræder én gang i hvert af de ti depoter i de undermiljøer der placerer den, og dens blok navngiver `t_mil_crate_03_cs` og `_nmt` blandt de delte detaljekort. En blok navngiver hver tekstur shaderen samler, og hvilken der er farvekortet, står ikke; den vælges derfor: en sRGB 2D-tekstur hvis navn holder de fleste ord fra materialets navn (`M_ConcreteWall_01`: concrete, wall), derefter fra meshets, derefter en der ikke er en detalje-, dekal- (`t_de_...`) eller skadekort, derefter den som færrest blokke bruger. En vejskilts blok navngiver dens panel `t_com_highwaysignage_01_cs` og et dekalark `t_de_com_highwaysignage_01_ca` med et skjold lagt på siden; begge matcher ordene, og uden dekalreglen vandt arket på brug og skiltet viste skjoldet drejet en kvart, gennem hver teksturkoordinatsæt sektionen har. `..._sdf`-signerede afstandsfelter, paletter og kanalmasker (`_rgb`) vælges aldrig, uanset hvilke ord de deler (`_rgba`-kort gør: de fleste er farve med en alfa, og at udelade dem byttede et kraftledningsmasts og en trappes egne kort ud med urelaterede). En baggrunds vegetationsatlas `..._atlas_a_sdf` tegnet som farve viste sorte og hvide stjerner for træer, en baggrunds bygningspalet et konfetti af farveprøver for vægge, og glasaffald tegnet gennem sin kanalmaske kom ud cyan. En sektion hvis eneste kandidater er delte detaljekort, forbliver fladfarvet.

**Paletter.** En baggrunds bygninger tager deres farver fra en palet, 256 x 256 texels af 16 x 16 farveprøver: hver vertex bærer fire bytes (usage `0x1E`) hvis to første siger hvor i paletten dens farve er, x og y ud af 255. `level` tegner en sådan sektion med paletten som dens tekstur, hver vertex i midten af sin prøve. Tegnet sådan kommer en banes baggrundsblokke ud som pastelvægge, terracotta og mørke vinduer hvor de var ren hvide.

**Overlays.** Store objekter flisebelægger et trimark gennem deres første teksturkoordinater og lægger et overlay over det gennem det andet sæt, som ligger inden for 0 til 1: en udfoldning af hele objektet. Overlayet (`..._overlay_cs`, med sin maske `..._overlay_a`) bærer hvordan objektet ser ud på afstand, en olietanks røde bånd og rust; tegnet med trimarket alene kom en banes tanke ud som grå paneler. En sektion hvis blok navngiver et overlay med sin maske, og hvis andet sæt koordinater er sådan en udfoldning, tegnes med overlayet gennem dem (36 sektioner i den bane).

**Tints.** Mange farvekort er grå (deres kanalers middelværdier inden for 6 % af hinanden): shaderen maler dem med farver fra blokkens parametre. Efter dens teksturposter (49 byte hver) lister en blok sine parametre, hver en typemarkør (`f11af825` en float3, `a5e1f2de` en float4, `c1b1a014` en float, `4a4fc3a1` et heltal), flag-bytes `01 80` for én værdi, en to-byte hash af parameterens navn, et u32-antal, værdien og et otte-byte id. Navnene er ikke gemt. Syv float3-navnehashes virker som tints: i en bane holder tre af dem en farve i omkring 1 blok ud af 6 hvis kort er grå og næsten aldrig hvor kortet har sin egen farve, og de andre holder de farver et grått kort males i hvor materialets navn siger det (en brobanes `..._blue`-kant: 0,047, 0,098, 0,171 mod en neutral 0,5). En familie kan holde flere værdier, én pr. kanal i en maske, de fleste neutrale, og en værdi med en kanal der er næsten intet (ren grøn på murstensfacader) vælger en maskes kanal i stedet for at male. `level` ganger et grråt farvekort, i lineært lys, med hver families første værdi der hverken er neutral eller sådan en vælger, over dens neutrale, og gemmer resultatet som en tekstur for sig selv; et kort med farve lades som det er. Reglen er eksporterens egen: hvilken kanal i en maske der får hvilken tint, læses ikke. I én bane tog den andelen af strukturtrekanter tegnet nær hvid fra 19,4 % til 3,9 %.

**Objektvariationer.** Ét mesh placeres i flere udseender: en lagervæg med en rød eller blå stribe og et andet nummer malet på, en container i grøn eller grå. Hver placeret kopi navngiver sit udseende:

| Hvor | Felt |
|---|---|
| statisk modelgruppe-medlem | +32: et array med én pointer pr. kopi, til en objektvariation eller null |
| objektreference | +120: en pointer til en objektvariation eller null |
| objektvariation (`ov_...`-partition, type `235f2a9c...`) | dens første instans +32: variationens u32-navnehash |

En sektions udseende i en variation er shaderblokken nøglet med sektionens egen nøgle med variationens hash lagt til dens første fire bytes, som et little-endian u32 (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); en sektion uden en blok under den nøgle ser ens ud i hver variation. Meshets variationsdatabaser (`meshvariationdb_win32`) lister pr. mesh og variationshash de materialer hver variation berører, men ikke nøglerne: reglen blev fundet ud fra nøglerne selv og holder for hver sektion med varianter der er kontrolleret (de fire variationer af én væg, tre af dens sektioner hver). En variations blok bringer sine egne teksturer med såvel som sine tints: det malede nummer på væggen er et bogstavark som variationens blok navngiver. En stor andel af gruppede kopier er placeret i en variation.

En blok bages én gang for hvert sæt indhold, og depotets post for en nøgle bærer en hash af dem (depotets anden u64). Hvor en sektion ikke har en blok under sin variations nøgle, når variationen den alligevel via en *tvilling*: en anden sektion hvis standardblok har samme indhold og har en. Uden tvillinger kan en væg hvis længder deler én standardblok komme ud i to farver. En sektion uden sin egen variant tager den variant de fleste af dens tvillinger har.

**Ødelæggelige meshes.** Et mesh en kamp kan slå ned har et destruktionsaktiv af sit eget navn ved siden af sig (`.../br_x.destruction` for `.../br_x_mesh`): de brydelige bygninger og vægge (`br_`) og mange rekvisitter. `level` holder deres overflader i dele af egen, navngivet med ` (destructible)`, hvis glTF-noder bærer `{"destructible": true}`. Deres ødelagte tilstande er `dc_..._part<N>_mesh`-meshes ved siden af dem, hver centreret på sit eget origin; hvor en del står, ligger i destruktionsaktivet, som ikke læses, så de ødelagte tilstande eksporteres ikke.

**Udeladt.** Sektioner med pladsholder-blockout-materialer (`M_Whitebox`: nogle få store utextureret trekanter nogle bygninger beholder ved siden af deres flader, som stod ud af en bane som hvide finner), meshes lavet til filmsekvenser (en helikopter placeret hvor dens scene begynder) og belysningshjælpere (planer der blokerer lys, tegnes aldrig). En banes genererede baggrundsbygninger (`..._generated_blueprints_..._mesh`) tegnes, men deres vægges materialenavne er kun støjkort, og deres vertices bærer ingen farve, så de forbliver almindelige. Næsten hver tegnet sektion får et farvekort.

**Bogstavark.** En væg's malede nummer eller en kranes billboard-tryk er en sektion for sig selv, hvis farvekort er et ark (`_ca`): et bogstavs alfa over fast maling, eller et tryk. Dets første teksturkoordinater flisebelægger væggens puds hen over panelet (u -0,2 til 1,7 på én væg), hvilket tegner arket næsten to gange; det fjerde sæt (`0x24`, ellers det tredje, `0x23`) lægger det på præcis én gang (u -1 til 0, v 1 til 2, et par tusindedele over i de grovere detaljeniveauer). Hvor det første sæt efterlader ét eksemplar af billedet, og det fjerde eller tredje ligger inden for et, tegnes arket gennem det, flyttet ind i 0 til 1. Et ark med alfa tegnes 1 cm foran den flade det er malet på, som tegnes under det i blokkens anden farvekort gennem det første sæt: uden det viste arkets tomme texels væggens indre. Det andet sæt er et objekts udfoldning til dets overlay og bruges ikke her.

**Udklipskort.** Farvekortets fjerde kanal betyder forskellige ting efter kortets navn. I `_cs` er den det hyppigste (893 af en banes valgte kort): den er glathed, 1 % af et mediankorts alfa ligger inden for 0,1 af 0 eller 1. I `_cu` (blade, græs) og `_ca` (farve og alfa) er den opacitet: 90 % og 87 %. Et farvekort navngivet `..._cu` eller `..._ca` hvis alfa mindst 75 % ligger nær 0 eller 1, mindst 1 % under 0,5 og mindst 5 % over, skrives med sin alfa, som PNG, og dets materiale som glTF `alphaMode` MASK, `alphaCutoff` 0,5, dobbeltsidet; bladkort viser så blade, ikke deres sorte hjørner. Et træs bladkort har ingen alfa overhovedet (højst 4 af 255): dets blade klippes af geometrien, og med kun de to første betingelser blev hele kronen klippet væk.

Teksturkoordinater er vertex-usage `0x21`, to halvtal (format 6) eller to floats (format 2). Sektioner bærer op til tre flere sæt (`0x22` til `0x24`) til dekal- og detaljelag. Koordinaterne flisebelægger: en containers ribbede side løber fra -1,6 til 1,8, banebaggrundens fliser ligger helt uden for 0..1, og i en bane ligger 23 % af de teksturerede trekanter uden for 0..1. De skrives som de er, med en gentagende sampler; 3DHeat-vieweren pakker hver gentagende tekstur ind i sin atlas. En renderer der i stedet klemmer dem, udtrækker ribbene til dobbelt bredde, gør en betongulv til striber langs én akse, og giver en tårns stålbjælker deres teksturs kantfarve; for den skærer `--clamped-uvs` hver trekant langs linjerne hvor dens tekstur gentages og flytter hvert stykke ind i 0..1 (se [Outputformat](output-format.md)). Derefter ligger 0,03 % af de teksturerede trekanter, hvor en tekstur gentages mere end 16 gange, uden for, og en trekant som skæringen ville lave mere end 4 stykker af, tegnes i sin teksturs gennemsnitsfarve i stedet: bark gentages ned ad hver gren, og skåret gik en banes træer fra 6,4 til 24 millioner trekanter.

Højdefeltet har ikke et farvekort af sit eget, som kunne læses. Hvor et af banebaggrundens kort dækker det, farves det derfra: baggrundens teksturkoordinater er en lineær funktion af verdens x og z (99 % af dens vertices inden for 0,001 af den, og kortet dækker en 65.536 m kvadrat, drejet en kvart), og den samme funktion giver højdefeltets. Banen leverer det kort's mips fra 2.048 px og ned, så højdefeltet får 32 m pr. pixel. Dens mørke klippe ligger på den stejle jord: korrelationen mellem mørke og hældning er 0,48, og højst 0,34 for de syv andre orienteringer.

En anden banes baggrund er otte nære og otte fjerne fliser rundt om spilleområdet, hver gentager sin egen tekstur hen over flisen, og ingen når højdefeltet. Hver baggrundstekstur fittes for sig, og når ingen dækker højdefeltet, tager den den gennemsnitsfarve baggrunden viser inden for en kilometer fra terrænkvadratet, som `--ground-texture` bager dekalerne over. Et baggrundsmateriale er et hvis navn holder `TerrainBackdrop`, eller `BD_` og `Terrain` (`M_BD_<site>_Terrain..._Near`); eller et baggrundsmesh (`bd_..._terrain<site>_04_far_mesh`) har et almindeligt terrainmateriale (`M_<region>_Terrain<site>_04_Far`), som de to første regler missede i én bane og derfor farvede dens jord ud fra dens overflader i stedet.

Hvor intet baggrundskort dækker højdefeltet, tager det dog middelfarven af terrænets egne overflader før baggrundens gennemsnit: `_cv`-farvekortene dens lagdiagrams shaderblokke navngiver (27 i en bane: sand, grus, jorder, græs, revnet beton), hver midlet, derefter medianen af hver kanal, uden motorens standardoverflade. En baggrund kan være et helt andet landskab: i en bane gjorde dens gennemsnit (95, 99, 80 i sRGB) spilleområdets jord til en grå spillet ikke viser. Med `--ground-texture` ganges den farve med to gange farvekortet, hvilket lader mellemgråt være som den er, og bages med dekalerne over, over både dekalernes og farvekortets udstrækning.

Mod spillet: medianfarven af hvert banes bagte spilleområde og af spilframes (rækker 55 til 72 % af billedet ved siden af HUD'en, 24 frames hver; sRGB; framene er belyst og gradueret, så forholdene r/g og b/g er den rimelige sammenligning):

| Bane | Frames | Baggrundens gennemsnit | Nu |
|---|---|---|---|
| første | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| anden | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| tredje | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Den første er rettet; de to andre var en smule tættere i nuance før. Én farve for en hel bane kan ikke være rigtig overalt; masker ville være det.

## Navigationsmesh {#navigation-mesh}

Kilde: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

En bane leverer én partition pr. agent, `<level>/dbt/<level>_navmesh_layer_<n>`: i én bane er lag 0 soldaten (1,8 m høj, 0,18 m trin, 0,4 m radius), og to andre er køretøjer (3,5 og 10 m høje). Hver partition holder to arrays:

| Array | Element |
|---|---|
| tiles | 28 byte: u32 0, u32 hash, u32 0, u32 chunk-indeks, u16 flise x, u16 flise z, u32 forskydning, u32 størrelse |
| chunks | 20 byte: chunkens GUID, u32 størrelse |

En flise er `size` byte ved `offset` i chunk `chunk index`, little-endian, og lagt op som Detours (Recast Navigation) bag en længere header:

| Forskydning | Indhold |
|---|---|
| 0 | `VAND`, version 7 |
| 24 | antal: polygoner, vertices, links, detaljemeshes, detaljevertices, detaljetrekanter, bounding-volume-noder, off-mesh-links, den første off-mesh-polygon |
| 188 | agentens højde, trin, radius |
| 200 | flisens bounding box, seks floats |
| 232 | vertices: x, y, z floats, verdenskoordinater |
| næste 8-byte grænse | polygoner, 32 byte: u32, seks u16 vertex-indekser, seks u16 naboer, u16 flag, vertexantal ved +30, ved +31 området (lave seks bits) og typen (øverste to) |
| derefter, pakket | links (16 byte), detaljemeshes (12: første detaljevertex u32, første detaljetrekant u32, vertex- og trekantantal u8), detaljevertices (tre floats), detaljetrekanter (tre indeks og flag), bounding-volume-noder (16), off-mesh-links (80) |

I hver flise i de kontrollerede baner summerer disse til flisens størrelse, til byten, og detaljemeshes nummererer polygonerne før den første off-mesh.

En polygon er flad mellem sine hjørner; dens **detaljemesh** holder fladens rigtige højde over ujævnheder, klipper og trin, og det er det der tegnes. Et detaljetrekants indeks under polygonens hjørnetal er det hjørne, ellers detaljevertex `first + index - corners`. Vifteformet opdeling af polygonerne i stedet lægger mange flere trekanter under terrænet og laver lange slivere; med detaljemeshes er ingen længere end en 16 m flises diagonal plus trinet op ad en skråning.

Art 0 er jord, art 2 små stejle pletter (omkring 45 grader, en kvadratmeter hver), art 1 et link mellem flader: dets hjørner spænder 125 m eller mere i højden og ligger uden for flisen, nogle i origin. Links udelades; resten tegnes af deres detaljemeshes, eller viftes i en flise uden en.

Kontroller: chunks' størrelser summerer til flisenes præcist; hver overfladevertex ligger inden for sin flises boks, plus eller minus omkring en meter; næsten alle trekanter vender opad. En flise der fejler, afvises og tælles, og i den bane er ingen det.

Hvad soldatens mesh dækker, set oppefra i testbanen: jorden, gulve, trapper og nogle tage, og ikke toppene af fragtcontainere. Det er AI'ens kort over hvor en soldat kan stå, det tætteste filerne kommer på hvor spillere står.

## Ikke implementeret {#not-implemented}

- Terrænets lagdiagram, som blander dets overfladelag (se [Terrænlag](#terrain-layers)): jordens farve følger en regel af denne læsers egen, ud fra lagenes masker og højdefeltets hældning, og baner hvis maskesider ikke passer sammen, får én farve.
- Dekalmaterialers farveparametre: markeringer gennem kanalmasker males i en neutral farve.
- Blueprints af objekter der ikke er meshes (gameplay-logik, effekter, lyde).
- Ødelagte tilstande for ødelæggelige meshes: deres dele steder ligger i destruktionsaktivet, som ikke læses.
- Navigationsmeshets links (spring, stiger, spring over) og dets køretøjslag.
- Meshniveauer lagret inline i resen (10 meshes i en bane, gadgets), og skinnede og sammensatte meshes' knogler og dele, og normaler (beregnet af skriveren).
- Normal-, ruhed- og andre kort; alfa andet end et udklip (gennemsigtigt glas og dekaler tegnes ugennemsigtige).
- Terrænhuller: en hul-overfladeshader er navngivet, men hvad den læser er ikke fundet (se [Terrænlag](#terrain-layers)), så højdefeltet skæres ikke der hvor den gangbare jord løber under det.
- Hvilken tint der hører til hvilken kanal i et materiales maske: et grått farvekort tager den første tint der ikke er neutral (se [Teksturer og materialer](#textures-and-materials)).
- Effekter (`fx/`-stier) og kabelmeshes, hvis bounding boxes er titalls kilometer lange; de udelades og tælles i opsummeringen.
- Den XOR-obfuskerede tabelform.
