---
title: Desarrollo
nav_order: 14
lang: "es"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Desarrollo {#development}

## Estructura {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Mapa de módulos {#module-map}

| Módulo | Qué hace |
|---|---|
| `__main__.py` | ejecuta la comprobación de actualización y luego `cli.main()` |
| `cli.py` | los verbos, `identify`, el despacho de archivos, el escritor de circuitos de Forza |
| `lapinput.py` | cada forma de vuelta en posiciones; búsqueda en la biblioteca de FH Companion |
| `corridor.py` | la banda a cada lado de la conducción, como una rasterización de 4 m |
| `surfaces.py` | los tipos de suelo, sus nombres de parte y sus colores |
| `glb.py` | el escritor de `.glb` (partes, normales, colores, texturas, cuantización) |
| `courseexport.py` | Forza: UV de losetas planas, división carretera/arcén, horneado del suelo, elevación de calcomanías |
| `forzainstall.py` | bibliotecas de Steam y Xbox; a qué circuito de Forza pertenece una caja |
| `minizip.py` | archivos `.minizip` de ForzaTech y sus listas de nombres |
| `forzatech.py` | `.modelbin`: fragmentos, búferes, diseños, submallas, materiales |
| `forzaterrain.py` | losetas de terreno por lugar; clases de superficie |
| `forzatexture.py` | muestras `.pb`; mapas de losetas; el horneado del suelo |
| `forzamaterial.py` | `AssetManifest.xml`; qué colores de textura tiene un modelo; temporadas |
| `forzaplacement.py` | colocaciones `.pgeo`, niveles de modelo, texturas, recortes, sustitutos, el presupuesto |
| `beamng.py` | instalación de BeamNG, sistema de archivos montado, escena, terreno, materiales |
| `beamngcourse.py` | la exportación de circuito de BeamNG |
| `beamngshape.py` | formas compiladas `.cdae` |
| `beamngcollada.py` | respaldo `.dae` |
| `acrally.py` | instalación de AC Rally, etapas, colocación de componentes, volumen de textura virtual |
| `acrallycourse.py` | la exportación de circuito de AC Rally: ajuste de marco, suelo, colocación |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | paquetes cocinados de Unreal 5 |
| `unversioned.py` | esquemas y lector de propiedades sin versión |
| `unrealmesh.py` | mallas estáticas cocinadas |
| `unrealtexture.py` | texturas y texturas virtuales de streaming |
| `oodle.py` | buscar y llamar a una biblioteca Oodle instalada |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | contenedores, paquetes y mallas de Unity |
| `frostbite.py` | `.toc` de Frostbite, tablas de secciones, paquetes de instalación, ubicaciones de fragmentos, datos |
| `frostbitebundle.py` | paquetes en línea de Frostbite, manifiestos de paquetes, el catálogo de un nivel, la lista de niveles |
| `frostbiteebx.py` | particiones RIFF EBX de Frostbite sin biblioteca de tipos |
| `frostbitemesh.py` | MeshSet de Frostbite y sus fragmentos de nivel de detalle |
| `frostbiteterrain.py` | árbol de streaming del terreno de Frostbite, páginas de altura, la malla del suelo |
| `frostbitematerial.py` | texturas de Frostbite (mips BC1/BC3/BC7), depósitos de bloques de shader, elección del mapa de color |
| `frostbitedecals.py` | calcomanías del terreno de Frostbite y el horneado del suelo |
| `frostbitenav.py` | teselas de malla de navegación de Frostbite: las superficies transitables de los soldados |
| `frostbitelevel.py` | grupos de modelos estáticos de Frostbite, colocación, la exportación `level` |
| `vpk.py` | VPK de Source 2 |
| `unreallandscape.py` | componentes de paisaje de Unreal 5: mapas de altura en la malla del suelo (`ue-map`) |
| `unreallevel.py` | mapas World Partition de Unreal 5: listado, estructuras HLOD, agua, la exportación `ue-map` |
| `enfusion.py` | `.pak` de Enfusion, `.edds`, losetas de terreno, `resourceDatabase.rdb` |
| `enfusionworld.py` | mundos de Arma Reforger: archivos `.ent`, cajas, la exportación `enfusion-world` |
| `forzacars.py` | cada coche de Forza a bajo detalle en `.h3dcars` (`cars`) |

Todos los módulos están en GitHub, en
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Ejecutar las pruebas {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` define `testpaths = tests` y `-q`. Importan dos tipos de prueba, por razones distintas:

- **Pruebas sintéticas.** Construyen archivos byte a byte y se ejecutan en cualquier equipo. Fijan las estructuras de campos que en algún momento estuvieron mal: la base de 64 bits del segmento `.minizip` y su relleno de alineación, el escape del tamaño de bloque de pak, el u32 del encabezado de Unity entre dos int64, el índice `0x7FFF` de VPK, la X dividida de la normal de Forza.
- **Pruebas con juegos instalados.** Se ejecutan contra los archivos reales cuando el juego está en el equipo, y **se omiten** (no fallan) cuando no lo está. Son lo único que detecta una estructura que es correcta para un archivo pequeño y errónea para uno grande.

### Accesorios de prueba {#fixtures}

| Accesorio | Construye |
|---|---|
| `tests/forza_fixtures.py` | archivos `.minizip` (con la base de 64 bits, relleno, códecs mixtos), manifiestos, modelos `.modelbin` y terreno, muestras `.pb` |
| `tests/beamng_fixtures.py` | una pequeña instalación de BeamNG: `gameengine.zip`, `content`, un zip de nivel con un terreno de 64 m, una franja de asfalto, una calcomanía de carretera, un raíl, un prefab, un elemento de bosque, el mar, materiales y formas `.cdae` en el diseño documentado |
| `tests/unreal_fixtures.py` | un contenedor IoStore con un directorio, un paquete zen, un bloque de propiedades sin versión |
| `tests/frostbite_fixtures.py` | tablas, paquetes, particiones EBX, mallas y páginas de terreno de Frostbite, byte a byte |

### Archivos de prueba {#test-files}

| Archivo | Cubre |
|---|---|
| `test_minizip.py` | lectura de vuelta, la base de 64 bits, tablas de paquetes pares e impares, rechazos, el archivo de nombres |
| `test_forzatech.py` | la tabla y la cadena de fragmentos, rechazos; instalado: las cadenas y etiquetas de modelos reales |
| `test_forza_geometry.py` | colocación en el mundo, diseño de vértices, formatos rechazados, submallas, normales y UV |
| `test_forzaterrain.py` | la rejilla de losetas (1023 frente a 512 m), recorte, extracción |
| `test_forzatexture.py` | cabecera de muestra, decodificación, la estantería de texturas, el horneado del suelo |
| `test_forzamaterial.py` | el manifiesto, nombres, hashes de material, la elección de color, temporadas |
| `test_forzaplacement.py` | el registro `.pgeo`, colocación de copias, niveles, variantes, superficies translúcidas, una caja completa, el presupuesto, el color provisional, el presupuesto automático; instalado: bordillos sobre el suelo |
| `test_forzainstall.py` | encontrar el juego, elegir el circuito |
| `test_courseexport.py` | UV de losetas, plan de partes, elevación de calcomanías |
| `test_course_cli.py` | los verbos `course` y `courses` completos sobre un circuito sintético; `terrain --route` con una marca de orden de bytes, y sin `bounds` |
| `test_archive_cli.py` | `identify`, `list` y `extract` sobre cada archivo con lector (`.pak`, IoStore, `.vpk`, `.minizip` con y sin su lista de nombres, zip, `.cdae`, `.ter`); los fallos como una línea y un código de salida: un pak cifrado, un contenedor cifrado, un archivo que no es un archivo, una `--key` incorrecta |
| `test_corridor.py` | la banda, cortar el terreno con ella |
| `test_lapinput.py` | cada forma de vuelta, la caja, los fallos, la búsqueda de nombres de circuito, qué juego es una carpeta |
| `test_surfaces.py` | qué nombres deciden una superficie, cuáles no, nombres de partes |
| `test_glb.py` | el archivo es válido, los nodos llevan la clase, rechazos, cuantización |
| `test_beamng.py` | formas, el nivel, categorías, encontrar el nivel a partir de una vuelta, el circuito, el respaldo Collada; instalado: `.cdae` frente a `.dae`, todo nivel se abre |
| `test_acrally.py` | contenedores, paquetes, propiedades, transformaciones, el ajuste de marco, partes y presupuesto de los modelos colocados, texturas virtuales; instalado: etapas y el color de suelo horneado |
| `test_pak.py` | pie, entradas, el escape del tamaño de bloque, rechazos; instalado: desplazamientos y SHA-1 |
| `test_unity.py` | rechazos; instalado: la tabla de objetos cubre el archivo, cadenas de versión, límites de las mallas |
| `test_frostbite.py` | cabeceras con firma frente a ofuscadas, rechazos, paquetes de instalación (dos paquetes con el mismo número de blob); instalado: cada tabla, superpaquetes, cadenas de secciones, ids distintos, muestras de datos del paquete correcto |
| `test_frostbitelevel.py` | ids de fragmento emparejados con su propia ubicación, paquetes en línea, manifiestos, una MeshSet con una sección de sombra y UV, un miembro de grupo, la convención de transformación, un terreno de dos niveles, elección del mapa de color, un fragmento de textura sin sus mips más grandes, el muestreador repetido, registros de calcomanía, una calcomanía compuesta por su alfa, una hoja de calcomanías que pierde frente al mapa propio de una superficie, la textura de una señal dibujada como su panel, teselas de navegación (superficies conservadas, enlaces omitidos, rechazos, mallas de detalle), texturas repetidas escritas con sus propias coordenadas, triángulos cortados donde su textura se repite para salida con recorte, el color del suelo a partir de sus materiales de superficie, páginas de máscara (BC4 y sin comprimir) colocadas en sus cuadrantes y rechazadas si sus bordes no encajan, páginas de mapa de color colocadas en sus cuadrantes y halladas después de las páginas de máscara que cuenta el árbol de máscaras, campos de distancia, paletas y máscaras de canal que nunca se toman por color, el tinte de un bloque y un mapa en grises pintado con él, un vértice de paleta en el centro de su muestra, la rejilla de pendiente extendida de vuelta en bilineal, la superposición de un objeto dibujada a través de su desenvolvimiento, una variación cuyo bloque se identifica por su hash y se alcanza mediante un bloque gemelo, una hoja de letras colocada por sus cuartas coordenadas de textura sobre la superficie que pinta, la pintura de una calcomanía leída de su material, líneas de pista y huellas de neumáticos dibujadas, mapas de un solo canal decodificados, mallas destructibles etiquetadas en sus partes y extras, mallas de blockout, cinemáticas e iluminación omitidas y un diseño de mapa de color que no se lee, mapas de recorte y sus materiales enmascarados, materiales PNG de dos caras, fondos de losetas nombrados por su malla; instalado: las calcomanías de terreno del nivel, el catálogo del nivel más grande, mallas dentro de sus límites, miembros de grupo, vegetación sobre el terreno decodificado |
| `test_vpk.py` | el directorio, rechazos, archivos divididos; instalado: los mapas se abren, los CRC coinciden, la malla de navegación |
| `test_enfusion.py` | `.pak` de Enfusion, `.edds`, losetas de terreno y archivos de mundo; la exportación `enfusion-world` |
| `test_forzacars.py` | el archivo `.h3dcars` que escribe el verbo `cars` |
| `test_unreallevel.py` | paisajes de Unreal 5, estructuras HLOD, agua; la exportación `ue-map` |

## Pruebas con juegos instalados {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
busca juegos para las pruebas. `steam_common()` lista la carpeta `steamapps\common` de cada biblioteca de Steam (incluidas las carpetas propias de Steam), e `installed(*globs)` devuelve las rutas que coinciden con cualquiera de los patrones bajo ellas, recursivamente cuando un patrón tiene `**`. Cada prueba decide lo que necesita:

| Prueba | Busca | Se omite con |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` con un índice **sin cifrar**, hasta 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` en `*/*_Data` o `*/*/*_Data` que el lector acepta, hasta 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, hasta 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | los circuitos de la biblioteca de FH Companion (inicio y final a 50 m), con más vueltas, que `find_track` ubica; o `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Ejecuta solo las pruebas de un juego, o apunta la prueba de bordillos de Forza a un circuito:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Las pruebas con juegos instalados solo leen de los juegos. No escriben nada en las carpetas de los juegos. Las salidas de prueba van a las carpetas temporales de pytest.

## Convenciones {#conventions}

- **Negarse antes que adivinar.** Cada lector lanza su propia excepción (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) con un mensaje que dice qué se encontró y por qué no se leyó.
- **Comprobar contra el propio formato.** Un hash, un CRC, una cadena de desplazamientos, una caja delimitadora guardada, el terreno conducido sobre el suelo. No "no se cerró".
- **Sin claves, sin código propietario incluido.** Ver [Reglas y licencias](rules-and-licences.md).
- **Los datos confidenciales quedan fuera.** Los archivos de juego, las exportaciones, las vueltas, las grabaciones y las capturas nunca entran en el repositorio. `.gitignore` los excluye por carpeta y por tipo. Las pruebas usan datos sintéticos y juegos instalados, nunca contenido de juego incluido en el repositorio.
