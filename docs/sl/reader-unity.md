---
title: "Unity"
nav_order: 4
lang: "sl"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, paketi, meshi {#unity-serializedfile-bundles-meshes}

**Izpiše predmete in dekodira meshe** formata `SerializedFile` Unity 22 in novejšega (Unity 2020 do 6000) ter odpre pakete `UnityFS`. Izvoza proge za Unity ni.

Viri: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Ukazi: `identify` (kontejnerji in paketi), `meshes` (samo goli kontejnerji).

## Kontejner {#the-container}

Unity pošilja nivo kot serializirane grafe predmetov: `globalgamemanagers`, `sharedassets*.assets`, `resources.assets`, `level*` in sredstvene pakete. Vsak ima tabelo predmetov, označenih z ID-jem razreda.

Glava je mesto, kjer se branje tiho pokvari. Prvih šestnajst bajtov so štirje big-endian `uint32`, ohranjeni zaradi združljivosti. V formatu 22 so trije od njih ničle, pravi podatki pa sledijo, ker lahko datoteka preseže 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Drugi `metadata size` je `uint32` med dvema `int64`. Če bi se vsi trije brali kot 64-bitni, bi se niz različice premaknil za štiri bajte. Še vedno se dekodira v nekaj, kar je videti kot niz, in vse za njim pošlje narobe. Glava je big-endian. Vse za njo sledi bajtu endianness (0, little-endian, pri vseh namiznih gradnjah).

Za glavo: niz različice motorja, platforma, zastavica drevesa tipov, tabela tipov (ID razreda na tip), tabela predmetov (path id, odmik, velikost, tip) in zunanji viri (druge datoteke, na katere lahko kazalec kaže).

| Primer | Rezultat |
|---|---|
| format 22-30 | prebran |
| format 9-21 (pred Unity 2020) | zavrnjen: odmiki so v stari glavi, nobena datoteka, ki jo imamo, je ne uporablja |
| zunaj 9-30 | zavrnjen |
| vgrajeno drevo tipov (gradnje urejevalnika) | zavrnjen: gradnje za igranje drevesa ne vgrajujejo, pot urejevalnika ni implementirana |
| paket podan tam, kjer se pričakuje kontejner | zavrnjen, s kazalom na bralnik paketov |

**Splošnega deserializatorja ni.** Gradnje za igranje nimajo drevesa tipov, ker je shema vgrajena v predvajalnik, zato je treba vsak razred razčleniti glede na postavitev, znano za njegovo različico. Dekodiran je samo `Mesh`. Drugi razredi so prijavljeni po imenu in številu (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; drugi kot `class<id>`).

**Preverjeno** na mnogo nameščenih igrah in milijonih predmetov: tabela predmetov mora natanko prekrivati podatkovni del, brez prekrivanj, med predmeti ni nič razen poravnalnega polnila, zadnji predmet pa se konča na zadnjem bajtu datoteke. Napačno branje glave tega ne more proizvesti. Test na nameščeni igri to ponovi na do šestih datotekah `resources.assets` / `sharedassets0.assets` v mapah `*_Data`.

## Paketi (`UnityFS`) {#bundles-unityfs}

Paket je stisnjen vsebnik datotek SerializedFile. Seznam blokov in imenik sta prav tako stisnjena. Metoda je v nižjih šestih bitih besede zastavic: 0 shranjeno, 1 LZMA (Unityjeva 5-bajtna glava z vstavljeno velikostjo), 2 in 3 LZ4 / LZ4HC. Format 7 in novejši poravna glavo na 16 bajtov. Zastavica `0x80` postavi imenik na konec datoteke. `UnityWeb`, `UnityRaw` in `UnityArchive` (pred 5.3) so prepoznani, a niso prebrani.

## Meshi {#meshes}

`read_mesh` dekodira predmet `Mesh` v položaje, normale, prvi nabor UV in trikotnike, v vrstnem redu, v katerem jih Unity 2019+ zapisuje: ime, podmeshi, oblike mešanja (preskočeno), bind poses in podatki o kosteh (preskočeno), zastavice stiskanja in branja, medpomnilnik indeksov, kanali oglišč in podatki oglišč, stisnjen blok meša, lokalna omejujoča škatla in podatki o pretakanju.

- **Zunanja oglišča.** Večina objavljene geometrije je v datoteki `.resS` ob kontejnerju. Orodje jo prebere iz mape kontejnerja (uporabi se samo ime datoteke shranjene poti `archive:/...`). Manjkajoča `.resS` je napaka, ne prazen mesh.
- **Tokovi in kanali.** Kanali povedo, kateri tok, odmik, format in dimenzijo ima vsak atribut. Tokovi so zloženi drug za drugim, vsak poravnan na 16 bajtov, zato se začetek toka sešteva iz korakov pred njim. Formati: float32, float16, unorm/snorm 8 in 16 (normalizirani) ter navadna cela števila.
- **Topologija.** Samo trikotniki (topologija 0). Trakovi, štirikotniki in črte so zavrnjeni, ker je napačna pretvorba videti kot prava geometrija.
- **Stisnjeni meshi** (kvantizirane razlike) so zavrnjeni: "mesh '...' is stored compressed; that encoding is not implemented".

### Samopreverjanje {#the-self-check}

Branje strukture v napačnem vrstnem redu ne sproži napake. Dajo pa vrednosti, ki so videti verjetne. Zato se vsak dekodiran mesh preveri proti **omejujoči škatli, ki jo je Unity shranil zanj**, izračunani v urejevalniku iz pravih oglišč. `aabb_matches()` uspe, kadar so vogali dekodirane škatle znotraj 2 % velikosti shranjene škatle. `meshes` izpiše `ok` ali `BOUNDS DISAGREE` pri vsaki vrstici.

**Preverjeno:** vzorčeni meshi čez več iger se dekodirajo s skladnimi mejami. Test na nameščeni igri ponovi preverjanje na nameščenih kontejnerjih.

## Ni implementirano {#not-implemented}

- Formati pred letom 2020.
- Stisnjeni meshi.
- Vsak razred razen `Mesh`: ni grafa scene, transformacij ali materialov, zato so meshi v svojem lastnem lokalnem prostoru.
- `meshes` na paketu. Bralnik paketov obstaja v Pythonu (`UnityBundle.serialized_files()`), ukaz pa vzame goli kontejner.
