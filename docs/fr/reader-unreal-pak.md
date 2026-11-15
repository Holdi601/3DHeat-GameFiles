---
title: "Unreal .pak"
nav_order: 1
lang: fr
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Liste et extrait** les archives `.pak` d'Unreal 4.22 à 5.x : versions 8, 9, 10, 11 et 12, compression Zlib,
Gzip et Oodle, et archives chiffrées quand vous fournissez la clé AES. Il n'interprète pas ce qu'il extrait
(`.uasset`, `.umap`).

Source : [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Commandes : `identify`, `list`, `extract` (voir [Commandes](commands.md)).

## Disposition {#layout}

Le pied de page est à la fin du fichier et se trouve en cherchant dans les 1 024 derniers octets le magic
`0x5A6F12E1`. L'ordre de ses champs compte :

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

L'indicateur de chiffrement se trouve **avant** le magic. Le lire après le magic tombe sur le « Z » de « Zlib ».
Alors chaque archive se déclare chiffrée, et chaque nom de méthode perd sa première lettre (« lib », « odle »), une
panne discrète mais plausible. La version est l'octet faible, car les builds « à index figé » mettent un bit de tête.

L'index contient le point de montage, l'index des hash de chemins, l'index complet des répertoires, et un bloc
d'**entrées codées** : une forme compactée où un mot de drapeaux indique quels nombres sont sur 32 bits, la méthode de
compression (6 bits), si l'entrée est chiffrée, le nombre de blocs (16 bits) et la taille de bloc en unités de 2 048
(6 bits). La taille de bloc tout à 1 est un échappement : la vraie taille suit en u32 **avant** le décalage. Dans une
grande archive, la lire après les tailles a décalé 7 % des entrées de quatre octets, et leur a donné des décalages dans
les exaoctets.

L'enregistrement complet de chaque entrée est répété juste avant sa charge utile, donc la charge commence après
`8+8+8+20+4+1+4` octets, plus `4 + 16 x blocks` quand elle est compressée. Les blocs chiffrés sont complétés à 16 octets.

## Ce qui est lu, et ce qui est refusé {#what-it-reads-and-what-it-refuses}

| Cas | Résultat |
|---|---|
| versions 8-12 | lues |
| toute autre version | `pak version N; this reader handles 8-12` (les anciennes versions stockent une liste plate d'enregistrements, et aucun fichier de test n'était disponible) |
| pas de magic de pied de page | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| index hors du fichier | refusé : le pied de page n'a pas été lu comme annoncé |
| index des seuls hash de chemins | refusé : les noms de fichiers ont été hachés à la compilation et ne peuvent pas être retrouvés |
| entrées dans la liste de débordement de l'index (décalage de répertoire -1) | sautées, non fabriquées |
| index chiffré, sans clé | `EncryptedPak` : « Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys. » En ligne de commande : une ligne et le code de sortie 1 |
| entrée chiffrée, sans clé | `EncryptedPak` à la lecture |
| méthodes Zlib, Gzip, Oodle | décompressées (Oodle a besoin d'une bibliothèque, voir [Oodle](reader-oodle.md)) |
| toute autre méthode | `compression method '...' is not supported` |

## Clés {#keys}

`--key` sur `list` et `extract` prend une clé AES-256 que vous détenez déjà, en 64 chiffres hexadécimaux, avec ou
sans `0x`. Toute autre valeur est refusée avant l'ouverture de l'archive, avec le code de sortie 2. Le déchiffrement
est AES-256-ECB par le paquet `cryptography`. Aucun chemin de code n'obtient de clé : pas de clés intégrées, pas de
recherche dans les exécutables, pas de lecture de mémoire. Voir [Règles et licences](rules-and-licences.md).

## Vérifié {#verified}

Sur des archives livrées de plusieurs jeux, chaque entrée, y compris une très grande archive, correspond au SHA-1
qu'Unreal écrit avant chaque charge utile. Ce hash couvre les octets tels que stockés, donc une correspondance signifie
que le décodage de l'index, le décalage de la charge utile et chaque frontière de bloc compressé étaient justes. Les
tests sur jeux installés (`test_pak.py`) répètent cela sur jusqu'à quatre pak non chiffrés trouvés sous
`steamapps\common\*\...\Content\Paks`. Ils vérifient que le décalage de chaque entrée tombe dans le fichier, et que le
SHA-1 correspond pour un échantillon aléatoire de 150 entrées par archive.
