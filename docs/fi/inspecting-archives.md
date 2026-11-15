---
title: "Arkistojen tarkastelu"
nav_order: 3
lang: "fi"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Arkistojen tarkastelu: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Peli pakkaa tiedostonsa isoihin laatikoihin, joita kutsutaan **arkistoiksi**. Nämä komennot katsovat laatikon tarraa, listaavat sen sisällön ja ottavat yhden asian ulos.

Ennen kuin viet mitään tuntemattomasta pelistä, katso, mitä se sisältää. Nämä neljä komentoa lukevat tiedoston ja kertovat, mikä se on ja mitä se pitää sisällään. Ne eivät kirjoita mitään muuta kuin yhden merkinnän, jonka pyydät `extract`-komennolla.

![identify, list ja extract ajettuna pienellä zip-tiedostolla](../assets/img/inspect-archives.svg)

*Ajo synteettisellä zip-tiedostolla, joka on järjestetty BeamNG.drive-kentän mukaan.*

## Vaihe vaiheelta {#step-by-step}

1. **Kysy, mikä tiedosto on.** `identify` lukee tavut, ei tiedostopäätettä:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Se kertoo muodon (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity-paketti tai `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` tai `.modelbin`, BeamNG `.cdae`/`.ter`, zip), sen version, kuinka monta merkintää siinä on ja onko se salattu.

2. **Listaa, mitä sisällä on.** `list` tulostaa yhden rivin per merkintä: koko, pakkaus ja polku. Kavenna tulostetta `--filter`-valinnalla ja rajoita sitä `--limit`-valinnalla:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Ota yksi merkintä ulos.** `extract` kirjoittaa yhden merkinnän (siihen kansioon, jossa olet, ellei `--out` kerro muuta), sen polun mukaan, jonka `list` tulosti (tai `#12` numerolla `.minizip`-tiedostossa, jossa ei ole nimiä):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` listaa ja tarkistaa `SerializedFile`-tiedoston verkot:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Valinnat {#options}

| Komento | Valinta | Merkitys |
|---|---|---|
| `identify` | `<file>` | mikä tahansa tiedosto |
| `list` | `<archive>` | `.pak`, `.utoc` (tai sen vieressä oleva `.ucas`), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | vain polut, joissa on TEXT |
| | `--limit N` | enintään N riviä |
| | `--key HEX` | AES-256-avain (64 heksadesimaalinumeroa), joka sinulla jo on; vain salattu `.pak` tarvitsee sen |
| `extract` | `<archive> <path>` | arkisto ja merkinnän polku sellaisena kuin `list` sen tulostaa |
| | `--out FILE` | mihin tiedosto kirjoitetaan (oletus: merkinnän tiedostonimi) |
| | `--key HEX` | kuten `list`-komennossa |
| `meshes` | `<file>`, `--limit N` | Unity-`SerializedFile`; enintään N verkkoa |

Työkalu ei sisällä avaimia eikä palauta niitä: salattu arkisto aukeaa vain avaimella, jonka annat. Tiedosto, jota se ei voi lukea, hylätään yhdellä rivillä ja poistumiskoodilla 1. Jokainen komento ja poistumiskoodi on sivulla [Komennot](commands.md). Miten kukin muoto luetaan, on kohdassa [Arkistolukijat](archive-readers.md).
