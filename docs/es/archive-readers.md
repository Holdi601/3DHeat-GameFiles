---
title: Lectores de archivos
nav_order: 9
lang: es
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Lectores de archivos {#archive-readers}

Un **contenedor** (o archivo) es un único archivo grande en el que un juego mete muchos archivos. Un **CRC** o hash es una huella corta de unos bytes: si coincide, los bytes se leyeron bien. Una **caja delimitadora** es la caja más pequeña que rodea a un modelo.

Debajo de los comandos hay lectores para los contenedores que usan los juegos. Sus formatos no están documentados, salvo el VPK de Valve y el `.cdae` de BeamNG, así que "compatible" tiene que significar **comprobado con archivos reales**, y no solo "no se cerró". Cada lector se comprueba contra algo que el formato garantiza: un hash, un CRC, una cadena de desplazamientos que tiene que cerrarse, una caja delimitadora guardada. Cuando una comprobación falla, el lector se niega con un mensaje en lugar de adivinar. Una malla incorrecta parece correcta hasta que alguien la pone junto al circuito.

| Lector | Módulo | Lee | No lee | Se llega desde |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versiones 8-12: índice, entradas, bloques Zlib/Gzip/Oodle, AES con una clave que tú proporcionas | versiones anteriores a la 8, índices solo con hash de ruta, entradas de desbordamiento, el contenido de los assets | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5 o posterior, comprobado en la v8), paquetes zen, propiedades sin versión de unas pocas clases de componentes, mallas estáticas cocinadas, texturas, texturas virtuales de streaming | contenedores cifrados, paquetes con versión, mallas solo Nanite, propiedades de otras clases | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | bloques Oodle a través de una biblioteca que ya está en el equipo | cualquier cosa sin esa biblioteca; nunca se incluye | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` formato 22 o posterior (Unity 2020 a 6000), paquetes `UnityFS`, mallas sin comprimir, incluidos los `.resS` | formatos anteriores a 2020, árboles de tipos incrustados, mallas comprimidas, cualquier clase que no sea `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | árboles `.toc` de DbObject y tablas binarias de secciones, paquetes de instalación, ubicaciones de fragmentos, paquetes en línea y sus manifiestos, particiones RIFF EBX, mallas MeshSet, el campo de alturas del terreno, texturas BC1/BC3/BC7 y sus bloques de shaders, colocación de grupos de modelos estáticos | tablas ofuscadas con XOR, el color del terreno cerca del suelo y sus huecos, mapas de normales, canal alfa que no sea de recortes | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versiones 1 y 2, archivos divididos, datos de precarga, comprobación CRC | recursos compilados (`.vmdl_c`, `.vtex_c`), el formato de la malla de navegación de CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, sin comprimir), geometría `.modelbin`, muestras `.pb` (BC1, BC7, RGBA), colocaciones `.pgeo`, hashes de texturas de materiales | otros formatos de vértices e índices, otros formatos de textura, capas de shader del terreno | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` y `extract` (`.minizip`) |
| [Archivos de BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | el sistema de archivos montado de los zip, escenas JSON y TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiales | mallas con esqueleto y de calcomanías, secuencias animadas, cobertura de suelo procedural | `course` (BeamNG), `identify` (zips, `.cdae`, `.ter`), `list` y `extract` (zips) |

## Reglas que sigue todo lector {#rules-every-reader-follows}

- **Ninguna clave incluida, ninguna recuperada.** Un archivo cifrado solo se abre con una clave que tú pasas (Unreal `.pak`, `--key`). Un contenedor IoStore cifrado se rechaza. Nada busca una clave dentro de un ejecutable ni lee la memoria de otro proceso. Consulta [Reglas y licencias](rules-and-licences.md).
- **No se incluye código propietario.** Oodle se carga desde un juego o motor que ya está instalado en el equipo.
- **Negarse antes que adivinar.** Una versión, códec, formato de vértices o formato de textura desconocido provoca un error concreto, como `texture format 42 has not been identified; refusing to guess`.
- **Solo lectura.** Ningún lector escribe en la carpeta de un juego. Las exportaciones van donde tú digas.

## Qué significa "verificado" {#what-verified-meant}

Las cifras de verificación que aparecen en estas páginas vienen de las cadenas de documentación de los módulos (docstrings). Se midieron con juegos instalados mientras se escribía cada lector. Las pruebas sintéticas (ver [Desarrollo](development.md)) fijan la estructura de los campos. Las pruebas con juegos instalados repiten algunas comprobaciones cuando el juego está en el equipo, y se omiten si no lo está. Las cifras que no cubre ninguna prueba no se han vuelto a comprobar desde entonces.
