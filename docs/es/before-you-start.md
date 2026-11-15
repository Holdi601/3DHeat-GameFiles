---
title: Antes de empezar
nav_order: 2
lang: es
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Antes de empezar {#before-you-start}

¿Nuevo en la línea de comandos? Esta página te lleva de cero a una herramienta en funcionamiento en
unos diez minutos. Escribes comandos en una ventana llamada **terminal**, y la herramienta responde
con texto.

## 1. Instalar Python {#install-python}

1. Ve a [python.org/downloads](https://www.python.org/downloads/) y descarga
   **Python 3.10 o posterior**.
2. Ejecuta el instalador. En su primera pantalla marca **"Add python.exe to PATH"**,
   y haz clic en **Install Now**.

## 2. Conseguir la herramienta {#get-the-tool}

- **Con git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Sin git:** en la [página de GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  haz clic en el botón verde **Code** y después en **Download ZIP**, y descomprímelo.

## 3. Abrir una terminal en la carpeta de la herramienta {#open-a-terminal-in-the-tools-folder}

- En el Explorador de archivos, abre la carpeta que contiene `README.md`. Haz clic en la barra de
  direcciones, escribe `cmd` y pulsa Intro. Se abre una ventana negra, ya en esa carpeta.
- O abre **Windows Terminal** y ve allí con `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Instalar lo que necesita la herramienta {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Deberías ver líneas que terminan en `Successfully installed ...`.

## 5. Comprobar que funciona {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Deberías ver `usage: heat3d_gamefiles [-h]` y una lista de verbos (`identify`,
`list`, `extract`, `course`, ...). Eso significa que la herramienta está lista.

## Cómo leer los ejemplos {#reading-the-examples}

- `<algo>` es un **marcador**: escribe tu propio valor, sin los corchetes angulares. `<lap file>` se
  convierte, por ejemplo, en `laps\my_lap.json`.
- `[--option]` entre corchetes es **opcional**: déjalo fuera si no lo necesitas.
- Una ruta con espacios necesita **comillas dobles**: `"C:\My Games\lap.json"`.
- Ejecuta cada comando en la carpeta de la herramienta (paso 3).

## Cuando algo sale mal {#when-something-goes-wrong}

| Ves | Qué hacer |
|---|---|
| `'python' is not recognized` | Python no está instalado, o no se marcó "Add to PATH". Ejecuta el instalador de nuevo, marca la casilla y abre una terminal nueva. |
| `No module named heat3d_gamefiles` | La terminal está en otra carpeta. Usa `cd` para ir a la carpeta que contiene `README.md`. |
| `No module named numpy` (u otro nombre) | Se saltó el paso 4. Ejecuta `pip install -r requirements.txt`. |
| `can't open file` / `not found` con una ruta | La ruta tiene espacios y no lleva comillas, o hay una errata. Ponla entre comillas dobles. |

Más mensajes y cómo resolverlos: [Solución de problemas](../troubleshooting.md).
