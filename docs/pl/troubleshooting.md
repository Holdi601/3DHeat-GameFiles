---
title: Rozwiązywanie problemów
nav_order: 11
lang: "pl"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Rozwiązywanie problemów {#troubleshooting}

Komunikaty, które narzędzie wypisuje, gdy coś je zatrzymuje, co każdy znaczy i co zrobić. Komunikaty są cytowane z kodu, z symbolami w nawiasach ostrych jako miejscami na wartości.

## Zanim narzędzie w ogóle ruszy {#before-the-tool-even-starts}

| Widzisz | Zrób |
|---|---|
| `'python' is not recognized` | zainstaluj Python 3.10 lub nowszy i zaznacz "Add python.exe to PATH"; otwórz nowy terminal ([Zanim zaczniesz](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminal jest w złym folderze: przejdź (`cd`) do folderu z `README.md` |
| `No module named numpy` (albo inny pakiet) | uruchom `pip install -r requirements.txt` |
| ścieżka ze spacjami jest ucięta albo `unrecognized arguments` | ujmij ścieżkę w cudzysłowy: `"C:\My Games\lap.json"` |

## Znajdowanie gry {#finding-the-game}

| Komunikat | Znaczenie | Zrób |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | żadna biblioteka Steam ani `C:\XboxGames` nie ma gry z `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | współrzędne okrążenia nie leżą na żadnym zainstalowanym torze | sprawdź, czy okrążenie pochodzi z tej gry; podaj `--track`, jeśli tor leży gdzie indziej |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | kafelki są w pobliżu pudełka, ale żaden nie pokrywa jazdy w korytarzu | jak wyżej |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | folder nie ma `.utoc`, który by się otworzył | wskaż `--install` na folder z plikami `.utoc` |

## Znajdowanie miejsca {#finding-the-place}

| Komunikat | Znaczenie | Zrób |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: żaden poziom nie uzyskał 30% | `--level <name>`; sprawdź, czy okrążenie jest w ramce przeglądarki |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` nie pasuje do niczego | użyj jednej z wymienionych nazw folderów |
| `<level> has no scene (no main/*.level.json and no .mis)` | folder poziomu nie ma plików sceny | uszkodzony albo niepełny poziom lub mod |
| `no terrain of <level> lies along the driving.` | BeamNG: korytarz nie ma kwadratów terenu | zły poziom albo poziom bez terenu tam, gdzie jest okrążenie |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: żaden etap i ramka nie uzyskały 50% | `--level <stage>`; sprawdź, czy pozycje okrążenia są w metrach z osią Y w górę |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` nie pasuje do niczego | użyj jednej z wymienionych nazw |
| `no ground of <stage> lies along the driving.` | AC Rally: żaden kafelek podłoża nie jest w korytarzu | zły etap |

## Okrążenie {#the-lap}

| Komunikat | Co zrobić |
|---|---|
| `<file> is not a lap this can read. ...` | podaj obsługiwany kształt, zob. [Dane okrążenia](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | ten JSON nie jest okrążeniem |
| `<file> has no x, y and z columns` | nazwij kolumny CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | sprawdź nazwę albo podaj plik |
| `'<name>' matches 3 courses: ...` | użyj dłuższej części nazwy |
| `<name> holds no driving` | okrążenie ma mniej niż dwie próbki |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` potrzebuje pliku trasy JSON z `bounds`, takiego, jak zapisują go `heat3d_capture route` i `laps`; plik okrążenia służy do `course` |
| `give exactly one of --box and --route` | `terrain` potrzebuje jednego regionu |
| `no course export for this lap: <reason>.` | gra nie jest obsługiwana, zob. [Ograniczenia i znane braki](limits-and-known-gaps.md) |

## Archiwa {#archives}

| Komunikat | Znaczenie |
|---|---|
| `no Oodle library found. ...` | ustaw `HEAT3D_OODLE`, zob. [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | zaszyfrowany pak: `--key <hex>`, jeśli masz klucz. Innej drogi nie ma |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | klucz to 32 bajty zapisane jako 64 cyfry szesnastkowe, `0x` opcjonalne (kod wyjścia 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | to żaden z nich; `identify` powie, czym jest. Kontener Unity przyjmuje `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | zaszyfrowany kontener IoStore. Nie da się go odczytać |
| `pak version <n>; this reader handles 8-12` | starszy albo nowszy format pak |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | z Pythona: spróbuj `.utoc`, który biorą też `list` i `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | kontener IoStore, który nie nazywa plików; jego chunki są dostępne tylko przez inne pakiety |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` obok archiwum pochodzi z innego builda albo innego archiwum; bez niego wpisy wyświetlą się po numerze |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | nazwy zostały zahaszowane podczas budowania |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | tabela Frostbite w zaciemnionej formie |
| `no Frostbite game found in a Steam library; give --install` | `levels` albo `level` nie znalazły gry Steam, której `Data` ma `layout.toc`; podaj folder gry |
| `no level called '<name>'; did you mean one of ...?` | nazwa nie pasuje do tabeli żadnego poziomu albo pasuje do kilku; `levels` wypisuje je wszystkie |
| `nothing was placed: no static model group was recognised` | członkowie grup poziomu mają inną sygnaturę typu, po aktualizacji gry albo w innej grze Frostbite; układ trzeba zmierzyć od nowa |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | skompresowana siatka Unity |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | trzymaj `.resS` obok `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | starszy build Unity |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` przyjmuje gołe kontenery |
| `texture format <n> has not been identified; refusing to guess` | format swatcha Forzy, którego jeszcze nie widziano |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | trzymaj części podzielonego VPK razem |

## Eksporty, które wychodzą źle {#exports-that-come-out-wrong}

| Objaw | Prawdopodobna przyczyna |
|---|---|
| trasa jest przesunięta względem okrążenia w przeglądarce | okrążenie i eksport używają różnych ramek: sprawdź `--game` (na przykład okrążenie BeamNG odczytane jako Forza) |
| brak pobocza w trasie Forzy | `--no-textures`, albo kafelek nie miał map dla danego `--season` (konsola pisze `N without maps`) |
| kafelek Forzy w jednolitych kolorach | jego mapy podłoża brakuje dla tej pory roku |
| znacznie mniej umieszczonych obiektów, niż oczekiwano | jawnie podany `--detail-budget` jest za mały; podsumowanie mówi, ile kopii pominięto |
| plik jest bardzo duży (setki MB) | miejski korytarz przy automatycznym budżecie; użyj `--detail-budget`, `--texture-size 1024` albo `--margin 40` |
| brak płotów | powierzchnie przeźroczyste są celowo pomijane (podsumowanie je wymienia) |
| `N meshes could not be read` | niektóre modele używają formatu, który czytnik odrzuca; reszta i tak się eksportuje |
| `N of M components could not be read` (AC Rally) | łatka gry mogła przesunąć sloty właściwości; zgłoś to |
