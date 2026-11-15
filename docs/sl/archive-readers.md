---
title: "Bralniki arhivov"
nav_order: 9
lang: "sl"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Bralniki arhivov {#archive-readers}

**Kontejner** (ali arhiv) je ena velika datoteka, v katero igra spakira veliko datotek. **CRC** ali zgoščena vrednost (hash) je kratek prstni odtis nekaj bajtov: če se ujema, so bajti prebrani pravilno. **Omejujoči kvader** je najmanjši kvader okoli modela.

Pod ukazi so bralniki za kontejnerje, ki jih igre uporabljajo. Njihovi formati niso dokumentirani, razen Valvovega VPK in BeamNGove datoteke `.cdae`, zato "podprto" pomeni **preverjeno na pravih datotekah**, ne "ni se sesulo". Vsak bralnik se preveri z nečim, kar format zagotavlja: z zgoščeno vrednostjo, s CRC-jem, z verigo odmikov, ki se mora sklepati, ali s shranjenim omejujočim kvadrom. Kjer preverjanje ne uspe, bralnik zavrne z sporočilom in ne ugiba. Napačna mreža izgleda kot pravilna, dokler je nekdo ne postavi ob progo.

| Bralnik | Modul | Bere | Ne bere | Doseže ga |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | različice 8-12: kazalo, vnosi, bloki Zlib/Gzip/Oodle, AES s ključem, ki ga vnesete | različice pred 8, kazala samo s zgoščenimi potmi, vnosi v prelivnem seznamu, vsebina sredstev | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5 in novejši, preverjeno na v8), zen paketi, neimenovane lastnosti za nekaj razredov komponent, obdelane statične meshe, teksture in tokovne virtualne teksture | šifrirani kontejnerji, različični paketi, meshe samo za Nanite, lastnosti drugih razredov | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | bloki Oodle prek knjižnice, ki je že na računalniku | vse brez takšne knjižnice; nikoli ni priložena | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22 in novejši (Unity 2020 do 6000), `UnityFS` paketi, nestisnjeni meshi, vključno z `.resS` | formati pred letom 2020, vgrajena drevesa tipov, stisnjeni meshi, vsak razred razen `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | drevesa predmetov `.toc` in binarne tabele odsekov, namestitveni paketi, lokacije chunkov, vgrajeni paketi in njihovi manifesti, particije RIFF EBX, meshi MeshSet, višinska mreža terena, teksture BC1/BC3/BC7 in njihovi bloki senčilnikov, postavitev skupin statičnih modelov | tabele, zakrite z XOR, skoraj barvo tal v bližini in luknje, normalne mape, prosojnost razen izrezov | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | različici 1 in 2, razdeljeni arhivi, predhodno naloženi podatki, preverjanje CRC | prevedena sredstva (`.vmdl_c`, `.vtex_c`), format navigacijske mreže CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, shranjeno), geometrija `.modelbin`, vzorci `.pb` (BC1, BC7, RGBA), postavitve `.pgeo`, zgoščene vrednosti tekstur materialov | drugi formati oglišč in indeksov, drugi formati tekstur, plasti senčilnika terena | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` in `extract` (`.minizip`) |
| [Datoteke BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | sistem datotek iz zip arhivov, scenske datoteke JSON in TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiali | meshi s skeleti in odtisi, animirana zaporedja, proceduralno rastlinje na tleh | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` in `extract` (zip) |

## Pravila, ki jih upošteva vsak bralnik {#rules-every-reader-follows}

- **Ni shranjenih ključev, nobeden se ne izlušči.** Šifriran arhiv se odpre samo s ključem, ki ga podate (Unreal `.pak`, `--key`). Šifriran kontejner IoStore je zavrnjen. Nič ne išče ključa v izvršljivi datoteki in ne bere pomnilnika drugega procesa. Glejte [Pravila in licence](rules-and-licences.md).
- **Nobena lastniška koda ni priložena.** Oodle se naloži iz igre ali pogona, ki je že nameščen na računalniku.
- **Raje zavrni kot ugibaj.** Neznana različica, stiskalnik, format oglišč ali format teksture sproži določeno napako, na primer `texture format 42 has not been identified; refusing to guess`.
- **Samo za branje.** Noben bralnik ne piše v mapo igre. Izvozi gredo tja, kamor poveste.

## Kaj pomeni "preverjeno" {#what-verified-meant}

Številke preverjanja, navedene na teh straneh, so iz docstringov modulov. Izmerjene so bile na nameščenih igrah, medtem ko je bil vsak bralnik napisan. Sintetični testi (glejte [Razvoj](development.md)) zaklenejo postavitve polj. Testi na nameščenih igrah ponovijo nekatera preverjanja, kadar je igra na računalniku, sicer se preskočijo. Številke, ki jih test ne pokriva, od takrat niso bile ponovno preverjene.
