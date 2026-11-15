---
title: "Unity"
nav_order: 4
lang: "bs"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, bundlovi, mreže {#unity-serializedfile-bundles-meshes}

**Navodi objekte i dekodira mreže** Unity formata `SerializedFile` 22 i
novijeg (Unity 2020 do 6000) i otvara `UnityFS` bundlove. Ne postoji izvoz
staze za Unity.

Izvori: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Komande: `identify` (kontejneri i bundlovi), `meshes` (samo goli kontejneri).

## Kontejner {#the-container}

Unity isporučuje nivo kao serijalizirane grafove objekata: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` i asset bundlove. Svaki
sadrži tablicu objekata označenih id-om klase.

Zaglavlje je mjesto gdje čitanje tiho pođe po zlu. Prvih šesnaest bajta su četiri
big-endian `uint32` zadržana radi kompatibilnosti. U formatu 22 tri od njih su
nula, a prave vrijednosti slijede jer datoteka može premašiti 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Drugi `metadata size` je `uint32` između dva `int64`. Pretpostavka da su sva
tri 64-bitna stavlja niz verzije četiri bajta prekasno. On se i dalje dekodira
u nešto oblika niza i sve nakon njega šalje stranputicom. Zaglavlje je
big-endian. Sve nakon njega prati bajt endianosti (0, little-endian, na svakoj
desktop verziji).

Nakon zaglavlja: niz verzije enginea, platforma, zastavica stabla tipova, tablica
tipova (id klase po tipu), tablica objekata (path id, pomak, veličina, tip) i
eksterni (druge datoteke na koje pokazivač može upućivati).

| Slučaj | Rezultat |
|---|---|
| format 22-30 | čita se |
| format 9-21 (prije Unity 2020) | odbija se: pomaci su u naslijeđenom zaglavlju, a nijedna dostupna datoteka ga nije koristila |
| izvan 9-30 | odbija se |
| ugrađeno stablo tipova (editor verzije) | odbija se: isporučene verzije ga ne ugrađuju, a putanja za editor nije implementirana |
| bundle predan tamo gdje se očekuje kontejner | odbija se, uz upućivanje na čitač bundlova |

**Ne postoji opći deserijalizator.** Isporučene verzije ne nose stablo tipova,
jer je shema kompilirana u player, pa se svaka klasa mora parsirati prema
rasporedu poznatom za njenu verziju. Dekodira se samo `Mesh`. Ostale klase
prijavljuju se po imenu i broju (`GameObject`, `Transform`, `MeshRenderer`,
`MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; ostale kao `class<id>`).

**Provjereno** na mnogo instaliranih igara i milionima objekata: tablica objekata
mora tačno popločati sekciju podataka, bez preklapanja, ništa osim paddinga za
poravnanje između objekata, a posljednji objekat završava na posljednjem bajtu
datoteke. Pogrešno pročitano zaglavlje to ne može proizvesti. Test na
instaliranoj igri ponavlja to na do šest datoteka `resources.assets` /
`sharedassets0.assets` pronađenih u folderima `*_Data`.

## Bundlovi (`UnityFS`) {#bundles-unityfs}

Bundle je komprimirani kontejner SerializedFile datoteka. Lista blokova i
direktorij su također komprimirani. Metoda je u donjih šest bitova riječi
zastavica: 0 pohranjeno, 1 LZMA (Unityjevo zaglavlje od 5 bajta s umetnutom
veličinom), 2 i 3 LZ4 / LZ4HC. Format 7 i noviji poravnavaju zaglavlje na 16
bajta. Zastavica `0x80` stavlja direktorij na kraj datoteke. `UnityWeb`,
`UnityRaw` i `UnityArchive` (prije 5.3) se prepoznaju, ali ne čitaju.

## Mreže {#meshes}

`read_mesh` dekodira objekat `Mesh` u pozicije, normale, prvi UV skup i
trouglove, redoslijedom kojim ih piše Unity 2019+: ime, podmreže, blend shapeovi
(preskaču se), bind poze i podaci o kostima (preskaču se), zastavice kompresije i
čitljivosti, bafer indeksa, kanali vrhova i podaci vrhova, blok komprimirane
mreže, lokalna granična kutija i informacije o streamingu.

- **Vanjski vrhovi.** Većina isporučene geometrije živi u `.resS` datoteci pored
  kontejnera. Alat je čita iz foldera kontejnera (koristi se samo ime datoteke
  pohranjene putanje `archive:/...`). Nedostajući `.resS` je greška, a ne prazna
  mreža.
- **Streamovi i kanali.** Kanali kažu koji stream, pomak, format i dimenziju ima
  svaki atribut. Streamovi su pakirani jedan za drugim, svaki dopunjen na 16
  bajta, pa se početak streama akumulira iz striddova prije njega. Formati:
  float32, float16, unorm/snorm 8 i 16 (normalizirani) i obični cijeli brojevi.
- **Topologija.** Samo trouglovi (topologija 0). Trake, četverouglovi i linije se
  odbijaju, jer pogrešna konverzija izgleda kao prava geometrija.
- **Komprimirane mreže** (kvantizirane delte) se odbijaju: "mesh '...' is stored
  compressed; that encoding is not implemented".

### Samoprovjera {#the-self-check}

Čitanje strukture pogrešnim redoslijedom ne izaziva grešku. Daje uvjerljive
brojeve. Zato se svaka dekodirana mreža provjerava naspram **granične kutije koju
je Unity pohranio za nju**, a koju je editor izračunao iz pravih vrhova.
`aabb_matches()` prolazi kad su uglovi dekodirane kutije unutar 2% veličine
pohranjene kutije. `meshes` na svakom redu ispisuje `ok` ili `BOUNDS DISAGREE`.

**Provjereno:** mreže uzorkovane iz nekoliko igara dekodiraju se s granicama koje
se slažu. Test na instaliranoj igri ponavlja provjeru na instaliranim kontejnerima.

## Nije implementirano {#not-implemented}

- Formati prije 2020.
- Komprimirane mreže.
- Bilo koja klasa osim `Mesh`: nema grafa scene, transformacija ili materijala,
  pa su mreže u svom lokalnom prostoru.
- `meshes` na bundleu. Čitač bundlova postoji u Pythonu
  (`UnityBundle.serialized_files()`), ali komanda uzima goli kontejner.
