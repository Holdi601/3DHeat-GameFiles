---
title: Naredbe
nav_order: 2
lang: "hr"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Naredbe {#commands}

Svaka naredba pokreće se kao `python -m heat3d_gamefiles <radnja> ...` iz mape repozitorija. Radnje su poredane onim redom kojim ih obično trebate: što je ova datoteka, što je u njoj, daj mi taj dio, i pretvori krug u stazu.

| Naredba | Ulaz | Što radi |
|---|---|---|
| [`identify`](#identify) | bilo koju datoteku | imenuje format spremnika čitajući njegove bajtove |
| [`list`](#list) | Unreal `.pak` ili IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip` ili zip | popisuje njegove stavke |
| [`extract`](#extract) | isto | zapisuje jednu stavku na disk |
| [`meshes`](#meshes) | Unity `SerializedFile` | popisuje i provjerava njegove mreže |
| [`course`](#course) | krug | izvozi stazu oko njega (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | biblioteku snimljenih krugova | pokreće `course` na svakoj stazi u njoj (Forza) |
| [`races`](#races) | instaliranu Forzu | popisuje svaku utrku koju igra definira: što dodaje, što skriva, mjesta održavanja, stanje njezina izvoza |
| [`terrain`](#terrain) | mapu staze Forze | izrezuje područje po svjetskim koordinatama |
| [`levels`](#levels-and-level-frostbite) | instaliranu Frostbite igru (Battlefield 6) | popisuje njezine razine |
| [`level`](#levels-and-level-frostbite) | ime razine | izvozi razinu: teren, postavljene mreže, po izboru i njihove mape boja (Battlefield 6) |
| [`cars`](#cars) | instaliranu Forzu | svako vozilo u niskoj razini detalja, u jednoj datoteci za karticu Analiza utrke u pregledniku |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | igru na Unreal 5 | popisuje njezine karte World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | ime karte | izvozi kartu: teren, HLOD strukture, vodu |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | instaliran Arma Reforger | popisuje njegove svjetove |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | ime svijeta | izvozi svijet: teren u njegovim bojama, more, zgrade kao kutije |

**Kako čitati primjere:** `<x>` znači da zamijenite to vlastitom vrijednošću, bez kutnih zagrada; `[...]` je izborno; put s razmacima stavite u "dvostruke navodnike", na primjer `"C:\Games\My Game"`. Prvi put ovdje? Pogledajte [Prije nego što počnete](before-you-start.md). Puni `--help` svake naredbe nalazi se na [stranici s referencom naredbi](../cli-reference.md).

Pri svakom pokretanju program može prvo provjeriti ima li novije izdanje. Pogledajte [Ažuriranja](updates.md). `HEAT3D_NO_UPDATE=1` isključuje tu provjeru.

Izvor: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Stranice korak po korak: [Pregled arhiva](inspecting-archives.md), [Izvoz staze](course-export.md), [Cijele razine](whole-levels.md), [Forza automobili](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Izlazni kodovi {#exit-codes}

| Kod | Značenje |
|---|---|
| 0 | uspjeh |
| 1 | rad nije uspio (nečitljiv krug, nije nađena igra, nema što izvesti, staza u `courses` nije uspjela; za `list` i `extract`, datoteka koja nije nijedan od arhiva koje ove naredbe čitaju, datoteka koja se ne može otvoriti ili pročitati - šifrirani pak bez `--key`, šifrirani IoStore spremnik - ili stavka koje nema u arhivu) |
| 2 | loši argumenti (argparse), put koji ne postoji, `--key` koji nije 64 heksadecimalne znamenke, ili `terrain` dobiven i oboje ili nijedno od `--box` i `--route` |

Greške naredbi `list` i `extract` svaka je jedan redak na standardnom izlazu za greške, a ne Python traceback.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Naredba čita datoteku i kaže koji je to spremnik. Ne gleda ekstenziju (jedina iznimka je `.ucas`, dolje). Formate isprobava ovim redom i staje na prvom koji se može raščlaniti:

1. **Unreal `.pak`**: podnožje s pak oznakom u posljednjih 1,024 bajta. Ispisuje verziju, pomak i veličinu indeksa, je li indeks šifriran te metode kompresije.
2. **Unreal IoStore `.utoc`**: IoStore oznaka na početku. Ispisuje verziju, broj dijelova i je li spremnik šifriran; ako nije, broj datoteka koje imenuje njegov direktorij (i pod kojom točkom montiranja), metode kompresije i je li njegov `.ucas` pored njega. `.ucas` nema vlastito zaglavlje, pa se prepoznaje po `.utoc`-u istog imena pored njega, a `identify` imenuje tu datoteku.
3. **ForzaTech `.minizip`**: oznaka `PGZP`. Ispisuje verziju, broj stavki i segmenata te je li `ChunkContentsMiniZip<n>.txt`, koji imenuje stavke, pored njega (i, ako jest, imenuje li ih onoliko koliko ih ima).
4. **zip**: zip zaglavlje lokalne datoteke na početku. Ispisuje broj stavki, šest najčešćih ekstenzija i imena razina kada stavke leže pod `levels/<name>/`, kao u arhivu razine BeamNG.drive.
5. **Unity**: `UnityFS` paket (ispisuje verziju motora i broj stavki) ili goli `SerializedFile` (ispisuje format, verziju motora, broj objekata i šest najčešćih klasa).
6. **Frostbite `.toc`**: ispisuje vrstu (`plain` ili `signed`), gdje počinje stablo te ili broj resursa (binarna tablica dijelova) ili broj superpaketa (stablo DbObject).
7. **Source 2 `.vpk`**: ispisuje verziju, broj stavki i prvu `.nav` mrežu navigacije, ako je arhiv ima.
8. **BeamNG `.cdae`**: verzija oblika 31 koja se raščlani. Ispisuje broj mreža, broj nacrtanih razina detalja i prve materijale.
9. **BeamNG `.ter`**: nema oznake, pa sve mora biti usklađeno - strana od 2 do 16,384, toliko kvadriranih visina i bajtova slojeva, zatim 1 do 255 ispisivih imena slojeva. Ispisuje verziju, veličinu i imena slojeva.
10. **ForzaTech `.modelbin`**: ispisuje verziju, broj dijelova i šest najčešćih oznaka dijelova. Sadržaj dijelova se ovdje ne dekodira.

Formati s vlastitom oznakom (2 do 4) dolaze prije Unityja i Frostbitea, čije provjere čitaju cijelu datoteku: Forza arhiv je dug desetke gigabajta.

Ako se nijedan ne podudara, ispisuje se `not a format this tool reads` i zadnji razlog. Taj razlog dolazi iz provjere ForzaTech.

Primjer (izmišljen):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Opcija | Zadano | Značenje |
|---|---|---|
| `<archive>` | obavezno | Unreal `.pak`; IoStore `.utoc` (ili `.ucas` pored njega); Source 2 `.vpk` (za podijeljene VPK, `_dir.vpk`); ForzaTech `.minizip`; zip, kao arhivi razina i sadržaja BeamNG-a |
| `--filter TEXT` | nema | samo putevi koji sadrže TEXT, bez obzira na velika i mala slova |
| `--limit N` | 50 | ispiše najviše N stavki (ukupan broj se uvijek ispisuje) |
| `--key HEX` | nema | AES-256 ključ koji već imate, 64 heksadecimalne znamenke, s ili bez `0x`. Koristi ga samo šifrirani `.pak`. Sve što nije 64 heksadecimalne znamenke odbija se prije otvaranja arhiva (izlazni kod 2) |

Alat odlučuje o formatu prema bajtovima: sadržaj IoStorea, `.minizip` i VPK po potpisu kojim počinju, zip po zaglavlju lokalne datoteke, a `.pak` po podnožju na kraju. `.ucas` nema zaglavlje i otvara se preko `.utoc`-a istog imena. Datoteka koja nije nijedan od ovih formata odbija se porukom `<file> is not an archive list and extract read (...)`. Datoteka koja jest, ali se ne može otvoriti, odbija se s razlogom čitača: šifrirani pak bez `--key`, šifrirani IoStore spremnik, verzija paka koju alat ne čita. U oba slučaja to je jedan redak i izlazni kod 1.

Svaki redak prikazuje veličinu bez kompresije, metodu kompresije i put:

| Arhiv | Metoda | Putevi |
|---|---|---|
| `.pak` | `none`, ili naziv iz podnožja (`Zlib`, `Oodle`, `Gzip`...) | s točkom montiranja arhiva, na primjer `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, ili metoda spremnika (`Oodle`, `Zlib`...), kako je spremljen njegov prvi blok | s točkom montiranja, na primjer `../../../<Project>/Content/...`. Spremnik bez indeksa direktorija ne imenuje datoteke i odbija se |
| `.vpk` | uvijek `stored` | kako je u direktoriju |
| `.minizip` | `lz4`, `deflate` ili `stored` | kako ih piše `ChunkContentsMiniZip<n>.txt` pored `GeoChunk<n>.minizip`, bez prefiksa računala na kojem su građeni (obrnute kose crte, kako ih igra piše). Arhiv ne sprema imena, pa bez te datoteke stavke su `#0`, `#1`... Popis čiji se broj redaka razlikuje od broja stavki odbija se, jer ne pripadaju zajedno |
| zip | `stored`, `deflate`, ... | kako su spremljeni; mape se ne ispisuju |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Opcija | Zadano | Značenje |
|---|---|---|
| `<archive>` | obavezno | kao kod `list` |
| `<entry>` | obavezno | put točno kako ga ispiše `list` (osjetljivo na velika i mala slova); u `.minizip` radi i `#<broj>` |
| `--out FILE` | ime stavke (nakon zadnje `/` ili `\`), u trenutnoj mapi | kamo zapisati; nadređene mape se stvaraju |
| `--key HEX` | nema | kao kod `list` |

Stavka se dešifrira (pak, uz ključ), dekomprimira i zapisuje. Ispisuje `<bytes> bytes -> <file>`. Ako put nije u arhivu, naredba izlazi s kodom 1. Isto vrijedi i za stavku koju nije moguće pročitati (šifrirana stavka bez ključa, stavka komprimirana Oodleom bez Oodle biblioteke), s razlogom u jednom retku. VPK stavka se ovdje ne provjerava CRC-om. Čitač za to ima metodu `verify()` (vidi [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Opcija | Zadano | Značenje |
|---|---|---|
| `<path>` | obavezno | goli Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), a ne paket |
| `--limit N` | 25 | dekodira i ispiše najviše N mreža |

Ispisuje broj `Mesh` objekata, zatim po jedan redak za svaku mrežu: ime (prvih 40 znakova), broj vrhova i trokuta te `ok` ili `BOUNDS DISAGREE`. `BOUNDS DISAGREE` znači da dekodirani vrhovi ne reproduciraju okvir koji je Unity spremio za mrežu, u granici od 2% veličine okvira. To je vlastita provjera raščlanjivanja (vidi [Unity](reader-unity.md)). Mreža koja se ne može pročitati prijavljuje se s razlogom i ubraja se u granicu. Podaci vrhova u datoteci `.resS` čitaju se iz mape u kojoj je spremnik.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Ova naredba izvozi stazu oko kruga: teren u pojasu s obje strane vožnje i ono što na njemu stoji, kao jednu `.glb` datoteku. Ostalo sama odlučuje: koja igra, koja instalacija, koja staza, razina ili etapa i (za Assetto Corsa Rally) kako su osi okrenute. Vidi [Izvoz staze](course-export.md).

`<lap>` može biti bilo što od sljedećeg (pojedinosti u [Ulazni podaci kruga](lap-inputs.md)):

- datoteka kruga: JSON s rutom, JSON kruga FH Companion, JSON `heat3d-lap`, `.npz` ili `.csv` sa stupcima x, y, z
- mapa datoteka krugova, pretražena rekurzivno (cijela snimljena staza)
- **ime** staze, potraženo u biblioteci FH Companion na `%LOCALAPPDATA%\FHCompanion\laps`

### Opcije {#options}

| Opcija | Zadano | Igre | Značenje |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` u trenutnoj mapi | sve | kamo zapisati; ime se pretvara u mala slova, a nizovi ostalih znakova pretvaraju se u `_` |
| `--game {forza,beamng,acrally}` | što kaže datoteka kruga, inače `forza` | sve | iz koje je igre krug |
| `--margin M` | 80 | sve | metara tla zadržanih s obje strane vožnje |
| `--texture-size {2048,1024,512}` | 2048 | sve | pikseli teksture tla po pločici od 512 m (2048 = 25 cm po pikselu) |
| `--no-textures` | isključeno | sve | samo ravne boje: znatno manja datoteka. Za Forzu ovo također preskače podjelu ceste i ruba (vidi dolje) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | mape tla i teksture modela za koje godišnje doba |
| `--no-placed` | isključeno | sve | samo teren: bez rubnjaka, barijera, znakova i zgrada. Za BeamNG se površine vožnje modelirane kao mreže i dalje zadržavaju |
| `--trees` | isključeno | sve | dodaje i raslinje (Forza: drveće, grmlje i razbijajući objekti; BeamNG: drveće; AC Rally: drveće i instancirano raslinje) |
| `--detail-budget N` | automatski | sve | gornja granica trokuta za sve postavljeno; vidi [Razine detalja i proračun](detail-budget.md) |
| `--track DIR` | pretraži | Forza | mapa staze (pod `media\Tracks`, s `GeoChunk0.minizip`), ako se instalirana igra ne smije pretraživati |
| `--level NAME` | nađe se iz kruga | BeamNG, AC Rally | razina (ime mape u BeamNG-u) ili etapa (ime karte u AC Rally), bez obzira na velika i mala slova |
| `--install DIR` | traži se u Steam bibliotekama | BeamNG, AC Rally | BeamNG: mapa koja sadrži `gameengine.zip`. AC Rally: mapa igre, ili njezin `acr\Content\Paks` / `Content\Paks` |

Opcije koje se ne odnose na neku igru ignoriraju se bez upozorenja. Na primjer, `--season` ne radi ništa za BeamNG i AC Rally, a `--track` također ne radi ništa za njih.

### Koja igra {#which-game}

Igra se uzima iz `--game`, zatim iz polja `game` datoteke `heat3d-lap` (ili iz retka opisa `# {...}` u CSV-u), a inače je Forza. Mapa dobiva igru čije datoteke navode, kada navode samo jednu. Datoteka koja ne navodi nijednu (krug FH Companion, `course.json`, CSV bez retka opisa) se ne računa (vidi [Ulazni podaci kruga](lap-inputs.md)).

| Vrijednost | Izvoz |
|---|---|
| počinje s `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` ili `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | odbijeno: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | odbijeno: "tracks ship in a protected format that is not a file-extraction target" |
| sve drugo | odbijeno: "there is no course reader for <game> yet" |

Odbijanje također predlaže alternative: rekonstruirati stazu iz igranja (3DHeat GameCapture) ili analizirati krugove bez staze, jer kartica **Analiza utrke** u 3DHeat pregledniku iz njih crta cestu.

### Primjeri {#examples}

```
# Staza iz biblioteke FH Companion, po imenu
python -m heat3d_gamefiles course "Example Circuit"

# Jedna datoteka kruga, uža traka, manja datoteka
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Teksture za zimu, uključeno drveće
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Tvrda granica od 500,000 postavljenih trokuta
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Mapa staze zadana izravno (igra instalirana izvan Steama)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: navedite razinu, pokažite na instalaciju
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, s običnim CSV krugom koji ne kaže svoju igru
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Primjer ispisa (Forza, izmišljeni brojevi):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Svako vozilo instalirane Forze u niskoj razini detalja igre, u jednoj datoteci za karticu Analiza utrke u pregledniku: model `ProxyLOD` koji svaki arhiv vozila pod `media/Cars` nosi, otprilike 900 trokuta, s brojem vozila kako ga navodi telemetrija, markom, oznakom modela i godinom iz imena arhiva te kotačima i stražnjim svjetlima. Traje sekunde i zapisuje oko 5 MB. Pokrenite ponovno kada igra dobije nova vozila. Arhiv bez takvog modela (rekvizit u prometu) imenuje se i izostavlja. Format je opisan u [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Oblici su u metrima, kako ih ima igra: 1:1 s vozilom. Datoteka sadrži sadržaj igre, pa je namijenjena računalu na kojem je nastala, a ne za dijeljenje.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Ova naredba pokreće izvoz Forze `course` na svakoj mapi staze u snimljenoj biblioteci krugova i zapisuje po jedan `<name>.glb`. Samo je za Forzu. Izravno poziva izvoz Forze i ne čita `--game`, `--level` ni `--install`.

| Opcija | Zadano | Značenje |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | mapa u koju se piše (stvara se ako ne postoji) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | biblioteka krugova |
| `--only TEXT [TEXT ...]` | sve | samo staze čija imena mapa sadrže jedan od ovih tekstova (bez obzira na velika i mala slova) |
| `--force` | isključeno | ponovno izvezi ono što već ima `.glb` |
| `--track DIR` | pretraži | kao za `course` |
| `--margin M` | 80 | kao za `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | kao za `course` |

Mapa staze je izravna podmapa biblioteke čije ime sadrži ` (course_`, kako ih imenuje FH Companion, na primjer `Example Circuit (course_1200_3400_to_1175_3400)`. Dio imena od ` (course_` nadalje odbacuje se.

Kako se pokretanje ponaša:

- Staza čiji `.glb` već postoji preskače se (`kept`), osim ako nije dan `--force`, pa prekinuto pokretanje nastavlja tamo gdje je stalo.
- `.glb` koji je napisala starija verzija, bez vlastitog sloja utrke i mjesta održavanja (njegov `asset.extras.course_format` nedostaje ili je niži od trenutačnog), izvozi se ponovno, kao da je dan `--force` samo za njega.
- Dvije mape staza s istim imenom prije ` (course_` (snimač je novu stazu nazvao po staroj) ne prepisuju jedna drugu: mapa stvorena prva zadržava `<name>.glb`, a druga se piše kao `<name>_<start>.glb`, gdje je `<start>` mjesto početka, a minusi kao `m` (na primjer `example_circuit_m120_m340.glb`).
- Staza koja ne uspije (krugovi koji se ne mogu pročitati, nedostatak memorije, nema terena...) prijavljuje se kao `FAILED`, a pokretanje se nastavlja.
- Na kraju ispisuje tablicu statusa, veličine u MB, trajanja u sekundama i imena, zatim `<n> of <total> courses in <folder>`.
- Izlazni kod je 1 ako je neka staza neuspjela.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Ispisuje svaku utrku koju instalirana Forza definira, iz njezinih definicija ruta (vidi [Forza Horizon staze](course-forza-horizon.md#which-race)), i provjerava izvoze u mapi `courses` u odnosu na njih. Čita igru i biblioteku krugova; ne piše ništa osim neobavezne tablice.

| Opcija | Zadano | Značenje |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | mapa u koju piše `courses`, čije se datoteke provjeravaju |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | biblioteka krugova |
| `--track DIR` | pretraži | mapa staze, ako nije mapa instalirane igre |
| `--markdown FILE` | nema | i tablicu zapiši tamo, kao Markdown |

Jedan redak po utrci i jedan po snimljenoj stazi koja je na njoj vožena:

| Stupac | Značenje |
|---|---|
| route | id rute |
| course | snimljena staza koja je uparena s njom, ako postoji |
| own assets | kopije koje utrka dodaje svijetu slobodne vožnje |
| drawn | od njih, kopije čiji model staza isporučuje |
| kinds | dodane kopije po vrsti (barijere, rekviziti, naljepnice, infrastruktura, ...) |
| not geometry | markeri gledatelja i kolizijski splajnovi, prebrojani |
| hidden | objekti slobodne vožnje koje utrka uklanja |
| venue | modeli tla mjesta održavanja kroz koja AI linija utrke prolazi unutar 10 m |
| export | `current`, `older format` (ponovno izvezeno pomoću `courses`), `not exported`, ili prazno za utrku bez snimljene staze |

Na kraju je zbroj: `<n> races: <a> with assets of their own, <v> through a venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Ovo je Forza izrez, ali sve navedeno ručno: zadajete mapu staze i područje, a ne krug. Korisno je kada je područje koje želite kutija, a ne vožnja.

| Opcija | Zadano | Značenje |
|---|---|---|
| `<path>` | obavezno | mapa Forza staze pod `media\Tracks` (s `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | obavezno | `.glb` koji se piše |
| `--box X0 Z0 X1 Z1` | | područje, u metrima igre (x i z, kako ih telemetrija prijavljuje); kutovi u bilo kojem redoslijedu |
| `--route FILE` | | JSON rute s `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, kako ga pišu `heat3d_capture route` i `heat3d_capture laps`; čita se kao UTF-8, s oznakom redoslijeda bajtova ili bez nje |
| `--margin M` | **100** | metara dodanih oko granica rute, i širina koridora kada ruta ima liniju |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | kao za `course` |

Dajte točno jedan od `--box` i `--route`, inače je izlazni kod 2. Uz `--route`, izrez je `bounds` rute (`min`/`max`, x i z) proširen razmakom. Ako datoteka sadrži i barem 10 pozicija, izrez se sužava na koridor širine `--margin` metara oko njih, a postavljeni modeli dobivaju detalj prema udaljenosti od te linije. Uz `--box`, čitav okvir se zadržava, a detalj ide onome što stoji najbliže središtu okvira.

Visina nikad nije dio izreza. Kutija izvan karte ili na moru daje "no terrain there" (izlazni kod 1), a ne grešku o koordinatama.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` ispisuje razine koje instalirana Frostbite igra isporučuje, po imenu njihove tablice (`levels/<level>/<level>.toc`), s veličinom i odakle dolaze: `Data` za osnovnu igru, `Update/<pack>` za nadogradnju, i koliko tablica visoke razlučivosti dodaje. Razina koju nadogradnja isporučuje ima i u osnovnoj igri malu tablicu dijelova (chunkova); tablica s njezinim snopovima (bundles) jest razina (vidi [Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` izvozi jednu: teren kao visinsko polje, svaku mrežu koju grupe statičkih modela razine postavljaju, predmete postavljene pojedinačno i gdje stoje, te pozadinu terena razine oko karte. Uz `--textures`, svaka površina nosi svoju mapu boja; uz `--navmesh`, dolaze i površine po kojima hodaju vojnici. Kako se čita, opisano je na [Frostbite](reader-frostbite.md).

| Opcija | Zadano | Značenje |
|---|---|---|
| `<level>` | obavezno | ime kako ga ispisuje `levels`, jedinstveni dio imena, ili put do `.toc`-a razine |
| `-o`, `--out FILE` | `<level>.glb` | `.glb` koji se piše |
| `--install FOLDER` | prva Steam igra čiji `Data` sadrži `layout.toc` | mapa igre |
| `--textures [PIXELS]` | isključeno; 512 ako je dano bez veličine | zapiše mapu boja svake površine, najveći mip ne veći od PIXELS po strani, i njezine koordinate teksture kako ih igra ima, s ponavljajućim uzorkovanjem (vidi [Format izlaza](output-format.md)). Visinsko polje dobiva mapu boja pozadine terena gdje ona pokriva, inače srednju boju površinskih materijala terena, inače prosječnu boju pozadine oko njega. Isključeno, svaki dio je ravne boje |
| `--ground-texture [METRES]` | isključeno; 0.5 ako je dano bez veličine | peče dekale terena (ceste, uzletišta, perone, naslikane oznake) preko boje tla, pomnožene mapom boja terena gdje je razina ima, METRES po pikselu, u pločicama od najviše 4,096 piksela (`ground:terrain x<x> z<z>`). Radi s `--textures` ili bez njega |
| `--navmesh` | isključeno | dodaje navigacijsku mrežu razine za najmanjeg agenta, vojnika (1.8 m visok, 0.4 m širok), kao dio `nav:walkable`: tlo, podove, stube i krovove koje vojnik može doseći, bez poveznica (skokova, ljestava, preskakanja) među njima |
| `--ground-spacing METRES` | 4 | najfiniji razmak visinskog polja; čvorovi finiji od toga uzorkuju se rjeđe. 0 izostavlja visinsko polje |
| `--detail-budget N` | svaka kopija na najgrubljoj razini, plus četvrtina, najmanje 1,500,000 | gornja granica trokuta. Mreže koje najviše koštaju spuštaju razinu detalja jednu po jednu dok ne stanu; ako ni najgrublje razine ne stanu, najmanje kopije izostavljaju se prve. Pozadina terena se nikad ne zgrubljuje niti izostavlja |
| `--skip TEXT` | | izostavi grupe statičkih modela čije ime particije sadrži TEXT; ponovite za više. Na primjer sloj određenog načina igre |
| `--by-mesh` | isključeno | za traženje što je koji dio: jedan dio po izvornoj mreži i materijalu, imenovan `<part> \| <mesh> \| <material>`; znatno veća datoteka |
| `--clamped-uvs` | isključeno | za prikazivač koji ne može ponavljati teksturu: svaki teksturirani trokut reže se na komade čije koordinate leže u 0..1, a trokut koji bi trebao više od 4 komada crta se prosječnom bojom svoje teksture, u dijelu `<part> (average colour)` |

Ispisuje grupe i koliko je kopija svaka postavila, mreže koje je izostavio i zašto, trokute po dijelu (i uz `--textures` koliko tekstura, te koliko odjeljaka je našlo svoju mapu boja), što je tlo, a uz `--navmesh` koliko je navigacijskih pločica pročitano. Osim geometrije, o razini se ne zapisuje ništa: bez imena, bez metapodataka (vidi [Format izlaza](output-format.md)).

Proračun terena je zaseban: visinsko polje i pozadina se nikad ne zgrubljuju `--detail-budget`-om; `--ground-spacing` određuje veličinu visinskog polja.

Cijela razina je velika: obično preko deset milijuna trokuta i nekoliko stotina MB. `--textures` dodaje malo datoteci; razina bogata drvećem može doseći oko 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8` svodi razinu na otprilike trećinu toga.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` je mapa igre, njezin `Content/Paks`, ili ime njezine mape u Steam biblioteci (`"<Steam game folder name>"`). `ue-maps` popisuje svaku kartu koja ima pohranjene ćelije World Partition pored sebe. `ue-map` izvozi jednu kao `ground:<map>` (krajolik), `structure:<map>` (spojene HLOD mreže karte) i `water:<map>` (njezina vodena tijela tamo gdje stoje iznad tla), u Unreal **centimetrima**, s zamijenjenim Y i Z: jedini izvoz koji nije u metrima. Kako se svaki čita i provjerava: [Unreal 5 karte](level-unreal-world-partition.md).

| Opcija | Zadano | Značenje |
|---|---|---|
| `<map>` | obavezno | ime kako ga ispisuje `ue-maps`, ili jedinstveni dio imena |
| `-o`, `--out FILE` | `<map>.glb` | `.glb` koji se piše |
| `--ground-spacing METRES` | 2 | razmak vrhova krajolika u datoteci, zaokružen na cijeli broj njegovih vlastitih četverokuta |
| `--no-structures`, `--no-water` | | izostavi taj dio |

Ispisuje trokute po dijelu, koliko je komponenti krajolika pročitano i koliko se vrhova koje spremaju dvaput ne slaže. Karta od 3 km na 2 m ima oko 4.6 milijuna trokuta tla.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` popisuje svaki svijet s terenom, po njegovoj mapi pod `worlds/`. `enfusion-world` izvozi jedan: `ground:<world>` (teren, u bojama njegovih supertekstura), `water:<world>` (more, na visini nula) i `structure:<world>` (kutija svakog postavljenog modela), u metrima igre: x istok, y gore, z sjever. Kako se čita i provjerava: [Arma Reforger svjetovi](level-arma-reforger.md).

| Opcija | Zadano | Značenje |
|---|---|---|
| `<world>` | obavezno | svijet kako ga ispisuje `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | `.glb` koji se piše |
| `--install FOLDER` | Steam biblioteka koja sadrži igru | mapa igre |
| `--ground-spacing METRES` | 2 (terenov vlastiti) | razmak vrhova terena u datoteci |
| `--texture-size PIXELS` | 4096 | veća stranica slike boja tla; 0 za ravnu boju |
| `--no-structures` | | izostavi postavljene modele |
| `--trees` | isključeno | dodaje i drveće i drugo raslinje, kao kutije |

Ispisuje trokute po dijelu, koliko se vrhova rubova pločica ne slaže, koliko entiteta sadrži datoteka svijeta i koliko je kutija postavljeno, te što je izostavljeno i zašto.

## Varijable okruženja {#environment-variables}

| Varijabla | Učinak |
|---|---|
| `HEAT3D_OODLE` | put do `oo2core_*_win64.dll` ili mape koja ga sadrži; vidi [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | svaka vrijednost osim prazne, `0`, `false`, `no` isključuje provjeru ažuriranja; vidi [Ažuriranja](updates.md) |
| `LOCALAPPDATA` | gdje se traže biblioteka FH Companion, korisnička mapa BeamNG-a i predmemorija ažuriranja |
| `HEAT3D_COURSE` | samo za testove: staza koju koristi test instalirane igre (rubnjaci); vidi [Razvoj](development.md) |
