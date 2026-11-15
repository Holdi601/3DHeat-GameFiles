---
title: Abans de començar
nav_order: 2
lang: ca
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Abans de començar {#before-you-start}

Si és nou amb la línia d'ordres, aquesta pàgina el porta de no tenir res a una eina
en funcionament en uns deu minuts. Escriu ordres en una finestra que es diu **terminal**, i
l'eina respon amb text.

## 1. Instal·lar Python {#install-python}

1. Vagi a [python.org/downloads](https://www.python.org/downloads/) i descarregui
   **Python 3.10 o posterior**.
2. Executi l'instal·lador. A la primera pantalla, marqui **«Add python.exe to PATH»**,
   i després faci clic a **Install Now**.

## 2. Obtenir l'eina {#get-the-tool}

- **Amb git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Sense git:** a la [pàgina de GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  faci clic al botó verd **Code** i després a **Download ZIP**, i descomprimeixi-la.

## 3. Obrir una terminal a la carpeta de l'eina {#open-a-terminal-in-the-tools-folder}

- A l'Explorador de fitxers, obri la carpeta que conté `README.md`. Faci clic a la
  barra d'adreces, escrigui `cmd` i premi Intro. S'obre una finestra negra, ja en
  aquesta carpeta.
- O obri **Windows Terminal** i hi vagi amb `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Instal·lar el que necessita l'eina {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Hauria de veure línies que acaben en `Successfully installed ...`.

## 5. Comprovar que funciona {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Hauria de veure `usage: heat3d_gamefiles [-h]` i una llista de verbs (`identify`,
`list`, `extract`, `course`, ...). Això vol dir que va bé: l'eina està a punt.

## Llegir els exemples {#reading-the-examples}

- `<alguna cosa>` és un **marcador de posició**: escrigui el seu propi valor en lloc seu, sense
  els signes d'angle. `<lap file>` es converteix, per exemple, en `laps\my_lap.json`.
- `[--option]` entre claudàtors és **opcional**: deixi-ho estar si no ho necessita.
- Una ruta amb espais necessita **cometes dobles**: `"C:\My Games\lap.json"`.
- Executi cada ordre a la carpeta de l'eina (pas 3).

## Quan alguna cosa va malament {#when-something-goes-wrong}

| Veu | Què cal fer |
|---|---|
| `'python' is not recognized` | Python no està instal·lat, o no es va marcar «Add to PATH». Torni a executar l'instal·lador i marqui-la, i després obri una terminal nova. |
| `No module named heat3d_gamefiles` | La terminal és a la carpeta equivocada. Feu `cd` a la carpeta que conté `README.md`. |
| `No module named numpy` (o un altre nom) | Es va saltar el pas 4. Executi `pip install -r requirements.txt`. |
| `can't open file` / `not found` amb una ruta | La ruta té espais i no té cometes, o hi ha una errada. Posi-la entre cometes dobles. |

Més missatges i com resoldre'ls: [Resolució de problemes](../troubleshooting.md).
