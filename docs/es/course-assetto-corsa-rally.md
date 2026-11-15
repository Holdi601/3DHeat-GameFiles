---
title: Assetto Corsa Rally
nav_order: 3
lang: es
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Exportación de circuito: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally está construido sobre Unreal Engine 5 (5.6.1, una versión modificada) y distribuye su contenido en contenedores IoStore. Ninguno está cifrado. La exportación encuentra la etapa y la orientación de los ejes a partir de la vuelta. Escribe las losetas de suelo propias de la etapa, separadas en carretera y terreno, y texturizadas con el color de suelo horneado de la etapa. Los demás objetos los coloca en colores planos por categoría.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Fuentes: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (instalación, etapas, colocación),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (la exportación).
Los lectores de Unreal en los que se apoya están en [Unreal 5 IoStore](reader-unreal-iostore.md),
y la descompresión, en [Oodle](reader-oodle.md).

**Estado:** comprobado con el juego instalado, con vueltas generadas en un fotograma aleatorio en cada etapa, y encontró la etapa y el fotograma correctos en todos los casos. Todavía no ha pasado por ella ninguna vuelta grabada en el propio juego.

## Encontrar la instalación {#finding-the-install}

- `--install <carpeta>`: la carpeta del juego, su `Content\Paks`, o cualquier carpeta que tenga archivos `.utoc`. La herramienta mira en `<carpeta>`, luego en `<carpeta>\acr\Content\Paks` y después en `<carpeta>\Content\Paks`.
- Si no, se revisa de la misma forma `steamapps\common\Assetto Corsa Rally` en cada biblioteca de Steam.
- Cada `.utoc` de esa carpeta se abre como un único almacén. Los contenedores que no se pueden abrir se omiten. Si ninguno se abre: `no readable IoStore containers in ...`.

La mayoría de los bloques están comprimidos con Oodle, y se busca una biblioteca en el equipo (se busca en cada biblioteca de Steam). Ver [Oodle](reader-oodle.md).

El juego se toma como AC Rally cuando el archivo de la vuelta dice `"game": "assetto-corsa-rally"` (o `acrally`), o cuando pasas `--game acrally`.

## Qué es una etapa {#what-a-stage-is}

Una etapa es un mapa de **World Partition**:

- `Content\Levels\<Stage>.umap` coloca el terreno lejano.
- Las celdas cocinadas en `Content\Levels\<Stage>\_Generated_\*.umap` colocan todo lo demás.

Un nivel cuenta como etapa si su carpeta de entorno, `Content\Environments\<Stage>\`, tiene una carpeta `MeshesTrack`. La herramienta no se guía por los nombres de las losetas, porque una etapa puede nombrarlas por un pueblo en lugar de por su mapa. `--level` se compara sin distinguir mayúsculas con estos nombres de mapa. Un nombre incorrecto lista las etapas que hay.

No hay **ningún paisaje (landscape)**. El suelo son mallas estáticas:

| Losetas | Ruta | Se convierten en |
|---|---|---|
| losetas de pista, unos 175 m, divididas en dos | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` y `..._Terrain_k` | `ground:road` y `ground:terrain` (una loseta de pista sin dividir, como un lago helado, es toda carretera) |
| terreno lejano, losetas de 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Leer las colocaciones {#reading-the-placements}

Lo que coloca una malla es un `StaticMeshComponent`: su `StaticMesh`, y su `RelativeLocation`, `RelativeRotation` y `RelativeScale3D`, cada uno relativo al componente al que está unido (`AttachParent`), hasta la raíz del actor, que está en el mundo.

- Las propiedades son **sin versión (unversioned)**: se guardan por posición en la lista de propiedades de la clase, no por nombre. Se leen con los esquemas de
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (ver [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Un valor igual a la plantilla del componente (su archetype en un Blueprint) no se guarda, así que primero se leen los valores de la plantilla, recursivamente, y los valores propios del componente los sustituyen.
- Se omiten los componentes con `bVisible = 0` o `bHiddenInGame = 1`. También se omiten las mallas cuya ruta contiene `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/` o `_hlod`.
- Las rotaciones usan `FRotationMatrix` de Unreal (pitch, yaw, roll en grados).
- Los duplicados (la misma malla con la misma transformación, a 0,1 cm) se descartan.
- Los componentes que no se pueden leer se cuentan por motivo y se informan, por ejemplo `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Los componentes instanciados** (bosques, casi todos) solo se leen con `--trees`. Esta versión ha reordenado esas clases más allá de las cabeceras del motor, así que sus propiedades no se leen. En su lugar:

- la malla sale de la tabla de dependencias del paquete, donde cada uno de esos componentes lista exactamente una malla estática,
- las instancias salen del bloque nativo que sigue a las propiedades (`[1][1][128][count]` y luego `count` matrices 4x4 de doble precisión),
- se supone que el componente está en la raíz de su actor, que es como los actores de vegetación los colocan.

Las coordenadas son las de Unreal: centímetros, Z hacia arriba, X hacia delante, Y a la derecha, en un marco zurdo.

## Qué etapa, y en qué sentido {#which-stage-and-which-way-round}

El marco de la telemetría no está documentado, así que no se supone: se ajusta.

- **Ocho marcos candidatos.** La Z de Unreal (cm) por 0,01 pasa a ser la altura de la vuelta (y). La X e Y de Unreal pasan a ser la x y la z de la vuelta, intercambiadas o no, cada una con cualquiera de los signos, todo escalado por 0,01 a metros.
- **Una rejilla de alturas de carretera.** Para cada etapa, se coloca cada loseta de carretera (en su nivel de detalle más grosero) y se guarda el vértice de carretera más alto por celda de 2 m.
- **Puntuación.** Se toman hasta 400 muestras de la vuelta, repartidas uniformemente, y se llevan al espacio de Unreal con cada marco. Una muestra está en la carretera cuando, entre las 3 x 3 celdas que la rodean, la altura de carretera más cercana a ella está entre 1 m por debajo y 3 m por encima de la muestra (`ON_ROAD`). La puntuación es la proporción de muestras que están en la carretera.
- **Ganador.** El mejor marco en la mejor etapa, si puntúa al menos un 50%. Si no, la exportación se detiene: `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.`
- **Una vuelta que nombra su circuito.** Si el archivo de la vuelta tiene un campo `track`, primero se prueba, sola, una etapa cuyo nombre coincida de forma aproximada (solo letras y dígitos, y uno contiene al otro). Se acepta solo si puntúa al menos un 80%. Si no, se prueban todas las etapas.
- Con `--level`, solo se prueba esa etapa, en los ocho marcos.

La consola dice, por ejemplo, `on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Después todo se escribe **en el marco de la vuelta**: metros, Y hacia arriba. El sentido de los triángulos se invierte donde una transformación refleja, para que las caras sigan mirando al lado correcto.

## El suelo {#the-ground}

- El corredor es `--margin` metros alrededor de la vuelta, en su propio plano x/z.
- Cada loseta de suelo se coloca en su nivel de detalle más fino, y solo se conservan los triángulos que llegan al corredor.
- Los triángulos se agrupan por tipo (carretera o terreno) y por cuadrado de 512 m en el espacio de Unreal (51.200 cm), y cada cuadrado tiene su propia imagen. Las partes se llaman como `ground:road 1_-4`. Las UV son `(unreal_xy - square_origin) / 51200`.
- Las normales se calculan a partir de los triángulos para todo el archivo.

### La textura del suelo {#the-ground-texture}

Salvo que se use `--no-textures`, cada cuadrado se pinta con dos fuentes, a `--texture-size` píxeles:

1. **El color de suelo horneado.** El `RuntimeVirtualTextureComponent` del mapa de la etapa (su caja usa `RelativeLocation` como esquina y `RelativeScale3D` como tamaño, sin rotación) apunta a una **textura virtual** de streaming: el color de suelo que el juego horneó. Se lee la región del cuadrado, al nivel cuyos píxeles están más cerca del tamaño pedido. Eso son de 13 a 59 cm por píxel, según la etapa.
2. **La imagen satélite** rellena lo que la textura virtual deja en negro. Es la textura `sat*_(b|bc|c|basecolor)` de la etapa, en su carpeta de entorno, leída hasta 4096 px. Su colocación se encuentra con un ajuste por mínimos cuadrados de la primera capa de UV del terreno lejano frente a las x e y del mundo. El ajuste debe ser lineal con un error de 0,01 en el percentil 95, o la imagen no se usa. Si las UV del terreno lejano pasan de 1 (un material que las repite), el mapeo se divide por dos hasta que encajan una vez.

La consola dice cuál se usó, por ejemplo `ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`. Una etapa sin ninguna de las dos se dibuja en colores planos.

## Modelos colocados {#placed-models}

Cada colocación que no es una loseta de suelo se clasifica por su ruta de malla (gana la primera coincidencia):

| Categoría | El nombre de la malla (o la ruta, para árboles) contiene |
|---|---|
| árboles (solo con `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| rocas | `rock`, `cliff`, `boulder`, `stone` |
| bordillos | `kerb`, `curb` |
| barreras | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| señales | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| edificios | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infraestructura | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| objetos (props) | cualquier otra cosa |

- Una copia se considera si su origen está en el corredor de alcance (`margin + 60 m`), y se dibuja si sus límites tocan el corredor.
- Los niveles de detalle siguen a [Niveles de detalle y presupuesto](detail-budget.md): primero bandas de distancia, y luego los modelos más costosos bajan de nivel para encajar en el presupuesto de triángulos. Donde incluso los niveles más gruesos lo superan, se dejan fuera las copias más lejanas, como en BeamNG, hasta que encaja. Los bordillos mantienen el detalle completo y nunca se dejan fuera. El resumen imprime `placed on it (N triangles of a B budget)` y, cuando se han quitado copias, `N copies left out to fit the budget, the furthest from the driving first`.
- Cada categoría es una parte en color plano: `ground:kerbs` para los bordillos, que son superficie de conducción, como en Forza y BeamNG, y `structure:<category>` para el resto:

| Categoría | Color (RGB lineal) |
|---|---|
| barreras | 0.55, 0.52, 0.48 |
| señales | 0.75, 0.72, 0.65 |
| edificios | 0.62, 0.58, 0.52 |
| infraestructura | 0.48, 0.48, 0.50 |
| rocas | 0.45, 0.43, 0.40 |
| objetos (props) | 0.55, 0.45, 0.35 |
| árboles | 0.20, 0.32, 0.14 |
| bordillos | 0.70, 0.25, 0.22 |

Las mallas estáticas que no se pueden leer (mallas esqueléticas, mallas solo Nanite, niveles que no están guardados en línea) se cuentan: `N meshes could not be read`.

## Comprobaciones {#checks-behind-it}

Según el código fuente, en el juego instalado:

- Se lee cada tabla de contenidos (versión 8).
- Cada celda de cada etapa se abre, y cada componente de malla estática y de escena se decodifica terminando exactamente en el final nativo de su clase.
- Casi toda malla estática muestreada se decodifica (el resto son esqueléticas). La extensión decodificada de una loseta de carretera coincide con los límites que guarda.
- Los niveles de mip de una imagen satélite tienen exactamente los tamaños de sus entradas bulk.
- Las losetas de un trozo de textura virtual se cuentan hasta el byte, y las losetas de carretera caen sobre la carretera que muestra.

## Carencias conocidas {#known-gaps}

- Las propiedades propias de los componentes instanciados no se leen (ver arriba). Su colocación supone que están en la raíz del actor.
- Los bosques que genera PCG en tiempo de ejecución no se guardan en los archivos y no se pueden exportar.
- Las mallas de spline (muros de reaparición invisibles), los componentes de calcomanías y las texturas propias de los modelos colocados no se dibujan. Los modelos van en colores planos.
- `--season` no tiene efecto.
- Un parche del juego puede mover las posiciones de las propiedades. El lector se detiene en lugar de leer mal, y el circuito informa de cuántos componentes han fallado.
