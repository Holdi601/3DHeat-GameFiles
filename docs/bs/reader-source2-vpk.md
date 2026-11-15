---
title: "Source 2 VPK"
nav_order: 6
lang: "bs"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Ispisuje i izdvaja** Valveove VPK arhive, verzije 1 i 2, uključujući podijeljene
arhive i podatke pohranjene unutar datoteke direktorija. Svaki unos može se provjeriti
prema vlastitom CRC-u. Ovo je jedini format kontejnera ovdje čiji proizvođač
ga dokumentira. Igre: Counter-Strike 2, Dota 2, Half-Life: Alyx i druge na Source 2.

Izvor: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Komande: `identify`, `list`, `extract`.

## Raspored {#layout}

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

- Tri ugniježđene petlje, svaka završava praznim stringom, pa čitač koji očekuje
  broj ne nalazi nijedan. Putanje se pohranjuju jednom po grupi i sastavljaju iz sva
  tri dijela. Jedan razmak znači „nema foldera“ ili „nema ekstenzije“.
- Svaki zapis završava s `0xFFFF`. To se provjerava, pa čitač koji je izgubio
  mjesto staje odmah („the directory is not being read at the right offset“).
- **Podijeljene arhive:** `pak01_dir.vpk` drži direktorij, a podaci su u
  `pak01_000.vpk`, `pak01_001.vpk`... koje bira indeks arhive unosa.
- **Indeks arhive `0x7FFF`** znači da su bajtovi u samoj datoteci direktorija,
  iza stabla. Ako se pročita kao pravi indeks, čitač traži
  `pak01_32767.vpk`.
- **Preload:** male datoteke pohranjene su cijele u direktoriju. Dužina 0 tada
  nije greška.

## Komande {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` ispisuje verziju, broj unosa i prvu `.nav` datoteku. `list`
prikazuje svaki unos kao `stored`, jer VPK ne kompresira. `extract` upisuje
bajtove bez provjere CRC-a. U Pythonu, `VpkArchive(path).verify(name)`
uspoređuje bajtove unosa s CRC-om koji je direktorij zabilježio.

## Navigacijska mreža {#the-navigation-mesh}

Mapa isporučuje svoju **navigacijsku mrežu** (`maps/<map>.nav`) pored kompajlirane
geometrije. Za toplotnu mapu pozicija igrača ona je od ta dva daleko korisnija,
jer nav mreža *jeste* prohodni pod, već izračunat i hiljadu puta manji.
Test na instaliranoj igri provjerava da `.nav` isporučene mape počinje
Source navigacijskim magic-om `CE FA ED FE`.

## Provjereno {#verified}

Svaki unos uzorkovan iz arhiva mapa jedne igre vratio se bajt po bajt tačan
prema svom CRC-u, i svaka arhiva mape se parsira.
Testovi na instaliranoj igri ponavljaju provjeru CRC-a na 25 nasumičnih unosa iz svake od
najviše četiri arhive mapa.

## Nije implementirano {#not-implemented}

- Dekodiranje kompajliranih Source 2 sadržaja (`.vmdl_c`, `.vtex_c`). To su
  vlastiti binarni formati u dijelovima, isti posao kao Unreal i Frostbite
  formati mreža. Zasebni 3DHeat CS2 alat obrađuje geometriju CS2 mapa.
- Dekodiranje CS2 nav mreže. Njen format je verzija 36 i razlikuje se od široko
  dokumentiranog Source 1 formata. Njeni bajtovi su strukturirani, a ne kompresirani
  (entropija 6,2, 31% nula), ali samo 3% njenih riječi čita se kao koordinate, pa
  raspored nije očit i još nije razriješen.
