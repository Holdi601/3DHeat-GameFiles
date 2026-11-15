---
title: "Frostbite: `.toc`, `.cas`, bunter, meshes og nivåer"
lang: "no"
source: reader-frostbite.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, bunter, meshes og nivåer

**Leser et Battlefield 6-nivå helt ned til terrenget, de plasserte meshene og deres fargekart, og skriver det som en `.glb`.**
Frostbite-spill (Battlefield, Need for Speed, Dead Space) holder innholdet sitt i `.cas`-blobber, beskrevet av
`.toc`-innholdsfortegnelser. Et nivås tabell sier hvilke bunter nivået laster, buntene navngir hver ressurs, og
ressursene sier hvilket mesh som står hvor.

Kilder:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabeller, pakker, nyttelast),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bunter og deres manifester),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX-partisjoner),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(høydefelt),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(teksturer og materialer),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(plassering og eksport).
Kommandoer: `identify`, `levels`, `level` (se [Kommandoer](commands.md#levels-and-level-frostbite)).

Spillet dokumenterer ingenting av dette selv. Hvert oppsett nedenfor er lest av filene og så holdt mot alle filene,
og hver seksjon sier hva kontrollen var. Der Frosty-modding-verktøyene beskriver eldre versjoner av en struktur,
følger feltnavnene deres; ingen kode er tatt fra dem (se [Regler og lisenser](rules-and-licences.md)).

## Headeren som ser kryptert ut, men ikke er det

| Magi (u32, little-endian) | Betydning | Håndtert |
|---|---|---|
| `0x00CED100` | vanlig: treet begynner med en gang | leses |
| `0x01CED100` | signert: en 556 byte stor signatur, deretter treet **i klartekst** | leses |
| `0x03CED100` | XOR-tilslørt, med nøkkelen i filens egen header | oppdaget og avvist |

Den signerte formen er det nyere Battlefield leverer. De høyentropi-bytene etter magien er en signatur, ikke
chiffertekst.

## DbObject-treet

Én rekursiv struktur. Hvert felt er en typebyte (de fem nederste bitene er typen, bit 7 er "anonym"), et valgfritt
navn, og en verdi. Containere bærer sin lengde som et variabelt langt heltall og avsluttes med en nullbyte.
`parse_toc` sjekker lengden til hver container, så en fil som parser, er forstått. `layout.toc` er i denne formen.

## Installasjonspakker

Hver lokasjon nevner **installasjonspakken** dens blob hører til. Hver pakke nummererer sine blober fra `cas_01`, så
blobnummeret alene er tvetydig så snart mer enn én pakke er installert, og det er alltid mer enn én.

- `layout.toc` lister pakkene under `installManifest.installChunks`, hver med en `persistentIndex` og en
  `installBundle` som `Win32/installation/<package>`.
- Pakkens blober ligger i den mappen, under `Data` for hovedspillet eller under `Update/<pack>/Data` for det som kom
  senere.
- En lokasjonspost bærer den fulle 32-biters `persistentIndex`: den nedre halvdelen av det første ordet holder den
  øvre halvdelen, den øvre halvdelen av det andre ordet den nedre halvdelen; den nedre halvdelen av det andre ordet
  er blobnummeret.

Kontroll: hver lokasjon i hver binære tabell i en installasjon løses til en deklarert pakke, og havner innenfor blobben
den nevner. En tidligere versjon tok den første `cas_NN.cas` med riktig nummer. En tredjedel av nyttelastene den leste,
så da ut som høyentropi og ble tatt for kryptering. De var riktige forskyvninger i feil fil. Ingenting som ble funnet, er
kryptert.

## Nivåtabellen

Et nivås tabell (`levels/<level>/<level>.toc`) er en seksjonstabell: femten store-endian headerord, deretter seksjoner
lagt ende mot ende, der forskyvningene både er oppgitt og kan utledes fra to tall.

| Seksjon | Innhold |
|---|---|
| bunter | en hashtabell (ett ord hver), deretter en 16 byte stor post per bunt: nøkkel, `0x40000000` \| størrelse, 0, forskyvning |
| chunk-hashtabell | ett ord per chunk |
| chunks | 16 byte id (chunkens GUID **med byte-rekkefølgen snudd**), deretter et ord: `0x80000000` \| 4 x indeksen til lokasjonen |
| lokasjoner | fire store-endian ord: pakke (delt), blob, forskyvning, størrelse |

Chunk-idene og lokasjonene er i **forskjellige rekkefølger**. Leses de i filens rekkefølge, pares hver chunk med en
annen chunks bytes, som dekoder helt fint (for det meste som lyd), og så ser de heller ikke feil ut før et mesh kommer
ut som støy. Kontroll: i et nivå er indeksordene en permutasjon av 0 til antall chunks minus én.

Buntene er lagret innebygd etter seksjonstabellen. Hver er ni store-endian headerord, deretter sine poster: åtte byte
forskyvning og størrelse, foran åtte byte til som navngir pakke og blob når postens flaggbyte har sin øverste bit satt.
Kontroll: på hver bunt slutter den siste posten nøyaktig der flaggbytene begynner.

### Hvilken tabell er nivået

Et nivå kan ha flere tabeller med samme navn: én i hovedspillets `Data`, én i hver oppdatering (`Update/<pack>/Data`)
som leverer eller endrer det, og én i hver høyoppløselig pakke (`Update/<pack>/Data/Win32/installation/detail/<package>/...`).
Bare noen av dem har bunter. For et nivå som en oppdatering leverer, har tabellen i hovedspillet bare chunks og ingen
bunter, og tabellen i oppdateringen er nivået; å ta den første tabellen som ble funnet, eksporterte ingenting av det.

Så nivået er tabellen med flest bunter, der et senere lag vinner ved uavgjort (hovedspillet først, deretter oppdateringene
i navnerekkefølge), og tabellene med samme navn uten bunter er dets **tillegg**: deres chunks legges til nivåets, for de
holder de største mipene av teksturene. En teksturheader nevner den chunken ved +164 (se [Teksturer og materialer](#textures-and-materials)).
`levels` skriver ut hvor hvert nivå kommer fra, og hvor mange tillegg det har.

## Bunt-manifester

En bunts første post er manifestet, lagret ukomprimert. Det er det binære buntformatet fra tidligere Frostbite-spill med
ny magi, `0xD68E799D`: antall, SHA-1-er, ebx- og res-poster (navneforskyvning og størrelse), restyper, metadata og id-er,
chunk-GUID-er, strenger. De øvrige postene i buntene er ebx, res og chunks, i den rekkefølgen. Kontroll: antallene stemmer
med postene i hver bunt, og strengene starter der postene slutter.

Ressurstyper er hasher. `0x49B156D4` er MeshSet (hver res av den typen heter `..._mesh`), `0x6BDE20BA` Texture,
`0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` leser alt dette for ett nivå, på noen få sekunder: et nivå har titalls bunter og titusenvis av ebx-, res-
og chunk-poster.

## Nyttelastblokker

```
[dekomprimert størrelse : 4] [metode : 2] [komprimert størrelse : 2]    big-endian
```

En komprimert størrelse på null betyr lagret, så lenge det dekomprimerer til det samme.

| Metodeord | Kodek |
|---|---|
| `0x0070`, `0x0071` | ingen |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), fra spillets egen `oo2core`-DLL) |
| annet, med like størrelser | kopiert som lagret |
| annet | avvist |

Lest fra riktig pakke dekoderes hver nyttelast som ble samplet.

## EBX-partisjoner

EBX holder alt som ikke er rå data. Hver partisjon er en RIFF-fil: `EBXD` (dataene, justert til 16), `EFIX` (partisjons-GUID,
type-GUID-er og signaturer, instans-, peker-, import- og typeinfo-forskyvninger, importer, og forskyvningene til arrayene, de
boksede verdiene og strengene), `EBXX` (arraytabellen: forskyvning, antall, hash, flagg, elementtype). Et pekerfelt er åtte
byte: null er null, en oddetallsverdi er importnummer `value >> 1`, og alt annet er relativt til feltet.

**Typebiblioteket kan ikke leses**. Spillet leverer det i sitt startfilsystem, som er kryptert, og denne pakken rører det ikke.
Typer kjennes igjen på GUID og signatur, som hver partisjon bærer, og de få typene nivåeksporten trenger, er lagt ut fra dataene.

## MeshSet

Et mesh er en MeshSet-res (beskrivelsen) og én chunk per detaljnivå (bufferne).

| Del | Oppsett |
|---|---|
| prefiks | fire ord: headerstørrelse (176 eller 192), størrelse på nivåpost (176 til 188), størrelse på seksjonspost (368), 0 |
| header | omsluttende boks; seks i64-nivåforskyvninger; meshtype ved `0x6C` (stiv, skinnet, sammensatt); antall nivåer og seksjoner ved `0x9C` |
| nivå | seksjoner ved `+0x08`; fem tegnelister ved `+0x14` (ugjennomsiktig, gjennomsiktig, dekal, bare dybde, skygge); indeksformat `+0x54` (`0x21` u16, `0x2E` u32), indeks- og hjørnebyte; chunk-GUID ved `+0x74` |
| seksjon | materialnavn; hjørnestride; trekanter, første indeks, hjørneforskyvning (byte), antall hjørnepunkter ved `+0x20`; hjørneoppsett ved `+0x64`: 16 x (bruk, format, forskyvning, strøm), 16 strømstrider, antall |
| chunk | hjørnebufferen, deretter indeksbufferen. En seksjons strømmer følger hverandre, og indekser teller fra seksjonens første hjørnepunkt |

Posisjoner er bruk 1, strøm 0, forskyvning 0, som fire halvflytende eller tre flyttall. Bare de ugjennomsiktige og
gjennomsiktige seksjonene tegnes. Hver seksjon som heter `..._shadow`, er i skyggelisten og bare der, så listene avgjør.

Kontroll: hvert mesh i et nivå der nivåene er lagret i chunks, dekoderes, og nesten alle har 99 % eller mer av sine
hjørnepunkter innenfor sin deklarerte boks; resten bommer med halvflytende avrunding. En dekodet kasse måler omtrent en meter,
Y opp, med normalene pekende utover.

## Plassering

Innholdspipelinen samler de statiske objektene i hvert delområde i en **statisk modellgruppe**: en matrise med medlemmer, ett
per mesh, hver med sine instanstransformasjoner.

| Type (GUID, signatur) | Oppsett |
|---|---|
| medlem `ad13064e…`, `0xF861A878` | 224 byte: `+88` matrise med transformasjoner, `+112` objektblåkopien (import), `+160` meshressursen (import) |
| transformasjon `101dce06…`, `0x5E6D8C37` | 64 byte: høyre, opp, fremover, translasjon, hver en vec3 polstret til 16 |

Partisjonen til meshressursen er navngitt som sin MeshSet-res, så importens partisjons-GUID gir meshet. Et punkt havner på
`x·høyre + y·opp + z·fremover + translasjon`. Gruppens egen transformasjon var identiteten i hver gruppe i de nivåene som ble
sjekket, og brukes ikke.

Kontroll: i et nivå løses hvert medlem i hver gruppe til et mesh; de fleste kopiene har en rotasjon med determinant 1 til en
tusendel, resten er skalert eller speilet. Type-GUID-ene og signaturene er like i andre nivåer. En spilloppdatering som endrer
oppsettet, endrer signaturen, og leseren finner da ingenting i stedet for å lese feil.

### Objekter plassert ett og ett

Det pipelinen ikke kan gruppere - ødeleggbare objekter, containere, rester - plasseres av **objektreferanser** og
**prefabreferanser** i nivåets partisjoner:

| Type (GUID, signatur) | Oppsett |
|---|---|
| objektreferanse `a9a6a6ad…`, `0xC4856BEC` | `+32` transformasjonen (som over), `+112` objektblåkopien (import) |
| prefabreferanse `117c746e…`, `0xDE3FE9B4` | det samme; blåkopien er en prefab, en partisjon med flere referanser |

Prefabs nestes; en kopi havner på sin egen transformasjon ganget med forelderens (radvektorer), ned til åtte nivåer. En
objektblåkopi tegnes som meshene den importerer, uten de ødelagte tilstandene (`dc_...`). En gruppert prefab refereres som sin
`..._nongroupable_autogen`-rest, så ingenting tegnes to ganger.

Gjennomgangen starter bare fra nivåets verdener og lag. En partisjon hvis første instans er en prefab-blåkopi
(`134919fc…`, `0x0247807D`) er en prefabs definisjon, og et nivå holder mange av dem under sin egen mappe, plassert av sine
verdener på andre måter enn disse referansene; gått fra som om det var en verden, legger en prefab innholdet sitt i sine lokale
koordinater. Det hoper hundrevis av kopier rundt verdenens origo, langt under bakken. Verdener og lag har `a10ebe0f…`,
`0xD3D16C3C` først.

Blåkopier satt ut av spillet følges ikke: utviklings- og testmateriell (`game/dev/`, `test/`), settet til rundens
sluttfilmsekvens (`..._gameend_...`: satt under bakken) og dødskameraets kontroller (`.../deathflow/...`, der gadgetene står i
verdenens origo). De kjennes igjen på banen i ressursstien, ikke på laget: det samme laget som holder filmsettet, kan plassere
nivåets ekte vegger og tak. Etter begge reglene ligger ingen kopi mer enn 10 m under terrenget i nivåene som ble sjekket, og
kopiene står på terrenget der spillet viser dem.

**Detaljnivåer som stiller inn.** Et meshs siste detaljnivå kan bytte til en stedfortreder for fjernsyn med et eget materiale:
`M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Et gitter-tårn med titusenvis av trekanter kan ende i en silhuett på noen
hundre, som budsjettet ville valgt, og som på nært hold er en solid spiss. Et detaljnivå som tar inn et slikt materiale, et det
fineste nivået ikke har, velges aldri; meshets groveste er det siste ekte.

## Terreng

Kilde: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Terrenget er en TerrainStreamingTree-res (type `0x22FE8AC8`) og chunkene den nevner.

| Del | Oppsett |
|---|---|
| header | 34 byte; antall noder ved 25 |
| rastertrær | en typebyte og en u32-lengde for hver, til en typebyte `0xFF`. Type 0 er høydefeltet: prøver per side ved +5 (265), høydeområde ved +21 (1 280 m), terrengfirkanten i sin første nodepost ved +77 (8 192 m i nivået som ble sjekket). Den holder nodenes omsluttende bokser og et 16 x 16 min/maks-pyramide per node, ikke høydene |
| strømmende noder | quadtreet, dybde først: chunkstørrelse og GUID; en valgfri andre chunk; en flaggbyte (bit 0: chunken starter med en høysideside); har-barn. Barn i rekkefølgen (0,0), (1,0), (1,1), (0,1) |
| høydeside | de første 265 x 265 u16 i en flagget nodes chunk, rad for rad; høyde = verdi x 1 280 / 65 535 m; kolonner langs x, rader langs z, fra nodens lave hjørne; en kant på 4 prøver, altså 256 celler per node |

Hvert steg er kontrollert for seg:

- Quadtre-gjennomgangen av nodene bruker resen til siste byte, med de deklarerte 529 nodene.
- Nabonoder deler sine ni kantkolonner nøyaktig, så steget er 256.
- Et barns prøver på hver annen posisjon er lik forelderens nøyaktig med en kant på 4, og er 90 til 700 enheter av med en hvilken som helst annen kant.
- Det laveste ordet i nivået dekoderes til den laveste høyden i den omsluttende boksen, til centimeteren.
- Av de åtte måtene firkanten kan ligge på verden, er det bare x langs x og z langs z som legger de plasserte objektene på den:
  halvparten av de samplede kopiene innen omtrent 2 m, mot flere ganger så mye for alle de andre.

De plasserte objektene måler så resultatet. Det laveste punktet på hver kopi, mot terrenget under den (bilineært, fra den
fineste noden):

| Plassert | Median avstand | Signert median |
|---|---|---|
| trær og busker | godt under en meter | like under overflaten |
| rekvisitter | en til to meter | på overflaten |
| steiner | omtrent en meter | sunket inn med omtrent en meter |
| bygninger | flere meter (de står på fundamenter) | litt sunket inn |

Vegetasjon er plassert på bakken og ingen andre steder, som gjør den til den skarpeste kontrollen: origoene dens ligger
med median 0,07 m fra overflaten. Bygninger spres mye fordi kategorien rommer vegger, gulv og byggesett for flerete og
underjordiske konstruksjoner. Å forskyve terrenget 64 m sideveis reduserer andelen kopier innen 0,5 m fra 29 % til 10 %.

`level` tegner høydefeltet som `ground:terrain`, hver del av det fra den fineste noden med høyder der og ikke finere enn
`--ground-spacing` (4 m som standard: 3,7 millioner trekanter for nivået som ble sjekket, der de fineste nodene er 0,5 m).
Deler med ulik oppløsning møtes med små trinn; ingenting sømmer dem sammen.

En nodes chunk holder også sidene med lagmasker etter høyesiden, og dens andre chunk ender med nodens fargekart (se
[Terrenglag](#terrain-layers)).

## Terrenglag

Spillet skygger terrenget nær en spiller ved å splatte tilpassede overflatematerialer etter malte masker, med et fargekart
over dem, og tegne dekaler (veier, asfaltlapper, rullebanemerker) oppå. Frostbites egen beskrivelse av systemet (Widmark,
"Terrain in Battlefield 3", GDC 2012) lister terrengets rastre som høydefeltet, skyggesplattingsmasker, et fargekart "brukt
som et overlegg oppå shader splatting", fysikkmaterialer, en ødeleggelsesdybdemaske, et albedo-kart for bounce-lys og
ekstra maskekanaler; en rasters fliser bærer en kant for gjengivelsesalgoritmene. Strømmetreet i nivåene som ble sjekket,
har syv rastertrær, av type 0, 1, 2, 4, 5, 7 og 8, der hodene begynner med flisstørrelsen: 265 for høydefeltet (type 0) og
type 2, 72 eller 66 for maskene (type 1), 132 med en kant på 2 for fargekartet (type 4), 260 med en kant på 2 for type 5.

**Lagslisten.** Terrengets `....layergraphs`-res lister én 32-byte post per lag, i den rekkefølgen maskepostene nummererer dem
(34 poster, 34 depotseksjoner og lagindekser 0 til 33 i ett nivå); hver posts id slutter med sin seksjonsnøkkel i lagdiagrammets
shaderblokk-depot (`....layergraphs_shaderblockdepot`), der blokken navngir lagets kart: ett `_cv`-fargekart, `_nhs`- og `_ao`-kart
per overflate, pluss delte detalj- og støykart. Mange lag navngir ingen kart i det hele tatt: de er kilder lagdiagrammet leser. Et lags
farge er gjennomsnittet av dets `_cv`-kart; flisskalaen finnes ikke. Terrengressursen ender med en fembyte stor post per lag
(en byte, deretter et u32-lagindeks eller -1).

**Maskene.** Rastertre 1 er maskenes quadtre. Kroppen starter med 59 byte, sidelengden til siden ved 0: 72 der sidene er BC4
(72 x 72, 2 592 byte), 66 der de er ukomprimert åttebit (4 356 byte). Deretter kommer én gruppe per node, dybde først:

| Del | Oppsett |
|---|---|
| gruppe | u16; u16 postantall; u32 sideantall; postene; en nullbyte. En gruppe uten poster er 7 byte i alt |
| post | 33 byte: u16 lag, u16 hash, kvadrantens boks (fire flyttall), to flaggbyte, et 85-biters tilstedeværelsespyramide |

En gruppes poster er nodens fire kvadranter, lag for lag, hver lags kvadranter i rekkefølgen (0,0), (1,0), (1,1), (0,1). En post med
det andre flagget satt dekker sin kvadrant hel og har ingen side; en uten det har neste side; en kvadrant uten en post for et lag
gruppen nevner, er tom for det laget; det første flagget er bare klart når laget fortsetter i kvadrantens egen gruppe, ett nivå ned,
som erstatter det der. Sideantallet er antallet poster som har en side.

Sidene: en nodes egen gruppes sider følger i sin chunk etter høyesiden, en 4 358 byte stor 16-bit seksjon og et 67 x 67 åttebits
raster (fra chunkens start når den ikke har en høyeside); dens andre chunk holder sidene til de fire kvadrantenes grupper ett nivå
ned, med kvadrantene i fargekartets rekkefølge, og så fargekartet. En side er kvadrantens 64 x 64 texeler, med rader langs z og
kolonner langs x, med en kant kopiert fra naboene: 4 texeler på en BC4-side, 1 på en ukomprimert.

Kantene beviser plasseringen uten skjønn: to sider av ett lag ved siden av hverandre må bære hverandres kanttexeler. `read_masks` sjekker
det for hvert par den plasserer, og avviser et nivå der færre enn 99 % er enige. Omtrent en tredjedel av nivåene som ble sjekket leses,
med kantene enige; noen har ingen malte masker; resten avvises, nesten alle av kontrollen (chunkene deres holder mer enn dette oppsettet
kjenner til). Bakken til et avvist nivå tar midtfargen av sine overflatematerialer, og eksporten sier hvorfor. Kantene mot en full
kvadrant er 255 og de mot en tom 0.

De 4 358 byte store seksjonen og 67 x 67-rasteret før sidene leses ikke: verdiene deres ligger i et smalt høyt bånd, uten små verdier og
uten vaktverdi.

**Bakkens farge.** Lagdiagrammet blander lagene i en kompilert shader-graf av masker, helning, høyde og støy, som ikke leses.
`--ground-texture` farger bakken etter en regel av sin egen, og sier det her som nettopp det:

- lag som har et fargekart navngitt for avstand, er stedfortrederne for fjernvisningen og utelates;
- de teksturerte lagene som dekker ni tiendedeler av terrenget eller mer, er grunnlaget. Maskene deres er fulle nesten overalt, så
  der hvert ligger, er skyggerens valg, ikke deres: de som er navngitt for stein eller klippe farger bratte skråninger brattere enn 40 grader,
  de som er navngitt for grus gir flatt terreng (de andre grunnlagene når ingen er), blandet mellom 20 og 40 grader etter høydefeltets
  helning (tatt hver 4 m og spredt bilineært over de innbakte texelene: gjentatt i 4 m-blokker tegnet det den steinete fargen som harde
  flekker);
- hvert annet teksturert lag legges over grunnlaget etter sin egen maske, i lagrekkefølge;
- fargekartet legges over resultatet slik motoren gjør det, to ganger bakkens farge ganget med kartet, så middelgrått lar det være som
  det er; der fargekartet ikke har texeler, tar bakken kartets medianlysstyrke, i gråtoner.

Kontrollert mot medianfargen av spillbilder fra tre nivåer (krom som rød og blå over grønn): det innbakte spillområdet blir 1,00 / 0,69
mot bildenes 1,19 / 0,78 i ett, der gresslagene er grønne der bildene viser tørt gress; 1,19 / 0,82 mot 1,01 / 1,04 i et annet, der
fargekartet i seg selv er varmt (1,13 / 0,88); og 1,05 / 0,91 mot 0,93 / 0,92 i et tredje uten fargekart. Bildene er belyst og
gradert, så dette måler fargetonen, ikke lysstyrken.

**Fargekartet.** En nodes andre chunk holder, etter sidene til sine kvadranters grupper, fire BC7-sider på 132 x 132 (17 424 byte hver),
én per nodens kvadrant, i rekkefølgen (lav x, høy z), (høy x, høy z), (høy x, lav z), (lav x, lav z). Maskentreet sier hvor mange byte
maskesidene tar, så fargekartet finnes ved antall, ikke ved chunkens slutt: i ett nivå bærer de grovere nodene fire flere slike sider etter
det, en annen raster i ett flatt farge, og å lese chunkens fire siste sider mistet fargekartet over ni tiendedeler av terrenget. Uten den
tellingen ble fargekartet også savnet i nivåer med ukomprimerte masker, der sidene ikke er et helt antall BC4-sider; ett nivås fargekart
gikk fra 0,4 til 0,94 av sitt terreng. Rekkefølgen ble tilpasset: mot kantene av hver kvadrants høydefelt passer hver side i nodene med
trekk til én kvadrant, uten snu, på 0,3 til 0,54 der neste beste plassering er under 0,2. Sydd sammen med den, går et nivås sider sammen
uten søm inn i veiene, vannet og bebyggelsen i testnivået, på 0,5 m per texel i spillområdet. Der lagene gjør jobben, er fargekartet nær
nøytralt (median 110, 107, 104); ellers kan det bære full farge. Et nivå der de andre chunkene bare holder ukomprimerte masker, får ikke
fargekartet lest. En tidligere runde av denne leseren kalte disse sidene ikke geografiske: den matchet dem mot bakgrunnskartet, som kan
være et helt annet landskap, og plasserte hver side på hele noden i stedet for på en kvadrant.

**Albedoen for bounce-lys** ble lett etter og ikke funnet: rot- og førstenivånodenes chunker er hele maskesider, og type 5s nyttelast
er ikke funnet.

**Hull.** Et nivås terrengressurs (restype `0x1CA38E06`) nevner tre shadere: en standard overflateshader, en hull-overflateshader og en
standard kildeshader. Hvilket lag hull-shaderen leser, er ikke funnet, så høydefeltet ikke kuttes. I et nivå kan navigasjonsmeshen ligge
på steinmeshes titalls meter under høydefeltet, der spillet må ha kuttet det bort. Ser etter det der og fant det ikke: et lags maske, det
67 x 67 rasteret, en reservert høyde (ingen høyeside i nivået inneholder 0 eller 65 535) og en nodeflagg (hver node under roten har flagg 1).
Rastertre 7 og 8 er det som gjenstår. Begge er kjøringskodet: en byte lik den før den følges av et antall flere kopier (`ff ff 84` er 134 byte
med 255). Tre 7 (flis 256, et fullt quadtre med fem nivåer, fire bit per prøve) dekodes til bytepar med verdier 0 til 3; tre 8 (flis 265) til
bytes for det meste 255, med sine andre verdier i jevne serier. Ingen av dem sine fliser er plassert ennå, så ingen av dem er kjent for å holde hullene.

**Dekaler** leses og bakes; se [Terrengdekaler](#terrain-decals).

## Terrengdekaler

Kilde: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Veier, rullebaner, betongplattformer, malte linjer og bokstaver, dekkmerker: `TerrainDecals`-resen (type `0x15E1F32E`) holder dem som
flat geometri spillet drapperer over terrenget.

| Del | Oppsett |
|---|---|
| header | ved +16 et sporantall n, deretter n 16-byte spor, deretter postantallet |
| poster | én per tegnebatch, etter hverandre, av varierende lengde: 156 byte faste felt - første hjørnepunkt ved +32, trekantantall ved +36, teksturflislegging i meter ved +44 - deretter batchens hjørnebyte (forskyvning, størrelse), og en hale som navngir teksturene med deres ressursers partisjons-GUID-er |
| hjørnepunkter | 32 byte: x, z (f32), 8 pakkede byte, u, v (f32), r, g, b, a (f16); hver batch en ren trekantliste |
| indekser | u32, telt fra 0 i hver batch; ikke nødvendig |

Kontroller:

- postenes hjørneområder følger hverandre uten hull og dekker alle hjørnepunktene nøyaktig, og hver posts første hjørnepunkt x 32 er dens forskyvning;
- lest slik, er trekantene kompakte dekaler (bokstaver, linjestrimler, flekker); lest ett hjørnepunkt av gangen, er de flis over kartet;
- nesten alle batcher navngir teksturer i halen sin: et fargekart (`_cv`) med et opasitetskart (`_op`, rød kanal), eller for merkinger et kanalmaske (`_rgb`).

Etter tekstur-GUID-ene bærer halen batchens materialparametere, kodet slik en shaderblokks er (se Toninger under). Malingsfargen til en merking,
et dekkspor eller en linje er float3-en hashet `607e`: en sandfarget 0,64, 0,56, 0,48 for dekkspor i sand, nesten svart for tjære. Opasitetskart
er for det meste format 62, én kanal på 8 byte per blokk, lest som BC4.

En batch kartlegger sin tekstur enten etter verdensposisjon (u = x, v = z, teksturen gjentas hver flislagte meter: asfalt, betong, grus) eller
0 til 1 over dekalet (en linje, en bokstav, et dekkspor). Poster tegnes i filens rekkefølge.

**Bakingen.** `level --ground-texture M` maler, under dekalenes utstrekning og i fliser på høyst 4 096 piksler, bakgrunnens fargekart (bilineært), og
deretter hver batch over det etter sin opasitet x hjørnets alfa. Hjørnepunktenes farge brukes ikke: noen batcher har rene grønne eller blå hjørnepunkter,
som farget et nivås merkinger i de fargene. Høydefeltets trekanter der blir til `ground:terrain x<x> z<z>`-deler som bærer flisen. Hver batch tegnes med:

| Batchnavn | Tegnes som |
|---|---|
| et fargekart (`_cv`) | kartet, etter sitt opasitetskart |
| et multiplikasjonskart (`_mult`) og et opasitetskart | malingen (hvit der materialet ikke navngir noen) ganget med multiplikasjonskartet, etter opasitetskartet: en rullebanes slitte midtlinje, kantlinjer og terskelstolper |
| et kanalmaske (`_rgb`) | malingen, ellers hvitt for linjer og bokstaver, mørkt for konturer, en svak mørkning for slitasje, dekkmerker, flekker, pytter og fuktighet, etter masken |
| et opasitetskart alene, med en maling | malingen etter opasitetskartet: dekkspor |

Et veiens variasjonsmaske er ikke maling, men varierer underlaget under den, hundrevis av meter bredt, og tegnes ikke, uansett maling: malt hvit la
den to blekke rektangler på 150 til 250 m lengde i et nivås skråninger. `_mult`-kartet tas som malingens egen slitasje, ikke som en mørkning av
underlaget under den: det er nesten hvitt, og linjens form ligger i opasitetskartet.

Nesten hver batch tegnes, inn i noen få fliser på 0,5 m per piksel; eksporten vokser med noen få MB og tar noen sekunder mer. Sett ovenfra ligger
flyplassens plattformer, rullebaner og veinettet under anleggenes gjerder og bygninger, og fører inn til portene deres.

Tegnet som geometri i stedet, ville dekaler krevd alfablanding, som skriveren ikke bærer, og en forskyvning over et terreng ville kjempet med det
om hver piksel; bakingen beholder dem i bakkens egen farge.

## Teksturer og materialer

Kilde: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

En Texture-res (type `0x6BDE20BA`) er en 180 byte stor header: type og pikselformat ved +8, bredde og høyde ved +22, antall mipmaps ved +30,
chunk-GUID-en ved +40, femten mipstørrelser ved +56. Chunken er mip-kjeden, største først. Noen chunker mangler sine største mipper, som ligger i en
høyoppløselig pakke, og chunkens lengde sier hvilken mip den starter på. Den pakkens chunk er navngitt ved +164; den leses fra nivåets
[tillegg](#which-table-is-the-level) når en mip som hovedchunken mangler, trengs, og dens lengde pluss hovedchunkens er hele kjeden.

| Format | Dekodet som | Bevis |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineær) | et plasttanks fargeark dekoderes som det; som BC3 er de samme bytene støy |
| 61, 60 | BC3 | et kasseark dekoderes rent som BC3, ikke som BC1 eller BC7 |
| 57, 56, 55 | BC1 | en halv byte per piksel |

Meshressursen navngir ingen tekstur. Koblingen står i nivåets **shaderblokk-depoter** (restype `0x73312045`, ett per delområde), nøklet med de åtte
byte ved +0x130 i et meshsnittets post:

| Del | Oppsett |
|---|---|
| tabell, ved 16 | (seksjonsnøkkel u64, deskriptorforskyvning u64), til en forskyvning faller utenfor resen |
| deskriptor | (blokkforskyvning u64, hash u64, blokkstørrelse u64) |
| blokk | seksjonens shaderparametere; hver tekstur er en 49 byte stor post: en byte, 16 byte, teksturressursens partisjons-GUID, dens instans-GUID |

Kasse-seksjonens nøkkel står én gang i hvert av de ti depotene til delområdene som plasserer den, og blokken navngir `t_mil_crate_03_cs` og `_nmt` blant
de delte detaljkartene. En blokk navngir hver tekstur shaderen samplerer, og hvilken som er fargekartet, står ikke; den velges derfor: en sRGB 2D-tekstur
hvis navn har de fleste ordene i materialets navn (`M_ConcreteWall_01`: concrete, wall), deretter meshets, deretter en som ikke er en detalj-, dekal-
(`t_de_...`) eller skadekart, deretter den som færrest blokker bruker. En veiskilts blokk navngir sitt panel `t_com_highwaysignage_01_cs` og et dekalark
`t_de_com_highwaysignage_01_ca` med en skjold liggende på siden; begge passer ordene, og uten dekalregelen vant arket på bruk, og skiltet viste skjoldet
vridd en kvart, gjennom alle teksturkoordinatsettene seksjonen har. Signerte avstandsfelt (`..._sdf`), paletter og kanalmasker (`_rgb`) velges aldri,
uansett hvilke ord de deler (`_rgba`-kart gjør det: de fleste er farge med alfa, og å utelate dem byttet en kraftledning og en trapps egne kart mot
urelaterte). Et bakgrunnstreets vegetasjonsatlas `..._atlas_a_sdf`, tegnet som farge, viste svarte og hvite stjerner for trær, en bakgrunnsbygnings
palett ga et konfetti av fargeprøver på vegger, og glassrester tegnet gjennom sin kanalmaske kom ut cyan. En seksjon der de eneste kandidatene er delte
detaljkart, forblir flatt farget.

**Paletter.** En bakgrunnsbygnings farger hentes fra en palett på 256 x 256 texeler med 16 x 16 fargeprøver: hver hjørnepunkt bærer fire byte (bruk `0x1E`)
der de to første sier hvor i paletten fargen ligger, x og y av 255. `level` tegner en slik seksjon med paletten som sin tekstur, med hvert hjørnepunkt i midten
av sin fargeprøve. Tegnet slik, kommer et nivås bakgrunnsblokker ut som pastellvegger, terrakotta og mørke vinduer der de var ren hvit.

**Overlegg.** Store objekter fliser et trimsett gjennom sine første teksturkoordinater, og legger et overlegg over det gjennom de andre, som ligger innenfor
0 til 1: en utfolding av hele objektet. Overlegget (`..._overlay_cs`, med sin maske `..._overlay_a`) bærer hvordan objektet ser ut på avstand, en oljetanks røde
bånd og rust; tegnet med trimsettet alene, kom tankene i ett nivå ut som grå paneler. En seksjon der blokken navngir et overlegg med sin maske, og der dens
andre koordinater er en slik utfolding, tegnes med overlegget gjennom dem (36 seksjoner i det nivået).

**Toninger.** Mange fargekart er grå (kanalenes gjennomsnitt innenfor 6 % av hverandre): skyggeren maler dem med farger fra blokkens parametere. Etter sine
teksturposter (49 byte hver) lister en blokk sine parametere, hver en typekode (`f11af825` en float3, `a5e1f2de` en float4, `c1b1a014` en float, `4a4fc3a1` et
heltall), flaggbytene `01 80` for én verdi, en to-byte hash av parameterens navn, et u32-antall, verdien og en åtte-byte id. Navnene lagres ikke. Sju float3-navnhasher
virker som toninger: i ett nivå holder tre av dem en farge i omtrent 1 blokk av 6 der kartet er grått og nesten aldri der kartet har farge selv, og de andre holder
fargene et grått kart males i der materialets navn sier det (en broes `..._blue`-list: 0,047, 0,098, 0,171 mot en nøytral 0,5). En familie kan holde flere verdier,
én per kanal i en maske, de fleste nøytrale, og en verdi med en kanal nær ingenting (ren grønn på murfasader) velger en maskes kanal i stedet for å male. `level`
multipliserer et grått fargekart, i lineært lys, med hver families første verdi som verken er nøytral eller en slik velger, over dens nøytrale, og beholder resultatet
som en egen tekstur; et kart med farge lar stå. Regelen er eksportørens egen: hvilken kanal i en maske som får hvilken toning, leses ikke. I ett nivå tok den andelen
strukturtrekanter tegnet nær hvitt fra 19,4 % til 3,9 %.

**Objektvariasjoner.** Ett mesh plasseres i flere utseender: en lagervegg med en rød eller blå stripe og et annet nummer malt på seg, en container i grønt eller grått.
Hver plassert kopi navngir sitt utseende:

| Hvor | Felt |
|---|---|
| medlem i statisk modellgruppe | +32: en matrise med én peker per kopi, til en objektvariasjon eller null |
| objektreferanse | +120: en peker til en objektvariasjon eller null |
| objektvariasjon (`ov_...`-partisjon, type `235f2a9c...`) | dens første instans +32: variasjonens u32-navnehash |

En seksjons utseende i en variasjon er shaderblokken nøklet med seksjonens egen nøkkel med variasjonens hash lagt til dens fire første byte, som et little-endian
u32 (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); en seksjon uten blokk under den nøkkelen ser lik ut i hver variasjon. Nivåets
variasjonsdatabaser (`meshvariationdb_win32`) lister, per mesh og variasjonshash, materialene hver variasjon berører, men ikke nøklene: regelen ble funnet fra
nøklene selv og holder for hver seksjon med varianter som er kontrollert (de fire variasjonene til én vegg, tre av dens seksjoner hver). En variasjons blokk
tar med sine egne teksturer i tillegg til sine toninger: tallet malt på veggen er et bokstavark som variasjonens blokk navngir. En stor del av de gruppede kopiene
er plassert i en variasjon.

En blokk bakes én gang for hvert sett med innhold, og depotets oppføring for en nøkkel bærer en hash av dem (den andre u64-en i oppføringen). Der en seksjon ikke har
en blokk under sin variasjons nøkkel, når variasjonen den likevel gjennom en *tvilling*: en annen seksjon hvis standardblokk har samme innhold og har en. Uten tvillinger
kan en vegg hvis lengder deler én standardblokk, komme ut i to farger. En seksjon uten egen variant tar varianten de fleste av tvillingene har.

**Ødeleggbare meshes.** Et mesh en kamp kan slå ned, har en ødeleggelsesfil av sitt eget navn ved siden av seg (`.../br_x.destruction` for `.../br_x_mesh`): de
ødeleggbare bygningene og veggene (`br_`) og mange rekvisitter. `level` holder deres overflater i egne deler, navngitt med ` (destructible)`, hvis glTF-noder bærer
`{"destructible": true}`. Deres ødelagte tilstander er `dc_..._part<N>_mesh`-meshene ved siden av dem, hver sentrert på sitt eget origo; hvor en del står, ligger i
ødeleggelsesfilen, som ikke leses, så de ødelagte tilstandene eksporteres ikke.

**Utelatt.** Seksjoner med plassholdermaterialet for blokkering (`M_Whitebox`: noen få store, utexturerte trekanter som noen bygninger beholder ved siden av sine
overflater, og som stod ut av et nivå som hvite finner), meshes laget for filmsekvenser (en helikopter plassert der scenen starter) og lyshjelpere (plan som blokkerer
lys, og aldri tegnes). Et nivås genererte bakgrunnsbygninger (`..._generated_blueprints_..._mesh`) tegnes, men veggenes materialnavn bare støykart, og hjørnepunktene
bærer ingen farge, så de blir værende vanlige. Nesten hver tegnet seksjon får et fargekart.

**Bokstavark.** En veggs malte nummer eller en krans' reklameplakat er en seksjon for seg selv, der fargekartet er et ark (`_ca`): en bokstavs alfa over solid maling,
eller et trykk. Dens første teksturkoordinater flisløgger veggens puss over panelet (u -0,2 til 1,7 på én vegg), som tegner arket nesten to ganger; det fjerde settet
(`0x24`, ellers det tredje, `0x23`) legger det på nøyaktig én gang (u -1 til 0, v 1 til 2, noen tusendeler over i de grovere detaljnivåene). Der det første settet
etterlater ett eksemplar av bildet, og det fjerde eller tredje ligger innenfor ett, tegnes arket gjennom det, flyttet inn i 0 til 1. Et ark med alfa tegnes 1 cm foran
flaten det er malt på, som tegnes under det i blokkens andre fargekart gjennom det første settet: uten det viste arkets tomme texeler innsiden av veggen. Det andre
settet er et objekts utfolding for sitt overlegg og brukes ikke her.

**Utskjæringskart.** Fargekartets fjerde kanal betyr forskjellige ting etter kartets navn. I `_cs`, den klart vanligste (893 av ett nivås valgte kart), er den glatthet:
1 % av et median kart sin alfa ligger innenfor 0,1 av 0 eller 1. I `_cu` (løv, gress) og `_ca` (farge og alfa) er den opasitet: 90 % og 87 %. Et fargekart navngitt
`..._cu` eller `..._ca` der minst 75 % av alfaen er nær 0 eller 1, minst 1 % er under 0,5 og minst 5 % er over, skrives med sin alfa, som PNG, og dets materiale som
glTF `alphaMode` MASK, `alphaCutoff` 0,5, dobbeltsidig; løvkort viser da løv, ikke sine svarte hjørner. Ett tres løvkart har ingen alfa i det hele tatt (høyst 4 av 255):
dens kvister kuttes av geometri, og med bare de to første betingelsene ble hele kronen kuttet bort.

Teksturkoordinater er bruk `0x21`, to halve ord (format 6) eller to flyttall (format 2). Seksjoner bærer opptil tre sett til (`0x22` til `0x24`) for dekal- og detaljlag.
Koordinatene flislegges: en containers ribbede side går fra -1,6 til 1,8, bakgrunnsterrengets fliser ligger helt utenfor 0..1, og i ett nivå når 23 % av de teksturerte
trekantene utenfor 0..1. De skrives som de er, med en gjentakende sampler; 3DHeat-visningen pakker hver gjentakende tekstur inn i sitt atlas. En tegner som klemmer dem i
stedet, smører ribbene ut til to ganger sin bredde, gjør et betonggulv til striper langs én akse, og gir et tårns stålbjelker deres teksturs kantfarge; for den kuttes
hver trekant langs linjene der teksturen gjentas, og hver bit flyttes inn i 0..1 med `--clamped-uvs` (se [Utdataformat](output-format.md)). Deretter ligger 0,03 % av de
teksturerte trekantene, der teksturen gjentas mer enn 16 ganger, utenfor, og en trekant kuttingen ville gjort til mer enn 4 biter, tegnes i sin teksturs gjennomsnittsfarge
i stedet: bark gjentas nedover hver gren, og kuttet gikk et nivås trær fra 6,4 til 24 millioner trekanter.

Høydefeltet har ikke noe eget fargekart som kan leses. Der ett av bakgrunnsterrengets kart dekker det, farges det av det: bakgrunnens teksturkoordinater er en lineær
funksjon av verdens x og z (99 % av hjørnepunktene innenfor 0,001 av den, og kartet dekker en 65 536 m firkant, dreiet en kvart), og den samme funksjonen gir høydefeltets.
Nivået leverer det kartets mipper fra 2 048 px og ned, så høydefeltet får 32 m per piksel. Dens mørke stein ligger på den bratte bakken: korrelasjonen mellom mørke og
helning er 0,48, og høyst 0,34 for de syv andre orienteringene.

Et annet nivås bakgrunn er åtte nære og åtte fjerne fliser rundt spilleområdet, hver med sin egen tekstur som gjentas over flisen, og ingen når høydefeltet. Hver
bakgrunnstekstur tilpasses for seg, og når ingen dekker høydefeltet, tar den gjennomsnittsfargen bakgrunnen viser innenfor en kilometer fra terrengfirkanten, som
`--ground-texture` baker dekalene over. Et bakgrunnsmateriale er et hvis navn inneholder `TerrainBackdrop`, eller `BD_` og `Terrain` (`M_BD_<site>_Terrain..._Near`);
eller et bakgrunnsmesh (`bd_..._terrain<site>_04_far_mesh`) bærer et vanlig terrengmateriale (`M_<region>_Terrain<site>_04_Far`), som de to første reglene bommet på i ett
nivå og derfor farget bakken ut fra overflatene i stedet.

Der ingen bakgrunnskart dekker høydefeltet, tar det likevel midtfargen av terrengets egne overflater før bakgrunnens gjennomsnitt: `_cv`-fargekartene som nivåets
lagdiagram-shaderblokker navngir (27 i ett nivå: sand, grus, jord, gress, sprukket betong), hver gjennomsnittet, deretter medianen av hver kanal, med motorens standardoverflate
utelatt. En bakgrunn kan være et helt annet landskap: i ett nivå snudde gjennomsnittet (95, 99, 80 i sRGB) spilleområdets bakke til en grå som spillet ikke viser. Med
`--ground-texture` ganges den fargen med to ganger fargekartet, som middelgrått lar stå, og bakes med dekalene over både dekalenes og fargekartets utstrekning.

Mot spillet, medianfargen til hvert nivås innbakte spilleområde og til spillbilder (rader 55 til 72 % av bildet ved siden av HUD-en, 24 bilder hver; sRGB; bildene er
belyst og gradert, så forholdene r/g og b/g er den rettferdige sammenligningen):

| Nivå | Bilder | Bakgrunnens gjennomsnitt | Nå |
|---|---|---|---|
| første | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| andre | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| tredje | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Det første er rettet; de to andre var litt nærmere i fargetone før. Én farge for et helt nivå kan ikke stemme overalt; maskene ville kunne.

## Navigasjonsmesh

Kilde: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Et nivå leverer én partisjon per agent, `<level>/dbt/<level>_navmesh_layer_<n>`: i ett nivå er lag 0 soldaten (1,8 m høy, 0,18 m trinn, 0,4 m radius) og to andre er
kjøretøy (3,5 og 10 m høye). Hver partisjon holder to matriser:

| Matrise | Element |
|---|---|
| fliser | 28 byte: u32 0, u32 hash, u32 0, u32 chunk-indeks, u16 flis x, u16 flis z, u32 forskyvning, u32 størrelse |
| chunks | 20 byte: chunkens GUID, u32 størrelse |

En flis er `size` byte ved `offset` i chunk `chunk index`, little-endian, og lagt ut som Detours (Recast Navigation) bak en lengre header:

| Forskyvning | Innhold |
|---|---|
| 0 | `VAND`, versjon 7 |
| 24 | antall: polygoner, hjørnepunkter, lenker, detaljmeshes, detaljhjørnepunkter, detaljtrekanter, nodene for omsluttende volum, utenfor-mesh-lenker, det første utenfor-mesh-polygonet |
| 188 | agenthøyde, trinn, radius |
| 200 | flisens omsluttende boks, seks flyttall |
| 232 | hjørnepunkter: x, y, z flyttall, verdenskoordinater |
| neste 8-byte-grense | polygoner, 32 byte: u32, seks u16 hjørneindekser, seks u16 naboer, u16 flagg, hjørneantallet ved +30, ved +31 området (de seks nederste bitene) og typen (de øverste to) |
| deretter, pakket | lenker (16 byte), detaljmeshes (12: første detaljhjørnepunkt u32, første detaljtrekant u32, hjørne- og trekantantall u8), detaljhjørnepunkter (tre flyttall), detaljtrekanter (tre indekser og flagg), nodene for omsluttende volum (16), utenfor-mesh-lenker (80) |

I hver flis i nivåene som ble sjekket, summerer disse seg til flisens størrelse til byten, og detaljmeshene nummererer polygonene før det første utenfor-mesh-polygonet.

Et polygon er flatt mellom sine hjørner; dets **detaljmesh** holder flatens virkelige høyde over ujevnheter, steiner og trinn, og det er det som tegnes. En detaljtrekants
indeks under polygonets hjørneantall er det hjørnet, ellers detaljhjørnepunkt `first + index - corners`. Å vifte polygonene i stedet legger mange flere trekanter under
terrenget og lager lange flak; med detaljmeshene er ingen lengre enn en 16 m flis' diagonal pluss trinnet opp en skråning.

Type 0 er bakke, type 2 små bratte flekker (omtrent 45 grader, en kvadratmeter hver), type 1 en lenke mellom flater: hjørnene spenner over 125 m høyde eller mer og ligger
utenfor flisen, noen i origo. Lenker utelates; de andre tegnes av sine detaljmeshes, eller viftes i en flis uten noen.

Kontroller: chunkenes størrelser summerer seg nøyaktig til flisenes; hvert overflatehjørne ligger innenfor sin flis' boks, gitt eller tatt omtrent en meter; nesten alle
trekanter vender oppover. En flis som ikke består, avvises og telles, og i det nivået avvises ingen.

Det soldatens mesh dekker, sett ovenfra i testnivået: bakken, gulvene, trappene og noen tak, og ikke toppene av fraktcontainere. Det er KI-ens kart over hvor en soldat kan stå,
det nærmeste filene kommer hvor spillere står.

## Ikke implementert

- Terrengets lagdiagram, som blander dets overflatelag (se [Terrenglag](#terrain-layers)): bakkens farge følger en regel fra denne leseren selv, ut fra lagenes masker og
  høydefeltets helning, og nivåer der maskesidene ikke passer sammen får én farge.
- Dekalmaterialers fargeparametere: merkinger gjennom kanalmasker males i en nøytral farge.
- Objektblåkopier som ikke er meshes (spill-logikk, effekter, lyd).
- Ødelagte tilstander til ødeleggbare meshes: deres delers plasseringer ligger i ødeleggelsesfilen, som ikke leses.
- Navigasjonsmeshets lenker (hopp, stiger, klatring) og dets kjøretøylag.
- Mesh-nivåer lagret innebygd i resen (10 meshes i et nivå, gadgeter), og skinnede og sammensatte meshes' ben og deler, og normaler (beregnet av skriveren).
- Normal-, ruhets- og andre kart; alfa annet enn et utskjæringskart (gjennomsiktig glass og dekaler tegnes ugjennomsiktige).
- Terrenghull: en hull-overflateshader er navngitt, men hva den leser er ikke funnet (se [Terrenglag](#terrain-layers)), så høydefeltet kuttes ikke der den gangbare bakken går under det.
- Hvilken toning som hører til hvilken kanal i et materials maske: et grått fargekart tar den første toningen som ikke er nøytral (se [Teksturer og materialer](#textures-and-materials)).
- Effekter (`fx/`-stier) og kabelmeshene, hvis omsluttende bokser er titalls kilometer lange; de utelates og telles i sammendraget.
- Den XOR-tilslørte tabellformen.
