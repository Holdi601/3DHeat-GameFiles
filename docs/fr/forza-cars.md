---
title: "Voitures Forza"
nav_order: 6
lang: "fr"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Voitures Forza : `cars` {#forza-cars-cars}

Écrit chaque voiture d'un Forza installé, au niveau de détail bas du jeu, dans un seul fichier pour l'onglet Analyse de course de la visionneuse (elle dessine une voiture pour chaque tour que vous avez roulé). Chaque voiture enregistrée est donc dessinée dans sa propre forme, à sa taille réelle.

![cars --help](../assets/img/cars-help.svg)

## Étape par étape {#step-by-step}

1. **Lancez-la** avec le jeu installé (il est trouvé dans les bibliothèques Steam et dans `C:\XboxGames`) :

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Ou indiquez le dossier du jeu :

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Chargez le fichier dans la visionneuse** : **Charger le fichier de voitures…** dans les réglages d'affichage, ou déposez le fichier sur l'onglet Analyse de course ; il reste dans ce navigateur. Les tours dont le numéro de voiture figure dans le fichier sont alors dessinés avec cette voiture exacte (voir la documentation de la visionneuse sur le [rejeu de course](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Relancez-la** quand le jeu ajoute de nouvelles voitures. Cela prend quelques secondes et écrit environ 5 Mo.

## Options {#options}

| Option | Par défaut | Signification |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | le fichier à écrire |
| `--game FOLDER` | le jeu installé trouvé | le dossier du jeu |

## Ce qu'il y a dans le fichier {#what-is-in-the-file}

Pour chaque archive de voiture sous `media/Cars` : le modèle `ProxyLOD` qu'elle contient (environ 900 triangles), le numéro de la voiture tel que la télémétrie l'indique, sa marque, son étiquette de modèle et son année d'après le nom de l'archive, ainsi que ses roues et ses feux arrière. Les formes sont en mètres, à l'échelle 1:1 avec la voiture. Une archive sans un tel modèle (un accessoire de circulation) est nommée et laissée de côté.

Le fichier est conçu pour la visionneuse 3DHeat. Voici sa structure, pour quiconque le lit ailleurs ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)) :

| Partie | Structure |
|---|---|
| fichier entier | compressé en gzip |
| signature | les 8 octets `H3DCARS1` |
| longueur de l'en-tête | u32 en little-endian |
| en-tête | JSON UTF-8 : `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| remplissage | espaces jusqu'à un multiple de 4 octets |
| données | par voiture : sommets, trois i16 chacun (millimètres ; x à droite, y en haut, z en avant), puis triangles, trois u16 chacun |

Chaque entrée `cars` contient : `key`, `ordinals` (les numéros de la voiture tels que la télémétrie les indique), `make`, `model`, `year`, `height` et `length` (m), `wheels` (pour chaque roue `[x, y, z, radius]`, m), `lights` (points des feux arrière `[x, y, z]`, m), et `vertexAt`, `vertices`, `faceAt`, `faces` (décalages en octets depuis le début des données, et nombres).

Le fichier contient des éléments du jeu : il est destiné à la machine sur laquelle il a été fait, pas à être diffusé ([Règles et licences](rules-and-licences.md)).
