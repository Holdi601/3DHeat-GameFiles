---
title: Sviluppo
nav_order: 14
lang: "it"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Sviluppo {#development}

## Struttura {#layout}

```
heat3d_gamefiles/     il pacchetto: lettori, esportazioni dei percorsi, la riga di comando
heat3d_update/        il controllo delle versioni e l'aggiornamento (vedi Aggiornamenti)
tests/                test sintetici, fixture e test sui giochi installati
docs/                 questa documentazione (docs/wiki è generata da essa)
VERSION               la versione installata, confrontata con le release su GitHub
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Mappa dei moduli {#module-map}

| Modulo | Che cosa fa |
|---|---|
| `__main__.py` | esegue il controllo degli aggiornamenti, poi `cli.main()` |
| `cli.py` | i verbi, `identify`, la distribuzione degli archivi, lo scrittore del percorso di Forza |
| `lapinput.py` | ogni forma del giro in posizioni; ricerca nella libreria di FH Companion |
| `corridor.py` | la fascia intorno alla guida, come raster da 4 m |
| `surfaces.py` | i tipi di suolo, i loro nomi di parte e i colori |
| `glb.py` | lo scrittore `.glb` (parti, normali, colori, texture, quantizzazione) |
| `courseexport.py` | Forza: UV planari delle tessere, divisione strada/bordo, cottura del suolo, sollevamento delle decalcomanie |
| `forzainstall.py` | librerie Steam e Xbox; la pista di Forza a cui appartiene un riquadro |
| `minizip.py` | archivi `.minizip` di ForzaTech e i loro elenchi di nomi |
| `forzatech.py` | `.modelbin`: chunk, buffer, layout, sottomesh, materiali |
| `forzaterrain.py` | tessere di terreno per posizione; classi di superficie |
| `forzatexture.py` | campioni `.pb`; mappe delle tessere; la cottura del suolo |
| `forzamaterial.py` | `AssetManifest.xml`; quali colori di texture ha un modello; stagioni |
| `forzaplacement.py` | posizionamenti `.pgeo`, livelli dei modelli, texture, ritagli, sostituti, il budget |
| `beamng.py` | installazione di BeamNG, file system montato, scena, terreno, materiali |
| `beamngcourse.py` | l'esportazione del percorso di BeamNG |
| `beamngshape.py` | forme compilate `.cdae` |
| `beamngcollada.py` | ripiego su `.dae` |
| `acrally.py` | installazione di AC Rally, tappe, posizionamento dei componenti, volume della texture virtuale |
| `acrallycourse.py` | l'esportazione del percorso di AC Rally: adattamento del sistema di riferimento, suolo, posizionamento |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | pacchetti cotti di Unreal 5 |
| `unversioned.py` | schemi e lettore delle proprietà non versionate |
| `unrealmesh.py` | mesh statiche cotte |
| `unrealtexture.py` | texture e texture virtuali in streaming |
| `oodle.py` | ricerca e chiamata di una libreria Oodle installata |
| `pak.py` | `.pak` di Unreal |
| `unity.py`, `unity_mesh.py` | contenitori, bundle e mesh di Unity |
| `frostbite.py` | `.toc` di Frostbite, tabelle delle sezioni, pacchetti di installazione, posizioni dei chunk, payload |
| `frostbitebundle.py` | bundle inline di Frostbite, manifest dei bundle, il catalogo di un livello, l'elenco dei livelli |
| `frostbiteebx.py` | partizioni RIFF EBX di Frostbite senza una libreria di tipi |
| `frostbitemesh.py` | MeshSet di Frostbite e i suoi chunk di livello di dettaglio |
| `frostbiteterrain.py` | albero di streaming del terreno di Frostbite, pagine di altezza, la mesh del suolo |
| `frostbitematerial.py` | texture di Frostbite (mip BC1/BC3/BC7), depositi di blocchi shader, scelta della mappa colore |
| `frostbitedecals.py` | decalcomanie del terreno di Frostbite e la cottura del suolo |
| `frostbitenav.py` | tessere della mesh di navigazione di Frostbite: le superfici percorribili dai soldati |
| `frostbitelevel.py` | gruppi di modelli statici di Frostbite, posizionamento, l'esportazione `level` |
| `vpk.py` | VPK di Source 2 |
| `unreallandscape.py` | componenti paesaggio di Unreal 5: mappe di altezza nella mesh del suolo (`ue-map`) |
| `unreallevel.py` | mappe World Partition di Unreal 5: elenco, strutture HLOD, acqua, l'esportazione `ue-map` |
| `enfusion.py` | `.pak` di Enfusion, `.edds`, tessere del terreno, `resourceDatabase.rdb` |
| `enfusionworld.py` | mondi di Arma Reforger: file `.ent`, scatole, l'esportazione `enfusion-world` |
| `forzacars.py` | ogni auto di Forza a basso dettaglio in `.h3dcars` (`cars`) |

Tutti i moduli sono su GitHub in
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Eseguire i test {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` imposta `testpaths = tests` e `-q`. Due tipi di test contano, per motivi diversi:

- **I test sintetici** costruiscono archivi byte per byte e girano ovunque. Fissano le strutture dei campi che
  in qualche momento erano sbagliate: la base a 64 bit dei segmenti `.minizip` e il suo padding di
  allineamento, la scappatoia della dimensione dei blocchi del pak, l'u32 dell'intestazione Unity tra due
  int64, l'indice `0x7FFF` del VPK, la divisione x della normale di Forza.
- **I test sui giochi installati** girano sui file reali quando il gioco è sul computer, e **vengono saltati**
  (non falliscono) quando non lo è. Sono l'unica cosa che intercetta un layout giusto per un file piccolo e
  sbagliato per uno grande.

### Fixture {#fixtures}

| Fixture | Costruisce |
|---|---|
| `tests/forza_fixtures.py` | archivi `.minizip` (con la base a 64 bit, il padding, codec misti), manifest, modelli `.modelbin` e terreno, campioni `.pb` |
| `tests/beamng_fixtures.py` | una piccola installazione di BeamNG: `gameengine.zip`, `content`, un zip di livello con un terreno da 64 m, una striscia d'asfalto, una decalcomania stradale, un guardrail, un prefab, un oggetto di foresta, il mare, materiali e forme `.cdae` nel layout documentato |
| `tests/unreal_fixtures.py` | un contenitore IoStore con una directory, un pacchetto zen, un blocco di proprietà non versionate |
| `tests/frostbite_fixtures.py` | tabelle, bundle, partizioni EBX, mesh e pagine di terreno di Frostbite, byte per byte |

### File di test {#test-files}

| File | Copre |
|---|---|
| `test_minizip.py` | lettura, la base a 64 bit, tabelle dei bundle pari e dispari, rifiuti, il file dei nomi |
| `test_forzatech.py` | la tabella dei chunk e la catena, rifiuti; installato: catene e tag dei modelli reali |
| `test_forza_geometry.py` | posizionamento nel mondo, layout dei vertici, formati rifiutati, sottomesh, normali e UV |
| `test_forzaterrain.py` | la griglia delle tessere (1023 contro 512 m), il ritaglio, l'estrazione |
| `test_forzatexture.py` | intestazione dei campioni, decodifica, lo scaffale delle texture, la cottura del suolo |
| `test_forzamaterial.py` | il manifest, i nomi, gli hash dei materiali, la scelta del colore, le stagioni |
| `test_forzaplacement.py` | il record `.pgeo`, la collocazione delle copie, i livelli, le varianti, le superfici trasparenti, un intero riquadro, il budget, il colore segnaposto, il budget automatico; installato: i cordoli sul suolo |
| `test_forzainstall.py` | ricerca del gioco, scelta della pista |
| `test_courseexport.py` | UV delle tessere, il piano delle parti, il sollevamento delle decalcomanie |
| `test_course_cli.py` | i verbi `course` e `courses` interi su una pista sintetica; `terrain --route` con un byte-order mark, e senza `bounds` |
| `test_archive_cli.py` | `identify`, `list` ed `extract` su ogni archivio con un lettore (`.pak`, IoStore, `.vpk`, `.minizip` con e senza i suoi nomi, zip, `.cdae`, `.ter`); errori come una riga e un codice di uscita: un pak cifrato, un contenitore cifrato, un file che non è un archivio, una `--key` sbagliata |
| `test_corridor.py` | la fascia, il taglio del terreno con essa |
| `test_lapinput.py` | ogni forma del giro, il riquadro, gli errori, la ricerca del nome della pista, quale gioco è una cartella |
| `test_surfaces.py` | quali nomi decidono una superficie, quali no, i nomi delle parti |
| `test_glb.py` | il file è valido, i nodi portano la classe, i rifiuti, la quantizzazione |
| `test_beamng.py` | forme, livello, categorie, trovare il livello da un giro, il percorso, il ripiego Collada; installato: `.cdae` contro `.dae`, ogni livello si apre |
| `test_acrally.py` | contenitori, pacchetti, proprietà, trasformazioni, l'adattamento del sistema di riferimento, le parti dei modelli collocati e il budget, texture virtuali; installato: tappe e il colore del suolo pre-calcolato |
| `test_pak.py` | footer, voci, la scappatoia della dimensione dei blocchi, rifiuti; installato: offset e SHA-1 |
| `test_unity.py` | rifiuti; installato: la tabella degli oggetti copre il file, stringhe di versione, limiti delle mesh |
| `test_frostbite.py` | intestazioni con segno contro offuscate, rifiuti, pacchetti di installazione (due pacchetti con lo stesso numero di blob); installato: ogni tabella, superbundle, catene delle sezioni, id distinti, payload campionati dal pacchetto giusto |
| `test_frostbitelevel.py` | id di chunk abbinati alle loro posizioni, bundle inline, manifest, una MeshSet con una sezione d'ombra e UV, un membro di gruppo, la convenzione delle trasformazioni, un terreno a due livelli, scelta della mappa colore, un chunk di texture senza i mip più grandi, il campionatore che ripete, record di decalcomanie, una decalcomania composta dal suo alfa, un foglio di decalcomanie che perde contro la mappa propria di una superficie, il terreno con le sue maschere e le mappe colore, la tinta di un blocco, una mappa grigia dipinta con essa, un vertice della tavolozza al centro del suo campione, la griglia delle pendenze ridistribuita in modo bilineare, la sovrapposizione di un oggetto disegnata attraverso il suo unwrap, una variazione il cui blocco è indicizzato dal suo hash e raggiunto tramite un blocco gemello, un foglio di lettere posato dalle sue quarte coordinate di texture sopra la superficie su cui è dipinto, la vernice di una decalcomania letta dal suo materiale, linee di pista e segni di pneumatici disegnati, mappe a canale singolo decodificate, mesh distruttibili marcate nelle loro parti ed extra, mesh di blockout, cinematiche e illuminazione escluse e una disposizione di mappe colore non letta, mappe di ritaglio e i loro PNG mascherati a due facce, tessere di fondale denominate dalla loro mesh; installato: le decalcomanie del terreno del livello, il catalogo del livello più grande, mesh dentro i loro limiti, membri di gruppo, vegetazione posata sul terreno decodificato |
| `test_vpk.py` | la directory, i rifiuti, gli archivi divisi; installato: le mappe si aprono, i CRC corrispondono, la mesh di navigazione |
| `test_enfusion.py` | `.pak` di Enfusion, `.edds`, tessere del terreno e file dei mondi; l'esportazione `enfusion-world` |
| `test_forzacars.py` | il file `.h3dcars` che scrive il verbo `cars` |
| `test_unreallevel.py` | paesaggio di Unreal 5, strutture HLOD, acqua; l'esportazione `ue-map` |

## Test sui giochi installati {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
trova i giochi per i test. `steam_common()` elenca la cartella `steamapps\common` di ogni libreria Steam
(comprese le cartelle proprie di Steam), e `installed(*globs)` restituisce i percorsi che corrispondono a uno
qualsiasi dei glob sotto di esse, in modo ricorsivo dove un glob ha `**`. Ogni test decide ciò che gli serve:

| Test | Cerca | Viene saltato con |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` con un indice **non cifrato**, fino a 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` in `*/*_Data` o `*/*/*_Data` che il lettore accetta, fino a 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, fino a 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | i circuiti della libreria dei giri di FH Companion (partenza e arrivo entro 50 m), con più giri, che `find_track` colloca; oppure `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Per eseguire i test di un solo gioco, oppure per puntare il test del cordolo di Forza su un percorso:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

I test sui giochi installati leggono solo dai giochi. Non scrivono nulla nelle cartelle di gioco. Gli output
dei test vanno nelle cartelle temporanee di pytest.

## Convenzioni {#conventions}

- **Rifiutare piuttosto che indovinare.** Ogni lettore solleva la propria eccezione
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) con un messaggio che dice che
  cosa è stato trovato e perché non è stato letto.
- **Controllare sul formato stesso.** Un hash, un CRC, una catena di offset, un riquadro salvato, la guida che
  sta sul suolo. Non "non si è bloccato".
- **Nessuna chiave, nessun codice proprietario incluso.** Vedi [Regole e licenze](rules-and-licences.md).
- **I dati riservati restano fuori.** File di gioco, esportazioni, giri, registrazioni e schermate non entrano
  mai nel repository. `.gitignore` le esclude per cartella e per tipo. I test usano dati sintetici e giochi
  installati, mai contenuti di gioco inclusi nel repository.
