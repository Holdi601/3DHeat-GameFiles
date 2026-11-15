---
title: "Source 2 `.vpk`"
nav_order: 6
lang: "hr"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Popisuje i izvlači** Valveove VPK arhive, verzije 1 i 2, uključujući podijeljene arhive i podatke pohranjene unutar datoteke direktorija. Svaki unos može se provjeriti vlastitim CRC-om. Ovo je jedini format spremnika ovdje čiji ga proizvođač dokumentira. Igre: Counter-Strike 2, Dota 2, Half-Life: Alyx i druge na Source 2.

Izvor: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Naredbe: `identify`, `list`, `extract`.

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

- Tri ugniježđene petlje, svaka završava praznim nizom, pa čitač koji očekuje broj ne nalazi ništa. Putanje se pohranjuju jednom po grupi i sastavljaju se iz sva tri dijela. Jedan razmak znači „nema mape” ili „nema ekstenzije”.
- Svaki zapis završava s `0xFFFF`. To se provjerava, pa čitač koji je izgubio mjesto staje odmah (poruka alata: „the directory is not being read at the right offset”).
- **Podijeljene arhive:** `pak01_dir.vpk` sadrži direktorij, a podaci su u `pak01_000.vpk`, `pak01_001.vpk`... i biraju se prema indeksu arhive unosa.
- **Indeks arhive `0x7FFF`** znači da su bajtovi u samoj datoteci direktorija, nakon stabla. Čitanje toga kao pravog indeksa šalje čitač da traži `pak01_32767.vpk`.
- **Predučitavanje:** male datoteke pohranjene su cijele u direktoriju. Duljina 0 tada nije greška.

## Naredbe {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` ispisuje verziju, broj unosa i prvu `.nav` datoteku. `list` prikazuje svaki unos kao `stored`, jer VPK ne komprimira. `extract` zapisuje bajtove bez provjere CRC-a. U Pythonu `VpkArchive(path).verify(name)` uspoređuje bajtove unosa s CRC-om koji je zabilježio direktorij.

## Navigacijska mreža {#the-navigation-mesh}

Karta isporučuje svoju **navigacijsku mrežu** (`maps/<map>.nav`) uz kompiliranu geometriju. Za toplinsku kartu pozicija igrača to je korisnije od ta dva s velikom razlikom, jer je nav mreža *upravo* prohodna podloga, već izračunata, i tisućiti dio veličine. Test na instaliranoj igri provjerava da `.nav` isporučene karte počinje Source navigacijskom magijom `CE FA ED FE`.

## Provjereno {#verified}

Svaki unos uzorkovan kroz isporučene arhive karata jedne igre vratio se bajt-točno u odnosu na svoj CRC, a svaka arhiva karte se parsira.
Testovi na instaliranoj igri ponavljaju CRC provjeru na 25 slučajnih unosa iz svake od do četiri arhive karata.

## Nije implementirano {#not-implemented}

- Dekodiranje Source 2 kompiliranih sredstava (`.vmdl_c`, `.vtex_c`). To su binarne datoteke po dijelovima, vlastiti posao, isti kao za Unreal i Frostbite formate mreža. Zasebni alat 3DHeat CS2 obrađuje geometriju karte CS2.
- Dekodiranje CS2 navigacijske mreže. Njezin format je verzija 36 i razlikuje se od široko dokumentiranog Source 1 formata. Bajtovi su strukturirani, a ne komprimirani (entropija 6.2, 31% nula), ali samo 3% riječi čita se kao koordinate, pa raspored nije očit i još nije razriješen.
