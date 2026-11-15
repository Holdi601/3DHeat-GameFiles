---
title: BeamNG.drive
nav_order: 2
lang: "fr"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Export de parcours : BeamNG.drive {#course-export-beamngdrive}

L'export BeamNG lit un niveau de la façon dont le jeu le monte, puis écrit le même type de
fichier que l'export Forza : du sol par carré de 512 m avec une texture cuite, la route et
le sol meuble comme parties à part, les modèles placés par catégorie, et l'eau.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Sources : [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (installation, système de fichiers, scène, terrain, matériaux),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (l'export),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) et
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (formes).
Formats de fichiers en détail : [Fichiers BeamNG](reader-beamng.md).

## Le repère du tour {#the-laps-frame}

L'export `course` attend des positions BeamNG dans le **repère de la visionneuse** :
`(x, z, -y)` du monde en Z vers le haut de BeamNG, en mètres. C'est la rotation qu'applique
l'enregistreur de télémétrie 3DHeat. L'export ramène le tour dans le repère de BeamNG
(`(x, -z, y)`), travaille dans ce repère, puis écrit tout de nouveau dans le repère de la
visionneuse. C'est une rotation, pas un miroir : rien ne sort inversé. Un tour enregistré
dans le repère brut de BeamNG ne serait pas placé correctement. Ceci n'a pas été testé avec
d'autres enregistreurs.

Le jeu est considéré comme BeamNG quand le fichier `heat3d-lap` indique `"game": "beamng"`,
ou quand vous passez `--game beamng`.

## Trouver l'installation {#finding-the-install}

- `--install <dossier>` : le dossier qui contient `gameengine.zip` et `content`.
- Sinon, le `steamapps\common\BeamNG.drive` de chaque bibliothèque Steam est vérifié pour ces deux éléments.
- Si aucun des deux ne fonctionne : "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Le système de fichiers {#the-file-system}

BeamNG livre des archives zip simples et les monte dans un système de fichiers unique auquel
les niveaux se réfèrent (`/art/shapes/...`, `/assets/materials/...`). L'export construit la
même chose : un seul index sans distinction de casse sur

1. `gameengine.zip`,
2. chaque `*.zip` sous `content`, sauf `content\vehicles\*` et les archives dont le nom commence par `art_sound` ou `audio`,
3. le contenu de l'utilisateur, dans l'ordre le plus récent d'abord : sous
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` et `%LOCALAPPDATA%\BeamNG.drive`, le dossier
   `current` et le dossier de version numéroté le plus élevé. De chacun : `mods\*.zip`,
   chaque dossier de `mods\unpacked`, et le dossier utilisateur lui-même s'il a un dossier
   `levels`.

Les ajouts plus tardifs l'emportent, comme dans le jeu : un mod remplace ce qu'il remplace.
Les mods sont toujours inclus dans un export de parcours.

Les chemins qu'un niveau nomme sont résolus comme le fait le jeu : tels quels, puis par
rapport au fichier qui les a nommés, et pour chacun aussi comme le `.dds` dans lequel une
texture a été compilée, le `.cdae` dans lequel un `.dae` a été compilé, ou par un fichier
`.link` qui pointe dans `/assets`.

## Quel niveau {#which-level}

Sans `--level`, chaque niveau est noté selon la part du tour qui se trouve sur lui :

- Jusqu'à 500 échantillons du tour, répartis régulièrement, sont utilisés.
- Pour le `TerrainBlock` de chaque niveau, l'étendue du terrain est lue dans les cinq premiers octets de son fichier `.ter`, si bien qu'un niveau loin du tour ne coûte rien. Si au moins 30 % des échantillons sont dans l'étendue, les hauteurs sont lues. Un échantillon compte comme **sur** le terrain quand il est entre 1 m sous et 3 m au-dessus (`ON_GROUND`), car le point de référence d'une voiture est sa carrosserie, pas ses pneus.
- Si aucun niveau n'atteint 50 %, les niveaux sont aussi notés sur leurs **routes**. Certains niveaux se prolongent au-delà de leur carte de hauteurs (leurs bords continuent en plaques de rocher). Un échantillon est sur une route quand il se trouve à moins de la demi-largeur de la route plus 4 m (au moins 6 m) d'un segment `DecalRoad`, et entre 2 m sous et 4 m au-dessus.
- Le meilleur niveau l'emporte s'il atteint au moins 30 %. Sinon, l'export s'arrête et liste les trois meilleurs : "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

La console affiche `on <level>: 87% of the lap lies on its terrain` (ou `roads`).
`--level` est comparé sans distinction de casse aux noms de dossiers de niveaux.

## Lire le niveau {#reading-the-level}

Ce dont un niveau est fait, chaque partie vérifiée sur les niveaux livrés
(détails dans [Fichiers BeamNG](reader-beamng.md)) :

- **Scène** : `levels\<name>\main\**\*.level.json` (un objet JSON par ligne, ou un tableau JSON), ou un fichier `.mis` pour les anciens niveaux. L'outil lit les objets `TSStatic` (modèles placés, en ignorant les cachés), `Prefab` (imbriqués jusqu'à 8 niveaux, fichiers TorqueScript `.prefab` ou `.prefab.json`), `DecalRoad` (routes peintes), `TerrainBlock`, `WaterPlane`, `WaterBlock` et `River`.
- **Objets de forêt** : `levels\<name>\forest\*.forest4.json`, typés par les enregistrements de `managedItemData.json`. Les barrières, clôtures et rochers sont aussi souvent des objets de forêt que les arbres.
- **Terrain** : le champ de hauteurs `.ter` et sa carte de couches.
- **Matériaux** : chaque `*.materials.json` en dehors de `levels\`, plus ceux de ce niveau.

## Le couloir et les décalcomanies de route {#the-corridor-and-the-road-decals}

Le couloir est `--margin` mètres autour du tour, dans le plan x/y de BeamNG (voir
[Export de parcours](course-export.md#the-corridor)). Un couloir d'atteinte de
`margin + 60 m` sélectionne les candidats.

**Les décalcomanies de route** (`DecalRoad`) forment la plupart des routes de BeamNG : peintes
sur le terrain, et non modélisées. Les décalcomanies dont l'étendue touche le couloir
d'atteinte sont prises dans l'ordre de dessin du jeu (`renderPriority` décroissant, puis
ordre du fichier), et disposées en rubans :

- Les nœuds (x, y, z, largeur) sont interpolés par une **spline de Catmull-Rom centripète** environ tous les 1 m. La variante uniforme boucle sur elle-même là où les nœuds se resserrent dans un virage en épingle. Les routes en boucle se referment.
- Chaque bord prend la hauteur du terrain là où le terrain est à moins de 1,5 m de la hauteur propre de la route, et garde la hauteur de la route ailleurs (sur un pont).
- Le nom du matériau décide de ce que la décalcomanie peint :

| Type | Le nom du matériau contient (la première correspondance l'emporte) |
|---|---|
| traces de pneus | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| superposition (cosmétique) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| marquages | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| meuble | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| route | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| superposition | tout le reste |

## Le sol {#the-ground}

Le champ de hauteurs du terrain à l'intérieur du couloir devient des triangles :

- Un quad par carré de terrain dont le centre est dans le couloir. Les carrés de couche 255 (trous) sont ignorés. Chaque quad est formé de deux triangles, la diagonale alternant comme dans le terrain de Torque.
- Les hauteurs valent `position.z + h * maxHeight / 65535`. Les normales viennent des différences de hauteur.
- Chaque carré est classé selon sa **couche** : le nom de la couche avec son modèle de sol et son annotation de matériau de terrain. Les mots de pavage en font `road`, `grass/forest/rock/moss/leaves/cliff/stone` en font `terrain`, et les mots de meuble en font `loose` (gravier et terre). Le reste est `terrain`.
- Puis les **décalcomanies de route et de meuble** recouvrent les carrés qu'elles couvrent, dans l'ordre de dessin : la dernière peinte décide.
- Les sommets sont séparés par carré de 512 m (`floor(x / 512)`, `floor(y / 512)`), si bien que chaque partie se projette dans exactement une image : `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

La console affiche `what the ground is made of` avec le nombre de triangles par type.

### Surface de roulage modélisée {#modelled-driving-surface}

Les circuits de BeamNG sont aussi souvent des modèles que du terrain. La piste d'un circuit
peut être un seul maillage, avec ses lignes, son caoutchouc et ses bandes rugueuses comme
maillages propres par-dessus. Ainsi, les modèles placés des catégories route, bordures,
bas-côtés, accessoires et ponts sont fouillés pour trouver une surface de roulage. Par
matériau :

| Surface | Décidée par (première correspondance) |
|---|---|
| traces de pneus | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` dans le nom, le type de sol ou l'annotation |
| marquages | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` dans le nom du matériau |
| bordures | `rumble`, `kerb`, `curb` |
| route | type de sol `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, ou le nom contient `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| meuble | type de sol `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| bas-côté | `sidewalk` |
| (la catégorie propre du modèle) | pour les modèles déjà classés route, bordures ou bas-côtés |

Parmi ces matériaux, les triangles **tournés vers le haut** (normale z supérieure à 0,5) à
l'intérieur du couloir sont retirés du modèle et deviennent du sol. Ils sont peints dans la
texture cuite de la tuile et écrits comme des parties telles que
`ground:road 3_-2 asphalt_light`. Les marquages et les traces de pneus sont seulement peints.
Les triangles restants du modèle restent avec lui. Ces modèles ne sont jamais simplifiés ni
retirés par le budget, car un tracé grossier est un mauvais tracé.

## La texture de sol cuite {#the-baked-ground-texture}

Chaque carré de 512 m qui a du sol reçoit une image de `--texture-size` pixels (2048 = 25 cm
par pixel), dessinée comme le jeu dessine son sol :

1. **Couches de terrain.** Par pixel, les couches des quatre carrés de terrain autour sont mélangées de façon bilinéaire. Chaque couche est colorée comme le jeu la colore : la **carte de base** du matériau étirée sur `diffuseSize` mètres (ou sur tout le terrain), puis les cartes de **détail** et **macro** en superpositions grises (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutre). Leurs valeurs par défaut se répètent tous les 2 m et 60 m, avec des forces de 0,5 et 0,3, sauf si le matériau dit autrement. Une couche sans matériau prend la couleur unie de sa surface. La ligne 0 de la carte de base est le nord.
2. **Décalcomanies de route** peintes seulement sur le terrain, dans l'ordre de dessin, chacune avec sa propre texture, sa carte d'opacité, sa teinte et son opacité, le long du ruban. Les niveaux livrés utilisent des priorités autour de 12 à 16 pour les bases d'asphalte, 10 pour les marquages et 4 pour le caoutchouc.
3. **Surface de roulage modélisée** vue d'en haut : d'abord les bases, puis les superpositions, chacune dans la texture répétée propre au modèle à un texel par pixel de cuisson.
4. **Décalcomanies qui se projettent aussi sur les objets** (`overObjects`), en dernier.

Avec `--no-textures`, rien n'est cuit : les parties de sol reçoivent des couleurs unies, et
les marquages et traces de pneus modélisés deviennent des parties à part, relevées de **3 cm**.

## Modèles placés {#placed-models}

Les candidats sont tous les `TSStatic`, enfants de préfabriqués et objets de forêt dont
l'origine se trouve dans le couloir d'atteinte. Un candidat est dessiné si la boîte englobante
mondiale de sa forme touche le couloir.

La **catégorie** vient de l'annotation propre du niveau et du chemin de la forme. La première
règle qui correspond l'emporte :

| Catégorie | Annotation | Le chemin ou le nom contient |
|---|---|---|
| arrière-plan (jamais dessiné) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| bordures | | `kerb`, `curb`, `rumble` |
| route | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| bas-côté | `SIDEWALK`, `COBBLESTONE` | |
| arbres (seulement avec `--trees`) | `NATURE` | tree, foliage, bush, grass, plant et mots semblables |
| rochers | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barrières | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| panneaux | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| ponts | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastructure | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| bâtiments | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| accessoires | | tout le reste |

**Les formes** sont lues dans le `.cdae` compilé, ou dans le Collada `.dae` quand il n'existe
pas de cache (mods). Une forme qu'on ne peut pas lire est comptée :
`N copies of M models could not be read`. Les matériaux nommés ou texturés `invisible`,
`collision` ou `nodraw` ne sont jamais dessinés.

**Textures.** Les modèles sont regroupés par catégorie et matériau en parties nommées
`structure:<catégorie> <matériau>` (ou `ground:kerbs <matériau>`). Un groupe reçoit la
texture de couleur de son matériau à **256 px** au plus seulement si ses UV restent entre 0
et 1 (98 % des sommets entre -0,02 et 1,02). La visionneuse range les textures dans un atlas
et ne peut pas en répéter une. Un groupe dont la texture se répète est dessiné dans la
couleur moyenne de la texture (pondérée par l'alpha, en sRGB, multipliée par la teinte du
matériau), ou dans la couleur de la catégorie s'il n'a pas de texture.

**Détail.** Il suit le schéma commun décrit dans [Niveaux de détail et budget](detail-budget.md).
Les niveaux de détail de BeamNG sont les `details` de la forme (taille en pixels la plus
grande en premier). Au-delà du budget, les copies les plus lointaines partent en premier. Les
bordures et les modèles portant une surface de roulage ne sont jamais simplifiés ni retirés.

`--no-placed` retire les structures mais garde la surface de roulage modélisée. `--trees`
ajoute la catégorie des arbres.

## Eau {#water}

| Source | Dessinée comme |
|---|---|
| `WaterPlane` (la mer) | un quad de 4 m à la hauteur de l'eau pour chaque cellule du couloir où aucun terrain n'atteint cette hauteur |
| `WaterBlock` | un quad, le carré unité à z = 0 local dans la transformation du bloc (donc son échelle règle la taille), s'il touche le couloir ; savoir si z = 0 est la surface du bloc n'est pas vérifié |
| `River` | un ruban passant par ses nœuds s'il touche le couloir |

Toute l'eau forme une seule partie plane, `water:water`.

## Non dessiné {#not-drawn}

- La couverture du sol (herbe procédurale).
- Le décor placé en bordure du monde (`backdrop` et semblables).
- Les textures de modèles qui se répètent, qui ressortent comme une couleur moyenne (voir plus haut).
- Les maillages squelettés (véhicules, personnages) et les maillages de décalcomanie à l'intérieur des formes.

## Vérifications {#checks-behind-it}

Comme indiqué dans la source, mesuré sur les niveaux livrés :

- Les nœuds de route se trouvent sur le terrain à 1-2 cm près (médiane) sur les niveaux vérifiés, avec `h * maxHeight / 65535` et les lignes le long de +y. `h / 32` ou l'autre ordre des axes manquent de dizaines à centaines de mètres.
- Les sections de rail enchaînées le long d'une route suivent la ligne 0 de `rotationMatrix` (la grande majorité).
- La rotation du nœud `.cdae` doit être transposée. Avec cela, les boîtes du monde correspondent au `.dae` source au millimètre près. Sans cela, elles sont décalées de 38 cm (médiane).
- Exporté sur plusieurs niveaux livrés de tous les types, en quelques secondes à quelques minutes chacun.
