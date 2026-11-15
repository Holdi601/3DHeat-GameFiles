---
title: С чего начать
nav_order: 2
lang: ru
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# С чего начать {#before-you-start}

Впервые в командной строке? Эта страница проведёт вас от нуля до рабочего инструмента примерно
за десять минут. Вы вводите команды в окно, которое называется **терминалом**, а инструмент
отвечает текстом.

## 1. Установите Python {#install-python}

1. Перейдите на [python.org/downloads](https://www.python.org/downloads/) и скачайте
   **Python 3.10 или новее**.
2. Запустите установщик. На его первом экране отметьте **«Add python.exe to PATH»**,
   затем нажмите **Install Now**.

## 2. Получите инструмент {#get-the-tool}

- **С git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Без git:** на [странице GitHub](https://github.com/Holdi601/3DHeat-GameFiles) нажмите
  зелёную кнопку **Code**, затем **Download ZIP**, и распакуйте архив.

## 3. Откройте терминал в папке инструмента {#open-a-terminal-in-the-tools-folder}

- В Проводнике откройте папку, в которой лежит `README.md`. Щёлкните в адресной строке, введите
  `cmd` и нажмите Enter. Откроется чёрное окно, уже в этой папке.
- Или откройте **Windows Terminal** и перейдите туда командой `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Установите то, что нужно инструменту {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Вы должны увидеть строки, которые заканчиваются на `Successfully installed ...`.

## 5. Проверьте, что всё работает {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Вы должны увидеть `usage: heat3d_gamefiles [-h]` и список команд (`identify`,
`list`, `extract`, `course`, ...). Это успех: инструмент готов.

## Как читать примеры {#reading-the-examples}

- `<something>` — это **заполнитель**: вместо него введите своё значение, без угловых скобок.
  `<lap file>` станет, например, `laps\my_lap.json`.
- `[--option]` в квадратных скобках — **необязательно**: не вводите, если не нужно.
- Путь с пробелами нужно брать в **двойные кавычки**: `"C:\My Games\lap.json"`.
- Выполняйте каждую команду в папке инструмента (шаг 3).

## Если что-то пошло не так {#when-something-goes-wrong}

| Вы видите | Что делать |
|---|---|
| `'python' is not recognized` | Python не установлен или не отмечена галочка «Add to PATH». Запустите установщик снова, отметьте её, затем откройте новый терминал. |
| `No module named heat3d_gamefiles` | Терминал в неверной папке. Выполните `cd` в папку, где лежит `README.md`. |
| `No module named numpy` (или другое имя) | Шаг 4 пропущен. Выполните `pip install -r requirements.txt`. |
| `can't open file` / `not found` с путём | В пути есть пробелы без кавычек или опечатка. Возьмите путь в двойные кавычки. |

Остальные сообщения и их решения: [Устранение неполадок](../troubleshooting.md).
