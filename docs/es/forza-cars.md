---
title: Coches de Forza
nav_order: 6
lang: es
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Coches de Forza: `cars` {#forza-cars-cars}

Escribe cada coche de un Forza instalado, con el nivel de detalle bajo del propio juego, en un único
archivo para la pestaña Análisis de carrera del visor (dibuja un coche por cada vuelta que hiciste), así que cada coche
registrado se dibuja con su propia forma y a su tamaño real.

![cars --help](../assets/img/cars-help.svg)

## Paso a paso {#step-by-step}

1. **Ejecútalo** con el juego instalado (lo encuentra en las bibliotecas de Steam y en
   `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   O indica la carpeta del juego:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<carpeta de Forza>" -o forza.h3dcars
   ```

2. **Cárgalo en el visor**: **Cargar archivo de coches...** en los ajustes de la vista, o suelta el
   archivo en la pestaña de carreras; se queda en ese navegador. Las vueltas cuyo número de coche
   esté en el archivo se dibujan entonces como ese mismo coche (ver la
   [documentación de la repetición de carreras del visor](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Vuelve a ejecutarlo** cuando el juego tenga coches nuevos. Tarda unos segundos y escribe
   unos 5 MB.

## Opciones {#options}

| Opción | Valor por defecto | Significado |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | el archivo que se escribe |
| `--game FOLDER` | el juego instalado que se encuentre | la carpeta del juego |

## Qué contiene el archivo {#what-is-in-the-file}

Para cada archivo de coche bajo `media/Cars`: el modelo `ProxyLOD` que trae (unos 900 triángulos), el
número del coche tal como lo indica la telemetría, su marca, la etiqueta del modelo y el año según el
nombre del archivo, y sus ruedas y luces traseras. Las formas están en metros, a escala 1:1 con el coche.
Un archivo sin ese modelo (un objeto de tráfico) se nombra y se deja fuera.

El archivo está hecho para el visor de 3DHeat; su formato, para quien lo lea en otro sitio
([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Parte | Formato |
|---|---|
| archivo completo | comprimido con gzip |
| marca | los 8 bytes `H3DCARS1` |
| longitud de la cabecera | u32 little-endian |
| cabecera | JSON en UTF-8: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| relleno | espacios hasta un múltiplo de 4 bytes |
| datos | por coche: los vértices como tres i16 cada uno (milímetros; x a la derecha, y arriba, z hacia delante), y luego los triángulos como tres u16 cada uno |

Cada entrada de `cars`: `key`, `ordinals` (los números del coche tal como los indica la telemetría),
`make`, `model`, `year`, `height` y `length` (m), `wheels` (por rueda `[x, y, z, radius]`, m),
`lights` (puntos de las luces traseras `[x, y, z]`, m), y `vertexAt`, `vertices`, `faceAt`, `faces`
(desplazamientos en bytes desde el inicio de los datos, y cantidades).

El archivo contiene el contenido del juego: es para la máquina en la que se hizo, no para
pasarlo a otros ([Reglas y licencias](rules-and-licences.md)).
