---
title: "Entrées de tour"
nav_order: 7
lang: "fr"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Entrées de tour {#lap-inputs}

Un **fichier de tour** est une liste de points x, y, z : là où votre voiture est passée.
Le plus rapide à faire à la main est le CSV décrit dans [5. Un tableau `.csv`](#5-a-csv-table)
plus bas.

Un tour indique à l'export de parcours **où la voiture est passée**. Rien d'autre n'y est
utilisé : la vitesse, les commandes et les forces G appartiennent au côté télémétrie de
3DHeat. L'outil lit les positions dans les mètres du monde propres au jeu, plus, quand le
fichier le dit, le jeu et la piste.

Source : [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Ce que `course` accepte {#what-course-accepts}

Le format est reconnu d'après le contenu du fichier, et non son nom, sauf que `.npz` et `.csv`
se reconnaissent à leur extension et que tout le reste est essayé comme du JSON.

### 1. Un document `heat3d-lap` (tous les jeux) {#1-a-heat3d-lap-document-any-game}

Écrit par les enregistreurs de télémétrie 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))) :

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y` et `channels.z` sont obligatoires. Les lignes où l'un des trois
  n'est pas un nombre fini sont supprimées. Les autres canaux sont ignorés.
- `game` détermine l'export (voir [Commandes](commands.md#which-game)).
- `track` sert à Assetto Corsa Rally pour essayer l'étape nommée en premier.
- Axes : y est la hauteur. Les tours de Forza et d'AC Rally utilisent les axes horizontaux du
  jeu tels que l'enregistreur les écrit. Les tours de BeamNG sont attendus dans le repère de la
  visionneuse, `(x, z, -y)` du monde de BeamNG en Z vers le haut (voir
  [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Un fichier de parcours (route) {#2-a-route-file}

Écrit par `heat3d_capture route` et `heat3d_capture laps` :

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` est une liste de `[x, y, z]`. Un fichier de parcours avec `bounds` mais sans
positions fonctionne quand même : ses deux coins forment une ligne dégénérée, mais une boîte
utilisable.

### 3. Un fichier de tour FH Companion {#3-an-fh-companion-lap-file}

Les fichiers de tour individuels de la bibliothèque enregistrée de FH Companion :

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Un `X`, `Y` ou `Z` absent se lit comme 0. Les fichiers sont écrits avec une marque d'ordre
d'octets, donc tout le JSON est lu en `utf-8-sig`.

### 4. Un enregistrement `.npz` {#4-an-npz-recording}

Une archive NumPy contenant un tableau `positions` de forme (n, 3).

### 5. Un tableau `.csv` {#5-a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Les colonnes nommées `x`, `y`, `z` (sans tenir compte de la casse ni des espaces autour)
  sont obligatoires. Les autres colonnes sont ignorées.
- Les lignes qui commencent par `#` sont sautées. Si la **première** ligne est `# {json}`, ses
  `game` et `track` sont lus.
- Les lignes qui ne se lisent pas comme des nombres sont sautées.

### 6. Un dossier {#6-a-folder}

Un dossier est fouillé **récursivement** à la recherche de fichiers `.json`, `.npz` et `.csv`,
et tous sont mis bout à bout en une seule ligne conduite. C'est ainsi qu'un parcours
enregistré entier est stocké : FH Companion range les dossiers par classe, voiture, réglage et
étiquette.

- `course.json` est sauté d'après son nom (c'est une métadonnée, pas un tour).
- Un fichier qui ne se lit pas est sauté discrètement. Un fichier défectueux parmi des
  centaines ne fait pas perdre les autres.
- La console indique combien de fichiers de tour ont été pris (`12 laps, 18,400 samples`).
- Le dossier prend le jeu que ses fichiers nomment, s'ils n'en nomment **qu'un seul**. Un
  fichier qui ne nomme aucun jeu (un tour FH Companion, `course.json`, un CSV sans sa ligne de
  description) ne compte pas, donc l'un d'eux parmi les enregistrements d'un jeu ne retire pas
  son jeu au dossier. Des fichiers qui nomment deux jeux différents forment un mélange, et le
  dossier n'en reçoit aucun. Un dossier sans jeu est exporté comme Forza, sauf si `--game`
  indique autre chose.
- Si rien ne se lit : « no readable laps under <folder> ».

### 7. Un nom de parcours {#7-a-course-name}

Si l'argument n'est ni un fichier ni un dossier existant, il est cherché comme nom de parcours
dans la bibliothèque FH Companion, `%LOCALAPPDATA%\FHCompanion\laps` :

1. un dossier dont le nom, sans le suffixe ` (course_...)`, est égal au nom (sans tenir compte
   de la casse) ;
2. sinon, le seul dossier dont le nom contient ce texte.

Ainsi, `"Example Circuit"` trouve `Example Circuit (course_1200_3400_to_1175_3400)` sans que
personne ait à connaître les coordonnées. Plusieurs correspondances forment une erreur qui les
liste. Un parcours trouvé par son nom ne porte pas de jeu, donc il est exporté comme Forza, sauf
si `--game` indique autre chose.

## Ce que `terrain --route` accepte {#what-terrain-route-accepts}

`terrain` a besoin du champ `bounds` du fichier de parcours (forme 2 ci-dessus),
`{"min": [x, y, z], "max": [x, y, z]}`. Sans `bounds`, il s'arrête avec
« <file> has no bounds; --route takes a route file with "bounds": {...} ». Le fichier est lu en
UTF-8, avec ou sans marque d'ordre d'octets, comme tout tour JSON. Si le même fichier a aussi au
moins 10 positions lisibles selon les règles ci-dessus, elles resserrent la découpe sur un
couloir et guident le détail.

## Comment le tour est utilisé {#how-the-lap-is-used}

| Usage | Détail |
|---|---|
| nom | le nom du fichier, ou le nom du dossier sans ` (course_...)` ; il devient le nom par défaut du fichier de sortie |
| distance parcourue | la somme des écarts entre points successifs (affichée `m driven` ; pour un dossier, cela inclut les sauts entre fichiers) |
| boîte | l'étendue en x et z élargie de `--margin` ; la hauteur n'est jamais bornée |
| couloir | les x et z de chaque point, voir [Export de parcours](course-export.md#the-corridor) |
| détail | la distance de chaque copie placée au point le plus proche, voir [Niveaux de détail et budget](detail-budget.md) |

Un tour de moins de deux points est refusé (« holds no driving »).

## Erreurs {#errors}

| Message | Signification |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | le fichier n'est pas du JSON (ni `.npz` ni `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | du JSON d'une autre forme |
| `<file> has no x, y and z columns` | un CSV sans ces en-têtes |
| `<file> has no positions array` | un `.npz` sans `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | un nom, mais pas de bibliothèque FH Companion |
| `'<name>' matches 3 courses: A, B, C` | soyez plus précis |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | seulement pour les recherches par nom et `courses` |
