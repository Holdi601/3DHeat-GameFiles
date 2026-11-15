---
title: "Unity: `SerializedFile`, pakiety, siatki"
nav_order: 4
lang: "pl"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, pakiety, siatki {#unity-serializedfile-bundles-meshes}

**Wypisuje obiekty i dekoduje siatki** plików Unity `SerializedFile` w formacie 22 i nowszym (Unity 2020 do 6000), oraz otwiera pakiety `UnityFS`. Nie ma eksportu trasy Unity.

Źródła: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Polecenia: `identify` (kontenery i pakiety), `meshes` (tylko gołe kontenery).

## Kontener {#the-container}

Unity dostarcza poziom jako serializowane grafy obiektów: `globalgamemanagers`, `sharedassets*.assets`, `resources.assets`, `level*` oraz pakiety zasobów. Każdy ma tabelę obiektów oznaczonych identyfikatorem klasy.

Nagłówek to miejsce, gdzie czytanie cicho się psuje. Pierwsze szesnaście bajtów to cztery `uint32` w big-endian, zachowane dla zgodności. W formacie 22 trzy z nich są zerami, a prawdziwe wartości idą za nimi, bo plik może przekroczyć 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Drugi `metadata size` to `uint32` między dwoma `int64`. Założenie, że wszystkie trzy są 64-bitowe, przesuwa łańcuch wersji o cztery bajty w prawo. Nadal dekoduje się to do czegoś, co wygląda jak napis, i wysyła wszystko za nim na manowce. Nagłówek jest big-endian. Wszystko po nim idzie za bajtem endianness (0, little-endian, we wszystkich wersjach desktopowych).

Po nagłówku: ciąg wersji silnika, platforma, flaga drzewa typów, tabela typów (identyfikator klasy na typ), tabela obiektów (identyfikator ścieżki, przesunięcie, rozmiar, typ) i zewnętrzne (inne pliki, do których może wskazywać wskaźnik).

| Przypadek | Wynik |
|---|---|
| format 22-30 | czytany |
| format 9-21 (przed Unity 2020) | odrzucany: przesunięcia są w starym nagłówku, a żaden posiadany plik go nie używał |
| poza 9-30 | odrzucany |
| osadzone drzewo typów (buildy edytorskie) | odrzucany: buildy dystrybuowane nie osadzają go, a ścieżka edytora nie jest zaimplementowana |
| pakiet podany tam, gdzie oczekiwano kontenera | odrzucany, ze wskazaniem czytnika pakietów |

**Nie ma ogólnego deserializatora.** Buildy dystrybuowane nie niosą drzewa typów, bo schemat jest wkompilowany w odtwarzacz, więc każda klasa musi być parsowana według układu znanego dla jej wersji. Dekoduje się tylko `Mesh`. Inne klasy są zgłaszane po nazwie i liczbie (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; inne jako `class<id>`).

**Sprawdzone** na wielu zainstalowanych grach i milionach obiektów: tabela obiektów musi pokrywać sekcję danych dokładnie, bez nakładania się, z niczym poza wypełnieniem wyrównania między obiektami i ostatnim obiektem kończącym się na ostatnim bajcie pliku. Błąd nagłówka nie może tego wytworzyć. Test na zainstalowanej grze powtarza to na do sześciu plikach `resources.assets` / `sharedassets0.assets` z folderów `*_Data`.

## Pakiety (`UnityFS`) {#bundles-unityfs}

Pakiet to skompresowany kontener plików `SerializedFile`. Lista bloków i katalog są też skompresowane. Metoda jest w niskich sześciu bitach słowa flag: 0 bez kompresji, 1 LZMA (5-bajtowy nagłówek Unity z wstawionym rozmiarem), 2 i 3 LZ4 / LZ4HC. Format 7 i nowsze wyrównują nagłówek do 16 bajtów. Flaga `0x80` ustawia katalog na końcu pliku. `UnityWeb`, `UnityRaw` i `UnityArchive` (sprzed 5.3) są rozpoznawane, ale nie są czytane.

## Siatki {#meshes}

`read_mesh` dekoduje obiekt `Mesh` do pozycji, normalnych, pierwszego zestawu UV i trójkątów, w kolejności, w jakiej Unity 2019+ je zapisuje: nazwa, podsiatki, blend shapes (pomijane), pozy wiązania i dane kości (pomijane), flagi kompresji i czytelności, bufor indeksów, kanały wierzchołków i dane wierzchołków, blok siatki skompresowanej, lokalne pudełko ograniczające i informacje o strumieniowaniu.

- **Wierzchołki zewnętrzne.** Większość dostarczanej geometrii leży w pliku `.resS` obok kontenera. Narzędzie czyta go z folderu kontenera (używana jest tylko nazwa pliku z zapisanej ścieżki `archive:/...`). Brakujący `.resS` to błąd, a nie pusta siatka.
- **Strumienie i kanały.** Kanały mówią, który strumień, przesunięcie, format i wymiar ma każdy atrybut. Strumienie są upakowane jeden za drugim, każdy dopełniony do 16 bajtów, więc początek strumienia to suma kroków przed nim.
- **Topologia.** Tylko trójkąty (topologia 0). Paski, czworokąty i linie są odrzucane, bo złe przekształcenie wygląda jak prawdziwa geometria.
- **Siatki skompresowane** (kwantyzowane delty) są odrzucane: "mesh '...' is stored compressed; that encoding is not implemented".

### Samokontrola {#the-self-check}

Odczyt struktury w złej kolejności nie zgłasza błędu. Daje wiarygodnie wyglądające liczby. Dlatego każda zdekodowana siatka jest sprawdzana względem **pudełka ograniczającego, które Unity dla niej zapisało**, obliczonego przez edytor z prawdziwych wierzchołków. `aabb_matches()` przechodzi, gdy rogi zdekodowanego pudełka leżą w granicach 2% rozmiaru zapisanego pudełka. `meshes` wypisuje `ok` albo `BOUNDS DISAGREE` w każdej linii.

**Sprawdzone:** siatki próbkowane w kilku grach dekodują się, a ich pudełka się zgadzają. Test na zainstalowanej grze powtarza sprawdzenie na zainstalowanych kontenerach.

## Nieobsługiwane {#not-implemented}

- Formaty sprzed 2020.
- Siatki skompresowane.
- Każda klasa poza `Mesh`: brak grafu sceny, transformacji i materiałów, więc siatki są w swojej lokalnej przestrzeni.
- `meshes` na pakiecie. Czytnik pakietów istnieje w Pythonie (`UnityBundle.serialized_files()`), ale polecenie bierze gołe kontenery.
