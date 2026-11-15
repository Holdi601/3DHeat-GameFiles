---
title: Unreal 5 IoStore
nav_order: 2
lang: "pl"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 dostarcza większość zawartości w kontenerach **IoStore**: spisie `.utoc` i danych `.ucas`, które on indeksuje. `.pak` nadal tam jest, ale zawiera niewiele więcej niż stopkę. Czytniki tutaj schodzą od kontenera do geometrii i pikseli, na tyle, na ile potrzebuje tego trasa. Zbudowano je i sprawdzono na Assetto Corsa Rally (Unreal 5.6.1, zmodyfikowany), dochodzi się do nich przez eksport trasy [Assetto Corsa Rally](course-assetto-corsa-rally.md), a `identify`, `list` i `extract` biorą `.utoc` (albo `.ucas` obok niego): pliki, które nazywa jego katalog, po ich ścieżce pod punktem montowania. Kontener bez indeksu katalogów nie nazywa plików i nie jest wyświetlany.

| Warstwa | Moduł |
|---|---|
| kontenery i magazyn | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| zapieczone pakiety „zen” | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| dane właściwości unversioned | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| siatki statyczne | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| tekstury i tekstury wirtualne | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Kontenery (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Spis treści, wersja 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Wersje starsze niż 5 są odrzucane. Tylko wersja 8 była sprawdzona na prawdziwych plikach.
- **Zaszyfrowane kontenery są odrzucane**: "<file> is encrypted. This tool holds no keys and recovers none." Dla IoStore nie da się podać żadnego klucza.
- Metody bloków: bez kompresji, `oodle` (przez [Oodle](reader-oodle.md)), `zlib`, `lz4`. Każda inna jest odrzucana.
- Partycje poza pierwszą leżą w `<name>_s<n>.ucas`.

**Magazyn** otwiera każdy `.utoc` w folderze `Paks` gry i indeksuje każdą ścieżkę pakietu, bez względu na wielkość liter. Kontenery, których nie da się otworzyć, są pomijane. `global.utoc` dostarcza obiekty skryptowe (klasy C++). Dane bulk pakietu (`.ubulk`) znajduje się jako chunk o tym samym identyfikatorze i typie `BULK_DATA`, w tym kontenerze, który go trzyma.

Sprawdzono: każdy kontener zainstalowanej gry i każdą ścieżkę pakietu w nim.

## Pakiety zen {#zen-packages}

Zapieczony pakiet to nagłówek (nazwy, importy, eksporty, pakiety eksportów, tabele zależności, nazwy importowanych pakietów), za którym idą serializowane dane każdego eksportu. Obiekty odwołują się do siebie przez 64-bitowy `FPackageObjectIndex`, którego dwa najwyższe bity mówią, czym jest: eksportem tego pakietu, obiektem skryptowym, importem z innego pakietu (który pakiet i eksport po haszu jego ścieżki) albo null.

- Układ podsumowania zmienił się w 5.3 (pakiety zależności i nazwy importowanych pakietów) i ponownie w 5.6 (dwa dodatkowe przesunięcia). Próbuje się obu układów i zachowuje ten, którego tablica nazw się parsuje, więc wersji nie trzeba znać.
- Pakiety **versioned** (w stylu nieskompilowanym) są odrzucane.
- Nazwy importowanych pakietów mają numer. Pakiet `_Terrain` z numerem 1 to plik `_Terrain_0`.
- Nazwy `/Game/...` mapują się na folder `Content` projektu w magazynie.
- Odwołania między pakietami śledzi się przez dopasowanie publicznego haszu eksportu.

Sprawdzono: każda komórka każdego etapu się otwiera.

## Właściwości unversioned {#unversioned-properties}

Zapieczone eksporty Unreal 5 nie nazywają swoich właściwości. Eksport zaczyna się nagłówkiem serii, „pomiń tyle slotów, potem tyle obecnych”, oraz maską mówiącą, które obecne są zerowe i nie mają bajtów. Wartości idą w kolejności właściwości klasy. Odczyt tego wymaga **schematu** każdej klasy: jej listy właściwości, w dokładnie takiej kolejności, w jakiej buduje ją silnik (własne właściwości najpierw, potem rodzica, jeden slot na każdy element tablicy statycznej, bez właściwości tylko edytorskich).

Schematy są wbudowane dla klas, których potrzebuje trasa:

| Klasa | Łańcuch |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | łańcuchy ISM (obecne, ale nieużywane przez eksport trasy, bo ta wersja je przearanżowała) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Obejmują też struktury, które one trzymają (`FBodyInstance`, odpowiedzi kolizji i inne). Typy wartości czyta się według kodowania: liczby o stałym rozmiarze i wektory (`FVector`, `FRotator` jako double, `FTransform`...), `FName`, enumy (jeden bajt), referencje do obiektów (indeks pakietu `i32`), miękkie ścieżki obiektów, tablice, zagnieżdżone struktury i delegaty multicast (pomijane).

Schematy zawierają **tylko nazwy i typy właściwości**, wyprowadzone z nagłówków Unreal Engine 5.6.1 (które Epic udostępnia każdemu z połączonym kontem). Nie ma w nich kodu silnika. Ten build ma **dwa dodatkowe sloty w `UPrimitiveComponent`** w porównaniu z nagłówkami oraz **jeden dodatkowy w objętości tekstury wirtualnej**, znalezione z danych i oznaczone `(unknown)`. Wartość obecna w jednym z tych slotów to błąd, a nie zgadywanie. Slot za końcem schematu albo nieznany typ zgłasza `PropertyError`.

Sprawdzono: każdy komponent statycznej siatki i sceny każdego etapu się dekoduje, a każdy kończy się dokładnie na stałym natywnym ogonie swojej klasy. Łatka gry może przesunąć sloty. Czytnik wtedy zgłasza błąd, a eksport podaje, ile komponentów się nie udało.

## Siatki statyczne {#static-meshes}

Eksport `UStaticMesh` to jego właściwości, po których idą dane natywne. Właściwości nie są potrzebne do geometrii i nie są czytane. Część natywną znajduje się po jej stałym początku: zerowa flaga GUID, dwa bajty flag pasków, `bCooked = 1` i indeks własnego eksportu `BodySetup` siatki. Potem czyta się ją w kolejności, w jakiej `UStaticMesh::Serialize` i `FStaticMeshRenderData::Serialize` zapisują ją dla **zapieczonej, nie-Nanite** siatki:

- do 16 poziomów szczegółowości, każdy z sekcjami (materiał, pierwszy indeks, liczba trójkątów), granicami i, gdy są **wbudowane**: bufor pozycji (float32 x 3), tangenty, UV (wszystkie kanały, połówkowa albo pełna precyzja), kolory i bufor indeksów (16- albo 32-bitowy);
- co idzie dalej (odwrócone i tylko-głębokościowe bufory indeksów, dane ray-tracingu, próbniki z wagą powierzchni) jest pomijane, by dojść do następnego poziomu.

Poziom, który nie jest przechowywany wewnątrz, kończy listę. Siatka bez żadnego jest odrzucana. Pozycje są Unrealowe: centymetry, X do przodu, Y w prawo, Z w górę.

Sprawdzono: prawie każda próbkowana siatka się dekoduje (reszta to szkieletowe), a zasięg zdekodowanego kafelka drogi zgadza się z granicami, które przechowuje.

## Tekstury {#textures}

Eksport `Texture2D` to jego właściwości, a potem jego zapieczone dane platformy: nazwa formatu pikseli, rozmiar i tabela poziomów mip, każdy wskazujący na **mapę danych bulk** pakietu (przesunięcie, rozmiar, flagi; wbudowane w eksport, gdy ustawiona jest flaga `0x40`, a w przeciwnym razie w `.ubulk`). Dane platformy znajduje się po ich własnym kształcie, a nie przez pomijanie właściwości, więc układ właściwości klasy tekstury nie ma znaczenia. Dekoduje się pierwszy mip nie większy niż żądany rozmiar.

| Format Unreal | Dekodowany jako |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | RGBA 8-bitowe |
| `PF_G8` | szarość 8-bitowa |

Sprawdzono: zdjęcie satelitarne DXT5 4096 px, którego trzynaście poziomów mip dokładnie równa się rozmiarom wpisów bulk.

## Strumieniowane tekstury wirtualne {#streaming-virtual-textures}

Zapieczona `VirtualTexture2D` to kwadratowe kafelki z obramowaniem, dla każdego poziomu szczegółowości, adresowane **kodem Mortona** (x w bitach parzystych), przechowywane w chunkach danych bulk pakietu. Układ czyta się tak, jak zapisuje go `FVirtualTextureBuiltData::Serialize` w Unreal 5.6: warstwy, rozmiar kafelka, obramowanie, tablice adresów kafelków dla każdego mipa, formaty warstw i chunk *n* jako wpis bulk *n*. Region tekstury składa się kafelek po kafelku, z usuniętymi obramowaniami, z poziomu, którego rozdzielczość jest najbliższa żądanemu rozmiarowi. Czyta się tylko pierwszą warstwę i tylko w formatach wymienionych wyżej.

Sprawdzono: kafelki chunku tekstury wirtualnej są rozliczone co do bajta.
