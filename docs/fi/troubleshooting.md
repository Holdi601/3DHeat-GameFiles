---
title: Vianetsintä
nav_order: 11
lang: "fi"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Vianetsintä {#troubleshooting}

Viestit, jotka työkalu tulostaa, kun jokin pysäyttää sen, mitä ne tarkoittavat ja mitä tehdä. Viestit
on lainattu koodista, paikkamerkit kulmasulkeissa.

## Ennen kuin työkalu edes käynnistyy {#before-the-tool-even-starts}

| Näet | Tee |
|---|---|
| `'python' is not recognized` | asenna Python 3.10 tai uudempi ja valitse "Add python.exe to PATH"; avaa uusi terminaali ([Ennen aloittamista](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminaali on väärässä kansiossa: `cd` kansioon, jossa on `README.md` |
| `No module named numpy` (tai muu paketti) | aja `pip install -r requirements.txt` |
| polku välilyönneillä katkeaa, tai `unrecognized arguments` | laita polku lainausmerkkeihin: `"C:\My Games\lap.json"` |

## Pelin löytäminen {#finding-the-game}

| Viesti | Merkitys | Tee |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | yhdessäkään Steam-kirjastossa tai `C:\XboxGames`-kansiossa ei ole peliä, jossa on `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | kierroksen koordinaatit eivät ole millään asennetulla radalla | tarkista, että kierros on tästä pelistä; anna `--track`, jos rata on muualla |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | laattoja on lähellä laatikkoa, mutta ei yhtään käytävässä | kuten yllä |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | kansiossa ei ole `.utoc`-tiedostoa, joka aukeaa | osoita `--install` kansioon, jossa `.utoc`-tiedostot ovat |

## Paikan löytäminen {#finding-the-place}

| Viesti | Merkitys | Tee |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: yksikään taso ei saanut 30 %:a | `--level <name>`; tarkista, että kierros on katseluohjelman koordinaatistossa |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` ei täsmännyt | käytä yhtä listatuista kansion nimistä |
| `<level> has no scene (no main/*.level.json and no .mis)` | tason kansiossa ei ole kohtaustiedostoja | rikkinäinen tai osittainen taso tai modi |
| `no terrain of <level> lies along the driving.` | BeamNG: käytävässä ei ole maastoruutuja | väärä taso, tai taso ilman maastoa siinä, missä kierros on |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: yksikään vaihe ja kehys ei saanut 50 %:a | `--level <stage>`; tarkista, että kierroksen sijainnit ovat metrejä ja y ylös |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` ei täsmännyt | käytä yhtä listatuista nimistä |
| `no ground of <stage> lies along the driving.` | AC Rally: käytävässä ei ole maalaattaa | väärä vaihe |

## Kierros {#the-lap}

| Viesti | Tee |
|---|---|
| `<file> is not a lap this can read. ...` | anna tuettu muoto, katso [Kierrosten syötteet](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON ei ole kierros |
| `<file> has no x, y and z columns` | nimeä CSV-sarakkeet `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | tarkista nimi, tai anna tiedosto |
| `'<name>' matches 3 courses: ...` | käytä pidempää osaa nimestä |
| `<name> holds no driving` | kierroksessa on alle kaksi näytettä |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` tarvitsee reitti-JSON-tiedoston, jossa on `bounds`, kuten `heat3d_capture route` ja `laps` kirjoittavat; kierrostiedosto on `course`-komennolle |
| `give exactly one of --box and --route` | `terrain` tarvitsee yhden alueen |
| `no course export for this lap: <reason>.` | peliä ei tueta, katso [Rajoitukset ja tunnetut puutteet](limits-and-known-gaps.md) |

## Arkistot {#archives}

| Viesti | Merkitys |
|---|---|
| `no Oodle library found. ...` | aseta `HEAT3D_OODLE`, katso [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | salattu pak: `--key <hex>`, jos sinulla on avain. Muuta tapaa ei ole |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | avain on 32 tavua kirjoitettuna 64 heksadesimaalina, `0x` valinnainen (poistumiskoodi 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | se ei ole mikään näistä; `identify` kertoo, mikä se on. Unity-kontti vaatii `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | salattu IoStore-kontti. Sitä ei voi lukea |
| `pak version <n>; this reader handles 8-12` | vanhempi tai uudempi pak-muoto |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | Pythonista: kokeile `.utoc`-tiedostoa, jonka `list` ja `extract` myös ottavat |
| `<file> has no directory index, so its chunks carry no names to list` | IoStore-kontti, joka ei nimeä tiedostoja; sen palat tavoitetaan vain muiden pakettien kautta |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt`-tiedosto arkiston vieressä on toisesta buildista tai toisesta arkistosta; ilman sitä merkinnät listautuvat numeroina |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | nimet hashattiin pois rakennusvaiheessa |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | Frostbite-taulukko hämärretyssä muodossa |
| `no Frostbite game found in a Steam library; give --install` | `levels` tai `level` ei löytänyt Steam-peliä, jonka `Data`-kansiossa on `layout.toc`; anna pelin kansio |
| `no level called '<name>'; did you mean one of ...?` | nimi ei täsmännyt yhdenkään kentän taulukkoon, tai täsmäsi useampaan; `levels` listaa ne |
| `nothing was placed: no static model group was recognised` | kentän ryhmän jäsenillä on eri tyyppisignatuuri, pelipäivityksen jälkeen tai toisessa Frostbite-pelissä; asettelu on mitattava uudelleen |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | pakattu Unity-malli |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | pidä `.resS` `.assets`-tiedoston vieressä |
| `<file>: format <n> predates Unity 2020 ...` | vanhempi Unity-build |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` ottaa paljaan kontin |
| `texture format <n> has not been identified; refusing to guess` | Forza-näytemuotoa ei ole vielä nähty |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | pidä jaetun VPK:n osat yhdessä |

## Viennit, jotka tulevat väärin {#exports-that-come-out-wrong}

| Oire | Todennäköinen syy |
|---|---|
| rata on siirtynyt kierroksesta katseluohjelmassa | kierros ja vienti käyttävät eri koordinaatistoja: tarkista `--game` (esimerkiksi BeamNG-kierros luettuna Forzana) |
| Forza-radalla ei ole reunaa | `--no-textures`, tai laatalla ei ollut karttoja tälle `--season`-arvolle (konsoli sanoo `N without maps`) |
| Forza-laatta tasaisin värein | sen maakartat puuttuvat vuodenajalle |
| sijoitettuja objekteja on paljon vähemmän kuin odotettiin | eksplisiittinen `--detail-budget` on liian pieni; yhteenveto kertoo, kuinka monta kopiota jätettiin pois |
| tiedosto on erittäin suuri (satoja megatavuja) | kaupunkikäytävä automaattisella budjetilla; käytä `--detail-budget`-valintaa, `--texture-size 1024`-valintaa tai `--margin 40`-valintaa |
| aidat puuttuvat | läpinäkyvät pinnat jätetään pois tarkoituksella (yhteenveto nimeää ne) |
| `N meshes could not be read` | jotkin mallit ovat muodossa, jonka lukija hylkää; loput viedään silti |
| `N of M components could not be read` (AC Rally) | pelipäivitys on ehkä siirtänyt ominaisuuspaikkoja; ilmoita siitä |
