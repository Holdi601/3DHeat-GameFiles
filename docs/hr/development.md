---
title: Razvoj
nav_order: 14
lang: "hr"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

## Raspored {#layout}

```
heat3d_gamefiles/     paket: čitači, izvozi staza, naredbeni redak
heat3d_update/        provjera izdanja i ažuriranje (vidi Ažuriranja)
tests/                sintetski testovi, fiksture i testovi na instaliranim igrama
docs/                 ova dokumentacija (docs/wiki se generira iz nje)
VERSION               instalirana verzija, uspoređena s izdanjima na GitHubu
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Karta modula {#module-map}

| Modul | Što radi |
|---|---|
| `__main__.py` | pokreće provjeru ažuriranja, zatim `cli.main()` |
| `cli.py` | naredbe, `identify`, prosljeđivanje arhiva, pisač Forza staze |
| `lapinput.py` | svaki oblik kruga u pozicije; traženje u biblioteci FH Companiona |
| `corridor.py` | pojas s obje strane vožnje, kao raster od 4 m |
| `surfaces.py` | vrste tla, njihova imena dijelova i boje |
| `glb.py` | pisač `.glb` (dijelovi, normale, boje, teksture, kvantizacija) |
| `courseexport.py` | Forza: planarne UV koordinate pločice, podjela ceste i ruba, pečenje tla, podizanje dekala |
| `forzainstall.py` | Steam i Xbox biblioteke; Forza staza kojoj okvir pripada |
| `minizip.py` | ForzaTech `.minizip` arhive i njihovi popisi imena |
| `forzatech.py` | `.modelbin`: segmenti, međuspremnici, rasporedi, podmreže, materijali |
| `forzaterrain.py` | pločice terena po mjestu; klase površine |
| `forzatexture.py` | `.pb` uzorci; karte pločica; pečenje tla |
| `forzamaterial.py` | `AssetManifest.xml`; koje boje tekture koristi model; godišnja doba |
| `forzaplacement.py` | `.pgeo` postavljanja, razine modela, teksture, izrezi, zamjene zgrada, proračun |
| `beamng.py` | instalacija BeamNG-a, montirani sustav datoteka, scena, teren, materijali |
| `beamngcourse.py` | izvoz staze za BeamNG |
| `beamngshape.py` | `.cdae` sastavljeni oblici |
| `beamngcollada.py` | `.dae` rezerva |
| `acrally.py` | instalacija AC Rally, etape, postavljanje komponenti, volumen virtualne teksture |
| `acrallycourse.py` | izvoz staze za AC Rally: prilagodba okvira, tlo, postavljanje |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 kompajlirani paketi |
| `unversioned.py` | sheme neverzioniranih svojstava i čitač |
| `unrealmesh.py` | kompajlirane statičke mreže |
| `unrealtexture.py` | teksture i streaming virtualne teksture |
| `oodle.py` | pronalaženje i pozivanje instalirane Oodle biblioteke |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity spremnici, paketi, mreže |
| `frostbite.py` | Frostbite `.toc`, tablice odjeljaka, instalacijski paketi, lokacije dijelova, podaci |
| `frostbitebundle.py` | Frostbite unutarnji paketi, manifesti paketa, katalog razine, popis razina |
| `frostbiteebx.py` | Frostbite RIFF EBX particije bez biblioteke tipova |
| `frostbitemesh.py` | Frostbite MeshSet i njegovi dijelovi razina detalja |
| `frostbiteterrain.py` | Frostbite streaming stablo terena, stranice visina, mreža tla |
| `frostbitematerial.py` | Frostbite teksture (BC1/BC3/BC7 mipovi), skladišta blokova sjenčala, izbor mape boja |
| `frostbitedecals.py` | Frostbite dekali terena i pečenje tla |
| `frostbitenav.py` | Frostbite pločice navigacijske mreže: hodajuće površine vojnika |
| `frostbitelevel.py` | Frostbite statičke grupe modela, postavljanje, izvoz `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 komponente krajolika: visinske mape u mrežu tla (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition karte: popis, HLOD strukture, voda, izvoz `ue-map` |
| `enfusion.py` | Enfusion `.pak`, `.edds`, pločice terena, `resourceDatabase.rdb` |
| `enfusionworld.py` | svjetovi Arma Reforgera: `.ent` datoteke, kutije, izvoz `enfusion-world` |
| `forzacars.py` | svaki Forza automobil u niskom detalju u `.h3dcars` (`cars`) |

Svi moduli su na GitHubu u
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Pokretanje testova {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` postavlja `testpaths = tests` i `-q`. Dvije vrste testova su važne, iz
različitih razloga:

- **Sintetski testovi** grade arhive bajt po bajt i rade bilo gdje. Fiksiraju
  rasporede polja koji su jednom bili krivi: 64-bitnu bazu segmenta `.minizip`
  i njezino poravnanje, izlaz za veličinu bloka u pak-u, u32 vrijednost Unity
  zaglavlja između dva int64, indeks VPK-a `0x7FFF`, podijeljeni x Forza normale.
- **Testovi na instaliranim igrama** rade nad stvarnim datotekama kad je igra na
  računalu, a **preskaču se** (ne padaju) kad nije. Jedino oni hvataju raspored koji
  je ispravan za malu datoteku a pogrešan za veliku.

### Fiksture {#fixtures}

| Fikstura | Gradi |
|---|---|
| `tests/forza_fixtures.py` | `.minizip` arhive (s 64-bitnom bazom, popunjavanjem, miješanim kodecima), manifeste, `.modelbin` modele i teren, `.pb` uzorke |
| `tests/beamng_fixtures.py` | malu BeamNG instalaciju: `gameengine.zip`, `content`, jedan zip razine s terenom od 64 m, asfaltnu traku, dekal ceste, ogradu, prefab, stavku šume, more, materijale i `.cdae` oblike u dokumentiranom rasporedu |
| `tests/unreal_fixtures.py` | IoStore spremnik s direktorijem, zen paket, blok neverzioniranih svojstava |
| `tests/frostbite_fixtures.py` | Frostbite tablice, paketi, EBX particije, mreže i stranice terena, bajt po bajt |

### Datoteke testova {#test-files}

| Datoteka | Pokriva |
|---|---|
| `test_minizip.py` | čitanje natrag, 64-bitnu bazu, parne i neparne tablice paketa, odbijanja, popis imena |
| `test_forzatech.py` | tablicu i lanac segmenata, odbijanja; na instaliranom: lance i oznake stvarnih modela |
| `test_forza_geometry.py` | smještanje u svijet, raspored vrhova, odbijene formate, podmreže, normale i UV |
| `test_forzaterrain.py` | mrežu pločica (1023 naspram 512 m), izrezivanje, izdvajanje |
| `test_forzatexture.py` | zaglavlje uzorka, dekodiranje, polica tekstura, pečenje tla |
| `test_forzamaterial.py` | manifest, imena, hashevi materijala, izbor boje, godišnja doba |
| `test_forzaplacement.py` | zapis `.pgeo`, postavljanje primjeraka, razine, varijante, prozirne površine, cijeli okvir, proračun, boju zamjenskog mjesta, automatski proračun; na instaliranom: rubnici na tlu |
| `test_forzainstall.py` | pronalaženje igre, odabir staze |
| `test_courseexport.py` | UV pločica, plan dijelova, podizanje dekala |
| `test_course_cli.py` | cijele naredbe `course` i `courses` na sintetskoj stazi; `terrain --route` s oznakom redoslijeda bajtova i bez `bounds` |
| `test_archive_cli.py` | `identify`, `list` i `extract` na svakoj arhivi s čitačem (`.pak`, IoStore, `.vpk`, `.minizip` sa i bez imena, zip, `.cdae`, `.ter`); greške kao jedan red i izlazni kod: šifrirani pak, šifrirani spremnik, datoteka koja nije arhiva, loš `--key` |
| `test_corridor.py` | pojas, rezanje terena njime |
| `test_lapinput.py` | svaki oblik kruga, okvir, greške, traženje imena staze, koja je igra mapa |
| `test_surfaces.py` | koja imena odlučuju o površini, koja ne, imena dijelova |
| `test_glb.py` | datoteka je ispravna, čvorovi nose klasu, odbijanja, kvantizacija |
| `test_beamng.py` | oblici, razina, kategorije, pronalaženje razine iz kruga, staza, Collada rezerva; na instaliranom: `.cdae` naspram `.dae`, svaka razina se otvara |
| `test_acrally.py` | spremnici, paketi, svojstva, transformacije, prilagodba okvira, dijelovi postavljenih modela i proračun, virtualne teksture; na instaliranom: etape i pečena boja tla |
| `test_pak.py` | podnožje, unosi, izlaz za veličinu bloka, odbijanja; na instaliranom: pomaci i SHA-1 |
| `test_unity.py` | odbijanja; na instaliranom: tablica objekata pokriva datoteku, verzijski nizovi, granice mreža |
| `test_frostbite.py` | zaglavlja s potpisom naspram zamaskiranih, odbijanja, instalacijski paketi (dva paketa s istim brojem bloba); na instaliranom: svaka tablica, superpaketi, lanci odjeljaka, različiti ID-jevi, uzorkovani podaci iz pravog paketa |
| `test_frostbitelevel.py` | ID-jevi dijelova upareni s vlastitim lokacijama, unutarnji paketi, manifesti, MeshSet s odjeljkom sjene i UV-ovima, član grupe, konvencija transformacije, teren s dvije razine, izbor mape boja, segment teksture kojem nedostaju najveći mipovi, ponavljajući uzorkivač, zapisi dekala, dekal sastavljen po svojoj alfi, list dekala koji gubi od vlastite mape površine, navigacijske pločice (površine zadržane, veze izostavljene, odbijanja, detaljne mreže), ponavljajuće teksture zapisane sa svojim koordinatama, trokuti rezani gdje se tekstura ponavlja za pritegnuti izlaz, boja tla iz materijala površina, maske stranica (BC4 i nekomprimirane) postavljene na svoje četvrtine i odbijene kad se rubovi ne slažu, stranice mapa boja postavljene na četvrtine i pronađene nakon stranica maski, udaljenosti polja, palete i kanalne maske nikad uzete kao boja, nijansa bloka i siva mapa obojena njome, vrh palete u središtu svoje palete, mreža nagiba razvučena natrag bilinearno, preklop objekta crtan kroz njegovo razmatanje, varijacija čiji se blok ključa hashem i dosiže preko bliznakog bloka, slovni list položen četvrtim UV koordinatama preko površine na kojoj je naslikan, boja dekala čitana iz materijala, crtani redovi pista i tragovi guma, jednokanalne mape dekodirane, uništive mreže označene u dijelovima i dodacima, slojevi za izradu nacrta, kinematografske i rasvjetne mreže izostavljene i nečitan raspored mapa boja, mape izrezā i njihovi maskirani, dvostrani PNG materijali, pozadinske pločice imenovane po mreži; na instaliranom: dekali terena razine, katalog najveće razine, mreže unutar svojih granica, članovi grupa, vegetacija na dekodiranom terenu |
| `test_vpk.py` | direktorij, odbijanja, podijeljene arhive; na instaliranom: karte se otvaraju, CRC-ovi se podudaraju, navigacijska mreža |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, pločice terena i datoteke svjetova; izvoz `enfusion-world` |
| `test_forzacars.py` | datoteku `.h3dcars` koju piše naredba `cars` |
| `test_unreallevel.py` | Unreal 5 krajolici, HLOD strukture, voda; izvoz `ue-map` |

## Testovi na instaliranim igrama {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
traži igre za testove. `steam_common()` popisuje `steamapps\common` svake Steam
biblioteke (uključujući Steamove vlastite mape), a `installed(*globs)` vraća putanje
koje odgovaraju bilo kojem uzorku pod njima, rekurzivno tamo gdje uzorak ima `**`. Svaki
test odlučuje što mu treba:

| Test | Traži | Preskače se uz |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` s **nešifriranim** indeksom, do 4 | "no shipped pak on this machine" (nema isporučenog paka na ovom računalu) |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` u `*/*_Data` ili `*/*/*_Data` koje čitač prihvaća, do 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, do 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | staze iz biblioteke snimljenih krugova FH Companiona (početak i kraj unutar 50 m), s najviše krugova, koje `find_track` smješta; ili `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Pokrenite testove samo jedne igre ili usmjerite test Forza rubnika na jednu stazu:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Testovi na instaliranim igrama čitaju samo iz igara. Ništa ne pišu u mape igara.
Izlazi testova idu u privremene mape pytesta.

## Konvencije {#conventions}

- **Odbij umjesto da nagađaš.** Svaki čitač podiže vlastitu iznimku
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) s
  porukom koja kaže što je nađeno i zašto nije pročitano.
- **Provjeri prema samom formatu.** Hash, CRC, lanac pomaka, spremljeni omeđujući okvir,
  vožnja koja leži na tlu. Ne "nije se srušilo".
- **Nema ključeva, nema isporučenog zaštićenog koda.** Vidi
  [Pravila i licence](rules-and-licences.md).
- **Povjerljivi podaci ostaju vani.** Datoteke igara, izvozi, krugovi, snimke i
  snimke zaslona nikad ne idu u repozitorij. `.gitignore` ih isključuje po mapi i po
  vrsti. Testovi koriste sintetske podatke i instalirane igre, nikad sadržaj igara
  pohranjen u repozitoriju.
