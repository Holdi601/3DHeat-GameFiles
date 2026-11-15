---
title: "Cititoare de arhive"
nav_order: 9
lang: "ro"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Cititoare de arhive {#archive-readers}

Un **container** (sau arhivă) este un singur fișier mare în care un joc împachetează multe fișiere. Un **CRC** sau un hash este o amprentă scurtă a unor octeți: dacă se potrivește, octeții au fost citiți corect. O **casetă de încadrare** (bounding box) este cea mai mică cutie din jurul unui model.

Sub comenzi se află cititoarele pentru containerele pe care le livrează jocurile. Formatele lor nu sunt documentate, în afară de VPK-ul Valve și `.cdae`-ul BeamNG, așa că „suportat” trebuie să însemne **verificat pe fișiere reale**, nu „nu s-a blocat”. Fiecare cititor se verifică singur față de ceva ce garantează formatul: un hash, un CRC, un lanț de decalaje care trebuie să se închidă, o casetă de încadrare stocată. Unde o verificare eșuează, cititorul refuză cu un mesaj, în loc să ghicească. Un mesh greșit arată la fel de bine ca unul corect, până îl puneți lângă traseu.

| Cititor | Modul | Citește | Nu citește | Se ajunge prin |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versiunile 8-12: index, intrări, blocuri Zlib/Gzip/Oodle, AES cu o cheie pe care o furnizați | versiunile dinainte de 8, indexuri doar cu hash de cale, intrări din lista de depășire, conținutul activelor | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, verificat pe v8), pachete zen, proprietăți neversionate pentru câteva clase de componente, mesh-uri statice compilate, texturi, texturi virtuale de streaming | containere criptate, pachete versionate, mesh-uri doar Nanite, proprietățile altor clase | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | blocuri Oodle printr-o bibliotecă deja existentă pe calculator | orice fără o asemenea bibliotecă; nu este inclusă niciodată | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22+ (Unity 2020 până la 6000), pachete `UnityFS`, mesh-uri necomprimate, inclusiv `.resS` | formate dinainte de 2020, arbori de tipuri încorporați, mesh-uri comprimate, orice clasă în afară de `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | tabele `.toc` DbObject și tabelele binare de secțiuni, pachete de instalare, locațiile bucăților, pachete inline și manifestele lor, partiții RIFF EBX, mesh-uri MeshSet, câmpul de înălțimi al terenului, texturi BC1/BC3/BC7 și blocurile lor de shader, plasarea grupurilor statice de modele | tabele obfuscate XOR, culoarea solului de lângă sol și golurile terenului, hărți de normale, alfa în afara decupărilor | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versiunile 1 și 2, arhive împărțite, date de preîncărcare, verificare CRC | active compilate (`.vmdl_c`, `.vtex_c`), formatul plasei de navigare CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, stocat), geometria `.modelbin`, mostrele `.pb` (BC1, BC7, RGBA), plasările `.pgeo`, hash-urile texturilor de material | alte formate de vertex și de index, alte formate de textură, straturile de material ale shaderului de teren | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` și `extract` (`.minizip`) |
| [Fișiere BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | sistemul de fișiere montat din zip-uri, scene JSON și TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiale | mesh-uri cu schelet și de decalcomanii, animații de secvențe, vegetație procedurală de sol | `course` (BeamNG), `identify` (zip-uri, `.cdae`, `.ter`), `list` și `extract` (zip-uri) |

## Reguli pe care le respectă fiecare cititor {#rules-every-reader-follows}

- **Nicio cheie livrată, niciuna recuperată.** O arhivă criptată se deschide doar cu o cheie pe care o dați dumneavoastră (Unreal `.pak`, `--key`). Un container IoStore criptat este refuzat. Nimic nu caută o cheie într-un executabil și nimic nu citește memoria unui alt proces. Vezi [Reguli și licențe](rules-and-licences.md).
- **Niciun cod proprietar inclus.** Oodle se încarcă din jocul sau motorul deja instalat pe calculator.
- **Refuză în loc să ghicească.** O versiune, un codec, un format de vertex sau de textură necunoscut ridică o eroare specifică, de exemplu `texture format 42 has not been identified; refusing to guess`.
- **Doar citire.** Niciun cititor nu scrie într-un folder de joc. Exporturile merg acolo unde spuneți dumneavoastră.

## Ce a însemnat „verificat” {#what-verified-meant}

Cifrele de verificare citate pe aceste pagini provin din docstring-urile modulelor. Au fost măsurate pe jocuri instalate, în timp ce fiecare cititor era scris. Testele sintetice (vezi [Dezvoltare](development.md)) fixează structura câmpurilor. Testele pe jocurile instalate repetă unele verificări atunci când jocul se află pe calculator și sar peste ele în caz contrar. Cifrele care nu sunt acoperite de un test nu au mai fost verificate din nou de atunci.
