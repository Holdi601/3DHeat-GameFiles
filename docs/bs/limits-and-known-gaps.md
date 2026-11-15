---
title: "Ograničenja i poznate praznine"
nav_order: 10
lang: "bs"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Ograničenja i poznate praznine {#limits-and-known-gaps}

Šta alat ne radi, šta radi samo djelimično i gdje je njegovo ponašanje
neujednačeno. Većina praznina su namjerna odbijanja. Dekodiranje bez datoteke s
kojom bi se provjerilo daje izlaz koji izgleda ispravno, a nije.

## Igre {#games}

| Igra | Izvoz staze | Zašto ne, ili dokle seže |
|---|---|---|
| Forza Horizon | da | boja tla je interpretacija (pogledajte ispod) |
| BeamNG.drive | da | nema raslinja po tlu, ponavljajuće teksture modela spljoštene |
| Assetto Corsa Rally | da | modeli u ravnim bojama; još nije pokrenuto na krugu snimljenom u igri |
| Assetto Corsa EVO | **ne** | sav sadržaj je u jednom paketu obfusciranom ključem, a ovaj alat ne otkriva ključeve |
| Battlefield 6 (izvoz nivoa, `level`) | da, cijeli nivo | teren, grupno i pojedinačno postavljene mreže i njihove mape boje, navigacijska mreža vojnika, raslinje s izrezima; boja tla područja igre je gruba (32 m po pikselu, ili jedna prosječna boja); bez prozirnosti ili normal mapa; razbijive mreže označene, njihova uništena stanja ne izvoze se |
| Unreal 5 World Partition igre (izvoz mape, `ue-map`) | da, cijela mapa | landscape tačan; zgrade kao pojednostavljene HLOD mreže mape, a ne modeli pune detaljnosti; vodena tijela; bez raslinja, decala ili boje tla |
| Arma Reforger (izvoz svijeta, `enfusion-world`) | da, cijeli svijet | teren u vlastitim bojama i more; zgrade, rekviziti i stijene kao kutije njihovih modela, a ne njihovi trouglovi; drveće na zahtjev (`--trees`), kao kutije; bez jezera, rijeka ili podređenih entiteta |
| iRacing | **ne** | staze se isporučuju u zaštićenom formatu koji nije meta za izvlačenje datoteka |
| bilo šta drugo | **ne** | nema čitača staze; rekonstruirajte iz igranja pomoću 3DHeat GameCapture, ili analizirajte krugove u kartici Analiza utrke u pregledniku bez staze |

## Engineovi i formati {#engines-and-formats}

| Format | Nije implementirano |
|---|---|
| Unreal `.pak` | verzije prije 8; indeksi samo s hashom putanje (imena se ne mogu povratiti); unosi u listi preljeva indeksa (preskaču se); dekodiranje sadržaja `.uasset`/`.umap` iz paka |
| Unreal IoStore | šifrirani kontejneri (odbijaju se, nema opcije ključa); listanje kontejnera bez indeksa direktorija (ne imenuje datoteke); verzionirani paketi; mreže samo za Nanite i neugrađene; skeletalne mreže; svojstva klasa bez sheme; svojstva instanciranih komponenti (raspored promijenjen u verziji igre); spline mreže i komponente decala |
| Unity | formati prije 22 (Unity 2019 i stariji); datoteke s ugrađenim stablima tipova; komprimirane mreže; sve klase osim `Mesh`, dakle bez transformacija, materijala ili scena; `meshes` na bundleu; `list`/`extract` (koristi `meshes`) |
| Frostbite | XOR-obfuscirane tablice; graf slojeva terena (maske pročitane u otprilike trećini provjerenih nivoa); nacrti objekata osim mreža (logika igre, efekti, zvukovi); nivoi mreža pohranjeni ugrađeno; normal i druge mape, alfa osim izreza; rupe u terenu; biblioteka tipova (šifrirana u početnom datotečnom sistemu, ne dira se); komanda za listanje ili izvlačenje pojedinačnih asseta |
| Source 2 | kompilirani asseti (`.vmdl_c`, `.vtex_c`); CS2 nav mreža (verzija 36) |
| ForzaTech | formati pozicija osim četiri skalirana shorta; formati indeksa osim u16; kodovi tekstura osim 0, 9, 13; slojevi materijala shadera terena; tangente |
| BeamNG | skinirane mreže i mreže decala; animacija; proceduralno raslinje po tlu; scenografija oko ruba svijeta |
| Unreal landscapeovi i World Partition mape | landscapeovi čije heightmape žive u pečenim ćelijama; slojevi uređivanja i rupe; Nanite mreže landscapea; modeli pune detaljnosti postavljeni u ćelije; raslinje; materijali landscapea |
| Enfusion | trouglovi modela (geometrija `.xob` je komprimirana u rasporedu koji se ne čita); `.edds` sa zaglavljima prije DX10; vrijednosti ugniježđenih objekata u datotekama svijeta (preskaču se, broje se); podređeni entiteti; generirana jezera i rijeke; `list`/`extract` na `.pak` |

## Ponašanje vrijedno znanja {#behaviour-worth-knowing}

- **Boja tla u Forzi nije ona iz igre.** Pečena tekstura crta se iz mapa pločica
  koje kažu *gdje* su asfalt, kratka trava, grubo tlo i šuma. Koristi fiksne
  boje i sjenčanje, jer slojevi materijala shadera terena nisu dekodirani.
- **`--no-textures` uklanja i bankinu u Forzi.** Podjela asfalt/bankina koristi
  masku asfalta koja dolazi uz pečene mape. Bez tekstura, trake ceste ostaju cijele
  kao cesta.
- **Budžet koji date mogu prekoračiti samo ivičnjaci.** Ivičnjaci (i BeamNG-ovi
  modeli površine za vožnju) nikad se ne pojednostavljuju niti izostavljaju, ni u
  jednoj igri, pa `--detail-budget` manji od onoga što oni koštaju prekoračuju oni
  sami; sve ostalo se prvo izostavlja. Pogledajte [Nivoi detalja i budžet](detail-budget.md).
- **Opcije koje se ne odnose ignoriraju se tiho**: `--season` za BeamNG i
  AC Rally, `--track` za BeamNG i AC Rally, `--level`/`--install` za Forzu.
- **Boja tla nivoa Battlefield 6 je gruba daleko od njegovih decala.**
  Visinsko polje se boji iz mape boje pozadine terena, 32 m po pikselu na
  najvećem mipu koji nivo isporučuje - ili, gdje je nijedna mapa pozadine ne
  pokriva, u srednjoj boji materijala površina terena; `--ground-texture`
  to množi colormapom terena (na 0,5 m po pikselu gdje je nivo ima) i peče
  ceste, platoe, linije piste, tragove guma i oznake preko toga, u boji boje
  njihovih materijala gdje je ona zadana, a neutralnoj gdje nije; maske varijacije
  ceste se izostavljaju. Igra miješa svoje slojeve površina u
  grafu shadera koji se ne čita; izvoz polaže boje slojeva po njihovim
  maskama i nagibu visinskog polja, po vlastitom pravilu, a nivo čije se
  stranice maski ne uklapaju dobija jednu boju. Svaki sloj je
  prosjek svoje mape boje, a ne njegova tekstura. Pogledajte
  [Frostbite](reader-frostbite.md#terrain-layers). Dijelovi
  visinskog polja različitih rezolucija sastaju se s malim stepenicama.
- **Mapa boje u Battlefield 6 se bira, ne čita.** Shader blok imenuje
  svaku teksturu koju uzorkuje a da ne kaže koja je boja; izbor ide
  po imenu (pogledajte [Frostbite](reader-frostbite.md#textures-and-materials)) i može
  izabrati list obruba ili detalja za površinu. Listovi decala (`t_de_...`) gube od
  vlastite mape površine; decal znaka nacrtan kao njegov panel prikazao je svoj
  štit okrenut za četvrtinu kruga. Polja udaljenosti, palete i maske kanala nikad se
  ne uzimaju. Zgrade pozadine crtaju se u bojama svoje palete; sive mape
  preuzimaju nijansu materijala po pravilu samog izvoznika, jer su
  imena parametara hashirana, a materijal koji sivu mapu slika
  kroz masku s više nijansi dobija jednu od njih.
- **Rupe terena u Battlefield 6 nisu izrezane.** Gdje hodljivo tlo nivoa
  prolazi ispod visinskog polja, igra je morala izrezati teren, a izvoz to
  ne radi. Isključeno kao mjesto rupa: maske slojeva terena (nijedna nije
  koncentrirana tamo), njegov raster čvorova 67 x 67, rezervirana vrijednost visine (nijedna
  stranica visina ne sadrži 0 ili 65.535), zastavice čvorova (sve iste), te mreže
  ili asseti koji režu tlo: ono što je tamo postavljeno ispod tla su
  mreže stijena i litica, a nijedan asset nivoa nije imenovan za rupe,
  tunele ili pećine. Dva rasterska stabla dekodiraju se run-length kodiranjem ali
  se ne postavljaju, i to je ono što je ostalo (pogledajte [Frostbite](reader-frostbite.md#terrain-layers)).
- **Varijacija objekta u Battlefield 6 dopire do sekcije kroz njene blizance.**
  Varijacija postavljene kopije bira shader blokove svojih sekcija po ključu; gdje
  mreža nema blok za varijaciju, uzima se varijanta sekcije druge mreže
  s identičnim zadanim blokom (pogledajte
  [Frostbite](reader-frostbite.md#textures-and-materials)). To je
  pravilo izvoznika; sekcija bez blizanca koja varira zadržava svoj zadani izgled.
- **Slojeviti materijali u Battlefield 6 crtaju se kao njihova baza i jedan list.**
  Zidni panel sa slovima crta se kao njegova žbuka sa listom slova preko nje;
  ostali slojevi materijala (prljavština kroz masku, detalj
  i mape mahovine) ne miješaju se.
- **Navigacijska mreža je AI-jeva, a ne igračeva.** Pokriva ono do čega vojnik
  može hodati: tlo, podove i stepenice, i
  neke krovove, ali ne svaku visoku tačku. Veze između površina (skokovi, ljestve, preskoci) su izostavljene.
- **Nivo Battlefield 6 uključuje sloj svakog načina igre.** Objekti koje postavlja
  samo jedan način mogu se preklapati s drugim. `--skip` izostavlja slojeve po imenu.
- **`courses` je samo za Forzu**, i uzima samo foldere biblioteke imenovane
  `... (course_...)`.
- **Pretpostavlja se okvir kruga BeamNG-a** koji je okvir preglednika `(x, z, -y)` koji
  piše 3DHeat snimač. Krugovi drugog snimača u BeamNG-ovom sirovom okviru
  ne bi bili postavljeni.
- **`list` i `extract` uzimaju arhive, ne svaki format.** Otvaraju
  `.pak`, IoStore `.utoc`, `.vpk`, `.minizip` i zip. Unity kontejner
  se čita pomoću `meshes`, Frostbite nivo pomoću `level`, a `.cdae` ili
  `.ter` je datoteka, a ne arhiva (`identify` ga imenuje). `.minizip`
  bez svog `ChunkContentsMiniZip<n>.txt` pored sebe lista se po broju unosa.
- **Postavljeni modeli u BeamNG-u koriste ponavljajuće teksture kao prosječne boje**, jer
  sampler u `.glb` clampa, a preglednik pakuje teksture u atlas.
- **U praksi samo Windows.** Steam putanje pod `C:\Program Files`,
  `%LOCALAPPDATA%`, `C:\XboxGames` i `*_win64.dll` za Oodle. Druge platforme
  nisu testirane.

## Neprovjereno {#unverified}

- Starije verzije Pythona (alat je pokretan s 3.13).
- Assetto Corsa Rally s krugom snimljenim u igri. Testiran je samo
  sa sintetičkim krugovima u nasumičnim okvirima.
- glTF preglednici osim 3DHeat preglednika.
- Da li je okvir svake igre lijevi ili desni. Izvoz zadržava telemetrijski
  okvir svake igre, pa se krugovi i staze poravnavaju bez obzira na to.
- Značenje lokalnog z = 0 kod `WaterBlock` kao njegove površine (BeamNG).
- Frostbite postavljanje na igrama osim Battlefield 6, i na Battlefield 6
  nakon ažuriranja koje mijenja raspored člana grupe. Čitač tada ne pronalazi
  grupe i to kaže.
- Da li se izvoz Battlefield 6 poravnava s pozicijama koje igra prijavljuje.
  Koordinate su vlastite igri, kao za druge igre, ali nijedan snimak još nije
  položen preko njega.
