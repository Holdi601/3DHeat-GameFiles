"""
`identify`, `list` and `extract` as someone runs them, on every archive there
is a reader for.

Each archive is built the way its game ships it (see the fixtures each reader's
own tests use), and the command line is given nothing but the file: the format
has to come from the bytes. The failures matter as much as the successes - a
file the tool cannot open has to say so in a line and exit non-zero, not end in
a traceback.
"""

from __future__ import annotations

import io
import zipfile

import pytest

from heat3d_gamefiles.cli import main
from heat3d_gamefiles.minizip import DEFLATE, LZ4, STORED

from .beamng_fixtures import cdae, terrain_file
from .forza_fixtures import build_contents, build_minizip
from .test_pak import build_pak
from .test_vpk import build_vpk
from .unreal_fixtures import write_container

#: An AES-256 key, as hex: 64 digits.
KEY = "00" * 32


def run(capsys, *argv) -> tuple[int, str, str]:
    code = main([str(a) for a in argv])
    out, err = capsys.readouterr()
    return code, out, err


@pytest.fixture
def minizip(tmp_path):
    payloads = [b"terrain " * 40, b"a guardrail", b"x" * 300]
    path = build_minizip(tmp_path / "GeoChunk2.minizip", payloads, codecs=[LZ4, STORED, DEFLATE])
    return path, payloads


def level_zip(path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("levels/example_level/info.json", '{"title": "Example"}')
        bundle.writestr("levels/example_level/main/items.level.json", "{}\n" * 50)
        bundle.writestr("levels/example_level/art/rock.cdae", b"\x1f" + bytes(40))
    path.write_bytes(buffer.getvalue())
    return path


class TestIdentify:
    def test_a_minizip_is_an_archive_this_reads(self, capsys, minizip):
        path, _ = minizip
        build_contents(path.with_name("ChunkContentsMiniZip2.txt"), ["a.modelbin", "b.modelbin", "c.pb"])

        code, out, _ = run(capsys, "identify", path)

        assert code == 0
        assert "ForzaTech .minizip archive, version 101" in out
        assert "3 in 1 segments" in out
        assert "ChunkContentsMiniZip2.txt" in out
        assert "not implemented" not in out and "not a format" not in out

    def test_a_minizip_without_its_manifest_goes_by_number(self, capsys, minizip):
        code, out, _ = run(capsys, "identify", minizip[0])

        assert code == 0 and "entries go by number" in out

    def test_an_iostore_container_and_its_partition(self, capsys, tmp_path):
        utoc = write_container(tmp_path, "pakchunk0-Windows", {"Maps/Example.umap": b"map", "a.uasset": b"x" * 10})

        code, out, _ = run(capsys, "identify", utoc)
        assert code == 0
        assert "Unreal IoStore table of contents, version 8" in out
        assert "files      2" in out and "encrypted  no" in out

        code, out, _ = run(capsys, "identify", utoc.with_suffix(".ucas"))
        assert code == 0 and "pakchunk0-Windows.utoc" in out

    def test_a_beamng_level_zip(self, capsys, tmp_path):
        code, out, _ = run(capsys, "identify", level_zip(tmp_path / "example_level.zip"))

        assert code == 0
        assert "zip archive, 3 entries" in out
        assert "example_level (laid out as a BeamNG.drive level)" in out

    def test_a_beamng_shape(self, capsys, tmp_path):
        path = tmp_path / "rail.cdae"
        path.write_bytes(cdae([[0, 0, 0], [4, 0, 0], [4, 0, 1]], [[0, 1, 2]], materials=("rail_mat",)))

        code, out, _ = run(capsys, "identify", path)

        assert code == 0
        assert "BeamNG.drive shape (.cdae), version 31" in out and "rail_mat" in out

    def test_a_beamng_terrain(self, capsys, tmp_path):
        path = tmp_path / "example.ter"
        path.write_bytes(terrain_file()[0])

        code, out, _ = run(capsys, "identify", path)

        assert code == 0
        assert "BeamNG.drive terrain (.ter), version 9" in out
        assert "65 x 65" in out and "Grass, Asphalt" in out

    def test_something_else_is_still_refused(self, capsys, tmp_path):
        path = tmp_path / "notes.txt"
        path.write_bytes(b"hello there " * 20)

        code, out, _ = run(capsys, "identify", path)

        assert code == 0 and "not a format this tool reads" in out


class TestListAndExtract:
    def test_a_minizip_by_the_names_beside_it(self, capsys, tmp_path, minizip):
        path, payloads = minizip
        build_contents(path.with_name("ChunkContentsMiniZip2.txt"), ["scene\\a.modelbin", "scene\\b.modelbin", "c.pb"])

        code, out, _ = run(capsys, "list", path, "--filter", "scene")
        assert code == 0
        assert "2 entries matching 'scene'" in out
        assert "lz4" in out and "stored" in out

        target = tmp_path / "out" / "b.modelbin"
        code, out, _ = run(capsys, "extract", path, "scene\\b.modelbin", "--out", target)
        assert code == 0 and target.read_bytes() == payloads[1]

    def test_a_minizip_without_names_by_number(self, capsys, tmp_path, minizip):
        path, payloads = minizip

        code, out, _ = run(capsys, "list", path)
        assert code == 0 and "#2" in out and "deflate" in out

        target = tmp_path / "third.bin"
        assert run(capsys, "extract", path, "#2", "--out", target)[0] == 0
        assert target.read_bytes() == payloads[2]

    def test_a_manifest_that_does_not_belong_is_refused(self, capsys, minizip):
        path, _ = minizip
        build_contents(path.with_name("ChunkContentsMiniZip2.txt"), ["only.modelbin"])

        code, _, err = run(capsys, "list", path)

        assert code == 1 and "do not belong together" in err

    def test_an_iostore_container(self, capsys, tmp_path):
        big = bytes(range(256)) * 600  # more than one block
        utoc = write_container(tmp_path / "paks", "pakchunk0-Windows", {"Maps/Example.umap": big, "a.uasset": b"hello"})

        code, out, _ = run(capsys, "list", utoc)
        assert code == 0
        assert "2 entries" in out and "../../../acr/Content/Maps/Example.umap" in out

        target = tmp_path / "Example.umap"
        code, _, _ = run(capsys, "extract", utoc.with_suffix(".ucas"), "../../../acr/Content/Maps/Example.umap", "--out", target)
        assert code == 0 and target.read_bytes() == big

    def test_a_zip(self, capsys, tmp_path):
        path = level_zip(tmp_path / "example_level.zip")

        code, out, _ = run(capsys, "list", path, "--filter", "info")
        assert code == 0 and "deflate" in out and "levels/example_level/info.json" in out

        target = tmp_path / "info.json"
        assert run(capsys, "extract", path, "levels/example_level/info.json", "--out", target)[0] == 0
        assert target.read_text() == '{"title": "Example"}'

    def test_a_pak_and_a_vpk_as_before(self, capsys, tmp_path):
        pak = build_pak(tmp_path / "sample.pak", {"Content/notes.txt": b"fox" * 40}, compress={"Content/notes.txt"})
        vpk = build_vpk(tmp_path / "sample_dir.vpk", {"maps/example.nav": b"NAV" * 50})

        code, out, _ = run(capsys, "list", pak)
        assert code == 0 and "Zlib" in out and "../../../Content/notes.txt" in out
        code, out, _ = run(capsys, "list", vpk)
        assert code == 0 and "stored" in out and "maps/example.nav" in out

        target = tmp_path / "example.nav"
        assert run(capsys, "extract", vpk, "maps/example.nav", "--out", target)[0] == 0
        assert target.read_bytes() == b"NAV" * 50


class TestFailuresAreOneLine:
    """Each of these ended in a traceback once."""

    @staticmethod
    def one_line(err: str) -> bool:
        return "Traceback" not in err and len(err.strip().splitlines()) == 1

    def encrypted_pak(self, tmp_path):
        path = build_pak(tmp_path / "locked.pak", {"Content/a.txt": b"secret"})
        data = bytearray(path.read_bytes())
        # The footer is 221 bytes; its encrypted-index flag follows the key GUID.
        data[len(data) - 221 + 16] = 1
        path.write_bytes(bytes(data))
        return path

    def test_an_encrypted_pak_without_a_key(self, capsys, tmp_path):
        code, _, err = run(capsys, "list", self.encrypted_pak(tmp_path))

        assert code == 1 and self.one_line(err)
        assert "encrypted index" in err and "--key" in err

    def test_a_file_that_is_no_archive(self, capsys, tmp_path):
        path = tmp_path / "notes.txt"
        path.write_bytes(b"hello there " * 200)

        for verb in (["list", path], ["extract", path, "a.txt"]):
            code, _, err = run(capsys, *verb)
            assert code == 1 and self.one_line(err)
            assert "is not an archive list and extract read" in err

    def test_a_pak_variant_says_what_is_wrong_with_it(self, capsys, tmp_path):
        path = build_pak(tmp_path / "old.pak", {"a.txt": b"x"})
        data = bytearray(path.read_bytes())
        data[len(data) - 221 + 21] = 3  # the version
        path.write_bytes(bytes(data))

        code, _, err = run(capsys, "list", path)

        assert code == 1 and self.one_line(err) and "pak version 3" in err

    @pytest.mark.parametrize("key", ["not-hex", "0x1234", "zz" * 32])
    def test_a_key_that_is_not_one(self, capsys, tmp_path, key):
        path = build_pak(tmp_path / "sample.pak", {"a.txt": b"x"})

        code, _, err = run(capsys, "list", path, "--key", key)

        assert code == 2 and self.one_line(err) and "--key" in err

    def test_a_well_formed_key_is_accepted(self, capsys, tmp_path):
        path = build_pak(tmp_path / "sample.pak", {"a.txt": b"x"})

        assert run(capsys, "list", path, "--key", "0x" + KEY)[0] == 0

    def test_an_encrypted_iostore_container(self, capsys, tmp_path):
        utoc = write_container(tmp_path, "locked", {"a.uasset": b"x"})
        data = bytearray(utoc.read_bytes())
        data[80] |= 2  # the encrypted flag
        utoc.write_bytes(bytes(data))

        code, _, err = run(capsys, "list", utoc)

        assert code == 1 and self.one_line(err) and "encrypted" in err
