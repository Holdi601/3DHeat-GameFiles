---
title: Before you start
nav_order: 2
---

# Before you start

New to the command line? This page gets you from nothing to a working tool in
about ten minutes. You type commands into a window called a **terminal**, and
the tool answers with text.

## 1. Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download
   **Python 3.10 or later**.
2. Run the installer. On its first screen, tick **"Add python.exe to PATH"**,
   then click **Install Now**.

## 2. Get the tool

- **With git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Without git:** on the [GitHub page](https://github.com/Holdi601/3DHeat-GameFiles),
  click the green **Code** button, then **Download ZIP**, and unpack it.

## 3. Open a terminal in the tool's folder

- In File Explorer, open the folder that holds `README.md`. Click the address
  bar, type `cmd` and press Enter. A black window opens, already in that folder.
- Or open **Windows Terminal** and go there with `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Install what the tool needs

```
pip install -r requirements.txt
```

You should see lines ending in `Successfully installed ...`.

## 5. Check that it works

```
python -m heat3d_gamefiles --help
```

You should see `usage: heat3d_gamefiles [-h]` and a list of verbs (`identify`,
`list`, `extract`, `course`, ...). That is success: the tool is ready.

## Reading the examples

- `<something>` is a **placeholder**: type your own value instead, without the
  angle brackets. `<lap file>` becomes, for example, `laps\my_lap.json`.
- `[--option]` in square brackets is **optional**: leave it out if you don't need it.
- A path with spaces needs **double quotes**: `"C:\My Games\lap.json"`.
- Run every command in the tool's folder (step 3).

## When something goes wrong

| You see | What to do |
|---|---|
| `'python' is not recognized` | Python is not installed, or "Add to PATH" was not ticked. Run the installer again and tick it, then open a new terminal. |
| `No module named heat3d_gamefiles` | The terminal is in the wrong folder. `cd` to the folder that holds `README.md`. |
| `No module named numpy` (or another name) | Step 4 was skipped. Run `pip install -r requirements.txt`. |
| `can't open file` / `not found` with a path | The path has spaces and no quotes, or a typo. Put it in double quotes. |

More messages and their fixes: [Troubleshooting](troubleshooting.md).
