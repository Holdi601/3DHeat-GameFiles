---
title: "Unity"
nav_order: 4
lang: "is"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, búnt, net {#unity-serializedfile-bundles-meshes}

**Listar hluti og afkóðar net** úr Unity `SerializedFile` sniði 22 og
síðari (Unity 2020 til 6000), og opnar `UnityFS` búnt. Enginn Unity
brautarútflutningur er til.

Heimildir: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Skipanir: `identify` (ílát og búnt), `meshes` (aðeins ber ílát).

## Ílátið {#the-container}

Unity sendir borð sem raðað hlutarit: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` og eignabúnt. Hvert
þeirra geymir töflu af hlutum merktum flokkaauðkenni.

Hausinn er þar sem lestur fer hljóðlega úrskeiðis. Fyrstu sextán bætin eru fjórir
big-endian `uint32` sem eru geymdir vegna samhæfni. Í sniði 22 eru þrír þeirra núll,
og raunverulegu gildin fylgja á eftir því skrá getur farið yfir 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Seinni `metadata size` er `uint32` milli tveggja `int64`. Ef gert er ráð fyrir að allir þrír
séu 64 bita lendir útgáfustrengurinn fjórum bætum of seint. Hann afkóðast samt sem eitthvað
sem líkist streng og sendir allt á eftir honum afvega. Hausinn er big-endian.
Allt á eftir honum fylgir bætaröðunarbætinu (0, little-endian, í öllum
tölvuútgáfum).

Á eftir hausnum: útgáfustrengur vélarinnar, vettvangurinn, gerðatrésfáninn,
gerðataflan (flokkaauðkenni fyrir hverja gerð), hlutataflan (slóðarauðkenni, hliðrun, stærð, gerð),
og ytri tilvísanir (aðrar skrár sem bendill getur vísað í).

| Tilvik | Niðurstaða |
|---|---|
| snið 22-30 | lesið |
| snið 9-21 (fyrir Unity 2020) | hafnað: hliðranirnar eru í gamla hausnum, og engin skrá við höndina notaði hann |
| utan 9-30 | hafnað |
| gerðatré innbyggt (ritilsútgáfur) | hafnað: sendar útgáfur fella ekki inn slíkt, og ritilsleiðin er ekki útfærð |
| búnt sent þar sem ílát er vænst | hafnað, með tilvísun á búntalesarann |

Það er **enginn almennur afraðari**. Sendar útgáfur bera ekkert gerðatré, því
skemað er þýtt inn í spilarann, svo hver flokkur þarf að þáttast gegn
uppröðun sem er þekkt fyrir útgáfu hans. Aðeins `Mesh` er afkóðað. Aðrir flokkar eru tilgreindir
með nafni og fjölda (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`,
`Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; aðrir sem `class<id>`).

**Sannreynt** í mörgum uppsettum leikjum og milljónum hluta: hlutataflan
verður að flísa gagnakaflann nákvæmlega, án skörunar, ekkert nema fyllingu
til jöfnunar milli hluta, og síðasti hluturinn endar á síðasta bæti
skrárinnar. Misskilinn haus getur ekki gefið það. Prófið á uppsettum leikjum endurtekur það á
allt að sex `resources.assets` / `sharedassets0.assets` skrám sem finnast í
`*_Data` möppum.

## Búnt (`UnityFS`) {#bundles-unityfs}

Búnt er þjappað ílát af SerializedFiles. Blokkalistinn og
mappan eru líka þjöppuð. Aðferðin er í lægstu sex bitum flaggaorðs:
0 geymt, 1 LZMA (5 bæta haus Unity með stærðinni skeytta inn), 2 og 3 LZ4 /
LZ4HC. Snið 7 og síðari jafna hausinn við 16 bæti. Flaggið `0x80` setur
möppuna aftast í skrána. `UnityWeb`, `UnityRaw` og `UnityArchive`
(fyrir 5.3) eru þekkt en ekki lesin.

## Net {#meshes}

`read_mesh` afkóðar `Mesh` hlut í staðsetningar, normala, fyrsta UV-safn og
þríhyrninga, í þeirri röð sem Unity 2019+ skrifar þá: nafn, undirnet, blend shapes
(sleppt), bind poses og beinagögn (sleppt), þjöppunar- og lesanleikafánar, vísabiðminnið,
hnútarásir og hnútagögn, þjappaða netblokkin, staðbundni umlykjandi kassinn,
og streymisupplýsingar.

- **Ytri hnútar.** Mest af sendri rúmfræði býr í `.resS` skrá við hlið
  ílátsins. Verkfærið les hana úr möppu ílátsins (aðeins skráarheiti
  geymdu `archive:/...` slóðarinnar er notað). `.resS` sem vantar er villa, ekki
  tómt net.
- **Straumar og rásir.** Rásir segja hvaða straumur, hliðrun, snið og
  vídd hver eigind hefur. Straumar eru pakkaðir hver á eftir öðrum, hver fylltur
  í 16 bæti, svo upphaf straums er safnað saman úr skrefum á undan honum.
  Snið: float32, float16, unorm/snorm 8 og 16 (stöðluð), og venjulegar
  heiltölur.
- **Grindarform (topology).** Aðeins þríhyrningar (topology 0). Ræmur, ferhyrningar og línur er hafnað,
  því röng umbreyting lítur út eins og raunveruleg rúmfræði.
- **Þjöppuð net** (magngreind delta) er hafnað: „mesh '...' is stored
  compressed; that encoding is not implemented“.

### Sjálfsprófunin {#the-self-check}

Að lesa gagnabyggingu í rangri röð kastar ekki villu. Það gefur trúverðugar tölur.
Því er hvert afkóðað net prófað á móti **umlykjandi kassanum sem Unity geymdi fyrir það**,
reiknuðum af ritlinum úr raunverulegum hnútum. `aabb_matches()` stenst þegar
horn afkóðaða kassans eru innan 2% af stærð geymda kassans. `meshes` prentar `ok`
eða `BOUNDS DISAGREE` í hverri línu.

**Sannreynt:** net sem voru sýnatekin í nokkrum leikjum afkóðast með mörkum sem passa. Prófið á
uppsettum leikjum endurtekur athugunina á uppsettu ílátunum.

## Ekki útfært {#not-implemented}

- Snið fyrir 2020.
- Þjöppuð net.
- Allir flokkar aðrir en `Mesh`: enginn senugraf, hnitabreytingar eða efni, svo
  net eru í eigin staðbundnu rými.
- `meshes` á búnti. Búntalesarinn er til í Python
  (`UnityBundle.serialized_files()`), en skipunin tekur ber ílát.
