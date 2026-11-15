---
title: "Unity"
nav_order: 4
lang: "sq"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, paketat, rrjetat {#unity-serializedfile-bundles-meshes}

**Liston objektet dhe dekodon rrjetat** e formatit `SerializedFile` 22 të Unity
e më vonë (Unity 2020 deri 6000), dhe hap paketat `UnityFS`. Nuk ka eksport
kursi për Unity.

Burimet: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Komandat: `identify` (kontejnerët dhe paketat), `meshes` (vetëm kontejnerët e zhveshur).

## Kontejneri {#the-container}

Unity e dërgon një nivel si grafe objektesh të serializuara: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*`, dhe paketa asetesh. Secili
mban një tabelë objektesh të etiketuara me një id klase.

Koka është vendi ku leximi gabon në heshtje. Gjashtëmbëdhjetë bajtet e para janë katër
`uint32` big-endian të mbajtura për përputhshmëri. Në formatin 22, tri prej tyre janë zero,
dhe vlerat e vërteta pasojnë sepse një skedar mund të kalojë 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

`metadata size` i dytë është një `uint32` midis dy `int64`-ve. Supozimi që të tria
janë 64-bit e vë vargun e versionit katër bajte vonë. Prapë dekodohet në diçka
në formë vargu dhe çon gjithçka pas tij në rrugë të gabuar. Koka është big-endian.
Gjithçka pas saj ndjek bajtin e endianness (0, little-endian, në çdo
ndërtim për desktop).

Pas kokës: vargu i versionit të motorit, platforma, flamuri i pemës së llojeve, tabela e
llojeve (id e klasës për çdo lloj), tabela e objekteve (path id, ofseti, madhësia, lloji),
dhe të jashtmet (skedarë të tjerë ku mund të referojë një tregues).

| Rasti | Rezultati |
|---|---|
| formati 22-30 | lexohet |
| formati 9-21 (para Unity 2020) | refuzohet: ofsetet janë në kokën e vjetër, dhe asnjë skedar në dorë nuk e përdorte |
| jashtë 9-30 | refuzohet |
| pema e llojeve e ngulitur (ndërtimet e editorit) | refuzohet: ndërtimet e dërguara nuk e ngulitin një, dhe shtegu i editorit nuk është zbatuar |
| një paketë e dhënë ku pritet një kontejner | refuzohet, me një referim te lexuesi i paketave |

**Nuk ka deserializues të përgjithshëm**. Ndërtimet e dërguara nuk mbajnë pemë llojesh, sepse
skema është e përpiluar në lojtar, prandaj çdo klasë duhet parsuar kundrejt një
strukture të njohur për versionin e saj. Dekodohet vetëm `Mesh`. Klasat e tjera raportohen
me emër dhe numër (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`,
`Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; të tjerat si `class<id>`).

**Verifikuar** nëpër shumë lojëra të instaluara dhe miliona objekte: tabela e objekteve
duhet ta mbulojë saktësisht seksionin e të dhënave, pa mbivendosje, me asgjë tjetër përveç mbushjes
së përafrimit midis objekteve, dhe objekti i fundit duhet të mbarojë në bajtin e fundit të
skedarit. Një kokë e lexuar gabim nuk mund ta prodhojë këtë. Testi me lojë të instaluar e përsërit në
deri në gjashtë skedarë `resources.assets` / `sharedassets0.assets` të gjetur në
dosjet `*_Data`.

## Paketat (`UnityFS`) {#bundles-unityfs}

Një paketë është një kontejner i kompresuar skedarësh SerializedFile. Lista e blloqeve dhe
direktoria janë gjithashtu të kompresuara. Metoda është në gjashtë bitet e ulët të një fjale flamujsh:
0 stored, 1 LZMA (koka 5-bajtëshe e Unity me madhësinë të ndërfutur), 2 dhe 3 LZ4 /
LZ4HC. Formati 7 e më vonë e përafron kokën në 16 bajte. Flamuri `0x80` e vë
direktorinë në fund të skedarit. `UnityWeb`, `UnityRaw` dhe `UnityArchive`
(para 5.3) njihen por nuk lexohen.

## Rrjetat {#meshes}

`read_mesh` dekodon një objekt `Mesh` në pozicione, normale, grupin e parë UV dhe
trekëndësha, në rendin që i shkruan Unity 2019+: emri, nën-rrjetat, format e përzierjes
(kapërcehen), pozat e lidhjes dhe të dhënat e kockave (kapërcehen), flamujt e kompresimit dhe
leximit, buferi i indekseve, kanalet e kulmeve dhe të dhënat e kulmeve, blloku i rrjetës
së kompresuar, kutia kufizuese lokale, dhe informacioni i transmetimit.

- **Kulme të jashtme.** Pjesa më e madhe e gjeometrisë së dërguar jeton në një skedar `.resS` pranë
  kontejnerit. Mjeti e lexon nga dosja e kontejnerit (përdoret vetëm emri i skedarit të
  shtegut të ruajtur `archive:/...`). Një `.resS` që mungon është gabim, jo një
  rrjetë bosh.
- **Rrjedhat dhe kanalet.** Kanalet thonë cila rrjedhë, ofset, format dhe
  dimension ka çdo atribut. Rrjedhat paketohen njëra pas tjetrës, secila e mbushur
  në 16 bajte, prandaj fillimi i një rrjedhe grumbullohet nga hapat para saj.
  Format: float32, float16, unorm/snorm 8 dhe 16 (të normalizuara), dhe numra të plotë
  të thjeshtë.
- **Topologjia.** Vetëm trekëndësha (topologjia 0). Shiritat, katërkëndëshat dhe vijat refuzohen,
  sepse një konvertim i gabuar duket si gjeometri e vërtetë.
- **Rrjetat e kompresuara** (delta të kuantizuara) refuzohen: "mesh '...' is stored
  compressed; that encoding is not implemented".

### Vetëkontrolli {#the-self-check}

Leximi i një strukture në rend të gabuar nuk ngre përjashtim. Jep numra të besueshëm.
Prandaj çdo rrjetë e dekoduar kontrollohet kundrejt **kutisë kufizuese që Unity ruajti për të**,
e llogaritur nga editori nga kulmet e vërteta. `aabb_matches()` kalon kur
cepat e kutisë së dekoduar janë brenda 2% të madhësisë së kutisë së ruajtur. `meshes` printon `ok`
ose `BOUNDS DISAGREE` në çdo rresht.

**Verifikuar:** rrjetat e mostruara nëpër disa lojëra dekodohen me kufijtë që përputhen. Testi
me lojë të instaluar e përsërit kontrollin në kontejnerët e instaluar.

## Nuk është zbatuar {#not-implemented}

- Formatet para 2020.
- Rrjetat e kompresuara.
- Çdo klasë përveç `Mesh`: pa graf skene, transformime ose materiale, prandaj
  rrjetat janë në hapësirën e tyre lokale.
- `meshes` në një paketë. Lexuesi i paketave ekziston në Python
  (`UnityBundle.serialized_files()`), por komanda merr një kontejner të zhveshur.
