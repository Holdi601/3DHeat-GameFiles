---
title: "Перад пачаткам"
nav_order: 2
lang: "be"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Перад пачаткам {#before-you-start}

Упершыню ў камандным радку? Гэтая старонка правядзе вас ад нуля да працоўнага інструмента
прыкладна за дзесяць хвілін. Вы друкуеце каманды ў акне, якое завецца **тэрмінал**, а
інструмент адказвае тэкстам.

## 1. Усталюйце Python {#install-python}

1. Перайдзіце на [python.org/downloads](https://www.python.org/downloads/) і спампуйце
   **Python 3.10 або навейшы**.
2. Запусціце ўсталёўшчык. На першым экране адзначце **«Add python.exe to PATH»**,
   потым націсніце **Install Now**.

## 2. Атрымайце інструмент {#get-the-tool}

- **З git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Без git:** на [старонцы GitHub](https://github.com/Holdi601/3DHeat-GameFiles)
  націсніце зялёную кнопку **Code**, потым **Download ZIP** і распакуйце архіў.

## 3. Адкрыйце тэрмінал у папцы інструмента {#open-a-terminal-in-the-tools-folder}

- У Правадыру адкрыйце папку, у якой ёсць `README.md`. Пстрыкніце ў адрасным
  радку, увядзіце `cmd` і націсніце Enter. Адкрыецца чорнае акно, ужо ў гэтай папцы.
- Або адкрыйце **Windows Terminal** і перайдзіце туды праз `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Усталюйце тое, што патрэбна інструменту {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Вы ўбачыце радкі, што заканчваюцца на `Successfully installed ...`.

## 5. Праверце, што ён працуе {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Вы ўбачыце `usage: heat3d_gamefiles [-h]` і спіс дзеясловаў (`identify`,
`list`, `extract`, `course`, ...). Гэта поспех: інструмент гатовы.

## Як чытаць прыклады {#reading-the-examples}

- `<something>` — гэта **запаўняльнік**: увядзіце сваё значэнне замест яго, без
  вуглавых дужак. `<lap file>` становіцца, напрыклад, `laps\my_lap.json`.
- `[--option]` у квадратных дужках — **неабавязковае**: прапусціце, калі не патрэбна.
- Шлях з прабеламі патрабуе **двайных двукоссяў**: `"C:\My Games\lap.json"`.
- Выконвайце кожную каманду ў папцы інструмента (крок 3).

## Калі нешта пайшло не так {#when-something-goes-wrong}

| Вы бачыце | Што рабіць |
|---|---|
| `'python' is not recognized` | Python не ўсталяваны, або не адзначылі «Add to PATH». Запусціце ўсталёўшчык зноў і адзначце гэта, потым адкрыйце новы тэрмінал. |
| `No module named heat3d_gamefiles` | Тэрмінал не ў той папцы. Перайдзіце праз `cd` у папку з `README.md`. |
| `No module named numpy` (або іншая назва) | Крок 4 прапушчаны. Выканайце `pip install -r requirements.txt`. |
| `can't open file` / `not found` са шляхам | У шляху ёсць прабелы без двукоссяў, або памылка ў напісанні. Вазьміце яго ў двайныя двукоссі. |

Больш паведамленняў і іх выпраўленняў: [Вырашэнне праблем](../troubleshooting.md).
