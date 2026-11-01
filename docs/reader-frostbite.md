---
title: Frostbite
parent: Archive readers
nav_order: 5
---

# Frostbite: `.toc` and `.cas`

**Reads the tables of contents, locates assets and decompresses most payloads.**
It does **not** decode meshes. Frostbite games (Battlefield, Need for Speed, Dead
Space) keep their content in a few dozen `.cas` blobs, described by `.toc` files
that name the superbundles, the bundles inside them, and for each piece of content
the blob, offset and length.

Source: [`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py).
Command: `identify`. The rest (`parse_toc`, `read_sections`, `locations`,
`read_asset`, `decompress_payload`) is a Python API. No command lists or extracts
Frostbite assets.

## The header that looks encrypted and is not

| Magic (u32, little-endian) | Meaning | Handled |
|---|---|---|
| `0x00CED100` | plain: the tree starts immediately | read |
| `0x01CED100` | signed: a 556-byte signature, then the tree **in the clear** | read |
| `0x03CED100` | XOR-obfuscated, with the key in the file's own header | detected and declined |

The signed form is what current Battlefield ships. The high-entropy bytes after
the magic are a signature, not ciphertext. Treating the whole file as encrypted
because its first kilobyte looks random is the easy mistake.

The obfuscated form needs no key from anyone, so it is not an access control. But
no file at hand uses it, and implementing a format with nothing to check it
against would produce something that looks like support and is not. It is refused
with a message saying so.

## The DbObject tree

One recursive structure. Each field is a type byte (low five bits the type, bit 7
"anonymous"), an optional name, and a value. Containers carry their length as a
variable-length integer and end with a zero byte. Types read: list, object, bool,
string, int (4), long (**8**), float, double, GUID, SHA-1, matrix, vector4, blob.

Every container declares its own length, so a wrong type desynchronises the cursor
and the length no longer matches. `parse_toc` checks that on every container. A
file that parses was understood, not just survived. Reading `long` as four bytes
is the classic slip: small little-endian integers often still land on something
that decodes, and the damage surfaces far from its cause.

`superbundles()` lists the declared superbundle names, and `cas_references()`
finds every `(cas, offset, size)` triple wherever it appears in the tree.

## The binary section table

Current Battlefield ships a second form: a section table. It is undocumented, and
every step was checked against the files:

| Step | Check | Result (from the source) |
|---|---|---|
| section chain | 15 big-endian header words; each section starts where the last ends | closes on all 136 tables Battlefield 6 ships |
| asset identifiers | 16-byte ids, 20-byte records | 74,175 of 74,175 distinct in one level |
| asset locations | four big-endian words per asset: package, cas number, offset, size | 74,175 of 74,175 inside an installed `.cas`, none past the end |
| payloads | chains of blocks with an 8-byte header | 218 of 299 sampled consume the payload exactly |

`read_asset()` finds `cas_NN.cas` under `**\installation\*\` (or anywhere under
the root) large enough to hold the record. The package words are not decoded, so
with several installation packages installed the first large-enough file wins.

## Payload blocks

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

A zero compressed size means stored, as long as it decompresses to. That rule
raised the share of a level's payloads that parse as a clean chain from 159 of 299
to 218.

| Method word | Codec |
|---|---|
| `0x0070` | none |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md)) |
| other, with equal sizes | copied as stored |
| other | refused |

Across a Battlefield 6 install, the tables catalogue 2.98 million assets.
Decoded payloads came to 63 MB carrying recognisable Frostbite signatures. The
81 sampled payloads that do not decode are high-entropy from their first byte, a
different encoding or encrypted, and they are refused rather than guessed at.

## Not implemented

- The XOR-obfuscated table form.
- The payloads that are not block chains.
- The Frostbite **mesh format**. The tables say what a level contains, where it lives, and hand you the bytes. Turning those into geometry is a separate and much larger problem.
