---
title: "Frostbite : `.toc`, `.cas`, bundles, maillages et niveaux"
nav_order: 5
lang: "fr"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite : `.toc`, `.cas`, bundles, maillages et niveaux {#frostbite-toc-cas-bundles-meshes-and-levels}

**Lit un niveau de Battlefield 6 jusqu'à son terrain, ses maillages placés et leurs cartes de couleur, et l'écrit en `.glb`.** Les jeux Frostbite (Battlefield, Need for Speed, Dead Space) gardent leur contenu dans des blobs `.cas`, décrits par des tables des matières `.toc`. La table d'un niveau indique quels bundles le niveau charge, les bundles nomment chaque ressource, et les ressources indiquent quel maillage se trouve où.

Sources :
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tables, paquets, charges utiles),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bundles et leurs manifestes),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(partitions EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(champ de hauteurs),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(textures et matériaux),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(placement et export).
Commandes : `identify`, `levels`, `level` (voir [Commandes](commands.md#levels-and-level-frostbite)).

Rien de ceci n'est documenté par le jeu. Chaque disposition ci-dessous a été lue dans les
fichiers, puis vérifiée sur l'ensemble de ceux-ci, et chaque section indique la vérification
faite. Là où les outils de modding Frosty décrivent d'anciennes versions d'une structure, les
noms de champs suivent les leurs ; aucun code n'a été repris d'eux (voir
[Règles et licences](rules-and-licences.md)).

## L'en-tête qui semble chiffré et ne l'est pas {#the-header-that-looks-encrypted-and-is-not}

| Signature (u32, little-endian) | Signification | Traitement |
|---|---|---|
| `0x00CED100` | simple : l'arbre commence immédiatement | lu |
| `0x01CED100` | signé : une signature de 556 octets, puis l'arbre **en clair** | lu |
| `0x03CED100` | obfusqué par XOR, avec la clé dans l'en-tête du fichier | détecté et refusé |

La forme signée est celle qu'envoie Battlefield actuel. Les octets à forte entropie après la
signature sont une signature, pas du texte chiffré.

## L'arbre DbObject {#the-dbobject-tree}

Une structure récursive unique. Chaque champ est un octet de type (les cinq bits de poids faible
le type, le bit 7 « anonyme »), un nom optionnel, et une valeur. Les conteneurs portent leur
longueur sous forme d'entier de longueur variable et se terminent par un octet zéro.
`parse_toc` vérifie la longueur de chaque conteneur, donc un fichier qui se lit a été compris.
`layout.toc` a cette forme.

## Paquets d'installation {#installation-packages}

Chaque emplacement nomme le **paquet d'installation** auquel appartient son blob. Chaque paquet
numérote ses blobs à partir de `cas_01`, si bien que le seul numéro de blob est ambigu dès que
plus d'un paquet est installé, ce qui est toujours le cas.

- `layout.toc` liste les paquets sous `installManifest.installChunks`, chacun avec un `persistentIndex` et un `installBundle` tel que `Win32/installation/<package>`.
- Les blobs du paquet se trouvent dans ce dossier, sous `Data` pour le jeu de base, ou sous `Update/<pack>/Data` pour ce qui est venu plus tard.
- Un enregistrement d'emplacement porte le `persistentIndex` complet sur 32 bits : la moitié basse de son premier mot contient la moitié haute, la moitié haute du second mot la moitié basse ; la moitié basse du second mot est le numéro de blob.

Vérification : chaque emplacement de chaque table binaire d'une installation se résout en un
paquet déclaré et tombe dans le blob qu'il nomme. Une version antérieure prenait le premier
`cas_NN.cas` du bon numéro. Un tiers des charges utiles qu'elle lisait alors paraissait à forte
entropie, et était pris pour du chiffrement. C'étaient les bons décalages dans le mauvais
fichier. Rien de trouvé n'est chiffré.

## La table du niveau {#the-level-table}

La table d'un niveau (`levels/<level>/<level>.toc`) est une table de sections : quinze mots
d'en-tête en big-endian, puis des sections placées bout à bout, dont les décalages sont à la fois
déclarés et calculables à partir de deux comptes.

| Section | Contenu |
|---|---|
| bundles | une table de hachage (un mot chacun), puis un enregistrement de 16 octets par bundle : clé, `0x40000000` \| taille, 0, décalage |
| table de hachage des morceaux | un mot par morceau |
| morceaux | identifiant de 16 octets (le GUID du morceau, **à octets inversés**), puis un mot : `0x80000000` \| 4 x l'index de son emplacement |
| emplacements | quatre mots big-endian : paquet (partagé), blob, décalage, taille |

Les identifiants de morceaux et les emplacements sont **dans des ordres différents**. Les lire
dans l'ordre du fichier associe chaque morceau aux octets d'un autre morceau, qui se décodent
parfaitement (surtout en son), et donc ne paraissent pas faux jusqu'à ce qu'un maillage sorte
en bruit. Vérification : dans un niveau, les mots d'index sont une permutation de 0 à
(nombre de morceaux - 1).

Les bundles sont stockés en ligne après la table des sections. Chacun a neuf mots d'en-tête
big-endian, puis ses entrées : huit octets de décalage et de taille, précédés de huit autres
octets nommant le paquet et le blob quand le bit de poids fort de l'octet d'indicateur de
l'entrée est à 1. Vérification : sur chaque bundle, la dernière entrée se termine exactement là
où commencent les octets d'indicateur.

### Quelle table est le niveau {#which-table-is-the-level}

Un niveau peut avoir plusieurs tables du même nom : une dans le `Data` du jeu de base, une dans
chaque mise à jour (`Update/<pack>/Data`) qui le livre ou le modifie, et une dans chaque pack
haute résolution (`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Seules certaines
contiennent des bundles. Pour un niveau livré par une mise à jour, la table du jeu de base ne
contient que des morceaux et aucun bundle, et celle de la mise à jour est le niveau ; prendre la
première table trouvée n'exportait rien de lui.

Le niveau est donc la table qui a le plus de bundles, une couche plus tardive l'emportant à
égalité (jeu de base d'abord, puis les mises à jour par ordre de nom), et les tables du même nom
sans bundle sont ses **compléments** : leurs morceaux sont ajoutés à ceux du niveau, car ils
portent les plus grands mips de ses textures. Un en-tête de texture nomme ce morceau à +164 (voir
[Textures et matériaux](#textures-and-materials)). `levels` affiche d'où vient chaque niveau et
combien de compléments il a.

## Manifestes de bundles {#bundle-manifests}

La première entrée d'un bundle est son manifeste, stocké sans compression. C'est le format binaire
de bundle des anciens jeux Frostbite avec une nouvelle signature, `0xD68E799D` : comptes, SHA-1,
enregistrements ebx et res (décalage de nom et taille), types de res, métadonnées et identifiants,
GUID de morceaux, chaînes. Les autres entrées du bundle sont l'ebx, le res et les morceaux, dans
cet ordre. Vérification : les comptes correspondent aux entrées sur chaque bundle, et les chaînes
commencent là où finissent les enregistrements.

Les types de ressources sont des hachages. `0x49B156D4` est MeshSet (chaque res de ce type se
nomme `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` lit tout cela pour un niveau, en quelques secondes : un niveau compte des dizaines
de bundles et des dizaines de milliers de ressources ebx, res et morceaux.

## Blocs de charge utile {#payload-blocks}

```
[taille décompressée : 4] [méthode : 2] [taille compressée : 2]    big-endian
```

Une taille compressée de zéro signifie stocké, à condition que cela se décompresse en la même taille.

| Mot de méthode | Codec |
|---|---|
| `0x0070`, `0x0071` | aucun |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), depuis la DLL `oo2core` du jeu) |
| autre, avec des tailles égales | copié tel quel |
| autre | refusé |

Lue depuis le bon paquet, chaque charge utile échantillonnée se décode.

## Partitions EBX {#ebx-partitions}

EBX contient tout ce qui n'est pas de la donnée brute. Chaque partition est un fichier RIFF :
`EBXD` (les données, alignées sur 16), `EFIX` (GUID de partition, GUID et signatures de types,
décalages d'instance, de pointeur, d'import et d'informations de type, imports, et décalages des
tableaux, valeurs encadrées et chaînes), `EBXX` (la table des tableaux : décalage, nombre, hachage,
drapeaux, type d'élément). Un champ de pointeur fait huit octets : zéro est nul, une valeur impaire
est le numéro d'import `value >> 1`, toute autre valeur est relative au champ.

La **bibliothèque de types n'est pas lisible**. Le jeu la livre dans son système de fichiers
initial, qui est chiffré, et ce paquet n'y touche pas. Les types sont connus par GUID et signature,
que chaque partition porte, et les quelques types dont l'export de niveau a besoin ont été
disposés d'après les données.

## MeshSet {#meshset}

Un maillage est une ressource res MeshSet (la description) et un morceau par niveau de détail (les
tampons).

| Partie | Disposition |
|---|---|
| préfixe | quatre mots : taille d'en-tête (176 ou 192), taille d'enregistrement de niveau (176 à 188), taille d'enregistrement de section (368), 0 |
| en-tête | boîte englobante ; six décalages de niveau en i64 ; type de maillage à `0x6C` (rigide, squelette, composite) ; nombre de niveaux et de sections à `0x9C` |
| niveau | sections à `+0x08` ; cinq listes de dessin à `+0x14` (opaque, transparent, décalcomanie, profondeur seule, ombre) ; format d'index à `+0x54` (`0x21` u16, `0x2E` u32), octets d'index et de sommets ; GUID de morceau à `+0x74` |
| section | nom du matériau ; pas de sommet ; triangles, premier index, décalage de sommets (en octets), nombre de sommets à `+0x20` ; déclaration de sommets à `+0x64` : 16 x (usage, format, décalage, flux), 16 pas de flux, comptes |
| morceau | le tampon de sommets, puis le tampon d'index. Les flux d'une section se suivent ; les index sont comptés à partir du premier sommet de la section |

Les positions sont d'usage 1, flux 0, décalage 0, en quatre demi-flottants ou trois flottants.
Seules les sections opaques et transparentes sont dessinées. Chaque section nommée `..._shadow` est
dans la liste d'ombre et seulement là : ce sont les listes qui décident.

Vérification : chaque maillage d'un niveau dont les niveaux sont stockés en morceaux se décode, et
presque tous ont 99 % ou plus de leurs sommets dans leur boîte déclarée ; le reste la rate d'un
arrondi de demi-flottant. Une caisse décodée mesure environ un mètre, Y vers le haut, avec ses
normales tournées vers l'extérieur.

## Placement {#placement}

Le pipeline de contenu rassemble les objets statiques de chaque sous-monde dans un **groupe de
modèles statiques** : un tableau de membres, un par maillage, chacun avec ses transformations
d'instance.

| Type (GUID, signature) | Disposition |
|---|---|
| membre `ad13064e…`, `0xF861A878` | 224 octets : `+88` tableau de transformations, `+112` le plan d'objet (import), `+160` le ressource de maillage (import) |
| transformation `101dce06…`, `0x5E6D8C37` | 64 octets : droite, haut, avant, translation, chacun un vec3 complété à 16 |

La partition de la ressource de maillage se nomme comme sa ressource res MeshSet, donc le GUID de
partition de l'import donne le maillage. Un point se place à
`x·right + y·up + z·forward + translation`. La transformation propre du groupe était l'identité dans
chaque groupe des niveaux vérifiés, et n'est pas appliquée.

Vérification : dans un niveau, chaque membre de chaque groupe se résout en un maillage ; la plupart
des copies ont une rotation de déterminant 1 à un millième près, les autres sont mises à l'échelle
ou en miroir. Les GUID et signatures de types sont les mêmes dans les autres niveaux. Une mise à
jour du jeu qui change la disposition change la signature, et le lecteur ne trouve alors rien au lieu
de lire de travers.

### Objets placés un par un {#objects-placed-one-by-one}

Ce que le pipeline ne peut pas grouper — objets destructibles, conteneurs, débris — est placé par des
**références d'objet** et des **références de préfabriqué** dans les partitions du niveau :

| Type (GUID, signature) | Disposition |
|---|---|
| référence d'objet `a9a6a6ad…`, `0xC4856BEC` | `+32` la transformation (comme ci-dessus), `+112` le plan d'objet (import) |
| référence de préfabriqué `117c746e…`, `0xDE3FE9B4` | la même ; le plan est un préfabriqué, une partition d'autres références |

Les préfabriqués s'imbriquent ; une copie se place à sa propre transformation multipliée par celle
de son parent (vecteurs lignes), jusqu'à huit niveaux. Un plan d'objet se dessine comme les
maillages qu'il importe, en laissant de côté les états détruits (`dc_...`). Un préfabriqué groupé
est référencé par son reste `..._nongroupable_autogen`, si bien que rien n'est dessiné deux fois.

La recherche ne part que des mondes et des couches du niveau. Une partition dont la première
instance est un plan de préfabriqué (`134919fc…`, `0x0247807D`) est la définition d'un préfabriqué,
et un niveau en garde beaucoup dans son propre dossier, placés par ses mondes d'autres façons que
ces références ; parcourue comme si c'était un monde, un préfabriqué met son contenu à ses
coordonnées locales. Cela entasse des centaines de copies autour de l'origine du monde, loin sous
le sol. Les mondes et les couches ont `a10ebe0f…`, `0xD3D16C3C` en premier.

Les plans mis hors jeu ne sont pas suivis : les ressources de développement et de test
(`game/dev/`, `test/`), l'ensemble de la cinématique de fin de manche (`..._gameend_...` : mis en
scène sous le sol) et le contrôleur de la caméra de mort (`.../deathflow/...`, dont les gadgets se
trouvent à l'origine du monde). Ils sont reconnus par leur chemin de ressource, non par leur couche :
la même couche qui contient l'ensemble de la cinématique peut placer les vrais murs et toits d'un
niveau. Après ces deux règles, aucune copie des niveaux vérifiés ne se trouve à plus de 10 m sous le
terrain, et les copies reposent sur le terrain là où le jeu les montre.

**Niveaux de détail qui font office de substitut.** Le dernier niveau de détail d'un maillage peut
passer à un substitut de vue lointaine avec un matériau propre : `M_LastLod`, `M_Billboard`,
`M_Vista`, `M_ProjectionLod`. Une tour en treillis de dizaines de milliers de triangles peut se
terminer par une silhouette de quelques centaines, que le budget choisirait et qui, de près, est une
pointe pleine. Un niveau de détail qui fait intervenir un tel matériau, que son niveau le plus fin
n'a pas, n'est jamais choisi : le plus grossier du maillage est le dernier vrai.

## Terrain {#terrain}

Source : [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Le terrain est une ressource res TerrainStreamingTree (type `0x22FE8AC8`) et les morceaux qu'elle
nomme.

| Partie | Disposition |
|---|---|
| en-tête | 34 octets ; le nombre de nœuds à 25 |
| arbres raster | un octet de type et un u32 de longueur chacun, jusqu'à un octet de type `0xFF`. Type 0 est le champ de hauteurs : des échantillons par côté à +5 (265), plage de hauteurs à +21 (1 280 m), le carré de terrain dans son premier enregistrement de nœud à +77 (8 192 m dans le niveau vérifié). Il contient les boîtes englobantes des nœuds et une pyramide min/max de 16 x 16 par nœud, pas les hauteurs |
| nœuds de flux | le quadtree, en profondeur d'abord : taille de morceau et GUID ; un second morceau optionnel ; un octet d'indicateurs (bit 0 : le morceau commence par une page de hauteurs) ; a des enfants. Enfants dans l'ordre (0,0), (1,0), (1,1), (0,1) |
| page de hauteurs | les premiers 265 x 265 u16 du morceau d'un nœud marqué, ligne par ligne ; hauteur = valeur x 1 280 / 65 535 m ; colonnes le long de x, lignes le long de z, à partir du coin bas du nœud ; une bordure de 4 échantillons, soit 256 cellules par nœud |

Chaque étape a été vérifiée séparément :

- L'analyse du quadtree de nœuds consomme la ressource jusqu'à son dernier octet, avec les 529 nœuds déclarés.
- Les nœuds voisins partagent exactement leurs neuf colonnes de bord, donc le pas est 256.
- Les échantillons d'un enfant à chaque autre position sont exactement égaux à ceux de son parent avec une bordure de 4, et s'écartent de 90 à 700 unités avec toute autre bordure.
- Le plus petit mot du niveau se décode en la plus basse hauteur de la boîte englobante, au centimètre près.
- Parmi les huit façons dont le carré pourrait se poser sur le monde, seules x le long de x et z le long de z placent les objets sur lui : la moitié des copies échantillonnées à environ 2 m près, contre plusieurs fois plus pour chacune des autres façons.

Les objets placés mesurent ensuite le résultat. Le point le plus bas de chaque copie, par rapport au
terrain dessous (bilinéaire, depuis le nœud le plus fin) :

| Placé | Distance médiane | Médiane signée |
|---|---|---|
| arbres et buissons | nettement moins d'un mètre | juste sous la surface |
| accessoires | un ou deux mètres | sur la surface |
| rochers | environ un mètre | enfoncés d'environ un mètre |
| bâtiments | plusieurs mètres (ils reposent sur des fondations) | légèrement enfoncés |

La végétation est posée sur le sol et nulle part ailleurs, ce qui en fait la vérification la plus
nette : ses origines sont à une médiane de 0,07 m de la surface. Les bâtiments s'étalent largement
parce que la catégorie contient des murs, des planchers et des éléments de structures à plusieurs
étages et souterraines. Décaler le terrain de 64 m latéralement fait tomber la part des copies à
moins de 0,5 m de 29 % à 10 %.

`level` dessine le champ de hauteurs comme `ground:terrain`, chaque morceau à partir du nœud le plus
fin qui a des hauteurs là et pas plus fin que `--ground-spacing` (4 m par défaut : 3,7 millions de
triangles pour le niveau vérifié, dont les nœuds les plus fins font 0,5 m). Des morceaux de résolutions
différentes se rejoignent par de petites marches ; rien ne les raccorde.

Le morceau d'un nœud contient aussi les pages des masques de couches après sa page de hauteurs, et
son second morceau se termine par la carte de couleur du nœud (voir
[Couches de terrain](#terrain-layers)).

## Couches de terrain {#terrain-layers}

Le jeu ombre le terrain près d'un joueur en superposant des matériaux de surface en mosaïque par des
masques peints, avec une carte de couleur par-dessus, et en dessinant des décalcomanies (routes,
taches d'asphalte, marquages de piste) par-dessus. L'exposé de Frostbite sur le système (Widmark,
« Terrain in Battlefield 3 », GDC 2012) liste les rasters du terrain : le champ de hauteurs, les
masques de superposition des shaders, une carte de couleur « utilisée comme une superposition par-dessus
la superposition de shaders », des matériaux physiques, un masque de profondeur de destruction, une
carte d'albédo pour la lumière réfléchie et des canaux de masque supplémentaires ; les tuiles d'un
raster portent une bordure pour les algorithmes de rendu. L'arbre de flux des niveaux vérifiés a sept
arbres raster, de types 0, 1, 2, 4, 5, 7 et 8, dont les en-têtes commencent par leur taille de tuile :
265 pour le champ de hauteurs (type 0) et le type 2, 72 ou 66 pour les masques (type 1), 132 avec une
bordure de 2 pour la carte de couleur (type 4), 260 avec une bordure de 2 pour le type 5.

**La liste des couches.** La ressource `....layergraphs` du terrain liste une entrée de 32 octets par
couche, dans l'ordre où les enregistrements de masque les numérotent (34 entrées, 34 sections de dépôt
et index de couches de 0 à 33 dans un niveau) ; l'identifiant de chaque entrée se termine par sa clé de
section dans le dépôt de blocs de shader du graphe de couches (`....layergraphs_shaderblockdepot`), dont
le bloc nomme les cartes de la couche : une carte de couleur `_cv`, des cartes `_nhs` et `_ao` par surface,
plus des cartes de détail et de bruit partagées. Beaucoup de couches ne nomment aucune carte : ce sont des
sources que lit le graphe de couches. La couleur d'une couche est la moyenne de sa carte `_cv` ; l'échelle
de répétition n'est pas trouvée. L'asset du terrain se termine par une entrée de cinq octets par couche
(un octet, puis un u32 d'index de couche ou -1).

**Les masques.** Le raster d'arbre 1 est le quadtree des masques. Son corps commence par 59 octets, la
taille de la page à l'octet 0 : 72 quand les pages sont en BC4 (72 x 72, 2 592 octets), 66 quand elles
sont en huit bits non compressés (4 356 octets). Viennent ensuite un groupe par nœud, en profondeur
d'abord :

| Partie | Disposition |
|---|---|
| groupe | u16 ; u16 nombre d'enregistrements ; u32 nombre de pages ; les enregistrements ; un octet zéro. Un groupe sans enregistrement fait 7 octets en tout |
| enregistrement | 33 octets : u16 couche, u16 hachage, la boîte du quadrant (quatre flottants), deux octets d'indicateurs, une pyramide de présence de 85 bits |

Les enregistrements d'un groupe sont les quatre quadrants de son nœud, couche par couche, les quadrants
de chaque couche dans l'ordre (0, 0), (1, 0), (1, 1), (0, 1). Un enregistrement dont le second indicateur
est levé couvre son quadrant entier et n'a pas de page ; un enregistrement sans lui a la page suivante ;
un quadrant sans enregistrement d'une couche que son groupe nomme est vide pour cette couche ; le premier
indicateur est levé exactement quand la couche se poursuit dans le groupe du quadrant lui-même, un niveau
plus bas, qui la remplace là. Le nombre de pages est le nombre d'enregistrements qui ont une page.

Les pages : les pages du groupe propre d'un nœud de flux suivent, dans son morceau, la page de hauteurs,
une section de 4 358 octets en 16 bits et un raster 67 x 67 en huit bits (depuis le début du morceau quand
il n'a pas de page de hauteurs) ; son second morceau contient les pages des groupes de ses quatre quadrants,
un niveau plus bas, dans l'ordre de la carte de couleur, puis la carte de couleur. Une page est les 64 x 64
texels du quadrant, les lignes le long de z et les colonnes le long de x, avec une bordure recopiée de ses
voisins : 4 texels sur une page BC4, 1 sur une page non compressée.

Les bordures prouvent le placement sans jugement : deux pages d'une même couche côte à côte doivent
porter les texels de bord l'une de l'autre. `read_masks` le vérifie pour chaque paire qu'il place et refuse
un niveau où moins de 99 % concordent. Environ un tiers des niveaux vérifiés sont lus, avec leurs bordures
concordantes ; quelques-uns n'ont aucun masque peint ; les autres sont refusés, presque tous par la
vérification (leurs morceaux de nœuds contiennent plus que ce que la disposition connaît). Le sol d'un
niveau refusé prend la couleur moyenne de ses matériaux de surface, et l'export en indique la raison. Les
bords face à un quadrant plein valent 255, ceux face à un quadrant vide 0.

Les sections de 4 358 octets et le raster 67 x 67 qui précèdent les pages ne sont pas lus : leurs valeurs
se trouvent dans une bande haute et étroite, sans petites valeurs ni sentinelle.

**La couleur du sol.** Le graphe de couches mélange les couches dans un graphe de shaders compilé de masques,
de pente, de hauteur et de bruit, qui n'est pas lu. `--ground-texture` colore le sol par une règle propre,
énoncée ici comme telle :

- les couches dont la carte de couleur est nommée pour la distance sont les substituts de la vue lointaine et sont laissées de côté ;
- les couches texturées qui couvrent neuf dixièmes du terrain ou plus sont la base. Leurs masques sont pleins presque partout, donc où chacune se trouve est le choix du shader, non le leur : celles nommées pour la roche ou la falaise colorent les pentes de plus de 40 degrés, celles nommées pour le gravier colorent le sol plat (les autres couches de base quand aucune n'est nommée ainsi), mélangées entre 20 et 40 degrés selon la pente du champ de hauteurs (prise tous les 4 m et répartie bilinéairement sur les texels cuits : répétée par blocs de 4 m, elle dessinait la couleur rocheuse en taches aux bords durs) ;
- chaque autre couche texturée est posée sur la base par son propre masque, dans l'ordre des couches ;
- la carte de couleur est superposée au résultat comme le fait le moteur, deux fois la couleur du sol multipliée par la carte, si bien qu'un gris moyen la laisse telle quelle ; là où la carte de couleur n'a pas de texels, le sol prend la luminosité médiane de la carte, en gris.

Comparé à la médiane de couleur du sol dans des images de jeu de trois niveaux (chroma en rouge et bleu
par rapport au vert) : la zone de jeu cuite donne 1,00 / 0,69 contre 1,19 / 0,78 pour les images dans
l'un, dont les couches d'herbe sont vertes là où les images montrent de l'herbe sèche ; 1,19 / 0,82 contre
1,01 / 1,04 dans un autre, dont la carte de couleur est elle-même chaude (1,13 / 0,88) ; et 1,05 / 0,91
contre 0,93 / 0,92 dans un troisième sans carte de couleur. Les images sont éclairées et étalonnées, donc
ceci mesure la teinte, non la luminosité.

**La carte de couleur.** Le second morceau d'un nœud contient, après les pages de masques de ses groupes
de quadrants, quatre pages BC7 de 132 x 132 (17 424 octets chacune), une par quadrant du nœud, dans l'ordre
(x bas, z haut), (x haut, z haut), (x haut, z bas), (x bas, z bas). L'arbre des masques dit combien d'octets
prennent les pages de masques, donc la carte de couleur se trouve par compte, non par la fin du morceau : dans
un niveau, les nœuds plus grossiers portent quatre autres pages de ce type après elle, une autre raster en
couleur unie, et lire les quatre dernières pages du morceau a fait perdre la carte de couleur sur neuf dixièmes
du terrain. Sans ce compte, la carte était aussi manquée dans les niveaux aux pages de masques non
compressées, qui ne font pas un nombre entier de pages BC4 ; la carte d'un niveau est passée de 0,4 à 0,94 de
son terrain. L'ordre a été ajusté : contre les bords du champ de hauteurs de chaque quadrant, chaque page des
nœuds qui ont des particularités correspond à un quadrant, non retourné, à 0,3 - 0,54 là où le meilleur placement
suivant est sous 0,2. Assemblées ainsi, les pages d'un niveau se rejoignent sans couture dans les routes, l'eau
et les zones bâties du niveau d'essai, à 0,5 m par texel dans la zone de jeu. Là où les couches font le travail,
la carte est presque neutre (médiane 110, 107, 104) ; ailleurs elle peut porter une couleur pleine. Un niveau
dont les seconds morceaux ne contiennent que des pages de masques non compressées n'a pas de carte de couleur
lue. Une version antérieure de ce lecteur disait que ces pages n'étaient pas géographiques : elle les comparait à
la carte d'arrière-plan, qui peut être un tout autre paysage, et plaçait chaque page sur tout son nœud au lieu
d'un quadrant.

**L'albédo de lumière réfléchie** a été cherché et non trouvé : les morceaux du nœud racine et des nœuds du
premier niveau sont des pages de masques entières, et la charge utile du type 5 n'est pas localisée.

**Trous.** L'asset de terrain d'un niveau (type de ressource `0x1CA38E06`) nomme trois shaders : un shader de
surface par défaut, un shader de surface de trous et un shader source par défaut. La couche que lit le shader de
trous n'est pas trouvée, donc le champ de hauteurs n'est pas découpé. Dans un niveau, le maillage de navigation
peut passer sur des maillages rocheux à des dizaines de mètres sous le champ de hauteurs, là où le jeu doit
l'avoir découpé. Cherchés et non trouvés là : le masque d'une couche, le raster 67 x 67, une hauteur réservée
(aucune page de hauteurs du niveau ne contient 0 ou 65 535) et un indicateur de nœud (chaque nœud sous la
racine a les indicateurs 1). Les rasters 7 et 8 sont ce qui reste. Tous deux sont codés par longueur de série :
un octet égal à celui qui le précède est suivi d'un compte de copies supplémentaires (`ff ff 84` vaut 134 octets
de 255). L'arbre 7 (tuile 256, un quadtree complet à cinq niveaux, quatre bits par échantillon) se décode en
paires d'octets de valeurs 0 à 3 ; l'arbre 8 (tuile 265) en octets surtout à 255, avec ses autres valeurs en
séries régulières. Ni l'un ni l'autre n'a encore ses tuiles placées, donc on ne sait pas s'ils portent les trous.

**Les décalcomanies** sont lues et cuites ; voir [Décalcomanies de terrain](#terrain-decals).

## Décalcomanies de terrain {#terrain-decals}

Source : [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Routes, pistes, aires de béton, lignes et lettres peintes, traces de pneus : la ressource
`TerrainDecals` (type `0x15E1F32E`) les contient sous forme de géométrie plate que le jeu pose sur le
terrain.

| Partie | Disposition |
|---|---|
| en-tête | à +16 un nombre d'emplacements n, puis n emplacements de 16 octets, puis le nombre d'enregistrements |
| enregistrements | un par lot de dessin, bout à bout, de longueur variable : 156 octets de champs fixes — premier sommet à +32, nombre de triangles à +36, répétition de texture en mètres à +44 — puis les octets de sommets du lot (décalage, taille), puis une queue qui nomme ses textures par les GUID de partition de leurs ressources |
| sommets | 32 octets : x, z (f32), 8 octets compactés, u, v (f32), r, g, b, a (f16) ; chaque lot est une liste simple de triangles |
| index | u32, comptés à partir de 0 dans chaque lot ; non nécessaires |

Vérifications :

- les plages de sommets des enregistrements se suivent sans trou et couvrent exactement tous les sommets, et le premier sommet de chaque enregistrement multiplié par 32 donne son décalage ;
- ainsi lus, les triangles sont des décalcomanies compactes (lettres, bandes de ligne, taches) ; lus d'un sommet décalé, ce sont des éclats qui traversent la carte ;
- presque tous les lots nomment des textures dans leur queue : une carte de couleur (`_cv`) avec une carte d'opacité (`_op`, canal rouge), ou pour les marquages un masque de canaux (`_rgb`).

Après les GUID de texture, la queue porte les paramètres de matériau du lot, codés comme ceux d'un bloc de
shader (voir Teintes plus bas). La couleur de peinture d'un marquage, d'une trace de piste ou d'une ligne est
le float3 de hachage `607e` : un 0,64, 0,56, 0,48 sablonneux pour les traces dans le sable, presque noir pour
le goudron. Les cartes d'opacité sont surtout au format 62, un canal à 8 octets par bloc, lu comme BC4.

Un lot applique sa texture soit par position dans le monde (u = x, v = z, la texture se répétant tous les
mètres de répétition : asphalte, béton, gravier), soit de 0 à 1 à travers la décalcomanie (une ligne, une
lettre, une trace de pneu). Les enregistrements sont dessinés dans l'ordre du fichier.

**La cuisson.** `level --ground-texture M` peint, sous l'étendue des décalcomanies et en tuiles d'au plus
4 096 pixels, la carte de couleur d'arrière-plan (bilinéaire), puis chaque lot par-dessus selon son opacité
× l'alpha du sommet. La couleur des sommets n'est pas utilisée : certains sommets de lots sont vert pur ou bleu
pur, ce qui teintait les marquages d'un niveau de ces couleurs. Les triangles du champ de hauteurs là deviennent
des parties `ground:terrain x<x> z<z>` portant la tuile. Chaque lot se dessine ainsi :

| Les lots nomment | Dessiné comme |
|---|---|
| une carte de couleur (`_cv`) | la carte, par sa carte d'opacité |
| une carte de multiplication (`_mult`) et une carte d'opacité | la peinture (blanc si le matériau n'en nomme pas) multipliée par la carte de multiplication, par la carte d'opacité : la ligne centrale usée d'une piste, les lignes de bord et les barres de seuil |
| un masque de canaux (`_rgb`) | la peinture, sinon blanc pour les lignes et lettres, sombre pour les contours, un léger assombrissement pour l'usure, les traces de pneus, les taches, les flaques et l'humidité, par le masque |
| une carte d'opacité seule, avec une peinture | la peinture par la carte d'opacité : les traces de pneus |

Un masque de variation de route ne sert pas de peinture : il fait varier la surface qui se trouve dessous,
sur des centaines de mètres, et n'est pas dessiné, quelle que soit sa peinture ; peint en blanc, il posait
deux rectangles pâles de 150 à 250 m de long sur les pentes d'un niveau. La carte `_mult` est prise comme
l'usure propre de la peinture, non comme un assombrissement du sol dessous : elle est presque blanche, et la
forme de la ligne est dans la carte d'opacité.

Presque chaque lot se dessine, dans quelques tuiles à 0,5 m par pixel ; l'export grossit de quelques Mo et
prend quelques secondes de plus. Vus d'en haut, les tabliers, les voies de circulation et le réseau routier
se trouvent sous les clôtures et bâtiments des enceintes, et mènent à leurs portails.

Dessinées plutôt comme leur propre géométrie, les décalcomanies auraient besoin d'un mélange alpha que le
writer ne transporte pas, et d'un décalage au-dessus d'un terrain elles se battraient en profondeur avec lui ;
la cuisson les garde dans la couleur propre du sol.

## Textures et matériaux {#textures-and-materials}

Source : [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Une ressource Texture (type `0x6BDE20BA`) est un en-tête de 180 octets : type et format de pixel à +8,
largeur et hauteur à +22, nombre de mips à +30, GUID du morceau à +40, quinze tailles de mips à +56.
Le morceau est la chaîne de mips, du plus grand au plus petit. Certains morceaux n'ont pas leurs plus
grands mips, livrés dans un pack haute résolution, et la longueur du morceau indique à quel mip il
commence. Le morceau de ce pack est nommé à +164 ; il est lu depuis les
[compléments](#which-table-is-the-level) du niveau quand un mip qui manque au morceau principal est voulu,
et sa longueur plus celle du morceau principal donne toute la chaîne.

| Format | Décodé en | Preuve |
|---|---|---|
| 67, 66 | BC7 (sRGB, linéaire) | une feuille de couleur de réservoir en plastique se décode ainsi ; en BC3, les mêmes octets sont du bruit |
| 61, 60 | BC3 | une feuille de caisse se décode proprement en BC3, ni en BC1 ni en BC7 |
| 57, 56, 55 | BC1 | un demi-octet par pixel |

La ressource de maillage ne nomme aucune texture. Le lien se trouve dans les **dépôts de blocs de shader**
du niveau (type de ressource `0x73312045`, un par sous-monde), indexés par les huit octets à +0x130 de
l'enregistrement d'une section de maillage :

| Partie | Disposition |
|---|---|
| table, à 16 | (clé de section u64, décalage de descripteur u64), jusqu'à un décalage hors de la ressource |
| descripteur | (décalage de bloc u64, hachage u64, taille de bloc u64) |
| bloc | les paramètres de shader de la section ; chaque texture est un enregistrement de 49 octets : un octet, 16 octets, le GUID de partition de l'asset de texture, son GUID d'instance |

La clé de section de la caisse apparaît une fois dans chacun des dix dépôts des sous-mondes qui la placent,
et son bloc nomme `t_mil_crate_03_cs` et `_nmt` parmi les cartes de détail partagées. Un bloc nomme toutes
les textures que le shader échantillonne, et la carte de couleur n'est pas désignée : elle est donc choisie.
C'est une texture 2D sRGB dont le nom contient la plupart des mots du nom du matériau (`M_ConcreteWall_01` :
concrete, wall), puis ceux du nom du maillage, puis une qui n'est pas une carte de détail, de décalcomanie
(`t_de_...`) ou de dommage, puis celle que le moins de blocs utilisent. Le bloc d'un panneau de route nomme
son panneau `t_com_highwaysignage_01_cs` et une feuille de décalcomanie `t_de_com_highwaysignage_01_ca` avec
un bouclier couché ; les deux correspondent aux mots, et sans la règle de décalcomanie la feuille gagnait à
l'usage et le panneau montrait le bouclier tourné d'un quart, à travers chaque jeu de coordonnées de texture
de la section. Les signed distance fields (`..._sdf`), les palettes et les masques de canaux (`_rgb`) ne sont
jamais choisis, quels que soient les mots qu'ils partagent (les `_rgba` le sont : la plupart sont de la couleur
avec un alpha, et les laisser de côté remplaçait par des cartes sans rapport la carte propre d'un pylône et
celle d'un escalier) : l'atlas de végétation d'un arrière-plan `..._atlas_a_sdf`, dessiné en couleur, montrait
des étoiles noires et blanches pour les arbres ; la palette de bâtiments d'un arrière-plan, une confetti
d'échantillons pour les murs ; et du verre cassé dessiné à travers son masque de canaux sortait cyan. Une
section dont les seuls candidats sont des cartes de détail partagées reste de couleur unie.

**Palettes.** Les bâtiments d'un arrière-plan prennent leurs couleurs dans une palette de 256 x 256 texels de
pastilles de 16 x 16 : chaque sommet porte quatre octets (usage `0x1E`) dont les deux premiers indiquent où
se trouve sa couleur dans la palette, x et y sur 255. `level` dessine une telle section avec la palette comme
texture, chaque sommet au centre de sa pastille. Ainsi dessinés, les blocs d'arrière-plan d'un niveau sortent
en murs pastel, terre cuite et fenêtres sombres là où ils étaient blancs unis.

**Superpositions.** Les grands objets font une mosaïque de feuille de finition par leurs premières coordonnées
de texture, et posent une superposition par-dessus à travers la seconde, qui se trouve dans 0 à 1 : un dépliage
de l'objet entier. La superposition (`..._overlay_cs`, avec son masque `..._overlay_a`) porte ce à quoi
ressemble l'objet de loin, les bandes rouges et la rouille d'un réservoir d'huile ; dessinés avec la seule feuille
de finition, les réservoirs d'un niveau sortaient en panneaux gris. Une section dont le bloc nomme une
superposition avec son masque, et dont les secondes coordonnées sont un tel dépliage, est dessinée avec la
superposition à travers elles (36 sections dans ce niveau).

**Teintes.** Beaucoup de cartes de couleur sont grises (leurs moyennes de canaux à 6 % près les unes des autres) :
le shader les peint avec des couleurs prises dans les paramètres du bloc. Après ses entrées de texture (49 octets
chacune), un bloc liste ses paramètres, chacun avec une étiquette de type (`f11af825` un float3, `a5e1f2de` un
float4, `c1b1a014` un float, `4a4fc3a1` un entier), les octets d'indicateurs `01 80` pour une seule valeur, un
hachage de deux octets du nom du paramètre, un compte u32, la valeur et un identifiant de huit octets. Les noms
ne sont pas stockés. Sept hachages de noms de float3 agissent comme des teintes : dans un niveau, trois d'entre
eux portent une couleur dans environ 1 bloc sur 6 dont la carte est grise et presque jamais là où la carte a sa
propre couleur, et les autres portent les couleurs dont une carte grise est peinte quand le nom du matériau
l'indique (le liseré `..._blue` d'un pont : 0,047, 0,098, 0,171 contre un 0,5 neutre). Une famille peut contenir
plusieurs valeurs, une par canal d'un masque, la plupart neutres ; et une valeur dont un canal est presque nul
(vert pur sur les façades de briques) choisit un canal du masque au lieu de peindre. `level` multiplie une carte
de couleur grise, en lumière linéaire, par la première valeur de chaque famille qui n'est ni neutre ni un tel
sélecteur, par rapport à sa valeur neutre, et garde le résultat comme texture propre ; une carte qui a de la
couleur est laissée telle quelle. La règle est celle de l'exporteur : quel canal d'un masque reçoit quelle teinte
n'est pas lu. Dans un niveau, elle a fait passer la part des triangles de structure dessinés près de blanc de
19,4 % à 3,9 %.

**Variations d'objet.** Un maillage est placé dans plusieurs apparences : un mur d'entrepôt avec une bande rouge
ou bleue et un numéro différent peint dessus, un conteneur en vert ou en gris. Chaque copie placée nomme son
apparence :

| Où | Champ |
|---|---|
| membre de groupe de modèles statiques | +32 : un tableau d'un pointeur par copie, vers une variation d'objet ou nul |
| référence d'objet | +120 : un pointeur vers une variation d'objet ou nul |
| variation d'objet (partition `ov_...`, type `235f2a9c...`) | sa première instance +32 : le hachage de nom u32 de la variation |

L'apparence d'une section dans une variation est le bloc de shader indexé par la clé propre de la section,
avec le hachage de la variation ajouté à ses quatre premiers octets, en u32 little-endian
(`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`) ; une section sans bloc sous cette clé a la même
apparence dans chaque variation. Les bases de données de variations de maillages du niveau
(`meshvariationdb_win32`) listent, par maillage et par hachage de variation, les matériaux que chaque variation
touche, mais non les clés : la règle a été trouvée à partir des clés elles-mêmes et tient pour chaque section à
variantes vérifiée (les quatre variations d'un mur, trois de ses sections chacune). Le bloc d'une variation apporte
ses propres textures autant que ses teintes : le numéro peint sur le mur est une feuille de lettres que nomme le
bloc de la variation. Une grande part des copies groupées sont placées dans une variation.

Un bloc est cuit une fois pour chaque ensemble de contenus, et l'entrée du dépôt pour une clé porte un hachage
de ceux-ci (le second u64 de l'entrée). Quand une section n'a pas de bloc sous la clé de sa variation, la variation
l'atteint quand même par un *jumeau* : une autre section dont le bloc par défaut a le même contenu et en possède
un. Sans jumeaux, un mur dont les longueurs partagent un même bloc par défaut peut sortir en deux couleurs. Une
section sans variante propre prend la variante que la plupart de ses jumeaux ont.

**Maillages destructibles.** Un maillage qu'un match peut abattre a à côté de lui un élément de destruction de
son propre nom (`.../br_x.destruction` pour `.../br_x_mesh`) : les bâtiments et murs cassables (`br_`) et de
nombreux accessoires. `level` garde leurs surfaces dans des parties à part, nommées ` (destructible)`, dont les
nœuds glTF portent `{"destructible": true}`. Leurs états détruits sont les maillages `dc_..._part<N>_mesh` à côté
d'eux, chacun centré sur sa propre origine ; l'endroit où se pose chaque morceau est dans l'élément de destruction,
qui n'est pas lu, donc les états détruits ne sont pas exportés.

**Laissé de côté.** Les sections de matériaux de maquette provisoire (`M_Whitebox` : quelques grands triangles
sans texture que certains bâtiments gardent à côté de leurs surfaces, qui dépassaient d'un niveau en ailerons
blancs), les maillages faits pour les cinématiques (un hélicoptère placé là où débute sa scène) et les aides
d'éclairage (plans qui bloquent la lumière, jamais dessinés). Les bâtiments d'arrière-plan générés d'un niveau
(`..._generated_blueprints_..._mesh`) sont dessinés, mais leurs murs ne nomment que des cartes de bruit et leurs
sommets ne portent aucune couleur : ils restent unis. Presque chaque section dessinée reçoit une carte de couleur.

**Feuilles de lettres.** Le numéro peint sur un mur ou l'impression d'un panneau d'une grue est une section à part
dont la carte de couleur est une feuille (`_ca`) : l'alpha d'une lettre sur de la peinture pleine, ou une impression.
Ses premières coordonnées de texture font une mosaïque du crépi du mur sur le panneau (u -0,2 à 1,7 sur un mur), ce
qui dessine presque deux fois la feuille ; le quatrième jeu (`0x24`, sinon le troisième, `0x23`) la pose exactement
une fois (u -1 à 0, v 1 à 2, quelques millièmes en trop dans les niveaux de détail plus grossiers). Quand le premier
jeu laisse une copie de l'image et que le quatrième ou le troisième tient dans une, la feuille est dessinée à travers
celui-ci, déplacée dans 0 à 1. Une feuille avec alpha est dessinée à 1 cm devant la surface sur laquelle elle est
peinte, qui est dessinée dessous dans l'autre carte de couleur du bloc à travers le premier jeu : sans cela, les
texels vides de la feuille montraient l'intérieur du mur. Le second jeu est le dépliage d'un objet pour sa
superposition et n'est pas utilisé ici.

**Cartes de découpe.** Le quatrième canal de la carte de couleur signifie des choses différentes selon le nom de
la carte. Dans `_cs`, de loin le plus courant (893 des cartes choisies d'un niveau), c'est le lissé : 1 % de l'alpha
d'une carte médiane se trouve à 0,1 près de 0 ou 1. Dans `_cu` (feuilles, herbe) et `_ca` (couleur et alpha), c'est
l'opacité : 90 % et 87 %. Une carte de couleur nommée `..._cu` ou `..._ca` dont l'alpha est à au moins 75 % près de
0 ou 1, à au moins 1 % sous 0,5 et à au moins 5 % au-dessus, est écrite avec son alpha, en PNG, et son matériau en
glTF `alphaMode` MASK, `alphaCutoff` 0,5, double face ; les cartes de feuilles montrent alors des feuilles, non leurs
coins noirs. La carte de feuilles d'un arbre n'a aucun alpha (4 sur 255 au plus) : ses frondes sont découpées par la
géométrie, et avec seulement les deux premières conditions, toute la couronne était coupée.

Les coordonnées de texture sont l'usage de sommet `0x21`, deux demi-flottants (format 6) ou deux flottants
(format 2). Les sections portent jusqu'à trois autres jeux (`0x22` à `0x24`) pour les couches de décalcomanie et de
détail. Les coordonnées se répètent en mosaïque : le côté nervuré d'un conteneur va de -1,6 à 1,8, les tuiles du
décor de terrain sont entièrement hors de 0..1, et dans un niveau 23 % des triangles texturés atteignent hors de 0..1.
Elles sont écrites telles quelles, avec un échantillonneur qui répète ; la visionneuse 3DHeat enroule chaque texture
répétée dans son atlas. Un moteur qui les bride à la place étire les nervures au double de leur largeur, transforme un
sol de béton en traînées le long d'un axe, et donne aux poutres d'acier d'une tour la couleur du bord de leur texture ;
pour lui, `--clamped-uvs` découpe chaque triangle le long des lignes où sa texture se répète et déplace chaque morceau
dans 0..1 (voir [Format de sortie](output-format.md)). Ensuite, 0,03 % des triangles texturés, sur lesquels une texture se
répète plus de 16 fois, atteignent hors de 0..1, et un triangle que la découpe rendrait en plus de 4 morceaux est dessiné
dans la couleur moyenne de sa texture à la place : l'écorce se répète sur chaque branche, et découpés, les arbres d'un
niveau sont passés de 6,4 à 24 millions de triangles.

Le champ de hauteurs n'a pas de carte de couleur propre qui puisse être lue. Là où l'une des cartes du décor de terrain
le couvre, il est coloré par elle : les coordonnées de texture du décor sont une fonction linéaire de x et z du monde
(99 % de ses sommets à 0,001 près de celle-ci ; la carte couvre un carré de 65 536 m, tourné d'un quart), et la même
fonction donne celles du champ de hauteurs. Le niveau livre les mips de cette carte à partir de 2 048 px, si bien que
le champ de hauteurs a 32 m par pixel. Sa roche sombre se trouve sur le sol pentu : la corrélation entre l'obscurité et
la pente est de 0,48, et au plus 0,34 pour les sept autres orientations.

Le décor d'un autre niveau est constitué de huit tuiles proches et huit lointaines autour de la zone de jeu, chacune
répétant sa propre texture à travers la tuile, et aucune n'atteint le champ de hauteurs. Chaque texture de décor est
ajustée séparément, et quand aucune ne couvre le champ de hauteurs, il prend la couleur moyenne que le décor montre à
moins d'un kilomètre du carré de terrain, dans laquelle `--ground-texture` cuit les décalcomanies. Un matériau de décor
est celui dont le nom contient `TerrainBackdrop`, ou `BD_` et `Terrain` (`M_BD_<site>_Terrain..._Near`) ; ou un maillage
de décor (`bd_..._terrain<site>_04_far_mesh`) porte un matériau de terrain simple (`M_<region>_Terrain<site>_04_Far`),
que les deux premières règles ont manqué dans un niveau, et qui colorait donc son sol à partir de ses surfaces.

Quand aucune carte de décor ne couvre le champ de hauteurs, celui-ci prend pourtant la couleur médiane des surfaces
propres du terrain avant la moyenne du décor : les cartes de couleur `_cv` que nomment les blocs de shader de son
graphe de couches (27 dans un niveau : sables, graviers, terres, herbe, béton fissuré), chacune moyennée, puis la
médiane de chaque canal, en laissant de côté la surface par défaut du moteur. Un décor peut être un tout autre paysage :
dans un niveau, sa moyenne (95, 99, 80 en sRGB) donnait au sol de la zone de jeu un gris que le jeu ne montre pas. Avec
`--ground-texture`, cette couleur est multipliée par le double de la carte de couleur, ce qui laisse un gris moyen tel
quel, et cuite avec les décalcomanies par-dessus, sur l'étendue des décalcomanies et de la carte de couleur.

Face au jeu, la couleur médiane du sol de la zone de jeu cuite de chaque niveau et celle des images de jeu (lignes à
55 à 72 % de l'image à côté de l'ATH, 24 images chacun ; sRGB ; les images sont éclairées et étalonnées, donc les rapports
r/g et b/g sont la comparaison juste) :

| Niveau | Images | Moyenne du décor | Maintenant |
|---|---|---|---|
| premier | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| deuxième | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| troisième | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Le premier est corrigé ; les deux autres étaient un peu plus proches en teinte avant. Une seule couleur pour tout un
niveau ne peut pas être juste partout ; les masques, eux, le seraient.

## Maillage de navigation {#navigation-mesh}

Source : [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Un niveau livre une partition par agent, `<level>/dbt/<level>_navmesh_layer_<n>` : dans un niveau, la couche 0 est le
soldat (1,8 m de haut, marche de 0,18 m, rayon de 0,4 m) et deux autres sont des véhicules (3,5 et 10 m de haut). Chaque
partition contient deux tableaux :

| Tableau | Élément |
|---|---|
| tuiles | 28 octets : u32 0, u32 hachage, u32 0, u32 index de morceau, u16 x de tuile, u16 z de tuile, u32 décalage, u32 taille |
| morceaux | 20 octets : le GUID du morceau, u32 taille |

Une tuile occupe `size` octets à `offset` dans le morceau d'index `chunk index`, en little-endian, et son
agencement suit celui de Detour (Recast Navigation) derrière un en-tête plus long :

| Décalage | Contenu |
|---|---|
| 0 | `VAND`, version 7 |
| 24 | comptes : polygones, sommets, liens, maillages de détail, sommets de détail, triangles de détail, nœuds de volume englobant, liens hors maillage, le premier polygone hors maillage |
| 188 | hauteur, marche et rayon de l'agent |
| 200 | la boîte englobante de la tuile, six flottants |
| 232 | sommets : flottants x, y, z, coordonnées du monde |
| au prochain multiple de 8 octets | polygones, 32 octets : u32, six index de sommets u16, six voisins u16, indicateur u16, le nombre de sommets à +30, à +31 l'aire (six bits de poids faible) et le genre (deux de poids fort) |
| puis, compactés | liens (16 octets), maillages de détail (12 : premier sommet de détail u32, premier triangle de détail u32, nombre de sommets et de triangles u8), sommets de détail (trois flottants), triangles de détail (trois index et indicateurs), nœuds de volume englobant (16), liens hors maillage (80) |

Dans chaque tuile des niveaux vérifiés, ces éléments donnent la taille de la tuile à l'octet près, et les maillages de
détail numérotent les polygones avant le premier hors maillage.

Un polygone est plat entre ses coins ; son **maillage de détail** contient la hauteur réelle de la surface par-dessus
bosses, rochers et marches, et c'est lui qui est dessiné. Un index de triangle de détail inférieur au nombre de coins du
polygone désigne ce coin, sinon le sommet de détail `first + index - corners`. Trianguler en éventail les polygones à la
place met beaucoup plus de triangles sous le terrain et crée de longues fines lamelles ; avec les maillages de détail,
aucun n'est plus long que la diagonale d'une tuile de 16 m plus la marche d'une pente.

Le genre 0 est le sol, le genre 2 de petites plaques raides (environ 45 degrés, un mètre carré chacune), le genre 1 un
lien entre surfaces : ses coins s'étendent sur 125 m de hauteur ou plus et se trouvent hors de la tuile, certains à
l'origine. Les liens sont laissés de côté ; les autres sont dessinés par leurs maillages de détail, ou trianguler en
éventail dans une tuile qui n'en a pas.

Vérifications : les tailles des morceaux additionnent exactement celles des tuiles ; chaque sommet de surface se trouve
dans la boîte de sa tuile à un mètre près environ ; presque tous les triangles regardent vers le haut. Une tuile qui
échoue est refusée et comptée, et dans ce niveau il n'y en a aucune.

Ce que couvre le maillage du soldat, vu d'en haut dans le niveau d'essai : le sol, les planchers, les escaliers et une
partie des toits, et non le dessus des conteneurs de fret. C'est la carte qu'a l'IA des endroits où un soldat peut se
tenir, ce que les fichiers montrent de plus proche de l'endroit où se tiennent les joueurs.

## Non implémenté {#not-implemented}

- Le graphe de couches du terrain, qui mélange ses couches de surface (voir [Couches de terrain](#terrain-layers)) : la couleur du sol suit une règle propre au lecteur, d'après les masques des couches et la pente du champ de hauteurs, et les niveaux dont les pages de masques ne s'assemblent pas reçoivent une seule couleur.
- Les paramètres de couleur des matériaux de décalcomanie : les marquages par masques de canaux sont peints dans une couleur neutre.
- Les plans de bloc d'objet qui ne sont pas des maillages (logique de jeu, effets, sons).
- Les états détruits des maillages destructibles : la place de leurs morceaux se trouve dans l'élément de destruction, qui n'est pas lu.
- Les liens du maillage de navigation (sauts, échelles, franchissements) et ses couches de véhicules.
- Les niveaux de maillage stockés en ligne dans la ressource (10 maillages dans un niveau, gadgets), les os et parties des maillages squelettés et composites, et les normales (calculées par l'écrivain).
- Les cartes de normales, de rugosité et autres ; l'alpha autre que la découpe (le verre translucide et les décalcomanies sont dessinés opaques).
- Les trous du terrain : un shader de surface de trous est nommé, mais ce qu'il lit n'est pas trouvé (voir [Couches de terrain](#terrain-layers)), donc le champ de hauteurs n'est pas découpé là où le sol praticable passe dessous.
- La teinte qui va avec chaque canal du masque d'un matériau : une carte de couleur grise prend la première teinte qui n'est pas neutre (voir [Textures et matériaux](#textures-and-materials)).
- Les effets (chemins `fx/`) et les maillages de câbles, dont les boîtes englobantes font des dizaines de kilomètres de long ; ils sont laissés de côté et comptés dans le résumé.
- La forme de table obfusquée par XOR.
