---
title: Unity
nav_order: 4
lang: "hu"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, csomagok, hálók {#unity-serializedfile-bundles-meshes}

**Listázza az objektumokat és dekódolja a hálókat** a Unity `SerializedFile` 22-es és újabb formátumából
(Unity 2020-tól 6000-ig), és megnyitja a `UnityFS` csomagokat. Nincs Unity-pályaexport.

Forrás: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Parancsok: `identify` (konténerek és csomagok), `meshes` (csak önálló konténerek).

## A konténer {#the-container}

A Unity a pályát szerializált objektumgráfként szállítja: `globalgamemanagers`, `sharedassets*.assets`,
`resources.assets`, `level*`, és asset-csomagok. Mindegyik tartalmaz egy objektumtáblát, osztályazonosítóval
megjelölve.

A fejléc az a hely, ahol az olvasás csendben elromlik. Az első tizenhat bájt négy big-endian `uint32`, a
kompatibilitás miatt. A 22-es formátumban háromnak nulla az értéke, és a valódi értékek utána következnek,
mert egy fájl meghaladhatja a 4 GB-ot:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

A második `metadata size` egy `uint32` két `int64` között. Ha mindhárom 64 bitesnek vesszük, a verziósztring
négy bájttal későn kezdődik. Ettől még sztringszerűnek dekódolódik, és minden utána lévő dolgot félre visz.
A fejléc big-endian. Minden utána következő az endianness-bájtot követi (0, little-endian, minden asztali
buildnél).

A fejléc után: a motor verziósztringje, a platform, a típusfa-jelző, a típustábla (osztályazonosító típusonként),
az objektumtábla (útvonal-azonosító, eltolás, méret, típus) és a külső hivatkozások (más fájlok, amelyekre egy
mutató hivatkozhat).

| Eset | Eredmény |
|---|---|
| 22-30-as formátum | olvasva |
| 9-21-es formátum (Unity 2020 előtt) | megtagadva: az eltolások a régi fejlécben vannak, és nem volt olyan fájl, amellyel tesztelhettük volna |
| 9–30-on kívül | megtagadva |
| beágyazott típusfa (szerkesztői buildek) | megtagadva: a szállított buildek nem ágyazzák be, a szerkesztői út nincs megvalósítva |
| csomag ott, ahol konténert várnak | megtagadva, a csomagolvasóra mutató utalással |

Nincs **általános deszerializáló**. A szállított buildek nem tartalmaznak típusfát, mert a séma bele van
fordítva a lejátszóba, ezért minden osztályt az verziójára ismert elrendezés szerint kell elemezni. Csak a
`Mesh` van dekódolva. A többi osztályt név és darabszám szerint jelentjük (`GameObject`, `Transform`,
`MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; a többi `class<id>`).

**Ellenőrizve** sok telepített játékon és többmillió objektumon: az objektumtáblának pontosan le kell fednie az
adatszakaszt, átfedés nélkül, és az objektumok között csak igazítási kitöltés lehet, az utolsó objektum pedig a
fájl utolsó bájtján ér véget. A fejléc-hibaolvasás ilyet nem tud előállítani. A telepített játékon futó teszt
ezt megismétli legfeljebb hat, a `*_Data` mappákban talált `resources.assets` / `sharedassets0.assets` fájlon.

## Csomagok (`UnityFS`) {#bundles-unityfs}

A csomag tömörített konténer a `SerializedFile`-okból. A blokklista és a könyvtár is tömörítve van. A módszer
a jelzőszó alsó hat bitjében van: 0 tárolt, 1 LZMA (a Unity 5 bájtos fejlécével, a mérettel beillesztve), 2 és 3
LZ4 / LZ4HC. A 7-es és újabb formátum 16 bájtra igazítja a fejlécet. A `0x80` jelző a könyvtárat a fájl végére
teszi. Az `UnityWeb`, `UnityRaw` és `UnityArchive` (5.3 előtt) felismerve, de nincs beolvasva.

## Hálók {#meshes}

A `read_mesh` egy `Mesh` objektumot dekódol pozíciókra, normálokra, az első UV-készletre és háromszögekre, abban
a sorrendben, ahogy a Unity 2019+ írja: név, részhálók, alakzatkulcsok (kihagyva), kötési pózok és csontadatok
(kihagyva), a tömörítési és olvashatósági jelzők, az indexpuffer, a csúcscsatornák és csúcsadatok, a tömörített
hálóblokk, a helyi határoló doboz és a streaming-információ.

- **Külső csúcsok.** A legtöbb szállított geometria a konténer melletti `.resS` fájlban van. Az eszköz a
  konténer mappájából olvassa (a tárolt `archive:/...` útvonalból csak a fájlnév számít). A hiányzó `.resS`
  hiba, nem üres háló.
- **Folyamok és csatornák.** A csatornák megmondják, melyik folyam, eltolás, formátum és dimenzió tartozik
  minden attribútumhoz. A folyamok egymás után vannak csomagolva, mindegyik 16 bájtra kitöltve, így egy folyam
  kezdete az előtte lévő lépések összegéből adódik. Formátumok: float32, float16, unorm/snorm 8 és 16 (normalizált),
  és sima egészek.
- **Topológia.** Csak háromszögek (0-s topológia). A csíkokat, négyszögeket és vonalakat elutasítjuk, mert egy
  rossz átalakítás valódi geometriának látszik.
- **Tömörített hálók** (kvantált különbségek) megtagadva: „mesh '...' is stored compressed; that encoding is not implemented".

### Az önellenőrzés {#the-self-check}

Egy struktúra rossz sorrendben olvasása nem dob hibát. Hihető számokat ad. Ezért minden dekódolt hálót ahhoz a
**határoló dobozhoz hasonlítunk, amelyet a Unity tárolt rá**, a szerkesztő számította a valódi csúcsokból.
Az `aabb_matches()` akkor megfelelő, ha a dekódolt doboz sarkai a tárolt doboz méretének 2%-án belül vannak.
A `meshes` minden során `ok` vagy `BOUNDS DISAGREE` áll.

**Ellenőrizve:** több játékból mintavett hálók dekódolódnak, a határolóik egyeznek. A telepített játékon futó
teszt ezt megismétli a telepített konténereken.

## Nincs megvalósítva {#not-implemented}

- 2020 előtti formátumok.
- Tömörített hálók.
- A `Mesh`-en kívüli bármely osztály: nincs jelenetgráf, transzformáció vagy anyag, így a hálók a saját helyi
  terükben vannak.
- `meshes` csomagon. A csomagolvasó létezik Pythonban (`UnityBundle.serialized_files()`), de a parancs csak
  önálló konténert fogad.
