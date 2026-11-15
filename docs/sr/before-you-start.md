---
title: Пре почетка
nav_order: 2
lang: sr
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Пре почетка {#before-you-start}

Први пут у командној линији? Ова страница вас води од нуле до алата који
ради, за око десет минута. Команде куцате у прозор који се зове **терминал**, а
алат одговара текстом.

## 1. Инсталирајте Python {#install-python}

1. Идите на [python.org/downloads](https://www.python.org/downloads/) и преузмите
   **Python 3.10 или новији**.
2. Покрените инсталер. На његовом првом екрану штиклирајте **„Add python.exe to PATH"**,
   па кликните на **Install Now**.

## 2. Набави алат {#get-the-tool}

- **Ако имате git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Ако немате git:** на [GitHub страници](https://github.com/Holdi601/3DHeat-GameFiles)
  кликните на зелено дугме **Code**, па на **Download ZIP**, и распакујте га.

## 3. Отворите терминал у фасцикли алата {#open-a-terminal-in-the-tools-folder}

- У File Explorer-у отворите фасциклу која садржи `README.md`. Кликните у адресну траку,
  укуцајте `cmd` и притисните Enter. Отвара се црни прозор, већ у тој фасцикли.
- Или отворите **Windows Terminal** и идите тамо помоћу `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Инсталирајте што алат треба {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Требало би да видите редове који се завршавају са `Successfully installed ...`.

## 5. Проверите да ради {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Требало би да видите `usage: heat3d_gamefiles [-h]` и списак глагола (`identify`,
`list`, `extract`, `course`, ...). То је успех: алат је спреман.

## Читање примера {#reading-the-examples}

- `<something>` је **место за попуњавање**: уместо тога укуцајте своју вредност, без
  угластих заграда. `<lap file>` постаје, на пример, `laps\my_lap.json`.
- `[--option]` у угластим заградама је **необавезно**: изоставите га ако вам не треба.
- Путања са размацима треба **двоструке наводнике**: `"C:\My Games\lap.json"`.
- Покрећите сваку команду у фасцикли алата (корак 3).

## Кад нешто није у реду {#when-something-goes-wrong}

| Видите | Шта да урадите |
|---|---|
| `'python' is not recognized` | Python није инсталиран, или „Add to PATH" није штиклирано. Покрените инсталер поново и штиклирајте га, па отворите нови терминал. |
| `No module named heat3d_gamefiles` | Терминал је у погрешној фасцикли. `cd` до фасцикле која садржи `README.md`. |
| `No module named numpy` (или неко друго име) | Корак 4 је прескочен. Покрените `pip install -r requirements.txt`. |
| `can't open file` / `not found` са путањом | Путања има размаке а нема наводнике, или је погрешно написана. Ставите је под двоструке наводнике. |

Више порука и њихових решења: [Решавање проблема](../troubleshooting.md).
