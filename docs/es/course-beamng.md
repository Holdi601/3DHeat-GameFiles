---
title: "BeamNG.drive"
nav_order: 2
lang: es
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Exportar recorrido: BeamNG.drive {#course-export-beamngdrive}

La exportación de BeamNG lee un nivel tal como lo monta el juego, y luego escribe el mismo tipo de archivo que escribe la de Forza: suelo por cuadrado de 512 m con una textura horneada, la carretera y el suelo suelto como partes propias, los modelos colocados por categoría, y el agua.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Fuentes: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (instalación, sistema de archivos, escena, terreno, materiales),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (la exportación),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) y
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (formas).
Formatos de archivo con detalle: [Archivos de BeamNG](reader-beamng.md).

## El marco de la vuelta {#the-laps-frame}

La exportación `course` espera posiciones de BeamNG en el **marco del visor**: `(x, z, -y)` del mundo de BeamNG con Z hacia arriba, en metros. Es la rotación que aplica la grabadora de telemetría de 3DHeat. La exportación devuelve la vuelta al marco de BeamNG (`(x, -z, y)`), trabaja allí y vuelve a escribirlo todo en el marco del visor. Es una rotación, no un espejo, así que nada sale reflejado. Una vuelta grabada en el marco crudo de BeamNG no quedaría colocada. Esto no se ha probado con otras grabadoras.

El juego se toma como BeamNG cuando el archivo `heat3d-lap` dice `"game": "beamng"`, o cuando pasas `--game beamng`.

## Cómo se encuentra la instalación {#finding-the-install}

- `--install <folder>`: la carpeta que contiene `gameengine.zip` y `content`.
- Si no, se comprueba en cada biblioteca de Steam la carpeta `steamapps\common\BeamNG.drive`, buscando esos dos elementos.
- Si ninguna de las dos cosas funciona: "no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip)."

## El sistema de archivos {#the-file-system}

BeamNG distribuye archivos zip normales y los monta en un solo sistema de archivos al que se refieren los niveles (`/art/shapes/...`, `/assets/materials/...`). La exportación construye lo mismo: un único índice sin distinguir mayúsculas sobre

1. `gameengine.zip`,
2. cada `*.zip` bajo `content`, salvo `content\vehicles\*` y los archivos cuyo nombre empieza por `art_sound` o `audio`,
3. el contenido del usuario, con la disposición más reciente primero: bajo `%LOCALAPPDATA%\BeamNG\BeamNG.drive` y `%LOCALAPPDATA%\BeamNG.drive`, la carpeta `current` y la carpeta de versión con el número más alto. De cada una: `mods\*.zip`, cada carpeta de `mods\unpacked`, y la propia carpeta del usuario si tiene una carpeta `levels`.

Las adiciones posteriores ganan, como en el juego, así que un mod sustituye lo que sobrescribe. Los mods siempre se incluyen en una exportación de recorrido.

Las rutas que nombra un nivel se resuelven como lo hace el juego: tal como están, luego relativas al archivo que las nombró, y para cada una también como el `.dds` en que se compiló una textura, el `.cdae` en que se compiló un `.dae`, o a través de un archivo `.link` que apunta a `/assets`.

## Qué nivel {#which-level}

Sin `--level`, cada nivel se puntúa según cuánta parte de la vuelta está en él:

- Se usan hasta 500 muestras de la vuelta, repartidas de manera uniforme.
- Para el `TerrainBlock` de cada nivel, la extensión del terreno se lee de los primeros cinco bytes de su archivo `.ter`, así que un nivel en el que la vuelta no está para nada no cuesta nada. Si al menos el 30 % de las muestras están dentro de la extensión, se leen las alturas. Una muestra cuenta como **sobre** el terreno cuando está entre 1 m por debajo y 3 m por encima de él (`ON_GROUND`), porque el punto de referencia de un coche es su carrocería, no sus neumáticos.
- Si ningún nivel llega al 50 % o más, los niveles también se puntúan por sus **carreteras**. Algunos niveles continúan más allá de su mapa de alturas (sus bordes siguen como láminas de roca). Una muestra está sobre una carretera cuando cae dentro de la semianchura de la carretera más 4 m (al menos 6 m) de un segmento `DecalRoad`, y entre 2 m por debajo y 4 m por encima de él.
- Gana el mejor nivel si puntúa al menos un 30 %. Si no, la exportación se detiene y muestra los tres mejores: "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

La consola dice `on <level>: 87% of the lap lies on its terrain` (o `roads`). `--level` se compara sin distinguir mayúsculas con los nombres de carpeta de los niveles.

## Cómo se lee el nivel {#reading-the-level}

De qué está hecho un nivel, cada parte comprobada con los niveles incluidos (detalles en [Archivos de BeamNG](reader-beamng.md)):

- **Escena**: `levels\<name>\main\**\*.level.json` (un objeto JSON por línea, o un array JSON), o un archivo `.mis` en los niveles antiguos. La herramienta lee los objetos `TSStatic` (modelos colocados, sin los ocultos), los objetos `Prefab` (anidados hasta 8 niveles, `.prefab` de TorqueScript o `.prefab.json`), los objetos `DecalRoad` (carreteras pintadas), `TerrainBlock`, `WaterPlane`, `WaterBlock` y `River`.
- **Elementos de bosque**: `levels\<name>\forest\*.forest4.json`, tipados con los registros de `managedItemData.json`. Las barreras, vallas y rocas son elementos de bosque tan a menudo como lo son los árboles.
- **Terreno**: el mapa de alturas `.ter` y su mapa de capas.
- **Materiales**: cada `*.materials.json` fuera de `levels\`, más los de este nivel.

## El corredor y las calcomanías de carretera {#the-corridor-and-the-road-decals}

El corredor es de `--margin` metros alrededor de la vuelta, en el plano x/y de BeamNG (mira [Exportar recorrido](course-export.md#the-corridor)). Un corredor de alcance de `margin + 60 m` selecciona los candidatos.

**Las calcomanías de carretera** (`DecalRoad`) son donde están la mayoría de las carreteras de BeamNG: pintadas sobre el terreno, no modeladas. Las calcomanías cuya extensión toca el corredor de alcance se toman en el orden de dibujo del juego (`renderPriority` descendente, y luego orden de archivo), y se disponen como cintas:

- Los nodos (x, y, z, ancho) se interpolan con una **spline Catmull-Rom centrípeta** cada 1 m aproximadamente. La variante uniforme da la vuelta sobre sí misma donde los nodos se agrupan en una horquilla. Las carreteras cerradas se cierran.
- Cada borde toma la altura del terreno donde el terreno está a 1,5 m de la altura propia de la carretera, y mantiene la altura de la carretera en el resto (en un puente).
- El nombre del material decide qué pinta una calcomanía:

| Tipo | El nombre del material coincide (gana la primera coincidencia) |
|---|---|
| marcas de neumáticos | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| superposición (solo cosmética) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| marcas | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| suelto | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| carretera | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| superposición | cualquier otra cosa |

## El suelo {#the-ground}

El mapa de alturas del terreno dentro del corredor se convierte en triángulos:

- Un cuadrilátero por cuadrado de terreno cuyo centro está en el corredor. Los cuadrados con capa 255 (huecos) se omiten. Cada cuadrilátero son dos triángulos, con la diagonal alternando como lo hace el terreno de Torque.
- Las alturas son `position.z + h * maxHeight / 65535`. Las normales salen de las diferencias de altura.
- Cada cuadrado se clasifica por su **capa**: el nombre de la capa con su modelo de suelo y su anotación del material de terreno. Las palabras de pavimento lo hacen `road`, `grass/forest/rock/moss/leaves/cliff/stone` lo hacen `terrain`, y las palabras de suelo suelto lo hacen `loose` (grava y tierra). Lo demás es `terrain`.
- Después, las **calcomanías de carretera y de suelo suelto anulan los cuadrados que cubren**, en orden de dibujo, así que decide la última calcomanía pintada.
- Los vértices se separan por cuadrado de 512 m (`floor(x / 512)`, `floor(y / 512)`), de modo que cada parte cae en exactamente una imagen: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

La consola imprime `what the ground is made of` con el número de triángulos por tipo.

### Superficie de conducción modelada {#modelled-driving-surface}

Los circuitos de BeamNG son modelos tanto como son terreno. El trazado de una pista puede ser una sola malla con sus líneas, sus gomas y sus bandas de rugosidad como mallas propias encima. Por eso, los modelos colocados de las categorías carretera, bordillos, arcén, objetos y puentes se buscan en busca de superficie de conducción. Por material:

| Superficie | Decidida por (la primera coincidencia) |
|---|---|
| marcas de neumáticos | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` en el nombre, el tipo de suelo o la anotación |
| marcas | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` en el nombre del material |
| bordillos | `rumble`, `kerb`, `curb` |
| carretera | tipo de suelo `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, o el nombre contiene `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| suelto | tipo de suelo `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| arcén | `sidewalk` |
| (la categoría propia del modelo) | para los modelos ya clasificados como carretera, bordillos o arcén |

De esos materiales, los triángulos **que miran hacia arriba** (normal z mayor que 0,5) dentro del corredor se sacan del modelo y pasan a ser suelo. Se pintan en la textura horneada de la loseta y se escriben como partes como `ground:road 3_-2 asphalt_light`. Las marcas y las huellas de neumáticos solo se pintan. Los triángulos restantes del modelo se quedan con el modelo. Estos modelos nunca se simplifican ni se dejan fuera por el presupuesto, porque un trazado grosero es un trazado equivocado.

## La textura horneada del suelo {#the-baked-ground-texture}

Cada cuadrado de 512 m que tiene suelo recibe una imagen de `--texture-size` píxeles (2048 = 25 cm por píxel), dibujada como el juego dibuja su suelo:

1. **Capas del terreno.** Por píxel, las capas de los cuatro cuadrados de terreno que lo rodean se mezclan de forma bilineal. Cada capa se colorea como la colorea el juego: el **mapa base** del material estirado sobre `diffuseSize` metros (o sobre todo el terreno), luego los mapas de **detalle** y **macro** como superposiciones grises (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutro). Sus valores por defecto se repiten cada 2 m y cada 60 m, con intensidades de 0,5 y 0,3, salvo que el material diga otra cosa. Una capa sin material toma el color plano de su superficie. La fila 0 del mapa base es el norte.
2. **Calcomanías de carretera** que se pintan solo sobre el terreno, en orden de dibujo, cada una con su propia textura, su mapa de opacidad, su tinte y su opacidad, a lo largo de la cinta. Los niveles incluidos usan prioridades alrededor de 12-16 para las bases de asfalto, 10 para las marcas y 4 para las gomas.
3. **Superficie de conducción modelada** vista desde arriba: primero las bases, luego las superposiciones, cada una en la textura repetida propia del modelo a un texel por píxel de horneado.
4. **Calcomanías que también se proyectan sobre los objetos** (`overObjects`), al final.

Con `--no-textures`, no se hornea nada: las partes del suelo reciben colores planos, y las marcas y huellas de neumáticos modeladas se convierten en partes propias, levantadas **3 cm**.

## Modelos colocados {#placed-models}

Los candidatos son todos los `TSStatic`, los hijos de prefabricados y los elementos de bosque cuyo origen está en el corredor de alcance. Un candidato se dibuja si la caja delimitadora mundial de su forma toca el corredor.

La **categoría** sale de la anotación del propio nivel y de la ruta de la forma. Gana la primera regla que coincide:

| Categoría | Anotación | La ruta o el nombre contienen |
|---|---|---|
| fondo (nunca se dibuja) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| bordillos | | `kerb`, `curb`, `rumble` |
| carretera | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| arcén | `SIDEWALK`, `COBBLESTONE` | |
| árboles (solo con `--trees`) | `NATURE` | tree, foliage, bush, grass, plant y palabras parecidas |
| rocas | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barreras | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| señales | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| puentes | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infraestructura | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| edificios | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| objetos | | cualquier otra cosa |

**Las formas** se leen del `.cdae` compilado, o del `.dae` de Collada donde no hay caché (mods). Una forma que no se puede leer se cuenta: `N copies of M models could not be read`. Los materiales con nombre o textura `invisible`, `collision` o `nodraw` nunca se dibujan.

**Texturas.** Los modelos se agrupan por categoría y material en partes con el nombre `structure:<category> <material>` (o `ground:kerbs <material>`). Un grupo recibe la textura de color de su material a hasta **256 px** solo si sus UV se quedan entre 0 y 1 (el 98 % de los vértices entre -0,02 y 1,02). El visor empaqueta las texturas en un atlas y no puede repetir una. Un grupo cuya textura se repite se dibuja con el color medio de la textura (ponderado por alfa, en sRGB, por el tinte del material), o con el color de la categoría si no tiene textura.

**El detalle** sigue el esquema común de [Niveles de detalle y presupuesto](detail-budget.md). Los niveles de detalle de BeamNG son los `details` de la forma (primero el de mayor tamaño en píxeles). Si se pasa del presupuesto, primero se quitan las copias más lejanas. Los bordillos y los modelos que llevan superficie de conducción nunca se simplifican ni se dejan fuera.

`--no-placed` quita las estructuras, pero sigue manteniendo la superficie de conducción modelada. `--trees` añade la categoría de árboles.

## Agua {#water}

| Fuente | Se dibuja como |
|---|---|
| `WaterPlane` (el mar) | un cuadrilátero de 4 m a la altura del agua por cada celda del corredor donde ningún terreno llega a esa altura |
| `WaterBlock` | un cuadrilátero, el cuadrado unidad en z local = 0 en la transformación del bloque (así que su escala fija el tamaño), si toca el corredor; no está comprobado si z = 0 es la superficie del bloque |
| `River` | una cinta a través de sus nodos si toca el corredor |

Toda el agua es una sola parte plana, `water:water`.

## Lo que no se dibuja {#not-drawn}

- La cubierta del suelo (hierba procedural).
- El decorado colocado en el borde del mundo (`backdrop` y similares).
- Las texturas repetidas de los modelos, que salen como un color medio (mira arriba).
- Las mallas esqueletizadas (vehículos, personajes) y las mallas de calcomanía dentro de las formas.

## Comprobaciones que lo respaldan {#checks-behind-it}

Según el código fuente, medidas en los niveles incluidos:

- Los nodos de carretera están sobre el terreno a 1-2 cm (mediana) en los niveles comprobados, con `h * maxHeight / 65535` y las filas a lo largo de +y. `h / 32` o el otro orden de ejes fallan por decenas o cientos de metros.
- Las secciones de rail encadenadas a lo largo de una carretera siguen la fila 0 de `rotationMatrix` (la gran mayoría).
- La rotación del nodo `.cdae` tiene que transponerse. Con eso, los límites del mundo coinciden con el `.dae` de origen hasta el milímetro. Sin transponer, quedan a 38 cm (mediana).
- Exportado en varios niveles incluidos de todo tipo, en segundos o minutos cada uno.
