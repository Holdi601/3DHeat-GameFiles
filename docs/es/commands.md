---
title: "Comandos"
nav_order: 2
lang: "es"
source: commands.md
source_hash: "8ae04c37b1a4"
nav_exclude: true
search_exclude: true
---
# Comandos {#commands}

Cada comando se ejecuta como `python -m heat3d_gamefiles <verbo> ...` desde la carpeta del repositorio. Los verbos vienen en el orden en que normalmente los necesitas: qué es este archivo, qué contiene, dame eso y convierte una vuelta en un recorrido.

| Verbo | Recibe | Hace |
|---|---|---|
| [`identify`](#identify) | cualquier archivo | dice qué formato de contenedor es, leyendo sus bytes |
| [`list`](#list) | un `.pak` o `.utoc` de Unreal, un `.vpk` de Source 2, o un zip (un `.minizip` de ForzaTech mediante la herramienta de Forza) | lista sus entradas |
| [`extract`](#extract) | lo mismo | escribe una entrada en el disco |
| [`meshes`](#meshes) | un `SerializedFile` de Unity | lista y comprueba sus mallas |
| [`course`](#course) | una vuelta | exporta el recorrido alrededor de ella (Forza, BeamNG.drive, Assetto Corsa Rally) (la ejecuta la herramienta de Forza, BeamNG.drive o AC Rally) |
| [`courses`](#courses) | una biblioteca de vueltas grabadas | ejecuta `course` en cada recorrido de ella (Forza) (la ejecuta la herramienta de Forza) |
| [`races`](#races) | un Forza instalado | lista cada carrera que define el juego: lo que añade, lo que oculta, los lugares, el estado de su exportación (la ejecuta la herramienta de Forza) |
| [`terrain`](#terrain) | una carpeta de circuito de Forza | recorta una zona por coordenadas del mundo (la ejecuta la herramienta de Forza) |
| [`levels`](#levels-and-level-frostbite) | un juego Frostbite instalado (Battlefield 6) | lista sus niveles (la ejecuta la herramienta de Battlefield) |
| [`level`](#levels-and-level-frostbite) | el nombre de un nivel | exporta el nivel: terreno, mallas colocadas, opcionalmente sus mapas de color (Battlefield 6) (la ejecuta la herramienta de Battlefield) |
| [`cars`](#cars) | un Forza instalado | cada coche con bajo detalle, en un solo archivo para la pestaña de carrera del visor (la ejecuta la herramienta de Forza) |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | un juego de Unreal 5 | lista sus mapas de World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | el nombre de un mapa | exporta el mapa: paisaje, estructuras HLOD y agua |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | un Arma Reforger instalado | lista sus mundos (la ejecuta la herramienta de Reforger) |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | el nombre de un mundo | exporta el mundo: terreno en sus colores, el mar, edificios como cajas (la ejecuta la herramienta de Reforger) |

**Cómo leer los ejemplos:** `<x>` significa que lo cambies por tu propio valor, sin los paréntesis angulares; `[...]` es opcional; pon entre "comillas dobles" una ruta con espacios, por ejemplo `"C:\Games\My Game"`. ¿Es nuevo en esto? Mira [Antes de empezar](before-you-start.md). El `--help` completo de cada verbo está en la [Referencia de comandos](../cli-reference.md).

Cada vez que arranca el programa, puede comprobar primero si hay una versión más nueva. Mira [Actualizaciones](updates.md). `HEAT3D_NO_UPDATE=1` desactiva esa comprobación.

Fuente: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Páginas paso a paso: [Inspeccionar archivos](inspecting-archives.md), [Exportación de circuito](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html), [Niveles completos](whole-levels.md), [Coches de Forza](https://holdi601.github.io/3DHeat-Ext-Forza/forza-cars.html).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Códigos de salida {#exit-codes}

| Código | Significado |
|---|---|
| 0 | éxito |
| 1 | el trabajo falló (una vuelta ilegible, no se encontró ningún juego, nada que exportar, un recorrido de `courses` falló; para `list` y `extract`, un archivo que no es ninguno de los que leen, uno que no se puede abrir o leer -un pak cifrado sin `--key`, un contenedor IoStore cifrado- o una entrada que no está en el archivo) |
| 2 | argumentos incorrectos (argparse), una ruta que no existe, una `--key` que no tiene 64 dígitos hexadecimales, o `terrain` con ambos o con ninguno de `--box` y `--route` |

Los fallos de `list` y `extract` son cada uno una línea en la salida de error estándar, no un rastreo de Python.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Esto lee el archivo y dice qué contenedor es. No se fía de la extensión (la única excepción es un `.ucas`, más abajo). Prueba los formatos en este orden y se detiene en el primero que se lee correctamente:

1. **`.pak` de Unreal**: un pie con la firma de pak en los últimos 1.024 bytes. Muestra la versión, el desplazamiento y el tamaño del índice, si el índice está cifrado y los métodos de compresión.
2. **IoStore `.utoc` de Unreal**: la firma de IoStore al inicio. Muestra la versión, el número de fragmentos y si el contenedor está cifrado; si no lo está, el número de archivos que nombra su directorio (y bajo qué punto de montaje), los métodos de compresión y si su `.ucas` está al lado. Un `.ucas` no tiene cabecera propia, así que se reconoce por el `.utoc` del mismo nombre que tiene al lado, y `identify` nombra ese archivo.
3. **`.minizip` de ForzaTech**: la firma `PGZP`. Muestra la versión, el número de entradas y de segmentos, y si el `ChunkContentsMiniZip<n>.txt` que nombra las entradas está al lado (y, si está, si nombra tantas como hay).
4. **zip**: una cabecera de archivo local zip al inicio. Muestra el número de entradas, las seis extensiones más comunes y los nombres de nivel cuando las entradas están bajo `levels/<name>/`, como en un archivo de nivel de BeamNG.drive.
5. **Unity**: un paquete `UnityFS` (muestra la versión del motor y el número de entradas) o un `SerializedFile` suelto (muestra el formato, la versión del motor, el número de objetos y las seis clases más comunes).
6. **`.toc` de Frostbite**: muestra el tipo (`plain` o `signed`), dónde empieza el árbol, y o bien el número de recursos (tabla binaria de secciones) o el número de superbundles (árbol DbObject).
7. **`.vpk` de Source 2**: muestra la versión, el número de entradas y la primera malla de navegación `.nav` si el archivo tiene una.
8. **`.cdae` de BeamNG**: versión de forma 31 que se puede leer. Muestra el número de mallas, el número de niveles de detalle dibujados y los primeros materiales.
9. **`.ter` de BeamNG**: no tiene firma, así que todo tiene que cuadrar: un lado de 2 a 16.384, esa cantidad al cuadrado de alturas y bytes de capa, y luego de 1 a 255 nombres de capa imprimibles. Muestra la versión, el tamaño y los nombres de capa.
10. **`.modelbin` de ForzaTech**: muestra la versión, el número de fragmentos y las seis etiquetas de fragmento más comunes. El contenido de los fragmentos no se decodifica aquí.

Los formatos con firma propia (del 2 al 4) van antes que Unity y Frostbite, cuyas comprobaciones leen el archivo entero: un archivo de Forza pesa decenas de gigabytes.

Si ninguno coincide, imprime `not a format this tool reads` y la última razón. Esa razón viene de la comprobación de ForzaTech.

Ejemplo (sintético):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Opción | Por defecto | Significado |
|---|---|---|
| `<archive>` | obligatorio | un `.pak` de Unreal; un `.utoc` de IoStore (o el `.ucas` que tiene al lado); un `.vpk` de Source 2 (para VPK partidos, el `_dir.vpk`); un `.minizip` de ForzaTech; un zip, como los archivos de nivel y de contenido de BeamNG |
| `--filter TEXT` | ninguno | solo las rutas que contienen TEXT, sin distinguir mayúsculas |
| `--limit N` | 50 | muestra como mucho N entradas (el total siempre se muestra) |
| `--key HEX` | ninguna | una clave AES-256 que ya tengas, 64 dígitos hexadecimales, con o sin `0x`. Solo la usa un `.pak` cifrado. Cualquier valor que no tenga 64 dígitos hexadecimales se rechaza antes de abrir el archivo (código de salida 2) |

La herramienta decide el formato por los bytes: una tabla de contenidos de IoStore, un `.minizip` y un VPK por la firma con la que empiezan, un zip por su cabecera de archivo local y un `.pak` por el pie al final. Un `.ucas` no tiene cabecera y se abre a través del `.utoc` del mismo nombre. Un archivo que no es ninguno de estos se rechaza con `<file> is not an archive list and extract read (...)`. Uno que sí lo es, pero que no se puede abrir, se rechaza con la razón del lector: un pak cifrado sin `--key`, un contenedor IoStore cifrado, una versión de pak que no se lee. En cualquier caso, es una línea y código de salida 1.

Cada línea muestra el tamaño sin comprimir, el método de compresión y la ruta:

| Archivo | Método | Rutas |
|---|---|---|
| `.pak` | `none`, o el nombre del pie (`Zlib`, `Oodle`, `Gzip`...) | con el punto de montaje del archivo, por ejemplo `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, o el método del contenedor (`Oodle`, `Zlib`...), tal como está guardado su primer bloque | con el punto de montaje, por ejemplo `../../../<Project>/Content/...`. Un contenedor sin índice de directorio no nombra archivos y se rechaza |
| `.vpk` | siempre `stored` | tal como están en el directorio |
| `.minizip` | `lz4`, `deflate` o `stored` | tal como las escribe el `ChunkContentsMiniZip<n>.txt` que está al lado de `GeoChunk<n>.minizip`, sin el prefijo de la máquina de compilación (con barras invertidas, como las escribe el juego). El archivo no guarda nombres, así que sin ese archivo las entradas son `#0`, `#1`... Una lista cuyo número de líneas no coincide con el de entradas se rechaza: no pertenecen juntas |
| zip | `stored`, `deflate`, ... | tal como están guardadas; las carpetas no se listan |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Opción | Por defecto | Significado |
|---|---|---|
| `<archive>` | obligatorio | igual que en `list` |
| `<entry>` | obligatorio | la ruta exactamente como la imprime `list` (distingue mayúsculas); en un `.minizip`, también vale `#<número>` |
| `--out FILE` | el nombre de la entrada (después del último `/` o `\`), en la carpeta actual | dónde escribir; las carpetas padre se crean |
| `--key HEX` | ninguna | igual que en `list` |

La entrada se descifra (en un pak, con clave), se descomprime y se escribe. Imprime `<bytes> bytes -> <file>`. Si la ruta no está en el archivo, el comando termina con código 1. También termina así una entrada que no se puede leer (una entrada cifrada sin clave, o comprimida con Oodle sin la biblioteca de Oodle), con la razón en una línea. Aquí no se comprueba una entrada VPK con su CRC. El lector tiene un método `verify()` para eso (mira [VPK de Source 2](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Opción | Por defecto | Significado |
|---|---|---|
| `<path>` | obligatorio | un `SerializedFile` de Unity suelto (`sharedassets0.assets`, `level0`...), no un paquete |
| `--limit N` | 25 | decodifica e imprime como mucho N mallas |

Imprime el número de objetos `Mesh` y luego una línea por malla: el nombre (los primeros 40 caracteres), el número de vértices y de triángulos, y `ok` o `BOUNDS DISAGREE`. `BOUNDS DISAGREE` significa que los vértices decodificados no reproducen la caja delimitadora que Unity guardó para la malla, dentro del 2 % del tamaño de la caja. Es la comprobación propia del análisis (mira [Unity](reader-unity.md)). Una malla que no se puede leer se informa con la razón y cuenta para el límite. Los datos de vértices de un archivo `.resS` se leen de la carpeta donde está el contenedor.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## Los verbos propios de cada juego {#the-games-own-verbs}

Cada lector de juego es un pequeño proyecto propio, con su propio archivo de licencia, sus versiones y su gestor de incidencias, así que puede instalarse, actualizarse, mantenerse - o retirarse a petición de un titular de derechos - por separado, sin afectar al visor ni a las demás herramientas. Instala el de tu juego (su página dice cómo), y tanto su comando propio como los verbos de aquí funcionan. GameFiles ejecuta la herramienta del juego con los argumentos que le diste; no se importa nada de ella. Se encuentra como su comando en `PATH`, como su paquete instalado, o como su carpeta en `HEAT3D_<GAME>_MAPS` o junto a GameFiles (`exporters/ext/<game>-maps` en una copia de 3DHeat, o `3DHeat-Ext-<Game>` al lado de esta carpeta). Si no está instalada, el verbo dice dónde conseguirla y sale con código 2.

| Juego | Su herramienta propia | Verbos de aquí que la ejecutan |
|---|---|---|
| Forza Horizon / Motorsport | [3DHeat-Ext-Forza](https://holdi601.github.io/3DHeat-Ext-Forza/) (`heat3d-forza-maps`) | `course` (vueltas de Forza), `courses`, `races`, `cars`, `terrain`; `identify`, `list`, `extract` de un `.minizip` |
| Battlefield (Frostbite) | [3DHeat-Ext-Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/) (`heat3d-battlefield-maps`) | `levels`, `level`; `identify` de un `.toc` de Frostbite |
| BeamNG.drive | [3DHeat-Ext-BeamNG](https://holdi601.github.io/3DHeat-Ext-BeamNG/) (`heat3d-beamng-maps`) | `course` (vueltas de BeamNG); `identify` de un `.cdae` o `.ter` |
| Assetto Corsa Rally | [3DHeat-Ext-ACRally](https://holdi601.github.io/3DHeat-Ext-ACRally/) (`heat3d-acrally-maps`) | `course` (vueltas de AC Rally) |
| Arma Reforger (Enfusion) | [3DHeat-Ext-Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/) (`heat3d-reforger-maps`) | `enfusion-worlds`, `enfusion-world` |

`python -m heat3d_gamefiles <verbo> --help` muestra las opciones propias de la herramienta del juego.

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Esto exporta el recorrido alrededor de una vuelta: el suelo en una franja a cada lado de la conducción, y lo que hay sobre él, como un único `.glb`, hecho por la herramienta propia del juego de la vuelta, ejecutada con los mismos argumentos: [Forza](https://holdi601.github.io/3DHeat-Ext-Forza/course-forza-horizon.html), [BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html), [Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html). Qué puede ser una vuelta: [Entradas de vuelta](lap-inputs.md); cuánto detalle se conserva: [Niveles de detalle y presupuesto](detail-budget.md).

### Qué juego {#which-game}

El juego se toma de `--game`, luego del campo `game` de un archivo `heat3d-lap` (o de la línea de descripción `# {...}` de un CSV), y si no hay nada, se usa Forza. Una carpeta toma el juego que nombran sus archivos, cuando nombran solo uno. Un archivo que no nombra ninguno (una vuelta de FH Companion, `course.json`, un CSV sin línea de descripción) no cuenta (mira [Entradas de vuelta](lap-inputs.md)).

| Valor | Lo ejecuta |
|---|---|
| empieza por `forza` | `heat3d-forza-maps course` |
| `beamng` | `heat3d-beamng-maps course` |
| `assetto-corsa-rally` o `acrally` | `heat3d-acrally-maps course` |
| `assetto-corsa-evo` | rechazado: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | rechazado: "tracks ship in a protected format that is not a file-extraction target" |
| cualquier otro | rechazado: "there is no course reader for <game> yet" |

Un rechazo también sugiere las alternativas: reconstruir el recorrido a partir de la partida (3DHeat GameCapture), o analizar las vueltas sin un recorrido, porque la pestaña Análisis de carrera del visor dibuja una carretera a partir de ellas.

## courses, races, cars, terrain (Forza) {#courses}

Lo ejecuta `heat3d-forza-maps` con los mismos argumentos: [sus comandos](https://holdi601.github.io/3DHeat-Ext-Forza/commands.html).

## levels and level (Frostbite) {#levels-and-level-frostbite}

Lo ejecuta `heat3d-battlefield-maps` con los mismos argumentos: [Niveles de Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/level-battlefield.html).

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` es la carpeta del juego, su `Content/Paks`, o el nombre de su carpeta en una biblioteca de Steam (`"<Steam game folder name>"`). `ue-maps` lista cada mapa que tiene celdas de World Partition ya compiladas junto a él. `ue-map` exporta uno como `ground:<map>` (el paisaje), `structure:<map>` (las mallas HLOD fusionadas del mapa) y `water:<map>` (sus masas de agua donde están por encima del suelo), en **centímetros** de Unreal, con Y y Z intercambiados: la única exportación que no está en metros. Cómo se lee y se comprueba: [Mapas de Unreal 5](level-unreal-world-partition.md).

| Opción | Por defecto | Significado |
|---|---|---|
| `<map>` | obligatorio | un nombre como lo imprime `ue-maps`, o una parte única de uno |
| `-o`, `--out FILE` | `<map>.glb` (en `$HEAT3D_LEVELS/<game>/` cuando esa variable está definida) | el `.glb` a escribir |
| `--ground-spacing METRES` | 2 | el espaciado de vértices del paisaje en el archivo, redondeado a un número entero de sus propios cuadrados |
| `--no-structures`, `--no-water` | | deja fuera esa parte |

Imprime los triángulos por parte, cuántos componentes de paisaje se leyeron y cuántos de los vértices que guardan dos veces no coinciden. Un mapa de 3 km a 2 m tiene unos 4,6 millones de triángulos de suelo.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

Lo ejecuta `heat3d-reforger-maps` con los mismos argumentos (sus `worlds` y `world`): [Mundos de Arma Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/level-arma-reforger.html).

## Variables de entorno {#environment-variables}

| Variable | Efecto |
|---|---|
| `HEAT3D_OODLE` | ruta a un `oo2core_*_win64.dll`, o a una carpeta que lo contenga; mira [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | una carpeta para cada exportación hecha sin `-o`: las de cada juego van en `<HEAT3D_LEVELS>/<game>/` (los recorridos en `<game>/courses/`, el paquete de coches en `forza/`). Si no está definida, van a la carpeta actual |
| `HEAT3D_FORZA_MAPS`, `HEAT3D_BATTLEFIELD_MAPS`, `HEAT3D_BEAMNG_MAPS`, `HEAT3D_ACRALLY_MAPS`, `HEAT3D_REFORGER_MAPS` | la carpeta de la herramienta de un juego, cuando no está instalada ni junto a GameFiles |
| `HEAT3D_NO_UPDATE` | cualquier valor distinto de vacío, `0`, `false` o `no` desactiva la comprobación de actualizaciones; mira [Actualizaciones](updates.md) |
| `LOCALAPPDATA` | donde se buscan la biblioteca de FH Companion, la carpeta de usuario de BeamNG y la caché de actualizaciones |
| `HEAT3D_COURSE` | solo para pruebas: el recorrido que usa la prueba de bordillos del juego instalado; mira [Desarrollo](development.md) |
