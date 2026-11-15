---
title: "Mises à jour"
nav_order: 13
lang: fr
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Mises à jour {#updates}

3DHeat GameFiles vérifie les versions publiées de ce dépôt GitHub au démarrage, indique quand une version plus récente est sortie, et propose la mise à jour. Vos propres fichiers (tours, exports) ne sont jamais touchés.

Source : [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
La version installée est celle du fichier [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) du dépôt.

## La vérification au démarrage {#the-check-at-start-up}

Chaque lancement de `python -m heat3d_gamefiles ...` appelle la vérification avant d'analyser ses arguments :

- Elle interroge `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`, avec un délai d'attente de **5 secondes**.
- La réponse est mise en cache pendant **6 heures** dans `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (ou `~/.cache/3DHeat/...` sans `LOCALAPPDATA`). Pendant ce délai, aucune requête n'est envoyée. « Pas encore de version » (HTTP 404) est mis en cache aussi.
- Hors ligne, limité en débit ou derrière un proxy, la vérification se termine simplement et l'outil fonctionne avec la version qu'il a.
- Si l'étiquette (tag) de la dernière version (`v1.2.3` ou `1.2.3` ; tout ce qui suit `-` ou `+` est ignoré) est plus récente que `VERSION`, il écrit sur la sortie d'erreur :

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **Dans un terminal** (entrée et sortie d'erreur sont toutes deux un TTY), il demande `Update now? [Y/n]`. Entrée, `y`, `yes`, `j` ou `ja` lance la mise à jour. Après une mise à jour réussie, la **même commande est relancée** sur le nouveau code, et son code de sortie est transmis.
- **Sans terminal** (une exécution planifiée, un pipe), il affiche seulement ``Run `python -m heat3d_update` in <folder> to update.`` et poursuit.

## Mise à jour sur demande {#updating-on-request}

```
python -m heat3d_update          # passer à la version la plus récente, si elle existe
python -m heat3d_update --check  # indiquer seulement si une version plus récente est sortie
```

Cette commande interroge toujours GitHub (sans cache). Elle affiche `Up to date: 1.0.1.`, `No release found (...)`, ou ce qu'elle a fait. Le code de sortie est 1 si la mise à jour n'a pas pu être appliquée.

## Comment une mise à jour est appliquée {#how-an-update-is-applied}

| Installé comme | Mise à jour |
|---|---|
| un **clone git** (un dossier `.git` et `git` dans le PATH) | `git pull --ff-only`. **Refusée** tant que des fichiers suivis ont des modifications locales : « this checkout has local changes; commit or stash them, then run `git pull` ». Les fichiers non suivis ne bloquent pas la mise à jour |
| une **copie téléchargée** | l'archive source de la version (`zipball_url`) est téléchargée et décompressée dans un dossier temporaire, en ignorant tout chemin qui sortirait de ce dossier ; sa `VERSION` doit être identique à celle de la version, sinon rien n'est copié ; ensuite ses fichiers sont copiés dans ce dossier |

Lors de la copie depuis une archive, les fichiers qui ne font pas partie de la version (tours, exports, environnements virtuels, tout ce que vous avez créé) sont laissés intacts. La mise à jour essaie aussi de supprimer les modules `.py` qu'une version a retirés de ses paquets, pour qu'un module périmé ne masque pas son remplaçant. Elle cherche les paquets `heat3d_*` à la racine de l'archive et à un niveau en dessous, et supprime les fichiers `.py` que la version n'a plus.

## Désactiver la vérification {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Toute valeur autre que vide, `0`, `false` ou `no` désactive à la fois la vérification au démarrage et la proposition. `python -m heat3d_update` fonctionne toujours lorsqu'il est lancé à la main.
