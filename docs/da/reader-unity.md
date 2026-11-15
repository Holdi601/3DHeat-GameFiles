---
title: "Unity: `SerializedFile`, bundles, meshes"
nav_order: 4
lang: "da"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, bundles, meshes {#unity-serializedfile-bundles-meshes}

**Lister objekter og afkoder meshes** af Unity `SerializedFile` format 22 og senere (Unity 2020 til 6000), og åbner `UnityFS`-bundles. Der er ingen Unity course-eksport.

Kilder: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Kommandoer: `identify` (containere og bundles), `meshes` (kun rene containere).

## Containeren {#the-container}

Unity leverer et niveau som serialiserede objektgrafer: `globalgamemanagers`, `sharedassets*.assets`, `resources.assets`, `level*` og asset-bundles. Hver indeholder en tabel over objekter mærket med et klasse-id.

Headeren er der, læsning stille går galt. De første seksten bytes er fire big-endian `uint32` bevaret af hensyn til kompatibilitet. I format 22 er tre af dem nul, og de rigtige værdier følger, fordi en fil kan overstige 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Den anden `metadata size` er en `uint32` mellem to `int64`. Hvis man antager, at alle tre er 64-bit, placeres versionsstrengen fire bytes for sent. Den afkodes stadig til noget strengagtigt og sender alt efter den på afveje. Headeren er big-endian. Alt efter den følger endianness-byten (0, little-endian, på hver desktop-build).

Efter headeren: motorversionsstrengen, platformen, typetræ-flaget, typetabellen (klasse-id pr. type), objekttabellen (sti-id, offset, størrelse, type) og de eksterne (andre filer en pointer kan henvise til).

| Tilfælde | Resultat |
|---|---|
| format 22-30 | læst |
| format 9-21 (før Unity 2020) | afvist: offsets står i den ældre header, og ingen fil ved hånden brugte den |
| uden for 9-30 | afvist |
| typetræ indlejret (editor-builds) | afvist: leverede builds indlejrer ikke et, og editorstien er ikke implementeret |
| en bundle givet, hvor en container forventes | afvist, med en henvisning til bundle-læseren |

Der er **ingen generel deserialiserer**. Leverede builds har intet typetræ, fordi skemaet er kompileret ind i afspilleren, så hver klasse skal parses mod et layout, der er kendt for dens version. Kun `Mesh` afkodes. Andre klasser rapporteres med navn og antal (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; andre som `class<id>`).

**Verificeret** på tværs af mange installerede spil og millioner af objekter: objekttabellen skal dække datasektionen præcist, uden overlap, med kun justerings-padding mellem objekter, og det sidste objekt slutter på filens sidste byte. En fejllæst header kan ikke frembringe det. Testen mod det installerede spil gentager det på op til seks `resources.assets` / `sharedassets0.assets`-filer i `*_Data`-mapper.

## Bundles (`UnityFS`) {#bundles-unityfs}

En bundle er en komprimeret container af SerializedFiles. Blok-listen og mappen er også komprimeret. Metoden ligger i de laveste seks bit af et flag-ord: 0 gemt, 1 LZMA (Unitys 5-byte header med størrelsen indsat), 2 og 3 LZ4 / LZ4HC. Format 7 og senere justerer headeren til 16 bytes. Flag `0x80` lægger mappen til sidst i filen. `UnityWeb`, `UnityRaw` og `UnityArchive` (før 5.3) genkendes, men læses ikke.

## Meshes {#meshes}

`read_mesh` afkoder et `Mesh`-objekt til positioner, normaler, det første UV-sæt og trekanter, i den rækkefølge Unity 2019+ skriver dem: navn, undermeshes, blend shapes (springes over), bind poses og bone-data (springes over), komprimerings- og læsbarhedsflag, indeksbufferen, vertex-kanalerne og vertexdata, den komprimerede meshblok, den lokale bounding box og streaming-info.

- **Eksterne vertices.** Det meste leverede geometri ligger i en `.resS`-fil ved siden af containeren. Værktøjet læser den fra containerens mappe (kun filnavnet i den gemte `archive:/...`-sti bruges). En manglende `.resS` er en fejl, ikke en tom mesh.
- **Streams og kanaler.** Kanaler angiver, hvilken stream, offset, format og dimension hver attribut har. Streams er pakket efter hinanden, hver polstret til 16 bytes, så en streams start akkumuleres ud fra skridtene før den. Formater: float32, float16, unorm/snorm 8 og 16 (normaliseret) og rene heltal.
- **Topologi.** Kun trekanter (topologi 0). Strimler, quads og linjer afvises, fordi en forkert konvertering ligner rigtig geometri.
- **Komprimerede meshes** (kvantiserede deltaer) afvises: `mesh '...' is stored compressed; that encoding is not implemented`.

### Selvtjekket {#the-self-check}

At læse en struct i forkert rækkefølge giver ikke en fejl. Det giver troværdige tal. Derfor tjekkes hver afkodet mesh mod den **bounding box, Unity gemte for den**, beregnet af editoren ud fra de rigtige vertices. `aabb_matches()` består, når den afkodede boks' hjørner er inden for 2 % af den gemte boks' størrelse. `meshes` udskriver `ok` eller `BOUNDS DISAGREE` på hver linje.

**Verificeret:** meshes stikprøvet på tværs af flere spil afkodes med enige grænser. Testen mod det installerede spil gentager tjekket på de installerede containere.

## Ikke implementeret {#not-implemented}

- Formater før 2020.
- Komprimerede meshes.
- Enhver klasse ud over `Mesh`: ingen scenegraf, transformationer eller materialer, så meshes er i deres egen lokale plads.
- `meshes` på en bundle. Bundle-læseren findes i Python (`UnityBundle.serialized_files()`), men kommandoen tager en ren container.
