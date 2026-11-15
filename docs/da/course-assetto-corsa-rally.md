---
title: "Course-eksport: Assetto Corsa Rally"
nav_order: 3
lang: "da"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Course-eksport: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally er bygget på Unreal Engine 5 (5.6.1, en ændret udgave) og leverer sit indhold som IoStore-containere. Ingen af dem er krypteret. Eksporten finder etapen og akseretningen ud fra runden. Den skriver etapens egne jordfliser, delt i vej og terræn og teksturet ud fra etapens indbagte jordfarve, og placerer de øvrige modeller i flade farver efter kategori.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Kilder: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (installation, etaper, placering),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (eksporten).
Unreal-læserne under den findes på [Unreal 5 IoStore](reader-unreal-iostore.md),
og dekomprimering på [Oodle](reader-oodle.md).

**Status:** tjekket på det installerede spil med runder, der var genereret i en tilfældig frame på hver etape, og den fandt den rigtige etape og frame hver gang. Ingen runde optaget i selve spillet har været igennem den endnu.

## Find installationen {#finding-the-install}

- `--install <mappe>`: spilmappen, eller dens `Content\Paks`, eller en hvilken som helst mappe med `.utoc`-filer. Værktøjet tjekker `<mappe>`, derefter `<mappe>\acr\Content\Paks`, derefter `<mappe>\Content\Paks`.
- Ellers tjekkes hvert Steam-biblioteks `steamapps\common\Assetto Corsa Rally` på samme måde.
- Hver `.utoc` i mappen åbnes som ét lager. Containere, der ikke kan åbnes, springes over. Hvis ingen kan åbnes: "no readable IoStore containers in ...".

De fleste blokke er Oodle-komprimerede, og et bibliotek søges efter på maskinen (hvert Steam-bibliotek gennemsøges). Se [Oodle](reader-oodle.md).

Spillet tages som AC Rally, når rundefilen siger `"game": "assetto-corsa-rally"` (eller `acrally`), eller når du angiver `--game acrally`.

## Hvad en etape er {#what-a-stage-is}

En etape er et **World Partition**-kort:

- `Content\Levels\<Stage>.umap` placerer det fjerne terræn.
- Bagte celler under `Content\Levels\<Stage>\_Generated_\*.umap` placerer alt andet.

Et niveau tæller som etape, hvis dets miljømappe, `Content\Environments\<Stage>\`, har en `MeshesTrack`-mappe. Værktøjet går ikke efter fliserne navne, for en etape kan kalde dem efter en by frem for sit kort. `--level` matches uden hensyn til store og små bogstaver mod disse kortnavne. Et forkert navn lister de etaper, der findes.

Der er **intet landskab**. Jorden er statiske meshes:

| Fliser | Sti | Bliver til |
|---|---|---|
| banefliser, ca. 175 m, delt i to | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` og `..._Terrain_k` | `ground:road` og `ground:terrain` (en udelt banefliser, fx en frossen sø, er helt vej) |
| fjernt terræn, fliser på 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Læsning af placeringerne {#reading-the-placements}

Det, der placerer en mesh, er en `StaticMeshComponent`: dens `StaticMesh` og dens `RelativeLocation`, `RelativeRotation` og `RelativeScale3D`, hver i forhold til den komponent, den er fastgjort til (`AttachParent`), op til aktørens rod, der ligger i verden.

- Egenskaberne er **uversionerede**: gemt efter position i klassens egenskabsliste, ikke efter navn. De læses med skemaerne i [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (se [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- En værdi, der er lig komponentens skabelon (dens archetype i en Blueprint), gemmes ikke, så skabelonens værdier læses først, rekursivt, og komponentens egne værdier overstyrer dem.
- Komponenter med `bVisible = 0` eller `bHiddenInGame = 1` springes over. Det samme gælder meshes, hvis sti matcher `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/` eller `_hlod`.
- Rotationer bruger Unreals `FRotationMatrix` (pitch, yaw, roll i grader).
- Dubletter (den samme mesh på samme transformation, til 0,1 cm) fjernes.
- Komponenter, der ikke kan læses, tælles efter årsag og rapporteres, fx `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instancerede komponenter** (skove, næsten alle) læses kun med `--trees`. Denne build har omarrangeret disse klasser ud over motorens headers, så deres egenskaber læses ikke. I stedet:

- kommer meshen fra pakkens afhængighedstabel, hvor hver sådan komponent angiver præcis én statisk mesh,
- kommer forekomsterne fra den native blok efter egenskaberne (`[1][1][128][count]` og derefter `count` 4x4 double-matricer),
- antages komponenten at sidde i sin aktørs rod, sådan som bevoksningsaktørerne placerer dem.

Koordinaterne er Unreals: centimeter, Z op, X fremad, Y til højre, et venstrehåndet koordinatsystem.

## Hvilken etape, og hvilken vej rundt {#which-stage-and-which-way-round}

Telemetriens koordinatsystem er ikke dokumenteret, så det antages ikke. Det tilpasses:

- **Otte kandidat-koordinatsystemer.** Unreal Z (cm) gange 0,01 bliver rundens højde (y). Unreal X og Y bliver rundens x og z, byttet om eller ej, hver med fortegn efter eget valg, alt skaleret med 0,01 til meter.
- **Et gitter af vejhøjder.** For hver etape placeres hver vejflise (på sit groveste detaljeniveau), og den højeste vejvertex gemmes pr. 2 m celle.
- **Scoring.** Op til 400 rundepunkter, jævnt fordelt, omregnes til Unreal-rum gennem hvert koordinatsystem. Et punkt er på vejen, når den vejhøjde, der ligger tættest på det blandt de 3 x 3 celler omkring det, er mellem 1 m under og 3 m over punktet (`ON_ROAD`). Scoren er andelen af punkter på vejen.
- **Vinder.** Det bedste koordinatsystem på den bedste etape, hvis den scorer mindst 50 %. Ellers stopper eksporten: "the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level." Angiv etapen med `--level`.
- **En runde, der navngiver sin bane.** Hvis rundefilen har et `track`-felt, prøves først en etape, hvis navn løst passer (kun bogstaver og tal, og den ene indeholder den anden), alene, og den accepteres kun, hvis den scorer mindst 80 %. Ellers prøves alle etaper.
- Med `--level` prøves kun den etape, i alle otte koordinatsystemer.

Konsollen skriver fx `on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Alt skrives derefter i **rundens koordinatsystem**: meter, Y op. En trekants vikling vendes, hvor en transformation spejler, så flader stadig peger den rigtige vej.

## Jorden {#the-ground}

- Korridoren er `--margin` meter til hver side af runden, i dens egen x/z-plan.
- Hver jordflise placeres på sit fineste detaljeniveau, og kun trekanter, der rækker ind i korridoren, beholdes.
- Trekanter grupperes efter type (vej eller terræn) og efter 512 m kvadrat i Unreal-rum (51.200 cm), og hvert kvadrat får sit eget billede. Dele navngives fx `ground:road 1_-4`. UV'er er `(unreal_xy - kvadratets_oprindelse) / 51200`.
- Normaler beregnes ud fra trekanterne for hele filen.

### Jordteksturen {#the-ground-texture}

Medmindre `--no-textures`, males hvert kvadrat ud fra to kilder, i `--texture-size` pixels:

1. **Den indbagte jordfarve.** Etapens kort' `RuntimeVirtualTextureComponent` (dens boks er `RelativeLocation` som hjørne og `RelativeScale3D` som størrelse, uden rotation) peger på en streaming-**virtuel tekstur**, den jordfarve spillet har bagt. Kvadratets område læses fra den, på det niveau, hvis pixels ligger tættest på den ønskede størrelse. Det er 13 til 59 cm pr. pixel, afhængigt af etapen.
2. **Satellitbilledet** fylder det, den virtuelle tekstur efterlader sort. Det er etapens `sat*_(b|bc|c|basecolor)`-tekstur i dens miljømappe, læst i op til 4096 px. Dens placering findes ved en mindste-kvadraters tilpasning af det fjerne terræns første UV-kanal mod verdens x og y. Tilpasningen skal være lineær inden for 0,01 ved 95. percentil, ellers bruges billedet ikke. Hvis det fjerne terræns UV'er går over 1 (et materiale, der gentager dem), halveres afbildningen, indtil de passer én gang.

Konsollen siger, hvilken der blev brugt, fx `ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`. En etape med ingen af dem tegnes i flade farver.

## Placerede modeller {#placed-models}

Hver placering, der ikke er en jordflise, klassificeres efter sin meshsti (første match vinder):

| Kategori | Mesh-navn (eller sti, for træer) indeholder |
|---|---|
| træer (kun med `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| klipper | `rock`, `cliff`, `boulder`, `stone` |
| kantsten | `kerb`, `curb` |
| barrierer | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| skilte | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| bygninger | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktur | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekvisitter | alt andet |

- En kopi tages med, hvis dens origo ligger i rækkeviddekorridoren (`margin + 60 m`), og tegnes, hvis dens grænser rører korridoren.
- Detaljeniveauer følger [Detaljeniveauer og budgettet](detail-budget.md): afstandsbånd, og derefter trapper de dyreste modeller ned, indtil de passer i budgettet. Hvor selv de groveste niveauer overskrider det, udelades de fjerneste kopier, som i BeamNG, indtil det passer. Kantsten beholder fuld detalje og udelades aldrig. Opsummeringen skriver `placed on it (N triangles of a B budget)` og, hvis kopier blev udeladt, `N copies left out to fit the budget, the furthest from the driving first`.
- Hver kategori er én del i en flad farve: `ground:kerbs` for kantsten, der er kørselsflade, som i Forza og BeamNG, og `structure:<kategori>` for resten:

| Kategori | Farve (lineær RGB) |
|---|---|
| barrierer | 0.55, 0.52, 0.48 |
| skilte | 0.75, 0.72, 0.65 |
| bygninger | 0.62, 0.58, 0.52 |
| infrastruktur | 0.48, 0.48, 0.50 |
| klipper | 0.45, 0.43, 0.40 |
| rekvisitter | 0.55, 0.45, 0.35 |
| træer | 0.20, 0.32, 0.14 |
| kantsten | 0.70, 0.25, 0.22 |

Statiske meshes, der ikke kan læses (skeletmeshes, meshes kun med Nanite, niveauer der ikke er gemt inline), tælles: `N meshes could not be read`.

## Tjek bag det {#checks-behind-it}

Som angivet i kildekoden, på det installerede spil:

- Hver indholdsfortegnelse læses (version 8).
- Hver celle i hver etape åbnes, og hver statisk-mesh- og scenekomponent afkodes og slutter præcis ved sin klasses native hale.
- Næsten hver stikprøvet statisk mesh afkodes (resten er skeletmeshes). En vejflises afkodede udstrækning passer med de grænser, den gemmer.
- Et satellitbilledes mip-niveauer har præcis størrelserne på deres bulk-poster.
- En virtuel teksturchunks fliser er gjort op til byte, og vejfliserne lander på den vej, den viser.

## Kendte mangler {#known-gaps}

- Instancerede komponenters egne egenskaber læses ikke (se ovenfor). Deres placering antager aktørens rod.
- Skove, som PCG genererer under kørsel, gemmes ikke i filerne og kan ikke eksporteres.
- Spline-meshes (usynlige respawn-vægge), decal-komponenter og de placerede modellers egne teksturer tegnes ikke. Modellerne har flade farver.
- `--season` har ingen virkning.
- En spilopdatering kan flytte egenskabspladser. Læseren rejser da en fejl i stedet for at læse forkert, og banen rapporterer, hvor mange komponenter der fejlede.
