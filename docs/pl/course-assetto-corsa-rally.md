---
title: "Eksport trasy: Assetto Corsa Rally"
nav_order: 3
lang: "pl"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Eksport trasy: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally działa na Unreal Engine 5 (wersja 5.6.1, zmodyfikowana) i dostarcza zawartość jako kontenery IoStore. Żaden z nich nie jest zaszyfrowany. Eksport znajduje etap i orientację osi na podstawie okrążenia. Zapisuje kafelki terenu samego etapu, podzielone na drogę i teren, z teksturą z zapieczonego w grze koloru podłoża etapu. Pozostałe modele umieszcza w jednolitych kolorach, według kategorii.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Źródła: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (instalacja, etapy, rozmieszczenie),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (eksport).
Czytniki Unreal, na których to stoi, opisano w [Unreal 5 IoStore](reader-unreal-iostore.md),
a dekompresję w [Oodle](reader-oodle.md).

**Stan:** sprawdzone na zainstalowanej grze, z okrążeniami wygenerowanymi w losowej klatce na każdym etapie. Za każdym razem znalazło właściwy etap i klatkę. Żadne okrążenie nagrane w samej grze jeszcze przez nie nie przeszło.

## Znajdowanie instalacji {#finding-the-install}

- `--install <folder>`: folder gry, jej `Content\Paks` albo dowolny folder z plikami `.utoc`. Narzędzie sprawdza `<folder>`, potem `<folder>\acr\Content\Paks`, potem `<folder>\Content\Paks`.
- W przeciwnym razie sprawdzany jest folder `steamapps\common\Assetto Corsa Rally` w każdej bibliotece Steam, w ten sam sposób.
- Każdy plik `.utoc` w tym folderze jest otwierany jako jeden magazyn. Kontenery, których nie da się otworzyć, są pomijane. Jeśli żaden się nie otworzy, pojawia się komunikat: "no readable IoStore containers in ...".

Większość bloków jest skompresowana Oodle, a bibliotekę szuka się na komputerze (przeszukiwane są wszystkie biblioteki Steam). Zobacz [Oodle](reader-oodle.md).

Gra zostaje uznana za AC Rally, gdy plik okrążenia ma `"game": "assetto-corsa-rally"` (albo `acrally`), albo gdy podasz `--game acrally`.

## Czym jest etap {#what-a-stage-is}

Etap to mapa **World Partition**:

- `Content\Levels\<Stage>.umap` umieszcza odległy teren.
- Zapieczone komórki w `Content\Levels\<Stage>\_Generated_\*.umap` umieszczają wszystko inne.

Poziom liczy się jako etap, jeśli jego folder środowiska, `Content\Environments\<Stage>\`, ma folder `MeshesTrack`. Narzędzie nie opiera się na nazwach kafelków, bo etap może nazwać je od miasteczka, a nie od swojej mapy. `--level` dopasowuje się bez względu na wielkość liter do tych nazw map. Złą nazwę zastępuje lista istniejących etapów.

Nie ma **żadnego landscape**. Podłoże to siatki statyczne:

| Kafelki | Ścieżka | Stają się |
|---|---|---|
| kafelki trasy, około 175 m, podzielone na dwie części | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` i `..._Terrain_k` | `ground:road` i `ground:terrain` (kafelek trasy bez podziału, na przykład zamarznięte jezioro, jest w całości drogą) |
| odległy teren, kafelki 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Odczyt rozmieszczeń {#reading-the-placements}

To, co umieszcza siatkę, to `StaticMeshComponent`: jej `StaticMesh` oraz `RelativeLocation`, `RelativeRotation` i `RelativeScale3D`. Każde z nich jest względne wobec komponentu, do którego jest podpięty (`AttachParent`), aż do korzenia aktora, który leży w świecie.

- Właściwości są **unversioned**: zapisane według pozycji na liście właściwości klasy, a nie po nazwie. Odczytuje się je schematami z [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) (zob. [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Wartość równa szablonowi komponentu (jego archetypowi w Blueprincie) nie jest zapisywana. Dlatego najpierw czyta się wartości szablonu, rekurencyjnie, a własne wartości komponentu je nadpisują.
- Komponenty z `bVisible = 0` albo `bHiddenInGame = 1` są pomijane. Pomijane są też siatki, których ścieżka pasuje do `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/` lub `_hlod`.
- Obroty używają `FRotationMatrix` z Unreala (pitch, yaw, roll w stopniach).
- Duplikaty (ta sama siatka w tej samej transformacji, z dokładnością 0,1 cm) są usuwane.
- Komponenty, których nie da się odczytać, są liczone według przyczyny i zgłaszane, na przykład `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Komponenty instancjonowane** (lasy, prawie wszystkie) są czytane tylko z `--trees`. Ta wersja gry przearanżowała te klasy poza nagłówki silnika, więc ich właściwości nie są czytane. Zamiast tego:

- siatka pochodzi z tabeli zależności pakietu, gdzie każdy taki komponent wskazuje dokładnie jedną siatkę statyczną,
- instancje pochodzą z natywnego bloku po właściwościach (`[1][1][128][count]`, a potem `count` macierzy 4x4 w double),
- komponent uznaje się za leżący w korzeniu swojego aktora, tak jak aktory roślinności go umieszczają.

Współrzędne są Unrealowe: centymetry, Z w górę, X do przodu, Y w prawo, układ lewoskrętny.

## Który etap i w którą stronę {#which-stage-and-which-way-round}

Ramka telemetrii nie jest udokumentowana, więc nie zakłada się jej z góry. Jest dopasowywana:

- **Osiem kandydujących ramek.** Unreal Z (cm) razy 0,01 staje się wysokością okrążenia (y). Unreal X i Y stają się x i z okrążenia, zamienione albo nie, każde z dowolnym znakiem, wszystko przeskalowane przez 0,01 na metry.
- **Siatka wysokości drogi.** Dla każdego etapu każdy kafelek drogi jest umieszczany (na najgrubszym poziomie szczegółowości), a dla każdej komórki 2 m zachowuje się najwyższy wierzchołek drogi.
- **Ocena.** Do 400 równomiernie rozłożonych próbek okrążenia przenosi się do przestrzeni Unreala przez każdą ramkę. Próbka leży na drodze, gdy wśród 3 x 3 komórek wokół niej wysokość drogi najbliższa próbce mieści się między 1 m poniżej a 3 m powyżej niej (`ON_ROAD`). Wynik to udział próbek na drodze.
- **Zwycięzca.** Najlepsza ramka na najlepszym etapie, jeśli wynik wynosi co najmniej 50%. W przeciwnym razie eksport się zatrzymuje: "the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level."
- **Okrążenie, które podaje swój tor.** Jeśli plik okrążenia ma pole `track`, najpierw sprawdzany jest sam ten etap, jeśli jego nazwa luźno pasuje (same litery i cyfry, jedna zawiera drugą). Przyjmuje się go tylko przy wyniku co najmniej 80%. W przeciwnym razie sprawdza się wszystkie etapy.
- Z `--level` sprawdza się tylko ten etap, we wszystkich ośmiu ramkach.

Konsola pokazuje na przykład: `on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Wszystko zapisuje się potem **w ramce okrążenia**: w metrach, Y w górę. Kolejność wierzchołków trójkąta odwraca się wszędzie tam, gdzie transformacja odbija, więc ściany nadal wskazują właściwą stronę.

## Podłoże {#the-ground}

- Korytarz to `--margin` metrów wokół okrążenia, w jego własnej płaszczyźnie x/z.
- Każdy kafelek podłoża umieszcza się na najdrobniejszym poziomie szczegółowości i zachowuje tylko trójkąty sięgające do korytarza.
- Trójkąty grupuje się według rodzaju (droga albo teren) i według kwadratu 512 m w przestrzeni Unreala (51 200 cm). Każdy kwadrat ma własny obraz. Części nazywają się na przykład `ground:road 1_-4`. UV to `(unreal_xy - square_origin) / 51200`.
- Normalne liczy się z trójkątów dla całego pliku.

### Tekstura podłoża {#the-ground-texture}

Chyba że podasz `--no-textures`, każdy kwadrat maluje się z dwóch źródeł, w rozmiarze `--texture-size` pikseli:

1. **Zapieczony kolor podłoża.** `RuntimeVirtualTextureComponent` mapy etapu (jego pudełko to `RelativeLocation` jako narożnik i `RelativeScale3D` jako rozmiar, bez obrotu) wskazuje na strumieniowaną **teksturę wirtualną**, czyli kolor podłoża zapieczony przez grę. Z niej odczytuje się obszar kwadratu, na poziomie, którego piksele są najbliższe żądanemu rozmiarowi. To od 13 do 59 cm na piksel, zależnie od etapu.
2. **Zdjęcie satelitarne** wypełnia to, co tekstura wirtualna zostawia czarne. To tekstura `sat*_(b|bc|c|basecolor)` etapu, w jego folderze środowiska, czytana w rozdzielczości do 4096 px. Jej położenie znajduje się dopasowaniem najmniejszych kwadratów pierwszego kanału UV dalekiego terenu do współrzędnych świata x i y. Dopasowanie musi być liniowe z dokładnością 0,01 na 95. percentylu, inaczej obrazu się nie używa. Jeśli UV dalekiego terenu wychodzą poza 1 (materiał, który je powtarza), mapowanie dzieli się przez dwa, aż pasuje raz.

Konsola podaje, którego użyto, na przykład `ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`. Etap bez żadnego z nich rysuje się w jednolitych kolorach.

## Umieszczone modele {#placed-models}

Każde rozmieszczenie, które nie jest kafelkiem podłoża, klasyfikuje się po ścieżce siatki (pierwsze trafienie wygrywa):

| Kategoria | Nazwa siatki (albo ścieżka, dla drzew) zawiera |
|---|---|
| drzewa (tylko z `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| skały | `rock`, `cliff`, `boulder`, `stone` |
| krawężniki | `kerb`, `curb` |
| bariery | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| znaki | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| budynki | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktura | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekwizyty | cokolwiek innego |

- Kopia jest brana pod uwagę, jeśli jej początek leży w korytarzu zasięgu (`margin + 60 m`), a rysowana, jeśli jej granice dotykają korytarza.
- Poziomy szczegółowości wynikają z [Poziomy szczegółowości i budżet](detail-budget.md): najpierw pasma odległości, potem najbardziej kosztowne modele schodzą w dół, aż się zmieszczą w budżecie. Gdy nawet najgrubsze poziomy go przekraczają, najdalsze kopie są pomijane, jak w BeamNG, aż budżet się domknie. Krawężniki zachowują pełny szczegół i nigdy nie są pomijane. Podsumowanie wypisuje `placed on it (N triangles of a B budget)` i, gdy jakieś kopie zostały pominięte, `N copies left out to fit the budget, the furthest from the driving first`.
- Każda kategoria to jedna część w jednolitym kolorze: `ground:kerbs` dla krawężników, które są nawierzchnią jezdni, jak w Forzie i BeamNG, oraz `structure:<category>` dla reszty:

| Kategoria | Kolor (liniowe RGB) |
|---|---|
| bariery | 0.55, 0.52, 0.48 |
| znaki | 0.75, 0.72, 0.65 |
| budynki | 0.62, 0.58, 0.52 |
| infrastruktura | 0.48, 0.48, 0.50 |
| skały | 0.45, 0.43, 0.40 |
| rekwizyty | 0.55, 0.45, 0.35 |
| drzewa | 0.20, 0.32, 0.14 |
| krawężniki | 0.70, 0.25, 0.22 |

Siatki statyczne, których nie da się odczytać (siatki szkieletowe, siatki tylko Nanite, poziomy niezapisane w pliku), są liczone: `N meshes could not be read`.

## Sprawdzenia {#checks-behind-it}

Jak podano w źródle, na zainstalowanej grze:

- Każda tabela zawartości się odczytuje (wersja 8).
- Każda komórka każdego etapu się otwiera, a każdy komponent siatki statycznej i sceny dekoduje się i kończy dokładnie na natywnym ogonie swojej klasy.
- Prawie każda próbkowana siatka statyczna się dekoduje (reszta to siatki szkieletowe). Zdekodowany zasięg kafelka drogi zgadza się z zapisanymi dla niego granicami.
- Poziomy mip zdjęcia satelitarnego mają dokładnie rozmiary swoich wpisów bulk.
- Kafelki fragmentu tekstury wirtualnej są rozliczone co do bajta, a kafelki drogi lądują na drodze, którą ona pokazuje.

## Znane braki {#known-gaps}

- Właściwości samych komponentów instancjonowanych nie są czytane (zob. wyżej). Ich umieszczenie zakłada korzeń aktora.
- Lasy generowane przez PCG w czasie działania gry nie są zapisane w plikach i nie da się ich wyeksportować.
- Siatki splajnowe (niewidzialne ściany respawnu), komponenty nakładek i własne tekstury umieszczonych modeli nie są rysowane. Modele mają jednolite kolory.
- `--season` nie działa.
- Łatka gry może przesunąć sloty właściwości. Czytnik zgłasza błąd zamiast czytać źle, a eksport podaje, ile komponentów się nie udało.
