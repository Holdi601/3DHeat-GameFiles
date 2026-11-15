---
title: Unreal .pak
nav_order: 1
lang: "es"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Lista y extrae** archivos `.pak` de Unreal 4.22-5.x: versiones 8, 9, 10, 11 y 12, compresión Zlib, Gzip y Oodle, y archivos cifrados cuando proporcionas la clave AES. No interpreta lo que extrae (`.uasset`, `.umap`).

Fuente: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Comandos: `identify`, `list`, `extract` (ver [Comandos](commands.md)).

## Diseño {#layout}

El pie está al final del archivo y se encuentra buscando en los últimos 1.024 bytes la marca `0x5A6F12E1`. Su orden de campos importa:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

El flag de cifrado está **antes** de la marca. Si se toma después de la marca, cae sobre la "Z" de "Zlib". Entonces cada archivo se declara cifrado y cada nombre de método pierde su primera letra ("lib", "odle"), un fallo silencioso y plausible. La versión es el byte bajo, porque las compilaciones de "índice congelado" activan un bit alto.

El índice contiene el punto de montaje, el índice de hashes de ruta, el índice de directorios completo, y un bloque de **entradas codificadas**: una forma empaquetada a nivel de bit donde una palabra de flags indica qué números son de 32 bits, el método de compresión (6 bits), si la entrada está cifrada, el número de bloques (16 bits) y el tamaño de bloque en unidades de 2.048 (6 bits). El tamaño de bloque todo a unos es un escape: el tamaño real sigue como u32 **antes** del desplazamiento. En un archivo grande, leerlo después de los tamaños desplazó el 7% de las entradas cuatro bytes, y les dio desplazamientos en los exabytes.

El registro completo de cada entrada se repite justo antes de su carga útil, así que la carga útil empieza tras `8+8+8+20+4+1+4` bytes, más `4 + 16 x bloques` cuando está comprimida. Los bloques cifrados se rellenan a 16 bytes.

## Qué lee y qué rechaza {#what-it-reads-and-what-it-refuses}

| Caso | Resultado |
|---|---|
| versiones 8-12 | se lee |
| cualquier otra versión | `pak version N; this reader handles 8-12` (las versiones anteriores guardan una lista plana de registros, y no había archivo con el que probarlas) |
| sin marca de pie | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| índice fuera del archivo | se rechaza: el pie no se analizó como se afirmaba |
| solo índice de hashes de ruta | se rechaza: los nombres de archivo se ocultaron con hash en la compilación y no se pueden recuperar |
| entradas en la lista de desbordamiento del índice (desplazamiento de directorio -1) | se omiten, no se inventan |
| índice cifrado, sin clave | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." En la línea de comandos, una línea y código de salida 1 |
| entrada cifrada, sin clave | `EncryptedPak` al leer |
| métodos Zlib, Gzip, Oodle | se descomprimen (Oodle necesita una biblioteca, ver [Oodle](reader-oodle.md)) |
| cualquier otro método | `compression method '...' is not supported` |

## Claves {#keys}

`--key` en `list` y `extract` toma una clave AES-256 que ya tienes, como 64 dígitos hexadecimales, con o sin `0x`. Cualquier otra cosa se rechaza antes de abrir el archivo, con código de salida 2. El descifrado es AES-256-ECB a través del paquete `cryptography`. No existe ninguna ruta de código que obtenga una clave: ni claves incluidas, ni búsqueda en ejecutables, ni lectura de memoria. Ver [Reglas y licencias](rules-and-licences.md).

## Verificado {#verified}

Contra archivos distribuidos de más de un juego, cada entrada, incluido un archivo muy grande, coincidió con el SHA-1 que escribe Unreal delante de cada carga útil. Ese hash cubre los bytes tal como se guardan, así que una coincidencia significa que la decodificación del índice, el desplazamiento de la carga útil y cada límite de bloque comprimido eran correctos. Las pruebas con juegos instalados (`test_pak.py`) lo repiten en hasta cuatro paks sin cifrar que se encuentran en `steamapps\common\*\...\Content\Paks`. Comprueban que el desplazamiento de cada entrada cae dentro del archivo, y que el SHA-1 coincide en una muestra aleatoria de 150 entradas por archivo.
