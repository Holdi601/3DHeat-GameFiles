---
title: "Lecteurs d'archives"
nav_order: 9
lang: fr
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Lecteurs d'archives {#archive-readers}

Un **conteneur** (ou archive) est un gros fichier dans lequel un jeu range beaucoup
d'autres fichiers. Un **CRC** ou hash est une courte empreinte de quelques octets :
si elle correspond, les octets ont été bien lus. Une **boîte englobante** est la plus
petite boîte qui entoure un modèle.

Sous les commandes se trouvent des lecteurs pour les conteneurs que livrent les jeux.
Leur format n'est pas documenté, à part le VPK de Valve et le `.cdae` de BeamNG. Donc
« pris en charge » doit vouloir dire **vérifié sur de vrais fichiers**, et non « ne
plante pas ». Chaque lecteur se vérifie avec quelque chose que le format garantit : un
hash, un CRC, une chaîne de décalages qui doit se refermer, une boîte englobante
stockée. Quand une vérification échoue, le lecteur refuse avec un message au lieu de
deviner. Un mauvais maillage ressemble à un bon, jusqu'au moment où on le pose à côté
de la piste.

| Lecteur | Module | Lit | Ne lit pas | Atteint depuis |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versions 8 à 12 : index, entrées, blocs Zlib/Gzip/Oodle, AES avec une clé que vous fournissez | versions avant 8, index qui ne contiennent que des hash de chemins, entrées de débordement, contenu des assets | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5 et plus, vérifié en v8), paquets zen, propriétés sans version pour quelques classes de composants, maillages statiques cuits, textures, textures virtuelles en flux | conteneurs chiffrés, paquets versionnés, maillages Nanite seuls, propriétés d'autres classes | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | blocs Oodle, via une bibliothèque déjà présente sur la machine | tout ce qui n'a pas une telle bibliothèque ; elle n'est jamais fournie avec l'outil | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22 et plus (Unity 2020 à 6000), bundles `UnityFS`, maillages non compressés, y compris `.resS` | formats d'avant 2020, arbres de types intégrés, maillages compressés, toute classe sauf `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | tables `.toc` DbObject et tables de sections binaires, paquets d'installation, emplacements des morceaux, bundles intégrés et leurs manifestes, partitions RIFF EBX, maillages MeshSet, champ de hauteurs du terrain, textures BC1/BC3/BC7 et leurs blocs de shaders, placement des groupes de modèles statiques | tables brouillées par XOR, couleur du sol près du sol, trous, cartes de normales, alpha autre que les découpes | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versions 1 et 2, archives découpées, données de préchargement, contrôle CRC | assets compilés (`.vmdl_c`, `.vtex_c`), format du maillage de navigation de CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, stocké), géométrie `.modelbin`, nuanciers `.pb` (BC1, BC7, RGBA), placements `.pgeo`, hash des textures des matériaux | autres formats de sommets et d'index, autres formats de textures, couches de shaders du terrain | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` et `extract` (`.minizip`) |
| [Fichiers BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | le système de fichiers zip monté, les scènes en JSON et en TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, matériaux | maillages skinnés et de décalques, séquences animées, végétation au sol générée par procédé | `course` (BeamNG), `identify` (zips, `.cdae`, `.ter`), `list` et `extract` (zips) |

## Les règles que suit chaque lecteur {#rules-every-reader-follows}

- **Aucune clé fournie, aucune clé récupérée.** Une archive chiffrée ne s'ouvre qu'avec
  une clé que vous transmettez (`--key` pour un `.pak` Unreal). Un conteneur IoStore
  chiffré est refusé. Rien ne cherche une clé dans un exécutable, rien ne lit la
  mémoire d'un autre processus. Voir [Règles et licences](rules-and-licences.md).
- **Aucun code propriétaire inclus.** Oodle est chargé depuis un jeu ou un moteur déjà
  installé sur la machine.
- **Refuser plutôt que deviner.** Une version, un codec, un format de sommets ou de
  textures inconnu lève une erreur précise, par exemple
  `texture format 42 has not been identified; refusing to guess`.
- **Lecture seule.** Aucun lecteur n'écrit dans un dossier de jeu. Les exports vont où
  vous le dites.

## Ce que « vérifié » veut dire {#what-verified-meant}

Les chiffres de vérification cités sur ces pages viennent des docstrings des modules.
Ils ont été mesurés sur des jeux installés pendant l'écriture de chaque lecteur. Les
tests synthétiques (voir [Développement](development.md)) figent la disposition des
champs. Les tests sur jeux installés répètent certaines vérifications quand le jeu est
sur la machine, et sont sautés sinon. Les chiffres non couverts par un test n'ont pas
été revérifiés depuis.
