---
title: Frostbite
nav_order: 5
lang: "sl"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, paketi, mreže in nivoji {#frostbite-toc-cas-bundles-meshes-and-levels}

**Prebere nivo Battlefield 6 do njegovega terena, njegovih postavljenih mrež in njihovih barvnih
zemljevidov ter ga zapiše kot `.glb`.** Igre Frostbite (Battlefield, Need for Speed, Dead Space)
hranijo svojo vsebino v blobih `.cas`, opisanih z tabelami vsebine `.toc`. Tabela nivoja pove,
kateri paketi nivo naložijo, paketi imenujejo vsako sredstvo, sredstva pa povedo, katera mreža
kje stoji.

Viri:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabele, namestitveni paketi, koristni tovori),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(paketi in njihovi manifesti),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(particije EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(višinski model),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(teksture in materiali),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(postavitev in izvoz).
Ukazi: `identify`, `levels`, `level` (glejte [Ukazi](commands.md#levels-and-level-frostbite)).

Igra tega ni dokumentirala. Vsaka postavitev spodaj je bila prebrana iz datotek in nato
preverjena na vseh datotekah, vsak oddelek pa pove, kakšen je bil preizkus. Kjer kakšna stran
opisuje starejše različice strukture, imena polj sledijo njihovim, vendar kode od tam ni
(glejte [Pravila in licence](rules-and-licences.md)).

## Glava, ki izgleda šifrirana, pa ni {#the-header-that-looks-encrypted-and-is-not}

| Oznaka (u32, little-endian) | Pomen | Obravnava |
|---|---|---|
| `0x00CED100` | navadna: drevo se začne takoj | prebrano |
| `0x01CED100` | podpisana: 556-bajtni podpis, nato drevo **v čistopisu** | prebrano |
| `0x03CED100` | XOR-zamaskirana, s ključem v glavi datoteke | zaznano in zavrnjeno |

Podpisana oblika je tista, ki jo trenutni Battlefield dostavlja. Visoko-entropijski bajti za
oznako so podpis, ne šifrirano besedilo.

## Drevo DbObject {#the-dbobject-tree}

Ena rekurzivna struktura. Vsako polje ima bajt tipa (spodnjih pet bitov je tip, bit 7 pomeni
"anonimno"), neobvezno ime in vrednost. Vsebniki nosijo svojo dolžino kot spremenljivo celo
število in se končajo z ničelnim bajtom. `parse_toc` preveri dolžino vsakega vsebnika, zato
datoteka, ki se razčleni, pomeni, da je bila razumljena. `layout.toc` je v tej obliki.

## Namestitveni paketi {#installation-packages}

Vsaka lokacija imenuje **namestitveni paket**, kateremu blob pripada. Vsak paket številči svoje
bloba od `cas_01`, zato številka bloba sama po sebi ni enoznačna takoj, ko je nameščen več kot
en paket, kar je vedno.

- `layout.toc` našteje pakete pod `installManifest.installChunks`, vsak z `persistentIndex` in
  `installBundle`, na primer `Win32/installation/<package>`.
- Bloba paketa sta v tej mapi, pod `Data` za osnovno igro ali pod `Update/<pack>/Data` za
  kasneje dodano.
- Zapis lokacije nosi polni 32-bitni `persistentIndex`: nizka polovica prve besede drži visoko
  polovico, visoka polovica druge besede pa nizko polovico; nizka polovica druge besede je
  številka bloba.

Preverjanje: vsaka lokacija v vsaki binarni tabeli namestitve se razreši v deklariran paket in
pade znotraj bloba, ki ga imenuje. Prejšnja različica je vzela prvi `cas_NN.cas` prave številke.
Tretjina njenih tovorov je bila videti visoko-entropijsko in so jih vzeli za šifriranje. Bili so
pravi odmiki v napačni datoteki. Nič najdenega ni šifrirano.

## Tabela nivoja {#the-level-table}

Tabela nivoja (`levels/<level>/<level>.toc`) je tabela oddelkov: petnajst besed glave v big-endian,
nato oddelki, položeni drug za drugim, katerih odmiki so hkrati navedeni in izpeljivi iz dveh
številk.

| Oddelek | Vsebina |
|---|---|
| paketi | razpršilna tabela (ena beseda na vsakega), nato 16-bajtni zapis na paket: ključ, `0x40000000` \| velikost, 0, odmik |
| razpršilna tabela kosov | ena beseda na kos |
| kosi | 16-bajtni ID (GUID kosa **z obrnjenim vrstnim redom bajtov**), nato beseda: `0x80000000` \| 4 x indeks njegove lokacije |
| lokacije | štiri big-endian besede: paket (razdeljen), blob, odmik, velikost |

ID-ji kosov in lokacije so **v različnih vrstnih redih**. Če se berejo po vrstnem redu v datoteki,
se vsak kos poveže z bajti drugega kosa, ki se dekodirajo čisto v redu (večinoma kot zvok), zato
se ne zdi narobe, dokler mreža ne pride ven kot šum.
Preverjanje: v nivoju so indeksne besede permutacija od 0 do števila kosov minus ena.

Paketi so shranjeni takoj za tabelo oddelkov. Vsak ima devet big-endian besed glave, nato svoje
vnose: osem bajtov odmika in velikosti, pred katerimi so še osem bajtov za paket in blob, kadar
ima zastavica vnosa nastavljen zgornji bit. Preverjanje: pri vsakem paketu se zadnji vnos konča
natanko tam, kjer se začnejo zastavični bajti.

### Katera tabela je nivo {#which-table-is-the-level}

Nivo je lahko imel več tabel z istim imenom: eno v osnovni igri `Data`, po eno v vsaki
posodobitvi (`Update/<pack>/Data`), ki ga dostavi ali spremeni, in po eno v vsakem paketu visoke
ločljivosti (`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Samo nekatere
imajo pakete. Za nivo, ki ga dostavi posodobitev, ima tabela v osnovni igri samo kose in nobenih
paketov, nivo pa je tabela v posodobitvi; vzeti prvo najdeno tabelo ni izvozilo ničesar od tega.

Torej je nivo tabela z največ paketi, pri čemer v izenačenju zmaga kasnejši sloj (najprej osnovna
igra, nato posodobitve po imenu datoteke). Tabele z istim imenom brez paketov so njegovi
**dodatki**: njihovi kosi se dodajo nivojevim, saj vsebujejo največje mipe njegovih tekstur.
Glava teksture imenuje ta kos pri +164 (glejte [Teksture in materiali](#textures-and-materials)).
`levels` izpiše, od kod prihaja vsak nivo in koliko dodatkov ima.

## Manifesti paketov {#bundle-manifests}

Prvi vnos paketa je njegov manifest, shranjen nestisnjen. Gre za binarno obliko paketa iz prejšnjih
iger Frostbite z novo oznako `0xD68E799D`: števila, zgoščene vrednosti SHA-1, zapisi ebx in res
(odmik imena in velikost), vrste res, metapodatki in ID-ji, GUID-ji kosov, nizi. Preostali vnosi
paketa so ebx, res in kosi v tem vrstnem redu. Preverjanje: števila se ujemajo z vnosi na vsakem
paketu, nizi pa se začnejo tam, kjer se zapisi končajo.

Vrste virov so zgoščene vrednosti. `0x49B156D4` je MeshSet (vsak res te vrste se imenuje
`..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` prebere vse to za en nivo v nekaj sekundah: nivo ima desetine paketov in deset
tisoče ebx, res in kosov.

## Bloki tovora {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Ničelna stisnjena velikost pomeni shranjeno, če se le-ta dekompresira v isto.

| Beseda metode | Kodek |
|---|---|
| `0x0070`, `0x0071` | brez |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), iz igrine lastne DLL `oo2core`) |
| drugo, z enakima velikostma | kopirano, kot je shranjeno |
| drugo | zavrnjeno |

Prebrano iz pravega paketa: vsak vzorčeni tovor se dekodira.

## Particije EBX {#ebx-partitions}

EBX hrani vse, kar ni surovi podatek. Vsaka particija je datoteka RIFF: `EBXD` (podatki,
poravnani na 16), `EFIX` (GUID particije, GUID-ji tipov in podpisi, odmiki instance, kazalca,
uvoza in informacij o tipu, uvozi ter odmiki tabel, tabel z vrednostmi v polju in nizov), `EBXX`
(tabela tabel: odmik, število, zgoščena vrednost, zastavice, tip elementa). Polje kazalca je
osem bajtov: nič je null, liho število je uvoz številka `value >> 1`, karkoli drugega je relativno
glede na polje.

**Knjižnica tipov ni berljiva.** Igra jo shranjuje v svojem začetnem datotečnem sistemu, ki je
šifriran, ta paket pa se ga ne dotika. Tipi so znani po GUID-ju in podpisu, ki ju ima vsaka
particija, nekaj tipov, ki jih izvoz nivoja potrebuje, pa je bilo postavljenih po podatkih.

## MeshSet {#meshset}

Mreža je res MeshSet (opis) in en kos za vsako stopnjo podrobnosti (medpomnilniki).

| Del | Postavitev |
|---|---|
| predpona | štiri besede: velikost glave (176 ali 192), velikost zapisa stopnje (176 do 188), velikost zapisa oddelka (368), 0 |
| glava | omejevalna škatla; šest i64 odmikov stopenj; vrsta mreže pri `0x6C` (togo, skinned, sestavljeno); števila stopenj in oddelkov pri `0x9C` |
| stopnja | oddelki pri `+0x08`; pet seznamov risanja pri `+0x14` (neprozorno, prosojno, nalepke, samo globina, senca); oblika indeksa pri `+0x54` (`0x21` u16, `0x2E` u32), bajti indeksov in oglišč; GUID kosa pri `+0x74` |
| oddelek | ime materiala; korak oglišč; trikotniki, prvi indeks, odmik oglišč (bajti), število oglišč pri `+0x20`; deklaracija oglišč pri `+0x64`: 16 x (uporaba, format, odmik, tok), 16 korakov toka, števila |
| kos | medpomnilnik oglišč, nato medpomnilnik indeksov. Tokovi oddelka sledijo drug drugemu, indeksi štejejo od prvega oglišča oddelka |

Položaji so uporaba 1, tok 0, odmik 0, kot štirje poli ali trije float. Riše se samo neprozorne
in prosojne oddelke. Vsak oddelek z imenom `..._shadow` je na seznamu sence in samo tam, zato
odločajo seznami.

Preverjanje: vsaka mreža nivoja, katerega stopnje so shranjene v kosih, se dekodira, skoraj vsaka
ima 99 % ali več svojih oglišč znotraj deklarirane škatle; ostala zgreši zaradi zaokroževanja
polovičnih float-ov. Dekodirana zabojnik meri približno en meter, y navzgor, z normalami, ki
kažejo navzven.

## Postavitev {#placement}

Cevovod vsebine zbere statične predmete vsakega podsveta v **skupino statičnih modelov**: polje
članov, po enega za vsako mrežo, vsak s svojimi transformacijami primerkov.

| Tip (GUID, podpis) | Postavitev |
|---|---|
| član `ad13064e…`, `0xF861A878` | 224 bajtov: `+88` polje transformacij, `+112` plan predmeta (uvoz), `+160` sredstvo mreže (uvoz) |
| transformacija `101dce06…`, `0x5E6D8C37` | 64 bajtov: desno, gor, naprej, translacija, vsak vec3 zapolnjen na 16 |

Particija uvoznega sredstva mreže se imenuje kakor njen res MeshSet, zato GUID particije uvoza
določi mrežo. Točka pristane na `x·right + y·up + z·forward + translation`. Transformacija same
skupine je bila v vsaki skupini preverjenih nivojev identiteta in se ne uporablja.

Preverjanje: v nivoju se vsak član vsake skupine razreši v mrežo; večina kopij ima rotacijo
determinante 1 na tisočinko, ostale so razširjene ali zrcaljene. GUID-ji tipov in podpisi so v
drugih nivojih enaki. Posodobitev igre, ki spremeni postavitev, spremeni podpis, bralnik pa potem
ne najde ničesar, namesto da bi jo napačno bral.

### Predmeti, postavljeni posamično {#objects-placed-one-by-one}

Kar cevovod ne more združiti, so uničljivi predmeti, zabojniki, odpadki, se postavi z **referencami
predmetov** in **referencami prefabov** v particijah nivoja:

| Tip (GUID, podpis) | Postavitev |
|---|---|
| referenca predmeta `a9a6a6ad…`, `0xC4856BEC` | `+32` transformacija (kot zgoraj), `+112` plan predmeta (uvoz) |
| referenca prefaba `117c746e…`, `0xDE3FE9B4` | enako; plan je prefab, particija nadaljnjih referenc |

Prefabi se gnezdijo; kopija pristane na svoji transformaciji, pomnoženi s transformacijo starša
(vektorji vrstic), navzdol do osmih nivojev. Plan predmeta se riše kot mreže, ki jih uvaža, brez
uničenih stanj (`dc_...`). Združen prefab se sklicuje kot svoj ostanek `..._nongroupable_autogen`,
zato se nič ne riše dvakrat.

Hoja se začne samo od svetov in slojev nivoja. Particija, katere prvi primerek je plan prefaba
(`134919fc…`, `0x0247807D`), je definicija prefaba, nivo pa jih hrani veliko pod svojo mapo, postavljenih
po svetovih na načine, ki niso te reference. Če bi se hodilo od njih, kot da so svet, bi prefab
postavil svojo vsebino na lokalne koordinate. To pa nakopiči na stotine kopij okoli izhodišča sveta,
daleč pod tlemi. Svetovi in sloji imajo `a10ebe0f…`, `0xD3D16C3C` na začetku.

Planov, ki so postavljeni izven igre, se ne sledi: razvojna in testna sredstva (`game/dev/`,
`test/`), komplet konca runde (`..._gameend_...`: postavljen pod tlemi) in kontroler kamere
smrti (`.../deathflow/...`, katerega pripomočki stojijo v izhodišču sveta). Prepoznajo se po poti
sredstva, ne po sloju: isti sloj, ki vsebuje komplet filmske scene, lahko postavi tudi prave zidove
in strehe nivoja. Po obeh pravilih nobena kopija v preverjenih nivojih ne leži več kot 10 m pod
terenom, kopije pa stojijo na terenu, kjer jih igra prikaže.

**Stopnje podrobnosti, ki nadomeščajo.** Zadnja stopnja podrobnosti mreže se lahko preklopi na
oddaljen nadomestek s svojim materialom: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`.
Rešetkasti stolp z desettisoči trikotniki se lahko konča v silhueti nekaj sto trikotnikov, ki jo
proračun izbere in ki je od blizu trdi bodič. Stopnja podrobnosti, ki prinese tak material, ki ga
njena najfinejša stopnja nima, se nikoli ne izbere; najgrobejša stopnja mreže je zadnja prava.

## Teren {#terrain}

Vir:
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Teren je res TerrainStreamingTree (tip `0x22FE8AC8`) in kosi, ki jih imenuje.

| Del | Postavitev |
|---|---|
| glava | 34 bajtov; število vozlišč pri 25 |
| drevesa rastrov | bajt tipa in u32 dolžina za vsakega, dokler bajt tipa ni `0xFF`. Tip 0 je višinski model: vzorci na stran pri +5 (265), razpon višin pri +21 (1.280 m), kvadrat terena v zapisu prvega vozlišča pri +77 (8.192 m v preverjenem nivoju). Hrani škatle vozlišč in 16 x 16 piramido min/max na vozlišče, ne višin |
| vozlišča pretakanja | kvadrantno drevo, najprej globina: velikost kosa in GUID; neobvezen drugi kos; bajt zastavic (bit 0: kos se začne s stranjo višin); ima otroke. Otroci v vrstnem redu (0,0), (1,0), (1,1), (0,1) |
| stran višin | prvih 265 x 265 u16 kosa označenega vozlišča, vrstica za vrstico; višina = vrednost x 1.280 / 65.535 m; stolpci vzdolž x, vrstice vzdolž z, od spodnjega kota vozlišča; obroba 4 vzorcev, torej 256 celic na vozlišče |

Vsak korak je bil preverjen posebej:

- Razčlenjevanje kvadrantnega drevesa vozlišč porabi res do zadnjega bajta, z deklariranimi 529
  vozlišči.
- Sosednja vozlišča si delijo svojih devet robnih stolpcev natanko, zato je korak 256.
- Vzorci otroka na vsaki drugi poziciji so natanko enaki staršu z obrobo 4, z drugo obrobo pa
  so 90 do 700 enot narazen.
- Najnižja beseda v nivoju se dekodira v najnižjo višino omejevalne škatle na centimeter natančno.
- Od osmih načinov, na katere bi se kvadrat lahko postavil na svet, samo x vzdolž x in z vzdolž z
  postavi postavljene predmete na teren: polovica vzorčenih kopij znotraj približno 2 m, proti več
  kot to za vse druge načine.

Postavljeni predmeti nato merijo rezultat. Najnižja točka vsake kopije proti terenu pod njo
(bilinearno, iz najfinejšega vozlišča):

| Postavljeno | Mediana razdalje | Predznačena mediana |
|---|---|---|
| drevesa in grmovje | dobro pod metrom | tik pod površino |
| rekviziti | meter ali dva | na površini |
| skale | okoli metra | potopljene za približno meter |
| stavbe | več metrov (stojijo na temeljih) | rahlo potopljene |

Rastlinje je postavljeno na tla in nikjer drugje, zato je najostrejše preverjanje: njegova izhodišča
sedijo na mediani 0,07 m od površine. Stavbe se široko razpršijo, ker kategorija vsebuje stene,
tla in dele opreme večetažnih in podzemnih struktur. Premik terena za 64 m v stran zmanjša delež
kopij znotraj 0,5 m z 29 % na 10 %.

`level` nariše višinski model kot `ground:terrain`, vsak njegov del iz najfinejšega vozlišča z
višinami tam in ne finejšega od `--ground-spacing` (privzeto 4 m: 3,7 milijona trikotnikov za
preverjeni nivo, katerega najfinejša vozlišča so 0,5 m). Deli različne ločljivosti se srečajo z
majhnimi stopničkami; nič jih ne stakne.

Kos vozlišča hrani tudi strani mask plasti za svojo stranjo višin, njegov drugi kos pa se konča z
barvnim zemljevidom vozlišča (glejte [Plasti terena](#terrain-layers)).

## Plasti terena {#terrain-layers}

Igra osvetli teren blizu igralca tako, da s slikanimi maskami meša površinske materiale in preko njih
položi barvni zemljevid, na vrh pa riše dekale (ceste, asfaltne krpe, oznake vzletnih stez). Frostbitov
lastni opis sistema (Widmark, "Terrain in Battlefield 3", GDC 2012) našteje rastre terena kot
višinski model, maske mešanja senčilnika, barvni zemljevid, "uporabljen kot prekrivka čez mešanje
senčilnika", fizikalne materiale, masko globine uničenja, albedo zemljevid za odboj svetlobe in
dodatne kanale mask; stran rastrov nosi obrobo za algoritme upodabljanja. Drevo pretakanja preverjenih
nivojev ima sedem dreves rastrov, tipov 0, 1, 2, 4, 5, 7 in 8, katerih glave se začnejo z velikostjo
ploščice: 265 za višinski model (tip 0) in tip 2, 72 ali 66 za maske (tip 1), 132 z obrobo 2 za
barvni zemljevid (tip 4), 260 z obrobo 2 za tip 5.

**Seznam plasti.** Res `....layergraphs` terena našteje po en 32-bajtni vnos na plast, v vrstnem redu,
v katerem jih štejejo zapisi mask (34 vnosov, 34 oddelkov dela in indeksov plasti od 0 do 33 v enem
nivoju); ID vsakega vnosa se konča s ključem njegovega oddelka v bloku senčilnika grafa plasti
(`....layergraphs_shaderblockdepot`), katerega blok imenuje zemljevide plasti: en `_cv` barvni
zemljevid, `_nhs` in `_ao` zemljevide na površino, plus skupne podrobne in šumne zemljevide. Mnoge
plasti ne imenujejo nobenih zemljevidov: so viri, ki jih bere graf plasti. Barva plasti je povprečje
njenega zemljevida `_cv`; merila popločenja ni najti. Sredstvo terena se konča s peterobajtnim
vnosom na plast (bajt, nato u32 indeks plasti ali -1).

**Maske.** Rastr 1 je kvadrantno drevo mask. Njeno telo se začne s 59 bajti, velikostjo strani pri
0: 72, kadar so strani BC4 (72 x 72, 2.592 bajtov), 66, kadar so nestisnjene osembitne (4.356
bajtov). Sledi skupina na vozlišče, najprej globina:

| Del | Postavitev |
|---|---|
| skupina | u16; u16 število zapisov; u32 število strani; zapisi; ničelni bajt. Skupina brez zapisov je v vsem 7 bajtov |
| zapis | 33 bajtov: u16 plast, u16 zgoščena vrednost, škatla kvadranta (štirje float), dva bajta zastavic, 85-bitna piramida prisotnosti |

Zapisi skupine so štirje kvadranti njenega vozlišča, plast za plastjo; kvadranti vsake plasti so v
vrstnem redu (0,0), (1,0), (1,1), (0,1). Zapis z drugo zastavico nastavljeno pokriva svoj kvadrant v
celoti in nima strani; zapis brez nje ima naslednjo stran; kvadrant brez zapisa plasti, ki jo njegova
skupina imenuje, je prazen za to plast; prva zastavica je izključena natanko tedaj, ko plast nadaljuje
v lastni skupini kvadranta, eno raven niže, ki jo tam nadomesti. Število strani je število zapisov s
stranjo.

Strani: za lastno skupino vozlišča pretakanja sledijo njegove strani v njegovem kosu, stran višin, 4.358
bajtov dolg 16-bitni oddelek in raster 67 x 67 osembitno (od začetka kosa, kadar nima strani višin); njegov
drugi kos hrani strani kvadrantov svojih skupin eno raven niže, kvadranti v vrstnem redu barvnega
zemljevida, nato barvni zemljevid. Stran je 64 x 64 texelov kvadranta, vrstice vzdolž z in stolpci vzdolž x,
z obrobo, kopirano od sosedov: 4 texeli na stran BC4, 1 na nestisnjeni. 

Obrobe dokazujejo postavitev brez presoje: dve strani iste plasti drug ob drugem morata nositi robne
texele druga drugega. `read_masks` to preveri za vsak par, ki ga postavi, in zavrne nivo, kjer se manj
kot 99 % ujema. Približno tretjina preverjenih nivojev je prebrana, z obrobami, ki se ujemajo; nekateri
nimajo slikanih mask; ostali so zavrnjeni, skoraj vsi zaradi preverjanja (kosi njihovih vozlišč imajo več,
kot ta postavitev pozna). Teren zavrnjenega nivoja vzame srednjo barvo svojih površinskih materialov,
izvoz pa pove zakaj. Obrobe ob polnem kvadrantu so 255, tiste ob prazni pa 0.

Rastra 4.358-bajtnega oddelka in 67 x 67 pred stranmi se ne bereta: njune vrednosti sedijo v ozkem
visokem pasu, brez majhnih vrednosti in brez zaznamovalca.

**Barva tal.** Graf plasti meša plasti v sestavljenem grafu senčilnikov mask, naklona, višine in šuma,
ki ni prebran. `--ground-texture` barva tla po lastnem pravilu, ki je tu navedeno kot tako:

- plasti, katerih barvni zemljevid je poimenovan za razdaljo, so nadomestki daljnega pogleda in se
  izpustijo;
- teksturirane plasti, ki pokrivajo devet desetin terena ali več, so osnova. Njihove maske so skoraj
  povsod polne, zato to, kje vsaka leži, odloči senčilnik, ne one: tiste, poimenovane za skalo ali
  pečino, obarvajo strmine nad 40 stopinj, tiste, poimenovane za gramoz, ravna tla (druge osnovne
  plasti, kadar ni nobene), in se med 20 in 40 stopinjami mešajo po naklonu višinskega modela (vzet na
  vsaka 4 m in razpršen bilinearno čez zapečene texele: ponovljen v blokih po 4 m je narisal skalno barvo
  kot trde krpe);
- vsaka druga teksturirana plast se položi čez osnovo po svoji maski, v vrstnem redu plasti;
- barvni zemljevid se položi čez rezultat tako, kot ga dela motor: dvakratna barva tal, pomnožena z
  zemljevidom, tako da srednje siva pusti vse, kakor je; kjer barvni zemljevid nima texelov, tla dobijo
  srednjo svetlost zemljevida, v sivi barvi.

Preverjeno glede na mediano barve tal zapečenega območja igre in posnetkov igre (kromatičnost kot
rdeča in modra proti zeleni) na treh nivojih: zapečeno območje igre je 1,00 / 0,69 proti posnetkom
1,19 / 0,78 v enem, katerega travne plasti so zelene, kjer posnetki kažejo suho travo; 1,19 / 0,82 proti
1,01 / 1,04 v drugem, katerega barvni zemljevid je sam topel (1,13 / 0,88); in 1,05 / 0,91 proti 0,93 /
0,92 v tretjem brez barvnega zemljevida. Posnetki so osvetljeni in obdelani, zato to meri odtenek, ne
svetlosti.

**Barvni zemljevid.** Drugi kos vozlišča hrani, za stranmi mask kvadrantov njegovih skupin, štiri strani
BC7 po 132 x 132 (po 17.424 bajtov), po eno za vsak kvadrant vozlišča, v vrstnem redu (nizek x, visok z),
(visok x, visok z), (visok x, nizek z), (nizek x, nizek z). Drevo mask pove, koliko bajtov zavzamejo strani
mask, zato se barvni zemljevid najde po številu, ne po koncu kosa: v enem nivoju imajo grobejša vozlišča za
njim še štiri take strani, drug raster v enotni barvi, in branje zadnjih štirih strani kosa je izgubilo
barvni zemljevid čez devet desetin terena. Brez tega števila je bil barvni zemljevid zgrešen tudi v nivojih
z nestisnjenimi stranmi mask, katerih strani niso celo število strani BC4; en nivo se je zvišal z 0,4 na 0,94
svojega terena. Vrstni red je bil prilagojen: proti robovom višinskega modela vsakega kvadranta se vsaka stran
vozlišč z značilnostmi ujema z enim kvadrantom, nespremenjena, pri 0,3 do 0,54, kjer je naslednja najboljša
postavitev pod 0,2. Tako postavljene strani se brez šiva spojijo v ceste, vodo in naseljena območja preizkusnega
nivoja, pri 0,5 m na texel v območju igre. Kjer delajo plasti, je barvni zemljevid skoraj nevtralen (mediana
110, 107, 104); drugje lahko nosi polno barvo. Nivo, katerega drugi kosi vsebujejo samo nestisnjene strani mask,
nima prebranega barvnega zemljevida. Prejšnji krog tega bralnika je te strani imenoval negeografske: primerjal
jih je z zemljevidom ozadja, ki je lahko povsem druga pokrajina, in vsako stran postavil na celo vozlišče namesto
na kvadrant.

**Albedo za odboj svetlobe** so iskali in ga niso našli: kosi korenskega in prvega vozlišča so cele strani mask,
tip 5 pa njegov tovor ni najden.

**Luknje.** Sredstvo terena nivoja (tip res `0x1CA38E06`) imenuje tri senčilnike: privzeti površinski, površinski
za luknje in privzeti izvorni senčilnik. Katero plast bere senčilnik za luknje, ni najdeno, zato se višinski
model ne reže. V nivoju lahko navigacijska mreža teče po skalnih mrežah desetine metrov pod višinskim modelom,
kjer jih igra mora bila odrezati. Iskano in nenajdeno tam: maska plasti, raster 67 x 67, rezervirana višina
(nobena stran višin nivoja nima 0 ali 65.535) in zastavica vozlišča (vsako vozlišče pod korenom ima zastavice 1).
Ostaneta rastra 7 in 8. Oba sta kodirana z dolžinami nizov: bajt, enak prejšnjemu, mu sledi število dodatnih
kopij (`ff ff 84` je 134 bajtov po 255). Drevo 7 (ploščica 256, popolno kvadrantno drevo s petimi stopnjami, štiri
bite na vzorec) se dekodira v pare bajtov z vrednostmi od 0 do 3; drevo 8 (ploščica 265) v bajte večinoma 255, z
drugimi vrednostmi v rednih nizih. Ploščice nobenega še niso postavljene, zato ni znano, da bi katero držalo
luknje.

**Dekali** so prebrani in zapečeni; glejte [Dekali terena](#terrain-decals).

## Dekali terena {#terrain-decals}

Vir:
[`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Ceste, vzletne steze, betonske ploščadi, naslikane črte in črke, sledi pnevmatik: res `TerrainDecals`
(tip `0x15E1F32E`) jih hrani kot ploska geometrija, ki jo igra položi čez teren.

| Del | Postavitev |
|---|---|
| glava | pri +16 število rež n, nato n 16-bajtnih rež, nato število zapisov |
| zapisi | eden za vsak paket risanja, drug za drugim, različnih dolžin: 156 bajtov fiksnih polj - prvo oglišče pri +32, število trikotnikov pri +36, popločenje teksture v metrih pri +44 - nato bajti oglišč paketa (odmik, velikost) in rep, ki imenuje njegove teksture po GUID-ih particij sredstev |
| oglišča | 32 bajtov: x, z (f32), 8 pakiranih bajtov, u, v (f32), r, g, b, a (f16); vsak paket je navaden seznam trikotnikov |
| indeksi | u32, štejejo od 0 v vsakem paketu; niso potrebni |

Preverjanja:

- obsegi oglišč zapisov si sledijo brez vrzeli in pokrijejo vsa oglišča natanko, prvo oglišče vsakega
  zapisa, pomnoženo z 32, pa je njegov odmik;
- tako prebrani so trikotniki kompaktni dekali (črke, trakovi črte, zaplate), prebrani pa za eno oglišče
  narobe so reže čez zemljevid;
- skoraj vsi paketi v repu imenujejo teksture: barvni zemljevid (`_cv`) z zemljevidom neprozornosti (`_op`,
  rdeči kanal), ali za oznake masko kanalov (`_rgb`).

Za GUID-ji tekstur rep nosi parametre materiala paketa, kodirane kakor parametre bloka senčilnika (glejte
Odtenki spodaj). Barva barve oznake, sledi pnevmatika ali črte je float3, zgoščen kot `607e`: peščeno
0,64, 0,56, 0,48 za sledi pnevmatik v pesku, skoraj črna za katran. Zemljevidi neprozornosti so večinoma
format 62, en kanal po 8 bajtov na blok, prebran kot BC4.

Paket preslika svojo teksturo bodisi po svetovni poziciji (u = x, v = z, tekstura se ponavlja vsakih
popločilnih metrov: asfalt, beton, gramoz) ali od 0 do 1 čez dekal (črta, črka, sled pnevmatika).
Zapisi se rišejo v vrstnem redu v datoteki.

**Pečenje.** `level --ground-texture M` naslika pod razširitvijo dekalov in ploščicami največ 4.096
pik zemljevid barve ozadja (bilinearno), nato pa čez to vsak paket z njegovo neprozornostjo × alfa
oglišč. Barva oglišč se ne uporablja: nekatera oglišča paketov so čisto zelena ali modra, kar je
obarvalo oznake nivoja s temi barvami. Trikotniki višinskega modela tam postanejo deli
`ground:terrain x<x> z<z>`, ki nosijo ploščico. Vsak paket riše s temle:

| Imena paketov | Narisano kot |
|---|---|
| barvni zemljevid (`_cv`) | zemljevid, po njegovi neprozornosti |
| zemljevid množenja (`_mult`) in zemljevid neprozornosti | barva (bela, kjer material ne imenuje nobene) pomnožena z zemljevidom množenja, po zemljevidu neprozornosti: obrabljena središčna črta vzletne steze, robne črte in pragovi |
| maska kanalov (`_rgb`) | barva, sicer bela za črte in črke, temna za obrise, rahlo zatemnitev za obrabo, sledi pnevmatik, madeže, luže in vlažnost, po maski |
| samo zemljevid neprozornosti, z barvo | barva po zemljevidu neprozornosti: sledi pnevmatik |

Zemljevid cestne variacije ni barva, ampak spreminja površino pod njim, na stotine metrov naokoli, zato se
ne riše, ne glede na svojo barvo: pobarvan belo je položil dve bledi pravokotniki dolgi 150 do 250 m na
strminah nivoja. Zemljevid `_mult` se vzame kot lastna obraba barve, ne kot zatemnitev tal pod njo: je
skoraj bel, oblika črte pa je v zemljevidu neprozornosti.

Skoraj vsak paket se riše, v nekaj ploščic po 0,5 m na piko; izvoz zraste za nekaj MB in se doda nekaj
sekund. Gledano od zgoraj, vzletne steze, taksiji in cestno omrežje ležijo pod ograjami in stavbami
kompleksov ter vodijo do njihovih vrat.

Če bi jih narisali kot lastno geometrijo, bi dekali potrebovali mešanje alfe, ki ga pisalnik ne nosi, nad
terenom pa bi se z odmikom bolj prepirali z njim; pečenje jih ohrani v lastni barvi tal.

## Teksture in materiali {#textures-and-materials}

Vir:
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Res Texture (tip `0x6BDE20BA`) je 180-bajtna glava: tip in format pikslov pri +8, širina in višina pri +22,
število mipov pri +30, GUID kosa pri +40, petnajst velikosti mipov pri +56. Kos je veriga mipov, največji
najprej. Nekateri kosi nimajo svojih največjih mipov, ki so v paketu visoke ločljivosti; velikost kosa pove,
pri katerem mipu se začne, in ta kos je imenovan pri +164; prebere se iz [dodatkov](#which-table-is-the-level)
nivoja, kadar je potreben mip, ki ga glavni kos nima, in njegova dolžina plus glavnega kosa je celotna veriga.

| Format | Dekodirano kot | Dokaz |
|---|---|---|
| 67, 66 | BC7 (sRGB, linearno) | barvni list plastične tenkovke se dekodira kot BC7; kot BC3 so isti bajti šum |
| 61, 60 | BC3 | list škatle se čisto dekodira kot BC3, ne kot BC1 ali BC7 |
| 57, 56, 55 | BC1 | pol bajta na piksel |

Sredstvo mreže ne imenuje nobene teksture. Povezava je v **blokih senčilnikov nivoja** (res tipa
`0x73312045`, po eden na podsvet), ključih po osmih bajtih pri +0x130 zapisa oddelka mreže:

| Del | Postavitev |
|---|---|
| tabela, pri 16 | (ključ oddelka u64, odmik deskriptorja u64), dokler odmik ne pade izven resa |
| deskriptor | (odmik bloka u64, zgoščena vrednost u64, velikost bloka u64) |
| blok | parametri senčilnika oddelka; vsaka tekstura je zapis 49 bajtov: bajt, 16 bajtov, GUID particije sredstva teksture, njen GUID primerka |

Ključ zabojnika oddelka se pojavi enkrat v vsakem od desetih depojev podsvetov, ki ga postavljajo, in
njegov blok imenuje `t_mil_crate_03_cs` in `_nmt` med skupnimi zemljevidi podrobnosti. Blok imenuje vsako
teksturo, ki jo senčilnik vzorči, katera od njih je barvni zemljevid, pa ni navedeno, zato se izbere: 2D
tekstura sRGB, katere ime vsebuje večino besed imena materiala (`M_ConcreteWall_01`: concrete, wall), nato
mreže, nato tista, ki ni podrobnost, dekal (`t_de_...`) ali zemljevid poškodb, nato tista, ki jo uporablja
najmanj blokov. Blok cestnega znaka imenuje njegov panel `t_com_highwaysignage_01_cs` in list dekalov
`t_de_com_highwaysignage_01_ca` s ščitom, položenim na stran; oba se ujemata z besedami, in brez pravila za
dekale je list zmagal po uporabi, znak pa je pokazal ščit obrnjen za četrtino, skozi vse nize koordinat
teksture, ki jih oddelek ima. Podpisne razdalje (`..._sdf`), palete in maske kanalov (`_rgb`) se nikoli ne
izberejo, ne glede na to, katere besede delijo (`_rgba` zemljevidi se: večina so barva z alfo, izpustitev pa je
zamenjala lastna zemljevida za električni vod in stopnice z drugimi, nepovezanimi); atlas rastlinja v ozadju `..._atlas_a_sdf`,
narisan kot barva, je pokazal črne in bele zvezde za drevesa, paleta stavb v ozadju pa konfete vzorcev za stene,
steklen odpadek, narisan skozi svojo masko kanalov, pa je prišel ven cijan. Oddelek, katerega edini kandidati so
skupni zemljevidi podrobnosti, ostane ploska barva.

**Palete.** Stavbe v ozadju jemljejo svoje barve iz palete, 256 x 256 texelov iz kvadratkov 16 x 16: vsako oglišče
nosi štiri bajte (uporaba `0x1E`), katerih prva dva povesta, kje v paleti je njegova barva, x in y od 255. `level`
tak oddelek riše s paleto kot njegovo teksturo, vsako oglišče v središču svojega kvadratka. Tako narisani bloki
ozadja nivoja postanejo pastelne stene, opečnato in temna okna tam, kjer so bili preprosto beli.

**Prekrivke.** Veliki predmeti popločijo list teksture skozi svoje prve koordinate teksture in čez njega položijo
prekrivko skozi druge, ki ležijo med 0 in 1: razgrnitev celotnega predmeta. Prekrivka (`..._overlay_cs`, z masko
`..._overlay_a`) nosi videz predmeta od daleč, rdeče pasove in rjo naftnega rezervoarja; če bi bil narisan samo
z listom, so rezervoarji ene stopnje prišli ven kot sivi paneli. Oddelek, katerega blok imenuje prekrivko z masko
in katerega druge koordinate so takšna razgrnitev, se riše s prekrivko čez njih (36 oddelkov v tem nivoju).

**Odtenki.** Mnogi barvni zemljevidi so sivi (sredine njihovih kanalov so v 6 % druga od druge): senčilnik jih
pobarva z barvami iz parametrov bloka. Po vnosih tekstur (49 bajtov vsak) blok našteje svoje parametre, vsak
z oznako tipa (`f11af825` float3, `a5e1f2de` float4, `c1b1a014` float, `4a4fc3a1` celo število), zastavicami
`01 80` za eno vrednost, dvobajtno zgoščeno vrednostjo imena parametra, številom u32, vrednostjo in osembajtnim
ID-jem. Imena niso shranjena. Sedem zgoščenih imen float3 deluje kot odtenki: v enem nivoju trije od njih držijo
barvo v približno 1 bloku od 6, katerega zemljevid je siv in skoraj nikoli tam, kjer ima zemljevid lastno barvo,
ostali pa držijo barve, s katerimi je siv zemljevid pobarvan, kadar to pove ime materiala (modra obroba mostu
`..._blue`: 0,047, 0,098, 0,171 proti nevtralni 0,5). Družina lahko drži več vrednosti, po eno za vsak kanal maske,
večina nevtralnih, vrednost s kanalom skoraj nič (čisto zelena na opečnih fasadah) pa izbere kanal maske, ne
barva. `level` pomnoži siv barvni zemljevid, v linearni svetlobi, s prvo vrednostjo vsake družine, ki ni niti
nevtralna niti taka izbirna, čez njeno nevtralno, in rezultat ohrani kot lastno teksturo; zemljevid z barvo se pusti,
kakor je. Pravilo je izvoznikovo lastno: kateri kanal maske dobi kateri odtenek, ni prebrano. V enem nivoju je
delež trikotnikov konstrukcij, narisanih skoraj belo, padel z 19,4 % na 3,9 %.

**Različice predmetov.** Ena mreža je postavljena v več videzih: stena skladišča z rdečim ali modrim pasom in drugo
številko, naslikano nanjo, zabojnik v zeleni ali sivi barvi. Vsaka postavljena kopija imenuje svoj videz:

| Kje | Polje |
|---|---|
| član skupine statičnih modelov | +32: polje enega kazalca na kopijo, na različico predmeta ali null |
| referenca predmeta | +120: kazalec na različico predmeta ali null |
| različica predmeta (particija `ov_...`, tip `235f2a9c...`) | njen prvi primerek +32: 32-bitna zgoščena vrednost imena različice |

Videz oddelka v različici je blok senčilnika, ki ga določa ključ oddelka sam, z zgoščeno vrednostjo različice,
dodano njegovim prvim štirim bajtom kot u32 little-endian (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`);
oddelek brez bloka pod tem ključem izgleda enako v vsaki različici. Zbirke variant mrež nivoja (`meshvariationdb_win32`)
za vsako mrežo in zgoščeno vrednost različice navajajo materiale, ki se jih različica dotika, ne pa ključev. Pravilo
je bilo najdeno iz samih ključev in velja za vsak oddelek z variantami, ki je bil preverjen (štiri različice ene stene,
tri njeni oddelki vsaka). Blok različice prinese svoje teksture, kakor tudi tinte: naslikana številka na steni je list
črk, ki ga imenuje blok različice. Velik delež kopij v skupinah je postavljen v različico.

Blok se za vsako vsebino zapeče enkrat, vnos depoja za ključ pa nosi zgoščeno vrednost (drugi u64 vnosa). Kjer oddelek
nima bloka pod ključem svoje različice, različica še vedno doseže oddelek prek *dvojnika*: drugega oddelka, čigar privzeti
blok ima enako vsebino in ga ima. Brez dvojnikov se stena, katere dolžine delijo en privzeti blok, lahko pokaže v dveh
barvah. Oddelek brez svoje različice vzame različico, ki jo ima večina njegovih dvojnikov.

**Uničljive mreže.** Mreža, ki jo lahko ujemanje podre, ima poleg sebe sredstvo za uničenje z lastnim imenom
(`.../br_x.destruction` za `.../br_x_mesh`): lomljive stavbe in stene (`br_`) ter veliko rekvizitov. `level` jih
površine hrani v lastnih delih, poimenovanih z ` (destructible)`, katerih vozlišča glTF nosijo
`{"destructible": true}`. Njihova uničena stanja so mreže `dc_..._part<N>_mesh` poleg njih, vsaka središčena na svoje
izhodišče; kje sedi kateri del, je v sredstvu za uničenje, ki ni prebrano, zato uničena stanja niso izvožena.

**Izpuščeno.** Oddelki placeholder materialov (`M_Whitebox`: nekaj velikih netexturiranih trikotnikov, ki jih nekatere
stavbe hranijo ob svojih površinah, in so iz nivoja štrleli kot bela krila), mreže, narejene za filmske posnetke (helikopter,
postavljen, kjer se začne njegova scena), in pomožni predmeti za osvetlitev (ravnine, ki blokirajo svetlobo, se nikoli ne
rišejo). Generirani zadnji stavbni objekti nivoja (`..._generated_blueprints_..._mesh`) so narisani, a imena materialov
njihovih sten imenujejo samo šumne zemljevide, njihova oglišča pa ne nosijo barve, zato ostanejo navadni. Skoraj vsak
narisan oddelek dobi barvni zemljevid.

**Liste s črkami.** Naslikana številka na steni ali plakat na žerjavu je oddelek sam zase, katerega barvni zemljevid je list
(`_ca`): alfa črke čez trdno barvo ali tisk. Njegove prve koordinate teksture popločijo ometanje stene čez ploščo (u -0,2 do
1,7 na eni steni), kar nariše list skoraj dvakrat. Četrti nabor (`0x24`, sicer tretji, `0x23`) ga položi natanko enkrat (u -1 do
0, v 1 do 2, nekaj tisočink čez v grobejših stopnjah podrobnosti). Kjer prvi nabor pusti eno kopijo slike in četrti ali tretji
leži znotraj ene, se list riše skozi to, premaknjen v 0 do 1. List z alfo se riše 1 cm pred površino, na katero je naslikan,
ki je narisana pod njim v drugem barvnem zemljevidu bloka skozi prvi nabor: brez tega so prazni texeli lista pokazali
notranjost stene. Drugi nabor je razgrnitev predmeta za njegovo prekrivko in se tu ne uporablja.

**Izrezi.** Četrti kanal barvnega zemljevida pomeni različno glede na ime zemljevida. V `_cs`, daleč najpogostejši
(893 izbranih zemljevidov v enem nivoju), je to gladkost: 1 % alfe mediane karte leži znotraj 0,1 od 0 ali 1. V `_cu`
(listi, trava) in `_ca` (barva in alfa) je neprozornost: 90 % in 87 %. Barvni zemljevid, imenovan `..._cu` ali `..._ca`,
katerega alfa je vsaj 75 % blizu 0 ali 1, vsaj 1 % pod 0,5 in vsaj 5 % nad njim, se zapiše z alfo, kot PNG, njegov material
pa kot glTF `alphaMode` MASK, `alphaCutoff` 0,5, dvostranski; kartice listov tako kažejo liste, ne njihovih črnih kotov.
Zemljevid listov enega drevesa nima alfe sploh (največ 4 od 255): njegove perje so izrezane z geometrijo, in z samo prvima
dvema pogojema je bila izrezana cela krošnja.

Koordinate teksture so vrsta vozlišča `0x21`, dva pola (format 6) ali dva floata (format 2). Oddelki nosijo do tri
dodatne nize (`0x22` do `0x24`) za dekalne in podrobne plasti. Koordinate se popločijo: rebrasta stranica vsebnika teče
od -1,6 do 1,8, ploščice terena v ozadju ležijo povsem zunaj 0..1, v enem nivoju pa 23 % teksturiranih trikotnikov sega
zunaj 0..1. Zapišejo se, kakršne so, s ponavljajočim vzorčilnikom; 3DHeat pregledovalnik ovije vsako ponavljajočo se teksturo
znotraj svojega atlasa. Upodabljalnik, ki jih namesto tega vpne, raztegne rebra na dvakratno širino, betonsko ploščad
spremeni v proge vzdolž ene osi in da nosilcem stolpa robno barvo svoje teksture; zanj `--clamped-uvs` razreže vsak trikotnik
vzdolž črt, kjer se tekstura ponavlja, in vsak kos premakne v 0..1 (glejte [Oblika izhoda](output-format.md)). Potem
0,03 % teksturiranih trikotnikov, čez katere se tekstura ponovi več kot 16-krat, seže ven, trikotnik, ki bi ga rezanje
razdelilo na več kot 4 kose, pa se nariše v povprečni barvi teksture: lubje se ponavlja po vsaki veji, in razrezana so
drevesa nivoja šla z 6,4 na 24 milijonov trikotnikov.

Višinski model nima lastnega barvnega zemljevida, ki bi ga bilo mogoče prebrati. Kjer ga pokriva eden od zemljevidov
ozadja terena, se obarva iz njega: koordinate teksture ozadja so linearna funkcija svetovnega x in z (99 % njegovih
oglišč je znotraj 0,001 od nje; zemljevid pokriva kvadrat 65.536 m, obrnjen za četrtino), ista funkcija pa da tudi
višinskemu modelu. Nivo pošilja mipe tega zemljevida od 2.048 px navzdol, zato višinski model dobi 32 m na piko. Njegova
temna skala leži na strmem terenu: korelacija temnosti z naklonom je 0,48, pri ostalih sedmih usmeritvah največ 0,34.

Ozadje drugega nivoja je osem bližnjih in osem daljnih ploščic okoli območja igre, vsaka ponavlja svojo teksturo čez
ploščico, nobena pa ne seže do višinskega modela. Vsaka tekstura ozadja se prilagodi sama, in kadar nobena ne pokriva
višinskega modela, vzame povprečno barvo, ki jo ozadje kaže v kilometru od kvadrata terena, ki ga `--ground-texture` peče
skupaj z dekali. Material ozadja je tisti, katerega ime vsebuje `TerrainBackdrop` ali `BD_` in `Terrain` (`M_BD_<site>_Terrain..._Near`);
ali mreža ozadja (`bd_..._terrain<site>_04_far_mesh`) nosi navaden material terena (`M_<region>_Terrain<site>_04_Far`), ki
sta ga prvi dve pravili v enem nivoju zgrešili, zato je svoje tla obarval iz svojih površin.

Kjer nobeden zemljevid ozadja ne pokriva višinskega modela, pa vzame srednjo barvo lastnih površin terena, pred povprečjem
ozadja: barvne zemljevide `_cv`, ki jih imenujejo bloki senčilnikov grafa plasti terena (27 v enem nivoju: peski, gramozi,
prst, trava, razpokan beton), vsakega povprečenega, nato mediano vsakega kanala, brez privzete površine motorja. Ozadje je
lahko povsem druga pokrajina: v enem nivoju je njegovo povprečje (95, 99, 80 v sRGB) obarvalo tla območja igre v sivo, ki je
igra ne kaže. Z `--ground-texture` se ta barva pomnoži z dvakratnim barvnim zemljevidom, kar srednje sivo pusti, kakor je, in
zapeče z dekali čez oboje, čez razširitev dekalov in barvnega zemljevida.

Glede na igro: mediana barve tal zapečenega območja igre vsakega nivoja in posnetkov igre (vrstice od 55 do 72 % slike ob
HUD-u, po 24 posnetkov; sRGB; posnetki so osvetljeni in obdelani, zato so razmerja r/g in b/g pošteno primerjava):

| Nivo | Posnetki | Povprečje ozadja | Zdaj |
|---|---|---|---|
| prvi | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| drugi | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| tretji | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Prvi je popravljen; druga dva sta bila pred tem nekoliko bližje po odtenku. Ena barva za cel nivo ne more biti
prava povsod; prave bi bile maske.

## Navigacijska mreža {#navigation-mesh}

Vir:
[`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Nivo dostavlja eno particijo na agenta, `<level>/dbt/<level>_navmesh_layer_<n>`: v enem nivoju je plast 0
vojak (1,8 m visok, korak 0,18 m, polmer 0,4 m), dve drugi sta vozili (3,5 in 10 m visoki). Vsaka particija
nosi dve polji:

| Polje | Element |
|---|---|
| ploščice | 28 bajtov: u32 0, u32 zgoščena vrednost, u32 0, u32 indeks kosa, u16 x ploščice, u16 z ploščice, u32 odmik, u32 velikost |
| kosi | 20 bajtov: GUID kosa, u32 velikost |

Ploščica je `size` bajtov pri `offset` v kosu `chunk index`, little-endian, in je razporejena kot pri Detourju
(Recast Navigation) za daljšo glavo:

| Odmik | Vsebina |
|---|---|
| 0 | `VAND`, različica 7 |
| 24 | števila: poligoni, oglišča, povezave, detajlne mreže, detajlna oglišča, detajlni trikotniki, vozlišča ovojnice, povezave izven mreže, prvi poligon izven mreže |
| 188 | višina agenta, korak, polmer |
| 200 | omejevalna škatla ploščice, šest floatov |
| 232 | oglišča: x, y, z floati, svetovne koordinate |
| naslednja meja 8 bajtov | poligoni, 32 bajtov: u32, šest u16 indeksov oglišč, šest u16 sosedov, u16 zastavice, število oglišč pri +30, pri +31 območje (spodnjih šest bitov) in vrsta (zgornja dva) |
| nato, zapakirano | povezave (16 bajtov), detajlne mreže (12: prvo detajlno oglišče u32, prvi detajlni trikotnik u32, število oglišč in trikotnikov u8), detajlna oglišča (trije floati), detajlni trikotniki (trije indeksi in zastavice), vozlišča ovojnice (16), povezave izven mreže (80) |

V vsaki ploščici teh preverjenih nivojev se to točno sešteje v velikost ploščice do bajta, detajlne mreže pa
oštevilčijo poligone pred prvim poligonom izven mreže.

Poligon je raven med svojimi vogali; njegova **detajlna mreža** nosi pravo višino površine čez grbine, skale in
stopnice, in to je tisto, kar se riše. Detajlni trikotnik z indeksom pod številom vogalov poligona je ta vogal, sicer
detajlno oglišče `first + index - corners`. Če bi poligone napihnili v trikotnike, bi jih bilo veliko več pod terenom
in bi nastali dolgi lističi; z detajlnimi mrežami nobeden ni daljši od diagonale ploščice 16 m in dviga stopnje navzgor
po strmini.

Vrsta 0 je tla, vrsta 2 majhne strme zaplate (približno 45 stopinj, kvadratni meter vsaka), vrsta 1 je povezava med
površinami: njeni vogali obsegajo 125 m višine ali več in ležijo izven ploščice, nekateri v izhodišču. Povezave se
izpustijo; ostale se narišejo po svojih detajlnih mrežah ali se razpnejo v ploščici brez nje.

Preverjanja: velikosti kosov se natanko seštejejo v velikosti ploščic; vsako oglišče površine leži znotraj škatle
svoje ploščice, vsaj do približno enega metra; skoraj vsi trikotniki gledajo navzgor. Ploščica, ki ne uspe, je
zavrnjena in prešteta, in v tem nivoju nobena ni.

Kar pokriva vojakova mreža, gledano z vrha v preizkusnem nivoju: tla, ploščadi, stopnice in nekatere strehe, ne pa
vrhovi tovornih zabojnikov. To je zemljevid AI o tem, kje lahko vojak stoji, najbližje, kar datoteke povedo o tem, kje
stojijo igralci.

## Ni implementirano {#not-implemented}

- Graf plasti terena, ki meša njegove površinske plasti (glejte [Plasti terena](#terrain-layers)): barva tal sledi pravilu
  tega bralnika iz mask plasti in naklona višinskega modela, nivoji, katerih strani mask se ne ujemajo, pa dobijo eno barvo.
- Barvni parametri dekalnih materialov: oznake, narisane z masko kanalov, so pobarvane v nevtralni barvi.
- Predmetne skice, ki niso mreže (logika igre, učinki, zvoki).
- Uničena stanja uničljivih mrež: njihova mesta so v sredstvu za uničenje, ki ni prebrano.
- Povezave navigacijske mreže (skoki, lestve, preskoki) in njene vozniške plasti.
- Mreže nivojev, shranjene v vrsti res (10 mrež v nivoju, pripomočki), in kosti ter sestavljeni deli skinned in sestavljenih mrež,
  ter normale (izračuna jih zapisovalnik).
- Normalni, hrapavostni in drugi zemljevidi; alfa razen izreza (prosojno steklo in dekali so narisani neprozorno).
- Luknje terena: senčilnik za luknje je imenovan, a kaj bere, ni najdeno (glejte [Plasti terena](#terrain-layers)), zato
  višinski model ni prerezan tam, kjer teče hodljivo tla pod njim.
- Katera barva gre s katerim kanalom maske materiala: siv barvni zemljevid vzame prvi odtenek, ki ni nevtralen (glejte
  [Teksture in materiali](#textures-and-materials)).
- Efekti (poti `fx/`) in kabelske mreže, katerih škatle so dolge desetine kilometrov; izpuščene so in prešteta v povzetku.
- Format XOR z zamaskiranimi tabelami.
