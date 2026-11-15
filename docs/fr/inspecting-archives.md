---
title: "Inspecter les archives"
nav_order: 3
lang: "fr"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Inspecter les archives : `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Un jeu range ses fichiers dans de grandes boîtes appelées **archives**. Ces commandes regardent l'étiquette d'une boîte, listent ce qu'elle contient et en sortent une chose.

Avant d'exporter quoi que ce soit d'un jeu inconnu, regardez ce qu'il livre. Ces quatre verbes lisent un fichier et vous disent ce que c'est et ce qu'il contient ; ils n'écrivent rien, sauf l'unique entrée que vous demandez à `extract`.

![identify, list et extract lancés sur un petit zip](../assets/img/inspect-archives.svg)

*Un essai sur un zip fictif organisé comme un niveau de BeamNG.drive.*

## Étape par étape {#step-by-step}

1. **Demandez ce qu'est le fichier.** `identify` lit les octets, pas l'extension :

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Il indique le format (Unreal `.pak`, IoStore `.utoc`/`.ucas`, paquet Unity ou `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` ou `.modelbin`, BeamNG `.cdae`/`.ter`, zip), sa version, le nombre d'entrées qu'il contient, et s'il est chiffré.

2. **Listez ce qu'il contient.** `list` affiche une ligne par entrée : taille, compression, chemin. Filtrez avec `--filter`, limitez le nombre de lignes avec `--limit` :

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Sortez une entrée.** `extract` écrit une entrée (dans le dossier où vous vous trouvez, sauf si `--out` indique un autre endroit), selon le chemin affiché par `list` (ou `#12`, par numéro, dans un `.minizip` sans noms) :

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity :** `meshes` liste et vérifie les maillages d'un `SerializedFile` :

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Options {#options}

| Verbe | Option | Signification |
|---|---|---|
| `identify` | `<file>` | n'importe quel fichier |
| `list` | `<archive>` | `.pak`, `.utoc` (ou le `.ucas` à côté), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | seulement les chemins contenant TEXT |
| | `--limit N` | au plus N lignes |
| | `--key HEX` | une clé AES-256 (64 chiffres hexadécimaux) que vous possédez déjà ; seul un `.pak` chiffré en a besoin |
| `extract` | `<archive> <path>` | l'archive et le chemin de l'entrée, tel qu'affiché par `list` |
| | `--out FILE` | où l'écrire (par défaut : le nom du fichier de l'entrée) |
| | `--key HEX` | comme pour `list` |
| `meshes` | `<file>`, `--limit N` | un `SerializedFile` Unity ; au plus N maillages |

L'outil n'embarque aucune clé et n'en retrouve aucune : une archive chiffrée ne s'ouvre qu'avec une clé que vous fournissez. Un fichier qu'il ne peut pas lire est refusé en une ligne avec le code de sortie 1. Chaque verbe et chaque code de sortie figurent dans [Commandes](commands.md) ; la façon dont chaque format est lu se trouve dans [Lecteurs d'archives](archive-readers.md).
