---
title: "Skjalasafnslesarar"
nav_order: 9
lang: "is"
source: archive-readers.md
source_hash: "0f1064f05cfd"
nav_exclude: true
search_exclude: true
---
# Skjalasafnslesarar {#archive-readers}

**Ílát** (eða skjalasafn) er ein stór skrá sem leikur pakkar mörgum skrám í. **CRC**
eða tætigildi er stutt fingrafar af nokkrum bætum: ef það stemmir voru bætin
lesin rétt. **Umlykjandi kassi** (bounding box) er minnsti kassinn utan um líkan.

Undir skipununum eru lesarar fyrir ílátin sem leikir senda með. Snið þeirra
eru óskjalfest, fyrir utan VPK frá Valve og `.cdae` frá BeamNG, svo „studd“ þarf að
þýða **sannreynt á raunverulegum skrám**, ekki „hrundi ekki“. Hver lesari prófar
sjálfan sig á einhverju sem sniðið tryggir: tætigildi, CRC, keðju af hliðrunum
sem verður að ganga upp, geymdum umlykjandi kassa. Þar sem prófun mistekst neitar lesarinn
með skilaboðum í stað þess að giska. Rangt net lítur út eins og rétt þar til
einhver leggur það við hliðina á brautinni.

| Lesari | Eining | Les | Les ekki | Nást með |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | útgáfur 8-12: vísi, færslur, Zlib/Gzip/Oodle blokkir, AES með lykli sem þú gefur upp | útgáfur fyrir 8, vísa sem hafa aðeins slóðatætigildi, yfirflæðisfærslur, innihald eigna | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, prófað á v8), zen-pakka, óútgefnar eigindir fyrir nokkra íhlutaflokka, bakaða kyrrstæða net, áferðir, streymandi sýndaráferðir | dulkóðuð ílát, útgáfumerkta pakka, net sem eru eingöngu Nanite, eigindir annarra flokka | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle blokkir í gegnum safn sem er þegar á vélinni | allt án slíks safns; það er aldrei sent með | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` snið 22+ (Unity 2020 til 6000), `UnityFS` búnt, óþjöppuð net þar með talið `.resS` | snið fyrir 2020, innbyggð gerðatré, þjöppuð net, allir flokkar nema `Mesh` | `identify`, `meshes` |
| [Frostbite](../reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc` DbObject tré og tvíundar kaflatöflur, uppsetningarpakka, staðsetningar bita, innbyggð búnt og skrár þeirra, RIFF EBX skipt svæði, MeshSet net, landhæðarsvið, BC1/BC3/BC7 áferðir og skuggablokkir þeirra, staðsetningu hópa kyrrstæðra líkana | XOR-hulin töflur, nærlitun og göt landsins, normal-kort, alfa annað en útklippur | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | útgáfur 1 og 2, skipt skjalasöfn, forhleðslugögn, CRC-prófun | þýddar eignir (`.vmdl_c`, `.vtex_c`), CS2 leiðarnetssniðið | `identify`, `list`, `extract` |
| [ForzaTech](../reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, geymt), `.modelbin` rúmfræði, `.pb` sýnishorn (BC1, BC7, RGBA), `.pgeo` staðsetningar, tætigildi áferða efnis | önnur snið hnúta og vísa, önnur áferðarsnið, skuggalög landsins | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` og `extract` (`.minizip`) |
| [BeamNG skrár](../reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | tengda zip-skráakerfið, senu-JSON og TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, efni | net með beinagrind og límmiðanet, hreyfiraðir, kerfisbundinn gróður á jörðu | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` og `extract` (zip) |

## Reglur sem hver lesari fylgir {#rules-every-reader-follows}

- **Engir lyklar sendir með, engir endurheimtir.** Dulkóðað skjalasafn opnast aðeins með lykli
  sem þú gefur upp (Unreal `.pak`, `--key`). Dulkóðað IoStore ílát er hafnað.
  Ekkert leitar að lykli í keyrsluskrá eða les minni annars ferlis. Sjá
  [Reglur og leyfi](rules-and-licences.md).
- **Enginn séreignarkóði sendur með.** Oodle er hlaðið úr leik eða vél sem þegar
  er sett upp á tölvunni.
- **Neita frekar en að giska.** Óþekkt útgáfa, þjöppun, hnútasnið eða
  áferðarsnið veldur sértækri villu, til dæmis
  `texture format 42 has not been identified; refusing to guess`.
- **Skrifvarið.** Enginn lesari skrifar í leikjamöppu. Útflutningur fer þangað sem þú segir.

## Hvað „sannreynt“ þýddi {#what-verified-meant}

Sannprófunartölurnar á þessum síðum koma úr skýringartexta eininganna.
Þær voru mældar á uppsettum leikjum þegar hver lesari var skrifaður. Gervipróf
(sjá [Þróun](development.md)) festa í sessi uppröðun reitanna. Prófin á uppsettum leikjum
endurtaka sum athugananna þegar leikurinn er á tölvunni, og sleppa þeim annars.
Tölur sem ekkert próf nær yfir hafa ekki verið athugaðar aftur síðan.
