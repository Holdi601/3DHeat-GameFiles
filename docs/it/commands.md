---
title: Comandi
nav_order: 2
lang: "it"
source: commands.md
source_hash: "8ae04c37b1a4"
nav_exclude: true
search_exclude: true
---
# Comandi {#commands}

Ogni comando si esegue come `python -m heat3d_gamefiles <verbo> ...` dalla cartella
del repository. I verbi sono nell'ordine in cui di solito servono: che file è
questo, cosa c'è dentro, estrai quello che ti serve, e trasforma un giro in un percorso.

| Verbo | Accetta | Fa |
|---|---|---|
| [`identify`](#identify) | qualsiasi file | dice quale formato di contenitore è, leggendo i suoi byte |
| [`list`](#list) | un `.pak` o un `.utoc` IoStore di Unreal, un `.vpk` di Source 2, oppure uno zip (un `.minizip` di ForzaTech tramite lo strumento di Forza) | elenca le sue voci |
| [`extract`](#extract) | lo stesso | scrive una voce su disco |
| [`meshes`](#meshes) | un `SerializedFile` di Unity | elenca e controlla le sue mesh |
| [`course`](#course) | un giro | esporta il percorso attorno ad esso (Forza, BeamNG.drive, Assetto Corsa Rally) (eseguito dallo strumento di Forza, BeamNG.drive o AC Rally) |
| [`courses`](#courses-races-cars-terrain-forza) | una libreria di giri registrati | esegue `course` su ogni percorso che contiene (Forza) (eseguito dallo strumento di Forza) |
| [`races`](#courses-races-cars-terrain-forza) | una Forza installata | elenca ogni gara che il gioco definisce: cosa aggiunge, cosa nasconde, i luoghi, lo stato della sua esportazione (eseguito dallo strumento di Forza) |
| [`terrain`](#courses-races-cars-terrain-forza) | una cartella di tracciato di Forza | ritaglia una regione tramite coordinate del mondo (eseguito dallo strumento di Forza) |
| [`levels`](#levels-and-level-frostbite) | un gioco Frostbite installato (Battlefield 6) | elenca i suoi livelli (eseguito dallo strumento di Battlefield) |
| [`level`](#levels-and-level-frostbite) | il nome di un livello | esporta il livello: terreno, mesh posizionate, facoltativamente le loro mappe di colore (Battlefield 6) (eseguito dallo strumento di Battlefield) |
| [`cars`](#courses-races-cars-terrain-forza) | una Forza installata | ogni auto a basso dettaglio, in un unico file per la scheda Analisi di gara del visualizzatore (eseguito dallo strumento di Forza) |
| [`ue-maps`](#ue-maps-e-ue-map-unreal-5-world-partition) | un gioco Unreal 5 | elenca le sue mappe World Partition |
| [`ue-map`](#ue-maps-e-ue-map-unreal-5-world-partition) | il nome di una mappa | esporta la mappa: paesaggio, strutture HLOD, acqua |
| [`enfusion-worlds`](#enfusion-worlds-e-enfusion-world-arma-reforger) | un Arma Reforger installato | elenca i suoi mondi (eseguito dallo strumento di Reforger) |
| [`enfusion-world`](#enfusion-worlds-e-enfusion-world-arma-reforger) | il nome di un mondo | esporta il mondo: terreno nei suoi colori, il mare, gli edifici come scatole (eseguito dallo strumento di Reforger) |

**Come leggere gli esempi:** `<x>` significa da sostituire con il tuo valore, senza
le parentesi angolari; `[...]` indica un'opzione facoltativa; racchiudi tra
"doppi apici" un percorso con spazi, per esempio `"C:\Giochi\Il mio gioco"`.
Non hai mai usato questi strumenti? Vedi [Prima di iniziare](before-you-start.md).
Il `--help` completo di ogni verbo è nella [Guida ai comandi](../cli-reference.md).

Ogni volta che il programma si avvia, può controllare prima se esiste una versione
più recente. Vedi [Aggiornamenti](updates.md). `HEAT3D_NO_UPDATE=1` disattiva
questo controllo.

Fonte: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Pagine passo passo: [Ispezionare gli archivi](inspecting-archives.md), [Esportazione
del percorso](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html),
[Livelli interi](whole-levels.md), [Auto di Forza](https://holdi601.github.io/3DHeat-Ext-Forza/forza-cars.html).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Codici di uscita {#exit-codes}

| Codice | Significato |
|---|---|
| 0 | operazione riuscita |
| 1 | il lavoro non è andato a buon fine (giro illeggibile, nessun gioco trovato, niente da esportare, un percorso in `courses` non riuscito; per `list` ed `extract`, un file che non è nessuno degli archivi che leggono, uno che non si può aprire o leggere - un pak cifrato senza `--key`, un contenitore IoStore cifrato - oppure una voce che non è nell'archivio) |
| 2 | argomenti sbagliati (argparse), un percorso che non esiste, una `--key` che non è di 64 cifre esadecimali, oppure `terrain` con entrambi o nessuno tra `--box` e `--route` |

Gli errori di `list` ed `extract` sono ciascuno una sola riga sull'errore standard,
non un traceback di Python.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <percorso>
```

Questo comando legge il file e dice di quale contenitore si tratta. Non si basa
sull'estensione (l'unica eccezione è un `.ucas`, più sotto). Prova i formati in
questo ordine e si ferma al primo che si legge correttamente:

1. **`.pak` di Unreal**: un footer con la firma pak negli ultimi 1.024 byte. Mostra
   la versione, l'offset e la dimensione dell'indice, se l'indice è cifrato e i
   metodi di compressione.
2. **`.utoc` IoStore di Unreal**: la firma IoStore all'inizio. Mostra la versione,
   il numero di blocchi e se il contenitore è cifrato; per uno non cifrato, il
   numero di file che la sua directory nomina (e sotto quale mount point), i metodi
   di compressione, e se il suo `.ucas` si trova accanto. Un `.ucas` non ha un'intestazione
   propria, quindi viene riconosciuto grazie al `.utoc` con lo stesso nome accanto
   a lui, e `identify` indica quel file.
3. **`.minizip` di ForzaTech**: la firma `PGZP`. Mostra la versione, il numero di
   voci e di segmenti, e se accanto c'è il `ChunkContentsMiniZip<n>.txt` che
   nomina le voci (e, in tal caso, se ne nomina tante quante sono).
4. **zip**: un'intestazione di file locale zip all'inizio. Mostra il numero di voci,
   le sei estensioni più comuni e i nomi dei livelli quando le voci stanno sotto
   `levels/<nome>/`, come in un archivio di livelli di BeamNG.drive.
5. **Unity**: un pacchetto `UnityFS` (mostra la versione del motore e il numero di
   voci) oppure un `SerializedFile` semplice (mostra il formato, la versione del
   motore, il numero di oggetti e le sei classi più comuni).
6. **`.toc` di Frostbite**: mostra il tipo (`plain` o `signed`), dove inizia l'albero,
   e o il numero di asset (tabella binaria delle sezioni) o il numero di superbundle
   (albero DbObject).
7. **`.vpk` di Source 2**: mostra la versione, il numero di voci e la prima mesh di
   navigazione `.nav`, se l'archivio ne ha una.
8. **`.cdae` di BeamNG**: versione di forma 31 che si legge. Mostra il numero di
   mesh, il numero di livelli di dettaglio disegnati e i primi materiali.
9. **`.ter` di BeamNG**: non c'è una firma, quindi tutto deve tornare - una
   dimensione da 2 a 16.384, quel numero di altezze al quadrato e di byte di
   strato, poi da 1 a 255 nomi di strato stampabili. Mostra la versione, la
   dimensione e i nomi degli strati.
10. **`.modelbin` di ForzaTech**: mostra la versione, il numero di blocchi e i sei
    tag di blocco più comuni. Il contenuto dei blocchi qui non viene decodificato.

I formati con una firma propria (dal 2 al 4) vengono prima di Unity e Frostbite,
i cui controlli leggono l'intero file: un archivio di Forza pesa decine di gigabyte.

Se nessuno corrisponde, stampa `not a format this tool reads` e l'ultimo motivo.
Quel motivo viene dal controllo di ForzaTech.

Esempio (dati sintetici):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archivio> [--filter TESTO] [--limit N] [--key HEX]
```

| Opzione | Predefinito | Significato |
|---|---|---|
| `<archivio>` | obbligatorio | un `.pak` di Unreal; un `.utoc` IoStore (o il `.ucas` accanto); un `.vpk` di Source 2 (per i VPK divisi, il `_dir.vpk`); un `.minizip` di ForzaTech; uno zip, come gli archivi di livelli e contenuti di BeamNG |
| `--filter TESTO` | nessuno | solo i percorsi che contengono TESTO, senza distinguere maiuscole e minuscole |
| `--limit N` | 50 | stampa al massimo N voci (il conteggio totale viene sempre stampato) |
| `--key HEX` | nessuna | una chiave AES-256 che già possiedi, 64 cifre esadecimali, con o senza `0x`. La usa solo un `.pak` cifrato. Qualsiasi valore che non sia di 64 cifre esadecimali viene rifiutato prima di aprire l'archivio (codice di uscita 2) |

Lo strumento decide il formato dai byte: una tabella dei contenuti IoStore, un
`.minizip` e un VPK dalla firma con cui iniziano, uno zip dalla sua intestazione
di file locale, e un `.pak` dal footer alla fine. Un `.ucas` non ha intestazione
e si apre tramite il `.utoc` con lo stesso nome. Un file che non è nessuno di
questi viene rifiutato con `<file> is not an archive list and extract read (...)`.
Uno che lo è ma non si può aprire viene rifiutato con il motivo del lettore: un
pak cifrato senza `--key`, un contenitore IoStore cifrato, una versione di pak che
non legge. In entrambi i casi è una sola riga e codice di uscita 1.

Ogni riga mostra la dimensione non compressa, il metodo di compressione e il percorso:

| Archivio | Metodo | Percorsi |
|---|---|---|
| `.pak` | `none`, oppure il nome dal footer (`Zlib`, `Oodle`, `Gzip`...) | con il mount point dell'archivio, per esempio `../../../Game/Content/...` |
| `.utoc` IoStore | `none`, oppure il metodo del contenitore (`Oodle`, `Zlib`...), come è memorizzato il suo primo blocco | con il mount point, per esempio `../../../<Project>/Content/...`. Un contenitore senza indice di directory non nomina file e viene rifiutato |
| `.vpk` | sempre `stored` | come nella directory |
| `.minizip` | `lz4`, `deflate` o `stored` | come li scrive il `ChunkContentsMiniZip<n>.txt` accanto a `GeoChunk<n>.minizip`, senza il prefisso della macchina di build (barre rovesciate, come le scrive il gioco). L'archivio non memorizza nomi, quindi senza quel file le voci sono `#0`, `#1`... Un elenco il cui numero di righe non corrisponde alle voci viene rifiutato: i due non appartengono insieme |
| zip | `stored`, `deflate`, ... | come memorizzato; le cartelle non sono elencate |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archivio> <voce> [--out FILE] [--key HEX]
```

| Opzione | Predefinito | Significato |
|---|---|---|
| `<archivio>` | obbligatorio | come per `list` |
| `<voce>` | obbligatorio | il percorso esattamente come lo stampa `list` (distingue maiuscole e minuscole); in un `.minizip` funziona anche `#<numero>` |
| `--out FILE` | il nome del file della voce (dopo l'ultimo `/` o `\`), nella cartella corrente | dove scrivere; le cartelle madri vengono create |
| `--key HEX` | nessuna | come per `list` |

La voce viene decifrata (pak, con una chiave), decompressa e scritta. Stampa
`<bytes> bytes -> <file>`. Se il percorso non è nell'archivio, il comando esce
con codice 1. Lo stesso vale per una voce che non si può leggere (una voce cifrata
senza chiave, compressa con Oodle senza la libreria Oodle), con il motivo su una
riga. Una voce VPK non viene verificata qui con il suo CRC. Il lettore ha un metodo
`verify()` per questo (vedi [VPK di Source 2](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <file .assets di Unity> [--limit N]
```

| Opzione | Predefinito | Significato |
|---|---|---|
| `<percorso>` | obbligatorio | un `SerializedFile` di Unity semplice (`sharedassets0.assets`, `level0`...), non un pacchetto |
| `--limit N` | 25 | decodifica e stampa al massimo N mesh |

Stampa il numero di oggetti `Mesh`, poi una riga per mesh: il nome (primi 40
caratteri), il numero di vertici e di triangoli, e `ok` oppure `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` significa che i vertici decodificati non riproducono il riquadro
di delimitazione che Unity ha memorizzato per la mesh, entro il 2% della dimensione
del riquadro. È il controllo interno dell'analisi (vedi [Unity](reader-unity.md)).
Una mesh che non si può leggere viene segnalata con il motivo e conta nel limite.
I dati dei vertici in un file `.resS` vengono letti dalla cartella in cui si trova
il contenitore.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## I verbi dei giochi {#the-games-own-verbs}

Ogni lettore di gioco è un piccolo progetto a sé, con il proprio file di licenza, le proprie release e il
proprio tracker delle segnalazioni, così può essere installato, aggiornato, mantenuto - o ritirato su
richiesta di un titolare dei diritti - in modo indipendente, senza toccare il visualizzatore né gli altri
strumenti. Installa quello per il tuo gioco (la sua pagina dice come), e sia il suo comando sia i verbi qui
funzionano. GameFiles esegue lo strumento del gioco con gli argomenti che gli hai dato; non importa nulla
dello strumento. Viene trovato come suo comando in `PATH`, come suo pacchetto installato, oppure come sua
cartella in `HEAT3D_<GAME>_MAPS` o accanto a GameFiles (`exporters/ext/<game>-maps` in una copia di lavoro di
3DHeat, oppure `3DHeat-Ext-<Game>` accanto a questa cartella). Quando non è installato, il verbo dice dove
prenderlo ed esce con codice 2.

| Gioco | Il suo strumento | Verbi qui che lo eseguono |
|---|---|---|
| Forza Horizon / Motorsport | [3DHeat-Ext-Forza](https://holdi601.github.io/3DHeat-Ext-Forza/) (`heat3d-forza-maps`) | `course` (giri di Forza), `courses`, `races`, `cars`, `terrain`; `identify`, `list`, `extract` di un `.minizip` |
| Battlefield (Frostbite) | [3DHeat-Ext-Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/) (`heat3d-battlefield-maps`) | `levels`, `level`; `identify` di un `.toc` di Frostbite |
| BeamNG.drive | [3DHeat-Ext-BeamNG](https://holdi601.github.io/3DHeat-Ext-BeamNG/) (`heat3d-beamng-maps`) | `course` (giri di BeamNG); `identify` di un `.cdae` o di un `.ter` |
| Assetto Corsa Rally | [3DHeat-Ext-ACRally](https://holdi601.github.io/3DHeat-Ext-ACRally/) (`heat3d-acrally-maps`) | `course` (giri di AC Rally) |
| Arma Reforger (Enfusion) | [3DHeat-Ext-Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/) (`heat3d-reforger-maps`) | `enfusion-worlds`, `enfusion-world` |

`python -m heat3d_gamefiles <verbo> --help` mostra le opzioni dello strumento del gioco.

## course {#course}

```
python -m heat3d_gamefiles course <giro> [-o FILE] [opzioni]
```

Il percorso attorno a un giro - il terreno in una fascia su entrambi i lati della guida, e ciò che vi
sorge, come un unico `.glb` - creato dallo strumento proprio del gioco del giro, eseguito con gli stessi
argomenti: [Forza](https://holdi601.github.io/3DHeat-Ext-Forza/course-forza-horizon.html),
[BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html),
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html). Cosa può
essere un giro: [Input dei giri](lap-inputs.md); quanto dettaglio si conserva:
[Livelli di dettaglio e budget](detail-budget.md).

### Quale gioco {#which-game}

Il gioco viene preso da `--game`, poi dal campo `game` di un file `heat3d-lap`
(o dalla riga di descrizione `# {...}` di un CSV), e in mancanza è Forza. Una
cartella prende il gioco che nominano i suoi file, quando ne nominano uno solo; un
file che non ne nomina nessuno (un giro di FH Companion, `course.json`, un CSV senza
riga di descrizione) non conta (vedi [Input dei giri](lap-inputs.md)).

| Valore | Eseguito da |
|---|---|
| inizia con `forza` | `heat3d-forza-maps course` |
| `beamng` | `heat3d-beamng-maps course` |
| `assetto-corsa-rally` o `acrally` | `heat3d-acrally-maps course` |
| `assetto-corsa-evo` | rifiutato: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | rifiutato: "tracks ship in a protected format that is not a file-extraction target" |
| qualsiasi altro | rifiutato: "there is no course reader for <game> yet" |

Un rifiuto suggerisce anche le alternative: ricostruire il percorso dal gioco
(3DHeat GameCapture), oppure analizzare i giri senza un percorso, perché la scheda
Analisi di gara del visualizzatore disegna una strada a partire da essi.

## courses, races, cars, terrain (Forza) {#courses-races-cars-terrain-forza}

Eseguiti da `heat3d-forza-maps` con gli stessi argomenti:
[i suoi comandi](https://holdi601.github.io/3DHeat-Ext-Forza/commands.html).

## levels e level (Frostbite) {#levels-and-level-frostbite}

Eseguiti da `heat3d-battlefield-maps` con gli stessi argomenti:
[Livelli di Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/level-battlefield.html).

## ue-maps e ue-map (Unreal 5 World Partition) {#ue-maps-e-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <gioco>
python -m heat3d_gamefiles ue-map  <gioco> <mappa> [-o FILE] [--ground-spacing METRI] [--no-structures] [--no-water]
```

`<gioco>` è la cartella del gioco, la sua `Content/Paks`, oppure il nome della sua
cartella in una libreria Steam (`"<nome della cartella del gioco Steam>"`).
`ue-maps` elenca ogni mappa che ha celle World Partition già compilate accanto a
sé. `ue-map` ne esporta una come `ground:<mappa>` (il paesaggio), `structure:<mappa>`
(le mesh HLOD unite della mappa) e `water:<mappa>` (i suoi corpi d'acqua dove
sorgono sopra il suolo), in **centimetri** di Unreal con Y e Z scambiati - l'unica
esportazione che non è in metri. Come si legge e si controlla ciascuna:
[Mappe di Unreal 5](level-unreal-world-partition.md).

| Opzione | Predefinito | Significato |
|---|---|---|
| `<mappa>` | obbligatorio | un nome come lo stampa `ue-maps`, o una parte unica di esso |
| `-o`, `--out FILE` | `<mappa>.glb` (in `$HEAT3D_LEVELS/<gioco>/` quando è impostata) | il `.glb` da scrivere |
| `--ground-spacing METRI` | 2 | la spaziatura dei vertici del paesaggio nel file, arrotondata a un numero intero di suoi quad |
| `--no-structures`, `--no-water` | | lascia fuori quella parte |

Stampa i triangoli per parte, quante componenti del paesaggio sono state lette e
quanti dei vertici che ne memorizzano due volte non concordano. Una mappa di 3 km
a 2 m sono circa 4,6 milioni di triangoli del suolo.

## enfusion-worlds e enfusion-world (Arma Reforger) {#enfusion-worlds-e-enfusion-world-arma-reforger}

Eseguiti da `heat3d-reforger-maps` con gli stessi argomenti (i suoi `worlds` e
`world`): [Mondi di Arma Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/level-arma-reforger.html).

## Variabili d'ambiente {#environment-variables}

| Variabile | Effetto |
|---|---|
| `HEAT3D_OODLE` | percorso di un `oo2core_*_win64.dll`, oppure di una cartella che lo contiene; vedi [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | una cartella per ogni esportazione fatta senza `-o`: quelle di ogni gioco vanno in `<HEAT3D_LEVELS>/<gioco>/` (i percorsi in `<gioco>/courses/`, il pacchetto auto in `forza/`). Se non è impostata, vanno nella cartella corrente |
| `HEAT3D_FORZA_MAPS`, `HEAT3D_BATTLEFIELD_MAPS`, `HEAT3D_BEAMNG_MAPS`, `HEAT3D_ACRALLY_MAPS`, `HEAT3D_REFORGER_MAPS` | la cartella di uno strumento di un gioco, quando non è installato e non si trova accanto a GameFiles |
| `HEAT3D_NO_UPDATE` | qualsiasi valore diverso da vuoto, `0`, `false`, `no` disattiva il controllo degli aggiornamenti; vedi [Aggiornamenti](updates.md) |
| `LOCALAPPDATA` | dove vengono cercate la libreria di FH Companion, la cartella utente di BeamNG e la cache degli aggiornamenti |
| `HEAT3D_COURSE` | solo per i test: il percorso usato dal test dei cordoli del gioco installato; vedi [Sviluppo](development.md) |
