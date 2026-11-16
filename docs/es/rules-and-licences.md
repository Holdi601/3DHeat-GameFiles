---
title: Reglas y licencias
nav_order: 12
lang: "es"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Reglas y licencias {#rules-and-licences}

Tres reglas dan forma a toda la herramienta. Texto completo: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Sin claves: ninguna incluida, ninguna recuperada {#no-keys-none-shipped-none-recovered}

**Lee contenedores.** Analizar un formato de contenedor es manejo ordinario de archivos, y FModel, UModel y AssetRipper lo han hecho abiertamente durante años.

**La línea que importa es el cifrado, y se traza dentro de la herramienta.**

- **Ninguna clave incluida.** No hay ninguna clave en el código ni en los datos.
- **Ninguna recuperación de claves.** Nada busca una clave en un ejecutable, y nada lee la memoria de otro proceso.
- **Una clave que tú tienes, o ninguna.** Un `.pak` de Unreal cifrado solo se abre con `--key <hex>` (en Python, `PakArchive(path, aes_key=...)`). `pak.py` no tiene ninguna ruta de código que obtenga una clave. Un contenedor IoStore cifrado se rechaza directamente.
- **La ofuscación tampoco se implementa.** Las tablas ofuscadas con XOR de Frostbite guardan su clave en el propio archivo, así que son ofuscación y no un control de acceso. Aun así se detectan y se rechazan, porque ningún archivo a mano usa esa forma y no habría nada con qué comprobar una implementación. El paquete con clave de Assetto Corsa EVO se rechaza por la misma razón por la que existe la regla de las claves.
- **Los archivos cifrados siguen cerrados.** El sistema de archivos inicial de Battlefield 6, que contiene la biblioteca de tipos del juego, está cifrado y no se lee. La exportación de nivel trabaja con los archivos que no están cifrados, y define a partir de los datos los dos tipos que necesita.
- **Nada se inyecta en un proceso de juego.** La telemetría viene de fuentes que los propios juegos publican, y la captura usa APIs públicas de grabación de pantalla (en las otras herramientas de 3DHeat). La inyección en un título con anticheat pone en riesgo la cuenta de quien la ejecuta.

Cada archivo probado hasta ahora está sin cifrar.

## 2. Tus archivos {#your-own-files}

La herramienta lee los archivos del juego **instalados en tu equipo**. Nunca descarga contenido de juegos.

No incluye nada de ningún juego: ni contenido del juego, ni código del juego, ni DLL. Lo que exporta se escribe en tu disco y en ningún otro sitio.

3DHeat GameFiles no está afiliado a ningún editor de juegos ni cuenta con su respaldo. Los juegos y los nombres y marcas relacionados pertenecen a sus propietarios. Titulares de derechos: abran una incidencia en [github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) - respondemos rápido y retiramos lo que se nos pida.

## 3. La salida no es para redistribuir {#output-is-not-for-redistribution}

Lo que sale es geometría para **contexto espacial**: el suelo, la carretera y lo que hay al lado, reducido a un presupuesto, para poder analizar las vueltas en su sitio. Es lo menos valioso de lo que contiene un archivo, y sigue siendo contenido del editor del juego.

- Conserva los `.glb` exportados, y las texturas que contienen, para tu propio análisis.
- No publiques, compartas ni vendas circuitos, niveles, modelos ni texturas exportados.
- El `.gitignore` del repositorio mantiene los archivos de juego, las exportaciones, las vueltas y las grabaciones fuera del control de versiones, por carpeta y por tipo de archivo (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` y más).

## Oodle se encuentra, no se incluye {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, ahora Epic) es propietario y no tiene una compilación redistribuible. `oo2core_*.dll` está licenciado al producto que lo distribuye. Por eso `oodle.py` carga una biblioteca que ya está en el equipo en lugar de llevar una. Es el acuerdo que contempla la licencia, y el mismo que usan FModel y UModel. Ver [Oodle](reader-oodle.md).

## Los formatos en sí {#the-formats-themselves}

- Los formatos `.pak`, IoStore, `SerializedFile` de Unity, `.toc` de Frostbite y de ForzaTech no están documentados. Ninguno de los lectores aquí procede del código fuente de otro proyecto. Para Frostbite, las descripciones públicas de versiones anteriores (las herramientas de modding Frosty, una nota de formato de Need for Speed Heat, una charla de GDC) aportaron nombres de campos y un mapa de qué buscar. No se tomó código; cada desplazamiento se midió en los archivos (ver [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Los niveles extraídos son para tu propio uso. La herramienta los escribe en tu disco y en ningún otro sitio; no los publiques.
- BeamNG publica el diseño de su `.cdae`, y el lector lo sigue.
- Valve documenta VPK.
- Los datos de propiedades cocinados de Unreal 5 necesitan la lista de propiedades de cada clase. Las listas de `unversioned.py` son **solo nombres y tipos**, hechos sobre el formato como los que contiene un archivo de mapeos de interoperabilidad. Se derivaron de las cabeceras de Unreal Engine que Epic pone a disposición de cualquiera con una cuenta vinculada, y se comprobaron contra los datos distribuidos. No se incluye ni se requiere código del motor.

## Licencia de esta herramienta {#this-tools-licence}

Todo lo escrito para este repositorio está bajo la **licencia MIT** ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): úsalo, cámbialo, distribúyelo, con fines comerciales o no.

Los paquetes de terceros son todos permisivos, así que el exportador no tiene restricciones propias:

| Paquete | Licencia | Para qué |
|---|---|---|
| numpy | BSD-3-Clause | decodificación de mallas |
| cryptography | Apache-2.0 / BSD-3-Clause | solo para archivos de los que tienes la clave |
| lz4 | BSD-3-Clause | archivos de Forza, algunos paquetes de Unity, bloques LZ4 de IoStore |
| Pillow | MIT-CMU (HPND) | texturas de bloques comprimidos, salida JPEG |
| msgpack | Apache-2.0 | `.cdae` de BeamNG |
| zstandard | BSD-3-Clause | los pocos `.cdae` comprimidos con zstd, bloques zstd de Frostbite |
| pytest | MIT | solo desarrollo |

Las licencias se leyeron de los metadatos de los paquetes en septiembre de 2026. Si las condiciones de un componente cambian después, lo que cuenta es el código fuente.
