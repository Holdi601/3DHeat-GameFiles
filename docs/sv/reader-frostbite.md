---
title: Frostbite
lang: "sv"
source: reader-frostbite.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, bundles, meshar och nivåer

**Läser en Battlefield 6-nivå ned till dess terräng, dess placerade meshar och deras färgkartor, och
skriver den som en `.glb`.** Frostbite-spel (Battlefield, Need for Speed, Dead Space) håller sitt innehåll i
`.cas`-blobbar, beskrivna av `.toc`-innehållsförteckningar. En nivås tabell säger vilka bundles nivån laddar,
bundles namnger varje tillgång, och tillgångarna säger vilket mesh som står var.

Källor:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabeller, paket, nyttolaster),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bundles och deras manifest),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX-partitioner),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(höjdfält),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(texturer och material),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(placering och export).
Kommandon: `identify`, `levels`, `level` (se [Kommandon](commands.md#levels-and-level-frostbite)).

Inget här är dokumenterat av spelet. Varje layout nedan lästes av filerna och hölls sedan mot alla
filerna, och varje avsnitt säger vad kontrollen var. Där Frosty-modderingsverktygen beskriver äldre
versioner av en struktur följer fältnamnen deras; ingen kod togs från dem (se
[Regler och licenser](rules-and-licences.md)).

## Huvudet som ser krypterat ut och inte är det

| Magi (u32, little-endian) | Betydelse | Hantering |
|---|---|---|
| `0x00CED100` | naken: trädet börjar direkt | läses |
| `0x01CED100` | signerad: en 556-byte signatur, sedan trädet **i klartext** | läses |
| `0x03CED100` | XOR-förvrängd, med nyckeln i filens eget huvud | upptäckt och avböjd |

Den signerade formen är vad nuvarande Battlefield levererar. De högentropiska byten efter magin
är en signatur, inte chiffertext.

## DbObject-trädet

En rekursiv struktur. Varje fält är en typbyte (de nedre fem bitarna är typen, bit 7 är "anonym"), ett
valfritt namn och ett värde. Containrar bär sin längd som ett variabelt heltal och slutar med en nollbyte.
`parse_toc` kontrollerar varje containers längd, så en fil som tolkas blev förstådd. `layout.toc` är i
denna form.

## Installationspaket

Varje position namnger det **installationspaket** dess blobb hör till. Varje paket numrerar sina
blobbar från `cas_01`, så blobbnumret ensamt är tvetydigt så snart mer än ett paket är installerat,
vilket alltid är fallet.

- `layout.toc` listar paketen under `installManifest.installChunks`, var och en med en
  `persistentIndex` och en `installBundle` såsom `Win32/installation/<package>`.
- Paketets blobbar finns i den mappen, under `Data` för basspelet eller under `Update/<pack>/Data` för
  det som kom senare.
- En positionspost bär hela 32-bitars `persistentIndex`: den låga halvan av dess första ord håller den
  höga halvan, den höga halvan av dess andra ord den låga halvan; den låga halvan av det andra ordet är
  blobbnumret.

Kontroll: varje position i varje binär tabell i en installation löser till ett deklarerat paket och
ligger inom blobben den namnger. En tidigare version tog den första `cas_NN.cas` med rätt nummer. En
tredjedel av nyttolasterna den läste såg då högentropiska ut och togs för kryptering. De var rätt
förskjutningar i fel fil. Inget som hittades är krypterat.

## Nivåtabellen

En nivås tabell (`levels/<level>/<level>.toc`) är en sektionstabell: femton big-endian-huvudord, sedan
sektioner lagda ände mot ände, vars förskjutningar både anges och kan härledas från två antal.

| Sektion | Innehåll |
|---|---|
| bundles | en hashtabell (ett ord var), sedan en 16-byte-post per bundle: nyckel, `0x40000000` \| storlek, 0, förskjutning |
| chunkhashtabell | ett ord per chunk |
| chunkar | 16-byte-id (chunkens GUID **med bytes i omvänd ordning**), sedan ett ord: `0x80000000` \| 4 x indexet för dess position |
| positioner | fyra big-endian-ord: paket (delat), blobb, förskjutning, storlek |

Chunk-id:na och positionerna står i **olika ordning**. Läser man dem i filordning parar man varje
chunk med en annan chunks bytes, som avkodas perfekt (mest som ljud) och därför inte ser fel ut förrän
ett mesh blir brus. Kontroll: i en nivå är indexorden en permutation av 0 till antalet chunkar minus ett.

Bundlesen lagras inline efter sektionstabellen. Var och en är nio big-endian-huvudord, sedan dess poster:
åtta byte förskjutning och storlek, föregångna av åtta fler som namnger paket och blobb när postens
flaggbyte har sin översta bit satt. Kontroll: på varje bundle slutar den sista posten exakt där
flaggbyten börjar.

### Vilken tabell är nivån

En nivå kan ha flera tabeller med samma namn: en i basspelets `Data`, en i varje uppdatering
(`Update/<pack>/Data`) som levererar eller ändrar den, och en i varje högupplöst paket
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Bara några innehåller bundles. För en nivå
som en uppdatering levererar har tabellen i basspelet bara chunkar och inga bundles, och den i
uppdateringen är nivån; att ta första tabellen som hittas exporterade ingenting av den.

Så nivån är tabellen med flest bundles, där ett senare lager vinner ett lika (basspelet först, sedan
uppdateringarna i namnordning), och tabellerna med samma namn utan bundles är dess **tillägg**: deras
chunkar läggs till nivåns, för de håller texturernas största mips. En texturhuvud anger den chunken vid
+164 (se [Texturer och material](#textures-and-materials)). `levels` skriver ut var varje nivå kommer från
och hur många tillägg den har.

## Bundle-manifest

En bundles första post är dess manifest, lagrat okomprimerat. Det är det binära bundle-formatet från tidigare
Frostbite-spel med en ny magi, `0xD68E799D`: räknare, SHA-1, ebx- och res-poster (namnoffset och storlek),
res-typer, metadata och id:n, chunk-GUID:er, strängar. Bundlens övriga poster är ebx, res och chunkar, i den
ordningen. Kontroll: räknarna stämmer med posterna på varje bundle, och strängarna börjar där posterna slutar.

Resurstyper är hashar. `0x49B156D4` är MeshSet (varje res av den typen heter `..._mesh`), `0x6BDE20BA` Texture,
`0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` läser allt detta för en nivå, på några sekunder: en nivå har tiotals bundles och tiotusentals
ebx-, res- och chunk-poster.

## Nyttolastblock

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

En komprimerad storlek på noll betyder lagrat, så länge det packas upp till samma.

| Metodord | Kodek |
|---|---|
| `0x0070`, `0x0071` | ingen |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), från spelets egen `oo2core`-DLL) |
| annat, med lika storlekar | kopieras som lagrat |
| annat | vägras |

Läst från rätt paket avkodas varje nyttolast som togs prov på.

## EBX-partitioner

EBX håller allt som inte är rådata. Varje partition är en RIFF-fil: `EBXD` (datan, justerad till 16), `EFIX`
(partitions-GUID, typ-GUID:er och signaturer, instans, pekare, importer och typinformationens förskjutningar,
importer, och förskjutningarna för arrayer, boxade värden och strängar), `EBXX` (arraytabellen: förskjutning,
antal, hash, flaggor, elementtyp). Ett pekarfält är åtta byte: noll är null, ett udda värde är importnummer
`value >> 1`, annars är det relativt fältet.

**Typbiblioteket går inte att läsa.** Spelet levererar det i sitt initiala filsystem, som är krypterat, och
detta paket rör det inte. Typer känns igen på GUID och signatur, som varje partition bär, och de få typer
nivåexporten behöver lades ut från datan.

## MeshSet

Ett mesh är en MeshSet-res (beskrivningen) och en chunk per detaljnivå (buffrarna).

| Del | Layout |
|---|---|
| prefix | fyra ord: huvudstorlek (176 eller 192), storlek på nivåpost (176 till 188), storlek på sektionspost (368), 0 |
| huvud | begränsningslåda; sex i64-nivåförskjutningar; mesh-typ vid `0x6C` (rigid, skinned, composite); antal nivåer och sektioner vid `0x9C` |
| nivå | sektioner vid `+0x08`; fem ritlistor vid `+0x14` (ogenomskinlig, genomskinlig, dekal, bara djup, skugga); indexformat `+0x54` (`0x21` u16, `0x2E` u32), index- och vertexbyte; chunk-GUID vid `+0x74` |
| sektion | materialnamn; vertexsteg; trianglar, första index, vertexförskjutning (byte), antal vertexar vid `+0x20`; vertexdeklaration vid `+0x64`: 16 x (användning, format, förskjutning,ström), 16 stegs-strömmar, räknare |
| chunk | vertexbufferten, sedan indexbufferten. En sektions strömmar följer på varandra, och index räknas från sektionens första vertex |

Positioner är användning 1, ström 0, förskjutning 0, som fyra halvord eller tre floats.
Bara de ogenomskinliga och genomskinliga sektionerna ritas. Varje sektion med namnet `..._shadow` ligger i
skuggslistan och bara där, så det är listorna som avgör.

Kontroll: varje mesh i en nivå vars nivåer lagras i chunkar avkodas, och nästan alla har 99 % eller mer av sina
vertexar inom deklarerad låda; resten missar med halvflyttalsavrundning. En avkodad låda mäter ungefär en
meter, Y uppåt, med normaler som pekar utåt.

## Placering

Innehållspipelinen samlar en undervärldens statiska objekt i en **statisk modellgrupp**: en array av medlemmar,
en per mesh, var och en med sina instanstransformer.

| Typ (GUID, signatur) | Layout |
|---|---|
| medlem `ad13064e…`, `0xF861A878` | 224 byte: `+88` array av transformer, `+112` objektblueprinten (import), `+160` mesh-tillgången (import) |
| transform `101dce06…`, `0x5E6D8C37` | 64 byte: höger, upp, framåt, translation, var och en en vec3 utfylld till 16 |

Partitionen för mesh-tillgången heter som dess MeshSet-res, så importens partitions-GUID ger meshen. En punkt
hamnar på `x·right + y·up + z·forward + translation`. Gruppens egen transform var identiteten i varje grupp
i de kontrollerade nivåerna, och tillämpas inte.

Kontroll: i en nivå löser varje medlem i varje grupp till ett mesh; de flesta kopior har en rotation med
determinant 1 till en tusendel, resten är skalade eller speglade. Typ-GUID:erna och signaturerna är desamma i
andra nivåer. En spelsuppdatering som ändrar layouten ändrar signaturen, och läsaren hittar då ingenting i
stället för att läsa fel.

### Objekt placerade ett i taget

Det pipelinen inte kan gruppera — förstörbara objekt, containrar, skräp — placeras av **objektreferenser** och
**prefabreferenser** i nivåns partitioner:

| Typ (GUID, signatur) | Layout |
|---|---|
| objektreferens `a9a6a6ad…`, `0xC4856BEC` | `+32` transformen (som ovan), `+112` objektblueprinten (import) |
| prefabreferens `117c746e…`, `0xDE3FE9B4` | detsamma; blueprinten är en prefab, en partition med fler referenser |

Prefabs kapslar; en kopia hamnar på sin egen transform gånger sin förälders (radvektorer), ner till åtta nivåer.
En objektblueprint ritas som de meshar den importerar, utan de förstörda tillstånden (`dc_...`). En grupperad
prefab refereras som sin `..._nongroupable_autogen`-rest, så ingenting ritas två gånger.

Gången startar bara från nivåns världar och lager. En partition vars första instans är en prefab-blueprint
(`134919fc…`, `0x0247807D`) är en prefabs definition, och en nivå håller många under sin egen mapp, placerade
av sina världar på andra sätt än dessa referenser; gången från dem som om de vore en värld lägger deras
innehåll vid deras lokala koordinater. Det staplar hundratals kopior kring världens origo, långt under marken.
Världar och lager har `a10ebe0f…`, `0xD3D16C3C` först.

Blueprints som tagits ut ur spelet följs inte: utvecklings- och testtillgångar (`game/dev/`, `test/`), slutrundans
filmsekvens set (`..._gameend_...`: staplat under marken) och dödskamerans styrenhet (`.../deathflow/...`, vars
gadgets står i världens origo). De känns igen på tillgångens sökväg, inte sitt lager: samma lager som håller
filmsetet kan placera en nivås riktiga väggar och tak. Efter båda reglerna ligger ingen kopia i de kontrollerade
nivåerna mer än 10 m under terrängen, och kopiorna står på terrängen där spelet visar dem.

**Detaljnivåer som står in.** En mesh sista detaljnivå kan byta till en stand-in för distansvyn med ett eget material:
`M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Ett gittertorn med tiotusentals trianglar kan sluta i en
silhuett på några hundra, som budgeten skulle välja och som nära håll är en fast spik. En detaljnivå som
introducerar ett sådant material, ett som dess finaste nivå inte har, väljs aldrig; meshens grövsta är den sista
riktiga.

## Terräng

Källa: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Terrängen är en TerrainStreamingTree-res (typ `0x22FE8AC8`) och de chunkar den namnger.

| Del | Layout |
|---|---|
| huvud | 34 byte; nodantalet vid 25 |
| rastraträd | en typbyte och ett u32-längdfält var, tills en typbyte `0xFF`. Typ 0 är höjdfältet: sampel per sida vid +5 (265), höjdintervall vid +21 (1 280 m), terrängkvadraten i dess första nodpost vid +77 (8 192 m i den kontrollerade nivån). Den håller nodernas begränsningslådor och en 16 x 16 min/max-pyramid per nod, inte höjderna |
| streaming-noder | kvadtreet, djupet först: chunkstorlek och GUID; en valfri andra chunk; en flaggbyte (bit 0: chunken börjar med en höjdsida); har-barn. Barn i ordningen (0,0), (1,0), (1,1), (0,1) |
| höjdsida | de första 265 x 265 u16 i en flaggad nods chunk, rad för rad; höjd = värde x 1 280 / 65 535 m; kolumner längs x, rader längs z, från nodens låga hörn; en kant på 4 sampel, så 256 celler per nod |

Varje steg kontrollerades för sig:

- Nodkvadtreets parsning förbrukar resen till sista byten, med de deklarerade 529 noderna.
- Grannnoder delar sina nio kantkolumner exakt, så steget är 256.
- En barnnods sampel vid varannan position är exakt lika med förälderns med en kant på 4, och
  ligger 90 till 700 enheter från med någon annan kant.
- Det lägsta ordet i nivån avkodas till den lägsta höjden i begränsningslådan till centimetern.
- Av de åtta sätt kvadraten kan ligga på världen är det bara x längs x och z längs z som sätter de placerade
  objekten på den: hälften av de samplade kopiorna inom cirka 2 m, mot flera gånger så mycket för varje annat sätt.

De placerade objekten mäter sedan resultatet. Varje kopias lägsta punkt, mot terrängen under den (bilinjärt,
från den finaste noden):

| Placerat | Medianavstånd | Signerad median |
|---|---|---|
| träd och buskar | väl under en meter | strax under ytan |
| rekvisita | en eller två meter | på ytan |
| stenar | cirka en meter | insjunkna med cirka en meter |
| byggnader | flera meter (de står på grunder) | något insjunkna |

Växtlighet placeras på marken och ingenstans annars, vilket gör det till den skarpaste kontrollen: dess origon
ligger med median 0,07 m från ytan. Byggnader sprider sig brett, eftersom kategorin rymmer väggar, golv och
delar av flervånings- och underjordiska byggnader. Att förskjuta terrängen 64 m åt sidan sänker andelen kopior
inom 0,5 m från 29 % till 10 %.

`level` ritar höjdfältet som `ground:terrain`, varje del av det från den finaste noden med höjder där och inte
finare än `--ground-spacing` (4 m som standard: 3,7 miljoner trianglar för den kontrollerade nivån, vars
finaste noder är 0,5 m). Delar med olika upplösning möts med små steg; ingenting sys ihop dem.

En nods chunk bär också sidorna för lagermaskerna efter dess höjdsida, och dess andra chunk slutar med nodens
färgkarta (se [Terränglager](#terrain-layers)).

## Terränglager

Spelet skuggar terrängen nära en spelare genom att splatta ytmaterial med avmålade masker, med en färgkarta
över dem, och ritar dekaler (vägar, asfaltslappar, landningsbanemarkeringar) ovanpå. Frostbites egen beskrivning
av systemet (Widmark, "Terrain in Battlefield 3", GDC 2012) räknar upp terrängens rastrar som höjdfältet,
shader-splattingmasker, en färgkarta "used as an overlay on top of shader splatting", fysikmaterial, en
förstörelsedjupmask, en albedokarta för studsljus och extra maskkanaler; en rasters kakel bär en kant för
renderingsalgoritmerna. Strömningsträdet i de kontrollerade nivåerna har sju rastraträd, typade 0, 1, 2, 4, 5, 7
och 8, vars huvuden börjar med deras kakelstorlek: 265 för höjdfältet (typ 0) och typ 2, 72 eller 66 för masker
(typ 1), 132 med en kant på 2 för färgkartan (typ 4), 260 med en kant på 2 för typ 5.

**Lagerlistan.** Terrängens `....layergraphs`-res listar en 32-byte-post per lager, i den ordning maskposterna
numrerar dem (34 poster, 34 depot-sektioner och lagerindex 0 till 33 i en nivå); varje posts id slutar med dess
sektionsnyckel i lagergrafens shader-blockdepå (`....layergraphs_shaderblockdepot`), vars block namnger lagrets
kartor: en `_cv`-färgkarta, `_nhs`- och `_ao`-kartor per yta, plus delade detalj- och brusmappar. Många lager
namnger inga kartor alls: de är källor som lagergrafen läser. Ett lagers färg är dess `_cv`-kartas medelvärde;
skalan för upprepningen hittas inte.
Terrängtillgången slutar med en femtebyte-post per lager (en byte, sedan ett u32-lagerindex eller -1).

**Maskerna.** Rastraträd 1 är maskernas kvadtree. Dess kropp börjar med 59 byte, sidan för sidan vid 0: 72 där
sidorna är BC4 (72 x 72, 2 592 byte), 66 där de är okomprimerade åttabitars (4 356 byte). Sedan kommer en grupp
per nod, djupet först:

| Del | Layout |
|---|---|
| grupp | u16; u16 postantal; u32 sidantal; posterna; en nollbyte. En grupp utan poster är 7 byte i sin helhet |
| post | 33 byte: u16 lager, u16 hash, kvadrantens låda (fyra floats), två flaggbyten, ett 85-bitars närvarandepyramid |

En grupps poster är hennes nods fyra kvadranter, lager för lager, varje lagers kvadranter i ordningen (0, 0),
(1, 0), (1, 1), (0, 1). En post med den andra flaggan satt täcker sin kvadrant helt och har ingen sida; en utan
den har nästa sida; en kvadrant utan post för ett lager som dess grupp namnger är tom för det lagret; den första
flaggan är klar exakt när lagret fortsätter i kvadrantens egen grupp, en nivå ner, som ersätter den där. Sidantalet
är antalet poster med en sida.

Sidorna: en strömmande nods egna gruppsidor följer i dess chunk, höjdsidan, en 4 358-byte 16-bitarssektion och en
67 x 67 åttabitars raster (från chunkens början när den saknar höjdsida); dess andra chunk håller sidorna för de
fyra kvadranternas grupper en nivå ner, kvadranterna i färgkartans ordning, och sedan färgkartan. En sida är
kvadrantens 64 x 64 texeler, rader längs z och kolumner längs x, med en kant kopierad från grannarna: 4 texeler på
en BC4-sida, 1 på en okomprimerad.

Kanterna bevisar placeringen utan omdöme: två sidor av ett lager sida vid sida måste bära varandras kanttexeler.
`read_masks` kontrollerar det för varje par den placerar och vägrar en nivå där färre än 99 % stämmer. Ungefär en
tredjedel av de kontrollerade nivåerna läses, med sina kanter överens; några har inga målade masker; resten
vägras, nästan alla av kontrollen (deras nods chunkar håller mer än vad layouten känner till). En vägrad nivås mark
får mellanfärgen för dess ytmaterial, och exporten säger varför. Kanterna mot en full kvadrant är 255 och de mot
en tom 0.

De 4 358 byten och 67 x 67-rastern före sidorna läses inte: deras värden ligger i ett smalt högt band, utan små värden
och utan vaktvärde.

**Markens färg.** Lagergrafen blandar lagren i en kompilerad shadergraf av masker, lutning, höjd och brus, som inte
läses. `--ground-texture` färgar marken efter en egen regel, som här sägs som sådan:

- lager vars färgkarta är namngiven för avstånd är de avlägsna vyns ersättare och utelämnas;
- de texturerade lagren som täcker nio tiondelar eller mer av terrängen är basen. Deras masker är fulla nästan överallt,
  så var var och en ligger är skuggans val, inte deras: de som är namngivna för berg eller klippa färgar lutningar brantare
  än 40 grader, de som är namngivna för grus färgar plan mark (de andra basskikten när inget annat finns), blandade
  mellan 20 och 40 grader efter höjdfältets lutning (tagen var 4 m och utspridd bilinjärt över de inbakade texlerna:
  upprepad i 4 m block ritade den den klippiga färgen som hårda fläckar);
- varje annat texturerat lager läggs över basen av sin egen mask, i lagerordning;
- färgkartan läggs över resultatet så som motorn gör det, dubbelt markens färg gånger kartan, så att mellangrått lämnar den
  som den är; där färgkartan saknar texeler tar marken kartans median-ljusstyrka, i grått.

Kontrollerat mot medianmarkfärgen i spelbilder av tre nivåer (krominans som rött och blått över grönt): den inbakade
spelytan blir 1,00 / 0,69 mot bildernas 1,19 / 0,78 i en, vars gräslager är gröna där bilderna visar torrt gräs,
1,19 / 0,82 mot 1,01 / 1,04 i en annan, vars färgkarta i sig är varm (1,13 / 0,88), och 1,05 / 0,91 mot 0,93 / 0,92 i
en tredje utan färgkarta. Bilderna är belysta och graderade, så detta mäter nyansen, inte ljusstyrkan.

**Färgkartan.** En nods andra chunk håller, efter maskpyramidsidorna för dess kvadranters grupper, fyra BC7-sidor på
132 x 132 (17 424 byte var), en per nodens kvadrant, i ordningen (låg x, hög z), (hög x, hög z), (hög x, låg z),
(låg x, låg z). Maskträdet anger hur många byte maskpyramidsidorna tar, så färgkartan hittas med antal, inte med
chunkens slut: i en nivå bär de grövre noderna fyra fler sådana sidor efter den, en annan raster i en enda platt
färg, och att läsa chunkens fyra sista sidor förlorade färgkartan över nio tiondelar av terrängen. Utan det antalet
missades färgkartan också i nivåer med okomprimerade maskpyramidsidor, vars sidor inte är ett helt antal BC4-sidor;
en nivås färgkarta gick från 0,4 till 0,94 av sin terräng. Ordningen anpassades: mot kanterna på varje kvadrants
höjdfält matchar varje sida av noderna med egenskaper en kvadrant, ej vänd, med 0,3 till 0,54 där nästa bästa
placering ligger under 0,2. Sydd på det sättet sammanfogas en nivås sidor utan söm till vägarna, vattnet och de
bebyggda områdena i testnivån, på 0,5 m per texel i spelytan. Där lagren gör jobbet är färgkartan nästan neutral
(median 110, 107, 104); annars kan den bära full färg. En nivå vars andra chunkar bara håller okomprimerade maskpyramidsidor
har ingen färgkarta läst. En tidigare omgång av läsaren kallade dessa sidor icke-geografiska: den matchade dem mot
bakgrundskartan, som kan vara ett helt annat landskap, och placerade varje sida över hela sin nod i stället för en kvadrant.

**Studsljusets albedo** letades efter och hittades inte: rot- och första-nivåns nodchunkar är hela maskpyramidsidor, och
typ 5:s nyttolast hittas inte.

**Hål.** En nivås terrängtillgång (res-typ `0x1CA38E06`) namnger tre shaders: en standardytshader, en hål-ytshader och en
standardkällshader. Vilket lager hål-shadern läser hittas inte, så höjdfältet skärs inte. I en nivå kan navigeringsmeshen
ligga på bergmeshar tiotals meter under höjdfältet, där spelet måste ha skurit bort dem. Letades efter och hittades inte där:
ett lagers mask, 67 x 67-rastern, en reserverad höjd (ingen höjdsida i nivån innehåller 0 eller 65 535) och en nodflagga (varje
nod under roten har flaggan 1). Rastraträd 7 och 8 är vad som återstår. Båda är längdkodade: en byte som är lika med den före
den följs av ett antal fler kopior (`ff ff 84` är 134 byte av 255). Träd 7 (kakel 256, ett fullt kvadtree med fem nivåer, fyra bitar
per sampel) avkodas till bytepar med värden 0 till 3; träd 8 (kakel 265) till byte mest 255, med sina övriga värden i regelbundna
serier. Ingen av deras kakel är placerade än, så ingen av dem vet man håller hålen.

**Dekaler** läses och bakas; se [Terrängdekaler](#terrain-decals).

## Terrängdekaler

Källa: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Vägar, landningsbanor, betongplattor, målade linjer och bokstäver, däckspår: `TerrainDecals`-resen (typ `0x15E1F32E`)
håller dem som plan geometri som spelet drapperar över terrängen.

| Del | Layout |
|---|---|
| huvud | vid +16 ett platsantal n, sedan n 16-byte-platser, sedan postantalet |
| poster | en per ritbatch, direkt efter varandra, av varierande längd: 156 byte fasta fält — första vertex vid +32, antal trianglar vid +36, texturens upprepning i meter vid +44 — sedan batchens vertexbyte (förskjutning, storlek), sedan en svans som namnger dess texturer med deras tillgångars partitions-GUID:er |
| vertexar | 32 byte: x, z (f32), 8 packade byte, u, v (f32), r, g, b, a (f16); varje batch är en ren triangellista |
| index | u32, räknade från 0 i varje batch; behövs inte |

Kontroller:

- postens vertexintervall följer varandra utan lucka och täcker alla vertexar exakt, och varje posts första vertex x 32 är
  dess förskjutning;
- så läst är trianglarna kompakta dekaler (bokstäver, linjeremsor, lappar); läser man en vertex för lite är de skärvor över kartan;
- nästan alla batchar namnger texturer i sin svans: en färgkarta (`_cv`) med en opacitetskarta (`_op`, röd kanal), eller för
  markeringar en kanalmask (`_rgb`).

Efter texturen-GUID:erna bär svansen batchens materialparametrar, kodade så som en shader-blocks är (se Nyanser nedan). Målfärgen
för en markering, ett däckspår eller en linje är float3 med hashen `607e`: en sandig 0,64, 0,56, 0,48 för däckspår i sand, nästan
svart för tjära. Opacitetskartor är mestadels format 62, en kanal med 8 byte per block, läst som BC4.

En batch mappar sin textur antingen efter världsposition (u = x, v = z, texturen upprepas var tiling-meter: asfalt, betong, grus) eller
0 till 1 över dekalen (en linje, en bokstav, ett däckspår). Poster ritas i filordning.

**Bakningen.** `level --ground-texture M` målar, under dekalernas utsträckning och kakel på högst 4 096 pixlar, bakgrundens färgkarta
(bilinjärt) och sedan varje batch över den efter dess opacitet gånger vertexalfan. Vertexarnas färg används inte: vissa batchars vertexar
är rent gröna eller blå, vilket färgade en nivås markeringar i de färgerna. Höjdfältets trianglar där blir `ground:terrain x<x> z<z>`-delar
som bär kakeln. Varje batch ritas med:

| Batchen namnger | Ritas som |
|---|---|
| en färgkarta (`_cv`) | kartan, efter dess opacitetskarta |
| en multiplikationskarta (`_mult`) och en opacitetskarta | färgen (vit där materialet inget namnger) gånger multiplikationskartan, efter opacitetskartan: en landningsbanas slitna mittlinje, kantlinjer och tröskelbalkar |
| en kanalmask (`_rgb`) | färgen, annars vitt för linjer och bokstäver, mörkt för konturer, en svag mörkning för slitage, däckspår, fläckar, pölar och fuktighet, efter masken |
| enbart en opacitetskarta, med en färg | färgen efter opacitetskartan: däckspår |

En vägvariationsmask är inte färg utan varierar ytan under den, hundratals meter över, och ritas inte, vad den än har för färg:
målad vit lade den två bleka rektanglar 150 till 250 m långa på en nivås sluttningar. `_mult`-kartan tas som färgens eget slitage,
inte som en mörkning av marken under den: den är nästan vit, och linjens form finns i opacitetskartan.

Nästan varje batch ritas, i några få kakel på 0,5 m per pixel; exporten växer med några MB och tar några sekunder till. Sett uppifrån
ligger plattorna, taxibanorna och vägnätet under anläggningarnas stängsel och byggnader och leder in i deras grindar.

Ritas de i stället som geometri för sig, skulle dekalerna behöva alfablandning, som skrivaren inte bär, och en förskjutning ovanför en
terräng skulle slåss med den om ytan; bakning håller dem i markens egen färg.

## Texturer och material

Källa: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

En Texture-res (typ `0x6BDE20BA`) är ett 180-byte huvud: typ och pixelformat vid +8, bredd och höjd vid +22, antal mips vid +30,
chunk-GUID:n vid +40, femton mipstorlekar vid +56. Chunken är mipkedjan, största först. Vissa chunkar saknar sina största mips, som
levereras i ett högupplöst paket, och chunkens längd säger vilken mip den börjar vid. Det paketets chunk namnges vid +164; den läses
från nivåns [tillägg](#which-table-is-the-level) när en mip som huvudchunken saknar efterfrågas, och dess längd plus huvudchunkens är
hela kedjan.

| Format | Avkodas som | Belägg |
|---|---|---|
| 67, 66 | BC7 (sRGB, linjärt) | en plastig tanks färgark avkodas som den; som BC3 är samma bytes brus |
| 61, 60 | BC3 | ett lådark avkodas rent som BC3, inte som BC1 eller BC7 |
| 57, 56, 55 | BC1 | en halv byte per pixel |

Meshtillgången anger ingen textur. Länken finns i nivåns **shader-blockdepåer** (res-typ `0x73312045`, en per undervärld),
nycklade av de åtta byten vid +0x130 i en meshsektions post:

| Del | Layout |
|---|---|
| tabell, vid 16 | (sektionsnyckel u64, deskriptorförskjutning u64), tills en förskjutning ligger utanför resen |
| deskriptor | (blockförskjutning u64, hash u64, blockstorlek u64) |
| block | sektionens shaderparametrar; varje textur är en 49-byte-post: en byte, 16 byte, texturtillgångens partitions-GUID, dess instans-GUID |

Lådans sektionsnyckel finns en gång i var och en av de tio depåerna för de undervärldar som placerar den, och dess block namnger
`t_mil_crate_03_cs` och `_nmt` bland de delade detaljkartorna. Ett block namnger varje textur shadern samplar, och vilken som är
färgkartan anges inte, så den väljs: en sRGB-2D-textur vars namn innehåller de flesta orden i materialets namn
(`M_ConcreteWall_01`: concrete, wall), sedan i meshens, sedan en som inte är en detalj-, dekal- (`t_de_...`) eller skadekarta,
sedan den som färre block använder. En vägskylts block namnger sin panel `t_com_highwaysignage_01_cs` och ett dekalark
`t_de_com_highwaysignage_01_ca` med en skylt liggande på sidan; båda matchar orden, och utan dekalregeln vann arket på användning
och skylten visade skylten vriden en kvarts varv, genom varje texturkoordinatuppsättning sektionen har. Signerade avståndsfält
(`..._sdf`), paletter och kanalmasker (`_rgb`) väljs aldrig, vilka ord de än delar (`_rgba`-kartor väljs: de flesta är färg med
en alfa, och att utelämna dem bytte en kraftledning och en trappas egna kartor mot orelaterade). En bakgrunds växtlighetsatlas
`..._atlas_a_sdf` ritad som färg visade svarta och vita stjärnor för träd, en bakgrunds byggnadspalett ett konfetti av färgprov för
väggar, och glasskärvor ritade genom sin kanalmask blev cyan. En sektion vars enda kandidater är delade detaljkartor förblir platt färgad.

**Paletter.** En bakgrunds byggnader tar sina färger från en palett, 256 x 256 texeler av 16 x 16 färgprov: varje vertex bär fyra byte
(användning `0x1E`) vars första två säger var i paletten dess färg ligger, x och y av 255. `level` ritar en sådan sektion med paletten
som sin textur, varje vertex i mitten av sitt färgprov. Så ritad blir en nivås bakgrundsblock pastellväggar, terrakotta och mörka fönster
där de var vit.

**Överlägg.** Stora objekt tilelägger ett trimark genom deras första texturkoordinater och lägger ett överlägg över det genom den andra,
som ligger inom 0 till 1: en upplåsning av hela objektet. Överlägget (`..._overlay_cs`, med sin mask `..._overlay_a`) bär hur objektet ser ut
på avstånd, en oljetanks röda band och rost; ritat med trimarket ensamt blev en nivås tankar grå paneler. En sektion vars block namnger ett
överlägg med dess mask, och vars andra koordinater är en sådan upplåsning, ritas med överlägget genom dem (36 sektioner i den nivån).

**Nyanser.** Många färgkartor är gråa (deras kanalers medelvärden inom 6 % av varandra): shadern målar dem med färger från blockets
parametrar. Efter sina texturposter (49 byte var) listar ett block sina parametrar, var och en en typtagg (`f11af825` en float3, `a5e1f2de` en
float4, `c1b1a014` en float, `4a4fc3a1` ett heltal), flaggbyten `01 80` för ett värde, en tvåbytes hash av parameterns namn, ett u32-antal, värdet
och ett åttabyte-id. Namnen lagras inte. Sju float3-namnhashar fungerar som nyanser: i en nivå håller tre av dem en färg i ungefär 1 block av 6 vars
karta är grå och nästan aldrig där kartan har färg själv, och de andra håller de färger en grå karta målas i där materialets namn säger det (en broes
`..._blue`-list: 0,047, 0,098, 0,171 mot en neutral 0,5). En familj kan hålla flera värden, ett per kanal i en mask, de flesta neutrala, och ett värde med en kanal
nära ingenting (ren grön på tegelfasader) väljer en maskkanal snarare än målar. `level` multiplicerar en grå färgkarta, i linjärt ljus, med varje familjs första
värde som varken är neutralt eller en sådan väljare, över dess neutrala, och behåller resultatet som en egen textur; en karta med färg lämnas som den är.
Regeln är exportörens egen: vilken kanal i en mask som tar vilken nyans läses inte. I en nivå sänkte den andelen strukturtrianglar ritade nära vitt
från 19,4 % till 3,9 %.

**Objektvariationer.** Ett mesh placeras i flera utseenden: en lagervägg med en röd eller blå rand och ett annat nummer målat på sig, en container i grönt
eller grått. Varje placerad kopia namnger sitt utseende:

| Var | Fält |
|---|---|
| statisk modellgruppsmedlem | +32: en array av en pekare per kopia, till en objektvariation eller null |
| objektreferens | +120: en pekare till en objektvariation eller null |
| objektvariation (`ov_...`-partition, typ `235f2a9c...`) | dess första instans +32: variationens u32-namnhash |

En sektions utseende i en variation är shader-blocket nyckat av sektionens egen nyckel med variationens hash adderad till dess första fyra byte,
som ett little-endian u32 (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); en sektion utan block under den nyckeln ser likadan ut i
varje variation. Nivåns meshvariationsdatabaser (`meshvariationdb_win32`) listar, per mesh och variationshash, de material varje variation berör,
men inte nycklarna. Regeln hittades från nycklarna själva och gäller för varje sektion med varianter som kontrollerats (de fyra variationerna av en vägg,
tre av dess sektioner vardera). En variations block tar med sina egna texturer såväl som sina nyanser: det målade numret på väggen är ett bokstavsark
som variationens block namnger. En stor andel grupperade kopior placeras i en variation.

Ett block bakas en gång för varje uppsättning innehåll, och depåns post för en nyckel bär en hash av dem (det andra u64:et i posten). Där en sektion
saknar block under sin variations nyckel når variationen ändå fram via en *tvilling*: en annan sektion vars standardblock har samma innehåll och har ett.
Utan tvillingar kan en vägg vars längder delar ett standardblock hamna i två färger. En sektion utan egen variant tar den variant de flesta av dess tvillingar har.

**Sönderslagbara meshar.** Ett mesh som en match kan slå ner har en förstörelsetillgång med sitt eget namn bredvid sig (`.../br_x.destruction` för
`.../br_x_mesh`): de brytbara byggnaderna och väggarna (`br_`) och många rekvisita. `level` håller deras ytor i delar för sig, namngivna med
` (destructible)`, vars glTF-noder bär `{"destructible": true}`. Deras förstörda tillstånd är `dc_..._part<N>_mesh`-meshen bredvid dem, var och en
centrerad på sin egen origo; var en del sitter finns i förstörelsetillgången, som inte läses, så de förstörda tillstånden exporteras inte.

**Utelämnat.** Sektioner av platshållande blockouts-material (`M_Whitebox`: några stora otexturerade trianglar som vissa byggnader har bredvid sina
ytor, som stack ut ur en nivå som vita fenor), meshar gjorda för filmsekvenser (en helikopter placerad där dess scen börjar) och belysningshjälpare (plan
som blockerar ljus, aldrig ritade). En nivås genererade bakgrundsbyggnader (`..._generated_blueprints_..._mesh`) ritas, men deras väggars materialnamn
bär bara brusmappar och deras vertexar har ingen färg, så de förblir vanliga. Nästan varje ritad sektion får en färgkarta.

**Bokstavsark.** Ett väggs målade nummer eller en kranreklams affisch är en egen sektion vars färgkarta är ett ark (`_ca`): en bokstavs alfa över fast färg, eller
ett tryck. Dess första texturkoordinater tilelägger väggens puts över panelen (u -0,2 till 1,7 på en vägg), vilket ritar arket nästan två gånger; den fjärde uppsättningen
(`0x24`, annars den tredje, `0x23`) lägger det exakt en gång (u -1 till 0, v 1 till 2, några tusendelar över i de grövre detaljnivåerna). Där den första uppsättningen
lämnar en kopia av bilden och den fjärde eller tredje ligger inom en, ritas arket genom den, flyttat till 0 till 1. Ett ark med alfa ritas 1 cm framför ytan det är målat på,
som ritas under det i blockets andra färgkarta genom den första uppsättningen: utan det visade arkets tomma texeler insidan av väggen. Den andra uppsättningen är ett objekts upplåsning för dess överlägg och används inte här.

**Utklippskartor.** Färgkartans fjärde kanal betyder olika saker efter kartans namn. I `_cs` är den, med god marginal den vanligaste (893 av en nivås valda kartor),
smidighet: 1 % av en median-kartas alfa ligger inom 0,1 från 0 eller 1. I `_cu` (löv, gräs) och `_ca` (färg och alfa) är den opacitet: 90 % och 87 %. En färgkarta
namngiven `..._cu` eller `..._ca` vars alfa ligger minst 75 % nära 0 eller 1, minst 1 % under 0,5 och minst 5 % över skrivs med sin alfa, som PNG, och
dess material som glTF `alphaMode` MASK, `alphaCutoff` 0.5, dubbelsidigt; lövkort visar då löv, inte deras svarta hörn. En trädlövkarta har ingen alfa alls
(4 av 255 högst): dess blad klipps av geometri, och med bara de två första villkoren skars hela kronan bort.

Texturkoordinater är vertexanvändning `0x21`, två halvord (format 6) eller två floats (format 2). Sektioner bär upp till tre fler uppsättningar (`0x22` till `0x24`)
för dekal- och detaljlager. Koordinaterna upprepas: en containers räfflade sida går från -1,6 till 1,8, terrängbakgrundens kakel ligger helt utanför 0..1, och i en nivå
når 23 % av de texturerade trianglarna utanför 0..1. De skrivs som de är, med en upprepande sampler; 3DHeat-visaren lindar varje upprepande textur i sin atlas.
En renderare som klämmer dem i stället smetar ribborna till dubbel bredd, vänder en betonggolv till strimmor längs en axel, och ger ett tornets stålbalkar kantfärgen
på sin textur; för den klipper `--clamped-uvs` varje triangel längs linjerna där dess textur upprepas och flyttar varje bit in i 0..1 (se [Utdataformat](output-format.md)).
Därefter är 0,03 % av de texturerade trianglarna, över vilka en textur upprepas mer än 16 gånger, utanför, och en triangel som klippningen skulle göra fler än
4 bitar av ritas i texturens medelfärg i stället: bark upprepas nedför varje gren, och klippt gick en nivås träd från 6,4 till 24 miljoner trianglar.

Höjdfältet har ingen egen färgkarta som kan läsas. Där en av terrängbakgrundens kartor täcker det färgas det från den: bakgrundens texturkoordinater är en linjär
funktion av världens x och z (99 % av dess vertexar inom 0,001 från den, kartan täcker en 65 536 m kvadrat, vriden ett kvarts varv), och samma funktion ger höjdfältets.
Nivån levererar den kartans mips från 2 048 px och neråt, så höjdfältet får 32 m per pixel. Dess mörka berg ligger på den branta marken: korrelationen mellan mörker och
lutning är 0,48, och högst 0,34 för de sju andra orienteringarna.

En annan nivås bakgrund är åtta nära och åtta fjärran kakel runt spelytan, vart och ett upprepar sin egen textur över kaklet, och ingen når höjdfältet. Varje bakgrundstextur
passas för sig, och när ingen täcker höjdfältet tar den medelfärgen bakgrunden visar inom en kilometer från terrängkvadraten, vilken `--ground-texture` bakar dekalerna över.
Ett bakgrundsmaterial är ett vars namn innehåller `TerrainBackdrop`, eller `BD_` och `Terrain` (`M_BD_<site>_Terrain..._Near`); eller en bakgrundsmesh
(`bd_..._terrain<site>_04_far_mesh`) bär ett vanligt terrängmaterial (`M_<region>_Terrain<site>_04_Far`), vilket de två första reglerna missade i en nivå och därför färgade dess mark från dess ytor i stället.

Där ingen bakgrundskarta täcker höjdfältet tar det i stället mellanfärgen för terrängens egna ytor före bakgrundens medelvärde: färgkartorna `_cv` som dess lagergrafs shader-block
namnger (27 i en nivå: sand, grus, jordar, gräs, sprucken betong), vart och ett medelvärdesbildat, sedan medianen av varje kanal, utan motorns standardyta. En bakgrund kan vara ett helt annat landskap:
i en nivå vände dess medelvärde (95, 99, 80 i sRGB) spelytans mark till en grå som spelet inte visar. Med `--ground-texture` multipliceras den färgen med två gånger färgkartan, vilket lämnar mellangrått som det är, och bakas med dekalerna över både dekalernas och färgkartans utsträckning.

Mot spelet, medianmarkfärgen för varje nivås inbakade spelyta och för spelbilder (rader 55 till 72 % av bilden bredvid HUD:en, 24 bilder vardera; sRGB; bilderna är belysta och graderade, så
förhållandena r/g och b/g är den rättvisa jämförelsen):

| Nivå | Bilder | Bakgrundens medelvärde | Nu |
|---|---|---|---|
| första | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| andra | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| tredje | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Den första är rättad; de andra två låg lite närmare i nyans förut. En färg för en hel nivå kan inte vara rätt överallt; maskerna skulle kunna det.

## Navigeringsmesh

Källa: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

En nivå levererar en partition per agent, `<level>/dbt/<level>_navmesh_layer_<n>`: i en nivå är lager 0 soldaten (1,8 m hög, 0,18 m
steg, 0,4 m radie) och två andra är fordon (3,5 och 10 m höga). Varje partition håller två arrayer:

| Array | Element |
|---|---|
| tiles | 28 byte: u32 0, u32 hash, u32 0, u32 chunkindex, u16 kakel x, u16 kakel z, u32 förskjutning, u32 storlek |
| chunks | 20 byte: chunkens GUID, u32 storlek |

Ett kakel är `size` byte vid `offset` i chunken `chunk index`, little-endian, och ligger ut som Detours (Recast Navigation) bakom ett längre
huvud:

| Förskjutning | Innehåll |
|---|---|
| 0 | `VAND`, version 7 |
| 24 | räknare: polygoner, vertexar, länkar, detaljmeshar, detaljvertexar, detaljtrianglar, avgränsningsvolymsnoder, off-mesh-länkar, den första off-mesh-polygonen |
| 188 | agentens höjd, steg, radie |
| 200 | kakelns avgränsningslåda, sex floats |
| 232 | vertexar: x, y, z floats, världskoordinater |
| nästa 8-bytesgräns | polygoner, 32 byte: u32, sex u16 vertexindex, sex u16 grannar, u16 flaggor, vertexantalet vid +30, vid +31 arean (låga sex bitar) och slaget (övre två) |
| sedan, packat | länkar (16 byte), detaljmeshar (12: första detaljvertex u32, första detaljtriangel u32, vertex- och triangelantal u8), detaljvertexar (tre floats), detaljtrianglar (tre index och flaggor), avgränsningsvolymsnoder (16), off-mesh-länkar (80) |

I varje kakel i de kontrollerade nivåerna summerar dessa till kakelns storlek till sista byten, och detaljmeshen numrerar polygonerna före den första off-mesh-polygonen.

En polygon är plan mellan sina hörn; dess **detaljmesh** håller ytans verkliga höjd över puckel, stenar och trappsteg, och det är den som ritas. En detaljtriangels
index under polygonens hörnantal är det hörnet, annars detaljvertex `first + index - corners`. Att vifta polygonerna i stället lägger många fler trianglar under
terrängen och ger långa skärvor; med detaljmeshen är ingen längre än ett 16 m kakels diagonal plus steget upp för en sluttning.

Art 0 är mark, art 2 små branta lappar (cirka 45 grader, en kvadratmeter var), art 1 en länk mellan ytor: dess hörn spänner över 125 m höjd eller mer och ligger utanför kaklet,
några vid origo. Länkar utelämnas; resten ritas av sina detaljmeshar, eller viftas i ett kakel utan någon.

Kontroller: chunkarnas storlekar summerar exakt till kakelns; varje ytvertex ligger inom sitt kakels låda, ±cirka en meter; nästan alla trianglar pekar uppåt. Ett kakel som
misslyckas vägras och räknas, och i den nivån vägras inget.

Det soldatens mesh täcker, sett uppifrån i testnivån: marken, golv, trappor och några tak, och inte toppen av frakt containrar. Det är AI:ns karta över var en soldat kan stå, det närmaste filerna kommer var spelare står.

## Ej implementerat

- Terrängens lagergraf, som blandar dess ytlager (se [Terränglager](#terrain-layers)): markens färg följer en regel från läsarens egen från lagrens masker och höjdfältets lutning, och nivåer vars maskpyramidsidor inte passar ihop får en enda färg.
- Dekalmaterialens färgparametrar: markeringar genom kanalmasker målas i en neutral färg.
- Objektblueprints som inte är meshar (spellogik, effekter, ljud).
- Förstörda tillstånd för sönderslagbara meshar: deras delars platser finns i förstörelsetillgången, som inte läses.
- Navigeringsmeshens länkar (hopp, stegar, klättringar) och dess fordonslager.
- Mesh-nivåer lagrade inline i resen (10 meshar i en nivå, gadgets), skinnade och sammansatta meshars ben och delar, och normaler (beräknas av skrivaren).
- Normal-, ojämnhets- och andra kartor; alfa utöver utklippskartor (genomskinligt glas och dekaler ritas ogenomskinliga).
- Terränghål: ett hål-ytshader är namngivet, men vad det läser är inte funnet (se [Terränglager](#terrain-layers)), så höjdfältet skärs inte där den gångbara marken går under det.
- Vilken nyans som hör till vilken kanal i ett materials mask: en grå färgkarta tar den första nyansen som inte är neutral (se [Texturer och material](#textures-and-materials)).
- Effekter (`fx/`-sökvägar) och kabelmeshar, vars begränsningslådor är tiotals kilometer långa; de utelämnas och räknas i sammanfattningen.
- Det XOR-förvrängda tabellformatet.
