---
title: Unity
nav_order: 4
lang: "hr"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, paketi, mreže {#unity-serializedfile-bundles-meshes}

**Popisuje objekte i dekodira mreže** Unity `SerializedFile` formata 22 i novijih (Unity 2020
do 6000), i otvara `UnityFS` pakete. Ne postoji izvoz staze za Unity.

Izvori: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Naredbe: `identify` (spremnici i paketi), `meshes` (samo goli spremnici).

## Spremnik {#the-container}

Unity isporučuje razinu kao serijalizirane grafove objekata: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` i paketi assetā. Svaka sadrži tablicu
objekata označenih ID-jem klase.

Zaglavlje je mjesto gdje čitanje tiho pogriješi. Prvih šesnaest bajtova su četiri
`uint32` u big-endianu, sačuvana radi kompatibilnosti. U formatu 22 tri su nula, a stvarne
vrijednosti slijede, jer datoteka može premašiti 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Drugi `metadata size` je `uint32` između dva `int64`. Ako se sve tri pretpostave kao 64-bitne,
verzijski niz se pomakne za četiri bajta. I dalje se dekodira u nešto što liči na niz i šalje
sve iza njega na krivo mjesto. Zaglavlje je big-endian. Sve iza njega slijedi bajt
endianness (0, little-endian, na svakoj desktop verziji).

Nakon zaglavlja: verzijski niz motora, platforma, zastavica stabla tipova, tablica tipova (ID
klase po tipu), tablica objekata (ID putanje, pomak, veličina, tip) i vanjski objekti (druge
datoteke na koje pokazivač može upućivati).

| Slučaj | Rezultat |
|---|---|
| format 22-30 | čita se |
| format 9-21 (prije Unity 2020) | odbijeno: pomaci su u legacy zaglavlju, a nijedna datoteka pri ruci ga nije koristila |
| izvan 9-30 | odbijeno |
| stablo tipova ugrađeno (izdanja urednika) | odbijeno: isporučene verzije ga ne ugrađuju, a put za urednik nije implementiran |
| paket predan tamo gdje se očekuje spremnik | odbijeno, uz upućivanje na čitač paketa |

**Nema općeg deserijalizatora.** Isporučene verzije ne nose stablo tipova, jer je shema
ugrađena u samu igru, pa svaka klasa mora biti parsirana prema rasporedu poznatom za njezinu
verziju. Dekodira se samo `Mesh`. Ostale klase prijavljuju se po imenu i broju
(`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`,
`MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`, `RectTransform`,
`PrefabInstance`; ostale kao `class<id>`).

**Provjereno** na mnogo instaliranih igara i milijunima objekata: tablica objekata mora
popločiti podatkovni dio točno, bez preklapanja, s ničim osim popunjavanja poravnanja između
objekata, a zadnji objekt završava na zadnjem bajtu datoteke. Pogreška u zaglavlju to ne može
proizvesti. Test na instaliranoj igri ponavlja to na do šest datoteka `resources.assets` /
`sharedassets0.assets` pronađenih u mapama `*_Data`.

## Paketi (`UnityFS`) {#bundles-unityfs}

Paket je komprimirani spremnik serijaliziranih datoteka. Popis blokova i direktorij su također
komprimirani. Metoda je u donjih šest bitova riječi zastavica: 0 pohranjeno, 1 LZMA (Unityjevo
zaglavlje od 5 bajtova s umetnutom veličinom), 2 i 3 LZ4 / LZ4HC. Format 7 i noviji poravnavaju
zaglavlje na 16 bajtova. Zastavica `0x80` stavlja direktorij na kraj datoteke. `UnityWeb`,
`UnityRaw` i `UnityArchive` (prije 5.3) se prepoznaju, ali se ne čitaju.

## Mreže {#meshes}

`read_mesh` dekodira objekt `Mesh` u pozicije, normale, prvi skup UV-ova i trokute, redoslijedom
kojim ga piše Unity 2019+: ime, podmreže, oblici mješavine (preskočeni), bind pozicije i podaci
o kostima (preskočeni), zastavice kompresije i čitljivosti, međuspremnik indeksa, kanali vrhova i
podaci vrhova, komprimirani blok mreže, lokalna granična kutija i podaci o streamingu.

- **Vanjski vrhovi.** Većina isporučene geometrije živi u `.resS` datoteci pored spremnika. Alat
  je čita iz mape spremnika (koristi se samo ime datoteke iz spremljene putanje `archive:/...`).
  Nedostajući `.resS` je greška, a ne prazna mreža.
- **Tokovi i kanali.** Kanali govore koji tok, pomak, format i dimenzija pripada svakom
  atributu. Tokovi su složeni jedan za drugim, svaki popunjen do 16 bajtova, pa se početak toka
  zbraja iz koraka prije njega. Formati: float32, float16, unorm/snorm 8 i 16 (normalizirani), i
  obični cijeli brojevi.
- **Topologija.** Samo trokuti (topologija 0). Trake, četverokuti i linije se odbijaju, jer
  krivo pretvaranje izgleda kao stvarna geometrija.
- **Komprimirane mreže** (kvantizirane razlike) se odbijaju: "mesh '...' is stored compressed;
  that encoding is not implemented".

### Samoprovjera {#the-self-check}

Čitanje strukture u krivom redoslijedu ne podiže grešku. Daje uvjerljive brojeve. Zato se svaka
dekodirana mreža provjerava prema **kutiji granica koju je Unity spremio za nju**, koju je
izračunao urednik iz stvarnih vrhova. `aabb_matches()` prolazi kad se kutovi dekodirane kutije
nalaze unutar 2% veličine spremljene kutije. `meshes` ispisuje `ok` ili `BOUNDS DISAGREE` u svakom
retku.

**Provjereno:** mreže uzorkovane kroz nekoliko igara se dekodiraju s podudarnim granicama.
Test na instaliranoj igri ponavlja provjeru na instaliranim spremnicima.

## Nije implementirano {#not-implemented}

- Formati prije 2020.
- Komprimirane mreže.
- Bilo koja klasa osim `Mesh`: nema grafa scene, transformacija ni materijala, pa su mreže u
  vlastitom lokalnom prostoru.
- `meshes` na paketu. Čitač paketa postoji u Pythonu (`UnityBundle.serialized_files()`), ali
  naredba uzima goli spremnik.
