---
title: "BeamNG-filer: niveauarkiver, `.ter`, `.cdae`, `.dae`"
nav_order: 8
lang: "da"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# BeamNG-filer: niveauarkiver, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive leverer almindelige zip-arkiver, så der er ingen container at reverse engineere. Arbejdet ligger i at læse et niveau **på den måde, spillet gør**: montere arkiverne i ét filsystem, følge scenefilerne og afkode terrænet og de kompilerede former. Disse læsere nås via [BeamNG.drive](course-beamng.md)-course-eksporten. `identify` navngiver også en niveau-zip, en `.cdae` og en `.ter`, og `list` og `extract` tager alle zip-filerne.

Kilder: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Det monterede filsystem {#the-mounted-file-system}

`Files.of_install(game)` bygger ét indeks, der ikke skelner store og små bogstaver, over `gameengine.zip`, `content`-zip-filerne (undtagen køretøjer og lyde) og brugerens mods (`mods\*.zip`, `mods\unpacked\*` og en brugermappe `levels`). Senere tilføjelser overstyrer tidligere, som i spillet. Opslag ser bort fra store og små bogstaver, fordi niveauernes egne referencer ikke stemmer med arkiverne (`.DAE` for en `.dae`). Detaljer står under [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` finder en sti, som spillet gør: som angivet, i forhold til filen der nævnte den, `x.png` som `x.dds`, `x.dae` som `x.cdae` (foretrukket), og via en `x.png.link`-JSON-fil, hvis `path` peger ind i `/assets`.

## Scenefiler {#scene-files}

| Kilde | Format | Læses |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | ét JSON-objekt pr. linje, eller et enkelt JSON-array eller -kort | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | de samme klasser, for ældre niveauer uden `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript eller JSON | børn placeret i forhold til prefab'en, op til 8 niveauer dybt |
| `levels\<name>\forest\*.forest4.json` | én forekomst pr. linje | typet af `TSForestItemData`-poster i `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | niveauets titel (oversættelsesnøgler ignoreres) |

**Transformationer.** `rotationMatrix` er ni tal, hvis **rækker** er objektets egne akser i verden. Autoværnssektioner kædet langs en vej løber langs række 0 (92 %), og op-rækken hælder med vejens stigning. Ældre prefabs giver `rotation = "x y z degrees"`, en højrehåndet drejning med den vinkel (92 % af skinnekæderne flugter med den, 19 % med den modsatte retning). Skala ganger rækkerne, og `position` (eller `pos`) er den sidste række. Et prefab-barns transformation sammensættes med prefabbens. Prefabbens `groupPosition` er et redigeringsdrejepunkt og trækkes **ikke** fra: en vognprefab står kun på jorden uden den.

TorqueScript-tal læses med et tolerant mønster, fordi nogle leverede prefabs skriver værdier som `-0.99563-0.0` uden mellemrum.

## Terræn: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Højde i meter: `position.z + h * maxHeight / 65535`, med `position`, `squareSize` og `maxHeight` fra `TerrainBlock` (standard 0, 1 og 2048).
- Rækker løber langs +y. Gitterpunkt (i, j) ligger ved `(position.x + i * squareSize, position.y + j * squareSize)`.
- Lag 255 er et hul.

Tjekket: vejnoder ligger på terrænet inden for 1-2 cm (median) på tre niveauer. `h / 32`, eller den anden akserækkefølge, rammer ved siden af med titals til hundredvis af meter.

## Materialer {#materials}

Hver `*.materials.json` uden for `levels\` samt det aktuelle niveaus, indekseret efter `mapTo`, `name` og nøgle:

| Klasse | Felter der bruges |
|---|---|
| `Material`, `CustomMaterial` | farvekort (`baseColorMap`, `colorMap` eller `diffuseMap`, første trin), farvefaktor, opacitetskort og faktor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | grundkort og `diffuseSize`, detaljekort, størrelse og styrke, makrokort, størrelse og styrke, `groundmodelName`, `annotation` |

Billeder afkodes med Pillow (DDS, PNG og så videre), med et udkast i reduceret størrelse hvor det er muligt, og caches pr. størrelse. En tekstur, der ikke kan læses, falder tilbage til flad farve.

## Kompilerede former: `.cdae` {#compiled-shapes-cdae}

`.cdae` er spillets egen cache af hver Collada-fil, skrevet som MessagePack. Dets layout er **dokumenteret af BeamNG** (documentation.beamng.com/modding/file_formats/cdae/), og læseren følger det:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Det, der læses: grænser, noder, objekter, details (detaljeniveauer), standard-nodrotationer (`Quat16`) og translationer, hver meshes vertices, UV'er, normaler, farver, primitiver og indekser, og materialenavnene. Materialenavne findes til sidst i strømmen, fordi en animeret rekvisits sekvenser kommer før dem i en form, der ikke er dokumenteret.

To ting, dokumentationen ikke forklarer udtrykkeligt, fastslået ved sammenligning med de `.dae`-filer, formerne blev bygget af:

- **Nodrotationer er Torques.** En `Quat16`, læst på den bogbekendte måde, roterer den forkerte vej. Dens matrix skal **transponeres**. Med det passer hver nodes verdensgrænser med Collada'en til millimeteren. Uden det er de 38 cm ude i medianen.
- **Enheder og akser er allerede anvendt.** En Collada-fil lavet i centimeter eller Y-op kommer ud af cachen i meter, Z-op.

Detaljeniveauer er `details` med en størrelse på nul eller mere, største først. Negative størrelser er kollisions- og sigtelinjemeshes, som aldrig tegnes. Objekter med navnene `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` eller `imposter` tegnes aldrig. Kun standard- og sorterede meshes tegnes. Skinnede meshes (figurer, køretøjer) og decal-meshes gør ikke. Trekantstrimler og vifter udrulles, og flader vikles om, så de passer med de gemte normaler, hvilket Torques egen vikling ikke garanterer.

Tjekket: næsten hver leveret form læses. De to andre er en ældre version.

## Collada-reserve: `.dae` {#collada-fallback-dae}

For former uden `.cdae` (mods, og den enkelte form, hvis cache er ældre) læses Collada-filen, som Torques importør læser den, ind i samme struktur:

- Detaljeniveauer ud fra Torques navngivning: en mesh-nodes efterfølgende tal er den pixelstørrelse, den tegnes ud fra (`barrier75`, `barrier40`). Et negativt tal, eller et navn `collision`/`Colmesh`/`LOS`/`nulldetail`, tegnes aldrig. En form uden konventionen er ét niveau.
- Enheder fra `<unit meter>`, og Y-op drejet til Z-op.
- UV'er vendt til cachens konvention (v løber nedad i billedet).

Tjekket mod spillets egen `.cdae` af de samme filer: næsten alle stikprøvede grænser inden for 1 cm, 583 med samme antal trekanter, 94 % af materialernes UV'er identiske. Testen mod det installerede spil kræver, at 90 % af op til 60 formpar fra det delte kunstarkiv er enige inden for 1 cm.

## Ikke læst {#not-read}

- Jordbevoksning (procedural græs) og alt, der genereres under kørsel.
- Animerede sekvenser og skinning.
- Køretøjer og lyde (aldrig monteret).
