
# Rules and licences

Three rules shape the whole tool. They are design decisions, not just
disclaimers. Full text: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
This page is a record of what the licences say, not legal advice.

## 1. No keys: none shipped, none recovered

**It reads containers.** Parsing an archive format is ordinary file handling, and
FModel, UModel and AssetRipper have done it in the open for years. Nothing about
parsing a container is itself a circumvention.

**The line that matters is encryption, and it is drawn inside the tool.** A tool
whose purpose is to defeat an access control is itself in scope of
anti-circumvention law (DMCA §1201(a)(2) reaches technologies, not only acts),
even if nobody distributes a single extracted file. So:

- **No bundled keys.** There is no key in the code or the data.
- **No key recovery.** Nothing searches an executable for a key, and nothing reads
  another process's memory.
- **A key you hold, or nothing.** An encrypted Unreal `.pak` opens only with
  `--key <hex>` (in Python, `PakArchive(path, aes_key=...)`). `pak.py` has no code
  path that obtains a key. An encrypted IoStore container is refused outright.
- **Obfuscation is not implemented either.** Frostbite's XOR-obfuscated tables
  keep their key in the file itself, so they are obfuscation rather than an access
  control. They are still detected and declined, because no file on hand uses that
  form and there would be nothing to check an implementation against. Assetto
  Corsa EVO's keyed package is refused for the same reason the keys rule exists.
- **Nothing injects into a game process.** Telemetry comes from feeds games
  publish themselves, and capture uses public screen-recording APIs (in the other
  3DHeat tools). Injection into a title with anti-cheat risks the account of
  whoever runs it.

Every archive tested so far is unencrypted.

## 2. Your own files, your responsibility

The tool reads the game files **installed on your machine**. It never downloads
game content.

What you point it at stays your responsibility. Games carry their own licence
terms, and EULAs commonly prohibit reverse engineering. Those are enforceable
contracts, and the obligation sits with whoever runs the tool, on whichever game.
No design choice here discharges it. The clearest legitimate case is a developer
reading their own studio's build: a different team's title, an old branch, a build
from a partner.

## 3. Output is not for redistribution

What comes out is geometry for **spatial context**: the ground, the road and what
stands beside it, decimated to a budget, so laps can be analysed in place. It is
the least of what an archive holds, and it is still the game publisher's content.

- Keep exported `.glb` files, and the textures inside them, for your own analysis.
- Do not publish, share or sell exported courses, levels, models or textures.
- The repository's `.gitignore` keeps game files, exports, laps and recordings out
  of version control by folder and by file type (`*.glb`, `*.pak`, `*.minizip`,
  `*.utoc`, `*.png`, `*.lap.json` and more).

## Oodle is found, not bundled

Oodle (RAD Game Tools, now Epic) is proprietary and has no redistributable build.
`oo2core_*.dll` is licensed to the product that ships it. `oodle.py` therefore
loads a library already on the machine rather than carrying one. This is the
arrangement the licence contemplates, and the same one FModel and UModel use.
See [Oodle](reader-oodle).

## The formats themselves

- `.pak`, IoStore, Unity's `SerializedFile`, Frostbite's `.toc` and ForzaTech's
  formats are undocumented. Reading them is reverse engineering of a container.
  None of the readers here is derived from another project's source.
- BeamNG publishes its `.cdae` layout, and the reader follows it.
- Valve documents VPK.
- Unreal 5's cooked property data needs each class's property list. The lists in
  `unversioned.py` are **names and types only**, facts about the format such as an
  interoperability mappings file holds. They were derived from the Unreal Engine
  headers Epic makes available to anyone with a linked account, and checked
  against the shipped data. No engine source is included or required.

## This tool's licence

Everything written for this repository is under the **MIT licence**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
use it, change it, ship it, commercially or not.

Third-party packages, all permissive, so the exporter carries no restriction of
its own:

| Package | Licence | Used for |
|---|---|---|
| numpy | BSD-3-Clause | mesh decoding |
| cryptography | Apache-2.0 / BSD-3-Clause | only archives you hold a key for |
| lz4 | BSD-3-Clause | Forza archives, some Unity bundles, IoStore LZ4 blocks |
| Pillow | MIT-CMU (HPND) | block-compressed textures, JPEG output |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | the few zstd-compressed `.cdae`, Frostbite zstd blocks |
| pytest | MIT | development only |

The licences were read off the package metadata in September 2026. Where a
component's terms changed after that, the source is what counts.
