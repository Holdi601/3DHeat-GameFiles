---
title: Ograniczenia i znane braki
nav_order: 10
lang: "pl"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Ograniczenia i znane braki {#limits-and-known-gaps}

Czego narzędzie nie robi, co robi tylko częściowo i gdzie jego zachowanie jest nierówne. Większość braków to celowe odmowy. Dekodowanie bez pliku, z którym można by to porównać, daje wynik, który wygląda dobrze, a nie jest dobry.

## Gry {#games}

| Gra | Eksport trasy | Dlaczego nie, albo jak daleko |
|---|---|---|
| Forza Horizon | tak | kolor podłoża to interpretacja (zob. niżej) |
| BeamNG.drive | tak | brak roślinności podłoża, powtarzające się tekstury modeli spłaszczone |
| Assetto Corsa Rally | tak | modele w jednolitych kolorach; jeszcze nie przetestowano na okrążeniu nagranym w grze |
| Assetto Corsa EVO | **nie** | cała zawartość jest w jednym pakiecie zaciemnionym kluczem, a narzędzie nie odzyskuje kluczy |
| Battlefield 6 (eksport poziomu, `level`) | tak, cały poziom | teren, zgrupowane i pojedynczo umieszczone siatki wraz z mapami kolorów, siatka nawigacyjna żołnierzy, wycinane roślinności; kolor podłoża w obszarze gry jest gruby (32 m na piksel albo jeden średni kolor); bez przezroczystości i map normalnych; siatki niszczalne oznaczone, ich zniszczone stany nie są eksportowane |
| Gry na Unreal 5 z World Partition (eksport mapy, `ue-map`) | tak, cała mapa | landscape dokładny; budynki jako uproszczone siatki HLOD mapy, nie pełnoszczegółowe modele; zbiorniki wodne; bez roślinności, nakładek i koloru podłoża |
| Arma Reforger (eksport świata, `enfusion-world`) | tak, cały świat | teren we własnych kolorach i morze; budynki, rekwizyty i skały jako pudełka z modeli, nie ich trójkąty; drzewa na żądanie (`--trees`), jako pudełka; bez jezior, rzek i encji potomnych |
| iRacing | **nie** | tory są dostarczane w chronionym formacie, który nie jest celem wyciągania plików |
| cokolwiek innego | **nie** | nie ma czytnika tras; odtwórz podłoże z gameplayu w 3DHeat GameCapture albo analizuj okrążenia w zakładce Analiza wyścigowa przeglądarki bez trasy |

## Silniki i formaty {#engines-and-formats}

| Format | Nieobsługiwane |
|---|---|
| Unreal `.pak` | wersje przed 8; indeksy zawierające tylko skróty ścieżek (nazw nie da się odzyskać); wpisy na liście przepełnienia indeksu (pomijane); dekodowanie zawartości `.uasset`/`.umap` z pak |
| Unreal IoStore | zaszyfrowane kontenery (odmawiane, brak opcji klucza); wyświetlanie kontenera bez indeksu katalogów (nie nazywa plików); pakiety versioned; siatki tylko Nanite i siatki nieumieszczone wewnątrz; skeletal meshes; właściwości klas bez schematu; właściwości komponentów instancjonowanych (układ zmieniony w buildzie gry); komponenty splajnowe i komponenty nakładek |
| Unity | formaty sprzed 22 (Unity 2019 i starsze); pliki z osadzonymi drzewami typów; skompresowane siatki; każda klasa poza `Mesh`, więc bez transformacji, materiałów i scen; `meshes` na pakiecie; `list`/`extract` (użyj `meshes`) |
| Frostbite | tabele zaciemnione XOR; graf warstw terenu (maski odczytane w około jednej trzeciej sprawdzonych poziomów); blueprinty obiektów inne niż siatki (logika gry, efekty, dźwięki); siatki poziomów przechowywane wewnątrz; mapy normalnych i inne mapy, alfa inna niż wycinanki; dziury w terenie; biblioteka typów (zaszyfrowana w początkowym systemie plików, nie jest dotykana); polecenie wyświetlające lub wyciągające pojedyncze zasoby |
| Source 2 | zasoby skompilowane (`.vmdl_c`, `.vtex_c`); siatka nawigacyjna CS2 (wersja 36) |
| ForzaTech | formaty pozycji inne niż cztery przeskalowane shorty; formaty indeksów inne niż u16; kody tekstur inne niż 0, 9, 13; warstwy materiałów shadera terenu; tangenty |
| BeamNG | siatki ze szkieletem i siatki nakładek; animacja; proceduralna roślinność podłoża; scenografia na krawędzi świata |
| Landscape Unreal i mapy World Partition | landscape, których mapy wysokości leżą w zapieczonych komórkach; warstwy edycji i dziury; siatki landscape Nanite; pełnoszczegółowe modele umieszczone w komórkach; roślinność; materiały landscape |
| Enfusion | trójkąty modeli (geometria `.xob` jest skompresowana w układzie, którego nie czytamy); `.edds` z nagłówkami sprzed DX10; wartości zagnieżdżonych obiektów w plikach świata (pomijane, liczone); encje potomne; generowane jeziora i rzeki; `list`/`extract` na `.pak` |

## Zachowania, które warto znać {#behaviour-worth-knowing}

- **Kolor podłoża Forzy nie jest kolorem gry.** Zapieczona tekstura jest rysowana z map kafelków, które mówią, *gdzie* są asfalt, krótka trawa, teren nierówny i zadrzewienie. Używa stałych kolorów i cieniowania, bo warstwy materiałów własnego shadera terenu nie są dekodowane.
- **`--no-textures` usuwa także pobocze Forzy.** Podział asfalt/pobocze używa maski asfaltu, która przychodzi z zapieczonymi mapami. Bez tekstur pasy drogi zostają całe jako droga.
- **Podany przez ciebie budżet może przekroczyć tylko krawężnik.** Krawężniki (a w BeamNG modele nawierzchni jezdni) nigdy nie są upraszczane ani pomijane, w żadnej grze, więc budżet mniejszy niż ich koszt przekroczą one same; wszystko inne jest najpierw pomijane. Zobacz [Poziomy szczegółowości i budżet](detail-budget.md).
- **Opcje, które nie dotyczą danej gry, są cicho ignorowane**: `--season` dla BeamNG i AC Rally, `--track` dla BeamNG i AC Rally, `--level`/`--install` dla Forzy.
- **Kolor podłoża poziomu Battlefield 6 jest gruby z dala od nakładek.** Mapa wysokości dostaje kolor z mapy kolorów tła terenu, 32 m na piksel przy największym mipie, jaki poziom zawiera, albo, gdy żadna mapa tła jej nie pokrywa, średni kolor materiałów powierzchni terenu; `--ground-texture` mnoży to przez mapę kolorów terenu (przy 0,5 m na piksel, gdzie poziom ją ma) i zapieka w nim drogi, place, linie pasa startowego, ślady opon i oznaczenia, w kolorze farby ich materiału, gdy jest ustawiony, a neutralnym, gdy nie jest; maski wariacji drogi są pomijane. Gra miesza warstwy powierzchni w grafie shaderów, który nie jest odczytywany; eksport rozkłada kolory warstw według ich masek i nachylenia mapy wysokości, zgodnie z własną regułą, a poziom, którego mapy masek do siebie nie pasują, dostaje jeden kolor. Każda warstwa to średnia jej mapy kolorów, a nie jej tekstura. Zobacz [Frostbite](reader-frostbite.md#terrain-layers). Fragmenty mapy wysokości w różnej rozdzielczości łączą się małymi schodkami.
- **Mapa kolorów Battlefield 6 jest wybierana, nie odczytywana.** Blok shadera wymienia każdą teksturę, którą próbkuje, bez mówienia, która jest kolorem; wybór idzie po nazwie (zob. [Frostbite](reader-frostbite.md#textures-and-materials)) i może wziąć arkusz detali albo wykończenia dla powierzchni. Arkusze nakładek (`t_de_...`) przegrywają z własną mapą powierzchni; nakładka znaku narysowana jako jego panel, z tarczą obróconą o ćwierć, jest błędem. Mapy odległości, palety i maski kanałów nigdy nie są brane. Budynki tła są rysowane w kolorach swojej palety; mapy szarości przyjmują tint materiału według reguły eksportera, bo nazwy parametrów są zahaszowane, a materiał, który maluje mapę szarości przez maskę z kilkoma tintami, dostaje jeden z nich.
- **Dziury w terenie Battlefield 6 nie są wycinane.** Tam, gdzie chodliwe podłoże poziomu leży pod mapą wysokości, gra musiała wyciąć teren, a eksport tego nie robi. Wykluczono jako miejsca dziur: maski warstw terenu (żadna nie skupia się tam), jego raster 67 x 67 węzłów, zarezerwowaną wartość wysokości (żadna strona wysokości nie zawiera 0 ani 65 535), flagi węzłów (wszystkie takie same) oraz siatki lub zasoby, które przecinają podłoże: pod podłożem tam stoją skały i klify, a żaden zasób poziomu nie jest nazwany od dziur, tuneli czy jaskiń. Dwa drzewa rastrowe są dekodowane przez długość serii, ale nie są umieszczane, i to one pozostają (zob. [Frostbite](reader-frostbite.md#terrain-layers)).
- **Wariacja obiektu Battlefield 6 dociera do sekcji przez bliźniaki.** Wariacja umieszczonej kopii wybiera bloki shaderów jej sekcji po kluczu; gdy siatka nie ma bloku dla wariacji, bierze się wariant sekcji innej siatki z identycznym domyślnym blokiem (zob. [Frostbite](reader-frostbite.md#textures-and-materials)). To reguła eksportera; sekcja bez bliźniaka, która się zmienia, zachowuje swój domyślny wygląd.
- **Warstwowe materiały Battlefield 6 są rysowane jako ich baza i jeden arkusz.** Ściana z napisami jest rysowana jako jej tynk z arkuszem liter na wierzchu; pozostałe warstwy materiału (nałożony brud przez maskę, mapy detali i mchu) nie są mieszane.
- **Siatka nawigacyjna należy do SI, nie do graczy.** Obejmuje to, dokąd może dojść żołnierz: podłoże, podłogi i schody, i niektóre dachy, ale nie każde wysokie miejsce. Połączenia między powierzchniami (skoki, drabiny, przeskoki) są pomijane.
- **Poziom Battlefield 6 zawiera warstwę każdego trybu gry.** Obiekty, które stawia tylko jeden tryb, mogą się nakładać na inny. `--skip` pomija warstwy po nazwie.
- **`courses` działa tylko dla Forzy** i bierze tylko foldery bibliotek nazwane `... (course_...)`.
- **Ramka okrążenia BeamNG jest zakładana** jako ramka przeglądarki `(x, z, -y)`, którą zapisuje rejestrator 3DHeat. Okrążenia z innego rejestratora, w surowej ramce BeamNG, nie zostaną umieszczone.
- **`list` i `extract` biorą archiwa, nie każdy format.** Otwierają `.pak`, IoStore `.utoc`, `.vpk`, `.minizip` i zip. Kontener Unity czyta się przez `meshes`, poziom Frostbite przez `level`, a `.cdae` albo `.ter` to plik, a nie archiwum (`identify` go nazwie). `.minizip` bez `ChunkContentsMiniZip<n>.txt` obok wyświetla się po numerze wpisu.
- **Umieszczone modele w BeamNG używają powtarzających się tekstur jako średnich kolorów**, bo sampler `.glb` przycina, a przeglądarka pakuje tekstury w atlas.
- **W praktyce tylko Windows.** Ścieżki Steama w `C:\Program Files`, `%LOCALAPPDATA%`, `C:\XboxGames` oraz `*_win64.dll` dla Oodle. Inne platformy nie były testowane.

## Niesprawdzone {#unverified}

- Starsze wersje Pythona (narzędzie było uruchamiane na 3.13).
- Assetto Corsa Rally z okrążeniem nagranym w grze. Testowano tylko syntetyczne okrążenia w losowych ramkach.
- Przeglądarki glTF inne niż przeglądarka 3DHeat.
- Czy ramka każdej gry jest lewo-, czy prawoskrętna. Eksport zachowuje ramkę telemetrii każdej gry, więc okrążenia i trasy i tak się zgadzają.
- Znaczenie `z = 0` lokalnego `WaterBlock` jako powierzchni (BeamNG).
- Umieszczanie we Frostbite w grach innych niż Battlefield 6 oraz w Battlefield 6 po aktualizacji, która zmienia układ członka grupy. Czytnik wtedy nie znajduje grup i mówi o tym.
- Czy eksport Battlefield 6 zgadza się z pozycjami, które podaje gra. Współrzędne są samej gry, jak w innych grach, ale żadne nagranie nie zostało jeszcze na nim nałożone.
