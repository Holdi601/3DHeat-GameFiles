---
title: "Commandes"
nav_order: 2
lang: "fr"
source: commands.md
source_hash: "8ae04c37b1a4"
nav_exclude: true
search_exclude: true
---
# Commandes {#commands}

Chaque commande s'exécute avec `python -m heat3d_gamefiles <verbe> ...` depuis le
dossier du dépôt. Les verbes sont dans l'ordre où on en a généralement besoin : quel
est ce fichier, qu'est-ce qu'il contient, donnez-moi cet élément, et transforme un tour
en parcours.

| Verbe | Prend | Fait |
|---|---|---|
| [`identify`](#identify) | n'importe quel fichier | donne le format du conteneur en lisant ses octets |
| [`list`](#list) | un `.pak` Unreal ou un `.utoc` IoStore, un `.vpk` Source 2, ou un zip (un `.minizip` ForzaTech par l'outil Forza) | liste ses entrées |
| [`extract`](#extract) | la même chose | écrit une entrée sur le disque |
| [`meshes`](#meshes) | un `SerializedFile` Unity | liste et vérifie ses maillages |
| [`course`](#course) | un tour | exporte le parcours autour de lui (Forza, BeamNG.drive, Assetto Corsa Rally) (lancé par l'outil Forza, BeamNG.drive ou AC Rally) |
| [`courses`](#courses) | une bibliothèque de tours enregistrés | lance `course` sur chaque parcours qu'elle contient (Forza) (lancé par l'outil Forza) |
| [`races`](#courses) | un Forza installé | liste chaque course que le jeu définit : ce qu'elle ajoute, ce qu'elle cache, les lieux, l'état de son export (lancé par l'outil Forza) |
| [`terrain`](#courses) | un dossier de piste Forza | découpe une zone selon des coordonnées du monde (lancé par l'outil Forza) |
| [`levels`](#levels-and-level-frostbite) | un jeu Frostbite installé (Battlefield 6) | liste ses niveaux (lancé par l'outil Battlefield) |
| [`level`](#levels-and-level-frostbite) | le nom d'un niveau | exporte le niveau : terrain, maillages placés, et éventuellement leurs cartes de couleur (Battlefield 6) (lancé par l'outil Battlefield) |
| [`cars`](#courses) | un Forza installé | chaque voiture en faible détail, dans un seul fichier pour l'onglet Analyse de course du visualiseur (lancé par l'outil Forza) |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | un jeu Unreal 5 | liste ses cartes World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | le nom d'une carte | exporte la carte : paysage, structures HLOD, eau |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | un Arma Reforger installé | liste ses mondes (lancé par l'outil Reforger) |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | le nom d'un monde | exporte le monde : terrain dans ses couleurs, la mer, les bâtiments en boîtes (lancé par l'outil Reforger) |

**Lire les exemples :** `<x>` signifie qu'il faut remplacer par votre propre valeur, sans
les chevrons ; `[...]` indique une option ; entourez un chemin contenant des espaces de
"guillemets doubles", par exemple `"C:\Games\My Game"`. Vous débutez ? Voir
[Avant de commencer](before-you-start.md). L'aide complète (`--help`) de chaque verbe
se trouve dans la [Référence des commandes](../cli-reference.md).

À chaque démarrage, le programme peut d'abord chercher une version plus récente. Voir
[Mises à jour](updates.md). `HEAT3D_NO_UPDATE=1` désactive cette vérification.

Source : [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Pages pas à pas : [Inspecter les archives](inspecting-archives.md), [Export de circuit](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html),
[Niveaux entiers](whole-levels.md), [Voitures Forza](https://holdi601.github.io/3DHeat-Ext-Forza/forza-cars.html).

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

## Les verbes propres aux jeux {#the-games-own-verbs}

Chaque lecteur de jeu est un petit projet à part, avec son propre fichier de licence, ses
versions et son suivi des tickets : il peut être installé, mis à jour, maintenu - ou retiré à
la demande d'un ayant droit - séparément, sans toucher au visualiseur ni aux autres outils.
Installez celui de votre jeu (sa page indique comment), et sa propre commande comme les verbes
d'ici fonctionnent. GameFiles lance l'outil du jeu avec les arguments que vous avez donnés ;
rien de cet outil n'est importé. Il est trouvé comme sa commande dans `PATH`, comme son paquet
installé, ou comme son dossier dans `HEAT3D_<GAME>_MAPS` ou à côté de GameFiles
(`exporters/ext/<game>-maps` dans une copie de 3DHeat, ou `3DHeat-Ext-<Game>` à côté de ce
dossier). Quand il n'est pas installé, le verbe indique où le trouver et se termine avec le
code 2.

| Jeu | Son propre outil | Verbes d'ici qui le lancent |
|---|---|---|
| Forza Horizon / Motorsport | [3DHeat-Ext-Forza](https://holdi601.github.io/3DHeat-Ext-Forza/) (`heat3d-forza-maps`) | `course` (tours Forza), `courses`, `races`, `cars`, `terrain` ; `identify`, `list`, `extract` d'un `.minizip` |
| Battlefield (Frostbite) | [3DHeat-Ext-Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/) (`heat3d-battlefield-maps`) | `levels`, `level` ; `identify` d'un `.toc` Frostbite |
| BeamNG.drive | [3DHeat-Ext-BeamNG](https://holdi601.github.io/3DHeat-Ext-BeamNG/) (`heat3d-beamng-maps`) | `course` (tours BeamNG) ; `identify` d'un `.cdae` ou `.ter` |
| Assetto Corsa Rally | [3DHeat-Ext-ACRally](https://holdi601.github.io/3DHeat-Ext-ACRally/) (`heat3d-acrally-maps`) | `course` (tours AC Rally) |
| Arma Reforger (Enfusion) | [3DHeat-Ext-Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/) (`heat3d-reforger-maps`) | `enfusion-worlds`, `enfusion-world` |

`python -m heat3d_gamefiles <verbe> --help` affiche les options propres à l'outil du jeu.

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Le parcours autour d'un tour (le sol dans une bande de chaque côté de la conduite, et ce qui
s'y dresse, en un seul `.glb`) est produit par l'outil propre au jeu du tour, lancé avec les
mêmes arguments : [Forza](https://holdi601.github.io/3DHeat-Ext-Forza/course-forza-horizon.html),
[BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html),
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html).
Ce qu'un tour peut être : [Entrées de tour](lap-inputs.md) ; combien de détail est gardé :
[Niveaux de détail et budget](detail-budget.md).

### Quel jeu {#which-game}

Le jeu est pris dans `--game`, puis dans le champ `game` d'un fichier `heat3d-lap` (ou de
la ligne de description `# {...}` d'un CSV), et par défaut c'est Forza. Un dossier prend le
jeu que nomment ses fichiers, s'il n'en nomme qu'un seul ; un fichier qui n'en nomme aucun
(un tour FH Companion, `course.json`, un CSV sans ligne de description) ne compte pas (voir
[Entrées de tour](lap-inputs.md)).

| Valeur | Lancé par |
|---|---|
| commence par `forza` | `heat3d-forza-maps course` |
| `beamng` | `heat3d-beamng-maps course` |
| `assetto-corsa-rally` ou `acrally` | `heat3d-acrally-maps course` |
| `assetto-corsa-evo` | refusé : "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | refusé : "tracks ship in a protected format that is not a file-extraction target" |
| tout le reste | refusé : "there is no course reader for <game> yet" |

Un refus indique aussi les solutions de rechange : reconstruire le parcours à partir du jeu
(3DHeat GameCapture), ou analyser les tours sans parcours, car l'onglet Analyse de course
du visualiseur dessine une route à partir d'eux.

## courses, races, cars, terrain (Forza) {#courses}

Lancé par `heat3d-forza-maps` avec les mêmes arguments :
[ses commandes](https://holdi601.github.io/3DHeat-Ext-Forza/commands.html).

## levels et level (Frostbite) {#levels-and-level-frostbite}

Lancé par `heat3d-battlefield-maps` avec les mêmes arguments :
[Niveaux de Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/level-battlefield.html).

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
| `-o`, `--out FICHIER` | `<map>.glb` (dans `$HEAT3D_LEVELS/<game>/` quand cette variable est définie) | le `.glb` à écrire |
| `--ground-spacing METRES` | 2 | l'espacement des sommets du paysage dans le fichier, arrondi à un nombre entier de ses propres quads |
| `--no-structures`, `--no-water` | | laisse cette partie de côté |

La commande affiche les triangles par partie, le nombre de composants de paysage lus, et
combien de leurs sommets stockés deux fois ne concordent pas. Une carte de 3 km à 2 m fait
environ 4,6 millions de triangles de sol.

## enfusion-worlds et enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

Lancé par `heat3d-reforger-maps` avec les mêmes arguments (ses `worlds` et `world`) :
[Mondes d'Arma Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/level-arma-reforger.html).

## Variables d'environnement {#environment-variables}

| Variable | Effet |
|---|---|
| `HEAT3D_OODLE` | chemin d'un `oo2core_*_win64.dll`, ou d'un dossier qui en contient un ; voir [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | un seul dossier pour chaque export fait sans `-o` : ceux de chaque jeu vont dans `<HEAT3D_LEVELS>/<jeu>/` (les parcours dans `<jeu>/courses/`, le lot de voitures dans `forza/`). Sans valeur, ils vont dans le dossier courant |
| `HEAT3D_FORZA_MAPS`, `HEAT3D_BATTLEFIELD_MAPS`, `HEAT3D_BEAMNG_MAPS`, `HEAT3D_ACRALLY_MAPS`, `HEAT3D_REFORGER_MAPS` | le dossier d'un outil de jeu, quand il n'est ni installé ni à côté de GameFiles |
| `HEAT3D_NO_UPDATE` | toute valeur autre que vide, `0`, `false`, `no` désactive la vérification de mise à jour ; voir [Mises à jour](updates.md) |
| `LOCALAPPDATA` | l'endroit où sont cherchés la bibliothèque FH Companion, le dossier utilisateur de BeamNG et le cache des mises à jour |
| `HEAT3D_COURSE` | tests seulement : le parcours utilisé par le test de bordure du jeu installé ; voir [Développement](development.md) |
