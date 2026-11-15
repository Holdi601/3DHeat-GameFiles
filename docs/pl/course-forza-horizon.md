---
title: Forza Horizon
nav_order: 1
lang: "pl"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Eksport toru: Forza Horizon {#course-export-forza-horizon}

Eksport Forzy czyta tor prosto z archiwów ForzaTech w grze: teren z rozdzielonymi
drogą, poboczem i trawą, teksturę gruntu zapieczoną z własnych map gruntu gry oraz
każdy umieszczony model we własnej teksturze (krawężniki, bariery z taśmy, ściany
z opon, znaki, rekwizyty, budynki). Znajduje też, na którym z wyścigów gry
przejechano okrążenie, i dokłada to, co gra wystawia tylko dla tego wyścigu
(jego warstwę zdarzeń: bariery, namioty, bramy, trybuny, flagi), oraz grunt każdej
areny, przez którą przebiega jazda, na przykład podłogę stadionu.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Źródła: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Same formaty kontenerów są opisane na stronie [ForzaTech](reader-forzatech.md).

## Znajdowanie zainstalowanej gry {#finding-the-installed-game}

Nikt nie powinien wpisywać ścieżki w rodzaju
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, więc ścieżka jest ustalana sama:

1. **Biblioteki Steam.** Plik `config\libraryfolders.vdf` Steam jest czytany z
   `C:\Program Files (x86)\Steam` albo `C:\Program Files\Steam`, a każdy wpis `"path"`
   w nim to biblioteka. W `steamapps\common` każdej biblioteki szukamy dalej.
2. **Microsoft Store.** Przeszukiwany jest `C:\XboxGames`, jeśli istnieje. Tam gra
   leży o jeden poziom głębiej, w `<game>\Content`.
3. **Folder gry** to każdy podfolder tych folderów, który ma folder `media\Tracks`,
   bez względu na nazwę.
4. **Folder toru** to każdy folder w `media\Tracks`, który zawiera `GeoChunk0.minizip`.
   Liczy się po zawartości, a nie po nazwie, więc tor o nazwie, której nikt nie widział,
   też zostanie znaleziony.

Jeśli gra jest gdzie indziej, podaj folder toru przez `--track`; zobacz
[Rozwiązywanie problemów](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` pomija całe to szukanie.

Folder toru zawiera pliki, które czyta eksport:

| Plik | Co to jest |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | archiwa: każdy model, tekstura i plik rozmieszczenia, bez nazw w środku |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | jeden wiersz na wpis archiwum, w kolejności wpisów: jedyne źródło nazw |
| `AssetManifest.xml` | każda tekstura, jaką ma tor, z hashem, po którym materiały się do niej odwołują |

## Który tor {#which-track}

Gra dostarcza więcej niż jeden folder toru (mapa otwartego świata, garaż czy dwa).
Właściwy wybiera się według **współrzędnych, nie nazwy**:

- Pytaniem jest pudełko ograniczające okrążenia, poszerzone o `--margin`.
- Dla każdego folderu toru czyta się jako tekst cztery manifesty `ChunkContentsMiniZip*.txt`, bez otwierania archiwum. Każda nazwa kafla terenu (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) niesie swoją pozycję w siatce. Narzędzie liczy, ile różnych kafli leży w pudełku.
- Wygrywa tor z największą liczbą kafli w tym miejscu. Jeśli żaden tor nie ma żadnego, eksport się zatrzymuje z komunikatem "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."

Cały tor odpowiada w niespełna sekundę. Dopasowanie po nazwie mogłoby wybrać złą
mapę, a zła mapa wygląda równie wiarygodnie jak dobra.

Konsola pisze `on <track>, in <game folder>`.

## Który wyścig {#which-race}

Gra zapisuje każdy wyścig jako trasę z numerem, jej **identyfikator trasy** (route
id). Do każdej trasy należą dwa pliki:

| Plik | Co zawiera |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | linia jazdy AI wyścigu: węzeł po 56 bajtów od bajtu `0x60`, liczba węzłów w `0x24`, każdy węzeł zaczyna się pozycją (x, y, z) w metrach gry |
| `media\Stripped\gs\<map>\routedefinitions.zip` | jeden `route<id>_<map>.rtd` na wyścig: zwykły XML wymieniający, co wyścig dodaje do świata i co z niego usuwa (zobacz [Warstwa własna wyścigu](#the-races-own-layer)) |

Okrążenie dopasowuje się do trasy przez porównanie z każdą linią AI, której pudełko
nachodzi na pudełko okrążenia:

- Dla każdej próbki okrążenia – odległość do najbliższego punktu linii; a dla każdego punktu linii – odległość do najbliższej próbki okrążenia.
- Dodaje się obie mediany. Wygrywa trasa z najmniejszą sumą, jeśli suma jest mniejsza niż **30 m** (`MATCH`).
- Potrzebne są oba kierunki: krótki sprint leży wzdłuż długiej trasy, która używa tej samej drogi, a długie okrążenie obejmuje krótką trasę.

Konsola pisze `the game's route <id> (driven line within <n> m of it)` albo że
żadna trasa nie pasuje. Bez dopasowania umieszcza się tylko świat wolnej jazdy.

## Teren {#terrain}

Jak znajdowany jest teren (w `forzaterrain.py`):

- Manifesty nazywają teren jako indeks przestrzenny:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Te dwie liczby to współrzędne siatki, które **rosną o 1023**, a każdy krok siatki to **kafel 512 m**. Kafel `x-2046` to `-2046 / 1023 = -2`, który zaczyna się w `-2 * 512 = -1024` m. Jeśli czytać nazwy jako metry, każde wyszukiwanie chybi o czynnik dwa i nadal zwróci teren, tyle że z innej części mapy.
- Kafel może występować trzy razy: zwykły, `_cb` i `_ul`. Wszystkie trzy pokrywają ten sam grunt. Bierze się jeden na kafel, w tej kolejności pierwszeństwa, bo łączenie ich potroiłoby geometrię w pokrywających się powierzchniach.
- Kafel jest czytany tylko wtedy, gdy dotyka pudełka okrążenia **i** korytarza. Kafel, którego korytarz nie dotyka, nigdy nie jest rozpakowywany.
- Każdy `.modelbin` wybranego kafla jest dekodowany tylko na **poziomie szczegółowości 0**. Kafel ma cztery poziomy nad tym samym gruntem, a eksport wszystkich czterech umieściłby ten sam metr kwadratowy w pliku cztery razy.
- Każda siatka niesie własną skalę i przesunięcie w przestrzeni świata, więc kafel ląduje tam, gdzie gra go umieszcza, bez przekształcenia instancji. Trójkąty, których obrys nachodzi na pudełko, są zachowywane, a potem tylko te sięgające do korytarza.
- Siatka w formacie, którego czytnik nie przyjmuje, jest pomijana i liczona (`N meshes could not be read`), więc słaby wynik mówi, dlaczego.

Podsumowanie terenu wypisuje liczbę wierzchołków, trójkątów, siatek i kafli oraz zakres x/y/z.

### Droga, pobocze, teren, oznaczenia, woda {#road-verge-terrain-markings-water}

Nazwy materiałów nie mówią, gdzie jest droga. Wokół toru 94% gruntu używa materiału
z shaderem drogi, bo teren przy drodze rysuje się tym shaderem, a shader decyduje
o asfalcie lub trawie dla każdego piksela. Dlatego:

| Rodzaj | Ustalany przez |
|---|---|
| pas drogi | **układ wierzchołków**: pasy drogi są jedynym gruntem z drugim zestawem UV (kanał 1); trójkąt, którego wszystkie trzy wierzchołki go mają, to droga |
| asfalt czy pobocze | w obrębie pasu drogi, maska asfaltu kafla w środku trójkąta: 0,5 lub więcej to `road`, mniej to `verge` |
| oznaczenia | dopasowanie nazwy materiału do `whiteline`, `yellowline` albo `decal` |
| ślady opon | dopasowanie nazwy materiału do `tyremark` albo `skid` (sprawdzane przed oznaczeniami, bo ślady opon są dostarczane jako `tyremark_decal_*`) |
| woda | dopasowanie nazwy materiału do `water`, `lake`, `river`, `paddy`, `ocean` albo `sea` |
| teren | wszystko inne |

Według zmierzonych okrążeń na torze testowym prawie wszystkie próbki trafiają w
trójkąty pasów drogi, a zdecydowana większość w część asfaltową, gdy maska odłączy pobocze.

Maska asfaltu istnieje tylko wtedy, gdy zapieka się tekstury gruntu. Przy
`--no-textures` albo dla kafla, którego mapy brakuje, pasy drogi zostają całe jako
`road` i pobocze się nie wydziela. Brakujące mapy kosztują szczegółowość, nigdy geometrię.

### Malowane warstwy są podniesione {#painted-layers-are-lifted}

Oznaczenia pasów i ślady opon są dostarczane jako własne trójkąty leżące dokładnie
na drodze. Gra rysuje je z przesunięciem głębi. Narysowane tak, jak są, droga i
farba walczą o każdy piksel. Eksport daje każdej części oznaczeń i śladów opon
własną kopię wierzchołków, podniesioną o **5 cm** (`DECAL_LIFT`) wzdłuż normalnej
powierzchni, tak żeby droga pod spodem nie była podniesiona razem z nimi.

### Normalne {#normals}

Normalne terenu pochodzą z archiwum. X normalnej jest zapisany jako czwarta krótka
wartość pozycji, a jej y i z w atrybucie `NORMAL` (zobacz [ForzaTech](reader-forzatech.md)).
Jeśli jakiś wierzchołek w wyciągu nie ma normalnej, normalne dla całego gruntu są
liczone z trójkątów.

## Tekstura gruntu {#the-ground-texture}

Każdy kafel terenu dostarcza trzy mapy obejmujące swój kwadrat 512 m, w pięciu
rozdzielczościach (`_quality1` do `_quality5`, największa 2048 px, czyli 25 cm na piksel):

| Mapa | Wzorzec nazwy pliku | Co zawiera (jak zmierzono) |
|---|---|---|
| main | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: normalna detalu (x, z). A: niska na asfalcie i na nierównym terenie |
| sub | `submap_x<X>_z<Z>_x<season>x_diff` | wagi warstw. B: wysoka na asfalcie (239 na linii jazdy, 165 obok niej) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: niska na asfalcie (147 wobec 215). B: rośnie w lesie |

Żadna z nich nie jest kolorowym zdjęciem. To wejścia, którymi shader terenu gry
miesza swoje warstwy materiałów, a te warstwy nie są dekodowane. Dlatego zapieczona
tekstura to **interpretacja, a nie kopia wyglądu gry**. Zachowuje *gdzie* jest każdy
rodzaj gruntu, z dokładnością 25 cm, i maluje go stałymi kolorami:

| Grunt | Liniowy RGB | Waga |
|---|---|---|
| trawa (krótka, przy torze) | 0,30, 0,44, 0,18 | podstawa |
| szorstki (dalej) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| las | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Dla asfaltu muszą zgadzać się obie mapy. Jedna sama zostawia szare plamy w trawie
tam, gdzie pierścienie kompresji bloków. Wynik jest cieniowany normalną detalu
z mapy main względem stałego światła (`0.55 + 0.6 * lambert`), więc krawędzie
krawężników, skarpy i koleiny czytają się jako rzeźba, i zapisywany jest jako 8-bitowy sRGB.

Orientacja: wiersz 0 piksela to krawędź **północna** kafla (największa wartość z), kolumna 0
to krawędź **zachodnia** (najmniejsze x). Ustalono to, rzutując zarejestrowane
okrążenia na maskę asfaltu we wszystkich ośmiu sposobach, na jakie można obrócić
lub odbić kwadrat. Dokładnie jeden sposób kładzie je na asfalcie. Współrzędne UV
wynikają z tego: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Mapy są czytane w najlepszej dostępnej rozdzielczości do jakości 5 i przeskalowywane
do rozmiaru mapy main. Jeśli obraz kolorów jest większy niż `--texture-size`, jest
potem zmniejszany do tego rozmiaru filtrem Lanczos. Maska asfaltu zawsze zostaje w pełnej
rozdzielczości, bo ona decyduje o geometrii. `--season` wybiera mapy `x<season>x`.
Kafel bez map dla tej pory roku jest rysowany płaskimi kolorami, a konsola podaje
`N without maps`.

## Umieszczone modele {#placed-models}

Teren niesie własną pozycję w świecie. Nic innego jej nie niesie. Gdzie stoi każda
kopia modelu, jest zapisane w plikach rozmieszczenia `.pgeo`, po jednym na kategorię
na komórkę przestrzenną:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Układ rekordu
jest opisany na stronie [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Co jest czytane {#what-is-read}

- Pliki rozmieszczenia są filtrowane **po nazwie**: rozmiar komórki i jej pozycja w ścieżce dają kwadrat komórki (`x * size` do `(x + 1) * size`), a otwierane są tylko komórki nachodzące na pudełko okrążenia, w pożądanej kategorii.
- Kategorie domyślnie: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` dodaje `trees`, `bushes` i `smashables`. Nigdy nie są czytane: `grasstemplate`, `crowdtemplate` i `cwdspline` (trawa i widzowie: gra rysuje je jako animowane sprity, nie mają geometrii).
- Każdy plik należy do **warstwy**, odczytanej z jego nazwy po `c<size>_<category>_`. Słowo poziomu szczegółowości (`do`, `so`, `ulc`, `ulp`, `cwd`) i opcjonalny numer sekcji oznaczają świat wolnej jazdy. Wszystko inne to warstwa, którą gra włącza: warstwa w czasie działania (`rt_0`), aktywność (`_tag_<name>_`), znajdźka, cokolwiek pod `evolving`. Warstwa nazywająca trasy (`rt_x<id>`, na przykład `rt_x1023_x2201`) należy tylko do tych wyścigów i jest czytana tylko wtedy, gdy okrążenie dopasowało się do jednego z nich. Zobacz [Warstwy włączane przez grę](#switched-on-layers).
- Kopia jest zachowywana, jeśli jej pozycja leży w pudełku i w korytarzu. Dokładne powtórki (ta sama pozycja i orientacja co do milimetra, wypisane przez dwie sąsiednie komórki) są scalane.
- **Krawężniki** to rekwizyty, których nazwa modelu zaczyna się od `road_gen_rum` (pasy wibracyjne). Są zapisywane jako `ground:kerbs`, nigdy nie są upraszczane ani pomijane, bo okrążenie mierzy się względem nich.

| Kategoria | Część | Kolor zapasowy (bez tekstury) |
|---|---|---|
| krawężniki | `ground:kerbs` | 0,60, 0,12, 0,10 |
| bariery | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekwizyty | `structure:props` | 0,45, 0,35, 0,25 |
| znaki | `structure:signs` | 0,70, 0,70, 0,70 |
| budynki | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastruktura | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| mosty | `structure:bridges` | 0,45, 0,45, 0,45 |
| skały | `structure:rocks` | 0,30, 0,28, 0,25 |
| rzeczy do roztrzaskania | `structure:smashables` | 0,12, 0,22, 0,06 |
| drzewa, krzewy | `structure:trees` | 0,10, 0,20, 0,05 |

### Geometria modelu {#the-models-geometry}

Nazwa umieszczona `<model>_3D` odwołuje się do plików modelu `<model>_cluster###.i.modelbin`
(do kilkunastu). Każdy trójkąt niesie maskę poziomów szczegółowości, do których należy:

- Poziomy modelu to jego trójkąty jawnie oznaczone dla tego poziomu. Poziomy idą ciągiem od 0, najdokładniejszy pierwszy.
- Trójkąty oznaczone `0xFFFF` (każdy poziom) to elementy, które dają się rozbić, na przykład słupki bariery czy pojedyncze opony stosu opon. Nakładają się na cały model, a gra rysuje je zamiast niego, gdy zostanie rozbity. Używa się ich tylko przy modelu bez jawnie oznaczonego poziomu.
- Podsiatki, których materiał ma shader rzutowanej **dekali**, są pomijane.

Każda kopia jest umieszczana według swojej pozycji, swoich osi x i y z rekordu
(z = x iloczyn wektorowy y) i skali. Normalne są przekształcane odwrotnością skali.

### Która tekstura {#which-texture}

Materiał nie nazywa swoich tekstur. Wymienia je jako hashe, a `AssetManifest.xml`
toru mapuje każdy hash (`SourceHash`) na nazwę tekstury. Czyta się tylko sekcję
`<Textures>`, a czytanie zatrzymuje się na `</Textures>` w pliku, który może mieć
dziesiątki megabajtów. Potem:

1. Slot `0x88B483AA` to kolor bazowy w standardowym shaderze środowiska (każdy próbkowany materiał). Jeśli materiał wiąże tam teksturę, ta jest używana.
2. Inaczej decyduje rodzaj samej tekstury, czyli słowo przed jej GUID: `_bclr_`, potem `_diff_`, potem `_colour_`.
3. Mapy terenu (`mainmap`, `submap`, `autogloss`) i palety odcieni (`tint`, `worldtint`) nigdy nie kolorują modelu.

Model jest więc kolorowany tym, co wiąże jego materiał, a nie teksturą nazwaną
jak sam model. Na przykład `bar_rur_armco_crct_02_c` używa tekstury `..._02_a`.

Tekstura jest czytana z archiwów w najmniejszej rozdzielczości, która ma co najmniej
**256 px** w szerokości (`MODEL_TEXTURE`), zmniejszana do 256, jeśli jest większa,
i zapisywana jako RGB JPEG w `.glb`. Kolor bariery z taśmy przy 256 px dla czterech
metrów to 1,6 cm na piksel, a w atlasie przeglądarki mieści się około 80 takich
tekstur obok kafli gruntu.

**Pory roku.** `--season` zamienia teksturę na jej sezonowy odpowiednik po nazwie,
z pominięciem GUID (`..._xsummerx_bclr` na `..._xwinterx_bclr` albo `..._bclr` na
`..._winter_bclr`), jeśli tor ma taki. Przy `--season winter` materiał zimowy podsiatki
jest też używany tam, gdzie wskazuje go jej tabela wariantów.

**Warianty.** Rekord podsiatki otwiera się tabelą par `(summer, winter)` materiałów,
po jednej na wygląd, jaki może mieć kopia: pięć nadruków na billboard, sześć kolorów
farby na stos opon. Każdy rekord rozmieszczenia mówi, który wariant nosi dana kopia.
Podsiatka z mniejszą liczbą wariantów niż model powtarza własne.

**Blok zastępczy.** Wspólne atlasy budynków rezerwują pełny blok RGB (255, 64, 0) dla
powierzchni, które shader budynku barwi z innych tekstur. Jeśli więcej niż jedna
dwudziesta tekstury jest w odległości 12 poziomów od tego koloru, blok jest
przemalowywany średnim kolorem tekstury. W przeciwnym razie całe miasto wychodzi pomarańczowe.

### Powierzchnie przezroczyste {#see-through-surfaces}

Płoty z siatki i sieci to pojedyncze czworokąty z dziurami w alfie tekstury. Narysowane
pełne, płot jest ścianą w poprzek widoku na tor. Powierzchnie, których materiał ma shader
pasujący do `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`,
`bush` albo `tree`, są sprawdzane:

- Krycie tekstury jest uśredniane po siatce 32 x 32.
- Dla każdej powierzchni (każdego trójkąta z wyciętymi dziurami dzielącego jedną teksturę) w przestrzeni UV pobiera się cztery punkty na trójkąt, ważone polem UV trójkąta.
- Jeśli średnie krycie wynosi co najmniej 0,05 i poniżej **0,5**, cała powierzchnia jest pomijana. Poniżej 0,05 alfa znaczy dla jej shadera coś innego (znak ostrzegawczy, który próbkuje 0,01), więc powierzchnia zostaje pełna.
- Model, którego każda powierzchnia została pominięta, jest zgłaszany: `N models left out as see-through (mostly holes in their texture)`.

Narzędzie ocenia całą powierzchnię, a nie pojedynczy trójkąt. Oceniane po trójkącie
połowa każdego czworokąta przeżywała i płoty wychodziły jako rzędy zębów.

### Budynki narysowane w całości {#buildings-drawn-whole}

Miasto buduje budynki z modularnych części: setki tysięcy wokół jednego ulicznego
toru, dziesiątki milionów trójkątów nawet w najgrubszym poziomie. Pomijanie części
pojedynczo zostawiało samotne płyty ścian. Gra dostarcza też w `scene\hlod_tier_1\`
całe zastępcze budynki, po jednej siatce na budynek (nazwa `hlod_tier_1_*`), już we
współrzędnych świata jak teren:

- Pudełko świata każdego zastępcy jest czytane z pudełka pozycji jego siatki (odczyt nagłówka, nie dekodowanie). Dla całej mapy trwa to sekundy.
- Używane są zastępcy dotykający pudełka okrążenia i korytarza.
- Każda część `buildings`, której pozycja leży w obrysie zastępcy (plus 0,5 m), jest pomijana, a rysowany jest zastępca. Jego odległość od jazdy mierzy się do najbliższej krawędzi budynku.
- Podsumowanie mówi `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Warstwy włączane przez grę {#switched-on-layers}

To, co włączona warstwa umieszcza, jest eksportowane, ale osobno od świata wolnej
jazdy, żeby przeglądarka mogła je pokazać lub ukryć:

| Warstwa | Część |
|---|---|
| świat wolnej jazdy | `structure:<category>` (jak dotąd) |
| warstwa nazywająca trasę dopasowanego wyścigu | `structure:event_<category>` |
| każda inna włączona warstwa | `structure:layer_<category>` |

Podsumowanie je liczy: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modele już we współrzędnych świata {#models-already-in-world-coordinates}

Kilka rodzajów modeli nie jest w żadnym pliku rozmieszczenia. Ich siatki niosą własną
pozycję w świecie, jak teren, więc nic ich nie musi ustawiać:

| Folder pod `scene\models\` | Co to jest | Część |
|---|---|---|
| `plots` | własny grunt areny: podłoga i wnętrze stadionu, teren festiwalu, plac | `ground:venue` |
| `plinths` (i każdy model o nazwie `floor`, `ground` albo `road`) | grunt, którym ubrano ulicę: donice, schody, nawierzchnia parku | `ground:plinths` |
| `hda_infrastructure` (mosty) | proceduralnie budowane mosty | `structure:bridges` |

- Model uznaje się za będący we współrzędnych świata, gdy środek jego pudełka leży dalej niż **300 m** (`WORLD_REACH`) od jego własnego punktu początkowego. Modele umieszczone przez pliki rozmieszczenia leżą w obrębie kilkuset metrów od swoich.
- Nie są rysowane: zasłaniacze, kable rozciągnięte wzdłuż dróg, tło morza, dachy i zasłaniacze modularnych budynków (zastępcy rysują te budynki), bryły kolizji i wody.
- Każdy jest czytany z pudełka swoich siatek (odczyt nagłówka), kilka sekund na całą mapę, raz na przebieg.
- Części gruntu nigdy nie są rysowane grubiej i nigdy nie są pomijane, by zmieścić się w budżecie, tak jak krawężniki.

**Arena jest wycinana w całości.** Gdy jazda dotyka gruntu areny (`ground:venue`),
korytarz jest poszerzany do pełnego obrysu tego gruntu plus `--margin`, więc trybuny,
mury i bariery wokół stadionu przychodzą razem z nim, a nie tylko pas, po którym jeździły
okrążenia. Konsola pisze `through a venue (<model names>): cutting all of its ground, <n> km2`.
Plinths nie poszerzają wycinka.

### Szczegółowość i budżet {#detail-and-the-budget}

Pasma odległości, budżet i to, które kopie znikają, gdy budżet jest za mały, są opisane na
stronie [Poziomy szczegółowości i budżet](detail-budget.md).

### Podsumowanie rozmieszczenia {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## Warstwa własna wyścigu {#the-races-own-layer}

Wiele wyścigów wystawia rzeczy, których nie ma w wolnej jeździe: betonowe ściany i
ogrodzenia zamykające boczne drogi, stosy opon, namioty, bramę startową, trybuny,
flagi, banery. Każdy wyścig wymienia je w swojej definicji trasy
(`route<id>_<map>.rtd` w `routedefinitions.zip`, zwykły XML w zwykłym zipie):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **Co jest dodawane.** Każdy wpis jest umieszczany jak kopia z pliku rozmieszczenia. 16 liczb przekształcenia to cztery wiersze: osie x, y i z modelu (każda przeskalowana) oraz jego pozycja w metrach gry. Trzeci wiersz to iloczyn wektorowy dwóch pierwszych. `Material` to wariant, który nosi kopia. Częścią jest `structure:event_<kind>`, gdzie `<kind>` to folder pod `scene\models\` (barriers, props, infrastructure, signs; cokolwiek innego liczy się jako props), a węzeł niesie dodatki glTF `{"layer": "event", "route": <id>}`.
- **Co jest usuwane.** Kopia z wolnej jazdy stojąca w odległości **0,1 m** od pozycji ukrytego zasobu jest pomijana. Ukryty zasób stojący w początku układu jest modelem we współrzędnych świata; jego GUID instancji wyszukuje się w `AssetManifest.xml` toru (lista `<Models>`: źródło modelu, potem GUID jego kopii), żeby go nazwać.
- **Grunt ukryty przez wyścig jest zachowywany.** Wyścig, który ukrywa grunt areny, kładzie tam własną powierzchnię. Gdy ta powierzchnia nie jest wśród modeli, które dostarcza tor, ukryty grunt zostaje jako najbliższa rzecz do tego, po czym się jeździ, a podsumowanie to mówi (`kept <model>: the race hides it for a surface of its own
  that the track does not ship`).
- **Nie rysowane, ale liczone.** Markery widzów (`crowd_proxies`: gra rysuje tłum jako sprity na ich podstawie) i splajny kolizji (`.splinecol`). Konsola je wypisuje: `its own layer: <n> copies of <m> models, <k> free-roam
  objects hidden; not drawn: ...`.
- Wpisy trasy, do których tor nie dostarcza modelu (poświaty świateł, niektóre znaki, treści, które gra strumieniuje w trakcie), są wymienione w `placed names have no model in the archives`.

Umieszczane są tylko kopie wewnątrz korytarza, tak jak dla wszystkiego innego.

## Zapisywanie pliku {#writing-the-file}

Części są zapisywane w tej kolejności: dla każdego kafla `terrain`, `verge`, `road` (każdy z obrazem kafla), potem `water`, `tyre marks`, `markings` (płaskie, dwie ostatnie podniesione), a potem każda umieszczona część posortowana po nazwie. Współrzędne są grą własne (metry, Y w górę). Zobacz [Format pliku wyjściowego](output-format.md).

Plik mówi, co zawiera, w `asset.extras` swojego glTF:

| Pole | Znaczenie |
|---|---|
| `course_format` | `2`: warstwa własna wyścigu, areny i modele we współrzędnych świata są w nim. [`courses`](commands.md#courses) eksportuje ponownie plik z niższym numerem (albo bez niego) |
| `route` | identyfikator dopasowanej trasy albo `null` |
| `event_copies`, `event_kinds` | ile kopii warstwy własnej wyścigu umieszczono i ich rodzaje |
| `hidden` | kopie wolnej jazdy pominięte, bo wyścig je usuwa |
| `venue` | modele gruntu aren, przez które przebiega jazda |
| `layers` | umieszczone włączane warstwy |

## Ile to kosztuje {#what-it-costs}

Rzędy wielkości:

| Tor | Wynik |
|---|---|
| krótki wiejski tor | kilkaset tysięcy trójkątów terenu, ponad milion umieszczonych; sekundy, poniżej 100 MB |
| długi sprint punkt-punkt | korytarz to niewielka część pudełka wokół niego; około minuty, kilkaset MB |
| uliczny tor miejski | tysiące barier, rekwizytów i znaków oraz całe budynki; przy automatycznym budżecie do kilkuset MB |

Kilometr kwadratowy terenu otwartego świata to około milion trójkątów.

## Sprawdzenia, na których to się opiera {#checks-behind-it}

To są pomiary wykonane podczas pisania czytnika, jak podano w źródle. Testy ich nie
powtarzają, chyba że gra jest zainstalowana.

- Na torze testowym samochód stoi około swojej wysokości jazdy nad wyciągniętym gruntem (mediana poniżej 0,2 m).
- Każdy próbkowany kafel leży w kwadracie 512 m, który przewiduje jego nazwa.
- Kolejne umieszczenia barier są dokładnie 4 m od siebie, a większość końców barier leży w odległości 5 cm od początku następnej.
- Krawężniki stoją kilka centymetrów nad wyciągniętym gruntem, twarzą do góry, w odległości 5 m od jazdy (także test w zainstalowanej grze, zobacz [Rozwój](development.md)).

## Nie jest rysowane {#not-drawn}

- Drzewa i krzewy, chyba że `--trees`. Trawy i tłumów nigdy (gra rysuje je jako sprity).
- Modele własne wyścigu, których tor nie dostarcza (zobacz [Warstwa własna wyścigu](#the-races-own-layer)).
- Materiały dekali rzutowanych na modele.
- Nadruki znaków, które są półprzezroczyste na tablicy, wychodzą nieprzezroczyste.
- Kolor gruntu to rekonstrukcja tego, gdzie są asfalt, trawa i las, a nie własne materiały terenu gry.
