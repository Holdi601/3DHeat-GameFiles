---
title: Commandes
nav_order: 2
lang: fr
source: commands.md
source_hash: "6c8d37db40e5"
nav_exclude: true
search_exclude: true
---
# Commandes {#commands}

Chaque commande s'exécute avec `python -m heat3d_gamefiles <verbe> ...` depuis le
dossier du dépôt. Les verbes sont dans l'ordre où on en a généralement besoin : quel
est ce fichier, qu'est-ce qu'il contient, donne-moi cet élément, et transforme un tour
en parcours.

| Verbe | Prend | Fait |
|---|---|---|
| [`identify`](#identify) | n'importe quel fichier | donne le format du conteneur en lisant ses octets |
| [`list`](#list) | un `.pak` Unreal ou un `.utoc` IoStore, un `.vpk` Source 2, un `.minizip` ForzaTech, ou un zip | liste ses entrées |
| [`extract`](#extract) | la même chose | écrit une entrée sur le disque |
| [`meshes`](#meshes) | un `SerializedFile` Unity | liste et vérifie ses maillages |
| [`course`](#course) | un tour | exporte le parcours autour de lui (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | une bibliothèque de tours enregistrés | lance `course` sur chaque parcours qu'elle contient (Forza) |
| [`terrain`](#terrain) | un dossier de piste Forza | découpe une zone selon des coordonnées du monde |
| [`levels`](#levels-and-level-frostbite) | un jeu Frostbite installé (Battlefield 6) | liste ses niveaux |
| [`level`](#levels-and-level-frostbite) | le nom d'un niveau | exporte le niveau : terrain, maillages placés, et éventuellement leurs cartes de couleur (Battlefield 6) |
| [`cars`](#cars) | un Forza installé | chaque voiture en faible détail, dans un seul fichier pour l'onglet course de la visionneuse |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | un jeu Unreal 5 | liste ses cartes World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | le nom d'une carte | exporte la carte : paysage, structures HLOD, eau |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | un Arma Reforger installé | liste ses mondes |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | le nom d'un monde | exporte le monde : terrain dans ses couleurs, la mer, les bâtiments en boîtes |

**Lire les exemples :** `<x>` signifie qu'il faut remplacer par votre propre valeur, sans
les chevrons ; `[...]` indique une option ; entourez un chemin contenant des espaces de
"guillemets doubles", par exemple `"C:\Games\My Game"`. Vous débutez ? Voir
[Avant de commencer](before-you-start.md). L'aide complète (`--help`) de chaque verbe
se trouve dans la [Référence des commandes](../cli-reference.md).

À chaque démarrage, le programme peut d'abord chercher une version plus récente. Voir
[Mises à jour](updates.md). `HEAT3D_NO_UPDATE=1` désactive cette vérification.

Source : [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Pages pas à pas : [Inspecter les archives](inspecting-archives.md), [Export de parcours](course-export.md),
[Niveaux complets](whole-levels.md), [Voitures Forza](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Codes de sortie {#exit-codes}

| Code | Signification |
|---|---|
| 0 | réussi |
| 1 | le travail a échoué (tour illisible, aucun jeu trouvé, rien à exporter, un parcours de `courses` a échoué ; pour `list` et `extract`, un fichier qui n'est aucune des archives qu'ils lisent, un fichier qu'on ne peut ni ouvrir ni lire - un pak chiffré sans `--key`, un conteneur IoStore chiffré - ou une entrée absente de l'archive) |
| 2 | mauvais arguments (argparse), un chemin qui n'existe pas, une `--key` qui n'a pas 64 chiffres hexadécimaux, ou `terrain` reçu à la fois avec `--box` et `--route`, ou sans l'un ni l'autre |

Les échecs de `list` et `extract` tiennent chacun sur une ligne de la sortie d'erreur
standard, et non sur une trace Python.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <chemin>
```

Cette commande lit le fichier et indique quel conteneur il est. Elle ne se fie pas à
l'extension (seule exception : un `.ucas`, voir plus bas). Elle essaie les formats dans
cet ordre et s'arrête au premier qui se lit :

1. **Unreal `.pak`** : un pied de page avec la signature pak dans les 1 024 derniers
   octets. Affiche la version, le décalage et la taille de l'index, si l'index est
   chiffré, et les méthodes de compression.
2. **Unreal IoStore `.utoc`** : la signature IoStore au début. Affiche la version, le
   nombre de morceaux et si le conteneur est chiffré ; pour un conteneur non chiffré,
   le nombre de fichiers que nomme son répertoire (et sous quel point de montage), les
   méthodes de compression, et si son `.ucas` se trouve à côté. Un `.ucas` n'a pas
   d'en-tête à lui : il est reconnu grâce au `.utoc` du même nom à côté, et `identify`
   nomme ce fichier.
3. **ForzaTech `.minizip`** : la signature `PGZP`. Affiche la version, le nombre
   d'entrées et de segments, et si le `ChunkContentsMiniZip<n>.txt` qui nomme les
   entrées se trouve à côté (et, si oui, s'il en nomme autant qu'il y en a).
4. **zip** : un en-tête de fichier zip local au début. Affiche le nombre d'entrées, les
   six extensions les plus fréquentes, et les noms de niveaux quand les entrées se
   trouvent sous `levels/<nom>/`, comme dans une archive de niveau BeamNG.drive.
5. **Unity** : un paquet `UnityFS` (affiche la version du moteur et le nombre d'entrées)
   ou un `SerializedFile` nu (affiche le format, la version du moteur, le nombre
   d'objets et les six classes les plus fréquentes).
6. **Frostbite `.toc`** : affiche le type (`plain` ou `signed`), l'endroit où commence
   l'arbre, et soit le nombre de ressources (table de sections binaire), soit le nombre
   de superbundles (arbre DbObject).
7. **Source 2 `.vpk`** : affiche la version, le nombre d'entrées, et le premier maillage
   de navigation `.nav` si l'archive en contient un.
8. **BeamNG `.cdae`** : version de forme 31 qui se lit. Affiche le nombre de maillages,
   le nombre de niveaux de détail dessinés et les premiers matériaux.
9. **BeamNG `.ter`** : il n'a pas de signature, donc tout doit concorder - un côté de 2 à
   16 384, autant de hauteurs au carré et d'octets de couche, puis 1 à 255 noms de couche
   imprimables. Affiche la version, la taille et les noms de couche.
10. **ForzaTech `.modelbin`** : affiche la version, le nombre de morceaux et les six
    étiquettes de morceau les plus fréquentes. Le contenu des morceaux n'est pas décodé ici.

Les formats qui ont leur propre signature (2 à 4) passent avant Unity et Frostbite, dont
les vérifications lisent le fichier entier : une archive Forza fait des dizaines de
gigaoctets.

Si aucun ne correspond, la commande affiche `not a format this tool reads` (format non
lu par cet outil) et la dernière raison, celle de la vérification ForzaTech.

Exemple (fictif) :

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archive> [--filter TEXTE] [--limit N] [--key HEX]
```

| Option | Défaut | Signification |
|---|---|---|
| `<archive>` | obligatoire | un `.pak` Unreal ; un `.utoc` IoStore (ou le `.ucas` à côté) ; un `.vpk` Source 2 (pour les VPK découpés, le `_dir.vpk`) ; un `.minizip` ForzaTech ; un zip, comme les archives de niveaux et de contenus de BeamNG |
| `--filter TEXTE` | aucun | seulement les chemins contenant TEXTE, sans tenir compte de la casse |
| `--limit N` | 50 | affiche au plus N entrées (le nombre total est toujours affiché) |
| `--key HEX` | aucun | une clé AES-256 que vous avez déjà, 64 chiffres hexadécimaux, avec ou sans `0x`. Seul un `.pak` chiffré l'utilise. Tout ce qui n'a pas 64 chiffres hexadécimaux est refusé avant l'ouverture de l'archive (code de sortie 2) |

L'outil détermine le format à partir des octets : une table des matières IoStore, un
`.minizip` et un VPK par la signature qui les commence, un zip par son en-tête de fichier
local, et un `.pak` par le pied de page à sa fin. Un `.ucas` n'a pas d'en-tête et s'ouvre
grâce au `.utoc` du même nom. Un fichier qui n'est aucun de ceux-là est refusé avec
`<file> is not an archive list and extract read (...)`. Un fichier qui en est un mais
qu'on ne peut pas ouvrir est refusé avec la raison du lecteur : un pak chiffré sans
`--key`, un conteneur IoStore chiffré, une version de pak qu'il ne lit pas. Dans tous les
cas, c'est une seule ligne et le code de sortie 1.

Chaque ligne affiche la taille non compressée, la méthode de compression et le chemin :

| Archive | Méthode | Chemins |
|---|---|---|
| `.pak` | `none`, ou le nom indiqué dans le pied de page (`Zlib`, `Oodle`, `Gzip`...) | avec le point de montage de l'archive, par exemple `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, ou la méthode du conteneur (`Oodle`, `Zlib`...), telle que stockée dans son premier bloc | avec le point de montage, par exemple `../../../<Project>/Content/...`. Un conteneur sans index de répertoire ne nomme aucun fichier et est refusé |
| `.vpk` | toujours `stored` | tel qu'il figure dans le répertoire |
| `.minizip` | `lz4`, `deflate` ou `stored` | tels qu'écrits dans le `ChunkContentsMiniZip<n>.txt` à côté de `GeoChunk<n>.minizip`, sans le préfixe du poste de compilation (antislashs, comme les écrit le jeu). L'archive ne stocke aucun nom : sans ce fichier, les entrées sont `#0`, `#1`... Une liste dont le nombre de lignes diffère de celui des entrées est refusée : les deux ne vont pas ensemble |
| zip | `stored`, `deflate`, ... | tels qu'ils sont stockés ; les dossiers ne sont pas listés |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FICHIER] [--key HEX]
```

| Option | Défaut | Signification |
|---|---|---|
| `<archive>` | obligatoire | comme pour `list` |
| `<entry>` | obligatoire | le chemin exactement tel que `list` l'affiche (sensible à la casse) ; dans un `.minizip`, `#<numéro>` fonctionne aussi |
| `--out FICHIER` | le nom de fichier de l'entrée (après le dernier `/` ou `\`), dans le dossier courant | où écrire ; les dossiers parents sont créés |
| `--key HEX` | aucun | comme pour `list` |

L'entrée est déchiffrée (pak, avec une clé), décompressée, puis écrite. La commande
affiche `<bytes> bytes -> <file>`. Si le chemin n'est pas dans l'archive, la commande
se termine avec le code 1. Il en va de même pour une entrée qu'on ne peut pas lire (une
entrée chiffrée sans clé, compressée en Oodle sans la bibliothèque Oodle), avec la raison
sur une ligne. Une entrée VPK n'est pas vérifiée ici par son CRC. Le lecteur a une méthode
`verify()` pour cela (voir [VPK Source 2](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Option | Défaut | Signification |
|---|---|---|
| `<path>` | obligatoire | un `SerializedFile` Unity nu (`sharedassets0.assets`, `level0`...), pas un paquet |
| `--limit N` | 25 | décode et affiche au plus N maillages |

La commande affiche le nombre d'objets `Mesh`, puis une ligne par maillage : le nom (40
premiers caractères), le nombre de sommets et de triangles, et `ok` ou `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` signifie que les sommets décodés ne reproduisent pas la boîte englobante
que Unity a stockée pour le maillage, à 2 % près de la taille de la boîte. C'est la
vérification propre à la lecture (voir [Unity](reader-unity.md)). Un maillage qu'on ne peut
pas lire est signalé avec la raison, et compte dans la limite. Les données de sommets d'un
fichier `.resS` sont lues dans le dossier où se trouve le conteneur.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <tour> [-o FICHIER] [options]
```

Cette commande exporte le parcours autour d'un tour : le sol dans une bande de chaque côté
de la conduite, et ce qui s'y dresse, dans un seul `.glb`. Elle trouve elle-même le reste :
quel jeu, quelle copie installée, quelle piste, quel niveau ou quelle étape, et (pour
Assetto Corsa Rally) dans quel sens sont les axes. Voir [Export de parcours](course-export.md).

`<tour>` peut être l'un des éléments suivants (détails dans [Entrées de tour](lap-inputs.md)) :

- un fichier de tour : JSON de route, JSON de tour FH Companion, JSON `heat3d-lap`, `.npz`, ou `.csv` avec les colonnes x, y, z
- un dossier de fichiers de tours, parcouru récursivement (un parcours enregistré complet)
- le **nom** d'un parcours, cherché dans la bibliothèque FH Companion à `%LOCALAPPDATA%\FHCompanion\laps`

### Options {#options}

| Option | Défaut | Jeux | Signification |
|---|---|---|---|
| `-o`, `--out FICHIER` | `<nom du parcours>.glb` dans le dossier courant | tous | où écrire ; le nom est mis en minuscules, et les suites d'autres caractères sont remplacées par `_` |
| `--game {forza,beamng,acrally}` | ce qu'indique le fichier de tour, sinon `forza` | tous | le jeu d'où vient le tour |
| `--margin M` | 80 | tous | mètres de sol conservés de chaque côté de la conduite |
| `--texture-size {2048,1024,512}` | 2048 | tous | pixels de texture du sol par tuile de 512 m (2048 = 25 cm par pixel) |
| `--no-textures` | désactivé | tous | couleurs unies seulement : un fichier bien plus petit. Pour Forza, cela supprime aussi la séparation route/bord (voir plus bas) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | les cartes de sol et les textures de modèles de quelle saison |
| `--no-placed` | désactivé | tous | terrain seulement : ni bordures, ni barrières, ni panneaux, ni bâtiments. Pour BeamNG, les surfaces de roulage modélisées en maillages sont quand même gardées |
| `--trees` | désactivé | tous | place aussi la végétation (Forza : arbres, buissons et objets cassables ; BeamNG : arbres ; AC Rally : arbres et feuillage instancié) |
| `--detail-budget N` | automatique | tous | un plafond de triangles pour tout ce qui est placé ; voir [Niveaux de détail et budget](detail-budget.md) |
| `--track DIR` | cherché | Forza | le dossier de piste (sous `media\Tracks`, contenant `GeoChunk0.minizip`) si le jeu installé ne doit pas être cherché |
| `--level NOM` | trouvé à partir du tour | BeamNG, AC Rally | le niveau (nom du dossier BeamNG) ou l'étape (nom de carte AC Rally), sans tenir compte de la casse |
| `--install DIR` | cherché dans les bibliothèques Steam | BeamNG, AC Rally | BeamNG : le dossier qui contient `gameengine.zip`. AC Rally : le dossier du jeu, ou son `acr\Content\Paks` / `Content\Paks` |

Les options qui ne s'appliquent pas à un jeu sont ignorées sans avertissement. Par
exemple, `--season` ne fait rien pour BeamNG et AC Rally, et `--track` ne fait rien pour
eux non plus.

### Quel jeu {#which-game}

Le jeu est pris dans `--game`, puis dans le champ `game` d'un fichier `heat3d-lap` (ou de
la ligne de description `# {...}` d'un CSV), et par défaut c'est Forza. Un dossier prend le
jeu que nomment ses fichiers, s'il n'en nomme qu'un seul ; un fichier qui n'en nomme aucun
(un tour FH Companion, `course.json`, un CSV sans ligne de description) ne compte pas (voir
[Entrées de tour](lap-inputs.md)).

| Valeur | Export |
|---|---|
| commence par `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` ou `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | refusé : "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | refusé : "tracks ship in a protected format that is not a file-extraction target" |
| tout le reste | refusé : "there is no course reader for <game> yet" |

Un refus indique aussi les solutions de rechange : reconstruire le parcours à partir du jeu
(3DHeat GameCapture), ou analyser les tours sans parcours, car l'onglet Analyse de course
de la visionneuse dessine une route à partir d'eux.

### Exemples {#examples}

```
# Un parcours depuis la bibliothèque FH Companion, par son nom
python -m heat3d_gamefiles course "Example Circuit"

# Un fichier de tour, une bande plus étroite, un fichier plus petit
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Textures d'hiver, arbres inclus
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Un plafond strict de 500 000 triangles placés
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Un dossier de piste donné directement (jeu installé hors de Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG : nommer le niveau, indiquer l'installation
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, avec un CSV de tour simple qui ne dit pas son jeu
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Exemple de sortie (Forza, chiffres fictifs) :

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Chaque voiture d'un Forza installé, au faible détail propre au jeu, dans un seul fichier
pour l'onglet course de la visionneuse : le modèle `ProxyLOD` que porte chaque archive de
voiture sous `media/Cars`, d'environ 900 triangles, avec le numéro de la voiture tel que la
télémétrie l'indique, sa marque, son étiquette de modèle et son année d'après le nom de
l'archive, ainsi que ses roues et ses feux arrière. Cela prend quelques secondes et écrit
environ 5 Mo. Relancez-la quand le jeu reçoit de nouvelles voitures. Une archive sans ce
modèle (un accessoire de circulation) est signalée et laissée de côté. Le format est décrit
dans [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Les formes sont en mètres, celles du jeu : 1:1 avec la voiture. Le fichier contient le
contenu du jeu, il est donc destiné à la machine où il a été fait, et non à être partagé.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o DOSSIER] [options]
```

Cette commande lance l'export `course` de Forza sur chaque dossier de parcours d'une
bibliothèque de tours enregistrés, en écrivant un `<nom>.glb` pour chacun. Elle ne concerne
que Forza. Elle appelle directement l'export Forza et ne lit ni `--game`, ni `--level`, ni
`--install`.

| Option | Défaut | Signification |
|---|---|---|
| `-o`, `--out DOSSIER` | `courses` | le dossier où écrire (créé s'il manque) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | la bibliothèque de tours |
| `--only TEXTE [TEXTE ...]` | tous | seulement les parcours dont le nom de dossier contient l'un de ces textes (sans tenir compte de la casse) |
| `--force` | désactivé | exporte de nouveau ce qui a déjà un `.glb` |
| `--track DIR` | cherché | comme pour `course` |
| `--margin M` | 80 | comme pour `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | comme pour `course` |

Ce qui compte comme dossier de parcours : un sous-dossier direct de la bibliothèque dont le
nom contient ` (course_`, qui est la façon dont FH Companion les nomme, par exemple
`Example Circuit (course_1200_3400_to_1175_3400)`. La partie à partir de ` (course_` est
retirée du nom.

Comment se déroule une exécution :

- Un parcours dont le `.glb` existe déjà est passé (`kept`), sauf si `--force` est donné ; ainsi une exécution interrompue reprend là où elle s'est arrêtée.
- Un parcours qui échoue (tours illisibles, mémoire insuffisante, pas de terrain...) est signalé `FAILED`, et l'exécution continue.
- À la fin, elle affiche un tableau : état, taille en Mo, secondes écoulées et nom, puis `<n> of <total> courses in <dossier>`.
- Le code de sortie est 1 si un parcours a échoué.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <dossier de piste> -o FICHIER (--box X0 Z0 X1 Z1 | --route FICHIER) [options]
```

C'est la découpe Forza avec tout détaillé à la main : vous donnez le dossier de piste et une
zone, pas un tour. C'est utile quand la zone voulue est un rectangle plutôt qu'un trajet.

| Option | Défaut | Signification |
|---|---|---|
| `<path>` | obligatoire | un dossier de piste Forza sous `media\Tracks` (contenant `GeoChunk*.minizip`) |
| `-o`, `--out FICHIER` | obligatoire | le `.glb` à écrire |
| `--box X0 Z0 X1 Z1` | | la zone, en mètres du jeu (x et z, comme les rapporte la télémétrie) ; coins dans n'importe quel ordre |
| `--route FICHIER` | | un JSON de route avec `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, tel qu'écrit par `heat3d_capture route` et `heat3d_capture laps` ; lu en UTF-8, avec ou sans marque d'ordre des octets |
| `--margin M` | **100** | mètres ajoutés autour des limites d'un tracé, et largeur du couloir quand le tracé a une ligne |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | comme pour `course` |

Donnez exactement un de `--box` et `--route`, sinon le code de sortie est 2. Avec
`--route`, la découpe correspond aux `bounds` du tracé (`min`/`max`, x et z) élargis de la
marge. Si le fichier contient aussi au moins 10 positions, la découpe se resserre sur un
couloir de `--margin` mètres autour d'elles, et les modèles placés reçoivent leur détail
selon leur distance à cette ligne. Avec `--box`, toute la zone est gardée, et le détail va
à ce qui se trouve le plus près du centre de la zone.

La hauteur ne fait jamais partie de la découpe. Une zone en dehors de la carte, ou en mer,
donne "no terrain there" (code de sortie 1), et non une erreur sur les coordonnées.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels et level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install DOSSIER]
python -m heat3d_gamefiles level <level> [-o FICHIER] [--install DOSSIER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXTE ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` liste les niveaux qu'un jeu Frostbite installé livre, d'après le nom de leur table
(`levels/<level>/<level>.toc`), avec sa taille et sa provenance : `Data` pour le jeu de
base, `Update/<pack>` pour une mise à jour, et le nombre de tables haute résolution qui s'y
ajoutent. Un niveau livré par une mise à jour a une petite table de morceaux, et il y en a
aussi une dans le jeu de base ; la table qui contient les bundles du niveau est le niveau
(voir [Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` en exporte un :
le champ de hauteurs du terrain, chaque maillage que placent les groupes de modèles statiques
du niveau, les objets placés un par un, où ils se trouvent, et le décor de terrain du niveau
autour de la carte. Avec `--textures`, chaque surface porte sa carte de couleur ; avec
`--navmesh`, les surfaces sur lesquelles marchent les soldats viennent aussi. La façon dont
il est lu est décrite dans [Frostbite](reader-frostbite.md).

| Option | Défaut | Signification |
|---|---|---|
| `<level>` | obligatoire | un nom tel que `levels` l'affiche, une partie unique de celui-ci, ou le chemin du `.toc` d'un niveau |
| `-o`, `--out FICHIER` | `<level>.glb` | le `.glb` à écrire |
| `--install DOSSIER` | le premier jeu Steam dont `Data` contient un `layout.toc` | le dossier du jeu |
| `--textures [PIXELS]` | désactivé ; 512 si donné sans taille | écrit la carte de couleur de chaque surface, le plus grand mip qui ne dépasse pas PIXELS de côté, et ses coordonnées de texture telles que le jeu les a, avec un échantillonneur qui répète (voir [Format de sortie](output-format.md)). Le champ de hauteurs reçoit la carte de couleur du décor de terrain là où cette carte le couvre, sinon la couleur moyenne des matériaux de surface du terrain, sinon la couleur moyenne du décor autour. Désactivé, chaque partie est d'une couleur unie |
| `--ground-texture [METRES]` | désactivé ; 0,5 si donné sans taille | cuit les décalcomanies de terrain — routes, pistes, aires, marquages peints — par-dessus la couleur du sol, multipliées par la carte de couleur du terrain là où le niveau en a une, dans la couleur du champ de hauteurs, METRES par pixel, par tuiles d'au plus 4 096 pixels (`ground:terrain x<x> z<z>`). Fonctionne avec ou sans `--textures` |
| `--navmesh` | désactivé | ajoute le maillage de navigation du niveau pour son plus petit agent, le soldat (1,8 m de haut, 0,4 m de large), sous la partie `nav:walkable` : le sol, les planchers, les escaliers et les toits qu'un soldat peut atteindre, sans les liens (sauts, échelles, franchissements) entre eux |
| `--ground-spacing METRES` | 4 | l'espacement le plus fin du champ de hauteurs ; les nœuds plus fins sont échantillonnés plus grossièrement. 0 supprime le champ de hauteurs |
| `--detail-budget N` | chaque copie à son niveau le plus grossier, plus un quart, au moins 1 500 000 | un plafond de triangles. Les maillages qui coûtent le plus perdent un niveau de détail à la fois jusqu'à ce que cela tienne ; si même les niveaux les plus grossiers ne suffisent pas, les plus petites copies sont retirées en premier. Le décor de terrain n'est jamais simplifié ni retiré |
| `--skip TEXTE` | | retire les groupes de modèles statiques dont le nom de partition contient TEXTE ; à répéter pour plusieurs. Par exemple, la couche d'un mode de jeu |
| `--by-mesh` | désactivé | pour trouver ce qu'est une partie : une partie par maillage source et matériau, nommée `<partie> \| <maillage> \| <matériau>` ; un fichier bien plus gros |
| `--clamped-uvs` | désactivé | pour un moteur de rendu qui ne peut pas répéter une texture : découpe chaque triangle texturé en morceaux dont les coordonnées restent entre 0 et 1, et dessine un triangle qui en demanderait plus de 4 morceaux dans la couleur moyenne de sa texture, dans une partie `<partie> (average colour)` |

La commande affiche les groupes et le nombre de copies placées pour chacun, les maillages
laissés de côté et pourquoi, les triangles par partie (et avec `--textures`, le nombre de
textures, et combien de sections ont trouvé leur carte de couleur), ce qu'est le sol, et
avec `--navmesh` le nombre de tuiles de navigation lues. Rien d'autre sur le niveau n'est
écrit que la géométrie : ni noms, ni métadonnées (voir [Format de sortie](output-format.md)).

Le budget du terrain est séparé : le champ de hauteurs et le décor ne sont jamais simplifiés
par `--detail-budget` ; `--ground-spacing` règle la taille du champ de hauteurs.

Un niveau complet est grand : généralement plus de dix millions de triangles et plusieurs
centaines de Mo. `--textures` ajoute un peu au fichier ; un niveau couvert d'arbres peut
atteindre environ 1 Go. `--textures 256 --detail-budget 3000000 --ground-spacing 8` ramène un
niveau à environ un tiers de cela.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps et ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FICHIER] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` est le dossier du jeu, son `Content/Paks`, ou le nom de son dossier dans une
bibliothèque Steam (`"<Steam game folder name>"`). `ue-maps` liste chaque carte qui a des
cellules World Partition compilées à côté. `ue-map` en exporte une sous la forme
`ground:<map>` (le paysage), `structure:<map>` (les maillages HLOD fusionnés de la carte) et
`water:<map>` (ses plans d'eau là où ils sont au-dessus du sol), en **centimètres** Unreal,
avec Y et Z échangés : le seul export qui n'est pas en mètres. Comment chacun est lu et
vérifié : [Cartes Unreal 5](level-unreal-world-partition.md).

| Option | Défaut | Signification |
|---|---|---|
| `<map>` | obligatoire | un nom tel que `ue-maps` l'affiche, ou une partie unique de celui-ci |
| `-o`, `--out FICHIER` | `<map>.glb` | le `.glb` à écrire |
| `--ground-spacing METRES` | 2 | l'espacement des sommets du paysage dans le fichier, arrondi à un nombre entier de ses propres quads |
| `--no-structures`, `--no-water` | | laisse cette partie de côté |

La commande affiche les triangles par partie, le nombre de composants de paysage lus, et
combien de leurs sommets stockés deux fois ne concordent pas. Une carte de 3 km à 2 m fait
environ 4,6 millions de triangles de sol.

## enfusion-worlds et enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install DOSSIER]
python -m heat3d_gamefiles enfusion-world <world> [-o FICHIER] [--install DOSSIER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` liste chaque monde qui a un terrain, par son dossier sous `worlds/`.
`enfusion-world` en exporte un : `ground:<world>` (le terrain, dans les couleurs de ses
tuiles de supertexture), `water:<world>` (la mer, à hauteur zéro) et `structure:<world>` (la
boîte de chaque modèle placé), dans les mètres du jeu : x vers l'est, y vers le haut, z vers
le nord. Comment chacun est lu et vérifié : [Mondes Arma Reforger](level-arma-reforger.md).

| Option | Défaut | Signification |
|---|---|---|
| `<world>` | obligatoire | un monde tel que `enfusion-worlds` l'affiche |
| `-o`, `--out FICHIER` | `<world>.glb` | le `.glb` à écrire |
| `--install DOSSIER` | la bibliothèque Steam qui contient le jeu | le dossier du jeu |
| `--ground-spacing METRES` | 2 (celui du terrain) | l'espacement des sommets du terrain dans le fichier |
| `--texture-size PIXELS` | 4096 | le plus grand côté de l'image de couleur du sol ; 0 pour une couleur unie |
| `--no-structures` | | laisse de côté les modèles placés |
| `--trees` | désactivé | place aussi les arbres et la végétation, en boîtes |

La commande affiche les triangles par partie, le nombre de sommets de bord de tuile qui ne
concordent pas, combien d'entités contient le fichier du monde et combien de boîtes ont été
placées, ainsi que ce qui a été laissé de côté et pourquoi.

## Variables d'environnement {#environment-variables}

| Variable | Effet |
|---|---|
| `HEAT3D_OODLE` | chemin d'un `oo2core_*_win64.dll`, ou d'un dossier qui en contient un ; voir [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | toute valeur autre que vide, `0`, `false`, `no` désactive la vérification de mise à jour ; voir [Mises à jour](updates.md) |
| `LOCALAPPDATA` | l'endroit où sont cherchés la bibliothèque FH Companion, le dossier utilisateur de BeamNG et le cache des mises à jour |
| `HEAT3D_COURSE` | tests seulement : le parcours utilisé par le test de bordure du jeu installé ; voir [Développement](development.md) |
