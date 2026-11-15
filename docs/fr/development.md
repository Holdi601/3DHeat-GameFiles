---
title: "Développement"
nav_order: 14
lang: "fr"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Développement {#development}

## Organisation {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Carte des modules {#module-map}

| Module | Ce qu'il fait |
|---|---|
| `__main__.py` | lance la vérification de mise à jour, puis `cli.main()` |
| `cli.py` | les verbes, `identify`, l'aiguillage des archives, l'écrivain de parcours Forza |
| `lapinput.py` | chaque forme de tour en positions ; recherche dans la bibliothèque FH Companion |
| `corridor.py` | la bande de part et d'autre de la conduite, en raster de 4 m |
| `surfaces.py` | les natures de sol, leurs noms de parties et leurs couleurs |
| `glb.py` | l'écrivain `.glb` (parties, normales, couleurs, textures, quantification) |
| `courseexport.py` | Forza : UV de tuiles planes, séparation route/accotement, cuisson du sol, relevé des décalques |
| `forzainstall.py` | bibliothèques Steam et Xbox ; la piste Forza à laquelle appartient une boîte |
| `minizip.py` | archives ForzaTech `.minizip` et leurs listes de noms |
| `forzatech.py` | `.modelbin` : morceaux, tampons, dispositions, sous-maillages, matériaux |
| `forzaterrain.py` | tuiles de terrain par emplacement ; classes de surface |
| `forzatexture.py` | nuanciers `.pb` ; cartes de tuiles ; la cuisson du sol |
| `forzamaterial.py` | `AssetManifest.xml` ; quelles couleurs de texture un modèle utilise ; saisons |
| `forzaplacement.py` | placements `.pgeo`, niveaux des modèles, textures, découpes, substitutions, budget |
| `beamng.py` | installation BeamNG, système de fichiers monté, scène, terrain, matériaux |
| `beamngcourse.py` | l'export de parcours BeamNG |
| `beamngshape.py` | formes compilées `.cdae` |
| `beamngcollada.py` | repli `.dae` |
| `acrally.py` | installation AC Rally, étapes, placement des composants, volume de texture virtuelle |
| `acrallycourse.py` | l'export de parcours AC Rally : ajustement du repère, sol, placement |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | paquets Unreal 5 cuits |
| `unversioned.py` | schémas et lecteur des propriétés sans version |
| `unrealmesh.py` | maillages statiques cuits |
| `unrealtexture.py` | textures et textures virtuelles en flux |
| `oodle.py` | recherche et appel d'une bibliothèque Oodle installée |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | conteneurs, bundles et maillages Unity |
| `frostbite.py` | `.toc` Frostbite, tables de sections, paquets d'installation, emplacements des morceaux, charges utiles |
| `frostbitebundle.py` | bundles Frostbite intégrés, manifestes de bundles, catalogue d'un niveau, liste des niveaux |
| `frostbiteebx.py` | partitions RIFF EBX Frostbite sans bibliothèque de types |
| `frostbitemesh.py` | MeshSet Frostbite et ses morceaux de niveaux de détail |
| `frostbiteterrain.py` | arbre de streaming du terrain Frostbite, pages de hauteur, maillage du sol |
| `frostbitematerial.py` | textures Frostbite (mips BC1/BC3/BC7), dépôts de blocs de shaders, choix de la carte de couleur |
| `frostbitedecals.py` | décalques de terrain Frostbite et cuisson du sol |
| `frostbitenav.py` | tuiles de maillage de navigation Frostbite : les surfaces praticables par les soldats |
| `frostbitelevel.py` | groupes de modèles statiques Frostbite, placement, l'export `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | composants de paysage Unreal 5 : cartes de hauteur vers le maillage du sol (`ue-map`) |
| `unreallevel.py` | cartes World Partition Unreal 5 : liste, structures HLOD, eau, export `ue-map` |
| `enfusion.py` | `.pak` Enfusion, `.edds`, tuiles de terrain, `resourceDatabase.rdb` |
| `enfusionworld.py` | mondes Arma Reforger : fichiers `.ent`, boîtes, export `enfusion-world` |
| `forzacars.py` | chaque voiture Forza à faible détail dans `.h3dcars` (`cars`) |

Tous les modules sont sur GitHub, dans
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Lancer les tests {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` règle `testpaths = tests` et `-q`. Deux sortes de tests comptent, pour des
raisons différentes :

- **Les tests synthétiques** construisent des archives octet par octet et tournent partout.
  Ils figent les dispositions de champs qui ont été fausses à un moment : la base 64 bits du
  segment `.minizip` et son bourrage d'alignement, l'échappement de taille de bloc du pak, le
  u32 de l'en-tête Unity entre deux int64, l'index `0x7FFF` du VPK, la coupure x de la normale
  Forza.
- **Les tests sur jeux installés** tournent sur les vrais fichiers quand le jeu est sur la
  machine, et **sont sautés** (ils n'échouent pas) quand il n'y est pas. Ce sont les seuls à
  attraper une disposition juste pour un petit fichier et fausse pour un gros.

### Jeux de test (fixtures) {#fixtures}

| Fixture | Construit |
|---|---|
| `tests/forza_fixtures.py` | archives `.minizip` (avec la base 64 bits, le bourrage, des codecs mélangés), manifestes, modèles et terrain `.modelbin`, nuanciers `.pb` |
| `tests/beamng_fixtures.py` | une petite installation BeamNG : `gameengine.zip`, `content`, un zip de niveau avec un terrain de 64 m, une bande d'asphalte, un décalque de route, une rail, un préfab, un élément de forêt, la mer, des matériaux, et des formes `.cdae` dans la disposition documentée |
| `tests/unreal_fixtures.py` | un conteneur IoStore avec un répertoire, un paquet zen, un bloc de propriétés sans version |
| `tests/frostbite_fixtures.py` | tables, bundles, partitions EBX, maillages et pages de terrain Frostbite, octet par octet |

### Fichiers de test {#test-files}

| Fichier | Couvre |
|---|---|
| `test_minizip.py` | relecture, base 64 bits, tables de bundles paires et impaires, refus, le fichier de noms |
| `test_forzatech.py` | la table et la chaîne des morceaux, refus ; installé : chaînes et étiquettes de vrais modèles |
| `test_forza_geometry.py` | placement dans le monde, disposition des sommets, formats refusés, sous-maillages, normales et UV |
| `test_forzaterrain.py` | la grille de tuiles (1023 contre 512 m), le découpage, l'extraction |
| `test_forzatexture.py` | en-tête de nuancier, décodage, l'étagère de textures, la cuisson du sol |
| `test_forzamaterial.py` | le manifeste, les noms, les hash de matériaux, le choix de couleur, les saisons |
| `test_forzaplacement.py` | l'enregistrement `.pgeo`, le placement des copies, les niveaux, les variantes, les surfaces transparentes, une boîte entière, le budget, la couleur de substitution, le budget automatique ; installé : bordures au sol |
| `test_forzainstall.py` | trouver le jeu, choisir la piste |
| `test_courseexport.py` | UV de tuiles, plan des parties, relevé des décalques |
| `test_course_cli.py` | les verbes complets `course` et `courses` sur une piste synthétique ; `terrain --route` avec une marque d'ordre d'octets, et sans `bounds` |
| `test_archive_cli.py` | `identify`, `list` et `extract` sur chaque archive avec un lecteur (`.pak`, IoStore, `.vpk`, `.minizip` avec et sans ses noms, zip, `.cdae`, `.ter`) ; échecs sur une ligne et code de sortie : un pak chiffré, un conteneur chiffré, un fichier qui n'est pas une archive, une mauvaise `--key` |
| `test_corridor.py` | la bande, la découpe du terrain avec elle |
| `test_lapinput.py` | chaque forme de tour, la boîte, les échecs, la recherche par nom de parcours, quel jeu est un dossier |
| `test_surfaces.py` | quels noms décident d'une surface, lesquels non, les noms de parties |
| `test_glb.py` | le fichier est valide, les nœuds portent la classe, refus, quantification |
| `test_beamng.py` | formes, niveau, catégories, trouver le niveau à partir d'un tour, le parcours, le repli Collada ; installé : `.cdae` contre `.dae`, chaque niveau s'ouvre |
| `test_acrally.py` | conteneurs, paquets, propriétés, transformations, ajustement du repère, parties des modèles placés et budget, textures virtuelles ; installé : étapes et couleur de sol cuite |
| `test_pak.py` | pied de page, entrées, échappement de taille de bloc, refus ; installé : décalages et SHA-1 |
| `test_unity.py` | refus ; installé : la table d'objets recouvre le fichier, chaînes de version, limites des maillages |
| `test_frostbite.py` | en-têtes signés contre brouillés, refus, paquets d'installation (deux paquets avec le même numéro de blob) ; installé : chaque table, superbundles, chaînes de sections, identifiants distincts, charges utiles échantillonnées du bon paquet |
| `test_frostbitelevel.py` | identifiants de morceaux appariés à leurs propres emplacements, bundles intégrés, manifestes, un MeshSet avec une section d'ombre et des UV, un membre de groupe, la convention de transformation, un terrain à deux niveaux, choix de carte de couleur, un morceau de texture sans ses plus grands mips, l'échantillonneur répétitif, enregistrements de décalques, un décalque composé par son alpha, une feuille de décalque cédant à la carte propre d'une surface, des pages de masque (BC4 et non compressées) placées sur leurs quadrants et refusées quand leurs bords ne concordent pas, des pages de colormap placées sur leurs quadrants et retrouvées après les pages de masque que l'arbre de masques compte, des champs de distance, des palettes et des masques de canaux jamais pris pour de la couleur, la teinte d'un bloc et une carte grise peinte avec elle, un sommet de palette au centre de son nuancier, la grille de pente redistribuée en bilinéaire, le surimpression d'un objet tracée à travers son dépliage, une variante dont le bloc est repéré par son hash et atteint par un bloc jumeau, une feuille de lettres posée par ses quatrièmes coordonnées de texture sur la surface qu'elle peint, la peinture d'un décalque lue dans son matériau et les lignes de piste et traces de pneus dessinées, des cartes à un seul canal décodées, des maillages destructibles marqués dans leurs parties et extras, les maillages de blockout, cinématiques et d'éclairage laissés de côté et une disposition de colormap non lue, des cartes de découpe et leurs parties masquées, des matériaux PNG bifaces, des tuiles de fond nommées par leur maillage ; installé : les décalques de terrain du niveau, le catalogue du plus grand niveau, des maillages dans leurs limites, des membres de groupe, la végétation posée sur le terrain décodé |
| `test_vpk.py` | le répertoire, les refus, les archives découpées ; installé : les cartes s'ouvrent, les CRC correspondent, le maillage de navigation |
| `test_enfusion.py` | `.pak` Enfusion, `.edds`, tuiles de terrain et fichiers de monde ; l'export `enfusion-world` |
| `test_forzacars.py` | le fichier `.h3dcars` qu'écrit le verbe `cars` |
| `test_unreallevel.py` | paysages Unreal 5, structures HLOD, eau ; l'export `ue-map` |

## Tests sur jeux installés {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
trouve les jeux pour les tests. `steam_common()` liste le `steamapps\common` de chaque
bibliothèque Steam (y compris les dossiers propres à Steam), et `installed(*globs)` renvoie
les chemins qui correspondent à l'un des motifs sous ces dossiers, récursivement quand un
motif contient `**`. Chaque test décide de ce dont il a besoin :

| Test | Cherche | Saute avec |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` avec un index **non chiffré**, jusqu'à 4 | « no shipped pak on this machine » |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` dans `*/*_Data` ou `*/*/*_Data` que le lecteur accepte, jusqu'à 6 | « no Unity game on this machine » |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | « no Frostbite game on this machine » |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | « no Frostbite level on this machine » |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, jusqu'à 6 | « Counter-Strike 2 is not installed » |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | « no Forza install on this machine » |
| `test_forzaplacement.py` | les circuits de la bibliothèque de tours FH Companion (départ et arrivée à 50 m près), ceux qui ont le plus de tours, que `find_track` place ; ou `HEAT3D_COURSE` | « no Forza install with a recorded lap library here » |
| `test_beamng.py` | `find_install()` | « BeamNG.drive is not installed » |
| `test_acrally.py` | `find_paks()` | « Assetto Corsa Rally is not installed » |

Lancer seulement les tests d'un jeu, ou faire pointer le test de bordure Forza vers un parcours :

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Les tests sur jeux installés ne font que lire les jeux. Ils n'écrivent rien dans les dossiers
de jeu. Les sorties de test vont dans les dossiers temporaires de pytest.

## Conventions {#conventions}

- **Refuser plutôt que deviner.** Chaque lecteur lève sa propre exception (`UnsupportedPak`,
  `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`,
  `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) avec un message qui dit ce qui a été
  trouvé et pourquoi ce n'a pas été lu.
- **Vérifier contre le format lui-même.** Un hash, un CRC, une chaîne de décalages, une boîte
  englobante stockée, la conduite posée sur le sol. Pas « ça n'a pas planté ».
- **Pas de clés, pas de code propriétaire inclus.** Voir [Règles et licences](rules-and-licences.md).
- **Les données confidentielles restent dehors.** Fichiers de jeu, exports, tours,
  enregistrements et captures d'écran ne vont jamais dans le dépôt. `.gitignore` les exclut par
  dossier et par type. Les tests utilisent des données synthétiques et des jeux installés, jamais
  du contenu de jeu versionné.
