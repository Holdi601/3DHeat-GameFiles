---
title: Преглед на архиви
nav_order: 3
lang: "bg"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Преглед на архиви: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Игрите събират файловете си в големи кутии, наречени **архиви**. Тези команди поглеждат етикета на кутия, изброяват какво има в нея и вадят едно нещо оттам.

Преди да експортирате нещо от непозната игра, вижте какво съдържа. Тези четири команди четат файл и ви казват какво е и какво съдържа; не записват нищо, освен единствения запис, който поискате от `extract`.

![identify, list и extract работят върху малък zip](../assets/img/inspect-archives.svg)

*Пример върху синтетичен zip, наредено като ниво на BeamNG.drive.*

## Стъпка по стъпка {#step-by-step}

1. **Попитайте какъв е файлът.** `identify` чете байтовете, а не разширението:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Той назовава формата (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle или `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` или `.modelbin`, BeamNG `.cdae`/`.ter`, zip), версията му, колко записа съдържа и дали е шифрован.

2. **Изброете какво има вътре.** `list` показва по един ред за всеки запис: размер, компресия, път. Стеснете с `--filter`, ограничете с `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Извадете един запис.** `extract` записва един запис (в папката, в която сте, освен ако `--out` не посочи друго), по пътя, както го показва `list` (или `#12`, с номер, при `.minizip` без имена):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` изброява и проверява мрежите в `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Опции {#options}

| Команда | Опция | Значение |
|---|---|---|
| `identify` | `<file>` | всеки файл |
| `list` | `<archive>` | `.pak`, `.utoc` (или `.ucas` до него), `.vpk`, `.minizip`, zip |
| | `--filter ТЕКСТ` | само пътища, които съдържат ТЕКСТ |
| | `--limit N` | най-много N реда |
| | `--key HEX` | AES-256 ключ (64 шестнадесетични цифри), който вече имате; нужен е само на шифриран `.pak` |
| `extract` | `<archive> <path>` | архивът и пътят на записа, както го показва `list` |
| | `--out ФАЙЛ` | къде да се запише (по подразбиране: името на записа) |
| | `--key HEX` | както при `list` |
| `meshes` | `<file>`, `--limit N` | Unity `SerializedFile`; най-много N мрежи |

Инструментът не носи ключове и не възстановява такива: шифриран архив се отваря само с ключ, който вие подадете. Файл, който не може да прочете, се отхвърля с един ред и код на изход 1. Всяка команда и код на изход са в [Команди](commands.md); как се чете всеки формат е в [Четци на архиви](archive-readers.md).
