---
title: Límites y carencias conocidas
nav_order: 10
lang: "es"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Límites y carencias conocidas {#limits-and-known-gaps}

Lo que la herramienta no hace, lo que hace solo en parte, y dónde su comportamiento es desigual. La mayoría de las carencias son rechazos deliberados. Decodificar sin un archivo con el que comprobar produce una salida que parece correcta y no lo es.

## Juegos {#games}

| Juego | Exportación de circuito | Por qué no, o hasta dónde llega |
|---|---|---|
| Forza Horizon | sí | el color del suelo es una interpretación (ver abajo) |
| BeamNG.drive | sí | sin cobertura de suelo; las texturas de modelos que se repiten se aplanan |
| Assetto Corsa Rally | sí | modelos con colores planos; todavía no se ha ejecutado sobre una vuelta grabada en el juego |
| Assetto Corsa EVO | **no** | todo el contenido está en un único paquete ofuscado con una clave, y esta herramienta no recupera claves |
| Battlefield 6 (exportación de nivel, `level`) | sí, un nivel completo | terreno, mallas agrupadas y colocadas una a una y sus mapas de color, la malla de navegación de los soldados, follaje recortado; el color del suelo de la zona de juego es grueso (32 m por píxel, o un único color medio); sin translucidez ni mapas de normales; las mallas destructibles se etiquetan, pero sus estados destruidos no se exportan |
| juegos de Unreal 5 con World Partition (exportación de mapa, `ue-map`) | sí, un mapa completo | el paisaje exacto; edificios como las mallas HLOD simplificadas del mapa, no los modelos de máximo detalle; masas de agua; sin follaje, calcomanías ni color del suelo |
| Arma Reforger (exportación de mundo, `enfusion-world`) | sí, un mundo completo | terreno en sus propios colores y el mar; edificios, objetos y rocas como cajas de sus modelos, no sus triángulos; árboles a petición (`--trees`), como cajas; sin lagos, ríos ni entidades hijas |
| iRacing | **no** | los circuitos vienen en un formato protegido que no es un objetivo de extracción de archivos |
| cualquier otro | **no** | no hay lector de circuitos; reconstruye a partir de la partida con 3DHeat GameCapture, o analiza las vueltas en la pestaña Análisis de carrera del visor sin circuito |

## Motores y formatos {#engines-and-formats}

| Formato | No implementado |
|---|---|
| Unreal `.pak` | versiones anteriores a la 8; índices solo con hash de ruta (los nombres no se pueden recuperar); entradas en la lista de desbordamiento del índice (se omiten); decodificar el contenido de `.uasset`/`.umap` desde un pak |
| Unreal IoStore | contenedores cifrados (se rechazan, no hay opción de clave); listar un contenedor sin índice de directorio (no nombra archivos); paquetes con versión; mallas solo Nanite y no guardadas en línea; mallas esqueléticas; propiedades de clases sin esquema; propiedades de componentes instanciados (el diseño cambió en la compilación del juego); mallas de spline y componentes de calcomanía |
| Unity | formatos anteriores a 22 (Unity 2019 y anteriores); archivos con árboles de tipos incrustados; mallas comprimidas; cualquier clase salvo `Mesh`, así que no hay transformaciones, materiales ni escenas; `meshes` sobre un paquete; `list`/`extract` (usa `meshes`) |
| Frostbite | tablas ofuscadas con XOR; el grafo de capas del terreno (máscaras leídas en unos dos tercios de los niveles revisados); plantillas de objetos distintas de las mallas (lógica de juego, efectos, sonidos); mallas de nivel no guardadas en línea; mapas normales y otros, canal alfa que no sea de recortes; huecos del terreno; la biblioteca de tipos (cifrada en el sistema de archivos inicial, no se toca); un comando para listar o extraer recursos sueltos |
| Source 2 | recursos compilados (`.vmdl_c`, `.vtex_c`); la malla de navegación de CS2 (versión 36) |
| ForzaTech | formatos de posición distintos de cuatro shorts escalados; formatos de índice distintos de u16; códigos de textura distintos de 0, 9, 13; las capas de material del shader del terreno; tangentes |
| BeamNG | mallas con esqueleto y de calcomanía; animación; cobertura de suelo procedural; escenografía en el borde del mundo |
| paisajes de Unreal y mapas World Partition | paisajes cuyos mapas de altura viven en las celdas cocinadas; capas de edición y huecos; mallas de paisaje Nanite; modelos de máximo detalle colocados en las celdas; follaje; materiales de paisaje |
| Enfusion | triángulos de modelos (la geometría `.xob` está comprimida en un diseño que no se lee); `.edds` con cabeceras anteriores a DX10; valores de objetos anidados en archivos de mundo (se omiten, y se cuentan); entidades hijas; lagos y ríos generados; `list`/`extract` sobre un `.pak` |

## Comportamientos que conviene conocer {#behaviour-worth-knowing}

- **El color del suelo de Forza no es el del juego.** La textura horneada se dibuja a partir de los mapas de losetas que dicen *dónde* hay asfalto, hierba corta, terreno irregular y bosque. Usa colores y sombreado fijos, porque las capas de material propias del shader del terreno no se decodifican.
- **`--no-textures` también quita el arcén de Forza.** La división asfalto/arcén usa la máscara de asfalto que viene con los mapas horneados. Sin texturas, las franjas de carretera quedan enteras como carretera.
- **Un presupuesto que tú das solo puede superarse con los bordillos.** Los bordillos (y los modelos de superficie de conducción de BeamNG) nunca se simplifican ni se dejan fuera, en ningún juego; así que un `--detail-budget` menor de lo que cuestan se supera solo por ellos; todo lo demás se deja fuera primero. Ver [Niveles de detalle y presupuesto](detail-budget.md).
- **Las opciones que no aplican se ignoran en silencio**: `--season` para BeamNG y AC Rally, `--track` para BeamNG y AC Rally, `--level`/`--install` para Forza.
- **El color del suelo de un nivel de Battlefield 6 es grueso lejos de sus calcomanías.** El campo de alturas se colorea con el mapa de color del fondo del terreno, a 32 m por píxel en el mip más grande que trae el nivel, o, donde ningún mapa de fondo lo cubre, con el color medio de los materiales de superficie del terreno. `--ground-texture` multiplica eso por el mapa de color del terreno (a 0,5 m por píxel donde el nivel lo tiene) y hornea sobre él las carreteras, plataformas, líneas de pista, huellas de neumáticos y marcas, con el color de pintura de su material cuando lo tiene y un color neutro cuando no; los mapas de máscara de variación de carretera se dejan fuera. El juego mezcla sus capas de superficie en un grafo de shaders que no se lee; la exportación coloca los colores de las capas según sus máscaras y la pendiente del campo de alturas, con una regla propia, y un nivel cuyas páginas de máscara no encajan entre sí recibe un solo color. Cada capa es la media de su mapa de color, no su textura. Ver [Frostbite](reader-frostbite.md#terrain-layers). Los trozos del campo de alturas con distinta resolución se encuentran con pequeños escalones.
- **Un mapa de color de Battlefield 6 se elige, no se lee.** Un bloque de shader nombra cada textura que muestrea sin decir cuál es el color; la elección se hace por nombre (ver [Frostbite](reader-frostbite.md#textures-and-materials)) y puede escoger una hoja de adornos o de detalle para una superficie. Las hojas de calcomanía (`t_de_...`) pierden frente al mapa propio de la superficie; la calcomanía de una señal, dibujada como su panel, hizo que su escudo girara un cuarto de vuelta. Los campos de distancia, las paletas y las máscaras de canal nunca se toman. Los edificios de fondo se dibujan con los colores de su paleta; los mapas en grises toman el tinte del material por una regla propia de la exportación, ya que los nombres de los parámetros están hasheados, y un material que pinta un mapa en grises a través de una máscara con varios tintes toma uno de ellos.
- **Los huecos del terreno de Battlefield 6 no se recortan.** Donde el suelo transitable de un nivel corre por debajo del campo de alturas, el juego debe haber cortado el terreno, y la exportación no lo hace. Se descartaron como lugar de los huecos: las máscaras de capa del terreno (ninguna se concentra allí), su rejilla de nodos de 67 x 67, un valor de altura reservado (ninguna página de altura contiene 0 ni 65.535), las banderas de los nodos (todas iguales), y las mallas o recursos que cortan el suelo: lo que se coloca bajo el suelo allí son mallas de roca y acantilado, y ningún recurso del nivel se llama para huecos, túneles o cuevas. Dos árboles de rasterización se decodifican por rachas pero no se colocan, y son lo que queda (ver [Frostbite](reader-frostbite.md#terrain-layers)).
- **Una variación de objeto de Battlefield 6 llega a una sección a través de sus gemelos.** La variación de una copia colocada elige los bloques de shader de sus secciones por clave; donde una malla no tiene bloque para una variación, se toma la variante de la sección de otra malla con un bloque por defecto idéntico (ver [Frostbite](reader-frostbite.md#textures-and-materials)). Esa es la regla de la exportación; una sección sin gemelo que varía conserva su aspecto por defecto.
- **Los materiales en capas de Battlefield 6 se dibujan como su base y una hoja.** Un panel de pared con letras se dibuja como su yeso con la hoja de letras encima; las demás capas del material (suciedad superpuesta a través de su máscara, y mapas de detalle y musgo) no se mezclan.
- **La malla de navegación es la de la IA, no la de los jugadores.** Cubre lo que un soldado puede recorrer andando: el suelo, los pisos y escaleras, y algunos tejados, pero no todos los puntos altos. Los enlaces entre superficies (saltos, escaleras, pasos sobre obstáculos) se dejan fuera.
- **Un nivel de Battlefield 6 incluye la capa de cada modo de juego.** Los objetos que solo coloca un modo pueden solaparse con los de otro. `--skip` deja capas fuera por nombre.
- **`courses` es solo de Forza**, y solo recoge carpetas de biblioteca con nombre `... (course_...)`.
- **Se supone el marco de vuelta de BeamNG**, el marco del visor `(x, z, -y)` que escribe el grabador de 3DHeat. Las vueltas de otro grabador en el marco crudo de BeamNG no se colocarían.
- **`list` y `extract` solo aceptan archivos, no todos los formatos.** Abren un `.pak`, un `.utoc` de IoStore, un `.vpk`, un `.minizip` y un zip. Un contenedor de Unity se lee con `meshes`, un nivel de Frostbite con `level`, y un `.cdae` o `.ter` es un archivo y no un archivo comprimido (`identify` lo indica). Un `.minizip` sin su `ChunkContentsMiniZip<n>.txt` a su lado se lista por número de entrada.
- **Las mallas colocadas en BeamNG usan las texturas que se repiten como colores medios**, porque el muestreador del `.glb` se ajusta y el visor empaqueta las texturas en un atlas.
- **En la práctica, solo Windows.** Rutas de Steam bajo `C:\Program Files`, `%LOCALAPPDATA%`, `C:\XboxGames`, y un `*_win64.dll` para Oodle. Otras plataformas no están probadas.

## Sin verificar {#unverified}

- Versiones antiguas de Python (la herramienta se ha ejecutado con la 3.13).
- Assetto Corsa Rally con una vuelta grabada en el juego. Solo se ha probado con vueltas sintéticas en marcos aleatorios.
- Visores de glTF distintos del visor de 3DHeat.
- Si el marco de telemetría de cada juego es zurdo o diestro. La exportación conserva el marco de telemetría de cada juego, así que vueltas y circuitos se alinean en cualquier caso.
- El significado de z = 0 de `WaterBlock` como su superficie (BeamNG).
- La colocación de Frostbite en juegos distintos de Battlefield 6, y en Battlefield 6 tras una actualización que cambie el diseño del miembro de grupo. El lector entonces no encuentra grupos y lo dice.
- Si una exportación de Battlefield 6 se alinea con las posiciones que informa el juego. Las coordenadas son las del propio juego, como en los demás juegos, pero todavía no se ha superpuesto ninguna grabación sobre una.
