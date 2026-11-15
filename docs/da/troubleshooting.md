---
title: Fejlfinding
nav_order: 11
lang: "da"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Fejlfinding {#troubleshooting}

Beskederne værktøjet skriver, når noget stopper det, hvad hver betyder, og hvad du skal gøre. Beskederne er citeret fra koden, med pladsholdere i vinkelparenteser.

## Før værktøjet overhovedet starter {#before-the-tool-even-starts}

| Du ser | Gør |
|---|---|
| `'python' is not recognized` | installér Python 3.10 eller nyere og sæt flueben i "Add python.exe to PATH"; åbn en ny terminal ([Før du starter](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminalen er i den forkerte mappe: `cd` til mappen med `README.md` |
| `No module named numpy` (eller en anden pakke) | kør `pip install -r requirements.txt` |
| en sti med mellemrum bliver klippet af, eller `unrecognized arguments` | sæt stien i dobbelte anførselstegn: `"C:\My Games\lap.json"` |

## At finde spillet {#finding-the-game}

| Besked | Betydning | Gør |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | intet Steam-bibliotek eller `C:\XboxGames` har et spil med `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | rundens koordinater ligger ikke på nogen installeret bane | tjek, at runden er fra dette spil; angiv `--track`, hvis banen er et andet sted |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | der findes fliser nær boksen, men ingen i korridoren | som ovenfor |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | mappen har ingen `.utoc`, der kan åbnes | peg `--install` på mappen med `.utoc`-filerne |

## At finde stedet {#finding-the-place}

| Besked | Betydning | Gør |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: intet niveau scorede 30 % | `--level <name>`; tjek, at runden er i viewer-koordinatsystemet |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` matchede ikke | brug et af de viste mappenavne |
| `<level> has no scene (no main/*.level.json and no .mis)` | niveaumappen har ingen scenefiler | et ødelagt eller ufuldstændigt niveau eller mod |
| `no terrain of <level> lies along the driving.` | BeamNG: korridoren har ingen terrænfirkanter | forkert niveau, eller et niveau uden terræn, der hvor runden er |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: ingen etape og frame scorede 50 % | `--level <stage>`; tjek, at rundens positioner er meter med y op |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` matchede ikke | brug et af de viste navne |
| `no ground of <stage> lies along the driving.` | AC Rally: ingen jordflise i korridoren | forkert etape |

## Runden {#the-lap}

| Besked | Gør |
|---|---|
| `<file> is not a lap this can read. ...` | giv den en understøttet form, se [Rundeinput](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON'en er ikke en runde |
| `<file> has no x, y and z columns` | navngiv CSV-kolonnerne `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | tjek navnet, eller giv en fil |
| `'<name>' matches 3 courses: ...` | brug en længere del af navnet |
| `<name> holds no driving` | runden har færre end to punkter |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` kræver en rute-JSON med `bounds`, som `heat3d_capture route` og `laps` skriver den; en rundefil er til `course` |
| `give exactly one of --box and --route` | `terrain` kræver ét område |
| `no course export for this lap: <reason>.` | spillet understøttes ikke, se [Begrænsninger og kendte huller](limits-and-known-gaps.md) |

## Arkiver {#archives}

| Besked | Betydning |
|---|---|
| `no Oodle library found. ...` | sæt `HEAT3D_OODLE`, se [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | en krypteret pak: `--key <hex>`, hvis du har nøglen. Der er ingen anden vej |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | nøglen er 32 bytes skrevet som 64 hex-cifre, `0x` valgfri (exit-kode 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | den er ingen af dem; `identify` siger, hvad den er. En Unity-container tager `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | en krypteret IoStore-container. Den kan ikke læses |
| `pak version <n>; this reader handles 8-12` | et ældre eller nyere pak-format |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | fra Python: prøv `.utoc`, som `list` og `extract` også tager |
| `<file> has no directory index, so its chunks carry no names to list` | en IoStore-container, der ikke navngiver filer; dens chunks nås kun via andre pakker |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` ved siden af arkivet er fra en anden build eller et andet arkiv; uden den listes posterne efter nummer |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | navnene blev hashet væk under build |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | en Frostbite-tabel i den slørede form |
| `no Frostbite game found in a Steam library; give --install` | `levels` eller `level` fandt intet Steam-spil, hvis `Data` har en `layout.toc`; angiv spillets mappe |
| `no level called '<name>'; did you mean one of ...?` | navnet passede ingen niveautabel, eller flere; `levels` lister dem |
| `nothing was placed: no static model group was recognised` | niveauets gruppemedlemmer har en anden typesignatur, efter en spilopdatering eller i et andet Frostbite-spil; layoutet skal måles igen |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | en komprimeret Unity-mesh |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | hold `.resS`-filen ved siden af `.assets`-filen |
| `<file>: format <n> predates Unity 2020 ...` | en ældre Unity-build |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` tager en ren container |
| `texture format <n> has not been identified; refusing to guess` | et Forza-farveprøveformat, der ikke er set endnu |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | hold en delt VPK's dele sammen |

## Eksporter, der bliver forkerte {#exports-that-come-out-wrong}

| Symptom | Sandsynlig årsag |
|---|---|
| banen er forskudt i forhold til runden i viewer'en | runden og eksporten bruger forskellige koordinatsystemer: tjek `--game` (en BeamNG-runde læst som Forza, f.eks.) |
| ingen kant i en Forza-bane | `--no-textures`, eller flisen havde ingen kort for den `--season` (konsollen siger `N without maps`) |
| en Forza-flise i flade farver | dens jordkort mangler for årstiden |
| langt færre placerede objekter end forventet | et eksplicit `--detail-budget` for lille; opsummeringen siger, hvor mange kopier der blev udeladt |
| filen er meget stor (hundredvis af MB) | en bykorridor under det automatiske budget; brug `--detail-budget`, `--texture-size 1024` eller `--margin 40` |
| hegn mangler | gennemsigtige flader er udeladt med vilje (opsummeringen navngiver dem) |
| `N meshes could not be read` | nogle modeller bruger et format, læseren afviser; resten eksporteres stadig |
| `N of M components could not be read` (AC Rally) | en spilopdatering kan have flyttet egenskabspladser; meld det venligst |
