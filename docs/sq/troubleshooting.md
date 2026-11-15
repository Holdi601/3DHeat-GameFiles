---
title: "Zgjidhja e problemeve"
nav_order: 11
lang: "sq"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Zgjidhja e problemeve {#troubleshooting}

Mesazhet që printon mjeti kur diçka e ndalon, çfarë do të thotë secili, dhe çfarë
të bësh. Mesazhet citohen nga kodi, me vendmbajtës në kllapa këndore.

## Para se të nisë fare mjeti {#before-the-tool-even-starts}

| Shikon | Bëj |
|---|---|
| `'python' is not recognized` | instalo Python 3.10 ose më të ri dhe shëno "Add python.exe to PATH"; hap një terminal të ri ([Para se të fillosh](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminali është në dosjen e gabuar: bëj `cd` te dosja me `README.md` |
| `No module named numpy` (ose një paketë tjetër) | ekzekuto `pip install -r requirements.txt` |
| një shteg me hapësira pritet, ose `unrecognized arguments` | vëre shtegun në thonjëza të dyfishta: `"C:\My Games\lap.json"` |

## Gjetja e lojës {#finding-the-game}

| Mesazhi | Kuptimi | Bëj |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | asnjë bibliotekë Steam ose `C:\XboxGames` nuk mban lojë me `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | koordinatat e xhiros nuk janë mbi asnjë pistë të instaluar | kontrollo që xhiroja është nga kjo lojë; jep `--track` nëse pista është diku tjetër |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | pllakat ekzistojnë pranë kutisë por asnjë në korridor | si më sipër |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | dosja nuk ka `.utoc` që hapet | drejto `--install` te dosja me skedarët `.utoc` |

## Gjetja e vendit {#finding-the-place}

| Mesazhi | Kuptimi | Bëj |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: asnjë nivel nuk mori 30% | `--level <name>`; kontrollo që xhiroja është në kornizën e shikuesit |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` nuk përputhej | përdor një nga emrat e dosjeve të listuara |
| `<level> has no scene (no main/*.level.json and no .mis)` | dosja e nivelit nuk ka skedarë skene | një nivel ose mod i prishur ose i paplotë |
| `no terrain of <level> lies along the driving.` | BeamNG: korridori nuk ka katrorë terreni | nivel i gabuar, ose një nivel pa terren aty ku është xhiroja |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: asnjë etapë dhe kornizë nuk mori 50% | `--level <stage>`; kontrollo që pozicionet e xhiros janë metra me y lart |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` nuk përputhej | përdor një nga emrat e listuar |
| `no ground of <stage> lies along the driving.` | AC Rally: asnjë pllakë toke në korridor | etapë e gabuar |

## Xhiroja {#the-lap}

| Mesazhi | Bëj |
|---|---|
| `<file> is not a lap this can read. ...` | jepi një formë të mbështetur, shih [Hyrjet e xhiros](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON nuk është xhiro |
| `<file> has no x, y and z columns` | emërtoji kolonat e CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | kontrollo emrin, ose jep një skedar |
| `'<name>' matches 3 courses: ...` | përdor një pjesë më të gjatë të emrit |
| `<name> holds no driving` | xhiroja ka më pak se dy mostra |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` ka nevojë për një JSON rruge me `bounds`, siç e shkruajnë `heat3d_capture route` dhe `laps`; një skedar xhiroje është për `course` |
| `give exactly one of --box and --route` | `terrain` ka nevojë për një zonë |
| `no course export for this lap: <reason>.` | loja nuk mbështetet, shih [Kufijtë dhe boshllëqet e njohura](limits-and-known-gaps.md) |

## Arkivat {#archives}

| Mesazhi | Kuptimi |
|---|---|
| `no Oodle library found. ...` | cakto `HEAT3D_OODLE`, shih [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | një pak i enkriptuar: `--key <hex>` nëse e ke çelësin. Nuk ka mënyrë tjetër |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | çelësi është 32 bajte të shkruara si 64 shifra heksadecimale, `0x` opsional (kodi i daljes 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | nuk është asnjë prej tyre; `identify` thotë çfarë është. Një kontejner Unity merr `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | një kontejner IoStore i enkriptuar. Nuk mund të lexohet |
| `pak version <n>; this reader handles 8-12` | një format pak më i vjetër ose më i ri |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | nga Python: provo `.utoc`, që e pranojnë edhe `list` dhe `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | një kontejner IoStore që nuk emërton skedarë; copat e tij arrihen vetëm përmes paketave të tjera |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` pranë arkivit është nga një ndërtim tjetër ose arkiv tjetër; pa të hyrjet listohen sipas numrit |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | emrat u hashuan gjatë ndërtimit |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | një tabelë Frostbite në formën e turbulluar |
| `no Frostbite game found in a Steam library; give --install` | `levels` ose `level` nuk gjeti lojë Steam që `Data` e saj mban një `layout.toc`; jep dosjen e lojës |
| `no level called '<name>'; did you mean one of ...?` | emri nuk përputhej me tabelën e asnjë niveli, ose me disa; `levels` i liston |
| `nothing was placed: no static model group was recognised` | anëtarët e grupeve të nivelit kanë një nënshkrim tjetër lloji, pas një përditësimi loje ose në një lojë tjetër Frostbite; struktura duhet matur përsëri |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | një rrjetë Unity e kompresuar |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | mbaje `.resS` pranë `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | një ndërtim Unity më i vjetër |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` merr një kontejner të zhveshur |
| `texture format <n> has not been identified; refusing to guess` | një format mostre Forza ende i pashikuar |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | mbaji bashkë pjesët e një VPK të ndarë |

## Eksportet që dalin gabim {#exports-that-come-out-wrong}

| Simptoma | Shkaku i mundshëm |
|---|---|
| kursi është i zhvendosur nga xhiroja në shikues | xhiroja dhe eksporti përdorin korniza të ndryshme: kontrollo `--game` (një xhiro BeamNG e lexuar si Forza, për shembull) |
| pa buzë në një kurs Forza | `--no-textures`, ose pllaka nuk kishte harta për atë `--season` (konsola thotë `N without maps`) |
| një pllakë Forza me ngjyra të sheshta | hartat e tokës së saj mungojnë për stinën |
| shumë më pak objekte të vendosura se sa pritej | një `--detail-budget` i qartë shumë i vogël; përmbledhja thotë sa kopje u lanë jashtë |
| skedari është shumë i madh (qindra MB) | një korridor qyteti nën buxhetin automatik; përdor `--detail-budget`, `--texture-size 1024`, ose `--margin 40` |
| mungojnë gardhet | sipërfaqet transparente lihen jashtë me qëllim (përmbledhja i emërton) |
| `N meshes could not be read` | disa modele përdorin një format që lexuesi e refuzon; pjesa tjetër eksportohet prapë |
| `N of M components could not be read` (AC Rally) | një përditësim loje mund t'i ketë lëvizur vendet e vetive; të lutem raportoje |
