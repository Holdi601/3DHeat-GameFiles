---
title: Archivos de BeamNG
nav_order: 8
lang: "es"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Archivos de BeamNG: archivos de nivel, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive distribuye archivos zip normales, así que no hay contenedor que haga falta ingeniar en sentido inverso. El trabajo está en leer un nivel **como lo hace el juego**: montar los archivos en un único sistema de archivos, seguir los archivos de escena, y decodificar el terreno y las formas compiladas. Se llega a estos lectores a través de la exportación de circuito de [BeamNG.drive](course-beamng.md). `identify` también reconoce un zip de nivel, un `.cdae` y un `.ter`, y `list` y `extract` aceptan cualquiera de los zip.

Fuentes: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## El sistema de archivos montado {#the-mounted-file-system}

`Files.of_install(game)` construye un único índice sin distinguir mayúsculas sobre `gameengine.zip`, los zip de `content` (salvo vehículos y sonidos), y los mods del usuario (`mods\*.zip`, `mods\unpacked\*`, y una carpeta `levels` del usuario). Las adiciones posteriores anulan a las anteriores, como en el juego. Las búsquedas ignoran las mayúsculas porque las referencias de los propios niveles no coinciden con los archivos en mayúsculas y minúsculas (`.DAE` para un `.dae`). Los detalles están en [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` encuentra una ruta como lo hace el juego: tal cual se dio, relativa al archivo que la nombró, `x.png` como `x.dds`, `x.dae` como `x.cdae` (preferido), y a través de un archivo JSON `x.png.link` cuyo `path` apunta a `/assets`.

## Archivos de escena {#scene-files}

| Origen | Formato | Lectura |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | un objeto JSON por línea, o un único array o mapa JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | las mismas clases, para niveles antiguos sin `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript o JSON | hijos colocados respecto al prefab, hasta 8 niveles de profundidad |
| `levels\<name>\forest\*.forest4.json` | una instancia por línea | tipadas por registros `TSForestItemData` en `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | el título del nivel (se ignoran las claves de traducción) |

**Transformaciones.** `rotationMatrix` son nueve números cuyas **filas** son los ejes propios del objeto en el mundo. Las secciones de guardarraíl encadenadas a lo largo de una carretera van a lo largo de la fila 0 (92%), y la fila de arriba se inclina con la pendiente de la carretera. Los prefabs antiguos dan `rotation = "x y z degrees"`, un giro diestro de ese ángulo (el 92% de las cadenas de raíles encajan con él, y el 19% con el sentido contrario). La escala multiplica las filas, y `position` (o `pos`) es la última fila. La transformación de un hijo de prefab se compone con la del prefab. El `groupPosition` del prefab es un pivote del editor y **no** se resta: un prefab de carrito solo queda sobre el suelo sin él.

Los números de TorqueScript se leen con un patrón tolerante, porque algunos prefabs incluidos escriben valores como `-0.99563-0.0` sin espacio.

## Terreno: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Altura en metros: `position.z + h * maxHeight / 65535`, con `position`, `squareSize` y `maxHeight` del `TerrainBlock` (valores por defecto 0, 1 y 2048).
- Las filas van a lo largo de +y. El punto de rejilla (i, j) está en `(position.x + i * squareSize, position.y + j * squareSize)`.
- La capa 255 es un hueco.

Comprobado: los nodos de carretera caen sobre el terreno a 1-2 cm (mediana) en tres niveles. `h / 32`, o el otro orden de ejes, falla por decenas o cientos de metros.

## Materiales {#materials}

Cada `*.materials.json` fuera de `levels\`, más el del nivel actual, indexado por `mapTo`, `name` y clave:

| Clase | Campos usados |
|---|---|
| `Material`, `CustomMaterial` | mapa de color (`baseColorMap`, `colorMap` o `diffuseMap`, primera etapa), factor de color, mapa de opacidad y su factor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | mapa base y `diffuseSize`, mapa de detalle, tamaño y fuerza, mapa macro, tamaño y fuerza, `groundmodelName`, `annotation` |

Las imágenes se decodifican con Pillow (DDS, PNG y demás), usando un tamaño reducido cuando es posible, y se guardan en caché por tamaño. Una textura que no se puede leer cae a color plano.

## Formas compiladas: `.cdae` {#compiled-shapes-cdae}

`.cdae` es la caché propia del juego de cada archivo Collada, escrita como MessagePack. Su diseño está **documentado por BeamNG** (documentation.beamng.com/modding/file_formats/cdae/) y el lector lo sigue:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Lo que se lee: límites, nodos, objetos, `details` (niveles de detalle), rotaciones por defecto de los nodos (`Quat16`) y traslaciones, los vértices, UV, normales, colores, primitivas e índices de cada malla, y los nombres de material. Los nombres de material se encuentran al final del flujo, porque las secuencias de un prop animado vienen antes en una forma que no está documentada.

Dos cosas que la documentación no detalla, establecidas comparando con los archivos `.dae` de los que se construyeron las formas:

- **Las rotaciones de nodo son las de Torque.** Un `Quat16` leído de la forma de libro se gira al revés. Su matriz hay que **transponerla**. Con eso, los límites del mundo de cada nodo coinciden con el Collada al milímetro. Sin ello, la mediana queda a 38 cm de distancia.
- **Las unidades y los ejes ya están aplicados.** Un archivo Collada hecho en centímetros o con Y hacia arriba sale de la caché en metros, con Z hacia arriba.

Los niveles de detalle son los `details` con tamaño no negativo, del mayor al menor. Los tamaños negativos son mallas de colisión y de línea de visión, que nunca se dibujan. Los objetos llamados `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` o `imposter` nunca se dibujan. Solo se dibujan las mallas estándar y ordenadas. No se dibujan las mallas con esqueleto (personajes, vehículos) ni las mallas de calcomanía. Las tiras y abanicos de triángulos se desenrollan, y las caras se reorientan para coincidir con las normales guardadas, algo que el propio orden de Torque no garantiza.

Comprobado: casi toda forma de juego se lee. Las otras dos son de una versión antigua.

## Respaldo Collada: `.dae` {#collada-fallback-dae}

Para formas sin `.cdae` (mods, y alguna forma suelta cuya caché es más antigua), el archivo Collada se lee como lo lee el importador de Torque, en la misma estructura:

- Niveles de detalle según la nomenclatura de Torque: el número final del nombre de un nodo de malla es el tamaño en píxeles con el que se dibuja (`barrier75`, `barrier40`). Un número negativo, o un nombre `collision`/`Colmesh`/`LOS`/`nulldetail`, nunca se dibuja. Una forma sin esa convención es un solo nivel.
- Unidades desde `<unit meter>`, y de Y hacia arriba a Z hacia arriba.
- UV volteadas al convenio de la caché (v va hacia abajo en la imagen).

Comprobado contra los `.cdae` del propio juego de los mismos archivos: casi todos los límites muestreados coinciden dentro de 1 cm, 583 con el mismo número de triángulos, y el 94% de las UV de materiales son idénticas. La prueba con juego instalado exige que el 90% de hasta 60 pares de formas del archivo de arte compartido coincida dentro de 1 cm.

## No se lee {#not-read}

- Cobertura de suelo (hierba procedural), y todo lo que se genera en tiempo de ejecución.
- Secuencias animadas y skinning.
- Vehículos y sonidos (nunca se montan).
