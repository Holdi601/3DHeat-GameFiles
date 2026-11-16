---
title: "Entradas de vuelta"
nav_order: 7
lang: "es"
source: lap-inputs.md
source_hash: "3f335d2fc454"
nav_exclude: true
search_exclude: true
---
# Entradas de vuelta {#lap-inputs}

Un **archivo de vuelta** es una lista de puntos x, y, z: por dónde fue el coche. La forma más rápida de hacer uno a mano es la tabla CSV de [5. Una tabla `.csv`](#a-csv-table) más abajo.

Una vuelta le dice a la exportación de circuito **por dónde fue el coche**. Nada más de ella se usa: la velocidad, los controles y las fuerzas g pertenecen al lado de telemetría de 3DHeat. La herramienta lee posiciones en metros del mundo del propio juego, y además, cuando el archivo lo indica, el juego y el circuito.

Fuente: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Lo que acepta `course` {#what-course-accepts}

El formato se reconoce mirando el archivo, no su nombre, salvo que `.npz` y `.csv` se reconocen por la extensión y todo lo demás se intenta como JSON.

### 1. Un documento `heat3d-lap` (cualquier juego) {#a-heat3d-lap-document-any-game}

Lo escriben los grabadores de telemetría de 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y`, `channels.z` son obligatorios. Las filas en las que alguno de los tres no es un número finito se descartan. Los demás canales se ignoran.
- `game` decide la exportación (ver [Comandos](commands.md#which-game)).
- `track` lo usa Assetto Corsa Rally para probar primero la etapa nombrada.
- Ejes: y es la altura. Las vueltas de Forza y de AC Rally usan los ejes horizontales del juego tal como los escribe el grabador. Las vueltas de BeamNG se esperan en el marco del visor, `(x, z, -y)` del mundo de BeamNG con Z hacia arriba (ver [BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html#the-laps-frame)).

### 2. Un archivo de ruta {#a-route-file}

Lo escriben `heat3d_capture route` y `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` es una lista de `[x, y, z]`. Un archivo de ruta con `bounds` pero sin posiciones también sirve: sus dos esquinas forman una línea degenerada, pero una caja utilizable.

### 3. Un archivo de vuelta de FH Companion {#an-fh-companion-lap-file}

Los archivos por vuelta de la biblioteca grabada de FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Una `X`, `Y` o `Z` que falte se lee como 0. Los archivos se escriben con una marca de orden de bytes, así que todo el JSON se lee como `utf-8-sig`.

### 4. Una grabación `.npz` {#a-npz-recording}

Un archivo de NumPy que contiene una matriz `positions` de forma (n, 3).

### 5. Una tabla `.csv` {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Las columnas llamadas `x`, `y`, `z` (sin distinguir mayúsculas ni espacios alrededor) son obligatorias. Las demás columnas se ignoran.
- Las líneas que empiezan por `#` se saltan. Si la **primera** línea es `# {json}`, se leen sus campos `game` y `track`.
- Las filas que no se leen como números se saltan.

### 6. Una carpeta {#a-folder}

Una carpeta se revisa **recursivamente** buscando archivos `.json`, `.npz` y `.csv`, y todos se concatenan en una única línea de conducción. Así se guarda un circuito grabado completo: FH Companion anida carpetas por clase, coche, puesta a punto y etiqueta.

- `course.json` se omite por su nombre (son metadatos, no una vuelta).
- Un archivo que no se puede leer se omite en silencio. Un archivo malo entre cientos no cuesta el resto.
- La consola informa de cuántos archivos de vuelta entraron (`12 laps, 18,400 samples`).
- La carpeta toma el juego que nombran sus archivos, cuando nombran **solo uno**. Un archivo que no nombra ningún juego (una vuelta de FH Companion, `course.json`, un CSV sin su línea de descripción) no cuenta, así que uno de ellos entre las grabaciones de un juego no le quita a la carpeta su juego. Si los archivos nombran dos juegos distintos, es una mezcla, y la carpeta no toma ninguno. Una carpeta sin juego se exporta como Forza, salvo que `--game` indique otra cosa.
- Si no se lee nada: `no readable laps under <folder>`.

### 7. Un nombre de circuito {#a-course-name}

Si el argumento no es un archivo ni una carpeta existentes, se busca como nombre de circuito en la biblioteca de FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. una carpeta cuyo nombre, sin el sufijo ` (course_...)`, sea igual al nombre (sin distinguir mayúsculas);
2. si no, la única carpeta cuyo nombre contenga el nombre dado.

Así, `"Example Circuit"` encuentra `Example Circuit (course_1200_3400_to_1175_3400)` sin que nadie conozca las coordenadas. Varias coincidencias son un error que las enumera. Un circuito encontrado por nombre no lleva juego, así que se exporta como Forza salvo que `--game` indique otra cosa.

## Lo que acepta `terrain --route` {#what-terrain---route-accepts}

`terrain` necesita el campo `bounds` del archivo de ruta (forma 2 de arriba), `{"min": [x, y, z], "max": [x, y, z]}`. Sin `bounds`, se detiene con `<file> has no bounds; --route takes a route file with "bounds": {...}`. El archivo se lee como UTF-8 con o sin marca de orden de bytes, igual que cualquier vuelta JSON. Si el mismo archivo también tiene al menos 10 posiciones legibles con las reglas de arriba, estas acotan el corte a un corredor y guían el detalle.

## Cómo se usa la vuelta {#how-the-lap-is-used}

| Uso | Detalle |
|---|---|
| nombre | el nombre base del archivo, o el nombre de la carpeta, sin ` (course_...)`; se convierte en el nombre de archivo de salida por defecto |
| distancia conducida | la suma de las separaciones entre muestras consecutivas (se imprime como `m driven`; en una carpeta incluye también los saltos entre archivos) |
| caja | la extensión en x y z ampliada con `--margin`; la altura nunca se acota |
| corredor | las x y z de cada muestra, ver [Exportación de circuito](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html#the-corridor) |
| detalle | la distancia de cada copia colocada a la muestra más cercana, ver [Niveles de detalle y presupuesto](detail-budget.md) |

Una vuelta con menos de dos muestras se rechaza (`holds no driving`).

## Errores {#errors}

| Mensaje | Significado |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | el archivo no es JSON (ni `.npz` ni `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON de otra forma |
| `<file> has no x, y and z columns` | un CSV sin esas cabeceras |
| `<file> has no positions array` | un `.npz` sin `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | un nombre, pero sin biblioteca de FH Companion |
| `'<name>' matches 3 courses: A, B, C` | sé más específico |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | solo para búsquedas por nombre y para `courses` |
