---
title: Unity
nav_order: 4
lang: "cs"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, bundly, sítě {#unity-serializedfile-bundles-meshes}

**Vypisuje objekty a dekóduje sítě** `SerializedFile` Unity formátu 22 a novějšího
(Unity 2020 až 6000) a otevírá bundly `UnityFS`. Export tratí pro Unity neexistuje.

Zdroje: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Příkazy: `identify` (kontejnery a bundly), `meshes` (jen holé kontejnery).

## Kontejner {#the-container}

Unity dodává úroveň jako serializované grafy objektů: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` a asset bundly. Každý obsahuje
tabulku objektů označených ID třídy.

Hlavička je místo, kde se čtení tiše pokazí. Prvních šestnáct bajtů jsou čtyři
`uint32` v big-endian, ponechané kvůli kompatibilitě. U formátu 22 jsou tři z nich
nulové a skutečné hodnoty následují, protože soubor může přesáhnout 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Druhá `metadata size` je `uint32` mezi dvěma `int64`. Kdyby se všechny tři braly
jako 64bitové, řetězec verze přijde o čtyři bajty pozdě. Pořád se dekóduje na něco,
co vypadá jako řetězec, a všechno za ním se posune špatně. Hlavička je big-endian.
Všechno za ní se řídí bajtem endianity (0, little-endian, u každé desktopové verze).

Za hlavičkou: řetězec verze enginu, platforma, příznak stromu typů, tabulka typů
(ID třídy na typ), tabulka objektů (ID cesty, posun, velikost, typ) a externí
odkazy (jiné soubory, na které může ukazatel směřovat).

| Případ | Výsledek |
|---|---|
| formát 22-30 | čte se |
| formát 9-21 (před Unity 2020) | odmítnuto: posuny jsou v legacy hlavičce a žádný soubor po ruce ji nepoužíval |
| mimo 9-30 | odmítnuto |
| vložený strom typů (buildy z editoru) | odmítnuto: dodané buildy strom nevkládají a cesta editoru není implementována |
| bundle předaný tam, kde se čeká kontejner | odmítnuto, s odkazem na čtečku bundlů |

Není tu **žádný obecný deserializátor**. Dodané buildy nesou strom typů, protože
schéma je zkompilované do přehrávače, takže každá třída se musí parsovat proti
rozložení známému pro danou verzi. Dekóduje se jen `Mesh`. Ostatní třídy se hlásí
podle jména a počtu (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`,
`Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; ostatní jako `class<id>`).

**Ověřeno** napříč mnoha nainstalovanými hrami a miliony objektů: tabulka objektů
musí přesně pokrývat datovou sekci, bez překryvů, s ničím jiným než zarovnávací
výplní mezi objekty, a poslední objekt musí končit na posledním bajtu souboru.
Chybné čtení hlavičky takový výsledek nevytvoří. Test na nainstalované hře to
opakuje na až šesti souborech `resources.assets` / `sharedassets0.assets` ve
složkách `*_Data`.

## Bundly (`UnityFS`) {#bundles-unityfs}

Bundle je komprimovaný kontejner souborů SerializedFile. Seznam bloků a adresář jsou
také komprimované. Metoda je v nízkých šesti bitech slova příznaků: 0 uloženo, 1 LZMA
(5bajtová hlavička Unity s vloženou velikostí), 2 a 3 LZ4 / LZ4HC. Formát 7 a novější
zarovnává hlavičku na 16 bajtů. Příznak `0x80` dá adresář na konec souboru.
`UnityWeb`, `UnityRaw` a `UnityArchive` (před 5.3) se rozpoznají, ale nečtou se.

## Sítě {#meshes}

`read_mesh` dekóduje objekt `Mesh` na pozice, normály, první sadu UV a trojúhelníky,
v pořadí, které zapisuje Unity 2019+: název, podsítě, tvarové klíče (přeskočí se),
bind pózy a kostní data (přeskočí se), příznaky komprese a čitelnosti, buffer
indexů, kanály vrcholů a data vrcholů, komprimovaný blok sítě, lokální ohraničující
box a informace o streamování.

- **Externí vrcholy.** Většina dodané geometrie je v souboru `.resS` vedle
  kontejneru. Nástroj ho čte ze složky kontejneru (použije se jen název souboru
  z uložené cesty `archive:/...`). Chybějící `.resS` je chyba, ne prázdná síť.
- **Proudy a kanály.** Kanály říkají, který proud, posun, formát a dimenzi má každý
  atribut. Proudy jsou za sebou, každý vyplněný na 16 bajtů, takže začátek proudu se
  počítá z kroků před ním. Formáty: float32, float16, unorm/snorm 8 a 16
  (normalizované) a prosté celé číslo.
- **Topologie.** Jen trojúhelníky (topologie 0). Pásy, čtyřúhelníky a čáry se
  odmítnou, protože špatná konverze vypadá jako skutečná geometrie.
- **Komprimované sítě** (kvantizované delty) se odmítnou: "mesh '...' is stored
  compressed; that encoding is not implemented".

### Vlastní kontrola {#the-self-check}

Čtení struktury v špatném pořadí nevyvolá chybu. Vyprodukuje věrohodná čísla. Proto
se každá dekódovaná síť kontroluje proti **ohraničujícímu boxu, který pro ni Unity
uložila**, spočítanému editorem z reálných vrcholů. `aabb_matches()` projde, když
rohy dekódovaného boxu jsou do 2 % velikosti uloženého boxu. `meshes` vypíše na
každém řádku `ok`, nebo `BOUNDS DISAGREE`.

**Ověřeno:** sítě vzorkované napříč několika hrami se dekódují a jejich hranice
souhlasí. Test na nainstalované hře opakuje kontrolu na nainstalovaných kontejnerech.

## Neimplementováno {#not-implemented}

- Formáty před rokem 2020.
- Komprimované sítě.
- Jakákoli třída kromě `Mesh`: žádný graf scény, transformace ani materiály, takže
  sítě jsou ve svém vlastním lokálním prostoru.
- `meshes` na bundlu. Čtečka bundlů v Pythonu existuje (`UnityBundle.serialized_files()`),
  ale příkaz bere holý kontejner.
