---
title: "Komande"
nav_order: 2
lang: "bs"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Komande {#commands}

Svaka komanda se pokreće kao `python -m heat3d_gamefiles <verb> ...` iz foldera
repozitorija. Glagoli su poredani kako ih obično trebate: šta je ova datoteka, šta je
u njoj, daj mi ono, i pretvori krug u stazu.

| Glagol | Prima | Radi |
|---|---|---|
| [`identify`](#identify) | bilo koja datoteka | imenuje format kontejnera čitanjem njegovih bajtova |
| [`list`](#list) | Unreal `.pak` ili IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip` ili zip | ispisuje njegove unose |
| [`extract`](#extract) | isto | upisuje jedan unos na disk |
| [`meshes`](#meshes) | Unity `SerializedFile` | ispisuje i provjerava njegove mreže (meshes) |
| [`course`](#course) | krug | izvozi stazu oko njega (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | snimljena biblioteka krugova | pokreće `course` za svaku stazu u njoj (Forza) |
| [`races`](#races) | instalirana Forza | ispisuje svaku utrku koju igra definira: šta dodaje, šta skriva, lokacije, stanje njenog izvoza |
| [`terrain`](#terrain) | folder Forza staze | izrezuje područje po svjetskim koordinatama |
| [`levels`](#levels-and-level-frostbite) | instalirana Frostbite igra (Battlefield 6) | ispisuje njene nivoe |
| [`level`](#levels-and-level-frostbite) | ime nivoa | izvozi nivo: teren, postavljene mreže, po želji njihove mape boja (Battlefield 6) |
| [`cars`](#cars) | instalirana Forza | svaki automobil u niskom detalju, u jednoj datoteci za karticu utrke u pregledniku |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | Unreal 5 igra | ispisuje njene World Partition mape |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | ime mape | izvozi mapu: teren, HLOD strukture, vodu |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | instalirani Arma Reforger | ispisuje njegove svjetove |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | ime svijeta | izvozi svijet: teren u njegovim bojama, more, zgrade kao kutije |

**Kako čitati primjere:** `<x>` znači zamijenite to vlastitom vrijednošću, bez
ugaonih zagrada; `[...]` je neobavezno; putanju s razmacima stavite u "dvostruke navodnike",
na primjer `"C:\Games\My Game"`. Ovo vam je novo? Pogledajte [Prije nego počnete](before-you-start.md).
Cijeli `--help` svake komande nalazi se u [Referenci komandi](../cli-reference.md).

Svaki put kad se program pokrene, može prvo provjeriti ima li novije izdanje. Pogledajte
[Ažuriranja](updates.md). `HEAT3D_NO_UPDATE=1` isključuje tu provjeru.

Izvor: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Stranice korak po korak: [Pregled arhiva](inspecting-archives.md), [Izvoz staze](course-export.md),
[Cijeli nivoi](whole-levels.md), [Forza automobili](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Izlazni kodovi {#exit-codes}

| Kod | Značenje |
|---|---|
| 0 | uspjeh |
| 1 | posao nije uspio (nečitljiv krug, igra nije pronađena, nema šta izvesti, staza u `courses` nije uspjela; za `list` i `extract`: datoteka koja nije nijedna od arhiva koje čitaju, onaj koji se ne može otvoriti ili pročitati - šifrirani pak bez `--key`, šifrirani IoStore kontejner - ili unos kojeg nema u arhivi) |
| 2 | loši argumenti (argparse), putanja koja ne postoji, `--key` koji nema 64 heksadecimalne cifre, ili `terrain` kojem su dani i `--box` i `--route` ili nijedan od njih |

Greške komandi `list` i `extract` su po jedan red na standardnom izlazu za greške, a ne
Python traceback.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Ovo čita datoteku i kaže o kojem je kontejneru riječ. Ne gleda ekstenziju
(jedini izuzetak je `.ucas`, niže). Isprobava formate ovim redom i staje na prvom
koji se uspije pročitati:

1. **Unreal `.pak`**: podnožje s pak magic vrijednošću u zadnjih 1.024 bajta. Ispisuje
   verziju, pomak i veličinu indeksa, je li indeks šifriran i metode
   kompresije.
2. **Unreal IoStore `.utoc`**: IoStore magic na njegovom početku. Ispisuje verziju,
   broj dijelova (chunks) i je li kontejner šifriran; za onaj koji nije,
   broj datoteka koje njegov direktorij imenuje (i pod kojom tačkom montiranja), metode
   kompresije i je li njegov `.ucas` pored njega. `.ucas` nema vlastito
   zaglavlje, pa se prepoznaje po `.utoc` istog imena pored njega,
   a `identify` imenuje tu datoteku.
3. **ForzaTech `.minizip`**: `PGZP` magic. Ispisuje verziju, broj unosa i
   segmenata, i je li pored njega `ChunkContentsMiniZip<n>.txt` koji imenuje
   unose (i, ako jest, imenuje li ih onoliko koliko ih ima).
4. **zip**: zip lokalno zaglavlje datoteke na početku. Ispisuje broj unosa, šest
   najčešćih ekstenzija i imena nivoa kad unosi leže pod
   `levels/<name>/`, kao u BeamNG.drive arhivi nivoa.
5. **Unity**: `UnityFS` paket (ispisuje verziju engine-a i broj unosa) ili
   goli `SerializedFile` (ispisuje format, verziju engine-a, broj objekata i
   šest najčešćih klasa).
6. **Frostbite `.toc`**: ispisuje vrstu (`plain` ili `signed`), gdje počinje
   stablo, i ili broj asseta (binarna tablica sekcija) ili broj
   superbundleova (DbObject stablo).
7. **Source 2 `.vpk`**: ispisuje verziju, broj unosa i prvu `.nav`
   navigacijsku mrežu ako je arhiva ima.
8. **BeamNG `.cdae`**: verzija oblika 31 koja se uspije pročitati. Ispisuje broj mreža,
   broj iscrtanih nivoa detalja i prve materijale.
9. **BeamNG `.ter`**: nema magic vrijednosti, pa sve mora štimati - stranica od 2
   do 16.384, toliko na kvadrat visina i bajtova slojeva, zatim 1 do 255 čitljivih
   imena slojeva. Ispisuje verziju, veličinu i imena slojeva.
10. **ForzaTech `.modelbin`**: ispisuje verziju, broj dijelova i šest
    najčešćih oznaka dijelova. Sadržaj dijelova se ovdje ne dekodira.

Formati s vlastitom magic vrijednošću (2 do 4) dolaze prije Unityja i Frostbitea,
čije provjere čitaju cijelu datoteku: Forza arhiva ima desetine gigabajta.

Ako se nijedan ne poklopi, ispisuje `not a format this tool reads` i zadnji
razlog. Taj razlog dolazi iz ForzaTech provjere.

Primjer (sintetički):

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
| `<archive>` | obavezno | Unreal `.pak`; IoStore `.utoc` (ili `.ucas` pored njega); Source 2 `.vpk` (za podijeljene VPK-ove, `_dir.vpk`); ForzaTech `.minizip`; zip, kao što su BeamNG arhive nivoa i sadržaja |
| `--filter TEXT` | nema | samo putanje koje sadrže TEXT, bez razlike velikih i malih slova |
| `--limit N` | 50 | ispisuje najviše N unosa (ukupan broj se uvijek ispisuje) |
| `--key HEX` | nema | AES-256 ključ koji već imate, 64 heksadecimalne cifre, sa `0x` ili bez njega. Koristi ga samo šifrirani `.pak`. Sve što nije 64 heksadecimalne cifre odbija se prije otvaranja arhive (izlazni kod 2) |

Alat format određuje iz bajtova: IoStore tablicu sadržaja, `.minizip` i VPK po
potpisu kojim počinju, zip po lokalnom zaglavlju datoteke, a `.pak` po podnožju na
njegovom kraju. `.ucas` nema zaglavlje i otvara se preko `.utoc` istog imena.
Datoteka koja nije ništa od toga odbija se s
`<file> is not an archive list and extract read (...)`. Ona koja jest, ali se
ne može otvoriti, odbija se s razlogom čitača: šifrirani pak bez
`--key`, šifrirani IoStore kontejner, verzija paka koju ne čita. U oba slučaja
to je jedan red i izlazni kod 1.

Svaki red prikazuje nekomprimiranu veličinu, metodu kompresije i putanju:

| Arhiva | Metoda | Putanje |
|---|---|---|
| `.pak` | `none` ili ime iz podnožja (`Zlib`, `Oodle`, `Gzip`...) | s tačkom montiranja arhive, na primjer `../../../Game/Content/...` |
| IoStore `.utoc` | `none` ili metoda kontejnera (`Oodle`, `Zlib`...), onako kako je pohranjen njegov prvi blok | s tačkom montiranja, na primjer `../../../<Project>/Content/...`. Kontejner bez indeksa direktorija ne imenuje datoteke i odbija se |
| `.vpk` | uvijek `stored` | kao u direktoriju |
| `.minizip` | `lz4`, `deflate` ili `stored` | onako kako ih ispisuje `ChunkContentsMiniZip<n>.txt` pored `GeoChunk<n>.minizip`, s uklonjenim prefiksom build-mašine (obrnute kose crte, kako ih igra piše). Arhiva ne pohranjuje imena, pa su bez te datoteke unosi `#0`, `#1`... Popis čiji se broj redova razlikuje od broja unosa se odbija: ta dva ne pripadaju zajedno |
| zip | `stored`, `deflate`, ... | kako je pohranjeno; folderi se ne ispisuju |

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
| `<archive>` | obavezno | kao za `list` |
| `<entry>` | obavezno | putanja tačno onako kako je `list` ispisuje (razlikuje velika i mala slova); u `.minizip` radi i `#<number>` |
| `--out FILE` | ime datoteke unosa (poslije zadnjeg `/` ili `\`), u trenutnom folderu | gdje upisati; nadređeni folderi se kreiraju |
| `--key HEX` | nema | kao za `list` |

Unos se dešifrira (pak, s ključem), dekomprimira i upisuje. Ispisuje
`<bytes> bytes -> <file>`. Ako putanje nema u arhivi, komanda završava
s kodom 1. Isto vrijedi za unos koji se ne može pročitati (šifrirani unos bez
ključa, komprimiran Oodleom bez Oodle biblioteke), s razlogom u jednom redu. VPK unos se ovdje ne provjerava prema njegovom CRC-u. Čitač ima
metodu `verify()` za to (pogledajte [Source 2 VPK](reader-source2-vpk.md)).

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
| `<path>` | obavezno | goli Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), ne paket |
| `--limit N` | 25 | dekodira i ispisuje najviše N mreža |

Ovo ispisuje broj `Mesh` objekata, zatim po jedan red za svaku mrežu: ime (prvih
40 znakova), broj vrhova i trouglova, te `ok` ili `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` znači da dekodirani vrhovi ne reproduciraju granični okvir
koji je Unity pohranio za mrežu, unutar 2% veličine okvira. To je vlastita provjera
parsiranja (pogledajte [Unity](reader-unity.md)). Mreža koja se ne može pročitati prijavljuje se
s razlogom i računa se u ograničenje. Podaci vrhova u `.resS` datoteci čitaju se
iz foldera u kojem je kontejner.

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

Ovo izvozi stazu oko kruga: tlo u pojasu s obje strane vožnje i ono što
stoji na njemu, kao jedan `.glb`. Ostalo se određuje samo: koja je igra, koja instalirana kopija,
koja staza, nivo ili etapa, i (za Assetto Corsa
Rally) na koju su stranu okrenute osi. Pogledajte [Izvoz staze](course-export.md).

`<lap>` može biti bilo šta od sljedećeg (detalji u [Ulazima kruga](lap-inputs.md)):

- datoteka kruga: route JSON, FH Companion JSON kruga, `heat3d-lap` JSON, `.npz` ili `.csv` s kolonama x, y, z
- folder datoteka krugova, pretražen rekurzivno (cijela snimljena staza)
- **ime** staze, potraženo u FH Companion biblioteci na `%LOCALAPPDATA%\FHCompanion\laps`

### Opcije {#options}

| Opcija | Zadano | Igre | Značenje |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` u trenutnom folderu | sve | gdje upisati; ime se piše malim slovima, a nizovi drugih znakova pretvaraju se u `_` |
| `--game {forza,beamng,acrally}` | ono što kaže datoteka kruga, inače `forza` | sve | iz koje je igre krug |
| `--margin M` | 80 | sve | metara tla zadržanog s obje strane vožnje |
| `--texture-size {2048,1024,512}` | 2048 | sve | pikseli teksture tla po pločici od 512 m (2048 = 25 cm po pikselu) |
| `--no-textures` | isključeno | sve | samo ravne boje: znatno manja datoteka. Za Forzu ovo također preskače podjelu cesta/rub (pogledajte niže) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | mape tla i teksture modela kojeg godišnjeg doba |
| `--no-placed` | isključeno | sve | samo teren: bez ivičnjaka, ograda, znakova, zgrada. Za BeamNG se površine za vožnju modelirane kao mreže i dalje zadržavaju |
| `--trees` | isključeno | sve | postavlja i vegetaciju (Forza: drveće, grmlje i objekti koji se mogu razbiti; BeamNG: drveće; AC Rally: drveće i instancirano lišće) |
| `--detail-budget N` | automatski | sve | gornja granica trouglova za sve postavljeno; pogledajte [Nivoi detalja i budžet](detail-budget.md) |
| `--track DIR` | traži se | Forza | folder staze (pod `media\Tracks`, s `GeoChunk0.minizip`) ako instaliranu igru ne treba tražiti |
| `--level NAME` | nađeno iz kruga | BeamNG, AC Rally | nivo (ime foldera u BeamNG-u) ili etapa (ime mape u AC Rally), bez razlike velikih i malih slova |
| `--install DIR` | traži se u Steam bibliotekama | BeamNG, AC Rally | BeamNG: folder s `gameengine.zip`. AC Rally: folder igre ili njegov `acr\Content\Paks` / `Content\Paks` |

Opcije koje se ne odnose na igru ignoriraju se bez upozorenja. Na primjer,
`--season` ne radi ništa za BeamNG i AC Rally, a `--track` također ne radi ništa
za njih.

### Koja igra {#which-game}

Igra se uzima iz `--game`, zatim iz polja `game` datoteke `heat3d-lap`
(ili iz opisnog reda `# {...}` u CSV-u), a zadano je Forza. Folder
dobiva igru koju njegove datoteke imenuju, kad imenuju samo jednu; datoteka koja ne imenuje nijednu
(FH Companion krug, `course.json`, CSV bez opisnog reda) ne
računa se (pogledajte [Ulazi kruga](lap-inputs.md)).

| Vrijednost | Izvoz |
|---|---|
| počinje s `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` ili `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | odbijeno: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | odbijeno: "tracks ship in a protected format that is not a file-extraction target" |
| bilo šta drugo | odbijeno: "there is no course reader for <game> yet" |

Odbijanje također predlaže alternative: rekonstruirati stazu iz igranja
(3DHeat GameCapture) ili analizirati krugove bez staze, jer kartica
Analiza utrke u pregledniku iz njih crta cestu.

### Primjeri {#examples}

```
# A course from the FH Companion library, by name
python -m heat3d_gamefiles course "Example Circuit"

# One lap file, a narrower band, a smaller file
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Winter textures, trees included
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# A hard ceiling of 500,000 placed triangles
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# A track folder given directly (game installed outside Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: name the level, point at the install
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, with a plain CSV lap that does not say its game
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Primjer izlaza (Forza, sintetički brojevi):

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

Svaki automobil instalirane Forze u niskom detalju same igre, u jednoj datoteci za
karticu utrke u pregledniku: `ProxyLOD` model koji nosi svaka arhiva automobila pod `media/Cars`,
oko 900 trouglova, s brojem automobila kako ga navodi telemetrija,
njegovom markom, oznakom modela i godinom iz imena arhive, te njegovim kotačima i zadnjim
svjetlima. Traje sekunde i upisuje oko 5 MB. Pokrenite ponovo kad igra dobije nove
automobile. Arhiva bez takvog modela (prometni rekvizit) se imenuje i izostavlja. Format
je u [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Oblici su u metrima, kao u samoj igri: 1:1 s automobilom. Datoteka sadrži
sadržaj igre, pa je za mašinu na kojoj je napravljen, a ne za dijeljenje.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Ovo pokreće Forza izvoz `course` za svaki folder staze u snimljenoj biblioteci
krugova, upisujući po jedan `<name>.glb`. Radi samo za Forzu. Poziva Forza
izvoz direktno i ne čita `--game`, `--level` ni `--install`.

| Opcija | Zadano | Značenje |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | folder u koji se upisuje (kreira se ako nedostaje) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | biblioteka krugova |
| `--only TEXT [TEXT ...]` | sve | samo staze čija imena foldera sadrže jedan od ovih tekstova (bez razlike velikih i malih slova) |
| `--force` | isključeno | ponovo izvozi ono što već ima `.glb` |
| `--track DIR` | traži se | kao za `course` |
| `--margin M` | 80 | kao za `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | kao za `course` |

Šta se računa kao folder staze: direktni podfolder biblioteke čije ime
sadrži ` (course_`, kako ih FH Companion imenuje, na primjer
`Example Circuit (course_1200_3400_to_1175_3400)`. Dio od ` (course_` nadalje
izbacuje se iz imena.

Kako se pokretanje ponaša:

- Staza čiji `.glb` već postoji preskače se (`kept`) osim ako je dan `--force`, pa prekinuto pokretanje nastavlja gdje je stalo.
- `.glb` koji je upisala starija verzija, bez vlastitog sloja utrke i lokacija (njegov `asset.extras.course_format` nedostaje ili je manji od trenutnog), izvozi se ponovo, kao da je `--force` dan samo za njega.
- Dva foldera staza s istim imenom prije ` (course_` (snimač koji je novu stazu imenovao po staroj) ne prepisuju jedan drugog: folder kreiran prvi zadržava `<name>.glb`, drugi se upisuje kao `<name>_<start>.glb`, gdje je `<start>` mjesto gdje počinje, a znakovi minus su `m` (na primjer `example_circuit_m120_m340.glb`).
- Staza koja ne uspije (nečitljivi krugovi, nedostatak memorije, nema terena...) prijavljuje se kao `FAILED`, a pokretanje se nastavlja.
- Na kraju ispisuje tablicu statusa, veličine u MB, utrošenih sekundi i imena, zatim `<n> of <total> courses in <folder>`.
- Izlazni kod je 1 ako je bilo koja staza zakazala.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Ispisuje svaku utrku koju instalirana Forza definira, iz njenih definicija ruta (pogledajte
[Forza Horizon staze](course-forza-horizon.md#which-race)), i provjerava
izvoze u folderu `courses` prema njima. Čita igru i biblioteku krugova;
ne upisuje ništa osim neobavezne tablice.

| Opcija | Zadano | Značenje |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | folder u koji piše `courses`, čiji se datoteke provjeravaju |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | biblioteka krugova |
| `--track DIR` | traži se | folder staze, ako nije onaj instalirane igre |
| `--markdown FILE` | nema | tablicu također upisuje tamo, kao Markdown |

Jedan red po utrci i jedan po snimljenoj stazi vožnjenoj na njoj:

| Kolona | Značenje |
|---|---|
| route | id rute |
| course | snimljena staza povezana s njom, ako postoji |
| own assets | kopije koje utrka dodaje svijetu slobodnog vožnjenja |
| drawn | od tih, kopije čiji model staza isporučuje |
| kinds | dodane kopije po vrsti (ograde, rekviziti, naljepnice, infrastruktura, ...) |
| not geometry | markeri gledalaca i splineovi sudara, izbrojani |
| hidden | objekti slobodnog vožnjenja koje utrka uklanja |
| venue | modeli tla lokacije pored kojih AI linija utrke prolazi unutar 10 m |
| export | `current`, `older format` (`courses` ga izvozi ponovo), `not exported`, ili prazno za utrku bez snimljene staze |

Završava brojanjem: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Ovo je Forza izrez s ručno navedenim svime: dajete folder staze
i područje, ne krug. Korisno je kad je područje koje želite kutija
a ne vožnja.

| Opcija | Zadano | Značenje |
|---|---|---|
| `<path>` | obavezno | folder Forza staze pod `media\Tracks` (s `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | obavezno | `.glb` koji se upisuje |
| `--box X0 Z0 X1 Z1` | | područje, u metrima igre (x i z, kako ih telemetrija prijavljuje); uglovi bilo kojim redom |
| `--route FILE` | | route JSON s `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, kako ga pišu `heat3d_capture route` i `heat3d_capture laps`; čita se kao UTF-8, sa ili bez oznake poretka bajtova |
| `--margin M` | **100** | metri dodani oko granica rute, i širina koridora kad ruta ima liniju |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | kao za `course` |

Navedite tačno jedno od `--box` i `--route`, inače je izlazni kod 2. Uz
`--route`, izrez je `bounds` rute (`min`/`max`, x i z) proširen za
marginu. Ako datoteka sadrži i najmanje 10 pozicija, izrez se sužava na
koridor od `--margin` metara oko njih, a postavljeni modeli dobivaju detalj prema
udaljenosti od te linije. Uz `--box`, zadržava se cijela kutija, a detalj ide
onome što stoji najbliže sredini kutije.

Visina nikad nije dio izreza. Kutija izvan mape, ili u moru, daje
"no terrain there" (izlazni kod 1), a ne grešku o koordinatama.

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

`levels` ispisuje nivoe koje isporučuje instalirana Frostbite igra, po imenu
njihove tablice (`levels/<level>/<level>.toc`), s njenom veličinom i odakle
dolazi: `Data` za osnovnu igru, `Update/<pack>` za ažuriranje, i koliko
tablica visoke rezolucije joj dodaje. Nivo koji isporučuje ažuriranje ima malu tablicu
dijelova (chunks) samo i u osnovnoj igri; tablica s paketima nivoa
je sam nivo (pogledajte [Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` izvozi jedan: heightfield terena, svaku mrežu koju
grupe statičkih modela nivoa postavljaju, objekte postavljene jedan po jedan, gdje stoje,
i pozadinu terena nivoa oko mape. Uz `--textures`, svaka površina nosi
svoju mapu boja; uz `--navmesh` dolaze i površine kojima hodaju vojnici. Kako
se čita opisano je u [Frostbite](reader-frostbite.md).

| Opcija | Zadano | Značenje |
|---|---|---|
| `<level>` | obavezno | ime kako ga ispisuje `levels`, jedinstven dio njega, ili putanja `.toc` nivoa |
| `-o`, `--out FILE` | `<level>.glb` | `.glb` koji se upisuje |
| `--install FOLDER` | prva Steam igra čiji `Data` sadrži `layout.toc` | folder igre |
| `--textures [PIXELS]` | isključeno; 512 kad je dano bez veličine | upisuje mapu boja svake površine, najveći mip koji nije veći od PIXELS po strani, i njene koordinate teksture kakve ih igra ima, s ponavljajućim uzorkivačem (pogledajte [Format izlaza](output-format.md)). Heightfield dobiva mapu boja pozadine terena gdje ta mapa pokriva, inače srednju boju materijala površine terena, inače prosječnu boju pozadine oko njega. Isključeno, svaki dio je ravna boja |
| `--ground-texture [METRES]` | isključeno; 0.5 kad je dano bez veličine | peče decale terena - ceste, piste, platforme, oslikane oznake - preko boje tla, pomnožene mapom boja terena gdje je nivo ima, u boju heightfielda, METRES po pikselu, u pločicama od najviše 4.096 piksela (`ground:terrain x<x> z<z>`). Radi sa ili bez `--textures` |
| `--navmesh` | isključeno | dodaje navigacijsku mrežu nivoa za njegovog najmanjeg agenta, vojnika (visok 1,8 m, širok 0,4 m), kao dio `nav:walkable`: tlo, podove, stepenice i krovove do kojih vojnik može doći, bez veza (skokovi, ljestve, preskakanja) među njima |
| `--ground-spacing METRES` | 4 | najfinije rastojanje heightfielda; čvorovi finiji od ovoga se uzorkuju naniže. 0 izostavlja heightfield |
| `--detail-budget N` | svaka kopija na najgrubljem nivou, plus četvrtina, najmanje 1.500.000 | gornja granica trouglova. Mreže koje najviše koštaju spuštaju se za jedan nivo detalja odjednom dok ne stane; ako ni najgrublji nivoi ne stanu, prvo se izostavljaju najmanje kopije. Pozadina terena se nikad ne zagrubljuje niti izostavlja |
| `--skip TEXT` | | izostavlja grupe statičkih modela čije ime particije sadrži TEXT; ponovite za više njih. Na primjer sloj načina igre |
| `--by-mesh` | isključeno | za otkrivanje šta je neki dio: jedan dio po izvornoj mreži i materijalu, nazvan `<part> \| <mesh> \| <material>`; mnogo veća datoteka |
| `--clamped-uvs` | isključeno | za renderer koji ne može ponavljati teksturu: siječe svaki teksturirani trougao na komade čije koordinate leže unutar 0..1, a trougao kojem bi trebalo više od 4 komada crta u prosječnoj boji njegove teksture, u dijelu `<part> (average colour)` |

Ispisuje grupe i koliko je kopija svaka postavila, mreže koje je izostavio i
zašto, trouglove po dijelu (a uz `--textures` koliko tekstura, i koliko
sekcija je našlo svoju mapu boja), šta je tlo, a uz
`--navmesh` koliko je navigacijskih pločica pročitano. Ništa se ne piše o nivou osim
geometrije: nema imena, nema metapodataka (pogledajte [Format izlaza](output-format.md)).

Budžet terena je odvojen: heightfield i pozadina se nikad
ne zagrubljuju zbog `--detail-budget`; `--ground-spacing` određuje veličinu heightfielda.

Cijeli nivo je velik: obično preko deset miliona trouglova i nekoliko
stotina MB. `--textures` datoteci dodaje malo; nivo gust od drveća
može doseći oko 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8`
spušta nivo na otprilike trećinu toga.

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

`<game>` je folder igre, njen `Content/Paks`, ili ime njenog foldera
u Steam biblioteci (`"<Steam game folder name>"`). `ue-maps` ispisuje svaku mapu
koja ima skuhane World Partition ćelije pored sebe. `ue-map` izvozi jednu kao
`ground:<map>` (krajolik), `structure:<map>` (spojene HLOD
mreže mape) i `water:<map>` (njena vodena tijela gdje stoje iznad
tla), u Unreal **centimetrima** sa zamijenjenim Y i Z - jedini izvoz koji nije
u metrima. Kako se svaki čita i provjerava: [Unreal 5 mape](level-unreal-world-partition.md).

| Opcija | Zadano | Značenje |
|---|---|---|
| `<map>` | obavezno | ime kako ga ispisuje `ue-maps`, ili jedinstven dio njega |
| `-o`, `--out FILE` | `<map>.glb` | `.glb` koji se upisuje |
| `--ground-spacing METRES` | 2 | razmak vrhova krajolika u datoteci, zaokružen na cijeli broj njegovih vlastitih kvadova |
| `--no-structures`, `--no-water` | | izostavlja taj dio |

Ispisuje trouglove po dijelu, koliko je komponenti krajolika pročitano i
koliko se od vrhova koje pohranjuju dvaput ne slaže. Mapa od 3 km pri 2 m ima oko
4,6 miliona trouglova tla.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` ispisuje svaki svijet s terenom, po njegovom folderu pod
`worlds/`. `enfusion-world` izvozi jedan: `ground:<world>` (teren, u
bojama njegovih pločica supertekstura), `water:<world>` (more, na visini nula)
i `structure:<world>` (kutija svakog postavljenog modela), u metrima same igre -
x istok, y gore, z sjever. Kako se svaki čita i provjerava:
[Arma Reforger svjetovi](level-arma-reforger.md).

| Opcija | Zadano | Značenje |
|---|---|---|
| `<world>` | obavezno | svijet kako ga ispisuje `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | `.glb` koji se upisuje |
| `--install FOLDER` | Steam biblioteka koja sadrži igru | folder igre |
| `--ground-spacing METRES` | 2 (vlastiti terena) | razmak vrhova terena u datoteci |
| `--texture-size PIXELS` | 4096 | veća strana slike boje tla; 0 za ravnu boju |
| `--no-structures` | | izostavlja postavljene modele |
| `--trees` | isključeno | postavlja i drveće i drugu vegetaciju, kao kutije |

Ispisuje trouglove po dijelu, koliko se vrhova na ivicama pločica ne slaže,
koliko entiteta datoteka svijeta sadrži i koliko je kutija postavljeno, te šta je
izostavljeno i zašto.

## Varijable okruženja {#environment-variables}

| Varijabla | Učinak |
|---|---|
| `HEAT3D_OODLE` | putanja do `oo2core_*_win64.dll`, ili folder koji je sadrži; pogledajte [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | bilo koja vrijednost osim praznog, `0`, `false`, `no` isključuje provjeru ažuriranja; pogledajte [Ažuriranja](updates.md) |
| `LOCALAPPDATA` | gdje se traže FH Companion biblioteka, BeamNG korisnički folder i keš ažuriranja |
| `HEAT3D_COURSE` | samo za testove: staza koju koristi test ivičnjaka instalirane igre; pogledajte [Razvoj](development.md) |
