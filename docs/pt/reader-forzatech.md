---
title: ForzaTech
nav_order: 7
lang: "pt"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, texturas `.pb`, posicionamentos {#forzatech-minizip-modelbin-swatches-placements}

O Forza Horizon executa no ForzaTech, o motor próprio da Turn 10. Estes leitores levam uma
pista, a partir dos seus ficheiros, até triângulos posicionados e texturizados. Eles são
acedidos por `course`, `courses` e `terrain` (veja [Forza Horizon](course-forza-horizon.md)).
O `identify` reconhece um `.minizip` e um `.modelbin` avulso, e `list` e `extract`
aceitam um `.minizip`, pelos nomes do `ChunkContentsMiniZip<n>.txt` ao lado dele ou pelo
número da entrada (`#12`).

| Formato | Módulo |
|---|---|
| ficheiros `.minizip` e suas listas de nomes | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modelos e terreno `.modelbin` | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| texturas `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| ficheiros de posicionamento `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` e hashes de textura dos materiais | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| tiles de terreno por lugar | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

O Forza também guarda boa parte do seu conteúdo em ficheiros ZIP comuns, dentro de
`media\`. O `zipfile` do Python os abre, e `forzatech.models_in_archive()` lista as suas
entradas `.modelbin`. A geometria das pistas está nos ficheiros `.minizip`.

## `.minizip`: um ficheiro sem nomes {#minizip-an-archive-with-no-names}

Uma pista traz quatro ficheiros `GeoChunk<n>.minizip`, de dezenas de gigabytes cada num
mapa de mundo aberto, com centenas de milhares de entradas. **Os ficheiros não guardam
nomes nenhum**: nem tabela de nomes nem cabeçalho por entrada, só um número de ordem.
Os nomes estão em `ChunkContentsMiniZip<n>.txt` ao lado de cada ficheiro, uma linha por
entrada na ordem das entradas (`<build path>zipcache\pc\<path>|<bundle>`). Esse
emparelhamento é a única forma de pedir um ficheiro. Tudo até `zipcache\pc\` é descartado,
e as buscas ignoram maiúsculas e minúsculas.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Três detalhes do índice ainda produzem saída quando lidos errado. O leitor acerta os três:

| Detalhe | O que um leitor descuidado faz | Como fica |
|---|---|---|
| a base do segmento é de **64 bits** | lê como u32 mais preenchimento | correta nos primeiros 4 GB, depois um ruído do tamanho certo |
| a base é **alinhada a 8 bytes** | ignora a palavra de preenchimento depois da tabela de bundles | em ficheiros com um número par de bundles, toda entrada declara um codec que não existe |
| o tamanho guardado de uma entrada é o intervalo até à próxima entrada (ou a base do próximo segmento) **menos o seu preenchimento** (bits de flag 12-13) | usa o intervalo inteiro | o LZ4 recusa o bloco de vez |

Os codecs são os cinco bits baixos das flags: `0x00` sem compressão, `0x08` deflate cru,
`0x1F` bloco LZ4. Qualquer outro é recusado. Cada entrada precisa descompactar exatamente
o tamanho que declara, senão é recusada. O índice (cerca de 5 MB) é lido uma vez, e os
conteúdos são lidos por busca de posição.

O cabeçalho é verificado: magic, um cabeçalho de 32 bytes, e um número de segmentos que
bate com `ceil(entries / per segment)`.

**Verificado:** entradas amostradas em todos os ficheiros de um mapa, cada uma
descompactando exatamente para o comprimento declarado nos três codecs.

## `.modelbin`: o contêiner de chunks {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- O tamanho de ficheiro declarado precisa ser igual ao tamanho real.
- A **cadeia**: cada chunk começa onde o anterior terminou, arredondado para cima para 4
  bytes. Nada no ficheiro diz isso, então é uma evidência: um registo lido com o passo
  errado não produz essa cadeia. Ela valeu para os 252 modelos amostrados.
- Um ficheiro `PGZP` dado ao leitor de modelos é recusado como "a ForzaTech .minizip
  archive, not a model" e apontado para `minizip.py`, em vez de ser rejeitado sem mais nada.

A geometria vem destes chunks:

| Chunk | Contém |
|---|---|
| `VLay` | um layout de vértice: nomes de atributos, depois elementos (índice de nome u16, canal, buffer, formato DXGI, deslocamento); a contagem de elementos é um u16 |
| `VerB` | um buffer de vértices atrás de um cabeçalho de 16 bytes (contagem, tamanho, passo u16, atributos u16, formato) |
| `IndB` | o buffer de índices, mesmo cabeçalho |
| `Mesh` | uma submalha: material, máscara de nível de detalhe, faixa de índices, layout, buffer, passo, tabela de variantes e uma caixa de posição no fim |
| `MatI` | uma instância de material: o seu caminho `.materialbin` e os hashes de textura |

### Posições e a caixa {#positions-and-the-box}

As posições são `R16G16B16A16_SNORM` (formato 13): quatro shorts com sinal por vértice.
`position = short / 32767 * scale + bias`, em que scale e bias são os últimos 32 bytes do
chunk `Mesh` (dois float4). O bias fica **nas coordenadas do mundo do jogo**, então um tile
de terreno cai onde o jogo o põe, sem nenhuma transformação de instância. É por isso que
uma volta de telemetria basta para pedir um pedaço do mapa. Toda submalha de um modelo
carrega a mesma caixa (verificado em 860 delas).

### O layout de vértices {#the-vertex-layout}

Um único buffer de posições cobre todos os vértices. Os outros atributos se dividem em
grupos de vértices consecutivos, cada um com o seu próprio buffer e o seu próprio layout:
uma estrada perto de um cruzamento leva três conjuntos de UV e duas tangentes, o barranco
ao lado só uma normal. Cada atributo que não é posição tem quatro bytes. Qual layout
descreve qual buffer é tirado das submalhas que desenham a partir dele, porque layouts e
buffers não estão na mesma ordem (igual, deslocada num, ou permutada, conforme o modelo).

| Formato DXGI | Código | Usado para |
|---|---|---|
| R16G16B16A16_SNORM | 13 | posição (o quarto short é o x da normal) |
| R16G16_SNORM | 37 | normal y, z |
| R16G16_UNORM | 35 | um par de UV (canal = qual conjunto) |
| R8G8B8A8_UNORM | 28 | cor ou pesos de mistura |
| R10G10B10A2_UNORM | 24 | tangente (não descodificada) |
| R16_UINT | 57 | índices |

**A normal é dividida.** `NORMAL` guarda y e z. O x é o quarto short da posição, que
parecia preenchimento. Sobre centenas de milhares de vértices de terreno, ele se
correlaciona +0,92 com o x da normal do triângulo e com mais nada. Com ele, 96% dos
vértices de solo inclinado ficam a 18° da normal calculada. Toda codificação de dois
componentes tentada sem ele (octaédrica em todas as 48 disposições, entre elas) acertava
y e z e errava x.

Outros formatos de posição ou de índice são **recusados** ("only 13 (four shorts, scaled)
is implemented"; "only unsigned shorts are implemented").

### Submalhas {#submeshes}

Um registo `Mesh` tem 238 bytes na forma padrão. Os mais longos trazem antes uma tabela
de **variantes** de material mais comprida, de 238 + 8 x count - 4 bytes, e cada campo
depois dela recua exatamente esse tanto. Os mais curtos (218 bytes, parte do terreno)
mantêm os deslocamentos. Cada entrada de variante é
`u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. A máscara de nível
de detalhe é um u16, com um bit por nível a partir do bit 1.

Nada é confiado sozinho. As faixas de índices precisam cobrir exatamente o buffer de
índices, cada `index count` precisa ser igual a 3 x `triangles`, e o passo que uma
submalha nomeia precisa ser o do seu buffer. Uma tabela que falha é recusada por inteiro,
porque rotular triângulos a partir de campos mal lidos é pior do que não rotular. Entre
milhares de submalhas amostradas, todas cujo índice de buffer está no intervalo passam.

### Materiais e hashes de textura {#materials-and-texture-hashes}

Um `MatI` nomeia o seu material por um caminho `Game:...\x.materialbin`, achado buscando
no chunk. As suas texturas são registos `u32 slot, u32, u32 hash`, a 33 bytes um do
outro e sem alinhamento, então o chunk é pesquisado em cada deslocamento de byte por
palavras que são hashes de textura conhecidos. Esses vêm do `AssetManifest.xml` da pista
(`<Texture Source="...\name.swatch" SourceHash="...">`, lido até `</Textures>`). O slot
`0x88B483AA` é a cor base do shader padrão. Como a textura de cor é então escolhida está em
[Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: texturas {#pb-texture-swatches}

Uma textura é o mesmo contêiner `burG` de um modelo: um cabeçalho `HCXT` de 96 bytes no
byte 44, depois um chunk de pixels. O cabeçalho traz o GUID da textura (o do nome do
ficheiro), largura e altura, a quantidade de mips e o **código de formato no byte 72**
(numeração própria do ForzaTech). O byte 84 traz a quantidade de bytes de pixel.

| Código | Formato | Identificado como |
|---|---|---|
| 0 | BC1, meio byte por pixel | descodifica como um lancil vermelho e branco (ruído sob BC4) |
| 9 | BC7, um byte por pixel | descodifica como um tile de terreno com o circuito visível |
| 13 | RGBA8, quatro bytes por pixel | simples |
| outro | recusado | "texture format N has not been identified; refusing to guess" |

Os formatos foram identificados descodificando ficheiros reais de todas as formas que o
tamanho do payload permite. O byte 47, que uma versão anterior tomou como formato, é 4 em
todas as texturas amostradas. Só o mip mais alto de um ficheiro é descodificado. Cada
resolução é uma entrada própria, `<name>_<guid>_quality<n>.pb`, da qualidade 1 (menor) à
5 (maior). Para mapas de terreno, as duas maiores ficam num ficheiro diferente do resto.
A descodificação passa pelo descodificador BCn do Pillow, por meio de um cabeçalho DDS gerado.

## Ficheiros de posicionamento (.pgeo) {#placement-files-pgeo}

Um ficheiro por categoria e por célula espacial:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. O caminho sozinho diz o
quadrado da célula e a categoria, então os ficheiros podem ser filtrados sem abri-los.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Como cada campo foi decidido:

| Campo | Decidido por |
|---|---|
| a posição é ponto fixo 16.16, não uma fração da caixa | guard-rails consecutivos ficam exatamente a 4,000 m um do outro (o comprimento do modelo) |
| magnitude com sinal, não complemento de dois | o complemento de dois punha coordenadas negativas dezenas de quilómetros fora do mapa; com o bit 31 como sinal, cada registo de cada categoria amostrada cai dentro da caixa do seu ficheiro |
| os vetores são os eixos próprios do modelo | a ponta de cada guard-rail cai no começo do próximo: 93,5% dentro de 5 cm, mediana 0,000 m |
| o byte 60 é a variante | as cinco cópias de um billboard leem 0, 2, 2, 3, 4, enquanto todo guard-rail lê 0 |

Só nomes que terminam em `_3D` são registos de modelo. A tabela de variantes antes deles
lista nomes sem o sufixo, e lidos como registos caem no infinito. Um registo candidato só
é aceito se a sua contagem couber no ficheiro, e instâncias com números não finitos são
descartadas.

## Não implementado {#not-implemented}

- Formatos de vértice e de índice que não sejam os acima (recusados).
- Formatos de textura que não sejam 0, 9 ou 13 (recusados).
- Tangentes (lidas e descartadas, não usadas).
- As camadas de material do shader do terreno. A textura do solo é uma interpretação dos
  mapas de tiles (veja [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
