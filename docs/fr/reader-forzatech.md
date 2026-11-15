---
title: "ForzaTech"
nav_order: 7
lang: "fr"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech : `.minizip`, `.modelbin`, nuanciers, placements {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon tourne sur ForzaTech, le moteur de Turn 10. Ces lecteurs font passer une piste de ses
archives jusqu'à des triangles positionnés et texturés. Ils sont atteints par `course`, `courses` et
`terrain` (voir [Forza Horizon](course-forza-horizon.md)). `identify` reconnaît un `.minizip` et un
`.modelbin` seul, et `list` et `extract` prennent un `.minizip`, d'après les noms du fichier
`ChunkContentsMiniZip<n>.txt` placé à côté, ou par numéro d'entrée (`#12`).

| Format | Module |
|---|---|
| archives `.minizip` et leurs listes de noms | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modèles et terrain `.modelbin` | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| nuanciers de textures `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| fichiers de placement `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` et hash des textures des matériaux | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| tuiles de terrain par emplacement | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza garde aussi une bonne part de son contenu dans des archives ZIP ordinaires sous `media\`. Le
`zipfile` de Python les ouvre, et `forzatech.models_in_archive()` liste leurs entrées `.modelbin`. La
géométrie des pistes se trouve dans les archives `.minizip`.

## `.minizip` : une archive sans noms {#minizip-an-archive-with-no-names}

Une piste livre quatre archives `GeoChunk<n>.minizip`, de dizaines de gigaoctets chacune pour une carte en
monde ouvert, avec des centaines de milliers d'entrées. **Les archives ne stockent aucun nom** : ni table
de noms, ni en-tête par entrée, seulement un numéro d'ordre. Les noms se trouvent dans
`ChunkContentsMiniZip<n>.txt`, à côté de chaque archive, une ligne par entrée dans l'ordre des entrées
(`<build path>zipcache\pc\<path>|<bundle>`). Ce couplage est la seule façon de demander un fichier. Tout
ce qui précède `zipcache\pc\` est retiré, et les recherches ignorent la casse.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Trois détails de l'index produisent encore une sortie quand on les lit mal. Le lecteur les gère tous les trois :

| Détail | Ce que fait un lecteur négligent | À quoi cela ressemble |
|---|---|---|
| la base de segment est **64 bits** | la lit comme u32 plus du bourrage | correct pour les 4 premiers Go, puis du bruit de la bonne longueur |
| la base est **alignée sur 8 octets** | ignore le mot de bourrage après la table des bundles | dans les archives à nombre pair de bundles, chaque entrée revendique un codec qui n'existe pas |
| la longueur stockée d'une entrée est l'écart jusqu'à l'entrée suivante (ou la base du segment suivant) **moins son bourrage** (bits de drapeaux 12-13) | utilise tout l'écart | LZ4 refuse le bloc tout net |

Les codecs sont les cinq bits faibles des drapeaux : `0x00` stocké, `0x08` deflate brut, `0x1F` bloc LZ4.
Tout autre est refusé. Chaque entrée doit se décompresser exactement à la taille qu'elle déclare, ou elle
est refusée. L'index (environ 5 Mo) est lu une fois, et les charges utiles sont lues en se positionnant.

L'en-tête est contrôlé : magic, un en-tête de 32 octets, et un nombre de segments égal à
`ceil(entries / per segment)`.

**Vérifié :** des entrées échantillonnées dans chaque archive d'une carte, chacune se décompressant
exactement à sa longueur déclarée sous les trois codecs.

## `.modelbin` : le conteneur de morceaux {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- La taille de fichier déclarée doit être égale à la taille réelle.
- **La chaîne** : chaque morceau commence là où le précédent s'est terminé, arrondi à 4 octets. Rien dans le
  fichier ne l'énonce, donc c'est une preuve : un enregistrement lu avec le mauvais pas ne produit pas cela. Elle
  a tenu pour les 252 modèles échantillonnés.
- Un fichier `PGZP` donné au lecteur de modèles est nommé « a ForzaTech .minizip archive, not a model » et
  renvoyé vers `minizip.py`, au lieu d'être rejeté sans explication.

La géométrie vient de ces morceaux :

| Morceau | Contient |
|---|---|
| `VLay` | une disposition de sommets : noms d'attributs, puis éléments (indice de nom u16, canal u16, tampon, format DXGI, décalage) ; le nombre d'éléments est un u16 |
| `VerB` | un tampon de sommets derrière un en-tête de 16 octets (nombre, taille, pas u16, attributs u16, format) |
| `IndB` | le tampon d'index, même en-tête |
| `Mesh` | un sous-maillage : matériau, masque de niveau de détail, plage d'index, disposition, tampon, pas, table de variantes, et une boîte de position à la fin |
| `MatI` | une instance de matériau : son chemin `.materialbin` et ses hash de textures |

### Positions et boîte {#positions-and-the-box}

Les positions sont `R16G16B16A16_SNORM` (format 13) : quatre shorts signés par sommet.
`position = short / 32767 * scale + bias`, où scale et bias sont les 32 derniers octets du morceau `Mesh`
(deux float4). Le biais est dans **les coordonnées monde du jeu**, donc une tuile de terrain tombe là où le
jeu la place sans transformation d'instance. C'est pourquoi un tour de télémétrie suffit pour demander un
morceau de carte. Chaque sous-maillage d'un modèle porte la même boîte (vérifié sur 860 d'entre eux).

### La disposition des sommets {#the-vertex-layout}

Un seul tampon de positions couvre chaque sommet. Les autres attributs sont répartis en groupes de sommets
consécutifs, chacun avec son propre tampon et sa propre disposition : la route près d'un carrefour porte trois
jeux d'UV et deux tangentes, le talus à côté seulement une normale. Chaque attribut non positionnel fait quatre
octets. Quelle disposition décrit quel tampon se déduit des sous-maillages qui dessinent depuis ce tampon, car
dispositions et tampons ne sont pas dans le même ordre (identique, décalé d'un cran, ou permuté, selon le modèle).

| Format DXGI | Code | Utilisé pour |
|---|---|---|
| R16G16B16A16_SNORM | 13 | position (le quatrième short est le x de la normale) |
| R16G16_SNORM | 37 | normale y, z |
| R16G16_UNORM | 35 | une paire d'UV (canal = quel jeu) |
| R8G8B8A8_UNORM | 28 | couleur ou poids de mélange |
| R10G10B10A2_UNORM | 24 | tangente (non décodée) |
| R16_UINT | 57 | indices |

**La normale est coupée en deux.** `NORMAL` contient y et z. Le x est le quatrième short de la position, qui
ressemblait à du bourrage. Sur des centaines de milliers de sommets de terrain, il est corrélé à +0,92 avec le x
de la normale du triangle, et à rien d'autre. Avec lui, 96 % des sommets de sol en pente sont à moins de 18° de
la normale calculée. Chaque codage à deux composantes essayé sans lui (octaédrique dans les 48 arrangements
compris) donnait juste y et z, et faux x.

Les autres formats de position ou d'index sont **refusés** (« only 13 (four shorts, scaled) is implemented » ;
« only unsigned shorts are implemented »).

### Sous-maillages {#submeshes}

Un enregistrement `Mesh` fait 238 octets sous sa forme standard. Les plus longs portent en tête une table de
**variantes** de matériau plus longue, de 238 + 8 x nombre - 4 octets, et chaque champ suivant recule exactement
de ce montant. Les plus courts (218 octets, certains terrains) gardent leurs décalages. Chaque entrée de variante
est `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. Le masque de niveau de détail est un u16,
un bit par niveau à partir du bit 1.

Rien n'est cru sur parole. Les plages d'index doivent recouvrir exactement le tampon d'index, chaque `index count`
doit valoir 3 x `triangles`, et le pas qu'un sous-maillage nomme doit être celui de son tampon. Une table qui échoue
est refusée en bloc, car étiqueter des triangles à partir de champs mal lus vaut pire que ne pas étiqueter. Sur des
milliers de sous-maillages échantillonnés, chacun dont l'indice de tampon est dans l'intervalle passe.

### Matériaux et hash de textures {#materials-and-texture-hashes}

Un `MatI` nomme son matériau par un chemin `Game:...\x.materialbin`, trouvé en cherchant dans le morceau. Ses
textures sont des enregistrements `u32 slot, u32, u32 hash`, espacés de 33 octets et non alignés, donc le morceau
est fouillé à chaque décalage d'octet pour trouver les mots qui sont des hash de textures connus. Ceux-ci viennent
du `AssetManifest.xml` de la piste (`<Texture Source="...\name.swatch" SourceHash="...">`, lu jusqu'à
`</Textures>`). L'emplacement `0x88B483AA` est la couleur de base du shader standard. Le choix de la texture de
couleur est décrit dans [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb` : nuanciers de textures {#pb-texture-swatches}

Un nuancier est le même conteneur `burG` qu'un modèle : un en-tête `HCXT` de 96 octets à l'octet 44, puis un
morceau de pixels. L'en-tête contient le GUID de la texture (celui de son nom de fichier), la largeur et la
hauteur, le nombre de mips, et le **code de format à l'octet 72** (numérotation propre à ForzaTech). L'octet 84
contient le nombre d'octets de pixels.

| Code | Format | Identifié comme |
|---|---|---|
| 0 | BC1, un demi-octet par pixel | se décode en bordure rouge et blanche (du bruit sous BC4) |
| 9 | BC7, un octet par pixel | se décode en tuile de terrain où le circuit est visible |
| 13 | RGBA8, quatre octets par pixel | simple |
| autre | refusé | « texture format N has not been identified; refusing to guess » |

Les formats ont été identifiés en décodant de vrais fichiers de toutes les manières que permet la taille de la
charge utile. L'octet 47, qu'une version antérieure prenait pour le format, vaut 4 dans toutes les textures
échantillonnées. Seul le mip supérieur d'un fichier est décodé. Chaque résolution est une entrée à part,
`<name>_<guid>_quality<n>.pb`, de la qualité 1 (la plus petite) à 5 (la plus grande). Pour les cartes de terrain,
les deux plus grandes sont dans une archive différente du reste. Le décodage passe par le décodeur BCn de Pillow,
via un en-tête DDS généré.

## Fichiers de placement (.pgeo) {#placement-files-pgeo}

Un fichier par catégorie et par cellule spatiale :
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Le chemin seul donne le carré de la cellule et
la catégorie, donc les fichiers peuvent être filtrés sans être ouverts.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Comment chaque champ a été décidé :

| Champ | Décidé par |
|---|---|
| la position est en virgule fixe 16.16, non une fraction de la boîte | les glissières consécutives sont exactement à 4,000 m d'écart (la longueur du modèle) |
| signe-grandeur, non complément à deux | le complément à deux plaçait les coordonnées négatives à des dizaines de kilomètres de la carte ; avec le bit 31 comme signe, chaque enregistrement de chaque catégorie échantillonnée tombe dans la boîte de son fichier |
| les vecteurs sont les axes propres du modèle | la fin de chaque glissière tombe sur le début de la suivante : 93,5 % à moins de 5 cm, médiane 0,000 m |
| l'octet 60 est la variante | les cinq copies d'un panneau-billboard valent 0, 2, 2, 3, 4 tandis que chaque glissière vaut 0 |

Seuls les noms finissant par `_3D` sont des enregistrements de modèle. La table de variantes qui les précède liste
des noms sans ce suffixe, et lus comme enregistrements, ceux-ci tombent à l'infini. Un enregistrement candidat n'est
accepté que si son nombre tient dans le fichier, et les instances aux nombres non finis sont supprimées.

## Non implémenté {#not-implemented}

- Formats de sommets et d'index autres que ceux ci-dessus (refusés).
- Formats de textures autres que 0, 9, 13 (refusés).
- Tangentes (lues et sautées, non utilisées).
- Les couches de matériaux du shader du terrain. La texture de sol est une interprétation des cartes de
  tuiles (voir [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
