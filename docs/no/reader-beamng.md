---
title: BeamNG-filer
lang: "no"
source: reader-beamng.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# BeamNG-filer: nivåarkiver, `.ter`, `.cdae`, `.dae`

BeamNG.drive leveres med vanlige zip-arkiver, så det finnes ingen beholder å reverse-engineere. Arbeidet
ligger i å lese et nivå **slik spillet gjør**: montere arkivene inn i ett filsystem, følge scenefilene, og
dekode terrenget og de kompilerte formene. Disse leserne nås gjennom [BeamNG.drive](course-beamng.md)-
løypeeksporten. `identify` navngir også et nivå-zip, en `.cdae` og en `.ter`, og `list` og `extract` tar
hvilken som helst av zip-filene.

Kilder: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Det monterte filsystemet

`Files.of_install(game)` bygger én indeks som ikke skiller store og små bokstaver, over `gameengine.zip`,
`content`-zipene (unntatt kjøretøy og lyder), og brukerens mods (`mods\*.zip`, `mods\unpacked\*`, og en
brukermappe `levels`). Senere tillegg overstyrer tidligere, som i spillet. Oppslag ignorerer store og små
bokstaver fordi nivåenes egne referanser ikke stemmer med arkivene (`.DAE` for en `.dae`). Detaljer står på
[BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` finner en sti på samme måte som spillet: slik den er gitt, relativt til filen som nevnte den,
`x.png` som `x.dds`, `x.dae` som `x.cdae` (foretrukket), og gjennom en `x.png.link`-JSON-fil der `path` peker
inn i `/assets`.

## Scenefiler

| Kilde | Format | Leses |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | ett JSON-objekt per linje, eller en enkelt JSON-matrise eller -tabell | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | de samme klassene, for eldre nivåer uten `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript eller JSON | barn plassert relativt til prefabben, opptil 8 nivåer dypt |
| `levels\<name>\forest\*.forest4.json` | én instans per linje | typet av `TSForestItemData`-poster i `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | nivåets tittel (oversettelsesnøkler ignoreres) |

**Transformasjoner.** `rotationMatrix` er ni tall der **radene** er objektets egne akser i verden. Veiinngjer-
seksjoner som kjedes langs en vei, går langs rad 0 (92 %), og opp-raden tilter med veiens helning. Eldre prefabber
gir `rotation = "x y z degrees"`, en høyrehåndet vending med den vinkelen (92 % av skinnekjedene stemmer med den,
19 % med motsatt retning). Skala multipliserer radene, og `position` (eller `pos`) er siste rad. Et prefab-barns
transform settes sammen med prefabbens. Prefabbens `groupPosition` er en redigerings-pivot og trekkes **ikke**
fra: en trillebår-prefab står bare på bakken uten den.

TorqueScript-tall leses med et toleranset mønster, fordi noen utgitte prefabber skriver verdier som `-0.99563-0.0`
uten mellomrom.

## Terreng: `.ter`

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Høyde i meter: `position.z + h * maxHeight / 65535`, med `position`, `squareSize` og `maxHeight` fra
  `TerrainBlock` (standard 0, 1 og 2048).
- Radene går langs +y. Rutenettpunkt (i, j) ligger på
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Lag 255 er et hull.

Kontrollert: veinoder ligger på terrenget til 1-2 cm (median) på tre nivåer. `h / 32`, eller den andre
aksrekkefølgen, bommer med titalls til hundrevis av meter.

## Materialer

Hver `*.materials.json` utenfor `levels\`, pluss den nåværende nivåets, indeksert etter `mapTo`, `name` og nøkkel:

| Klasse | Felter som brukes |
|---|---|
| `Material`, `CustomMaterial` | fargekart (`baseColorMap`, `colorMap` eller `diffuseMap`, første trinn), fargefaktor, opasitetskart og -faktor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | grunnkart og `diffuseSize`, detaljkart, størrelse og styrke, makrokart, størrelse og styrke, `groundmodelName`, `annotation` |

Bilder dekodes med Pillow (DDS, PNG og så videre), med en redusert størrelse der det går, og caches per størrelse.
En tekstur som ikke kan leses, faller tilbake til flat farge.

## Kompilerte former: `.cdae`

`.cdae` er spillets egen cache av hver Collada-fil, skrevet som MessagePack. Oppsettet er **dokumentert av BeamNG**
(documentation.beamng.com/modding/file_formats/cdae/), og leseren følger det:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Det som leses: grenser, noder, objekter, `details` (detaljnivåer), standard nodrotasjoner (`Quat16`) og
translasjoner, hver meshes hjørnepunkter, UV-er, normaler, farger, primitiver og indekser, og materialnavnene.
Materialnavnene finnes på slutten av strømmen, fordi en animert rekvisitts sekvenser kommer før dem i en form
som ikke er dokumentert.

To ting dokumentasjonen ikke spesifiserer, fastslått mot `.dae`-filene formene ble bygget av:

- **Nodrotasjoner er Torques.** En `Quat16` lest på den vanlige læreboksmåten roterer feil vei. Matrisen må
  **transponeres**. Med det stemmer hver nodes verdensgrenser med Collada til millimeteren. Uten det er de 38 cm
  unna i median.
- **Enheter og akser er allerede brukt.** En Collada-fil laget i centimeter eller Y-opp kommer ut av cachen i
  meter, Z-opp.

Detaljnivåer er `details` med ikke-negativ størrelse, størst først. Negative størrelser er kollisjons- og
siktlinjemeshes, som aldri tegnes. Objekter som heter `colmesh`, `collision`, `los`, `bb_`, `billboard`,
`autobillboard` eller `imposter`, tegnes aldri. Bare standard- og sorterte meshes tegnes. Skinnede meshes
(figurer, kjøretøy) og dekalmeshes gjør det ikke. Triangelstriper og vifter pakkes ut, og flatene vikles om for å
stemme med de lagrede normalene, som Torques egen vikling ikke garanterer.

Kontrollert: nesten hver utgitte form leses. De to andre er en eldre versjon.

## Collada-reserveløsning: `.dae`

For former uten `.cdae` (mods, og den sjeldne formen der cachen er eldre) leses Collada-filen slik Torques importør
leser den, inn i samme struktur:

- Detaljnivåer fra Torques navnekonvensjon: en mesh-nodes tall på slutten er pikselstørrelsen den tegnes fra
  (`barrier75`, `barrier40`). Et negativt tall, eller et navn `collision`/`Colmesh`/`LOS`/`nulldetail`, tegnes
  aldri. En form uten konvensjonen er ett nivå.
- Enheter fra `<unit meter>`, og Y-opp gjort om til Z-opp.
- UV-er vendt til cachens konvensjon (v går nedover bildet).

Kontrollert mot spillets egne `.cdae` for de samme filene: nesten alle stikkprøvede grenser innen 1 cm, 583 med
samme trekantantall, 94 % av materialenes UV-er identiske. Testen mot installerte spill krever at 90 % av opptil 60
formpar fra det delte kunstarkivet stemmer innen 1 cm.

## Ikke lest

- Bakkedekke (prosedyremessig gress), og alt som genereres under kjøring.
- Animerte sekvenser og skinning.
- Kjøretøy og lyder (aldri montert).
