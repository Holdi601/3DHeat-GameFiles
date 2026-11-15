---
title: "Ажурирања"
nav_order: 13
lang: "mk"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Ажурирања {#updates}

3DHeat GameFiles ги проверува изданијата на GitHub на ова складиште при стартување, кажува
кога има понова верзија и нуди ажурирање. Вашите датотеки (кругови,
извози) никогаш не се допираат.

Извор: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Инсталираната верзија е датотеката
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) на складиштето.

## Проверката при стартување {#the-check-at-start-up}

Секое извршување на `python -m heat3d_gamefiles ...` ја повикува проверката пред да ги обработи
аргументите:

- Прашува `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`,
  со време на чекање од **5 секунди**.
- Одговорот се чува во кеш **6 часа** во
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (или
  `~/.cache/3DHeat/...` без `LOCALAPPDATA`). Во тоа време не се праќа барање.
  „Сè уште нема издание“ (HTTP 404) исто така се чува во кеш.
- Офлајн, со ограничена стапка или зад прокси, проверката едноставно враќа и алатката
  работи на верзијата што ја има.
- Ако ознаката на последното издание (`v1.2.3` или `1.2.3`; сè по `-` или `+` се
  игнорира) е понова од `VERSION`, печати на stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **На терминал** (и stdin и stderr се TTY) прашува `Update now? [Y/n]`.
  Enter, `y`, `yes`, `j` или `ja` ажурира. По успешно ажурирање, **истата
  команда се стартува повторно** на новиот код, а нејзиниот излезен код се пренесува.
- **Без терминал** (закажано извршување, pipe) само печати
  ``Run `python -m heat3d_update` in <folder> to update.`` и продолжува.

## Ажурирање по барање {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Ова секогаш го прашува GitHub (без кеш). Печати `Up to date: 1.0.1.`,
`No release found (...)`, или што направило. Излезниот код е 1 ако ажурирањето
не можело да се примени.

## Како се применува ажурирање {#how-an-update-is-applied}

| Инсталирано како | Ажурирање |
|---|---|
| **git клон** (папка `.git` и `git` на PATH) | `git pull --ff-only`. **Одбива** додека следените датотеки имаат локални промени: „this checkout has local changes; commit or stash them, then run `git pull`“. Неследените датотеки не го блокираат |
| **преземена копија** | изворната архива на изданието (`zipball_url`) се презема и се распакува во привремена папка, игнорирајќи секоја патека што би излегла од неа; нејзиниот `VERSION` мора да е еднаков на верзијата на изданието, или ништо не се копира; потоа нејзините датотеки се копираат врз оваа папка |

При копирање од архива, датотеките што не се дел од изданието (кругови, извози,
виртуелни околини, сè што сте направиле) се оставаат на мира. Ажурирачот
исто така се обидува да ги избрише модулите `.py` што изданието ги отстранило од своите пакети, за да
застарен модул не го засени својата замена. Бара пакети `heat3d_*` во
коренот на архивата и една папка подолу, и ги отстранува датотеките `.py` што изданието
повеќе ги нема.

## Исклучување {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Секоја вредност освен празна, `0`, `false` или `no` ги исклучува и проверката при стартување
и понудата. `python -m heat3d_update` сепак работи кога се извршува рачно.
