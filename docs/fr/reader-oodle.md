---
title: "Oodle : trouvé, non fourni"
nav_order: 3
lang: "fr"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle : trouvé, non fourni {#oodle-found-not-bundled}

La plupart des contenus Unreal livrés, et certaines charges utiles Frostbite, sont compressés avec **Oodle** (RAD Game Tools, désormais Epic). Oodle est propriétaire. Il n'existe ni version redistribuable ni implémentation Python, et `oo2core_*.dll` est sous licence du produit qui le livre. Cet outil **trouve donc une copie déjà présente sur votre machine et la charge**. Il n'en embarque jamais. FModel et UModel fonctionnent de la même façon.

Source : [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Où il cherche {#where-it-looks}

Le premier fichier qui existe l'emporte, dans cet ordre :

1. Un chemin explicite transmis par l'appelant (API Python).
2. `HEAT3D_OODLE` : un chemin vers la DLL, ou un dossier qui en contient une.
3. Une recherche superficielle, sur un seul niveau, dans
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - le `steamapps\common` de chaque bibliothèque Steam

   Pour chaque sous-dossier `<game>`, il vérifie `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` et `<game>\Engine\Binaries\Win64`.

Noms de fichiers essayés, du plus récent au plus ancien : `oo2core_9_win64.dll` jusqu'à `oo2core_3_win64.dll`. Le format est rétrocompatible, donc une bibliothèque plus ancienne fonctionne en général encore.

La recherche n'est volontairement **pas** un parcours récursif de tous les disques, qui prendrait des minutes. Si elle ne trouve rien, définissez `HEAT3D_OODLE` :

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Un dossier fonctionne aussi bien que le fichier lui-même : les noms de DLL ci-dessus y sont essayés.

Une installation d'Unreal Engine en contient une sous `Engine\Binaries\ThirdParty\Oodle`, ce qui en fait la source la plus propre pour un développeur. Beaucoup de jeux en livrent une à côté de leur exécutable. Les jeux Unreal 5 lient souvent Oodle statiquement et ne livrent aucune DLL ; la copie trouvée peut donc appartenir à un autre jeu que l'archive lue. Le format est le même dans les deux cas.

## Comment il est appelé {#how-it-is-called}

`OodleLZ_Decompress` est appelé via `ctypes` avec la longueur de sortie attendue (l'index de l'archive la connaît toujours, et Oodle ne peut pas la déduire), le décodage résistant aux données malformées activé (l'entrée n'est pas fiable), pas de contrôle CRC (le SHA-1 du pak couvre déjà les octets), et sans threads. Un résultat de mauvaise longueur est une erreur. La bibliothèque est chargée une seule fois par exécution.

## Quand il n'y en a aucune {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Une entrée qui ne peut pas être décompressée est une erreur, jamais des données plausibles mais fausses.

Le chargeur ne fonctionne que sous Windows (il cherche `*_win64.dll`). Les bibliothèques pour Linux et macOS ne sont pas recherchées.
