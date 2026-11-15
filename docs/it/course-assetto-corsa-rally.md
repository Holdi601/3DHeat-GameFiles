---
title: Assetto Corsa Rally
nav_order: 3
lang: "it"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Esportazione del percorso: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally è costruito su Unreal Engine 5 (5.6.1, una build modificata) e distribuisce i suoi
contenuti come contenitori IoStore. Nessuno di essi è cifrato. L'esportazione trova la tappa e
l'orientamento degli assi a partire dal giro. Scrive le tessere di terreno della tappa stessa, divise in
strada e terreno e texturizzate con il colore del suolo pre-calcolato della tappa, e colloca gli altri
modelli a colori piatti per categoria.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Sorgenti: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (installazione, tappe, posizionamento),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (l'esportazione).
I lettori Unreal sottostanti sono descritti in [Unreal 5 IoStore](reader-unreal-iostore.md),
e la decompressione in [Oodle](reader-oodle.md).

**Stato:** verificato sul gioco installato con giri generati in un sistema di riferimento casuale su ogni tappa, e
ha trovato la tappa e il sistema di riferimento giusti ogni volta. Nessun giro registrato nel gioco stesso è ancora
passato da qui.

## Trovare l'installazione {#finding-the-install}

- `--install <cartella>`: la cartella del gioco, oppure la sua `Content\Paks`, oppure qualsiasi cartella
  che contiene file `.utoc`. Lo strumento controlla `<cartella>`, poi
  `<cartella>\acr\Content\Paks`, poi `<cartella>\Content\Paks`.
- Altrimenti viene controllata allo stesso modo la cartella `steamapps\common\Assetto Corsa Rally` di
  ogni libreria Steam.
- Ogni `.utoc` in quella cartella viene aperto come un unico contenitore. I contenitori che non si
  aprono vengono saltati. Se nessuno si apre: "no readable IoStore containers in ...".

La maggior parte dei blocchi è compressa con Oodle, e per averne una libreria viene cercata sul computer
(in ogni libreria Steam). Vedi [Oodle](reader-oodle.md).

Il gioco viene riconosciuto come AC Rally quando il file del giro dice `"game": "assetto-corsa-rally"`
(o `acrally`), oppure quando passi `--game acrally`.

## Che cos'è una tappa {#what-a-stage-is}

Una tappa è una mappa **World Partition**:

- `Content\Levels\<Stage>.umap` colloca il terreno lontano.
- Le celle compilate in `Content\Levels\<Stage>\_Generated_\*.umap` collocano tutto il resto.

Un livello conta come tappa se la sua cartella dell'ambiente, `Content\Environments\<Stage>\`, ha una
cartella `MeshesTrack`. Lo strumento non si basa sui nomi delle tessere, perché una tappa può chiamarle
con il nome di un paese invece che con quello della sua mappa. `--level` viene confrontato senza
distinguere maiuscole e minuscole con questi nomi di mappa. Un nome sbagliato elenca le tappe
disponibili.

Non c'è **nessun paesaggio**. Il suolo è fatto di mesh statiche:

| Tessere | Percorso | Diventano |
|---|---|---|
| tessere della pista, circa 175 m, divise in due | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` e `..._Terrain_k` | `ground:road` e `ground:terrain` (una tessera di pista non divisa, come un lago ghiacciato, è tutta strada) |
| terreno lontano, tessere da 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Leggere i posizionamenti {#reading-the-placements}

Ciò che colloca una mesh è un `StaticMeshComponent`: la sua `StaticMesh`, e i suoi `RelativeLocation`,
`RelativeRotation` e `RelativeScale3D`, ciascuno relativo al componente a cui è agganciato
(`AttachParent`), risalendo fino alla radice dell'attore, che è nel mondo.

- Le proprietà sono **non versionate**: memorizzate per posizione nell'elenco delle proprietà della
  classe, non per nome. Vengono lette con gli schemi di
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (vedi [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Un valore uguale a quello del modello del componente (il suo archetipo in un Blueprint) non viene
  memorizzato, quindi prima si leggono ricorsivamente i valori del modello, e i valori propri del
  componente li sovrascrivono.
- I componenti con `bVisible = 0` o `bHiddenInGame = 1` vengono saltati. Vengono saltate anche le mesh
  il cui percorso corrisponde a `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/` o `_hlod`.
- Le rotazioni usano `FRotationMatrix` di Unreal (pitch, yaw, roll in gradi).
- I duplicati (la stessa mesh con la stessa trasformazione, entro 0,1 cm) vengono eliminati.
- I componenti che non si possono leggere vengono contati per motivo e segnalati, per esempio
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**I componenti istanziati** (foreste, quasi tutte) vengono letti solo con `--trees`. Questa build ha
riorganizzato quelle classi oltre gli header del motore, quindi le loro proprietà non vengono lette.
Invece:

- la mesh arriva dalla tabella delle dipendenze del pacchetto, dove ogni componente di questo tipo elenca
  esattamente una mesh statica,
- le istanze arrivano dal blocco nativo dopo le proprietà
  (`[1][1][128][count]` seguito da `count` matrici 4x4 di double),
- si considera che il componente stia nella radice del suo attore, che è il modo in cui gli attori della
  vegetazione li collocano.

Le coordinate sono quelle di Unreal: centimetri, Z in alto, X in avanti, Y a destra, un sistema
mancino.

## Quale tappa, e in quale verso {#which-stage-and-which-way-round}

Il sistema di riferimento della telemetria non è documentato, quindi non viene assunto. Viene stimato:

- **Otto sistemi di riferimento candidati.** Z di Unreal (cm) per 0,01 diventa l'altezza del giro (y).
  X e Y di Unreal diventano la x e la z del giro, scambiate o no, ciascuna con un segno qualsiasi, tutte
  scalate per 0,01 in metri.
- **Una griglia delle altezze della strada.** Per ogni tappa, ogni tessera di strada viene collocata (al
  suo livello di dettaglio più grossolano) e si tiene il vertice stradale più alto per cella di 2 m.
- **Punteggio.** Fino a 400 campioni del giro, distribuiti uniformemente, vengono portati nello spazio di
  Unreal attraverso ogni sistema di riferimento. Un campione è sulla strada quando, tra le 3 x 3 celle
  che lo circondano, l'altezza della strada più vicina a esso sta tra 1 m sotto e 3 m sopra il campione
  (`ON_ROAD`). Il punteggio è la quota di campioni sulla strada.
- **Vincitore.** Il sistema di riferimento migliore sulla tappa migliore, se fa almeno il 50%. Altrimenti
  l'esportazione si ferma: "the lap does not lie on any stage's road in any frame (best: ...). Name the
  stage with --level."
- **Un giro che dichiara la sua pista.** Se il file del giro ha un campo `track`, una tappa il cui nome
  corrisponde approssimativamente (solo lettere e cifre, e l'uno contiene l'altro) viene provata per
  prima, da sola, e accettata solo se fa almeno l'80%. Altrimenti vengono provate tutte le tappe.
- Con `--level`, viene provata solo quella tappa, in tutti e otto i sistemi di riferimento.

La console dice, per esempio,
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Poi tutto viene scritto **nel sistema di riferimento del giro**: metri, Y in alto. L'avvolgimento di un
triangolo viene invertito ovunque una trasformazione specchia, così le facce puntano ancora nel verso
giusto.

## Il suolo {#the-ground}

- Il corridoio è `--margin` metri intorno al giro, nel suo piano x/z.
- Ogni tessera di suolo viene collocata al suo livello di dettaglio più fine, e si tengono solo i
  triangoli che entrano nel corridoio.
- I triangoli vengono raggruppati per tipo (strada o terreno) e per quadrato di 512 m nello spazio di
  Unreal (51.200 cm), con ciascun quadrato che ha la propria immagine. Le parti hanno nomi come
  `ground:road 1_-4`. Le UV sono `(unreal_xy - square_origin) / 51200`.
- Le normali vengono calcolate dai triangoli per l'intero file.

### La texture del suolo {#the-ground-texture}

Se non si usa `--no-textures`, ogni quadrato viene dipinto da due fonti, a `--texture-size` pixel:

1. **Il colore del suolo pre-calcolato.** Il `RuntimeVirtualTextureComponent` della mappa della tappa
   (la sua scatola è `RelativeLocation` come angolo e `RelativeScale3D` come dimensione, senza rotazione)
   punta a una **texture virtuale** in streaming, cioè il colore del suolo che il gioco ha pre-calcolato.
   La regione del quadrato viene letta da lì, al livello i cui pixel sono più vicini alla dimensione
   richiesta. Questo significa da 13 a 59 cm per pixel, a seconda della tappa.
2. **L'immagine satellitare** riempie tutto ciò che la texture virtuale lascia nero. È la texture
   `sat*_(b|bc|c|basecolor)` della tappa nella sua cartella dell'ambiente, letta fino a 4096 px. La sua
   posizione si trova con un adattamento a minimi quadrati del primo canale UV del terreno lontano rispetto
   alla x e alla y del mondo. L'adattamento deve essere lineare entro 0,01 al 95° percentile, altrimenti
   l'immagine non viene usata. Se le UV del terreno lontano superano 1 (un materiale che le ripete), la
   mappatura viene dimezzata finché non entrano una volta sola.

La console dice quale è stata usata, per esempio
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Una tappa senza nessuna delle due viene disegnata a colori piatti.

## Modelli collocati {#placed-models}

Ogni posizionamento che non è una tessera di suolo viene classificato dal percorso della mesh (vince la
prima corrispondenza):

| Categoria | Il nome della mesh (o il percorso, per gli alberi) contiene |
|---|---|
| alberi (solo con `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| rocce | `rock`, `cliff`, `boulder`, `stone` |
| cordoli | `kerb`, `curb` |
| barriere | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| cartelli | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| edifici | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastrutture | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| oggetti di scena | tutto il resto |

- Una copia viene considerata se la sua origine sta nel corridoio di portata (`margin + 60 m`) e viene
  disegnata se i suoi limiti toccano il corridoio.
- I livelli di dettaglio seguono [Livelli di dettaglio e budget](detail-budget.md): fasce di distanza, poi
  i modelli più costosi scendono di livello per entrare nel budget. Dove anche i livelli più grossolani
  superano il budget, le copie più lontane vengono escluse, come in BeamNG, finché non entrano. I cordoli
  mantengono il pieno dettaglio e non vengono mai esclusi. Il riepilogo stampa
  `placed on it (N triangles of a B budget)` e, quando alcune copie sono state tolte,
  `N copies left out to fit the budget, the furthest from the driving first`.
- Ogni categoria è una parte in un colore piatto: `ground:kerbs` per i cordoli, che sono superficie di
  guida, come in Forza e BeamNG, e `structure:<categoria>` per il resto:

| Categoria | Colore (RGB lineare) |
|---|---|
| barriere | 0,55, 0,52, 0,48 |
| cartelli | 0,75, 0,72, 0,65 |
| edifici | 0,62, 0,58, 0,52 |
| infrastrutture | 0,48, 0,48, 0,50 |
| rocce | 0,45, 0,43, 0,40 |
| oggetti di scena | 0,55, 0,45, 0,35 |
| alberi | 0,20, 0,32, 0,14 |
| cordoli | 0,70, 0,25, 0,22 |

Le mesh statiche che non si possono leggere (mesh scheletriche, mesh solo Nanite, livelli non memorizzati
in linea) vengono contate: `N meshes could not be read`.

## Verifiche alla base {#checks-behind-it}

Come dichiarato nel sorgente, sul gioco installato:

- Ogni indice dei contenuti si legge (versione 8).
- Ogni cella di ogni tappa si apre, e ogni mesh statica e ogni componente di scena si decodifica
  terminando esattamente alla coda nativa della sua classe.
- Quasi ogni mesh statica campionata si decodifica (le altre sono scheletriche). L'estensione decodificata
  di una tessera di strada corrisponde ai suoi limiti memorizzati.
- I livelli mip di un'immagine satellitare hanno esattamente le dimensioni delle sue voci bulk.
- Le tessere di un blocco di texture virtuale sono tutte contate, fino all'ultimo byte, e le tessere di
  strada cadono sulla strada che essa mostra.

## Limiti noti {#known-gaps}

- Le proprietà dei componenti istanziati non vengono lette (vedi sopra). Il loro posizionamento presuppone la
  radice dell'attore.
- Le foreste generate a runtime da PCG non sono memorizzate nei file e non possono essere esportate.
- Le mesh a spline (muri invisibili di respawn), i componenti decalcomania e le texture proprie dei
  modelli collocati non vengono disegnati. I modelli hanno colori piatti.
- `--season` non ha effetto.
- Una patch del gioco può spostare gli slot delle proprietà. Il lettore si ferma invece di leggere male, e
  l'esportazione riporta quanti componenti sono falliti.
