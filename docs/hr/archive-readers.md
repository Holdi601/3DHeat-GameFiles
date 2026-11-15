---
title: Čitači arhiva
nav_order: 9
lang: "hr"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Čitači arhiva {#archive-readers}

**Spremnik** (ili arhiva) je jedna velika datoteka u koju igra spakira mnogo
drugih datoteka. **CRC** ili hash je kratki otisak nekih bajtova: ako se
podudara, bajtovi su pročitani ispravno. **Omeđujući okvir** (bounding box) je
najmanji okvir oko modela.

Ispod naredbi nalaze se čitači za spremnike koje igre isporučuju. Njihovi formati
nisu dokumentirani, osim Valveovog VPK-a i BeamNG-ova `.cdae`-a, pa "podržano"
mora značiti **provjereno na stvarnim datotekama**, a ne "nije se srušilo". Svaki
čitač provjerava sebe prema nečemu što format jamči: hashu, CRC-u, lancu pomaka
koji se mora zatvoriti, spremljenom omeđujućem okviru. Gdje provjera ne prođe,
čitač odbija s porukom umjesto da nagađa. Pogrešna mreža izgleda kao ispravna
dok je ne stavite uz stazu.

| Čitač | Modul | Čita | Ne čita | Pokreće se iz |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | verzije 8-12: indeks, unosi, Zlib/Gzip/Oodle blokovi, AES s ključem koji vi dajete | verzije prije 8, indekse samo s hashevima putanja, prekoračene unose, sadržaj assetā | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, provjereno na v8), zen pakete, neverzionirana svojstva za nekoliko klasa komponenti, obrađene statičke mreže, teksture i streaming virtualne teksture | šifrirane spremnike, verzionirane pakete, mreže samo za Nanite, skeletne mreže, svojstva ostalih klasa | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle blokove kroz biblioteku koja je već na računalu | sve bez takve biblioteke; nikad se ne isporučuje uz alat | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22 i noviji (Unity 2020 do 6000), `UnityFS` pakete, nekomprimirane mreže, uključujući `.resS` | formate prije 2020., ugrađena stabla tipova, komprimirane mreže, bilo koju klasu osim `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc` stabla DbObject i binarne tablice odjeljaka, instalacijske pakete, lokacije dijelova, unutarnje pakete i njihove manifeste, RIFF EBX particije, MeshSet mreže, visinsko polje terena, BC1/BC3/BC7 teksture i njihove blokove sjenčala, raspored statičkih grupa modela | tablice zaštićene XOR-om, boju terena blizu tla, rupe u terenu, normalne mape, alfa osim izrezā | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | verzije 1 i 2, podijeljene arhive, prethodno učitane podatke, provjeru CRC-a | kompajlirane assete (`.vmdl_c`, `.vtex_c`), format CS2 navigacijske mreže | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, bez kompresije), geometriju `.modelbin`, uzorke boja `.pb` (BC1, BC7, RGBA), položaje `.pgeo`, hashove tekstura materijala | ostale formate vrhova i indeksa, ostale formate tekstura, slojeve sjenčala terena | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` i `extract` (`.minizip`) |
| [BeamNG datoteke](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | montirani zip sustav datoteka, JSON scene i TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materijale | skinned i decal mreže, animirane sekvence, proceduralni pokrov tla | `course` (BeamNG), `identify` (zipovi, `.cdae`, `.ter`), `list` i `extract` (zipovi) |

## Pravila koja slijedi svaki čitač {#rules-every-reader-follows}

- **Nema ključeva u isporuci, nijedan se ne izvlači.** Šifrirani arhiv se otvara
  samo ključem koji vi imate (Unreal `.pak`, `--key`). Šifrirani IoStore spremnik
  se odbija. Ništa ne traži ključ u izvršnoj datoteci i ne čita memoriju tuđeg
  procesa. Vidi [Pravila i licence](rules-and-licences.md).
- **Nema tuđeg zaštićenog koda u paketu.** Oodle se učitava iz igre ili pogona
  koji je već instaliran na računalu.
- **Odbij umjesto da nagađaš.** Nepoznata verzija, kodek, format vrhova ili format
  teksture daje specifičnu grešku, na primjer
  `texture format 42 has not been identified; refusing to guess`.
- **Samo čitanje.** Nijedan čitač ne piše u mapu igre. Izvoz ide tamo gdje vi kažete.

## Što znači "provjereno" {#what-verified-meant}

Brojke provjere na ovim stranicama dolaze iz docstringova modula. Mjerene su na
instaliranim igrama dok se svaki čitač pisao. Sintetski testovi (vidi
[Razvoj](development.md)) fiksiraju raspored polja. Testovi na instaliranim
igrama ponavljaju neke provjere kad je igra na računalu, a inače se preskaču.
Brojke koje nisu pokrivene testom nisu ponovno provjerene otkad su zapisane.
