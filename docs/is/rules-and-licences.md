---
title: "Reglur og leyfi"
nav_order: 12
lang: "is"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Reglur og leyfi {#rules-and-licences}

Þrjár reglur móta allt verkfærið. Fullur texti:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Engir lyklar: enginn sendur með, enginn endurheimtur {#1-no-keys-none-shipped-none-recovered}

**Það les ílát.** Að þátta skjalasafnssnið er venjuleg skráameðhöndlun, og FModel,
UModel og AssetRipper hafa gert það fyrir opnum tjöldum árum saman.

**Línan sem skiptir máli er dulkóðun, og hún er dregin inni í verkfærinu.**

- **Engir lyklar sendir með.** Enginn lykill er í kóðanum eða gögnunum.
- **Engin lyklaendurheimt.** Ekkert leitar að lykli í keyrsluskrá, og ekkert les
  minni annars ferlis.
- **Lykill sem þú átt, eða ekkert.** Dulkóðað Unreal `.pak` opnast aðeins með
  `--key <hex>` (í Python, `PakArchive(path, aes_key=...)`). `pak.py` hefur enga kóðaleið
  sem útvegar lykil. Dulkóðuðu IoStore íláti er hafnað með öllu.
- **Hulning er heldur ekki útfærð.** XOR-hulin töflur Frostbite
  geyma lykil sinn í skránni sjálfri, svo þær eru hulning frekar en aðgangsstýring.
  Þær eru samt greindar og hafnað, því engin skrá við höndina notar það
  form og ekkert væri til að prófa útfærslu á móti. Lyklaður pakki Assetto
  Corsa EVO er afþakkaður af sömu ástæðu og lyklareglan er til.
- **Dulkóðaðar skrár haldast lokaðar.** Upphafsskráakerfi Battlefield 6, sem
  geymir gerðasafn leiksins, er dulkóðað og er ekki lesið. Borðsútflutningurinn
  vinnur úr skránum sem eru ekki dulkóðaðar, og leggur út gerðirnar tvær sem hann
  þarf úr gögnunum.
- **Ekkert sprautar sig inn í leikjaferli.** Mælingar koma úr straumum sem leikir
  gefa sjálfir út, og upptaka notar opinber skjáupptökuviðmót (í hinum
  3DHeat verkfærunum). Innspýting í leik með svindlvörn stofnar reikningi
  þess sem keyrir hana í hættu.

Öll skjalasöfn sem hafa verið prófuð hingað til eru ódulkóðuð.

## 2. Þínar eigin skrár {#your-own-files}

Verkfærið les leikjaskrárnar sem eru **uppsettar á tölvunni þinni**. Það sækir aldrei
leikjaefni.

Ekkert úr leik fylgir með: ekkert leikjaefni, enginn leikjakóði, engin DLL-söfn. Það sem
verkfærið flytur út er skrifað á þinn disk og hvergi annað.

3DHeat GameFiles tengist engum útgefanda leikja og nýtur ekki stuðnings þeirra.
Leikirnir og tengd nöfn og vörumerki tilheyra eigendum sínum. Rétthafar: stofnið
verkbeiðni (issue) á
[github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) -
við svörum fljótt og fjarlægjum hvað sem er sé þess óskað.

## 3. Úttakið er ekki til endurdreifingar {#3-output-is-not-for-redistribution}

Það sem kemur út er rúmfræði fyrir **rýmissamhengi**: jörðin, vegurinn og það sem
stendur við hlið hans, grisjað niður í hámark, svo hægt sé að greina hringi á staðnum. Það er
það minnsta sem skjalasafn geymir, og er samt efni útgefanda leiksins.

- Geymdu útfluttar `.glb` skrár, og áferðirnar í þeim, fyrir eigin greiningu.
- Ekki gefa út, deila eða selja útfluttar brautir, borð, líkön eða áferðir.
- `.gitignore` geymslunnar heldur leikjaskrám, útflutningi, hringjum og upptökum utan
  útgáfustýringar eftir möppu og skráargerð (`*.glb`, `*.pak`, `*.minizip`,
  `*.utoc`, `*.png`, `*.lap.json` og fleiri).

## Oodle er fundið, ekki sent með {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, nú Epic) er séreign og hefur enga endurdreifanlega smíð.
`oo2core_*.dll` er með leyfi fyrir vörunni sem sendir það með. `oodle.py` hleður því
safni sem er þegar á tölvunni frekar en að bera eitt með sér. Þetta er
fyrirkomulagið sem leyfið gerir ráð fyrir, og það sama og FModel og UModel nota.
Sjá [Oodle](reader-oodle.md).

## Sniðin sjálf {#the-formats-themselves}

- `.pak`, IoStore, `SerializedFile` frá Unity, `.toc` frá Frostbite og snið
  ForzaTech eru óskjalfest. Enginn lesaranna hér er leiddur af frumkóða annars verkefnis. Fyrir
  Frostbite gáfu opinberar lýsingar á eldri útgáfum (Frosty módunarverkfærin, ein
  sniðsathugasemd um Need for Speed Heat, GDC fyrirlestur) reitanöfn og kort af
  því sem leita átti að. Enginn kóði var tekinn; hver hliðrun var mæld á skránum
  (sjá [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Útdregin borð eru til eigin nota. Verkfærið skrifar þau á diskinn þinn og
  hvergi annars staðar; ekki gefa þau út.
- BeamNG gefur út `.cdae` uppröðun sína, og lesarinn fylgir henni.
- Valve skjalfestir VPK.
- Bökuð eigindagögn Unreal 5 þurfa eigindalista hvers flokks. Listarnir í
  `unversioned.py` eru **aðeins nöfn og gerðir**, staðreyndir um sniðið eins og
  samvirknikortaskrá geymir. Þeir voru leiddir af Unreal Engine hausunum sem Epic gerir aðgengilega
  hverjum sem hefur tengdan reikning, og prófaðir á móti sendu gögnunum.
  Enginn frumkóði vélarinnar er innifalinn eða nauðsynlegur.

## Leyfi þessa verkfæris {#this-tools-licence}

Allt sem er skrifað fyrir þessa geymslu er undir **MIT leyfinu**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
notaðu það, breyttu því, sendu það áfram, í viðskiptaskyni eða ekki.

Þriðju aðila pakkar, allir með frjálslynd leyfi, svo útflytjandinn ber engar
eigin takmarkanir:

| Pakki | Leyfi | Notað fyrir |
|---|---|---|
| numpy | BSD-3-Clause | afkóðun neta |
| cryptography | Apache-2.0 / BSD-3-Clause | aðeins skjalasöfn sem þú átt lykil að |
| lz4 | BSD-3-Clause | Forza skjalasöfn, sum Unity búnt, IoStore LZ4 blokkir |
| Pillow | MIT-CMU (HPND) | blokkþjappaðar áferðir, JPEG úttak |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | fáein zstd-þjöppuð `.cdae`, Frostbite zstd blokkir |
| pytest | MIT | aðeins þróun |

Leyfin voru lesin úr lýsigögnum pakkanna í september 2026. Þar sem skilmálar
íhlutar breyttust eftir það gildir frumkóðinn.
