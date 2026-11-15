---
title: Archívumolvasók
nav_order: 9
lang: "hu"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Archívumolvasók {#archive-readers}

Egy **konténer** (vagy archívum) egy nagy fájl, amelybe a játék sok fájlt csomagol.
Egy **CRC** vagy hash rövid ujjlenyomat néhány bájtról: ha egyezik, a bájtokat helyesen
olvasták be. Egy **határoló doboz** (bounding box) a modell körüli legkisebb doboz.

A parancsok alatt olyan olvasók vannak, amelyek a játékok konténereit olvassák. Ezek
formátuma nem dokumentált, a Valve VPK-ja és a BeamNG `.cdae` formátuma kivételével. Ezért
a „támogatott" azt jelenti: **valódi fájlokon ellenőrizve**, nem azt, hogy „nem omlott
össze". Minden olvasó ellenőrzi magát valamivel, amit a formátum garantál: hash-sel, CRC-vel,
eltolások láncával, amelynek záródnia kell, vagy a tárolt határoló dobozzal. Ha egy
ellenőrzés nem sikerül, az olvasó üzenettel megáll, és nem találgat. A rossz háló pontosan
úgy néz ki, mint a jó, amíg valaki a pálya mellé nem teszi.

| Olvasó | Modul | Olvassa | Nem olvassa | Innen hívják |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | 8–12-es verziók: index, bejegyzések, Zlib/Gzip/Oodle blokkok, AES a megadott kulccsal | 8 előtti verziók, csak path-hash indexek, túlcsordulási bejegyzések, eszköztartalmak | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, v8-on ellenőrizve), zen csomagok, nem verziózott tulajdonságok néhány komponensosztályhoz, feldolgozott statikus hálók, textúrák, streamelt virtuális textúrák | titkosított konténerek, verziózott csomagok, csak Nanite hálók, más osztályok tulajdonságai | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle blokkok a gépen már meglévő könyvtáron keresztül | bármi, amihez nincs ilyen könyvtár; soha nincs csomagolva | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` 22-es és újabb formátum (Unity 2020-tól 6000-ig), `UnityFS` csomagok, tömörítetlen hálók, a `.resS`-ben lévők is | 2020 előtti formátumok, beágyazott típusfák, tömörített hálók, a `Mesh`-en kívül más osztály | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc` DbObject fák és bináris szakasztáblák, telepítőcsomagok, darabhelyek, beágyazott csomagok és jegyzékeik, RIFF EBX partíciók, MeshSet hálók, a terep magassági mezője, BC1/BC3/BC7 textúrák és árnyalóblokkjaik, statikus modellcsoportok elhelyezése | XOR-ral elrejtett táblák, a terep talajszíne és lyukai a talaj közelében, normáltérképek, a vágásokon kívüli alfa | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | 1-es és 2-es verzió, többrészes archívumok, előtöltött adatok, CRC-ellenőrzés | fordított eszközök (`.vmdl_c`, `.vtex_c`), a CS2 navigációs háló formátuma | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, tárolt), `.modelbin` geometria, `.pb` mintakártyák (BC1, BC7, RGBA), `.pgeo` elhelyezések, anyagok textúra-hashei | más csúcs- és indexformátumok, más textúraformátumok, a terep árnyalórétegei | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` és `extract` (`.minizip`) |
| [BeamNG-fájlok](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | a csatolt zip-fájlrendszer, jelenetfájlok JSON-ban és TorqueScriptben, `.ter`, `.cdae` v31, Collada `.dae`, anyagok | csontozott és matricaháló, animált sorozatok, procedurális talajborítás | `course` (BeamNG), `identify` (zipek, `.cdae`, `.ter`), `list` és `extract` (zipek) |

## Minden olvasó szabályai {#rules-every-reader-follows}

- **Nincs kulcs a csomagban, és nem is nyerünk ki.** Titkosított archívum csak az általad
  megadott kulccsal nyílik meg (Unreal `.pak`, `--key`). A titkosított IoStore-konténert
  elutasítjuk. Semmi nem keres kulcsot futtatható fájlban, és semmi nem olvassa egy másik
  folyamat memóriáját. Lásd: [Szabályok és licencek](rules-and-licences.md).
- **Nincs csomagolt zárt kód.** Az Oodle-t olyan játékból vagy motorból töltjük be, amely már
  telepítve van a gépen.
- **Inkább megtagadjuk, mint kitalálunk.** Ismeretlen verzió, kodek, csúcsformátum vagy
  textúraformátum konkrét hibát dob, például `texture format 42 has not been identified; refusing to guess`.
- **Csak olvasás.** Egyik olvasó sem ír játékmappába. Az exportok oda kerülnek, ahová megmondod.

## Mit jelent az, hogy „ellenőrizve" {#what-verified-meant}

Az ezeken az oldalakon idézett ellenőrzési számok a modulok docstringjeiből származnak. Azokat
a telepített játékokon mérték, miközben minden olvasót írtak. A szintetikus tesztek (lásd:
[Fejlesztés](development.md)) rögzítik a mezők elrendezését. A telepített játékon futó
tesztek megismétlik az ellenőrzések egy részét, ha a játék a gépen van, egyébként kihagyják
őket. Ami nincs tesztelve, azt azóta nem ellenőriztük újra.
