---
title: ForzaTech
nav_order: 7
lang: es
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, muestras, colocaciones {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon funciona con ForzaTech, el motor propio de Turn 10. Estos lectores llevan un circuito desde sus archivos hasta triángulos colocados y texturizados. Se llega a ellos a través de `course`, `courses` y `terrain` (ver [Forza Horizon](course-forza-horizon.md)). `identify` reconoce un `.minizip` y un `.modelbin` suelto, y `list` y `extract` aceptan un `.minizip`, por los nombres de la `ChunkContentsMiniZip<n>.txt` que está a su lado o por número de entrada (`#12`).

| Formato | Módulo |
|---|---|
| archivos `.minizip` y sus listas de nombres | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modelos `.modelbin` y terreno | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| muestras de textura `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| archivos de colocación `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` y hashes de textura de materiales | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| losetas de terreno por lugar | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza también guarda buena parte de su contenido en archivos ZIP normales bajo `media\`. `zipfile` de Python los abre, y `forzatech.models_in_archive()` lista sus entradas `.modelbin`. La geometría del circuito está en los archivos `.minizip`.

## `.minizip`: un archivo sin nombres {#minizip-an-archive-with-no-names}

Un circuito trae cuatro archivos `GeoChunk<n>.minizip`, de decenas de gigabytes cada uno en un mapa de mundo abierto, con cientos de miles de entradas. **Los archivos no guardan ningún nombre**: ni tabla de nombres ni cabecera por entrada, solo un ordinal. Los nombres están en `ChunkContentsMiniZip<n>.txt`, junto a cada archivo, una línea por entrada en orden de entrada (`<build path>zipcache\pc\<path>|<bundle>`). Ese emparejamiento es la única forma de pedir un archivo. Todo lo que hay hasta `zipcache\pc\` se descarta, y las búsquedas ignoran las mayúsculas.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tres detalles del índice siguen produciendo salida cuando se leen mal. El lector los acierta los tres:

| Detalle | Lo que hace un lector descuidado | Cómo se ve |
|---|---|---|
| la base del segmento es de **64 bits** | la lee como u32 más relleno | correcta para los primeros 4 GB, y después ruido de la longitud correcta |
| la base está **alineada a 8 bytes** | ignora la palabra de relleno tras la tabla de paquetes | en archivos con un número par de paquetes, cada entrada reclama un códec que no existe |
| la longitud guardada de una entrada es el hueco hasta la siguiente entrada (o hasta la base del siguiente segmento) **menos su relleno** (bits de flags 12-13) | usa el hueco entero | LZ4 rechaza el bloque directamente |

Los códecs son los cinco bits bajos de los flags: `0x00` sin comprimir, `0x08` deflate crudo, `0x1F` bloque LZ4. Cualquier otro se rechaza. Cada entrada debe descomprimirse exactamente al tamaño que declara, o se rechaza. El índice (unos 5 MB) se lee una vez, y los datos se leen buscando posición.

La cabecera se comprueba: la marca, una cabecera de 32 bytes, y un número de segmentos que coincide con `ceil(entries / per segment)`.

**Verificado:** entradas muestreadas en cada archivo de un mapa, cada una descomprimiéndose exactamente a su longitud declarada con los tres códecs.

## `.modelbin`: el contenedor de fragmentos {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- El tamaño de archivo declarado debe ser igual al tamaño real.
- La **cadena**: cada fragmento empieza donde terminó el anterior, redondeado a 4 bytes. Nada en el archivo lo afirma, así que es una prueba: un registro leído con el paso equivocado no produce esa cadena. Se cumplió en los 252 modelos muestreados.
- Un archivo `PGZP` dado al lector de modelos se nombra como "a ForzaTech .minizip archive, not a model" y se señala a `minizip.py`, en lugar de rechazarse sin más.

La geometría sale de estos fragmentos:

| Fragmento | Contiene |
|---|---|
| `VLay` | un diseño de vértices: nombres de atributo, luego elementos (índice de nombre u16, canal u16, búfer, formato DXGI, desplazamiento); el número de elementos es un u16 |
| `VerB` | un búfer de vértices tras una cabecera de 16 bytes (recuento, tamaño, paso u16, atributos u16, formato) |
| `IndB` | el búfer de índices, misma cabecera |
| `Mesh` | una submalla: material, máscara de nivel de detalle, rango de índices, diseño, búfer, paso, tabla de variantes y una caja de posición al final |
| `MatI` | una instancia de material: su ruta `.materialbin` y hashes de textura |

### Posiciones y la caja {#positions-and-the-box}

Las posiciones son `R16G16B16A16_SNORM` (formato 13): cuatro shorts con signo por vértice. `position = short / 32767 * scale + bias`, donde scale y bias son los últimos 32 bytes del fragmento `Mesh` (dos float4). El bias está en **las coordenadas del mundo del juego**, así que una loseta de terreno cae donde la pone el juego sin ninguna transformación de instancia. Por eso basta una vuelta de telemetría para pedir un trozo de mapa.

Cada submalla de un modelo lleva la misma caja (comprobado en 860 de ellas).

### El diseño de vértices {#the-vertex-layout}

Un único búfer de posición cubre todos los vértices. Los demás atributos se reparten en grupos de vértices consecutivos, cada uno con su propio búfer y su propio diseño: la carretera cerca de un cruce lleva tres conjuntos de UV y dos tangentes, y el talud junto a ella solo una normal. Cada atributo que no es posición ocupa cuatro bytes. Qué diseño describe qué búfer se toma de las submallas que dibujan desde él, porque los diseños y los búferes no están en el mismo orden (igual, desplazado en uno o permutado, según el modelo).

| Formato DXGI | Código | Usado para |
|---|---|---|
| R16G16B16A16_SNORM | 13 | posición (el cuarto short es la x de la normal) |
| R16G16_SNORM | 37 | normal y, z |
| R16G16_UNORM | 35 | un par de UV (canal = qué conjunto) |
| R8G8B8A8_UNORM | 28 | color o pesos de mezcla |
| R10G10B10A2_UNORM | 24 | tangente (no decodificada) |
| R16_UINT | 57 | índices |

**La normal está partida.** `NORMAL` guarda y y z. La x es el cuarto short de la posición, que parecía relleno. En cientos de miles de vértices de terreno se correlaciona +0,92 con la x de la normal del triángulo, y con nada más. Con ella, el 96% de los vértices de suelo en pendiente quedan a 18° de la normal calculada. Todas las codificaciones de dos componentes probadas sin ella (octaédrica en las 48 disposiciones, entre ellas) acertaban y y z, y fallaban x.

Otros formatos de posición o de índice se **rechazan** (`only 13 (four shorts, scaled) is implemented`; `only unsigned shorts are implemented`).

### Submallas {#submeshes}

Un registro `Mesh` ocupa 238 bytes en la forma estándar. Los más largos llevan una tabla de **variantes** de material más larga al principio, 238 + 8 x recuento - 4 bytes, y cada campo posterior se desplaza exactamente esa cantidad. Los más cortos (218 bytes, algún terreno) mantienen los desplazamientos. Cada entrada de variante es `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. La máscara de nivel de detalle es un u16, un bit por nivel desde el bit 1.

Nada se fía solo. Los rangos de índices deben cubrir exactamente el búfer de índices, cada recuento de índices debe ser igual a 3 x `triangles`, y el paso que nombra una submalla debe ser el de su búfer. Una tabla que falla se rechaza entera, porque etiquetar triángulos a partir de campos mal leídos es peor que no etiquetarlos. En miles de submallas muestreadas, todas cuyo índice de búfer está en rango pasan.

### Materiales y hashes de textura {#materials-and-texture-hashes}

Un `MatI` nombra su material con una ruta `Game:...\x.materialbin`, encontrada buscando en el fragmento. Sus texturas son registros `u32 slot, u32, u32 hash` separados 33 bytes, sin alinear, así que el fragmento se busca en cada desplazamiento de byte en busca de palabras que son hashes de textura conocidos. Esos vienen del `AssetManifest.xml` del circuito (`<Texture Source="...\name.swatch" SourceHash="...">`, leído hasta `</Textures>`). El slot `0x88B483AA` es el color base del shader estándar. Cómo se elige después la textura de color está en [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: muestras de textura {#pb-texture-swatches}

Una muestra es el mismo contenedor `burG` que un modelo: una cabecera `HCXT` de 96 bytes en el byte 44, y luego un fragmento de píxeles. La cabecera contiene el GUID de la textura (el del nombre de archivo), ancho y alto, el número de mips, y el **código de formato en el byte 72** (la numeración propia de ForzaTech). El byte 84 contiene el número de bytes de píxeles.

| Código | Formato | Identificado como |
|---|---|---|
| 0 | BC1, medio byte por píxel | decodifica a un bordillo rojo y blanco (ruido bajo BC4) |
| 9 | BC7, un byte por píxel | decodifica a una loseta de terreno con el circuito visible |
| 13 | RGBA8, cuatro bytes por píxel | sin codificar |
| otro | rechazado | `texture format N has not been identified; refusing to guess` |

Los formatos se identificaron decodificando archivos reales de todas las formas que permite el tamaño del contenido. El byte 47, que una versión anterior tomaba por el formato, es 4 en todas las texturas muestreadas. Solo se decodifica el mip superior de un archivo. Cada resolución es una entrada propia, `<name>_<guid>_quality<n>.pb`, de calidad 1 (la más pequeña) a 5 (la mayor). En los mapas de terreno, las dos mayores están en un archivo distinto del resto. La decodificación pasa por el decodificador BCn de Pillow, mediante una cabecera DDS generada.

## Archivos de colocación (.pgeo) {#placement-files-pgeo}

Un archivo por categoría y por celda espacial: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. La ruta sola indica el cuadrado de la celda y la categoría, así que los archivos se pueden filtrar sin abrirlos.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Cómo se decidió cada campo:

| Campo | Decidido por |
|---|---|
| la posición es coma fija 16.16, no una fracción de la caja | los guardarraíles consecutivos están exactamente a 4,000 m (la longitud del modelo) |
| magnitud con signo, no complemento a dos | el complemento a dos ponía las coordenadas negativas a decenas de kilómetros del mapa; con el bit 31 como signo, cada registro de cada categoría muestreada cae dentro de la caja de su archivo |
| los vectores son los ejes propios del modelo | el final de cada guardarraíl cae en el inicio del siguiente: 93,5% a menos de 5 cm, mediana 0,000 m |
| el byte 60 es la variante | las cinco copias de un cartel leen 0, 2, 2, 3, 4, mientras que todos los guardarraíles leen 0 |

Solo los nombres que terminan en `_3D` son registros de modelo. La tabla de variantes que va antes lista nombres sin ese sufijo, y leídos como registros caen en el infinito. Un registro candidato solo se acepta si su recuento cabe en el archivo, y se descartan las instancias con números no finitos.

## No implementado {#not-implemented}

- Formatos de vértices e índices distintos de los de arriba (se rechazan).
- Formatos de textura distintos de 0, 9, 13 (se rechazan).
- Tangentes (se leen y se saltan, no se usan).
- Las capas de material del shader del terreno. La textura del suelo es una interpretación de los mapas de losetas (ver [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
