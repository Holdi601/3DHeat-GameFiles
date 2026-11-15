---
title: Frostbite
nav_order: 5
lang: "hr"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, snopovi, mreže i razine {#frostbite-toc-cas-bundles-meshes-and-levels}

**Čita Battlefield 6 razinu do njezina terena, njezinih postavljenih mreža i njihovih mapa boja, i zapisuje je kao `.glb`.** Frostbite igre (Battlefield, Need for Speed, Dead Space) čuvaju svoj sadržaj u `.cas` blobovima, opisanim `.toc` tablicama sadržaja. Tablica razine kaže koje snopove razina učitava, snopovi imenuju svako sredstvo, a sredstva kažu koja mreža stoji gdje.

Izvori:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tablice, paketi, korisni tereti),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(snopovi i njihovi manifesti),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX particije),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(visinsko polje),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(teksture i materijali),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(postavljanje i izvoz).
Naredbe: `identify`, `levels`, `level` (vidi [Naredbe](commands.md#levels-and-level-frostbite)).

Igra ovo ništa ne dokumentira. Svaki raspored ispod pročitan je iz datoteka, a zatim provjeren na svima njima, i svaki odjeljak kaže što je bila provjera. Gdje alati za modifikaciju Frosty opisuju starije verzije strukture, nazivi polja slijede njihove; nijedan kod nije preuzet od njih (vidi [Pravila i licence](rules-and-licences.md)).

## Zaglavlje koje izgleda šifrirano, a nije {#the-header-that-looks-encrypted-and-is-not}

| Magija (u32, little-endian) | Značenje | Obrada |
|---|---|---|
| `0x00CED100` | plain: stablo počinje odmah | pročitano |
| `0x01CED100` | signed: potpis od 556 bajtova, zatim stablo **u čistom obliku** | pročitano |
| `0x03CED100` | XOR-zamagljeno, s ključem u vlastitom zaglavlju datoteke | otkriveno i odbijeno |

Potpisani oblik je ono što isporučuje aktualni Battlefield. Bajtovi visoke entropije iza magije su potpis, a ne šifrirani tekst.

## Stablo DbObject {#the-dbobject-tree}

Jedna rekurzivna struktura. Svako polje je bajt vrste (donjih pet bitova je vrsta, bit 7 je "anonymous"), izborno ime i vrijednost. Spremnici nose svoju duljinu kao cijeli broj promjenjive duljine i završavaju nultim bajtom. `parse_toc` provjerava duljinu svakog spremnika, pa datoteka koja se raščlani znači da je razumljena. `layout.toc` je u ovom obliku.

## Instalacijski paketi {#installation-packages}

Svaka lokacija imenuje **instalacijski paket** kojem njezin blob pripada. Svaki paket numerira svoje blobove od `cas_01`, pa je sam broj bloba dvosmislen čim je instalirano više od jednog paketa, a to je uvijek.

- `layout.toc` navodi pakete pod `installManifest.installChunks`, svaki s `persistentIndex` i `installBundle`, na primjer `Win32/installation/<package>`.
- Blobovi paketa su u toj mapi, pod `Data` za osnovnu igru ili pod `Update/<pack>/Data` za ono što je došlo kasnije.
- Zapis lokacije nosi puni 32-bitni `persistentIndex`: donja polovica njezine prve riječi drži gornju polovicu, a gornja polovica njezine druge riječi donju polovicu; donja polovica druge riječi je broj bloba.

Provjera: svaka lokacija u svakoj binarnoj tablici instalacije razrješava se u deklarirani paket i pada unutar bloba koji imenuje. Ranija verzija uzela je prvi `cas_NN.cas` pravog broja. Trećina korisnih tereta koje je čitala tada izgledala je kao visoka entropija i bila je uzeta za šifriranje. Bili su to pravi pomaci u krivoj datoteci. Ništa pronađeno nije šifrirano.

## Tablica razine {#the-level-table}

Tablica razine (`levels/<level>/<level>.toc`) je tablica odjeljaka: petnaest big-endian zaglavnih riječi, zatim odjeljci poredani jedan za drugim, čiji su pomaci i navedeni i izvedivi iz dva brojanja.

| Odjeljak | Sadržaj |
|---|---|
| snopovi (bundles) | tablica heša (po jedna riječ), zatim zapis od 16 bajtova po snopu: ključ, `0x40000000` \| veličina, 0, pomak |
| tablica heša chunkova | jedna riječ po chunku |
| chunkovi | 16-bajtni id (GUID chunka **s obrnutim bajtovima**), zatim riječ: `0x80000000` \| 4 x indeks njegove lokacije |
| lokacije | četiri big-endian riječi: paket (podijeljen), blob, pomak, veličina |

Id-ovi chunkova i lokacije su **u različitom redoslijedu**. Čitanje po redoslijedu u datoteci uparuje svaki chunk s bajtovima drugog chunka, koji se dobro dekodiraju (uglavnom kao zvuk), pa ne izgledaju pogrešno dok mreža ne ispadne kao šum. Provjera: u razini, indeksne riječi su permutacija od 0 do broja chunkova minus jedan.

Snopovi su spremljeni unutar tablice odjeljaka, odmah iza nje. Svaki ima devet big-endian zaglavnih riječi, zatim svoje stavke: osam bajtova pomaka i veličine, a prije njih još osam koji imenuju paket i blob kada gornji bit bajta zastavice stavke stoji. Provjera: na svakom snopu zadnja stavka završava upravo tamo gdje počinju bajtovi zastavica.

### Koja je tablica razine {#which-table-is-the-level}

Razina može imati nekoliko tablica istog imena: jednu u `Data` osnovne igre, jednu u svakoj nadogradnji (`Update/<pack>/Data`) koja je isporučuje ili mijenja, i jednu u svakom paketu visoke razlučivosti (`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Samo neke sadrže snopove. Za razinu koju nadogradnja isporučuje, tablica u osnovnoj igri sadrži samo chunkove i nema snopova, a ona u nadogradnji je razina; uzimanje prve pronađene tablice nije izvezlo ništa od nje.

Razina je dakle tablica s najviše snopova, a kasniji sloj pobjeđuje u izjednačenju (prvo osnovna igra, zatim nadogradnje po imenu). Tablice istog imena bez snopova su njezini **dodaci**: njihovi chunkovi dodaju se razinskima, jer drže najveće mipove njezinih tekstura. Zaglavlje teksture imenuje taj chunk na +164 (vidi [Teksture i materijali](#textures-and-materials)). `levels` ispisuje odakle dolazi svaka razina i koliko dodataka ima.

## Manifesti snopova {#bundle-manifests}

Prva stavka snopa je njegov manifest, spremljen nekomprimiran. To je binarni format snopova ranijih Frostbite igara s novom magijom, `0xD68E799D`: brojevi, SHA-1, zapisi ebx i res (pomak i veličina imena), vrste res, metapodaci i id-ovi, GUID-ovi chunkova, nizovi. Ostale stavke snopa su ebx, res i chunkovi tim redom. Provjera: brojevi se podudaraju sa stavkama na svakom snopu, a nizovi počinju tamo gdje zapisi završavaju.

Vrste resursa su heševi. `0x49B156D4` je MeshSet (svaki res te vrste imenovan je `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` čita sve ovo za jednu razinu, za nekoliko sekundi: razina ima desetke snopova i desetke tisuća ebx, res i chunkova.

## Blokovi korisnog tereta {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Nulta komprimirana veličina znači da je blok spremljen bez kompresije, ako se ona podudara s dekomprimiranom veličinom.

| Riječ metode | Kodek |
|---|---|
| `0x0070`, `0x0071` | nema |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), iz vlastite DLL-a igre `oo2core`) |
| ostalo, s jednakim veličinama | kopira se kao spremljeno |
| ostalo | odbijeno |

Pročitano iz pravog paketa, svaki uzorkovani korisni teret se dekodira.

## EBX particije {#ebx-partitions}

EBX sadrži sve što nije sirovi podatak. Svaka particija je RIFF datoteka: `EBXD` (podaci, poravnati na 16), `EFIX` (GUID particije, GUID-ovi vrsta i potpisi, instanca, pokazivač, uvoz i pomaci informacija o vrsti, uvozi, te pomaci nizova, boxed vrijednosti i stringova), `EBXX` (tablica nizova: pomak, broj, heš, zastavice, vrsta elementa). Polje pokazivača je osam bajtova: nula je null, neparna vrijednost je broj uvoza `value >> 1`, a sve ostalo je relativno u odnosu na polje.

**Biblioteka vrsta se ne može pročitati.** Igra je isporučuje u svom početnom datotečnom sustavu, koji je šifriran, a ovaj paket ga ne dira. Vrste se prepoznaju po GUID-u i potpisu, koje nosi svaka particija, a nekoliko vrsta koje izvoz razine treba posloženo je iz podataka.

## MeshSet {#meshset}

Mreža je MeshSet res (opis) i jedan chunk po razini detalja (međuspremnici).

| Dio | Raspored |
|---|---|
| prefiks | četiri riječi: veličina zaglavlja (176 ili 192), veličina zapisa razine (176 do 188), veličina zapisa odjeljka (368), 0 |
| zaglavlje | okvir; šest i64 pomaka razina; vrsta mreže na `0x6C` (rigid, skinned, composite); brojevi razina i odjeljaka na `0x9C` |
| razina | odjeljci na `+0x08`; pet popisa crtanja na `+0x14` (neprozirni, prozirni, dekal, samo dubina, sjena); vrsta indeksa `+0x54` (`0x21` u16, `0x2E` u32), bajtovi indeksa i vrhova; GUID chunka na `+0x74` |
| odjeljak | ime materijala; korak vrhova; trokuti, prvi indeks, pomak vrhova (u bajtovima), broj vrhova na `+0x20`; deklaracija vrhova na `+0x64`: 16 x (usage, format, offset, stream), 16 koraka tokova, brojevi |
| chunk | međuspremnik vrhova, zatim međuspremnik indeksa. Tokovi odjeljka slijede jedan za drugim; indeksi se broje od prvog vrha odjeljka |

Pozicije su usage 1, stream 0, offset 0, kao četiri polovice ili tri float-a. Crtaju se samo neprozirni i prozirni odjeljci. Svaki odjeljak imenovan `..._shadow` nalazi se u popisu sjena i samo tamo, pa popisi odlučuju.

Provjera: svaka mreža razine čije su razine spremljene u chunkovima se dekodira, a gotovo sve imaju 99% ili više vrhova unutar deklariranog okvira; ostale promaše zbog zaokruživanja polovičnih float-ova. Dekodirana kutija mjeri oko jedan metar, Y gore, s normalama koje pokazuju prema van.

## Postavljanje {#placement}

Proces sadržaja skuplja statične predmete svakog podsvijeta u **grupu statičkih modela**: niz članova, po jedan za svaku mrežu, svaki sa svojim transformacijama instanci.

| Vrsta (GUID, potpis) | Raspored |
|---|---|
| član `ad13064e…`, `0xF861A878` | 224 bajta: `+88` niz transformacija, `+112` blueprint predmeta (uvoz), `+160` sredstvo mreže (uvoz) |
| transformacija `101dce06…`, `0x5E6D8C37` | 64 bajta: right, up, forward, translation, svaki vec3 dopunjen na 16 |

Particija sredstva mreže imenovana je kao njezin MeshSet res, pa GUID particije uvoza daje mrežu. Točka se nalazi na `x·right + y·up + z·forward + translation`. Vlastita transformacija grupe bila je identitet u svakoj grupi provjerenih razina i ne primjenjuje se.

Provjera: u razini, svaki član svake grupe razrješava se u mrežu; većina kopija ima rotaciju determinante 1 do tisućinke, ostale su skalirane ili zrcaljene. GUID-ovi vrsta i potpisi isti su u drugim razinama. Igrina nadogradnja koja promijeni raspored mijenja potpis, a čitač tada ne nađe ništa, umjesto da pogrešno čita.

### Predmeti postavljeni pojedinačno {#objects-placed-one-by-one}

Ono što proces ne može grupirati (uništivi predmeti, kontejneri, krhotine) postavlja se preko **referenci predmeta** i **referenci prefaba** u particijama razine:

| Vrsta (GUID, potpis) | Raspored |
|---|---|
| referenca predmeta `a9a6a6ad…`, `0xC4856BEC` | `+32` transformacija (kao gore), `+112` blueprint predmeta (uvoz) |
| referenca prefaba `117c746e…`, `0xDE3FE9B4` | isto; blueprint je prefab, particija s daljnjim referencama |

Prefabi se gnijezde; kopija se nalazi na vlastitoj transformaciji pomnoženoj s roditeljskom (vektori redaka), do osam razina. Blueprint predmeta crta se kao mreže koje uvozi, bez uništenih stanja (`dc_...`). Grupirani prefab se referencira kao svoj ostatak `..._nongroupable_autogen`, pa se ništa ne crta dvaput.

Obilazak počinje samo od svjetova i slojeva razine. Particija čija je prva instanca blueprint prefaba (`134919fc…`, `0x0247807D`) je definicija prefaba, a razina ih drži mnogo pod vlastitom mapom, postavljenih po svjetovima na načine koji nisu ove reference; kada bi se obilazili kao svijet, prefab bi stavio svoj sadržaj na lokalne koordinate. To nagomila stotine kopija oko ishodišta svijeta, daleko ispod tla. Svjetovi i slojevi imaju `a10ebe0f…`, `0xD3D16C3C` na prvom mjestu.

Blueprinti postavljeni izvan igre se ne prate: razvojna i testna sredstva (`game/dev/`, `test/`), postava završnog filma runde (`..._gameend_...`: postavljena pod tlom) i kontroler kamere smrti (`.../deathflow/...`, čiji su rekviziti na ishodištu svijeta). Prepoznaju se po putanji sredstva, a ne po sloju: isti sloj koji sadrži postavu filma može postaviti prave zidove i krovove razine. Nakon oba pravila nijedna kopija u provjerenim razinama ne leži više od 10 m pod terenom, a kopije stoje na terenu tamo gdje ih igra prikazuje.

**Razine detalja koje zamjenjuju.** Posljednja razina detalja mreže se može prebaciti na zamjenu za daleki pogled s vlastitim materijalom: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Rešetkasti toranj od desetaka tisuća trokuta može završiti siluetom od nekoliko stotina, koju bi proračun odabrao, a koja izbliza ispada kao čvrst šiljak. Razina detalja koja uvodi takav materijal, koji njezina najfinija razina nema, nikad se ne bira; najgrublja razina mreže je posljednja prava.

## Teren {#terrain}

Izvor: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Teren je TerrainStreamingTree res (vrsta `0x22FE8AC8`) i chunkovi koje imenuje.

| Dio | Raspored |
|---|---|
| zaglavlje | 34 bajta; broj čvorova na 25 |
| stabla rastera | vrsta bajta i u32 duljina za svako, dok ne dođe do bajta vrste `0xFF`. Vrsta 0 je visinsko polje: uzorci po strani na +5 (265), raspon visina na +21 (1,280 m), kvadrat terena u prvom zapisu čvora na +77 (8,192 m u provjerenoj razini). Drži okvire čvorova i piramidu min/max 16 x 16 po čvoru, a ne visine |
| čvorovi streaminga | quadtree, prvo u dubinu: veličina chunka i GUID; izborni drugi chunk; bajt zastavica (bit 0: chunk počinje visinskom stranicom); ima djecu. Djeca po redu (0,0), (1,0), (1,1), (0,1) |
| visinska stranica | prvih 265 x 265 u16 chunka označenog čvora, red po red; visina = vrijednost x 1,280 / 65,535 m; stupci duž x, redovi duž z, od donjeg ugla čvora; rub od 4 uzorka, pa 256 ćelija po čvoru |

Svaki korak je provjeren zasebno:

- Raščlanjivanje quadtreeja čvorova potroši res do posljednjeg bajta, s deklariranih 529 čvorova.
- Susjedni čvorovi dijele svojih devet rubnih stupaca točno, pa je korak 256.
- Uzorci djeteta na svakoj drugoj poziciji točno su jednaki roditeljskima uz rub od 4, a s bilo kojim drugim rubom odstupaju za 90 do 700 jedinica.
- Najniža riječ u razini dekodira se u najnižu visinu okvira do centimetra.
- Od osam načina na koje kvadrat može ležati na svijetu, samo x duž x i z duž z stavljaju postavljene predmete na njega: pola uzorkovanih kopija unutar oko 2 m, naspram nekoliko puta toga za svaki drugi način.

Postavljeni predmeti zatim mjere rezultat. Najniža točka svake kopije, u odnosu na teren ispod nje (bilinearno, iz najfinijeg čvora):

| Postavljeno | Medijan udaljenosti | Medijan s predznakom |
|---|---|---|
| drveće i grmlje | znatno ispod metra | tik ispod površine |
| rekviziti | metar ili dva | na površini |
| stijene | oko metar | utonule za oko metar |
| zgrade | nekoliko metara (stoje na temeljima) | neznatno utonule |

Vegetacija se postavlja na tlo i nigdje drugdje, pa je to najoštrija provjera: njezina ishodišta su medijalno 0.07 m od površine. Zgrade se jako razilaze jer kategorija sadrži zidove, podove i dijelove višekatnih i podzemnih građevina. Pomak terena za 64 m u stranu spušta udio kopija unutar 0.5 m s 29% na 10%.

`level` crta visinsko polje kao `ground:terrain`, svaki njegov dio iz najfinijeg čvora s visinama i ne finije od `--ground-spacing` (zadano 4 m: 3.7 milijuna trokuta za provjerenu razinu, čiji su najfiniji čvorovi 0.5 m). Komadi različite razlučivosti spajaju se malim stepenicama; ništa ih ne šiva.

Chunk čvora također drži stranice maski slojeva iza svoje visinske stranice, a njegov drugi chunk završava mapom boja čvora (vidi [Slojevi terena](#terrain-layers)).

## Slojevi terena {#terrain-layers}

Igra sjenča teren blizu igrača tako što splatanjem (splatting) lijepi popločane površinske materijale po naslikanim maskama, preko njih stavlja mapu boja i na vrh crta dekale (ceste, zakrpe asfalta, oznake uzletišta). Vlastiti opis sustava od strane Frostbitea (Widmark, "Terrain in Battlefield 3", GDC 2012) navodi rasteri terena kao visinsko polje, maske splatinga sjenčara, mapu boja "used as an overlay on top of shader splatting" (korištenu kao preklop preko splatinga sjenčara), fizikalne materijale, masku dubine uništenja, albedo kartu za odbijeno svjetlo i dodatne kanale maske; pločice rastera nose rub za algoritme prikaza. Streaming stablo razina koje su provjerene ima sedam stabala rastera, tipiziranih 0, 1, 2, 4, 5, 7 i 8, čija zaglavlja počinju veličinom pločice: 265 za visinsko polje (vrsta 0) i vrstu 2, 72 ili 66 za maske (vrsta 1), 132 s rubom od 2 za mapu boja (vrsta 4), 260 s rubom od 2 za vrstu 5.

**Popis slojeva.** Res `....layergraphs` terena navodi jedan unos od 32 bajta po sloju, redom kojim ih zapisi maski broje (u jednoj razini 34 unosa, 34 odjeljka depoa i indeksi slojeva 0 do 33). Id svakog unosa završava njegovim ključem odjeljka u shader block depou grafa slojeva (`....layergraphs_shaderblockdepot`), čiji blok imenuje karte sloja: jednu kartu boja `_cv`, karte `_nhs` i `_ao` po površini, plus zajedničke karte detalja i šuma. Mnogi slojevi uopće ne imenuju karte: to su izvori koje graf slojeva čita. Boja sloja je srednja vrijednost njegove karte `_cv`; skala popločavanja se ne nalazi. Asset terena završava jednim unosom od pet bajtova po sloju (bajt, zatim u32 indeks sloja ili -1).

**Maske.** Raster stablo 1 je quadtree maski. Njegovo tijelo počinje s 59 bajtova, stranica na 0: 72 gdje su stranice BC4 (72 x 72, 2,592 bajta), 66 gdje su nekomprimirane osmobitne (4,356 bajtova). Zatim dolazi po jedna grupa po čvoru, u dubinu:

| Dio | Raspored |
|---|---|
| grupa | u16; u16 broj zapisa; u32 broj stranica; zapisi; nulti bajt. Grupa bez zapisa je ukupno 7 bajtova |
| zapis | 33 bajta: u16 sloj, u16 heš, okvir kvadranta (četiri float-a), dva bajta zastavica, 85-bitna piramida prisutnosti |

Zapisi grupe su četiri kvadranta njezina čvora, sloj po sloj, a kvadranti svakog sloja po redu (0, 0), (1, 0), (1, 1), (0, 1). Zapis s postavljenom drugom zastavicom pokriva svoj kvadrant cijelo i nema stranicu; zapis bez nje ima sljedeću stranicu; kvadrant bez zapisa sloja koji njegova grupa imenuje prazan je za taj sloj; prva zastavica je čista točno kada sloj nastavlja u vlastitoj grupi kvadranta, jednu razinu niže, koja ga tamo zamjenjuje. Broj stranica je broj zapisa sa stranicom.

**Stranice.** Stranice vlastite grupe streaming čvora slijede u njegovu chunku, iza visinske stranice: 16-bitni odjeljak od 4,358 bajtova i osmobitni raster 67 x 67 (od početka chunka kada nema visinske stranice). Njegov drugi chunk drži stranice četiri grupe svojih kvadranata jednu razinu niže, kvadranti po redu mape boja, zatim sama mapa boja. Stranica su 64 x 64 texela kvadranta, redovi duž z i stupci duž x, s rubom kopiranim od susjeda: 4 texela na BC4 stranici, 1 na nekomprimiranoj.

Rubovi dokazuju postavljanje bez prosuđivanja: dvije stranice jednog sloja jedna do druge moraju nositi međusobne rubne texele. `read_masks` to provjerava za svaki par koji postavi i odbija razinu gdje se slaže manje od 99%. Otprilike trećina provjerenih razina se čita, s rubovima koji se slažu; nekoliko nema naslikanih maski; ostale se odbijaju, gotovo sve provjerom (chunkovi njihovih čvorova drže više nego što ovaj raspored zna). Tlo odbijene razine uzima srednju boju svojih površinskih materijala, a izvoz kaže zašto. Rubovi okrenuti prema punom kvadrantu su 255, a oni prema praznom 0.

Odjeljak od 4,358 bajtova i raster 67 x 67 ispred stranica se ne čitaju: njihove vrijednosti leže u uskom visokom pojasu, bez malih vrijednosti i bez čuvara.

**Boja tla.** Graf slojeva miješa slojeve u prevedenom grafu sjenčara od maski, nagiba, visine i šuma, a taj se ne čita. `--ground-texture` boji tlo prema vlastitom pravilu, ovdje navedenom kao takvom:

- slojevi čija je karta boja imenovana za udaljenost su zamjene za daleki pogled i izostavljaju se;
- teksturirani slojevi koji pokrivaju devet desetina terena ili više čine osnovu. Njihove maske su gotovo svugdje pune, pa je to gdje koji leži izbor sjenčara, a ne njihov: oni imenovani za stijenu ili litica boje nagibe strmije od 40 stupnjeva, oni imenovani za šljunak boje ravno tlo (ili ostale osnovne slojeve kad nema takvih), miješani između 20 i 40 stupnjeva prema nagibu visinskog polja (uzimanog svakih 4 m i bilinearno raspršenog po pečenim texelima: ponavljano u blokovima od 4 m, stjenovitu boju je crtalo kao zakrpe s oštrim rubovima);
- svaki drugi teksturirani sloj polaže se preko osnove vlastitom maskom, redom slojeva;
- mapa boja polaže se preko rezultata kako to radi motor, dvostruka boja tla pomnožena kartom, tako da sivo srednje ga ostavlja kakvim jest; gdje mapa boja nema texela, tlo uzima medijansku svjetlinu karte, sivom.

Provjereno prema srednjoj boji tla iz snimaka igranja triju razina (kroma kao crvena i plava naspram zelene): pečeno igrano područje daje 1.00 / 0.69 naspram 1.19 / 0.78 snimaka u jednoj, čiji su travnati slojevi zeleni gdje snimke prikazuju suhu travu; 1.19 / 0.82 naspram 1.01 / 1.04 u drugoj, čija je sama mapa boja topla (1.13 / 0.88); i 1.05 / 0.91 naspram 0.93 / 0.92 u trećoj bez mape boja. Snimke su osvijetljene i gradirane, pa ovo mjeri ton, a ne svjetlinu.

**Mapa boja.** Drugi chunk čvora drži, nakon stranica maski grupa njegovih kvadranata, četiri BC7 stranice od 132 x 132 (po 17,424 bajta), po jednu za svaki kvadrant čvora, redom (nizak x, visok z), (visok x, visok z), (visok x, nizak z), (nizak x, nizak z). Stablo maski kaže koliko bajtova zauzimaju stranice maski, pa se mapa boja nalazi po broju, a ne po kraju chunka: u jednoj razini grubi čvorovi nose iza nje još četiri takve stranice, još jedan raster u jednoj ravnoj boji, a čitanje zadnje četiri stranice chunka izgubilo je mapu boja preko devet desetina terena. Bez tog brojanja mapa boja je također bila promašena u razinama s nekomprimiranim stranicama maski, čije stranice nisu cijeli broj BC4 stranica; mapa boja jedne razine je prešla s 0.4 na 0.94 svog terena. Redoslijed je namješten: naspram rubova visinskog polja svakog kvadranta, svaka stranica čvorova s obilježjima odgovara jednom kvadrantu, nepreokrenuta, s 0.3 do 0.54 gdje je sljedeći najbolji smještaj ispod 0.2. Tako složene stranice razine spajaju se bez šava u ceste, vodu i izgrađena područja probne razine, na 0.5 m po texelu u igranom području. Gdje slojevi rade posao, mapa boja je gotovo neutralna (medijan 110, 107, 104); inače može nositi punu boju. Razina čiji drugi chunkovi drže samo nekomprimirane stranice maski nema pročitanu mapu boja. Raniji krug ovog čitača nazivao je te stranice negeografskima: uspoređivao ih je s kartom pozadine, koja može biti potpuno drugi krajolik, i stavljao svaku stranicu na cijeli čvor umjesto na kvadrant.

**Albedo za odbijeno svjetlo** je tražen i nije nađen: chunkovi korijenskog i čvorova prve razine su cijele stranice maski, a korisni teret vrste 5 nije lociran.

**Rupe.** Asset terena razine (vrsta res `0x1CA38E06`) imenuje tri sjenčara: zadani sjenčar površine, sjenčar rupa i zadani izvorni sjenčar. Koji sloj čita sjenčar rupa nije nađeno, pa se visinsko polje ne reže. U jednoj razini navigacijska mreža može ići preko stijenskih mreža desetke metara ispod visinskog polja, gdje ih je igra morala izrezati. Traženo i nenađeno tamo: maska sloja, raster 67 x 67, rezervirana visina (nijedna visinska stranica razine ne sadrži 0 ili 65,535) i zastavica čvora (svaki čvor ispod korijena ima zastavicu 1). Ostali su rasteri 7 i 8. Oba su kodirana duljinom niza (run-length): bajt jednak onom prije njega slijedi brojač daljnjih kopija (`ff ff 84` je 134 bajta od 255). Stablo 7 (pločica 256, potpuni quadtree od pet razina, četiri bita po uzorku) dekodira se u parove bajtova s vrijednostima 0 do 3; stablo 8 (pločica 265) u bajtove uglavnom 255, s ostalim vrijednostima u pravilnim nizovima. Ni pločice jednog ni drugog još nisu postavljene, pa se ni za jedan ne zna da drži rupe.

**Dekali** se čitaju i peku; vidi [Dekali terena](#terrain-decals).

## Dekali terena {#terrain-decals}

Izvor: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Ceste, uzletišta, betonske platforme, naslikane linije i slova, tragovi guma: res `TerrainDecals` (vrsta `0x15E1F32E`) drži ih kao ravnu geometriju koju igra prebacuje preko terena.

| Dio | Raspored |
|---|---|
| zaglavlje | na +16 broj slotova n, zatim n slotova od 16 bajtova, zatim broj zapisa |
| zapisi | jedan po batchu crtanja, jedan za drugim, promjenjive duljine: 156 bajtova fiksnih polja (prvi vrh na +32, broj trokuta na +36, popločavanje teksture u metrima na +44), zatim bajtovi vrhova batcha (pomak, veličina), zatim rep koji imenuje njegove teksture po GUID-ovima particija njihovih sredstava |
| vrhovi | 32 bajta: x, z (f32), 8 spakiranih bajtova, u, v (f32), r, g, b, a (f16); svaki batch je obični popis trokuta |
| indeksi | u32, brojeni od 0 u svakom batchu; ne trebaju |

Provjere:

- rasponi vrhova zapisa slijede jedan za drugim bez praznine i točno pokrivaju sve vrhove, a prvi vrh svakog zapisa × 32 je njegov pomak;
- tako pročitani, trokuti su kompaktni dekali (slova, pruge linija, zakrpe); ako se pročita jedan vrh pomaknuto, to su tanke krhotine preko cijele karte;
- gotovo svi batchevi imenuju teksture u svom repu: mapu boja (`_cv`) s mapom neprozirnosti (`_op`, crveni kanal), ili za oznake masku kanala (`_rgb`).

Iza GUID-ova tekstura rep nosi parametre materijala batcha, kodirane kao što su u shader bloku (vidi dolje Nijanse). Boja naslikanog dijela, traga gume ili linije je float3 heširan kao `607e`: pješčano 0.64, 0.56, 0.48 za tragove guma u pijesku, gotovo crno za katran. Mape neprozirnosti su uglavnom format 62, jedan kanal po 8 bajtova po bloku, čitano kao BC4.

Batch preslikava svoju teksturu ili po položaju u svijetu (u = x, v = z, tekstura se ponavlja svake metre popločavanja: asfalt, beton, šljunak) ili od 0 do 1 preko dekala (linija, slovo, trag gume). Zapisi se crtaju po redoslijedu u datoteci.

**Pečenje.** `level --ground-texture M` slika, ispod opsega dekala i u pločicama od najviše 4,096 piksela, kartu boja pozadine (bilinearno), a zatim svaki batch preko nje prema njegovoj neprozirnosti × alfa vrha. Boja vrhova se ne koristi: neki vrhovi batcheva su čisto zeleni ili plavi, što je obojilo oznake razine tim bojama. Trokuti visinskog polja tu postaju dijelovi `ground:terrain x<x> z<z>` koji nose pločicu. Svaki batch crta se ovako:

| Batch imenuje | Crta se kao |
|---|---|
| mapu boja (`_cv`) | kartu, prema njezinoj karti neprozirnosti |
| kartu množenja (`_mult`) i kartu neprozirnosti | boju (bijelu tamo gdje materijal ne imenuje nijednu) puta kartu množenja, prema karti neprozirnosti: istrošena središnja linija uzletišta, rubne linije i pragovi |
| masku kanala (`_rgb`) | boju, inače bijelu za linije i slova, tamnu za obrise, blago zatamnjenje za trošenje, tragove guma, mrlje, lokve i vlagu, prema maski |
| samo kartu neprozirnosti, s bojom | boju prema karti neprozirnosti: tragovi guma |

Maska varijacije ceste nije boja nego mijenja površinu ispod nje, stotine metara široka, i ne crta se, bez obzira na svoju boju: naslikana bijelo, polagala je dva blijeda pravokutnika od 150 do 250 m na padinama razine. Karta `_mult` shvaća se kao vlastito trošenje boje, a ne kao zatamnjenje tla ispod: gotovo je bijela, a oblik linije je u karti neprozirnosti.

Gotovo svaki batch se crta, u nekoliko pločica na 0.5 m po pikselu; izvoz naraste za nekoliko MB i traje nekoliko sekundi duže. Gledano odozgo, platforme, rulanje i cestovna mreža leže pod ogradama i zgradama kompleksa i vode do njihovih vrata.

Nacrtani kao vlastita geometrija, dekali bi trebali alfa stapanje, koje pisac ne nosi, a pomak iznad terena bi se s njim borio na z-osi (z-fighting); pečenje ih drži u boji samog tla.

## Teksture i materijali {#textures-and-materials}

Izvor: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Res Texture (vrsta `0x6BDE20BA`) je zaglavlje od 180 bajtova: vrsta i format piksela na +8, širina i visina na +22, broj mipova na +30, GUID chunka na +40, petnaest veličina mipova na +56. Chunk je lanac mipova, od najvećeg. Neki chunkovi nemaju svoje najveće mipove, koji se isporučuju u paketu visoke razlučivosti, a duljina chunka kaže od kojeg mipa počinje. Chunk tog paketa imenovan je na +164; čita se iz [dodataka](#which-table-is-the-level) razine kada je potreban mip koji glavni chunk nema, a njegova duljina plus duljina glavnog chunka čine cijeli lanac.

| Format | Dekodira se kao | Dokaz |
|---|---|---|
| 67, 66 | BC7 (sRGB, linearno) | plastična tenkova tablica boja dekodira se kao ona; kao BC3 isti bajtovi su šum |
| 61, 60 | BC3 | list boja sanduka dekodira se čisto kao BC3, ne kao BC1 ili BC7 |
| 57, 56, 55 | BC1 | pola bajta po pikselu |

Asset mreže ne imenuje teksturu. Veza je u **shader block depotima** razine (vrsta res `0x73312045`, po jedan za svaki podsvijet), ključem od osam bajtova na +0x130 zapisa odjeljka mreže:

| Dio | Raspored |
|---|---|
| tablica, na 16 | (ključ odjeljka u64, pomak deskriptora u64), dok pomak ne padne izvan rese |
| deskriptor | (pomak bloka u64, heš u64, veličina bloka u64) |
| blok | parametri shadera odjeljka; svaka tekstura je zapis od 49 bajtova: bajt, 16 bajtova, GUID particije sredstva teksture, njegov GUID instance |

Ključ odjeljka sanduka pojavljuje se jednom u svakom od deset depota podsvjetova koji ga postavljaju, a njegov blok imenuje `t_mil_crate_03_cs` i `_nmt` među zajedničkim kartama detalja. Blok imenuje svaku teksturu koju sjenčar uzorkuje, a koja je karta boja nije navedeno, pa se bira: 2D tekstura u sRGB čije ime sadrži većinu riječi iz imena materijala (`M_ConcreteWall_01`: concrete, wall), zatim iz imena mreže, zatim ona koja nije detalj, dekal (`t_de_...`) ili karta oštećenja, pa ona koju najmanje blokova koristi.

Blok prometnog znaka imenuje svoju ploču `t_com_highwaysignage_01_cs` i list dekala `t_de_com_highwaysignage_01_ca` sa štitom položenim na bok; oba se podudaraju s riječima, a bez pravila o dekalu list je pobijedio po korištenju i znak je prikazivao štit okrenut za četvrtinu, kroz svaki skup UV koordinata koji odjeljak ima.

Polja udaljenosti predznaka (`..._sdf`), palete i maske kanala (`_rgb`) se nikad ne biraju, bez obzira na to koje riječi dijele (karte `_rgba` jesu: većina su boja s alfom, a njihovo izostavljanje zamijenilo je vlastite karte dalekovoda i stubišta tuđima): atlas vegetacije pozadine `..._atlas_a_sdf` nacrtan kao boja prikazivao je crne i bijele zvijezde za drveće, paleta zgrada pozadine konfete uzoraka za zidove, a krhotine stakla nacrtane kroz masku kanala ispale su cijan. Odjeljak čiji su jedini kandidati zajedničke karte detalja ostaje ravne boje.

**Palete.** Zgrade pozadine uzimaju svoje boje iz palete, 256 x 256 texela od uzoraka 16 x 16: svaki vrh nosi četiri bajta (usage `0x1E`), čija prva dva kažu gdje je u paleti njegova boja, x i y od 255. `level` crta takav odjeljak s paletom kao teksturom, svaki vrh u središtu svog uzorka. Tako nacrtani blokovi pozadine razine ispadaju kao pastelni zidovi, terakota i tamni prozori tamo gdje su bili obični bijeli.

**Preklopi.** Veliki predmeti popločavaju list obrade (trim sheet) kroz svoje prve UV koordinate i preko njega polažu preklop kroz druge, koje leže unutar 0 do 1: razvoj cijelog predmeta. Preklop (`..._overlay_cs`, s maskom `..._overlay_a`) nosi ono kako predmet izgleda izdaleka, crvene pruge i hrđu naftnog spremnika; nacrtani samo s listom obrade, spremnici jedne razine ispali su kao sivi paneli. Odjeljak čiji blok imenuje preklop s maskom, a čije su druge koordinate takav razvoj, crta se s preklopom kroz njih (36 odjeljaka u toj razini).

**Nijanse.** Mnoge karte boja su sive (srednje vrijednosti njihovih kanala unutar 6% jedna od druge): sjenčar ih boji bojama iz parametara bloka. Nakon svojih unosa tekstura (po 49 bajtova) blok navodi svoje parametre, svaki s oznakom vrste (`f11af825` float3, `a5e1f2de` float4, `c1b1a014` float, `4a4fc3a1` cijeli broj), zastavicama `01 80` za jednu vrijednost, dvobajtnim hešom imena parametra, u32 brojem, vrijednošću i osmobajtnim id-om. Imena se ne spremaju. Sedam heševa imena float3 djeluje kao nijanse: u jednoj razini tri od njih drže boju u otprilike 1 bloku od 6 čija je karta siva i gotovo nikad tamo gdje karta ima vlastitu boju, a ostali drže boje u kojima se siva karta boji kada to ime materijala kaže (mosni `..._blue` ukras: 0.047, 0.098, 0.171 naspram neutralnih 0.5). Obitelj može držati više vrijednosti, po jednu za svaki kanal maske, većina neutralne, a vrijednost s kanalom gotovo ničim bira kanal maske umjesto da boji (čista zelena na fasadama od opeke). `level` množi sivu kartu boja, u linearnom svjetlu, prvom vrijednošću svake obitelji koja nije ni neutralna ni takav izbornik, preko njezine neutralne, i zadržava rezultat kao vlastitu teksturu; karta s bojom ostaje kakva jest. Pravilo je izvoznikovo: koji kanal maske dobiva koju nijansu nije pročitano. U jednoj razini smanjilo je udio strukturnih trokuta nacrtanih blizu bijelog s 19.4% na 3.9%.

**Varijacije predmeta.** Jedna mreža postavlja se u nekoliko izgleda: skladišni zid s crvenom ili plavom prugom i drugačijim brojem naslikanim na njemu, kontejner u zelenoj ili sivoj boji. Svaka postavljena kopija imenuje svoj izgled:

| Gdje | Polje |
|---|---|
| član grupe statičkih modela | +32: niz od jednog pokazivača po kopiji, na varijaciju predmeta ili null |
| referenca predmeta | +120: pokazivač na varijaciju predmeta ili null |
| varijacija predmeta (particija `ov_...`, vrsta `235f2a9c...`) | njezina prva instanca +32: u32 heš imena varijacije |

Izgled odjeljka u varijaciji je shader blok ključan vlastitim ključem odjeljka uz heš varijacije dodan njegovim prvim četirima bajtovima, kao little-endian u32 (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); odjeljak bez bloka pod tim ključem izgleda isto u svakoj varijaciji.

Baze podataka varijacija mreža razine (`meshvariationdb_win32`) navode, po mreži i heš-vrijednosti varijacije, materijale koje svaka varijacija dira, ali ne i ključeve: pravilo je nađeno iz samih ključeva i vrijedi za svaki provjereni odjeljak s varijantama (četiri varijacije jednog zida, po tri njegova odjeljka svaka). Blok varijacije donosi vlastite teksture kao i nijanse: naslikani broj na zidu je list slova koji blok varijacije imenuje. Velik dio grupiranih kopija postavljen je u varijaciju.

Blok se peče jednom za svaki skup sadržaja, a unos depota za ključ nosi heš tih sadržaja (drugi u64 unosa). Gdje odjeljak nema blok pod ključem svoje varijacije, varijacija ga ipak doseže preko *blizanca* (*twin*): drugog odjeljka čiji zadani blok ima iste sadržaje i ima ga. Bez blizanaca, zid čije duljine dijele jedan zadani blok može ispasti u dvije boje. Odjeljak bez vlastite varijante uzima varijantu koju većina njegovih blizanaca ima.

**Uništive mreže.** Mreža koju utakmica može srušiti ima pored sebe sredstvo uništenja istog imena (`.../br_x.destruction` za `.../br_x_mesh`): razbijive zgrade i zidove (`br_`) i mnoge rekvizite. `level` drži njihove površine u vlastitim dijelovima, imenovanim s ` (destructible)`, čiji glTF čvorovi nose `{"destructible": true}`. Njihova uništena stanja su mreže `dc_..._part<N>_mesh` pored njih, svaka centrirana na vlastito ishodište; gdje dio stoji je u sredstvu uništenja, koje se ne čita, pa se uništena stanja ne izvoze.

**Izostavljeno.** Odjeljci privremenih blokovskih materijala (`M_Whitebox`: nekoliko velikih neteksturiranih trokuta koje neke zgrade drže uz svoje površine, koji su iz razine ispadali kao bijela krilca), mreže napravljene za filmove (helikopter postavljen gdje njegova scena počinje) i pomoćni elementi za svjetlo (ravnine koje blokiraju svjetlo, nikad se ne crtaju). Generirane zgrade pozadine razine (`..._generated_blueprints_..._mesh`) se crtaju, ali se imena materijala njihovih zidova odnose samo na karte šuma, a vrhovi im ne nose boju, pa ostaju obični. Gotovo svaki nacrtani odjeljak dobiva kartu boja.

**Listovi slova.** Naslikani broj na zidu ili otisak reklamnog panoa na kranu je vlastiti odjeljak čija je karta boja list (`_ca`): alfa slova preko čvrste boje, ili otisak. Njegove prve UV koordinate popločavaju žbuku zida preko ploče (u -0.2 do 1.7 na jednom zidu), što list crta gotovo dvaput; četvrti skup (`0x24`, inače treći, `0x23`) polaže ga točno jednom (u -1 do 0, v 1 do 2, nekoliko tisućinki preko u grubljim razinama detalja). Gdje prvi skup ostavlja jednu kopiju slike, a četvrti ili treći leži unutar jedne, list se crta kroz njega, pomaknut u 0 do 1. List s alfom crta se 1 cm ispred površine na koju je naslikan, koja se ispod njega crta drugom kartom boja bloka kroz prvi skup: bez toga su prazni texeli lista pokazivali unutrašnjost zida. Drugi skup je razvoj predmeta za njegov preklop i ovdje se ne koristi.

**Mape izrezivanja.** Četvrti kanal karte boja znači različite stvari prema imenu karte. U `_cs`, daleko najčešćoj (893 od izabranih karata jedne razine), to je glatkoća: 1% alfe medijan karte leži unutar 0.1 od 0 ili 1. U `_cu` (lišće, trava) i `_ca` (boja i alfa) to je neprozirnost: 90% i 87%. Karta boja imenovana `..._cu` ili `..._ca` čija je alfa barem 75% blizu 0 ili 1, barem 1% ispod 0.5 i barem 5% iznad, zapisuje se s alfom, kao PNG, a njezin materijal kao glTF `alphaMode` MASK, `alphaCutoff` 0.5, dvostrano; kartice lišća tada pokazuju lišće, a ne svoje crne kutove. Karta lišća jednog stabla uopće nema alfe (najviše 4 od 255): njezine grane su izrezane geometrijom, a uz samo prva dva uvjeta cijela krošnja bi bila odsječena.

UV koordinate teksture su usage `0x21`, dvije polovice (format 6) ili dva float-a (format 2). Odjeljci nose do tri dodatna skupa (`0x22` do `0x24`) za slojeve dekala i detalja. Koordinate se popločavaju: rebrasta strana spremnika ide od -1.6 do 1.8, pločice pozadine terena leže potpuno izvan 0..1, a u jednoj razini 23% teksturiranih trokuta seže izvan 0..1. Zapisuju se takve kakve jesu, s ponavljajućim uzorkovanjem; preglednik 3DHeat omata svaku ponavljajuću teksturu unutar svog atlasa. Prikazivač koji ih umjesto toga steže razmazuje rebra na dvostruku širinu, pretvara betonski pod u pruge duž jedne osi i daje čeličnim gredama tornja rubnu boju njihove teksture; za njega `--clamped-uvs` reže svaki trokut duž linija na kojima se njegova tekstura ponavlja i pomiče svaki komad u 0..1 (vidi [Format izlaza](output-format.md)). Nakon toga 0.03% teksturiranih trokuta, preko kojih se tekstura ponavlja više od 16 puta, seže izvan, a trokut koji bi rezanje napravilo u više od 4 komada crta se umjesto toga u prosječnoj boji svoje teksture: kora se ponavlja niz svaku granu, a s rezanjem su stabla jedne razine prešla s 6.4 na 24 milijuna trokuta.

Visinsko polje nema vlastitu kartu boja koja bi se mogla pročitati. Gdje je pokrije jedna od karata pozadine terena, boji se iz nje: UV koordinate pozadine su linearna funkcija svjetskih x i z (99% njezinih vrhova unutar 0.001 od nje; karta pokriva kvadrat od 65,536 m, okrenut za četvrtinu), a ista funkcija daje one visinskog polja. Razina isporučuje mipove te karte od 2,048 px dolje, pa visinsko polje dobiva 32 m po pikselu. Njegova tamna stijena leži na strmom tlu: korelacija tamnoće i nagiba je 0.48, a najviše 0.34 za sedam drugih orijentacija.

Pozadina druge razine je osam bliskih i osam dalekih pločica oko igranog područja, svaka ponavlja vlastitu teksturu preko pločice, a nijedna ne dopire do visinskog polja. Svaka tekstura pozadine se uklapa sama za sebe, a kada nijedna ne pokriva visinsko polje, uzima prosječnu boju koju pozadina pokazuje unutar kilometra od kvadrata terena, a preko nje `--ground-texture` peče dekale. Materijal pozadine je onaj čije ime sadrži `TerrainBackdrop`, ili `BD_` i `Terrain` (`M_BD_<site>_Terrain..._Near`); ili mreža pozadine (`bd_..._terrain<site>_04_far_mesh`) nosi običan materijal terena (`M_<region>_Terrain<site>_04_Far`), što su prva dva pravila u jednoj razini propustila, pa je tlo obojila prema površinama.

Gdje ipak nijedna karta pozadine ne pokriva visinsko polje, ono uzima srednju boju vlastitih površina terena prije prosjeka pozadine: karte boja `_cv` koje imenuju shader blokovi njegova grafa slojeva (27 u jednoj razini: pijesci, šljunci, zemlje, trava, ispucani beton), svaka usrednjena, zatim medijan svakog kanala, izostavljajući zadanu površinu motora. Pozadina može biti potpuno drugi krajolik: u jednoj razini njezin prosjek (95, 99, 80 u sRGB) obojio je tlo igranog područja sivo, što igra ne prikazuje. Uz `--ground-texture`, ta se boja množi s dvostrukom mapom boja, koju sivo srednje ostavlja kakva jest, i peče se s dekalima preko opsega i dekala i mape boja.

Naspram igre, srednja boja tla pečenog igranog područja svake razine i snimaka igranja (retci 55 do 72% slike pored HUD-a, po 24 snimke; sRGB; snimke su osvijetljene i gradirane, pa su omjeri r/g i b/g pošteno usporedivi):

| Razina | Snimke | Prosjek pozadine | Sada |
|---|---|---|---|
| prva | 167, 140, 109 (1.19, 0.78) | 95, 99, 80 (0.96, 0.81) | 117, 108, 86 (1.08, 0.80) |
| druga | 72, 71, 74 (1.01, 1.04) | 117, 110, 104 (1.06, 0.95) | 146, 135, 117 (1.08, 0.87) |
| treća | 83, 89, 82 (0.93, 0.92) | 160, 148, 136 (1.08, 0.92) | 148, 137, 117 (1.08, 0.85) |

Prva je ispravljena; druge dvije su prije bile malo bliže po nijansi. Jedna boja za cijelu razinu ne može biti ispravna svugdje; maske bi mogle.

## Navigacijska mreža {#navigation-mesh}

Izvor: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Razina isporučuje po jednu particiju za svakog agenta, `<level>/dbt/<level>_navmesh_layer_<n>`: u jednoj razini sloj 0 je vojnik (visok 1.8 m, korak 0.18 m, polumjer 0.4 m), a dva druga su vozila (visoka 3.5 i 10 m). Svaka particija drži dva niza:

| Niz | Element |
|---|---|
| pločice | 28 bajtova: u32 0, u32 heš, u32 0, u32 indeks chunka, u16 x pločice, u16 z pločice, u32 pomak, u32 veličina |
| chunkovi | 20 bajtova: GUID chunka, u32 veličina |

Pločica je `size` bajtova na `offset` u chunku `chunk index`, little-endian, i posložena kao Detourova (Recast Navigation) iza duljeg zaglavlja:

| Pomak | Sadržaj |
|---|---|
| 0 | `VAND`, verzija 7 |
| 24 | brojevi: poligoni, vrhovi, poveznice, detaljne mreže, detaljni vrhovi, detaljni trokuti, čvorovi ograničavajućih volumena, poveznice izvan mreže, prvi poligon izvan mreže |
| 188 | visina agenta, korak, polumjer |
| 200 | okvir pločice, šest float-ova |
| 232 | vrhovi: x, y, z float-ovi, koordinate svijeta |
| sljedeća granica od 8 bajtova | poligoni, 32 bajta: u32, šest u16 indeksa vrhova, šest u16 susjeda, u16 zastavice, broj vrhova na +30, na +31 područje (donjih šest bitova) i vrsta (gornja dva) |
| zatim, zbijeno | poveznice (16 bajtova), detaljne mreže (12: prvi detaljni vrh u32, prvi detaljni trokut u32, broj vrhova i trokuta u8), detaljni vrhovi (tri float-a), detaljni trokuti (tri indeksa i zastavice), čvorovi ograničavajućih volumena (16), poveznice izvan mreže (80) |

U svakoj pločici provjerenih razina ovo se zbraja u veličinu pločice do bajta, a detaljne mreže broje poligone prije prvog poligona izvan mreže.

Poligon je ravan između svojih kutova; njegova **detaljna mreža** drži stvarnu visinu površine preko neravnina, stijena i stepenica, i to se crta. Indeks detaljnog trokuta ispod broja kutova poligona je taj kut, inače detaljni vrh `first + index - corners`. Umjesto toga, raspoređivanje poligona u vjetar stavlja puno više trokuta pod teren i pravi dugačke krhotine; s detaljnim mrežama nijedan nije duži od dijagonale pločice od 16 m plus stepenice uz padinu.

Vrsta 0 je tlo, vrsta 2 male strme zakrpe (oko 45 stupnjeva, po jedan kvadratni metar), vrsta 1 poveznica između površina: njezini kutovi obuhvaćaju 125 m visine ili više i leže izvan pločice, neki na ishodištu. Poveznice se izostavljaju; ostale se crtaju svojim detaljnim mrežama, ili raspoređuju u vjetar u pločici bez ijedne.

Provjere: veličine chunkova se zbrajaju točno u veličine pločica; svaki vrh površine leži unutar okvira svoje pločice uz otprilike metar odstupanja; gotovo svi trokuti gledaju prema gore. Pločica koja ne uspije se odbija i broji, a u toj razini nijedna nije odbijena.

Što mreža vojnika pokriva, gledano odozgo u probnoj razini: tlo, podovi, stube i neki krovovi, a ne vrhovi teretnih kontejnera. To je AI-jeva karta gdje vojnik može stati, najbliže što datoteke dolaze tome gdje stoje igrači.

## Nije implementirano {#not-implemented}

- Graf slojeva terena, koji miješa njegove površinske slojeve (vidi [Slojevi terena](#terrain-layers)): boja tla slijedi pravilo samog ovog čitača iz maski slojeva i nagiba visinskog polja, a razine čije stranice maski ne pristaju jedna uz drugu dobivaju jednu boju.
- Parametri boje materijala dekala: oznake kroz maske kanala boje se neutralnom bojom.
- Blueprinti predmeta koji nisu mreže (logika igre, efekti, zvukovi).
- Uništena stanja uništivih mreža: mjesta njihovih dijelova su u sredstvu uništenja, koje se ne čita.
- Poveznice navigacijske mreže (skokovi, ljestve, preskakanja) i njezini slojevi za vozila.
- Razine mreža spremljene unutar rese (10 mreža u razini, rekviziti), kosti i dijelovi skinned i composite mreža, te normale (računa ih pisac).
- Karte normala, hrapavosti i ostale karte; alfa osim izrezivanja (prozirno staklo i dekali crtaju se neprozirno).
- Rupe u terenu: sjenčar rupa je imenovan, ali se ne zna što čita (vidi [Slojevi terena](#terrain-layers)), pa se visinsko polje ne reže tamo gdje pod njim ide hodljivo tlo.
- Koja nijansa ide uz koji kanal maske materijala: siva karta boja uzima prvu nijansu koja nije neutralna (vidi [Teksture i materijali](#textures-and-materials)).
- Efekti (putanje `fx/`) i mreže kablova, čiji su ograničavajući okviri dugi desetke kilometara; izostavljaju se i broje u sažetku.
- Oblik tablice zamućen XOR-om.
