---
title: "Comandos"
nav_order: 2
lang: es
source: commands.md
source_hash: "6c8d37db40e5"
nav_exclude: true
search_exclude: true
---
# Comandos {#commands}

Cada comando se ejecuta como `python -m heat3d_gamefiles <verbo> ...` desde la carpeta del repositorio. Los verbos vienen en el orden en que normalmente los necesitas: qué es este archivo, qué contiene, dame eso y convierte una vuelta en un recorrido.

| Verbo | Recibe | Hace |
|---|---|---|
| [`identify`](#identify) | cualquier archivo | dice qué formato de contenedor es, leyendo sus bytes |
| [`list`](#list) | un `.pak` o `.utoc` de Unreal, un `.vpk` de Source 2, un `.minizip` de ForzaTech, o un zip | lista sus entradas |
| [`extract`](#extract) | lo mismo | escribe una entrada en el disco |
| [`meshes`](#meshes) | un `SerializedFile` de Unity | lista y comprueba sus mallas |
| [`course`](#course) | una vuelta | exporta el recorrido alrededor de ella (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | una biblioteca de vueltas grabadas | ejecuta `course` en cada recorrido de ella (Forza) |
| [`terrain`](#terrain) | una carpeta de circuito de Forza | recorta una zona por coordenadas del mundo |
| [`levels`](#levels-and-level-frostbite) | un juego Frostbite instalado (Battlefield 6) | lista sus niveles |
| [`level`](#levels-and-level-frostbite) | el nombre de un nivel | exporta el nivel: terreno, mallas colocadas y, opcionalmente, sus mapas de color (Battlefield 6) |
| [`cars`](#cars) | un Forza instalado | cada coche con bajo detalle, en un solo archivo para la pestaña de carrera del visor |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | un juego de Unreal 5 | lista sus mapas de World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | el nombre de un mapa | exporta el mapa: paisaje, estructuras HLOD y agua |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | un Arma Reforger instalado | lista sus mundos |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | el nombre de un mundo | exporta el mundo: terreno con sus colores, el mar, edificios como cajas |

**Cómo leer los ejemplos:** `<x>` significa que lo cambies por tu propio valor, sin los paréntesis angulares; `[...]` es opcional; pon entre "comillas dobles" una ruta con espacios, por ejemplo `"C:\Games\My Game"`. ¿Es nuevo en esto? Mira [Antes de empezar](before-you-start.md). El `--help` completo de cada verbo está en la [Referencia de comandos](../cli-reference.md).

Cada vez que arranca el programa, puede comprobar primero si hay una versión más nueva. Mira [Actualizaciones](updates.md). `HEAT3D_NO_UPDATE=1` desactiva esa comprobación.

Fuente: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Páginas paso a paso: [Inspeccionar archivos](inspecting-archives.md), [Exportar recorridos](course-export.md), [Niveles completos](whole-levels.md), [Coches de Forza](forza-cars.md).

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

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Esto exporta el recorrido alrededor de una vuelta: el suelo en una franja a cada lado de la conducción, y lo que hay sobre él, en un solo `.glb`. Lo demás lo averigua solo: qué juego, qué copia instalada, qué circuito, nivel o etapa, y (para Assetto Corsa Rally) en qué sentido van los ejes. Mira [Exportar recorridos](course-export.md).

`<lap>` puede ser cualquiera de estos (detalles en [Entradas de vuelta](lap-inputs.md)):

- un archivo de vuelta: JSON de ruta, JSON de vuelta de FH Companion, JSON `heat3d-lap`, `.npz`, o `.csv` con columnas x, y, z
- una carpeta de archivos de vuelta, buscada de forma recursiva (un recorrido grabado completo)
- un **nombre** de recorrido, buscado en la biblioteca de FH Companion en `%LOCALAPPDATA%\FHCompanion\laps`

### Opciones {#options}

| Opción | Por defecto | Juegos | Significado |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` en la carpeta actual | todos | dónde escribir; el nombre se pasa a minúsculas, y las secuencias de otros caracteres se cambian por `_` |
| `--game {forza,beamng,acrally}` | lo que diga el archivo de vuelta; si no, `forza` | todos | de qué juego es la vuelta |
| `--margin M` | 80 | todos | metros de suelo que se conservan a cada lado de la conducción |
| `--texture-size {2048,1024,512}` | 2048 | todos | píxeles de textura del suelo por cada loseta de 512 m (2048 = 25 cm por píxel) |
| `--no-textures` | desactivado | todos | solo colores planos: un archivo mucho más pequeño. En Forza, esto también omite la división entre calzada y arcén (mira abajo) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | de qué temporada son los mapas de suelo y las texturas de los modelos |
| `--no-placed` | desactivado | todos | solo terreno: sin bordillos, barreras, señales ni edificios. En BeamNG, las superficies de conducción modeladas como mallas se siguen conservando |
| `--trees` | desactivado | todos | coloca también la vegetación (Forza: árboles, arbustos y objetos rompibles; BeamNG: árboles; AC Rally: árboles y la vegetación instanciada) |
| `--detail-budget N` | automático | todos | un techo de triángulos para todo lo colocado; mira [Niveles de detalle y presupuesto](detail-budget.md) |
| `--track DIR` | buscada | Forza | la carpeta del circuito (bajo `media\Tracks`, la que contiene `GeoChunk0.minizip`) si no debe buscarse en el juego instalado |
| `--level NAME` | se encuentra a partir de la vuelta | BeamNG, AC Rally | el nivel (nombre de carpeta de BeamNG) o la etapa (nombre de mapa de AC Rally), sin distinguir mayúsculas |
| `--install DIR` | buscada en las bibliotecas de Steam | BeamNG, AC Rally | BeamNG: la carpeta que contiene `gameengine.zip`. AC Rally: la carpeta del juego, o su `acr\Content\Paks` / `Content\Paks` |

Las opciones que no se aplican a un juego se ignoran sin aviso. Por ejemplo, `--season` no hace nada con BeamNG ni con AC Rally, y `--track` tampoco hace nada con ellos.

### Qué juego {#which-game}

El juego se toma de `--game`, luego del campo `game` de un archivo `heat3d-lap` (o de la línea de descripción `# {...}` de un CSV), y si no hay nada, se usa Forza. Una carpeta toma el juego que nombran sus archivos, cuando nombran solo uno. Un archivo que no nombra ninguno (una vuelta de FH Companion, `course.json`, un CSV sin línea de descripción) no cuenta (mira [Entradas de vuelta](lap-inputs.md)).

| Valor | Exportación |
|---|---|
| empieza por `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` o `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | rechazado: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | rechazado: "tracks ship in a protected format that is not a file-extraction target" |
| cualquier otro | rechazado: "there is no course reader for <game> yet" |

Un rechazo también sugiere las alternativas: reconstruir el recorrido a partir de la partida (3DHeat GameCapture), o analizar las vueltas sin un recorrido, porque la pestaña Análisis de carrera del visor dibuja una carretera a partir de ellas.

### Ejemplos {#examples}

```
# Un recorrido de la biblioteca de FH Companion, por nombre
python -m heat3d_gamefiles course "Example Circuit"

# Un archivo de vuelta, una franja más estrecha, un archivo más pequeño
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Texturas de invierno, con árboles
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Un techo firme de 500.000 triángulos colocados
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Una carpeta de circuito dada directamente (juego instalado fuera de Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: nombra el nivel y apunta a la instalación
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, con un CSV de vuelta sencillo que no dice su juego
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Ejemplo de salida (Forza, cifras sintéticas):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Cada coche de un Forza instalado, con el bajo detalle propio del juego, en un solo archivo para la pestaña de carrera del visor: el modelo `ProxyLOD` que lleva cada archivo de coche bajo `media/Cars`, de unos 900 triángulos, con el número del coche tal como lo indica la telemetría, su marca, la etiqueta del modelo y el año a partir del nombre del archivo, y sus ruedas y luces traseras. Tarda segundos y escribe unos 5 MB. Vuelve a ejecutarlo cuando el juego tenga coches nuevos. Un archivo sin ese modelo (un objeto de tráfico) se nombra y se deja fuera. El formato está en [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Las formas están en metros, las del propio juego: 1:1 con el coche. El archivo contiene el contenido del juego, así que sirve para la máquina en la que se hizo, no para pasarlo a otros.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Esto ejecuta la exportación `course` de Forza en cada carpeta de recorrido de una biblioteca de vueltas grabadas, y escribe un `<name>.glb` por cada una. Es solo para Forza. Llama directamente a la exportación de Forza y no lee `--game`, `--level` ni `--install`.

| Opción | Por defecto | Significado |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | la carpeta donde escribir (se crea si falta) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | la biblioteca de vueltas |
| `--only TEXT [TEXT ...]` | todos | solo los recorridos cuyos nombres de carpeta contienen alguno de estos (sin distinguir mayúsculas) |
| `--force` | desactivado | exporta de nuevo lo que ya tiene un `.glb` |
| `--track DIR` | buscada | igual que en `course` |
| `--margin M` | 80 | igual que en `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | igual que en `course` |

Qué cuenta como carpeta de recorrido: una subcarpeta directa de la biblioteca cuyo nombre contiene ` (course_`, que es como las nombra FH Companion, por ejemplo `Example Circuit (course_1200_3400_to_1175_3400)`. La parte desde ` (course_` en adelante se quita del nombre.

Cómo se comporta una ejecución:

- Un recorrido cuyo `.glb` ya existe se salta (`kept`) salvo que se dé `--force`, así que una ejecución interrumpida continúa donde se quedó.
- Un recorrido que falla (vueltas ilegibles, memoria agotada, sin terreno...) se informa como `FAILED`, y la ejecución sigue.
- Al final imprime una tabla con el estado, el tamaño en MB, los segundos y el nombre, y luego `<n> of <total> courses in <folder>`.
- El código de salida es 1 si algún recorrido falló.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Es el corte de Forza con todo especificado a mano: das la carpeta del circuito y una zona, no una vuelta. Sirve cuando la zona que quieres es una caja y no una conducción.

| Opción | Por defecto | Significado |
|---|---|---|
| `<path>` | obligatorio | una carpeta de circuito de Forza bajo `media\Tracks` (la que contiene `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | obligatorio | el `.glb` a escribir |
| `--box X0 Z0 X1 Z1` | | la zona, en metros del juego (x y z, como los informa la telemetría); las esquinas en cualquier orden |
| `--route FILE` | | un JSON de ruta con `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, como lo escriben `heat3d_capture route` y `heat3d_capture laps`; se lee como UTF-8, con o sin marca de orden de bytes |
| `--margin M` | **100** | metros añadidos alrededor de los límites de una ruta, y ancho del corredor cuando la ruta tiene una línea |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | igual que en `course` |

Hay que dar exactamente uno de `--box` y `--route`; si no, el código de salida es 2. Con `--route`, el corte son los `bounds` de la ruta (`min`/`max`, x y z) ampliados con el margen. Si el archivo también tiene al menos 10 posiciones, el corte se estrecha a un corredor de `--margin` metros alrededor de ellas, y los modelos colocados reciben su detalle según la distancia a esa línea. Con `--box`, se conserva toda la caja, y el detalle va a lo que está más cerca del centro de la caja.

La altura nunca forma parte del corte. Una caja fuera del mapa, o en el mar, da `no terrain there` (código de salida 1), no un error sobre coordenadas.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` lista los niveles que trae un juego Frostbite instalado, por el nombre de su tabla (`levels/<level>/<level>.toc`), con su tamaño y de dónde viene: `Data` para el juego base, `Update/<pack>` para una actualización, y cuántas tablas de alta resolución le añaden. Un nivel que trae una actualización tiene una tabla pequeña de fragmentos en el juego base; la tabla con los paquetes del nivel es el nivel (mira [Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` exporta uno: el mapa de alturas del terreno, cada malla que colocan los grupos de modelos estáticos del nivel, los objetos colocados uno a uno y dónde están, y el fondo de terreno del nivel alrededor del mapa. Con `--textures`, cada superficie lleva su mapa de color; con `--navmesh`, también las superficies sobre las que caminan los soldados. Cómo se lee está en [Frostbite](reader-frostbite.md).

| Opción | Por defecto | Significado |
|---|---|---|
| `<level>` | obligatorio | un nombre como lo imprime `levels`, una parte única de uno, o la ruta del `.toc` de un nivel |
| `-o`, `--out FILE` | `<level>.glb` | el `.glb` a escribir |
| `--install FOLDER` | el primer juego de Steam cuyo `Data` contiene un `layout.toc` | la carpeta del juego |
| `--textures [PIXELS]` | desactivado; 512 si se da sin tamaño | escribe el mapa de color de cada superficie, el mip más grande que no pase de PIXELS por lado, y sus coordenadas de textura tal como las tiene el juego, con un muestreador que repite (mira [Formato de salida](output-format.md)). La altura recibe el mapa de color del fondo de terreno donde ese mapa la cubre; si no, el color medio de los materiales de superficie del terreno; si no, el color medio del fondo alrededor. Sin esta opción, cada parte es de color plano |
| `--ground-texture [METRES]` | desactivado; 0.5 si se da sin tamaño | pinta las calcomanías del terreno (carreteras, pistas, plataformas, marcas pintadas) sobre el color del suelo, multiplicadas por el mapa de color del terreno cuando el nivel lo tiene, dentro del color de la altura, a METRES por píxel, en losetas de como mucho 4.096 píxeles (`ground:terrain x<x> z<z>`). Funciona con o sin `--textures` |
| `--navmesh` | desactivado | añade la malla de navegación del nivel para su agente más pequeño, el soldado (1,8 m de alto, 0,4 m de ancho), como la parte `nav:walkable`: el suelo, los pisos, las escaleras y los tejados a los que puede llegar un soldado, sin los enlaces (saltos, escaleras de mano, pasos por encima) entre ellos |
| `--ground-spacing METRES` | 4 | el espaciado más fino del mapa de alturas; los nodos más finos se muestrean más gruesos. 0 deja fuera el mapa de alturas |
| `--detail-budget N` | cada copia en su nivel más grueso, más un cuarto, como mínimo 1.500.000 | un techo de triángulos. Las mallas que más cuestan bajan un nivel de detalle cada vez hasta que caben; si ni siquiera los niveles más gruesos bastan, primero se dejan fuera las copias más pequeñas. El fondo de terreno nunca se engrosa ni se deja fuera |
| `--skip TEXT` | | deja fuera los grupos de modelos estáticos cuyo nombre de partición contiene TEXT; repítelo para varios. Por ejemplo, la capa de un modo de juego |
| `--by-mesh` | desactivado | para averiguar qué es una parte: una parte por malla de origen y material, nombrada `<part> \| <mesh> \| <material>`; un archivo mucho más grande |
| `--clamped-uvs` | desactivado | para un renderizador que no puede repetir una textura: corta cada triángulo texturizado en trozos cuyas coordenadas caen dentro de 0..1, y dibuja un triángulo que necesitaría más de 4 trozos con el color medio de su textura, en una parte `<part> (average colour)` |

Imprime los grupos y cuántas copias colocó cada uno, las mallas que dejó fuera y por qué, los triángulos por parte (y, con `--textures`, cuántas texturas y cuántas secciones encontraron su mapa de color), qué es el suelo y, con `--navmesh`, cuántas teselas de navegación se leyeron. No se escribe nada del nivel más allá de la geometría: ni nombres ni metadatos (mira [Formato de salida](output-format.md)).

El presupuesto del terreno es aparte: el mapa de alturas y el fondo nunca se engrosan con `--detail-budget`; `--ground-spacing` dimensiona el mapa de alturas.

Un nivel completo es grande: normalmente más de diez millones de triángulos y varios cientos de MB. `--textures` añade poco al archivo; un nivel lleno de árboles puede llegar a unos 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8` lo deja en aproximadamente un tercio de eso.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` es la carpeta del juego, su `Content/Paks`, o el nombre de su carpeta en una biblioteca de Steam (`"<Steam game folder name>"`). `ue-maps` lista cada mapa que tiene celdas de World Partition ya compiladas junto a él. `ue-map` exporta uno como `ground:<map>` (el paisaje), `structure:<map>` (las mallas HLOD fusionadas del mapa) y `water:<map>` (sus masas de agua donde están por encima del suelo), en **centímetros** de Unreal, con Y y Z intercambiados: la única exportación que no está en metros. Cómo se lee y se comprueba cada una: [Mapas de Unreal 5](level-unreal-world-partition.md).

| Opción | Por defecto | Significado |
|---|---|---|
| `<map>` | obligatorio | un nombre como lo imprime `ue-maps`, o una parte única de uno |
| `-o`, `--out FILE` | `<map>.glb` | el `.glb` a escribir |
| `--ground-spacing METRES` | 2 | el espaciado de vértices del paisaje en el archivo, redondeado a un número entero de sus propios cuadrados |
| `--no-structures`, `--no-water` | | deja fuera esa parte |

Imprime los triángulos por parte, cuántos componentes de paisaje se leyeron y cuántos de los vértices que guardan dos veces no coinciden. Un mapa de 3 km a 2 m tiene unos 4,6 millones de triángulos de suelo.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` lista cada mundo con terreno, por su carpeta bajo `worlds/`. `enfusion-world` exporta uno: `ground:<world>` (el terreno, con los colores de sus teselas de supertextura), `water:<world>` (el mar, a altura cero) y `structure:<world>` (la caja de cada modelo colocado), en los metros propios del juego: x hacia el este, y hacia arriba, z hacia el norte. Cómo se lee y se comprueba: [Mundos de Arma Reforger](level-arma-reforger.md).

| Opción | Por defecto | Significado |
|---|---|---|
| `<world>` | obligatorio | un mundo como lo imprime `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | el `.glb` a escribir |
| `--install FOLDER` | la biblioteca de Steam que contiene el juego | la carpeta del juego |
| `--ground-spacing METRES` | 2 (el del terreno) | el espaciado de vértices del terreno en el archivo |
| `--texture-size PIXELS` | 4096 | el lado mayor de la imagen de color del suelo; 0 para color plano |
| `--no-structures` | | deja fuera los modelos colocados |
| `--trees` | desactivado | coloca también árboles y otra vegetación, como cajas |

Imprime los triángulos por parte, cuántos vértices de borde de teselas no coinciden, cuántas entidades contiene el archivo del mundo y cuántas cajas se colocaron, y qué se dejó fuera y por qué.

## Variables de entorno {#environment-variables}

| Variable | Efecto |
|---|---|
| `HEAT3D_OODLE` | ruta a un `oo2core_*_win64.dll`, o a una carpeta que lo contenga; mira [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | cualquier valor distinto de vacío, `0`, `false` o `no` desactiva la comprobación de actualizaciones; mira [Actualizaciones](updates.md) |
| `LOCALAPPDATA` | donde se buscan la biblioteca de FH Companion, la carpeta de usuario de BeamNG y la caché de actualizaciones |
| `HEAT3D_COURSE` | solo para pruebas: el recorrido que usa la prueba de bordillos del juego instalado; mira [Desarrollo](development.md) |
