---
title: "Source 2 VPK"
nav_order: 6
lang: "fi"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Listaa ja purkaa** Valven VPK-arkistot, versiot 1 ja 2, mukaan lukien jaetut arkistot ja data, joka on tallennettu hakemistotiedoston sisään. Jokainen merkintä voidaan tarkistaa omalla CRC:llään. Tämä on ainoa tässä käytetty säilömuoto, jonka valmistaja on dokumentoinut. Pelejä: Counter-Strike 2, Dota 2, Half-Life: Alyx ja muut Source 2 -pelit.

Lähde: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Komennot: `identify`, `list`, `extract`.

## Rakenne {#layout}

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

- Kolme sisäkkäistä silmukkaa, joista kukin päättyy tyhjään merkkijonoon, joten lukija, joka odottaa lukumäärää, ei löydä sellaista. Polut tallennetaan kerran ryhmää kohden ja kootaan uudelleen kaikista kolmesta osasta. Yksi väli tarkoittaa "ei kansiota" tai "ei päätettä".
- Jokainen tietue päättyy arvoon `0xFFFF`. Se tarkistetaan, joten lukija, joka on menettänyt paikkansa, pysähtyy heti ("the directory is not being read at the right offset" eli hakemistoa ei lueta oikeasta kohdasta).
- **Jaetut arkistot:** `pak01_dir.vpk` sisältää hakemiston, ja data on tiedostoissa `pak01_000.vpk`, `pak01_001.vpk`... jotka valitaan merkinnän arkistoindeksin mukaan.
- **Arkistoindeksi `0x7FFF`** tarkoittaa, että tavut ovat itse hakemistotiedostossa puun jälkeen. Jos lukija lukisi sen oikeana indeksinä, se etsisi tiedostoa `pak01_32767.vpk`.
- **Esilataus:** pienet tiedostot on tallennettu kokonaisina hakemistoon. Pituus 0 ei silloin ole virhe.

## Komennot {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` tulostaa version, merkintöjen määrän ja ensimmäisen `.nav`-tiedoston. `list` näyttää jokaisen merkinnän muodossa `stored`, koska VPK ei pakkaa. `extract` kirjoittaa tavut tarkistamatta CRC:tä. Pythonissa `VpkArchive(path).verify(name)` vertaa merkinnän tavuja hakemistoon tallennettuun CRC:hen.

## Navigointiverkko {#the-navigation-mesh}

Kartta toimittaa **navigointiverkkonsa** (`maps/<map>.nav`) käännetyn geometrian viereen. Pelaajien sijaintien lämpökarttaan se on selvästi hyödyllisempi kahdesta, koska navigointiverkko *on* kävelykelpoinen lattia, valmiiksi laskettuna ja tuhannesosan kokoisena. Asennetun pelin testi tarkistaa, että toimitetun kartan `.nav` alkaa Source-navigointiverkon tunnisteella `CE FA ED FE`.

## Todennettu {#verified}

Jokainen pelin mukana tulevista karttaarkistoista otetusta merkinnästä tuli takaisin tavu tavulta oikeana CRC:tä vasten, ja jokainen karttaarkisto jäsentyy. Asennetun pelin testit toistavat CRC-tarkistuksen 25 satunnaiselle merkinnälle kustakin enintään neljästä karttaarkistosta.

## Ei vielä toteutettu {#not-implemented}

- Source 2:n käännettyjen resurssien (`.vmdl_c`, `.vtex_c`) purku. Ne ovat omia palasiaan jaettuja binäärejä, samanlainen työ kuin Unreal- ja Frostbite-mallimuodot. Erillinen 3DHeat CS2 -työkalu käsittelee CS2-karttojen geometrian.
- CS2:n navigointiverkon purku. Sen muoto on versio 36 ja eroaa laajasti dokumentoidusta Source 1 -muodosta. Sen tavut eivät ole pakattuja vaan rakenteellisia (entropia 6.2, 31 % nollia), mutta vain 3 % sanoista lukee koordinaatteina. Asettelu ei siis ole ilmeinen, eikä sitä ole vielä selvitetty.
