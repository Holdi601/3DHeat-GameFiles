---
title: Lettori di archivi
nav_order: 9
lang: "it"
source: archive-readers.md
source_hash: "0f1064f05cfd"
nav_exclude: true
search_exclude: true
---
# Lettori di archivi {#archive-readers}

Un **contenitore** (o archivio) è un unico file grande in cui un gioco impacchetta molti file. Un
**CRC** o hash è una breve impronta di alcuni byte: se corrisponde, i byte sono stati letti bene. Un
**riquadro di contenimento** (bounding box) è il riquadro più piccolo che racchiude un modello.

Sotto i comandi ci sono i lettori dei contenitori che i giochi distribuiscono. I loro formati non sono
documentati, a parte il VPK di Valve e il `.cdae` di BeamNG, quindi "supportato" deve voler dire
**verificato su file reali**, non "non si è bloccato". Ogni lettore controlla se stesso con qualcosa che
il formato garantisce: un hash, un CRC, una catena di offset che deve chiudersi, un riquadro di
contenimento salvato. Quando un controllo fallisce, il lettore si rifiuta e mostra un messaggio invece
di indovinare. Una mesh sbagliata sembra giusta finché non la metti accanto al tracciato.

| Lettore | Modulo | Legge | Non legge | Raggiunto da |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versioni 8-12: indice, voci, blocchi Zlib/Gzip/Oodle, AES con una chiave che fornisci tu | versioni prima dell'8, indici solo con hash dei percorsi, voci di overflow, contenuti degli asset | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, verificati sulla v8), pacchetti zen, proprietà non versionate per alcune classi di componenti, mesh statiche cotte, texture e texture virtuali in streaming | contenitori cifrati, pacchetti versionati, mesh solo Nanite, proprietà di altre classi | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | blocchi Oodle, tramite una libreria già presente sul computer | tutto ciò che non ha una libreria del genere; non viene mai incluso | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | formato `SerializedFile` 22 e successivi (Unity dal 2020 al 6000), bundle `UnityFS`, mesh non compresse, `.resS` incluso | formati precedenti al 2020, type tree incorporati, mesh compresse, qualsiasi classe tranne `Mesh` | `identify`, `meshes` |
| [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | alberi `.toc` DbObject e tabelle binarie delle sezioni, pacchetti di installazione, posizioni dei chunk, bundle inline e i loro manifest, partizioni RIFF EBX, mesh MeshSet, il campo di altezze del terreno, texture BC1/BC3/BC7 e i loro blocchi shader, posizionamento dei gruppi di modelli statici | tabelle offuscate con XOR, il colore del terreno vicino al suolo e i buchi, mappe delle normali, alfa diverso dai ritagli | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versioni 1 e 2, archivi divisi, dati di precaricamento, controllo CRC | asset compilati (`.vmdl_c`, `.vtex_c`), il formato della mesh di navigazione di CS2 | `identify`, `list`, `extract` |
| [ForzaTech](https://holdi601.github.io/3DHeat-Ext-Forza/reader-forzatech.html) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, memorizzati), geometria `.modelbin`, campioni `.pb` (BC1, BC7, RGBA), posizionamenti `.pgeo`, hash delle texture dei materiali | altri formati di vertici e indici, altri formati di texture, livelli di materiale del terreno dello shader | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` ed `extract` (`.minizip`) |
| [File di BeamNG](https://holdi601.github.io/3DHeat-Ext-BeamNG/reader-beamng.html) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | il file system montato dagli zip, scene JSON e TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiali | mesh con skinning e decalcomanie, sequenze animate, copertura del suolo procedurale | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` ed `extract` (zip) |

## Regole che ogni lettore segue {#rules-every-reader-follows}

- **Nessuna chiave distribuita, nessuna chiave recuperata.** Un archivio cifrato si apre solo con una
  chiave che passi tu (un `.pak` di Unreal, con `--key`). Un contenitore IoStore cifrato viene
  rifiutato. Niente cerca una chiave in un eseguibile o legge la memoria di un altro processo. Vedi
  [Regole e licenze](rules-and-licences.md).
- **Nessun codice proprietario incluso.** Oodle viene caricato da un gioco o da un motore già
  installato sul computer.
- **Rifiutare piuttosto che indovinare.** Una versione, un codec, un formato di vertici o di texture
  sconosciuto genera un errore specifico, per esempio
  `texture format 42 has not been identified; refusing to guess`.
- **Sola lettura.** Nessun lettore scrive dentro una cartella di gioco. Le esportazioni vanno dove
  indichi tu.

## Che cosa vuol dire "verificato" {#what-verified-meant}

Le cifre di verifica citate in queste pagine vengono dalle docstring dei moduli. Sono state misurate su
giochi installati mentre ogni lettore veniva scritto. I test sintetici (vedi [Sviluppo](development.md))
fissano la struttura dei campi. I test sui giochi installati ripetono alcuni controlli quando il gioco è
presente sul computer, altrimenti vengono saltati. Le cifre che nessun test copre non sono state
ricontrollate da allora.
