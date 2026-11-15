---
title: Frostbite
nav_order: 5
lang: "it"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, bundle, mesh e livelli {#frostbite-toc-cas-bundles-meshes-and-levels}

**Legge un livello di Battlefield 6 fino al suo terreno, alle sue mesh collocate e alle
loro mappe di colore, e lo scrive come `.glb`.** I giochi Frostbite (Battlefield, Need for
Speed, Dead Space) tengono i loro contenuti in blob `.cas`, descritti da tabelle dei
contenuti `.toc`. La tabella di un livello dice quali bundle carica il livello, i bundle
nominano ogni asset, e gli asset dicono quale mesh sta dove.

Fonti:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabelle, pacchetti, payload),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bundle e i loro manifesti),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(partizioni EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(campo altimetrico),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(texture e materiali),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(posizionamento ed esportazione).
Comandi: `identify`, `levels`, `level` (vedi [Comandi](commands.md#levels-and-level-frostbite)).

Niente di qui è documentato dal gioco. Ogni disposizione qui sotto è stata letta dai file
e poi verificata su tutti i file, e ogni sezione dice quale fosse il controllo. Dove i
strumenti di modding Frosty descrivono versioni più vecchie di una struttura, i nomi dei
campi seguono i loro; nessun codice è stato preso da loro (vedi [Regole e licenze](rules-and-licences.md)).

## L'intestazione che sembra cifrata e non lo è {#the-header-that-looks-encrypted-and-is-not}

| Firma (u32, little-endian) | Significato | Gestito |
|---|---|---|
| `0x00CED100` | semplice: l'albero inizia subito | letto |
| `0x01CED100` | firmato: una firma di 556 byte, poi l'albero **in chiaro** | letto |
| `0x03CED100` | offuscato con XOR, con la chiave nell'intestazione del file | riconosciuto e rifiutato |

La forma firmata è quella che Battlefield attuale distribuisce. I byte ad alta entropia
dopo la firma sono una firma, non un testo cifrato.

## L'albero DbObject {#the-dbobject-tree}

Una struttura ricorsiva unica. Ogni campo è un byte di tipo (i cinque bit bassi il tipo, il
bit 7 "anonimo"), un nome facoltativo, e un valore. I contenitori portano la loro lunghezza
come intero di lunghezza variabile e finiscono con un byte zero. `parse_toc` controlla la
lunghezza di ogni contenitore, quindi un file che si legge è stato compreso. `layout.toc`
è in questa forma.

## Pacchetti di installazione {#installation-packages}

Ogni posizione nomina il **pacchetto di installazione** a cui appartiene il suo blob. Ogni
pacchetto numera i suoi blob a partire da `cas_01`, quindi il solo numero del blob è
ambiguo non appena è installato più di un pacchetto, cosa che accade sempre.

- `layout.toc` elenca i pacchetti sotto `installManifest.installChunks`, ciascuno con un
  `persistentIndex` e un `installBundle` come `Win32/installation/<pacchetto>`.
- I blob del pacchetto si trovano in quella cartella, sotto `Data` per il gioco base o sotto
  `Update/<pacchetto>/Data` per ciò che è arrivato dopo.
- Un record di posizione porta il `persistentIndex` completo a 32 bit: la metà bassa della
  sua prima parola contiene la metà alta, la metà alta della sua seconda parola la metà
  bassa; la metà bassa della seconda parola è il numero del blob.

Controllo: ogni posizione in ogni tabella binaria di un'installazione si risolve in un
pacchetto dichiarato e cade dentro il blob che nomina. Una versione precedente prendeva il
primo `cas_NN.cas` del numero giusto. Un terzo dei payload che leggeva sembrava ad alta
entropia e veniva preso per cifratura. Erano gli offset giusti nel file sbagliato. Niente di
trovato è cifrato.

## La tabella del livello {#the-level-table}

La tabella di un livello (`levels/<livello>/<livello>.toc`) è una tabella di sezioni: quindici
parole d'intestazione in big-endian, poi sezioni messe una dopo l'altra, i cui offset sono
sia dichiarati sia ricavabili da due conteggi.

| Sezione | Contenuto |
|---|---|
| bundle | una tabella hash (una parola ciascuno), poi un record di 16 byte per bundle: chiave, `0x40000000` \| dimensione, 0, offset |
| tabella hash dei chunk | una parola per chunk |
| chunk | un id di 16 byte (il GUID del chunk con i **byte invertiti**), poi una parola: `0x80000000` \| 4 x l'indice della sua posizione |
| posizioni | quattro parole big-endian: pacchetto (diviso), blob, offset, dimensione |

Gli id dei chunk e le posizioni sono **in ordini diversi**. Leggerli nell'ordine del file
accoppia ogni chunk con i byte di un altro chunk, che si decodificano benissimo (per lo più
come suono) e quindi non sembrano sbagliati finché una mesh non esce come rumore.
Controllo: in un livello, le parole di indice sono una permutazione da 0 al numero dei
chunk meno uno.

I bundle sono memorizzati in linea dopo la tabella delle sezioni. Ciascuno ha nove parole
d'intestazione big-endian, poi le sue voci: otto byte di offset e dimensione, preceduti da
altri otto che nominano pacchetto e blob quando il bit alto del byte di flag è acceso.
Controllo: su ogni bundle, l'ultima voce finisce esattamente dove iniziano i byte di flag.

### Quale tabella è il livello {#which-table-is-the-level}

Un livello può avere più tabelle con lo stesso nome: una nel `Data` del gioco base, una in
ogni aggiornamento (`Update/<pacchetto>/Data`) che lo distribuisce o lo cambia, e una in ogni
pacchetto ad alta risoluzione (`Update/<pacchetto>/Data/Win32/installation/detail/<pacchetto>/...`).
Solo alcune contengono bundle. Per un livello che un aggiornamento distribuisce, la tabella
nel gioco base contiene solo chunk e nessun bundle, e quella nell'aggiornamento è il livello;
prendere la prima tabella trovata non esportava nulla.

Quindi il livello è la tabella con più bundle, vincendo a parità uno strato successivo (prima
il gioco base, poi gli aggiornamenti in ordine di nome), e le tabelle dello stesso nome senza
bundle sono i suoi **supplementi**: i loro chunk vengono aggiunti a quelli del livello, perché
contengono i mip più grandi delle sue texture. L'intestazione di una texture nomina quel chunk
a +164 (vedi [Texture e materiali](#textures-and-materials)). `levels` stampa da dove viene ogni
livello e quanti supplementi ha.

## Manifesti dei bundle {#bundle-manifests}

La prima voce di un bundle è il suo manifesto, memorizzato senza compressione. È il formato
binario dei bundle dei giochi Frostbite precedenti con una nuova firma, `0xD68E799D`: conteggi,
SHA-1, record ebx e res (offset e dimensione del nome), tipi di res, metadati e id, GUID dei
chunk, stringhe. Le altre voci del bundle sono ebx, res e chunk, in quell'ordine. Controllo:
i conteggi corrispondono alle voci in ogni bundle, e le stringhe iniziano dove finiscono i record.

I tipi di risorsa sono hash. `0x49B156D4` è MeshSet (ogni res di quel tipo si chiama
`..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` legge tutto questo per un livello, in pochi secondi: un livello ha decine di
bundle e decine di migliaia di ebx, res e chunk.

## Blocchi di payload {#payload-blocks}

```
[dimensione decompressa : 4] [metodo : 2] [dimensione compressa : 2]    big-endian
```

Una dimensione compressa pari a zero significa memorizzato, purché decomprima fino a quella dimensione.

| Parola di metodo | Codec |
|---|---|
| `0x0070`, `0x0071` | nessuno |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), dalla DLL `oo2core` del gioco stesso) |
| altro, con dimensioni uguali | copiato come memorizzato |
| altro | rifiutato |

Letto dal pacchetto giusto, ogni payload campionato si decodifica.

## Partizioni EBX {#ebx-partitions}

EBX contiene tutto ciò che non è dato grezzo. Ogni partizione è un file RIFF: `EBXD` (i dati,
allineati a 16), `EFIX` (GUID della partizione, GUID dei tipi e firme, istanza, offset di
puntatori, importazioni e informazioni di tipo), `EBXX` (la tabella degli array: offset,
conteggio, hash, flag, tipo di elemento). Un campo puntatore è di otto byte: zero è null, un
valore dispari è il numero di importazione `value >> 1`, qualsiasi altro valore è relativo al campo.

La **libreria dei tipi non è leggibile**. Il gioco la distribuisce nel suo file system iniziale,
che è cifrato, e questo pacchetto non la tocca. I tipi si riconoscono per GUID e firma, che ogni
partizione porta, e i pochi tipi che l'esportazione del livello richiede sono stati disegnati
dai dati.

## MeshSet {#meshset}

Una mesh è una res MeshSet (la descrizione) e un chunk per ogni livello di dettaglio (i buffer).

| Parte | Disposizione |
|---|---|
| prefisso | quattro parole: dimensione dell'intestazione (176 o 192), dimensione del record di livello (da 176 a 188), dimensione del record di sezione (368), 0 |
| intestazione | riquadro di delimitazione; sei offset di livello i64; tipo di mesh a `0x6C` (rigida, skinnata, composita); conteggi di livelli e sezioni a `0x9C` |
| livello | sezioni a `+0x08`; cinque liste di disegno a `+0x14` (opache, trasparenti, decal, solo profondità, ombra); formato degli indici `+0x54` (`0x21` u16, `0x2E` u32), byte di indici e vertici; GUID del chunk a `+0x74` |
| sezione | nome del materiale; passo dei vertici; triangoli, primo indice, offset dei vertici (in byte), numero di vertici a `+0x20`; dichiarazione dei vertici a `+0x64`: 16 x (uso, formato, offset, stream), 16 passi di stream, conteggi |
| chunk | il buffer dei vertici, poi il buffer degli indici. Gli stream di una sezione si susseguono, e gli indici contano dal primo vertice della sezione |

Le posizioni sono uso 1, stream 0, offset 0, come quattro half o tre float.
Vengono disegnate solo le sezioni opache e trasparenti. Ogni sezione chiamata `..._shadow`
sta nella lista delle ombre e solo lì, quindi decidono le liste.

Controllo: ogni mesh di un livello i cui livelli sono memorizzati in chunk si decodifica, e quasi
tutte hanno il 99% o più dei vertici dentro il riquadro dichiarato; il resto lo manca per
arrotondamento dei half. Una cassa decodificata misura circa un metro, Y in alto, con le normali
rivolte verso l'esterno.

## Posizionamento {#placement}

La pipeline dei contenuti raccoglie gli oggetti statici di ogni sotto-mondo in un **gruppo di
modelli statici**: un array di membri, uno per mesh, ciascuno con le sue trasformazioni di istanza.

| Tipo (GUID, firma) | Disposizione |
|---|---|
| membro `ad13064e…`, `0xF861A878` | 224 byte: `+88` array di trasformazioni, `+112` il blueprint dell'oggetto (importazione), `+160` l'asset della mesh (importazione) |
| trasformazione `101dce06…`, `0x5E6D8C37` | 64 byte: destra, su, avanti, traslazione, ciascuno un vec3 riempito a 16 |

La partizione dell'asset della mesh si chiama come la sua res MeshSet, quindi il GUID di partizione
dell'importazione dà la mesh. Un punto cade in `x·right + y·up + z·forward + translation`. La
trasformazione del gruppo stesso era l'identità in ogni gruppo dei livelli controllati, e non viene applicata.

Controllo: in un livello, ogni membro di ogni gruppo si risolve in una mesh; la maggior parte delle
copie ha una rotazione con determinante 1 a un millesimo, le altre sono scalate o specchiate. I GUID
e le firme dei tipi sono gli stessi negli altri livelli. Un aggiornamento del gioco che cambia la
disposizione cambia la firma, e il lettore allora non trova nulla invece di leggere male.

### Oggetti collocati uno per uno {#objects-placed-one-by-one}

Ciò che la pipeline non può raggruppare - oggetti distruttibili, contenitori, detriti - viene
collocato tramite **riferimenti a oggetti** e **riferimenti a prefab** nelle partizioni del livello:

| Tipo (GUID, firma) | Disposizione |
|---|---|
| riferimento a oggetto `a9a6a6ad…`, `0xC4856BEC` | `+32` la trasformazione (come sopra), `+112` il blueprint dell'oggetto (importazione) |
| riferimento a prefab `117c746e…`, `0xDE3FE9B4` | lo stesso; il blueprint è un prefab, una partizione di altri riferimenti |

I prefab si annidano; una copia finisce alla propria trasformazione moltiplicata per quella del
genitore (vettori riga), fino a otto livelli di profondità. Un blueprint di oggetto viene disegnato
come le mesh che importa, lasciando fuori gli stati distrutti (`dc_...`). Un prefab raggruppato
viene referenziato come il suo residuo `..._nongroupable_autogen`, così nulla viene disegnato due volte.

La visita parte solo dai mondi e dai layer del livello. Una partizione il cui primo elemento è un
blueprint di prefab (`134919fc…`, `0x0247807D`) è la definizione di un prefab, e un livello ne tiene
molti nella propria cartella, collocati dai suoi mondi in modi diversi da questi riferimenti;
trattato come un mondo, un prefab mette i suoi contenuti alle sue coordinate locali. Questo ammassa
centinaia di copie intorno all'origine del mondo, molto sotto il suolo. I mondi e i layer hanno
`a10ebe0f…`, `0xD3D16C3C` per primo.

I blueprint messi fuori gioco non vengono seguiti: asset di sviluppo e di test (`game/dev/`,
`test/`), il set della sequenza cinematica di fine round (`..._gameend_...`: messo sotto il
suolo) e il controller della telecamera di morte (`.../deathflow/...`, i cui gadget stanno
nell'origine del mondo). Vengono riconosciuti dal percorso dell'asset, non dal layer: lo stesso
layer che contiene il set della sequenza può collocare i veri muri e tetti del livello. Dopo
entrambe le regole, nessuna copia nei livelli controllati sta più di 10 m sotto il terreno, e le
copie stanno sul terreno dove il gioco le mostra.

**Livelli di dettaglio che fanno da sostituto.** L'ultimo livello di dettaglio di una mesh può
passare a una sagoma di visione lontana con un materiale proprio: `M_LastLod`, `M_Billboard`,
`M_Vista`, `M_ProjectionLod`. Una torre a traliccio di decine di migliaia di triangoli può
finire in una silhouette di poche centinaia, che il budget sceglierebbe e che da vicino è un
pilone pieno. Un livello di dettaglio che porta un materiale del genere, che il suo livello più
fine non ha, non viene mai scelto: il più grossolano della mesh è l'ultimo vero.

## Terreno {#terrain}

Fonte: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Il terreno è una res TerrainStreamingTree (tipo `0x22FE8AC8`) e i chunk che essa nomina.

| Parte | Disposizione |
|---|---|
| intestazione | 34 byte; il numero di nodi a 25 |
| alberi raster | un byte di tipo e una lunghezza u32 ciascuno, finché un byte di tipo `0xFF`. Il tipo 0 è il campo altimetrico: campioni per lato a +5 (265), intervallo di altezze a +21 (1.280 m), il quadrato del terreno nel suo primo record di nodo a +77 (8.192 m nel livello controllato). Contiene i riquadri dei nodi e una piramide min/max 16 x 16 per nodo, non le altezze |
| nodi di streaming | il quadtree, in profondità: dimensione del chunk e GUID; un secondo chunk facoltativo; un byte di flag (bit 0: il chunk inizia con una pagina di altezza); ha-figli. I figli nell'ordine (0,0), (1,0), (1,1), (0,1) |
| pagina di altezza | le prime 265 x 265 u16 del chunk di un nodo con flag, riga per riga; altezza = valore x 1.280 / 65.535 m; colonne lungo x, righe lungo z, dall'angolo basso del nodo; un bordo di 4 campioni, quindi 256 celle per nodo |

Ogni passo è stato controllato da solo:

- L'analisi dell'albero quadrato dei nodi consuma la res fino all'ultimo byte, con i 529 nodi dichiarati.
- I nodi vicini condividono esattamente le loro nove colonne di bordo, quindi il passo è 256.
- I campioni di un figlio a ogni altra posizione sono esattamente uguali a quelli del genitore con un
  bordo di 4, e distano da 90 a 700 unità con qualsiasi altro bordo.
- La parola più bassa del livello decodifica al centimetro l'altezza più bassa del riquadro di delimitazione.
- Fra gli otto modi in cui il quadrato potrebbe giacere sul mondo, solo x lungo x e z lungo z mette
  gli oggetti collocati sopra di esso: metà delle copie campionate entro circa 2 m, contro diverse
  volte tanto per ogni altro modo.

Gli oggetti collocati misurano poi il risultato. Il punto più basso di ogni copia, rispetto al terreno
sotto di essa (bilineare, dal nodo più fine):

| Collocato | Distanza mediana | Mediana con segno |
|---|---|---|
| alberi e cespugli | ben sotto un metro | appena sotto la superficie |
| oggetti di scena | un metro o due | sulla superficie |
| rocce | circa un metro | affondate di circa un metro |
| edifici | diversi metri (poggiano su fondamenta) | leggermente affondati |

La vegetazione viene collocata sul suolo e da nessun'altra parte, il che la rende il controllo più
severo: le sue origini stanno a una mediana di 0,07 m dalla superficie. Gli edifici si spargono molto
perché la categoria contiene muri, pavimenti e pezzi di kit di strutture a più piani e sotterranee.
Spostando il terreno di 64 m di lato, la quota di copie entro 0,5 m scende dal 29% al 10%.

`level` disegna il campo altimetrico come `ground:terrain`, ogni sua parte dal nodo più fine con
altezze lì e non più fine di `--ground-spacing` (4 m di default: 3,7 milioni di triangoli per il livello
controllato, i cui nodi più fini sono 0,5 m). Pezzi di risoluzione diversa si incontrano con piccoli
gradini; nulla li cuce insieme.

Il chunk di un nodo contiene anche le pagine delle maschere di strato dopo la sua pagina di altezza, e
il suo secondo chunk termina con la mappa di colore del nodo (vedi [Strati del terreno](#terrain-layers)).

## Strati del terreno {#terrain-layers}

Il gioco ombreggia il terreno vicino a un giocatore facendo splatting di materiali superficiali in
mosaico tramite maschere dipinte, con una mappa di colore sopra, e disegnando decal (strade, rattoppi
di asfalto, segnaletica di piste) sopra. Il resoconto di Frostbite sul sistema (Widmark, "Terrain in
Battlefield 3", GDC 2012) elenca i raster del terreno come il campo altimetrico, le maschere di splatting
dello shader, una mappa di colore usata "come sovrapposizione sopra lo shader splatting", materiali fisici,
una maschera di profondità della distruzione, una mappa dell'albedo per la luce riflessa e canali di
maschera aggiuntivi; un tassello di raster porta un bordo per gli algoritmi di rendering. L'albero dei nodi
dei livelli controllati ha sette alberi raster, di tipo 0, 1, 2, 4, 5, 7 e 8, le cui intestazioni iniziano
con la dimensione del tassello: 265 per il campo altimetrico (tipo 0) e il tipo 2, 72 o 66 per le maschere
(tipo 1), 132 con un bordo di 2 per la mappa di colore (tipo 4), 260 con un bordo di 2 per il tipo 5.

**L'elenco degli strati.** La res `....layergraphs` del terreno elenca una voce di 32 byte per strato, nell'ordine
in cui i record delle maschere li numerano (34 voci, 34 sezioni del deposito e indici di strato da 0 a 33 in un
livello); l'id di ogni voce termina con la sua chiave di sezione nel blocco degli shader del layer graph
(`....layergraphs_shaderblockdepot`), il cui blocco nomina le mappe dello strato: una mappa di colore `_cv`,
le mappe `_nhs` e `_ao` per superficie, più mappe di dettaglio e di rumore condivise. Molti strati non
nominano alcuna mappa: sono sorgenti che il layer graph legge. Il colore di uno strato è la media della sua
mappa `_cv`; la scala del mosaico non si trova. L'asset del terreno termina con una voce di cinque byte per
strato (un byte, poi un u32 indice di strato o -1).

**Le maschere.** L'albero raster 1 è il quadtree delle maschere. Il suo corpo inizia con 59 byte, il lato
della pagina a 0: 72 dove le pagine sono BC4 (72 x 72, 2.592 byte), 66 dove sono a otto bit non compressi
(4.356 byte). Poi viene un gruppo per nodo, in profondità:

| Parte | Disposizione |
|---|---|
| gruppo | u16; u16 numero di record; u32 numero di pagine; i record; un byte zero. Un gruppo senza record è lungo 7 byte in tutto |
| record | 33 byte: u16 strato, u16 hash, il riquadro del quadrante (quattro float), due byte di flag, una piramide di presenza a 85 bit |

I record di un gruppo sono i quattro quadranti del suo nodo, strato per strato, e i quadranti di ogni
strato nell'ordine (0, 0), (1, 0), (1, 1), (0, 1). Un record con il secondo flag acceso copre il suo
quadrante per intero e non ha pagina; uno senza di esso ha la pagina successiva; un quadrante senza
record di uno strato che il suo gruppo nomina è vuoto per quello strato; il primo flag è spento esattamente
quando lo strato continua nel gruppo del quadrante stesso, un livello più in basso, che lo sostituisce lì.
Il numero di pagine è il numero dei record con una pagina.

Le pagine: nel chunk di un nodo di streaming seguono le pagine del proprio gruppo del nodo, cioè la pagina
di altezza, una sezione a 16 bit di 4.358 byte e un raster a otto bit di 67 x 67 (dall'inizio del chunk
quando non ha una pagina di altezza); il suo secondo chunk contiene le pagine dei gruppi dei suoi quattro
quadranti un livello più in basso, nell'ordine dei quadranti della mappa di colore, poi la mappa di colore
stessa. Una pagina è di 64 x 64 texel del quadrante, con le righe lungo z e le colonne lungo x, con un bordo
copiato dai vicini: 4 texel su una pagina BC4, 1 su una non compressa.

I bordi dimostrano il posizionamento senza giudizio: due pagine di uno stesso strato affiancate devono
portare i texel di bordo l'una dell'altra. `read_masks` lo controlla per ogni coppia che colloca e rifiuta
un livello in cui meno del 99% concorda. Circa un terzo dei livelli controllati viene letto, con i bordi
che concordano; alcuni non hanno maschere dipinte; gli altri vengono rifiutati, quasi tutti dal controllo
(i chunk dei loro nodi contengono più di quanto questa disposizione conosca). Il suolo di un livello
rifiutato prende il colore medio dei suoi materiali di superficie, e l'esportazione dice perché. I bordi
che affacciano su un quadrante pieno valgono 255 e quelli che affacciano su uno vuoto valgono 0.

La sezione a 4.358 byte e il raster 67 x 67 prima delle pagine non vengono letti: i loro valori stanno in
una banda alta e stretta, senza valori piccoli e senza sentinella.

**Il colore del suolo.** Il layer graph mescola gli strati in un grafo di shader compilato di maschere,
pendenza, altezza e rumore, che non viene letto. `--ground-texture` colora il suolo con una regola
propria, dichiarata qui come tale:

- gli strati la cui mappa di colore porta un nome da distanza sono i sostituti della vista lontana
  e vengono lasciati fuori;
- gli strati testurizzati che coprono nove decimi del terreno o più sono la base. Le loro maschere sono
  piene quasi ovunque, quindi dove ciascuno sta è scelta dello shader, non loro: quelli con nome da roccia
  o scogliera colorano le pendenze più ripide di 40 gradi, quelli con nome da ghiaia colorano il terreno
  piatto (gli altri strati di base quando nessuno altro c'è), mescolati tra 20 e 40 gradi dalla pendenza
  della mappa dell'altezza (presa ogni 4 m e distribuita in modo bilineare sui texel cotti: ripetuta in
  blocchi di 4 m disegnava il colore roccioso in toppe a bordo netto);
- ogni altro strato testurizzato viene steso sulla base con la sua maschera, nell'ordine degli strati;
- la mappa di colore viene stesa sopra il risultato come fa il motore, due volte il colore del suolo per
  la mappa, così che il grigio medio la lascia com'è; dove la mappa di colore non ha texel il suolo prende
  la luminosità mediana della mappa, in grigio.

Confrontato con il colore mediano del suolo dei fotogrammi di gioco di tre livelli (la cromaticità come
rosso e blu su verde): la zona di gioco cotta arriva a 1,00 / 0,69 contro 1,19 / 0,78 dei fotogrammi in
uno, i cui strati d'erba sono verdi dove i fotogrammi mostrano erba secca, 1,19 / 0,82 contro 1,01 / 1,04
in un altro, la cui mappa di colore è di per sé calda (1,13 / 0,88), e 1,05 / 0,91 contro 0,93 / 0,92 in un
terzo senza mappa di colore. I fotogrammi sono illuminati e gradati, quindi questo misura la tinta, non la luminosità.

**La mappa di colore.** Il secondo chunk di un nodo contiene, dopo le pagine di maschera dei gruppi dei suoi
quadranti, quattro pagine BC7 di 132 x 132 (17.424 byte ciascuna), una per quadrante del nodo, nell'ordine
(x basso, z alto), (x alto, z alto), (x alto, z basso), (x basso, z basso). L'albero delle maschere dice
quanti byte occupano le pagine di maschera, quindi la mappa di colore si trova per conteggio, non dalla fine
del chunk: in un livello i nodi più grossolani portano altre quattro di queste pagine dopo di essa, un'altra
raster a colore piatto, e leggere le ultime quattro pagine del chunk perdeva la mappa di colore su nove
decimi del terreno. Senza quel conteggio la mappa di colore veniva persa anche nei livelli con pagine di
maschera non compresse, le cui pagine non sono un numero intero di pagine BC4; in un livello la mappa di
colore è passata da 0,4 a 0,94 del suo terreno. L'ordine è stato stimato: confrontando i bordi del campo
altimetrico di ogni quadrante, ogni pagina dei nodi con caratteristiche combacia con un quadrante, non
ribaltata, a 0,3-0,54 dove il posizionamento successivo migliore è sotto 0,2. Cucita così, le pagine di un
livello si uniscono senza giunture nelle strade, nell'acqua e nelle zone edificate del livello di prova, a 0,5 m
per texel nella zona di gioco. Dove sono gli strati a fare il lavoro, la mappa di colore è quasi neutra (mediana
110, 107, 104); altrove può portare colore pieno. Un livello i cui secondi chunk contengono solo pagine di
maschera non compresse non ha una mappa di colore letta. Una versione precedente di questo lettore chiamava
queste pagine non geografiche: le confrontava con la mappa dello sfondo, che può essere un altro paesaggio
del tutto, e collocava ogni pagina sull'intero nodo invece che su un quadrante.

**La luce riflessa (albedo)** è stata cercata e non trovata: i chunk dei nodi radice e di primo livello sono
pagine di maschera intere, e il payload del tipo 5 non è stato localizzato.

**I buchi.** L'asset del terreno di un livello (res di tipo `0x1CA38E06`) nomina tre shader: uno shader di
superficie predefinito, uno shader di superficie per i buchi e uno shader sorgente predefinito. Quale strato
legga lo shader dei buchi non è stato trovato, quindi il campo altimetrico non viene tagliato. In un livello
la mesh di navigazione può passare su mesh di roccia decine di metri sotto il campo altimetrico, dove il gioco
deve averle tagliate via. Cercato e non trovato lì: la maschera di uno strato, il raster 67 x 67, un'altezza
riservata (nessuna pagina di altezza del livello contiene 0 o 65.535) e un flag di nodo (ogni nodo sotto la
radice ha flag 1). Restano gli alberi raster 7 e 8. Entrambi sono codificati a lunghezza di sequenza: un byte
uguale a quello prima è seguito da un conteggio di copie in più (`ff ff 84` sono 134 byte di 255). L'albero 7
(tassello 256, un quadtree completo di cinque livelli, quattro bit per campione) si decodifica in coppie di
byte con valori da 0 a 3; l'albero 8 (tassello 265) in byte per lo più 255, con gli altri valori in sequenze
regolari. Nessuno dei due tasselli è ancora posizionato, quindi non si sa che contengano i buchi.

**I decal** vengono letti e cotti; vedi [Decal del terreno](#terrain-decals).

## Decal del terreno {#terrain-decals}

Fonte: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Strade, piste, piazzali di cemento, linee dipinte e lettere, segni di pneumatici: la res `TerrainDecals`
(tipo `0x15E1F32E`) li contiene come geometria piatta che il gioco stende sul terreno.

| Parte | Disposizione |
|---|---|
| intestazione | a +16 un conteggio di slot n, poi n slot di 16 byte, poi il conteggio dei record |
| record | uno per batch di disegno, uno dopo l'altro, di lunghezza variabile: 156 byte di campi fissi - il primo vertice a +32, il numero di triangoli a +36, la ripetizione della texture in metri a +44 - poi i byte dei vertici del batch (offset, dimensione), poi una coda che nomina le sue texture tramite i GUID di partizione dei loro asset |
| vertici | 32 byte: x, z (f32), 8 byte impacchettati, u, v (f32), r, g, b, a (f16); ogni batch è una semplice lista di triangoli |
| indici | u32, che contano da 0 in ogni batch; non servono |

Controlli:

- gli intervalli di vertici dei record si susseguono senza buchi e coprono esattamente tutti i vertici, e il
  primo vertice di ogni record × 32 è il suo offset;
- letti così, i triangoli sono decal compatti (lettere, strisce di linea, toppe), mentre leggendo un vertice
  in meno sono schegge attraverso la mappa;
- quasi tutti i batch nominano nella coda le loro texture: una mappa di colore (`_cv`) con una mappa di opacità
  (`_op`, canale rosso), oppure per la segnaletica una maschera di canali (`_rgb`).

Dopo i GUID delle texture, la coda porta i parametri materiali del batch, codificati come quelli di un blocco
di shader (vedi Tinte più sotto). Il colore di vernice di una marcatura, di una traccia di pneumatico o di una
linea è il float3 con hash `607e`: un 0,64, 0,56, 0,48 sabbioso per le tracce nella sabbia, quasi nero per il catrame.
Le mappe di opacità sono per lo più di formato 62, un canale a 8 byte per blocco, letto come BC4.

Un batch mappa la sua texture o per posizione nel mondo (u = x, v = z, la texture che si ripete ogni tot metri di
ripetizione: asfalto, cemento, ghiaia) oppure da 0 a 1 attraverso il decal (una linea, una lettera, una traccia di
pneumatico). I record vengono disegnati nell'ordine del file.

**La cottura.** `level --ground-texture METRI` dipinge, sotto l'estensione dei decal e in tasselli di al massimo 4.096
pixel, la mappa di colore dello sfondo (bilineare) e poi ogni batch sopra di essa secondo la sua opacità × l'alfa
del vertice. Il colore dei vertici non viene usato: alcuni vertici dei batch sono verde o blu puri, il che tingeva
le marcature di un livello con quei colori. I triangoli del campo altimetrico in quel punto diventano parti
`ground:terrain x<x> z<z>` che portano il tassello. Ogni batch viene disegnato con:

| I batch nominano | Disegnato come |
|---|---|
| una mappa di colore (`_cv`) | la mappa, tramite la sua mappa di opacità |
| una mappa di moltiplicazione (`_mult`) e una mappa di opacità | la vernice (bianca dove il materiale non ne nomina una) per la mappa di moltiplicazione, tramite la mappa di opacità: la linea centrale consumata di una pista, le linee di bordo e le barre di soglia |
| una maschera di canali (`_rgb`) | la vernice, altrimenti bianco per linee e lettere, scuro per i contorni, un leggero scurimento per l'usura, le tracce di pneumatici, le macchie, le pozzanghere e l'umidità, tramite la maschera |
| una mappa di opacità da sola, con una vernice | la vernice tramite la mappa di opacità: tracce di pneumatici |

Una maschera di variazione stradale non è vernice: varia la superficie sotto di essa, per centinaia di metri,
e non viene disegnata, qualunque sia la sua vernice. Dipinta di bianco, stendeva due rettangoli chiari lunghi
150-250 m sui pendii di un livello. La mappa `_mult` viene presa come l'usura propria della vernice, non come un
oscuramento del suolo sotto: è quasi bianca, e la forma della linea sta nella mappa di opacità.

Quasi ogni batch viene disegnato, in pochi tasselli a 0,5 m per pixel; l'esportazione cresce di alcuni MB e
impiega qualche secondo in più. Visti dall'alto, i piazzali, le vie di rullaggio e la rete stradale stanno sotto
le recinzioni e gli edifici dei complessi e portano ai loro cancelli.

Disegnati come geometria propria, i decal richiederebbero una miscelazione alfa, che lo scrittore non porta, e con
un offset sopra un terreno entrerebbero in z-fighting; la cottura li tiene nel colore del suolo stesso.

## Texture e materiali {#textures-and-materials}

Fonte: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Una res Texture (tipo `0x6BDE20BA`) è un'intestazione di 180 byte: tipo e formato dei pixel a +8, larghezza e
altezza a +22, numero di mip a +30, il GUID del chunk a +40, quindici dimensioni di mip a +56. Il chunk è la
catena dei mip, dal più grande. Alcuni chunk non hanno i mip più grandi, che stanno in un pacchetto ad alta
risoluzione; la lunghezza del chunk dice da quale mip inizia. Il chunk di quel pacchetto è nominato a +164; viene
letto dai [supplementi](#which-table-is-the-level) del livello quando serve un mip che al chunk principale manca, e
la sua lunghezza più quella del chunk principale è l'intera catena.

| Formato | Decodificato come | Prova |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineare) | la mappa di colore di un serbatoio di plastica si decodifica così; come BC3 gli stessi byte sono rumore |
| 61, 60 | BC3 | una mappa di cassa si decodifica pulita come BC3, non come BC1 o BC7 |
| 57, 56, 55 | BC1 | mezzo byte per pixel |

La mesh non nomina alcuna texture. Il collegamento sta nei **blocchi degli shader** del livello (res di tipo
`0x73312045`, una per sotto-mondo), indicizzati dagli otto byte a +0x130 del record di una sezione di mesh:

| Parte | Disposizione |
|---|---|
| tabella, a 16 | (chiave di sezione u64, offset del descrittore u64), finché un offset cade fuori dalla res |
| descrittore | (offset del blocco u64, hash u64, dimensione del blocco u64) |
| blocco | i parametri di shader della sezione; ogni texture è un record di 49 byte: un byte, 16 byte, il GUID di partizione dell'asset della texture, il suo GUID di istanza |

La chiave di sezione della cassa compare una volta in ciascuno dei dieci depositi dei sotto-mondi che la
collocano, e il suo blocco nomina `t_mil_crate_03_cs` e `_nmt` tra le mappe di dettaglio condivise. Un blocco
nomina ogni texture che lo shader campiona, e non viene detto quale sia la mappa di colore: quindi si sceglie.
Viene preso una texture 2D sRGB il cui nome contenga la maggior parte delle parole del nome del materiale
(`M_ConcreteWall_01`: concrete, wall), poi quelle del nome della mesh, poi una che non sia un decal di dettaglio
(`t_de_...`) o una mappa di danno, poi quella usata da meno blocchi. Il blocco di un cartello stradale nomina il
suo pannello `t_com_highwaysignage_01_cs` e un foglio di decal `t_de_com_highwaysignage_01_ca` con uno scudo
disteso su un fianco; entrambi corrispondono alle parole, e senza la regola del decal il foglio vinceva per uso e
il cartello mostrava lo scudo ruotato di un quarto, attraverso ogni set di coordinate di texture della sezione.
Le distanze con campo di segno (`..._sdf`), le palette e le maschere di canali (`_rgb`) non vengono mai scelte,
qualunque parola condividano (le `_rgba` invece sì: la maggior parte sono colore con alfa, e lasciarle fuori
scambiava la mappa di un traliccio elettrico e di una scala con altre non correlate): l'atlante di vegetazione
di uno sfondo `..._atlas_a_sdf`, disegnato come colore, mostrava stelle bianche e nere per gli alberi, la
palette degli edifici di uno sfondo un confetti di campioni per i muri, e i detriti di vetro disegnati tramite la
loro maschera di canali risultavano ciano. Una sezione i cui unici candidati sono mappe di dettaglio condivise
resta a colore piatto.

**Palette.** Gli edifici di uno sfondo prendono i loro colori da una palette, di 256 x 256 texel di campioni da 16 x 16:
ogni vertice porta quattro byte (uso `0x1E`) i cui primi due dicono dove nella palette sta il suo colore, x e y su
255. `level` disegna una sezione così con la palette come texture, ogni vertice al centro del suo campione. Disegnati
così, i blocchi di sfondo di un livello diventano muri pastello, terracotta e finestre scure dove erano bianchi semplici.

**Sovrapposizioni.** Gli oggetti grandi affiancano un foglio di rifinitura tramite le loro prime coordinate di texture e
ci stendono sopra una sovrapposizione tramite le seconde, che stanno tra 0 e 1: uno svolgimento dell'intero oggetto.
La sovrapposizione (`..._overlay_cs`, con la sua maschera `..._overlay_a`) porta l'aspetto che l'oggetto ha da
lontano, le bande rosse e la ruggine di un serbatoio d'olio; disegnato con il solo foglio di rifinitura, i serbatoi di
un livello uscivano come pannelli grigi. Una sezione il cui blocco nomina una sovrapposizione con la sua maschera, e
le cui seconde coordinate sono uno svolgimento del genere, viene disegnata con la sovrapposizione attraverso di esse
(36 sezioni in quel livello).

**Tinte.** Molte mappe di colore sono grigie (le medie dei loro canali entro il 6% l'una dall'altra): lo shader le
dipinge con colori dai parametri del blocco. Dopo le sue voci di texture (49 byte ciascuna) un blocco elenca i suoi
parametri, ciascuno con un tag di tipo (`f11af825` un float3, `a5e1f2de` un float4, `c1b1a014` un float, `4a4fc3a1` un
intero), i byte di flag `01 80` per un solo valore, un hash di due byte del nome del parametro, un conteggio u32, il
valore e un id di otto byte. I nomi non sono memorizzati. Sette hash di nome float3 agiscono come tinte: in un livello
tre di essi tengono un colore in circa 1 blocco su 6 la cui mappa è grigia, e quasi mai dove la mappa ha colore
proprio; gli altri tengono i colori in cui si dipinge una mappa grigia quando il nome del materiale lo dice (il
rivestimento blu di un ponte: 0,047, 0,098, 0,171 contro un neutro 0,5). Una famiglia può contenere più valori, uno per
canale di una maschera, la maggior parte neutri, e un valore con un canale quasi nullo (verde puro sulle facciate di
mattoni) seleziona un canale della maschera invece di dipingere. `level` moltiplica una mappa di colore grigia, in luce
lineare, per il primo valore di ogni famiglia che non sia né neutro né un selettore del genere, rispetto al suo valore
neutro, e tiene il risultato come texture propria; una mappa con colore viene lasciata com'è. La regola è quella
dell'esportatore: quale canale di una maschera riceve quale tinta non viene letto. In un livello ha portato la quota dei
triangoli di struttura disegnati quasi bianchi dal 19,4% al 3,9%.

**Varianti di oggetto.** Una mesh viene collocata in più aspetti: un muro di magazzino con una striscia rossa o blu e un
numero diverso dipinto sopra, un container verde o grigio. Ogni copia collocata nomina il suo aspetto:

| Dove | Campo |
|---|---|
| membro del gruppo di modelli statici | +32: un array di un puntatore per copia, a una variazione di oggetto o null |
| riferimento a oggetto | +120: un puntatore a una variazione di oggetto o null |
| variazione di oggetto (partizione `ov_...`, tipo `235f2a9c...`) | la sua prima istanza +32: l'hash u32 del nome della variazione |

L'aspetto di una sezione in una variazione è il blocco di shader indicizzato dalla chiave propria della sezione con
l'hash della variazione aggiunto ai suoi primi quattro byte, come u32 little-endian (`05177857 76ddd22e` + `0x88af2290`
= `953927e0 76ddd22e`); una sezione senza blocco sotto quella chiave ha lo stesso aspetto in ogni variazione. Le banche
dati delle variazioni di mesh del livello (`meshvariationdb_win32`) elencano, per mesh e hash di variazione, i materiali
che ogni variazione tocca, ma non le chiavi: la regola è stata ricavata dalle chiavi stesse e vale per ogni sezione con
varianti controllata (le quattro variazioni di un muro, tre delle sue sezioni ciascuna). Il blocco di una variazione porta
con sé le proprie texture oltre alle sue tinte: il numero dipinto sul muro è un foglio di lettere che il blocco della
variazione nomina. Una quota grande delle copie raggruppate viene collocata in una variazione.

Un blocco viene cotto una volta per ogni insieme di contenuti, e la voce del deposito per una chiave porta un hash di
essi (il secondo u64 della voce). Quando una sezione non ha un blocco sotto la chiave della sua variazione, la variazione
la raggiunge comunque tramite un *gemello*: un'altra sezione il cui blocco predefinito ha lo stesso contenuto e ne ha
uno. Senza gemelli, un muro i cui tratti condividono un blocco predefinito può uscire in due colori. Una sezione senza
una variante propria prende la variante che la maggior parte dei suoi gemelli porta.

**Mesh distruttibili.** Una mesh che una partita può abbattere ha accanto un asset di distruzione del proprio nome
(`.../br_x.destruction` per `.../br_x_mesh`): gli edifici e i muri frantumabili (`br_`) e molti oggetti di scena.
`level` tiene le loro superfici in parti proprie, chiamate con ` (destructible)`, i cui nodi glTF portano
`{"destructible": true}`. I loro stati distrutti sono le mesh `dc_..._part<N>_mesh` accanto a loro, ciascuna centrata sul
proprio punto di origine; dove si trova ogni pezzo è nell'asset di distruzione, che non viene letto, quindi gli stati
distrutti non vengono esportati.

**Lasciato fuori.** Sezioni di materiali di blockout segnaposto (`M_Whitebox`: alcuni grandi triangoli senza texture
che certi edifici tengono accanto alle loro superfici, e che da un livello spiccavano come pinne bianche), mesh fatte per
le sequenze cinematiche (un elicottero collocato dove inizia la sua scena) e aiutanti di illuminazione (piani che bloccano
la luce, mai disegnati). Gli edifici generati dello sfondo di un livello (`..._generated_blueprints_..._mesh`) vengono
disegnati, ma i loro muri portano nomi di materiale che indicano solo mappe di rumore e i loro vertici non portano colore,
quindi restano semplici. Quasi ogni sezione disegnata riceve una mappa di colore.

**Fogli di lettere.** Il numero dipinto su un muro o la stampa di un cartellone di un gru è una sezione propria la cui
mappa di colore è un foglio (`_ca`): l'alfa di una lettera sopra una vernice piena, oppure una stampa. Le sue prime
coordinate di texture tassellano l'intonaco del muro sul pannello (u da -0,2 a 1,7 su un muro), il che disegna il foglio
quasi due volte; il quarto set (`0x24`, altrimenti il terzo, `0x23`) lo stende esattamente una volta (u da -1 a 0, v da 1 a 2,
di qualche millesimo in più nei livelli di dettaglio più grossolani). Dove il primo set lascia una copia dell'immagine e il
quarto o il terzo ne sta entro una, il foglio viene disegnato attraverso di esso, spostato in 0-1. Un foglio con alfa viene
disegnato 1 cm davanti alla superficie su cui è dipinto, che viene disegnata sotto di esso nell'altra mappa di colore del
blocco attraverso il primo set: senza, i texel vuoti del foglio mostravano l'interno del muro. Il secondo set è lo
svolgimento di un oggetto per la sua sovrapposizione e qui non viene usato.

**Mappe ritagliate.** Il quarto canale della mappa di colore significa cose diverse a seconda del nome della mappa. In
`_cs`, di gran lunga la più comune (893 delle mappe scelte di un livello), è la levigatezza: l'1% dell'alfa di una mappa
mediana sta entro 0,1 da 0 o 1. In `_cu` (foglie, erba) e `_ca` (colore e alfa) è l'opacità: 90% e 87%. Una mappa di colore
chiamata `..._cu` o `..._ca` il cui alfa è per almeno il 75% vicino a 0 o 1, per almeno l'1% sotto 0,5 e per almeno il 5% sopra,
viene scritta con il suo alfa, come PNG, e il suo materiale come `alphaMode` MASK di glTF, `alphaCutoff` 0,5, a doppia faccia;
così le schede delle foglie mostrano foglie, non i loro angoli neri. Una mappa di foglie di un albero non ha alcun alfa (4 di
255 al massimo): le sue fronde vengono tagliate dalla geometria, e con solo le prime due condizioni tutta la chioma veniva tagliata via.

Le coordinate di texture sono uso di vertice `0x21`, due half (formato 6) o due float (formato 2). Le sezioni portano fino a
altri tre set (`0x22` a `0x24`) per strati di decal e di dettaglio. Le coordinate tassellano: il lato con nervature di un
contenitore va da -1,6 a 1,8, le tessere di sfondo del terreno stanno tutte fuori da 0..1, e in un livello il 23% dei
triangoli testurizzati esce da 0..1. Vengono scritte così come sono, con un campionatore che si ripete; il visualizzatore 3DHeat
avvolge ogni texture ripetuta dentro il suo atlante. Un renderer che le limita invece le stira: le nervature diventano il
doppio della loro larghezza, un pavimento di cemento si trasforma in strisce lungo un asse, e le travi d'acciaio di una torre
prendono il colore del bordo della loro texture; per lui, `--clamped-uvs` taglia ogni triangolo lungo le linee in cui la sua
texture si ripete e sposta ogni pezzo in 0..1 (vedi [Formato del file](output-format.md)). Dopo, lo 0,03% dei triangoli
testurizzati, attraverso i quali una texture si ripete più di 16 volte, esce, e un triangolo che il taglio renderebbe più di
4 pezzi viene disegnato invece con il colore medio della sua texture: la corteccia si ripete lungo ogni ramo, e tagliata, gli
alberi di un livello passavano da 6,4 a 24 milioni di triangoli.

Il campo altimetrico non ha una mappa di colore propria che si possa leggere. Dove lo copre una delle mappe di sfondo del
terreno, viene colorato da quella: le coordinate di texture dello sfondo sono una funzione lineare di x e z del mondo (il 99%
dei suoi vertici sta entro 0,001 da essa; la mappa copre un quadrato di 65.536 m, ruotato di un quarto), e la stessa funzione
dà quelle del campo altimetrico. Il livello distribuisce i mip di quella mappa a partire da 2.048 px in giù, quindi il campo
altimetrico ottiene 32 m per pixel. La sua roccia scura sta sui pendii ripidi: la correlazione tra oscurità e pendenza è 0,48,
e al massimo 0,34 per le altre sette orientazioni.

Lo sfondo di un altro livello sono otto tessere vicine e otto lontane intorno alla zona di gioco, ciascuna che ripete la sua
texture sulla tessera, e nessuna raggiunge il campo altimetrico. Ogni texture di sfondo viene adattata da sola, e quando
nessuna copre il campo altimetrico prende il colore medio che lo sfondo mostra entro un chilometro dal quadrato del terreno,
su cui `--ground-texture` cuoce i decal.
Un materiale di sfondo è uno il cui nome contiene `TerrainBackdrop`, oppure `BD_` e `Terrain` (`M_BD_<sito>_Terrain..._Near`);
oppure una mesh di sfondo (`bd_..._terrain<sito>_04_far_mesh`) porta un semplice materiale di terreno
(`M_<regione>_Terrain<sito>_04_Far`), che le prime due regole non prendevano in un livello, e quindi colorava il suo suolo
dalle sue superfici.

Dove nessuna mappa di sfondo copre il campo altimetrico, invece, esso prende il colore medio centrale delle superfici del
terreno stesso prima della media dello sfondo: le mappe di colore `_cv` che i blocchi di shader del layer graph nominano (27
in un livello: sabbie, ghiaie, terreni, erba, cemento screpolato), ciascuna mediata, poi la mediana di ciascun canale, senza
la superficie predefinita del motore. Uno sfondo può essere un altro paesaggio del tutto: in un livello la sua media (95, 99,
80 in sRGB) faceva virare il suolo della zona di gioco a un grigio che il gioco non mostra. Con `--ground-texture`, quel colore
viene moltiplicato per il doppio della mappa di colore, che lascia com'è il grigio medio, e cotto con i decal sopra entrambe le
estensioni, quella dei decal e quella della mappa di colore.

Rispetto al gioco, il colore mediano del suolo della zona di gioco cotta di ogni livello e dei fotogrammi di gioco (righe dal 55 al
72% dell'immagine accanto all'HUD, 24 fotogrammi ciascuno; sRGB; i fotogrammi sono illuminati e gradati, quindi i rapporti r/g e
b/g sono il confronto corretto):

| Livello | Fotogrammi | Media dello sfondo | Esportazione |
|---|---|---|---|
| primo | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| secondo | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| terzo | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Il primo è stato sistemato; gli altri due erano prima un po' più vicini nella tonalità. Un solo colore per un intero livello
non può essere giusto ovunque; le maschere lo sarebbero.

## Mesh di navigazione {#navigation-mesh}

Fonte: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Un livello distribuisce una partizione per agente, `<livello>/dbt/<livello>_navmesh_layer_<n>`: in un livello il
layer 0 è il soldato (alto 1,8 m, gradino di 0,18 m, raggio 0,4 m) e altri due sono veicoli (alti 3,5 e 10 m). Ogni
partizione contiene due array:

| Array | Elemento |
|---|---|
| tessere | 28 byte: u32 0, u32 hash, u32 0, u32 indice del chunk, u16 x della tessera, u16 z della tessera, u32 offset, u32 dimensione |
| chunk | 20 byte: il GUID del chunk, u32 dimensione |

Una tessera è `size` byte a `offset` nel chunk con indice `chunk index`, little-endian, e disposta come quella di Detour
(Recast Navigation) dietro un'intestazione più lunga:

| Offset | Contenuto |
|---|---|
| 0 | `VAND`, versione 7 |
| 24 | conteggi: poligoni, vertici, collegamenti, mesh di dettaglio, vertici di dettaglio, triangoli di dettaglio, nodi del volume di delimitazione, collegamenti fuori mesh, il primo poligono fuori mesh |
| 188 | altezza, gradino e raggio dell'agente |
| 200 | il riquadro di delimitazione della tessera, sei float |
| 232 | vertici: float x, y, z, coordinate del mondo |
| successivo limite di 8 byte | poligoni, 32 byte: u32, sei indici di vertice u16, sei vicini u16, flag u16, conteggio dei vertici a +30, a +31 l'area (sei bit bassi) e il tipo (i due alti) |
| poi, compatti | collegamenti (16 byte), mesh di dettaglio (12: primo vertice di dettaglio u32, primo triangolo di dettaglio u32, conteggio di vertici e triangoli u8), vertici di dettaglio (tre float), triangoli di dettaglio (tre indici e flag), nodi del volume di delimitazione (16), collegamenti fuori mesh (80) |

In ogni tessera dei livelli controllati questi sommano esattamente alla dimensione della tessera, al byte, e le mesh
di dettaglio numerano i poligoni prima del primo fuori mesh.

Un poligono è piatto tra i suoi angoli; la sua **mesh di dettaglio** contiene l'altezza reale della superficie su
dossi, rocce e gradini, ed è ciò che viene disegnato. Un indice di triangolo di dettaglio sotto il numero di angoli del
poligono è quell'angolo, altrimenti il vertice di dettaglio `first + index - corners`. Trasformare i poligoni in ventaglio
invece mette molti più triangoli sotto il terreno e crea lunghe schegge; con le mesh di dettaglio nessuno è più lungo della
diagonale di una tessera di 16 m più il gradino di una salita.

Il tipo 0 è suolo, il tipo 2 piccole toppe ripide (circa 45 gradi, un metro quadrato ciascuna), il tipo 1 un collegamento tra
superfici: i suoi angoli coprono 125 m o più di dislivello e stanno fuori dalla tessera, alcuni nell'origine. I collegamenti
vengono lasciati fuori; il resto è disegnato dalle proprie mesh di dettaglio, o a ventaglio in una tessera senza altro.

Controlli: le dimensioni dei chunk sommano esattamente quelle delle tessere; ogni vertice di superficie sta entro il riquadro
della sua tessera, più o meno un metro; quasi tutti i triangoli sono rivolti verso l'alto. Una tessera che fallisce viene
rifiutata e contata, e in quel livello nessuna lo è.

Ciò che copre la mesh del soldato, vista dall'alto nel livello di prova: il suolo, i pavimenti, le scale e alcuni tetti, e non
le cime dei container. È la mappa che l'IA usa per sapere dove un soldato può stare, la cosa più vicina, nei file, a dove stanno
i giocatori.

## Non implementato {#not-implemented}

- Il layer graph del terreno, che mescola i suoi strati superficiali (vedi [Strati del terreno](#terrain-layers)): il colore
  del suolo segue una regola di questo lettore, dalle maschere degli strati e dalla pendenza del campo altimetrico, e i livelli
  le cui pagine di maschera non combaciano ricevono un solo colore.
- I parametri di colore dei materiali dei decal: la segnaletica tramite maschere di canali viene dipinta in un colore neutro.
- I blueprint di oggetti che non sono mesh (logica di gioco, effetti, suoni).
- Gli stati distrutti delle mesh distruttibili: le posizioni dei loro pezzi stanno nell'asset di distruzione, che non viene letto.
- I collegamenti della mesh di navigazione (salti, scale, scavalcamenti) e i suoi layer per veicoli.
- Mesh a livelli memorizzati in linea nella res (10 mesh in un livello, gadget), ossa e parti di mesh skinnate e composite,
  e normali (calcolate dallo scrittore).
- Mappe di normali, rugosità e altre; alfa diverso dal ritaglio (il vetro traslucido e i decal vengono disegnati opachi).
- Buchi del terreno: uno shader di superficie per i buchi è nominato, ma ciò che legge non è stato trovato (vedi
  [Strati del terreno](#terrain-layers)), quindi il campo altimetrico non viene tagliato dove sotto scorre il terreno percorribile.
- Quale tinta va con quale canale della maschera di un materiale: una mappa di colore grigia prende la prima tinta che non sia
  neutra (vedi [Texture e materiali](#textures-and-materials)).
- Effetti (percorsi `fx/`) e le mesh dei cavi, i cui riquadri sono lunghi decine di chilometri; vengono lasciati fuori e contati nel riepilogo.
- La forma con offuscamento XOR della tabella.
