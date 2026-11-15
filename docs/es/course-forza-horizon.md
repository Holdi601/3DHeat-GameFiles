---
title: "Forza Horizon"
nav_order: 1
lang: "es"
source: course-forza-horizon.md
source_hash: "7b7eaaf2d8b9"
nav_exclude: true
search_exclude: true
---
# Exportar recorrido: Forza Horizon {#course-export-forza-horizon}

La exportación de Forza lee el circuito directamente de los archivos ForzaTech del juego: el terreno con la carretera, el arcén y la hierba separados, una textura del suelo horneada a partir de los propios mapas de suelo del juego, y cada modelo colocado con su propia textura (bordillos, guardarraíles, muros de neumáticos, señales, objetos, edificios).

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Fuentes: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py).
Los propios formatos de contenedor están en [ForzaTech](reader-forzatech.md).

## Cómo se encuentra el juego instalado {#finding-the-installed-game}

Nadie debería tener que escribir una ruta como
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, así que la ruta se calcula sola:

1. **Bibliotecas de Steam.** Se lee `config\libraryfolders.vdf` de Steam, en `C:\Program Files (x86)\Steam` o `C:\Program Files\Steam`, y cada entrada `"path"` es una biblioteca. Se busca en el `steamapps\common` de cada biblioteca.
2. **Microsoft Store.** Se busca `C:\XboxGames` si existe. Allí el juego está un nivel más abajo, en `<game>\Content`.
3. Una **carpeta de juego** es cualquier subcarpeta de esas que tenga una carpeta `media\Tracks`, sea cual sea su nombre.
4. Una **carpeta de circuito** es cualquier carpeta bajo `media\Tracks` que contenga un `GeoChunk0.minizip`. Se reconoce por su contenido, no por su nombre, así que un circuito con un nombre que nadie ha visto antes también se encuentra.

Si el juego está en otro sitio, pasa la carpeta del circuito con `--track`; mira [Solución de problemas](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` se salta todo esto.

Una carpeta de circuito contiene lo que lee la exportación:

| Archivo | Qué es |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | los archivos: todos los modelos, texturas y archivos de colocación, sin nombres dentro |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | una línea por entrada del archivo, en el orden de las entradas: la única fuente de nombres |
| `AssetManifest.xml` | cada textura que trae el circuito, con el hash por el que los materiales la nombran |

## Qué circuito {#which-track}

Un juego trae más de una carpeta de circuito (el mapa de mundo abierto, un garaje o dos). El correcto se elige por **coordenadas, no por nombre**:

- La pregunta es la caja delimitadora de la vuelta, ampliada con `--margin`.
- Para cada carpeta de circuito se leen como texto, sin abrir ningún archivo, los cuatro manifiestos `ChunkContentsMiniZip*.txt`. Cada nombre de loseta de terreno (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) lleva su posición en la cuadrícula. La herramienta cuenta cuántas losetas distintas caen dentro de la caja.
- Gana el circuito con más losetas allí. Si ningún circuito tiene ninguna, la exportación se detiene con "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."

Un circuito completo responde en menos de un segundo. Un emparejamiento por nombre podría elegir el mapa equivocado, y un mapa equivocado parece tan plausible como el correcto.

La consola dice `on <track>, in <game folder>`.

## Terreno {#terrain}

Cómo se encuentra el terreno (en `forzaterrain.py`):

- Los manifiestos nombran el terreno como un índice espacial:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Los dos números son coordenadas de cuadrícula que **avanzan de 1023 en 1023**, y cada paso de la cuadrícula es una loseta de **512 m**. La loseta `x-2046` es `-2046 / 1023 = -2`, que empieza en `-2 * 512 = -1024` m. Si lees los nombres como metros, cada búsqueda falla por un factor de dos y aun así devuelve terreno, de la parte equivocada del mapa.
- Una loseta puede aparecer tres veces: normal, `_cb` y `_ul`. Las tres cubren el mismo suelo. Se toma una por loseta, en ese orden de preferencia, porque fusionarlas triplicaría la geometría en superficies coincidentes.
- Una loseta se lee solo si toca la caja de la vuelta **y** el corredor. Una loseta que el corredor no toca nunca se descomprime.
- Cada `.modelbin` de una loseta elegida se decodifica solo en **nivel de detalle 0**. Una loseta lleva cuatro niveles sobre el mismo suelo, y exportarlos todos pondría el mismo metro cuadrado cuatro veces en el archivo.
- Cada malla lleva su propia escala y sesgo en coordenadas del mundo, así que cae donde la pone el juego, sin transformación de instancia. Se conservan los triángulos cuya huella solapa la caja, y luego solo los que llegan al corredor.
- Una malla en un formato que el lector rechaza se salta y se cuenta (`N meshes could not be read`), para que un resultado escaso diga por qué.

El resumen del terreno imprime el número de vértices, de triángulos, de mallas y de losetas, y la extensión en x/y/z.

### Carretera, arcén, terreno, marcas, agua {#road-verge-terrain-markings-water}

El nombre de los materiales no puede decir dónde está la carretera. Alrededor de un circuito, el 94 % del suelo usa un material de sombreado de carretera, porque el terreno cerca de una carretera se dibuja con él y el sombreador decide asfalto o hierba píxel a píxel. Así que:

| Tipo | Decidido por |
|---|---|
| tira de carretera | el **diseño de vértices**: las tiras de carretera son el único suelo con un segundo conjunto de UV (canal 1); un triángulo cuyos tres vértices lo tienen es carretera |
| asfalto frente a arcén | dentro de una tira de carretera, la **máscara de asfalto** de la loseta en el centroide del triángulo: 0,5 o más es `road`, menos es `verge` |
| marcas | coincidencia del nombre del material con `whiteline`, `yellowline` o `decal` |
| huellas de neumáticos | coincidencia del nombre del material con `tyremark` o `skid` (se comprueba antes que las marcas, porque las huellas vienen como `tyremark_decal_*`) |
| agua | coincidencia del nombre del material con `water`, `lake`, `river`, `paddy`, `ocean` o `sea` |
| terreno | todo lo demás |

Medido en las vueltas grabadas del circuito de prueba, casi todas las muestras caen en triángulos de tira de carretera, y la gran mayoría en la parte de asfalto una vez que la máscara ha separado el arcén.

La máscara de asfalto solo existe cuando se hornean las texturas del suelo. Con `--no-textures`, o en una loseta cuyos mapas faltan, las tiras de carretera quedan enteras como `road` y no se separa ningún arcén. Los mapas que faltan cuestan detalle, nunca geometría.

### Las capas pintadas se levantan {#painted-layers-are-lifted}

Las marcas de carril y las huellas de neumáticos vienen como triángulos propios que yacen exactamente sobre la carretera. El juego las dibuja con un desplazamiento de profundidad. Dibujadas tal cual, la carretera y la pintura se pelean en cada píxel. La exportación da a cada parte de marcas y de huellas su propia copia de vértices, levantada **5 cm** (`DECAL_LIFT`) a lo largo de la normal de la superficie, para que la carretera de debajo no se levante también.

### Normales {#normals}

Las normales del terreno vienen del archivo. La x de la normal se guarda como el cuarto short de la posición, y su y y su z en el atributo `NORMAL` (mira [ForzaTech](reader-forzatech.md)). Si a algún vértice de la extracción le falta una normal, las normales de todo el suelo se calculan a partir de los triángulos.

## La textura del suelo {#the-ground-texture}

Cada loseta de terreno trae tres mapas que cubren su cuadrado de 512 m, en cinco resoluciones (`_quality1` a `_quality5`, la mayor de 2048 px, que son 25 cm por píxel):

| Mapa | Patrón del nombre | Qué contiene (medido) |
|---|---|---|
| principal | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: normal de detalle (x, z). A: más bajo en asfalto y en terreno áspero |
| secundario | `submap_x<X>_z<Z>_x<season>x_diff` | pesos de capas. B: alto en asfalto (239 en la línea de conducción, 165 al lado) |
| brillo | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: bajo en asfalto (147 frente a 215). B: sube en el bosque |

Ninguno de estos es una fotografía en color. Son las entradas con las que el sombreador de terreno del juego mezcla sus capas de material, y esas capas no se decodifican. Así que la textura horneada es **una interpretación, no una copia del aspecto del juego**. Conserva *dónde* está cada tipo de suelo, a 25 cm, y lo pinta con colores fijos:

| Suelo | RGB lineal | Peso |
|---|---|---|
| hierba (corta, cerca de la pista) | 0,30, 0,44, 0,18 | la base |
| áspero (más lejos) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| bosque | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalto | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Para el asfalto tienen que coincidir los dos mapas. Uno solo deja motas grises en la hierba allí donde la compresión por bloques hace anillos. El resultado se sombrea con la normal de detalle del mapa principal frente a una luz fija (`0.55 + 0.6 * lambert`), para que los labios de bordillo, los taludes y los surcos se lean como relieve, y se escribe como sRGB de 8 bits.

Orientación: la fila 0 del píxel es el borde **norte** de la loseta (la z mayor), y la columna 0 su borde **oeste** (la x menor). Se averiguó proyectando vueltas grabadas sobre la máscara de asfalto de las ocho formas en que se puede voltear o girar un cuadrado. Exactamente una de ellas las pone sobre asfalto. Los UV salen de ahí: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Los mapas se leen a la mejor resolución disponible hasta la calidad 5 y se remuestrean al tamaño del mapa principal. Si la imagen de color es mayor que `--texture-size`, se reduce a ese tamaño con filtro de Lanczos. La máscara de asfalto siempre se conserva a resolución completa, porque decide la geometría. `--season` elige los mapas `x<season>x`. Una loseta sin mapas para esa temporada se dibuja con colores planos, y la consola informa `N without maps`.

## Modelos colocados {#placed-models}

El terreno lleva su propia posición en el mundo. Nada más la lleva. Dónde está cada copia de un modelo se registra en archivos de colocación `.pgeo`, uno por categoría y por celda espacial:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. El diseño de los registros está en [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Qué se lee {#what-is-read}

- Los archivos de colocación se filtran **por nombre**: el tamaño de celda y la posición de la celda en la ruta dan el cuadrado de la celda (`x * size` a `(x + 1) * size`), y solo se abren las celdas que solapan la caja de la vuelta y que están en una categoría buscada.
- Categorías por defecto: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`. `--trees` añade `trees`, `bushes` y `smashables`. Estas nunca se leen: `grasstemplate`, `crowdtemplate` y `cwdspline` (hierba y espectadores), y `evolving` (sitios de festival que cambian con el progreso).
- Una copia se conserva si su posición está dentro de la caja y dentro del corredor. Las repeticiones exactas (la misma posición y orientación hasta el milímetro, listadas por dos celdas vecinas) se fusionan.
- Los **bordillos** son props cuyo nombre de modelo empieza por `road_gen_rum` (bandas de rugosidad). Se escriben como `ground:kerbs`, nunca se simplifican ni se dejan fuera, porque una vuelta se mide contra ellos.

| Categoría | Parte | Color de respaldo (sin textura) |
|---|---|---|
| bordillos | `ground:kerbs` | 0,60, 0,12, 0,10 |
| barreras | `structure:barriers` | 0,50, 0,50, 0,50 |
| props | `structure:props` | 0,45, 0,35, 0,25 |
| señales | `structure:signs` | 0,70, 0,70, 0,70 |
| edificios | `structure:buildings` | 0,55, 0,52, 0,48 |
| infraestructura | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| puentes | `structure:bridges` | 0,45, 0,45, 0,45 |
| rocas | `structure:rocks` | 0,30, 0,28, 0,25 |
| objetos rompibles | `structure:smashables` | 0,12, 0,22, 0,06 |
| árboles, arbustos | `structure:trees` | 0,10, 0,20, 0,05 |

### La geometría del modelo {#the-models-geometry}

Un nombre colocado `<model>_3D` se refiere a los archivos del modelo `<model>_cluster###.i.modelbin` (hasta una docena). Cada triángulo lleva una máscara de los niveles de detalle a los que pertenece:

- Los niveles de un modelo son sus triángulos marcados explícitamente para ese nivel. Los niveles van seguidos desde 0, del más fino al más grueso.
- Los triángulos marcados `0xFFFF` (todos los niveles) son las piezas rompibles, como los postes de un guardarraíl o los neumáticos sueltos de una pila. Cubren todo el modelo, y el juego dibuja esas piezas en lugar del modelo una vez que se ha roto en trozos. Solo se usan en un modelo sin ningún nivel marcado explícitamente.
- Los submallas cuyo sombreador de material es una **calcomanía** proyectada se dejan fuera.

Cada copia se coloca con su posición, sus ejes x e y del registro (z = x por y), y su escala. Las normales se transforman con la inversa de la escala.

### Qué textura {#which-texture}

Un material no nombra sus texturas. Las enumera como hashes, y el `AssetManifest.xml` del circuito asigna cada hash (`SourceHash`) a un nombre de textura. Solo se lee la sección `<Textures>`, que deja de leerse en `</Textures>` en un archivo que puede pesar decenas de megabytes. Después:

1. La ranura `0x88B483AA` es el color base del sombreador de entorno estándar (en todo material muestreado). Si el material enlaza una textura ahí, se usa esa.
2. Si no, decide el tipo propio de la textura, que es la palabra antes de su GUID: `_bclr_`, luego `_diff_`, luego `_colour_`.
3. Los mapas de terreno (`mainmap`, `submap`, `autogloss`) y las paletas de tinte (`tint`, `worldtint`) nunca colorean un modelo.

Así que un modelo se colorea por lo que enlaza su material, no por una textura con nombre parecido al modelo. Por ejemplo, `bar_rur_armco_crct_02_c` usa la textura de `..._02_a`.

La textura se lee de los archivos al tamaño más pequeño que tenga al menos **256 px** de lado (`MODEL_TEXTURE`), se reduce a 256 si es mayor, y se guarda como JPEG RGB dentro del `.glb`. El color de un guardarraíl a 256 px para cuatro metros es de 1,6 cm por píxel, y unas 80 de estas texturas caben en el atlas del visor junto a las losetas del suelo.

**Temporadas.** `--season` cambia una textura por su gemela de temporada por nombre, ignorando el GUID (`..._xsummerx_bclr` a `..._xwinterx_bclr`, o `..._bclr` a `..._winter_bclr`), cuando el circuito la tiene. Con `--season winter`, el material de invierno de una submalla también se usa donde su tabla de variantes lo nombra.

**Variantes.** El registro de una submalla empieza con una tabla de materiales `(summer, winter)`, uno por cada aspecto que puede tener una copia: cinco impresiones para una valla publicitaria, seis colores de pintura para una pila de neumáticos. Cada registro de colocación dice qué variante lleva esa copia. Una submalla con menos variantes que el modelo repite las suyas.

**El bloque de marcador.** Los atlas de edificios compartidos reservan un bloque RGB sólido (255, 64, 0) para las superficies que el sombreador del edificio tiñe con otras texturas. Si más de una veinteava parte de una textura está a 12 niveles de ese color, el bloque se repinta con el color medio propio de la textura. Si no, una ciudad sale naranja.

### Superficies translúcidas {#see-through-surfaces}

Las vallas de eslabones y las redes son cuadriláteros sueltos con agujeros en el canal alfa de la textura. Dibujadas sólidas, una valla es un muro atravesado en la vista de la pista. Las superficies cuyo sombreador de material coincide con `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` o `tree` se someten a prueba:

- La opacidad de la textura se promedia sobre una cuadrícula de 32 x 32.
- Por superficie (cada triángulo recortado que comparte una textura), se muestrean cuatro puntos por triángulo en el espacio UV y se ponderan por el área UV del triángulo.
- Si la opacidad media es de al menos 0,05 y menos de **0,5**, toda la superficie se deja fuera. Por debajo de 0,05, el alfa significa claramente otra cosa para su sombreador (una señal de advertencia que muestrea 0,01), y la superficie se conserva sólida.
- Un modelo cuyas superficies se dejaron todas fuera se informa: `N models left out as see-through (mostly holes in their texture)`.

La herramienta juzga la superficie entera y no triángulo a triángulo. Juzgado por triángulo, la mitad de cada cuadrilátero sobrevivía y las vallas salían como filas de dientes.

### Edificios dibujados enteros {#buildings-drawn-whole}

Una ciudad construye sus edificios con piezas modulares: cientos de miles alrededor de un circuito urbano, decenas de millones de triángulos incluso en su nivel más grueso. Dejar piezas fuera una a una dejaba en pie losas de pared sueltas. El juego además trae sustitutos de edificio entero en `scene\hlod_tier_1\`, una malla por edificio (nombre `hlod_tier_1_*`), ya en coordenadas del mundo como el terreno:

- La caja mundial de cada sustituto se lee de la caja de posición de su malla (una lectura de cabecera, no una decodificación). Esto tarda segundos en un mapa entero.
- Se usan los sustitutos que tocan la caja de la vuelta y el corredor.
- Cada pieza `buildings` cuya posición cae dentro de la huella de un sustituto (más 0,5 m) se descarta, y se dibuja el sustituto en su lugar. Su distancia a la conducción se mide hasta el borde más cercano del edificio.
- El resumen dice `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Detalle y presupuesto {#detail-and-the-budget}

Las bandas de distancia, el presupuesto y las copias que se van cuando el presupuesto es demasiado pequeño están en [Niveles de detalle y presupuesto](detail-budget.md).

### Resumen de colocación {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
```

## Escritura del archivo {#writing-the-file}

Las partes se escriben en este orden: por loseta `terrain`, `verge`, `road` (cada una con la imagen de la loseta); luego `water`, `tyre marks`, `markings` (planas, las dos últimas levantadas), y después cada parte colocada ordenada por nombre. Las coordenadas son las propias del juego (metros, Y hacia arriba). Mira [Formato de salida](output-format.md).

## Lo que cuesta {#what-it-costs}

Órdenes de magnitud aproximados:

| Recorrido | Resultado |
|---|---|
| un circuito corto de campo | unos cientos de miles de triángulos de terreno, más de un millón colocados; segundos, menos de 100 MB |
| un sprint largo de punto a punto | el corredor es una pequeña fracción de la caja alrededor; un minuto aproximadamente, unos cientos de MB |
| un circuito urbano | miles de barreras, props y señales, y edificios enteros; con el presupuesto automático, hasta varios cientos de MB |

Un kilómetro cuadrado de terreno de mundo abierto son alrededor de un millón de triángulos.

## Comprobaciones que lo respaldan {#checks-behind-it}

Son medidas hechas mientras se escribía el lector, según se indica en el código fuente. Las pruebas no las repiten salvo que el juego esté instalado.

- En el circuito de prueba, el coche está aproximadamente a su altura de marcha sobre el suelo extraído (mediana por debajo de 0,2 m).
- Cada loseta muestreada cae dentro del cuadrado de 512 m que predice su nombre.
- Las colocaciones consecutivas de guardarraíles están exactamente a 4 m, y la mayoría de los extremos de guardarraíl caen a menos de 5 cm del inicio del siguiente.
- Los bordillos quedan a unos centímetros por encima del suelo extraído, con la cara hacia arriba, a menos de 5 m de la conducción (también una prueba con el juego instalado, mira [Desarrollo](development.md)).

## Lo que no se dibuja {#not-drawn}

- Los árboles y arbustos salvo con `--trees`. La hierba, las multitudes y los sitios de festival nunca.
- Los materiales de calcomanía proyectada sobre los modelos.
- Las impresiones de señales mezcladas con alfa sobre su tablero salen opacas.
- El color del suelo es una reconstrucción de dónde están el asfalto, la hierba y el bosque, no los materiales de terreno propios del juego.
