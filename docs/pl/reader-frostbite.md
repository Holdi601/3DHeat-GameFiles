---
title: Frostbite
nav_order: 5
lang: "pl"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, paczki, siatki i poziomy {#frostbite-toc-cas-bundles-meshes-and-levels}

**Czyta poziom Battlefield 6 aż do jego terenu, umieszczonych siatek i ich map kolorów
i zapisuje go jako `.glb`.** Gry Frostbite (Battlefield, Need for Speed, Dead Space)
trzymają swoją zawartość w blobach `.cas`, opisanych przez tabele spisu treści `.toc`.
Tabela poziomu mówi, które paczki (bundle) ładuje poziom, paczki nazywają każdy zasób,
a zasoby mówią, która siatka gdzie stoi.

Źródła:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabele, pakiety, ładunki),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(paczki i ich manifesty),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(partycje EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(mapa wysokości),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(tekstury i materiały),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(rozmieszczenie i eksport).
Polecenia: `identify`, `levels`, `level` (zobacz [Polecenia](commands.md#levels-and-level-frostbite)).

Gra niczego z tego nie dokumentuje. Każdy poniższy układ został odczytany z plików,
a potem sprawdzony na wszystkich z nich, i każda sekcja mówi, jak wyglądało sprawdzenie.
Tam, gdzie opisy Frosty opisują starsze wersje struktury, nazwy pól idą za ich nazwami;
nie wzięto żadnego kodu z tamtych narzędzi (zobacz [Zasady i licencje](rules-and-licences.md)).

## Nagłówek, który wygląda na zaszyfrowany, a nie jest {#the-header-that-looks-encrypted-and-is-not}

| Magia (u32, little-endian) | Znaczenie | Obsługa |
|---|---|---|
| `0x00CED100` | zwykły: drzewo zaczyna się od razu | czytany |
| `0x01CED100` | podpisany: 556-bajtowy podpis, potem drzewo **jawnie** | czytany |
| `0x03CED100` | XOR-zaciemniony, z kluczem w nagłówku pliku | wykryty i odrzucony |

Postać podpisana to ta, którą dostarcza obecne Battlefield. Gęste bajty po magii to
podpis, a nie szyfrogram.

## Drzewo DbObject {#the-dbobject-tree}

Jedna rekurencyjna struktura. Każde pole to bajt typu (dolne pięć bitów to typ, bit 7
„anonimowe”), opcjonalna nazwa i wartość. Kontenery niosą swoją długość jako liczbę
o zmiennej długości i kończą się zerowym bajtem. `parse_toc` sprawdza długość każdego
kontenera, więc plik, który się parsuje, został zrozumiany. `layout.toc` ma tę postać.

## Pakiety instalacyjne {#installation-packages}

Każda lokalizacja podaje **pakiet instalacyjny**, do którego należy jej blob. Każdy
pakiet numeruje swoje bloby od `cas_01`, więc sam numer bloba jest dwuznaczny, gdy
zainstalowanych jest więcej niż jeden pakiet, a zawsze są.

- `layout.toc` wymienia pakiety pod `installManifest.installChunks`, każdy z
  `persistentIndex` i `installBundle`, na przykład `Win32/installation/<package>`.
- Bloby pakietu leżą w tym folderze, pod `Data` dla gry podstawowej albo pod
  `Update/<pack>/Data` dla tego, co przyszło później.
- Rekord lokalizacji niesie pełne 32-bitowe `persistentIndex`: dolna połowa pierwszego
  słowa trzyma górną połowę, górna połowa drugiego słowa trzyma dolną połowę; dolna
  połowa drugiego słowa to numer bloba.

Sprawdzenie: każda lokalizacja w każdej binarnej tabeli instalacji rozwiązuje się do
zadeklarowanego pakietu i mieści się w blobie, który nazywa. Wcześniejsza wersja brała
pierwszy `cas_NN.cas` o właściwym numerze. Jedna trzecia ładunków, które czytała, wyglądała
wtedy na gęsto upakowaną i brana była za szyfrowanie. Miały właściwe przesunięcia w złym
pliku. Nic znalezionego nie jest zaszyfrowane.

## Tabela poziomu {#the-level-table}

Tabela poziomu (`levels/<level>/<level>.toc`) to tabela sekcji: piętnaście nagłówkowych
słów big-endian, potem sekcje ułożone jedna po drugiej, których przesunięcia są
podane wprost i dają się wyliczyć z dwóch liczb.

| Sekcja | Zawartość |
|---|---|
| paczki | tablica haszy (jedno słowo na paczkę), potem rekord 16 bajtów na paczkę: klucz, `0x40000000` \| rozmiar, 0, przesunięcie |
| tablica haszy fragmentów | jedno słowo na fragment |
| fragmenty | 16-bajtowy identyfikator (GUID fragmentu **z odwróconą kolejnością bajtów**), potem słowo: `0x80000000` \| 4 x indeks jego lokalizacji |
| lokalizacje | cztery słowa big-endian: pakiet (podzielony), blob, przesunięcie, rozmiar |

Identyfikatory fragmentów i lokalizacje są **w różnej kolejności**. Czytanie ich w
kolejności pliku paruje każdy fragment z bajtami innego fragmentu, które dekodują się
dobrze (głównie jako dźwięk) i dlatego nie wyglądają źle, dopóki siatka nie wyjdzie
jako szum. Sprawdzenie: w poziomie słowa indeksów są permutacją liczb od 0 do liczby
fragmentów minus jeden.

Paczki leżą w linii za tabelą sekcji. Każda ma dziewięć nagłówkowych słów big-endian,
potem swoje wpisy: osiem bajtów przesunięcia i rozmiaru, poprzedzone jeszcze ośmioma
bajtami nazywającymi pakiet i blob, gdy bajt flagi wpisu ma ustawiony najwyższy bit.
Sprawdzenie: w każdej paczce ostatni wpis kończy się dokładnie tam, gdzie zaczynają się
bajty flag.

### Która tabela to poziom {#which-table-is-the-level}

Poziom może mieć kilka tabel o tej samej nazwie: jedną w `Data` gry podstawowej, po
jednej w każdej aktualizacji (`Update/<pack>/Data`), która go dostarcza lub zmienia, i po
jednej w każdym pakiecie wysokiej rozdzielczości
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Tylko niektóre zawierają
paczki. Dla poziomu, który dostarcza aktualizacja, tabela w grze podstawowej zawiera
tylko fragmenty i żadnych paczek, a poziomem jest ta z aktualizacji; wzięcie pierwszej
znalezionej tabeli nie wyeksportowało z niego niczego.

Poziomem jest więc tabela z największą liczbą paczek, a w remisie wygrywa późniejsza
warstwa (najpierw gra podstawowa, potem aktualizacje w kolejności nazw). Tabele o tej
samej nazwie bez paczek są jego **uzupełnieniami**: ich fragmenty są dodawane do fragmentów
poziomu, bo trzymają największe mipy jego tekstur. Nagłówek tekstury nazywa taki fragment
pod przesunięciem +164 (zobacz [Tekstury i materiały](#textures-and-materials)).
`levels` wypisuje, skąd pochodzi każdy poziom i ile ma uzupełnień.

## Manifesty paczek {#bundle-manifests}

Pierwszy wpis paczki to jej manifest, zapisany bez kompresji. To binarny format paczek
z wcześniejszych gier Frostbite, z nową magią `0xD68E799D`: liczniki, SHA-1, rekordy ebx
i res (przesunięcie nazwy i rozmiar), typy res, metadane i identyfikatory, GUID-y
fragmentów, ciągi znaków. Pozostałe wpisy paczki to ebx, res i fragmenty, w tej kolejności.
Sprawdzenie: liczniki zgadzają się z wpisami w każdej paczce, a ciągi zaczynają się tam,
gdzie kończą się rekordy.

Typy zasobów to hashe. `0x49B156D4` to MeshSet (każdy res tego typu nazywa się
`..._mesh`), `0x6BDE20BA` to Texture, `0x22FE8AC8` to TerrainStreamingTree.

`LevelCatalogue` czyta to wszystko dla jednego poziomu w kilka sekund: poziom ma
dziesiątki paczek i dziesiątki tysięcy ebx, res i fragmentów.

## Bloki ładunku {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Zerowy rozmiar skompresowany oznacza zapisane bez kompresji, o ile po rozpakowaniu
daje to tyle samo.

| Słowo metody | Kodek |
|---|---|
| `0x0070`, `0x0071` | brak |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), z własnej biblioteki DLL `oo2core` gry) |
| inne, z równymi rozmiarami | skopiowane tak, jak zapisane |
| inne | odrzucone |

Czytane z właściwego pakietu, każdy próbkowany ładunek się dekoduje.

## Partycje EBX {#ebx-partitions}

EBX trzyma wszystko, co nie jest surowymi danymi. Każda partycja to plik RIFF:
`EBXD` (dane, wyrównane do 16), `EFIX` (GUID partycji, GUID-y typów i sygnatury,
instancja, wskaźnik, przesunięcia importów i informacji o typach, importy oraz
przesunięcia tablic, wartości w pudełkach i ciągów), `EBXX` (tablica tablic:
przesunięcie, liczba, hasz, flagi, typ elementu). Pole wskaźnika ma osiem bajtów:
zero to null, nieparzysta wartość to numer importu `value >> 1`, cokolwiek innego jest
względne wobec pola.

**Biblioteka typów nie jest czytelna.** Gra trzyma ją w swoim początkowym systemie plików,
który jest zaszyfrowany, a ten pakiet go nie rusza. Typy rozpoznaje się po GUID i
sygnaturze, które niesie każda partycja, a kilka typów potrzebnych eksportowi poziomu
rozpisano na podstawie samych danych.

## MeshSet {#meshset}

Siatka to res MeshSet (opis) i jeden fragment na poziom szczegółowości (bufory).

| Część | Układ |
|---|---|
| prefiks | cztery słowa: rozmiar nagłówka (176 albo 192), rozmiar rekordu poziomu (176 do 188), rozmiar rekordu sekcji (368), 0 |
| nagłówek | pudełko ograniczające; sześć przesunięć poziomów typu i64; typ siatki pod `0x6C` (sztywna, szkieletowa, złożona); liczby poziomów i sekcji pod `0x9C` |
| poziom | sekcje pod `+0x08`; pięć list rysowania pod `+0x14` (nieprzezroczyste, przezroczyste, dekale, tylko głębia, cień); format indeksów `+0x54` (`0x21` u16, `0x2E` u32), bajty indeksów i wierzchołków; GUID fragmentu pod `+0x74` |
| sekcja | nazwa materiału; krok wierzchołka; trójkąty, pierwszy indeks, przesunięcie wierzchołka (w bajtach), liczba wierzchołków pod `+0x20`; deklaracja wierzchołków pod `+0x64`: 16 x (użycie, format, przesunięcie, strumień), 16 kroków strumieni, liczniki |
| fragment | bufor wierzchołków, potem bufor indeksów. Strumienie sekcji idą jeden za drugim, a indeksy liczą od pierwszego wierzchołka sekcji |

Pozycje to użycie 1, strumień 0, przesunięcie 0, jako cztery półliczby albo trzy
liczby zmiennoprzecinkowe. Rysowane są tylko sekcje nieprzezroczyste i przezroczyste.
Każda sekcja nazwana `..._shadow` jest na liście cieni i tylko na niej, więc decydują listy.

Sprawdzenie: każda siatka poziomu, którego poziomy są zapisane we fragmentach, się
dekoduje, a prawie wszystkie mają 99% lub więcej wierzchołków w swoim zadeklarowanym
pudełku; reszta chybia o zaokrąglenie półprecyzji. Odkodowana skrzynka ma około metra,
Y w górę, a jej normalne wskazują na zewnątrz.

## Rozmieszczenie {#placement}

Potok treści zbiera statyczne obiekty każdego pod-świata w **grupę modeli statycznych**:
tablicę członków, po jednym na siatkę, każdy z przekształceniami swoich instancji.

| Typ (GUID, sygnatura) | Układ |
|---|---|
| członek `ad13064e…`, `0xF861A878` | 224 bajty: `+88` tablica przekształceń, `+112` plan obiektu (import), `+160` zasób siatki (import) |
| przekształcenie `101dce06…`, `0x5E6D8C37` | 64 bajty: prawo, góra, przód, przesunięcie, każdy wektor vec3 dopełniony do 16 |

Partycja zasobu siatki nazywa się tak jak jej res MeshSet, więc GUID partycji importu
podaje siatkę. Punkt ląduje w `x·right + y·up + z·forward + translation`. Przekształcenie
samej grupy było tożsamością w każdej grupie sprawdzonych poziomów i nie jest stosowane.

Sprawdzenie: w poziomie każdy członek każdej grupy rozwiązuje się do siatki; większość
kopii ma rotację o wyznaczniku 1 z dokładnością do tysięcznej, reszta jest skalowana albo
odbita lustrzanie. GUID-y typów i sygnatury są takie same w innych poziomach. Aktualizacja
gry, która zmienia układ, zmienia sygnaturę, a czytnik wtedy nic nie znajduje, zamiast
czytać źle.

### Obiekty umieszczone pojedynczo {#objects-placed-one-by-one}

To, czego potok nie potrafi zgrupować (obiekty do zniszczenia, kontenery, odłamki), jest
umieszczane przez **odwołania do obiektów** i **odwołania do prefabów** w partycjach poziomu:

| Typ (GUID, sygnatura) | Układ |
|---|---|
| odwołanie do obiektu `a9a6a6ad…`, `0xC4856BEC` | `+32` przekształcenie (jak wyżej), `+112` plan obiektu (import) |
| odwołanie do prefabu `117c746e…`, `0xDE3FE9B4` | to samo; plan to prefab, czyli partycja dalszych odwołań |

Prefaby się zagnieżdżają; kopia ląduje w swoim przekształceniu pomnożonym przez
przekształcenie rodzica (wektory wierszowe), do ośmiu poziomów w głąb. Plan obiektu
rysuje się jako siatki, które importuje, z pominięciem stanów po zniszczeniu (`dc_...`).
Zgrupowany prefab jest przywoływany jako jego reszta `..._nongroupable_autogen`, więc
nic nie jest rysowane dwa razy.

Przejście zaczyna się tylko od światów i warstw poziomu. Partycja, której pierwszą
instancją jest plan prefabu (`134919fc…`, `0x0247807D`), to definicja prefabu, a poziom
trzyma ich wiele we własnym folderze, umieszczanych przez jego światy innymi sposobami
niż te odwołania; przejściu traktującemu ją jak świat prefab wkłada swoją zawartość
w jej współrzędne lokalne. To piętrzy setki kopii wokół początku świata, daleko pod ziemią.
Światy i warstwy mają na początku `a10ebe0f…`, `0xD3D16C3C`.

Plany wycofane z gry nie są śledzone: zasoby deweloperskie i testowe (`game/dev/`,
`test/`), zestaw sceny końcowej rundy (`..._gameend_...`: ustawiony pod ziemią)
oraz kontroler kamery śmierci (`.../deathflow/...`, którego gadżety stoją w początku
świata). Rozpoznaje się je po ścieżce zasobu, a nie po warstwie: ta sama warstwa, która
trzyma zestaw sceny końcowej, może umieszczać prawdziwe ściany i dachy poziomu. Po
obu regułach żadna kopia w sprawdzonych poziomach nie leży więcej niż 10 m pod terenem,
a kopie stoją na terenie tam, gdzie gra je pokazuje.

**Poziomy szczegółowości zastępujące.** Ostatni poziom szczegółowości siatki może przełączyć
się na zastępczy widok z daleka z własnym materiałem: `M_LastLod`, `M_Billboard`,
`M_Vista`, `M_ProjectionLod`. Kratownicowa wieża z dziesiątkami tysięcy trójkątów może
kończyć się sylwetką z kilkuset trójkątów, którą budżet by wybrał, a z bliska jest to
pełny słup. Poziom szczegółowości, który wprowadza taki materiał, a którego nie ma jego
najdokładniejszy poziom, nigdy nie jest wybierany; najgrubszy poziom siatki jest ostatnim
prawdziwym.

## Teren {#terrain}

Źródło: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Teren to res TerrainStreamingTree (typ `0x22FE8AC8`) i fragmenty, które nazywa.

| Część | Układ |
|---|---|
| nagłówek | 34 bajty; liczba węzłów pod 25 |
| drzewa rastrowe | bajt typu i u32 długości każde, aż do bajtu typu `0xFF`. Typ 0 to mapa wysokości: próbki na bok pod +5 (265), zakres wysokości pod +21 (1 280 m), kwadrat terenu w pierwszym rekordzie węzła pod +77 (8 192 m w sprawdzonym poziomie). Trzyma pudełka węzłów i piramidę min/max 16 x 16 na węzeł, a nie wysokości |
| węzły strumieniowe | czwórkowe drzewo, w głąb: rozmiar fragmentu i GUID; opcjonalny drugi fragment; bajt flag (bit 0: fragment zaczyna się stroną wysokości); ma dzieci. Dzieci w kolejności (0,0), (1,0), (1,1), (0,1) |
| strona wysokości | pierwsze 265 x 265 u16 fragmentu węzła z flagą, wiersz po wierszu; wysokość = wartość x 1 280 / 65 535 m; kolumny wzdłuż x, wiersze wzdłuż z, od niskiego rogu węzła; obramowanie 4 próbek, więc 256 komórek na węzeł |

Każdy krok sprawdzono osobno:

- Parsowanie czwórkowego drzewa węzłów zużywa res do ostatniego bajtu, z zadeklarowanymi 529 węzłami.
- Sąsiednie węzły dzielą swoje dziewięć kolumn krawędziowych dokładnie, więc krok wynosi 256.
- Próbki dziecka w co drugiej pozycji są dokładnie równe próbkom rodzica przy obramowaniu 4, a przy każdym innym obramowaniu różnią się o 90 do 700 jednostek.
- Najniższe słowo w poziomie dekoduje się do najniższej wysokości pudełka z dokładnością do centymetra.
- Spośród ośmiu sposobów, w jakie kwadrat mógłby leżeć na świecie, tylko x wzdłuż x i z wzdłuż z kładzie umieszczone obiekty na nim: połowa próbkowanych kopii w odległości około 2 m, przy czym każdy inny sposób daje wielokrotność tego.

Umieszczone obiekty mierzą potem wynik. Najniższy punkt każdej kopii względem terenu
pod nią (dwuliniowo, z najdokładniejszego węzła):

| Umieszczone | Mediana odległości | Mediana ze znakiem |
|---|---|---|
| drzewa i krzewy | dobrze poniżej metra | tuż pod powierzchnią |
| rekwizyty | metr albo dwa | na powierzchni |
| skały | około metra | zapadnięte o około metr |
| budynki | kilka metrów (stoją na fundamentach) | lekko zapadnięte |

Roślinność stoi na ziemi i nigdzie indziej, co czyni ją najostrzejszym sprawdzeniem:
jej punkty początkowe leżą w medianie 0,07 m od powierzchni. Budynki rozkładają się
szeroko, bo ta kategoria obejmuje ściany, podłogi i elementy zestawów wielopiętrowych
i podziemnych konstrukcji. Przesunięcie terenu o 64 m w bok zmniejsza udział kopii w
odległości 0,5 m z 29% do 10%.

`level` rysuje mapę wysokości jako `ground:terrain`, każdą jej część z najdokładniejszego
węzła, który ma tam wysokości, i nie dokładniej niż `--ground-spacing` (domyślnie 4 m:
3,7 miliona trójkątów dla sprawdzonego poziomu, którego najdrobniejsze węzły mają 0,5 m).
Kawałki o różnej rozdzielczości stykają się małymi schodkami; nic ich nie zszywa.

Fragment węzła niesie też strony masek warstw po swojej stronie wysokości, a jego drugi
fragment kończy się mapą kolorów węzła (zobacz [Warstwy terenu](#terrain-layers)).

## Warstwy terenu {#terrain-layers}

Gra cieniuje teren przy graczu, nakładając na niego materiały powierzchni, które się
powtarzają, malowanymi maskami, z mapą kolorów nad nimi i nakładając dekale (drogi,
łaty asfaltu, oznaczenia pasów startowych) na wierzchu. Opis tego systemu przez samą
Frostbite (Widmark, "Terrain in Battlefield 3", GDC 2012) wymienia rastry terenu: mapę
wysokości, maski splatowania shadera, mapę kolorów "używaną jako nakładka na splatowanie
shaderem", materiały fizyczne, maskę głębi zniszczeń, mapę albedo do odbitego światła
i dodatkowe kanały masek; kafle rastra mają obramowanie dla algorytmów renderowania.
Drzewo strumieniowe sprawdzonych poziomów ma siedem drzew rastrowych, typów 0, 1, 2, 4, 5,
7 i 8, których nagłówki zaczynają się od rozmiaru kafla: 265 dla mapy wysokości (typ 0)
i typu 2, 72 albo 66 dla masek (typ 1), 132 z obramowaniem 2 dla mapy kolorów (typ 4), 260
z obramowaniem 2 dla typu 5.

**Lista warstw.** Res `....layergraphs` terenu wymienia po jednym wpisie 32 bajty na
warstwę, w kolejności, w jakiej rekordy masek je numerują (w jednym poziomie: 34 wpisy,
34 sekcje depotu i indeksy warstw od 0 do 33); id każdego wpisu kończy się kluczem jego
sekcji w depocie bloków shadera warstw (`....layergraphs_shaderblockdepot`), którego blok
nazywa mapy warstwy: jedną mapę koloru `_cv`, mapy `_nhs` i `_ao` na powierzchnię, plus
wspólne mapy detalu i szumu. Wiele warstw nie nazywa żadnych map: to źródła, które czyta
graf warstw. Kolor warstwy to średnia jej mapy `_cv`; skali kafelkowania nie udało się
ustalić. Asset terenu kończy się pięciobajtowym wpisem na warstwę (bajt, potem u32 indeks
warstwy albo -1).

**Maski.** Drzewo rastrowe 1 to czwórkowe drzewo masek. Jego treść zaczyna się od 59
bajtów, a bok strony jest pod 0: 72, gdy strony są BC4 (72 x 72, 2 592 bajty), 66, gdy
są nieskompresowane ośmiobitowe (4 356 bajtów). Potem idzie po jednej grupie na węzeł,
w głąb:

| Część | Układ |
|---|---|
| grupa | u16; u16 liczba rekordów; u32 liczba stron; rekordy; zerowy bajt. Grupa bez rekordów ma w sumie 7 bajtów |
| rekord | 33 bajty: u16 warstwa, u16 hasz, pudełko ćwiartki (cztery liczby zmiennoprzecinkowe), dwa bajty flag, 85-bitowa piramida obecności |

Rekordy grupy to cztery ćwiartki jej węzła, warstwa po warstwie, a ćwiartki każdej
warstwy w kolejności (0,0), (1,0), (1,1), (0,1). Rekord z ustawionym drugim bitem flag
pokrywa swoją ćwiartkę w całości i nie ma strony; ten bez niego ma następną stronę;
ćwiartka bez rekordu warstwy, którą nazywa jej grupa, jest pusta z tej warstwy; pierwsza
flaga jest wyzerowana dokładnie wtedy, gdy warstwa ciągnie się dalej w grupie samej
ćwiartki, o jeden poziom niżej, która ją zastępuje. Liczba stron to liczba rekordów ze stroną.

Strony: po stronie wysokości węzła w jego fragmencie idą strony masek własnej grupy
węzła, 4 358-bajtowa sekcja 16-bitowa i raster 67 x 67 po ośmiu bitów (od początku
fragmentu, gdy nie ma strony wysokości); jego drugi fragment trzyma strony czterech
ćwiartek grup o jeden poziom niżej, ćwiartki w kolejności mapy kolorów, a potem samą
mapę kolorów. Strona to 64 x 64 texele ćwiartki, wiersze wzdłuż z i kolumny wzdłuż x,
z obramowaniem skopiowanym od sąsiadów: 4 texele na stronie BC4, 1 na nieskompresowanej.

Obramowania dowodzą rozmieszczenia bez oceniania: dwie strony tej samej warstwy obok
siebie muszą nieść swoje krawędziowe texele. `read_masks` sprawdza to dla każdej pary,
którą umieszcza, i odrzuca poziom, w którym zgadza się mniej niż 99%. Około jednej trzeciej
sprawdzonych poziomów jest czytana, z obramowaniami, które się zgadzają; kilka nie ma
malowanych masek; reszta jest odrzucana, prawie wszystkie przez to sprawdzenie (ich
fragmenty węzłów trzymają więcej, niż ten układ zna). Grunt odrzuconego poziomu dostaje
średni kolor swoich materiałów powierzchni, a eksport mówi dlaczego. Obramowania
przylegające do pełnej ćwiartki mają wartość 255, a te przy pustej 0.

Nieprzeczytana zostaje sekcja 4 358 bajtów i raster 67 x 67 przed stronami: jej wartości
leżą w wąskim wysokim paśmie, bez małych wartości i bez strażnika.

**Kolor gruntu.** Graf warstw miesza warstwy w skompilowanym grafie shaderów masek,
nachylenia, wysokości i szumu, którego nie czyta się. `--ground-texture` koloruje grunt
regułą własną, podaną tutaj jako taką:

- warstwy, których mapa koloru jest nazwana jako odległa, to zastępcze widoki z daleka i są pomijane;
- warstwy z teksturą pokrywające dziewięć dziesiątych terenu lub więcej to baza. Ich maski są pełne prawie wszędzie, więc to, gdzie każda leży, wybiera shader, a nie ona: te nazwane dla skały albo klifu barwią zbocza stromsze niż 40 stopni, te nazwane dla żwiru barwią płaski teren (inne warstwy bazowe, gdy żadna inna nie pasuje), a między 20 a 40 stopniami mieszają się według nachylenia mapy wysokości (brane co 4 m i rozkładane dwuliniowo na texele zapieczone: powtarzane w blokach 4 m rysowały kolor skalny jako plamy o ostrych krawędziach);
- każda inna warstwa z teksturą jest nakładana na bazę według swojej maski, w kolejności warstw;
- mapa kolorów jest nakładana na wynik tak, jak robi to silnik: dwukrotność koloru gruntu razy mapa, więc środkowa szarość nic nie zmienia; tam, gdzie mapa kolorów nie ma texeli, grunt przyjmuje medianę jasności mapy, w szarości.

Sprawdzone względem mediany koloru gruntu z klatek rozgrywki trzech poziomów (chroma jako
czerwony i niebieski względem zielonego): zapieczony obszar gry wychodzi 1,00 / 0,69 wobec
1,19 / 0,78 w klatkach w jednym, którego warstwy trawy są zielone tam, gdzie klatki pokazują
suchą trawę; 1,19 / 0,82 wobec 1,01 / 1,04 w innym, którego sama mapa kolorów jest ciepła
(1,13 / 0,88); i 1,05 / 0,91 wobec 0,93 / 0,92 w trzecim bez mapy kolorów. Klatki są
oświetlone i z gradacją, więc to mierzy odcień, a nie jasność.

**Mapa kolorów.** Drugi fragment węzła trzyma, po stronach masek jego ćwiartkowych grup,
cztery strony BC7 po 132 x 132 (po 17 424 bajty), po jednej na ćwiartkę węzła, w kolejności
(niskie x, wysokie z), (wysokie x, wysokie z), (wysokie x, niskie z), (niskie x, niskie z).
Drzewo masek mówi, ile bajtów zajmują strony masek, więc mapa kolorów jest znajdowana przez
liczenie, a nie przez koniec fragmentu: w jednym poziomie grubsze węzły niosą po niej cztery
kolejne takie strony, inny raster w jednym płaskim kolorze, a czytanie ostatnich czterech
stron fragmentu zgubiło mapę kolorów na dziewięciu dziesiątych terenu. Bez tego liczenia
mapa kolorów ginęła też w poziomach z nieskompresowanymi stronami masek, których strony nie
tworzą całej liczby stron BC4; w jednym poziomie mapa przeszła z 0,4 do 0,94 swojego terenu.
Kolejność została dopasowana: względem krawędzi mapy wysokości każdej ćwiartki każda strona
węzłów z cechami pasuje do jednej ćwiartki, bez odwrócenia, z wynikiem 0,3 do 0,54, gdzie
następne najlepsze ułożenie jest poniżej 0,2. Złożone według niej, strony poziomu łączą się
bez szwu w drogi, wodę i zabudowę testowego poziomu, przy 0,5 m na texel w obszarze gry.
Tam, gdzie pracują warstwy, mapa kolorów jest prawie neutralna (mediana 110, 107, 104); w innych
miejscach może nieść pełny kolor. Poziom, którego drugie fragmenty zawierają tylko
nieskompresowane strony masek, nie ma odczytanej mapy kolorów. Wcześniejsza runda tego
czytnika nazywała te strony nie-geograficznymi: dopasowywała je do mapy tła, która może być
zupełnie innym krajobrazem, i umieszczała każdą stronę na całym węźle zamiast na ćwiartce.

**Albedo odbitego światła** było szukane i nie znalezione: fragmenty węzła korzenia i
pierwszego poziomu to całe strony masek, a ładunek typu 5 nie został zlokalizowany.

**Dziury.** Asset terenu poziomu (typ res `0x1CA38E06`) nazywa trzy shadery: domyślny
shader powierzchni, shader dziur powierzchni i domyślny shader źródła. Nie ustalono, którą
warstwę czyta shader dziur, więc mapa wysokości nie jest wycinana. W jednym poziomie siatka
nawigacyjna biegnie na siatkach skalnych dziesiątki metrów pod mapą wysokości, tam gdzie gra
musiała je wyciąć. Szukano i nie znaleziono: maski warstwy, rastra 67 x 67, zarezerwowanej
wysokości (żadna strona wysokości w poziomie nie ma 0 ani 65 535) i flagi węzła (każdy węzeł
poniżej korzenia ma flagi 1). Zostają drzewa rastrowe 7 i 8. Oba są kodowane długościami
serii: bajt równy poprzedniemu jest po nim liczbą dalszych kopii (`ff ff 84` to 134 bajty
o wartości 255). Drzewo 7 (kafel 256, pełne czwórkowe drzewo pięciu poziomów, cztery bity na
próbkę) dekoduje się do par bajtów o wartościach od 0 do 3; drzewo 8 (kafel 265) do bajtów
w większości 255, z innymi wartościami w regularnych seriach. Żadne z nich nie ma jeszcze
umieszczonych kafli, więc nie wiadomo, czy któreś trzyma dziury.

**Dekale** są czytane i zapiekane; zobacz [Dekale terenu](#terrain-decals).

## Dekale terenu {#terrain-decals}

Źródło: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Drogi, pasy startowe, betonowe place, malowane linie i litery, ślady opon: res
`TerrainDecals` (typ `0x15E1F32E`) trzyma je jako płaską geometrię, którą gra
przykłada do terenu.

| Część | Układ |
|---|---|
| nagłówek | pod +16 liczba slotów n, potem n slotów po 16 bajtów, potem liczba rekordów |
| rekordy | jeden na partię rysowania, jeden za drugim, o różnej długości: 156 bajtów stałych pól - pierwszy wierzchołek pod +32, liczba trójkątów pod +36, kafelkowanie tekstury w metrach pod +44 - potem bajty wierzchołków partii (przesunięcie, rozmiar), potem ogon nazywający jej tekstury po GUID-ach partycji ich zasobów |
| wierzchołki | 32 bajty: x, z (f32), 8 spakowanych bajtów, u, v (f32), r, g, b, a (f16); każda partia to zwykła lista trójkątów |
| indeksy | u32, liczone od 0 w każdej partii; niepotrzebne |

Sprawdzenia:

- zakresy wierzchołków rekordów następują po sobie bez przerwy i pokrywają dokładnie wszystkie wierzchołki, a pierwszy wierzchołek rekordu razy 32 to jego przesunięcie;
- tak odczytane trójkąty są zwartymi dekalami (litery, paski linii, łaty); odczytane z przesunięciem o jeden wierzchołek, są cienkimi szczelinami przez całą mapę;
- prawie wszystkie partie nazywają w ogonie tekstury: mapę koloru (`_cv`) z mapą krycia (`_op`, kanał czerwony), albo dla oznaczeń maskę kanałów (`_rgb`).

Po GUID-ach tekstur ogon niesie parametry materiału partii, zakodowane tak, jak
kodowane są w bloku shadera (zobacz Odcienie niżej). Kolor farby oznaczenia, śladu opony
albo linii to float3 z haszem `607e`: piaskowy 0,64, 0,56, 0,48 dla śladów opon w piasku,
prawie czarny dla smoły. Mapy krycia są w większości formatu 62, jeden kanał po 8 bajtów
na blok, czytany jako BC4.

Partia mapuje swoją teksturę albo według pozycji w świecie (u = x, v = z, tekstura
powtarza się co tyle metrów kafelkowania: asfalt, beton, żwir), albo 0 do 1 przez cały
dekal (linia, litera, ślad opony). Rekordy są rysowane w kolejności pliku.

**Zapiekanie.** `level --ground-texture M` maluje, pod obszarem dekali i w kafelkach do
4 096 pikseli, mapę koloru tła (dwuliniowo), a potem każdą partię na niej według jej krycia
razy alfa wierzchołków. Kolor wierzchołków się nie używa: niektóre wierzchołki partii są
czysto zielone albo niebieskie, co zabarwiało oznaczenia poziomu na te kolory. Trójkąty
mapy wysokości w tym miejscu stają się częściami `ground:terrain x<x> z<z>` niosącymi kafel.
Każda partia rysuje się tak:

| Nazwy partii | Rysowana jako |
|---|---|
| mapa koloru (`_cv`) | mapa, według jej mapy krycia |
| mapa mnożenia (`_mult`) i mapa krycia | farba (biała, gdy materiał nie nazywa żadnej) razy mapa mnożenia, według mapy krycia: zużyta środkowa linia pasa startowego, linie krawędziowe i progi |
| maska kanałów (`_rgb`) | farba, albo biały dla linii i liter, ciemny dla konturów, lekkie przyciemnienie dla zużycia, śladów opon, plam, kałuż i wilgoci, według maski |
| sama mapa krycia, z farbą | farba według mapy krycia: ślady opon |

Maska wariacji drogi nie jest farbą, tylko zmienia nawierzchnię pod nią na setki metrów
i nie jest rysowana, czymkolwiek by była pomalowana: pomalowana na biało położyła na zboczach
poziomu dwa jasne prostokąty o długości 150 do 250 m. Mapa `_mult` jest brana jako własne
zużycie farby, a nie jako przyciemnienie gruntu pod nią: jest prawie biała, a kształt linii
jest w mapie krycia.

Prawie każda partia się rysuje, w kilku kafelkach po 0,5 m na piksel; eksport rośnie o kilka
MB i trwa kilka sekund dłużej. Widziane z góry, perony, drogi kołowania i sieć dróg leżą pod
ogrodzeniami i budynkami zagród i prowadzą do ich bram.

Narysowane jako geometria własna, dekale wymagałyby mieszania alfy, którego zapisujący nie
obsługuje, a przesunięcie nad terenem walczyłoby z nim o głębię; zapiekanie zostawia je w
kolorze samego gruntu.

## Tekstury i materiały {#textures-and-materials}

Źródło: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Res Texture (typ `0x6BDE20BA`) to 180-bajtowy nagłówek: typ i format pikseli pod +8,
szerokość i wysokość pod +22, liczba mipów pod +30, GUID fragmentu pod +40, piętnaście
rozmiarów mipów pod +56. Fragment to łańcuch mipów, od największego. Niektóre fragmenty nie
mają swoich największych mipów, które są w pakiecie wysokiej rozdzielczości; długość
fragmentu mówi, od którego mipa się zaczyna. Fragment tego pakietu jest nazwany pod +164;
czyta się go z [uzupełnień](#which-table-is-the-level) poziomu, gdy brakującego w głównym
fragmencie mipa jest potrzebny, a jego długość plus długość głównego fragmentu to cały łańcuch.

| Format | Dekodowany jako | Dowód |
|---|---|---|
| 67, 66 | BC7 (sRGB, liniowy) | plastikowy arkusz koloru zbiornika dekoduje się jako BC7; jako BC3 te same bajty są szumem |
| 61, 60 | BC3 | arkusz skrzyni dekoduje się czysto jako BC3, nie jako BC1 ani BC7 |
| 57, 56, 55 | BC1 | pół bajtu na piksel |

Zasób siatki nie nazywa tekstury. Powiązanie jest w **depotach bloków shadera** poziomu
(res typu `0x73312045`, jeden na pod-świat), kluczowanych przez osiem bajtów pod +0x130
rekordu sekcji siatki:

| Część | Układ |
|---|---|
| tabela, od 16 | (klucz sekcji u64, przesunięcie deskryptora u64), aż przesunięcie wypada poza res |
| deskryptor | (przesunięcie bloku u64, hasz u64, rozmiar bloku u64) |
| blok | parametry shadera sekcji; każda tekstura to rekord 49 bajtów: bajt, 16 bajtów, GUID partycji zasobu tekstury, jej GUID instancji |

Klucz sekcji skrzyni pojawia się raz w każdym z dziesięciu depotów pod-światów, które ją
umieszczają, a jej blok nazywa wśród wspólnych map detalu `t_mil_crate_03_cs` i `_nmt`.
Blok nazywa każdą teksturę, którą shader próbkuje, a która z nich jest mapą koloru, nie jest
powiedziane, więc wybiera się ją: tekstura 2D sRGB, której nazwa zawiera większość słów nazwy
materiału (`M_ConcreteWall_01`: concrete, wall), potem nazwy siatki, potem taka, która nie
jest detalem, dekalem (`t_de_...`) ani mapą uszkodzeń, a potem ta, której używa najmniej
bloków. Blok znaku drogowego nazywa jego panel `t_com_highwaysignage_01_cs` i arkusz dekalu
`t_de_com_highwaysignage_01_ca` z tarczą leżącą na boku; oba pasują do słów, a bez reguły
dekalu arkusz wygrywał przez częstość użycia i znak pokazywał tarczę obróconą o ćwierć przez
wszystkie zestawy współrzędnych tekstur sekcji. Maski sygnowanych pól odległości (`..._sdf`),
palety i maski kanałów (`_rgb`) nigdy nie są wybierane, cokolwiek mają wspólnego; mapy
`_rgba` są (większość to kolor z alfą, a ich pominięcie podmieniało własne mapy słupa
linii energetycznej i schodów na obce). Atlas roślinności tła `..._atlas_a_sdf`, rysowany
jako kolor, pokazywał czarne i białe gwiazdy zamiast drzew, paleta budynków tła dawała
konfetti z próbek na ściany, a szkło odłamków rysowane przez maskę kanałów wychodziło
cyjanowe. Sekcja, której jedynymi kandydatami są wspólne mapy detalu, zostaje pokolorowana płasko.

**Palety.** Budynki tła biorą kolory z palety, 256 x 256 texeli, z próbkami 16 x 16: każdy
wierzchołek niesie cztery bajty (użycie `0x1E`), których dwa pierwsze mówią, gdzie w palecie
jest jego kolor, x i y z 255. `level` rysuje taką sekcję z paletą jako teksturą, każdy
wierzchołek w środku swojej próbki. Tak narysowane bloki tła poziomu wychodzą jako pastelowe
ściany, terakota i ciemne okna tam, gdzie były czysto białe.

**Nakładki.** Duże obiekty kafelkują arkusz tekstur przez swoje pierwsze współrzędne tekstury
i nakładają na niego nakładkę przez drugie, które leżą w zakresie 0 do 1: rozwinięcie całego
obiektu. Nakładka (`..._overlay_cs`, z maską `..._overlay_a`) niesie to, jak obiekt wygląda z
daleka, na zbiorniku oleju czerwone pasy i rdzę; narysowany samym arkuszem, zbiornik tego
poziomu wyszedł jako szare panele. Sekcja, której blok nazywa nakładkę z maską, a jej drugie
współrzędne są takim rozwinięciem, jest rysowana z nakładką przez nie (36 sekcji w tym poziomie).

**Odcienie.** Wiele map kolorów jest szarych (średnie ich kanałów w odległości 6% od siebie):
shader maluje je kolorami z parametrów bloku. Po swoich wpisach tekstur (po 49 bajtów)
blok wymienia parametry, każdy z bajtem typu (`f11af825` float3, `a5e1f2de` float4, `c1b1a014`
float, `4a4fc3a1` liczba całkowita), bajtami flag `01 80` dla jednej wartości, dwubajtowym
haszem nazwy parametru, u32 liczbą, wartością i ośmiobajtowym id. Nazwy nie są zapisane.
Siedem haszów nazw float3 działa jako odcienie: w jednym poziomie trzy z nich trzymają kolor
w około 1 bloku na 6, którego mapa jest szara i prawie nigdy tam, gdzie mapa ma własny kolor,
a pozostałe trzymają kolory, którymi maluje się szarą mapę, gdy nazwa materiału tak mówi
(niebieska lamówka mostu `..._blue`: 0,047, 0,098, 0,171 wobec neutralnego 0,5). Rodzina może
mieć kilka wartości, po jednej na kanał maski, z większością neutralnych, a wartość, przy której
kanał jest prawie zerowy (czysta zieleń na ceglanych fasadach), wybiera kanał maski zamiast
malować. `level` mnoży szarą mapę kolorów, w świetle liniowym, przez pierwszą wartość każdej
rodziny, która nie jest ani neutralna, ani takim selektorem, w stosunku do jej neutralnej, i
zachowuje wynik jako własną teksturę; mapa z kolorem zostaje bez zmian. Reguła należy do
eksportera: który kanał maski dostaje który odcień, nie jest odczytywane. W jednym poziomie
zmniejszyło to udział trójkątów konstrukcji rysowanych w pobliżu bieli z 19,4% do 3,9%.

**Wariacje obiektu.** Jedna siatka jest umieszczana w kilku wyglądach: ściana magazynu z
czerwonym albo niebieskim pasem i innym numerem namalowanym na nim, kontener w zieleni albo
szarości. Każda umieszczona kopia nazywa swój wygląd:

| Gdzie | Pole |
|---|---|
| członek grupy modeli statycznych | +32: tablica jednego wskaźnika na kopię, do wariacji obiektu albo null |
| odwołanie do obiektu | +120: wskaźnik do wariacji obiektu albo null |
| wariacja obiektu (partycja `ov_...`, typ `235f2a9c...`) | jej pierwsza instancja +32: u32 hasz nazwy wariacji |

Wygląd sekcji w wariacji to blok shadera kluczowany kluczem własnym sekcji z dodanym
haszem wariacji do jej pierwszych czterech bajtów, jako little-endian u32 (`05177857 76ddd22e`
+ `0x88af2290` = `953927e0 76ddd22e`); sekcja bez bloku pod tym kluczem wygląda tak samo we
wszystkich wariacjach. Tabele wariacji siatek poziomu (`meshvariationdb_win32`) wymieniają dla
każdej siatki i hasza wariacji materiały, których wariacja dotyka, ale nie klucze; regułę
wyprowadzono z samych kluczy i sprawdzono dla każdej sekcji z wariantami (cztery wariacje
jednej ściany, po trzy jej sekcje). Blok wariacji niesie własne tekstury, a nie tylko odcienie:
namalowany numer na ścianie to arkusz liter, który nazywa blok wariacji. Duży udział
zgrupowanych kopii jest umieszczony w wariacji.

Blok jest zapiekany raz dla każdego zestawu zawartości, a wpis depotu dla klucza niesie hasz
tych zawartości (drugie u64 wpisu). Tam, gdzie sekcja nie ma bloku pod kluczem swojej
wariacji, wariacja i tak do niej dociera przez *bliźniaka*: inną sekcję, której domyślny blok
ma tę samą zawartość i ten blok ma. Bez bliźniaków ściana, której długości dzielą jeden
domyślny blok, może wyjść w dwóch kolorach. Sekcja bez własnej wariacji bierze wariant, który
ma większość jej bliźniaków.

**Niszczalne siatki.** Siatka, którą mecz może powalić, ma obok siebie zasób zniszczenia o
tej samej nazwie (`.../br_x.destruction` dla `.../br_x_mesh`): zniszczalne budynki i ściany
(`br_`) oraz wiele rekwizytów. `level` trzyma ich powierzchnie w osobnych częściach, nazwanych
` (destructible)`, których węzły glTF niosą `{"destructible": true}`. Ich stany po zniszczeniu
to siatki `dc_..._part<N>_mesh` obok nich, każda wyśrodkowana na własnym początku; gdzie leży
dana część, jest w assecie zniszczenia, którego się nie czyta, więc stany po zniszczeniu nie są
eksportowane.

**Pomijane.** Sekcje materiałów zastępczych bryły (`M_Whitebox`: kilka dużych,
nieteksturowanych trójkątów, które niektóre budynki trzymają obok swoich powierzchni i które
wystawały z poziomu jako białe płetwy), siatki zrobione na potrzeby filmów (helikopter
ustawiony tam, gdzie zaczyna się jego scena) i pomocnicze elementy oświetlenia (płaszczyzny,
które blokują światło, nigdy nie rysowane). Wygenerowane zaplecze budynków poziomu
(`..._generated_blueprints_..._mesh`) jest rysowane, ale ich materiały ścian nazywają tylko
mapy szumu, a wierzchołki nie niosą koloru, więc zostają zwykłe. Prawie każda rysowana sekcja
dostaje mapę kolorów.

**Arkusze liter.** Namalowany numer na ścianie albo nadruk na billboardzie dźwigu to osobna
sekcja, której mapa koloru jest arkuszem (`_ca`): alfa litery na pełnej farbie albo nadruk.
Jej pierwsze współrzędne tekstury kafelkują tynk ściany po panelu (u od -0,2 do 1,7 na jednej
ścianie), co rysuje arkusz prawie dwa razy. Czwarty zestaw (`0x24`, a w razie jego braku
trzeci, `0x23`) kładzie go dokładnie raz (u od -1 do 0, v od 1 do 2, kilka tysięcznych
za daleko w grubszych poziomach szczegółowości). Gdy pierwszy zestaw zostawia jedną kopię
obrazu, a czwarty albo trzeci mieści się w jednej, arkusz rysuje się przez niego, przesunięty
w 0 do 1. Arkusz z alfą jest rysowany 1 cm przed powierzchnią, na której jest namalowany, a
ta powierzchnia jest rysowana pod nim w drugiej mapie koloru bloku przez pierwszy zestaw: bez
tego puste texele arkusza pokazywały wnętrze ściany. Drugi zestaw to rozwinięcie obiektu dla
jego nakładki i nie jest tu używany.

**Wycinane mapy.** Czwarty kanał mapy koloru znaczy co innego zależnie od nazwy mapy. W `_cs`,
zdecydowanie najczęściej (893 z wybranych map jednego poziomu), to gładkość: 1% alfy mediany
mapy leży w odległości 0,1 od 0 albo 1. W `_cu` (liście, trawa) i `_ca` (kolor i alfa) to
krycie: 90% i 87%. Mapa koloru nazwana `..._cu` albo `..._ca`, której alfa ma co najmniej 75%
wartości blisko 0 albo 1, co najmniej 1% poniżej 0,5 i co najmniej 5% powyżej, jest zapisywana
z alfą jako PNG, a jej materiał jako glTF `alphaMode` MASK, `alphaCutoff` 0,5, dwustronny; karty
liści pokazują wtedy liście, a nie ich czarne rogi. Mapa liści jednego drzewa nie ma w ogóle
alfy (najwyżej 4 z 255): jego listowie jest wycinane geometrią, a przy samych dwóch pierwszych
warunkach wycięto by całą koronę.

Współrzędne tekstury to użycie wierzchołka `0x21`, dwie półliczby (format 6) albo dwie liczby
zmiennoprzecinkowe (format 2). Sekcje niosą do trzech kolejnych zestawów (`0x22` do `0x24`) dla
warstw dekali i detalu. Współrzędne się kafelkują: bok żebrowany kontenera biegnie od -1,6 do
1,8, kafle tła terenu leżą w całości poza 0..1, a w jednym poziomie 23% trójkątów z teksturą
sięga poza 0..1. Zapisuje się je tak, jak są, z powtarzającym się próbnikiem; przeglądarka
3DHeat zawija każdą powtarzającą się teksturę w swoim atlasie. Renderer, który je przycina,
rozmazuje żebra do dwukrotnej szerokości, zamienia betonową podłogę w smugi wzdłuż jednej osi
i daje belkom stalowym wieży kolor krawędzi tekstury; dla niego `--clamped-uvs` tnie każdy
trójkąt wzdłuż linii, gdzie jego tekstura się powtarza, i przesuwa każdy kawałek w 0..1 (zobacz
[Format pliku wyjściowego](output-format.md)). Potem 0,03% trójkątów z teksturą, na których
tekstura powtarza się ponad 16 razy, sięga poza zakres, a trójkąt, który cięcie podzieliłoby
na więcej niż 4 kawałki, rysuje się w średnim kolorze tekstury: kora powtarza się w dół każdej
gałęzi, a pocięte drzewa poziomu wzrosły z 6,4 do 24 milionów trójkątów.

Mapy tła poziomu nie mają własnej mapy koloru, którą dałoby się odczytać. Tam, gdzie pokrywa
mapę wysokości jedna z map tła terenu, jest ona kolorowana z niej: współrzędne tekstury tła to
funkcja liniowa świata x i z (99% wierzchołków w odległości 0,001 od niej; mapa pokrywa kwadrat
65 536 m, obrócony o ćwierć), a ta sama funkcja daje współrzędne mapy wysokości. Poziom
dostarcza mipy tej mapy od 2 048 px w dół, więc mapa wysokości dostaje 32 m na piksel. Jej
ciemna skała leży na stromym terenie: korelacja ciemności z nachyleniem wynosi 0,48, a dla
siedmiu pozostałych orientacji najwyżej 0,34.

Tło innego poziomu to osiem bliskich i osiem dalekich kafli wokół obszaru gry, każdy powtarza
własną teksturę na całym kaflu i żaden nie dosięga mapy wysokości. Każda tekstura tła jest
dopasowywana osobno, a gdy żadna nie pokrywa mapy wysokości, bierze średni kolor, jaki tło
pokazuje w odległości kilometra od kwadratu terenu; tym kolorem `--ground-texture` zapieka
dekale. Materiał tła to taki, którego nazwa zawiera `TerrainBackdrop`, albo `BD_` i `Terrain`
(`M_BD_<site>_Terrain..._Near`); albo siatka tła (`bd_..._terrain<site>_04_far_mesh`) niesie
zwykły materiał terenu (`M_<region>_Terrain<site>_04_Far`), który w jednym poziomie przeoczyły
pierwsze dwie reguły, więc jego grunt był kolorowany z powierzchni, a nie z tła.

Tam, gdzie żadna mapa tła nie pokrywa mapy wysokości, bierze ona jednak średni kolor
własnych powierzchni terenu, zanim wezmie średnią tła: mapy `_cv` bloków shadera grafu
warstw poziomu (27 w jednym poziomie: piaski, żwiry, gleby, trawa, popękany beton), każda
uśredniona, potem mediana każdego kanału, z pominięciem domyślnej powierzchni silnika. Tło
może być zupełnie innym krajobrazem: w jednym poziomie jego średnia (95, 99, 80 w sRGB)
zmieniała grunt obszaru gry na szarość, której gra nie pokazuje. Przy `--ground-texture`
ten kolor jest mnożony przez dwukrotność mapy kolorów, co środkową szarość zostawia bez
zmian, i zapiekany z dekalami nad obydwoma zasięgami: dekali i mapy kolorów.

Względem gry: mediana koloru gruntu zapieczonego obszaru gry każdego poziomu i klatek
rozgrywki (wiersze od 55 do 72% obrazu obok HUD, po 24 klatki; sRGB; klatki są oświetlone
i z gradacją, więc właściwym porównaniem są stosunki r/g i b/g):

| Poziom | Klatki | Średnia tła | Teraz |
|---|---|---|---|
| pierwszy | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| drugi | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| trzeci | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Pierwszy jest poprawiony; pozostałe dwa były wcześniej nieco bliżej w odcieniu. Jeden kolor
dla całego poziomu nie może być dobry wszędzie; mogłyby nim być maski.

## Siatka nawigacyjna {#navigation-mesh}

Źródło: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Poziom dostarcza po jednej partycji na agenta, `<level>/dbt/<level>_navmesh_layer_<n>`:
w jednym poziomie warstwa 0 to żołnierz (1,8 m wysokości, 0,18 m schodek, 0,4 m promienia), a
dwie inne to pojazdy (3,5 i 10 m wysokości). Każda partycja trzyma dwie tablice:

| Tablica | Element |
|---|---|
| kafle | 28 bajtów: u32 0, u32 hasz, u32 0, u32 indeks fragmentu, u16 x kafla, u16 z kafla, u32 przesunięcie, u32 rozmiar |
| fragmenty | 20 bajtów: GUID fragmentu, u32 rozmiar |

Kafel to `size` bajtów pod `offset` we fragmencie o indeksie `chunk index`, little-endian,
ułożone jak w Detour (Recast Navigation), za dłuższym nagłówkiem:

| Przesunięcie | Zawartość |
|---|---|
| 0 | `VAND`, wersja 7 |
| 24 | liczniki: wielokąty, wierzchołki, połączenia, siatki detalu, wierzchołki detalu, trójkąty detalu, węzły bryły ograniczającej, połączenia poza siatką, pierwszy wielokąt poza siatką |
| 188 | wysokość agenta, schodek, promień |
| 200 | pudełko ograniczające kafla, sześć liczb zmiennoprzecinkowych |
| 232 | wierzchołki: liczby zmiennoprzecinkowe x, y, z, współrzędne świata |
| następna granica 8 bajtów | wielokąty, po 32 bajty: u32, sześć indeksów wierzchołków u16, sześć sąsiadów u16, flagi u16, liczba wierzchołków pod +30, pod +31 obszar (dolne sześć bitów) i rodzaj (dwa górne) |
| potem, upakowane | połączenia (16 bajtów), siatki detalu (12: pierwszy wierzchołek detalu u32, pierwszy trójkąt detalu u32, liczba wierzchołków i trójkątów u8), wierzchołki detalu (trzy liczby zmiennoprzecinkowe), trójkąty detalu (trzy indeksy i flagi), węzły bryły ograniczającej (16), połączenia poza siatką (80) |

We wszystkich kaflach sprawdzonych poziomów te części sumują się do rozmiaru kafla co do
bajtu, a siatki detalu liczą wielokąty przed pierwszym wielokątem poza siatką.

Wielokąt jest płaski między swoimi rogami; jego **siatka detalu** trzyma prawdziwą wysokość
powierzchni nad garbami, skałami i schodkami i to ona jest rysowana. Indeks trójkąta detalu
poniżej liczby rogów wielokąta to ten róg, a w przeciwnym razie wierzchołek detalu
`first + index - corners`. Rozwijanie wielokątów wachlarzem daje wielokrotnie więcej trójkątów
pod terenem i długie szczeliny; z siatkami detalu żaden nie jest dłuższy niż przekątna kafla
16 m plus schodek w górę zbocza.

Rodzaj 0 to grunt, rodzaj 2 to małe strome łaty (około 45 stopni, po metrze kwadratowym),
rodzaj 1 to połączenie między powierzchniami: jego rogi rozciągają się na 125 m wysokości lub
więcej i leżą poza kaflem, niektóre w początku. Połączenia są pomijane; reszta jest rysowana
przez swoje siatki detalu albo wachlarzem w kaflu bez żadnej.

Sprawdzenia: rozmiary fragmentów sumują się dokładnie do rozmiarów kafli; każdy wierzchołek
powierzchni leży w pudełku swojego kafla z dokładnością do około metra; prawie wszystkie
trójkąty są skierowane w górę. Kafel, który nie przechodzi, jest odrzucany i liczony, a w tym
poziomie żaden nie jest.

Co obejmuje siatka żołnierza, widziane z góry w testowym poziomie: grunt, podłogi, schody i
część dachów, a nie wierzchy kontenerów towarowych. To mapa AI, na której żołnierz może stać,
i najbliższe, co pliki pokazują, do miejsc, w których stoją gracze.

## Nie zaimplementowane {#not-implemented}

- Graf warstw terenu, który miesza jego warstwy powierzchni (zobacz [Warstwy terenu](#terrain-layers)): kolor gruntu idzie regułą tego czytnika, wziętą z masek warstw i nachylenia mapy wysokości, a poziomy, których strony masek do siebie nie pasują, dostają jeden kolor.
- Parametry koloru materiałów dekali: oznaczenia przez maski kanałów są malowane neutralnym kolorem.
- Plany obiektów, które nie są siatkami (logika gry, efekty, dźwięki).
- Stany po zniszczeniu niszczalnych siatek: ich miejsca są w assecie zniszczenia, którego nie czyta się.
- Połączenia siatki nawigacyjnej (skoki, drabiny, przeskoki) i jej warstwy pojazdów.
- Siatki poziomów zapisane wewnątrz res (10 siatek w poziomie, gadżety), kości i części siatek szkieletowych i złożonych oraz normalne (liczone przez zapisującego).
- Mapy normalnych, szorstkości i inne; alfa inna niż wycinanie (przezroczyste szkło i dekale są rysowane nieprzezroczyste).
- Dziury w terenie: nazwany jest shader dziur powierzchni, ale nie ustalono, co czyta (zobacz [Warstwy terenu](#terrain-layers)), więc mapa wysokości nie jest wycinana tam, gdzie pod nią leży grunt, po którym chodzi żołnierz.
- Który odcień idzie z którym kanałem maski materiału: szara mapa kolorów bierze pierwszy odcień, który nie jest neutralny (zobacz [Tekstury i materiały](#textures-and-materials)).
- Efekty (ścieżki `fx/`) i siatki kabli, których pudełka ograniczające mają dziesiątki kilometrów; są pomijane i liczone w podsumowaniu.
- Wersja tabeli z zaciemnieniem XOR.
