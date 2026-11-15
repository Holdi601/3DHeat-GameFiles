---
title: "Bilanaleit"
nav_order: 11
lang: "is"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Bilanaleit {#troubleshooting}

Skilaboðin sem verkfærið prentar þegar eitthvað stöðvar það, hvað hvert þeirra þýðir, og hvað
á að gera. Skilaboð eru vitnuð beint úr kóðanum, með staðgenglum í oddklofum.

## Áður en verkfærið byrjar yfirleitt {#before-the-tool-even-starts}

| Þú sérð | Gerðu |
|---|---|
| `'python' is not recognized` | settu upp Python 3.10 eða nýrra og hakaðu við „Add python.exe to PATH“; opnaðu nýja skipanalínu ([Áður en þú byrjar](before-you-start.md)) |
| `No module named heat3d_gamefiles` | skipanalínan er í rangri möppu: `cd` í möppuna með `README.md` |
| `No module named numpy` (eða annar pakki) | keyrðu `pip install -r requirements.txt` |
| slóð með bilum er skorin af, eða `unrecognized arguments` | settu slóðina í tvöfaldar gæsalappir: `"C:\My Games\lap.json"` |

## Að finna leikinn {#finding-the-game}

| Skilaboð | Merking | Gerðu |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | ekkert Steam-safn eða `C:\XboxGames` geymir leik með `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | hnit hringsins eru ekki á neinni uppsettri braut | athugaðu að hringurinn sé úr þessum leik; gefðu upp `--track` ef brautin er annars staðar |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | flísar eru nálægt kassanum en engar í ganginum | eins og að ofan |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | mappan hefur enga `.utoc` sem opnast | beindu `--install` að möppunni með `.utoc` skránum |

## Að finna staðinn {#finding-the-place}

| Skilaboð | Merking | Gerðu |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: ekkert borð fékk 30% | `--level <name>`; athugaðu að hringurinn sé í ásakerfi skoðarans |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` passaði ekki | notaðu eitt af listuðu möppuheitunum |
| `<level> has no scene (no main/*.level.json and no .mis)` | borðsmappan hefur engar senuskrár | bilað eða hlutaborð eða mod |
| `no terrain of <level> lies along the driving.` | BeamNG: gangurinn hefur enga landferninga | rangt borð, eða borð án lands þar sem hringurinn er |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: engin sérleið og ásakerfi fékk 50% | `--level <stage>`; athugaðu að staðsetningar hringsins séu metrar með y upp |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` passaði ekki | notaðu eitt af listuðu heitunum |
| `no ground of <stage> lies along the driving.` | AC Rally: engin jarðarflís í ganginum | röng sérleið |

## Hringurinn {#the-lap}

| Skilaboð | Gerðu |
|---|---|
| `<file> is not a lap this can read. ...` | gefðu því studda lögun, sjá [Hringinntök](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON-ið er ekki hringur |
| `<file> has no x, y and z columns` | nefndu CSV dálkana `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | athugaðu heitið, eða gefðu upp skrá |
| `'<name>' matches 3 courses: ...` | notaðu lengri hluta heitisins |
| `<name> holds no driving` | hringurinn hefur færri en tvö sýni |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` þarf leiðar-JSON með `bounds`, eins og `heat3d_capture route` og `laps` skrifa það; hringskrá er fyrir `course` |
| `give exactly one of --box and --route` | `terrain` þarf eitt svæði |
| `no course export for this lap: <reason>.` | leikurinn er ekki studdur, sjá [Takmarkanir og þekktar eyður](limits-and-known-gaps.md) |

## Skjalasöfn {#archives}

| Skilaboð | Merking |
|---|---|
| `no Oodle library found. ...` | stilltu `HEAT3D_OODLE`, sjá [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | dulkóðað pak: `--key <hex>` ef þú átt lykilinn. Engin önnur leið er til |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | lykillinn er 32 bæti skrifuð sem 64 sextándakerfis tölustafir, `0x` valkvætt (útgangskóði 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | það er ekkert af þessu; `identify` segir hvað það er. Unity ílát tekur `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | dulkóðað IoStore ílát. Það er ekki hægt að lesa |
| `pak version <n>; this reader handles 8-12` | eldra eða nýrra pak snið |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | úr Python: prófaðu `.utoc`, sem `list` og `extract` taka líka |
| `<file> has no directory index, so its chunks carry no names to list` | IoStore ílát sem nefnir engar skrár; bitar þess nást aðeins í gegnum aðra pakka |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` við hlið skjalasafnsins er úr annarri smíð eða öðru skjalasafni; án hennar listast færslur eftir númeri |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | nöfn voru tætt í burtu við smíði |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | Frostbite tafla í huldu formi |
| `no Frostbite game found in a Steam library; give --install` | `levels` eða `level` fann engan Steam leik þar sem `Data` geymir `layout.toc`; gefðu upp möppu leiksins |
| `no level called '<name>'; did you mean one of ...?` | heitið passaði við enga borðstöflu, eða fleiri en eina; `levels` listar þau |
| `nothing was placed: no static model group was recognised` | hópmeðlimir borðsins hafa aðra gerðarundirskrift, eftir leikjauppfærslu eða í öðrum Frostbite leik; mæla þarf uppröðunina aftur |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | þjappað Unity net |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | hafðu `.resS` við hlið `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | eldri Unity smíð |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` tekur ber ílát |
| `texture format <n> has not been identified; refusing to guess` | Forza sýnishornssnið sem hefur ekki sést enn |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | hafðu hluta skipts VPK saman |

## Útflutningur sem kemur rangur út {#exports-that-come-out-wrong}

| Einkenni | Líkleg orsök |
|---|---|
| brautin er hliðruð frá hringnum í skoðaranum | hringurinn og útflutningurinn nota ólík ásakerfi: athugaðu `--game` (til dæmis BeamNG hringur lesinn sem Forza) |
| engin vegöxl í Forza braut | `--no-textures`, eða flísin hafði engin kort fyrir þá `--season` (skjárinn segir `N without maps`) |
| Forza flís í sléttum litum | jarðarkort hennar vantar fyrir árstíðina |
| mun færri staðsettir hlutir en búist var við | of lítið `--detail-budget` sem var gefið upp; samantektin segir hve mörg eintök voru skilin eftir |
| skráin er mjög stór (hundruð MB) | borgargangur undir sjálfvirka hámarkinu; notaðu `--detail-budget`, `--texture-size 1024` eða `--margin 40` |
| girðingar vantar | gegnsæir fletir eru skildir eftir af ásettu ráði (samantektin nefnir þá) |
| `N meshes could not be read` | sum líkön nota snið sem lesarinn hafnar; restin er samt flutt út |
| `N of M components could not be read` (AC Rally) | leikjauppfærsla gæti hafa fært eigindareiti; vinsamlegast tilkynntu það |
