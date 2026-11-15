---
title: Solución de problemas
nav_order: 11
lang: "es"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Solución de problemas {#troubleshooting}

Los mensajes que imprime la herramienta cuando algo la detiene, qué significa cada uno y qué hacer. Los mensajes se citan del código, con los marcadores entre corchetes angulares.

## Antes de que arranque la herramienta {#before-the-tool-even-starts}

| Ves | Haz esto |
|---|---|
| `'python' is not recognized` | instala Python 3.10 o posterior y marca "Add python.exe to PATH"; abre una terminal nueva ([Antes de empezar](before-you-start.md)) |
| `No module named heat3d_gamefiles` | la terminal está en la carpeta equivocada: haz `cd` a la carpeta que tiene `README.md` |
| `No module named numpy` (u otro paquete) | ejecuta `pip install -r requirements.txt` |
| una ruta con espacios aparece cortada, o `unrecognized arguments` | pon la ruta entre comillas dobles: `"C:\My Games\lap.json"` |

## Encontrar el juego {#finding-the-game}

| Mensaje | Significado | Haz esto |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | ninguna biblioteca de Steam ni `C:\XboxGames` tiene un juego con `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | las coordenadas de la vuelta no están en ningún circuito instalado | comprueba que la vuelta es de este juego; pasa `--track` si el circuito está en otro sitio |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | hay losetas cerca de la caja pero ninguna en el corredor | igual que arriba |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | la carpeta no tiene ningún `.utoc` que se abra | apunta `--install` a la carpeta con los archivos `.utoc` |

## Encontrar el lugar {#finding-the-place}

| Mensaje | Significado | Haz esto |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: ningún nivel superó el 30% | `--level <name>`; comprueba que la vuelta está en el marco del visor |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` no coincidió | usa uno de los nombres de carpeta que se listan |
| `<level> has no scene (no main/*.level.json and no .mis)` | la carpeta del nivel no tiene archivos de escena | un nivel o mod roto o incompleto |
| `no terrain of <level> lies along the driving.` | BeamNG: el corredor no tiene cuadros de terreno | nivel equivocado, o un nivel sin terreno donde está la vuelta |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: ninguna etapa ni marco superó el 50% | `--level <stage>`; comprueba que las posiciones de la vuelta están en metros con Y hacia arriba |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` no coincidió | usa uno de los nombres que se listan |
| `no ground of <stage> lies along the driving.` | AC Rally: ninguna loseta de suelo en el corredor | etapa equivocada |

## La vuelta {#the-lap}

| Mensaje | Haz esto |
|---|---|
| `<file> is not a lap this can read. ...` | dale una forma compatible, ver [Entradas de vuelta](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | el JSON no es una vuelta |
| `<file> has no x, y and z columns` | pon en la cabecera del CSV las columnas `x`, `y` y `z` |
| `'<name>' is not a file, and no course in <library> matches it` | comprueba el nombre, o pasa un archivo |
| `'<name>' matches 3 courses: ...` | usa una parte más larga del nombre |
| `<name> holds no driving` | la vuelta tiene menos de dos muestras |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` necesita un JSON de ruta con `bounds`, como lo escriben `heat3d_capture route` y `laps`; un archivo de vuelta es para `course` |
| `give exactly one of --box and --route` | `terrain` necesita una sola región |
| `no course export for this lap: <reason>.` | el juego no está soportado, ver [Límites y carencias conocidas](limits-and-known-gaps.md) |

## Archivos {#archives}

| Mensaje | Significado |
|---|---|
| `no Oodle library found. ...` | define `HEAT3D_OODLE`, ver [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | un pak cifrado: `--key <hex>` si tienes la clave. No hay otra forma |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | la clave son 32 bytes escritos como 64 dígitos hexadecimales, `0x` opcional (código de salida 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | no es ninguno de esos; `identify` dice qué es. Un contenedor de Unity usa `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | un contenedor IoStore cifrado. No se puede leer |
| `pak version <n>; this reader handles 8-12` | un formato de pak anterior o posterior |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | desde Python: prueba con el `.utoc`, que también aceptan `list` y `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | un contenedor IoStore que no nombra archivos; sus fragmentos solo se alcanzan a través de otros paquetes |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | la `ChunkContentsMiniZip<n>.txt` que está junto al archivo es de otra compilación u otro archivo; sin ella las entradas se listan por número |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | los nombres se ocultaron con hash en la compilación |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | una tabla de Frostbite en la forma ofuscada |
| `no Frostbite game found in a Steam library; give --install` | `levels` o `level` no encontraron ningún juego de Steam cuyo `Data` tenga un `layout.toc`; pasa la carpeta del juego |
| `no level called '<name>'; did you mean one of ...?` | el nombre no coincidió con ninguna tabla de nivel, o coincidió con varias; `levels` las lista |
| `nothing was placed: no static model group was recognised` | los miembros de grupo del nivel tienen una firma de tipo distinta, tras una actualización del juego o en otro juego de Frostbite; hay que volver a medir el diseño |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | una malla de Unity comprimida |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | guarda el `.resS` junto al `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | una compilación de Unity anterior |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` acepta un contenedor suelto |
| `texture format <n> has not been identified; refusing to guess` | un formato de muestra de Forza que aún no se ha visto |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | mantén juntas las partes de un VPK dividido |

## Exportaciones que salen mal {#exports-that-come-out-wrong}

| Síntoma | Causa probable |
|---|---|
| el circuito está desplazado respecto a la vuelta en el visor | la vuelta y la exportación usan marcos distintos: revisa `--game` (una vuelta de BeamNG leída como Forza, por ejemplo) |
| no hay arcén en un circuito de Forza | `--no-textures`, o la loseta no tenía mapas para esa `--season` (la consola dice `N without maps`) |
| una loseta de Forza en colores planos | faltan sus mapas de suelo para la temporada |
| muchos menos objetos colocados de lo esperado | un `--detail-budget` explícito demasiado pequeño; el resumen dice cuántas copias se dejaron fuera |
| el archivo es muy grande (cientos de MB) | un corredor urbano con el presupuesto automático; usa `--detail-budget`, `--texture-size 1024` o `--margin 40` |
| faltan vallas | las superficies translúcidas se dejan fuera a propósito (el resumen las nombra) |
| `N meshes could not be read` | algunos modelos usan un formato que el lector rechaza; el resto sí se exporta |
| `N of M components could not be read` (AC Rally) | un parche del juego puede haber movido las ranuras de propiedades; por favor, repórtalo |
