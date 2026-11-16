---
title: "Rregullat dhe licencat"
nav_order: 12
lang: "sq"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Rregullat dhe licencat {#rules-and-licences}

Tri rregulla e formësojnë gjithë mjetin. Teksti i plotë:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Pa çelësa: asnjë i dërguar, asnjë i rikuperuar {#no-keys-none-shipped-none-recovered}

**Lexon kontejnerë.** Parsimi i një formati arkivi është trajtim i zakonshëm skedarësh, dhe
FModel, UModel dhe AssetRipper e kanë bërë hapur për vite me radhë.

**Vija që ka rëndësi është enkriptimi, dhe vizatohet brenda mjetit.**

- **Pa çelësa të përfshirë.** Nuk ka çelës në kod ose në të dhëna.
- **Pa rikuperim çelësash.** Asgjë nuk kërkon çelës brenda një ekzekutuesi, dhe asgjë nuk lexon
  memorien e procesit tjetër.
- **Një çelës që e ke, ose asgjë.** Një `.pak` Unreal i enkriptuar hapet vetëm me
  `--key <hex>` (në Python, `PakArchive(path, aes_key=...)`). `pak.py` nuk ka asnjë shteg
  kodi që merr një çelës. Një kontejner IoStore i enkriptuar refuzohet krejt.
- **As turbullimi (obfuscation) nuk është zbatuar.** Tabelat e turbulluara me XOR të Frostbite
  e mbajnë çelësin e tyre në vetë skedarin, prandaj janë turbullim dhe jo kontroll
  aksesi. Ato prapë zbulohen dhe refuzohen, sepse asnjë skedar në dorë nuk e përdor atë
  formë dhe nuk do të kishte çfarë të kontrollohej një zbatim. Paketa me çelës e Assetto
  Corsa EVO refuzohet për të njëjtën arsye për të cilën ekziston rregulli i çelësave.
- **Skedarët e enkriptuar mbeten të mbyllur.** Sistemi fillestar i skedarëve i Battlefield 6, që
  mban bibliotekën e llojeve të lojës, është i enkriptuar dhe nuk lexohet. Eksporti i nivelit
  punon me skedarët që nuk janë të enkriptuar, dhe i vendos dy llojet që i duhen
  nga të dhënat.
- **Asgjë nuk injektohet në proces loje.** Telemetria vjen nga burime që lojërat
  i publikojnë vetë, dhe kapja përdor API publike të regjistrimit të ekranit (në mjetet e tjera
  3DHeat). Injektimi në një titull me anti-cheat rrezikon llogarinë e
  atij që e ekzekuton.

Çdo arkiv i testuar deri tani është i paenkriptuar.

## 2. Skedarët e tu {#your-own-files}

Mjeti lexon skedarët e lojës **të instaluar në kompjuterin tënd**. Nuk shkarkon kurrë
përmbajtje loje.

Asgjë nga një lojë nuk shpërndahet bashkë me të: asnjë përmbajtje e lojës, asnjë kod i lojës,
asnjë DLL. Ajo që eksporton shkruhet në diskun tënd dhe askund tjetër.

3DHeat GameFiles nuk është i lidhur me asnjë botues lojërash dhe nuk miratohet prej tyre.
Lojërat dhe emrat e markat tregtare përkatëse u përkasin pronarëve të tyre. Mbajtësit e të
drejtave: hapni një issue te
[github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) -
përgjigjemi shpejt dhe heqim gjithçka me kërkesë.

## 3. Dalja nuk është për rishpërndarje {#output-is-not-for-redistribution}

Ajo që del është gjeometri për **kontekst hapësinor**: toka, rruga dhe ajo që
qëndron pranë saj, e zvogëluar në një buxhet, që xhirot të analizohen në vend. Është
më pak nga ajo që mban një arkiv, dhe prapë është përmbajtje e botuesit të lojës.

- Mbaji skedarët `.glb` të eksportuar, dhe teksturat brenda tyre, për analizën tënde.
- Mos botoni, ndani ose shisni kurse, nivele, modele ose tekstura të eksportuara.
- `.gitignore` i repozitorit i mban skedarët e lojës, eksportet, xhirot dhe regjistrimet jashtë
  kontrollit të versioneve sipas dosjes dhe llojit të skedarit (`*.glb`, `*.pak`, `*.minizip`,
  `*.utoc`, `*.png`, `*.lap.json` e më shumë).

## Oodle gjendet, nuk përfshihet {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, tani Epic) është pronësor dhe nuk ka ndërtim të rishpërndashëm.
`oo2core_*.dll` është licencuar për produktin që e dërgon. Prandaj `oodle.py`
ngarkon një bibliotekë që ndodhet tashmë në kompjuter në vend që të mbajë një. Ky është
rregullimi që e parashikon licenca, i njëjti që përdorin FModel dhe UModel.
Shih [Oodle](reader-oodle.md).

## Vetë formatet {#the-formats-themselves}

- `.pak`, IoStore, `SerializedFile` i Unity, `.toc` i Frostbite dhe formatet e ForzaTech
  janë të padokumentuara. Asnjë nga lexuesit këtu nuk rrjedh nga kodi burimor i një projekti tjetër. Për
  Frostbite, përshkrimet publike të versioneve më të vjetra (mjetet e modifikimit Frosty, një shënim formati
  Need for Speed Heat, një bisedë GDC) dhanë emra fushash dhe një hartë se
  çfarë të kërkohet. Nuk u mor kod; çdo ofset u mat në skedarët
  (shih [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Nivelet e nxjerra janë për përdorimin tënd. Mjeti i shkruan në diskun tënd dhe
  askund tjetër; mos i botoni.
- BeamNG e boton strukturën e `.cdae`, dhe lexuesi e ndjek.
- Valve e dokumenton VPK.
- Të dhënat e gatuara të vetive të Unreal 5 kërkojnë listën e vetive të çdo klase. Listat në
  `unversioned.py` janë **vetëm emra dhe lloje**, fakte për formatin si ato që mban një
  skedar hartash ndërveprueshmërie. U nxorën nga titujt e Unreal Engine
  që Epic i vë në dispozicion të këdo me një llogari të lidhur, dhe u kontrolluan
  kundrejt të dhënave të dërguara. Nuk përfshihet dhe nuk kërkohet kod burimor motori.

## Licenca e këtij mjeti {#this-tools-licence}

Gjithçka e shkruar për këtë repozitor është nën **licencën MIT**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
përdore, ndryshoje, shpërndaje, komercialisht ose jo.

Paketat e palëve të treta, të gjitha lejuese, që eksportuesi të mos mbartë kufizim
të vetin:

| Paketa | Licenca | Përdoret për |
|---|---|---|
| numpy | BSD-3-Clause | dekodimin e rrjetave |
| cryptography | Apache-2.0 / BSD-3-Clause | vetëm arkivat për të cilat ke çelës |
| lz4 | BSD-3-Clause | arkivat Forza, disa paketa Unity, blloqet LZ4 të IoStore |
| Pillow | MIT-CMU (HPND) | tekstura të kompresuara në blloqe, dalje JPEG |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | pak `.cdae` të kompresuara me zstd, blloqet zstd të Frostbite |
| pytest | MIT | vetëm zhvillimi |

Licencat u lexuan nga metadata e paketave në shtator 2026. Ku kushtet e një
përbërësi ndryshuan pas kësaj, burimi është ai që vlen.
