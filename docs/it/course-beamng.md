---
title: BeamNG.drive
nav_order: 2
lang: "it"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Esportazione del percorso: BeamNG.drive {#course-export-beamngdrive}

L'esportazione BeamNG legge un livello nel modo in cui il gioco lo monta, poi scrive
lo stesso tipo di file che scrive l'esportazione di Forza: il terreno per ogni quadrato
di 512 m con una texture cotta, strada e terreno sciolto come parti proprie, modelli
collocati per categoria, e l'acqua.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <cartella del livello>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Fonti: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (installazione, file system, scena, terreno, materiali),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (l'esportazione),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) e
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (forme).
Formati dei file in dettaglio: [File di BeamNG](reader-beamng.md).

## Il sistema di riferimento del giro {#the-laps-frame}

L'esportazione `course` si aspetta che le posizioni di BeamNG siano nel **sistema
di riferimento del visualizzatore**: `(x, z, -y)` del mondo con Z in alto di BeamNG, in
metri. È la rotazione che applica il registratore di telemetria di 3DHeat. Il
comando riporta il giro nel sistema di BeamNG (`(x, -z, y)`), lavora lì, e scrive
di nuovo tutto nel sistema del visualizzatore. È una rotazione, non uno specchio, quindi
nulla esce speculare. Un giro registrato nel sistema grezzo di BeamNG non verrebbe
posizionato. Non è stato provato con altri registratori.

Il gioco viene riconosciuto come BeamNG quando il file `heat3d-lap` dice
`"game": "beamng"`, oppure quando passi `--game beamng`.

## Trovare l'installazione {#finding-the-install}

- `--install <cartella>`: la cartella che contiene `gameengine.zip` e `content`.
- In alternativa, si controlla `steamapps\common\BeamNG.drive` in ogni libreria Steam
  cercando quei due elementi.
- Se nessuna delle due funziona: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Il file system {#the-file-system}

BeamNG distribuisce archivi zip semplici e li monta in un unico file system a cui
i livelli fanno riferimento (`/art/shapes/...`, `/assets/materials/...`). L'esportazione
costruisce la stessa cosa: un unico indice senza distinzione tra maiuscole e minuscole
su

1. `gameengine.zip`,
2. ogni `*.zip` sotto `content`, eccetto `content\vehicles\*` e gli archivi i cui
   nomi iniziano con `art_sound` o `audio`,
3. i contenuti dell'utente, con il layout più recente per primo: sotto
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` e `%LOCALAPPDATA%\BeamNG.drive`, la cartella
   `current` e la cartella di versione con il numero più alto. Da ciascuna: `mods\*.zip`,
   ogni cartella in `mods\unpacked`, e la cartella utente stessa se ha una cartella
   `levels`.

Le aggiunte successive hanno la precedenza, come nel gioco, quindi una mod sostituisce
ciò che sovrascrive. Le mod sono sempre incluse in un'esportazione del percorso.

I percorsi che un livello nomina vengono risolti come lo fa il gioco: così come sono
scritti, poi relativi al file che li ha nominati, e per ciascuno anche come il `.dds`
in cui una texture è stata compilata, il `.cdae` in cui un `.dae` è stato compilato,
oppure tramite un file `.link` che punta dentro `/assets`.

## Quale livello {#which-level}

Senza `--level`, ogni livello viene valutato in base a quanto del giro si trova su di esso:

- Vengono usati fino a 500 campioni del giro, distribuiti in modo uniforme.
- Per il `TerrainBlock` di ogni livello, l'estensione del terreno viene letta dai
  primi cinque byte del suo file `.ter`, quindi un livello lontano dal giro non
  costa nulla. Se almeno il 30% dei campioni è dentro l'estensione, si leggono le
  altezze. Un campione conta come **sul** terreno quando si trova tra 1 m sotto e 3 m
  sopra di esso (`ON_GROUND`), perché il punto di riferimento di un'auto è la sua
  carrozzeria, non i pneumatici.
- Se nessun livello raggiunge il 50% o più, i livelli vengono valutati anche sulle
  loro **strade**. Alcuni livelli proseguono oltre la loro mappa delle altezze (i
  bordi continuano come lastre di roccia). Un campione è su una strada quando si
  trova entro la mezza larghezza della strada più 4 m (almeno 6 m) da un segmento di
  `DecalRoad`, e tra 2 m sotto e 4 m sopra di essa.
- Vince il livello migliore, se raggiunge almeno il 30%. Altrimenti l'esportazione
  si ferma ed elenca i tre migliori: "the lap does not lie on any installed level's terrain
  (best: ...). Name the level with --level."

La console scrive `on <livello>: 87% of the lap lies on its terrain` (oppure `roads`).
`--level` viene confrontato senza distinzione tra maiuscole e minuscole con i nomi
delle cartelle dei livelli.

## Leggere il livello {#reading-the-level}

Di cosa è fatto un livello, ogni parte controllata sui livelli distribuiti
(dettagli in [File di BeamNG](reader-beamng.md)):

- **Scena**: `levels\<nome>\main\**\*.level.json` (un oggetto JSON per riga, oppure
  un array JSON), oppure un file `.mis` per i livelli più vecchi. Lo strumento legge
  gli oggetti `TSStatic` (modelli collocati, saltando quelli nascosti), gli oggetti
  `Prefab` (annidati fino a 8 livelli di profondità, file `.prefab` di TorqueScript
  o `.prefab.json`), gli oggetti `DecalRoad` (strade dipinte), `TerrainBlock`,
  `WaterPlane`, `WaterBlock` e `River`.
- **Oggetti della foresta**: `levels\<nome>\forest\*.forest4.json`, tipizzati tramite
  i record di `managedItemData.json`. Barriere, recinzioni e rocce sono oggetti della
  foresta tanto spesso quanto lo sono gli alberi.
- **Terreno**: il campo altimetrico `.ter` e la sua mappa di strati.
- **Materiali**: ogni `*.materials.json` fuori da `levels\`, più quelli di questo livello.

## Il corridoio e i decal delle strade {#the-corridor-and-the-road-decals}

Il corridoio è `--margin` metri attorno al giro, nel piano x/y di BeamNG (vedi
[Esportazione del percorso](course-export.md#the-corridor)). Un corridoio di
portata di `margin + 60 m` seleziona i candidati.

**I decal stradali** (`DecalRoad`) sono dove si trova gran parte delle strade di
BeamNG: dipinti sul terreno, non modellati. I decal la cui estensione tocca il
corridoio di portata vengono presi nell'ordine di disegno del gioco
(`renderPriority` decrescente, poi ordine nel file), e disposti come nastri:

- I nodi (x, y, z, larghezza) vengono interpolati da una **spline di Catmull-Rom
  centripeta** circa ogni 1 m. Il tipo uniforme si riavvolge su se stesso dove i
  nodi si addensano in una curva a gomito. Le strade ad anello si chiudono.
- Ogni bordo prende l'altezza del terreno dove il terreno è entro 1,5 m dall'altezza
  della strada, e mantiene l'altezza della strada altrove (su un ponte).
- Il nome del materiale decide cosa dipinge un decal:

| Tipo | Il nome del materiale contiene (vince la prima corrispondenza) |
|---|---|
| segni di pneumatici | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| sovrapposizione (solo estetica) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| segnaletica | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| sciolto | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| strada | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| sovrapposizione | qualsiasi altra cosa |

## Il suolo {#the-ground}

Il campo altimetrico del terreno dentro il corridoio diventa triangoli:

- Un quad per ogni quadrato del terreno il cui centro è nel corridoio. I quadrati con
  strato 255 (buchi) vengono saltati. Ogni quad sono due triangoli, con la diagonale
  che alterna nel modo in cui lo fa il terreno di Torque.
- Le altezze sono `position.z + h * maxHeight / 65535`. Le normali vengono dalle
  differenze di altezza.
- Ogni quadrato viene classificato in base al suo **strato**: il nome dello strato con
  il modello di suolo e l'annotazione del materiale del terreno. Parole come
  "paved" lo rendono `road`, `grass/forest/rock/moss/leaves/cliff/stone` lo rendono
  `terrain`, e parole di materiale sciolto lo rendono `loose` (ghiaia e terra).
  Tutto il resto è `terrain`.
- Poi i **decal di strada e sciolti sovrascrivono** i quadrati che coprono, nell'ordine
  di disegno, quindi vince l'ultimo decal dipinto.
- I vertici vengono divisi per quadrato di 512 m (`floor(x / 512)`, `floor(y / 512)`),
  così ogni parte corrisponde esattamente a un'immagine: `u = (x - x0) / 512`,
  `v = 1 - (y - y0) / 512`.

La console stampa `what the ground is made of` con il numero di triangoli per tipo.

### Superficie di guida modellata {#modelled-driving-surface}

I circuiti di BeamNG sono modelli tanto spesso quanto sono terreno. Il tracciato di
un autodromo può essere una mesh unica, con le sue linee, la gomma e i cordoli come
mesh proprie sopra. Quindi le mesh collocate nelle categorie strada, cordoli,
banchina, oggetti di scena e ponti vengono cercate per la superficie di guida. Per
materiale:

| Superficie | Decisa da (prima corrispondenza) |
|---|---|
| segni di pneumatici | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` nel nome, nel tipo di suolo o nell'annotazione |
| segnaletica | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` nel nome del materiale |
| cordoli | `rumble`, `kerb`, `curb` |
| strada | tipo di suolo `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, oppure il nome contiene `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| sciolto | tipo di suolo `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| banchina | `sidewalk` |
| (la categoria propria del modello) | per i modelli già classificati come strada, cordoli o banchina |

Di quei materiali, i triangoli **rivolti verso l'alto** (normale z sopra 0,5) dentro
il corridoio vengono tolti dal modello e diventano suolo. Vengono dipinti nella
texture cotta della tessera e scritti come parti come
`ground:road 3_-2 asphalt_light`. Segnaletica e segni di pneumatici vengono solo
dipinti. I triangoli rimanenti del modello restano con il modello. Questi modelli
non vengono mai semplificati o lasciati fuori dal budget, perché un percorso
grossolano è un percorso sbagliato.

## La texture cotta del suolo {#the-baked-ground-texture}

Ogni quadrato di 512 m che ha suolo riceve un'immagine di `--texture-size` pixel
(2048 = 25 cm per pixel), disegnata come il gioco disegna il suo suolo:

1. **Strati del terreno.** Per ogni pixel, gli strati dei quattro quadrati del terreno
   intorno vengono mescolati in modo bilineare. Ogni strato è colorato come lo colora
   il gioco: la **base map** del materiale stesa su `diffuseSize` metri (oppure
   sull'intero terreno), poi le mappe **detail** e **macro** come sovrapposizioni in
   grigio (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutro). I loro valori
   predefiniti si ripetono ogni 2 m e ogni 60 m, con intensità 0,5 e 0,3, salvo che
   il materiale dica altrimenti. Uno strato senza materiale prende il colore piatto
   della sua superficie. La riga 0 della base map è nord.
2. **Decal stradali** dipinti solo sul terreno, nell'ordine di disegno, ciascuno con la
   sua texture, mappa di opacità, tinta e opacità, lungo il nastro. I livelli
   distribuiti usano priorità intorno a 12-16 per le basi in asfalto, 10 per la
   segnaletica e 4 per la gomma.
3. **Superficie di guida modellata** vista dall'alto: prima le basi, poi le
   sovrapposizioni, ciascuna nella texture ripetuta del modello, a un texel per pixel
   di cottura.
4. **I decal che si proiettano anche sugli oggetti** (`overObjects`), per ultimi.

Con `--no-textures` non viene cotto nulla: le parti del suolo prendono colori piatti,
e la segnaletica e i segni di pneumatici modellati diventano parti proprie, sollevate
di **3 cm**.

## Modelli collocati {#placed-models}

I candidati sono ogni `TSStatic`, figlio di prefab e oggetto della foresta la cui
origine si trova nel corridoio di portata. Un candidato viene disegnato se il
riquadro di delimitazione mondiale della sua forma tocca il corridoio.

La **categoria** viene dall'annotazione del livello e dal percorso della forma. Vince
la prima regola che corrisponde:

| Categoria | Annotazione | Il percorso o il nome contiene |
|---|---|---|
| sfondo (mai disegnato) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| cordoli | | `kerb`, `curb`, `rumble` |
| strada | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| banchina | `SIDEWALK`, `COBBLESTONE` | |
| alberi (solo con `--trees`) | `NATURE` | tree, foliage, bush, grass, plant e parole simili |
| rocce | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barriere | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| cartelli | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| ponti | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastrutture | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| edifici | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| oggetti di scena | | qualsiasi altra cosa |

**Le forme** vengono lette dal `.cdae` compilato, oppure dal `.dae` di Collada dove
non esiste una cache (mod). Una forma che non si può leggere viene contata:
`N copies of M models could not be read`. I materiali chiamati o texturizzati
`invisible`, `collision` o `nodraw` non vengono mai disegnati.

**Texture.** I modelli vengono raggruppati per categoria e materiale in parti chiamate
`structure:<categoria> <materiale>` (oppure `ground:kerbs <materiale>`). Un gruppo
riceve la texture di colore del suo materiale fino a **256 px** solo se le sue UV
restano entro 0-1 (98% dei vertici tra -0,02 e 1,02). Il visualizzatore impacchetta le texture
in un atlante e non ne può ripetere una. Un gruppo la cui texture si ripete viene
disegnato con il colore medio della texture (ponderato per alfa, in sRGB, moltiplicato
per la tinta del materiale), oppure con il colore della categoria se non ha texture.

**Dettaglio.** Segue lo schema comune descritto in
[Livelli di dettaglio e budget](detail-budget.md). I livelli di dettaglio di BeamNG
sono i `details` della forma (dimensione in pixel più grande per prima). Sopra il
budget, prima vanno le copie più lontane. Cordoli e modelli che portano superficie
di guida non vengono mai semplificati o lasciati fuori.

`--no-placed` elimina le strutture ma conserva la superficie di guida modellata.
`--trees` aggiunge la categoria degli alberi.

## Acqua {#water}

| Fonte | Disegnata come |
|---|---|
| `WaterPlane` (il mare) | un quad di 4 m all'altezza dell'acqua per ogni cella del corridoio in cui nessun terreno raggiunge quell'altezza |
| `WaterBlock` | un quad, il quadrato unitario a z locale = 0 nella trasformazione del blocco (quindi la sua scala ne fissa la dimensione), se tocca il corridoio; non è verificato se z = 0 sia la superficie del blocco |
| `River` | un nastro attraverso i suoi nodi, se tocca il corridoio |

Tutta l'acqua è una sola parte piatta, `water:water`.

## Non disegnato {#not-drawn}

- La copertura del suolo (erba procedurale).
- Scenografia collocata ai margini del mondo (`backdrop` e simili).
- Texture ripetute dei modelli, che risultano come colore medio (vedi sopra).
- Mesh skinnate (veicoli, personaggi) e mesh di decal dentro le forme.

## Controlli alla base {#checks-behind-it}

Come dichiarato nel sorgente, misurato sui livelli distribuiti:

- I nodi della strada si trovano sul terreno entro 1-2 cm (mediana) sui livelli controllati, con `h * maxHeight / 65535` e le righe lungo +y. `h / 32` o l'altro ordine degli assi sbagliano di decine o centinaia di metri.
- Le sezioni di rotaia concatenate lungo una strada corrono lungo la riga 0 di `rotationMatrix` (la grande maggioranza).
- La rotazione del nodo `.cdae` va trasposta. Con questo, i limiti mondiali coincidono con il `.dae` sorgente fino al millimetro. Il modo più ovvio di farlo le sbaglia di 38 cm (mediana).
- Esportato su diversi livelli distribuiti di ogni tipo, in secondi o minuti ciascuno.
