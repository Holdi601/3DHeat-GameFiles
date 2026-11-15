---
title: Actualizaciones
nav_order: 13
lang: "es"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Actualizaciones {#updates}

3DHeat GameFiles consulta las versiones publicadas de este repositorio en GitHub al arrancar, indica
cuándo hay una versión nueva y ofrece actualizar. Tus propios archivos (vueltas,
exportaciones) nunca se tocan.

Fuente: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
La versión instalada es el archivo
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) del repositorio.

## La comprobación al arrancar {#the-check-at-start-up}

Cada ejecución de `python -m heat3d_gamefiles ...` llama a la comprobación antes de leer
sus argumentos:

- Pregunta a `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`,
  con un límite de **5 segundos**.
- La respuesta se guarda en caché durante **6 horas** en
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (o
  `~/.cache/3DHeat/...` si no existe `LOCALAPPDATA`). Durante ese tiempo no se hace ninguna petición. "Todavía no hay
  versión" (HTTP 404) también se guarda en caché.
- Sin conexión, con límite de peticiones o detrás de un proxy, la comprobación simplemente termina y la
  herramienta funciona con la versión que tiene.
- Si la etiqueta de la última versión (`v1.2.3` o `1.2.3`; todo lo que siga a `-` o `+` se ignora) es
  más nueva que `VERSION`, escribe por la salida de error:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **En una terminal** (la entrada y la salida de error son ambas un TTY) pregunta `Update now? [Y/n]`.
  Enter, `y`, `yes`, `j` o `ja` actualizan. Tras una actualización correcta, el **mismo
  comando vuelve a arrancar** con el código nuevo, y se devuelve su código de salida.
- **Sin terminal** (una ejecución programada, una tubería) solo imprime
  ``Run `python -m heat3d_update` in <carpeta> to update.`` y sigue.

## Actualizar a petición {#updating-on-request}

```
python -m heat3d_update          # actualiza a la versión más reciente, si hay una
python -m heat3d_update --check  # solo dice si hay una versión nueva
```

Esto siempre pregunta a GitHub (sin caché). Imprime `Up to date: 1.0.1.`,
`No release found (...)`, o lo que haya hecho. El código de salida es 1 si no se pudo aplicar
la actualización.

## Cómo se aplica una actualización {#how-an-update-is-applied}

| Instalado como | Actualización |
|---|---|
| un **clon de git** (una carpeta `.git` y `git` en el PATH) | `git pull --ff-only`. **Se rechaza** mientras los archivos rastreados tengan cambios locales: "this checkout has local changes; commit or stash them, then run `git pull`". Los archivos sin rastrear no lo bloquean |
| una **copia descargada** | se descarga el archivo de código fuente de la versión (`zipball_url`) y se descomprime en una carpeta temporal, ignorando cualquier ruta que se salga de ella; su `VERSION` debe coincidir con la versión publicada, o no se copia nada; después sus archivos se copian sobre esta carpeta |

Al copiar desde un archivo, los archivos que no forman parte de la versión (vueltas, exportaciones,
entornos virtuales, todo lo que hayas creado) se dejan en paz. El actualizador
también intenta borrar los módulos `.py` que una versión haya quitado de sus paquetes, para que un
módulo antiguo no tape a su sustituto. Busca paquetes `heat3d_*` en la raíz del archivo y
una carpeta más abajo, y borra los archivos `.py` que la versión ya no tiene.

## Desactivarlo {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Cualquier valor distinto de vacío, `0`, `false` o `no` desactiva tanto la comprobación al arrancar
como la oferta. `python -m heat3d_update` sigue funcionando si lo ejecutas a mano.
