---
title: Преглед архива
nav_order: 3
lang: "sr"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Преглед архива: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Игре пакују своје фајлове у велике кутије које се зову **архиви**. Ове команде погледају етикету кутије, испишу шта је у њој и извуку једну ствар.

Пре извоза било чега из непознате игре, погледајте шта она испоручује. Ове четири команде читају фајл и кажу шта је и шта садржи; ништа не записују осим једног уноса који тражите помоћу `extract`.

![identify, list и extract покренути на малом zip архиву](../assets/img/inspect-archives.svg)

*Покретање над синтетичким zip архивом распоређеним као ниво BeamNG.drive.*

## Корак по корак {#step-by-step}

1. **Питајте шта је фајл.** `identify` чита бајтове, а не екстензију:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Именује формат (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle или `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` или `.modelbin`, BeamNG `.cdae`/`.ter`, zip), његову верзију, колико уноса садржи и да ли је шифрован.

2. **Испиши шта је унутра.** `list` исписује по један ред за сваки унос: величину, компресију, путању. Сузите га са `--filter`, а ограничите са `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Извуците један унос.** `extract` записује један унос (у фасцикли у којој сте, осим ако `--out` каже другачије), по путањи коју је `list` исписао (или `#12`, по броју, у `.minizip` без имена):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` исписује и проверава мреже у `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Опције {#options}

| Команда | Опција | Значење |
|---|---|---|
| `identify` | `<file>` | било који фајл |
| `list` | `<archive>` | `.pak`, `.utoc` (или `.ucas` поред њега), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | само путање које садрже TEXT |
| | `--limit N` | највише N редова |
| | `--key HEX` | AES-256 кључ (64 хекс цифре) који већ имате; само шифрован `.pak` га захтева |
| `extract` | `<archive> <path>` | архив и путања уноса онако како је исписује `list` |
| | `--out FILE` | где да се записује (подразумевано: име фајла уноса) |
| | `--key HEX` | као код `list` |
| `meshes` | `<file>`, `--limit N` | Unity `SerializedFile`; највише N мрежа |

Алат не испоручује кључеве и не открива их: шифрован архив се отвара само кључем који наведете. Фајл који не може да прочита одбија се у једном реду са излазним кодом 1.

Свака команда и излазни код су на [Командама](commands.md); како се сваки формат чита је под [Читачи архива](archive-readers.md).
