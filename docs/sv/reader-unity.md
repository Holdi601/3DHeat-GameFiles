---
title: Unity
nav_order: 4
lang: "sv"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, paket, meshar {#unity-serializedfile-bundles-meshes}

**Listar objekt och avkodar meshar** i Unity `SerializedFile` format 22 och senare
(Unity 2020 till 6000), och öppnar `UnityFS`-paket. Det finns ingen Unity-banexport.

Källkod: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Kommandon: `identify` (behållare och paket), `meshes` (bara nakna behållare).

## Behållaren {#the-container}

Unity levererar en nivå som serialiserade objektgrafer: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` och assetpaket. Varje
innehåller en tabell med objekt, taggade med ett klass-id.

Headern är där läsningen går fel på ett tyst sätt. De första sexton byten är fyra
big-endian `uint32` som finns kvar av kompatibilitetsskäl. I format 22 är tre av dem
noll, och de riktiga värdena följer eftersom en fil kan vara större än 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Den andra `metadata size` är en `uint32` mellan två `int64`. Antar man att alla tre är
64-bitars hamnar versionssträngen fyra byte för sent. Den avkodas ändå till något som
ser ut som en sträng och skickar allt efter den vilse. Headern är big-endian. Allt
efter den följer endianness-byten (0, little-endian, på alla stationära byggen).

Efter headern: motorversionssträngen, plattformen, typträdsflaggan, typtabellen (klass-id per
typ), objekttabellen (sökvägs-id, offset, storlek, typ) och externa referenser (andra
filer som en pekare kan hänvisa till).

| Fall | Resultat |
|---|---|
| format 22-30 | läses |
| format 9-21 (före Unity 2020) | vägras: offseten finns i den gamla headern, och ingen fil på hand använde den |
| utanför 9-30 | vägras |
| inbäddat typträd (editorbyggen) | vägras: levererade byggen bäddar inte in ett, och editorvägen är inte implementerad |
| ett paket där en behållare väntas | vägras, med en pekare till paketläsaren |

Det finns **ingen generell deserialiserare**. Levererade byggen bär inget typträd,
eftersom schemat är kompilerat i spelaren, så varje klass måste parsas mot en layout
som är känd för sin version. Bara `Mesh` avkodas. Andra klasser rapporteras med namn
och antal (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`,
`BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`,
`RectTransform`, `PrefabInstance`; andra som `class<id>`).

**Verifierat** över många installerade spel och miljontals objekt: objekttabellen
måste lägga sig exakt över datasektionen, utan överlapp, med bara justeringsutfyllnad
mellan objekten, och det sista objektet slutar på filens sista byte. En felläst header
kan inte ge det. Testet mot installerat spel upprepar det på upp till sex
`resources.assets`- / `sharedassets0.assets`-filer i `*_Data`-mappar.

## Paket (`UnityFS`) {#bundles-unityfs}

Ett paket är en komprimerad behållare av SerializedFiles. Blocklistan och katalogen är
också komprimerade. Metoden finns i de lägsta sex bitarna i ett flaggord: 0 lagrad,
1 LZMA (Unitys 5-byte-header med storleken infogad), 2 och 3 LZ4 / LZ4HC. Format 7 och
senare justerar headern till 16 byte. Flagga `0x80` lägger katalogen i slutet av filen.
`UnityWeb`, `UnityRaw` och `UnityArchive` (före 5.3) känns igen men läses inte.

## Meshar {#meshes}

`read_mesh` avkodar ett `Mesh`-objekt till positioner, normaler, den första UV-uppsättningen
och trianglar, i den ordning Unity 2019+ skriver dem: namn, undermeshar, blendformer
(hoppas över), bind-poser och benData (hoppas över), komprimerings- och läsbarhetsflaggorna,
indexbufferten, vertexkanalerna och vertexdata, det komprimerade meshblocket, den lokala
omslutningsrutan och strömningsinformationen.

- **Externa vertexar.** Det mesta levererade geometrin ligger i en `.resS`-fil bredvid
  behållaren. Verktyget läser den från behållarens mapp (bara filnamnet i den lagrade
  `archive:/...`-sökvägen används). En saknad `.resS` är ett fel, inte en tom mesh.
- **Strömmar och kanaler.** Kanalerna anger vilken ström, offset, format och dimension
  varje attribut har. Strömmarna packas efter varandra, var och en utfylld till 16 byte,
  så en strömsstarts position ackumuleras från stridarna före den.
  Format: float32, float16, unorm/snorm 8 och 16 (normaliserade) och vanliga heltal.
- **Topologi.** Bara trianglar (topologi 0). Band, fyrhörningar och linjer vägras,
  eftersom en felaktig konvertering ser ut som verklig geometri.
- **Komprimerade meshar** (kvantiserade deltan) vägras: "mesh '...' is stored
  compressed; that encoding is not implemented".

### Självkontrollen {#the-self-check}

Att läsa en struktur i fel ordning ger inget fel. Det ger rimliga tal. Därför kontrolleras
varje avkodad mesh mot **omslutningsrutan som Unity lagrat för den**, beräknad av
editorn från de riktiga vertexarna. `aabb_matches()` passerar när den avkodade rutans
hörn ligger inom 2 % av den lagrade rutans storlek. `meshes` skriver `ok` eller
`BOUNDS DISAGREE` på varje rad.

**Verifierat:** meshar samplade över flera spel avkodas med omslutningsrutor som
stämmer. Testet mot installerat spel upprepar kontrollen på de installerade behållarna.

## Inte implementerat {#not-implemented}

- Format före 2020.
- Komprimerade meshar.
- Någon klass utom `Mesh`: ingen scengraf, inga transformer eller material, så meshar
  ligger i sitt eget lokala rum.
- `meshes` på ett paket. Paketläsaren finns i Python (`UnityBundle.serialized_files()`),
  men kommandot tar en naken behållare.
