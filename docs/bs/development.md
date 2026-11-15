---
title: "Razvoj"
nav_order: 14
lang: "bs"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

## Raspored {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Mapa modula {#module-map}

| Modul | Šta radi |
|---|---|
| `__main__.py` | pokreće provjeru ažuriranja, zatim `cli.main()` |
| `cli.py` | glagoli (verbs), `identify`, raspodjela po arhivama, pisac staze za Forzu |
| `lapinput.py` | svaki oblik kruga u pozicije; traženje u biblioteci FH Companion |
| `corridor.py` | pojas s obje strane vožnje, kao raster od 4 m |
| `surfaces.py` | vrste tla, njihova imena dijelova i boje |
| `glb.py` | pisac `.glb` (dijelovi, normale, boje, teksture, kvantizacija) |
| `courseexport.py` | Forza: planarni UV-ovi pločica, podjela cesta/bankina, pečenje tla, podizanje decala |
| `forzainstall.py` | Steam i Xbox biblioteke; staza Forze kojoj kutija pripada |
| `minizip.py` | ForzaTech `.minizip` arhive i njihove liste imena |
| `forzatech.py` | `.modelbin`: chunkovi, baferi, rasporedi, podmreže, materijali |
| `forzaterrain.py` | pločice terena po mjestu; klase površina |
| `forzatexture.py` | `.pb` uzorci; mape pločica; pečenje tla |
| `forzamaterial.py` | `AssetManifest.xml`; koja tekstura boji model; godišnja doba |
| `forzaplacement.py` | `.pgeo` postavljanja, nivoi modela, teksture, izresci, zamjene, budžet |
| `beamng.py` | BeamNG instalacija, montirani datotečni sistem, scena, teren, materijali |
| `beamngcourse.py` | BeamNG izvoz staze |
| `beamngshape.py` | `.cdae` kompilirani oblici |
| `beamngcollada.py` | `.dae` rezerva |
| `acrally.py` | AC Rally instalacija, etape, postavljanje komponenti, volumen virtualne teksture |
| `acrallycourse.py` | AC Rally izvoz staze: fit okvira, tlo, postavljanje |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 pečeni paketi |
| `unversioned.py` | sheme i čitač neverzioniranih svojstava |
| `unrealmesh.py` | pečene statičke mreže |
| `unrealtexture.py` | teksture i streaming virtualne teksture |
| `oodle.py` | pronalaženje i pozivanje instalirane Oodle biblioteke |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity kontejneri, bundlovi, mreže |
| `frostbite.py` | Frostbite `.toc`, tablice sekcija, instalacijski paketi, lokacije chunkova, payloadi |
| `frostbitebundle.py` | Frostbite ugrađeni bundlovi, manifesti bundlova, katalog nivoa, lista nivoa |
| `frostbiteebx.py` | Frostbite RIFF EBX particije bez biblioteke tipova |
| `frostbitemesh.py` | Frostbite MeshSet i njegovi chunkovi nivoa detalja |
| `frostbiteterrain.py` | Frostbite streaming stablo terena, stranice visina, mreža tla |
| `frostbitematerial.py` | Frostbite teksture (BC1/BC3/BC7 mipovi), depoi shader blokova, izbor mape boje |
| `frostbitedecals.py` | Frostbite decali terena i pečenje tla |
| `frostbitenav.py` | Frostbite pločice navigacijske mreže: površine po kojima vojnici mogu hodati |
| `frostbitelevel.py` | Frostbite grupe statičkih modela, postavljanje, izvoz `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 komponente landscapea: heightmape u mrežu tla (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition mape: listanje, HLOD strukture, voda, izvoz `ue-map` |
| `enfusion.py` | Enfusion `.pak`, `.edds`, pločice terena, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger svjetovi: `.ent` datoteke, kutije, izvoz `enfusion-world` |
| `forzacars.py` | svaki Forza auto u niskom detalju u `.h3dcars` (`cars`) |

Svi moduli su na GitHubu pod
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Pokretanje testova {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` postavlja `testpaths = tests` i `-q`. Važe dvije vrste testova, iz
različitih razloga:

- **Sintetički testovi** grade arhive bajt po bajt i rade bilo gdje. Učvršćuju
  rasporede polja koji su u nekom trenutku bili pogrešni: 64-bitnu bazu segmenta
  `.minizip` i njen padding za poravnanje, escape veličine bloka u paku, u32
  između dva int64 u Unity zaglavlju, VPK indeks `0x7FFF`, podijeljeni x Forzine
  normale.
- **Testovi na instaliranim igrama** rade na stvarnim datotekama kad je igra na
  računaru, a **preskaču se** (ne padaju) kad nije. Samo oni hvataju raspored
  koji je ispravan za malu datoteku, a pogrešan za veliku.

### Fixtureovi {#fixtures}

| Fixture | Gradi |
|---|---|
| `tests/forza_fixtures.py` | `.minizip` arhive (s 64-bitnom bazom, paddingom, miješanim kodecima), manifeste, `.modelbin` modele i teren, `.pb` uzorke |
| `tests/beamng_fixtures.py` | malu BeamNG instalaciju: `gameengine.zip`, `content`, jedan zip nivoa s terenom od 64 m, trakom asfalta, decalom ceste, ogradom, prefabom, stavkom šume, morem, materijalima i `.cdae` oblicima u dokumentiranom rasporedu |
| `tests/unreal_fixtures.py` | IoStore kontejner s direktorijem, zen paketom, blokom neverzioniranih svojstava |
| `tests/frostbite_fixtures.py` | Frostbite tablice, bundlove, EBX particije, mreže i stranice terena, bajt po bajt |

### Datoteke testova {#test-files}

| Datoteka | Pokriva |
|---|---|
| `test_minizip.py` | čitanje nazad, 64-bitnu bazu, neparne i parne tablice bundlova, odbijanja, datoteku imena |
| `test_forzatech.py` | tablicu chunkova i lanac, odbijanja; instalirano: lanci i tagovi stvarnih modela |
| `test_forza_geometry.py` | svjetsko postavljanje, raspored vrhova, odbijene formate, podmreže, normale i UV-ove |
| `test_forzaterrain.py` | mrežu pločica (1023 naspram 512 m), rezanje, izvlačenje |
| `test_forzatexture.py` | zaglavlje uzorka, dekodiranje, policu tekstura, pečenje tla |
| `test_forzamaterial.py` | manifest, imena, hasheve materijala, izbor boje, godišnja doba |
| `test_forzaplacement.py` | zapis `.pgeo`, postavljanje kopija, nivoe, varijante, prozirne površine, cijelu kutiju, budžet, boju rezervnog mjesta, automatski budžet; instalirano: ivičnjaci na tlu |
| `test_forzainstall.py` | pronalaženje igre, biranje staze |
| `test_courseexport.py` | UV-ove pločica, plan dijelova, podizanje decala |
| `test_course_cli.py` | cijele glagole `course` i `courses` na sintetičkoj stazi; `terrain --route` sa oznakom redoslijeda bajtova i bez `bounds` |
| `test_archive_cli.py` | `identify`, `list` i `extract` na svakoj arhivi s čitačem (`.pak`, IoStore, `.vpk`, `.minizip` sa i bez njegovih imena, zip, `.cdae`, `.ter`); greške kao jedan red i izlazni kod: šifrirani pak, šifrirani kontejner, datoteka koja nije arhiva, loš `--key` |
| `test_corridor.py` | pojas, rezanje terena njime |
| `test_lapinput.py` | svaki oblik kruga, kutiju, greške, traženje imena staze, koja je igra u folderu |
| `test_surfaces.py` | koja imena određuju površinu, koja ne, imena dijelova |
| `test_glb.py` | datoteka je valjana, čvorovi nose klasu, odbijanja, kvantizaciju |
| `test_beamng.py` | oblike, nivo, kategorije, pronalaženje nivoa iz kruga, stazu, Collada rezervu; instalirano: `.cdae` naspram `.dae`, svaki nivo se otvara |
| `test_acrally.py` | kontejnere, pakete, svojstva, transformacije, fit okvira, dijelove postavljenih modela i budžet, virtualne teksture; instalirano: etape i pečena boja tla |
| `test_pak.py` | podnožje, unose, escape veličine bloka, odbijanja; instalirano: pomaci i SHA-1 |
| `test_unity.py` | odbijanja; instalirano: tablica objekata popločava datoteku, nizovi verzija, granice mreža |
| `test_frostbite.py` | potpisana naspram obfusciranih zaglavlja, odbijanja, instalacijski paketi (dva paketa s istim brojem bloba); instalirano: svaka tablica, superbundlovi, lanci sekcija, različiti id-ovi, uzorkovani payloadi iz ispravnog paketa |
| `test_frostbitelevel.py` | ids chunkova upareni s vlastitim lokacijama, ugrađeni bundlovi, manifesti, MeshSet sa sekcijom sjene i UV-ovima, član grupe, konvenciju transformacije, teren s dva nivoa, izbor mape boje, chunk teksture kojem fale najveći mipovi, ponavljajući sampler, zapise decala, decal složen po svojoj alfi, list decala koji gubi od vlastite mape površine, tablicu nivoa odabranu preko osnovne igre i njenih ažuriranja, navigacijske pločice (površine zadržane, veze izostavljene, odbijanja, detaljne mreže), ponavljajuće teksture zapisane s vlastitim koordinatama, trouglove rezane gdje se njihova tekstura ponavlja za izlaz s clampom, boju tla iz materijala njegovih površina, stranice maski (BC4 i nekomprimirane) postavljene na svoje kvadrante i odbijene kad se njihove ivice ne slažu, stranice colormapa postavljene na svoje kvadrante i pronađene nakon stranica maski koje stablo maski broji, polja udaljenosti, palete i maske kanala nikad uzete kao boja, nijansu bloka i sivu mapu oslikanu njome, vrh palete u središtu njenog uzorka, mrežu nagiba bilinearno raširenu nazad, prekrivku objekta nacrtanu kroz njegovo odmotavanje, blok varijacije ključan po svom hashu i dosegnut kroz blizanački blok, list slova položen četvrtim teksturnim koordinatama preko površine na kojoj je naslikan, boju decala čitanu iz njegovog materijala i nacrtane linije piste i tragove guma, dekodirane jednokanalne mape, razbijive mreže označene u njihovim dijelovima i extras, blockout, cinematic i lighting mreže izostavljene i raspored colormape koji se ne čita, mape izreza i njihove maskirane, dvostrane PNG materijale, tilove pozadine imenovane po njihovoj mreži; instalirano: decali terena nivoa, katalog najvećeg nivoa, mreže unutar svojih granica, članovi grupa, vegetacija koja stoji na dekodiranom terenu |
| `test_vpk.py` | direktorij, odbijanja, podijeljene arhive; instalirano: mape se otvaraju, CRC-ovi se podudaraju, nav mreža |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, pločice terena i datoteke svijeta; izvoz `enfusion-world` |
| `test_forzacars.py` | datoteka `.h3dcars` koju piše glagol `cars` |
| `test_unreallevel.py` | Unreal 5 landscapeove, HLOD strukture, vodu; izvoz `ue-map` |

## Testovi na instaliranim igrama {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
pronalazi igre za testove. `steam_common()` navodi `steamapps\common` svake Steam
biblioteke (uključujući Steamove vlastite foldere), a `installed(*globs)` vraća
putanje koje odgovaraju bilo kojem globu ispod njih, rekurzivno gdje glob ima
`**`. Svaki test sam odlučuje šta mu treba:

| Test | Traži | Preskače se s |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` s **nešifriranim** indeksom, do 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` u `*/*_Data` ili `*/*/*_Data` koje čitač prihvata, do 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, do 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | staze biblioteke FH Companion (start i cilj unutar 50 m), s najviše krugova, koje `find_track` smjesti; ili `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Pokrenite samo testove jedne igre, ili usmjerite Forza test ivičnjaka na stazu:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Testovi na instaliranim igrama čitaju samo iz igara. Ne pišu ništa u foldere
igara. Izlazi testova idu u pytestove privremene foldere.

## Konvencije {#conventions}

- **Odbijanje umjesto pogađanja.** Svaki čitač izaziva vlastiti izuzetak
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) s
  porukom koja kaže šta je pronađeno i zašto nije pročitano.
- **Provjerite prema samom formatu.** Hash, CRC, lanac pomaka, pohranjena granična
  kutija, vožnja koja leži na tlu. Ne "nije se srušilo".
- **Bez ključeva, bez priloženog vlasničkog koda.** Pogledajte [Pravila i licence](rules-and-licences.md).
- **Povjerljivi podaci ostaju vani.** Datoteke igara, izvozi, krugovi, snimci i
  snimke ekrana nikad ne idu u repozitorij. `.gitignore` ih isključuje po folderu
  i po tipu. Testovi koriste sintetičke podatke i instalirane igre, nikad
  ubačen sadržaj igara.
