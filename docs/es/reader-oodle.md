---
title: Oodle
nav_order: 3
lang: "es"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: se busca, no se incluye {#oodle-found-not-bundled}

La mayor parte del contenido Unreal distribuido, y algunas cargas de Frostbite, están comprimidas con
**Oodle** (RAD Game Tools, ahora Epic). Oodle es propietario. No hay una versión redistribuible
ni una implementación en Python, y `oo2core_*.dll` tiene licencia del producto que lo distribuye.
Por eso esta herramienta **busca una copia que ya esté en tu equipo y la carga**. Nunca trae
una. FModel y UModel funcionan igual.

Fuente: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Dónde busca {#where-it-looks}

Gana el primer archivo que exista, en este orden:

1. Una ruta explícita que pase quien llama (API de Python).
2. `HEAT3D_OODLE`: una ruta a la DLL, o a una carpeta que la contenga.
3. Una búsqueda superficial, de un solo nivel, en
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - el `steamapps\common` de cada biblioteca de Steam

   Para cada carpeta hija `<juego>`, revisa `<juego>`,
   `<juego>\Engine\Binaries\ThirdParty\Oodle\Win64` y
   `<juego>\Engine\Binaries\Win64`.

Nombres de archivo que prueba, del más nuevo al más antiguo: desde `oo2core_9_win64.dll` hasta
`oo2core_3_win64.dll`. El formato es compatible hacia atrás, así que una biblioteca más antigua
suele funcionar igual.

La búsqueda **no** es a propósito un recorrido recursivo de todos los discos, que tardaría minutos. Si no
encuentra nada, define `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Una carpeta sirve igual que el archivo: dentro de ella se prueban los nombres de DLL de arriba.

Una instalación de Unreal Engine trae una en `Engine\Binaries\ThirdParty\Oodle`, que es la
fuente más ordenada para un desarrollador. Muchos juegos traen una junto a su ejecutable. Los juegos de Unreal 5 suelen
enlazar Oodle de forma estática y no traen DLL, así que la copia encontrada puede pertenecer a otro juego
distinto del archivo que se lee. El formato es el mismo de todos modos.

## Cómo se llama {#how-it-is-called}

`OodleLZ_Decompress` se llama mediante `ctypes` con la longitud de salida esperada (el índice del
archivo siempre la conoce, y Oodle no puede deducirla), decodificación a prueba de fallos activada
(la entrada no es de confianza), sin comprobación CRC (el SHA-1 del pak ya cubre los bytes) y sin hilos.
Un resultado de longitud incorrecta es un error. La biblioteca se carga una vez por ejecución.

## Cuando no hay ninguna {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Una entrada que no se puede descomprimir es un error, nunca basura que parece plausible.

El cargador solo funciona en Windows (busca `*_win64.dll`). No se buscan bibliotecas
de Linux ni de macOS.
