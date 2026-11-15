---
title: "Unity: `SerializedFile`, pachete, mesh-uri"
nav_order: 4
lang: "ro"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, pachete, mesh-uri {#unity-serializedfile-bundles-meshes}

**Listează obiecte și decodează mesh-uri** din `SerializedFile` Unity format 22 și mai nou (Unity 2020 până la 6000), și deschide pachete `UnityFS`. Nu există un export de circuit Unity.

Surse: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Comenzi: `identify` (containere și pachete), `meshes` (doar containere simple).

## Containerul {#the-container}

Unity livrează un nivel ca grafuri de obiecte serializate: `globalgamemanagers`, `sharedassets*.assets`, `resources.assets`, `level*` și pachete de active. Fiecare conține un tabel de obiecte etichetate cu un id de clasă.

Antetul este locul unde citirea greșește pe tăcute. Primii șaisprezece octeți sunt patru `uint32` big-endian păstrate din compatibilitate. În format 22, trei dintre ele sunt zero, iar valorile reale urmează, pentru că un fișier poate depăși 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

A doua `metadata size` este un `uint32` între două `int64`. Dacă presupui că toate trei sunt de 64 de biți, șirul de versiune este deplasat cu patru octeți. Tot se decodează ca ceva cu formă de șir și trimite tot ce urmează pe un drum greșit. Antetul este big-endian. Totul de după el urmează octetul de ordine (0, little-endian, pe orice build de desktop).

După antet: șirul de versiune al motorului, platforma, indicatorul arborelui de tipuri, tabelul de tipuri (id de clasă pentru fiecare tip), tabelul de obiecte (id de cale, decalaj, dimensiune, tip) și externele (alte fișiere la care poate face referire un pointer).

| Caz | Rezultat |
|---|---|
| format 22-30 | citit |
| format 9-21 (dinainte de Unity 2020) | refuzat: decalajele sunt în antetul vechi, iar niciun fișier la îndemână nu îl folosea |
| în afara lui 9-30 | refuzat |
| arbore de tipuri încorporat (build-uri de editor) | refuzat: build-urile livrate nu încorporează unul, iar calea de editor nu este implementată |
| un pachet dat unde se așteaptă un container | refuzat, cu o indicație spre cititorul de pachete |

Nu există **niciun deserializator general**. Build-urile livrate nu poartă arbore de tipuri, pentru că schema este compilată în player, deci fiecare clasă trebuie parsată după un layout cunoscut pentru versiunea ei. Doar `Mesh` este decodat. Celelalte clase sunt raportate după nume și număr (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; restul ca `class<id>`).

**Verificat** pe multe jocuri instalate și pe milioane de obiecte: tabelul de obiecte trebuie să acopere exact secțiunea de date, fără suprapuneri, fără nimic altceva decât padding de aliniere între obiecte, iar ultimul obiect să se termine la ultimul octet al fișierului. O citire greșită a antetului nu poate produce asta. Testul pe jocul instalat repetă verificarea pe până la șase fișiere `resources.assets` / `sharedassets0.assets` găsite în folderele `*_Data`.

## Pachete (`UnityFS`) {#bundles-unityfs}

Un pachet este un container comprimat de fișiere SerializedFile. Lista de blocuri și directorul sunt și ele comprimate. Metoda se află în cei șase biți mici ai unui cuvânt de steaguri: 0 stocat, 1 LZMA (antetul de 5 octeți al Unity cu dimensiunea lipită în el), 2 și 3 LZ4 / LZ4HC. Formatul 7 și cele ulterioare aliniază antetul la 16 octeți. Steagul `0x80` pune directorul la sfârșitul fișierului. `UnityWeb`, `UnityRaw` și `UnityArchive` (dinainte de 5.3) sunt recunoscute, dar nu sunt citite.

## Mesh-uri {#meshes}

`read_mesh` decodează un obiect `Mesh` în poziții, normale, primul set de UV și triunghiuri, în ordinea în care scrie Unity 2019+: nume, submeshuri, blend shape-uri (sărite), poziții de bind și date de oase (sărite), steagurile de compresie și de citibilitate, bufferul de index, canalele și datele de vertex, blocul de mesh comprimat, caseta locală de încadrare și informațiile de streaming.

- **Vertexuri externe.** Cea mai mare parte a geometriei livrate se află într-un fișier `.resS` de lângă container. Instrumentul îl citește din folderul containerului (se folosește doar numele fișierului din calea stocată `archive:/...`). Un `.resS` lipsă este o eroare, nu un mesh gol.
- **Fluxuri și canale.** Canalele spun ce flux, decalaj, format și dimensiune are fiecare atribut. Fluxurile sunt puse unul după altul, fiecare umplut până la 16 octeți, deci începutul unui flux se acumulează din pașii dinaintea lui. Formate: float32, float16, unorm/snorm pe 8 și 16 biți (normalizate) și numere întregi simple.
- **Topologie.** Doar triunghiuri (topologia 0). Benzile, patrulaterele și liniile sunt refuzate, pentru că o conversie greșită arată a geometrie reală.
- **Mesh-uri comprimate** (delte cuantizate) sunt refuzate: "mesh '...' is stored compressed; that encoding is not implemented".

### Autoverificarea {#the-self-check}

Citirea unei structuri în ordinea greșită nu ridică o eroare. Produce numere plauzibile. Așadar fiecare mesh decodat este verificat față de **caseta de încadrare pe care Unity a stocat-o pentru el**, calculată de editor din vertexurile reale. `aabb_matches()` trece când colțurile casetei decodate sunt în 2% din dimensiunea casetei stocate. `meshes` afișează `ok` sau `BOUNDS DISAGREE` pe fiecare rând.

**Verificat:** mesh-uri eșantionate din mai multe jocuri se decodează cu limitele lor în acord. Testul pe jocul instalat repetă verificarea pe containerele instalate.

## Neimplementat {#not-implemented}

- Formate dinainte de 2020.
- Mesh-uri comprimate.
- Orice clasă în afară de `Mesh`: fără graf de scenă, transformări sau materiale, deci mesh-urile sunt în spațiul lor local.
- `meshes` pe un pachet. Cititorul de pachete există în Python (`UnityBundle.serialized_files()`), dar comanda primește un container simplu.
