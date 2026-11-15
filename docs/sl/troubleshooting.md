---
title: "Odpravljanje težav"
nav_order: 11
lang: "sl"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Odpravljanje težav {#troubleshooting}

Sporočila, ki jih orodje izpiše, ko kaj ustavi, kaj pomeni vsako in kaj storiti. Sporočila so citirana iz kode, z zamenjavami v oglatih oklepajih.

## Preden se orodje sploh zažene {#before-the-tool-even-starts}

| Vidite | Kaj storiti |
|---|---|
| `'python' is not recognized` | namestite Python 3.10 ali novejši in obkljukajte "Add python.exe to PATH"; odprite nov terminal ([Preden začnete](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminal je v napačni mapi: z `cd` pojdite v mapo z `README.md` |
| `No module named numpy` (ali drug paket) | zaženite `pip install -r requirements.txt` |
| pot s presledki je odrezana ali `unrecognized arguments` | postavite pot v dvojne narekovaje: `"C:\My Games\lap.json"` |

## Iskanje igre {#finding-the-game}

| Sporočilo | Pomen | Kaj storiti |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | nobena knjižnica Steam ali `C:\XboxGames` nima igre z `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | koordinate kroga niso na nobeni nameščeni progi | preverite, da je krog iz te igre; podajte `--track`, če je proga drugje |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | ploščice obstajajo blizu škatle, vendar nobena ne pokrije vožnje v pasu | enako kot zgoraj |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | mapa nima `.utoc`, ki bi se odprl | usmerite `--install` na mapo z datotekami `.utoc` |

## Iskanje kraja {#finding-the-place}

| Sporočilo | Pomen | Kaj storiti |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: noben nivo ni dosegel 30 % | `--level <name>`; preverite, da je krog v koordinatnem sistemu pregledovalnika |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` se ni ujemal | uporabite eno od naštetih imen map |
| `<level> has no scene (no main/*.level.json and no .mis)` | mapa nivoja nima scenskih datotek | pokvarjen ali nepopoln nivo ali mod |
| `no terrain of <level> lies along the driving.` | BeamNG: koridor nima kvadratov terena | napačen nivo ali nivo brez terena tam, kjer je krog |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: nobena etapa in koordinatni sistem nista dosegla 50 % | `--level <stage>`; preverite, da so položaji kroga v metrih z y navzgor |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` se ni ujemal | uporabite eno od naštetih imen |
| `no ground of <stage> lies along the driving.` | AC Rally: v koridorju ni talne ploščice | napačna etapa |

## Krog {#the-lap}

| Sporočilo | Kaj storiti |
|---|---|
| `<file> is not a lap this can read. ...` | podajte podprto obliko, glejte [Vhodi za krog](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON ni krog |
| `<file> has no x, y and z columns` | poimenujte stolpce CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | preverite ime ali podajte datoteko |
| `'<name>' matches 3 courses: ...` | uporabite daljši del imena |
| `<name> holds no driving` | krog ima manj kot dva vzorca |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` potrebuje JSON poti z `bounds`, kot ga zapišeta `heat3d_capture route` in `laps`; datoteka kroga je za `course` |
| `give exactly one of --box and --route` | `terrain` potrebuje eno območje |
| `no course export for this lap: <reason>.` | igra ni podprta, glejte [Meje in znane vrzeli](limits-and-known-gaps.md) |

## Arhivi {#archives}

| Sporočilo | Pomen |
|---|---|
| `no Oodle library found. ...` | nastavite `HEAT3D_OODLE`, glejte [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | šifriran pak: `--key <hex>`, če imate ključ. Drugega načina ni |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | ključ je 32 bajtov, zapisanih kot 64 šestnajstiških številk, `0x` ni obvezen (izhodna koda 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | ni nobeden od teh; `identify` pove, kaj je. Kontejner Unity vzame `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | šifrirani kontejner IoStore. Ne da se prebrati |
| `pak version <n>; this reader handles 8-12` | starejši ali novejši format pak |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | iz Pythona: poskusite `.utoc`, ki ga sprejmeta tudi `list` in `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | kontejner IoStore, ki ne imenuje datotek; do njegovih chunkov se pride samo prek drugih paketov |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` ob arhivu je iz druge gradnje ali drugega arhiva; brez njega se vnosi izpišejo po številki |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | imena so bila ob gradnji zgoščena |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | tabela Frostbite v zakriti obliki |
| `no Frostbite game found in a Steam library; give --install` | `levels` ali `level` nista našla igre Steam, katere `Data` ima `layout.toc`; podajte mapo igre |
| `no level called '<name>'; did you mean one of ...?` | ime se ni ujemalo z nobeno tabelo nivoja ali se je ujemalo z več; `levels` jih izpiše |
| `nothing was placed: no static model group was recognised` | člani skupin nivoja imajo drugačen podpis tipa, po posodobitvi igre ali v drugi igri Frostbite; postavitev je treba znova izmeriti |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | stisnjen mesh Unity |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | ohranite `.resS` ob `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | starejša gradnja Unity |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` vzame goli kontejner |
| `texture format <n> has not been identified; refusing to guess` | format vzorca Forze, še ni viden |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | ohranite dele razdeljenega VPK skupaj |

## Izvozi, ki pridejo narobe {#exports-that-come-out-wrong}

| Simptom | Verjeten vzrok |
|---|---|
| proga je v pregledovalniku zamaknjena od kroga | krog in izvoz uporabljata različna koordinatna sistema: preveri `--game` (na primer krog BeamNG, prebran kot Forza) |
| v progi Forze ni bankine | `--no-textures` ali ploščica nima map za izbrani `--season` (konzola pove `N without maps`) |
| ploščica Forze v enobarvnih ploskvah | njene talne mape manjkajo za letni čas |
| veliko manj postavljenih predmetov, kot pričakujete | eksplicitni `--detail-budget` je premajhen; povzetek pove, koliko kopij je bilo izpuščenih |
| datoteka je zelo velika (sto MB) | mestni koridor pod samodejnim proračunom; uporabite `--detail-budget`, `--texture-size 1024` ali `--margin 40` |
| manjkajo ograje | prosojne površine so namerno izpuščene (povzetek jih imenuje) |
| `N meshes could not be read` | nekateri modeli uporabljajo format, ki ga bralnik zavrne; ostalo se vseeno izvozi |
| `N of M components could not be read` (AC Rally) | posodobitev igre je morda premaknila reže lastnosti; prijavite to |
