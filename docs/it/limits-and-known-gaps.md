---
title: Limiti e lacune note
nav_order: 10
lang: "it"
source: limits-and-known-gaps.md
source_hash: "02df0dd20fc9"
nav_exclude: true
search_exclude: true
---
# Limiti e lacune note {#limits-and-known-gaps}

Che cosa lo strumento non fa, che cosa fa solo in parte, e dove il suo comportamento è irregolare. La maggior
parte delle lacune sono rifiuti voluti. Decodificare senza un file con cui confrontarsi produce un risultato che
sembra giusto e non lo è.

## Giochi {#games}

| Gioco | Esportazione del percorso | Perché no, o fino a che punto |
|---|---|---|
| Forza Horizon | sì | il colore del suolo è un'interpretazione (vedi sotto) |
| BeamNG.drive | sì | nessuna copertura del suolo, texture dei modelli ripetute appiattite |
| Assetto Corsa Rally | sì | modelli a colori piatti; non ancora provato su un giro registrato nel gioco |
| Assetto Corsa EVO | **no** | tutti i contenuti sono in un unico pacchetto offuscato con una chiave, e questo strumento non recupera chiavi |
| Battlefield 6 (esportazione di livello, `level`) | sì, un livello intero | terreno, mesh raggruppate e posizionate singolarmente e le loro mappe colore, la mesh di navigazione dei soldati, fogliame ritagliato; il colore del suolo dell'area di gioco è grossolano (32 m per pixel, oppure un unico colore medio); nessuna trasparenza né mappe delle normali; mesh distruttibili marcate, ma i loro stati distrutti non vengono esportati |
| Giochi Unreal 5 World Partition (esportazione di mappa, `ue-map`) | sì, una mappa intera | il paesaggio esatto; edifici come mesh HLOD semplificate della mappa, non i modelli a pieno dettaglio; corpi d'acqua; niente vegetazione, decalcomanie o colore del suolo |
| Arma Reforger (esportazione di mondo, `enfusion-world`) | sì, un mondo intero | terreno nei suoi colori e mare; edifici, oggetti e rocce come riquadri dei loro modelli, non i loro triangoli; alberi su richiesta (`--trees`), come riquadri; niente laghi, fiumi o entità figlie |
| iRacing | **no** | i circuiti sono distribuiti in un formato protetto che non è un bersaglio di estrazione di file |
| qualsiasi altro | **no** | non esiste un lettore di percorsi; ricostruisci dal gioco con 3DHeat GameCapture, oppure analizza i giri nella scheda Analisi di gara del visualizzatore senza un percorso |

## Motori e formati {#engines-and-formats}

| Formato | Non implementato |
|---|---|
| Unreal `.pak` | versioni prima dell'8; indici solo con hash dei percorsi (i nomi non si possono recuperare); voci nell'elenco di overflow dell'indice (saltate); decodifica dei contenuti `.uasset`/`.umap` da un pak |
| Unreal IoStore | contenitori cifrati (rifiutati, nessuna opzione per la chiave); elenco di un contenitore senza indice di directory (non nomina file); pacchetti versionati; mesh solo Nanite e non in linea; mesh scheletriche; proprietà di classi senza schema; proprietà dei componenti istanziati (layout cambiato nella build del gioco); mesh a spline e componenti decalcomania |
| Unity | formati prima del 22 (Unity 2019 e precedenti); file con type tree incorporati; mesh compresse; ogni classe tranne `Mesh`, quindi niente trasformazioni, materiali o scene; `meshes` su un bundle; `list`/`extract` (usa `meshes`) |
| Frostbite | tabelle offuscate con XOR; il grafo dei livelli del terreno (le maschere si leggono in circa un terzo dei livelli controllati); blueprint di oggetti diversi dalle mesh (logica di gioco, effetti, suoni); livelli di mesh memorizzati in linea; mappe delle normali e altre, alfa diverso dai ritagli; buchi nel terreno; la libreria dei tipi (cifrata nel file system iniziale, non toccata); un comando per elencare o estrarre singoli asset |
| Source 2 | asset compilati (`.vmdl_c`, `.vtex_c`); la mesh di navigazione di CS2 (versione 36) |
| ForzaTech | formati di posizione diversi da quattro short scalati; formati di indice diversi da u16; codici di texture diversi da 0, 9, 13; i livelli di materiale dello shader del terreno; tangenti |
| BeamNG | mesh con skinning e decalcomanie; animazione; copertura del suolo procedurale; scenografia ai margini del mondo |
| Landscape Unreal e mappe World Partition | paesaggio le cui mappe delle altezze vivono nelle celle compilate; livelli di modifica e buchi; mesh paesaggio Nanite; modelli a pieno dettaglio collocati nelle celle; vegetazione; materiali del paesaggio |
| Enfusion | triangoli dei modelli (la geometria `.xob` è compressa in un layout non letto); `.edds` con intestazioni precedenti a DX10; valori di oggetti annidati nei file di mondo (saltati e contati); entità figlie; laghi e fiumi generati; `list`/`extract` su un `.pak` |

## Comportamenti da conoscere {#behaviour-worth-knowing}

- **Il colore del suolo di Forza non è quello del gioco.** La texture cotta viene disegnata dalle mappe delle
  tessere che dicono *dove* ci sono asfalto, erba corta, terreno accidentato e boschi. Usa colori e ombreggiatura
  fissi, perché i livelli di materiale dello shader del terreno non vengono decodificati.
- **`--no-textures` rimuove anche il bordo di Forza.** La divisione asfalto/bordo usa la maschera dell'asfalto che
  arriva con le mappe cotte. Senza texture, le strisce di strada restano intere come strada.
- **Un budget che dai tu può essere superato solo dai cordoli.** I cordoli (e i modelli di superficie di guida di
  BeamNG) non vengono mai semplificati né esclusi, in nessun gioco, quindi un `--detail-budget` più piccolo di quanto
  costano viene superato solo da loro; tutto il resto viene escluso per primo. Vedi
  [Livelli di dettaglio e budget](detail-budget.md).
- **Le opzioni che non si applicano vengono ignorate in silenzio**: `--season` per BeamNG e AC Rally, `--track` per
  BeamNG e AC Rally, `--level`/`--install` per Forza.
- **Il colore del suolo di un livello di Battlefield 6 è grossolano lontano dalle sue decalcomanie.** La mappa delle
  altezze viene colorata dalla mappa colore del fondale del terreno, a 32 m per pixel alla mip più grande che il
  livello fornisce — oppure, dove nessuna mappa di fondale la copre, con il colore medio dei materiali di superficie
  del terreno; `--ground-texture` moltiplica questo per la mappa colore del terreno (a 0,5 m per pixel dove il livello
  ne ha una) e cuoce sopra strade, piazzali, linee della pista, segni di pneumatici e segnaletica, nel colore di
  vernice dei loro materiali dove è impostato e in un colore neutro dove non lo è; le maschere di variazione delle
  strade vengono lasciate fuori. Il gioco mescola i suoi strati di superficie in un grafo di shader che non viene
  letto; l'esportazione dispone i colori degli strati secondo le loro maschere e la pendenza della mappa delle altezze,
  con una regola propria, e un livello le cui pagine di maschera non combaciano ottiene un unico colore. Ogni strato
  è la media della sua mappa colore, non la sua texture. Vedi [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#terrain-layers). I pezzi
  della mappa delle altezze a risoluzioni diverse si incontrano con piccoli gradini.
- **Una mappa colore di Battlefield 6 viene scelta, non letta.** Un blocco shader elenca ogni texture che campiona
  senza dire quale sia il colore; la scelta avviene per nome (vedi [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#textures-and-materials))
  e può prendere un foglio di rifinitura o di dettaglio per una superficie. I fogli di decalcomania (`t_de_...`) perdono
  contro la mappa propria della superficie; la decalcomania di un cartello disegnata come il suo pannello mostrava il
  suo scudo ruotato di un quarto. Campi di distanza, tavolozze e maschere di canale non vengono mai presi. Gli edifici
  del fondale vengono disegnati con i colori della loro tavolozza; le mappe grigie prendono la tinta del materiale
  secondo una regola propria dell'esportatore, dato che i nomi dei parametri sono sottoposti a hash, e un materiale che
  dipinge una mappa grigia attraverso una maschera con più tinte ne ottiene una sola.
- **I buchi nel terreno di Battlefield 6 non vengono scavati.** Dove il suolo percorribile di un livello passa sotto la
  mappa delle altezze, il gioco deve aver scavato il terreno, e l'esportazione non lo fa. Sono stati esclusi come luoghi
  dei buchi: le maschere di strato del terreno (nessuna è concentrata lì), la sua griglia raster di 67 x 67 nodi, un
  valore di altezza riservato (nessuna pagina di altezze contiene 0 o 65.535), i flag dei nodi (tutti uguali), e le mesh
  o gli asset che scavano il suolo: ciò che è collocato sotto il suolo lì sono mesh di roccia e scogliera, e nessun asset
  del livello è dichiarato per buchi, gallerie o grotte. Due alberi raster sono decodificati a sequenze di lunghezza ma
  non collocati, e sono ciò che resta (vedi [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#terrain-layers)).
- **Una variazione di oggetto di Battlefield 6 raggiunge una sezione tramite i suoi gemelli.** La variazione di una copia
  collocata sceglie i blocchi shader delle sue sezioni tramite chiave; dove una mesh non ha un blocco per una variazione,
  si prende la variante di una sezione di un'altra mesh con un blocco predefinito identico (vedi
  [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#textures-and-materials)). Questa è la regola dell'esportatore; una sezione senza un
  gemello che varia mantiene il suo aspetto predefinito.
- **I materiali stratificati di Battlefield 6 vengono disegnati come la loro base e un unico foglio.** Un pannello di
  parete con scritte viene disegnato come il suo intonaco con sopra il foglio delle lettere; gli altri strati del
  materiale (sporco sovrapposto tramite la sua maschera, mappe di dettaglio e di muschio) non vengono miscelati.
- **La mesh di navigazione è quella dell'IA, non quella dei giocatori.** Copre ciò su cui un soldato può camminare:
  il suolo, i piani e le scale, e alcuni tetti, ma non ogni punto alto. I collegamenti tra le superfici (salti, scale,
  scavalcamenti) vengono lasciati fuori.
- **Un livello di Battlefield 6 include il livello di ogni modalità di gioco.** Gli oggetti che solo una modalità colloca
  possono sovrapporsi a quelli di un'altra. `--skip` lascia fuori i livelli per nome.
- **`courses` riguarda solo Forza**, e raccoglie solo le cartelle della libreria chiamate `... (course_...)`.
- **Il sistema di riferimento del giro di BeamNG è presunto** come il sistema di riferimento del visualizzatore
  `(x, z, -y)` che scrive il registratore di 3DHeat. I giri scritti da un altro registratore nel sistema grezzo di
  BeamNG non verrebbero collocati.
- **`list` ed `extract` prendono gli archivi, non ogni formato.** Aprono un `.pak`, un `.utoc` IoStore, un `.vpk`, un
  `.minizip` e uno zip. Un contenitore Unity si legge con `meshes`, un livello Frostbite con `level`, e un `.cdae` o un
  `.ter` è un file e non un archivio (`identify` lo indica). Un `.minizip` senza il suo `ChunkContentsMiniZip<n>.txt`
  accanto viene elencato per numero di voce.
- **I modelli collocati in BeamNG usano le texture ripetute come colori medi**, perché il campionatore del `.glb` le
  blocca e il visualizzatore le impacchetta in un atlante.
- **In pratica solo Windows.** Percorsi Steam sotto `C:\Program Files`, `%LOCALAPPDATA%`, `C:\XboxGames`, e una
  `*_win64.dll` per Oodle. Gli altri sistemi non sono stati provati.

## Non verificato {#unverified}

- Versioni di Python precedenti (lo strumento è stato eseguito con la 3.13).
- Assetto Corsa Rally con un giro registrato nel gioco. È stato provato solo con giri sintetici in sistemi di riferimento casuali.
- Visualizzatori glTF diversi dal visualizzatore di 3DHeat.
- Se il sistema di riferimento di ogni gioco è mancino o destrorso. L'esportazione mantiene il sistema di riferimento
  della telemetria di ogni gioco, quindi giri e percorsi si allineano comunque.
- Il significato della z = 0 locale di `WaterBlock` come sua superficie (BeamNG).
- Il posizionamento Frostbite su giochi diversi da Battlefield 6, e su Battlefield 6 dopo un aggiornamento che cambia il
  layout del membro di gruppo. In quel caso il lettore non trova gruppi e lo dice.
- Se un'esportazione di Battlefield 6 si allinea alle posizioni che il gioco riporta. Le coordinate sono quelle del gioco,
  come per gli altri giochi, ma non è stata ancora sovrapposta una registrazione.
