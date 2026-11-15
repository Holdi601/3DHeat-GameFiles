---
title: Comandi
nav_order: 2
lang: "it"
source: commands.md
source_hash: "6c8d37db40e5"
nav_exclude: true
search_exclude: true
---
# Comandi {#commands}

Ogni comando si esegue come `python -m heat3d_gamefiles <verbo> ...` dalla cartella
del repository. I verbi sono nell'ordine in cui di solito servono: che file è
questo, cosa c'è dentro, dammi quella cosa, e trasforma un giro in un percorso.

| Verbo | Accetta | Fa |
|---|---|---|
| [`identify`](#identify) | qualsiasi file | dice quale formato di contenitore è, leggendo i suoi byte |
| [`list`](#list) | un `.pak` o un `.utoc` IoStore di Unreal, un `.vpk` di Source 2, un `.minizip` di ForzaTech, oppure uno zip | elenca le sue voci |
| [`extract`](#extract) | lo stesso | scrive una voce su disco |
| [`meshes`](#meshes) | un `SerializedFile` di Unity | elenca e controlla le sue mesh |
| [`course`](#course) | un giro | esporta il percorso attorno ad esso (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | una libreria di giri registrati | esegue `course` su ogni percorso che contiene (Forza) |
| [`terrain`](#terrain) | una cartella di tracciato di Forza | ritaglia una regione tramite coordinate del mondo |
| [`levels`](#levels-and-level-frostbite) | un gioco Frostbite installato (Battlefield 6) | elenca i suoi livelli |
| [`level`](#levels-and-level-frostbite) | il nome di un livello | esporta il livello: terreno, mesh posizionate, facoltativamente le loro mappe di colore (Battlefield 6) |
| [`cars`](#cars) | una Forza installata | ogni auto a basso dettaglio, in un unico file per la scheda Analisi di gara del visualizzatore |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | un gioco Unreal 5 | elenca le sue mappe World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | il nome di una mappa | esporta la mappa: paesaggio, strutture HLOD, acqua |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | un Arma Reforger installato | elenca i suoi mondi |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | il nome di un mondo | esporta il mondo: terreno nei suoi colori, il mare, gli edifici come scatole |

**Come leggere gli esempi:** `<x>` significa da sostituire con il tuo valore, senza
le parentesi angolari; `[...]` indica un'opzione facoltativa; racchiudi tra
"doppi apici" un percorso con spazi, per esempio `"C:\Giochi\Il mio gioco"`.
Non hai mai usato questi strumenti? Vedi [Prima di iniziare](before-you-start.md).
Il `--help` completo di ogni verbo è nella [Guida ai comandi](../cli-reference.md).

Ogni volta che il programma si avvia, può controllare prima se esiste una versione
più recente. Vedi [Aggiornamenti](updates.md). `HEAT3D_NO_UPDATE=1` disattiva
questo controllo.

Fonte: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Pagine passo passo: [Esaminare gli archivi](inspecting-archives.md), [Esportazione
del percorso](course-export.md), [Livelli interi](whole-levels.md), [Auto di
Forza](forza-cars.md).

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

## course {#course}

```
python -m heat3d_gamefiles course <giro> [-o FILE] [opzioni]
```

Esporta il percorso attorno a un giro: il terreno in una fascia su entrambi i lati
della guida, e ciò che vi sorge, in un unico `.glb`. Il comando ricava da solo il
resto: quale gioco, quale copia installata, quale tracciato, livello o tappa, e
(per Assetto Corsa Rally) in che verso sono orientati gli assi. Vedi
[Esportazione del percorso](course-export.md).

`<giro>` può essere uno dei seguenti (dettagli in [Input del giro](lap-inputs.md)):

- un file del giro: JSON di percorso, JSON di giro di FH Companion, JSON `heat3d-lap`, `.npz`, oppure `.csv` con le colonne x, y, z
- una cartella di file di giro, cercata ricorsivamente (un intero percorso registrato)
- il **nome** di un percorso, cercato nella libreria di FH Companion in `%LOCALAPPDATA%\FHCompanion\laps`

### Opzioni {#options}

| Opzione | Predefinito | Giochi | Significato |
|---|---|---|---|
| `-o`, `--out FILE` | `<nome del percorso>.glb` nella cartella corrente | tutti | dove scrivere; il nome viene convertito in minuscolo, e sequenze di altri caratteri diventano `_` |
| `--game {forza,beamng,acrally}` | quanto dice il file del giro, altrimenti `forza` | tutti | da quale gioco proviene il giro |
| `--margin M` | 80 | tutti | metri di terreno conservati su entrambi i lati della guida |
| `--texture-size {2048,1024,512}` | 2048 | tutti | pixel della texture del terreno per ogni tassello di 512 m (2048 = 25 cm per pixel) |
| `--no-textures` | disattivato | tutti | solo colori piatti: un file molto più piccolo. Per Forza questo salta anche la divisione tra strada e banchina (vedi sotto) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | le mappe del terreno e le texture dei modelli di quale stagione |
| `--no-placed` | disattivato | tutti | solo terreno: niente cordoli, barriere, cartelli, edifici. Per BeamNG, le superfici di guida modellate come mesh restano |
| `--trees` | disattivato | tutti | colloca anche la vegetazione (Forza: alberi, cespugli e oggetti frantumabili; BeamNG: alberi; AC Rally: alberi e la vegetazione istanziata) |
| `--detail-budget N` | automatico | tutti | un tetto di triangoli per tutto ciò che viene collocato; vedi [Livelli di dettaglio e budget](detail-budget.md) |
| `--track DIR` | cercata | Forza | la cartella del tracciato (sotto `media\Tracks`, con `GeoChunk0.minizip`) se il gioco installato non deve essere cercato |
| `--level NAME` | ricavato dal giro | BeamNG, AC Rally | il livello (nome della cartella di BeamNG) o la tappa (nome della mappa di AC Rally), senza distinzione tra maiuscole e minuscole |
| `--install DIR` | cercata nelle librerie Steam | BeamNG, AC Rally | BeamNG: la cartella che contiene `gameengine.zip`. AC Rally: la cartella del gioco, oppure la sua `acr\Content\Paks` / `Content\Paks` |

Le opzioni che non valgono per un gioco vengono ignorate senza avviso. Per
esempio, `--season` non fa nulla per BeamNG e AC Rally, e anche `--track` non fa
nulla per loro.

### Quale gioco {#which-game}

Il gioco viene preso da `--game`, poi dal campo `game` di un file `heat3d-lap`
(o dalla riga di descrizione `# {...}` di un CSV), e in mancanza è Forza. Una
cartella prende il gioco che nominano i suoi file, quando ne nominano uno solo; un
file che non ne nomina nessuno (un giro di FH Companion, `course.json`, un CSV senza
riga di descrizione) non conta (vedi [Input del giro](lap-inputs.md)).

| Valore | Esportazione |
|---|---|
| inizia con `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` o `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | rifiutato: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | rifiutato: "tracks ship in a protected format that is not a file-extraction target" |
| qualsiasi altro | rifiutato: "there is no course reader for <game> yet" |

Un rifiuto suggerisce anche le alternative: ricostruire il percorso dal gioco
(3DHeat GameCapture), oppure analizzare i giri senza un percorso, perché la scheda
Analisi di gara del visualizzatore disegna una strada a partire da loro.

### Esempi {#examples}

```
# Un percorso dalla libreria di FH Companion, per nome
python -m heat3d_gamefiles course "Example Circuit"

# Un file di giro, una fascia più stretta, un file più piccolo
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Texture invernali, alberi inclusi
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Un tetto rigido di 500.000 triangoli collocati
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Una cartella di tracciato indicata direttamente (gioco installato fuori da Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: indica il livello, punta all'installazione
python -m heat3d_gamefiles course beamng_lap.json --level <cartella del livello> --install "D:\Games\BeamNG.drive"

# AC Rally, con un giro CSV semplice che non dice il suo gioco
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Esempio di output (Forza, numeri sintetici):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<cartella del gioco>" -o forza.h3dcars
```

Ogni auto di una Forza installata, al basso dettaglio del gioco stesso, in un unico
file per la scheda Analisi di gara del visualizzatore: il modello `ProxyLOD` che ogni archivio auto
sotto `media/Cars` contiene, circa 900 triangoli, con il numero dell'auto come lo
indica la telemetria, la sua marca, il tag del modello e l'anno ricavati dal nome
dell'archivio, e le sue ruote e fanali posteriori. Richiede pochi secondi e scrive
circa 5 MB. Eseguilo di nuovo quando il gioco ottiene nuove auto. Un archivio senza
quel modello (un oggetto di traffico) viene indicato e lasciato fuori. Il formato
è in [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Le forme sono in metri, quelle proprie del gioco: 1:1 con l'auto. Il file contiene
i contenuti del gioco, quindi serve per la macchina su cui è stato creato, non per
essere passato ad altri.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o CARTELLA] [opzioni]
```

Esegue l'esportazione `course` di Forza su ogni cartella di percorso di una
libreria di giri registrati, scrivendo un `<nome>.glb` per ciascuna. Vale solo per
Forza. Chiama direttamente l'esportazione di Forza e non legge `--game`, `--level` o
`--install`.

| Opzione | Predefinito | Significato |
|---|---|---|
| `-o`, `--out CARTELLA` | `courses` | la cartella in cui scrivere (creata se manca) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | la libreria dei giri |
| `--only TESTO [TESTO ...]` | tutti | solo i percorsi i cui nomi di cartella contengono uno di questi testi (senza distinzione tra maiuscole e minuscole) |
| `--force` | disattivato | esporta di nuovo ciò che ha già un `.glb` |
| `--track DIR` | cercata | come per `course` |
| `--margin M` | 80 | come per `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | come per `course` |

Cosa conta come cartella di percorso: una sottocartella diretta della libreria il
cui nome contiene ` (course_`, che è il modo in cui FH Companion le chiama, per
esempio `Example Circuit (course_1200_3400_to_1175_3400)`. La parte da ` (course_`
in poi viene tolta dal nome.

Come si comporta un'esecuzione:

- Un percorso il cui `.glb` esiste già viene saltato (`kept`), a meno che non si usi `--force`, così un'esecuzione interrotta riprende da dove si era fermata.
- Un percorso che non riesce (giri illeggibili, memoria esaurita, nessun terreno...) viene segnalato come `FAILED`, e l'esecuzione prosegue.
- Alla fine stampa una tabella con stato, dimensione in MB, secondi impiegati e nome, poi `<n> of <totale> courses in <cartella>`.
- Il codice di uscita è 1 se un percorso è fallito.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <cartella del tracciato> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [opzioni]
```

È il ritaglio di Forza con tutto indicato a mano: si danno la cartella del tracciato
e una regione, non un giro. È utile quando la zona che vuoi è un riquadro e non un
percorso di guida.

| Opzione | Predefinito | Significato |
|---|---|---|
| `<percorso>` | obbligatorio | una cartella di tracciato di Forza sotto `media\Tracks` (con `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | obbligatorio | il `.glb` da scrivere |
| `--box X0 Z0 X1 Z1` | | la regione, in metri del gioco (x e z, come li riporta la telemetria); gli angoli in qualsiasi ordine |
| `--route FILE` | | un JSON di percorso con `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, come lo scrivono `heat3d_capture route` e `heat3d_capture laps`; letto come UTF-8, con o senza byte order mark |
| `--margin M` | **100** | metri aggiunti attorno ai limiti di un percorso, e larghezza del corridoio quando il percorso ha una linea |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | come per `course` |

Indica esattamente uno tra `--box` e `--route`, altrimenti il codice di uscita è 2.
Con `--route`, il ritaglio sono i `bounds` (`min`/`max`, x e z) del percorso allargati
dal margine. Se il file contiene anche almeno 10 posizioni, il ritaglio si stringe
a un corridoio di `--margin` metri attorno a loro, e le mesh collocate ricevono il
dettaglio in base alla distanza da quella linea. Con `--box`, viene conservato
l'intero riquadro, e il dettaglio va a ciò che sta più vicino al centro del riquadro.

L'altezza non fa mai parte del ritaglio. Un riquadro fuori dalla mappa, o nel mare,
dà "no terrain there" (codice di uscita 1), non un errore sulle coordinate.

```
python -m heat3d_gamefiles terrain "<gioco>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<gioco>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels e level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install CARTELLA]
python -m heat3d_gamefiles level <livello> [-o FILE] [--install CARTELLA] [--textures [PIXEL]]
                                 [--ground-texture [METRI]] [--ground-spacing METRI]
                                 [--navmesh] [--detail-budget N] [--skip TESTO ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` elenca i livelli che un gioco Frostbite installato contiene, con il nome
della loro tabella (`levels/<livello>/<livello>.toc`), con la dimensione e la
provenienza: `Data` per il gioco base, `Update/<pacchetto>` per un aggiornamento, e
quante tabelle ad alta risoluzione vi si aggiungono. Un livello che un aggiornamento
porta con sé ha una piccola tabella di blocchi anche nel gioco base; la tabella con
i pacchetti del livello è il livello (vedi [Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` ne esporta uno: il campo altimetrico del terreno, ogni mesh che i gruppi di
modelli statici del livello collocano, gli oggetti collocati uno per uno, dove si
trovano, e lo sfondo di terreno del livello intorno alla mappa. Con `--textures`,
ogni superficie porta con sé la sua mappa di colore; con `--navmesh`, arrivano
anche le superfici su cui camminano i soldati. Come viene letto è descritto in
[Frostbite](reader-frostbite.md).

| Opzione | Predefinito | Significato |
|---|---|---|
| `<livello>` | obbligatorio | un nome come lo stampa `levels`, una parte unica di un nome, oppure il percorso del `.toc` di un livello |
| `-o`, `--out FILE` | `<livello>.glb` | il `.glb` da scrivere |
| `--install CARTELLA` | la prima installazione Steam il cui `Data` contiene un `layout.toc` | la cartella del gioco |
| `--textures [PIXEL]` | disattivato; 512 se dato senza dimensione | scrive la mappa di colore di ogni superficie, il mip più grande non più grande di PIXEL per lato, e le sue coordinate di texture come le ha il gioco, con un campionatore che ripete (vedi [Formato del file](output-format.md)). L'altezza prende la mappa di colore dello sfondo del terreno dove quella mappa la copre, altrimenti il colore medio dei materiali di superficie del terreno, altrimenti il colore medio dello sfondo intorno. Disattivato, ogni parte è un colore piatto |
| `--ground-texture [METRI]` | disattivato; 0,5 se dato senza dimensione | cuoce i decal del terreno - strade, piste, piazzali, segnaletica dipinta - sopra il colore del suolo, moltiplicato per la mappa di colore del terreno dove il livello ne ha una, nel colore dell'altezza, METRI per pixel, in tasselli di al massimo 4.096 pixel (`ground:terrain x<x> z<z>`). Funziona con o senza `--textures` |
| `--navmesh` | disattivato | aggiunge la mesh di navigazione del livello per il suo agente più piccolo, il soldato (alto 1,8 m, largo 0,4 m), come parte `nav:walkable`: il suolo, i pavimenti, le scale e i tetti su cui un soldato può arrivare, senza i collegamenti (salti, scale, scavalcamenti) tra di essi |
| `--ground-spacing METRI` | 4 | la spaziatura più fine dell'altezza; i nodi più fini vengono campionati più in basso. 0 lascia fuori l'altezza |
| `--detail-budget N` | ogni copia al suo livello più grossolano, più un quarto, almeno 1.500.000 | un tetto di triangoli. Le mesh che costano di più perdono un livello di dettaglio alla volta finché non rientrano; se nemmeno i livelli più grossolani bastano, le copie più piccole vengono lasciate fuori per prime. Lo sfondo del terreno non viene mai reso più grossolano né lasciato fuori |
| `--skip TESTO` | | lascia fuori i gruppi di modelli statici il cui nome di partizione contiene TESTO; ripetilo per più valori. Il livello di una modalità di gioco, per esempio |
| `--by-mesh` | disattivato | per capire cosa sia una parte: una parte per mesh sorgente e materiale, chiamata `<parte> \| <mesh> \| <materiale>`; un file molto più grande |
| `--clamped-uvs` | disattivato | per un renderer che non sa ripetere una texture: taglia ogni triangolo texturizzato in pezzi le cui coordinate stanno tra 0 e 1, e disegna un triangolo che ne servirebbe più di 4 con il colore medio della sua texture, in una parte `<parte> (average colour)` |

Stampa i gruppi e quante copie ha collocato ciascuno, le mesh lasciate fuori e il
motivo, i triangoli per parte (e con `--textures` quante texture, e quante sezioni
hanno trovato la loro mappa di colore), che cosa è il suolo, e con `--navmesh`
quante tessere di navigazione sono state lette. Del livello non viene scritto nulla
oltre alla geometria: nessun nome, nessun metadato (vedi [Formato del file](output-format.md)).

Il budget del terreno è separato: l'altezza e lo sfondo non vengono mai resi più
grossolani da `--detail-budget`; è `--ground-spacing` a dimensionare l'altezza.

Un livello intero è grande: di solito più di dieci milioni di triangoli e diverse
centinaia di MB. `--textures` aggiunge poco al file; un livello ricco di alberi può
arrivare a circa 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8`
lo porta a circa un terzo di quella dimensione.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <livello> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <livello> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <livello> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps e ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

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
| `-o`, `--out FILE` | `<mappa>.glb` | il `.glb` da scrivere |
| `--ground-spacing METRI` | 2 | la spaziatura dei vertici del paesaggio nel file, arrotondata a un numero intero di suoi quad |
| `--no-structures`, `--no-water` | | lascia fuori quella parte |

Stampa i triangoli per parte, quante componenti del paesaggio sono state lette e
quanti dei vertici che ne memorizzano due volte non concordano. Una mappa di 3 km
a 2 m sono circa 4,6 milioni di triangoli del suolo.

## enfusion-worlds e enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install CARTELLA]
python -m heat3d_gamefiles enfusion-world <mondo> [-o FILE] [--install CARTELLA] [--ground-spacing METRI]
                                          [--texture-size PIXEL] [--no-structures] [--trees]
```

`enfusion-worlds` elenca ogni mondo che ha un terreno, per la sua cartella sotto
`worlds/`. `enfusion-world` ne esporta uno: `ground:<mondo>` (il terreno, nei colori
delle sue tessere di supertexture), `water:<mondo>` (il mare, ad altezza zero) e
`structure:<mondo>` (la scatola di ogni modello collocato), nei metri propri del
gioco - x verso est, y in alto, z verso nord. Come si legge e si controlla ciascuno:
[Mondi di Arma Reforger](level-arma-reforger.md).

| Opzione | Predefinito | Significato |
|---|---|---|
| `<mondo>` | obbligatorio | un mondo come lo stampa `enfusion-worlds` |
| `-o`, `--out FILE` | `<mondo>.glb` | il `.glb` da scrivere |
| `--install CARTELLA` | la libreria Steam che contiene il gioco | la cartella del gioco |
| `--ground-spacing METRI` | 2 (quello del terreno) | la spaziatura dei vertici del terreno nel file |
| `--texture-size PIXEL` | 4096 | il lato maggiore dell'immagine di colore del suolo; 0 per il colore piatto |
| `--no-structures` | | lascia fuori i modelli collocati |
| `--trees` | disattivato | colloca anche alberi e altra vegetazione, come scatole |

Stampa i triangoli per parte, quanti vertici di bordo di tessera non concordano,
quante entità contiene il file del mondo e quante scatole sono state collocate, e
che cosa è stato lasciato fuori e perché.

## Variabili d'ambiente {#environment-variables}

| Variabile | Effetto |
|---|---|
| `HEAT3D_OODLE` | percorso di un `oo2core_*_win64.dll`, oppure di una cartella che lo contiene; vedi [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | qualsiasi valore diverso da vuoto, `0`, `false`, `no` disattiva il controllo degli aggiornamenti; vedi [Aggiornamenti](updates.md) |
| `LOCALAPPDATA` | dove vengono cercate la libreria di FH Companion, la cartella utente di BeamNG e la cache degli aggiornamenti |
| `HEAT3D_COURSE` | solo per i test: il percorso usato dal test dei cordoli del gioco installato; vedi [Sviluppo](development.md) |
