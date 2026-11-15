---
title: "Dezvoltare"
nav_order: 14
lang: "ro"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Dezvoltare {#development}

## Structura {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Harta modulelor {#module-map}

| Modul | Ce face |
|---|---|
| `__main__.py` | rulează verificarea de actualizare, apoi `cli.main()` |
| `cli.py` | comenzile, `identify`, trimiterea către arhive, scriitorul de circuit Forza |
| `lapinput.py` | fiecare formă de tur devine poziții; căutarea numelui de circuit din biblioteca FH Companion |
| `corridor.py` | fâșia de o parte și de alta a parcursului, ca raster de 4 m |
| `surfaces.py` | tipurile de sol, numele pieselor și culorile lor |
| `glb.py` | scriitorul `.glb` (piese, normale, culori, texturi, cuantizare) |
| `courseexport.py` | Forza: UV-uri plane ale dalelor, separarea drum/acostament, coacerea solului, ridicarea decalcomaniilor |
| `forzainstall.py` | bibliotecile Steam și Xbox; traseul Forza căruia îi aparține o casetă |
| `minizip.py` | arhivele ForzaTech `.minizip` și listele lor de nume |
| `forzatech.py` | `.modelbin`: bucăți, buffere, layout-uri, submeshuri, materiale |
| `forzaterrain.py` | dalele de teren după loc; clasele de suprafață |
| `forzatexture.py` | mostrele `.pb`; hărțile de dale; coacerea solului |
| `forzamaterial.py` | `AssetManifest.xml`; ce culori de textură are un model; sezoane |
| `forzaplacement.py` | plasările `.pgeo`, nivelurile modelelor, texturile, decupările, înlocuitorii pentru clădiri, bugetul |
| `beamng.py` | instalarea BeamNG, sistemul de fișiere montat, scena, terenul, materialele |
| `beamngcourse.py` | exportul de circuit BeamNG |
| `beamngshape.py` | forme compilate `.cdae` |
| `beamngcollada.py` | rezerva `.dae` |
| `acrally.py` | instalarea AC Rally, etapele, plasarea componentelor, texturile virtuale |
| `acrallycourse.py` | exportul de circuit AC Rally: potrivirea cadrului, solul, plasarea |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | pachete Unreal 5 compilate |
| `unversioned.py` | scheme de proprietăți neversionate și cititorul lor |
| `unrealmesh.py` | mesh-uri statice compilate |
| `unrealtexture.py` | texturi și texturi virtuale de streaming |
| `oodle.py` | găsirea și apelarea unei biblioteci Oodle instalate |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | containere, pachete și mesh-uri Unity |
| `frostbite.py` | `.toc` Frostbite, tabele de secțiuni, pachete de instalare, locații de bucăți, încărcături |
| `frostbitebundle.py` | pachete inline Frostbite, manifestele lor, catalogul unui nivel, lista nivelurilor |
| `frostbiteebx.py` | partiții RIFF EBX Frostbite, fără o bibliotecă de tipuri |
| `frostbitemesh.py` | MeshSet Frostbite și bucățile lui de nivel de detaliu |
| `frostbiteterrain.py` | arborele de streaming al terenului Frostbite, paginile de înălțime, meshul solului |
| `frostbitematerial.py` | texturi Frostbite (mip-uri BC1/BC3/BC7), depozitele blocurilor de shader, alegerea hărții de culoare |
| `frostbitedecals.py` | decalcomaniile de teren Frostbite și coacerea solului |
| `frostbitenav.py` | dalele plasei de navigare Frostbite: suprafețele pe care merg soldații |
| `frostbitelevel.py` | grupuri statice de modele Frostbite, plasarea, exportul `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | componente de landscape Unreal 5: câmpuri de înălțime în mesh-ul solului (`ue-map`) |
| `unreallevel.py` | hărți Unreal 5 World Partition: listare, structuri HLOD, apă, exportul `ue-map` |
| `enfusion.py` | `.pak` Enfusion, `.edds`, dale de teren, `resourceDatabase.rdb` |
| `enfusionworld.py` | lumile Arma Reforger: fișiere `.ent`, casete, exportul `enfusion-world` |
| `forzacars.py` | fiecare mașină Forza la detaliu redus, în `.h3dcars` (`cars`) |

Toate modulele sunt pe GitHub, în [`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Rularea testelor {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` setează `testpaths = tests` și `-q`. Două tipuri de teste contează, din motive diferite:

- **Testele sintetice** construiesc arhive octet cu octet și rulează oriunde. Ele fixează structurile câmpurilor care au fost greșite la un moment dat: baza `.minizip` pe 64 de biți și padding-ul ei de aliniere, escape-ul dimensiunii de bloc din pak, cuvântul de 32 de biți din antetul Unity dintre două int64, indexul VPK `0x7FFF`, despicarea x a normalei Forza.
- **Testele pe jocurile instalate** rulează pe fișierele reale când jocul se află pe calculator și **sar** (nu eșuează) când nu se află. Ele sunt singurul lucru care prinde o structură care este corectă pentru un fișier mic și greșită pentru unul mare.

### Fixturi {#fixtures}

| Fixtură | Construiește |
|---|---|
| `tests/forza_fixtures.py` | arhive `.minizip` (cu baza de 64 de biți, padding, codecuri amestecate), manifeste, modele `.modelbin` și teren, mostre `.pb` |
| `tests/beamng_fixtures.py` | o mică instalare BeamNG: `gameengine.zip`, `content`, un zip de nivel cu un teren de 64 m, o bandă de asfalt, o decalcomanie de drum, o barieră, un prefab, un obiect de pădure, marea, materiale și forme `.cdae` în structura documentată |
| `tests/unreal_fixtures.py` | un container IoStore cu un director, un pachet zen, un bloc de proprietăți neversionate |
| `tests/frostbite_fixtures.py` | tabele Frostbite, pachete, partiții EBX, mesh-uri și pagini de teren, octet cu octet |

### Fișierele de test {#test-files}

| Fișier | Acoperă |
|---|---|
| `test_minizip.py` | citirea înapoi, baza de 64 de biți, tabele de pachete pare și impare, refuzuri, fișierul cu nume |
| `test_forzatech.py` | tabelul și lanțul de bucăți, refuzuri; instalat: lanțurile și etichetele modelelor reale |
| `test_forza_geometry.py` | plasarea în lume, layout-ul vertexurilor, formatele refuzate, submeshurile, normalele și UV-urile |
| `test_forzaterrain.py` | grila dalelor (1023 vs 512 m), decuparea, extragerea |
| `test_forzatexture.py` | antetul mostrei, decodarea, rafturile de texturi, coacerea solului |
| `test_forzamaterial.py` | manifestul, numele, hash-urile materialelor, alegerea culorii, sezoanele |
| `test_forzaplacement.py` | înregistrarea `.pgeo`, plasarea copiilor, nivelurile, variantele, suprafețele transparente, o casetă întreagă, bugetul, culoarea de substituție, bugetul automat; instalat: bordurile pe sol |
| `test_forzainstall.py` | găsirea jocului, alegerea traseului |
| `test_courseexport.py` | UV-urile dalelor, planul pieselor, ridicarea decalcomaniilor |
| `test_course_cli.py` | comenzile complete `course` și `courses` pe un traseu sintetic; `terrain --route` cu marcaj de ordine a octeților și fără `bounds` |
| `test_archive_cli.py` | `identify`, `list` și `extract` pe fiecare arhivă cu cititor (`.pak`, IoStore, `.vpk`, `.minizip` cu și fără nume, zip, `.cdae`, `.ter`); erorile ca o linie și un cod de ieșire: un pak criptat, un container criptat, un fișier care nu e arhivă, o cheie `--key` greșită |
| `test_corridor.py` | fâșia, tăierea terenului cu ea |
| `test_lapinput.py` | fiecare formă de tur, caseta, erorile, căutarea numelui de circuit, ce joc este un folder |
| `test_surfaces.py` | ce nume decid o suprafață și care nu, numele pieselor |
| `test_glb.py` | fișierul este valid, nodurile poartă clasa, refuzuri, cuantizare |
| `test_beamng.py` | forme, nivelul, categoriile, găsirea nivelului dintr-un tur, circuitul, rezerva Collada; instalat: `.cdae` față de `.dae`, fiecare nivel se deschide |
| `test_acrally.py` | containere, pachete, proprietăți, transformări, potrivirea cadrului, piesele și bugetul modelelor plasate, texturi virtuale; instalat: etapele și culoarea de sol coaptă |
| `test_pak.py` | footer, intrări, escape-ul dimensiunii de bloc, refuzuri; instalat: decalaje și SHA-1 |
| `test_unity.py` | refuzuri; instalat: tabelul de obiecte acoperă fișierul, șirurile de versiune, limitele mesh-urilor |
| `test_frostbite.py` | antete cu semn față de cele obfuscate, refuzuri, pachete de instalare (două pachete cu același număr de blob); instalat: fiecare tabel, superbundle-uri, lanțuri de secțiuni, id-uri distincte, încărcături eșantionate din pachetul potrivit |
| `test_frostbitelevel.py` | id-urile de bucăți asociate cu locațiile lor, pachete inline, manifeste, un MeshSet cu o secțiune de umbră și UV-uri, un membru de grup, convenția de transformare, un teren cu două nivele, alegerea hărții de culoare, o bucată de textură fără cele mai mari mip-uri, eșantionatorul care se repetă, înregistrările de decalcomanii, o decalcomanie compusă după alfa, un sheet de decalcomanie care cedează în fața hărții proprii a unei suprafețe, tabelul nivelului ales între jocul de bază și actualizările lui, dale de navigare (suprafețe păstrate, legături lăsate afară, refuzuri, mesh-uri de detaliu), texturi care se repetă scrise cu propriile coordonate, triunghiuri tăiate unde textura se repetă pentru ieșire cu clamp, culoarea de sol din materialele suprafeței, hărți de mască (BC4 și neederivate) puse pe cadranele lor și refuzate când marginile nu se potrivesc, pagini de hartă de culoare puse pe cadrane și găsite după paginile de mască pe care le contează arborele măștilor, câmpuri de distanță, palete și măști de canal care nu sunt niciodată luate drept culoare, nuanța unei blocuri și o hartă gri vopsită cu ea, un vertex de paletă la centrul mostrei lui, grila de pante redistribuită biliniar, suprapunerea unui obiect desfășurată prin unwrap-ul lui, blocul unei variante indexat după hash și atins printr-un bloc geamăn, un sheet de litere pus peste suprafața pe care e pictat prin a patra coordonată de textură, decalcomanii de pistă și urme de anvelope desenate, hărți cu un singur canal decodate, mesh-uri distructibile etichetate în piesele și extra-urile lor, mesh-uri de blockout, cinematice și de iluminare lăsate afară și o structură de hartă de culoare necitită, hărți de decupare și materialele lor mascate, materiale PNG cu două fețe; instalat: decalcomaniile de teren ale nivelului, catalogul celui mai mare nivel, mesh-urile în limitele lor, membrii de grup, vegetația care stă pe terenul decodat |
| `test_vpk.py` | directorul, refuzuri, arhive împărțite; instalat: hărțile se deschid, CRC-urile se potrivesc, plasa de navigare |
| `test_enfusion.py` | `.pak` Enfusion, `.edds`, dale de teren și fișiere de lume; exportul `enfusion-world` |
| `test_forzacars.py` | fișierul `.h3dcars` pe care îl scrie comanda `cars` |
| `test_unreallevel.py` | landscape-uri Unreal 5, structuri HLOD, apă; exportul `ue-map` |

## Testele pe jocurile instalate {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
găsește jocuri pentru teste. `steam_common()` listează `steamapps\common` din fiecare bibliotecă Steam (inclusiv folderele proprii ale Steam), iar `installed(*globs)` întoarce căile care se potrivesc cu oricare glob de sub ele, recursiv acolo unde un glob are `**`. Fiecare test decide ce are nevoie:

| Test | Caută | Sare cu |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` cu un index **necriptat**, până la 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` în `*/*_Data` sau `*/*/*_Data` pe care cititorul le acceptă, până la 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, până la 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | cursurile din biblioteca de tururi FH Companion (start și sosire la 50 m), cu cele mai multe tururi, pe care le plasează `find_track`; sau `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Rulați doar testele unui singur joc sau îndreptați testul de borduri Forza spre un circuit:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Testele pe jocurile instalate citesc doar din jocuri. Nu scriu nimic în folderele jocurilor. Ieșirile testelor merg în folderele temporare ale pytest.

## Convenții {#conventions}

- **Refuză în loc să ghicească.** Fiecare cititor ridică propria excepție (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...), cu un mesaj care spune ce s-a găsit și de ce nu a fost citit.
- **Verifică față de formatul însuși.** Un hash, un CRC, un lanț de decalaje, o casetă de încadrare stocată, drumul întins pe sol. Nu „nu s-a blocat”.
- **Fără chei, fără cod proprietar inclus.** Vezi [Reguli și licențe](rules-and-licences.md).
- **Datele confidențiale rămân afară.** Fișierele de joc, exporturile, tururile, înregistrările și capturile de ecran nu intră niciodată în depozit. `.gitignore` le exclude după folder și după tip. Testele folosesc date sintetice și jocuri instalate, niciodată conținut de joc pus în depozit.
