---
title: Обновления
nav_order: 13
lang: "bg"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Обновления {#updates}

3DHeat GameFiles проверява GitHub изданията на това хранилище при стартиране, казва кога е излязла по-нова версия и предлага обновяване. Вашите собствени файлове (обиколки, експорти) никога не се пипат.

Източник: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Инсталираната версия е файлът [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) на хранилището.

## Проверката при стартиране {#the-check-at-start-up}

Всяко изпълнение на `python -m heat3d_gamefiles ...` извиква проверката, преди да обработи аргументите си:

- Пита `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest` с време за изчакване **5 секунди**.
- Отговорът се кешира **6 часа** в `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (или `~/.cache/3DHeat/...` без `LOCALAPPDATA`). През това време не се прави заявка. "Няма издание още" (HTTP 404) също се кешира.
- Офлайн, при ограничение на заявките или зад прокси проверката просто връща и инструментът работи с версията, която има.
- Ако етикетът на последното издание (`v1.2.3` или `1.2.3`; всичко след `-` или `+` се пренебрегва) е по-нов от `VERSION`, се показва на stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **В терминал** (stdin и stderr са TTY) пита `Update now? [Y/n]`. Enter, `y`, `yes`, `j` или `ja` обновява. След успешно обновяване **същата команда се стартира отново** върху новия код и кодът ѝ на изход се предава.
- **Без терминал** (планирано изпълнение, тръба) само извежда ``Run `python -m heat3d_update` in <folder> to update.`` и продължава работа.

## Обновяване при желание {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Това винаги пита GitHub (без кеш). Извежда `Up to date: 1.0.1.`, `No release found (...)` или какво е направило. Кодът на изход е 1, ако обновяването не може да се приложи.

## Как се прилага обновлението {#how-an-update-is-applied}

| Инсталиран като | Обновяване |
|---|---|
| **git клониране** (папка `.git` и `git` в PATH) | `git pull --ff-only`. **Отказва**, докато следените файлове имат локални промени: "this checkout has local changes; commit or stash them, then run `git pull`". Незаписаните файлове не блокират |
| **изтеглено копие** | архивът с изходния код на изданието (`zipball_url`) се изтегля и разархивира въвъв временна папка, като се игнорира всеки път, който би излязъл навън; неговият `VERSION` трябва да е равен на версията на изданието, иначе нищо не се копира; после файловете му се копират върху тази папка |

Когато копира от архив, файловете, които не са част от изданието (обиколки, експорти, виртуални среди, всичко, което сте направили), се оставят на мира. Обновяващият се опитва също да изтрие `.py` модули, които изданието е премахнало от пакетите си, така че остарял модул да не засенчва заместителя си. Търси пакети `heat3d_*` в корена на архива и една папка по-надолу и премахва `.py` файловете, които изданието вече няма.

## Изключване {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Всяка стойност, различна от празна, `0`, `false` или `no`, изключва и проверката при стартиране, и предложението. `python -m heat3d_update` пак работи, когато се стартира ръчно.
