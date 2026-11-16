---
title: Input dei giri
nav_order: 7
lang: "it"
source: lap-inputs.md
source_hash: "3f335d2fc454"
nav_exclude: true
search_exclude: true
---
# Input dei giri {#lap-inputs}

Un **file di giro** è un elenco di punti x, y, z: dove è andata la tua auto. Il modo più rapido per farne uno
a mano è il CSV descritto sotto in [5. Una tabella `.csv`](#5-a-csv-table).

Un giro dice all'esportazione del percorso **dove è andata l'auto**. Nient'altro al suo interno viene usato:
velocità, comandi e forze g appartengono alla parte di telemetria di 3DHeat. Lo strumento legge le posizioni
nei metri del mondo del gioco, più, dove il file lo dichiara, il gioco e la pista.

Sorgente: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Che cosa accetta `course` {#what-course-accepts}

Il formato viene riconosciuto guardando il file, non il suo nome, tranne che `.npz` e `.csv` si riconoscono
dall'estensione e tutto il resto viene provato come JSON.

### 1. Un documento `heat3d-lap` (qualsiasi gioco) {#a-heat3d-lap-document-any-game}

Scritto dai registratori di telemetria di 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y`, `channels.z` sono obbligatori. Le righe in cui uno dei tre non è un numero finito
  vengono scartate. Gli altri canali vengono ignorati.
- `game` decide l'esportazione (vedi [Comandi](commands.md#which-game)).
- `track` viene usato da Assetto Corsa Rally per provare per prima la tappa indicata.
- Assi: y è l'altezza. I giri di Forza e AC Rally usano gli assi orizzontali del gioco così come il
  registratore li scrive. I giri di BeamNG sono attesi nel sistema di riferimento del visualizzatore,
  `(x, z, -y)` del mondo di BeamNG con Z in alto (vedi [BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html#the-laps-frame)).

### 2. Un file di percorso {#a-route-file}

Scritto da `heat3d_capture route` e `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` è un elenco di `[x, y, z]`. Un file di percorso con `bounds` ma senza posizioni funziona lo stesso:
i suoi due angoli formano una linea degenere ma un riquadro utilizzabile.

### 3. Un file di giro di FH Companion {#an-fh-companion-lap-file}

I file per giro della libreria registrata di FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Una `X`, `Y` o `Z` mancante viene letta come 0. I file sono scritti con un byte-order mark, quindi tutto il
JSON viene letto come `utf-8-sig`.

### 4. Una registrazione `.npz` {#a-npz-recording}

Un archivio NumPy che contiene un array `positions` di forma (n, 3).

### 5. Una tabella `.csv` {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Le colonne chiamate `x`, `y`, `z` (senza distinguere maiuscole e spazi attorno) sono obbligatorie. Le altre
  colonne vengono ignorate.
- Le righe che iniziano con `#` vengono saltate. Se la **prima** riga è `# {json}`, ne vengono letti `game` e
  `track`.
- Le righe che non si leggono come numeri vengono saltate.

### 6. Una cartella {#a-folder}

Una cartella viene cercata **ricorsivamente** per file `.json`, `.npz` e `.csv`, e tutti vengono concatenati in
un'unica linea di guida. È così che si memorizza un intero percorso registrato: FH Companion annida cartelle per
classe, auto, messa a punto ed etichetta.

- `course.json` viene saltato per nome (sono metadati, non un giro).
- Un file che non si legge viene saltato in silenzio. Un file difettoso tra centinaia non fa perdere gli altri.
- La console riporta quanti file di giro sono entrati (`12 laps, 18,400 samples`).
- La cartella riceve il gioco che i suoi file nominano, quando ne nominano **uno solo**. Un file che non nomina
  alcun gioco (un giro di FH Companion, `course.json`, un CSV senza la riga di descrizione) non conta, quindi uno
  di questi tra le registrazioni di un gioco non fa perdere alla cartella il suo gioco. I file che nominano due
  giochi diversi sono un miscuglio, e la cartella non riceve nessuno. Una cartella senza gioco viene esportata
  come Forza, a meno che `--game` non dica altro.
- Se nulla si legge: "no readable laps under <folder>".

### 7. Il nome di un percorso {#a-course-name}

Se l'argomento non è un file o una cartella esistente, viene cercato come nome di percorso nella libreria di
FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. una cartella il cui nome, senza il suffisso ` (course_...)`, è uguale al nome (senza distinguere maiuscole e
   minuscole);
2. altrimenti l'unica cartella il cui nome contiene il nome dato.

Quindi `"Example Circuit"` trova `Example Circuit (course_1200_3400_to_1175_3400)` senza che nessuno conosca le
coordinate. Più corrispondenze sono un errore che le elenca. Un percorso trovato per nome non porta un gioco,
quindi viene esportato come Forza, a meno che `--game` non dica altro.

## Che cosa accetta `terrain --route` {#what-terrain---route-accepts}

`terrain` ha bisogno dei `bounds` del file di percorso (forma 2 qui sopra),
`{"min": [x, y, z], "max": [x, y, z]}`. Senza `bounds`, si ferma con
"<file> has no bounds; --route takes a route file with "bounds": {...}". Il file viene letto come UTF-8 con o
senza byte-order mark, come ogni giro JSON. Se lo stesso file ha anche almeno 10 posizioni leggibili con le
regole sopra, queste restringono il ritaglio a un corridoio e guidano il dettaglio.

## Come viene usato il giro {#how-the-lap-is-used}

| Uso | Dettaglio |
|---|---|
| nome | il nome base del file, o il nome della cartella, senza ` (course_...)`; diventa il nome predefinito del file di output |
| distanza percorsa | la somma degli intervalli tra campioni consecutivi (stampata come `m driven`; per una cartella questo include i salti tra un file e l'altro) |
| riquadro | l'estensione di x e z allargata di `--margin`; l'altezza non viene mai limitata |
| corridoio | le x e le z di ogni campione, vedi [Esportazione del percorso](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html#the-corridor) |
| dettaglio | la distanza di ogni copia collocata dal campione più vicino, vedi [Livelli di dettaglio e budget](detail-budget.md) |

Un giro con meno di due campioni viene rifiutato ("holds no driving").

## Errori {#errors}

| Messaggio | Significato |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | il file non è JSON (e non è `.npz` o `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON di un'altra forma |
| `<file> has no x, y and z columns` | un CSV senza quelle intestazioni |
| `<file> has no positions array` | un `.npz` senza `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | un nome, ma nessuna libreria di FH Companion |
| `'<name>' matches 3 courses: A, B, C` | sii più preciso |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | solo per la ricerca per nome e per `courses` |
