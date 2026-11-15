---
title: "ForzaTech: `.minizip`, `.modelbin`, próbki, rozmieszczenia"
nav_order: 7
lang: "pl"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, próbki, rozmieszczenia {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon działa na ForzaTech, własnym silniku Turn 10. Te czytniki biorą tor z jego archiwów aż do pozycjonowanych, teksturowanych trójkątów. Dochodzi się do nich przez `course`, `courses` i `terrain` (zob. [Forza Horizon](course-forza-horizon.md)). `identify` rozpoznaje `.minizip` i gołe `.modelbin`, a `list` i `extract` biorą `.minizip`, po nazwach z pliku `ChunkContentsMiniZip<n>.txt` obok niego albo po numerze wpisu (`#12`).

| Format | Moduł |
|---|---|
| archiwa `.minizip` i ich listy nazw | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modele i teren `.modelbin` | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| próbki tekstur `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| pliki rozmieszczeń `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` i skróty tekstur materiałów | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| kafelki terenu według miejsca | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza trzyma też sporo zawartości w zwykłych archiwach ZIP w `media\`. Biblioteka `zipfile` Pythona je otwiera, a `forzatech.models_in_archive()` wypisuje ich wpisy `.modelbin`. Geometria toru jest w archiwach `.minizip`.

## `.minizip`: archiwum bez nazw {#minizip-an-archive-with-no-names}

Tor ma cztery archiwa `GeoChunk<n>.minizip`, każde po dziesiątki gigabajtów przy mapie open-world, z setkami tysięcy wpisów. **Archiwa nie przechowują żadnych nazw**: ani tabeli nazw, ani nagłówka na wpis, tylko numer porządkowy. Nazwy są w `ChunkContentsMiniZip<n>.txt` obok każdego archiwum, jedna linia na wpis w kolejności wpisów (`<build path>zipcache\pc\<path>|<bundle>`). To jedyny sposób, by poprosić o plik. Wszystko do `zipcache\pc\` jest odrzucane, a wyszukiwania ignorują wielkość liter.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Trzy szczegóły indeksu nadal dają wynik, gdy odczyta się je źle. Czytnik obsługuje wszystkie trzy poprawnie:

| Szczegół | Co robi niedbały czytnik | Jak to wygląda |
|---|---|---|
| baza segmentu ma **64 bity** | czyta ją jako u32 plus wypełnienie | poprawne przez pierwsze 4 GB, potem szum o właściwej długości |
| baza jest wyrównana do **8 bajtów** | ignoruje słowo wypełnienia za tabelą pakietów | w archiwach z parzystą liczbą pakietów każdy wpis deklaruje kodek, którego nie ma |
| zapisana długość wpisu to odstęp do następnego wpisu (albo bazy następnego segmentu) **minus jego wypełnienie** (bity flag 12-13) | bierze cały odstęp | LZ4 odmawia bloku w całości |

Kodeki to pięć najniższych bitów flag: `0x00` bez kompresji, `0x08` surowy deflate, `0x1F` blok LZ4. Każdy inny jest odrzucany. Każdy wpis musi rozpakować się do dokładnie zadeklarowanego rozmiaru, inaczej jest odrzucany. Indeks (około 5 MB) czyta się raz, a ładunki czyta się przez przeszukiwanie.

Nagłówek jest sprawdzany: magiczne bajty, nagłówek 32-bajtowy i liczba segmentów zgodna z `ceil(entries / per segment)`.

**Sprawdzone:** wpisy próbkowane w każdym archiwum mapy, każdy rozpakowuje się do dokładnie zadeklarowanej długości przy każdym z trzech kodeków.

## `.modelbin`: kontener chunków {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Zadeklarowany rozmiar pliku musi równać się rzeczywistemu.
- **Łańcuch**: każdy chunk zaczyna się tam, gdzie skończył się poprzedni, zaokrąglone w górę do 4 bajtów. Nic w pliku tego nie mówi, więc jest to dowód: rekord czytany ze złym krokiem tego nie wytwarza. Trzymało się dla wszystkich 252 próbkowanych modeli.
- Plik `PGZP` podany czytnikowi modeli jest nazwany jako "a ForzaTech .minizip archive, not a model" i wskazuje na `minizip.py`, zamiast być odrzucony bez słowa.

Geometrię czyta się z tych chunków:

| Chunk | Zawiera |
|---|---|
| `VLay` | układ wierzchołków: nazwy atrybutów, potem elementy (indeks nazwy u16, kanał u16, bufor, format DXGI, przesunięcie); liczba elementów to u16 |
| `VerB` | bufor wierzchołków za 16-bajtowym nagłówkiem (liczba, rozmiar, krok u16, atrybuty u16, format) |
| `IndB` | bufor indeksów, ten sam nagłówek |
| `Mesh` | jedna podsiatka: materiał, maska poziomu szczegółowości, zakres indeksów, układ, bufor, krok, tabela wariantów i pudełko pozycji na końcu |
| `MatI` | instancja materiału: jej ścieżka `.materialbin` i skróty tekstur |

### Pozycje i pudełko {#positions-and-the-box}

Pozycje to `R16G16B16A16_SNORM` (format 13): cztery znakowe shorty na wierzchołek. `position = short / 32767 * scale + bias`, gdzie scale i bias to ostatnie 32 bajty chunku `Mesh` (dwa float4). Bias jest we **współrzędnych świata gry**, więc kafelek terenu ląduje tam, gdzie gra go umieszcza, bez transformacji instancji. Dlatego do pobrania kawałka mapy wystarcza linia telemetrii. Każda podsiatka modelu niesie to samo pudełko (sprawdzono na 860 z nich).

### Układ wierzchołków {#the-vertex-layout}

Jeden bufor pozycji obejmuje każdy wierzchołek. Pozostałe atrybuty są podzielone na kolejne grupy wierzchołków, każda z własnym buforem i własnym układem: droga przy skrzyżowaniu niesie trzy zestawy UV i dwie tangenty, a bank obok tylko normalną. Wszystkie atrybuty poza pozycją mają po cztery bajty. Który układ opisuje który bufor, ustala się z podsiatek, które z niego rysują, bo układy i bufory nie są w tej samej kolejności (taka sama, przesunięta o jeden albo przemieszana, zależnie od modelu).

| Format DXGI | Kod | Używany do |
|---|---|---|
| R16G16B16A16_SNORM | 13 | pozycja (czwarty short to x normalnej) |
| R16G16_SNORM | 37 | normalna y, z |
| R16G16_UNORM | 35 | para UV (kanał = który zestaw) |
| R8G8B8A8_UNORM | 28 | kolor albo wagi mieszania |
| R10G10B10A2_UNORM | 24 | tangenta (nie dekodowana) |
| R16_UINT | 57 | indeksy |

**Normalna jest podzielona.** `NORMAL` przechowuje y i z. X to czwarty short pozycji, który wyglądał na wypełnienie. Przy setkach tysięcy wierzchołków terenu koreluje on +0,92 z x normalnej trójkąta i z niczym innym. Dzięki niemu 96% wierzchołków na zboczu leży w granicach 18° od obliczonej normalnej. Każde kodowanie z dwoma składowymi wypróbowane bez niego (oktaedryczne we wszystkich 48 ustawieniach też) dawało dobre y i z, a złe x.

Inne formaty pozycji i indeksów są **odrzucane** ("only 13 (four shorts, scaled) is implemented"; "only unsigned shorts are implemented").

### Podsiatki {#submeshes}

Rekord `Mesh` ma w standardowej postaci 238 bajtów. Dłuższe niosą na początku dłuższą tabelę **wariantów** materiału, 238 + 8 x count - 4 bajty, a każde pole po niej przesuwa się o dokładnie tyle. Krótsze (218 bajtów, część terenu) zachowują przesunięcia. Każdy wpis wariantu to `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. Maska poziomu szczegółowości to u16, jeden bit na poziom, od bitu 1.

Nic nie jest ufane samo w sobie. Zakresy indeksów muszą dokładnie pokryć bufor indeksów, każde `index count` musi równać się 3 x `triangles`, a krok, który podaje podsiatka, musi być krokiem jej bufora. Tabela, która nie przechodzi, jest odrzucana w całości, bo etykietowanie trójkątów z błędnie odczytanych pól jest gorsze niż ich brak. Wśród tysięcy próbkowanych podsiatek każda, której indeks bufora jest w zakresie, przechodzi.

### Materiały i skróty tekstur {#materials-and-texture-hashes}

`MatI` nazywa swój materiał ścieżką `Game:...\x.materialbin`, znalezioną przez przeszukanie chunku. Jego tekstury to rekordy `u32 slot, u32, u32 hash` co 33 bajty i bez wyrównania, więc chunk przeszukuje się od każdego bajtu offsetu w poszukiwaniu słów, które są znanymi skrótami tekstur. Te pochodzą z `AssetManifest.xml` toru (`<Texture Source="...\name.swatch" SourceHash="...">`, czytane do `</Textures>`). Slot `0x88B483AA` to kolor bazowy standardowego shadera. Jak potem wybiera się teksturę koloru, opisano na [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: próbki tekstur {#pb-texture-swatches}

Próbka to ten sam kontener `burG` co model: nagłówek `HCXT` o długości 96 bajtów od bajtu 44, potem jeden chunk pikseli. Nagłówek zawiera GUID tekstury (ten z jej nazwy pliku), szerokość i wysokość, liczbę mipów oraz **kod formatu w bajcie 72** (własna numeracja ForzaTech). Bajt 84 to liczba bajtów pikseli.

| Kod | Format | Rozpoznany jako |
|---|---|---|
| 0 | BC1, pół bajta na piksel | dekoduje się jako czerwono-biały krawężnik (szum pod BC4) |
| 9 | BC7, jeden bajt na piksel | dekoduje się jako kafelek terenu z widocznym torem |
| 13 | RGBA8, cztery bajty na piksel | zwykły |
| inne | odrzucany | "texture format N has not been identified; refusing to guess" |

Formaty ustalono przez dekodowanie prawdziwych plików na każdy sposób, na jaki pozwala rozmiar ładunku. Bajt 47, który wcześniejsza wersja brała za format, to 4 we wszystkich próbkowanych teksturach. Dekoduje się tylko górny mip pliku. Każda rozdzielczość to osobny wpis, `<name>_<guid>_quality<n>.pb`, jakość 1 najmniejsza, 5 największa. Dla map terenu dwie największe są w innym archiwum niż reszta. Dekodowanie idzie przez dekoder BCn Pillow, przez wygenerowany nagłówek DDS.

## Pliki rozmieszczeń (.pgeo) {#placement-files-pgeo}

Jeden plik na kategorię i komórkę przestrzenną: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Sama ścieżka podaje kwadrat komórki i kategorię, więc pliki można filtrować, nie otwierając ich.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Jak ustalono każde pole:

| Pole | Ustalone przez |
|---|---|
| pozycja to stałoprzecinkowe 16.16, a nie ułamek pudełka | kolejne bariery są dokładnie 4,000 m od siebie (długość modelu) |
| znak-moduł, nie dopełnienie do dwóch | dopełnienie do dwóch wrzucało ujemne współrzędne dziesiątki kilometrów poza mapę; z bitem 31 jako znakiem każdy rekord każdej kategorii próbkowany trafia w pudełko swojego pliku |
| wektory to własne osie modelu | koniec każdej bariery trafia w początek następnej: 93,5% w granicach 5 cm, mediana 0,000 m |
| bajt 60 to wariant | pięć kopii pachołka czyta 0, 2, 2, 3, 4, podczas gdy każda bariera czyta 0 |

Tylko nazwy kończące się na `_3D` to rekordy modeli. Tabela wariantów przed nimi wymienia nazwy bez tego przyrostka i odczytane jako rekordy trafiałyby w nieskończoność. Kandydujący rekord jest przyjmowany tylko wtedy, gdy jego liczba mieści się w pliku, a instancje z liczbami niebędącymi skończonymi są odrzucane.

## Nieobsługiwane {#not-implemented}

- Formaty wierzchołków i indeksów inne niż wyżej (odrzucane).
- Formaty tekstur inne niż 0, 9, 13 (odrzucane).
- Tangenty (przeczytane i pominięte, nie używane).
- Warstwy materiałów shadera terenu. Tekstura podłoża to interpretacja map kafelków (zob. [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
