---
title: Пред да започнете
nav_order: 2
lang: "mk"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Пред да започнете {#before-you-start}

Нови сте со командната линија? Оваа страница ве води од нула до алатка што работи за
околу десет минути. Пишувате команди во прозорец наречен **терминал**, а
алатката одговара со текст.

## 1. Инсталирајте Python {#install-python}

1. Одете на [python.org/downloads](https://www.python.org/downloads/) и преземете
   **Python 3.10 или понов**.
2. Пуштете го инсталерот. На неговиот прв екран штиклирајте **„Add python.exe to PATH“**,
   а потоа кликнете **Install Now**.

## 2. Преземете ја алатката {#get-the-tool}

- **Со git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Без git:** на [страницата на GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  кликнете на зеленото копче **Code**, потоа **Download ZIP**, и распакувајте го.

## 3. Отворете терминал во папката на алатката {#open-a-terminal-in-the-tools-folder}

- Во File Explorer, отворете ја папката што ја содржи `README.md`. Кликнете во адресната
  лента, напишете `cmd` и притиснете Enter. Се отвора црн прозорец, веќе во таа папка.
- Или отворете **Windows Terminal** и одете таму со `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Инсталирајте што му треба на алатката {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Треба да видите линии што завршуваат со `Successfully installed ...`.

## 5. Проверете дали работи {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Треба да видите `usage: heat3d_gamefiles [-h]` и список на глаголи (`identify`,
`list`, `extract`, `course`, ...). Тоа е успех: алатката е подготвена.

## Читање на примерите {#reading-the-examples}

- `<something>` е **место за пополнување**: напишете своја вредност наместо тоа, без аголните
  загради. `<lap file>` станува, на пример, `laps\my_lap.json`.
- `[--option]` во средни загради е **по избор**: изоставете го ако не ви треба.
- Патека со празни места бара **двојни наводници**: `"C:\My Games\lap.json"`.
- Пуштајте ја секоја команда во папката на алатката (чекор 3).

## Кога нешто ќе тргне наопаку {#when-something-goes-wrong}

| Што гледате | Што да направите |
|---|---|
| `'python' is not recognized` | Python не е инсталиран, или „Add to PATH“ не е штиклирано. Пуштете го инсталерот повторно и штиклирајте го, потоа отворете нов терминал. |
| `No module named heat3d_gamefiles` | Терминалот е во погрешна папка. Со `cd` одете во папката што ја содржи `README.md`. |
| `No module named numpy` (или друго име) | Чекор 4 е прескокнат. Пуштете `pip install -r requirements.txt`. |
| `can't open file` / `not found` со патека | Патеката има празни места без наводници, или грешка во пишувањето. Ставете ја во двојни наводници. |

Повеќе пораки и нивните решенија: [Отстранување проблеми](troubleshooting.md).
