---
title: Problemen oplossen
nav_order: 11
lang: "nl"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Problemen oplossen {#troubleshooting}

De meldingen die de tool afdrukt wanneer iets hem stopt, wat elk betekent, en wat je moet doen. Meldingen zijn letterlijk uit de code overgenomen, met plaatshouders tussen punthaken.

## Voordat de tool zelfs start {#before-the-tool-even-starts}

| Je ziet | Doe dit |
|---|---|
| `'python' is not recognized` | installeer Python 3.10 of nieuwer en vink "Add python.exe to PATH" aan; open een nieuwe terminal ([Voordat je begint](before-you-start.md)) |
| `No module named heat3d_gamefiles` | de terminal staat in de verkeerde map: `cd` naar de map met `README.md` |
| `No module named numpy` (of een ander pakket) | voer `pip install -r requirements.txt` uit |
| een pad met spaties wordt afgekapt, of `unrecognized arguments` | zet het pad tussen dubbele aanhalingstekens: `"C:\My Games\lap.json"` |

## Het spel vinden {#finding-the-game}

| Melding | Betekenis | Doe dit |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | geen Steam-bibliotheek of `C:\XboxGames` bevat een spel met `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | de coördinaten van de ronde staan op geen enkele geïnstalleerde baan | controleer of de ronde uit dit spel komt; geef `--track` op als de baan elders staat |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | er zijn tegels in de buurt van de doos, maar geen die de corridor dekken | zie hierboven |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | de map heeft geen `.utoc` die opent | laat `--install` naar de map met de `.utoc`-bestanden wijzen |

## De plek vinden {#finding-the-place}

| Melding | Betekenis | Doe dit |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: geen enkel level scoorde 30% | `--level <name>`; controleer of de ronde in het stelsel van de viewer staat |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` kwam met niets overeen | gebruik een van de genoemde mapnamen |
| `<level> has no scene (no main/*.level.json and no .mis)` | de levelmap heeft geen scènebestanden | een kapot of onvolledig level, of een mod |
| `no terrain of <level> lies along the driving.` | BeamNG: de corridor heeft geen terreinvakken | verkeerd level, of een level zonder terrein waar de ronde is |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: geen enkele etappe en richting scoorde 50% | `--level <stage>`; controleer of de posities van de ronde meters zijn met y omhoog |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` kwam met niets overeen | gebruik een van de genoemde namen |
| `no ground of <stage> lies along the driving.` | AC Rally: geen grondtegel in de corridor | verkeerde etappe |

## De ronde {#the-lap}

| Melding | Doe dit |
|---|---|
| `<file> is not a lap this can read. ...` | geef een ondersteunde vorm, zie [Rondebestanden](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | de JSON is geen ronde |
| `<file> has no x, y and z columns` | noem de CSV-kolommen `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | controleer de naam, of geef een bestand op |
| `'<name>' matches 3 courses: ...` | gebruik een langer deel van de naam |
| `<name> holds no driving` | de ronde heeft minder dan twee punten |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` heeft een routes-JSON met `bounds` nodig, zoals `heat3d_capture route` en `laps` die schrijven; een rondebestand is voor `course` |
| `give exactly one of --box and --route` | `terrain` heeft precies één gebied nodig |
| `no course export for this lap: <reason>.` | het spel wordt niet ondersteund, zie [Grenzen en bekende lacunes](limits-and-known-gaps.md) |

## Archieven {#archives}

| Melding | Betekenis |
|---|---|
| `no Oodle library found. ...` | stel `HEAT3D_OODLE` in, zie [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | een versleuteld pak: `--key <hex>` als je de sleutel hebt. Er is geen andere manier |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | de sleutel is 32 bytes geschreven als 64 hexadecimale cijfers, `0x` optioneel (exitcode 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | het is geen van die; `identify` zegt wat het is. Een Unity-container gebruikt `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | een versleutelde IoStore-container. Die kan niet worden gelezen |
| `pak version <n>; this reader handles 8-12` | een oudere of nieuwere pak-indeling |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | vanuit Python: probeer de `.utoc`, die `list` en `extract` ook nemen |
| `<file> has no directory index, so its chunks carry no names to list` | een IoStore-container die geen bestanden noemt; zijn chunks worden alleen via andere pakketten bereikt |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | de `ChunkContentsMiniZip<n>.txt` ernaast komt van een andere build of een ander archief; zonder die lijst worden de items op nummer weergegeven |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | de namen zijn bij het bouwen weggehasht |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | een Frostbite-tabel in de verhulde vorm |
| `no Frostbite game found in a Steam library; give --install` | `levels` of `level` vond geen Steam-spel waarvan `Data` een `layout.toc` heeft; geef de map van het spel op |
| `no level called '<name>'; did you mean one of ...?` | de naam kwam met geen enkele leveltabel overeen, of met meerdere; `levels` toont ze |
| `nothing was placed: no static model group was recognised` | de groepsleden van het level hebben een andere typehandtekening, na een spelupdate of in een ander Frostbite-spel; de indeling moet opnieuw worden gemeten |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | een gecomprimeerde Unity-mesh |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | houd de `.resS` naast de `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | een oudere Unity-build |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` neemt een kale container |
| `texture format <n> has not been identified; refusing to guess` | een Forza-swatchformaat dat nog niet is gezien |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | houd de delen van een gesplitste VPK bij elkaar |

## Exports die verkeerd uitkomen {#exports-that-come-out-wrong}

| Symptoom | Waarschijnlijke oorzaak |
|---|---|
| de baan staat verschoven ten opzichte van de ronde in de viewer | de ronde en de export gebruiken verschillende stelsels: controleer `--game` (een BeamNG-ronde die als Forza wordt gelezen, bijvoorbeeld) |
| geen berm in een Forza-baan | `--no-textures`, of de tegel had geen kaarten voor dat `--season` (de console zegt `N without maps`) |
| een Forza-tegel in vlakke kleuren | zijn grondkaarten ontbreken voor het seizoen |
| veel minder geplaatste objecten dan verwacht | een expliciet `--detail-budget` dat te klein is; de samenvatting zegt hoeveel kopieën zijn weggelaten |
| het bestand is zeer groot (honderden MB) | een stadscorridor onder het automatische budget; gebruik `--detail-budget`, `--texture-size 1024`, of `--margin 40` |
| hekken ontbreken | doorzichtige oppervlakken worden met opzet weggelaten (de samenvatting noemt ze) |
| `N meshes could not be read` | sommige modellen gebruiken een formaat dat de lezer weigert; de rest wordt wel geëxporteerd |
| `N of M components could not be read` (AC Rally) | een patch van het spel heeft mogelijk de plekken van eigenschappen verschoven; meld het alsjeblieft |
