---
title: "Mantenimiento"
nav_order: 99
lang: es
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Mantenimiento: la lista de comprobación de versión {#maintaining-the-release-checklist}

Antes de etiquetar una versión (`v` + el número de `VERSION`), repase esta lista
en orden. Mantiene las páginas, las imágenes y las traducciones fieles al código.

1. **Regenerar las páginas generadas.**
   - `python tools/gen_docs_reference.py` reescribe
     [Referencia de comandos](../cli-reference.md) a partir del `--help` del propio programa.
     `python tools/gen_docs_reference.py --check` devuelve 1 mientras la página
     guardada no esté al día.
   - `python tools/docs_diagrams.py --strings` redibuja los diagramas en
     `docs/assets/img/` y reescribe `docs/assets/i18n/en.json`, la lista de
     todas las etiquetas de diagrama que hay que traducir.
2. **Listar lo que ha cambiado desde la última versión:**
   `git log --oneline v<last VERSION>..HEAD`. Cada verbo, opción, campo de
   salida o comportamiento nuevo necesita una línea en `CHANGELOG.md` y una fila en su tabla
   **Docs** que nombre la página que lo explica. Actualice esa página.
3. **Pedir una revisión independiente** de las páginas e imágenes modificadas, a alguien
   (o a un agente) que no las haya escrito, leyendo como tres personas: un principiante que
   nunca ha usado una terminal, un niño de 8 años y un profesional. También se revisan
   los diagramas: legibles al ancho de la página, etiquetas correctas, colores explicados.
4. **Corregir lo que encuentre la revisión**, y comprobar después que no se ha colado ningún dato real de juego:
   ningún nombre de mapa, nivel o jugador, ninguna cifra de grabaciones o instalaciones reales
   (use marcadores como `<map>` o «el nivel de prueba»).
5. **Volver a traducir las páginas modificadas.** Cada página traducida guarda el hash de
   la página inglesa de la que procede; las páginas cuya fuente inglesa ha cambiado se
   traducen de nuevo, y con ellas las etiquetas de los diagramas. Después revise cada
   lengua: clara para los mismos tres lectores, etiquetas correctas, palabras que coincidan con
   la interfaz del visor en esa lengua.
6. **Publicar solo con el visto bueno del usuario.** No se sube ni se etiqueta nada antes de que
   el propietario lo haya dicho.

## Traducciones: los comandos {#translations-the-commands}

El sitio está traducido a las 40 lenguas del visor 3DHeat: el inglés en `docs/`, cada otra
lengua en `docs/<lang>/` con los mismos nombres de archivo. `tools/docs_i18n.py` lleva la contabilidad:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Traduzca solo lo que `todo` lista: deje el Markdown, los enlaces, el código y los nombres de archivos y de columnas tal cual,
traduzca los títulos y las descripciones de las imágenes, y use las palabras propias del visor 3DHeat para sus botones
y paneles (su carpeta `src/i18n/locales/<lang>/`). Las páginas de referencia generadas y las imágenes de terminal siguen
en inglés. En el sitio, una traducción desactualizada lo indica y enlaza la página en inglés; una página que falta
recurre al inglés. El menú de idioma de la cabecera y la redirección de la página de inicio según el idioma del navegador
vienen de `docs/_includes/`.
