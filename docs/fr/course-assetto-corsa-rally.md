---
title: "Assetto Corsa Rally"
nav_order: 3
lang: "fr"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Export de parcours : Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally repose sur Unreal Engine 5 (5.6.1, une version modifiée) et livre
son contenu sous forme de conteneurs IoStore. Aucun n'est chiffré. L'export trouve
l'étape et l'orientation des axes à partir du tour. Il écrit les tuiles de sol propres
à l'étape, séparées en route et terrain, et texturées avec la couleur de sol cuite de
l'étape. Il place les autres modèles en couleurs unies, par catégorie.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Sources : [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (installation, étapes, placement),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (l'export).
Les lecteurs Unreal sous-jacents sont décrits dans [Unreal 5 IoStore](reader-unreal-iostore.md),
et la décompression dans [Oodle](reader-oodle.md).

**Statut :** testé sur le jeu installé avec des tours générés à une image aléatoire sur
chaque étape. Il a trouvé à chaque fois la bonne étape et la bonne image. Aucun tour
enregistré dans le jeu lui-même n'a encore été passé dedans.

## Trouver l'installation {#finding-the-install}

- `--install <dossier>` : le dossier du jeu, ou son `Content\Paks`, ou tout dossier qui
  contient des fichiers `.utoc`. L'outil regarde dans `<dossier>`, puis dans
  `<dossier>\acr\Content\Paks`, puis dans `<dossier>\Content\Paks`.
- Sinon, le `steamapps\common\Assetto Corsa Rally` de chaque bibliothèque Steam est
  examiné de la même façon.
- Chaque `.utoc` de ce dossier est ouvert comme un seul conteneur. Les conteneurs qui ne
  s'ouvrent pas sont sautés. Si aucun ne s'ouvre : « no readable IoStore containers in ... ».

La plupart des blocs sont compressés en Oodle, et une bibliothèque est cherchée sur la
machine (toutes les bibliothèques Steam sont parcourues). Voir [Oodle](reader-oodle.md).

Le jeu est reconnu comme AC Rally quand le fichier de tour contient
`"game": "assetto-corsa-rally"` (ou `acrally`), ou quand vous passez `--game acrally`.

## Ce qu'est une étape {#what-a-stage-is}

Une étape est une carte **World Partition** :

- `Content\Levels\<Stage>.umap` place le terrain lointain.
- Les cellules cuites sous `Content\Levels\<Stage>\_Generated_\*.umap` placent tout le reste.

Un niveau compte comme étape si son dossier d'environnement,
`Content\Environments\<Stage>\`, contient un dossier `MeshesTrack`. L'outil ne se fie pas
aux noms des tuiles, car une étape peut les nommer d'après une ville plutôt que d'après
sa carte. `--level` est comparé sans tenir compte de la casse à ces noms de carte. Un
mauvais nom affiche la liste des étapes disponibles.

Il n'y a **pas de terrain à proprement parler**. Le sol est fait de maillages statiques :

| Tuiles | Chemin | Deviennent |
|---|---|---|
| tuiles de piste, environ 175 m, coupées en deux | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` et `..._Terrain_k` | `ground:road` et `ground:terrain` (une tuile de piste non coupée, comme un lac gelé, est entièrement route) |
| terrain lointain, tuiles de 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Lire les placements {#reading-the-placements}

Ce qui place un maillage est un `StaticMeshComponent` : son `StaticMesh`, et ses
`RelativeLocation`, `RelativeRotation` et `RelativeScale3D`, chacun relatif au composant
auquel il est attaché (`AttachParent`), jusqu'à la racine de l'acteur, qui est dans le
monde.

- Les propriétés sont **sans version** : stockées par position dans la liste de
  propriétés de la classe, et non par nom. Elles sont lues avec les schémas de
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (voir [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Une valeur égale à celle du modèle du composant (son archetype dans un Blueprint) n'est
  pas stockée. Les valeurs du modèle sont donc lues d'abord, récursivement, et les
  valeurs propres du composant les remplacent.
- Les composants avec `bVisible = 0` ou `bHiddenInGame = 1` sont sautés. Le sont aussi les
  maillages dont le chemin contient `respawnwall`, `collision`, `blocker`, `invisible`,
  `/hlod/` ou `_hlod`.
- Les rotations suivent la `FRotationMatrix` d'Unreal (tangage, lacet, roulis en degrés).
- Les doublons (même maillage à la même transformation, à 0,1 cm près) sont supprimés.
- Les composants qui ne peuvent pas être lus sont comptés par raison et signalés, par
  exemple `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Composants instanciés** (forêts, presque toutes) : ils ne sont lus qu'avec `--trees`.
Cette version du jeu a réarrangé ces classes au-delà des en-têtes du moteur, donc leurs
propriétés ne sont pas lues. À la place :

- le maillage vient de la table de dépendances du paquet, où chaque composant de ce type
  liste exactement un maillage statique,
- les instances viennent du bloc natif situé après les propriétés
  (`[1][1][128][count]` puis `count` matrices 4x4 en double),
- le composant est considéré comme posé à la racine de son acteur, ce qui est la façon
  dont les acteurs de végétation les placent.

Les coordonnées sont celles d'Unreal : centimètres, Z vers le haut, X vers l'avant, Y vers
la droite, un repère gauche.

## Quelle étape, et dans quel sens {#which-stage-and-which-way-round}

Le repère de la télémétrie n'est pas documenté, donc il n'est pas supposé. Il est ajusté :

- **Huit repères candidats.** La hauteur Unreal Z (cm) multipliée par 0,01 devient la
  hauteur du tour (y). Les X et Y d'Unreal deviennent les x et z du tour, échangés ou non,
  chacun avec l'un ou l'autre signe, le tout mis à l'échelle de 0,01 pour passer en mètres.
- **Une grille de hauteurs de route.** Pour chaque étape, chaque tuile de route est placée
  (à son niveau de détail le plus grossier) et le point de route le plus haut est gardé
  par cellule de 2 m.
- **Notation.** Jusqu'à 400 points du tour, répartis régulièrement, sont ramenés dans
  l'espace Unreal avec chaque repère. Un point est sur la route quand, parmi les 3 x 3
  cellules qui l'entourent, la hauteur de route la plus proche de lui est entre 1 m en
  dessous et 3 m au-dessus du point (`ON_ROAD`). La note est la part des points sur la
  route.
- **Le gagnant.** Le meilleur repère sur la meilleure étape, s'il atteint au moins 50 %.
  Sinon l'export s'arrête : « the lap does not lie on any stage's road in any frame
  (best: ...). Name the stage with --level. »
- **Un tour qui nomme sa piste.** Si le fichier de tour a un champ `track`, une étape dont
  le nom correspond à peu près (lettres et chiffres seulement, l'un contenant l'autre) est
  essayée en premier, seule, et acceptée seulement si elle atteint au moins 80 %. Sinon,
  toutes les étapes sont essayées.
- Avec `--level`, seule cette étape est essayée, dans les huit repères.

La console indique par exemple
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Tout est ensuite écrit **dans le repère du tour** : mètres, Y vers le haut. L'ordre
d'enroulement d'un triangle est inversé partout où une transformation réfléchit, pour que
les faces restent orientées du bon côté.

## Le sol {#the-ground}

- Le couloir est une bande de `--margin` mètres autour du tour, dans son plan x/z.
- Chaque tuile de sol est placée à son niveau de détail le plus fin, et seuls les
  triangles qui atteignent le couloir sont gardés.
- Les triangles sont regroupés par nature (route ou terrain) et par carré de 512 m dans
  l'espace Unreal (51 200 cm), chaque carré ayant sa propre image. Les parties sont
  nommées par exemple `ground:road 1_-4`. Les UV valent
  `(unreal_xy - origine_du_carré) / 51200`.
- Les normales sont calculées à partir des triangles, pour tout le fichier.

### La texture du sol {#the-ground-texture}

Sauf avec `--no-textures`, chaque carré est peint à partir de deux sources, à
`--texture-size` pixels :

1. **La couleur de sol cuite.** La `RuntimeVirtualTextureComponent` de la carte de l'étape
   (sa boîte est `RelativeLocation` comme coin et `RelativeScale3D` comme taille, sans
   rotation) pointe vers une **texture virtuelle** en flux : la couleur de sol que le jeu a
   cuite. La zone du carré est lue dedans, au niveau dont les pixels sont les plus proches
   de la taille voulue. Cela fait de 13 à 59 cm par pixel selon l'étape.
2. **L'image satellite** remplit ce que la texture virtuelle laisse noir. C'est la texture
   `sat*_(b|bc|c|basecolor)` de l'étape, dans son dossier d'environnement, lue jusqu'à
   4096 px. Son placement est trouvé par un ajustement aux moindres carrés du premier
   canal UV du terrain lointain par rapport aux x et y du monde. L'ajustement doit être
   linéaire à 0,01 près au 95e percentile, sinon l'image n'est pas utilisée. Si les UV du
   terrain lointain dépassent 1 (un matériau qui les répète), la correspondance est divisée
   par deux jusqu'à ce qu'elles tiennent une fois.

La console dit laquelle a servi, par exemple
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Une étape sans aucune des deux est dessinée en couleurs unies.

## Modèles placés {#placed-models}

Chaque placement qui n'est pas une tuile de sol est classé d'après le chemin de son
maillage (la première correspondance l'emporte) :

| Catégorie | Le nom du maillage (ou le chemin, pour les arbres) contient |
|---|---|
| arbres (seulement avec `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| rochers | `rock`, `cliff`, `boulder`, `stone` |
| bordures | `kerb`, `curb` |
| barrières | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| panneaux | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| bâtiments | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastructure | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| accessoires | tout le reste |

- Une copie est considérée si son origine est dans le couloir d'atteinte (`margin + 60 m`)
  et dessinée si ses limites touchent le couloir.
- Les niveaux de détail suivent [Niveaux de détail et budget](detail-budget.md) : des
  bandes de distance, puis les modèles les plus coûteux descendent d'un cran pour tenir
  dans le budget. Quand même les niveaux les plus grossiers dépassent, les copies les plus
  lointaines sont laissées de côté, comme dans BeamNG, jusqu'à ce que ça tienne. Les
  bordures gardent tout leur détail et ne sont jamais laissées de côté. Le résumé affiche
  `placed on it (N triangles of a B budget)` et, si des copies ont été retirées,
  `N copies left out to fit the budget, the furthest from the driving first`.
- Chaque catégorie est une partie en couleur unie : `ground:kerbs` pour les bordures, qui
  sont une surface de conduite, comme dans Forza et BeamNG, et `structure:<category>` pour
  le reste :

| Catégorie | Couleur (RVB linéaire) |
|---|---|
| barrières | 0.55, 0.52, 0.48 |
| panneaux | 0.75, 0.72, 0.65 |
| bâtiments | 0.62, 0.58, 0.52 |
| infrastructure | 0.48, 0.48, 0.50 |
| rochers | 0.45, 0.43, 0.40 |
| accessoires | 0.55, 0.45, 0.35 |
| arbres | 0.20, 0.32, 0.14 |
| bordures | 0.70, 0.25, 0.22 |

Les maillages statiques qui ne peuvent pas être lus (maillages squelettiques, maillages
Nanite seuls, niveaux non stockés en ligne) sont comptés : `N meshes could not be read`.

## Contrôles derrière l'export {#checks-behind-it}

Comme indiqué dans le code source, sur le jeu installé :

- Chaque table des matières se lit (version 8).
- Chaque cellule de chaque étape s'ouvre, et chaque composant de maillage statique et de
  scène se décode en finissant exactement à la fin native de sa classe.
- Presque chaque maillage statique échantillonné se décode (les autres sont squelettiques).
  L'étendue décodée d'une tuile de route correspond à ses limites stockées.
- Les niveaux de mip d'une image satellite ont exactement la taille de leurs entrées en
  masse.
- Les tuiles d'un morceau de texture virtuelle sont comptées jusqu'à l'octet, et les tuiles
  de route tombent sur la route qu'elle montre.

## Lacunes connues {#known-gaps}

- Les propriétés propres des composants instanciés ne sont pas lues (voir plus haut). Leur
  placement suppose la racine de l'acteur.
- Les forêts générées par PCG à l'exécution ne sont pas stockées dans les fichiers et ne
  peuvent pas être exportées.
- Les maillages en spline (murs de réapparition invisibles), les composants de décalques et
  les textures propres des modèles placés ne sont pas dessinés. Les modèles sont en
  couleurs unies.
- `--season` n'a aucun effet.
- Un correctif du jeu peut déplacer les emplacements des propriétés. Le lecteur lève une
  erreur au lieu de mal lire, et le parcours indique combien de composants ont échoué.
