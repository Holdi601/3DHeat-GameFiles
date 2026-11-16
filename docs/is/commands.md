---
title: "Skipanir"
nav_order: 2
lang: "is"
source: commands.md
source_hash: "8ae04c37b1a4"
nav_exclude: true
search_exclude: true
---
# Skipanir

Sérhver skipun er keyrð sem `python -m heat3d_gamefiles <verb> ...` úr möppu
geymslunnar. Skipanirnar (verb) koma í þeirri röð sem þú þarft þær oftast: hvað er þessi skrá,
hvað er inni í henni, láttu mig fá þetta, og breyttu hring í braut.

| Skipun | Tekur við | Gerir |
|---|---|---|
| [`identify`](#identify) | hvaða skrá sem er | nefnir gámasniðið með því að lesa bætin |
| [`list`](#list) | Unreal `.pak` eða IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip` eða zip | telur upp færslurnar í því |
| [`extract`](#extract) | það sama | skrifar eina færslu á disk |
| [`meshes`](#meshes) | Unity `SerializedFile` | telur upp net þess og athugar þau |
| [`course`](#course) | hring | flytur út brautina í kringum hann (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | upptekið hringasafn | keyrir `course` á sérhverja braut í því (Forza) |
| [`races`](#races) | uppsettan Forza | telur upp sérhvert kappakstursmót sem leikurinn skilgreinir: hvað það bætir við, hvað það felur, vettvang, stöðu útflutningsins |
| [`terrain`](#terrain) | Forza brautarmöppu | sker út svæði eftir heimshnitum |
| [`levels`](#levels-and-level-frostbite) | uppsettan Frostbite leik (Battlefield 6) | telur upp borðin hans |
| [`level`](#levels-and-level-frostbite) | nafn borðs | flytur borðið út: landslag, sett net, ef vill litakort þeirra (Battlefield 6) |
| [`cars`](#cars) | uppsettan Forza | sérhvern bíl í lágum smáatriðum, í einni skrá fyrir kappakstursflipa skoðarans |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | Unreal 5 leik | telur upp World Partition kortin hans |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | nafn korts | flytur kortið út: landslag, HLOD byggingar, vatn |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | uppsettan Arma Reforger | telur upp heimana hans |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | nafn heims | flytur heiminn út: landslag í sínum litum, sjóinn, byggingar sem kassa |

**Að lesa dæmin:** `<x>` þýðir að þú setur þitt eigið gildi í staðinn, án
oddklofanna; `[...]` er valfrjálst; settu slóð með bilum í "tvöfaldar gæsalappir",
til dæmis `"C:\Games\My Game"`. Ertu nýr í þessu? Sjá [Áður en þú byrjar](before-you-start.md).
Fullt `--help` hverrar skipunar er á [Skipanayfirliti](../cli-reference.md).

Í hvert sinn sem forritið ræsist getur það fyrst athugað hvort nýrri útgáfa sé til. Sjá
[Uppfærslur](updates.md). `HEAT3D_NO_UPDATE=1` slekkur á þeirri athugun.

Frumkóði: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Síður skref fyrir skref: [Skoðun skjalasafna](inspecting-archives.md), [Brautarútflutningur](course-export.md),
[Heil borð](whole-levels.md), [Forza bílar](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Skilakóðar {#exit-codes}

| Kóði | Merking |
|---|---|
| 0 | tókst |
| 1 | verkið mistókst (ólæsilegur hringur, enginn leikur fannst, ekkert til að flytja út, braut í `courses` mistókst; fyrir `list` og `extract`: skrá sem er ekkert af skjalasöfnunum sem þær lesa, skrá sem ekki er hægt að opna eða lesa - dulkóðað pak án `--key`, dulkóðaður IoStore gámur - eða færsla sem er ekki í skjalasafninu) |
| 2 | rangar breytur (argparse), slóð sem er ekki til, `--key` sem er ekki 64 sextándakerfisstafir, eða `terrain` fær bæði eða hvorugt af `--box` og `--route` |

Villur í `list` og `extract` eru hvor um sig ein lína á staðalvillu (standard error), ekki
Python-rakning (traceback).

---

## identify

```
python -m heat3d_gamefiles identify <path>
```

Þetta les skrána og segir hvaða gámur hún er. Það fer ekki eftir
skráarendingunni (eina undantekningin er `.ucas`, hér á eftir). Það prófar sniðin í þessari
röð og stoppar við það fyrsta sem tekst að þátta:

1. **Unreal `.pak`**: fótur með pak-töfratölunni (magic) í síðustu 1.024 bætunum. Prentar
   útgáfuna, staðsetningu og stærð vísisins, hvort vísirinn er dulkóðaður og
   þjöppunaraðferðirnar.
2. **Unreal IoStore `.utoc`**: IoStore-töfratalan í upphafinu. Prentar útgáfuna,
   fjölda bita (chunks) og hvort gámurinn er dulkóðaður; fyrir gám sem er það ekki,
   fjölda skráa sem skráin hans nefnir (og undir hvaða tengipunkti), þjöppunaraðferðirnar
   og hvort `.ucas` hans er við hliðina. `.ucas` ber enga haus af sjálfu sér, svo það er
   þekkt á `.utoc` með sama nafni við hliðina á því, og `identify` nefnir þá skrá.
3. **ForzaTech `.minizip`**: `PGZP` töfratalan. Prentar útgáfuna, fjölda færslna og
   hluta (segments), og hvort `ChunkContentsMiniZip<n>.txt` sem nefnir
   færslurnar er við hliðina (og ef svo er, hvort hún nefnir jafn margar).
4. **zip**: zip-staðarskráarhaus í upphafinu. Prentar fjölda færslna, algengustu
   sex endingarnar og borðanöfnin þegar færslur liggja undir
   `levels/<name>/`, eins og í BeamNG.drive borðasafni.
5. **Unity**: `UnityFS` búnt (prentar vélarútgáfuna og fjölda færslna) eða
   bert `SerializedFile` (prentar sniðið, vélarútgáfuna, fjölda hluta og
   algengustu sex flokkana).
6. **Frostbite `.toc`**: prentar tegundina (`plain` eða `signed`), hvar tréð
   byrjar og annaðhvort fjölda eigna (tvíundar hlutatafla) eða fjölda
   ofurbúnta (DbObject tré).
7. **Source 2 `.vpk`**: prentar útgáfuna, fjölda færslna og fyrsta `.nav`
   leiðsögunetið ef skjalasafnið hefur eitt.
8. **BeamNG `.cdae`**: formútgáfa 31 sem þáttast. Prentar fjölda neta, fjölda
   teiknaðra smáatriðastiga og fyrstu efnin.
9. **BeamNG `.ter`**: það er engin töfratala, svo allt þarf að ganga upp - hlið frá 2
   til 16.384, svo margar hæðir í öðru veldi og lagabæti, síðan 1 til 255 prentanleg
   lagaheiti. Prentar útgáfuna, stærðina og lagaheitin.
10. **ForzaTech `.modelbin`**: prentar útgáfuna, fjölda bita og algengustu sex
    bitamerkin. Innihald bita er ekki afkóðað hér.

Sniðin með eigin töfratölu (2 til 4) koma á undan Unity og Frostbite,
en athuganir þeirra lesa alla skrána: Forza-skjalasafn er tugir gígabæta.

Ef ekkert þeirra passar prentar það `not a format this tool reads` og síðustu
ástæðuna. Sú ástæða kemur úr ForzaTech athuguninni.

Dæmi (tilbúið):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `<archive>` | nauðsynlegt | Unreal `.pak`; IoStore `.utoc` (eða `.ucas` við hliðina); Source 2 `.vpk` (fyrir skipt VPK, `_dir.vpk`); ForzaTech `.minizip`; zip, eins og borða- og efnissöfn BeamNG |
| `--filter TEXT` | ekkert | aðeins slóðir sem innihalda TEXT, hástafir og lágstafir skipta ekki máli |
| `--limit N` | 50 | prenta í mesta lagi N færslur (heildarfjöldinn er alltaf prentaður) |
| `--key HEX` | ekkert | AES-256 lykill sem þú átt þegar, 64 sextándakerfisstafir, með eða án `0x`. Aðeins dulkóðað `.pak` notar hann. Allt sem er ekki 64 sextándakerfisstafir er hafnað áður en skjalasafnið er opnað (skilakóði 2) |

Verkfærið ákveður sniðið út frá bætunum: IoStore efnisskrá, `.minizip` og VPK
eftir undirskriftinni sem þau byrja á, zip eftir staðarskráarhausnum sínum, og `.pak` eftir fætinum
í endanum. `.ucas` hefur engan haus og er opnað gegnum `.utoc` með sama nafni. Skrá sem er
ekkert af þessu er hafnað með `<file> is not an archive list and extract read (...)`. Skrá sem er
eitthvað af þessu en er ekki hægt að opna er hafnað með ástæðu lesarans: dulkóðað pak án
`--key`, dulkóðaður IoStore gámur, pak-útgáfa sem hann les ekki. Hvort sem er
er það ein lína og skilakóði 1.

Hver lína sýnir óþjappaða stærð, þjöppunaraðferðina og slóðina:

| Skjalasafn | Aðferð | Slóðir |
|---|---|---|
| `.pak` | `none`, eða nafnið úr fætinum (`Zlib`, `Oodle`, `Gzip`...) | með tengipunkti skjalasafnsins, til dæmis `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, eða aðferð gámsins (`Oodle`, `Zlib`...), eins og fyrsti blokkin hans er geymd | með tengipunkti, til dæmis `../../../<Project>/Content/...`. Gámi án möppuvísis nefnir engar skrár og er hafnað |
| `.vpk` | alltaf `stored` | eins og í möppunni |
| `.minizip` | `lz4`, `deflate` eða `stored` | eins og `ChunkContentsMiniZip<n>.txt` við hliðina á `GeoChunk<n>.minizip` stafar þær, forskeyti byggingarvélar fjarlægt (öfugir skástrikar, eins og leikurinn skrifar þá). Skjalasafnið geymir engin nöfn, svo án þeirrar skrár heita færslurnar `#0`, `#1`... Lista þar sem línufjöldinn er annar en fjöldi færslna er hafnað: þetta tvennt á ekki saman |
| zip | `stored`, `deflate`, ... | eins og geymt; möppur eru ekki taldar upp |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `<archive>` | nauðsynlegt | eins og fyrir `list` |
| `<entry>` | nauðsynlegt | slóðin nákvæmlega eins og `list` prentar hana (hástafir og lágstafir skipta máli); í `.minizip` virkar `#<number>` líka |
| `--out FILE` | skráarheiti færslunnar (eftir síðasta `/` eða `\`), í núverandi möppu | hvert á að skrifa; yfirmöppur eru búnar til |
| `--key HEX` | ekkert | eins og fyrir `list` |

Færslan er afkóðuð (pak, með lykli), afþjöppuð og skrifuð út. Það prentar
`<bytes> bytes -> <file>`. Ef slóðin er ekki í skjalasafninu hættir skipunin með
skilakóða 1. Það gerist líka þegar færsla er ólæsileg (dulkóðuð færsla án
lykils, Oodle-þjöppuð án Oodle-safns), með ástæðunni í einni línu. VPK-færsla er ekki athuguð gegn CRC hér. Lesarinn hefur
`verify()` aðferð til þess (sjá [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `<path>` | nauðsynlegt | bert Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), ekki búnt |
| `--limit N` | 25 | afkóða og prenta í mesta lagi N net |

Þetta prentar fjölda `Mesh` hluta og síðan eina línu fyrir hvert net: nafnið (fyrstu
40 stafir), fjölda hnúta og þríhyrninga, og `ok` eða `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` þýðir að afkóðuðu hnútarnir endurskapa ekki afmörkunarkassann
sem Unity geymdi fyrir netið, innan 2% af stærð kassans. Það er eigin athugun
þáttunarinnar (sjá [Unity](reader-unity.md)). Net sem ekki er hægt að lesa er tilkynnt með
ástæðunni og telst með í mörkunum. Hnútagögn í `.resS` skrá eru lesin
úr möppunni sem gámurinn er í.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Þetta flytur út brautina í kringum hring: jörðina í belti beggja vegna
aksturslínunnar og það sem stendur á henni, sem eina `.glb` skrá. Það finnur afganginn sjálft: hvaða
leikur, hvaða uppsett eintak, hvaða braut, borð eða áfangi, og (fyrir Assetto Corsa
Rally) hvernig ásarnir snúa. Sjá [Brautarútflutningur](course-export.md).

`<lap>` getur verið hvað sem er af eftirfarandi (nánar í [Hringinntök](lap-inputs.md)):

- hringskrá: leið-JSON, FH Companion hring-JSON, `heat3d-lap` JSON, `.npz` eða `.csv` með x, y, z dálkum
- mappa með hringskrám, leitað endurkvæmt (heil upptekin braut)
- **nafn** brautar, flett upp í FH Companion safninu á `%LOCALAPPDATA%\FHCompanion\laps`

### Valkostir {#options}

| Valkostur | Sjálfgefið | Leikir | Merking |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` í núverandi möppu, eða í `$HEAT3D_LEVELS/<game>/courses/` þegar það er stillt | allir | hvert á að skrifa; nafnið er í lágstöfum, og runur annarra stafa verða `_` |
| `--game {forza,beamng,acrally}` | það sem hringskráin segir, annars `forza` | allir | úr hvaða leik hringurinn er |
| `--margin M` | 80 | allir | metrar af jörð sem haldið er beggja vegna aksturslínunnar |
| `--texture-size {2048,1024,512}` | 2048 | allir | punktar jarðaráferðar á hverja 512 m flís (2048 = 25 cm á punkt) |
| `--no-textures` | af | allir | aðeins flatir litir: miklu minni skrá. Fyrir Forza sleppir þetta líka skiptingu í veg og vegöxl (sjá hér að neðan) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | jarðarkort og líkanaáferðir hvaða árstíðar |
| `--no-placed` | af | allir | aðeins landslag: engir kantsteinar, varnir, skilti, byggingar. Fyrir BeamNG eru akstursflatir sem eru smíðaðir sem net samt áfram |
| `--trees` | af | allir | setja líka gróður (Forza: tré, runnar og brjótanlegir hlutir; BeamNG: tré; AC Rally: tré og gróður í eintökum) |
| `--detail-budget N` | sjálfvirkt | allir | hámark á þríhyrninga fyrir allt sem er sett; sjá [Smáatriðastig og kostnaðarhámarkið](detail-budget.md) |
| `--track DIR` | leitað | Forza | brautarmappan (undir `media\Tracks`, með `GeoChunk0.minizip`) ef ekki á að leita í uppsetta leiknum |
| `--level NAME` | fundið út frá hringnum | BeamNG, AC Rally | borðið (BeamNG möppuheiti) eða áfanginn (AC Rally kortaheiti), hástafir og lágstafir skipta ekki máli |
| `--install DIR` | leitað í Steam-söfnum | BeamNG, AC Rally | BeamNG: mappan með `gameengine.zip`. AC Rally: leikjamappan, eða `acr\Content\Paks` / `Content\Paks` hennar |

Valkostir sem eiga ekki við um leik eru hunsaðir án viðvörunar. Til dæmis
gerir `--season` ekkert fyrir BeamNG og AC Rally, og `--track` gerir ekkert fyrir
þá heldur.

### Hvaða leikur {#which-game}

Leikurinn er tekinn úr `--game`, síðan úr `game` reitnum í `heat3d-lap`
skrá (eða úr `# {...}` lýsingarlínu CSV), og er annars sjálfgefið Forza. Mappa
fær þann leik sem skrárnar í henni nefna, þegar þær nefna aðeins einn; skrá sem nefnir engan
(FH Companion hringur, `course.json`, CSV án lýsingarlínu) telst ekki
með (sjá [Hringinntök](lap-inputs.md)).

| Gildi | Útflutningur |
|---|---|
| byrjar á `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` eða `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | hafnað: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | hafnað: "tracks ship in a protected format that is not a file-extraction target" |
| allt annað | hafnað: "there is no course reader for <game> yet" |

Höfnunin bendir líka á aðra kosti: endurbyggja brautina úr leiknum sjálfum
(3DHeat GameCapture), eða greina hringina án brautar, því flipinn Kappakstursgreining
í skoðaranum teiknar veg út frá þeim.

### Dæmi {#examples}

```
# A course from the FH Companion library, by name
python -m heat3d_gamefiles course "Example Circuit"

# One lap file, a narrower band, a smaller file
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Winter textures, trees included
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# A hard ceiling of 500,000 placed triangles
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# A track folder given directly (game installed outside Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: name the level, point at the install
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, with a plain CSV lap that does not say its game
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Dæmi um úttak (Forza, tilbúnar tölur):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Sérhver bíll uppsetts Forza í lágum smáatriðum leiksins sjálfs, í einni skrá fyrir
kappakstursflipa skoðarans: `ProxyLOD` líkanið sem hvert bílaskjalasafn undir `media/Cars`
ber, um 900 þríhyrningar, með númeri bílsins eins og mælingagögnin nefna það,
framleiðanda, gerðarmerki og árgerð úr nafni skjalasafnsins, og hjólum og afturljósum hans. Tekur
sekúndur og skrifar um 5 MB. Keyrðu það aftur þegar leikurinn fær nýja
bíla. Skjalasafn án slíks líkans (umferðarhlutur) er nefnt og sleppt. Sniðið
er í [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Formin eru í metrum, leiksins eigin: 1:1 við bílinn. Skráin geymir
efni leiksins, svo hún er fyrir vélina sem hún var gerð á, ekki til að dreifa.

## courses

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Þetta keyrir Forza `course` útflutninginn á sérhverja brautarmöppu í upptekn­u hringasafni,
og skrifar eina `<name>.glb` fyrir hverja. Það er aðeins fyrir Forza. Það kallar beint á Forza
útflutninginn og les ekki `--game`, `--level` eða `--install`.

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `-o`, `--out FOLDER` | `courses`, eða `$HEAT3D_LEVELS/forza/courses` þegar það er stillt | mappan sem skrifað er í (búin til ef hún vantar) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | hringasafnið |
| `--only TEXT [TEXT ...]` | allt | aðeins brautir þar sem möppuheitið inniheldur eitt af þessu (hástafir og lágstafir skipta ekki máli) |
| `--force` | af | flytja aftur út það sem á þegar `.glb` |
| `--track DIR` | leitað | eins og fyrir `course` |
| `--margin M` | 80 | eins og fyrir `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | eins og fyrir `course` |

Hvað telst brautarmappa: bein undirmappa safnsins sem heiti hennar
inniheldur ` (course_`, en þannig nefnir FH Companion þær, til dæmis
`Example Circuit (course_1200_3400_to_1175_3400)`. Hlutinn frá ` (course_` og áfram
er felldur úr nafninu.

Hvernig keyrslan hegðar sér:

- Braut sem `.glb` er þegar til fyrir er sleppt (`kept`) nema `--force` sé gefið, svo rofin keyrsla heldur áfram þar sem hún hætti.
- `.glb` sem eldri útgáfa skrifaði, án eigin lags kappakstursmótsins og vettvanga þess (`asset.extras.course_format` vantar eða er lægra en núverandi), er flutt aftur út, eins og `--force` hefði verið gefið fyrir hana eina.
- Tvær brautarmöppur með sama nafn á undan ` (course_` (upptökuforrit sem nefndi nýja braut eftir gamalli) skrifa ekki yfir hvor aðra: mappan sem var búin til fyrst heldur `<name>.glb`, hin er skrifuð sem `<name>_<start>.glb`, þar sem `<start>` er upphafsstaðurinn, mínusmerki sem `m` (til dæmis `example_circuit_m120_m340.glb`).
- Braut sem mistekst (ólæsilegir hringir, minni þraut, ekkert landslag...) er tilkynnt sem `FAILED`, og keyrslan heldur áfram.
- Í lokin prentar hún töflu með stöðu, stærð í MB, sekúndum og nafni, síðan `<n> of <total> courses in <folder>`.
- Skilakóðinn er 1 ef einhver braut mistókst.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Telur upp sérhvert kappakstursmót sem uppsettur Forza skilgreinir, út frá leiðaskilgreiningum hans (sjá
[Forza Horizon brautir](course-forza-horizon.md#which-race)), og ber útflutninginn
í `courses` möppu saman við þau. Það les leikinn og hringasafnið;
það skrifar ekkert nema valfrjálsu töfluna.

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `-o`, `--out FOLDER` | eins og fyrir `courses` | mappan sem `courses` skrifar í, en skrárnar í henni eru athugaðar |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | hringasafnið |
| `--track DIR` | leitað | brautarmappan, ef hún er ekki sú í uppsetta leiknum |
| `--markdown FILE` | ekkert | skrifa líka töfluna þangað, sem Markdown |

Ein röð fyrir hvert kappakstursmót, og ein fyrir hverja upptekna braut sem ekin var á því:

| Dálkur | Merking |
|---|---|
| route | leiðarauðkennið |
| course | upptekna brautin sem passar við það, ef einhver |
| own assets | eintök sem mótið bætir við frjálsa heiminn |
| drawn | af þeim, eintök sem brautin sendir líkan fyrir |
| kinds | eintökin sem bætt er við eftir tegund (varnir, leikmunir, límmiðar (decals), innviðir, ...) |
| not geometry | áhorfendamerki og árekstrarferlar (collision splines), talin |
| hidden | hlutir í frjálsa heiminum sem mótið fjarlægir |
| venue | vettvangsjarðarlíkönin sem gervigreindarlína mótsins fer innan 10 m frá |
| export | `current`, `older format` (flutt aftur út af `courses`), `not exported`, eða tómt fyrir mót án upptekinnar brautar |

Það endar á tölu: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Þetta er Forza skurðurinn með allt stafað út í höndunum: þú gefur brautarmöppuna
og svæði, ekki hring. Það nýtist þegar svæðið sem þú vilt er kassi
frekar en akstur.

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `<path>` | nauðsynlegt | Forza brautarmappa undir `media\Tracks` (með `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | nauðsynlegt | `.glb` skráin sem skrifuð er |
| `--box X0 Z0 X1 Z1` | | svæðið, í metrum leiksins (x og z, eins og mælingagögnin gefa þau upp); hornin í hvaða röð sem er |
| `--route FILE` | | leið-JSON með `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, eins og `heat3d_capture route` og `heat3d_capture laps` skrifa hana; lesin sem UTF-8, með eða án bætaraðarmerkis (byte-order mark) |
| `--margin M` | **100** | metrar sem bætast í kringum mörk leiðar, og breidd gangsins þegar leiðin hefur línu |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | eins og fyrir `course` |

Gefðu nákvæmlega eitt af `--box` og `--route`, annars er skilakóðinn 2. Með
`--route` er skurðurinn `bounds` leiðarinnar (`min`/`max`, x og z) víkkað um
jaðarinn. Ef skráin geymir líka að minnsta kosti 10 staðsetningar mjókkar skurðurinn í
gang sem er `--margin` metrar í kringum þær, og sett líkön fá smáatriði sín eftir
fjarlægð frá þeirri línu. Með `--box` er allur kassinn geymdur, og smáatriðin fara til
þess sem stendur næst miðju kassans.

Hæð er aldrei hluti af skurðinum. Kassi utan kortsins, eða í sjónum, gefur
"no terrain there" (skilakóði 1), ekki villu um hnit.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels og level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` telur upp borðin sem uppsettur Frostbite leikur sendir með, eftir nafni
töflu þeirra (`levels/<level>/<level>.toc`), með stærð hennar og hvaðan hún
kemur: `Data` fyrir grunnleikinn, `Update/<pack>` fyrir uppfærslu, og hversu margar
háupplausnartöflur bæta við hana. Borð sem uppfærsla sendir hefur litla töflu
með bitum eingöngu í grunnleiknum líka; taflan með búntum borðsins er
borðið (sjá [Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` flytur eitt út: landslagshæðarsviðið, sérhvert net sem kyrrnetahópar (static model groups) borðsins
setja, hlutina sem eru settir einn og einn, hvar þeir standa, og
landslagsbakgrunn borðsins í kringum kortið. Með `--textures` ber sérhver flötur
litakort sitt; með `--navmesh` fylgja flötarnir sem hermenn ganga á. Hvernig
það er lesið er í [Frostbite](reader-frostbite.md).

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `<level>` | nauðsynlegt | nafn eins og `levels` prentar það, einkennandi hluti þess, eða slóð `.toc` borðsins |
| `-o`, `--out FILE` | `<level>.glb` (í `$HEAT3D_LEVELS/<game>/` þegar það er stillt) | `.glb` skráin sem skrifuð er |
| `--install FOLDER` | fyrsti Steam leikurinn sem `Data` hans geymir `layout.toc` | leikjamappan |
| `--textures [PIXELS]` | af; 512 þegar gefið án stærðar | skrifa litakort hvers flatar, stærsta mip-stigið sem er ekki stærra en PIXELS á hlið, og áferðarhnit þess eins og leikurinn hefur þau, með endurtekandi sýnatökutæki (sampler) (sjá [Úttakssnið](output-format.md)). Hæðarsviðið fær litakort landslagsbakgrunnsins þar sem það kort nær yfir það, annars miðlit yfirborðsefna landslagsins, annars meðallit bakgrunnsins í kring. Af er sérhver hluti flatur litur |
| `--ground-texture [METRES]` | af; 0.5 þegar gefið án stærðar | baka landslagsmerkingarnar (decals) — vegi, flugbrautir, stæði, máluð merki — yfir jarðarlitinn, margfaldað með litakorti landslagsins þar sem borðið hefur slíkt, inn í lit hæðarsviðsins, METRES á punkt, í flísum sem eru í mesta lagi 4.096 punktar (`ground:terrain x<x> z<z>`). Virkar með eða án `--textures` |
| `--navmesh` | af | bæta við leiðsögunetinu fyrir minnsta geranda borðsins, hermanninn (1,8 m á hæð, 0,4 m á breidd), sem hlutanum `nav:walkable`: jörðin, gólf, stigar og þökin sem hermaður kemst á, án tenginganna (stökk, stigar, yfirstig) á milli þeirra |
| `--ground-spacing METRES` | 4 | fínasta bil hæðarsviðsins; hnútar sem eru fínni en þetta eru teknir niður. 0 sleppir hæðarsviðinu |
| `--detail-budget N` | hvert eintak á grófasta stigi sínu, auk fjórðungs, að minnsta kosti 1.500.000 | hámark á þríhyrninga. Netin sem kosta mest fara niður um eitt smáatriðastig í einu þar til það passar; ef ekki einu sinni grófustu stigin duga eru minnstu eintökin skilin út fyrst. Landslagsbakgrunnurinn er aldrei grófgerður eða skilinn eftir |
| `--skip TEXT` | | sleppa kyrrnetahópum þar sem skiptingarheitið inniheldur TEXT; endurtaktu fyrir fleiri. Til dæmis lag leikjaháttar |
| `--by-mesh` | af | til að finna hvað hlutur er: einn hluti fyrir hvert upprunanet og efni, nefndur `<part> \| <mesh> \| <material>`; miklu stærri skrá |
| `--clamped-uvs` | af | fyrir birti sem getur ekki endurtekið áferð: skera sérhvern áferðarþríhyrning í búta þar sem hnitin liggja innan 0..1, og teikna þríhyrning sem þyrfti fleiri en 4 búta í meðallit áferðar sinnar, í hlutanum `<part> (average colour)` |

Það prentar hópana og hversu mörg eintök hver setti, netin sem það sleppti og
hvers vegna, þríhyrningana fyrir hvern hluta (og með `--textures` hversu margar áferðir, og hversu
margir hlutar fundu litakort sitt), hvað jörðin er, og með
`--navmesh` hversu margar leiðsöguflísar voru lesnar. Ekkert er skrifað um borðið nema
rúmfræðina: engin nöfn, engin lýsigögn (sjá [Úttakssnið](output-format.md)).

Landslagskostnaðurinn er aðskilinn: hæðarsviðið og bakgrunnurinn eru aldrei
grófgerð af `--detail-budget`; `--ground-spacing` ákvarðar stærð hæðarsviðsins.

Heilt borð er stórt: yfirleitt yfir tíu milljón þríhyrninga og nokkur
hundruð MB. `--textures` bætir litlu við skrána; borð þétt af trjám
getur náð um 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8`
kemur borði niður í um þriðjung af því.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps og ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` er mappa leiksins, `Content/Paks` hennar, eða nafn möppu hans
í Steam-safni (`"<Steam game folder name>"`). `ue-maps` telur upp sérhvert kort
sem hefur eldaðar World Partition frumur (cells) við hliðina. `ue-map` flytur eitt út sem
`ground:<map>` (landslagið), `structure:<map>` (sameinuðu HLOD
net kortsins) og `water:<map>` (vatnshlot þess þar sem þau standa fyrir ofan
jörðina), í Unreal **sentímetrum** með Y og Z víxlað - eini útflutningurinn sem
er ekki í metrum. Hvernig hver er lesinn og athugaður: [Unreal 5 kort](level-unreal-world-partition.md).

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `<map>` | nauðsynlegt | nafn eins og `ue-maps` prentar það, eða einkennandi hluti þess |
| `-o`, `--out FILE` | `<map>.glb` (í `$HEAT3D_LEVELS/<game>/` þegar það er stillt) | `.glb` skráin sem skrifuð er |
| `--ground-spacing METRES` | 2 | hnútabil landslagsins í skránni, námundað að heilli tölu af eigin ferningum þess |
| `--no-structures`, `--no-water` | | sleppa þeim hluta |

Það prentar þríhyrningana fyrir hvern hluta, hversu margir landslagshlutar voru lesnir og
hversu margir af hnútunum sem þeir geyma tvisvar eru ósammála. 3 km kort
með 2 m bili eru um 4,6 milljón jarðarþríhyrningar.

## enfusion-worlds og enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` telur upp sérhvern heim með landslagi, eftir möppu hans undir
`worlds/`. `enfusion-world` flytur einn út: `ground:<world>` (landslagið, í
litum yfirtexture-flísa þess), `water:<world>` (sjóinn, í hæð núll)
og `structure:<world>` (kassa hvers settra líkans), í metrum leiksins sjálfs -
x austur, y upp, z norður. Hvernig hver er lesinn og athugaður:
[Arma Reforger heimar](level-arma-reforger.md).

| Valkostur | Sjálfgefið | Merking |
|---|---|---|
| `<world>` | nauðsynlegt | heimur eins og `enfusion-worlds` prentar hann |
| `-o`, `--out FILE` | `<world>.glb` (í `$HEAT3D_LEVELS/<game>/` þegar það er stillt) | `.glb` skráin sem skrifuð er |
| `--install FOLDER` | Steam-safnið sem geymir leikinn | leikjamappan |
| `--ground-spacing METRES` | 2 (eigið bil landslagsins) | hnútabil landslagsins í skránni |
| `--texture-size PIXELS` | 4096 | stærri hlið jarðarlitamyndarinnar; 0 fyrir flatan lit |
| `--no-structures` | | sleppa settu líkönunum |
| `--trees` | af | setja líka tré og annan gróður, sem kassa |

Það prentar þríhyrningana fyrir hvern hluta, hversu margir flísarbrúnahnútar eru ósammála,
hversu margar einingar (entities) heimsskráin geymir og hversu margir kassar voru settir, og hvað var
skilið eftir og hvers vegna.

## Umhverfisbreytur {#environment-variables}

| Breyta | Áhrif |
|---|---|
| `HEAT3D_OODLE` | slóð að `oo2core_*_win64.dll`, eða möppu sem geymir eina; sjá [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | ein mappa fyrir sérhvern útflutning sem er gerður án `-o`: útflutningur hvers leiks fer í `<HEAT3D_LEVELS>/<game>/` (brautir í `<game>/courses/`, bílapakkinn í `forza/`). Óstillt fara þeir í núverandi möppu |
| `HEAT3D_NO_UPDATE` | hvaða gildi sem er annað en tómt, `0`, `false`, `no` slekkur á uppfærsluathuguninni; sjá [Uppfærslur](updates.md) |
| `LOCALAPPDATA` | hvar FH Companion safnið, notendamappa BeamNG og uppfærsluskyndiminnið eru leitað |
| `HEAT3D_COURSE` | aðeins prófanir: brautin sem kantsteinaprófun uppsetts leiks notar; sjá [Þróun](development.md) |
