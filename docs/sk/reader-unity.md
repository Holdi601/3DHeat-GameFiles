---
title: Unity
nav_order: 4
lang: "sk"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, zväzky, siete {#unity-serializedfile-bundles-meshes}

**Vypisuje objekty a dekóduje siete** formátu `SerializedFile` Unity 22 a novšieho
(Unity 2020 až 6000) a otvára zväzky `UnityFS`. Export trate pre Unity neexistuje.

Zdroje: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Príkazy: `identify` (kontajnery a zväzky), `meshes` (len holé kontajnery).

## Kontajner {#the-container}

Unity dodáva level ako serializované grafy objektov: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` a asset zväzky. Každý obsahuje
tabuľku objektov označených ID triedy.

Hlavička je miesto, kde sa čítanie potichu pokazí. Prvých šestnásť bajtov sú štyri
`uint32` v big-endian, zachované kvôli kompatibilite. Vo formáte 22 sú tri z nich nula
a skutočné hodnoty nasledujú, lebo súbor môže presiahnuť 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Druhá `metadata size` je `uint32` medzi dvoma `int64`. Ak sa predpokladá, že všetky tri
sú 64-bitové, reťazec verzie sa posunie o štyri bajty. Stále to dekóduje na niečo, čo
vyzerá ako reťazec, a pošle všetko za ním zle. Hlavička je big-endian. Všetko ostatné
nasleduje bajt endianity (0, little-endian, na každom desktopovom builde).

Za hlavičkou: reťazec verzie enginu, platforma, príznak stromu typov, tabuľka typov
(ID triedy na typ), tabuľka objektov (path id, offset, veľkosť, typ) a externé odkazy
(iné súbory, na ktoré môže ukazovateľ smerovať).

| Prípad | Výsledok |
|---|---|
| formát 22-30 | prečíta sa |
| formát 9-21 (pred Unity 2020) | odmietnuté: offsety sú v starej hlavičke a žiadny súbor po ruke ju nepoužíval |
| mimo 9-30 | odmietnuté |
| strom typov vložený (editorové buildy) | odmietnuté: dodávané buildy strom nevkladajú a cesta pre editor nie je implementovaná |
| zväzok podaný tam, kde sa čaká kontajner | odmietnuté, s odkazom na čítačku zväzkov |

**Nie je tu žiadny všeobecný deserializátor.** Dodávané buildy nenesú strom typov,
lebo schéma je skompilovaná do prehrávača, takže každá trieda sa musí parsovať proti
rozloženiu známemu pre jej verziu. Dekóduje sa len `Mesh`. Ostatné triedy sa hlásia
menom a počtom (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`,
`BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`,
`RectTransform`, `PrefabInstance`; ostatné ako `class<id>`).

**Overené** naprieč mnohými nainštalovanými hrami a miliónmi objektov: tabuľka objektov
musí pokrývať dátovú sekciu presne, bez prekryvov, nič okrem zarovnávacej výplne medzi
objektmi a posledný objekt končí na poslednom bajte súboru. Chyba v hlavičke takéto
niečo nevyprodukuje. Test na nainštalovanej hre to zopakuje na až šiestich súboch
`resources.assets` / `sharedassets0.assets` nájdených v priečinkoch `*_Data`.

## Zväzky (`UnityFS`) {#bundles-unityfs}

Zväzok je komprimovaný kontajner súborov SerializedFile. Zoznam blokov a adresár sú
tiež komprimované. Metóda je v nižších šiestich bitoch slova príznakov: 0 uložené, 1
LZMA (Unity 5-bajtová hlavička s vloženou veľkosťou), 2 a 3 LZ4 / LZ4HC. Formát 7
a novšie zarovnávajú hlavičku na 16 bajtov. Príznak `0x80` dáva adresár na koniec
súboru. `UnityWeb`, `UnityRaw` a `UnityArchive` (pred 5.3) sa rozpoznajú, ale nečítajú.

## Siete {#meshes}

`read_mesh` dekóduje objekt `Mesh` na pozície, normály, prvú sadu UV a trojuholníky,
v poradí, v akom ho píše Unity 2019+: názov, podsiete, tvary blendu (preskočené),
bind pózy a dáta kostí (preskočené), príznaky kompresie a čitateľnosti, buffer indexov,
kanály vrcholov a dáta vrcholov, komprimovaný blok siete, lokálny ohraničujúci box
a informácie o streamovaní.

- **Externé vrcholy.** Väčšina dodávanej geometrie je v súbore `.resS` vedľa
  kontajnera. Nástroj ho číta z priečinka kontajnera (použije sa len názov súboru
  z uloženej cesty `archive:/...`). Chýbajúci `.resS` je chyba, nie prázdna sieť.
- **Streamy a kanály.** Kanály hovoria, ktorý stream, offset, formát a dimenziu má
  každý atribút. Streamy sú zabalené jeden za druhým, každý zarovnaný na 16 bajtov,
  takže začiatok streamu sa nasčíta z krokov pred ním. Formáty: float32, float16,
  unorm/snorm 8 a 16 (normalizované) a obyčajné celé čísla.
- **Topológia.** Len trojuholníky (topológia 0). Pásy, štvorce a čiary sa odmietnu,
  lebo zlá konverzia vyzerá ako skutočná geometria.
- **Komprimované siete** (kvantizované delty) sa odmietnu: „mesh '...' is stored
  compressed; that encoding is not implemented“.

### Sebakontrola {#the-self-check}

Čítanie štruktúry v zlom poradí nevyhodí chybu. Vyprodukuje vierohodné čísla. Preto sa
každá dekódovaná sieť overí voči **ohraničujúcemu boxu, ktorý pre ňu Unity uložila**,
vypočítanému editorom zo skutočných vrcholov. `aabb_matches()` prejde, keď rohy
dekódovaného boxu sú do 2 % veľkosti uloženého boxu. `meshes` vypíše pri každom riadku
`ok` alebo `BOUNDS DISAGREE`.

**Overené:** siete vzorkované naprieč viacerými hrami sa dekódujú a ich boxy sedia.
Test na nainštalovanej hre to zopakuje na nainštalovaných kontajneroch.

## Nie je implementované {#not-implemented}

- Formáty pred rokom 2020.
- Komprimované siete.
- Akákoľvek trieda okrem `Mesh`: žiadny graf scény, transformácie ani materiály, takže
  siete sú vo svojom lokálnom priestore.
- `meshes` nad zväzkom. Čítačka zväzkov v Pythone existuje
  (`UnityBundle.serialized_files()`), ale príkaz berie holý kontajner.
