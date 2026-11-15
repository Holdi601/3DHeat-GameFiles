---
title: "Čitači arhiva"
nav_order: 9
lang: "bs"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Čitači arhiva {#archive-readers}

**Kontejner** (ili arhiva) je jedna velika datoteka u koju igra pakuje mnogo
datoteka. **CRC** ili hash je kratki otisak nekoliko bajtova: ako se podudara,
bajtovi su ispravno pročitani. **Granična kutija** (bounding box) je najmanja
kutija oko modela.

Ispod komandi nalaze se čitači za kontejnere koje igre isporučuju. Njihovi formati
nisu dokumentirani, osim Valveovog VPK-a i BeamNG-ovog `.cdae`, pa "podržano"
mora značiti **provjereno na stvarnim datotekama**, a ne "nije se srušilo". Svaki
čitač provjerava sam sebe nečim što format jamči: hashom, CRC-om, lancem pomaka
koji se mora zatvoriti, pohranjenom graničnom kutijom. Gdje provjera ne uspije,
čitač odbija nastaviti uz poruku umjesto da pogađa. Pogrešna mreža izgleda kao
ispravna sve dok je neko ne stavi pored staze.

| Čitač | Modul | Čita | Ne čita | Dostupno iz |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | verzije 8-12: indeks, unose, Zlib/Gzip/Oodle blokove, AES s ključem koji date | verzije prije 8, indekse samo s hashom putanje, unose preljeva (overflow), sadržaj asseta | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, provjereno na v8), zen pakete, neverzionirana svojstva za nekoliko klasa komponenti, pečene statičke mreže, teksture, streaming virtualne teksture | šifrirane kontejnere, verzionirane pakete, mreže samo za Nanite, svojstva drugih klasa | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle blokove kroz biblioteku koja je već na računaru | sve bez takve biblioteke; nikad se ne isporučuje | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | format `SerializedFile` 22+ (Unity 2020 do 6000), `UnityFS` pakete, nekomprimirane mreže uklj. `.resS` | formate prije 2020, ugrađena stabla tipova, komprimirane mreže, sve klase osim `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc` DbObject stabla i binarne tablice sekcija, instalacijske pakete, lokacije chunkova, ugrađene bundlove i njihove manifeste, RIFF EBX particije, MeshSet mreže, visinsko polje terena, BC1/BC3/BC7 teksture i njihove shader blokove, postavljanje grupa statičkih modela | XOR-obfuscirane tablice, boju terena blizu tla i rupe, normal mape, alfu osim izreza (cut-out) | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | verzije 1 i 2, podijeljene arhive, preload podatke, CRC provjeru | kompilirane assete (`.vmdl_c`, `.vtex_c`), CS2 format navigacijske mreže | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, pohranjeno), `.modelbin` geometriju, `.pb` uzorke (BC1, BC7, RGBA), `.pgeo` postavljanja, hasheve tekstura materijala | druge formate vrhova i indeksa, druge formate tekstura, slojeve shadera terena | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` i `extract` (`.minizip`) |
| [BeamNG datoteke](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | montirani zip datotečni sistem, JSON scene i TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materijale | skinirane mreže i mreže decala, animirane sekvence, proceduralno raslinje po tlu | `course` (BeamNG), `identify` (zipovi, `.cdae`, `.ter`), `list` i `extract` (zipovi) |

## Pravila kojih se drži svaki čitač {#rules-every-reader-follows}

- **Nikakvi ključevi se ne isporučuju, nijedan se ne otkriva.** Šifrirana arhiva
  se otvara samo ključem koji predate (Unreal `.pak`, `--key`). Šifrirani
  IoStore kontejner se odbija. Ništa ne traži ključ u izvršnoj datoteci niti čita
  memoriju drugog procesa. Pogledajte [Pravila i licence](rules-and-licences.md).
- **Nikakav vlasnički kod nije priložen.** Oodle se učitava iz igre ili engina
  koji je već instaliran na računaru.
- **Odbijanje umjesto pogađanja.** Nepoznata verzija, kodek, format vrhova ili
  format teksture izaziva određenu grešku, na primjer
  `texture format 42 has not been identified; refusing to guess`.
- **Samo za čitanje.** Nijedan čitač ne piše u folder igre. Izvozi idu tamo gdje
  vi kažete.

## Šta je značilo "provjereno" {#what-verified-meant}

Brojke provjere navedene na ovim stranicama potiču iz docstringova modula.
Mjerene su na instaliranim igrama dok je svaki čitač pisan. Sintetički testovi
(pogledajte [Razvoj](development.md)) učvršćuju rasporede polja. Testovi na
instaliranim igrama ponavljaju neke provjere kad je igra na računaru, a inače se
preskaču. Brojke koje nijedan test ne pokriva nisu ponovo provjeravane.
