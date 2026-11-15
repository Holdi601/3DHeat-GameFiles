---
title: Fejlesztés
nav_order: 14
lang: "hu"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Fejlesztés {#development}

## Felépítés {#layout}

```
heat3d_gamefiles/     a csomag: olvasók, pályaexportok, a parancssor
heat3d_update/        a kiadás-ellenőrzés és a frissítő (lásd: Frissítések)
tests/                szintetikus tesztek, tesztadatok és a telepített játékokon futó tesztek
docs/                 ez a dokumentáció (a docs/wiki ebből készül)
VERSION               a telepített verzió, összevetve a GitHub-kiadásokkal
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Modultérkép {#module-map}

| Modul | Mit csinál |
|---|---|
| `__main__.py` | lefuttatja a frissítés-ellenőrzést, aztán a `cli.main()`-t |
| `cli.py` | a parancsok, `identify`, archívum-kiválasztás, a Forza pályaíró |
| `lapinput.py` | minden körforma pozíciókká alakítása; FH Companion könyvtári keresés |
| `corridor.py` | a vezetés mindkét oldalán lévő sáv, 4 m-es rasztereként |
| `surfaces.py` | a talajfajták, részneveik és színeik |
| `glb.py` | a `.glb` író (részek, normálok, színek, textúrák, kvantálás) |
| `courseexport.py` | Forza: síkbeli csempe-UV-k, út/padka-szétbontás, talajsütés, matricaemelés |
| `forzainstall.py` | Steam- és Xbox-könyvtárak; melyik Forza-pályához tartozik egy doboz |
| `minizip.py` | ForzaTech `.minizip` archívumok és nevlistáik |
| `forzatech.py` | `.modelbin`: darabok, pufferek, elrendezések, részhálók, anyagok |
| `forzaterrain.py` | terepcsempék helyük szerint; felületi osztályok |
| `forzatexture.py` | `.pb` mintakártyák; csempe-térképek; a talajsütés |
| `forzamaterial.py` | `AssetManifest.xml`; mely textúra színezi a modellt; évszakok |
| `forzaplacement.py` | `.pgeo` elhelyezések, modellszintek, textúrák, kivágások, helyettesítők, a keret |
| `beamng.py` | BeamNG-telepítés, csatolt fájlrendszer, jelenet, terep, anyagok |
| `beamngcourse.py` | a BeamNG pályaexport |
| `beamngshape.py` | `.cdae` fordított alakzatok |
| `beamngcollada.py` | `.dae` tartalék |
| `acrally.py` | AC Rally-telepítés, szakaszok, komponens-elhelyezés, virtuálistextúra-kötet |
| `acrallycourse.py` | az AC Rally pályaexport: keretillesztés, talaj, elhelyezés |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 cookolt csomagok |
| `unversioned.py` | nem verziózott tulajdonság-sémák és olvasó |
| `unrealmesh.py` | cookolt statikus hálók |
| `unrealtexture.py` | textúrák és streamelt virtuális textúrák |
| `oodle.py` | a gépen lévő Oodle-könyvtár megtalálása és hívása |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity-konténerek, csomagok, hálók |
| `frostbite.py` | Frostbite `.toc`, szakasztáblák, telepítőcsomagok, darabhelyek, adatok |
| `frostbitebundle.py` | Frostbite beágyazott csomagok, csomagjegyzékek, egy pálya katalógusa, a pályalista |
| `frostbiteebx.py` | Frostbite RIFF EBX partíciók típuskönyvtár nélkül |
| `frostbitemesh.py` | Frostbite MeshSet és részletességi szint darabjai |
| `frostbiteterrain.py` | Frostbite terep-streaming fa, magasságlapok, a talajháló |
| `frostbitematerial.py` | Frostbite textúrák (BC1/BC3/BC7 mipek), árnyalóblokk-tárak, színtérkép-választás |
| `frostbitedecals.py` | Frostbite terepmatricák és a talajsütés |
| `frostbitenav.py` | Frostbite navigációs háló-csempék: a katonák járható felületei |
| `frostbitelevel.py` | Frostbite statikus modellcsoportok, elhelyezés, a `level` export |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 talajrács-komponensek: magasságtérképek a talajhálóba (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition térképek: listázás, HLOD-szerkezetek, víz, az `ue-map` export |
| `enfusion.py` | Enfusion `.pak`, `.edds`, terepcsempék, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger világok: `.ent` fájlok, dobozok, az `enfusion-world` export |
| `forzacars.py` | minden Forza-autó alacsony részletességen `.h3dcars` fájlba (`cars`) |

Minden modul megtalálható a GitHubon a
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles)
alatt.

## A tesztek futtatása {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

A `pytest.ini` beállítja a `testpaths = tests` és a `-q` opciókat. Kétfajta teszt számít,
különböző okokból:

- **Szintetikus tesztek** bájtról bájtra építenek archívumokat, és bárhol futnak. Ezek rögzítik
  azokat a mezőelrendezéseket, amelyek valaha rosszak voltak: a 64 bites `.minizip` szegmensbázis
  és igazító kitöltése, a pak blokkméret-escape, a Unity-fejléc két int64 közötti u32-je, a VPK
  `0x7FFF` indexe, a Forza-normál felosztott x-e.
- **Telepített játékokon futó tesztek** a valódi fájlokon futnak, ha a játék a gépen van, és
  **kihagyják** (nem buknak el), ha nincs. Ezek az egyetlen dolog, amely elkapja azt az elrendezést,
  amely egy kis fájlon helyes, egy nagyon nagyon nagyon nagyon nagyon nagy fájlon viszont rossz.

### Tesztadatok {#fixtures}

| Tesztadat | Készít |
|---|---|
| `tests/forza_fixtures.py` | `.minizip` archívumok (64 bites bázissal, kitöltéssel, vegyes kodekekkel), manifesztek, `.modelbin` modellek és terep, `.pb` mintakártyák |
| `tests/beamng_fixtures.py` | egy kis BeamNG-telepítés: `gameengine.zip`, `content`, egy szintzip 64 m-es terepgel, egy aszfaltcsík, úti matrica, korlát, előregyártott elem, erdei elem, a tenger, anyagok, és dokumentált elrendezésű `.cdae` alakzatok |
| `tests/unreal_fixtures.py` | IoStore-konténer könyvtárral, zen csomag, egy nem verziózott tulajdonságblokk |
| `tests/frostbite_fixtures.py` | Frostbite táblák, csomagok, EBX partíciók, hálók és terepoldalak, bájtról bájtra |

### Tesztfájlok {#test-files}

| Fájl | Lefedi |
|---|---|
| `test_minizip.py` | visszaolvasás, a 64 bites bázis, páros és páratlan csomagtáblák, elutasítások, a nevfájl |
| `test_forzatech.py` | a darabtábla és -lánc, elutasítások; telepítve: valódi modellek láncai és címkéi |
| `test_forza_geometry.py` | világbeli elhelyezés, csúcselrendezés, elutasított formátumok, részhálók, normálok és UV-k |
| `test_forzaterrain.py` | a csempe-rács (1023 vs 512 m), vágás, kinyerés |
| `test_forzatexture.py` | mintakártya-fejléc, dekódolás, a textúrapolc, a talajsütés |
| `test_forzamaterial.py` | a manifeszt, nevek, anyag-hash-ek, a színválasztás, évszakok |
| `test_forzaplacement.py` | a `.pgeo` rekord, példányok elhelyezése, szintek, változatok, áttetsző felületek, egész doboz, a keret, a helyőrző szín, az automatikus keret; telepítve: szegélykövek a talajon |
| `test_forzainstall.py` | a játék megtalálása, a pálya kiválasztása |
| `test_courseexport.py` | csempe-UV-k, a részterv, matricaemelés |
| `test_course_cli.py` | a teljes `course` és `courses` parancs egy szintetikus pályán; `terrain --route` bájtsorrend-jelzővel és `bounds` nélkül |
| `test_archive_cli.py` | `identify`, `list` és `extract` minden olvasóval rendelkező archívumon (`.pak`, IoStore, `.vpk`, `.minizip` névvel és név nélkül, zip, `.cdae`, `.ter`); a hibák egy sorban, kilépési kóddal: titkosított pak, titkosított konténer, nem archívum fájl, rossz `--key` |
| `test_corridor.py` | a sáv, terep vágása vele |
| `test_lapinput.py` | minden köralak, a doboz, hibák, pályanév-keresés, melyik játék egy mappa |
| `test_surfaces.py` | mely nevek döntenek egy felületről, melyek nem, részvnevek |
| `test_glb.py` | a fájl érvényes, a csomópontok viselik az osztályt, elutasítások, kvantálás |
| `test_beamng.py` | alakzatok, a szint, kategóriák, a szint megtalálása egy körből, a pályaexport, a Collada-tartalék; telepítve: `.cdae` vs `.dae`, minden szint megnyílik |
| `test_acrally.py` | konténerek, csomagok, tulajdonságok, transzformációk, a keretillesztés, elhelyezett modellek részei és a keret, virtuális textúrák; telepítve: szakaszok és a sütött talajszín |
| `test_pak.py` | lábléc, bejegyzések, a blokkméret-escape, elutasítások; telepítve: eltolások és SHA-1 |
| `test_unity.py` | elutasítások; telepítve: az objektumtábla lefedi a fájlt, verziósztringek, háló-határolók |
| `test_frostbite.py` | aláírt vs elhomályosított fejlécek, elutasítások, telepítőcsomagok (két csomag ugyanazzal a blobszámmal); telepítve: minden tábla, szuperdarabok, szakaszláncok, különböző azonosítók, mintavett adatok a helyes csomagból |
| `test_frostbitelevel.py` | darazonosítók a saját helyükkel párosítva, beágyazott csomagok, jegyzékek, MeshSet árnyéksemmel és UV-kkel, egy csoporttag, a transzformációs konvenció, kétszintű terep, színtérkép-választás, egy textúra-darab, amelyből hiányoznak a legnagyobb mipek, az ismétlődő mintavevő, matricarekordok, egy matricát az alfája alapján kompozitoltak, egy matricalap, amely veszít a felület saját térképével szemben, a szint matricatáblája a főjáték és a frissítései között, navigációs csempék (felületek megtartva, kapcsolatok kihagyva, elutasítások, részletes hálók), ismétlődő textúrák a saját koordinátáikkal, háromszögek vágva ott, ahol a textúra ismétlődik, a talaj színe a felületi anyagaiból, maszklapok (BC4 és nem tömörített) a negyedeikre helyezve és elutasítva, ha a szegélyeik nem illenek, színtérkép-lapok a negyedeikre helyezve, és a maszkfa által számolt maszk-lapok után megtalálva, távolságmezők, paletták és csatornamaszkok sosem színként véve, egy blokk színezése és egy szürke térkép a színnel festve, paletta-csúcs a mintakártya közepén, a lejtőrács visszaterítve bilineárisan, egy objektum rávetített képe a kibontásán át, egy változat blokkja a hash-ével kulcsolva és egy ikerblokkon át elérve, egy betűlap a negyedik textúra-koordinátákkal a felületre fektetve, amelyre festik, egy matrica festéke az anyagából, futópálya-vonalak és gumiabroncs-nyomok rajzolva, egyetlen csatornás térképek dekódolva, összetörhető hálók megjelölve a részeikben és extrákban, blockout-, filmes és világítási hálók kihagyva, és egy elrendezés, amelyet nem olvasnak, az áttetsző térképek és azok maszkjai, kétoldalas PNG-anyagok, a háttértégla-csempék a hálójuk szerint nevezve; telepítve: a szint terepmatricái, a legnagyobb szint katalógusa, hálók a határoló dobozaikon belül, csoporttagok, növényzet a dekódolt terepen |
| `test_vpk.py` | a könyvtár, elutasítások, többrészes archívumok; telepítve: a térképek megnyílnak, CRC-k egyeznek, a navigációs háló |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, terepcsempék és világfájlok; az `enfusion-world` export |
| `test_forzacars.py` | a `cars` parancs által írt `.h3dcars` fájl |
| `test_unreallevel.py` | Unreal 5 talajrácsok, HLOD-szerkezetek, víz; az `ue-map` export |

## Telepített játékon futó tesztek {#installed-game-tests}

A [`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
játékokat keres a tesztekhez. A `steam_common()` minden Steam-könyvtár `steamapps\common`
mappáját listázza (a Steam saját mappáival együtt), az `installed(*globs)` pedig a mintának
megfelelő elérési utakat adja vissza, rekurzívan, ahol a mintában `**` van. Minden teszt maga
dönti el, mire van szüksége:

| Teszt | Ezt keresi | Ezzel hagyja ki |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` **titkosítatlan** indexszel, legfeljebb 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` a `*/*_Data` vagy `*/*/*_Data` mappákban, amelyeket az olvasó elfogad, legfeljebb 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, legfeljebb 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | az FH Companion könyvtárának pályái (rajt és cél 50 m-en belül), a legtöbb körrel, amelyet a `find_track` megtalál; vagy `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Csak egy játék tesztjeit futtatni, vagy a Forza szegély-tesztjét egy pályára irányítani:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

A telepített játékon futó tesztek csak a játékokat olvassák. Semmit nem írnak játékmappákba.
A tesztek kimenete a pytest ideiglenes mappáiba kerül.

## Konvenciók {#conventions}

- **Inkább megtagadjuk, mint kitalálunk.** Minden olvasó a saját kivételét dobja (`UnsupportedPak`,
  `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`,
  `BeamNGError`, `PropertyError`...), egy üzenettel, amely megmondja, mit talált és miért nem
  olvasta.
- **Ellenőrzés magával a formátummal.** Hash, CRC, eltolások láncolata, tárolt határoló doboz,
  a vezetés a talajon fekszik. Nem az, hogy „nem omlott össze".
- **Nincs kulcs, nincs csomagolt zárt kód.** Lásd: [Szabályok és licencek](rules-and-licences.md).
- **A bizalmas adatok kimaradnak.** A játékfájlok, exportok, körök, felvételek és képernyőképek
  soha nem kerülnek a tárolóba. A `.gitignore` mappa és típus szerint kizárja őket. A tesztek
  szintetikus adatokat vagy telepített játékokat használnak, soha nem ellenőrzött játéktartalmat.
