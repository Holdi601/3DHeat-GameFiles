---
title: "Undersøge arkiver"
nav_order: 3
lang: "da"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Undersøge arkiver: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Et spil pakker sine filer i store kasser, der kaldes **arkiver**. Disse kommandoer
kigger på etiketten på en kasse, lister, hvad der ligger i den, og tager én ting ud.

Før du eksporterer noget fra et ukendt spil, så kig på, hvad det leverer.
Disse fire verber læser en fil og fortæller, hvad den er, og hvad den indeholder; de skriver
intet undtagen den ene post, du beder `extract` om.

![identify, list and extract run on a small zip](../assets/img/inspect-archives.svg)

*En kørsel på en kunstig zip-fil, opbygget som et BeamNG.drive-bane.*

## Trin for trin {#step-by-step}

1. **Spørg, hvad filen er.** `identify` læser bytene, ikke filendelsen:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Den angiver formatet (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity-bundle eller
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` eller
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), dens version, hvor mange poster den
   indeholder, og om den er krypteret.

2. **List, hvad der er indeni.** `list` skriver én linje pr. post: størrelse, komprimering,
   sti. Indsnævr den med `--filter`, og begræns antallet med `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Tag én post ud.** `extract` skriver én post (i den mappe, du står i, medmindre `--out` siger andet),
   efter den sti, `list` skrev ud (eller `#12`, efter nummer, i en `.minizip` uden navne):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` lister og kontrollerer meshene i en `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Valgmuligheder {#options}

| Verbum | Valgmulighed | Betydning |
|---|---|---|
| `identify` | `<file>` | en hvilken som helst fil |
| `list` | `<archive>` | `.pak`, `.utoc` (eller `.ucas` ved siden af), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | kun stier, der indeholder TEXT |
| | `--limit N` | højst N linjer |
| | `--key HEX` | en AES-256-nøgle (64 hex-cifre), du allerede har; kun en krypteret `.pak` har brug for den |
| `extract` | `<archive> <path>` | arkivet og postens sti, som `list` skriver den ud |
| | `--out FILE` | hvor den skrives (standard: postens filnavn) |
| | `--key HEX` | som for `list` |
| `meshes` | `<file>`, `--limit N` | en Unity `SerializedFile`; højst N meshes |

Værktøjet leverer ingen nøgler og finder ingen; et krypteret arkiv åbner kun med en nøgle,
du angiver. En fil, det ikke kan læse, afvises med én linje og afslutningskode 1.
Alle verber og afslutningskoder står på [Kommandoer](commands.md); hvordan hvert format
læses, står under [Arkivlæsere](archive-readers.md).
