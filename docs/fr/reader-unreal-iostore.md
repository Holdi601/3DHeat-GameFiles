---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "fr"
source: reader-unreal-iostore.md
source_hash: "a71af3169c83"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 livre la plupart de son contenu dans des conteneurs **IoStore** : une table des matières `.utoc` et
les données `.ucas` qu'elle indexe. Un `.pak` est toujours là, mais il ne contient guère plus qu'un pied de
page. Les lecteurs décrits ici vont du conteneur jusqu'à la géométrie et aux pixels, autant qu'un parcours en
a besoin. Ils ont été construits et vérifiés sur Assetto Corsa Rally (Unreal 5.6.1, modifié), et sont atteints
par l'export de parcours [Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html). `identify`, `list` et `extract`
prennent un `.utoc` (ou le `.ucas` à côté) : les fichiers que son répertoire nomme, par leur chemin sous le
point de montage. Un conteneur sans index de répertoires ne nomme aucun fichier et n'est pas listé.

| Couche | Module |
|---|---|
| conteneurs et magasin | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| paquets « zen » cuits | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| données de propriétés sans version | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| maillages statiques | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| textures et textures virtuelles | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Conteneurs (`.utoc`, `.ucas`) {#containers-utoc-ucas}

La table des matières, version 8 (Unreal 5.6), little-endian :

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Les versions antérieures à 5 sont refusées. Seule la version 8 a été vérifiée sur de vrais fichiers.
- **Les conteneurs chiffrés sont refusés** : « <file> is encrypted. This tool holds no keys and recovers none. »
  Aucune clé ne peut être transmise pour IoStore.
- Méthodes de bloc : stocké, `oodle` (par [Oodle](reader-oodle.md)), `zlib`, `lz4`. Toute autre est refusée.
- Les partitions au-delà de la première vivent dans `<name>_s<n>.ucas`.

Le **magasin** ouvre chaque `.utoc` du dossier `Paks` du jeu et indexe chaque chemin de paquet, sans tenir
compte de la casse. Les conteneurs qui ne s'ouvrent pas sont sautés. `global.utoc` fournit les objets de script
(classes C++). Les données en masse d'un paquet (`.ubulk`) sont trouvées comme le morceau de même identifiant et
de type `BULK_DATA`, dans le conteneur qui le contient.

Vérifié : chaque conteneur du jeu installé et chaque chemin de paquet qu'il contient.

## Paquets zen {#zen-packages}

Un paquet cuit est un en-tête (noms, imports, exports, bundles d'exports, tables de dépendances, noms de paquets
importés) suivi des données sérialisées de chaque export. Les objets se réfèrent les uns aux autres par un
`FPackageObjectIndex` de 64 bits dont les deux bits de tête disent ce qu'il est : un export de ce paquet, un objet
de script, un import d'un autre paquet (quel paquet, et l'export par un hash de son chemin), ou nul.

- La disposition du résumé a changé en 5.3 (bundles de dépendances et noms de paquets importés) puis en 5.6 (deux
  décalages de plus). Les deux dispositions sont essayées, et celle dont la table de noms s'analyse est gardée, donc
  il n'est pas nécessaire de connaître la version.
- Les paquets **versionnés** (de style non cuit) sont refusés.
- Les noms de paquets importés portent un numéro. Un paquet `_Terrain` numéroté 1 est le fichier `_Terrain_0`.
- Les noms `/Game/...` correspondent au dossier `Content` du projet dans le magasin.
- Les références sont suivies entre paquets en faisant correspondre le hash public de l'export.

Vérifié : chaque cellule de chaque étape s'ouvre.

## Propriétés sans version {#unversioned-properties}

Les exports Unreal 5 cuits ne nomment pas leurs propriétés. Un export commence par un en-tête de suites, « sauter
tant d'emplacements, puis tant de présents », et un masque qui indique lesquels des présents valent zéro et n'ont
donc pas d'octets. Les valeurs suivent dans l'ordre des propriétés de la classe. Lire cela demande le **schéma**
de chaque classe : sa liste de propriétés, dans l'ordre exact que construit le moteur (les propriétés propres
d'abord, puis celles du parent, un emplacement par élément de tableau statique, les propriétés réservées à
l'éditeur laissées de côté).

Des schémas sont intégrés pour les classes dont un parcours a besoin :

| Classe | Chaîne |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | les chaînes ISM (présentes, mais non utilisées par l'export de parcours, car cette version les a réarrangées) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Ils couvrent aussi les structures qu'elles contiennent (`FBodyInstance`, réponses de collision et autres). Les
types valeur sont lus par leur codage : nombres et vecteurs de taille fixe (`FVector`, `FRotator` en doubles,
`FTransform`...), `FName`, énumérations (un octet), références d'objets (indice de paquet `i32`), chemins d'objets
souples, tableaux, structures imbriquées, et délégués multicast (sautés).

Les schémas ne contiennent que **les noms et les types des propriétés**, tirés des en-têtes Unreal Engine 5.6.1
(que Epic met à disposition de quiconque a un compte lié). Aucun code du moteur n'est inclus. Cette version a
**deux emplacements de plus dans `UPrimitiveComponent`** que les en-têtes, et **un de plus dans le volume de texture
virtuelle**, trouvés d'après les données et marqués `(unknown)`. Une valeur présente dans l'un de ces emplacements
est une erreur, non une supposition. Un emplacement au-delà de la fin d'un schéma, ou un type inconnu, lève
`PropertyError`.

Vérifié : chaque composant de maillage statique et de scène de chaque étape se décode, en finissant exactement à la
fin native fixe de sa classe. Un correctif du jeu peut déplacer les emplacements. Le lecteur lève alors une erreur,
et le parcours indique combien de composants ont échoué.

## Maillages statiques {#static-meshes}

Un export `UStaticMesh` est constitué de ses propriétés suivies de données natives. Les propriétés ne servent pas à
la géométrie et ne sont pas lues. La partie native se trouve par son début fixe : un drapeau GUID nul, deux octets de
drapeaux de bandes, `bCooked = 1`, et l'indice de l'export `BodySetup` propre au maillage. Elle se lit ensuite dans
l'ordre où `UStaticMesh::Serialize` et `FStaticMeshRenderData::Serialize` l'écrivent pour un maillage **cuit, non
Nanite** :

- jusqu'à 16 niveaux de détail, chacun avec ses sections (matériau, premier index, nombre de triangles), ses
  limites, et, quand il est **intégré** : le tampon de positions (float32 x 3), les tangentes, les UV (tous les canaux,
  demi ou pleine précision), les couleurs, et le tampon d'index (16 ou 32 bits) ;
- ce qui suit (tampons d'index inversés et de profondeur seule, données de lancer de rayons, échantillonneurs à
  surface pondérée) est sauté pour atteindre le niveau suivant.

Un niveau qui n'est pas stocké en ligne termine la liste. Un maillage sans aucun niveau est refusé. Les positions
sont celles d'Unreal : centimètres, X vers l'avant, Y vers la droite, Z vers le haut.

Vérifié : presque chaque maillage échantillonné se décode (les autres sont squelettiques), et l'étendue décodée d'une
tuile de route correspond aux limites qu'elle stocke.

## Textures {#textures}

Un export `Texture2D` est constitué de ses propriétés, puis de ses données de plateforme cuites : le nom du format de
pixels, la taille, et une table de niveaux de mip, chacun pointant dans la **table de données en masse** du paquet
(décalage, taille, drapeaux ; en ligne dans l'export quand le drapeau `0x40` est posé, sinon dans le `.ubulk`). Les
données de plateforme sont trouvées par leur propre forme, non en sautant les propriétés, donc la disposition des
propriétés de la classe de texture n'a pas d'importance. Le premier mip qui ne dépasse pas la taille demandée est
décodé.

| Format Unreal | Décodé en |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | RGBA 8 bits |
| `PF_G8` | gris 8 bits |

Vérifié : une image satellite DXT5 de 4096 px dont les treize niveaux ont exactement la taille des entrées en masse.

## Textures virtuelles en flux {#streaming-virtual-textures}

Une `VirtualTexture2D` cuite est faite de tuiles carrées avec bordure, par niveau de détail, adressées par un
**code de Morton** (x dans les bits pairs), stockées en morceaux des données en masse du paquet. La disposition se lit
comme l'écrit `FVirtualTextureBuiltData::Serialize` dans Unreal 5.6 : couches, taille des tuiles, bordure, tables
d'adresses de tuiles par mip, formats de couches, et le morceau *n* correspond à l'entrée en masse *n*. Une région de
la texture est assemblée tuile par tuile, bordures retirées, depuis le niveau dont la résolution est la plus proche de
la taille voulue. Seule la première couche est lue, et seulement dans les formats ci-dessus.

Vérifié : les tuiles d'un morceau de texture virtuelle sont comptées jusqu'à l'octet.
