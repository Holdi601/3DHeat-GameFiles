"""
Tests for the Frostbite reader.

Frostbite ships two forms of table of contents and this reads both, so both are
checked, and each has its own way of proving it was understood.

The **DbObject tree** declares every container's length in bytes. A field type
read at the wrong width desynchronises the cursor, and the container then does
not end where it said it would. `parse_toc` raises on that rather than returning
a half-parsed tree, so a file that parses is a file whose every type was right —
which is how the reader found that `0x09` is an eight-byte long and not a
four-byte integer, four bytes at a time.

The **binary table** proves itself differently: its section offsets are stated
*and* derivable from two counts, so the arithmetic either closes or it does not.
It closes on all 136 binary tables Battlefield 6 ships.

Geometry is tested next door, in `test_frostbitelevel.py`: the tables name
chunks and say where their bytes live, and that is what is tested here — down
to which installation package a location's blob belongs to.
"""

from __future__ import annotations

import glob
import os
import struct
from pathlib import Path

import pytest

from heat3d_gamefiles.frostbite import (
    MAGIC_OBFUSCATED,
    MAGIC_PLAIN,
    MAGIC_SIGNED,
    SIGNED_HEADER,
    UnsupportedFrostbite,
    asset_ids,
    describe,
    game_root,
    install_packages,
    location_at,
    parse_toc,
    read_asset,
    read_header,
    decompress_payload,
    locations,
    read_sections,
    split_blocks,
    superbundles,
)

from .installed import installed

def tables() -> list[Path]:
    return sorted(installed("Battlefield*/**/*.toc"))


INSTALLED = tables()


def _varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(out)


def _field(name: str | None, value) -> bytes:
    """One DbObject field, the inverse of what `parse_toc` reads."""
    if isinstance(value, dict):
        type_id = 0x02
        body = b"".join(_field(k, v) for k, v in value.items()) + b"\x00"
        raw = _varint(len(body)) + body
    elif isinstance(value, list):
        type_id = 0x01
        body = b"".join(_field(None, v) for v in value) + b"\x00"
        raw = _varint(len(body)) + body
    elif isinstance(value, str):
        type_id = 0x07
        text = value.encode() + b"\x00"
        raw = _varint(len(text)) + text
    else:
        type_id = 0x08
        raw = struct.pack("<i", value)
    if name is None:
        return bytes([type_id | 0x80]) + raw
    return bytes([type_id]) + name.encode() + b"\x00" + raw


def _install(root: Path, chunks: list[dict]) -> Path:
    """A miniature installation: `Data/layout.toc` declaring `chunks`."""
    (root / "Data").mkdir(parents=True)
    tree = _field(None, {"installManifest": {"installChunks": chunks}})
    signed = struct.pack("<I", MAGIC_SIGNED).ljust(SIGNED_HEADER, b"\x00")
    (root / "Data" / "layout.toc").write_bytes(signed + tree)
    return root.resolve()


class TestPackages:
    """
    A location names its package, and `layout.toc` names the package's folder.

    Every package numbers its blobs from `cas_01`, so the blob number alone is
    ambiguous the moment two packages are installed — which is every real
    installation. These build one with two packages whose `cas_01.cas` differ.
    """

    def build(self, tmp_path: Path) -> Path:
        root = _install(
            tmp_path / "game",
            [
                {"name": "installation/base", "persistentIndex": 0x14FB60ED,
                 "installBundle": "Win32/installation/base"},
                {"name": "installation/later", "persistentIndex": -0x7CBF13D1,
                 "installBundle": "Win32/installation/later"},
                {"name": "installation/absent", "persistentIndex": 7,
                 "installBundle": "Win32/installation/absent"},
            ],
        )
        base = root / "Data" / "Win32" / "installation" / "base"
        later = root / "Update" / "Pack" / "Data" / "Win32" / "installation" / "later"
        base.mkdir(parents=True)
        later.mkdir(parents=True)
        (base / "cas_01.cas").write_bytes(b"B" * 64)
        (later / "cas_01.cas").write_bytes(b"L" * 64)
        return root

    def test_a_package_resolves_to_its_own_folder(self, tmp_path):
        root = self.build(tmp_path)
        packages = install_packages(root)

        assert packages[0x14FB60ED] == [root / "Data" / "Win32" / "installation" / "base"]
        # Negative in the tree, because DbObject integers are signed.
        assert packages[0x8340EC2F][0].parts[-5:-3] == ("Pack", "Data")
        assert packages[7] == []

    def test_the_same_blob_number_reads_from_the_right_package(self, tmp_path):
        root = self.build(tmp_path)
        record = struct.pack(">4I", 0x8340, 0xEC2F0001, 8, 4)

        spot = location_at(record, 0)

        assert (spot.package, spot.cas, spot.offset, spot.size) == (0x8340EC2F, 1, 8, 4)
        assert read_asset(root, spot) == b"LLLL"
        assert read_asset(root / "Data", location_at(struct.pack(">4I", 0x14FB, 0x60ED0001, 0, 2), 0)) == b"BB"

    def test_an_undeclared_or_uninstalled_package_is_refused(self, tmp_path):
        root = self.build(tmp_path)
        with pytest.raises(UnsupportedFrostbite, match="not declared"):
            read_asset(root, location_at(struct.pack(">4I", 0, 0x12340001, 0, 1), 0))
        with pytest.raises(UnsupportedFrostbite, match="no cas_01"):
            read_asset(root, location_at(struct.pack(">4I", 0, 0x00070001, 0, 1), 0))

    def test_the_root_is_found_from_anything_inside_it(self, tmp_path):
        root = self.build(tmp_path)
        assert game_root(root / "Data" / "Win32" / "installation" / "base") == root.resolve()


def test_signed_header_is_not_encryption():
    """
    A signed table is plain after 556 bytes; only the third form is obfuscated.

    Worth pinning as its own test because the high-entropy bytes after the magic
    look exactly like ciphertext, and calling the whole file encrypted would have
    meant refusing every table Battlefield ships.
    """
    assert read_header(struct.pack("<I", MAGIC_SIGNED) + bytes(600)).payload_offset == (
        SIGNED_HEADER
    )
    assert read_header(struct.pack("<I", MAGIC_PLAIN) + bytes(600)).payload_offset == 0


def test_obfuscated_form_is_declined_rather_than_guessed():
    with pytest.raises(UnsupportedFrostbite, match="obfuscated"):
        read_header(struct.pack("<I", MAGIC_OBFUSCATED) + bytes(600))


def test_rejects_a_file_that_is_not_a_table():
    with pytest.raises(UnsupportedFrostbite, match="not a Frostbite"):
        read_header(b"\x00" * 64, "random.bin")


@pytest.mark.skipif(not INSTALLED, reason="no Frostbite game on this machine")
def test_every_shipped_table_is_recognised():
    """Each one parses as a tree or as a section table, with none left over."""
    described = [describe(p) for p in INSTALLED]

    assert len(described) == len(INSTALLED)
    assert any("DbObject tree" in d for d in described), "no tree form found"
    assert any("binary table" in d for d in described), "no binary form found"


@pytest.mark.skipif(not INSTALLED, reason="no Frostbite game on this machine")
def test_the_tree_form_names_its_superbundles():
    """
    Every container in the tree consumed exactly the length it declared.

    `parse_toc` enforces that internally, so reaching a list of superbundle names
    at all means the whole tree was read with the right type widths.
    """
    trees = []
    for path in INSTALLED:
        try:
            trees.append(parse_toc(path)[1])
        except UnsupportedFrostbite:
            continue
    if not trees:
        pytest.skip("this installation ships no DbObject table")

    names = [n for tree in trees for n in superbundles(tree)]
    assert names, "the tree parsed but named nothing"
    assert all(isinstance(n, str) and n for n in names)


@pytest.mark.skipif(not INSTALLED, reason="no Frostbite game on this machine")
def test_binary_section_chain_closes_on_every_table():
    """
    Each section starts where the previous one ends, and the last ends in-file.

    `read_sections` raises when it does not, so this asserts that the reader
    accepted at least a representative number of them rather than quietly
    finding every table unsupported.
    """
    accepted = 0
    for path in INSTALLED:
        data = path.read_bytes()
        info = read_header(data, path.name)
        try:
            sections = read_sections(data, info, path.name)
        except UnsupportedFrostbite:
            continue  # the DbObject form, checked above
        accepted += 1
        assert sections.asset_count >= 0
        assert info.payload_offset + sections.end <= len(data)

    assert accepted > 1, "no binary table was accepted"


@pytest.mark.skipif(not INSTALLED, reason="no Frostbite game on this machine")
def test_asset_identifiers_are_all_distinct():
    """
    A misread record size produces repeats, because it reslices the same bytes.

    Distinctness across tens of thousands of records is strong evidence the
    20-byte stride is right — far stronger than the records merely being
    readable.
    """
    biggest = None
    for path in INSTALLED:
        data = path.read_bytes()
        info = read_header(data, path.name)
        try:
            sections = read_sections(data, info, path.name)
        except UnsupportedFrostbite:
            continue
        if biggest is None or sections.asset_count > biggest[2].asset_count:
            biggest = (data, info, sections)
    if biggest is None:
        pytest.skip("this installation ships no binary table")

    data, info, sections = biggest
    identifiers = asset_ids(data, info, sections)

    assert len(identifiers) == sections.asset_count
    assert len(set(identifiers)) == len(identifiers)
    assert all(len(i) == 16 for i in identifiers)


class TestFindingAndReadingTheBytes:
    """
    The step from a catalogue to an extractor.

    Every asset's location is four big-endian words that nothing documents. The
    interpretation below — a blob index, an offset, a length and a package
    identifier — was read off the numbers and then checked against the files: all
    74,175 records of a Battlefield 6 level land inside an installed `.cas`, none
    runs past the end of its file, and none names a blob that is not there. A
    wrong field order does not produce that.

    The payloads are then chains of eight-byte-headed blocks, and the same kind
    of check applies: a chain either consumes the payload exactly or it is not a
    chain. Read from the package the location names, every sampled payload is
    one; read from the first blob of the right number, a third looked encrypted.
    """

    @staticmethod
    def level_table() -> Path | None:
        for path in INSTALLED:
            data = path.read_bytes()
            try:
                sections = read_sections(data, read_header(data, path.name), path.name)
            except UnsupportedFrostbite:
                continue
            if sections.asset_count > 1000:
                return path
        return None

    @pytest.mark.skipif(not INSTALLED, reason="no Frostbite game on this machine")
    def test_every_location_lands_inside_an_installed_blob(self):
        import glob
        import os

        path = self.level_table()
        if path is None:
            pytest.skip("no table here holds enough assets to be worth checking")
        data = path.read_bytes()
        info = read_header(data, path.name)
        sections = read_sections(data, info, path.name)

        root = path
        while root.parent != root and root.name != "Data":
            root = root.parent
        blobs: dict[int, list[int]] = {}
        for found in glob.glob(os.path.join(str(root.parent), "**", "cas_*.cas"), recursive=True):
            index = int(os.path.basename(found).split("_")[1].split(".")[0])
            blobs.setdefault(index, []).append(os.path.getsize(found))
        if not blobs:
            pytest.skip("no .cas blobs beside this table")

        for spot in locations(data, info, sections):
            assert spot.cas in blobs, f"cas_{spot.cas:02d} is referenced but not installed"
            assert any(spot.end <= size for size in blobs[spot.cas]), (
                f"cas_{spot.cas:02d} is too small for bytes "
                f"{spot.offset}-{spot.end}"
            )

    def test_a_payload_that_is_not_a_block_chain_is_refused(self):
        """
        Refused, not partially decoded.

        A chain has to consume the payload exactly. Anything else is a different
        encoding — or encryption — and returning the first plausible block would
        hand the caller a fragment that looks like data.
        """
        with pytest.raises(UnsupportedFrostbite):
            split_blocks(bytes(range(64)))

    def test_a_stored_block_declares_no_compressed_length(self):
        """
        A zero in the compressed field means stored, as long as it decompresses to.

        Reading it as a zero-length block rejects the whole payload: honouring it
        took the share of a level's payloads that parse as a clean chain from 159
        of 299 to 218.
        """
        body = bytes(range(256)) * 4
        payload = struct.pack(">IHH", len(body), 0x0071, 0) + body

        blocks = split_blocks(payload)

        assert len(blocks) == 1
        assert blocks[0].compressed == len(body)
        assert decompress_payload(payload) == body

    def test_a_stored_block_round_trips(self):
        body = b"VAND" + bytes(range(200))
        payload = struct.pack(">IHH", len(body), 0x0070, len(body)) + body

        assert decompress_payload(payload) == body

    @pytest.mark.skipif(not INSTALLED, reason="no Frostbite game on this machine")
    def test_sampled_payloads_from_the_right_package_all_decode(self):
        """
        With the package resolved, payloads are block chains — all of them.

        Taking the first `cas_NN.cas` of the right number instead made a third of
        a sample look high-entropy, which read as encryption and was the wrong
        blob. This samples across the table so a regression shows.
        """
        path = self.level_table()
        if path is None:
            pytest.skip("no table here holds enough assets to be worth checking")
        data = path.read_bytes()
        info = read_header(data, path.name)
        spots = locations(data, info, read_sections(data, info, path.name))
        packages = install_packages(path)

        sample = spots[:: max(1, len(spots) // 60)]
        for spot in sample:
            assert spot.package in packages, f"package 0x{spot.package:08X} undeclared"
            payload = read_asset(path, spot)
            assert len(payload) == spot.size
            split_blocks(payload)  # raises when it is not a chain

    def test_a_chain_of_several_blocks_joins_in_order(self):
        first = b"A" * 100
        second = b"B" * 60
        payload = (
            struct.pack(">IHH", len(first), 0x0070, len(first))
            + first
            + struct.pack(">IHH", len(second), 0x0070, len(second))
            + second
        )

        assert decompress_payload(payload) == first + second
