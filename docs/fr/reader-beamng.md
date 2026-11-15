---
title: "Fichiers BeamNG"
nav_order: 8
lang: fr
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Fichiers BeamNG : archives de niveau, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive livre des archives zip ordinaires : il n'y a donc aucun conteneur à rétro-ingénierer.
Le travail consiste à lire un niveau **comme le fait le jeu** : monter les archives dans un seul
système de fichiers, suivre les fichiers de scène, et décoder le terrain et les formes compilées. Ces
lecteurs sont atteints par l'export de parcours [BeamNG.drive](course-beamng.md). `identify` reconnaît
aussi une archive de niveau, un `.cdae` et un `.ter`, et `list` et `extract` prennent n'importe lequel
des zips.

Sources : [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Le système de fichiers monté {#the-mounted-file-system}

`Files.of_install(game)` construit un seul index insensible à la casse sur `gameengine.zip`, les zips
`content` (sauf véhicules et sons), et les mods de l'utilisateur (`mods\*.zip`, `mods\unpacked\*`, et un
dossier `levels` de l'utilisateur). Les ajouts postérieurs remplacent les précédents, comme dans le jeu.
Les recherches ignorent la casse, car les références des niveaux ne concordent pas avec les archives sur ce
point (`.DAE` pour un `.dae`). Détails sur [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` trouve un chemin comme le fait le jeu : tel quel, relativement au fichier qui l'a nommé, `x.png`
comme `x.dds`, `x.dae` comme `x.cdae` (préféré), et par un fichier JSON `x.png.link` dont le `path` pointe
dans `/assets`.

## Fichiers de scène {#scene-files}

| Source | Format | Lu |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | un objet JSON par ligne, ou un seul tableau ou dictionnaire JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | les mêmes classes, pour les anciens niveaux sans `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript ou JSON | enfants placés relativement au préfab, jusqu'à 8 niveaux de profondeur |
| `levels\<name>\forest\*.forest4.json` | une instance par ligne | typées par des enregistrements `TSForestItemData` dans `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | le titre du niveau (les clés de traduction sont ignorées) |

**Transformations.** `rotationMatrix` est un ensemble de neuf nombres dont les **lignes** sont les axes
propres de l'objet dans le monde. Les sections de glissière enchaînées le long d'une route suivent la ligne
0 (92 %), et la ligne « haut » s'incline avec la pente de la route. Les anciens préfabs donnent
`rotation = "x y z degrees"`, une rotation droite de cet angle (92 % des chaînes de rails s'alignent avec
elle, 19 % avec le sens opposé). L'échelle multiplie les lignes, et `position` (ou `pos`) est la dernière
ligne. La transformation d'un enfant de préfab est composée avec celle du préfab. Le `groupPosition` du
préfab est un pivot d'éditeur et n'est **pas** soustrait : un chariot de préfab ne repose sur le sol que sans
cela.

Les nombres TorqueScript sont lus avec un motif tolérant, car certains préfabs livrés écrivent des valeurs
telles que `-0.99563-0.0` sans espace.

## Terrain : `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Hauteur en mètres : `position.z + h * maxHeight / 65535`, avec `position`, `squareSize` et `maxHeight`
  tirés du `TerrainBlock` (valeurs par défaut 0, 1 et 2048).
- Les lignes suivent +y. Le point de grille (i, j) est à
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- La couche 255 est un trou.

Vérifié : les nœuds de route se posent sur le terrain à 1-2 cm près (médiane) sur trois niveaux. `h / 32`,
ou l'autre ordre des axes, se trompe de dizaines à centaines de mètres.

## Matériaux {#materials}

Chaque `*.materials.json` hors de `levels\`, plus celui du niveau courant, indexé par `mapTo`, `name` et clé :

| Classe | Champs utilisés |
|---|---|
| `Material`, `CustomMaterial` | carte de couleur (`baseColorMap`, `colorMap` ou `diffuseMap`, premier étage), facteur de couleur, carte d'opacité et facteur, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | carte de base et `diffuseSize`, carte de détail, taille et force, carte macro, taille et force, `groundmodelName`, `annotation` |

Les images sont décodées avec Pillow (DDS, PNG, etc.), en utilisant une version réduite quand c'est possible,
et mises en cache par taille. Une texture illisible retombe sur une couleur unie.

## Formes compilées : `.cdae` {#compiled-shapes-cdae}

`.cdae` est le cache propre au jeu de chaque fichier Collada, écrit en MessagePack. Sa disposition est
**documentée par BeamNG** (documentation.beamng.com/modding/file_formats/cdae/) et le lecteur la suit :

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Ce qui est lu : les limites, les nœuds, les objets, les `details` (niveaux de détail), les rotations de
nœuds par défaut (`Quat16`) et les translations, chaque maillage (sommets, UV, normales, couleurs, primitives
et indices), et les noms de matériaux. Les noms de matériaux se trouvent à la fin du flux, car les séquences
d'un accessoire animé viennent avant eux sous une forme non documentée.

Deux points que la documentation ne précise pas, réglés sur les fichiers `.dae` dont les formes sont issues :

- **Les rotations de nœuds sont celles de Torque.** Un `Quat16` lu de la façon classique tourne dans le
  mauvais sens. Sa matrice doit être **transposée**. Avec cela, les limites monde de chaque nœud correspondent
  au Collada au millimètre près. Sans cela, elles sont décalées de 38 cm en médiane.
- **Les unités et axes sont déjà appliqués.** Un fichier Collada écrit en centimètres ou en Y vers le haut
  sort du cache en mètres, Z vers le haut.

Les niveaux de détail sont les `details` dont la taille est positive ou nulle, du plus grand au plus petit.
Les tailles négatives sont des maillages de collision et de ligne de visée, jamais dessinés. Les objets nommés
`colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` ou `imposter` ne sont jamais dessinés. Seuls
les maillages standard et triés sont dessinés. Les maillages skinnés (personnages, véhicules) et de décalques
ne le sont pas. Les bandes et éventails de triangles sont dépliés, et les faces sont réorientées pour concorder
avec les normales stockées, ce que l'enroulement de Torque ne garantit pas.

Vérifié : presque toutes les formes livrées se lisent. Les deux autres sont d'une version plus ancienne.

## Repli Collada : `.dae` {#collada-fallback-dae}

Pour les formes sans `.cdae` (mods, et la rare forme dont le cache est plus ancien), le fichier Collada est
lu comme le fait l'importeur de Torque, dans la même structure :

- Niveaux de détail d'après la convention de nommage de Torque : le nombre final du nom d'un nœud de
  maillage est la taille en pixels à laquelle il est dessiné (`barrier75`, `barrier40`). Un nombre négatif, ou
  un nom `collision`/`Colmesh`/`LOS`/`nulldetail`, n'est jamais dessiné. Une forme sans cette convention n'a
  qu'un niveau.
- Unités d'après `<unit meter>`, et Y vers le haut transformé en Z vers le haut.
- UV retournés vers la convention du cache (v descend dans l'image).

Vérifié contre le `.cdae` du jeu pour les mêmes fichiers : presque toutes les limites échantillonnées à 1 cm
près, 583 avec le même nombre de triangles, 94 % des UV de matériaux identiques. Le test sur jeu installé exige
que 90 % des 60 paires de formes au plus de l'archive d'art partagée concordent à 1 cm près.

## Non lu {#not-read}

- La végétation au sol (herbe procédurale) et tout ce qui est généré à l'exécution.
- Les séquences animées et le skinning.
- Véhicules et sons (jamais montés).
