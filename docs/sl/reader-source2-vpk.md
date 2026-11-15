---
title: "Source 2 `.vpk`"
nav_order: 6
lang: "sl"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Izpisuje in izvlači** arhive VPK podjetja Valve, različici 1 in 2, vključno z razdeljenimi arhivi in podatki, shranjenimi znotraj datoteke imenika. Vsak vnos je mogoče preveriti z njegovim lastnim CRC. To je edini tu uporabljen vsebniški format, ki ga njegov proizvajalec dokumentira. Igre: Counter-Strike 2, Dota 2, Half-Life: Alyx in druge na Source 2.

Vir: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Ukazi: `identify`, `list`, `extract`.

## Postavitev {#layout}

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

- Tri ugnezdene zanke, vsaka se konča s praznim nizom, zato bralnik, ki pričakuje število, ne najde nobenega. Poti so shranjene enkrat na skupino in se iz vseh treh delov sestavijo znova. En sam presledek pomeni "brez mape" ali "brez končnice".
- Vsak zapis se konča z `0xFFFF`. To se preverja, zato se bralnik, ki je izgubil svoje mesto, takoj ustavi ("the directory is not being read at the right offset").
- **Razdeljeni arhivi:** `pak01_dir.vpk` hrani imenik, podatki pa so v `pak01_000.vpk`, `pak01_001.vpk` … izbrani po indeksu arhiva vnosa.
- **Indeks arhiva `0x7FFF`** pomeni, da so bajti v samem datoteki imenika, za drevesom. Če bi ga bralnik vzel kot pravi indeks, bi iskal `pak01_32767.vpk`.
- **Preload:** majhne datoteke so shranjene v celoti v imeniku. Dolžina 0 tedaj ni napaka.

## Ukazi {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` izpiše različico, število vnosov in prvo datoteko `.nav`. `list` prikaže vsak vnos kot `stored`, ker VPK ne stiska. `extract` zapiše bajte brez preverjanja CRC. V Pythonu `VpkArchive(path).verify(name)` primerja bajte vnosa s CRC, ki ga je zabeležil imenik.

## Navigacijska mreža {#the-navigation-mesh}

Zemljevid v igri ima svojo **navigacijsko mrežo** (`maps/<map>.nav`) poleg kompiliranega prostora. Za toplotni zemljevid položajev igralcev je veliko bolj uporabna od obeh, ker je navigacijska mreža *sama* hoden tla, že izračunana in tisočkrat manjša. Installed-game test preveri, da se `.nav` objavljenega zemljevida začne z navigacijskim magičnim zaporedjem Source `CE FA ED FE`.

## Preverjeno {#verified}

Vsak vnos, vzorčen po objavljenih arhivih zemljevidov ene igre, je prišel bajt za bajtom enak svojemu CRC, vsak arhiv zemljevida pa se razčleni.
Testi z nameščeno igro ponovijo preverjanje CRC na 25 naključnih vnosih iz vsakega od do štirih arhivov zemljevidov.

## Ni izvedeno {#not-implemented}

- Dekodiranje prevedenih sredstev Source 2 (`.vmdl_c`, `.vtex_c`). To so razdeljene binarne datoteke svoje vrste, enako delo kot pri formatih mrež Unreal in Frostbite. Ločeno orodje 3DHeat za CS2 obravnava geometrijo zemljevidov CS2.
- Dekodiranje navigacijske mreže CS2. Njen format je različica 36 in se razlikuje od splošno dokumentiranega formata Source 1. Njeni bajti so strukturirani, ne stisnjeni (entropija 6,2, 31 % ničel), vendar le 3 % njenih besed bere kot koordinate, zato postavitev ni očitna in še ni razvozlana.
