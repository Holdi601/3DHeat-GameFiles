---
title: "Depanare"
nav_order: 11
lang: "ro"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Depanare {#troubleshooting}

Mesajele pe care le afișează instrumentul când ceva îl oprește, ce înseamnă fiecare și ce de făcut. Mesajele sunt citate din cod, cu semnele dintre paranteze unghiulare ca locuri de completat. Mesajele din cod rămân în engleză, exact ca în program.

## Înainte ca instrumentul să pornească {#before-the-tool-even-starts}

| Vedeți | Faceți |
|---|---|
| `'python' is not recognized` | instalați Python 3.10 sau mai nou și bifați „Add python.exe to PATH”; deschideți un terminal nou ([Înainte de a începe](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminalul este în folderul greșit: faceți `cd` în folderul cu `README.md` |
| `No module named numpy` (sau alt pachet) | rulați `pip install -r requirements.txt` |
| o cale cu spații este tăiată, sau `unrecognized arguments` | puneți calea între ghilimele duble: `"C:\My Games\lap.json"` |

## Găsirea jocului {#finding-the-game}

| Mesaj | Înseamnă | Faceți |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | nicio bibliotecă Steam și nicio `C:\XboxGames` nu conține un joc cu `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | coordonatele turului nu se află pe niciun traseu instalat | verificați că turul este din acest joc; dați `--track` dacă traseul este în altă parte |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | există dale în apropiere, dar niciuna nu acoperă parcursul din fâșie | la fel ca mai sus |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | folderul nu are niciun `.utoc` care să se deschidă | indicați `--install` spre folderul cu fișierele `.utoc` |

## Găsirea locului {#finding-the-place}

| Mesaj | Înseamnă | Faceți |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: niciun nivel nu a obținut 30% | `--level <name>`; verificați că turul este în cadrul vizualizatorului |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` nu s-a potrivit | folosiți unul dintre numele de folder listate |
| `<level> has no scene (no main/*.level.json and no .mis)` | folderul nivelului nu are fișiere de scenă | un nivel sau un mod defect ori incomplet |
| `no terrain of <level> lies along the driving.` | BeamNG: fâșia nu are pătrate de teren | nivel greșit, sau un nivel fără teren acolo unde este turul |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: nicio etapă și niciun cadru nu au obținut 50% | `--level <stage>`; verificați că pozițiile turului sunt în metri, cu y în sus |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` nu s-a potrivit | folosiți unul dintre numele listate |
| `no ground of <stage> lies along the driving.` | AC Rally: niciun pătrat de sol în fâșie | etapă greșită |

## Turul {#the-lap}

| Mesaj | Faceți |
|---|---|
| `<file> is not a lap this can read. ...` | dați o formă acceptată, vezi [Intrările de tur](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON-ul nu este un tur |
| `<file> has no x, y and z columns` | numiți coloanele CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | verificați numele sau dați un fișier |
| `'<name>' matches 3 courses: ...` | folosiți o parte mai lungă a numelui |
| `<name> holds no driving` | turul are mai puțin de două eșantioane |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` are nevoie de un JSON de traseu cu `bounds`, cum îl scriu `heat3d_capture route` și `laps`; un fișier de tur este pentru `course` |
| `give exactly one of --box and --route` | `terrain` are nevoie de o singură regiune |
| `no course export for this lap: <reason>.` | jocul nu este acceptat, vezi [Limite și lacune cunoscute](limits-and-known-gaps.md) |

## Arhive {#archives}

| Mesaj | Înseamnă |
|---|---|
| `no Oodle library found. ...` | setați `HEAT3D_OODLE`, vezi [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | un pak criptat: `--key <hex>` dacă aveți cheia. Nu există altă cale |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | cheia are 32 de octeți scriși ca 64 de cifre hexazecimale, `0x` opțional (codul de ieșire 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | nu este niciuna dintre acestea; `identify` spune ce este. Un container Unity se citește cu `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | un container IoStore criptat. Nu poate fi citit |
| `pak version <n>; this reader handles 8-12` | un format de pak mai vechi sau mai nou |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | din Python: încercați `.utoc`, pe care îl iau și `list` și `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | un container IoStore care nu numește fișiere; bucățile lui se ating doar prin alte pachete |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` de lângă arhivă este dintr-un alt build sau dintr-o altă arhivă; fără el, intrările se listează după număr |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | numele au fost ascunse prin hash la compilare |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | un tabel Frostbite în forma obfuscată |
| `no Frostbite game found in a Steam library; give --install` | `levels` sau `level` nu au găsit un joc Steam al cărui `Data` să conțină un `layout.toc`; indicați folderul jocului |
| `no level called '<name>'; did you mean one of ...?` | numele nu se potrivește cu tabelul niciunui nivel sau se potrivește cu mai multe; `levels` le listează |
| `nothing was placed: no static model group was recognised` | membrii grupurilor nivelului au o altă semnătură de tip, după o actualizare a jocului sau într-un alt joc Frostbite; layout-ul trebuie măsurat din nou |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | un mesh Unity comprimat |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | păstrați `.resS` lângă `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | un build Unity mai vechi |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` ia un container simplu |
| `texture format <n> has not been identified; refusing to guess` | un format de mostră Forza nevăzut până acum |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | păstrați împreună piesele unui VPK împărțit |

## Exporturi care ies greșit {#exports-that-come-out-wrong}

| Simptom | Cauza probabilă |
|---|---|
| circuitul este decalat față de tur în vizualizator | turul și exportul folosesc cadre diferite: verificați `--game` (un tur BeamNG citit ca Forza, de exemplu) |
| niciun acostament într-un circuit Forza | `--no-textures`, sau dala nu avea hărți pentru `--season` ales (consola afișează `N without maps`) |
| o dală Forza în culori uniforme | hărțile ei de sol lipsesc pentru sezon |
| mult mai puține obiecte plasate decât se aștepta | un `--detail-budget` dat explicit prea mic; sumarul spune câte copii au fost lăsate afară |
| fișierul este foarte mare (sute de MB) | un coridor urban sub bugetul automat; folosiți `--detail-budget`, `--texture-size 1024` sau `--margin 40` |
| garduri lipsă | suprafețele transparente sunt lăsate afară intenționat (sumarul le numește) |
| `N meshes could not be read` | unele modele folosesc un format pe care cititorul îl refuză; restul se exportă oricum |
| `N of M components could not be read` (AC Rally) | o actualizare a jocului poate fi mutat sloturile proprietăților; vă rugăm să raportați |
