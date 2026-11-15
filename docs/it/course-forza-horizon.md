---
title: Forza Horizon
nav_order: 1
lang: "it"
source: course-forza-horizon.md
source_hash: "7b7eaaf2d8b9"
nav_exclude: true
search_exclude: true
---
# Esportazione del percorso: Forza Horizon {#course-export-forza-horizon}

L'esportazione di Forza legge il tracciato direttamente dagli archivi ForzaTech del
gioco: il terreno con strada, banchina ed erba distinti tra loro, una texture del
suolo cotta dalle mappe del suolo del gioco stesso, e ogni modello collocato con la
propria texture (cordoli, guardrail, muri di pneumatici, cartelli, oggetti di scena,
edifici).

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<gioco>\media\Tracks\<map>" --route lap.json -o map.glb
```

Fonti: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py).
I formati dei contenitori stessi sono su [ForzaTech](reader-forzatech.md).

## Trovare il gioco installato {#finding-the-installed-game}

Nessuno dovrebbe dover digitare un percorso come
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, quindi il percorso viene
ricavato automaticamente:

1. **Librerie Steam.** Il file `config\libraryfolders.vdf` di Steam viene letto da
   `C:\Program Files (x86)\Steam` o `C:\Program Files\Steam`, e ogni voce `"path"` al
   suo interno è una libreria. In `steamapps\common` di ogni libreria si cerca.
2. **Microsoft Store.** Si cerca in `C:\XboxGames`, se esiste. Lì il gioco sta un
   livello più in basso, in `<gioco>\Content`.
3. Una **cartella di gioco** è qualsiasi figlio di queste cartelle che abbia una
   cartella `media\Tracks`, comunque si chiami.
4. Una **cartella di tracciato** è qualsiasi cartella sotto `media\Tracks` che contenga
   un `GeoChunk0.minizip`. Conta in base al contenuto, non al nome, quindi un tracciato
   con un nome che nessuno ha mai visto viene comunque trovato.

Se il gioco si trova altrove, passa la cartella del tracciato con `--track`; vedi
[Risoluzione dei problemi](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <cartella>` salta tutto questo.

Una cartella di tracciato contiene ciò che l'esportazione legge:

| File | Cos'è |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | gli archivi: ogni file di modelli, texture e posizionamenti, senza nomi al suo interno |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | una riga per voce dell'archivio, nell'ordine delle voci: l'unica fonte dei nomi |
| `AssetManifest.xml` | ogni texture che il tracciato contiene, con l'hash con cui i materiali la richiamano |

## Quale tracciato {#which-track}

Un gioco contiene più di una cartella di tracciato (la mappa open world, un garage
o due). Quella giusta viene scelta per **coordinate, non per nome**:

- La domanda è il riquadro di delimitazione del giro, allargato da `--margin`.
- Per ogni cartella di tracciato vengono letti come testo, senza aprire alcun
  archivio, i quattro manifesti `ChunkContentsMiniZip*.txt`. Ogni nome di tassello del
  terreno (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) porta la sua posizione
  nella griglia. Lo strumento conta quanti tasselli distinti cadono dentro il riquadro.
- Vince il tracciato con più tasselli. Se nessun tracciato ne ha, l'esportazione si
  ferma con "none of the installed tracks (...) has terrain at x ..., z .... Those are
  the game's own metres, as its telemetry reports them."

Un tracciato intero risponde in meno di un secondo. Una corrispondenza per nome potrebbe
scegliere la mappa sbagliata, e una mappa sbagliata sembra plausibile quanto quella giusta.

La console scrive `on <tracciato>, in <cartella del gioco>`.

## Terreno {#terrain}

Come viene trovato il terreno (in `forzaterrain.py`):

- I manifesti indicano il terreno come indice spaziale:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- I due numeri sono coordinate di griglia che **avanzano di 1023**, e ogni passo della
  griglia è un tassello di **512 m**. Il tassello `x-2046` è `-2046 / 1023 = -2`, che
  inizia a `-2 * 512 = -1024` m. Se si leggono i nomi come metri, ogni ricerca sbaglia
  di un fattore due e restituisce comunque terreno, preso da un'altra parte della mappa.
- Un tassello può comparire tre volte: normale, `_cb` e `_ul`. Tutti e tre coprono lo
  stesso suolo. Se ne prende uno per tassello, in quell'ordine di preferenza, perché
  unirli triplicherebbe la geometria in superfici coincidenti.
- Un tassello viene letto solo se tocca il riquadro del giro **e** il corridoio. Un
  tassello che il corridoio non tocca non viene mai decompresso.
- Ogni `.modelbin` di un tassello scelto viene decodificato al **livello di dettaglio 0
  soltanto**. Un tassello contiene quattro livelli sullo stesso suolo, ed esportarli
  tutti metterebbe lo stesso metro quadrato quattro volte nel file.
- Ogni mesh porta con sé la propria scala e il proprio bias nel mondo, quindi un
  tassello finisce dove lo mette il gioco senza alcuna trasformazione dell'istanza.
  Vengono tenuti i triangoli la cui impronta si sovrappone al riquadro, poi solo quelli
  che arrivano nel corridoio.
- Una mesh in un formato che il lettore rifiuta viene saltata e contata
  (`N meshes could not be read`), così un risultato scarso spiega il motivo.

Il riepilogo del terreno stampa il numero di vertici, di triangoli, di mesh e di
tasselli, e l'estensione x/y/z.

### Strada, banchina, terreno, segnaletica, acqua {#road-verge-terrain-markings-water}

I nomi dei materiali non dicono dove sia la strada. Intorno a un circuito, il 94% del
suolo usa un materiale con shader stradale, perché il terreno vicino alla strada viene
disegnato con esso, e lo shader decide asfalto o erba pixel per pixel. Quindi:

| Tipo | Deciso da |
|---|---|
| striscia di strada | il **layout dei vertici**: le strisce di strada sono l'unico suolo con un secondo set di UV (canale 1); un triangolo i cui tre vertici li hanno tutti è strada |
| asfalto o banchina | dentro una striscia di strada, la **maschera di asfalto** del tassello nel baricentro del triangolo: 0,5 o più è `road`, meno è `verge` |
| segnaletica | nome del materiale che corrisponde a `whiteline`, `yellowline` o `decal` |
| segni di pneumatici | nome del materiale che corrisponde a `tyremark` o `skid` (controllato prima della segnaletica, perché i segni di pneumatici sono distribuiti come `tyremark_decal_*`) |
| acqua | nome del materiale che corrisponde a `water`, `lake`, `river`, `paddy`, `ocean` o `sea` |
| terreno | tutto il resto |

Misurato sui giri registrati sul circuito di prova, quasi tutti i campioni cadono su
triangoli di striscia di strada, e la grande maggioranza sulla parte di asfalto una
volta che la maschera ha separato la banchina.

La maschera di asfalto esiste solo quando le texture del suolo vengono cotte. Con
`--no-textures`, o per un tassello le cui mappe mancano, le strisce di strada restano
intere come `road` e non si separa alcuna banchina. Le mappe mancanti costano dettaglio,
mai geometria.

### Le superfici dipinte vengono sollevate {#painted-layers-are-lifted}

La segnaletica e i segni di pneumatici sono distribuiti come propri triangoli che
giacciono esattamente sulla strada. Il gioco li disegna con un offset di profondità.
Disegnati così come sono, strada e vernice si contendono ogni pixel. L'esportazione dà
a ogni parte di segnaletica e di segni di pneumatici una propria copia dei vertici,
sollevata di **5 cm** (`DECAL_LIFT`) lungo la normale della superficie, così la strada
sotto non viene sollevata con loro.

### Normali {#normals}

Le normali del terreno vengono dall'archivio. La componente x della normale è memorizzata
come quarto short della posizione, e y e z nell'attributo `NORMAL` (vedi
[ForzaTech](reader-forzatech.md)). Se anche un solo vertice dell'estrazione non ha una
normale, le normali di tutto il suolo vengono calcolate dai triangoli.

## La texture del suolo {#the-ground-texture}

Ogni tassello del terreno distribuisce tre mappe che coprono il suo quadrato di 512 m,
in cinque risoluzioni (da `_quality1` a `_quality5`, la più grande da 2048 px, cioè
25 cm per pixel):

| Mappa | Schema del nome del file | Cosa contiene (come misurato) |
|---|---|---|
| principale | `mainmap_x<X>_z<Z>_x<stagione>x_diff` | R, G: normale di dettaglio (x, z). A: più bassa sull'asfalto e sul terreno accidentato |
| secondaria | `submap_x<X>_z<Z>_x<stagione>x_diff` | pesi degli strati. B: alta sull'asfalto (239 sulla linea guidata, 165 accanto) |
| lucentezza | `autoglossf0_x<X>_z<Z>_x<stagione>x_glos` | G: bassa sull'asfalto (147 contro 215). B: sale nei boschi |

Nessuna di queste è una fotografia a colori. Sono gli ingressi con cui lo shader del
terreno del gioco miscela i suoi strati di materiale, e quegli strati non vengono
decodificati. Quindi la texture cotta è **una interpretazione, non una copia dell'aspetto
del gioco**. Mantiene *dove* sta ciascun tipo di suolo, a 25 cm, e lo dipinge con colori fissi:

| Suolo | RGB lineare | Peso |
|---|---|---|
| erba (corta, vicino alla pista) | 0,30, 0,44, 0,18 | la base |
| terreno accidentato (più lontano) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| bosco | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalto | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Per l'asfalto devono concordare entrambe le mappe. Da sola, una delle due lascia
un'aria grigia macchiata nell'erba dove la compressione a blocchi fa anelli. Il
risultato viene ombreggiato dalla normale di dettaglio della mappa principale contro
una luce fissa (`0.55 + 0.6 * lambert`), così i bordi dei cordoli, le scarpate e i
solchi si leggono come rilievo, e viene scritto come sRGB a 8 bit.

Orientamento: la riga 0 dei pixel è il bordo **nord** del tassello (z più grande), la
colonna 0 il suo bordo **ovest** (x più piccolo). Lo si è trovato proiettando i giri
registrati sulla maschera dell'asfalto in tutti gli otto modi in cui un quadrato può
essere ribaltato o ruotato. Esattamente uno dei modi li mette sull'asfalto. Le UV ne
derivano: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Le mappe vengono lette alla migliore risoluzione disponibile fino alla qualità 5 e
ricampionate alla dimensione della mappa principale. Se l'immagine a colori è più grande
di `--texture-size`, viene poi ridotta a quella dimensione con filtro Lanczos. La
maschera dell'asfalto resta sempre a piena risoluzione, perché decide la geometria.
`--season` sceglie le mappe `x<stagione>x`. Un tassello senza mappe per quella stagione
viene disegnato a colori piatti, e la console segnala `N without maps`.

## Modelli collocati {#placed-models}

Il terreno porta con sé la sua posizione nel mondo. Nient'altro la porta. Dove si trova
ogni copia di un modello è registrato nei file di posizionamento `.pgeo`, uno per
categoria per cella spaziale:
`scene\proc\cellsize\<dimensione>\<x>_<z>\c<dimensione>_<categoria>_....pgeo`. La
struttura dei record è descritta in [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Cosa viene letto {#what-is-read}

- I file di posizionamento vengono filtrati **per nome**: la dimensione della cella e la
  sua posizione nel percorso danno il quadrato della cella (da `x * size` a
  `(x + 1) * size`), e vengono aperte solo le celle che si sovrappongono al riquadro del
  giro e che appartengono a una categoria richiesta.
- Categorie predefinite: `barriers`, `props`, `signs`, `buildings`, `infrastructure`,
  `bridges`, `rocks`. `--trees` aggiunge `trees`, `bushes` e `smashables`. Queste non
  vengono mai lette: `grasstemplate`, `crowdtemplate` e `cwdspline` (erba e spettatori),
  e `evolving` (siti dei festival che cambiano con la progressione).
- Una copia viene tenuta se la sua posizione sta dentro il riquadro e dentro il
  corridoio. I ripetuti esatti (stessa posizione e orientamento al millimetro, elencati
  da due celle vicine) vengono uniti.
- I **cordoli** sono oggetti di scena il cui nome di modello inizia con `road_gen_rum`
  (strisce vibranti). Vengono scritti come `ground:kerbs`, mai semplificati e mai lasciati
  fuori, perché un giro si misura proprio su di loro.

| Categoria | Parte | Colore di riserva (senza texture) |
|---|---|---|
| cordoli | `ground:kerbs` | 0,60, 0,12, 0,10 |
| barriere | `structure:barriers` | 0,50, 0,50, 0,50 |
| oggetti di scena | `structure:props` | 0,45, 0,35, 0,25 |
| cartelli | `structure:signs` | 0,70, 0,70, 0,70 |
| edifici | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastrutture | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| ponti | `structure:bridges` | 0,45, 0,45, 0,45 |
| rocce | `structure:rocks` | 0,30, 0,28, 0,25 |
| oggetti frantumabili | `structure:smashables` | 0,12, 0,22, 0,06 |
| alberi, cespugli | `structure:trees` | 0,10, 0,20, 0,05 |

### La geometria del modello {#the-models-geometry}

Un nome collocato `<modello>_3D` si riferisce ai file del modello
`<modello>_cluster###.i.modelbin` (fino a una dozzina). Ogni triangolo porta una
maschera dei livelli di dettaglio a cui appartiene:

- I livelli di un modello sono i suoi triangoli marcati esplicitamente per quel livello.
  I livelli vanno in sequenza da 0, il più fine per primo.
- I triangoli marcati `0xFFFF` (ogni livello) sono i pezzi che si rompono, come i pali
  di un guardrail o i singoli pneumatici di un muro. Coprono tutto il modello, e il gioco
  disegna loro al posto del modello quando è stato fatto a pezzi. Vengono usati solo per
  un modello senza un livello marcato esplicitamente.
- Le sotto-mesh il cui shader di materiale è un **decal** proiettato vengono lasciate fuori.

Ogni copia viene collocata con la sua posizione, i suoi assi x e y dal record (z = x ×
y) e la sua scala. Le normali vengono trasformate con l'inversa della scala.

### Quale texture {#which-texture}

Un materiale non nomina le sue texture. Le elenca come hash, e il `AssetManifest.xml` del
tracciato associa ogni hash (`SourceHash`) a un nome di texture. Viene letta solo la
sezione `<Textures>`, e la lettura si ferma a `</Textures>` in un file che può arrivare a
decine di megabyte. Poi:

1. Lo slot `0x88B483AA` è il colore di base nello shader ambientale standard (ogni materiale
   campionato). Se il materiale vi lega una texture, quella viene usata.
2. Altrimenti decide il tipo della texture stessa, cioè la parola prima del suo GUID:
   `_bclr_`, poi `_diff_`, poi `_colour_`.
3. Le mappe del terreno (`mainmap`, `submap`, `autogloss`) e le palette di tinta
   (`tint`, `worldtint`) non colorano mai un modello.

Quindi un modello è colorato da ciò che il suo materiale lega, non da una texture chiamata
come il modello. Per esempio, `bar_rur_armco_crct_02_c` usa la texture di `..._02_a`.

La texture viene letta dagli archivi alla risoluzione più piccola che sia almeno
**256 px** su un lato (`MODEL_TEXTURE`), ridotta a 256 se più grande, e memorizzata come
JPEG RGB nel `.glb`. Il colore di un guardrail a 256 px per quattro metri è di 1,6 cm per
pixel, e circa 80 di queste texture entrano nell'atlante del visualizzatore accanto alle tessere del suolo.

**Stagioni.** `--season` sostituisce una texture con il suo gemello stagionale per nome,
ignorando il GUID (`..._xsummerx_bclr` diventa `..._xwinterx_bclr`, oppure `..._bclr`
diventa `..._winter_bclr`), quando il tracciato ne ha uno. Con `--season winter`, il
materiale invernale di una sotto-mesh viene usato anche dove la sua tabella di varianti
lo indica.

**Varianti.** Il record di una sotto-mesh inizia con una tabella di materiali `(estate,
inverno)`, uno per ogni aspetto che una copia può avere: cinque stampe per un cartellone,
sei colori di vernice per una pila di pneumatici. Ogni record di posizionamento indica
quale variante porta quella copia. Una sotto-mesh con meno varianti del modello ripete le
sue.

**Il blocco segnaposto.** Gli atlanti condivisi degli edifici riservano un blocco RGB
solido (255, 64, 0) per le superfici che lo shader dell'edificio tinge con altre texture.
Se più di un ventesimo di una texture è entro 12 livelli da quel colore, il blocco viene
ridipinto con il colore medio della texture stessa. Altrimenti una città viene fuori
arancione.

### Superfici trasparenti {#see-through-surfaces}

Le recinzioni a maglia e le reti sono singoli quad con buchi nel canale alfa della texture.
Disegnate piene, una recinzione diventa un muro che attraversa la vista del tracciato.
Le superfici il cui shader di materiale corrisponde a `alphatest`, `alphablend`,
`transmissive`, `anim_flag`, `impostor`, `branch`, `bush` o `tree` vengono verificate:

- L'opacità della texture viene mediata su una griglia di 32 x 32.
- Per superficie (ogni triangolo ritagliato che condivide una texture), si campionano
  quattro punti per triangolo nello spazio UV, pesati dall'area UV del triangolo.
- Se l'opacità media è almeno 0,05 e sotto **0,5**, l'intera superficie viene lasciata
  fuori. Sotto 0,05 l'alfa significa chiaramente qualcos'altro per il suo shader (un
  segnale di avvertimento che campiona 0,01), e la superficie resta piena.
- Un modello in cui ogni superficie è stata lasciata fuori viene segnalato:
  `N models left out as see-through (mostly holes in their texture)`.

Lo strumento giudica l'intera superficie, non un triangolo alla volta. Giudicato per
triangolo, metà di ogni quad sopravviveva e le recinzioni uscivano come file di denti.

### Edifici disegnati interi {#buildings-drawn-whole}

Una città costruisce i suoi edifici da pezzi modulari: centinaia di migliaia intorno a un
solo circuito cittadino, decine di milioni di triangoli anche al loro livello più
grossolano. Lasciare fuori i pezzi uno alla volta lasciava in piedi lastre di muro isolate.
Il gioco inoltre distribuisce sagome intere per edificio in `scene\hlod_tier_1\`, una mesh
per edificio (radice `hlod_tier_1_*`), già in coordinate del mondo come il terreno:

- Il riquadro mondiale di ogni sagoma viene letto dal riquadro di posizione della sua mesh
  (una lettura dell'intestazione, non una decodifica). Per una mappa intera richiede secondi.
- Vengono usate le sagome che toccano il riquadro del giro e il corridoio.
- Ogni pezzo `buildings` la cui posizione cade dentro l'impronta di una sagoma (più 0,5 m)
  viene eliminato, e al suo posto si disegna la sagoma. La sua distanza dalla guida si misura
  fino allo spigolo più vicino dell'edificio.
- Il riepilogo scrive `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Dettaglio e budget {#detail-and-the-budget}

Le fasce di distanza, il budget e quali copie vengono tolte quando il budget è troppo
piccolo sono descritti in [Livelli di dettaglio e budget](detail-budget.md).

### Riepilogo del posizionamento {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
```

## Scrivere il file {#writing-the-file}

Le parti vengono scritte in quest'ordine: per tassello `terrain`, `verge`, `road` (ciascuna
con l'immagine del tassello), poi `water`, `tyre marks`, `markings` (piatte, le ultime due
sollevate), poi ogni parte collocata in ordine di nome. Le coordinate sono quelle del gioco
(metri, Y in alto). Vedi [Formato del file](output-format.md).

## Quanto costa {#what-it-costs}

Ordini di grandezza approssimativi:

| Tracciato | Risultato |
|---|---|
| un circuito di campagna breve | qualche centinaio di migliaia di triangoli di terreno, oltre un milione di collocati; secondi, sotto 100 MB |
| una lunga sprint da punto a punto | il corridoio è una piccola frazione del riquadro intorno; circa un minuto, qualche centinaio di MB |
| un circuito cittadino | migliaia di barriere, oggetti di scena e cartelli, e interi edifici; con il budget automatico fino a diverse centinaia di MB |

Un chilometro quadrato di terreno open-world sono circa un milione di triangoli.

## Controlli alla base {#checks-behind-it}

Sono misurazioni fatte mentre il lettore veniva scritto, come dichiarato nel sorgente.
Non vengono rieseguite dai test, a meno che il gioco non sia installato.

- Sul circuito di prova, l'auto sta circa alla sua altezza di marcia sopra il suolo
  estratto (mediana sotto 0,2 m).
- Ogni tassello campionato cade dentro il quadrato di 512 m che il suo nome prevede.
- Posizionamenti consecutivi di guardrail distano esattamente 4 m, e la maggior parte delle
  estremità dei guardrail cade entro 5 cm dall'inizio del successivo.
- I cordoli si trovano pochi centimetri sopra il suolo estratto, con la faccia verso l'alto,
  entro 5 m dalla guida (anche un test sul gioco installato, vedi [Sviluppo](development.md)).

## Non disegnato {#not-drawn}

- Alberi e cespugli a meno di `--trees`. Erba, folle e siti dei festival mai.
- Materiali decal proiettati sui modelli.
- Le stampe dei cartelli fuse in alfa sul loro pannello vengono rese opache.
- Il colore del suolo è una ricostruzione di dove si trovano asfalto, erba e bosco, non i
  materiali del terreno del gioco.
