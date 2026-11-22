---
title: Before you start
nav_order: 2
---

# Before you start

New to the command line? This page gets you from nothing to a working tool in
about ten minutes. You type commands into a window called a **terminal**, and
the tool answers with text.

## The standalone program (no Python needed)

Each [release](https://github.com/Holdi601/3DHeat-GameFiles/releases/latest)
has a ready-to-run program for Windows (`heat3d-gamefiles-<version>-windows-x64.zip`),
Linux (`...-linux-x64.tar.gz`) and macOS (`...-macos-arm64.tar.gz`), with a
`SHA256SUMS` file to check the download. Unpack it anywhere and start
`heat3d-gamefiles` (on macOS the first start may need *Open* from the
right-click menu, as the program is not notarised); steps 1 to 4 below are
then not needed.

Started without arguments it opens a window that:

- says what is missing: the Oodle library some archives need (it comes from a
  game or engine installed on your machine), free disk space;
- lists an Unreal 5 game's World Partition maps and exports the one you name
  into the 3DHeat levels folder (`HEAT3D_LEVELS`, by default
  `%LOCALAPPDATA%\3DHeat\levels` on Windows and `~/.local/share/3dheat/levels`
  elsewhere), where the viewer finds it;
- says what a file is, and lists what an archive holds;
- checks for updates and asks before installing one, unless you tick
  *Update automatically*.

The same program runs every command on these pages:
`heat3d-gamefiles heat3d-gamefiles identify <file>`, or simply
`heat3d-gamefiles identify <file>`. For scripts: `heat3d-gamefiles --check --json`
reports what is found and missing; GameFiles has no fixed games, so
`heat3d-gamefiles status --json` lists none. The game readers built on it
(Forza, BeamNG.drive, AC Rally, ...) have programs of their own. The 3DHeat
app's Extractors panel installs, updates and starts it for you.

The window walks through four steps (find the game, choose, work, done) in the 3DHeat look, dark or light. On Windows the program opens only its window, with no console window; in a terminal it prints as usual, and `heat3d-gamefiles-cli.cmd` in the same folder makes the terminal wait for it and pass on its exit code.

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
