---
title: Unreal 5 IoStore
nav_order: 2
lang: "fi"
source: reader-unreal-iostore.md
source_hash: "a71af3169c83"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 toimittaa suurimman osan sisällöstään **IoStore**-konteissa: `.utoc`-sisällysluettelo
ja `.ucas`-datat, joihin se viittaa. `.pak` on yhä olemassa, mutta se sisältää vain vähän muuta
kuin alatunnisteen. Tässä olevat lukijat etenevät kontista geometriaan ja pikseleihin, niin pitkälle
kuin rata tarvitsee. Ne rakennettiin ja tarkistettiin Assetto Corsa Rallyllä (Unreal 5.6.1,
muokattu), ja niihin päästään [Assetto Corsa Rally](course-assetto-corsa-rally.md)-radan viennin
kautta. Lisäksi `identify`, `list` ja `extract` ottavat `.utoc`-tiedoston (tai sen vieressä olevan
`.ucas`-tiedoston): tiedostot, jotka sen hakemisto nimeää, polkuineen kiinnityspisteen alla. Kontti
ilman hakemistoindeksiä ei nimeä tiedostoja, eikä sitä listata.

| Kerros | Moduuli |
|---|---|
| kontit ja varasto | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| käännetyt "zen"-paketit | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| versiottomat ominaisuustiedot | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| staattiset mallit | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| tekstuurit ja virtuaalitekstuurit | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Kontit (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Sisällysluettelo, versio 8 (Unreal 5.6), little-endian:

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

- Versiot vanhempia kuin 5 hylätään. Vain versio 8 on tarkistettu oikeilla tiedostoilla.
- **Salatut kontit hylätään**: "<file> is encrypted. This tool holds no keys and recovers none."
  IoStoreen ei voi antaa avainta.
- Lohkomenetelmät: tallentamaton, `oodle` ([Oodle](reader-oodle.md)-sivun kautta), `zlib`, `lz4`.
  Muu hylätään.
- Ensimmäisen jälkeiset osiot ovat tiedostossa `<name>_s<n>.ucas`.

**Varasto** avaa jokaisen `.utoc`-tiedoston pelin `Paks`-kansiossa ja indeksoi jokaisen paketin
polun kirjainkoosta välittämättä. Kontit, jotka eivät aukea, ohitetaan. `global.utoc` antaa
skriptiobjektit (C++-luokat). Paketin massadata (`.ubulk`) löytyy palana, jolla on sama tunniste ja
tyyppi `BULK_DATA`, siinä kontissa, joka sen pitää.

Tarkistettu: jokainen asennetun pelin kontti ja jokainen niissä oleva paketin polku.

## Zen-paketit {#zen-packages}

Käännetty paketti on otsikko (nimet, tuonnit, viennit, vientipaketit, riippuvuustaulukot,
tuodut paketin nimet), jota seuraa kunkin viennin sarjallistettu data. Objektit viittaavat toisiinsa
64-bittisellä `FPackageObjectIndex`-luvulla, jonka ylimmät kaksi bittiä kertovat, mitä se on: tämän
paketin vienti, skriptiobjekti, tuonti toisesta paketista (mikä paketti, ja vienti polun hashin
mukaan) tai tyhjä.

- Yhteenvedon asettelu muuttui versiossa 5.3 (riippuvuuspaketit ja tuodut paketin nimet) ja uudelleen
  versiossa 5.6 (kaksi lisäsiirtymää). Molemmat asettelut kokeillaan, ja se, jonka nimitaulu jäsentyy,
  pidetään, joten versiota ei tarvitse tuntea.
- **Versioidut** (käsittelemättömän tyylin) paketit hylätään.
- Tuodut paketin nimet kantavat numeron. Paketti `_Terrain`, numerolla 1, on tiedosto `_Terrain_0`.
- `/Game/...`-nimet kartoitetaan projektin `Content`-kansioon varastossa.
- Viittauksia seurataan pakettien yli vastaamalla viennin julkisen hashin kanssa.

Tarkistettu: jokainen vaiheen jokainen solu aukeaa.

## Versiottomat ominaisuudet {#unversioned-properties}

Käännetyt Unreal 5 -viennit eivät nimeä ominaisuuksiaan. Vienti alkaa otsikolla, jossa on
ajoja: "ohita niin monta paikkaa, sitten niin monta läsnä olevaa", ja maski kertoo, mitkä läsnä
olevista ovat nollia eivätkä kanna tavuja. Arvot seuraavat luokan ominaisuusjärjestyksessä. Tämän
lukemiseen tarvitaan jokaisen luokan **skeema**: sen ominaisuuslista täsmälleen siinä järjestyksessä,
jonka moottori sen rakentaa (omat ominaisuudet ensin, sitten vanhemman, yksi paikka per staattisen
taulukon alkio, vain editorin ominaisuudet pois jätettynä).

Skeemat on upotettu radan tarvitsemille luokille:

| Luokka | Ketju |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | ISM-ketjut (olemassa, mutta radan vienti ei käytä niitä, koska tämä versio järjesti ne uudelleen) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Ne kattavat myös näiden pitämät rakenteet (`FBodyInstance`, törmäysvasteet ja muut). Arvotyypit
luetaan koodauksen mukaan: kiinteän kokoiset luvut ja vektorit (`FVector`, `FRotator` double-
lukuina, `FTransform` ...), `FName`, enumit (yksi tavu), objektiviitteet (`i32`-paketti-indeksi),
pehmeät objektipolut, taulukot, sisäkkäiset rakenteet ja monikanavaiset delegaatit (ohitetaan).

Skeemat ovat **vain ominaisuuksien nimet ja tyypit**, johdettu Unreal Engine 5.6.1 -otsikoista
(jotka Epic tarjoaa jokaiselle linkitetyn tilin omistajalle). Mitään moottorin koodia ei ole mukana.
Tässä versiossa on **kaksi lisäpaikkaa `UPrimitiveComponent`issa** otsikoihin verrattuna ja **yksi
lisäpaikka virtuaalitekstuurivolyymissa**, jotka löydettiin datasta ja merkitään `(unknown)`.
Arvo näissä paikoissa on virhe, ei arvaus. Paikka skeeman lopun jälkeen tai tuntematon tyyppi
nostaa `PropertyError`-virheen.

Tarkistettu: jokainen staattisen mallin ja näkymän komponentti jokaisesta vaiheesta dekoodautuu,
ja jokainen päättyy täsmälleen luokkansa kiinteään natiiviin häntään. Pelipäivitys voi siirtää
paikkoja. Lukija nostaa silloin virheen, ja rata ilmoittaa, kuinka monta komponenttia epäonnistui.

## Staattiset mallit {#static-meshes}

`UStaticMesh`-objekti on sen ominaisuudet ja niiden jälkeen natiivi data. Ominaisuuksia ei tarvita
geometriaan, eikä niitä lueta. Natiivi osa löytyy kiinteästä alustasta: nolla-GUID-lippu, kaksi tavua
nauhalippuja, `bCooked = 1` ja mallin oman `BodySetup`-viennin indeksi. Se luetaan siinä järjestyksessä,
jonka `UStaticMesh::Serialize` ja `FStaticMeshRenderData::Serialize` kirjoittavat **käännetylle,
ei-Naniten mallille**:

- enintään 16 yksityiskohtatasoa, joista kullakin on osat (materiaali, ensimmäinen indeksi, kolmiomäärä),
  rajat ja kun **sisäistetty**: sijaintipuskuri (float32 x 3), tangentit, UV:t (kaikki kanavat, puoli- tai
  täysi tarkkuus), värit ja indeksipuskuri (16- tai 32-bittinen);
- seuraava (käännetyt ja vain syvyyden indeksipuskurit, säteenseurantadata, aluepainotetut otantajat)
  ohitetaan, jotta päästään seuraavaan tasoon.

Taso, jota ei ole tallennettu sisäisesti, päättää listan. Mallilla, jolla ei ole yhtään, on hylätty.
Sijainnit ovat Unrealin: senttimetrit, X eteenpäin, Y oikealle, Z ylös.

Tarkistettu: lähes jokainen otannan malli dekoodautuu (loput ovat luurankomalleja), ja tielaatan
dekoodattu laajuus vastaa sen tallentamia rajoja.

## Tekstuurit {#textures}

`Texture2D`-objekti on sen ominaisuudet ja sen jälkeen käännetty alustadata: pikselimuodon nimi,
koko ja mip-tasojen taulukko, joka osoittaa paketin **massadatakarttaan** (siirtymä, koko, liput;
objektin sisällä, kun lippu `0x40` on asetettu, muuten `.ubulk`-tiedostossa). Alustadata löydetään
sen omasta muodosta, ei ohittamalla ominaisuuksia, joten tekstuuriluokan ominaisuusasettelulla ei ole
merkitystä. Ensimmäinen mip, joka ei ole pyydettyä kokoa suurempi, dekoodataan.

| Unreal-muoto | Dekoodataan muodoksi |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bittinen RGBA |
| `PF_G8` | 8-bittinen harmaa |

Tarkistettu: 4096 px:n DXT5-satelliittikuva, jonka kolmetoista tasoa ovat täsmälleen massamerkintöjen kokoja.

## Suoratoistettavat virtuaalitekstuurit {#streaming-virtual-textures}

Käännetty `VirtualTexture2D` on neliön muotoisia laattoja reunuksineen, tasoittain, osoitettuna
**Morton-koodilla** (x parillisissa biteissä), tallennettuna paketin massadatan paloihin. Asettelu
luetaan siten kuin `FVirtualTextureBuiltData::Serialize` sen kirjoittaa Unreal 5.6:ssa: kerrokset,
laattakoko, reunus, mip-tasoittaiset laattaosoitetaulukot, kerrosmuodot ja pala *n* on massamerkintä *n*.
Alue tekstuurista kootaan laatta kerrallaan, reunukset poistettuina, tasolta, jonka resoluutio on
lähimpänä haluttua kokoa. Vain ensimmäinen kerros luetaan, ja vain yllä olevissa muodoissa.

Tarkistettu: virtuaalitekstuurin palan laatat on tiliin tavulleen.
