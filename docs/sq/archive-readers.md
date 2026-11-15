---
title: "Lexuesit e arkivave"
nav_order: 9
lang: "sq"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Lexuesit e arkivave {#archive-readers}

Një **kontejner** (ose arkiv) është një skedar i madh ku një lojë paketon shumë skedarë.
Një **CRC** ose hash është një gjurmë e shkurtër e disa bajteve: nëse përputhet, bajtet
janë lexuar saktë. Një **kuti kufizuese** (bounding box) është kutia më e vogël rreth një modeli.

Nën komandat ka lexues për kontejnerët që dërgojnë lojërat. Formatet e tyre nuk
janë të dokumentuara, përveç VPK të Valve dhe `.cdae` të BeamNG, prandaj "i mbështetur" duhet
të nënkuptojë **i verifikuar me skedarë të vërtetë**, jo "nuk u rrëzua". Çdo lexues kontrollon
veten me diçka që formati e garanton: një hash, një CRC, një zinxhir ofsetesh
që duhet të mbyllet, një kuti kufizuese e ruajtur. Kur një kontroll dështon, lexuesi refuzon
me një mesazh në vend që të hamendësojë. Një rrjetë e gabuar duket si e saktë derisa
dikush ta vendos pranë pistës.

| Lexuesi | Moduli | Lexon | Nuk lexon | Arrihet nga |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versionet 8-12: indeksin, hyrjet, blloqet Zlib/Gzip/Oodle, AES me një çelës që e jep ti | versionet para 8, indekset vetëm me hash të shtegut, hyrjet e tejmbushura, përmbajtjen e asete | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, kontrolluar në v8), paketat zen, veti pa version për disa klasa komponentësh, rrjeta statike të gatuara (cooked), teksturat, teksturat virtuale me transmetim | kontejnerët e enkriptuar, paketat me version, rrjetat vetëm Nanite, vetitë e klasave të tjera | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | blloqet Oodle përmes një biblioteke që ndodhet tashmë në kompjuter | gjithçka pa një bibliotekë të tillë; nuk përfshihet kurrë | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | formatin `SerializedFile` 22+ (Unity 2020 deri 6000), paketat `UnityFS`, rrjetat e pakompresuara përfshirë `.resS` | formatet para 2020, pemët e llojeve të ngulitura, rrjetat e kompresuara, çdo klasë përveç `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | pemët DbObject të `.toc` dhe tabelat binare të seksioneve, paketat e instalimit, vendndodhjet e copave (chunk), paketat e brendshme dhe manifestet e tyre, ndarjet RIFF EBX, rrjetat MeshSet, fushën e lartësive të terrenit, teksturat BC1/BC3/BC7 dhe blloqet e tyre të shaderave, vendosjen e grupeve të modeleve statike | tabelat e turbulluara me XOR, ngjyrën e terrenit afër tokës dhe vrimat, hartat e normaleve, alfën përveç prerjeve | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versionet 1 dhe 2, arkivat e ndara, të dhënat e para-ngarkimit, kontrollin CRC | asetet e përpiluara (`.vmdl_c`, `.vtex_c`), formatin e rrjetës së navigimit të CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, stored), gjeometrinë `.modelbin`, mostrat `.pb` (BC1, BC7, RGBA), vendosjet `.pgeo`, hash-et e teksturave të materialeve | formatet e tjera të kulmeve dhe indekseve, formatet e tjera të teksturave, shtresat e shaderit të terrenit | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` dhe `extract` (`.minizip`) |
| [Skedarët e BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | sistemin e montuar të skedarëve zip, JSON të skenës dhe TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materialet | rrjetat me skelet dhe me decal, sekuencat e animuara, mbulesën procedurale të tokës | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` dhe `extract` (zip) |

## Rregullat që ndjek çdo lexues {#rules-every-reader-follows}

- **Pa çelësa të dërguar, pa çelësa të rikuperuar.** Një arkiv i enkriptuar hapet vetëm me një çelës
  që e jep ti (Unreal `.pak`, `--key`). Një kontejner IoStore i enkriptuar refuzohet.
  Asgjë nuk kërkon çelës brenda një ekzekutuesi dhe nuk lexon memorien e procesit tjetër. Shih
  [Rregullat dhe licencat](rules-and-licences.md).
- **Pa kod pronësor të përfshirë.** Oodle ngarkohet nga një lojë ose motor që është
  tashmë i instaluar në kompjuter.
- **Refuzo në vend që të hamendësosh.** Një version, kodek, format kulmesh ose format
  teksture i panjohur ngre një gabim të veçantë, si
  `texture format 42 has not been identified; refusing to guess`.
- **Vetëm lexim.** Asnjë lexues nuk shkruan në dosjen e një loje. Eksportet shkojnë ku e thua ti.

## Çfarë nënkuptonte "i verifikuar" {#what-verified-meant}

Shifrat e verifikimit që citohen në këto faqe vijnë nga docstring-et e moduleve.
Ato u matën me lojëra të instaluara ndërsa shkruhej çdo lexues. Testet
sintetike (shih [Zhvillimi](development.md)) fiksojnë strukturën e fushave. Testet
me lojë të instaluar përsëritin disa nga kontrollet kur loja është në kompjuter,
dhe anashkalohen përndryshe. Shifrat që nuk mbulohen nga një test nuk janë rikontrolluar që atëherë.
