---
title: BeamNG-filer
lang: "sv"
source: reader-beamng.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# BeamNG-filer: nivåarkiv, `.ter`, `.cdae`, `.dae`

BeamNG.drive levereras i vanliga zip-arkiv, så det finns ingen behållare att
reverse-engineera. Arbetet ligger i att läsa en nivå **så som spelet gör**: montera
arkiven i ett filsystem, följa scenfilerna, och avkoda terrängen och de kompilerade
formerna. Dessa läsare nås via banexporten [BeamNG.drive](course-beamng.md).
`identify` känner även igen en nivå-zip, en `.cdae` och en `.ter`, och `list` och
`extract` tar vilken zip som helst.

Källkod: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Det monterade filsystemet

`Files.of_install(game)` bygger ett index utan hänsyn till stora och små bokstäver
över `gameengine.zip`, `content`-zip-filerna (utom fordon och ljud) och användarens
moddar (`mods\*.zip`, `mods\unpacked\*` och en användarmapp `levels`). Senare tillägg
skriver över tidigare, som i spelet. Uppslag ignorerar versaler och gemener, eftersom
nivåernas egna referenser inte stämmer med arkiven där (`.DAE` för en `.dae`). Detaljer
finns på [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` hittar en sökväg så som spelet gör: som den angavs, relativt filen som
nämnde den, `x.png` som `x.dds`, `x.dae` som `x.cdae` (föredras), och via en
`x.png.link`-JSON-fil vars `path` pekar in i `/assets`.

## Scenfiler

| Källa | Format | Läses |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | ett JSON-objekt per rad, eller en enda JSON-array eller -karta | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | samma klasser, för äldre nivåer utan `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript eller JSON | barn placerade relativt prefaben, upp till 8 nivåer djupt |
| `levels\<name>\forest\*.forest4.json` | en instans per rad | typad av `TSForestItemData`-poster i `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | nivåns titel (översättningsnycklar ignoreras) |

**Transformer.** `rotationMatrix` är nio tal vars **rader** är objektets egna axlar i
världen. Vägräcksektioner som är kedjade längs en väg går längs rad 0 (92 %), och
upp-raden lutar med vägens lutning. Äldre prefabs ger `rotation = "x y z degrees"`, en
högerhänt vridning med den vinkeln (92 % av räckeskedjorna stämmer med den, 19 % med
motsatt riktning). Skala multiplicerar raderna, och `position` (eller `pos`) är den sista
raden. En prefab-barns transform sätts samman med prefabens. Prefabens `groupPosition`
är en redigerarens vridpunkt och dras **inte** av: en vagnsprefab står bara på marken utan det.

TorqueScript-tal läses med ett toleranta mönster, eftersom vissa levererade prefabs
skriver värden som `-0.99563-0.0` utan mellanslag.

## Terräng: `.ter`

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Höjd i meter: `position.z + h * maxHeight / 65535`, med `position`,
  `squareSize` och `maxHeight` från `TerrainBlock` (standard 0, 1 och 2048).
- Raderna går längs +y. Rutnätspunkt (i, j) ligger på
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Lager 255 är ett hål.

Kontrollerat: vägnoder ligger på terrängen inom 1-2 cm (median) på tre nivåer.
`h / 32`, eller den andra axelordningen, missar med tiotals till hundratals meter.

## Material

Varje `*.materials.json` utanför `levels\`, plus den aktuella nivåns, indexerade efter
`mapTo`, `name` och nyckel:

| Klass | Använda fält |
|---|---|
| `Material`, `CustomMaterial` | färgkarta (`baseColorMap`, `colorMap` eller `diffuseMap`, första steget), färgfaktor, opacitetskarta och -faktor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | basekarta och `diffuseSize`, detaljkarta och styrka, makrokarta och styrka, `groundmodelName`, `annotation` |

Bilder avkodas med Pillow (DDS, PNG med mera), med en reducerad storlek där det går,
och cachas per storlek. En oläsbar textur faller tillbaka till platt färg.

## Kompilerade former: `.cdae`

`.cdae` är spelets egen cache av varje Collada-fil, skriven som MessagePack. Layouten
är **dokumenterad av BeamNG** (documentation.beamng.com/modding/file_formats/cdae/) och
läsaren följer den:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Det som läses: gränser, noder, objekt, `details` (detaljnivåer), standardrotationer för
noder (`Quat16`) och translationer, varje meshs vertexar, UV, normaler, färger,
primitiver och index, och materialnamnen. Materialnamnen hittas i slutet av strömmen,
eftersom en animerad rekvisitas sekvenser kommer före dem i ett format som inte är dokumenterat.

Två saker som dokumentationen inte förklarar, fastställda mot `.dae`-filerna formerna
byggdes av:

- **Nodrotationerna är Torques.** En `Quat16` läst på det läroboksmässiga sättet roterar
  åt fel håll. Dess matris måste **transponeras**. Med det stämmer varje nods världsgränser
  med Collada-filen till millimetern. Utan det är de 38 cm fel i median.
- **Enheter och axlar är redan tillämpade.** En Collada-fil skriven i centimeter eller
  med Y uppåt kommer ur cachen i meter, Z uppåt.

Detaljnivåerna är `details` med icke-negativ storlek, störst först. Negativa storlekar
är kollisions- och siktlinjemeshar, som aldrig ritas. Objekt som heter `colmesh`,
`collision`, `los`, `bb_`, `billboard`, `autobillboard` eller `imposter` ritas aldrig.
Bara standard- och sorterade meshar ritas. Skinnade meshar (figurer, fordon) och
dekalmeshar ritas inte. Triangelband och vifter packas upp, och ytornas vindning
vänds så att den stämmer med de lagrade normalerna, vilket Torques egen vindning inte garanterar.

Kontrollerat: nästan varje levererad form läses. De två andra är en äldre version.

## Reserv för Collada: `.dae`

För former utan `.cdae` (moddar, och den enstaka form vars cache är äldre) läses
Collada-filen så som Torques importör läser den, till samma struktur:

- Detaljnivåer enligt Torques namngivning: en mesh-nods avslutande tal är pixelstorleken
  den ritas från (`barrier75`, `barrier40`). Ett negativt tal, eller ett namn som
  `collision`/`Colmesh`/`LOS`/`nulldetail`, ritas aldrig. En form utan konventionen är en nivå.
- Enheter från `<unit meter>`, och Y-uppåt vrids till Z-uppåt.
- UV vänds till cachens konvention (v går nedåt i bilden).

Kontrollerat mot spelets egen `.cdae` av samma filer: nästan alla samplade gränser inom
1 cm, 583 med samma triangelantal, 94 % av materialens UV identiska. Testet mot
installerat spel kräver att 90 % av upp till 60 formpar från det delade konstarkivet
stämmer inom 1 cm.

## Läses inte

- Markvegetation (procedurellt gräs), och allt som genereras vid körning.
- Animerade sekvenser och skinning.
- Fordon och ljud (monteras aldrig).
