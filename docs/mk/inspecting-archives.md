---
title: "Преглед на архиви"
nav_order: 3
lang: "mk"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Преглед на архиви: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Играта ги пакува своите датотеки во големи кутии наречени **архиви**. Овие команди
ја гледаат етикетата на кутијата, наведуваат што има во неа и вадат една работа.

Пред да извезувате нешто од непозната игра, погледнете што испорачува.
Овие четири глаголи читаат датотека и ви кажуваат што е и што содржи; не
пишуваат ништо освен единствениот запис што го барате од `extract`.

![identify, list и extract извршени на мал zip](../assets/img/inspect-archives.svg)

*Извршување на синтетички zip сместен како ниво од BeamNG.drive.*

## Чекор по чекор {#step-by-step}

1. **Прашајте што е датотеката.** `identify` ги чита бајтите, а не наставката:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Го именува форматот (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle или
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` или
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), неговата верзија, колку записи
   содржи и дали е шифриран.

2. **Наведете што има внатре.** `list` печати по една линија за запис: големина, компресија,
   патека. Стеснете со `--filter`, ограничете со `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Извадете еден запис.** `extract` пишува еден запис (во папката во која сте,
   освен ако `--out` не каже каде), по патеката што ја испечатил `list`
   (или `#12`, по број, во `.minizip` без имиња):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` ги наведува и проверува мрежите во `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Опции {#options}

| Глагол | Опција | Значење |
|---|---|---|
| `identify` | `<file>` | која било датотека |
| `list` | `<archive>` | `.pak`, `.utoc` (или `.ucas` покрај него), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | само патеки што содржат TEXT |
| | `--limit N` | најмногу N линии |
| | `--key HEX` | AES-256 клуч (64 хексадецимални цифри) што веќе го имате; само шифриран `.pak` го бара |
| `extract` | `<archive> <path>` | архивата и патеката на записот како што ја печати `list` |
| | `--out FILE` | каде да се запише (основно: името на датотеката на записот) |
| | `--key HEX` | како за `list` |
| `meshes` | `<file>`, `--limit N` | Unity `SerializedFile`; најмногу N мрежи |

Алатката не испорачува клучеви и не враќа ниеден: шифрирана архива се отвора само со
клуч што вие го давате. Датотека што не може да ја прочита се одбива во една линија со излезен код 1.
Секој глагол и излезен код е на страницата [Команди](commands.md); како се чита секој формат
е под [Читачи на архиви](archive-readers.md).
