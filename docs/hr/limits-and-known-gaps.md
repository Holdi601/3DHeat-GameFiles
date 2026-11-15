---
title: Ograničenja i poznati nedostaci
nav_order: 10
lang: "hr"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Ograničenja i poznati nedostaci {#limits-and-known-gaps}

Što alat ne radi, što radi samo djelomično i gdje je njegovo ponašanje neujednačeno.
Većina nedostataka su namjerna odbijanja. Dekodiranje bez datoteke za provjeru daje
izlaz koji izgleda ispravno, a nije.

## Igre {#games}

| Igra | Izvoz staze | Zašto ne, ili koliko daleko |
|---|---|---|
| Forza Horizon | da | boja tla je tumačenje (vidi dolje) |
| BeamNG.drive | da | bez pokrova tla, ponavljajuće teksture modela se izravnavaju |
| Assetto Corsa Rally | da | modeli u jednolikim bojama; još nije pokrenuto na krugu snimljenom u igri |
| Assetto Corsa EVO | **ne** | sav sadržaj je u jednom paketu zamaskiranom ključem, a ovaj alat ne dobiva ključeve |
| Battlefield 6 (izvoz razine, `level`) | da, cijela razina | teren, grupirane i pojedinačno postavljene mreže i njihove mape boja, navigacijska mreža vojnika, izrezana vegetacija; boja tla područja igre je gruba (32 m po pikselu, ili jedna prosječna boja); nema prozirnosti ni normalnih mapa; uništive mreže su označene, njihova uništena stanja se ne izvoze |
| Unreal 5 igre World Partition (izvoz karte, `ue-map`) | da, cijela karta | krajolik točno; zgrade kao pojednostavljene HLOD mreže karte, a ne punodetaljni modeli; vodena tijela; bez vegetacije, dekala ili boje tla |
| Arma Reforger (izvoz svijeta, `enfusion-world`) | da, cijeli svijet | teren u vlastitim bojama i more; zgrade, rekviziti i stijene kao kutije njihovih modela, a ne kao njihovi trokuti; drveće na zahtjev (`--trees`), kao kutije; bez jezera, rijeka ili podređenih entiteta |
| iRacing | **ne** | staze su isporučene u zaštićenom formatu koji nije cilj izdvajanja datoteka |
| sve ostalo | **ne** | nema čitača staza; rekonstruirajte iz igranja s 3DHeat GameCaptureom, ili analizirajte krugove u kartici Analiza utrke preglednika bez staze |

## Motori i formati {#engines-and-formats}

| Format | Nije implementirano |
|---|---|
| Unreal `.pak` | verzije prije 8; indeksi samo s hashevima putanja (imena se ne mogu povratiti); unosi na popisu prekoračenja indeksa (preskaču se); dekodiranje sadržaja `.uasset`/`.umap` iz paka |
| Unreal IoStore | šifrirani spremnici (odbijeni, nema opcije za ključ); popis spremnika bez indeksa direktorija (ne imenuje datoteke); verzionirani paketi; mreže samo za Nanite i mreže koje nisu unutra; skeletne mreže; svojstva klasa bez sheme; svojstva instanciranih komponenti (raspored je promijenila verzija igre); komponente šipki i decala |
| Unity | formati prije 22 (Unity 2019 i stariji); datoteke s ugrađenim stablima tipova; komprimirane mreže; svaka klasa osim `Mesh`, pa nema transformacija, materijala ni scena; `meshes` na paketu; `list`/`extract` (koristite `meshes`) |
| Frostbite | tablice zaštićene XOR-om; graf slojeva terena (maske pročitane u otprilike trećini provjerenih razina); objekti blueprinta osim mreža (logika igre, efekti, zvukovi); mreže razina spremljene unutra; normalne i ostale mape, alfa osim izrezā; rupe u terenu; tip biblioteke (šifrirana u početnom datotečnom sustavu, ne dira se); naredba za popis ili izdvajanje pojedinačnih assetā |
| Source 2 | kompajlirani assete (`.vmdl_c`, `.vtex_c`); navigacijska mreža CS2 (verzija 36) |
| ForzaTech | formati pozicija osim četiri skalirana kratka broja; formati indeksa osim u16; kodovi tekstura osim 0, 9, 13; slojevi materijala sjenčala terena; tangente |
| BeamNG | skinned i decal mreže; animacija; proceduralni pokrov tla; scenografija uz rub svijeta |
| Unreal krajolici i World Partition karte | krajolici čije su visinske mape u pečenim ćelijama; slojevi uređivanja i rupe; mreže krajolika za Nanite; punodetaljni modeli postavljeni u ćelijama; vegetacija; materijali krajolika |
| Enfusion | modeli trokuta (geometrija `.xob` je komprimirana u rasporedu koji se ne čita); `.edds` s formatom zaglavlja prije DX10; vrijednosti ugniježđenih objekata u datotekama svijeta (preskače se, broji se); podređeni entiteti; generirana jezera i rijeke; `list`/`extract` na `.pak`-u |

## Ponašanje koje vrijedi znati {#behaviour-worth-knowing}

- **Boja tla Forze nije igrina.** Pečena tekstura crta se iz karti pločica koje kažu
  *gdje* su asfalt, kratka trava, grubo tlo i šumovitost. Koristi fiksne boje i sjenčanje,
  jer se slojevi materijala sjenčala terena ne dekodiraju.
- **`--no-textures` uklanja i Forzin rub.** Podjela na asfalt i rub koristi masku asfalta
  koja dolazi uz pečene karte. Bez tekstura trake ceste ostaju cijele kao cesta.
- **Proračun koji zadate može premašiti samo rubnik.** Rubnici (i modeli vožnje po
  površini u BeamNG-u) nikad se ne pojednostavljuju niti izostavljaju, ni u jednoj igri,
  pa `--detail-budget` manji od njihove cijene premašuju samo oni; sve drugo se prvo
  izostavlja. Vidi [Razine detalja i proračun](detail-budget.md).
- **Opcije koje se ne primjenjuju se tiho ignoriraju**: `--season` za BeamNG i AC Rally,
  `--track` za BeamNG i AC Rally, `--level`/`--install` za Forzu.
- **Boja tla razine Battlefield 6 je gruba daleko od dekala.** Visinsko polje dobiva boju
  iz mape boja pozadine terena, 32 m po pikselu na najvećem mipu koji razina ima, ili, gdje
  nijedna mapa pozadine ne pokriva, u srednjoj boji materijala površina terena;
  `--ground-texture` to množi s mapom boja terena (na 0,5 m po pikselu gdje razina
  ima jednu) i zapeče ceste, platoe, oznake piste, tragove guma i oznake preko toga, u boji
  premaza njihovih materijala gdje je postavljena, a neutralnoj gdje nije; maske varijacija
  cesta se izostavljaju. Igra miješa svoje slojeve površina u grafu sjenčala koji se ne
  čita; izvoz slaže boje slojeva prema njihovim maskama i nagibu visinskog polja, po
  pravilu koje je njegovo vlastito, a razina čije se maske stranica ne slažu dobiva jednu
  boju. Svaki sloj je prosjek svoje mape boja, a ne njegova tekstura. Vidi
  [Frostbite](reader-frostbite.md#terrain-layers). Dijelovi visinskog polja na različitim
  razlučivostima susreću se s malim stepenicama.
- **Mapa boja Battlefield 6 se bira, ne čita.** Blok sjenčala imenuje svaku teksturu koju
  uzorkuje, ne govoreći koja je boja; izbor ide po imenu (vidi
  [Frostbite](reader-frostbite.md#textures-and-materials)) i može odabrati mapu ukrasa ili
  detalja za površinu. Listovi dekala (`t_de_...`) gube od vlastite mape površine; dekal
  znaka nacrtan kao njegova ploča pokazao je svoj štit okrenut za četvrtinu. Udaljenosna
  polja, palete i kanalne maske se nikad ne uzimaju. Zgrade pozadine crtaju se u bojama
  svoje palete; sive mape uzimaju nijansu materijala pravilom izvoznika, jer se imena
  parametara hashiraju, a materijal koji sive mape boji kroz masku s više nijansi dobiva
  jednu od njih.
- **Rupe u terenu Battlefield 6 se ne režu.** Gdje hodajuće tlo razine teče ispod
  visinskog polja, igra je mora izrezati, a izvoz to ne radi. Isključeno kao mjesto rupa:
  maske slojeva terena (nijedna nije koncentrirana tamo), njegova rasterska mreža 67 x 67
  čvora, rezervirana vrijednost visine (nijedna stranica visina ne drži 0 ili 65 535),
  zastavice čvorova (sve iste), te mreže ili assete koji režu tlo: ono što je tamo
  postavljeno pod tlom su stijene i litice, a nijedan asset razine nije imenovan za rupe,
  tunele ili špilje. Dva rasterska stabla su dekodirana po duljini, ali nisu postavljena,
  i ona su ono što preostaje (vidi [Frostbite](reader-frostbite.md#terrain-layers)).
- **Varijacija objekta Battlefield 6 dopire do odjeljka kroz svoje blizance.** Varijacija
  postavljenog primjerka bira blokove sjenčala njegovih odjeljaka po ključu; gdje mreža
  nema blok za varijaciju, uzima se varijanta odjeljka neke druge mreže s istim zadanim
  blokom (vidi [Frostbite](reader-frostbite.md#textures-and-materials)). To je pravilo
  izvoznika; odjeljak bez blizanca koji se mijenja zadržava zadani izgled.
- **Slojeviti materijali Battlefield 6 crtaju se kao njihova osnova i jedan listić.** Zid
  s natpisom crta se kao njegova žbuka s listom slova preko nje; ostali slojevi materijala
  (prljavština kroz masku, detalj i mahovina) se ne miješaju.
- **Mreža navigacije je AI-jeva, ne igračeva.** Pokriva ono kamo vojnik može hodati: tlo,
  podove i stube te neke krovove, ali ne svako visoko mjesto. Veze između površina (skokovi,
  ljestve, preskakanja) se izostavljaju.
- **Razina Battlefield 6 uključuje sloj svakog načina igre.** Objekti koje postavlja samo
  jedan način igre mogu se preklapati s drugim. `--skip` izostavlja slojeve po imenu.
- **`courses` je samo za Forzu**, i uzima samo mape biblioteke imenovane `... (course_...)`.
- **Okvir kruga BeamNG-a pretpostavlja se** kao okvir preglednika `(x, z, -y)` koji
  piše snimač 3DHeata. Krugovi iz drugog snimača u sirovom okviru BeamNG-a ne bi se
  postavili.
- **`list` i `extract` uzimaju arhive, ne svaki format.** Otvaraju `.pak`, IoStore `.utoc`,
  `.vpk`, `.minizip` i zip. Unity spremnik se čita s `meshes`, Frostbite razina s `level`, a
  `.cdae` ili `.ter` je datoteka, a ne arhiva (`identify` ga imenuje). `.minizip` bez
  `ChunkContentsMiniZip<n>.txt` pored sebe popisuje se prema rednom broju unosa.
- **Postavljeni modeli u BeamNG-u koriste ponavljajuće teksture kao prosječne boje**, jer
  `.glb` uzorkivač steže, a preglednik pakira teksture u atlas.
- **Praktično samo Windows.** Steam putanje pod `C:\Program Files`, `%LOCALAPPDATA%`,
  `C:\XboxGames`, i `*_win64.dll` za Oodle. Ostale platforme nisu testirane.

## Neprovjereno {#unverified}

- Starije verzije Pythona (alat je pokretan s 3.13).
- Assetto Corsa Rally s krugom snimljenim u igri. Testiran je samo sintetskim krugovima u
  nasumičnim okvirima.
- glTF preglednici osim 3DHeat preglednika.
- Je li svaki okvir igre lijevo ili desno orijentiran. Izvoz zadržava telemetrijski okvir
  svake igre, pa se krugovi i staze poravnavaju bez obzira na to.
- Značenje z = 0 od `WaterBlock` kao njegove površine (BeamNG).
- Postavljanje Frostbitea na igrama osim Battlefield 6, i na Battlefield 6 nakon nadogradnje
  koja mijenja raspored člana grupe. Čitač tada ne nalazi grupe i to kaže.
- Poklapaju li se izvoz Battlefield 6 i pozicije koje igra prijavljuje. Koordinate su igrine
  vlastite, kao kod drugih igara, ali nijedna snimka još nije položena preko jednog.
