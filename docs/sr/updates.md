---
title: Ажурирања
nav_order: 13
lang: "sr"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Ажурирања {#updates}

3DHeat GameFiles при покретању проверава GitHub издања овог репозиторијума, каже када је нова верзија изашла и нуди ажурирање. Ваши фајлови (кругови, извози) никад се не дирају.

Извор: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Инсталирана верзија је фајл [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) у репозиторијуму.

## Провера при покретању {#the-check-at-start-up}

Свако покретање `python -m heat3d_gamefiles ...` позове проверу пре него што обради своје аргументе:

- Пита `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`, с временским ограничењем од **5 секунди**.
- Одговор се кешира **6 сати** у `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (или `~/.cache/3DHeat/...` без `LOCALAPPDATA`). У том времену ниједан захтев се не шаље. Одговор „Још нема издања“ (HTTP 404) се такође кешира.
- Ако нема везе, ако је ограничен број захтева или ако иде преко проксија, провера једноставно врати и алат ради на верзији коју има.
- Ако је ознака најновијег издања (`v1.2.3` или `1.2.3`; све после `-` или `+` се занемарује) новија од `VERSION`, на stderr се исписује:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **У терминалу** (stdin и stderr су оба TTY) пита `Update now? [Y/n]`. Enter, `y`, `yes`, `j` или `ja` ажурира. После успешног ажурирања **иста команда се поново покреће** на новом коду, а њен излазни код се прослеђује даље.
- **Без терминала** (заказано покретање, цев) само исписује поруку ``Run `python -m heat3d_update` in <folder> to update.`` и наставља даље.

## Ажурирање на захтев {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Ово увек пита GitHub (без кеша). Исписује `Up to date: 1.0.1.`, `No release found (...)`, или шта је урадило. Излазни код је 1 ако ажурирање није могло да се примени.

## Како се ажурирање примењује {#how-an-update-is-applied}

| Инсталирано као | Ажурирање |
|---|---|
| **git клон** (фолдер `.git` и `git` у PATH-у) | `git pull --ff-only`. **Одбија се** док праћени фајлови имају локалне измене, с поруком „this checkout has local changes; commit or stash them, then run `git pull`“. Непраћени фајлови не блокирају га |
| **преузета копија** | изворни архив издања (`zipball_url`) се преузима и распакује у привремени фолдер, а свака путања која би излазила из њега се занемарује; његов `VERSION` мора бити једнак верзији издања, или се ништа не копира; затим се његови фајлови копирају преко овог фолдера |

Кад се копира из архива, фајлови који нису део издања (кругови, извози, виртуелна окружења, све што сте направили) остају нетакнути. Ажурирач такође покушава да обрише `.py` модуле које је издање уклонило из својих пакета, да застарели модул не би засенио своју замену. Тражи `heat3d_*` пакете у корену архива и један ниво испод, и уклања `.py` фајлове које издање више нема.

## Искључивање {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Било која вредност осим празне, `0`, `false` или `no` искључује и проверу при покретању и понуду. `python -m heat3d_update` и даље ради кад се покрене ручно.
