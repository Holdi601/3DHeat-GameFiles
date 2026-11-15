---
title: Czytniki archiwów
nav_order: 9
lang: "pl"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Czytniki archiwów {#archive-readers}

**Kontener** (albo archiwum) to jeden duży plik, w który gra upycha wiele plików. **CRC** albo skrót to krótki odcisk palca kilku bajtów: jeśli się zgadza, bajty zostały odczytane dobrze. **Ramka ograniczająca** to najmniejsze pudełko, w które mieści się model.

Pod poleceniami leżą czytniki kontenerów, których używają gry. Ich formaty są nieudokumentowane, poza VPK firmy Valve i plikiem `.cdae` z BeamNG, więc „obsługiwany” musi znaczyć **sprawdzony na prawdziwych plikach**, a nie „nie wywala się”. Każdy czytnik sprawdza się czymś, co format gwarantuje: skrótem, CRC, łańcuchem przesunięć, który musi się domknąć, albo zapisaną ramką ograniczającą. Gdy sprawdzenie nie przechodzi, czytnik odmawia z komunikatem zamiast zgadywać. Zły model wygląda jak dobry, dopóki nie postawi się go obok trasy.

| Czytnik | Moduł | Czyta | Nie czyta | Wywoływany przez |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | wersje 8-12: indeks, wpisy, bloki Zlib/Gzip/Oodle, AES z kluczem, który podasz | wersje przed 8, indeksy zawierające tylko skróty ścieżek, wpisy z listy przepełnienia, zawartość zasobów | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, sprawdzone na v8), pakiety zen, właściwości unversioned kilku klas komponentów, skompilowane siatki statyczne, tekstury, strumieniowane tekstury wirtualne | zaszyfrowane kontenery, pakiety versioned, siatki tylko Nanite, skeletal meshes, właściwości innych klas | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | bloki Oodle przez bibliotekę już zainstalowaną na komputerze | wszystko bez takiej biblioteki; nigdy nie jest dołączana | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` w formacie 22 i nowszym (Unity 2020 do 6000), pakiety `UnityFS`, nieskompresowane siatki, także `.resS` | formaty sprzed 2020, osadzone drzewa typów, skompresowane siatki, każda klasa poza `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | tabele `.toc` z drzewami DbObject i binarnymi tabelami sekcji, pakiety instalacyjne, położenia fragmentów, pakiety wbudowane i ich manifesty, partycje RIFF EBX, siatki MeshSet, mapa wysokości terenu, tekstury BC1/BC3/BC7 i ich bloki shaderów, umieszczenie grup statycznych modeli | tabele zaciemnione XOR, bliski kolor terenu i dziury w nim, mapy normalnych, alfa inna niż wycinanki | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | wersje 1 i 2, archiwa podzielone na części, dane preload, sprawdzenie CRC | zasoby skompilowane (`.vmdl_c`, `.vtex_c`), format siatki nawigacyjnej CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, bez kompresji), geometria `.modelbin`, próbki kolorów `.pb` (BC1, BC7, RGBA), rozmieszczenia `.pgeo`, skróty tekstur materiałów | inne formaty wierzchołków i indeksów, inne formaty tekstur, warstwy materiałów shaderów terenu | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` i `extract` (`.minizip`) |
| [Pliki BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | zamontowany system plików zip, sceny JSON i TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiały | siatki ze szkieletem i siatki nakładek, animowane sekwencje, proceduralna roślinność terenu | `course` (BeamNG), `identify` (zipy, `.cdae`, `.ter`), `list` i `extract` (zipy) |

## Zasady, których trzyma się każdy czytnik {#rules-every-reader-follows}

- **Żadnych kluczy w zestawie, żadnych odzyskiwanych.** Zaszyfrowane archiwum Unreal `.pak` otwiera się tylko kluczem `--key` podanym przez ciebie. Zaszyfrowany kontener IoStore jest odrzucany. Nic nie przeszukuje pliku wykonywalnego w poszukiwaniu klucza i nic nie czyta pamięci innego procesu. Zobacz [Zasady i licencje](rules-and-licences.md).
- **Żadnego zastrzeżonego kodu w zestawie.** Oodle ładuje się z gry albo silnika już zainstalowanego na komputerze.
- **Odmawiaj zamiast zgadywać.** Nieznana wersja, kodek, format wierzchołków albo tekstury kończy się konkretnym błędem, na przykład `texture format 42 has not been identified; refusing to guess`.
- **Tylko do odczytu.** Żaden czytnik nie zapisuje do folderu gry. Eksporty trafiają tam, gdzie wskażesz.

## Co znaczy „sprawdzone” {#what-verified-meant}

Liczby weryfikacji podane na tych stronach pochodzą z docstringów modułów. Zmierzono je na zainstalowanych grach, podczas pisania każdego czytnika. Testy syntetyczne (zob. [Rozwój](development.md)) przypinają układ pól, a testy na zainstalowanych grach powtarzają część sprawdzeń, gdy gra jest na komputerze, a pomijają je, gdy jej nie ma. Liczby, których nie objął test, nie były od tamtej pory sprawdzane ponownie.
