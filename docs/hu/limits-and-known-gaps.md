---
title: Korlátok és ismert hiányosságok
nav_order: 10
lang: "hu"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Korlátok és ismert hiányosságok {#limits-and-known-gaps}

Mit nem csinál az eszköz, mit csak részben, és hol egyenetlen a viselkedése. A legtöbb hiányosság
szándékos megtagadás. Ha egy fájlt nincs mihez ellenőrizni, a visszafejtés olyan kimenetet ad,
amely jónak látszik, de nem az.

## Játékok {#games}

| Játék | Pályaexport | Miért nem, vagy mennyire |
|---|---|---|
| Forza Horizon | igen | a talajszín egy értelmezés (lásd lent) |
| BeamNG.drive | igen | nincs talajborítás, az ismétlődő modelltextúrák laposak |
| Assetto Corsa Rally | igen | a modellek egyszínűek; még nem futtattuk játékban rögzített körön |
| Assetto Corsa EVO | **nem** | minden tartalom egyetlen, kulccsal elrejtett csomagban van, és ez az eszköz nem nyer ki kulcsokat |
| Battlefield 6 (pályaexport, `level`) | igen, egész pálya | terep, csoportosított és egyenként elhelyezett hálók és színtérképeik, a katonák navigációs hálója, kivágott lombozat; a játéktér talajszíne durva (32 m pixelenként, vagy egy átlagszín); nincs áteresztőség vagy normáltérkép; a megsemmisíthető hálók megjelölve, de megsemmisült állapotaik nincsenek exportálva |
| Unreal 5 World Partition játékok (térképexport, `ue-map`) | igen, egész térkép | a talajrács pontos; az épületek a térkép egyszerűsített HLOD-hálói, nem a teljes részletességű modellek; vízterületek; nincs lombozat, matrica vagy talajszín |
| Arma Reforger (világexport, `enfusion-world`) | igen, egész világ | a terep a saját színeiben és a tenger; az épületek, kellékek és sziklák a modelljeik dobozai, nem a háromszögeik; fák kérésre (`--trees`), dobozként; nincsenek tavak, folyók vagy gyermek-entitások |
| iRacing | **nem** | a pályák védett formátumban vannak, amely nem fájl-kinyerési célpont |
| bármi más | **nem** | nincs pályaolvasó; építsd újra a játékból a 3DHeat GameCapture segítségével, vagy elemezd a köröket a nézegető Versenyelemzés paneljében pálya nélkül |

## Motorok és formátumok {#engines-and-formats}

| Formátum | Nincs megvalósítva |
|---|---|
| Unreal `.pak` | 8 előtti verziók; csak path-hash indexek (a nevek nem nyerhetők vissza); az index túlcsordulási listájában lévő bejegyzések (kihagyva); `.uasset`/`.umap` tartalmak visszafejtése pakból |
| Unreal IoStore | titkosított konténerek (megtagadva, nincs kulcsopció); olyan konténer felsorolása, amelynek nincs könyvtárindexe (nem nevez meg fájlokat); verziózott csomagok; csak Nanite és nem beágyazott hálók; csontozott hálók; olyan osztályok tulajdonságai, amelyekhez nincs séma; példányosított komponensek tulajdonságai (a játék buildjében megváltozott az elrendezés); spline-hálók és matricakomponensek |
| Unity | 22 előtti formátumok (Unity 2019 és régebbi); beágyazott típusfákkal rendelkező fájlok; tömörített hálók; a `Mesh` kivételével minden osztály, tehát nincs transzformáció, anyag vagy jelenet; `meshes` csomagon; `list`/`extract` (használd a `meshes`-t) |
| Frostbite | XOR-ral elrejtett táblák; a terep rétegkompozíciós gráfja (a maszkok az ellenőrzött pályák mintegy harmadában olvashatók); a hálókon kívüli objektum-tervrajzok (játéklogika, effektek, hangok); beágyazott hálószintek; normál- és egyéb térképek, az alfa a kivágásokon kívül; terepi lyukak; a típuskönyvtár (titkosítva a kezdeti fájlrendszerben, nem nyúlunk hozzá); parancs egyes eszközök felsorolására vagy kinyerésére |
| Source 2 | fordított eszközök (`.vmdl_c`, `.vtex_c`); a CS2 navigációs háló (36-os verzió) |
| ForzaTech | a négy skálázott rövid int-en kívüli pozícióformátumok; a u16-on kívüli indexformátumok; a 0, 9, 13-on kívüli textúrakódok; a terepárnyaló anyagrétegei; tangensek |
| BeamNG | csontozott és matricaháló; animáció; procedurális talajborítás; a világ szélén lévő díszlet |
| Unreal talajrácsok és World Partition térképek | olyan talajrácsok, amelyek magasságtérképei a cookolt cellákban vannak; szerkesztési rétegek és lyukak; Nanite talajrács-hálók; a cellákba helyezett teljes részletességű modellek; lombozat; talajanyagok |
| Enfusion | modellháromszögek (a `.xob` geometria olyan elrendezésben tömörített, amelyet nem olvasunk); pre-DX10 fejlécű `.edds`; beágyazott objektumértékek a világfájlokban (kihagyva, számolva); gyermek-entitások; generált tavak és folyók; `list`/`extract` `.pak`-on |

## Viselkedés, amit érdemes tudni {#behaviour-worth-knowing}

- **A Forza talajszíne nem a játék színe.** A sütött textúrát azokból a csempe-térképekből rajzoljuk,
  amelyek megmondják, hol van aszfalt, rövid fű, durva talaj és erdő. Rögzített színeket és
  árnyalást használ, mert a terepárnyaló saját anyagrétegeit nem dekódoljuk.
- **A `--no-textures` a Forza padkáját is eltávolítja.** Az aszfalt/padka szétválasztás az aszfaltmaszkot
  használja, amely a sütött térképekkel jön. Textúrák nélkül az úti csíkok egészek maradnak, mint út.
- **A megadott keretet csak a szegélykövek léphetik túl.** A szegélykövek (és a BeamNG vezetési felületű
  modelljei) minden játékban soha nincsenek egyszerűsítve vagy kihagyva, így egy `--detail-budget`,
  amely kisebb, mint amennyibe ezek kerülnek, csak miattuk lépi túl; minden más előbb kimarad.
  Lásd: [Részletességi szintek és a keret](detail-budget.md).
- **A nem alkalmazható beállításokat csendben figyelmen kívül hagyjuk**: a `--season` a BeamNG-nél és
  az AC Rally-nál, a `--track` a BeamNG-nél és az AC Rally-nál, a `--level`/`--install` a Forzánál.
- **Egy Battlefield 6-pálya talajszíne a matricáktól távol durva.** A magassági mezőt a terepi háttér
  színtérképéből színezzük, 32 m pixelenként a legnagyobb mipen, amelyet a pálya szállít — vagy, ahol
  nincs háttértérkép, a terep felületi anyagainak középső színéből. A `--ground-texture` ezt megszorozza
  a terep színtérképével (0,5 m pixelenként, ahol a pályának van), és az utakat, előtereket,
  kifutópálya-vonalakat, gumiabroncs-nyomokat és jelöléseket beleégeti, az anyagaik festékszínében, ahol
  az be van állítva, semleges színben, ahol nincs; az úti változatmaszkok kimaradnak. A játék a
  felületi rétegeit egy árnyalógráfban keveri, amelyet nem olvasunk; az export a rétegek színeit a
  maszkjaik és a magassági mező lejtése szerint fekteti le, saját szabály szerint, és a rétegek
  maszkjai nem illeszkedő pályán egyetlen szín kerül. Minden réteg a színtérképe átlaga, nem a
  textúrája. Lásd: [Frostbite](reader-frostbite.md#terrain-layers). A magassági mező különböző
  felbontású darabjai apró lépcsőkkel illeszkednek.
- **A Battlefield 6 színtérképe kiválasztott, nem olvasott.** Egy árnyalóblokk megnevezi az összes
  textúrát, amelyet mintavesz, de nem mondja meg, melyik a szín; a választás névvel történik (lásd:
  [Frostbite](reader-frostbite.md#textures-and-materials)), és egy felülethez díszítő vagy részletes
  lapot választhat. A matrica-lapok (`t_de_...`) veszítenek a felület saját térképével szemben; egy
  táblamatrica, amelyet a paneljaként rajzoltunk, a pajzsát negyed fordulattal mutatta. A távolsági
  mezőket, paletták és csatornamaszkok sosem vesszük. A háttérépületek a paletta színeivel rajzolódnak;
  a szürke térképek a anyag árnyalatát veszik egy saját szabály szerint, mivel a paraméterek nevei
  hashelve vannak, és egy anyag, amely szürke térképet több árnyalatú maszkon át fest, az egyiket kapja.
- **A Battlefield 6 terepi lyukai nincsenek kivágva.** Ahol egy pálya járható talaja a magassági mező
  alatt fut, a játéknak ki kell vágnia a terepet, az export pedig nem vágja ki. A lyukak helyeként
  kizárva: a terep rétegmaszkjai (egyik sem koncentrálódik ott), a 67 x 67-es csomópontrácsa, egy
  fenntartott magasságérték (egyik magasságlap sem tartalmaz 0-t vagy 65 535-öt), a csomópontok jelzői
  (mind egyformák), és a hálók vagy eszközök, amelyek kivágják a talajt: ami ott a talaj alatt van,
  sziklák és szikla-hálók, és a pálya egyetlen eszközét sem nevezik el lyukaknak, alagutaknak vagy
  barlangoknak. Két rasztercsa futáshossz-kódolva van dekódolva, de nincs elhelyezve, és ezek maradnak
  (lásd: [Frostbite](reader-frostbite.md#terrain-layers)).
- **A Battlefield 6 objektumváltozat a rokonai révén éri el a szakaszt.** Egy elhelyezett példány
  változata a kulcsa alapján választja ki a szakaszainak árnyalóblokkjait; ahol egy hálónak nincs blokkja
  egy változathoz, egy másik háló szakaszának változata kerül elő, azonos alapblokkkal (lásd
  [Frostbite](reader-frostbite.md#textures-and-materials)). Ez az exportőr szabálya; egy változó rokon
  nélküli szakasz az alapkinézetét tartja meg.
- **A Battlefield 6 rétegelt anyagai az alapjukként és egy lapként rajzolódnak.** Egy betűs falpanel a
  vakolatával rajzolódik, a betűlappal rajta; az anyag többi rétege (a koszmaszk, a részlet- és mohatérkép)
  nincs bekeverve.
- **A navigációs háló a mesterséges intelligenciáé, nem a játékosoké.** Azt fedi le, amire egy katona
  léphet: a talajt, padlót és lépcsőt, és néhány tetőt, de nem minden magas pontot. A felületek közötti
  kapcsolatok (ugrások, létrák, átugrások) kimaradnak.
- **A Battlefield 6 pálya minden játékmód rétegét tartalmazza.** Az objektumok, amelyeket csak egy
  mód helyez el, átfedhetik egy másikét. A `--skip` névvel hagy ki rétegeket.
- **A `courses` csak a Forzára vonatkozik**, és csak azokat a könyvtármappákat veszi fel, amelyek neve
  `... (course_...)`.
- **A BeamNG körkeret feltételezett**: a nézegető keret `(x, z, -y)`, amelyet a 3DHeat rögzítő ír.
  A BeamNG nyers keretében másik rögzítővel készült körök nem kerülnének a helyükre.
- **A `list` és `extract` csak az archívumokat veszi, nem minden formátumot.** Megnyitják a `.pak`-ot,
  az IoStore `.utoc`-ot, a `.vpk`-t, a `.minizip`-et és a zipet. Egy Unity-konténert a `meshes`-szel, egy
  Frostbite-pályát a `level`-lel olvasunk, a `.cdae` vagy `.ter` pedig fájl, nem archívum (az `identify`
  megnevezi). A `ChunkContentsMiniZip<n>.txt` nélküli `.minizip` a bejegyzésszámmal listázódik.
- **A BeamNG-modellek ismétlődő textúrái átlagszínként jelennek meg**, mert a `.glb` mintavevő
  szorítja, a nézegető pedig atlaszba csomagolja a textúrákat.
- **A gyakorlatban csak Windowsra.** A Steam-útvonalak a `C:\Program Files` alatt, a
  `%LOCALAPPDATA%`, a `C:\XboxGames`, és egy `*_win64.dll` az Oodle-hez. Más platformokat nem teszteltünk.

## Nem ellenőrzött {#unverified}

- Régebbi Python-verziók (az eszközt 3.13-mal futtatták).
- Assetto Corsa Rally játékban rögzített körrel. Csak szintetikus köröken, véletlen keretekben tesztelve.
- A 3DHeat nézegetőjén kívüli glTF-nézegetők.
- Hogy egy-egy játék keretje balkezes vagy jobbkezes-e. Az export minden játék telemetriai keretét
  megtartja, így a körök és a pályák így is illeszkednek.
- A `WaterBlock` helyi z = 0 jelentése a felületként (BeamNG).
- A Frostbite-elhelyezés a Battlefield 6-on kívül más játékokon, és a Battlefield 6-on olyan frissítés
  után, amely megváltoztatja a csoporttag elrendezését. Ilyenkor az olvasó nem talál csoportokat, és ezt
  jelzi.
- Hogy a Battlefield 6 export illeszkedik-e a játék által jelentett pozíciókhoz. A koordináták a játék
  saját koordinátái, mint a többi játéknál, de még nem rakódott rá rögzített felvétel.
