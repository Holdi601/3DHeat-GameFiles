---
title: Risoluzione dei problemi
nav_order: 11
lang: "it"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Risoluzione dei problemi {#troubleshooting}

I messaggi che lo strumento mostra quando qualcosa lo ferma, che cosa significa ciascuno e che cosa fare. I messaggi sono
citati dal codice, con i segnaposto tra parentesi angolari.

## Prima ancora che lo strumento parta {#before-the-tool-even-starts}

| Vedi | Fai |
|---|---|
| `'python' is not recognized` | installa Python 3.10 o successivo e spunta "Add python.exe to PATH"; apri un nuovo terminale ([Prima di iniziare](before-you-start.md)) |
| `No module named heat3d_gamefiles` | il terminale è nella cartella sbagliata: fai `cd` nella cartella con `README.md` |
| `No module named numpy` (o un altro pacchetto) | esegui `pip install -r requirements.txt` |
| un percorso con spazi viene tagliato, oppure `unrecognized arguments` | metti il percorso tra virgolette doppie: `"C:\My Games\lap.json"` |

## Trovare il gioco {#finding-the-game}

| Messaggio | Significato | Fai |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | nessuna libreria Steam o `C:\XboxGames` contiene un gioco con `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | le coordinate del giro non si trovano su nessuna pista installata | controlla che il giro venga da questo gioco; passa `--track` se la pista è altrove |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | ci sono tessere vicino al riquadro ma nessuna nel corridoio | come sopra |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | la cartella non ha nessun `.utoc` che si apra | indica con `--install` la cartella con i file `.utoc` |

## Trovare il posto {#finding-the-place}

| Messaggio | Significato | Fai |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: nessun livello ha fatto almeno il 30% | `--level <name>`; controlla che il giro sia nel sistema di riferimento del visualizzatore |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` non corrisponde a nulla | usa uno dei nomi di cartella elencati |
| `<level> has no scene (no main/*.level.json and no .mis)` | la cartella del livello non ha file di scena | un livello o una mod rotti o incompleti |
| `no terrain of <level> lies along the driving.` | BeamNG: il corridoio non ha quadrati di terreno | livello sbagliato, oppure un livello senza terreno dove passa il giro |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: nessuna tappa e nessun fotogramma ha fatto il 50% | `--level <stage>`; controlla che le posizioni del giro siano in metri con y in alto |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` non corrisponde a nulla | usa uno dei nomi elencati |
| `no ground of <stage> lies along the driving.` | AC Rally: nessuna tessera di suolo nel corridoio | tappa sbagliata |

## Il giro {#the-lap}

| Messaggio | Fai |
|---|---|
| `<file> is not a lap this can read. ...` | usa una forma supportata, vedi [Input dei giri](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | il JSON non è un giro |
| `<file> has no x, y and z columns` | chiama le colonne del CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | controlla il nome, oppure passa un file |
| `'<name>' matches 3 courses: ...` | usa una parte più lunga del nome |
| `<name> holds no driving` | il giro ha meno di due campioni |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` richiede un JSON di percorso con `bounds`, come lo scrivono `heat3d_capture route` e `laps`; un file di giro serve a `course` |
| `give exactly one of --box and --route` | `terrain` richiede una sola regione |
| `no course export for this lap: <reason>.` | il gioco non è supportato, vedi [Limiti e lacune note](limits-and-known-gaps.md) |

## Archivi {#archives}

| Messaggio | Significato |
|---|---|
| `no Oodle library found. ...` | imposta `HEAT3D_OODLE`, vedi [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | un pak cifrato: `--key <hex>` se possiedi la chiave. Non c'è altro modo |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | la chiave è di 32 byte scritti come 64 cifre esadecimali, `0x` facoltativo (codice di uscita 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | non è nessuno di questi; `identify` dice che cos'è. Un contenitore Unity richiede `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | un contenitore IoStore cifrato. Non si può leggere |
| `pak version <n>; this reader handles 8-12` | un formato pak più vecchio o più nuovo |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | da Python: prova il `.utoc`, che anche `list` ed `extract` accettano |
| `<file> has no directory index, so its chunks carry no names to list` | un contenitore IoStore che non nomina file; i suoi chunk si raggiungono solo tramite altri pacchetti |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | il `ChunkContentsMiniZip<n>.txt` accanto all'archivio viene da un'altra build o da un altro archivio; senza di esso le voci si elencano per numero |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | i nomi sono stati sottoposti a hash in fase di build |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | una tabella Frostbite nella forma offuscata |
| `no Frostbite game found in a Steam library; give --install` | `levels` o `level` non hanno trovato un gioco Steam il cui `Data` contiene un `layout.toc`; indica la cartella del gioco |
| `no level called '<name>'; did you mean one of ...?` | il nome non corrisponde alla tabella di nessun livello, oppure ne corrisponde più di uno; `levels` li elenca |
| `nothing was placed: no static model group was recognised` | la firma dei tipi dei membri di gruppo del livello è diversa, dopo un aggiornamento del gioco o in un altro gioco Frostbite; il layout va misurato di nuovo |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | una mesh Unity compressa |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | tieni il `.resS` accanto all'`.assets` |
| `<file>: format <n> predates Unity 2020 ...` | una build Unity più vecchia |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` accetta un contenitore semplice |
| `texture format <n> has not been identified; refusing to guess` | un formato di campione Forza non ancora visto |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | tieni insieme le parti di un VPK diviso |

## Esportazioni che escono sbagliate {#exports-that-come-out-wrong}

| Sintomo | Causa probabile |
|---|---|
| il percorso è spostato rispetto al giro nel visualizzatore | il giro e l'esportazione usano sistemi di riferimento diversi: controlla `--game` (un giro di BeamNG letto come Forza, per esempio) |
| nessun bordo in un percorso di Forza | `--no-textures`, oppure la tessera non aveva mappe per quella `--season` (la console dice `N without maps`) |
| una tessera di Forza a colori piatti | le sue mappe del suolo mancano per la stagione |
| molti meno oggetti collocati del previsto | un `--detail-budget` esplicito troppo piccolo; il riepilogo dice quante copie sono state escluse |
| il file è molto grande (centinaia di MB) | un corridoio urbano sotto il budget automatico; usa `--detail-budget`, `--texture-size 1024` oppure `--margin 40` |
| recinzioni mancanti | le superfici trasparenti vengono lasciate fuori di proposito (il riepilogo le nomina) |
| `N meshes could not be read` | alcuni modelli usano un formato che il lettore rifiuta; il resto viene comunque esportato |
| `N of M components could not be read` (AC Rally) | una patch del gioco può aver spostato gli slot delle proprietà; per favore segnalalo |
