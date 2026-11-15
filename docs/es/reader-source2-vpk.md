---
title: VPK de Source 2
nav_order: 6
lang: es
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# VPK de Source 2 (`.vpk`) {#source-2-vpk}

**Lista y extrae** los archivos VPK de Valve, versiones 1 y 2, incluidos los archivos divididos y los datos
guardados dentro del archivo de directorio. Cada entrada puede comprobarse contra su propio CRC. Es el único
formato de contenedor de esta herramienta que su fabricante documenta. Juegos: Counter-Strike 2, Dota 2, Half-Life: Alyx y otros
sobre Source 2.

Fuente: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Comandos: `identify`, `list`, `extract`.

## Estructura {#layout}

```
u32 magic 0x55AA1234, u32 versión (1 o 2), u32 tamaño del árbol
  (versión 2: 16 bytes de cabecera más; la cabecera mide 12 o 28 bytes)
árbol de directorios:
  extensión        "vmdl_c", luego "vtex_c", ..., luego ""
    ruta           "maps/example_map", luego ""
      nombre       "world_layer0", luego ""
        u32 crc, u16 tamaño de precarga, u16 índice de archivo, u32 desplazamiento, u32 longitud, u16 0xFFFF
        [bytes de precarga]
```

- Tres bucles anidados, cada uno termina en una cadena vacía, así que un lector que espera un contador
  no encuentra ninguno. Las rutas se guardan una vez por grupo y se reconstruyen con las tres partes. Un único
  espacio significa "sin carpeta" o "sin extensión".
- Cada registro termina en `0xFFFF`. Eso se comprueba, así que un lector que ha perdido
  su posición se detiene enseguida ("the directory is not being read at the right offset").
- **Archivos divididos:** `pak01_dir.vpk` contiene el directorio, y los datos están en
  `pak01_000.vpk`, `pak01_001.vpk`... elegidos según el índice de archivo de la entrada.
- **Índice de archivo `0x7FFF`** significa que los bytes están en el propio archivo de directorio,
  después del árbol. Leerlo como un índice real manda a un lector a buscar
  `pak01_32767.vpk`.
- **Precarga:** los archivos pequeños se guardan enteros en el directorio. Una longitud de 0 no es
  entonces un error.

## Comandos {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` imprime la versión, el número de entradas y el primer archivo `.nav`. `list`
muestra cada entrada como `stored`, porque VPK no comprime. `extract` escribe los bytes
sin comprobar el CRC. En Python, `VpkArchive(path).verify(name)`
compara los bytes de una entrada con el CRC que registró el directorio.

## La malla de navegación {#the-navigation-mesh}

Un mapa trae su **malla de navegación** (`maps/<mapa>.nav`) junto a la geometría compilada.
Para un mapa de calor de posiciones de jugadores es, por mucho, la más útil de las dos, porque la malla de navegación *es* el
suelo transitable, ya calculado y con un tamaño mil veces menor. La prueba con el juego instalado comprueba que el
`.nav` de un mapa distribuido empieza por la cabecera de navegación de Source `CE FA ED FE`.

## Verificado {#verified}

Cada entrada muestreada de los archivos de mapas distribuidos de un juego salió byte a byte correcta
frente a su CRC, y todos los archivos de mapas se analizan bien.
Las pruebas con el juego instalado repiten la comprobación CRC con 25 entradas aleatorias de cada
uno de hasta cuatro archivos de mapas.

## No implementado {#not-implemented}

- Decodificar los recursos compilados de Source 2 (`.vmdl_c`, `.vtex_c`). Son binarios por bloques
  propios, el mismo tipo de trabajo que los formatos de malla de Unreal y Frostbite. La herramienta
  separada 3DHeat CS2 se encarga de la geometría de los mapas de CS2.
- Decodificar la malla de navegación de CS2. Su formato es la versión 36 y difiere del de Source 1, que está
  documentado ampliamente. Sus bytes están estructurados y no comprimidos (entropía 6.2, 31% de ceros), pero solo
  el 3% de sus palabras se leen como coordenadas, así que la estructura no es la obvia y todavía no se ha descifrado.
