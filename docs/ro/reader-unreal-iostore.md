---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "ro"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 livrează cea mai mare parte a conținutului în containere **IoStore**: un tabel de conținut `.utoc` și datele `.ucas` pe care le indexează. Un `.pak` mai există, dar conține puțin mai mult decât un footer. Cititoarele de aici merg de la container până la geometrie și pixeli, cât are nevoie un circuit. Au fost construite și verificate pe Assetto Corsa Rally (Unreal 5.6.1, modificat) și se ating prin exportul de circuit [Assetto Corsa Rally](course-assetto-corsa-rally.md), iar `identify`, `list` și `extract` iau un `.utoc` (sau `.ucas` de lângă el): fișierele pe care le numește directorul lui, după calea lor sub punctul de montare. Un container fără index de directoare nu numește niciun fișier și nu este listat.

| Strat | Modul |
|---|---|
| containere și depozitul | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| pachete compilate „zen” | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| date de proprietăți neversionate | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| mesh-uri statice | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| texturi și texturi virtuale | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Containere (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Tabelul de conținut, versiunea 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Versiunile mai vechi de 5 sunt refuzate. Doar versiunea 8 a fost verificată pe fișiere reale.
- **Containerele criptate sunt refuzate**: "<file> is encrypted. This tool holds no keys and recovers none." Pentru IoStore nu se poate transmite nicio cheie.
- Metode de bloc: stocat, `oodle` (prin [Oodle](reader-oodle.md)), `zlib`, `lz4`. Orice altceva este refuzat.
- Partițiile de după prima trăiesc în `<name>_s<n>.ucas`.

**Depozitul** deschide fiecare `.utoc` din folderul `Paks` al jocului și indexează fiecare cale de pachet, fără a ține cont de majuscule. Containerele care nu se deschid sunt sărite. `global.utoc` oferă obiectele de script (clasele C++). Datele în bloc ale unui pachet (`.ubulk`) se găsesc ca bucata cu același id și tipul `BULK_DATA`, în orice container o conține.

Verificat: fiecare container al jocului instalat și fiecare cale de pachet din el.

## Pachete zen {#zen-packages}

Un pachet compilat este un antet (nume, importuri, exporturi, pachete de export, tabele de dependențe, numele pachetelor importate), urmat de datele serializate ale fiecărui export. Obiectele se referă unul la altul printr-un `FPackageObjectIndex` de 64 de biți ale cărui doi biți de sus spun ce este: un export al acestui pachet, un obiect de script, un import dintr-un alt pachet (care pachet, și exportul după un hash al căii lui) sau nul.

- Layout-ul rezumatului s-a schimbat în 5.3 (pachete de dependențe și nume de pachete importate) și din nou în 5.6 (două decalaje în plus). Ambele layout-uri sunt încercate, iar cel a cărui tabelă de nume se parsează este păstrat, deci versiunea nu trebuie cunoscută.
- Pachetele **versionate** (în stil neconstruit) sunt refuzate.
- Numele pachetelor importate poartă un număr. Un pachet `_Terrain` numerotat 1 este fișierul `_Terrain_0`.
- Numele `/Game/...` se mapează pe folderul `Content` al proiectului în depozit.
- Referințele sunt urmărite peste pachete prin potrivirea hash-ului public al exportului.

Verificat: fiecare celulă a fiecărei etape se deschide.

## Proprietăți neversionate {#unversioned-properties}

Exporturile Unreal 5 compilate nu își numesc proprietățile. Un export începe cu un antet de serii, „sari peste atâtea sloturi, apoi atâtea prezente”, și o mască ce spune care dintre cele prezente sunt zero și nu poartă octeți. Valorile urmează în ordinea proprietăților clasei. Pentru a le citi este nevoie de **schema** fiecărei clase: lista ei de proprietăți, exact în ordinea în care o construiește motorul (întâi proprietățile proprii, apoi ale părintelui, câte un slot pentru fiecare element al unui tablou static, fără proprietățile doar pentru editor).

Schemele sunt încorporate pentru clasele de care are nevoie un circuit:

| Clasă | Lanțul |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | lanțurile ISM (prezente, dar nefolosite de exportul de circuit, pentru că această versiune le-a rearanjat) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Acoperă și structurile pe care acestea le țin (`FBodyInstance`, răspunsurile de coliziune și altele). Tipurile de valoare sunt citite după codare: numere și vectori de dimensiune fixă (`FVector`, `FRotator` ca double, `FTransform`...), `FName`, enumerări (un octet), referințe la obiecte (index de pachet `i32`), căi de obiect soft, tablouri, structuri imbricate și delegări multicast (sărite).

Schemele conțin **doar nume și tipuri de proprietăți**, derivate din anteturile Unreal Engine 5.6.1 (pe care Epic le pune la dispoziția oricui are un cont legat). Nu este inclus cod de motor. Această versiune are **două sloturi în plus în `UPrimitiveComponent`** față de antete și **unul în plus în volumul de textură virtuală**, găsite din date și marcate `(unknown)`. O valoare prezentă în unul dintre aceste sloturi este o eroare, nu o ghicire. Un slot dincolo de sfârșitul unei scheme, sau un tip necunoscut, ridică `PropertyError`.

Verificat: fiecare componentă de mesh static și de scenă a fiecărei etape se decodează, terminând fiecare exact la coada nativă fixă a clasei sale. O actualizare a jocului poate muta sloturile. Cititorul ridică atunci o eroare, iar circuitul raportează câte componente au eșuat.

## Mesh-uri statice {#static-meshes}

Un export `UStaticMesh` este proprietățile lui urmate de date native. Proprietățile nu sunt necesare pentru geometrie și nu sunt citite. Partea nativă se găsește după începutul ei fix: un flag GUID zero, doi octeți de steaguri de benzi, `bCooked = 1` și indexul exportului `BodySetup` propriu al mesh-ului. Apoi se citește în ordinea în care `UStaticMesh::Serialize` și `FStaticMeshRenderData::Serialize` o scriu pentru un mesh **compilat, non-Nanite**:

- până la 16 niveluri de detaliu, fiecare cu secțiunile lui (material, primul index, numărul de triunghiuri), limitele și, când este **inline**: bufferul de poziții (float32 x 3), tangentele, UV-urile (toate canalele, precizie pe jumătate sau completă), culorile și bufferul de index (16 sau 32 de biți);
- ce urmează (bufferele de index inversate și doar pentru adâncime, datele de ray tracing, eșantionatorii ponderați pe arie) este sărit pentru a ajunge la nivelul următor.

Un nivel care nu este stocat inline încheie lista. Un mesh fără niciunul este refuzat. Pozițiile sunt ale Unreal: centimetri, X înainte, Y la dreapta, Z în sus.

Verificat: aproape fiecare mesh eșantionat se decodează (restul sunt cu schelet), iar extinderea decodată a unei dale de drum se potrivește cu limitele pe care le stochează.

## Texturi {#textures}

Un export `Texture2D` este proprietățile lui, apoi datele lui de platformă compilate: numele formatului de pixeli, dimensiunea și un tabel de niveluri de mip, fiecare indicând în **harta de date în bloc** a pachetului (decalaj, dimensiune, steaguri; inline în export când steagul `0x40` este setat, altfel în `.ubulk`). Datele de platformă se găsesc după propria lor formă, nu sărind peste proprietăți, deci layout-ul proprietăților clasei de textură nu contează. Primul mip nu mai mare decât dimensiunea cerută este decodat.

| Format Unreal | Decodat ca |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | RGBA pe 8 biți |
| `PF_G8` | gri pe 8 biți |

Verificat: o imagine satelit DXT5 de 4096 px ale cărei treisprezece niveluri sunt exact dimensiunile intrărilor în bloc.

## Texturi virtuale de streaming {#streaming-virtual-textures}

O `VirtualTexture2D` coaptă este un set de dale pătrate cu bordură, pentru fiecare nivel de detaliu, adresate printr-un **cod Morton** (x pe biții pari), stocate în bucăți ale datelor în bloc ale pachetului. Layout-ul este citit cum îl scrie `FVirtualTextureBuiltData::Serialize` în Unreal 5.6: straturile, dimensiunea dalei, bordura, tabelele de adrese ale dalelor pe fiecare mip, formatele straturilor, iar bucata *n* ca intrarea *n* în bloc. O regiune a texturii este asamblată dală cu dală, cu bordurile scoase, de la nivelul a cărui rezoluție este cea mai apropiată de dimensiunea dorită. Doar primul strat este citit, și doar în formatele de mai sus.

Verificat: dalele unei bucăți de textură virtuală sunt contabilizate până la octet.
