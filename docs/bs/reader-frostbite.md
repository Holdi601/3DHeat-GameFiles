---
title: "Frostbite"
nav_order: 5
lang: "bs"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, paketi (bundles), mreže i nivoi {#frostbite-toc-cas-bundles-meshes-and-levels}

**Čita Battlefield 6 nivo do njegovog terena, postavljenih mreža i njihovih
mapa boja, i upisuje ga kao `.glb`.** Frostbite igre (Battlefield, Need for Speed, Dead Space) drže svoj
sadržaj u `.cas` blobovima, opisanim `.toc` tablicama sadržaja. Tablica nivoa
kaže koje pakete (bundles) nivo učitava, paketi imenuju svaki asset,
a asseti kažu koja mreža gdje stoji.

Izvori:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tablice, paketi, payloadi),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(paketi i njihovi manifesti),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX particije),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(heightfield),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(teksture i materijali),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(postavljanje i izvoz).
Komande: `identify`, `levels`, `level` (pogledajte [Komande](commands.md#levels-and-level-frostbite)).

Ništa od ovoga igra ne dokumentira. Svaki raspored niže pročitan je iz
datoteka pa provjeren prema svima njima, a svaki odjeljak kaže kakva je bila provjera.
Gdje Frosty modding alati opisuju starije verzije strukture, nazivi polja
slijede njihove; nikakav kod nije preuzet od njih (pogledajte
[Pravila i licence](rules-and-licences.md)).

## Zaglavlje koje izgleda šifrirano a nije {#the-header-that-looks-encrypted-and-is-not}

| Magic (u32, little-endian) | Značenje | Obrada |
|---|---|---|
| `0x00CED100` | obično: stablo počinje odmah | čita se |
| `0x01CED100` | potpisano: potpis od 556 bajta, pa stablo **otvoreno** | čita se |
| `0x03CED100` | XOR-zamućeno, s ključem u zaglavlju same datoteke | otkriva se i odbija |

Potpisani oblik je ono što isporučuje aktuelni Battlefield. Bajtovi visoke entropije poslije
magic vrijednosti su potpis, a ne šifrat.

## DbObject stablo {#the-dbobject-tree}

Jedna rekurzivna struktura. Svako polje je bajt tipa (nižih pet bitova je tip, bit 7
"anonimno"), neobavezno ime i vrijednost. Kontejneri nose svoju dužinu kao
cijeli broj promjenljive dužine i završavaju nultim bajtom. `parse_toc` provjerava dužinu svakog
kontejnera, pa je datoteka koja se uspije parsirati shvaćena. `layout.toc` je u
ovom obliku.

## Instalacijski paketi {#installation-packages}

Svaka lokacija imenuje **instalacijski paket** kojem pripada njen blob. Svaki
paket numerira svoje blobove od `cas_01`, pa je sam broj bloba dvosmislen čim
je instaliran više od jednog paketa, što je uvijek.

- `layout.toc` navodi pakete pod `installManifest.installChunks`, svaki
  s `persistentIndex` i `installBundle` kao što je
  `Win32/installation/<package>`.
- Blobovi paketa su u tom folderu, pod `Data` za osnovnu igru ili
  pod `Update/<pack>/Data` za ono što je došlo kasnije.
- Zapis lokacije nosi puni 32-bitni `persistentIndex`: niža polovina
  njegove prve riječi drži višu polovinu, viša polovina druge riječi nižu
  polovinu; niža polovina druge riječi je broj bloba.

Provjera: svaka lokacija u svakoj binarnoj tablici instalacije
razrješava se na deklarirani paket i pada unutar bloba koji imenuje. Raniji
oblik je uzimao prvi `cas_NN.cas` ispravnog broja. Trećina
payloada koje je čitao tada je izgledala kao visoka entropija i smatrana je šifriranjem. To
su bili ispravni pomaci u pogrešnoj datoteci. Ništa pronađeno nije šifrirano.

## Tablica nivoa {#the-level-table}

Tablica nivoa (`levels/<level>/<level>.toc`) je tablica sekcija: petnaest
big-endian riječi zaglavlja, pa sekcije složene jedna za drugom, čiji su pomaci i
navedeni i izvedivi iz dva broja.

| Sekcija | Sadržaj |
|---|---|
| bundles | hash tablica (po jedna riječ), pa zapis od 16 bajta po paketu: ključ, `0x40000000` \| veličina, 0, pomak |
| chunk hash tablica | jedna riječ po dijelu (chunk) |
| chunks | 16-bajtni id (GUID dijela **obrnutog redoslijeda bajta**), pa riječ: `0x80000000` \| 4 x indeks njegove lokacije |
| locations | četiri big-endian riječi: paket (podijeljen), blob, pomak, veličina |

Id-ovi dijelova i lokacije su **različitim redoslijedom**. Čitanje u
redoslijedu datoteke spaja svaki dio s bajtovima drugog dijela, koji se savršeno
dobro dekodiraju (uglavnom kao zvuk) pa ne izgledaju pogrešno dok mreža ne ispadne kao šum.
Provjera: u nivou, riječi indeksa su permutacija od 0 do broja dijelova
minus jedan.

Paketi su pohranjeni u nizu poslije tablice sekcija. Svaki je devet big-endian
riječi zaglavlja, pa njegovi unosi: osam bajta pomaka i veličine, kojima prethodi
još osam koji imenuju paket i blob kad je u zastavici unosa postavljen najviši bit.
Provjera: na svakom paketu, zadnji unos završava tačno tamo gdje počinju
bajtovi zastavica.

### Koja je tablica nivo {#which-table-is-the-level}

Nivo može imati nekoliko tablica istog imena: jednu u `Data` osnovne igre,
jednu u svakom ažuriranju (`Update/<pack>/Data`) koje ga isporučuje ili mijenja, i
jednu u svakom paketu visoke rezolucije
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Samo neke sadrže
pakete. Za nivo koji isporučuje ažuriranje, tablica u osnovnoj igri drži samo
dijelove i nijedan paket, a ona u ažuriranju je nivo; uzimanje
prve pronađene tablice nije izvezlo ništa od njega.

Dakle nivo je tablica s najviše paketa, a kasniji sloj pobjeđuje u neriješenom (prvo
osnovna igra, zatim ažuriranja po redoslijedu imena), a tablice istog imena
bez paketa su njegovi **dodaci** (supplements): njihovi dijelovi se dodaju dijelovima nivoa,
jer drže najveće mipove njegovih tekstura. Zaglavlje teksture imenuje taj
dio na +164 (pogledajte [Teksture i materijali](#textures-and-materials)). `levels`
ispisuje odakle dolazi svaki nivo i koliko dodataka ima.

## Manifesti paketa {#bundle-manifests}

Prvi unos paketa je njegov manifest, pohranjen nekomprimiran. To je binarni
format paketa ranijih Frostbite igara s novom magic vrijednošću, `0xD68E799D`: brojevi,
SHA-1 vrijednosti, ebx i res zapisi (pomak imena i veličina), res tipovi, metapodaci i
id-ovi, GUID-ovi dijelova, stringovi. Ostali unosi paketa su ebx-ovi, res-ovi
i dijelovi tim redom. Provjera: brojevi se poklapaju s unosima na svakom
paketu, a stringovi počinju tamo gdje završavaju zapisi.

Tipovi resursa su hashevi. `0x49B156D4` je MeshSet (svaki res tog tipa
zove se `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` čita sve ovo za jedan nivo, za nekoliko sekundi: nivo
ima desetine paketa i desetine hiljada ebx-ova, res-ova i dijelova.

## Blokovi payloada {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Nulta komprimirana veličina znači pohranjeno, onoliko dugo koliko se dekomprimira.

| Riječ metode | Kodek |
|---|---|
| `0x0070`, `0x0071` | nema |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), iz `oo2core` DLL-a same igre) |
| ostalo, s jednakim veličinama | kopira se kako je pohranjeno |
| ostalo | odbija se |

Pročitan iz ispravnog paketa, svaki uzorkovani payload se dekodira.

## EBX particije {#ebx-partitions}

EBX drži sve što nije sirovi podatak. Svaka particija je RIFF datoteka:
`EBXD` (podaci, poravnati na 16), `EFIX` (GUID particije, GUID-ovi tipova i
potpisi, pomaci instanci, pokazivača, importa i informacija o tipovima, importi, te
pomaci nizova, boxed vrijednosti i stringova), `EBXX` (tablica nizova: pomak, broj,
hash, zastavice, tip elementa). Polje pokazivača je osam bajta: nula je null, neparna
vrijednost je import broj `value >> 1`, sve ostalo je relativno prema polju.

**Biblioteka tipova se ne može čitati.** Igra je isporučuje u svom početnom datotečnom
sistemu, koji je šifriran, a ovaj paket ga ne dira. Tipovi su poznati
po GUID-u i potpisu, koje nosi svaka particija, a nekoliko tipova koje
izvoz nivoa treba rasporedilo se iz podataka.

## MeshSet {#meshset}

Mreža je MeshSet res (opis) i jedan dio po nivou detalja (baferi).

| Dio | Raspored |
|---|---|
| prefiks | četiri riječi: veličina zaglavlja (176 ili 192), veličina zapisa nivoa (176 do 188), veličina zapisa sekcije (368), 0 |
| zaglavlje | granični okvir; šest i64 pomaka nivoa; tip mreže na `0x6C` (kruta, skinned, kompozitna); brojevi nivoa i sekcija na `0x9C` |
| nivo | sekcije na `+0x08`; pet lista crtanja na `+0x14` (neprozirno, prozirno, decal, samo dubina, sjena); format indeksa `+0x54` (`0x21` u16, `0x2E` u32), bajtovi indeksa i vrhova; GUID dijela na `+0x74` |
| sekcija | ime materijala; stride vrhova; trouglovi, prvi indeks, pomak vrhova (bajti), broj vrhova na `+0x20`; deklaracija vrhova na `+0x64`: 16 x (upotreba, format, pomak, stream), 16 stride-ova streamova, brojevi |
| dio (chunk) | bafer vrhova, pa bafer indeksa. Streamovi sekcije slijede jedan drugog; indeksi se broje od prvog vrha sekcije |

Pozicije su upotreba 1, stream 0, pomak 0, kao četiri polovine (half) ili tri floata.
Crtaju se samo neprozirne i prozirne sekcije. Svaka sekcija nazvana
`..._shadow` je u listi sjena i samo tamo, pa liste odlučuju.

Provjera: svaka mreža nivoa čiji su nivoi pohranjeni u dijelovima dekodira se, i
gotovo sve imaju 99% ili više svojih vrhova unutar deklariranog okvira; ostale
promašuju zbog zaokruživanja half vrijednosti. Dekodirano sanduče mjeri otprilike metar, Y gore, s normalama
okrenutim prema van.

## Postavljanje {#placement}

Content pipeline skuplja statične objekte svakog pod-svijeta u
**grupu statičkih modela**: niz članova, po jedan po mreži, svaki sa svojim
transformacijama instanci.

| Tip (GUID, potpis) | Raspored |
|---|---|
| član `ad13064e…`, `0xF861A878` | 224 bajta: `+88` niz transformacija, `+112` nacrt objekta (import), `+160` asset mreže (import) |
| transformacija `101dce06…`, `0x5E6D8C37` | 64 bajta: desno, gore, naprijed, translacija, svaki vec3 dopunjen na 16 |

Particija asseta mreže zove se kao njen MeshSet res, pa GUID particije importa
daje mrežu. Tačka sjedne na
`x·right + y·up + z·forward + translation`. Vlastita transformacija grupe bila je
identitet u svakoj grupi provjerenih nivoa i ne primjenjuje se.

Provjera: u nivou, svaki član svake grupe razrješava se na mrežu; većina kopija ima rotaciju s determinantom 1 na
hiljaditi dio, ostale su skalirane ili zrcaljene. GUID-ovi tipova i potpisi su
isti u drugim nivoima. Ažuriranje igre koje mijenja raspored mijenja
potpis, a čitač tada ne nalazi ništa umjesto da pogrešno pročita.

### Objekti postavljeni jedan po jedan {#objects-placed-one-by-one}

Ono što pipeline ne može grupirati — destruktivni objekti, kontejneri, krhotine — postavlja se
**referencama objekata** i **referencama prefaba** u
particijama nivoa:

| Tip (GUID, potpis) | Raspored |
|---|---|
| referenca objekta `a9a6a6ad…`, `0xC4856BEC` | `+32` transformacija (kao gore), `+112` nacrt objekta (import) |
| referenca prefaba `117c746e…`, `0xDE3FE9B4` | isto; nacrt je prefab, particija daljnjih referenci |

Prefabovi se gnijezde; kopija sjedne na svoju transformaciju puta transformaciju roditelja (redni
vektori), do osam nivoa. Nacrt objekta crta se kao mreže koje
importira, izostavljajući uništena stanja (`dc_...`). Grupirani prefab
referencira se kao njegov ostatak `..._nongroupable_autogen`, pa se ništa ne crta
dvaput.

Obilazak počinje samo od svjetova i slojeva nivoa. Particija čija je
prva instanca nacrt prefaba (`134919fc…`, `0x0247807D`) je definicija prefaba,
a nivo ih drži mnogo pod svojim folderom, postavljenih njegovim svjetovima
na načine drukčije od ovih referenci; obiđen kao da je svijet, prefab
stavlja svoj sadržaj na svoje lokalne koordinate. To nagomila
stotine kopija oko ishodišta svijeta, daleko ispod tla. Svjetovi i slojevi imaju `a10ebe0f…`, `0xD3D16C3C` prvo.

Nacrti postavljeni izvan igre ne slijede se: razvojni i test asseti
(`game/dev/`, `test/`), set završne kinematike runde (`..._gameend_...`: postavljen
ispod tla)
i kontroler kamere smrti (`.../deathflow/...`, čiji gadgeti stoje u
ishodištu svijeta). Prepoznaju se po putanji asseta, a ne po sloju:
isti sloj koji drži set kinematike može postaviti prave zidove i krovove nivoa. Poslije oba pravila nijedna kopija u provjerenim nivoima ne leži
više od 10 m ispod terena, a kopije stoje na terenu tamo gdje ih igra
prikazuje.

**Nivoi detalja koji zamjenjuju.** Zadnji nivo detalja mreže može se prebaciti
na zamjenu za daljinski pogled s vlastitim materijalom: `M_LastLod`,
`M_Billboard`, `M_Vista`, `M_ProjectionLod`. Rešetkasti toranj od desetina
hiljada trouglova može završiti siluetom od nekoliko stotina, koju bi
budžet izabrao a koja izbliza je puni šiljak. Nivo detalja koji donosi takav materijal, kakav
njegov najfiniji nivo nema, nikad se ne bira; najgrublji nivo mreže je zadnji pravi.

## Teren {#terrain}

Izvor: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Teren je TerrainStreamingTree res (tip `0x22FE8AC8`) i dijelovi koje
imenuje.

| Dio | Raspored |
|---|---|
| zaglavlje | 34 bajta; broj čvorova na 25 |
| raster stabla | bajt tipa i u32 dužina svako, do bajta tipa `0xFF`. Tip 0 je heightfield: uzorci po strani na +5 (265), raspon visine na +21 (1.280 m), kvadrat terena u njegovom prvom zapisu čvora na +77 (8.192 m u provjerenom nivou). Drži granične okvire čvorova i 16 x 16 min/max piramidu po čvoru, a ne visine |
| streaming čvorovi | quadtree (quadtree), prvo u dubinu: veličina dijela i GUID; neobavezan drugi dio; bajt zastavica (bit 0: dio počinje stranicom visina); ima djecu. Djeca redom (0,0), (1,0), (1,1), (0,1) |
| stranica visina | prvih 265 x 265 u16 dijela označenog čvora, red po red; visina = vrijednost x 1.280 / 65.535 m; kolone duž x, redovi duž z, od donjeg ugla čvora; ivica od 4 uzorka, pa 256 ćelija po čvoru |

Svaki korak je provjeren posebno:

- Parsiranje quadtree-a čvorova troši res do zadnjeg bajta, s deklariranih
  529 čvorova.
- Susjedni čvorovi dijele svojih devet rubnih kolona tačno, pa je korak 256.
- Uzorci djeteta na svakoj drugoj poziciji tačno su jednaki roditeljevim s
  ivicom od 4, a 90 do 700 jedinica su pogrešni s bilo kojom drugom ivicom.
- Najniža riječ u nivou dekodira se u najnižu visinu graničnog okvira do na
  centimetar.
- Od osam načina na koje kvadrat može ležati na svijetu, samo x duž x i z
  duž z stavlja postavljene objekte na njega: polovina uzorkovanih kopija unutar
  oko 2 m, naspram nekoliko puta toliko za svaki drugi način.

Postavljeni objekti zatim mjere rezultat. Najniža tačka svake kopije,
prema terenu ispod nje (bilinearno, iz najfinijeg čvora):

| Postavljeno | Medijan udaljenosti | Medijan s predznakom |
|---|---|---|
| drveće i grmlje | znatno manje od metra | tek ispod površine |
| rekviziti | metar ili dva | na površini |
| stijene | oko metar | uronjene oko metar |
| zgrade | nekoliko metara (stoje na temeljima) | blago uronjene |

Vegetacija se postavlja na tlo i nigdje drugdje, što je čini
najoštrijom provjerom: njena ishodišta sjede medijanom 0,07 m od površine. Zgrade
su široko raspršene jer kategorija drži zidove, podove i dijelove kompleta
višespratnih i podzemnih struktura. Pomjeranje terena 64 m u stranu
spušta udio kopija unutar 0,5 m sa 29% na 10%.

`level` crta heightfield kao `ground:terrain`, svaki njegov dio iz
najfinijeg čvora s visinama tamo i ne finije od `--ground-spacing` (4 m
zadano: 3,7 miliona trouglova za provjereni nivo, čiji su najfiniji čvorovi
0,5 m). Dijelovi različitih rezolucija sastaju se s malim stepenicama; ništa ih
ne šije.

Dio čvora također drži stranice slojeva maski poslije njegove stranice visina,
a njegov drugi dio završava colormapom čvora (pogledajte
[Slojevi terena](#terrain-layers)).

## Slojevi terena {#terrain-layers}

Igra sjenči teren blizu igrača nanošenjem (splatting) teksturiranih materijala površine
po oslikanim maskama, s colormapom preko njih, i crtanjem decala (ceste,
asfaltne zakrpe, oznake pista) povrh. Vlastiti opis sistema u Frostbiteu
(Widmark, "Terrain in Battlefield 3", GDC 2012) navodi rastere terena kao
heightfield, shader splatting maske, colormapu "korištenu kao preklop povrh
shader splattinga", fizičke materijale, masku dubine uništenja, albedo
mapu za odbijeno svjetlo i dodatne kanale maski; pločice rastera nose
ivicu za algoritme renderiranja. Streaming stablo provjerenih nivoa
ima sedam raster stabala, tipova 0, 1, 2, 4, 5, 7 i 8, čija zaglavlja počinju
veličinom pločice: 265 za heightfield (tip 0) i tip 2, 72 ili 66 za
maske (tip 1), 132 s ivicom od 2 za colormapu (tip 4), 260 s ivicom
od 2 za tip 5.

**Lista slojeva.** Res terena `....layergraphs` navodi jedan unos od 32 bajta po
sloju, redoslijedom kojim ih numeriraju zapisi maski (34 unosa, 34 sekcije depoa
i indeksi slojeva 0 do 33 u jednom nivou); id svakog unosa završava
ključem njegove sekcije u depou shader blokova grafa slojeva
(`....layergraphs_shaderblockdepot`), čiji blok imenuje mape sloja: jednu
`_cv` mapu boje, `_nhs` i `_ao` mape po površini, plus zajedničke detail i
noise mape. Mnogi slojevi uopće ne imenuju mape: oni su izvori koje
graf slojeva čita. Boja sloja je srednja vrijednost njegove `_cv` mape; skala tilinga nije pronađena.
Asset terena završava jednim unosom od pet bajta po sloju (bajt, pa u32
indeks sloja ili -1).

**Maske.** Raster stablo 1 je quadtree maski. Njegovo tijelo počinje s 59
bajta, strana stranice na 0: 72 gdje su stranice BC4 (72 x 72, 2.592
bajta), 66 gdje su nekomprimirane osmobitne (4.356 bajta). Zatim dolazi jedna
grupa po čvoru, prvo u dubinu:

| Dio | Raspored |
|---|---|
| grupa | u16; u16 broj zapisa; u32 broj stranica; zapisi; nulti bajt. Grupa bez zapisa ukupno je 7 bajta |
| zapis | 33 bajta: u16 sloj, u16 hash, okvir kvadranta (četiri floata), dva bajta zastavica, 85-bitna piramida prisutnosti |

Zapisi grupe su četiri kvadranta njenog čvora, sloj po sloj, kvadranti svakog sloja
redom (0, 0), (1, 0), (1, 1), (0, 1). Zapis s postavljenom
drugom zastavicom pokriva cijeli svoj kvadrant i nema stranicu; onaj bez nje ima
sljedeću stranicu; kvadrant bez zapisa sloja koji njegova grupa imenuje je prazan
od tog sloja; prva zastavica je čista tačno kad sloj ide dalje u
grupi samog kvadranta, jedan nivo niže, koja ga tamo zamjenjuje. Broj stranica
je broj zapisa sa stranicom.

Stranice: stranice grupe samog streaming čvora slijede, u njegovom dijelu,
stranicu visina, 16-bitnu sekciju od 4.358 bajta i 67 x 67 osmobitni raster (od
početka dijela kad nema stranicu visina); njegov drugi dio drži
stranice grupa njegova četiri kvadranta jedan nivo niže, kvadrante redom
colormape, zatim colormapu. Stranica je 64 x 64 teksela kvadranta,
redovi duž z i kolone duž x, s ivicom kopiranom od susjeda: 4
teksela na BC4 stranici, 1 na nekomprimiranoj.

Ivice dokazuju postavljanje bez prosuđivanja: dvije stranice jednog sloja jedna
pored druge moraju nositi međusobne rubne teksele. `read_masks` to provjerava za svaki
par koji postavi i odbija nivo u kojem se slaže manje od 99%. Oko
trećine provjerenih nivoa se čita, s ivicama koje se slažu; nekoliko ih nema
oslikanih maski; ostali se odbijaju, gotovo svi tom provjerom (dijelovi
njihovih čvorova drže više nego što ovaj raspored zna). Tlo odbijenog nivoa
dobiva srednju boju svojih materijala površine, a izvoz kaže zašto.
Ivice okrenute prema punom kvadrantu su 255, a one prema praznom 0.

Sekcija od 4.358 bajta i 67 x 67 raster prije stranica se ne čitaju:
njene vrijednosti leže u uskom visokom pojasu, bez malih vrijednosti i bez sentinela.

**Boja tla.** Graf slojeva miješa slojeve u kompajliranom shader
grafu maski, nagiba, visine i šuma, koji se ne čita. `--ground-texture`
boji tlo vlastitim pravilom, rečenim ovdje kao takvim:

- slojevi čija je mapa boje nazvana po udaljenosti su zamjene za daleki pogled
  i izostavljaju se;
- teksturirani slojevi koji pokrivaju devet desetina terena ili više su
  osnova. Njihove maske su gotovo svugdje pune, pa gdje svaki leži
  odlučuje shader, a ne oni: oni nazvani po stijeni ili litici boje nagibe
  strmije od 40 stepeni, oni nazvani po šljunku ravno tlo (ostali slojevi osnove kad
  ga nema), miješano između 20 i 40 stepeni po
  nagibu heightfielda (uzet svakih 4 m i bilinearno raširen preko pečenih
  teksela: ponovljen u blokovima od 4 m crtao je boju stijene kao zakrpe
  oštrih ivica);
- svaki drugi teksturirani sloj polaže se preko osnove vlastitom maskom, redom
  slojeva;
- colormapa se polaže preko rezultata kako to radi engine, dvostruka
  boja tla puta boja mape, tako da je srednje sivo ostavlja kakva jeste; gdje
  colormapa nema teksela tlo uzima srednju svjetlinu mape, u
  sivom.

Provjereno prema medijanu boje tla frejmova igranja triju nivoa
(hroma kao crveno i plavo prema zelenom): pečeno područje igre iznosi 1,00 / 0,69
naspram 1,19 / 0,78 frejmova u jednom, čiji su slojevi trave zeleni gdje
frejmovi pokazuju suhu travu, 1,19 / 0,82 naspram 1,01 / 1,04 u drugom, čija
je colormapa sama topla (1,13 / 0,88), i 1,05 / 0,91 naspram 0,93 / 0,92 u
trećem bez colormape. Frejmovi su osvijetljeni i graduirani, pa ovo
mjeri nijansu, a ne svjetlinu.

**Colormapa.** Drugi dio čvora drži, poslije stranica maski grupa njegovih
kvadranata, četiri BC7 stranice od 132 x 132 (po 17.424 bajta), po jednu za
svaki kvadrant čvora, redom (nizak x, visok z), (visok x, visok z), (visok x,
nizak z), (nizak x, nizak z). Stablo maski kaže koliko bajta zauzimaju stranice maski,
pa se colormapa nalazi brojanjem, a ne po kraju dijela: u jednom nivou
grublji čvorovi nose još četiri takve stranice poslije nje, drugi raster u jednoj ravnoj
boji, a čitanje zadnje četiri stranice dijela gubilo je colormapu preko devet
desetina terena. Bez tog brojanja colormapa je također promašena u
nivoima s nekomprimiranim stranicama maski, čije stranice nisu cijeli broj
BC4 stranica; colormapa jednog nivoa otišla je sa 0,4 na 0,94 njegovog terena. Redoslijed je uklopljen: prema ivicama
heightfielda svakog kvadranta, svaka stranica čvorova s detaljima odgovara jednom
kvadrantu, neokrenuta, sa 0,3 do 0,54 gdje je sljedeće najbolje postavljanje ispod
0,2. Sašiveno njime, stranice nivoa spajaju se bez šava u ceste, vodu
i izgrađena područja probnog nivoa, na 0,5 m po tekselu u području igre. Gdje
slojevi rade posao, colormapa je gotovo neutralna (medijan 110, 107, 104);
drugdje može nositi punu boju. Nivo čiji drugi dijelovi drže samo
nekomprimirane stranice maski nema pročitanu colormapu. Raniji krug ovog čitača
nazvao je te stranice ne-geografskim: poredio ih je s mapom pozadine,
koja može biti sasvim drugi krajolik, i postavljao je svaku stranicu na cijeli
čvor umjesto na kvadrant.

**Albedo odbijenog svjetla** je tražen a nije pronađen: dijelovi korijenskog i
čvorova prvog nivoa su cijele stranice maski, a payload tipa 5 nije
lociran.

**Rupe.** Asset terena nivoa (res tip `0x1CA38E06`) imenuje tri shadera:
zadani shader površine, shader površine za rupe i zadani izvorni shader.
Koji sloj shader rupa čita nije pronađeno, pa heightfield nije izrezan.
U jednom nivou navigacijska mreža može ići po mrežama stijena desetinama metara ispod
heightfielda, gdje ju je igra morala odrezati. Tamo traženo a nepronađeno: maska sloja,
67 x 67 raster, rezervirana visina (nijedna stranica visina nivoa ne drži 0 ili
65.535) i zastavica čvora (svaki čvor ispod korijena ima zastavice 1). Raster stabla
7 i 8 su ono što je ostalo. Oba su kodirana run-length: bajt jednak onom
prije njega slijedi broj daljnjih kopija (`ff ff 84` je 134 bajta
255). Stablo 7 (pločica 256, puno quadtree od pet nivoa, četiri bita po uzorku)
dekodira se u parove bajta vrijednosti 0 do 3; stablo 8 (pločica 265) u bajte uglavnom 255,
s ostalim vrijednostima u pravilnim nizovima. Pločice nijednog još nisu postavljene, pa se ni za jedno
ne zna drži li rupe.

**Decali** se čitaju i peku; pogledajte [Decali terena](#terrain-decals).

## Decali terena {#terrain-decals}

Izvor: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Ceste, piste, betonske platforme, oslikane linije i slova, tragovi guma: res
`TerrainDecals` (tip `0x15E1F32E`) drži ih
kao ravnu geometriju koju igra prebacuje preko terena.

| Dio | Raspored |
|---|---|
| zaglavlje | na +16 broj slotova n, zatim n slotova od 16 bajta, zatim broj zapisa |
| zapisi | jedan po batchu crtanja, jedan za drugim, promjenljive dužine: 156 bajta fiksnih polja — prvi vrh na +32, broj trouglova na +36, tiling teksture u metrima na +44 — zatim bajti vrhova batcha (pomak, veličina), zatim rep koji imenuje njegove teksture preko GUID-ova particija njihovih asseta |
| vrhovi | 32 bajta: x, z (f32), 8 pakiranih bajta, u, v (f32), r, g, b, a (f16); svaki batch je obična lista trouglova |
| indeksi | u32, broje se od 0 u svakom batchu; nisu potrebni |

Provjere:

- rasponi vrhova zapisa slijede jedan za drugim bez praznine i pokrivaju sve
  vrhove tačno, a prvi vrh × 32 svakog zapisa je njegov pomak;
- pročitani tako, trouglovi su kompaktni decali (slova, komadi linije, zakrpe);
  pročitani s pomakom od jednog vrha, to su iverice preko cijele mape;
- gotovo svi batchevi imenuju teksture u repu: mapu boje (`_cv`) s mapom
  prozirnosti (`_op`, crveni kanal), ili za oznake kanalnu masku (`_rgb`).

Poslije GUID-ova tekstura rep nosi parametre materijala batcha,
kodirane kao u shader bloku (pogledajte Nijanse niže). Boja farbe
oznake, traga gume ili linije je float3 hashiran `607e`: pjeskovita 0,64,
0,56, 0,48 za tragove guma u pijesku, gotovo crna za katran. Mape prozirnosti su
uglavnom format 62, jedan kanal na 8 bajta po bloku, čitane kao BC4.

Batch mapira svoju teksturu ili po svjetskoj poziciji (u = x, v = z, tekstura
se ponavlja svakih tiling-metara: asfalt, beton, šljunak) ili 0 do 1 preko
decala (linija, slovo, trag gume). Zapisi se crtaju redoslijedom u datoteci.

**Pečenje.** `level --ground-texture M` slika, ispod opsega decala i
pločica od najviše 4.096 piksela, mapu boje pozadine (bilinearno), a zatim svaki
batch preko nje po njegovoj prozirnosti × alfa vrha. Boja vrhova se ne
koristi: vrhovi nekih batcheva su čisto zeleni ili plavi, što je bojilo oznake
nivoa tim bojama. Trouglovi heightfielda tamo postaju
dijelovi `ground:terrain x<x> z<z>` koji nose pločicu. Svaki batch se crta s:

| Batch imenuje | Crta se kao |
|---|---|
| mapu boje (`_cv`) | mapa, po svojoj mapi prozirnosti |
| multiply mapu (`_mult`) i mapu prozirnosti | farba (bijela gdje je materijal ne imenuje) puta multiply mapa, po mapi prozirnosti: izlizana središnja linija piste, rubne linije i pragovi |
| kanalnu masku (`_rgb`) | farba, inače bijela za linije i slova, tamna za obrise, blago zatamnjenje za habanje, tragove guma, mrlje, lokve i vlažnost, po maski |
| samu mapu prozirnosti, s farbom | farba po mapi prozirnosti: tragovi guma |

Maska varijacije ceste nije farba nego varira površinu ispod sebe, stotinama
metara široko, i ne crta se, bez obzira na njenu farbu: oslikana bijelo
polagala je dva blijeda pravougaonika dugačka 150 do 250 m na padine nivoa. Mapa `_mult`
uzima se kao vlastito habanje farbe, a ne kao zatamnjenje tla ispod nje:
gotovo je bijela, a oblik linije je u mapi prozirnosti.

Gotovo svaki batch se crta, u nekoliko pločica na 0,5 m po pikselu; izvoz
naraste za nekoliko MB i traje nekoliko sekundi duže. Viđene odozgo,
platforme, rulne staze i mreža cesta leže ispod ograda i zgrada kompleksa i
vode do njihovih kapija.

Crtani umjesto toga kao vlastita geometrija, decali bi trebali alfa miješanje, koje
pisač ne nosi, i pomak iznad terena s kojim bi
imali z-fighting; pečenje ih zadržava u vlastitoj boji tla.

## Teksture i materijali {#textures-and-materials}

Izvor: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Texture res (tip `0x6BDE20BA`) je zaglavlje od 180 bajta: tip i format piksela
na +8, širina i visina na +22, broj mipova na +30, GUID dijela na +40, petnaest
veličina mipova na +56. Dio je lanac mipova, najveći prvi. Nekim dijelovima nedostaju
najveći mipovi, koji se isporučuju u paketu visoke rezolucije, a dužina dijela
kaže od kojeg mipa počinje. Dio tog paketa imenovan je na +164; čita se
iz [dodataka](#which-table-is-the-level) nivoa kad se traži mip koji glavnom
dijelu nedostaje, a njegova dužina plus dužina glavnog dijela je cijeli lanac.

| Format | Dekodira se kao | Dokaz |
|---|---|---|
| 67, 66 | BC7 (sRGB, linearno) | list boje plastičnog rezervoara dekodira se kao jedan; kao BC3 isti bajti su šum |
| 61, 60 | BC3 | list sanduka dekodira se čisto kao BC3, ne kao BC1 ili BC7 |
| 57, 56, 55 | BC1 | pola bajta po pikselu |

Asset mreže ne imenuje nijednu teksturu. Veza je u **depoima shader blokova**
nivoa (res tip `0x73312045`, jedan po pod-svijetu), s ključem od osam bajta na
+0x130 zapisa sekcije mreže:

| Dio | Raspored |
|---|---|
| tablica, na 16 | (ključ sekcije u64, pomak deskriptora u64), dok pomak ne padne izvan resa |
| deskriptor | (pomak bloka u64, hash u64, veličina bloka u64) |
| blok | shader parametri sekcije; svaka tekstura je zapis od 49 bajta: bajt, 16 bajta, GUID particije asseta teksture, njen GUID instance |

Ključ sekcije sanduka pojavljuje se jednom u svakom od deset depoa
pod-svjetova koji ga postavljaju, a njegov blok imenuje `t_mil_crate_03_cs` i `_nmt`
među zajedničkim detail mapama. Blok imenuje svaku teksturu koju shader uzorkuje,
a koja je od njih mapa boje nije navedeno, pa se bira: sRGB 2D
tekstura čije ime sadrži najviše riječi imena materijala
(`M_ConcreteWall_01`: concrete, wall), zatim imena mreže, zatim ona koja nije
detail, decal (`t_de_...`) ili mapa oštećenja, zatim ona koju koristi najmanje blokova. Blok
prometnog znaka imenuje njegovu ploču `t_com_highwaysignage_01_cs` i list
decala `t_de_com_highwaysignage_01_ca` sa štitom položenim na bok; obje se poklapaju
s riječima, a bez pravila za decal list je pobjeđivao po upotrebi i znak je prikazivao
štit okrenut za četvrtinu, kroz svaki skup koordinata teksture koji sekcija
ima. Polja udaljenosti (`..._sdf`), palete i kanalne maske (`_rgb`)
nikad se ne biraju, bez obzira na riječi koje dijele (mape `_rgba` se biraju: većina su boja
s alfom, a njihovo izostavljanje je mijenjalo vlastite mape dalekovoda i stepeništa
nepovezanim mapama): atlas vegetacije pozadine `..._atlas_a_sdf`
nacrtan kao boja prikazivao je crno-bijele zvijezde umjesto drveća, paleta zgrada pozadine
konfete uzoraka umjesto zidova, a stakleni krš nacrtan kroz svoju kanalnu masku ispao je
cijan. Sekcija čiji su jedini kandidati zajedničke detail mape ostaje ravne boje.

**Palete.** Zgrade pozadine uzimaju boje iz palete, 256 x
256 teksela uzoraka 16 x 16: svaki vrh nosi četiri bajta (upotreba `0x1E`)
čija prva dva kažu gdje je u paleti njegova boja, x i y od 255.
`level` crta takvu sekciju s paletom kao teksturom, svaki vrh u
središtu svog uzorka. Nacrtani tako, blokovi pozadine nivoa ispadaju
pastelnih zidova, terakote i tamnih prozora tamo gdje su bili obične bijele.

**Preklopi (overlays).** Veliki objekti tilaju trim list kroz svoje prve koordinate
teksture i polažu preklop preko njega kroz druge, koje leže unutar
0 do 1: razvijanje (unwrap) cijelog objekta. Preklop (`..._overlay_cs`, s njegovom
maskom `..._overlay_a`) nosi kako objekt izgleda izdaleka, crvene pojaseve i
rđu naftnog rezervoara; nacrtani samo s trim listom, rezervoari jednog
nivoa ispali su kao sive ploče. Sekcija čiji blok imenuje preklop s
njegovom maskom, a čije su druge koordinate takvo razvijanje, crta se s
preklopom kroz njih (36 sekcija u tom nivou).

**Nijanse (tints).** Mnoge mape boje su sive (srednje vrijednosti njihovih kanala unutar 6% jedne od
druge): shader ih boji bojama iz parametara bloka. Poslije
unosa tekstura (po 49 bajta) blok navodi svoje parametre, svaki s oznakom
tipa (`f11af825` float3, `a5e1f2de` float4, `c1b1a014` float,
`4a4fc3a1` cijeli broj), bajtovima zastavica `01 80` za jednu vrijednost, dvobajtnim hashom
imena parametra, u32 brojem, vrijednošću i osmobajtnim id-om. Imena
nisu pohranjena. Sedam float3 hasheva imena djeluje kao nijanse: u jednom nivou
tri od njih drže boju u otprilike 1 bloku od 6 čija je mapa siva i gotovo
nikad tamo gdje mapa ima vlastitu boju, a ostali drže boje u kojima se siva
mapa slika gdje to kaže ime materijala (`..._blue` obloga mosta:
0,047, 0,098, 0,171 naspram neutralnih 0,5). Porodica može držati
nekoliko vrijednosti, po jednu za kanal maske, većinu neutralnih, a vrijednost
s kanalom blizu ništice (čisto zelena na fasadama od cigle) bira kanal maske
umjesto da farba. `level` množi sivu mapu boje, u linearnom
svjetlu, prvom vrijednošću svake porodice koja nije ni neutralna ni takav
selektor, preko njene neutralne, i zadržava rezultat kao vlastitu teksturu;
mapa s bojom ostaje kakva jest. Pravilo je vlastito izvoznikovo:
koji kanal maske uzima koju nijansu nije pročitano. U jednom nivou to je
udio trouglova struktura nacrtanih skoro bijelo spustilo sa 19,4% na 3,9%.

**Varijacije objekata.** Jedna mreža se postavlja u nekoliko izgleda: zid
skladišta s crvenom ili plavom prugom i drukčijim brojem oslikanim na njemu,
kontejner u zelenoj ili sivoj. Svaka postavljena kopija imenuje svoj izgled:

| Gdje | Polje |
|---|---|
| član grupe statičkih modela | +32: niz od jednog pokazivača po kopiji, na varijaciju objekta ili null |
| referenca objekta | +120: pokazivač na varijaciju objekta ili null |
| varijacija objekta (particija `ov_...`, tip `235f2a9c...`) | njena prva instanca +32: u32 hash imena varijacije |

Izgled sekcije u varijaciji je shader blok s ključem vlastitog ključa
sekcije kojem je hash varijacije dodan prvim četirima bajtima, kao
little-endian u32 (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`);
sekcija bez bloka pod tim ključem izgleda isto u svakoj varijaciji.
Baze varijacija mreža nivoa (`meshvariationdb_win32`) navode, po mreži
i hashu varijacije, materijale koje svaka varijacija dira, ali ne i ključeve:
pravilo je nađeno iz samih ključeva i vrijedi za svaku provjerenu sekciju s
varijantama (četiri varijacije jednog zida, po tri njegove sekcije).
Blok varijacije donosi vlastite teksture kao i nijanse: oslikani broj
na zidu je list slova koji blok varijacije imenuje.
Velik udio grupiranih kopija postavljen je u varijaciji.

Blok se peče jednom za svaki skup sadržaja, a unos depoa za
ključ nosi njihov hash (drugi u64 unosa). Gdje sekcija nema
blok pod ključem svoje varijacije, varijacija je ipak dosegne preko
*blizanca*: druge sekcije čiji zadani blok ima isti sadržaj i
ima ga. Bez blizanaca, zid čije dužine dijele jedan zadani blok može ispasti u
dvije boje. Sekcija bez vlastite varijante uzima varijantu koju ima većina
njenih blizanaca.

**Destruktivne mreže.** Mreža koju meč može srušiti ima asset uništenja
vlastitog imena pored sebe (`.../br_x.destruction` za
`.../br_x_mesh`): zgrade i zidovi koji se mogu razbiti (`br_`) i mnogi rekviziti.
`level` drži njihove površine u vlastitim dijelovima, nazvanim s
` (destructible)`, čiji glTF čvorovi nose `{"destructible": true}`. Njihova
uništena stanja su mreže `dc_..._part<N>_mesh` pored njih, svaka
centrirana na vlastito ishodište; gdje dio stoji je u assetu uništenja,
koji se ne čita, pa uništena stanja nisu izvezena.

**Izostavljeno.** Sekcije materijala za blokout placeholdere (`M_Whitebox`: nekoliko
velikih neteksturiranih trouglova koje neke zgrade drže pored svojih površina,
a koji su stršili iz nivoa kao bijela peraja), mreže napravljene za kinematike (helikopter
postavljen tamo gdje njegova scena počinje) i pomoćnici osvjetljenja (ravni koje blokiraju svjetlo,
nikad se ne crtaju). Generirane zgrade pozadine nivoa
(`..._generated_blueprints_..._mesh`) se crtaju, ali materijal njihovih zidova
imenuje samo noise mape, a njihovi vrhovi ne nose boju, pa ostaju obični. Gotovo svaka
nacrtana sekcija dobiva mapu boje.

**Listovi slova.** Oslikani broj na zidu ili natpis na dizalici je
vlastita sekcija čija je mapa boje list (`_ca`): alfa slova preko
pune boje, ili otisak. Njene prve koordinate teksture tilaju žbuku zida
preko ploče (u -0,2 do 1,7 na jednom zidu), što crta list
gotovo dvaput; četvrti skup (`0x24`, inače treći, `0x23`) polaže ga
tačno jednom (u -1 do 0, v 1 do 2, nekoliko hiljaditih preko u grubljim
nivoima detalja). Gdje prvi skup ostavlja jednu kopiju slike, a
četvrti ili treći leži unutar jedne, list se crta kroz to, pomaknut u
0 do 1. List s alfom crta se 1 cm ispred površine na kojoj je naslikan,
a ona se crta ispod njega u drugoj mapi boje bloka kroz
prvi skup: bez toga prazni teksel lista pokazivali su unutrašnjost zida.
Drugi skup je razvijanje objekta za njegov preklop i ovdje se ne koristi.

**Cut-out mape.** Četvrti kanal mape boje znači različite stvari
prema imenu mape. U `_cs`, daleko najčešćem (893 od izabranih mapa jednog nivoa),
to je glatkoća: 1% alfe medijan mape leži unutar 0,1 od 0 ili 1.
U `_cu` (lišće, trava) i `_ca` (boja i alfa) to je prozirnost: 90% i
87%. Mapa boje nazvana `..._cu` ili `..._ca` čija je alfa najmanje 75% blizu
0 ili 1, najmanje 1% ispod 0,5 i najmanje 5% iznad upisuje se sa svojom alfom,
kao PNG, a njen
materijal kao glTF `alphaMode` MASK, `alphaCutoff` 0.5, dvostrano; kartice lišća
tada prikazuju lišće, a ne svoje crne uglove. Mapa lišća jednog drveta uopće nema alfu
(najviše 4 od 255): njegove grane su rezane geometrijom, a sa samo prva
dva uvjeta cijela krošnja je bila odrezana.

Koordinate teksture su upotreba vrhova `0x21`, dvije polovine (format 6) ili dva
floata (format 2). Sekcije nose do tri dodatna skupa (`0x22` do `0x24`) za
decal i detail slojeve. Koordinate se tilaju: rebrasta strana kontejnera ide
od -1,6 do 1,8, pločice pozadine terena leže potpuno izvan 0..1, a u
jednom nivou 23% teksturiranih trouglova sežu izvan 0..1. Upisuju se
kakve jesu, s uzorkivačem koji se ponavlja; 3DHeat preglednik omata svaku teksturu koja se ponavlja
unutar svog atlasa. Renderer koji ih umjesto toga ograničava razmazuje rebra
na dvostruku širinu, pretvara betonski pod u pruge duž jedne ose, i
daje čeličnim gredama tornja boju ruba njihove teksture; za njega,
`--clamped-uvs` siječe svaki trougao duž linija gdje se njegova tekstura ponavlja
i pomiče svaki komad u 0..1 (pogledajte [Format izlaza](output-format.md)).
Poslije toga 0,03% teksturiranih trouglova, preko kojih se tekstura ponavlja više
od 16 puta, seže izvan, a trougao koji bi sječenje napravilo od više od
4 komada crta se u prosječnoj boji svoje teksture: kora se ponavlja
niz svaku granu, a isječena, drveće jednog nivoa otišlo je sa 6,4 na 24 miliona
trouglova.

Heightfield nema vlastitu mapu boje koja bi se mogla pročitati. Gdje ga pokriva jedna od
mapa pozadine terena, boji se iz nje: koordinate teksture pozadine su linearna
funkcija svjetskih x i z (99% njenih vrhova unutar 0,001 od nje; mapa
pokriva kvadrat od 65.536 m, okrenut za četvrtinu), a ista funkcija daje
heightfieldovu. Nivo isporučuje mipove te mape od 2.048 px naniže, pa
heightfield dobiva 32 m po pikselu. Njegova tamna stijena leži na strmom tlu:
korelacija tamnoće s nagibom je 0,48, a najviše 0,34 za sedam drugih
orijentacija.

Pozadina drugog nivoa je osam bliskih i osam dalekih pločica oko područja igre,
svaka ponavlja vlastitu teksturu preko pločice, a nijedna ne dosegne
heightfield. Svaka tekstura pozadine uklapa se zasebno, a kad nijedna ne pokriva
heightfield, uzima prosječnu boju koju pozadina pokazuje unutar
kilometra od kvadrata terena, preko koje `--ground-texture` peče decale.
Materijal pozadine je onaj čije ime sadrži `TerrainBackdrop`, ili `BD_` i
`Terrain` (`M_BD_<site>_Terrain..._Near`); ili mreža pozadine
(`bd_..._terrain<site>_04_far_mesh`) nosi običan materijal terena
(`M_<region>_Terrain<site>_04_Far`), što su prva dva pravila promašila u jednom
nivou pa je njegovo tlo bojeno iz njegovih površina.

Gdje nijedna mapa pozadine ne pokriva heightfield, on ipak uzima srednju
boju vlastitih površina terena prije prosjeka pozadine: `_cv`
mape boje koje imenuju shader blokovi njegovog grafa slojeva (27 u jednom nivou: pijesci,
šljunci, tla, trava, napukli beton), svaka usrednjena, zatim medijan
svakog kanala, izostavljajući zadanu površinu enginea. Pozadina može biti
sasvim drugi krajolik: u jednom nivou njen prosjek (95, 99, 80 u sRGB)
pretvorio je tlo područja igre u sivu koju igra ne pokazuje. Uz `--ground-texture`, ta boja se
množi s dvostrukom colormapom, koju srednje sivo ostavlja kakva jest, i peče
s decalima preko opsega i decala i colormape.

Prema igri, medijan boje tla pečenog područja igre svakog nivoa
i frejmova igranja (redovi 55 do 72% slike pored HUD-a, po 24
frejma; sRGB; frejmovi su osvijetljeni i graduirani, pa su odnosi r/g i b/g
pošteno poređenje):

| Nivo | Frejmovi | Prosjek pozadine | Sada |
|---|---|---|---|
| prvi | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| drugi | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| treći | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Prvi je ispravljen; druga dva su ranije bila malo bliže po nijansi. Jedna
boja za cijeli nivo ne može biti ispravna svugdje; maske bi bile.

## Navigacijska mreža {#navigation-mesh}

Izvor: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Nivo isporučuje jednu particiju po agentu, `<level>/dbt/<level>_navmesh_layer_<n>`:
u jednom nivou sloj 0 je vojnik (visok 1,8 m, stepenica 0,18 m, radijus 0,4 m), a
dva druga su vozila (visoka 3,5 i 10 m). Svaka particija drži dva niza:

| Niz | Element |
|---|---|
| tiles | 28 bajta: u32 0, u32 hash, u32 0, u32 indeks dijela, u16 tile x, u16 tile z, u32 pomak, u32 veličina |
| chunks | 20 bajta: GUID dijela, u32 veličina |

Pločica (tile) je `size` bajta na `offset` u dijelu `chunk index`, little-endian, i
raspoređena kao Detourova (Recast Navigation) iza dužeg zaglavlja:

| Pomak | Sadržaj |
|---|---|
| 0 | `VAND`, verzija 7 |
| 24 | brojevi: poligoni, vrhovi, veze, detail mreže, detail vrhovi, detail trouglovi, čvorovi graničnog volumena, off-mesh veze, prvi off-mesh poligon |
| 188 | visina agenta, stepenica, radijus |
| 200 | granični okvir pločice, šest floata |
| 232 | vrhovi: x, y, z floatovi, svjetske koordinate |
| sljedeća 8-bajtna granica | poligoni, 32 bajta: u32, šest u16 indeksa vrhova, šest u16 susjeda, u16 zastavice, broj vrhova na +30, na +31 površina (nižih šest bita) i vrsta (gornja dva) |
| zatim, pakirano | veze (16 bajta), detail mreže (12: prvi detail vrh u32, prvi detail trougao u32, broj vrhova i trouglova u8), detail vrhovi (tri floata), detail trouglovi (tri indeksa i zastavice), čvorovi graničnog volumena (16), off-mesh veze (80) |

U svakoj pločici provjerenih nivoa ovo se zbraja na veličinu pločice do
bajta, a detail mreže broje poligone prije prvog off-mesh.

Poligon je ravan između svojih uglova; njegova **detail mreža** drži
stvarnu visinu površine preko neravnina, stijena i stepenica, i ona se crta. Indeks
detail trougla ispod broja uglova poligona je taj ugao,
inače detail vrh `first + index - corners`. Lepezasto razlaganje poligona
umjesto toga stavlja mnogo više trouglova ispod terena i pravi duge iverice;
s detail mrežama nijedna nije duža od dijagonale pločice od 16 m plus uspon
uz padinu.

Vrsta 0 je tlo, vrsta 2 male strme zakrpe (oko 45 stepeni, kvadratni metar
svaka), vrsta 1 veza između površina: njeni uglovi obuhvataju 125 m visine ili više
i leže izvan pločice, neki u ishodištu. Veze se izostavljaju; ostalo se
crta po detail mrežama, ili lepezasto u pločici bez njih.

Provjere: veličine dijelova zbrajaju se tačno u veličine pločica; svaki vrh površine
leži unutar okvira svoje pločice plus-minus oko metar; gotovo svi trouglovi
gledaju prema gore. Pločica koja ne prođe
odbija se i broji, a u tom nivou nijedna.

Šta mreža vojnika pokriva, viđeno odozgo u probnom nivou: tlo,
podove, stepenice i neke krovove, a ne vrhove teretnih kontejnera. To je AI-jeva mapa gdje vojnik može stajati,
najbliže što datoteke dolaze tome gdje stoje igrači.

## Nije implementirano {#not-implemented}

- Graf slojeva terena, koji miješa njegove slojeve površine (pogledajte
  [Slojevi terena](#terrain-layers)): boja tla slijedi pravilo
  ovog čitača iz maski slojeva i nagiba heightfielda, a
  nivoi čije se stranice maski ne uklapaju dobivaju jednu boju.
- Parametri boje materijala decala: oznake kroz kanalne maske su
  slikane neutralnom bojom.
- Nacrti objekata koji nisu mreže (logika igre, efekti, zvukovi).
- Uništena stanja destruktivnih mreža: mjesta njihovih dijelova su u
  assetu uništenja, koji se ne čita.
- Veze navigacijske mreže (skokovi, ljestve, preskakanja) i njeni slojevi za vozila.
- Nivoi mreža pohranjeni ugrađeno u resu (10 mreža u nivou, gadgeti), kosti i dijelovi
  skinned i kompozitnih mreža, te normale (računa ih pisač).
- Normal, roughness i druge mape; alfa osim cut-outa (prozirno
  staklo i decali crtaju se neprozirni).
- Rupe terena: shader površine za rupe je imenovan, ali šta čita nije
  pronađeno (pogledajte [Slojevi terena](#terrain-layers)), pa heightfield nije izrezan
  gdje prohodno tlo ide ispod njega.
- Koja nijansa ide s kojim kanalom maske materijala: siva mapa boje
  uzima prvu nijansu koja nije neutralna (pogledajte
  [Teksture i materijali](#textures-and-materials)).
- Efekti (`fx/` putanje) i mreže kablova, čiji su granični okviri dugi desetine
  kilometara; izostavljaju se i broje u sažetku.
- XOR-zamućeni oblik tablice.
