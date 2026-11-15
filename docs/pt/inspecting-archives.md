---
title: "Inspecionar ficheiros"
nav_order: 3
lang: "pt"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Inspecionar ficheiros: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Um jogo guarda os seus ficheiros em grandes caixas chamadas **ficheiros**. Estes comandos olham para o rótulo de uma caixa, listam o que há dentro e tiram uma coisa de lá.

Antes de exportar seja o que for de um jogo desconhecido, veja o que ele distribui. Estes quatro verbos leem um ficheiro e dizem o que ele é e o que contém; não escrevem nada, exceto a única entrada pedida ao `extract`.

![identify, list e extract executados num pequeno zip](../assets/img/inspect-archives.svg)

*Uma execução num zip sintético com a estrutura de um nível do BeamNG.drive.*

## Passo a passo {#step-by-step}

1. **Pergunte o que é o ficheiro.** O `identify` lê os bytes, não a extensão:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<jogo>\Content\Paks\<arquivo>.pak"
   ```

   Ele indica o formato (Unreal `.pak`, IoStore `.utoc`/`.ucas`, pacote Unity ou `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` ou `.modelbin`, BeamNG `.cdae`/`.ter`, zip), a versão, quantas entradas tem e se está encriptado.

2. **Liste o que está dentro.** O `list` imprime uma linha por entrada: tamanho, compressão, caminho. Restrinja com `--filter` e limite com `--limit`:

   ```
   python -m heat3d_gamefiles list <arquivo> --filter Maps/ --limit 50
   ```

3. **Tire uma entrada.** O `extract` escreve uma entrada (na pasta em que está, a menos que `--out` indique outro sítio), pelo caminho que o `list` imprimiu (ou `#12`, pelo número, num `.minizip` sem nomes):

   ```
   python -m heat3d_gamefiles extract <arquivo> <caminho dentro> --out out\entry.bin
   ```

4. **Unity:** o `meshes` lista e verifica as malhas num `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <ficheiro .assets da Unity> --limit 20
   ```

## Opções {#options}

| Verbo | Opção | Significado |
|---|---|---|
| `identify` | `<file>` | qualquer ficheiro |
| `list` | `<archive>` | `.pak`, `.utoc` (ou o `.ucas` ao lado), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | apenas os caminhos que contêm TEXT |
| | `--limit N` | no máximo N linhas |
| | `--key HEX` | uma chave AES-256 (64 dígitos hexadecimais) já disponível; só um `.pak` encriptado precisa dela |
| `extract` | `<archive> <path>` | o ficheiro e o caminho da entrada, tal como o `list` o imprime |
| | `--out FILE` | onde a escrever (predefinido: o nome do ficheiro da entrada) |
| | `--key HEX` | como no `list` |
| `meshes` | `<file>`, `--limit N` | um `SerializedFile` da Unity; no máximo N malhas |

A ferramenta não traz chaves nem recupera nenhuma: um ficheiro encriptado só se abre com uma chave passada. Um ficheiro que ela não consegue ler é recusado numa linha, com código de saída 1.

Cada verbo e cada código de saída estão em [Comandos](commands.md); a forma como cada formato é lido está em [Leitores de ficheiros](archive-readers.md).
