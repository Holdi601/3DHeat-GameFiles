---
title: "Frostbite"
nav_order: 5
lang: es
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, paquetes, mallas y niveles {#frostbite-toc-cas-bundles-meshes-and-levels}

**Lee un nivel de Battlefield 6 hasta su terreno, sus mallas colocadas y sus mapas de color, y lo escribe como un `.glb`.** Los juegos Frostbite (Battlefield, Need for Speed, Dead Space) guardan su contenido en blobs `.cas`, descritos por tablas de contenido `.toc`. La tabla de un nivel dice qué paquetes carga el nivel, los paquetes nombran cada activo, y los activos dicen qué malla va en qué sitio.

Fuentes:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tablas, instalaciones, cargas),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(paquetes y sus manifiestos),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(particiones EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(mapa de alturas),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(texturas y materiales),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(colocación y exportación).
Comandos: `identify`, `levels`, `level` (mira [Comandos](commands.md#levels-and-level-frostbite)).

Nada de esto lo documenta el juego. Cada diseño de abajo se leyó de los archivos y luego se contrastó con todos ellos, y cada sección dice cuál fue la comprobación. Cuando las páginas de herramientas de modding de Frosty describen versiones anteriores de una estructura, los nombres de los campos siguen los suyos; no se tomó código de ellas (mira [Reglas y licencias](rules-and-licences.md)).

## La cabecera que parece cifrada y no lo está {#the-header-that-looks-encrypted-and-is-not}

| Firma (u32, little-endian) | Significado | Tratamiento |
|---|---|---|
| `0x00CED100` | simple: el árbol empieza de inmediato | se lee |
| `0x01CED100` | firmado: una firma de 556 bytes, y luego el árbol **en claro** | se lee |
| `0x03CED100` | ofuscado con XOR, con la clave en la propia cabecera del archivo | detectado y rechazado |

La forma firmada es la que usa el Battlefield actual. Los bytes de alta entropía tras la firma son una firma, no texto cifrado.

## El árbol DbObject {#the-dbobject-tree}

Una estructura única y recursiva. Cada campo tiene un byte de tipo (los cinco bits bajos son el tipo, el bit 7 indica "anónimo"), un nombre opcional y un valor. Los contenedores llevan su longitud como entero de longitud variable y terminan con un byte cero. `parse_toc` comprueba la longitud de cada contenedor, así que un archivo que se parsea se ha entendido. `layout.toc` está en esta forma.

## Paquetes de instalación {#installation-packages}

Cada ubicación nombra el **paquete de instalación** al que pertenece su blob. Cada paquete numera sus blobs desde `cas_01`, así que el número de blob por sí solo es ambiguo en cuanto hay más de un paquete instalado, y siempre lo hay.

- `layout.toc` enumera los paquetes bajo `installManifest.installChunks`, cada uno con un `persistentIndex` y un `installBundle` como `Win32/installation/<package>`.
- Los blobs del paquete están en esa carpeta, bajo `Data` para el juego base o bajo `Update/<pack>/Data` para lo que llegó después.
- Un registro de ubicación lleva el `persistentIndex` completo de 32 bits: la mitad baja de su primera palabra guarda la mitad alta, la mitad alta de su segunda palabra la mitad baja; la mitad baja de la segunda palabra es el número de blob.

Comprobación: cada ubicación de cada tabla binaria de una instalación se resuelve en un paquete declarado y cae dentro del blob que nombra. Una versión anterior tomaba el primer `cas_NN.cas` del número correcto. Un tercio de las cargas que leía parecían de alta entropía y se tomaron por cifrado. Eran los desplazamientos correctos en el archivo equivocado. No se encontró nada cifrado.

## La tabla del nivel {#the-level-table}

La tabla de un nivel (`levels/<level>/<level>.toc`) es una tabla de secciones: quince palabras de cabecera big-endian, y luego secciones una tras otra, cuyos desplazamientos están tanto declarados como derivables de dos recuentos.

| Sección | Contenido |
|---|---|
| bundles | una tabla hash (una palabra cada uno), y luego un registro de 16 bytes por paquete: clave, `0x40000000` \| tamaño, 0, desplazamiento |
| tabla hash de fragmentos | una palabra por fragmento |
| fragmentos | id de 16 bytes (el GUID del fragmento con los **bytes invertidos**), y luego una palabra: `0x80000000` \| 4 x el índice de su ubicación |
| ubicaciones | cuatro palabras big-endian: paquete (dividido), blob, desplazamiento, tamaño |

Los identificadores de fragmento y las ubicaciones están en **órdenes distintos**. Leerlos en orden de archivo empareja cada fragmento con los bytes de otro fragmento, que se decodifican perfectamente bien (sobre todo como sonido), y por eso no parecen mal hasta que una malla sale como ruido. Comprobación: en un nivel, las palabras de índice son una permutación de 0 al número de fragmentos menos uno.

Los paquetes están guardados en línea tras la tabla de secciones. Cada uno tiene nueve palabras de cabecera big-endian, y luego sus entradas: ocho bytes de desplazamiento y tamaño, precedidos de otros ocho bytes que nombran el paquete y el blob cuando el bit alto del byte de marcas de la entrada está activo. Comprobación: en cada paquete, la última entrada termina exactamente donde empiezan los bytes de marca.

### Cuál tabla es el nivel {#which-table-is-the-level}

Un nivel puede tener varias tablas con el mismo nombre: una en el `Data` del juego base, una en cada actualización (`Update/<pack>/Data`) que lo trae o lo cambia, y una en cada paquete de alta resolución (`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Solo algunas tienen paquetes. En un nivel que trae una actualización, la tabla del juego base solo tiene fragmentos y ningún paquete, y la de la actualización es el nivel; tomar la primera tabla encontrada no exportaba nada de él.

Así que el nivel es la tabla con más paquetes, y gana una capa posterior en caso de empate (primero el juego base, luego las actualizaciones por orden de nombre). Las tablas con el mismo nombre sin paquetes son sus **complementos**: sus fragmentos se añaden a los del nivel, porque contienen los mips más grandes de sus texturas. Una cabecera de textura nombra ese fragmento en el desplazamiento +164 (mira [Texturas y materiales](#textures-and-materials)). `levels` imprime de dónde viene cada nivel y cuántos complementos tiene.

## Manifiestos de paquetes {#bundle-manifests}

La primera entrada de un paquete es su manifiesto, guardado sin comprimir. Es el formato binario de paquetes de los juegos Frostbite anteriores con una firma nueva, `0xD68E799D`: recuentos, SHA-1, registros ebx y res (desplazamiento y tamaño del nombre), tipos de res, metadatos e identificadores, GUID de fragmentos, cadenas. El resto de entradas del paquete son los ebx, los res y los fragmentos, en ese orden. Comprobación: los recuentos coinciden con las entradas en cada paquete, y las cadenas empiezan donde terminan los registros.

Los tipos de recurso son hashes. `0x49B156D4` es MeshSet (cada res de ese tipo se llama `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` lee todo esto para un nivel, en unos segundos: un nivel tiene decenas de paquetes y decenas de miles de ebx, res y fragmentos.

## Bloques de carga {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Un tamaño comprimido cero significa guardado sin comprimir, siempre que descomprima a ese mismo tamaño.

| Palabra de método | Códec |
|---|---|
| `0x0070`, `0x0071` | ninguno |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), desde la propia DLL `oo2core` del juego) |
| otra, con tamaños iguales | copiada tal cual |
| otra | rechazada |

Leída desde el paquete correcto, cada carga muestreada se decodifica.

## Particiones EBX {#ebx-partitions}

EBX guarda todo lo que no son datos crudos. Cada partición es un archivo RIFF: `EBXD` (los datos, alineados a 16), `EFIX` (GUID de partición, GUID de tipos y firmas, instancia, desplazamientos de puntero, importación e información de tipos, importaciones, y los desplazamientos del array, de valores encajados y de cadenas), `EBXX` (la tabla de arrays: desplazamiento, recuento, hash, marcas, tipo de elemento). Un campo de puntero ocupa ocho bytes: cero es nulo, un valor impar es la importación número `value >> 1`, y cualquier otro valor es relativo al campo.

La **biblioteca de tipos no se puede leer**. El juego la trae en su sistema de archivos inicial, que está cifrado, y este paquete no lo toca. Los tipos se conocen por GUID y firma, que lleva cada partición, y los pocos tipos que necesita la exportación del nivel se diseñaron a partir de los datos.

## MeshSet {#meshset}

Una malla es un res MeshSet (la descripción) y un fragmento por nivel de detalle (los búferes).

| Parte | Diseño |
|---|---|
| prefijo | cuatro palabras: tamaño de cabecera (176 o 192), tamaño del registro de nivel (176 a 188), tamaño del registro de sección (368), 0 |
| cabecera | caja delimitadora; seis desplazamientos de nivel i64; tipo de malla en `0x6C` (rígida, esquelética, compuesta); recuentos de niveles y secciones en `0x9C` |
| nivel | secciones en `+0x08`; cinco listas de dibujo en `+0x14` (opaca, transparente, calcomanía, solo profundidad, sombra); formato de índice en `+0x54` (`0x21` u16, `0x2E` u32), bytes de índices y de vértices; GUID de fragmento en `+0x74` |
| sección | nombre del material; paso de vértice; triángulos, primer índice, desplazamiento de vértices (en bytes), recuento de vértices en `+0x20`; declaración de vértices en `+0x64`: 16 x (uso, formato, desplazamiento, flujo), 16 pasos de flujo, recuentos |
| fragmento | el búfer de vértices, y luego el búfer de índices. Los flujos de una sección van uno tras otro, e indexan desde el primer vértice de la sección |

Las posiciones son de uso 1, flujo 0, desplazamiento 0, como cuatro medias o tres flotantes. Solo se dibujan las secciones opacas y transparentes. Toda sección llamada `..._shadow` está en la lista de sombras y solo ahí, así que deciden las listas.

Comprobación: cada malla de un nivel cuyos niveles están guardados en fragmentos se decodifica, y casi todas tienen el 99 % o más de sus vértices dentro de su caja declarada; el resto falla por el redondeo de media precisión. Un cajón decodificado mide un metro aproximadamente, con Y hacia arriba y sus normales apuntando hacia fuera.

## Colocación {#placement}

El proceso de contenido reúne los objetos estáticos de cada subnivel en un **grupo de modelos estáticos**: un array de miembros, uno por malla, cada uno con sus transformaciones de instancia.

| Tipo (GUID, firma) | Diseño |
|---|---|
| miembro `ad13064e…`, `0xF861A878` | 224 bytes: `+88` array de transformaciones, `+112` el plano del objeto (importación), `+160` el recurso de malla (importación) |
| transformación `101dce06…`, `0x5E6D8C37` | 64 bytes: derecha, arriba, adelante, traslación, cada una un vec3 con relleno hasta 16 |

La partición del recurso de malla se llama igual que su res MeshSet, así que el GUID de partición de la importación da la malla. Un punto cae en `x·right + y·up + z·forward + translation`. La transformación propia del grupo era la identidad en todos los grupos de los niveles comprobados, y no se aplica.

Comprobación: en un nivel, cada miembro de cada grupo se resuelve en una malla; la mayoría de las copias tienen una rotación de determinante 1 hasta una milésima, y el resto están escaladas o reflejadas. Los GUID y las firmas de tipo son los mismos en otros niveles. Una actualización del juego que cambie el diseño cambia la firma, y el lector entonces no encuentra nada en vez de leerlo mal.

### Objetos colocados uno a uno {#objects-placed-one-by-one}

Lo que la canalización no puede agrupar (objetos destructibles, contenedores, escombros) se coloca mediante **referencias a objetos** y **referencias a prefabricados** en las particiones del nivel:

| Tipo (GUID, firma) | Diseño |
|---|---|
| referencia a objeto `a9a6a6ad…`, `0xC4856BEC` | `+32` la transformación (como arriba), `+112` el plano del objeto (importación) |
| referencia a prefabricado `117c746e…`, `0xDE3FE9B4` | lo mismo; el plano es un prefabricado, una partición de más referencias |

Los prefabricados se anidan; una copia cae en su propia transformación multiplicada por la de su padre (vectores fila), hasta ocho niveles de profundidad. Un plano de objeto se dibuja como las mallas que importa, dejando fuera los estados destruidos (`dc_...`). Un prefabricado agrupado se referencia como su resto `..._nongroupable_autogen`, así que nada se dibuja dos veces.

El recorrido empieza solo desde los mundos y capas del nivel. Una partición cuya primera instancia es un plano de prefabricado (`134919fc…`, `0x0247807D`) es la definición de un prefabricado, y un nivel guarda muchas bajo su propia carpeta, colocadas por sus mundos de otras maneras distintas a estas referencias; si se recorriera como si fuera un mundo, un prefabricado pondría su contenido en sus coordenadas locales. Eso amontona cientos de copias alrededor del origen del mundo, muy por debajo del suelo. Los mundos y capas tienen `a10ebe0f…`, `0xD3D16C3C` como primera instancia.

No se siguen los planos retirados de la escena: los activos de desarrollo y de prueba (`game/dev/`, `test/`), el conjunto de la escena cinematográfica de fin de ronda (`..._gameend_...`: colocado bajo el suelo) y el controlador de la cámara de muerte (`.../deathflow/...`, cuyos accesorios se quedan en el origen del mundo). Se reconocen por su ruta de activo, no por su capa: la misma capa que contiene el conjunto de la escena cinematográfica puede colocar los muros y tejados reales de un nivel. Tras aplicar ambas reglas, ninguna copia de los niveles comprobados queda a más de 10 m bajo el terreno, y las copias se apoyan en el terreno donde el juego las muestra.

**Niveles de detalle que hacen de sustituto.** El último nivel de detalle de una malla puede cambiar a un sustituto de vista lejana con un material propio: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Una torre de celosía de decenas de miles de triángulos puede terminar en una silueta de unos cientos, que el presupuesto elegiría y que de cerca sería una aguja sólida. Un nivel de detalle que trae uno de esos materiales, que su nivel más fino no tiene, nunca se elige: el más grueso de la malla es el último real.

## Terreno {#terrain}

Fuente: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

El terreno es un res TerrainStreamingTree (tipo `0x22FE8AC8`) y los fragmentos que nombra.

| Parte | Diseño |
|---|---|
| cabecera | 34 bytes; el número de nodos en el 25 |
| árboles raster | un byte de tipo y una longitud u32 cada uno, hasta un byte de tipo `0xFF`. El tipo 0 es el mapa de alturas: muestras por lado en +5 (265), rango de alturas en +21 (1.280 m), el cuadrado de terreno en el primer registro de nodo en +77 (8.192 m en el nivel comprobado). Guarda las cajas de los nodos y una pirámide mín/máx de 16 x 16 por nodo, no las alturas |
| nodos de flujo | el cuadtree, en profundidad primero: tamaño de fragmento y GUID; un segundo fragmento opcional; un byte de marcas (bit 0: el fragmento empieza con una página de alturas); tiene hijos. Los hijos en el orden (0,0), (1,0), (1,1), (0,1) |
| página de alturas | los primeros 265 x 265 u16 de un fragmento de nodo marcado, fila a fila; altura = valor x 1.280 / 65.535 m; columnas a lo largo de x, filas a lo largo de z, desde la esquina baja del nodo; un borde de 4 muestras, así que 256 celdas por nodo |

Cada paso se comprobó por separado:

- El análisis del cuadtree de nodos consume el res hasta su último byte, con los 529 nodos declarados.
- Los nodos vecinos comparten exactamente sus nueve columnas de borde, así que el paso es 256.
- Las muestras de un hijo en cada posición alterna son exactamente iguales a las de su padre con un borde de 4, y difieren entre 90 y 700 unidades con cualquier otro borde.
- La palabra más baja del nivel se decodifica a la altura más baja de la caja delimitadora, con el centímetro de precisión.
- De las ocho formas en que el cuadrado podría quedar sobre el mundo, solo x a lo largo de x y z a lo largo de z pone los objetos colocados sobre él: la mitad de las copias muestreadas dentro de unos 2 m, frente a varias veces eso con cualquiera de las otras.

Los objetos colocados miden entonces el resultado. El punto más bajo de cada copia, frente al terreno bajo ella (bilineal, desde el nodo más fino):

| Colocado | Distancia mediana | Mediana con signo |
|---|---|---|
| árboles y arbustos | bastante menos de un metro | justo por debajo de la superficie |
| props | uno o dos metros | sobre la superficie |
| rocas | alrededor de un metro | hundidas unos metros |
| edificios | varios metros (se apoyan sobre cimientos) | ligeramente hundidos |

La vegetación se coloca sobre el suelo y en ningún otro sitio, lo que la convierte en la comprobación más precisa: sus orígenes quedan a una mediana de 0,07 m de la superficie. Los edificios se dispersan mucho porque la categoría incluye muros, suelos y piezas de equipamiento de estructuras de varias plantas y subterráneas. Desplazar el terreno 64 m de lado reduce la proporción de copias dentro de 0,5 m del 29 % al 10 %.

`level` dibuja el mapa de alturas como `ground:terrain`, cada parte de él desde el nodo más fino que tiene alturas allí, y no más fino que `--ground-spacing` (4 m por defecto: 3,7 millones de triángulos en el nivel comprobado, cuyos nodos más finos miden 0,5 m). Las piezas de distinta resolución se unen con pequeños escalones; nada las une.

El fragmento de un nodo también guarda las páginas de las máscaras de capa tras su página de alturas, y su segundo fragmento termina con el mapa de color del nodo (mira [Capas del terreno](#terrain-layers)).

## Capas del terreno {#terrain-layers}

El juego sombrea el terreno cerca de un jugador mezclando materiales de superficie con máscaras pintadas (*splatting*), con un mapa de color encima, y dibuja calcomanías (carreteras, parches de asfalto, marcas de pista) por encima. La propia descripción de Frostbite del sistema (Widmark, "Terrain in Battlefield 3", GDC 2012) enumera los rasters del terreno: el mapa de alturas, las máscaras de *splatting* del sombreador, un mapa de color "usado como superposición sobre el *splatting* del sombreador", materiales de física, una máscara de profundidad de destrucción, un mapa de albedo para la luz rebotada y canales de máscara adicionales; las losetas de un raster llevan un borde para los algoritmos de render. El árbol de flujo de los niveles comprobados tiene siete árboles raster, de tipos 0, 1, 2, 4, 5, 7 y 8, cuyas cabeceras empiezan por su tamaño de loseta: 265 para el mapa de alturas (tipo 0) y el tipo 2, 72 o 66 para las máscaras (tipo 1), 132 con un borde de 2 para el mapa de color (tipo 4), 260 con un borde de 2 para el tipo 5.

**La lista de capas.** El res `....layergraphs` del terreno enumera una entrada de 32 bytes por capa, en el orden en que los registros de máscara las numeran (34 entradas, 34 secciones de depósito e índices de capa de 0 a 33 en un nivel); el id de cada entrada termina con su clave de sección en el depósito de bloques de sombreador del grafo de capas (`....layergraphs_shaderblockdepot`), cuyo bloque nombra los mapas de la capa: un mapa de color `_cv`, mapas `_nhs` y `_ao` por superficie, y además mapas de detalle y de ruido compartidos. Muchas capas no nombran ningún mapa: son fuentes que el grafo de capas lee. El color de una capa es la media de su mapa `_cv`; la escala de repetición no se encuentra. El activo del terreno termina con una entrada de cinco bytes por capa (un byte, y luego un u32 con el índice de capa o -1).

**Las máscaras.** El árbol raster 1 es el cuadtree de las máscaras. Su cuerpo empieza con 59 bytes, y el lado de la página en el 0: 72 donde las páginas son BC4 (72 x 72, 2.592 bytes), 66 donde son de ocho bits sin comprimir (4.356 bytes). Luego viene un grupo por nodo, en profundidad primero:

| Parte | Diseño |
|---|---|
| grupo | u16; u16 número de registros; u32 número de páginas; los registros; un byte cero. Un grupo sin registros mide 7 bytes en total |
| registro | 33 bytes: u16 capa, u16 hash, la caja del cuadrante (cuatro flotantes), dos bytes de marcas, una pirámide de presencia de 85 bits |

Los registros de un grupo son los cuatro cuadrantes de su nodo, capa por capa, y los cuadrantes de cada capa en el orden (0,0), (1,0), (1,1), (0,1). Un registro con la segunda marca activa cubre su cuadrante entero y no tiene página; uno sin ella tiene la página siguiente; un cuadrante sin registro de una capa que su grupo nombra está vacío de esa capa; la primera marca está desactivada exactamente cuando la capa continúa en el propio grupo del cuadrante, un nivel más abajo, que la reemplaza allí. El número de páginas es el número de registros con página.

Las páginas: tras la página de alturas del propio grupo del nodo de flujo vienen sus páginas, en su fragmento, una sección de 4.358 bytes de 16 bits y un raster de 67 x 67 de ocho bits (desde el inicio del fragmento cuando no tiene página de alturas); su segundo fragmento guarda las páginas de los cuatro grupos de cuadrantes un nivel más abajo, en el orden de los cuadrantes del mapa de color, y luego el propio mapa de color. Una página es de 64 x 64 texels del cuadrante, con filas a lo largo de z y columnas a lo largo de x, con un borde copiado de sus vecinos: 4 texels en una página BC4, 1 en una sin comprimir. Las páginas se numeran y se ordenan en su lugar. El borde de cada página cabe en la siguiente.

Los bordes prueban la colocación sin juicio: dos páginas de una misma capa una junto a otra deben llevarse los texels de borde la una de la otra. `read_masks` lo comprueba para cada par que coloca, y rechaza un nivel en el que menos del 99 % coincida. Alrededor de un tercio de los niveles comprobados se leen, con sus bordes coincidiendo; unos pocos no tienen máscaras pintadas; el resto se rechaza, casi todos por esa comprobación (sus fragmentos de nodo guardan más de lo que este diseño conoce). El suelo de un nivel rechazado toma el color medio de sus materiales de superficie, y la exportación dice por qué. Los bordes frente a un cuadrante lleno valen 255, y los frente a uno vacío 0.

La página de 4.358 bytes y el raster de 67 x 67 que van antes de las páginas no se leen: sus valores están en una banda alta y estrecha, sin valores pequeños ni centinela.

**El color del suelo.** El grafo de capas mezcla las capas en un grafo de sombreador compilado de máscaras, pendiente, altura y ruido, que no se lee. `--ground-texture` colorea el suelo con una regla propia, dicha aquí como tal:

- las capas cuyo mapa de color lleva nombre de distancia son los sustitutos de la vista lejana y se dejan fuera;
- las capas texturadas que cubren nueve décimas partes del terreno o más son la base. Sus máscaras están llenas casi en todas partes, así que dónde está cada una lo elige el sombreador, no ellas: las que llevan nombre de roca o de acantilado colorean las pendientes de más de 40 grados, las que llevan nombre de grava colorean el terreno llano (las demás capas base cuando no hay ninguna), y se mezclan entre 20 y 40 grados según la pendiente del mapa de alturas (tomada cada 4 m y repartida de forma bilineal sobre los texels horneados: repetida en bloques de 4 m dibujaba el color rocoso en parches de borde duro);
- cada una de las demás capas texturadas se superpone sobre la base según su propia máscara, en orden de capas;
- el mapa de color se superpone al resultado como lo hace el motor: el doble del color del suelo multiplicado por el mapa, de modo que el gris medio lo deja tal cual; donde el mapa de color no tiene texels, el suelo toma la luminosidad mediana del mapa, en gris.

Comparado con el color mediano del suelo de fotogramas de juego de tres niveles (cromaticidad como rojo y azul frente a verde): el área de juego horneada da 1,00 / 0,69 frente a los 1,19 / 0,78 de los fotogramas en uno, cuyas capas de hierba son verdes donde los fotogramas muestran hierba seca; 1,19 / 0,82 frente a 1,01 / 1,04 en otro, cuyo mapa de color es en sí cálido (1,13 / 0,88); y 1,05 / 0,91 frente a 0,93 / 0,92 en un tercero sin mapa de color. Los fotogramas van iluminados y con gradación, así que esto mide el tinte, no la luminosidad.

**El mapa de color.** El segundo fragmento de un nodo guarda, tras las páginas de máscara de los grupos de sus cuadrantes, cuatro páginas BC7 de 132 x 132 (17.424 bytes cada una), una por cuadrante del nodo, en el orden (x baja, z alta), (x alta, z alta), (x alta, z baja), (x baja, z baja). El árbol de máscaras dice cuántos bytes ocupan las páginas de máscara, así que el mapa de color se encuentra por recuento, no por el final del fragmento: en un nivel los nodos más gruesos llevan cuatro páginas más tras él, otro raster de color plano, y leer las últimas cuatro páginas del fragmento perdió el mapa de color sobre nueve décimas partes del terreno. Sin ese recuento el mapa de color también se perdía en niveles con páginas de máscara sin comprimir, cuyas páginas no son un número entero de páginas BC4; el mapa de color de un nivel pasó de cubrir 0,4 a 0,94 de su terreno. El orden se ajustó: frente a los bordes del mapa de alturas de cada cuadrante, cada página de los nodos con rasgos coincide con un cuadrante, sin voltear, con 0,3 a 0,54, donde la siguiente mejor colocación queda por debajo de 0,2. Cosidas así, las páginas de un nivel se unen sin costura en las carreteras, el agua y las zonas edificadas del nivel de prueba, a 0,5 m por texel en el área de juego. Donde las capas hacen el trabajo, el mapa de color es casi neutro (mediana 110, 107, 104); en otros sitios puede tener color completo. Un nivel cuyos segundos fragmentos solo tienen páginas de máscara sin comprimir no tiene mapa de color leído. Una ronda anterior de este lector llamó a estas páginas no geográficas: las comparó con el mapa del fondo, que puede ser otro paisaje por completo, y colocó cada página en todo su nodo en lugar de en un cuadrante.

**El albedo de la luz rebotada** se buscó y no se encontró: los fragmentos del nodo raíz y de los nodos del primer nivel son páginas de máscara enteras, y el contenido del tipo 5 no se localiza.

**Huecos.** El activo del terreno de un nivel (tipo de res `0x1CA38E06`) nombra tres sombreadores: un sombreador de superficie por defecto, un sombreador de huecos y un sombreador de origen por defecto. No se encuentra qué capa lee el sombreador de huecos, así que el mapa de alturas no se recorta. En un nivel la malla de navegación puede correr sobre mallas de roca decenas de metros por debajo del mapa de alturas, donde el juego debe de haberla recortado. Se buscó y no se encontró allí: la máscara de una capa, el raster de 67 x 67, una altura reservada (ninguna página de alturas del nivel contiene 0 ni 65.535) y una marca de nodo (todo nodo por debajo de la raíz tiene marca 1). Quedan los árboles raster 7 y 8. Ambos usan codificación por longitudes: un byte igual al anterior va seguido de un recuento de copias adicionales (`ff ff 84` son 134 bytes de 255). El árbol 7 (loseta de 256, un cuadtree completo de cinco niveles, cuatro bits por muestra) se decodifica en pares de bytes con valores de 0 a 3; el árbol 8 (loseta de 265) en bytes sobre todo 255, con sus demás valores en series regulares. No se conoce que ninguno de los dos contenga los huecos, porque aún no se colocan sus losetas.

**Las calcomanías** se leen y se hornean; mira [Calcomanías del terreno](#terrain-decals).

## Calcomanías del terreno {#terrain-decals}

Fuente: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Carreteras, pistas, plataformas de hormigón, líneas y letras pintadas, huellas de neumáticos: el res `TerrainDecals` (tipo `0x15E1F32E`) las guarda como geometría plana que el juego coloca sobre el terreno.

| Parte | Diseño |
|---|---|
| cabecera | en +16 un número de ranuras n, luego n ranuras de 16 bytes, luego el número de registros |
| registros | uno por lote de dibujo, uno tras otro, de longitud variable: 156 bytes de campos fijos (primer vértice en +32, número de triángulos en +36, repetición de textura en metros en +44), luego los bytes de vértices del lote (desplazamiento, tamaño), y una cola que nombra sus texturas por los GUID de partición de sus activos |
| vértices | 32 bytes: x, z (f32), 8 bytes empaquetados, u, v (f32), r, g, b, a (f16); cada lote es una lista plana de triángulos |
| índices | u32, contando desde 0 en cada lote; no se necesitan |

Comprobaciones:

- los rangos de vértices de los registros se suceden sin huecos y cubren exactamente todos los vértices, y el primer vértice de cada registro por 32 es su desplazamiento;
- leídos así, los triángulos son calcomanías compactas (letras, tiras de línea, parches); leídos con un vértice de desfase, son astillas que cruzan el mapa;
- casi todos los lotes nombran texturas en su cola: un mapa de color (`_cv`) con un mapa de opacidad (`_op`, canal rojo), o, en las marcas, una máscara de canales (`_rgb`).

Tras los GUID de textura, la cola lleva los parámetros de material del lote, codificados como los de un bloque de sombreador (mira Tintes más abajo). El color de pintura de una marca, de una huella de neumático o de una línea es el float3 con hash `607e`: un 0,64, 0,56, 0,48 arenoso para huellas en arena, casi negro para el alquitrán. Los mapas de opacidad son sobre todo de formato 62, un canal a 8 bytes por bloque, leído como BC4.

Un lote asigna su textura, o bien por posición en el mundo (u = x, v = z, con la textura repitiéndose cada tantos metros como indique la repetición: asfalto, hormigón, grava), o bien de 0 a 1 a lo largo de la calcomanía (una línea, una letra, una huella de neumático). Los registros se dibujan en el orden del archivo.

**El horneado.** `level --ground-texture M` pinta, bajo la extensión de las calcomanías y en losetas de como máximo 4.096 píxeles, el mapa de color del fondo (bilineal) y luego cada lote encima según su opacidad por el alfa del vértice. El color de los vértices no se usa: algunos vértices de lotes son verde o azul puros, y tiñeron las marcas de un nivel con esos colores. Los triángulos del mapa de alturas en esa zona pasan a ser partes `ground:terrain x<x> z<z>` que llevan la loseta. Cada lote se dibuja así:

| Los lotes nombran | Se dibuja como |
|---|---|
| un mapa de color (`_cv`) | el mapa, por su mapa de opacidad |
| un mapa de multiplicación (`_mult`) y un mapa de opacidad | la pintura (blanca si el material no nombra ninguna) por el mapa de multiplicación, por el mapa de opacidad: la línea central desgastada de una pista, las líneas de borde y las barras de umbral |
| una máscara de canales (`_rgb`) | la pintura, o si no blanca para líneas y letras, oscura para contornos, un oscurecimiento leve para desgaste, huellas de neumáticos, manchas, charcos y humedad, por la máscara |
| solo un mapa de opacidad, con una pintura | la pintura por el mapa de opacidad: huellas de neumáticos |

Una máscara de variación de carretera no es pintura: varía la superficie bajo ella, a cientos de metros de distancia, y no se dibuja, sea cual sea su pintura; pintada de blanco dibujó dos rectángulos pálidos de 150 a 250 m en las laderas de un nivel. El mapa `_mult` se toma como el desgaste propio de la pintura, no como un oscurecimiento del suelo bajo ella: es casi blanco, y la forma de la línea está en el mapa de opacidad.

Casi todos los lotes se dibujan, en unas pocas losetas de 0,5 m por píxel; la exportación crece unos pocos MB y tarda unos segundos más. Vistos desde arriba, las plataformas, las calles de rodaje y la red de carreteras quedan bajo las vallas y los edificios de los recintos y llevan a sus puertas.

Dibujadas como geometría propia, las calcomanías necesitarían mezcla alfa, que el escritor no lleva, y un desplazamiento sobre un terreno chocaría con él; el horneado las mantiene en el color propio del suelo.

## Texturas y materiales {#textures-and-materials}

Fuente: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Un res Texture (tipo `0x6BDE20BA`) es una cabecera de 180 bytes: tipo y formato de píxel en +8, ancho y alto en +22, número de mips en +30, el GUID del fragmento en +40, quince tamaños de mip en +56. El fragmento es la cadena de mips, del más grande al más pequeño. Algunos fragmentos no traen sus mips más grandes, que vienen en un paquete de alta resolución, y la longitud del fragmento dice desde qué mip empieza. El fragmento de ese paquete se nombra en +164; se lee desde los [complementos](#which-table-is-the-level) del nivel cuando hace falta un mip que falta en el fragmento principal, y su longitud más la del fragmento principal es la cadena completa.

| Formato | Se decodifica como | Evidencia |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineal) | la hoja de color de un depósito de plástico se decodifica así; como BC3 los mismos bytes son ruido |
| 61, 60 | BC3 | una hoja de color de una caja se decodifica limpia como BC3, no como BC1 ni BC7 |
| 57, 56, 55 | BC1 | medio byte por píxel |

El recurso de malla no nombra ninguna textura. El enlace está en los **depósitos de bloques de sombreador** del nivel (tipo de res `0x73312045`, uno por subnivel), indexados por los ocho bytes en +0x130 del registro de una sección de malla:

| Parte | Diseño |
|---|---|
| tabla, en 16 | (clave de sección u64, desplazamiento de descriptor u64), hasta que un desplazamiento cae fuera del res |
| descriptor | (desplazamiento del bloque u64, hash u64, tamaño del bloque u64) |
| bloque | los parámetros de sombreador de la sección; cada textura es un registro de 49 bytes: un byte, 16 bytes, el GUID de partición del activo de textura, su GUID de instancia |

La clave de sección del cajón aparece una vez en cada uno de los diez depósitos de los subniveles que la colocan, y su bloque nombra `t_mil_crate_03_cs` y `_nmt` entre los mapas de detalle compartidos. Un bloque nombra toda textura que muestrea el sombreador, y no se dice cuál es el mapa de color, así que se elige: una textura 2D sRGB cuyo nombre contiene la mayoría de las palabras del nombre del material (`M_ConcreteWall_01`: concrete, wall), luego las del nombre de la malla, luego una que no sea de detalle, de calcomanía (`t_de_...`) ni de daño, y luego la que menos bloques usan. El bloque de una señal de carretera nombra su panel `t_com_highwaysignage_01_cs` y una hoja de calcomanía `t_de_com_highwaysignage_01_ca` con un escudo tumbado; ambas coinciden en las palabras, y sin la regla de calcomanía la hoja ganaba por uso y la señal mostraba el escudo girado un cuarto, en todos los conjuntos de coordenadas de textura de la sección. Las texturas de campos de distancia con signo (`..._sdf`), las paletas y las máscaras de canales (`_rgb`) nunca se eligen, sea cual sea lo que compartan en palabras (los mapas `_rgba` sí se eligen: casi todos son color con alfa, y dejarlos fuera cambió el mapa propio de un tendido eléctrico y de una escalera por otros ajenos); un atlas de vegetación de un fondo `..._atlas_a_sdf` dibujado como color mostraba estrellas negras y blancas en los árboles, una paleta de edificios de un fondo daba un confeti de muestras en los muros, y un vidrio roto dibujado por su máscara de canales salía cian. Una sección cuyos únicos candidatos son mapas de detalle compartidos se queda de color plano.

**Paletas.** Los edificios de un fondo toman sus colores de una paleta, de 256 x 256 texels de muestras de 16 x 16: cada vértice lleva cuatro bytes (uso `0x1E`) cuyos dos primeros indican dónde está en la paleta su color, x e y de 0 a 255. `level` dibuja una sección así con la paleta como textura, con cada vértice en el centro de su muestra. Dibujados así, los bloques de fondo de un nivel salen como muros pastel, terracota y ventanas oscuras, donde antes eran blancos lisos.

**Superposiciones.** Los objetos grandes forman mosaico de una hoja de recorte a través de sus primeras coordenadas de textura, y superponen una capa encima por medio de las segundas, que caen entre 0 y 1: un desenrollado de todo el objeto. La superposición (`..._overlay_cs`, con su máscara `..._overlay_a`) guarda cómo se ve el objeto de lejos: las bandas rojas y el óxido de un depósito de petróleo; dibujados solo con la hoja de recorte, los depósitos de un nivel salían como paneles grises. Una sección cuyo bloque nombra una superposición con su máscara, y cuyas segundas coordenadas son ese desenrollado, se dibuja con la superposición a través de ellas (36 secciones en ese nivel).

**Tintes.** Muchos mapas de color son grises (la media de sus canales coincide dentro del 6 %): el sombreador los pinta con colores de los parámetros del bloque. Tras sus entradas de textura (49 bytes cada una), un bloque enumera sus parámetros, cada uno con una etiqueta de tipo (`f11af825` un float3, `a5e1f2de` un float4, `c1b1a014` un float, `4a4fc3a1` un entero), los bytes de marca `01 80` para un solo valor, un hash de dos bytes del nombre del parámetro, un recuento u32, el valor y un id de ocho bytes. Los nombres no se guardan. Siete hashes de nombre float3 actúan como tintes: en un nivel, tres de ellos guardan un color en cerca de 1 bloque de cada 6 cuyo mapa es gris y casi nunca donde el mapa tiene color propio, y los demás guardan los colores en que se pinta un mapa gris cuando el nombre del material lo indica (el adorno azul de un puente, `..._blue`: 0,047, 0,098, 0,171 frente a un 0,5 neutro). Una familia puede tener varios valores, uno por canal de una máscara, la mayoría neutros, y un valor con un canal casi nulo (verde puro en fachadas de ladrillo) elige un canal de máscara en lugar de pintar. `level` multiplica un mapa de color gris, en luz lineal, por el primer valor de cada familia que no es neutro ni es un selector de ese tipo, sobre su valor neutro, y guarda el resultado como una textura propia; un mapa con color se deja tal cual. La regla es la del propio exportador: no se lee qué canal de una máscara toma qué tinte. En un nivel, esto bajó la proporción de triángulos de estructura pintados casi de blanco del 19,4 % al 3,9 %.

**Variaciones de objeto.** Una malla se coloca en varios aspectos: un muro de almacén con una franja roja o azul y un número distinto pintado, o un contenedor en verde o gris. Cada copia colocada nombra su aspecto:

| Dónde | Campo |
|---|---|
| miembro de un grupo de modelos estáticos | +32: un array de un puntero por copia, a una variación de objeto o nulo |
| referencia de objeto | +120: un puntero a una variación de objeto o nulo |
| variación de objeto (partición `ov_...`, tipo `235f2a9c...`) | su primera instancia +32: el hash u32 de nombre de la variación |

El aspecto de una sección en una variación es el bloque de sombreador indexado por la propia clave de la sección con el hash de la variación sumado a sus primeros cuatro bytes, como u32 little-endian (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); una sección sin bloque bajo esa clave luce igual en todas las variaciones. Las bases de datos de variaciones de malla del nivel (`meshvariationdb_win32`) enumeran, por malla y hash de variación, los materiales que toca cada variación, pero no las claves: la regla se dedujo de las propias claves y se cumple en todas las secciones con variantes comprobadas (las cuatro variaciones de un muro, tres de sus secciones cada una). El bloque de una variación trae sus propias texturas además de sus tintes: el número pintado en el muro es una hoja de letras que nombra el bloque de la variación. Una gran parte de las copias agrupadas se colocan en una variación.

Un bloque se hornea una vez por cada conjunto de contenidos, y la entrada del depósito de una clave lleva un hash de ellos (el segundo u64 de la entrada). Cuando una sección no tiene bloque bajo la clave de su variación, la variación llega igualmente a ella a través de un *gemelo*: otra sección cuyo bloque por defecto tiene el mismo contenido y sí tiene uno. Sin gemelos, un muro cuyas longitudes comparten un mismo bloque por defecto puede salir en dos colores. Una sección sin variante propia toma la variante que tienen la mayoría de sus gemelos.

**Mallas destructibles.** Una malla que una partida puede derribar tiene un activo de destrucción de su propio nombre junto a ella (`.../br_x.destruction` para `.../br_x_mesh`): los edificios y muros rompibles (`br_`) y muchos objetos. `level` guarda sus superficies en partes propias, nombradas con ` (destructible)`, cuyos nodos glTF llevan `{"destructible": true}`. Sus estados destruidos son las mallas `dc_..._part<N>_mesh` que tienen al lado, cada una centrada en su propio origen; dónde se sitúa cada una está en el activo de destrucción, que no se lee, así que los estados destruidos no se exportan.

**Dejado fuera.** Las secciones de materiales de bloqueo provisional (`M_Whitebox`: unos pocos triángulos grandes sin textura que algunos edificios guardan junto a sus superficies, y que sobresalían del nivel como aletas blancas), las mallas hechas para escenas cinematográficas (un helicóptero colocado donde empieza su escena) y los auxiliares de iluminación (planos que bloquean la luz y nunca se dibujan). Los edificios generados de fondo de un nivel (`..._generated_blueprints_..._mesh`) se dibujan, pero los nombres de material de sus muros solo nombran mapas de ruido y sus vértices no llevan color, así que quedan lisos. Casi toda sección dibujada recibe un mapa de color.

**Hojas de letras.** El número pintado en un muro o la impresión de un cartel de una grúa es una sección propia cuyo mapa de color es una hoja (`_ca`): el alfa de una letra sobre pintura sólida, o una impresión. Sus primeras coordenadas de textura hacen mosaico del revoque del muro a lo largo del panel (u de -0,2 a 1,7 en un muro), lo que dibuja la hoja casi dos veces; el cuarto conjunto (`0x24`, o si no el tercero, `0x23`) la pone una sola vez (u de -1 a 0, v de 1 a 2, unas milésimas más allá en los niveles de detalle más gruesos). Donde el primer conjunto deja una copia de la imagen y el cuarto o el tercero cae dentro de una, la hoja se dibuja a través de él, desplazada a 0 a 1. Una hoja con alfa se dibuja 1 cm delante de la superficie sobre la que está pintada, que se dibuja debajo en el otro mapa de color del bloque, a través del primer conjunto: sin eso, los texels vacíos de la hoja mostraban el interior del muro. El segundo conjunto es el desenrollado de un objeto para su superposición y aquí no se usa.

**Mapas de recorte.** El cuarto canal del mapa de color significa cosas distintas según el nombre del mapa. En `_cs`, con gran diferencia el más común (893 de los mapas elegidos de un nivel), es suavidad: el 1 % del alfa de un mapa mediano cae a 0,1 de 0 o de 1. En `_cu` (hojas, hierba) y `_ca` (color y alfa) es opacidad: el 90 % y el 87 %. Un mapa de color llamado `..._cu` o `..._ca` cuyo alfa está al menos un 75 % cerca de 0 o de 1, al menos un 1 % por debajo de 0,5 y al menos un 5 % por encima, se escribe con su alfa, como PNG, y su material como `alphaMode` MASK de glTF, `alphaCutoff` 0,5, doble cara; así las tarjetas de hoja muestran hojas, no sus esquinas negras. La hoja de un árbol no tiene alfa alguno (4 de 255 como mucho): sus frondes se recortan por geometría, y con solo las dos primeras condiciones se recortaba toda la copa.

Las coordenadas de textura son el uso de vértice `0x21`, dos medias (formato 6) o dos flotantes (formato 2). Las secciones llevan hasta tres conjuntos más (`0x22` a `0x24`) para capas de calcomanía y de detalle. Las coordenadas hacen mosaico: el lado acanalado de un contenedor va de -1,6 a 1,8, las losetas de fondo del terreno caen enteras fuera de 0..1, y en un nivel el 23 % de los triángulos texturizados llega fuera de 0..1. Se escriben tal cual, con un muestreador que repite; el visor de 3DHeat envuelve cada textura que se repite dentro de su atlas. Un renderizador que las recorta en su lugar estira las costillas al doble de su ancho, convierte un suelo de hormigón en rayas a lo largo de un eje, y da a las vigas de acero de una torre el color del borde de su textura; para él, `--clamped-uvs` corta cada triángulo a lo largo de las líneas donde su textura se repite y mueve cada trozo a 0..1 (mira [Formato de salida](output-format.md)). Después, el 0,03 % de los triángulos texturizados, sobre los que una textura se repite más de 16 veces, llega fuera, y un triángulo que el corte dejaría en más de 4 trozos se dibuja con el color medio de su textura: la corteza se repite por cada rama, y cortada, los árboles de un nivel pasaron de 6,4 a 24 millones de triángulos.

El mapa de alturas no tiene un mapa de color propio que se pueda leer. Donde lo cubre uno de los mapas del fondo del terreno, se colorea desde él: las coordenadas de textura del fondo son una función lineal de x y z del mundo (el 99 % de sus vértices a menos de 0,001 de ella; el mapa cubre un cuadrado de 65.536 m, girado un cuarto de vuelta), y la misma función da las del mapa de alturas. El nivel trae los mips de ese mapa desde 2.048 px hacia abajo, así que el mapa de alturas recibe 32 m por píxel. Su roca oscura está en el suelo empinado: la correlación entre oscuridad y pendiente es 0,48, y como mucho 0,34 para las otras siete orientaciones.

El fondo de otro nivel son ocho losetas cercanas y ocho lejanas alrededor del área de juego, cada una repitiendo su propia textura sobre la loseta, y ninguna llega al mapa de alturas. Cada textura de fondo se ajusta por separado, y cuando ninguna cubre el mapa de alturas, toma el color medio que muestra el fondo a menos de un kilómetro del cuadrado de terreno, que `--ground-texture` hornea bajo las calcomanías. Un material de fondo es el que tiene `TerrainBackdrop` en su nombre, o `BD_` y `Terrain` (`M_BD_<site>_Terrain..._Near`); o una malla de fondo (`bd_..._terrain<site>_04_far_mesh`) lleva un material de terreno corriente (`M_<region>_Terrain<site>_04_Far`), que las dos primeras reglas dejaban pasar en un nivel y que así coloreaba su suelo a partir de sus superficies.

Donde ningún mapa de fondo cubre el mapa de alturas, sin embargo, este toma el color medio de las propias superficies del terreno antes que el promedio del fondo: los mapas de color `_cv` que nombran los bloques de sombreador del grafo de capas del terreno (27 en un nivel: arenas, gravas, suelos, hierba, hormigón agrietado), cada uno promediado, luego la mediana de cada canal, dejando fuera la superficie por defecto del motor. Un fondo puede ser otro paisaje por completo: en un nivel, su promedio (95, 99, 80 en sRGB) volvía gris el suelo del área de juego, un gris que el juego no muestra. Con `--ground-texture`, ese color se multiplica por el doble del mapa de color, que deja el gris medio tal cual, y se hornea con las calcomanías encima sobre la extensión de ambos, de las calcomanías y del mapa de color.

Frente al juego, el color mediano del suelo del área de juego horneada de cada nivel y de los fotogramas de juego (filas del 55 al 72 % de la imagen junto al HUD, 24 fotogramas cada una; sRGB; los fotogramas van iluminados y con gradación, así que las razones r/g y b/g son la comparación justa):

| Nivel | Fotogramas | Promedio del fondo | Ahora |
|---|---|---|---|
| primero | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| segundo | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| tercero | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

El primero se corrigió; los otros dos estaban antes un poco más cerca en matiz. Un solo color para un nivel entero no puede ser correcto en todas partes; las máscaras sí podrían.

## Malla de navegación {#navigation-mesh}

Fuente: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Un nivel trae una partición por agente, `<level>/dbt/<level>_navmesh_layer_<n>`: en un nivel la capa 0 es el soldado (1,8 m de alto, paso de 0,18 m, radio de 0,4 m) y otras dos son vehículos (3,5 y 10 m de alto). Cada partición tiene dos arrays:

| Array | Elemento |
|---|---|
| teselas | 28 bytes: u32 0, u32 hash, u32 0, u32 índice de fragmento, u16 x de tesela, u16 z de tesela, u32 desplazamiento, u32 tamaño |
| fragmentos | 20 bytes: el GUID del fragmento, u32 tamaño |

Una tesela son `size` bytes en `offset` del fragmento `chunk index`, en little-endian, y tiene el diseño de Detour (Recast Navigation) tras una cabecera más larga:

| Desplazamiento | Contenido |
|---|---|
| 0 | `VAND`, versión 7 |
| 24 | recuentos: polígonos, vértices, enlaces, mallas de detalle, vértices de detalle, triángulos de detalle, nodos de volumen delimitador, enlaces fuera de malla, el primer polígono fuera de malla |
| 188 | altura, paso y radio del agente |
| 200 | la caja delimitadora de la tesela, seis flotantes |
| 232 | vértices: flotantes x, y, z, coordenadas del mundo |
| siguiente límite de 8 bytes | polígonos, 32 bytes: u32, seis índices de vértice u16, seis vecinos u16, marca u16, el recuento de vértices en +30, en +31 el área (seis bits bajos) y el tipo (los dos altos) |
| después, empaquetados | enlaces (16 bytes), mallas de detalle (12: primer vértice de detalle u32, primer triángulo de detalle u32, recuento de vértices y de triángulos u8), vértices de detalle (tres flotantes), triángulos de detalle (tres índices y marcas), nodos de volumen delimitador (16), enlaces fuera de malla (80) |

En cada tesela de los niveles comprobados, estos suman el tamaño de la tesela hasta el byte, y las mallas de detalle numeran los polígonos antes del primero fuera de malla.

Un polígono es plano entre sus esquinas; su **malla de detalle** guarda la altura real de la superficie sobre los baches, las rocas y los escalones, y es lo que se dibuja. El índice de un triángulo de detalle por debajo del número de esquinas del polígono es esa esquina; si no, el vértice de detalle `first + index - corners`. Abanicar los polígonos en lugar de eso pone muchos más triángulos bajo el terreno y crea astillas largas; con las mallas de detalle ninguno es más largo que la diagonal de una tesela de 16 m más el escalón de una pendiente.

El tipo 0 es suelo, el tipo 2 son pequeños parches empinados (unos 45 grados, de un metro cuadrado cada uno), y el tipo 1 es un enlace entre superficies: sus esquinas abarcan 125 m de altura o más y caen fuera de la tesela, algunas en el origen. Los enlaces se dejan fuera; el resto se dibuja por sus mallas de detalle, o se abanica en una tesela sin ninguna.

Comprobaciones: los tamaños de los fragmentos suman exactamente los de las teselas; cada vértice de superficie cae dentro de la caja de su tesela con una tolerancia de un metro aproximadamente; casi todos los triángulos miran hacia arriba. Una tesela que falla se rechaza y se cuenta, y en ese nivel no se rechaza ninguna.

Lo que cubre la malla del soldado, visto desde arriba en el nivel de prueba: el suelo, los pisos, las escaleras y algunos tejados, y no las partes superiores de los contenedores de carga. Es el mapa que usa la IA para saber dónde puede estar de pie un soldado, lo más cercano que los archivos llegan a dónde están los jugadores.

## No implementado {#not-implemented}

- El grafo de capas del terreno, que mezcla sus capas de superficie (mira [Capas del terreno](#terrain-layers)): el color del suelo sigue una regla propia de este lector, a partir de las máscaras de las capas y de la pendiente del mapa de alturas, y los niveles cuyas páginas de máscara no encajan entre sí reciben un solo color.
- Parámetros de color de los materiales de calcomanía: las marcas a través de máscaras de canales se pintan con un color neutro.
- Planos de objeto que no son mallas (lógica de juego, efectos, sonidos).
- Estados destruidos de las mallas destructibles: sus posiciones están en el activo de destrucción, que no se lee.
- Los enlaces de la malla de navegación (saltos, escaleras de mano, pasos por encima) y sus capas de vehículos.
- Mallas de niveles guardadas en línea dentro del res (10 mallas en un nivel, accesorios), y los huesos y partes de mallas esqueletizadas y compuestas, y las normales (que calcula el escritor).
- Mapas de normales, de rugosidad y otros; alfa distinto de un recorte (el vidrio translúcido y las calcomanías se dibujan opacos).
- Huecos del terreno: un sombreador de huecos está nombrado, pero no se encuentra lo que lee, así que el mapa de alturas no se recorta donde corre el suelo transitable (mira [Capas del terreno](#terrain-layers)).
- Qué tinte va con qué canal de la máscara de un material: un mapa gris toma el primer tinte que no es neutro (mira [Texturas y materiales](#textures-and-materials)).
- Efectos (rutas `fx/`) y las mallas de cable, cuyas cajas delimitadoras miden decenas de kilómetros; se dejan fuera y se cuentan en el resumen.
- La forma de tabla ofuscada con XOR.
