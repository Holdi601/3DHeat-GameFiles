---
title: Unity
nav_order: 4
lang: "no"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, pakker, meshes {#unity-serializedfile-bundles-meshes}

**Lister objekter og dekoder meshes** i Unity `SerializedFile` format 22 og nyere (Unity 2020 til 6000), og åpner
`UnityFS`-pakker. Det finnes ingen Unity-løypeeksport.

Kilder: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Kommandoer: `identify` (beholdere og pakker), `meshes` (bare rene beholdere).

## Beholderen {#the-container}

Unity leverer et nivå som serialiserte objektgrafer: `globalgamemanagers`, `sharedassets*.assets`, `resources.assets`,
`level*`, og ressurspakker. Hver holder en tabell med objekter merket med en klasse-id.

Headeren er der lesingen går galt stille. De første seksten byte er fire big-endian `uint32` beholdt for kompatibilitet.
I format 22 er tre av dem null, og de virkelige verdiene følger fordi en fil kan overstige 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Den andre `metadata size` er en `uint32` mellom to `int64`. Antar man at alle tre er 64-bit, havner versjonsstrengen fire
byte for sent. Den dekodes likevel til noe strengaktig og sender alt etter den på avveie. Headeren er big-endian.
Alt etter den følger endianness-byten (0, little-endian, på hver stasjonær build).

Etter headeren: motorversjonsstrengen, plattformen, typetre-flagget, typetabellen (klasse-id per type), objekttabellen
(sti-id, forskyvning, størrelse, type), og de eksterne (andre filer en peker kan referere til).

| Tilfelle | Resultat |
|---|---|
| format 22-30 | leses |
| format 9-21 (før Unity 2020) | avvist: forskyvningene står i den eldre headeren, og ingen fil ved hånden brukte den |
| utenfor 9-30 | avvist |
| innebygd typetre (editor-bygg) | avvist: utgitte bygg har ikke ett, og editor-veien er ikke implementert |
| en pakke gitt der en beholder forventes | avvist, med en peker til pakkeleseren |

Det finnes **ingen generell deserialisator**. Utgitte bygg har ingen typetre, fordi skjemaet er kompilert inn i spilleren,
så hver klasse må parses mot et oppsett kjent for sin versjon. Bare `Mesh` dekodes. Andre klasser rapporteres med navn og
antall (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`,
`MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; andre som `class<id>`).

**Verifisert** på tvers av mange installerte spill og millioner av objekter: objekttabellen må dekke dataseksjonen nøyaktig,
uten overlapp, og ingenting annet enn justeringsfylling mellom objektene, og det siste objektet må ende på filens siste byte.
En feillest header kan ikke produsere det. Testen mot installerte spill gjentar det på opptil seks `resources.assets` /
`sharedassets0.assets`-filer i `*_Data`-mapper.

## Pakker (`UnityFS`) {#bundles-unityfs}

En pakke er en komprimert beholder med SerializedFiles. Blokklisten og katalogen er også komprimert. Metoden ligger i de lave
seks bitene av et flaggord: 0 lagret, 1 LZMA (Unitys 5-byte header med størrelsen satt inn), 2 og 3 LZ4 / LZ4HC. Format 7 og
nyere justerer headeren til 16 byte. Flagget `0x80` legger katalogen på slutten av filen. `UnityWeb`, `UnityRaw` og
`UnityArchive` (før 5.3) gjenkjennes, men leses ikke.

## Meshes {#meshes}

`read_mesh` dekoder et `Mesh`-objekt til posisjoner, normaler, det første UV-settet og trekanter, i rekkefølgen Unity 2019+
skriver dem: navn, undermeshes, blend-former (hoppes over), bindeposer og beindata (hoppes over), komprimerings- og
lesbarhetsflagg, indeksbufferen, hjørnepunktkanalene og hjørnepunktdataene, den komprimerte mesh-blokken, den lokale
avgrensningsboksen, og strømmeinformasjonen.

- **Eksterne hjørnepunkter.** Mesteparten av geometrien ligger i en `.resS`-fil ved siden av beholderen. Verktøyet leser den fra
  beholderens mappe (bare filnavnet i den lagrede `archive:/...`-stien brukes). En manglende `.resS` er en feil, ikke en tom mesh.
- **Strømmer og kanaler.** Kanalene sier hvilken strøm, forskyvning, format og dimensjon hvert attributt har. Strømmene pakkes
  etter hverandre, hver fylt til 16 byte, så en strøms start akkumuleres fra stegene før den.
  Formater: float32, float16, unorm/snorm 8 og 16 (normalisert), og rene heltall.
- **Topologi.** Bare trekanter (topologi 0). Striper, firkanter og linjer avvises, fordi en feil konvertering ser ut som ekte geometri.
- **Komprimerte meshes** (kvantiserte deltaer) avvises: «mesh '...' is stored compressed; that encoding is not implemented».

### Selvkontrollen {#the-self-check}

Å lese en struktur i feil rekkefølge gir ingen feil. Den gir plausible tall. Derfor kontrolleres hver dekodet mesh mot
**avgrensningsboksen Unity lagret for den**, beregnet av editoren fra de virkelige hjørnepunktene. `aabb_matches()` består når
den dekodede boksens hjørner er innen 2 % av den lagrede boksens størrelse. `meshes` skriver `ok` eller `BOUNDS DISAGREE` på
hver linje.

**Verifisert:** meshes stikkprøvet fra flere spill dekodes med boksene sine stemmende. Testen mot installerte spill gjentar
kontrollen på de installerte beholderne.

## Ikke implementert {#not-implemented}

- Formater før 2020.
- Komprimerte meshes.
- Enhver klasse annen enn `Mesh`: ingen scenegraf, transformasjoner eller materialer, så meshes er i sitt eget lokale rom.
- `meshes` på en pakke. Pakkeleseren finnes i Python (`UnityBundle.serialized_files()`), men kommandoen tar en ren beholder.
