---
title: Hibaelhárítás
nav_order: 11
lang: "hu"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Hibaelhárítás {#troubleshooting}

Az üzenetek, amelyeket az eszköz kiír, amikor megáll, mit jelentenek, és mit tegyél. Az üzenetek a kódból
származnak, a zárójeles helyőrzők szögletes zárójelben vannak.

## Mielőtt az eszköz elindulna {#before-the-tool-even-starts}

| Amit látsz | Tedd |
|---|---|
| `'python' is not recognized` | telepítsd a Python 3.10 vagy újabb verzióját, és pipáld be az „Add python.exe to PATH" lehetőséget; nyiss új terminált ([Mielőtt elkezdenéd](before-you-start.md)) |
| `No module named heat3d_gamefiles` | a terminál rossz mappában van: menj (`cd`) a `README.md`-t tartalmazó mappába |
| `No module named numpy` (vagy más csomag) | futtasd: `pip install -r requirements.txt` |
| egy szóközös útvonal le van vágva, vagy `unrecognized arguments` | tedd az útvonalat idézőjelbe: `"C:\My Games\lap.json"` |

## A játék megtalálása {#finding-the-game}

| Üzenet | Jelentés | Tedd |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | egyik Steam-könyvtár vagy a `C:\XboxGames` sem tartalmaz `media\Tracks`-et tartalmazó játékot | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | a kör koordinátái nincsenek egyik telepített pályán sem | ellenőrizd, hogy a kör ettől a játéktól való; adj meg `--track`-et, ha a pálya máshol van |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | a doboz közelében vannak csempék, de egyik sem fedi a vezetést a sávban | ahogy fent |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | a mappában nincs olyan `.utoc`, amely megnyílna | mutass a `--install`-lal arra a mappára, amelyben a `.utoc` fájlok vannak |

## A hely megtalálása {#finding-the-place}

| Üzenet | Jelentés | Tedd |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: egyik pálya sem ért el 30%-ot | `--level <name>`; ellenőrizd, hogy a kör a nézegető keretében van |
| `no level called '<name>'; installed: ...` | BeamNG: a `--level` nem egyezett | használj egyet a felsorolt mappanevek közül |
| `<level> has no scene (no main/*.level.json and no .mis)` | a pályamappában nincsenek jelenetfájlok | sérült vagy hiányos pálya vagy mod |
| `no terrain of <level> lies along the driving.` | BeamNG: a sávban nincsenek terepnégyzetek | rossz pálya, vagy olyan pálya, amelynek ott nincs terepe, ahol a kör van |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: egyik szakasz és keret sem ért el 50%-ot | `--level <stage>`; ellenőrizd, hogy a kör pozíciói méterben vannak, y felfelé |
| `no stage called '<name>'; there are: ...` | AC Rally: a `--level` nem egyezett | használj egy felsorolt nevet |
| `no ground of <stage> lies along the driving.` | AC Rally: nincs talajcsempe a sávban | rossz szakasz |

## A kör {#the-lap}

| Üzenet | Tedd |
|---|---|
| `<file> is not a lap this can read. ...` | adj támogatott alakot, lásd: [Körfájl-bemenetek](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | a JSON nem kör |
| `<file> has no x, y and z columns` | nevezd el a CSV oszlopait `x`, `y`, `z`-nek |
| `'<name>' is not a file, and no course in <library> matches it` | ellenőrizd a nevet, vagy adj meg fájlt |
| `'<name>' matches 3 courses: ...` | használj a névnek hosszabb részét |
| `<name> holds no driving` | a körnek két mintánál kevesebb van |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | a `terrain --route`-nak `bounds`-os útvonal-JSON kell, ahogy a `heat3d_capture route` és `laps` írja; a körfájl a `course`-nak való |
| `give exactly one of --box and --route` | a `terrain`-nek egy régió kell |
| `no course export for this lap: <reason>.` | a játék nem támogatott, lásd: [Korlátok és ismert hiányosságok](limits-and-known-gaps.md) |

## Archívumok {#archives}

| Üzenet | Jelentés |
|---|---|
| `no Oodle library found. ...` | állítsd be a `HEAT3D_OODLE`-t, lásd: [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | titkosított pak: `--key <hex>`, ha megvan a kulcs. Más mód nincs |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | a kulcs 32 bájt, 64 hexadecimális számjegyként írva, `0x` opcionális (2-es kilépési kód) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | egyik sem; az `identify` megmondja, mi |
| `<file> is encrypted. This tool holds no keys and recovers none.` | titkosított IoStore-konténer. Nem olvasható |
| `pak version <n>; this reader handles 8-12` | régebbi vagy újabb pak-formátum |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | Pythonból: próbáld a `.utoc`-ot, amelyet a `list` és `extract` is elfogad |
| `<file> has no directory index, so its chunks carry no names to list` | olyan IoStore-konténer, amely nem nevez meg fájlokat; darabjait csak más csomagokon át érjük el |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | az archívum melletti `ChunkContentsMiniZip<n>.txt` másik buildből vagy másik archívumból való; nélküle a bejegyzések számmal listázódnak |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | a neveket az építéskor hash-elték el |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | egy Frostbite-tábla elrejtett formában |
| `no Frostbite game found in a Steam library; give --install` | a `levels` vagy `level` nem talált olyan Steam-játékot, amelynek `Data` mappájában van `layout.toc`; add meg a játék mappáját |
| `no level called '<name>'; did you mean one of ...?` | a név nem egyezett egyik pálya táblájával sem, vagy több egyezett; a `levels` felsorolja őket |
| `nothing was placed: no static model group was recognised` | a pálya csoporttagjainak típusa más, egy játékfrissítés után vagy más Frostbite-játékban; az elrendezést újra kell mérni |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | egy tömörített Unity-háló |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | tartsd a `.resS`-t az `.assets` mellett |
| `<file>: format <n> predates Unity 2020 ...` | régebbi Unity-build |
| `<file> is an asset bundle, not a bare SerializedFile` | a `meshes` önálló konténert vár |
| `texture format <n> has not been identified; refusing to guess` | egy eddig nem látott Forza-mintakártya-formátum |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | a szétdarabolt VPK részeit tartsd együtt |

## Az export rossz kimenete {#exports-that-come-out-wrong}

| Tünet | Valószínű ok |
|---|---|
| a pálya el van tolva a körtől a nézegetőben | a kör és az export másik keretet használ: ellenőrizd a `--game`-et (egy BeamNG-kör Forzaként olvasva, például) |
| nincs padka egy Forza-pályán | `--no-textures`, vagy a csempének nem volt térképe az adott `--season`-hoz (a konzol `N without maps`-et ír) |
| egy Forza-csempe egyszínű | a talajtérképei hiányoznak az évszakhoz |
| sokkal kevesebb elhelyezett tárgy, mint vártad | egy megadott `--detail-budget` túl kicsi; az összefoglaló megmondja, hány példány maradt ki |
| a fájl nagyon nagy (több száz MB) | városi sáv az automatikus kerettel; használd a `--detail-budget`-et, `--texture-size 1024`-et vagy `--margin 40`-et |
| hiányzó kerítések | az áttetsző felületek szándékosan kimaradnak (az összefoglaló megnevezi őket) |
| `N meshes could not be read` | néhány modell olyan formátumot használ, amelyet az olvasó megtagad; a többi exportálódik |
| `N of M components could not be read` (AC Rally) | egy játékfoltozás elmozdíthatta a tulajdonsági rekeszeket; kérjük, jelezd |
