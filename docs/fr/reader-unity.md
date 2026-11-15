---
title: "Unity"
nav_order: 4
lang: "fr"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity : `SerializedFile`, bundles, maillages {#unity-serializedfile-bundles-meshes}

**Liste les objets et décode les maillages** des `SerializedFile` Unity de format 22 et plus (Unity 2020
à 6000), et ouvre les bundles `UnityFS`. Il n'y a pas d'export de parcours Unity.

Sources : [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Commandes : `identify` (conteneurs et bundles), `meshes` (conteneurs nus seulement).

## Le conteneur {#the-container}

Unity livre un niveau sous forme de graphes d'objets sérialisés : `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*`, et des bundles d'assets. Chacun contient une table
d'objets étiquetés par un identifiant de classe.

L'en-tête est l'endroit où la lecture se trompe discrètement. Les seize premiers octets sont quatre `uint32`
en big-endian, conservés pour la compatibilité. Au format 22, trois d'entre eux valent zéro, et les vraies
valeurs suivent parce qu'un fichier peut dépasser 4 Go :

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

La seconde `metadata size` est un `uint32` pris entre deux `int64`. Si l'on suppose que les trois sont sur
64 bits, la chaîne de version se retrouve quatre octets trop loin. Elle se décode quand même en quelque chose
qui ressemble à une chaîne, et envoie tout ce qui suit de travers. L'en-tête est en big-endian. Tout le reste
suit l'octet d'ordre (0, little-endian, sur toutes les versions de bureau).

Après l'en-tête : la chaîne de version du moteur, la plateforme, l'indicateur d'arbre de types, la table des
types (identifiant de classe par type), la table des objets (identifiant de chemin, décalage, taille, type), et
les externes (autres fichiers vers lesquels un pointeur peut renvoyer).

| Cas | Résultat |
|---|---|
| format 22-30 | lu |
| format 9-21 (avant Unity 2020) | refusé : les décalages sont dans l'en-tête hérité, et aucun fichier disponible ne l'utilisait |
| hors de 9-30 | refusé |
| arbre de types intégré (builds éditeur) | refusé : les builds livrés n'en intègrent pas, et le chemin éditeur n'est pas implémenté |
| un bundle passé là où un conteneur est attendu | refusé, avec un renvoi vers le lecteur de bundles |

Il n'y a **pas de désérialiseur général**. Les builds livrés ne portent pas d'arbre de types, parce que le schéma
est compilé dans le lecteur ; chaque classe doit donc être analysée selon une disposition connue pour sa
version. Seul `Mesh` est décodé. Les autres classes sont signalées par leur nom et leur nombre (`GameObject`,
`Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance` ; les autres en `class<id>`).

**Vérifié** sur de nombreux jeux installés et des millions d'objets : la table des objets doit recouvrir
exactement la section de données, sans chevauchement, sans rien d'autre que du bourrage d'alignement entre les
objets, et le dernier objet doit finir sur le dernier octet du fichier. Une lecture fausse de l'en-tête ne peut
pas produire cela. Le test sur jeu installé le répète sur jusqu'à six fichiers `resources.assets` /
`sharedassets0.assets` trouvés dans les dossiers `*_Data`.

## Bundles (`UnityFS`) {#bundles-unityfs}

Un bundle est un conteneur compressé de `SerializedFile`. La liste des blocs et le répertoire sont aussi
compressés. La méthode est dans les six bits faibles d'un mot de drapeaux : 0 stocké, 1 LZMA (en-tête Unity de 5
octets avec la taille insérée), 2 et 3 LZ4 / LZ4HC. À partir du format 7, l'en-tête est aligné sur 16 octets.
Le drapeau `0x80` place le répertoire à la fin du fichier. `UnityWeb`, `UnityRaw` et `UnityArchive` (avant 5.3)
sont reconnus mais non lus.

## Maillages {#meshes}

`read_mesh` décode un objet `Mesh` en positions, normales, premier jeu d'UV et triangles, dans l'ordre où
Unity 2019+ les écrit : nom, sous-maillages, formes de fusion (ignorées), poses de liaison et données d'os
(ignorées), les drapeaux de compression et de lisibilité, le tampon d'index, les canaux de sommets et les données
de sommets, le bloc de maillage compressé, la boîte englobante locale, et les infos de streaming.

- **Sommets externes.** La plupart de la géométrie livrée vit dans un fichier `.resS` à côté du conteneur. L'outil
  le lit depuis le dossier du conteneur (seul le nom de fichier du chemin `archive:/...` stocké est utilisé). Un
  `.resS` manquant est une erreur, non un maillage vide.
- **Flux et canaux.** Les canaux indiquent quel flux, décalage, format et dimension a chaque attribut. Les flux sont
  empilés les uns après les autres, chacun complété à 16 octets, donc le début d'un flux se calcule en accumulant les
  pas qui le précèdent. Formats : float32, float16, unorm/snorm 8 et 16 (normalisés), et entiers simples.
- **Topologie.** Seulement les triangles (topologie 0). Les bandes, quads et lignes sont refusés, parce qu'une
  mauvaise conversion ressemble à une vraie géométrie.
- **Maillages compressés** (deltas quantifiés) refusés : « mesh '...' is stored compressed; that encoding is not
  implemented ».

### L'autocontrôle {#the-self-check}

Lire une structure dans le mauvais ordre ne lève aucune erreur. Cela donne des nombres plausibles. Donc chaque
maillage décodé est contrôlé contre la **boîte englobante qu'Unity a stockée pour lui**, calculée par l'éditeur à
partir des vrais sommets. `aabb_matches()` réussit quand les coins de la boîte décodée sont à 2 % près de la taille
de la boîte stockée. `meshes` affiche `ok` ou `BOUNDS DISAGREE` sur chaque ligne.

**Vérifié :** des maillages échantillonnés dans plusieurs jeux se décodent avec des boîtes concordantes. Le test sur
jeu installé répète le contrôle sur les conteneurs installés.

## Non implémenté {#not-implemented}

- Formats antérieurs à 2020.
- Maillages compressés.
- Toute classe autre que `Mesh` : pas de graphe de scène, de transformations ni de matériaux, donc les maillages sont
  dans leur propre espace local.
- `meshes` sur un bundle. Le lecteur de bundles existe en Python (`UnityBundle.serialized_files()`), mais la commande
  prend un conteneur nu.
