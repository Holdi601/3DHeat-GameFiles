---
title: "Source 2 `.vpk`"
nav_order: 6
lang: "pt"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Lista e extrai** os ficheiros VPK da Valve, versões 1 e 2, incluindo ficheiros divididos e dados guardados dentro do ficheiro de diretório. Cada entrada pode ser verificada contra o seu próprio CRC. Este é o único formato de contentor aqui cuja documentação é do próprio fabricante. Jogos: Counter-Strike 2, Dota 2, Half-Life: Alyx e outros em Source 2.

Fonte: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Comandos: `identify`, `list`, `extract`.

## Estrutura {#layout}

```
u32 magic 0x55AA1234, u32 version (1 ou 2), u32 tamanho da árvore
  (versão 2: mais 16 bytes de cabeçalho; cabeçalho de 12 ou 28 bytes)
árvore de diretórios:
  extensão         "vmdl_c", depois "vtex_c", ..., depois ""
    caminho        "maps/example_map", depois ""
      nome         "world_layer0", depois ""
        u32 crc, u16 tamanho de pré-carga, u16 índice do ficheiro, u32 deslocamento, u32 comprimento, u16 0xFFFF
        [bytes de pré-carga]
```

- Três ciclos aninhados, cada um a terminar numa cadeia vazia, para que um leitor que espere uma contagem não encontre nenhuma. Os caminhos são guardados uma vez por grupo e reconstruídos a partir das três partes. Um único espaço significa "sem pasta" ou "sem extensão".
- Cada registo termina em `0xFFFF`. Isso é verificado, por isso um leitor que tenha perdido a posição para imediatamente ("o diretório não está a ser lido no deslocamento certo").
- **Ficheiros divididos:** o `pak01_dir.vpk` guarda o diretório, e os dados ficam em `pak01_000.vpk`, `pak01_001.vpk`... selecionados pelo índice do ficheiro da entrada.
- **Índice de ficheiro `0x7FFF`** significa que os bytes estão no próprio ficheiro de diretório, depois da árvore. Lê-lo como um índice real manda um leitor à procura de `pak01_32767.vpk`.
- **Pré-carga:** os ficheiros pequenos são guardados inteiros no diretório. Um comprimento de 0 não é então um erro.

## Comandos {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

O `identify` imprime a versão, o número de entradas e o primeiro ficheiro `.nav`. O `list` mostra cada entrada como `stored`, porque o VPK não comprime. O `extract` escreve os bytes sem verificar o CRC. Em Python, `VpkArchive(path).verify(name)` compara os bytes de uma entrada com o CRC que o diretório registou.

## A malha de navegação {#the-navigation-mesh}

Um mapa distribui a sua **malha de navegação** (`maps/<map>.nav`) ao lado da geometria compilada. Para um mapa de calor das posições dos jogadores, é de longe a mais útil das duas, porque a malha de navegação *é* o chão percorrível, já calculado e com a milésima parte do tamanho. O teste com o jogo instalado verifica que o `.nav` de um mapa distribuído começa com a assinatura de navegação Source `CE FA ED FE`.

## Verificado {#verified}

Cada entrada amostrada entre os ficheiros de mapas distribuídos de um jogo voltou byte a byte exata em relação ao seu CRC, e todos os ficheiros de mapas são analisados. Os testes com o jogo instalado repetem a verificação de CRC em 25 entradas aleatórias de cada um de até quatro ficheiros de mapas.

## Não implementado {#not-implemented}

- A descodificação dos recursos compilados do Source 2 (`.vmdl_c`, `.vtex_c`). São binários em blocos próprios, o mesmo tipo de trabalho dos formatos de malhas Unreal e Frostbite. A ferramenta CS2 separada da 3DHeat trata da geometria dos mapas do CS2.
- A descodificação da malha de navegação do CS2. O seu formato é a versão 36 e difere do formato Source 1, amplamente documentado. Os seus bytes são estruturados e não comprimidos (entropia 6,2, 31% de zeros), mas apenas 3% das suas palavras se leem como coordenadas, por isso o layout não é o óbvio e ainda não foi descoberto.
