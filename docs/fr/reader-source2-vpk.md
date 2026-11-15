---
title: "Source 2 VPK"
nav_order: 6
lang: fr
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Liste et extrait** les archives VPK de Valve, versions 1 et 2, y compris les archives découpées et les données stockées dans le fichier de répertoire. Chaque entrée peut être vérifiée par son propre CRC. C'est le seul format de conteneur ici dont l'éditeur publie la documentation. Jeux : Counter-Strike 2, Dota 2, Half-Life: Alyx, et d'autres sur Source 2.

Source : [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Commandes : `identify`, `list`, `extract`.

## Structure {#layout}

```
u32 magic 0x55AA1234, u32 version (1 ou 2), u32 tree size
  (version 2 : 16 octets d'en-tête de plus ; en-tête de 12 ou 28 octets)
directory tree:
  extension        "vmdl_c", puis "vtex_c", ..., puis ""
    path           "maps/example_map", puis ""
      file name    "world_layer0", puis ""
        u32 crc, u16 preload size, u16 archive index, u32 offset, u32 length, u16 0xFFFF
        [octets préchargés]
```

- Trois boucles imbriquées, chacune se terminant par une chaîne vide : un lecteur qui attend un compte n'en trouve aucun. Les chemins sont stockés une fois par groupe et reconstitués à partir des trois parties. Un simple espace signifie « pas de dossier » ou « pas d'extension ».
- Chaque enregistrement se termine par `0xFFFF`. Cela est vérifié : un lecteur qui a perdu sa position s'arrête aussitôt (« the directory is not being read at the right offset »).
- **Archives découpées :** `pak01_dir.vpk` contient le répertoire, et les données se trouvent dans `pak01_000.vpk`, `pak01_001.vpk`... choisies par l'index d'archive de l'entrée.
- **L'index d'archive `0x7FFF`** signifie que les octets se trouvent dans le fichier de répertoire lui-même, après l'arborescence. Le lire comme un vrai index enverrait un lecteur chercher `pak01_32767.vpk`.
- **Préchargement :** les petits fichiers sont stockés entiers dans le répertoire. Une longueur de 0 n'est alors pas une erreur.

## Commandes {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` affiche la version, le nombre d'entrées et le premier fichier `.nav`. `list` affiche chaque entrée comme `stored`, car VPK ne compresse pas. `extract` écrit les octets sans vérifier le CRC. En Python, `VpkArchive(path).verify(name)` compare les octets d'une entrée avec le CRC noté dans le répertoire.

## Le maillage de navigation {#the-navigation-mesh}

Une carte livre son **maillage de navigation** (`maps/<map>.nav`) à côté de la géométrie compilée. Pour une carte de chaleur des positions des joueurs, c'est le plus utile des deux, et de loin, car le maillage de navigation *est* le sol praticable, déjà calculé, et mille fois plus petit. Le test sur jeu installé vérifie que le `.nav` d'une carte livrée commence par la signature de navigation Source `CE FA ED FE`.

## Vérifié {#verified}

Chaque entrée échantillonnée dans les archives de cartes livrées d'un jeu est revenue identique octet pour octet à son CRC, et toutes les archives de cartes s'analysent correctement. Les tests sur jeu installé répètent la vérification CRC sur 25 entrées tirées au hasard dans chacune des quatre archives de cartes au maximum.

## Non implémenté {#not-implemented}

- Le décodage des ressources compilées de Source 2 (`.vmdl_c`, `.vtex_c`). Ce sont des binaires découpés en blocs qui leur sont propres, le même type de travail que les formats de maillages Unreal et Frostbite. L'outil 3DHeat CS2 séparé gère la géométrie des cartes CS2.
- Le décodage du maillage de navigation de CS2. Son format est la version 36 et diffère de celui, largement documenté, de Source 1. Ses octets sont structurés plutôt que compressés (entropie 6,2, 31 % de zéros), mais seuls 3 % de ses mots se lisent comme des coordonnées : la structure n'est donc pas la structure évidente et n'a pas encore été élucidée.
