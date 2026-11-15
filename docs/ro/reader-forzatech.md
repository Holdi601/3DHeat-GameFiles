---
title: "ForzaTech: `.minizip`, `.modelbin`, mostre, plasări"
nav_order: 7
lang: "ro"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, mostre, plasări {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon rulează pe ForzaTech, motorul propriu al Turn 10. Aceste cititoare duc un traseu din arhivele lui până la triunghiuri poziționate și texturate. Se ajunge la ele prin `course`, `courses` și `terrain` (vezi [Forza Horizon](course-forza-horizon.md)). `identify` recunoaște un `.minizip` și un `.modelbin` de sine stătător, iar `list` și `extract` iau un `.minizip`, după numele din `ChunkContentsMiniZip<n>.txt` de lângă el sau după numărul intrării (`#12`).

| Format | Modul |
|---|---|
| arhivele `.minizip` și listele lor de nume | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modelele și terenul `.modelbin` | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| mostrele de textură `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| fișierele de plasare `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` și hash-urile texturilor de material | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| dalele de teren după loc | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza păstrează o mare parte din conținut și în arhive ZIP obișnuite sub `media\`. `zipfile` din Python le deschide, iar `forzatech.models_in_archive()` listează intrările lor `.modelbin`. Geometria traseului se află în arhivele `.minizip`.

## `.minizip`: o arhivă fără nume {#minizip-an-archive-with-no-names}

Un traseu livrează patru arhive `GeoChunk<n>.minizip`, de zeci de gigabytes fiecare pentru o hartă de lume deschisă, cu sute de mii de intrări. **Arhivele nu stochează niciun nume**: nicio tabelă de nume, niciun antet pe intrare, doar un ordinal. Numele sunt în `ChunkContentsMiniZip<n>.txt` de lângă fiecare arhivă, câte o linie pentru fiecare intrare, în ordinea intrărilor (`<build path>zipcache\pc\<path>|<bundle>`). Această asociere este singura cale de a cere un fișier. Tot ce ține până la `zipcache\pc\` se elimină, iar căutările ignoră majusculele.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Trei detalii din index produc în continuare ieșire chiar când sunt citite greșit. Cititorul le tratează pe toate trei corect:

| Detaliu | Ce face un cititor neatent | Cum arată |
|---|---|---|
| baza segmentului este **pe 64 de biți** | o citește ca u32 plus padding | corectă pentru primii 4 GB, apoi zgomot de lungimea potrivită |
| baza este **aliniată la 8 octeți** | ignoră cuvântul de padding de după tabela de pachete | în arhivele cu un număr par de pachete, fiecare intrare pretinde un codec care nu există |
| lungimea stocată a unei intrări este distanța până la intrarea următoare (sau baza segmentului următor) **minus padding-ul ei** (biții de steag 12-13) | ia toată distanța | LZ4 refuză blocul cu totul |

Codecurile sunt biții mici ai steagurilor: `0x00` stocat, `0x08` deflate brut, `0x1F` bloc LZ4. Orice altceva este refuzat. Fiecare intrare trebuie să se descomprime exact la dimensiunea pe care o declară, altfel este refuzată. Indexul (circa 5 MB) se citește o singură dată, iar încărcăturile se citesc prin poziționare.

Antetul este verificat: magicul, un antet de 32 de octeți și un număr de segmente care se potrivește cu `ceil(entries / per segment)`.

**Verificat:** intrări eșantionate din fiecare arhivă a unei hărți, fiecare descomprimându-se exact la lungimea declarată, sub toate cele trei codecuri.

## `.modelbin`: containerul de bucăți {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Dimensiunea fișierului declarată trebuie să fie egală cu dimensiunea reală.
- **Lanțul**: fiecare bucată începe unde s-a terminat cea precedentă, rotunjit în sus la 4 octeți. Nimic în fișier nu o afirmă, deci este o dovadă: o înregistrare citită cu un pas greșit nu produce asta. A ținut pentru toate cele 252 de modele eșantionate.
- Un fișier `PGZP` dat cititorului de modele este numit „o arhivă ForzaTech .minizip, nu un model” și indicat spre `minizip.py`, în loc să fie respins fără explicații.

Geometria vine din aceste bucăți:

| Bucată | Conține |
|---|---|
| `VLay` | un layout de vertex: numele atributelor, apoi elementele (indexul numelui u16, canalul u16, bufferul, formatul DXGI, decalajul); numărul de elemente este un u16 |
| `VerB` | un buffer de vertexuri în spatele unui antet de 16 octeți (număr, dimensiune, pas u16, atribute u16, format) |
| `IndB` | bufferul de index, același antet |
| `Mesh` | un submesh: material, masca nivelului de detaliu, intervalul de index, layout-ul, bufferul, pasul, tabela de variante și caseta de poziție de la sfârșit |
| `MatI` | o instanță de material: calea `.materialbin` și hash-urile texturilor sale |

### Poziții și caseta {#positions-and-the-box}

Pozițiile sunt `R16G16B16A16_SNORM` (format 13): patru scurte cu semn pentru fiecare vertex. `position = short / 32767 * scale + bias`, unde scala și bias-ul sunt ultimii 32 de octeți ai bucății `Mesh` (două float4). Bias-ul este în **coordonatele lumii jocului**, deci o dală de teren ajunge unde o pune jocul fără nicio transformare de instanță. De aceea un tur de telemetrie este suficient ca să cerem o bucată de hartă. Fiecare submesh al unui model poartă aceeași casetă (verificat pe 860 dintre ele).

### Layout-ul vertexurilor {#the-vertex-layout}

Un singur buffer de poziții acoperă fiecare vertex. Celelalte atribute sunt împărțite în grupuri consecutive de vertexuri, fiecare cu propriul buffer și propriul layout: drumul lângă o intersecție poartă trei seturi de UV și două tangente, iar malul de lângă el doar o normală. Fiecare atribut care nu este poziție are patru octeți. Care layout descrie care buffer se ia din submeshurile care trag din el, pentru că layout-urile și bufferele nu sunt în aceeași ordine (la fel, rotit cu unu sau permutat, în funcție de model).

| Format DXGI | Cod | Folosit pentru |
|---|---|---|
| R16G16B16A16_SNORM | 13 | poziție (al patrulea scurt este x-ul normalei) |
| R16G16_SNORM | 37 | normala y, z |
| R16G16_UNORM | 35 | o pereche UV (canalul = al câtelea set) |
| R8G8B8A8_UNORM | 28 | culoare sau greutăți de amestec |
| R10G10B10A2_UNORM | 24 | tangentă (nedecodată) |
| R16_UINT | 57 | indecși |

**Normala este despicată.** `NORMAL` conține y și z. X-ul este al patrulea scurt al poziției, care părea padding. Pe sute de mii de vertexuri de teren, corelează +0,92 cu x-ul normalei triunghiului și cu nimic altceva. Cu el, 96% dintre vertexurile de pantă sunt în 18° de normala calculată. Fiecare codare cu două componente încercată fără el (octaedrală, în toate cele 48 de aranjamente printre ele) a dat corect y și z, dar greșit x.

Alte formate de poziție sau de index sunt **refuzate** ("only 13 (four shorts, scaled) is implemented"; "only unsigned shorts are implemented").

### Submeshuri {#submeshes}

Un record `Mesh` are 238 de octeți în forma standard. Cele mai lungi poartă înainte un tabel de **variante** de material mai lung, de 238 + 8 x count - 4 octeți, iar fiecare câmp de după el se mută înapoi exact cu aceeași cantitate. Cele mai scurte (218 octeți, unele teren) își păstrează decalajele. Fiecare intrare de variantă este `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. Masca nivelului de detaliu este un u16, un bit pentru fiecare nivel începând cu bitul 1.

Nimic nu este crezut pe cuvânt. Intervalele de index trebuie să acopere exact bufferul de index, fiecare `index count` trebuie să fie egal cu 3 x `triangles`, iar pasul pe care îl numește un submesh trebuie să fie al bufferului lui. Un tabel care eșuează este refuzat în întregime, pentru că etichetarea triunghiurilor din câmpuri citite greșit este mai rea decât a nu le eticheta. Din mii de submeshuri eșantionate, fiecare al cărui index de buffer este în limită trece.

### Materiale și hash-uri de textură {#materials-and-texture-hashes}

Un `MatI` își numește materialul printr-o cale `Game:...\x.materialbin`, găsită căutând în bucată. Texturile lui sunt înregistrări `u32 slot, u32, u32 hash`, la 33 de octeți distanță una de alta și nealiniate, deci bucata este căutată la fiecare decalaj de octet pentru cuvinte care sunt hash-uri de textură cunoscute. Acestea vin din `AssetManifest.xml` al traseului (`<Texture Source="...\name.swatch" SourceHash="...">`, citit până la `</Textures>`). Slotul `0x88B483AA` este culoarea de bază a shaderului standard. Cum se alege apoi textura de culoare se află la [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: mostre de textură {#pb-texture-swatches}

O mostră este același container `burG` ca un model: un antet `HCXT` de 96 de octeți începând de la octetul 44, apoi o bucată cu pixeli. Antetul conține GUID-ul texturii (cel din numele fișierului), lățimea și înălțimea, numărul de mip-uri și **codul formatului la octetul 72** (numerotarea proprie a ForzaTech). Octetul 84 conține numărul de octeți ai pixelilor.

| Cod | Format | Identificat ca |
|---|---|---|
| 0 | BC1, o jumătate de octet pe pixel | se decodează ca o bordură roșie și albă (zgomot sub BC4) |
| 9 | BC7, un octet pe pixel | se decodează ca o dală de teren pe care se vede circuitul |
| 13 | RGBA8, patru octeți pe pixel | simplu |
| altul | refuzat | "texture format N has not been identified; refusing to guess" |

Formatele au fost identificate decodând fișiere reale în toate modurile permise de dimensiunea încărcăturii. Octetul 47, pe care o versiune mai veche îl lua drept format, este 4 în fiecare textură eșantionată. Se decodează doar mip-ul de sus al unui fișier. Fiecare rezoluție este propria ei intrare, `<name>_<guid>_quality<n>.pb`, calitatea 1 cea mai mică, 5 cea mai mare. Pentru hărțile de teren, cele două cele mai mari sunt într-o arhivă diferită de restul. Decodarea trece prin decodorul BCn din Pillow, printr-un antet DDS generat.

## Fișiere de plasare (.pgeo) {#placement-files-pgeo}

Un fișier pentru fiecare categorie și fiecare celulă spațială: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Calea singură dă pătratul celulei și categoria, deci fișierele pot fi filtrate fără a fi deschise.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Cum a fost hotărât fiecare câmp:

| Câmp | Hotărât de |
|---|---|
| poziția este în virgulă fixă 16.16, nu o fracțiune din casetă | bariere consecutive sunt exact la 4,000 m una de alta (lungimea modelului) |
| mărime cu semn, nu complement față de doi | complementul față de doi punea coordonatele negative la zeci de kilometri de hartă; cu bitul 31 drept semn, fiecare înregistrare din fiecare categorie eșantionată cade în caseta fișierului ei |
| vectorii sunt axele proprii ale modelului | capătul fiecărei bariere cade pe începutul celei următoare: 93,5% la 5 cm, mediana 0,000 m |
| octetul 60 este varianta | cele cinci copii ale unui panou publicitar citesc 0, 2, 2, 3, 4, în timp ce fiecare barieră citește 0 |

Doar numele care se termină în `_3D` sunt înregistrări de model. Tabelul de variante de dinainte listează nume fără sufix, și citite ca înregistrări, acestea ajung la infinit. O înregistrare candidată este acceptată doar dacă numărul ei încape în fișier, iar instanțele cu numere nefinite sunt eliminate.

## Neimplementat {#not-implemented}

- Formate de vertex și de index altele decât cele de mai sus (refuzate).
- Formate de textură altele decât 0, 9, 13 (refuzate).
- Tangentele (citite și sărite, nefolosite).
- Straturile de material ale shaderului de teren. Textura solului este o interpretare a hărților de dale (vezi [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
