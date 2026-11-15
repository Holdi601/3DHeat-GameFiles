---
title: "Преди да започнете"
nav_order: 2
lang: bg
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Преди да започнете {#before-you-start}

Нов ли сте в командния ред? Тази страница ви води от нищо до работещ инструмент за около
десет минути. Въвеждате команди в прозорец, наречен **терминал**, а инструментът отговаря с текст.

## 1. Инсталирайте Python {#install-python}

1. Отидете на [python.org/downloads](https://www.python.org/downloads/) и изтеглете
   **Python 3.10 или по-нов**.
2. Стартирайте инсталатора. На първия екран отметнете **„Add python.exe to PATH“**,
   после щракнете **Install Now**.

## 2. Вземете инструмента {#get-the-tool}

- **С git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Без git:** на [страницата в GitHub](https://github.com/Holdi601/3DHeat-GameFiles)
  щракнете зеления бутон **Code**, после **Download ZIP**, и разархивирайте.

## 3. Отворете терминал в папката на инструмента {#open-a-terminal-in-the-tools-folder}

- В File Explorer отворете папката, която съдържа `README.md`. Щракнете в адресния ред,
  напишете `cmd` и натиснете Enter. Отваря се черен прозорец, вече в тази папка.
- Или отворете **Windows Terminal** и отидете там с `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Инсталирайте нужното на инструмента {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Ще видите редове, които завършват с `Successfully installed ...`.

## 5. Проверете, че работи {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Трябва да видите `usage: heat3d_gamefiles [-h]` и списък с командите (`identify`,
`list`, `extract`, `course`, ...). Това е успех: инструментът е готов.

## Как да четете примерите {#reading-the-examples}

- `<нещо>` е **място за попълване**: напишете своята стойност вместо това, без
  ъгловите скоби. `<lap file>` става, например, `laps\my_lap.json`.
- `[--option]` в квадратни скоби е **по желание**: пропуснете го, ако не ви трябва.
- Път с интервали се пише в **двойни кавички**: `"C:\My Games\lap.json"`.
- Пускайте всяка команда в папката на инструмента (стъпка 3).

## Когато нещо се обърка {#when-something-goes-wrong}

| Виждате | Какво да направите |
|---|---|
| `'python' is not recognized` | Python не е инсталиран или не е отметнато „Add to PATH“. Стартирайте инсталатора отново, отметнете го и отворете нов терминал. |
| `No module named heat3d_gamefiles` | Терминалът е в грешна папка. `cd` до папката, която съдържа `README.md`. |
| `No module named numpy` (или друго име) | Стъпка 4 е пропусната. Стартирайте `pip install -r requirements.txt`. |
| `can't open file` / `not found` с път | Пътят има интервали без кавички, или е сбъркан. Сложете го в двойни кавички. |

Още съобщения и как да ги поправите: [Отстраняване на неизправности](../troubleshooting.md).
