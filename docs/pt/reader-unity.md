---
title: Unity
nav_order: 4
lang: "pt"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, bundles, malhas {#unity-serializedfile-bundles-meshes}

**Lista objetos e descodifica malhas** de `SerializedFile` do Unity no formato 22 ou
mais recente (Unity 2020 até 6000), e abre bundles `UnityFS`. Não há exportação de
percurso do Unity.

Fontes: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Comandos: `identify` (contêineres e bundles), `meshes` (só contêineres avulsos).

## O contêiner {#the-container}

O Unity traz um nível como grafos de objetos serializados: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` e bundles de assets. Cada um tem uma
tabela de objetos marcada com um id de classe.

O cabeçalho é onde a leitura erra em silêncio. Os primeiros dezesseis bytes são quatro
`uint32` big-endian mantidos por compatibilidade. No formato 22, três deles são zero, e os
valores reais vêm depois, porque um ficheiro pode passar de 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

O segundo `metadata size` é um `uint32` entre dois `int64`. Presumir que os três são de 64
bits empurra a string de versão quatro bytes para a frente. Ela ainda se descodifica como
algo com cara de string, e manda tudo o que vem depois para o lugar errado. O cabeçalho é
big-endian. Tudo depois dele segue o byte de endianness (0, little-endian, em toda versão
de desktop).

Depois do cabeçalho: a string de versão do motor, a plataforma, a flag de árvore de tipos,
a tabela de tipos (id de classe por tipo), a tabela de objetos (path id, deslocamento,
tamanho, tipo) e os externos (outros ficheiros para os quais um ponteiro pode apontar).

| Caso | Resultado |
|---|---|
| formato 22-30 | lido |
| formato 9-21 (antes do Unity 2020) | recusado: os deslocamentos estão no cabeçalho legado, e nenhum ficheiro disponível o usava |
| fora de 9-30 | recusado |
| árvore de tipos embutida (builds do editor) | recusado: builds distribuídas não embutem uma, e o caminho do editor não está implementado |
| um bundle passado onde se espera um contêiner | recusado, com um aviso para o leitor de bundles |

Não há **desserializador geral**. Builds distribuídas não trazem árvore de tipos, porque o
esquema fica compilado dentro do player, então cada classe precisa ser lida conforme um
layout conhecido para a sua versão. Só `Mesh` é descodificada. As outras classes são
informadas pelo nome e pela contagem (`GameObject`, `Transform`, `MeshRenderer`,
`MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; as outras como `class<id>`).

**Verificado** em muitos jogos instalados e milhões de objetos: a tabela de objetos precisa
cobrir a secção de dados exatamente, sem sobreposições, com nada além de preenchimento de
alinhamento entre objetos, e o último objeto terminando no último byte do ficheiro. Uma
leitura errada do cabeçalho não consegue produzir isso. O teste com jogo instalado repete
a verificação em até seis ficheiros `resources.assets` / `sharedassets0.assets` encontrados
em pastas `*_Data`.

## Bundles (`UnityFS`) {#bundles-unityfs}

Um bundle é um contêiner comprimido de ficheiros SerializedFile. A lista de blocos e o
diretório também são comprimidos. O método está nos seis bits baixos de uma palavra de
flags: 0 sem compressão, 1 LZMA (cabeçalho de 5 bytes do Unity com o tamanho inserido), 2 e
3 LZ4 / LZ4HC. O formato 7 em diante alinha o cabeçalho a 16 bytes. A flag `0x80` põe o
diretório no fim do ficheiro. `UnityWeb`, `UnityRaw` e `UnityArchive` (anteriores à 5.3) são
reconhecidos, mas não são lidos.

## Malhas {#meshes}

`read_mesh` descodifica um objeto `Mesh` em posições, normais, o primeiro conjunto de UV e
triângulos, na ordem em que o Unity 2019+ os escreve: nome, submalhas, blend shapes
(saltados), poses de bind e dados de ossos (saltados), as flags de compressão e de
legibilidade, o buffer de índices, os canais de vértice e os dados de vértice, o bloco de
malha comprimida, a caixa delimitadora local e as informações de streaming.

- **Vértices externos.** A maior parte da geometria distribuída fica num ficheiro `.resS`
  ao lado do contêiner. A ferramenta a lê da pasta do contêiner (só o nome do ficheiro do
  caminho guardado `archive:/...` é usado). Um `.resS` ausente é um erro, não uma malha
  vazia.
- **Streams e canais.** Os canais dizem qual stream, deslocamento, formato e dimensão cada
  atributo tem. Os streams vêm empacotados um após o outro, cada um com preenchimento até 16
  bytes, então o início de um stream é acumulado a partir dos passos antes dele. Formatos:
  float32, float16, unorm/snorm de 8 e 16 (normalizados) e inteiros simples.
- **Topologia.** Só triângulos (topologia 0). Tiras, quads e linhas são recusados, porque uma
  conversão errada parece geometria real.
- **Malhas comprimidas** (deltas quantizados) são recusadas: "mesh '...' is stored
  compressed; that encoding is not implemented".

### A autoverificação {#the-self-check}

Ler uma estrutura na ordem errada não lança erro. Produz números plausíveis. Por isso, toda
malha descodificada é verificada contra a **caixa delimitadora que o Unity guardou para ela**,
calculada pelo editor a partir dos vértices reais. `aabb_matches()` passa quando os cantos da
caixa descodificada ficam dentro de 2% do tamanho da caixa guardada. `meshes` imprime `ok` ou
`BOUNDS DISAGREE` em cada linha.

**Verificado:** malhas amostradas em vários jogos descodificam com as caixas batendo. O teste
com jogo instalado repete a verificação nos contêineres instalados.

## Não implementado {#not-implemented}

- Formatos anteriores a 2020.
- Malhas comprimidas.
- Qualquer classe além de `Mesh`: sem grafo de cena, transformações ou materiais, então as
  malhas ficam no próprio espaço local.
- `meshes` num bundle. O leitor de bundles existe em Python
  (`UnityBundle.serialized_files()`), mas o comando apanha um contêiner avulso.
