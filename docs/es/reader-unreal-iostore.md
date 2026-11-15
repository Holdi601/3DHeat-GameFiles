---
title: Unreal 5 IoStore
nav_order: 2
lang: "es"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 distribuye la mayor parte del contenido en contenedores **IoStore**: una tabla de contenidos `.utoc` y los datos `.ucas` que indexa. Un `.pak` sigue existiendo, pero contiene poco más que un pie. Los lectores de aquí van desde el contenedor hasta la geometría y los píxeles, hasta donde necesita un circuito. Se construyeron y comprobaron con Assetto Corsa Rally (Unreal 5.6.1, modificado), y se llega a ellos a través de la exportación de circuito de [Assetto Corsa Rally](course-assetto-corsa-rally.md). `identify`, `list` y `extract` aceptan un `.utoc` (o el `.ucas` que está a su lado): los archivos que nombra su directorio, por su ruta bajo el punto de montaje. Un contenedor sin índice de directorio no nombra archivos y no se lista.

| Capa | Módulo |
|---|---|
| contenedores y el almacén | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| paquetes "zen" cocinados | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| datos de propiedades sin versión | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| mallas estáticas | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| texturas y texturas virtuales | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Contenedores (`.utoc`, `.ucas`) {#containers-utoc-ucas}

La tabla de contenidos, versión 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Las versiones anteriores a la 5 se rechazan. Solo la versión 8 se ha comprobado con archivos reales.
- **Los contenedores cifrados se rechazan**: `<file> is encrypted. This tool holds no keys and recovers none.` No se puede pasar ninguna clave para IoStore.
- Métodos de bloque: sin comprimir, `oodle` (a través de [Oodle](reader-oodle.md)), `zlib`, `lz4`. Cualquier otro se rechaza.
- Las particiones tras la primera viven en `<name>_s<n>.ucas`.

El **almacén** abre cada `.utoc` de la carpeta `Paks` del juego e indexa cada ruta de paquete, sin distinguir mayúsculas. Los contenedores que no se abren se omiten. `global.utoc` proporciona los objetos de script (clases C++). Los datos masivos de un paquete (`.ubulk`) se encuentran como el fragmento con el mismo id y tipo `BULK_DATA`, en el contenedor que lo tenga.

Comprobado: cada contenedor del juego instalado y cada ruta de paquete de él.

## Paquetes zen {#zen-packages}

Un paquete cocinado es una cabecera (nombres, imports, exports, bundles de exports, tablas de dependencias, nombres de paquetes importados) seguida de los datos serializados de cada export. Los objetos se referencian entre sí mediante un `FPackageObjectIndex` de 64 bits cuyos dos bits altos indican qué es: un export de este paquete, un objeto de script, un import de otro paquete (qué paquete, y el export por un hash de su ruta), o nulo.

- El resumen cambió en la 5.3 (bundles de dependencias y nombres de paquetes importados) y otra vez en la 5.6 (dos desplazamientos más). Se prueban ambos diseños, y se conserva el que analiza su tabla de nombres, así que no hace falta conocer la versión.
- Los paquetes **con versión** (de estilo sin cocinar) se rechazan.
- Los nombres de paquetes importados llevan un número. Un paquete `_Terrain` numerado 1 es el archivo `_Terrain_0`.
- Los nombres `/Game/...` se corresponden con la carpeta `Content` del proyecto en el almacén.
- Las referencias se siguen entre paquetes emparejando el hash público del export.

Comprobado: cada celda de cada etapa se abre.

## Propiedades sin versión {#unversioned-properties}

Los exports cocinados de Unreal 5 no nombran sus propiedades. Un export empieza con una cabecera de tramos, "salta tantas ranuras, luego tantas presentes", y una máscara que dice cuáles de las presentes son cero y no llevan bytes. Los valores siguen en el orden de propiedades de la clase. Para leerlo hace falta el **esquema** de cada clase: su lista de propiedades, en exactamente el orden en que la construye el motor (primero las propias, luego las del padre, una ranura por elemento de array estático, sin las propiedades solo de editor).

Los esquemas van incrustados para las clases que necesita un circuito:

| Clase | Cadena |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | las cadenas ISM (presentes, pero la exportación de circuito no las usa, porque esta versión las reordenó) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

También cubren las estructuras que contienen estas (`FBodyInstance`, respuestas de colisión y otras). Los tipos de valor se leen por codificación: números y vectores de tamaño fijo (`FVector`, `FRotator` como dobles, `FTransform`...), `FName`, enumeraciones (un byte), referencias a objetos (índice de paquete `i32`), rutas de objeto blando, arrays, estructuras anidadas, y delegados multicast (se saltan).

Los esquemas son **solo nombres y tipos de propiedades**, derivados de las cabeceras de Unreal Engine 5.6.1 (que Epic pone a disposición de cualquiera con una cuenta vinculada). No se incluye código del motor. Esta versión tiene **dos ranuras más en `UPrimitiveComponent`** que las cabeceras, y **una más en el volumen de textura virtual**, halladas a partir de los datos y marcadas `(unknown)`. Un valor presente en una de esas ranuras es un error, no una suposición. Una ranura más allá del final de un esquema, o un tipo desconocido, lanza `PropertyError`.

Comprobado: cada componente de malla estática y de escena de cada etapa se decodifica, terminando cada uno exactamente en la cola nativa fija de su clase. Un parche del juego puede mover las ranuras. El lector entonces lanza un error, y el circuito informa de cuántos componentes han fallado.

## Mallas estáticas {#static-meshes}

Un export `UStaticMesh` son sus propiedades seguidas de datos nativos. Las propiedades no hacen falta para la geometría y no se leen. La parte nativa se encuentra por su inicio fijo: un flag de GUID a cero, dos bytes de flags de tira, `bCooked = 1`, y el índice del export `BodySetup` propio de la malla. Luego se lee en el orden en que `UStaticMesh::Serialize` y `FStaticMeshRenderData::Serialize` la escriben para una malla **cocinada, no Nanite**:

- hasta 16 niveles de detalle, cada uno con sus secciones (material, primer índice, número de triángulos), límites, y cuando está **en línea**: el búfer de posiciones (float32 x 3), tangentes, UV (todos los canales, de media o de precisión completa), colores, y el búfer de índices (de 16 o 32 bits);
- lo que sigue (búferes de índices invertidos y de solo profundidad, datos de trazado de rayos, muestreadores ponderados por área) se salta para llegar al siguiente nivel.

Un nivel que no está guardado en línea termina la lista. Una malla sin ninguno se rechaza. Las posiciones son las de Unreal: centímetros, X hacia delante, Y a la derecha, Z hacia arriba.

Comprobado: casi toda malla muestreada se decodifica (el resto son esqueléticas), y la extensión decodificada de una loseta de carretera coincide con los límites que guarda.

## Texturas {#textures}

Un export `Texture2D` son sus propiedades y luego sus datos de plataforma cocinados: el nombre del formato de píxel, el tamaño, y una tabla de niveles de mip, cada uno apuntando al mapa de datos masivos del paquete (desplazamiento, tamaño, banderas; en línea dentro del export cuando está activo el flag `0x40`, o si no en el `.ubulk`). Los datos de plataforma se encuentran por su propia forma, no saltando las propiedades, así que el diseño de propiedades de la clase de textura no importa. Se decodifica el primer mip que no sea mayor que el tamaño pedido.

| Formato de Unreal | Decodificado como |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | RGBA de 8 bits |
| `PF_G8` | gris de 8 bits |

Comprobado: una imagen satélite DXT5 de 4096 px cuyos trece niveles son exactamente los tamaños de las entradas masivas.

## Texturas virtuales de streaming {#streaming-virtual-textures}

Un `VirtualTexture2D` horneado son losetas cuadradas con borde, por nivel de detalle, direccionadas por **código Morton** (x en los bits pares), guardadas en fragmentos de los datos masivos del paquete. El diseño se lee como lo escribe `FVirtualTextureBuiltData::Serialize` en Unreal 5.6: capas, tamaño de loseta, borde, tablas de direcciones de losetas por mip, formatos de capa, y el fragmento *n* como la entrada masiva *n*. Una región de la textura se ensambla loseta a loseta, quitando los bordes, desde el nivel cuya resolución está más cerca de la pedida. Solo se lee la primera capa, y solo en los formatos de arriba.

Comprobado: las losetas de un fragmento de textura virtual se cuentan hasta el byte.
