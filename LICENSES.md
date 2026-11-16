# Licences and third-party components

Everything in this repository that was written for it is under the MIT licence in [`LICENSE`](LICENSE). Use it, change it,
ship it, commercially or not.

What the MIT licence cannot cover is what the tools are used with: the Python
packages they import and the models game capture runs. Those carry their own
licences, and they are listed here because the answer differs by part.

Every licence below was read off the package metadata or the model card in
September 2026, not recalled. Where a component's terms changed after that, the
source is what counts, not this file.

---

## Game files — `gamefiles/`

### Software

| Package | Licence | Note |
|---|---|---|
| numpy | BSD-3-Clause | Mesh decoding |
| cryptography | Apache-2.0 / BSD-3-Clause | Only for archives the user holds a key for |
| lz4 | BSD-3-Clause | Optional; some Unity bundles need it |
| Pillow | MIT-CMU (HPND) | Decoding block-compressed textures, writing JPEGs |
| pytest | MIT | Development only |

All permissive. This exporter carries no restriction of its own.

### Oodle is found, not bundled

Most shipped Unreal content is Oodle-compressed. **Oodle (RAD Game Tools, now
Epic) is proprietary and has no redistributable build**, so `oodle.py` loads a
library already on the machine rather than carrying one — the arrangement the
licence contemplates, and the same one FModel and UModel use. `oo2core_*.dll` is
licensed to the product that ships it; `HEAT3D_OODLE` points at a copy the user
already has.

### The engine formats themselves

`.pak`, Unity's `SerializedFile` and Frostbite's `.toc` are undocumented file
formats. None of the readers here is derived from another project's source.

The Frostbite readers (`frostbitebundle.py`, `frostbiteebx.py`,
`frostbitemesh.py`, `frostbitelevel.py`) were worked out from Battlefield 6's
own files. Public descriptions of older Frostbite versions served as a map of
what to look for and supplied field names, and nothing more: the FrostyToolsuite
modding tools (github.com/CadeEvs/FrostyToolsuite and its forks, CC BY-NC-ND 4.0;
the newer FrostyToolsuite/FrostyToolsuite, GPL-3.0) for the binary bundle
manifest, the RIFF EBX chunk layout and the MeshSet structure; a format note
for Need for Speed Heat (github.com/cmprssd/nfsh, GPL-3.0) for the vertex-stream
order and the terrain quadtree's child order; and Mattias Widmark's GDC 2012 talk
"Terrain in Battlefield 3". No code from any of them is in this repository, and
every offset the readers use was measured on the shipped files, which is why
they differ from all of those sources. None of those licences is compatible
with copying into an MIT repository, and none was copied.

The game's own type library sits in its initial file system, which is
encrypted. It is not read: no key is recovered or used, and the few types the
level export needs were laid out from the data instead.

The Enfusion readers (`enfusion.py`, `enfusionworld.py`) and the Unreal
landscape reader (`unreallandscape.py`) were worked out from Arma Reforger's
and Hell Let Loose: Vietnam's own installed files, with nothing else as a
source; nothing in either game is encrypted. Bohemia Interactive publishes its
game scripts under the Arma Public Licence, which is not MIT-compatible; none
of them was read for this or copied.

Two formats are not undocumented. BeamNG publishes its `.cdae` shape cache's
layout, and the reader follows that. Unreal 5's cooked property data needs each
class's property list in order to be read; the lists embedded here
(`unversioned.py`) are property names and types only - facts about the format,
as an interoperability mappings file holds them - derived from the Unreal
Engine headers Epic makes available to anyone with a linked account, and
checked against the shipped data. No engine source is
included or required.

---

## How geometry is obtained

Three routes exist to a level's geometry, and they are shaped by quite different
things.

**Nothing here injects into a game process.** Frames come from Windows Graphics
Capture, the public API screen recorders use, and telemetry from feeds games
publish themselves. That is a deliberate constraint: injection into a title with
anti-cheat risks the account of whoever runs it.

**ReShade** was considered. Its depth buffer would make reconstruction far more
accurate, and ReShade itself is broadly tolerated — BattlEye states it bans only
actual cheats. But ReShade **disables depth-buffer access in multiplayer sessions
by design**, because depth access is a wallhack, and that is why it is tolerated
at all. So it is usable for single-player and offline titles, where it would be a
genuine improvement, and unavailable for exactly the always-online case an
analytics capture usually needs.

**Extracting geometry from shipped game files** — `.pak` archives and the like —
is a third route, and it is built, as `gamefiles/`. It reads the files of
the user's own installation.

Extractors of this kind are published openly and used widely — FModel, UModel,
AssetRipper, Noesis — and the obvious use is a developer reading *their own*
game's build. Parsing a container format is ordinary file handling.

Where the tool stops is **encryption**, and that line is drawn inside the tool.
Like the established extractors, **it ships no keys and no key-recovery**: FModel
cannot open an encrypted archive until the user supplies an AES key they
obtained themselves. The tool reads containers; it does not break locks.

So the design, which is what was built:

- **Read unencrypted archives directly.** Ordinary parsing. Every archive
  tested so far has been in this category.
- **For encrypted archives, take a key from the user and never recover one.** No
  bundled keys, no key extraction from the executable, no memory scraping.
  `pak.py` takes `aes_key=` and has no code path that obtains one.
- **Extract geometry, not assets to redistribute.** The output wanted here is a
  decimated collision or terrain mesh for spatial context, which is also the
  least of what an archive holds. It is written to the user's disk and nowhere
  else.
- **Ship nothing from a game.** No game assets, no game code, no DLLs: Oodle is
  found on the machine, as above.

One consequence worth stating plainly: Frostbite's obfuscated table form is
*detected and declined*. Its key sits in the file itself, so it is obfuscation
rather than an access control and no key would be needed from anyone — but no
file on hand uses it, and implementing a format with nothing to check it against
produces something that looks like support and is not.

3DHeat GameFiles is not affiliated with or endorsed by any game publisher. The
games and related names and trademarks belong to their owners. Rights holders:
open an issue at <https://github.com/Holdi601/3DHeat-GameFiles/issues> - we respond quickly and
remove anything on request.

---

## Sources

- [Depth Anything V2 model cards](https://huggingface.co/depth-anything) — licence per size
- [facebook/VGGT-1B](https://huggingface.co/facebook/VGGT-1B) — CC-BY-NC-4.0
- [ReShade — PCGamingWiki](https://www.pcgamingwiki.com/wiki/ReShade) — anti-cheat position
- [ReShade forum, depth buffer detection](https://reshade.me/forum/general-discussion/4083-depth-buffer-detection-modifications?start=1200) — multiplayer depth disabling
- [FModel setup](https://modding.wiki/en/aewff/developers/fmodel) — established extractors require a user-supplied AES key rather than shipping one
- [facebook/VGGT-1B-Commercial](https://huggingface.co/facebook/VGGT-1B-Commercial) — gated; access is granted per account, so it cannot be a default
- [Oodle Data Compression](http://www.radgametools.com/oodle.htm) — proprietary, no redistributable build, hence found rather than bundled
- [Review of Feed-forward 3D Reconstruction: DUSt3R to VGGT](https://arxiv.org/abs/2507.08448)
