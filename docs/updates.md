---
title: Updates
nav_order: 10
---

# Updates

3DHeat GameFiles checks this repository's GitHub releases when it starts, says
when a newer version is out, and offers to update. Your own files (recordings,
settings, exports) are never touched.

Source: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
The installed version is the repository's
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) file.

## The check at start-up

Every `python -m heat3d_gamefiles ...` run calls the check before it parses its
arguments:

- It asks `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`,
  with a **5 second** timeout.
- The answer is cached for **6 hours** in
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (or
  `~/.cache/3DHeat/...` without `LOCALAPPDATA`). Within that time no request is
  made. "No release yet" (HTTP 404) is cached too.
- Offline, rate-limited or behind a proxy, the check simply returns and the tool
  runs on the version it has.
- If the latest release's tag (`v1.2.3` or `1.2.3`; anything after `-` or `+` is
  ignored) is newer than `VERSION`, it prints to stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **At a terminal** (stdin and stderr are both a TTY) it asks `Update now? [Y/n]`.
  Enter, `y`, `yes`, `j` or `ja` updates. After a successful update, the **same
  command is started again** on the new code, and its exit code is passed on.
- **Without a terminal** (a scheduled run, a pipe) it only prints
  ``Run `python -m heat3d_update` in <folder> to update.`` and carries on.

## Updating on request

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

This always asks GitHub (no cache). It prints `Up to date: 1.0.1.`,
`No release found (...)`, or what it did. The exit code is 1 if the update could
not be applied.

## How an update is applied

| Installed as | Update |
|---|---|
| a **git clone** (a `.git` folder and `git` on the PATH) | `git pull --ff-only`. **Refused** while tracked files have local changes: "this checkout has local changes; commit or stash them, then run `git pull`". Untracked files do not block it |
| a **downloaded copy** | the release's source archive (`zipball_url`) is downloaded and unpacked to a temporary folder, ignoring any path that would escape it; its `VERSION` must equal the release's version, or nothing is copied; then its files are copied over this folder |

When copying from an archive, files that are not part of the release (recordings,
virtual environments, settings, anything you made) are left alone. The updater
also tries to delete `.py` modules that a release removed from its packages, so a
stale module cannot shadow its replacement. As written, that step looks for
packages one folder below the archive root (`*/heat3d_*`). This repository's
packages sit at the root, so whether stale modules are actually removed here is
unverified.

## Switching it off

```
set HEAT3D_NO_UPDATE=1
```

Any value other than empty, `0`, `false` or `no` turns off both the start-up check
and the offer. `python -m heat3d_update` still works when run by hand.
