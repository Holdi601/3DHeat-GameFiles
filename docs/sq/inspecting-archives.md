---
title: "Shqyrtimi i arkivave"
nav_order: 3
lang: "sq"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Shqyrtimi i arkivave: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Një lojë i paketon skedarët e saj në kuti të mëdha që quhen **arkiva**. Këto komanda shikojnë
etiketën e një kutie, listojnë çfarë ka brenda dhe nxjerrin një gjë.

Para se të eksportosh diçka nga një lojë e panjohur, shiko çfarë përmban.
Këto katër komanda lexojnë një skedar dhe të thonë çfarë është e çfarë mban; nuk
shkruajnë asgjë, përveç hyrjes së vetme që kërkon me `extract`.

![identify, list dhe extract të ekzekutuara mbi një zip të vogël](../assets/img/inspect-archives.svg)

*Një ekzekutim mbi një zip sintetik të ndërtuar si një nivel i BeamNG.drive.*

## Hap pas hapi {#step-by-step}

1. **Pyet çfarë është skedari.** `identify` lexon bajtet, jo shtesën:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Ai emërton formatin (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle ose
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` ose
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), versionin, sa hyrje
   ka, dhe nëse është i enkriptuar.

2. **Liston çfarë ka brenda.** `list` printon një rresht për çdo hyrje: madhësia, ngjeshja,
   rruga. Ngushtoje me `--filter`, kufizoje me `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Nxirr një hyrje.** `extract` shkruan një hyrje (në dosjen ku je,
   përveç nëse `--out` thotë ndryshe), sipas rrugës që printoi `list`
   (ose `#12`, sipas numrit, në një `.minizip` pa emra):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` liston dhe kontrollon rrjetat (mesh) në një `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Opsionet {#options}

| Komanda | Opsioni | Kuptimi |
|---|---|---|
| `identify` | `<file>` | çdo skedar |
| `list` | `<archive>` | `.pak`, `.utoc` (ose `.ucas` pranë tij), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | vetëm rrugët që përmbajnë TEXT |
| | `--limit N` | së shumti N rreshta |
| | `--key HEX` | një çelës AES-256 (64 shifra hex) që e ke tashmë; vetëm një `.pak` i enkriptuar e kërkon |
| `extract` | `<archive> <path>` | arkivi dhe rruga e hyrjes ashtu siç e printon `list` |
| | `--out FILE` | ku të shkruhet (parazgjedhja: emri i skedarit të hyrjes) |
| | `--key HEX` | si për `list` |
| `meshes` | `<file>`, `--limit N` | një `SerializedFile` i Unity; së shumti N rrjeta |

Mjeti nuk sjell çelësa dhe nuk rikupton asnjë: një arkiv i enkriptuar hapet vetëm me
një çelës që e jep ti. Një skedar që nuk mund ta lexojë refuzohet me një rresht
dhe kodin e daljes 1.
Çdo komandë dhe çdo kod dalje është te [Komandat](commands.md); si lexohet secili format
është te [Lexuesit e arkivave](archive-readers.md).
