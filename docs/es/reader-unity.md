---
title: Unity
nav_order: 4
lang: es
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, paquetes, mallas {#unity-serializedfile-bundles-meshes}

**Lista objetos y decodifica mallas** de `SerializedFile` de Unity formato 22 o posterior (Unity 2020 a 6000), y abre los paquetes `UnityFS`. No hay exportación de circuitos de Unity.

Fuentes: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Comandos: `identify` (contenedores y paquetes), `meshes` (solo contenedores sueltos).

## El contenedor {#the-container}

Unity distribuye un nivel como grafos de objetos serializados: `globalgamemanagers`, `sharedassets*.assets`, `resources.assets`, `level*`, y los paquetes de assets. Cada uno contiene una tabla de objetos etiquetados con un id de clase.

La cabecera es donde la lectura se equivoca en silencio. Los primeros dieciséis bytes son cuatro `uint32` big-endian conservados por compatibilidad. En el formato 22, tres de ellos son cero, y los valores reales van después, porque un archivo puede superar los 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

El segundo `metadata size` es un `uint32` entre dos `int64`. Suponer que los tres son de 64 bits desplaza la cadena de versión cuatro bytes. Aun así decodifica a algo con forma de cadena y desvía todo lo que viene después. La cabecera es big-endian. Todo lo que sigue sigue el byte de endianness (0, little-endian, en todas las versiones de escritorio).

Tras la cabecera: la cadena de versión del motor, la plataforma, la marca de árbol de tipos, la tabla de tipos (id de clase por tipo), la tabla de objetos (id de ruta, desplazamiento, tamaño, tipo), y los externos (otros archivos a los que puede apuntar un puntero).

| Caso | Resultado |
|---|---|
| formato 22-30 | se lee |
| formato 9-21 (antes de Unity 2020) | se rechaza: los desplazamientos están en la cabecera antigua, y ningún archivo a mano la usaba |
| fuera de 9-30 | se rechaza |
| árbol de tipos incrustado (compilaciones de editor) | se rechaza: las compilaciones distribuidas no incrustan uno, y la ruta del editor no está implementada |
| un paquete pasado donde se espera un contenedor | se rechaza, con un aviso al lector de paquetes |

No hay **ningún deserializador general**. Las compilaciones distribuidas no llevan árbol de tipos, porque el esquema viene compilado en el reproductor, así que cada clase hay que analizarla contra un diseño conocido para su versión. Solo se decodifica `Mesh`. Las demás clases se informan por nombre y recuento (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; las demás como `class<id>`).

**Verificado** en muchos juegos instalados y millones de objetos: la tabla de objetos tiene que cubrir la sección de datos exactamente, sin solapes, sin nada salvo relleno de alineación entre objetos, y el último objeto tiene que terminar en el último byte del archivo. Una lectura errónea de la cabecera no puede producir eso. La prueba con juego instalado lo repite en hasta seis archivos `resources.assets` / `sharedassets0.assets` que están en carpetas `*_Data`.

## Paquetes (`UnityFS`) {#bundles-unityfs}

Un paquete es un contenedor comprimido de archivos SerializedFile. La lista de bloques y el directorio también están comprimidos. El método está en los seis bits bajos de una palabra de flags: 0 sin comprimir, 1 LZMA (la cabecera de 5 bytes de Unity con el tamaño insertado), 2 y 3 LZ4 / LZ4HC. Los formatos 7 y posteriores alinean la cabecera a 16 bytes. El flag `0x80` pone el directorio al final del archivo. `UnityWeb`, `UnityRaw` y `UnityArchive` (anteriores a la 5.3) se reconocen pero no se leen.

## Mallas {#meshes}

`read_mesh` decodifica un objeto `Mesh` a posiciones, normales, el primer conjunto de UV y triángulos, en el orden que escriben Unity 2019 y posteriores: nombre, submallas, formas de mezcla (se saltan), poses de unión y datos de huesos (se saltan), las banderas de compresión y de legibilidad, el búfer de índices, los canales y datos de vértices, el bloque de malla comprimida, la caja local de límites, y la información de streaming.

- **Vértices externos.** La mayoría de la geometría distribuida vive en un archivo `.resS` junto al contenedor. La herramienta lo lee de la carpeta del contenedor (solo se usa el nombre de archivo de la ruta guardada `archive:/...`). Un `.resS` que falta es un error, no una malla vacía.
- **Flujos y canales.** Los canales indican qué flujo, desplazamiento, formato y dimensión tiene cada atributo. Los flujos van uno tras otro, cada uno rellenado a 16 bytes, así que el inicio de un flujo se acumula a partir de los pasos de los anteriores. Formatos: float32, float16, unorm/snorm de 8 y 16 bits (normalizados), y enteros simples.
- **Topología.** Solo triángulos (topología 0). Las tiras, cuadriláteros y líneas se rechazan, porque una conversión errónea parece geometría real.
- **Mallas comprimidas** (deltas cuantizados) se rechazan: `mesh '...' is stored compressed; that encoding is not implemented`.

### La autocomprobación {#the-self-check}

Leer una estructura en el orden equivocado no produce error. Produce números plausibles. Por eso cada malla decodificada se comprueba contra la **caja de límites que Unity guardó para ella**, calculada por el editor a partir de los vértices reales. `aabb_matches()` da por bueno cuando las esquinas de la caja decodificada están a menos del 2% del tamaño de la caja guardada. `meshes` imprime `ok` o `BOUNDS DISAGREE` en cada línea.

**Verificado:** las mallas muestreadas en varios juegos se decodifican con sus límites coincidentes. La prueba con juego instalado repite la comprobación sobre los contenedores instalados.

## No implementado {#not-implemented}

- Formatos anteriores a 2020.
- Mallas comprimidas.
- Cualquier clase distinta de `Mesh`: sin grafo de escena, transformaciones ni materiales, así que las mallas están en su propio espacio local.
- `meshes` sobre un paquete. El lector de paquetes existe en Python (`UnityBundle.serialized_files()`), pero el comando solo acepta un contenedor suelto.
