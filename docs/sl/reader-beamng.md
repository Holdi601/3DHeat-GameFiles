---
title: "Datoteke BeamNG"
nav_order: 8
lang: "sl"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Datoteke BeamNG: arhivi nivojev, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive ima navadne zip arhive, zato ni nobenega kontejnerja za povratni inženiring. Delo je v branju nivoja **tako, kot ga bere igra**: sestavljanje arhivov v en datotečni sistem, sledenje scenskim datotekam ter dekodiranje terena in sestavljenih oblik. Do teh bralnikov pridemo prek izvoza proge [BeamNG.drive](course-beamng.md). `identify` prepozna tudi zip nivoje, `.cdae` in `.ter`, `list` in `extract` pa vzameta katerikoli zip.

Viri: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Nameščen datotečni sistem {#the-mounted-file-system}

`Files.of_install(game)` zgradi en indeks, neobčutljiv na velikost črk, nad `gameengine.zip`, zipi `content` (razen vozil in zvokov) ter uporabnikovimi modi (`mods\*.zip`, `mods\unpacked\*` in uporabnikova mapa `levels`). Poznejši dodatki prepišejo prejšnje, kot v igri. Iskanje ne upošteva velikosti črk, ker se sklici v nivojih ne ujemajo z arhivi (`.DAE` za `.dae`). Podrobnosti so na [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` najde pot tako, kot jo najde igra: kakor je podana, relativno glede na datoteko, ki jo je navedla, `x.png` kot `x.dds`, `x.dae` kot `x.cdae` (prednostno) in prek datoteke JSON `x.png.link`, katere `path` kaže v `/assets`.

## Scenske datoteke {#scene-files}

| Vir | Format | Prebrano |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | en objekt JSON na vrstico, ali en sam seznam ali preslikava JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | isti razredi, za starejše nivoje brez `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript ali JSON | otroci, postavljeni glede na prefab, do 8 nivojev globoko |
| `levels\<name>\forest\*.forest4.json` | en primerek na vrstico | tipizirano z zapisi `TSForestItemData` v `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | naslov nivoja (ključi prevodov se prezrejo) |

**Transformacije.** `rotationMatrix` so devet števil, katerih **vrstice** so lastne osi predmeta v svetu. Odseki varovalnih ograj, verižno vezani ob cesti, tečejo vzdolž vrstice 0 (92 %), zgornja vrstica pa se nagiba z naklonom ceste. Starejši prefabi dajo `rotation = "x y z degrees"`, desnosučni zasuk za ta kot (92 % verig ograj se ujema s tem, 19 % z nasprotnim smislom). Skala pomnoži vrstice, `position` (ali `pos`) pa je zadnja vrstica. Transformacija otroka prefaba se sestavi s transformacijo prefaba. `groupPosition` prefaba je pivot urejevalnika in se **ne** odšteje: prikolica na prefabu stoji na tleh samo brez njega.

Števila TorqueScript se berejo z dovoljenim vzorcem, ker nekateri objavljeni prefabi pišejo vrednosti kot `-0.99563-0.0` brez presledka.

## Teren: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Višina v metrih: `position.z + h * maxHeight / 65535`, pri čemer se `position`, `squareSize` in `maxHeight` vzamejo iz `TerrainBlock` (privzeto 0, 1 in 2048).
- Vrstice tečejo vzdolž +y. Mrežna točka (i, j) je na `(position.x + i * squareSize, position.y + j * squareSize)`.
- Plast 255 je luknja.

Preverjeno: cestna vozlišča ležijo na terenu do 1-2 cm (mediana) na treh nivojih. `h / 32` ali druga osna ureditev zgreši za desetine do stotine metrov.

## Materiali {#materials}

Vsaka `*.materials.json` zunaj `levels\`, plus tiste trenutnega nivoja, indeksirana po `mapTo`, `name` in ključu:

| Razred | Uporabljena polja |
|---|---|
| `Material`, `CustomMaterial` | barvna mapa (`baseColorMap`, `colorMap` ali `diffuseMap`, prva stopnja), faktor barve, mapa in faktor neprozornosti, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | osnovna mapa in `diffuseSize`, mapa podrobnosti, velikost in moč, makro mapa, velikost in moč, `groundmodelName`, `annotation` |

Slike se dekodirajo s Pillow (DDS, PNG in podobno), kjer je mogoče z zmanjšano ločljivostjo, in se predpomnijo po velikosti. Tekstura, ki je ni mogoče prebrati, se nadomesti z ravno barvo.

## Sestavljene oblike: `.cdae` {#compiled-shapes-cdae}

`.cdae` je igrin lastni predpomnilnik vsake datoteke Collada, zapisan kot MessagePack. Njegova postavitev je **dokumentirana s strani BeamNG** (documentation.beamng.com/modding/file_formats/cdae/), bralnik pa jo sledi:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Kaj se prebere: meje, vozlišča, predmeti, `details` (stopnje podrobnosti), privzete rotacije vozlišč (`Quat16`) in translacije, vsa oglišča, UV, normale, barve, primitivi in indeksi vsakega mesha ter imena materialov. Imena materialov so najdena na koncu toka, ker zaporedja animiranega rekvizita pridejo pred njimi v obliki, ki ni dokumentirana.

Dve stvari, ki dokumentacija ne pove, sta bili potrjeni proti datotekam `.dae`, iz katerih so bile oblike zgrajene:

- **Rotacije vozlišč so Torquove.** `Quat16`, prebran po učbeniku, se zavrti na napačno stran. Njegova matrika mora biti **transponirana**. S tem se meje vsakega vozlišča ujemajo s Collado do milimetra. Brez tega so za 38 cm narobe v mediani.
- **Enote in osi so že uveljavljene.** Collada datoteka, zapisana v centimetrih ali z Y navzgor, pride iz predpomnilnika v metrih, Z navzgor.

Stopnje podrobnosti so `details` z nenegativno velikostjo, največja prva. Negativne velikosti so mreže trkov in linije vida, nikoli se ne narišejo. Predmeti z imeni `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` ali `imposter` se nikoli ne narišejo. Narišejo se samo standardni in razvrščeni meshi. Skinned meshi (liki, vozila) in mesh nalepke niso. Trakovi in lepeze trikotnikov se razvijejo, ploskve pa se preobrnejo, da se ujemajo s shranjenimi normalami, ki Torquova lastna smer navijanja ne zagotavlja.

Preverjeno: skoraj vsaka objavljena oblika se prebere. Preostali dve sta iz starejše različice.

## Rezerva Collada: `.dae` {#collada-fallback-dae}

Za oblike brez `.cdae` (modi in redka oblika, katere predpomnilnik je starejši) se datoteka Collada prebere tako, kot jo bere Torquov uvoznik, v isto strukturo:

- Stopnje podrobnosti po Torquovem imenovanju: končna številka imena vozlišča mesha je pikselska velikost, iz katere je narisan (`barrier75`, `barrier40`). Negativna številka ali ime `collision`/`Colmesh`/`LOS`/`nulldetail` se nikoli ne nariše. Oblika brez te konvencije ima eno stopnjo.
- Enote iz `<unit meter>`, Y navzgor se obrne v Z navzgor.
- UV se obrnejo v konvencijo predpomnilnika (v gre navzdol po sliki).

Preverjeno proti igrinemu lastnemu `.cdae` istih datotek: skoraj vse vzorčene meje se ujemajo do 1 cm, 583 jih ima isto število trikotnikov, 94 % UV materialov je enakih. Test na nameščeni igri zahteva, da se 90 % do 60 parov oblik iz skupnega arhiva sredstev ujema v 1 cm.

## Ni prebrano {#not-read}

- Rastlinje na tleh (proceduralna trava) in vse, kar nastane med izvajanjem.
- Animirana zaporedja in skinning.
- Vozila in zvoki (nikoli se ne montirajo).
