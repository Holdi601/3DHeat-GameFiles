---
title: Перш ніж почати
nav_order: 2
lang: uk
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Перш ніж почати {#before-you-start}

Ви лише починаєте працювати з командним рядком? Ця сторінка проведе вас від нуля до
робочого інструмента приблизно за десять хвилин. Ви вводите команди у вікно, яке
називається **термінал**, а інструмент відповідає текстом.

## 1. Встановіть Python {#install-python}

1. Перейдіть на [python.org/downloads](https://www.python.org/downloads/) і завантажте
   **Python 3.10 або новіший**.
2. Запустіть інсталятор. На його першому екрані позначте **"Add python.exe to PATH"**,
   потім натисніть **Install Now**.

## 2. Отримайте інструмент {#get-the-tool}

- **З git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Без git:** на [сторінці GitHub](https://github.com/Holdi601/3DHeat-GameFiles)
  натисніть зелену кнопку **Code**, потім **Download ZIP**, і розпакуйте архів.

## 3. Відкрийте термінал у папці інструмента {#open-a-terminal-in-the-tools-folder}

- У Провіднику файлів відкрийте папку, у якій лежить `README.md`. Клацніть рядок адреси,
  введіть `cmd` і натисніть Enter. Відкриється чорне вікно, вже в цій папці.
- Або відкрийте **Windows Terminal** і перейдіть туди командою `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Встановіть те, що потрібно інструменту {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Ви маєте побачити рядки, що закінчуються на `Successfully installed ...`.

## 5. Перевірте, що він працює {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Ви маєте побачити `usage: heat3d_gamefiles [-h]` і список команд (`identify`,
`list`, `extract`, `course`, ...). Це означає успіх: інструмент готовий.

## Як читати приклади {#reading-the-examples}

- `<something>` — це **заповнювач**: введіть замість нього власне значення, без кутових
  дужок. Наприклад, `<lap file>` стає `laps\my_lap.json`.
- `[--option]` у квадратних дужках — **необов'язковий**: пропустіть його, якщо він вам не потрібен.
- Шлях із пробілами потребує **подвійних лапок**: `"C:\My Games\lap.json"`.
- Виконуйте кожну команду в папці інструмента (крок 3).

## Якщо щось пішло не так {#when-something-goes-wrong}

| Ви бачите | Що робити |
|---|---|
| `'python' is not recognized` | Python не встановлено або не було позначено **Add python.exe to PATH**. Запустіть інсталятор знову, позначте це і відкрийте новий термінал. |
| `No module named heat3d_gamefiles` | Термінал у неправильній папці. Виконайте `cd` до папки, у якій лежить `README.md`. |
| `No module named numpy` (або інша назва) | Крок 4 пропущено. Виконайте `pip install -r requirements.txt`. |
| `can't open file` / `not found` з шляхом | Шлях містить пробіли без лапок або є помилка в написанні. Візьміть його в подвійні лапки. |

Більше повідомлень і їхні виправлення: [Усунення несправностей](../troubleshooting.md).
