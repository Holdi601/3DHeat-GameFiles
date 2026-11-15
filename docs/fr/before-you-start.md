---
title: "Avant de commencer"
nav_order: 2
lang: "fr"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Avant de commencer {#before-you-start}

Vous débutez avec la ligne de commande ? Cette page vous mène de zéro à un outil qui fonctionne, en une dizaine de minutes.
Vous tapez des commandes dans une fenêtre appelée **terminal**, et l'outil répond par du texte.

## 1. Installer Python {#install-python}

1. Allez sur [python.org/downloads](https://www.python.org/downloads/) et téléchargez
   **Python 3.10 ou plus récent**.
2. Lancez l'installeur. Sur son premier écran, cochez **« Add python.exe to PATH »**,
   puis cliquez sur **Install Now**.

## 2. Récupérer l'outil {#get-the-tool}

- **Avec git :** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Sans git :** sur la [page GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  cliquez sur le bouton vert **Code**, puis sur **Download ZIP**, et décompressez-le.

## 3. Ouvrir un terminal dans le dossier de l'outil {#open-a-terminal-in-the-tools-folder}

- Dans l'Explorateur de fichiers, ouvrez le dossier qui contient `README.md`. Cliquez dans la
  barre d'adresse, tapez `cmd` et appuyez sur Entrée. Une fenêtre noire s'ouvre, déjà dans ce dossier.
- Ou ouvrez **Windows Terminal** et allez-y avec `cd` :

  ```
  cd "C:\Users\vous\Downloads\3DHeat-GameFiles"
  ```

## 4. Installer ce dont l'outil a besoin {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Vous devez voir des lignes se terminant par `Successfully installed ...`.

## 5. Vérifier que cela fonctionne {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Vous devez voir `usage: heat3d_gamefiles [-h]` et une liste de verbes (`identify`,
`list`, `extract`, `course`, ...). C'est la réussite : l'outil est prêt.

## Lire les exemples {#reading-the-examples}

- `<quelque chose>` est un **espace réservé** : tapez votre propre valeur à la place, sans les
  chevrons. `<fichier de tour>` devient, par exemple, `laps\mon_tour.json`.
- `[--option]` entre crochets est **facultatif** : omettez-le si vous n'en avez pas besoin.
- Un chemin qui contient des espaces demande des **guillemets doubles** : `"C:\Mes Jeux\tour.json"`.
- Lancez chaque commande dans le dossier de l'outil (étape 3).

## Quand quelque chose ne va pas {#when-something-goes-wrong}

| Vous voyez | Que faire |
|---|---|
| `'python' is not recognized` | Python n'est pas installé, ou « Add to PATH » n'était pas coché. Relancez l'installeur, cochez la case, puis ouvrez un nouveau terminal. |
| `No module named heat3d_gamefiles` | Le terminal est dans le mauvais dossier. Faites `cd` jusqu'au dossier qui contient `README.md`. |
| `No module named numpy` (ou un autre nom) | L'étape 4 a été sautée. Lancez `pip install -r requirements.txt`. |
| `can't open file` / `not found` avec un chemin | Le chemin contient des espaces sans guillemets, ou une faute de frappe. Mettez-le entre guillemets doubles. |

D'autres messages et leurs solutions : [Dépannage](troubleshooting.md).
