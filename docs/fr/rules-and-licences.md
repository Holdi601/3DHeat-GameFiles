---
title: "Règles et licences"
nav_order: 12
lang: fr
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Règles et licences {#rules-and-licences}

Trois règles façonnent tout l'outil. Ce sont des choix de conception, non de simples avertissements. Texte
complet : [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md). Cette page
consigne ce que disent les licences, elle ne constitue pas un avis juridique.

## 1. Aucune clé : aucune fournie, aucune récupérée {#1-no-keys-none-shipped-none-recovered}

**Il lit les conteneurs.** Analyser un format de conteneur est du traitement de fichiers ordinaire, et FModel,
UModel et AssetRipper le font ouvertement depuis des années. Analyser un conteneur n'est pas en soi un contournement.

**La ligne qui compte est le chiffrement, et elle est tracée à l'intérieur de l'outil.** Un outil dont le but est de
déjouer un contrôle d'accès relève lui-même du droit anti-contournement (le DMCA §1201(a)(2) vise les technologies, et
pas seulement les actes), même si personne ne distribue un seul fichier extrait. Donc :

- **Aucune clé intégrée.** Il n'y a aucune clé dans le code ni dans les données.
- **Aucune récupération de clé.** Rien ne cherche une clé dans un exécutable, et rien ne lit la mémoire d'un autre
  processus.
- **Une clé que vous détenez, ou rien.** Un `.pak` Unreal chiffré ne s'ouvre qu'avec `--key <hex>` (en Python,
  `PakArchive(path, aes_key=...)`). `pak.py` n'a aucun chemin de code qui obtienne une clé. Un conteneur IoStore
  chiffré est refusé d'emblée.
- **L'obfuscation n'est pas non plus implémentée.** Les tables Frostbite brouillées par XOR gardent leur clé dans le
  fichier lui-même : c'est de l'obfuscation plutôt qu'un contrôle d'accès. Elles sont tout de même détectées et
  refusées, car aucun fichier disponible n'utilise cette forme et il n'y aurait rien pour vérifier une implémentation.
  Le paquet à clé d'Assetto Corsa EVO est refusé pour la même raison que la règle des clés existe.
- **Les fichiers chiffrés restent fermés.** Le système de fichiers initial de Battlefield 6, qui contient la bibliothèque
  de types du jeu, est chiffré et n'est pas lu. L'export de niveau travaille à partir des fichiers non chiffrés, et
  établit les deux types dont il a besoin à partir des données.
- **Rien n'injecte dans un processus de jeu.** La télémétrie vient des flux que les jeux publient eux-mêmes, et la
  capture utilise les API publiques d'enregistrement d'écran (dans les autres outils 3DHeat). L'injection dans un titre
  doté d'un anti-triche met en danger le compte de celui qui l'exécute.

Chaque archive testée jusqu'ici est non chiffrée.

## 2. Vos fichiers, votre responsabilité {#2-your-own-files-your-responsibility}

L'outil lit les fichiers de jeu **installés sur votre machine**. Il ne télécharge jamais de contenu de jeu.

Ce que vous lui indiquez reste sous votre responsabilité. Les jeux ont leurs propres conditions de licence, et les
CLUF interdisent souvent la rétro-ingénierie. Ce sont des contrats opposables, et l'obligation pèse sur celui qui
exécute l'outil, quel que soit le jeu. Aucun choix de conception ici ne l'en décharge. Le cas légitime le plus clair
est celui d'un développeur qui lit le build de son propre studio : le titre d'une autre équipe, une vieille branche,
un build d'un partenaire.

## 3. Le résultat n'est pas à redistribuer {#3-output-is-not-for-redistribution}

Ce qui sort est de la géométrie pour le **contexte spatial** : le sol, la route et ce qui la borde, réduits à un
budget pour que les tours puissent être analysés sur place. C'est la part la moins importante d'une archive, et c'est
tout de même le contenu de l'éditeur du jeu.

- Gardez les `.glb` exportés, et les textures qu'ils contiennent, pour votre propre analyse.
- Ne publiez, ne partagez et ne vendez pas les parcours, niveaux, modèles ou textures exportés.
- Le `.gitignore` du dépôt tient les fichiers de jeu, exports, tours et enregistrements hors du contrôle de version,
  par dossier et par type de fichier (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` et d'autres).

## Oodle est trouvé, non fourni {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, désormais Epic) est propriétaire et n'a aucune version redistribuable. `oo2core_*.dll` est
concédé au produit qui le livre. `oodle.py` charge donc une bibliothèque déjà présente sur la machine au lieu d'en
embarquer une. C'est l'arrangement que prévoit la licence, le même que celui de FModel et UModel. Voir [Oodle](reader-oodle.md).

## Les formats eux-mêmes {#the-formats-themselves}

- `.pak`, IoStore, `SerializedFile` d'Unity, `.toc` de Frostbite et les formats de ForzaTech ne sont pas documentés.
  Les lire, c'est de la rétro-ingénierie d'un conteneur. Aucun des lecteurs ici ne dérive du code source d'un autre
  projet. Pour Frostbite, des descriptions publiques d'anciennes versions (les outils de modding Frosty, une note de
  format de Need for Speed Heat, une conférence GDC) ont fourni des noms de champs et une carte de ce qu'il faut
  chercher. Aucun code n'a été repris ; chaque décalage a été mesuré sur les fichiers (voir
  [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Les niveaux extraits sont pour votre usage personnel. L'outil les écrit sur votre disque et nulle part ailleurs ;
  ne les publiez pas.
- BeamNG publie la disposition de son `.cdae`, et le lecteur la suit.
- Valve documente le VPK.
- Les propriétés cuites d'Unreal 5 ont besoin de la liste des propriétés de chaque classe. Les listes de
  `unversioned.py` ne contiennent que **des noms et des types**, des faits sur le format, comme ceux que contient un
  fichier de correspondance d'interopérabilité. Elles ont été tirées des en-têtes d'Unreal Engine que Epic met à
  disposition de quiconque a un compte lié, et vérifiées contre les données livrées. Aucun code source du moteur n'est
  inclus ni requis.

## La licence de cet outil {#this-tools-licence}

Tout ce qui est écrit pour ce dépôt est sous **licence MIT**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)) : vous pouvez l'utiliser, le modifier,
le distribuer, à des fins commerciales ou non.

Les paquets tiers, tous permissifs, donc l'exporteur ne porte aucune restriction propre :

| Paquet | Licence | Utilisé pour |
|---|---|---|
| numpy | BSD-3-Clause | décodage des maillages |
| cryptography | Apache-2.0 / BSD-3-Clause | seulement les archives dont vous détenez une clé |
| lz4 | BSD-3-Clause | archives Forza, certains bundles Unity, blocs LZ4 d'IoStore |
| Pillow | MIT-CMU (HPND) | textures compressées par blocs, sortie JPEG |
| msgpack | Apache-2.0 | `.cdae` de BeamNG |
| zstandard | BSD-3-Clause | les rares `.cdae` compressés en zstd, blocs zstd de Frostbite |
| pytest | MIT | développement uniquement |

Les licences ont été relevées dans les métadonnées des paquets en septembre 2026. Si les conditions d'un composant ont
changé depuis, c'est la source qui fait foi.
