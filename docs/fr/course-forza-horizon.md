---
title: Forza Horizon
nav_order: 1
lang: fr
source: course-forza-horizon.md
source_hash: "7b7eaaf2d8b9"
nav_exclude: true
search_exclude: true
---
# Export de parcours : Forza Horizon {#course-export-forza-horizon}

L'export Forza lit la piste directement dans les archives ForzaTech du jeu : du terrain où la
route, le bord et l'herbe sont distingués, une texture de sol cuite à partir des cartes de sol
du jeu lui-même, et chaque modèle placé dans sa propre texture (bordures, glissières, murs de
pneus, panneaux, accessoires, bâtiments).

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Sources : [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py).
Les formats de conteneurs eux-mêmes sont décrits sur [ForzaTech](reader-forzatech.md).

## Trouver le jeu installé {#finding-the-installed-game}

Personne ne devrait avoir à taper un chemin comme
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, donc le chemin est trouvé
automatiquement :

1. **Bibliothèques Steam.** Le fichier `config\libraryfolders.vdf` de Steam est lu depuis
   `C:\Program Files (x86)\Steam` ou `C:\Program Files\Steam`, et chaque entrée `"path"` y
   est une bibliothèque. Le dossier `steamapps\common` de chaque bibliothèque est cherché.
2. **Microsoft Store.** `C:\XboxGames` est cherché s'il existe. Là, le jeu se trouve un
   niveau plus bas, dans `<game>\Content`.
3. Un **dossier de jeu** est tout enfant de ces dossiers qui possède un dossier
   `media\Tracks`, quel que soit son nom.
4. Un **dossier de piste** est tout dossier sous `media\Tracks` qui contient un
   `GeoChunk0.minizip`. Il est reconnu par son contenu, pas par son nom : une piste sous un
   nom que personne n'a encore vu est tout de même trouvée.

Si le jeu est ailleurs, donnez le dossier de piste avec `--track` ; voir
[Dépannage](troubleshooting.md#finding-the-game) (« no installed Forza track found »).

`--track <dossier>` saute toute cette recherche.

Un dossier de piste contient ce que l'export lit :

| Fichier | Ce que c'est |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | les archives : chaque modèle, texture et fichier de placement, sans noms à l'intérieur |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | une ligne par entrée d'archive, dans l'ordre des entrées : la seule source des noms |
| `AssetManifest.xml` | chaque texture que la piste livre, avec le hachage par lequel les matériaux la désignent |

## Quelle piste {#which-track}

Un jeu livre plusieurs dossiers de piste (la carte en monde ouvert, un garage ou deux). La
bonne est choisie **par coordonnées, pas par nom** :

- La boîte englobante du tour, élargie de `--margin`, est la question.
- Pour chaque dossier de piste, les quatre manifestes `ChunkContentsMiniZip*.txt` sont lus comme du texte, sans ouvrir d'archive. Chaque nom de tuile de terrain (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) porte sa position dans la grille. L'outil compte combien de tuiles distinctes tombent dans la boîte.
- La piste qui a le plus de tuiles là l'emporte. Si aucune n'en a, l'export s'arrête avec "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."

Une piste entière répond en bien moins d'une seconde. Une correspondance par nom pourrait
choisir la mauvaise carte, et une mauvaise carte paraît aussi plausible que la bonne.

La console affiche `on <track>, in <game folder>`.

## Terrain {#terrain}

Comment le terrain est trouvé (dans `forzaterrain.py`) :

- Les manifestes désignent le terrain par un index spatial :
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Les deux nombres sont des coordonnées de grille qui **avancent de 1023**, et chaque pas de grille est une tuile de **512 m**. La tuile `x-2046` vaut `-2046 / 1023 = -2`, qui commence à `-2 * 512 = -1024` m. Si l'on lit les noms comme des mètres, chaque recherche manque d'un facteur deux et renvoie tout de même du terrain, venu de la mauvaise partie de la carte.
- Une tuile peut apparaître trois fois : simple, `_cb` et `_ul`. Les trois couvrent le même sol. On en prend une par tuile, dans cet ordre de préférence, car les fusionner triplerait la géométrie en surfaces confondues.
- Une tuile n'est lue que si elle touche la boîte du tour **et** le couloir. Une tuile que le couloir ne touche pas n'est jamais décompressée.
- Chaque `.modelbin` d'une tuile choisie est décodé au **niveau de détail 0 seulement**. Une tuile porte quatre niveaux sur le même sol, et tous les exporter mettrait le même mètre carré quatre fois dans le fichier.
- Chaque maillage porte sa propre échelle et son propre décalage en coordonnées du monde, si bien qu'une tuile se pose là où le jeu la met, sans transformation d'instance. Les triangles dont l'emprise chevauche la boîte sont gardés, puis seulement ceux qui atteignent le couloir.
- Un maillage dans un format que le lecteur refuse est sauté et compté (`N meshes could not be read`), pour qu'un résultat maigre dise pourquoi.

Le résumé du terrain affiche le nombre de sommets, de triangles, de maillages et de tuiles,
et l'étendue x/y/z.

### Route, bord, terrain, marquages, eau {#road-verge-terrain-markings-water}

Les noms de matériaux ne disent pas où est la route. Autour d'un circuit, 94 % du sol utilise
un matériau à shader de route, car le terrain près d'une route est dessiné avec lui, et le
shader décide asphalte ou herbe pixel par pixel. Donc :

| Type | Décidé par |
|---|---|
| bande de route | la **disposition des sommets** : les bandes de route sont le seul sol avec un second jeu d'UV (canal 1) ; un triangle dont les trois sommets l'ont est une route |
| asphalte ou bord | dans une bande de route, le **masque d'asphalte** de la tuile au centre du triangle : 0,5 ou plus donne `road`, moins donne `verge` |
| marquages | le nom du matériau correspond à `whiteline`, `yellowline` ou `decal` |
| traces de pneus | le nom du matériau correspond à `tyremark` ou `skid` (vérifié avant les marquages, car les traces de pneus sont livrées en `tyremark_decal_*`) |
| eau | le nom du matériau correspond à `water`, `lake`, `river`, `paddy`, `ocean` ou `sea` |
| terrain | tout le reste |

Mesuré sur les tours enregistrés du circuit d'essai, presque tous les échantillons tombent sur
des triangles de bande de route, et la grande majorité sur la part asphalte une fois que le
masque a séparé le bord.

Le masque d'asphalte n'existe que si les textures de sol sont cuites. Avec `--no-textures`,
ou pour une tuile dont les cartes manquent, les bandes de route restent entières en `road`, et
aucun bord n'est séparé. Des cartes manquantes coûtent du détail, jamais de la géométrie.

### Les couches peintes sont relevées {#painted-layers-are-lifted}

Les marquages de voie et les traces de pneus sont livrés comme leurs propres triangles,
posés exactement sur la route. Le jeu les dessine avec un décalage de profondeur. Dessinés
tels quels, la route et la peinture se disputeraient chaque pixel. L'export donne à chaque
partie de marquage et de trace de pneus sa propre copie de sommets, relevée de **5 cm**
(`DECAL_LIFT`) le long de la normale de surface, pour que la route dessous ne soit pas
relevée aussi.

### Normales {#normals}

Les normales du terrain viennent de l'archive. La composante x de la normale est stockée
comme le quatrième short de la position, et ses composantes y et z dans l'attribut `NORMAL`
(voir [ForzaTech](reader-forzatech.md)). Si un sommet de l'extraction n'a pas de normale, les
normales de tout le sol sont calculées à partir des triangles.

## La texture de sol {#the-ground-texture}

Chaque tuile de terrain livre trois cartes couvrant son carré de 512 m, en cinq résolutions
(`_quality1` à `_quality5`, la plus grande fait 2048 px, soit 25 cm par pixel) :

| Carte | Modèle du nom de fichier | Ce qu'elle contient (mesuré) |
|---|---|---|
| principale | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G : normale de détail (x, z). A : plus bas sur l'asphalte et le sol accidenté |
| secondaire | `submap_x<X>_z<Z>_x<season>x_diff` | poids des couches. B : haut sur l'asphalte (239 sur la ligne de course, 165 à côté) |
| brillance | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G : bas sur l'asphalte (147 contre 215). B : monte dans les bois |

Aucune de ces cartes n'est une photographie en couleur. Ce sont les entrées avec lesquelles le
shader de terrain du jeu mélange ses couches de matériaux, et ces couches ne sont pas
décodées. La texture cuite est donc **une interprétation, pas une copie de l'apparence du jeu**.
Elle garde *où* se trouve chaque type de sol, à 25 cm, et le peint en couleurs fixes :

| Sol | RVB linéaire | Poids |
|---|---|---|
| herbe (courte, près de la piste) | 0,30, 0,44, 0,18 | la base |
| sol accidenté (plus loin) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| bois | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asphalte | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Les deux cartes doivent être d'accord pour l'asphalte. L'une seule laisse un grain gris dans
l'herbe là où la compression par blocs fait des anneaux. Le résultat est ombré par la normale
de détail de la carte principale face à une lumière fixe (`0.55 + 0.6 * lambert`), si bien que
les lèvres de bordure, les talus et les ornières se lisent comme du relief, et il est écrit en
sRGB 8 bits.

Orientation : la ligne 0 de pixels est le bord **nord** de la tuile (z le plus grand), la colonne
0 son bord **ouest** (x le plus petit). Cela a été trouvé en projetant les tours enregistrés sur
le masque d'asphalte selon les huit façons dont un carré peut être retourné ou tourné. Une seule
façon les pose sur l'asphalte. Les UV en découlent : `u = (x - x0) / 512`,
`v = 1 - (z - z0) / 512`.

Les cartes sont lues à la meilleure résolution disponible jusqu'à la qualité 5, puis rééchantillonnées
à la taille de la carte principale. Si l'image de couleur est plus grande que `--texture-size`,
elle est ensuite réduite à cette taille par filtre de Lanczos. Le masque d'asphalte est toujours
gardé en pleine résolution, car il décide de la géométrie. `--season` choisit les cartes
`x<season>x`. Une tuile sans cartes pour cette saison est dessinée en couleurs unies, et la
console l'annonce par `N without maps`.

## Modèles placés {#placed-models}

Le terrain porte sa propre position dans le monde. Rien d'autre ne le fait. L'endroit où se
trouve chaque copie d'un modèle est consigné dans des fichiers de placement `.pgeo`, un par
catégorie et par cellule spatiale :
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. La disposition des
enregistrements est décrite sur [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Ce qui est lu {#what-is-read}

- Les fichiers de placement sont filtrés **par nom** : la taille de cellule et la position de la cellule dans le chemin donnent son carré (`x * size` à `(x + 1) * size`), et seules les cellules qui chevauchent la boîte du tour, dans une catégorie voulue, sont ouvertes.
- Catégories par défaut : `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`. `--trees` ajoute `trees`, `bushes` et `smashables`. Ceux-ci ne sont jamais lus : `grasstemplate`, `crowdtemplate` et `cwdspline` (herbe et spectateurs), et `evolving` (sites de festival qui changent avec la progression).
- Une copie est gardée si sa position est dans la boîte et dans le couloir. Les répétitions exactes (même position et même orientation au millimètre, listées par deux cellules voisines) sont fusionnées.
- Les **bordures** sont des accessoires dont le nom de modèle commence par `road_gen_rum` (bandes rugueuses). Elles sont écrites comme `ground:kerbs`, jamais simplifiées ni retirées, car un tour est mesuré par rapport à elles.

| Catégorie | Partie | Couleur de repli (sans texture) |
|---|---|---|
| bordures | `ground:kerbs` | 0,60, 0,12, 0,10 |
| barrières | `structure:barriers` | 0,50, 0,50, 0,50 |
| accessoires | `structure:props` | 0,45, 0,35, 0,25 |
| panneaux | `structure:signs` | 0,70, 0,70, 0,70 |
| bâtiments | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastructure | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| ponts | `structure:bridges` | 0,45, 0,45, 0,45 |
| rochers | `structure:rocks` | 0,30, 0,28, 0,25 |
| objets cassables | `structure:smashables` | 0,12, 0,22, 0,06 |
| arbres, buissons | `structure:trees` | 0,10, 0,20, 0,05 |

### La géométrie du modèle {#the-models-geometry}

Un nom placé `<model>_3D` renvoie aux fichiers de modèle `<model>_cluster###.i.modelbin` (jusqu'à
une douzaine). Chaque triangle porte un masque des niveaux de détail auxquels il appartient :

- Les niveaux d'un modèle sont ses triangles explicitement marqués pour ce niveau. Les niveaux se suivent à partir de 0, le plus fin en premier.
- Les triangles marqués `0xFFFF` (tous les niveaux) sont les morceaux cassables, comme les poteaux d'une glissière ou les pneus uniques d'une pile de pneus. Ils recouvrent tout le modèle, et le jeu les dessine à sa place une fois qu'il est mis en pièces. Ils ne sont utilisés que par un modèle sans niveau explicitement marqué.
- Les sous-maillages dont le shader de matériau est une **décalcomanie** projetée sont retirés.

Chaque copie est placée avec sa position, ses axes x et y tirés de l'enregistrement (z = x produit vectoriel y),
et son échelle. Les normales sont transformées par l'inverse de l'échelle.

### Quelle texture {#which-texture}

Un matériau ne nomme pas ses textures. Il les liste par hachages, et le `AssetManifest.xml` de la
piste associe chaque hachage (`SourceHash`) à un nom de texture. Seule la section `<Textures>` est
lue, la lecture s'arrêtant à `</Textures>` dans un fichier qui peut peser des dizaines de
mégaoctets. Ensuite :

1. L'emplacement `0x88B483AA` est la couleur de base du shader d'environnement standard (tous les matériaux échantillonnés). Si le matériau y lie une texture, celle-ci est utilisée.
2. Sinon, le type propre de la texture décide, d'après le mot qui précède son GUID : `_bclr_`, puis `_diff_`, puis `_colour_`.
3. Les cartes de terrain (`mainmap`, `submap`, `autogloss`) et les palettes de teinte (`tint`, `worldtint`) ne colorent jamais un modèle.

Un modèle est donc coloré par ce que son matériau lie, et non par une texture qui porte le nom du
modèle. Par exemple, `bar_rur_armco_crct_02_c` utilise la texture de `..._02_a`.

La texture est lue dans les archives à la plus petite résolution dont le côté est d'au moins
**256 px** (`MODEL_TEXTURE`), réduite à 256 si elle est plus grande, et stockée en JPEG RVB dans le
`.glb`. La couleur d'une glissière à 256 px sur quatre mètres fait 1,6 cm par pixel, et environ 80
de ces textures tiennent dans l'atlas de la visionneuse à côté des tuiles de sol.

**Saisons.** `--season` remplace une texture par sa jumelle saisonnière d'après le nom, le GUID
étant ignoré (`..._xsummerx_bclr` devient `..._xwinterx_bclr`, ou `..._bclr` devient
`..._winter_bclr`), quand la piste en a une. Avec `--season winter`, le matériau d'hiver d'un
sous-maillage est aussi utilisé là où sa table de variantes en nomme un.

**Variantes.** L'enregistrement d'un sous-maillage s'ouvre sur une table de matériaux `(été, hiver)`,
un par apparence que peut porter une copie : cinq impressions pour un panneau, six couleurs de
peinture pour une pile de pneus. Chaque enregistrement de placement dit quelle variante porte cette
copie. Un sous-maillage ayant moins de variantes que le modèle répète les siennes.

**Le bloc de remplissage.** Les atlas de bâtiments partagés réservent un bloc RVB uni (255, 64, 0)
pour les surfaces que le shader du bâtiment teinte à partir d'autres textures. Si plus d'un vingtième
d'une texture est à 12 niveaux près de cette couleur, le bloc est repeint dans la couleur moyenne de
la texture. Sinon, une ville sort orange.

### Surfaces translucides {#see-through-surfaces}

Les grillages et les filets sont des quads simples avec des trous dans l'alpha de la texture. Dessinés
pleins, un grillage devient un mur en travers de la vue de la piste. Les surfaces dont le shader de
matériau correspond à `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`,
`bush` ou `tree` sont testées :

- L'opacité de la texture est moyennée sur une grille de 32 x 32.
- Pour chaque surface (chaque triangle découpé partageant une texture), quatre points par triangle sont échantillonnés dans l'espace UV et pondérés par l'aire UV du triangle.
- Si l'opacité moyenne vaut au moins 0,05 et moins de **0,5**, toute la surface est retirée. En dessous de 0,05, l'alpha signifie clairement autre chose pour son shader (un panneau d'avertissement qui échantillonne 0,01), et la surface est gardée pleine.
- Un modèle dont toutes les surfaces ont été retirées est signalé : `N models left out as see-through (mostly holes in their texture)`.

L'outil juge la surface entière plutôt que triangle par triangle. Jugé triangle par triangle, la moitié de
chaque quad survivait, et les grillages sortaient en rangées de dents.

### Bâtiments dessinés en entier {#buildings-drawn-whole}

Une ville construit ses bâtiments à partir de pièces modulaires : des centaines de milliers autour
d'un seul circuit urbain, des dizaines de millions de triangles même à leur niveau le plus grossier.
Retirer les pièces une à une laissait des dalles de mur isolées debout. Le jeu livre aussi des
substituts de bâtiment entier dans `scene\hlod_tier_1\`, un maillage par bâtiment (préfixe
`hlod_tier_1_*`), déjà en coordonnées du monde comme le terrain :

- La boîte mondiale de chaque substitut est lue dans la boîte de position de son maillage (une lecture d'en-tête, non un décodage). Cela prend quelques secondes pour une carte entière.
- Les substituts qui touchent la boîte du tour et le couloir sont utilisés.
- Chaque pièce `buildings` dont la position tombe dans l'emprise d'un substitut (plus 0,5 m) est retirée, et le substitut est dessiné à sa place. Sa distance à la conduite est mesurée jusqu'au bord le plus proche du bâtiment.
- Le résumé indique `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Détail et budget {#detail-and-the-budget}

Les bandes de distance, le budget, et les copies qui partent quand le budget est trop petit sont
décrits dans [Niveaux de détail et budget](detail-budget.md).

### Résumé du placement {#placement-summary}

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

## Écrire le fichier {#writing-the-file}

Les parties sont écrites dans cet ordre : par tuile `terrain`, `verge`, `road` (chacune avec
l'image de la tuile), puis `water`, `tyre marks`, `markings` (à plat, les deux dernières relevées),
puis chaque partie placée triée par nom. Les coordonnées sont celles du jeu (mètres, Y vers le
haut). Voir [Format de sortie](output-format.md).

## Ce que cela coûte {#what-it-costs}

Ordres de grandeur approximatifs :

| Parcours | Résultat |
|---|---|
| un petit circuit de campagne | quelques centaines de milliers de triangles de terrain, plus d'un million de triangles placés ; quelques secondes, moins de 100 Mo |
| un long sprint d'un point à un autre | le couloir est une petite fraction de la boîte autour ; environ une minute, quelques centaines de Mo |
| un circuit urbain | des milliers de barrières, accessoires et panneaux, et des bâtiments entiers ; avec le budget automatique, jusqu'à plusieurs centaines de Mo |

Un kilomètre carré de terrain en monde ouvert fait environ un million de triangles.

## Vérifications {#checks-behind-it}

Ce sont des mesures faites pendant l'écriture du lecteur, comme indiqué dans la source. Elles ne
sont pas relancées par les tests, sauf si le jeu est installé.

- Sur le circuit d'essai, la voiture se trouve à peu près à sa hauteur de roulage au-dessus du sol extrait (médiane inférieure à 0,2 m).
- Chaque tuile échantillonnée tombe dans le carré de 512 m que son nom annonce.
- Des placements de glissière consécutifs sont exactement à 4 m l'un de l'autre, et la plupart des extrémités de glissière tombent à moins de 5 cm du début de la suivante.
- Les bordures reposent à quelques centimètres au-dessus du sol extrait, face vers le haut, à moins de 5 m de la conduite (aussi un test sur jeu installé, voir [Développement](development.md)).

## Non dessiné {#not-drawn}

- Les arbres et buissons, sauf avec `--trees`. L'herbe, les foules et les sites de festival, jamais.
- Les matériaux de décalcomanie projetés sur les modèles.
- Les impressions de panneaux mélangées par alpha sur leur support sortent opaques.
- La couleur du sol est une reconstruction de l'emplacement de l'asphalte, de l'herbe et des bois, et non les matériaux de terrain du jeu.
