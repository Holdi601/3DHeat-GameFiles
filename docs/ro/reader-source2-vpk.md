---
title: "VPK din Source 2"
nav_order: 6
lang: "ro"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# `.vpk` din Source 2 {#source-2-vpk}

**Listează și extrage** arhivele VPK ale Valve, versiunile 1 și 2, inclusiv arhivele împărțite și datele stocate în fișierul de director. Fiecare intrare poate fi verificată față de propriul ei CRC. Este singurul format de container de aici a cărui producător îl documentează. Jocuri: Counter-Strike 2, Dota 2, Half-Life: Alyx și altele de pe Source 2.

Sursa: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Comenzi: `identify`, `list`, `extract`.

## Structura {#layout}

```
u32 magic 0x55AA1234, u32 version (1 or 2), u32 tree size
  (version 2: 16 more header bytes; header 12 or 28 bytes)
directory tree:
  extension        "vmdl_c", then "vtex_c", ..., then ""
    path           "maps/example_map", then ""
      file name    "world_layer0", then ""
        u32 crc, u16 preload size, u16 archive index, u32 offset, u32 length, u16 0xFFFF
        [preload bytes]
```

- Trei bucle imbricate, fiecare încheiată cu un șir gol, așa că un cititor care se așteaptă la un număr nu găsește niciunul. Căile sunt stocate o dată per grup și reasamblate din toate cele trei părți. Un singur spațiu înseamnă „niciun folder” sau „nicio extensie”.
- Fiecare înregistrare se încheie cu `0xFFFF`. Aceasta este verificată, deci un cititor care și-a pierdut locul se oprește imediat („the directory is not being read at the right offset”).
- **Arhive împărțite:** `pak01_dir.vpk` conține directorul, iar datele se află în `pak01_000.vpk`, `pak01_001.vpk`... alese după indexul arhivei intrării.
- **Indexul arhivei `0x7FFF`** înseamnă că octeții sunt în fișierul de director, după arbore. Dacă este citit ca index real, un cititor caută `pak01_32767.vpk`.
- **Preîncărcare:** fișierele mici sunt stocate întregi în director. O lungime de 0 nu este atunci o eroare.

## Comenzi {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` afișează versiunea, numărul de intrări și primul fișier `.nav`. `list` arată fiecare intrare ca `stored`, pentru că VPK nu comprimă. `extract` scrie octeții fără să verifice CRC-ul. În Python, `VpkArchive(path).verify(name)` compară octeții unei intrări cu CRC-ul pe care l-a notat directorul.

## Plasa de navigare {#the-navigation-mesh}

O hartă își livrează **plasa de navigare** (`maps/<map>.nav`) alături de geometria compilată. Pentru o hartă termică a pozițiilor jucătorilor, aceasta este mult mai utilă dintre cele două, pentru că plasa de navigare *este* podeaua pe care se poate merge, deja calculată și de o mie de ori mai mică. Testul pe jocul instalat verifică faptul că `.nav` al unei hărți livrate începe cu magicul de navigare Source `CE FA ED FE`.

## Verificat {#verified}

Fiecare intrare eșantionată din arhivele de hărți livrate ale unui joc a ieșit identică, octet cu octet, față de CRC-ul ei, iar fiecare arhivă de hartă se parsează.
Testele pe jocul instalat repetă verificarea CRC pe 25 de intrări aleatoare din fiecare arhivă de hartă, din până la patru arhive.

## Neimplementat {#not-implemented}

- Decodarea activelor compilate Source 2 (`.vmdl_c`, `.vtex_c`). Acestea sunt binare fragmentate proprii, același tip de muncă precum formatele de mesh Unreal și Frostbite. Instrumentul CS2 separat 3DHeat se ocupă de geometria hărților CS2.
- Decodarea plasei de navigare CS2. Formatul său este versiunea 36 și diferă de cel Source 1 documentat pe scară largă. Octeții săi sunt structurați, nu comprimați (entropie 6.2, 31% zerouri), dar doar 3% din cuvinte se citesc ca coordonate, deci structura nu este cea evidentă și nu a fost încă descifrată.
