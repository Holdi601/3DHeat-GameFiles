---
title: Forza Horizon
nav_order: 1
lang: "pt"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Exportação de percurso: Forza Horizon {#course-export-forza-horizon}

A exportação do Forza lê a pista diretamente dos ficheiros ForzaTech do jogo: o terreno com a estrada, a berma e a relva distinguidas, uma textura do chão cozida a partir dos próprios mapas de chão do jogo, e cada modelo colocado na sua própria textura (lancis, guardas de proteção, muros de pneus, sinais, adereços, edifícios). Também encontra qual das corridas do jogo a volta foi feita, e acrescenta o que o jogo põe para essa corrida apenas (a sua camada de evento: barreiras, tendas, pórticos, bancadas, bandeiras), e o chão de qualquer local por onde a condução passa, como o piso de um estádio.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<jogo>\media\Tracks\<map>" --route lap.json -o map.glb
```

Fontes: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Os próprios formatos de contentor estão em [ForzaTech](reader-forzatech.md).

## Encontrar o jogo instalado {#finding-the-installed-game}

Ninguém deve ter de escrever um caminho como
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, por isso o caminho é calculado:

1. **Bibliotecas do Steam.** O `config\libraryfolders.vdf` do Steam é lido de `C:\Program Files (x86)\Steam` ou `C:\Program Files\Steam`, e cada entrada `"path"` nele é uma biblioteca. O `steamapps\common` de cada biblioteca é pesquisado.
2. **Microsoft Store.** `C:\XboxGames` é pesquisado se existir. Aí o jogo fica um nível mais abaixo, em `<jogo>\Content`.
3. Uma **pasta de jogo** é qualquer filho dessas pastas que tenha uma pasta `media\Tracks`, seja qual for o seu nome.
4. Uma **pasta de pista** é qualquer pasta dentro de `media\Tracks` que tenha um `GeoChunk0.minizip`. Conta pelo seu conteúdo, não pelo nome, por isso uma pista com um nome que ninguém viu continua a ser encontrada.

Se o jogo estiver noutro sítio, passe a pasta da pista com `--track`; veja [Resolução de problemas](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <pasta>` salta tudo isto.

Uma pasta de pista contém o que a exportação lê:

| Ficheiro | O que é |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | os ficheiros: todos os modelos, texturas e ficheiros de colocação, sem nomes lá dentro |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | uma linha por entrada do ficheiro, pela ordem das entradas: a única fonte de nomes |
| `AssetManifest.xml` | cada textura que a pista traz, com o hash pelo qual os materiais a referem |

## Qual pista {#which-track}

Um jogo traz mais de uma pasta de pista (o mapa de mundo aberto, uma garagem ou duas). A correta é escolhida pelas **coordenadas, não pelo nome**:

- A caixa delimitadora da volta, alargada por `--margin`, é a pergunta.
- Para cada pasta de pista, os quatro manifestos `ChunkContentsMiniZip*.txt` são lidos como texto, sem abrir nenhum ficheiro. Cada nome de tile de terreno (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) transporta a sua posição na grelha. A ferramenta conta quantos tiles distintos caem dentro da caixa.
- A pista com mais tiles ali ganha. Se nenhuma tiver tiles, a exportação para com "none of the installed tracks (...) has terrain at x ..., z ....  Those are the game's own metres, as its telemetry reports them."

Uma pista inteira responde em bem menos de um segundo. Uma correspondência por nome podia escolher o mapa errado, e um mapa errado parece tão plausível como o certo.

A consola escreve `on <pista>, in <pasta do jogo>`.

## Qual corrida {#which-race}

O jogo distribui cada uma das suas corridas como uma rota com um número, o seu **id de rota**. Dois ficheiros pertencem a cada rota:

| Ficheiro | O que contém |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | a linha de condução da IA da corrida: um nó de 56 bytes a partir do byte `0x60`, a contagem de nós em `0x24`, cada nó começando pela sua posição (x, y, z) em metros do jogo |
| `media\Stripped\gs\<map>\routedefinitions.zip` | um `route<id>_<map>.rtd` por corrida: XML simples que lista o que a corrida acrescenta ao mundo e o que lhe tira (veja [A camada própria da corrida](#the-races-own-layer)) |

A volta é associada a uma rota comparando-a com cada linha da IA cuja caixa se sobrepõe à da volta:

- De cada amostra da volta, a distância ao ponto mais próximo da linha; e de cada ponto da linha, a distância à amostra mais próxima da volta.
- As duas medianas são somadas. A rota com a menor soma ganha se a soma for inferior a **30 m** (`MATCH`).
- As duas direções são necessárias: um sprint curto fica ao longo de uma rota longa que usa a mesma estrada, e uma volta longa cobre uma rota curta.

A consola escreve `the game's route <id> (driven line within <n> m of it)`, ou que nenhuma rota corresponde. Sem correspondência, só o mundo de conduta livre é colocado.

## Terreno {#terrain}

Como o terreno é encontrado (em `forzaterrain.py`):

- Os manifestos nomeiam o terreno como um índice espacial:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Os dois números são coordenadas de grelha que **avançam de 1023**, e cada passo da grelha é um tile de **512 m**. O tile `x-2046` é `-2046 / 1023 = -2`, que começa em `-2 * 512 = -1024` m. Se lesse os nomes como metros, cada pesquisa falharia por um fator de dois e ainda devolveria terreno, de uma parte errada do mapa.
- Um tile pode aparecer três vezes: normal, `_cb` e `_ul`. Os três cobrem o mesmo chão. Um é tomado por tile, por essa ordem de preferência, porque juntá-los triplicaria a geometria em superfícies coincidentes.
- Um tile só é lido se tocar a caixa da volta **e** o corredor. Um tile que o corredor não toca nunca é descomprimido.
- Cada `.modelbin` de um tile escolhido é descodificado só ao **nível de detalhe 0**. Um tile traz quatro níveis sobre o mesmo chão, e exportá-los todos põe o mesmo metro quadrado quatro vezes no ficheiro.
- Cada malha traz a sua própria escala e desvio em coordenadas do mundo, por isso cai onde o jogo a põe, sem transformação de instância. Os triângulos cuja pegada se sobrepõe à caixa são mantidos, depois só os que chegam ao corredor.
- Uma malha num formato que o leitor recusa é saltada e contada (`N meshes could not be read`), para que um resultado fraco diga porquê.

O resumo do terreno escreve o número de vértices, de triângulos, de malhas e de tiles, e a extensão x/y/z.

### Estrada, berma, terreno, marcações, água {#road-verge-terrain-markings-water}

Os nomes dos materiais não dizem onde está a estrada. À volta de um circuito, 94% do chão usa um material de sombreador de estrada, porque o terreno perto de uma estrada é desenhado com ele, e o sombreador decide asfalto ou relva pixel a pixel. Por isso:

| Tipo | Decidido por |
|---|---|
| faixa de estrada | o **layout dos vértices**: as faixas de estrada são o único chão com um segundo conjunto de UV (canal 1); um triângulo cujos três vértices o têm é estrada |
| asfalto ou berma | dentro de uma faixa de estrada, a **máscara de asfalto** do tile no centroide do triângulo: 0,5 ou mais é `road`, menos é `verge` |
| marcações | nome do material que corresponde a `whiteline`, `yellowline` ou `decal` |
| marcas de pneus | nome do material que corresponde a `tyremark` ou `skid` (verificado antes das marcações, porque as marcas de pneus vêm como `tyremark_decal_*`) |
| água | nome do material que corresponde a `water`, `lake`, `river`, `paddy`, `ocean` ou `sea` |
| terreno | tudo o resto |

Medido nas voltas gravadas do circuito de teste, quase todas as amostras caem em triângulos de faixa de estrada, e a grande maioria na parte de asfalto depois de a máscara separar a berma.

A máscara de asfalto só existe quando as texturas do chão são cozidas. Com `--no-textures`, ou para um tile cujos mapas faltam, as faixas de estrada ficam inteiras como `road` e nenhuma berma é separada. Mapas em falta custam detalhe, nunca geometria.

### As camadas pintadas são elevadas {#painted-layers-are-lifted}

As marcações das faixas e as marcas de pneus vêm como os seus próprios triângulos, deitados exatamente na estrada. O jogo desenha-os com um desvio de profundidade. Desenhados tal como estão, a estrada e a pintura lutam em cada pixel. A exportação dá a cada parte de marcação e de marca de pneus a sua própria cópia dos vértices, elevada **5 cm** (`DECAL_LIFT`) ao longo da normal da superfície, para que a estrada por baixo não seja elevada também.

### Normais {#normals}

As normais do terreno vêm do ficheiro. A componente x da normal está guardada como o quarto short da posição, e y e z no atributo `NORMAL` (veja [ForzaTech](reader-forzatech.md)). Se algum vértice da extração não tiver normal, as normais de todo o chão são calculadas a partir dos triângulos.

## A textura do chão {#the-ground-texture}

Cada tile do terreno traz três mapas que cobrem o seu quadrado de 512 m, em cinco resoluções (`_quality1` a `_quality5`, a maior de 2048 px, que são 25 cm por pixel):

| Mapa | Padrão do nome do ficheiro | O que contém (medido) |
|---|---|---|
| principal | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: normal de detalhe (x, z). A: mais baixo no asfalto e no terreno acidentado |
| secundário | `submap_x<X>_z<Z>_x<season>x_diff` | pesos das camadas. B: alto no asfalto (239 na linha conduzida, 165 ao lado) |
| brilho | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: baixo no asfalto (147 contra 215). B: sobe nos bosques |

Nenhum destes é uma fotografia a cores. São as entradas com que o sombreador de terreno do jogo mistura as suas camadas de material, e essas camadas não são descodificadas. Por isso, a textura cozida é **uma interpretação, não uma cópia do aspeto do jogo**. Mantém *onde* está cada tipo de chão, a 25 cm, e pinta-o em cores fixas:

| Chão | RGB linear | Peso |
|---|---|---|
| relva (curta, perto da pista) | 0,30, 0,44, 0,18 | a base |
| áspero (mais longe) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| bosque | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalto | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Os dois mapas têm de concordar para o asfalto. Um só deixa manchas cinzentas na relva onde a compressão de blocos faz anéis. O resultado é sombreado pelo normal de detalhe do mapa principal contra uma luz fixa (`0.55 + 0.6 * lambert`), para que os lábios dos lancis, os taludes e os sulcos se leiam como relevo, e é escrito em sRGB de 8 bits.

Orientação: a linha 0 do pixel é a borda **norte** do tile (maior z), a coluna 0 a sua borda **oeste** (menor x). Isto foi encontrado projetando voltas gravadas sobre a máscara de asfalto de todas as oito maneiras como um quadrado pode ser virado ou executado. Exatamente uma maneira as põe no asfalto. As UV seguem daí: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Os mapas são lidos à melhor resolução disponível até à qualidade 5 e reamostrados para o tamanho do mapa principal. Se a imagem de cor for maior que `--texture-size`, é depois reduzida para esse tamanho com filtragem Lanczos. A máscara de asfalto é sempre mantida à resolução total, porque decide a geometria. `--season` escolhe os mapas `x<season>x`. Um tile sem mapas para essa estação é desenhado com cores lisas, e a consola indica `N without maps`.

## Modelos colocados {#placed-models}

O próprio terreno traz a sua posição no mundo. Nada mais a traz. Onde cada cópia de um modelo está é registado em ficheiros de colocação `.pgeo`, um por categoria por célula espacial:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<categoria>_....pgeo`. O layout do registo está em [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### O que é lido {#what-is-read}

- Os ficheiros de colocação são filtrados **pelo nome**: o tamanho da célula e a posição da célula no caminho dão o quadrado da célula (`x * size` a `(x + 1) * size`), e só as células que se sobrepõem à caixa da volta, numa categoria pedida, são abertas.
- Categorias por omissão: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` acrescenta `trees`, `bushes` e `smashables`. Estas nunca são lidas: `grasstemplate`, `crowdtemplate` e `cwdspline` (relva e espetadores: o jogo desenha-os como sprites animados, não há geometria).
- Cada ficheiro pertence a uma **camada**, lida do nome depois de `c<size>_<categoria>_`. Uma palavra de nível de detalhe (`do`, `so`, `ulc`, `ulp`, `cwd`) e um número de secção opcional é o mundo de conduta livre. Qualquer outra coisa é uma camada que o jogo liga: uma camada de runtime (`rt_0`), uma atividade (`_tag_<nome>_`), um colecionável, qualquer coisa catalogada em `evolving`. Uma camada que nomeia rotas (`rt_x<id>`, por exemplo `rt_x1023_x2201`) pertence só a essas corridas, e só é lida se a volta tiver correspondido a uma delas. Veja [Camadas ativadas](#switched-on-layers).
- Uma cópia é mantida se a sua posição estiver dentro da caixa e dentro do corredor. As repetições exatas (a mesma posição e orientação ao milímetro, listadas por duas células vizinhas) são fundidas.
- Os **lancis** são adereços cujo nome de modelo começa por `road_gen_rum` (faixas sonoras). São escritos como `ground:kerbs`, nunca simplificados nem deixados de fora, porque uma volta é medida contra eles.

| Categoria | Parte | Cor de reserva (sem textura) |
|---|---|---|
| lancis | `ground:kerbs` | 0,60, 0,12, 0,10 |
| barreiras | `structure:barriers` | 0,50, 0,50, 0,50 |
| adereços | `structure:props` | 0,45, 0,35, 0,25 |
| sinais | `structure:signs` | 0,70, 0,70, 0,70 |
| edifícios | `structure:buildings` | 0,55, 0,52, 0,48 |
| infraestrutura | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| pontes | `structure:bridges` | 0,45, 0,45, 0,45 |
| rochas | `structure:rocks` | 0,30, 0,28, 0,25 |
| objetos destrutíveis | `structure:smashables` | 0,12, 0,22, 0,06 |
| árvores, arbustos | `structure:trees` | 0,10, 0,20, 0,05 |

### A geometria do modelo {#the-models-geometry}

Um nome colocado `<model>_3D` refere-se aos ficheiros de modelo `<model>_cluster###.i.modelbin` (até uma dúzia). Cada triângulo traz uma máscara dos níveis de detalhe a que pertence:

- Os níveis de um modelo são os seus triângulos marcados explicitamente para esse nível. Os níveis são contíguos desde 0, o mais fino primeiro.
- Os triângulos marcados `0xFFFF` (todos os níveis) são as peças que se partem, como os postes de uma guarda de proteção ou os pneus isolados de uma pilha. Sobrepõem-se a todo o modelo, e o jogo desenha-as no lugar dele quando ele está desfeito. São usados só por um modelo sem nenhum nível marcado explicitamente.
- As submalhas cujo sombreador de material é um **decalque** projetado são deixadas de fora.

Cada cópia é colocada com a sua posição, os seus eixos x e y do registo (z = x cruz y), e a sua escala. As normais são transformadas com a inversa da escala.

### Qual textura {#which-texture}

Um material não nomeia as suas texturas. Lista-as como hashes, e o `AssetManifest.xml` da pista associa cada hash (`SourceHash`) a um nome de textura. Só a secção `<Textures>` é lida, que para em `</Textures>` num ficheiro que pode ter dezenas de megabytes. Depois:

1. A ranhura `0x88B483AA` é a cor base no sombreador de ambiente padrão (todos os materiais amostrados). Se o material associar aí uma textura, essa é usada.
2. Senão, o tipo da própria textura decide, que é a palavra antes do seu GUID: `_bclr_`, depois `_diff_`, depois `_colour_`.
3. Mapas de terreno (`mainmap`, `submap`, `autogloss`) e paletas de tom (`tint`, `worldtint`) nunca colorem um modelo.

Assim, um modelo é colorido pelo que o seu material associa, não por uma textura com um nome parecido com o modelo. Por exemplo, `bar_rur_armco_crct_02_c` usa a textura de `..._02_a`.

A textura é lida dos ficheiros à menor resolução com pelo menos **256 px** no lado mais curto (`MODEL_TEXTURE`), reduzida a 256 se for maior, e guardada como JPEG RGB no `.glb`. A cor de uma guarda de proteção a 256 px para quatro metros é 1,6 cm por pixel, e cerca de 80 dessas texturas cabem no atlas do visualizador ao lado dos tiles do chão.

**Estações.** `--season` troca uma textura pela sua gémea sazonal pelo nome, ignorando o GUID (`..._xsummerx_bclr` para `..._xwinterx_bclr`, ou `..._bclr` para `..._winter_bclr`), quando a pista a tem. Com `--season winter`, o material de inverno de uma submalha é também usado onde a sua tabela de variantes indica um.

**Variantes.** O registo de uma submalha abre com uma tabela de materiais `(summer, winter)`, um por aspeto que uma cópia pode ter: cinco impressões para um painel publicitário, seis cores de tinta para uma pilha de pneus. Cada registo de colocação diz que variante essa cópia usa. Uma submalha com menos variantes do que o modelo repete as suas próprias.

**O bloco de marcação.** Os atlas de edifícios partilhados reservam um bloco RGB sólido (255, 64, 0) para superfícies que o sombreador do edifício tinge com outras texturas. Se mais de um vigésimo de uma textura estiver a 12 níveis dessa cor, o bloco é repintado com a cor média da própria textura. Caso contrário, uma cidade sairia laranja.

### Superfícies transparentes {#see-through-surfaces}

As vedações de arame e as redes são quadriláteros simples com buracos no canal alfa da textura. Desenhadas sólidas, uma vedação é uma parede através da vista da pista. As superfícies cujo sombreador de material corresponde a `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` ou `tree` são testadas:

- A opacidade da textura é média numa grelha de 32 x 32.
- Por superfície (cada triângulo recortado que partilha uma textura), quatro pontos por triângulo são amostrados no espaço UV e ponderados pela área UV do triângulo.
- Se a opacidade média for pelo menos 0,05 e inferior a **0,5**, a superfície inteira é deixada de fora. Abaixo de 0,05 o alfa claramente significa outra coisa para o seu sombreador (um sinal de aviso que amostra 0,01), e a superfície é mantida sólida.
- Um modelo cujas superfícies foram todas deixadas de fora é indicado: `N models left out as see-through (mostly holes in their texture)`.

A ferramenta julga a superfície inteira em vez de um triângulo de cada vez. Julgada triângulo a triângulo, metade de cada quadrilátero sobrevivia e as vedações saíam como fileiras de dentes.

### Edifícios desenhados por inteiro {#buildings-drawn-whole}

Uma cidade constrói os seus edifícios a partir de peças modulares: centenas de milhares delas à volta de um circuito urbano, dezenas de milhões de triângulos mesmo no mais grosseiro. Deixar peças de fora uma a uma deixava de pé placas de parede isoladas. O jogo também traz stand-ins de edifício inteiro em `scene\hlod_tier_1\`, uma malha por edifício (nome `hlod_tier_1_*`), já em coordenadas do mundo como o terreno:

- A caixa do mundo de cada stand-in é lida da caixa de posição da sua malha (uma leitura do cabeçalho, não uma descodificação). Isto demora segundos para um mapa inteiro.
- Os stand-ins que tocam a caixa e o corredor da volta são usados.
- Cada peça `buildings` cuja posição cai dentro da pegada de um stand-in (mais 0,5 m) é retirada, e o stand-in é desenhado no lugar dela. A sua distância à condução é medida até à aresta mais próxima do edifício.
- O resumo diz `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Camadas ativadas {#switched-on-layers}

O que uma camada ativada coloca é exportado, mas à parte do mundo de conduta livre, para que o visualizador a possa mostrar ou esconder:

| Camada | Parte |
|---|---|
| o mundo de conduta livre | `structure:<categoria>` (como antes) |
| uma camada que nomeia a rota da corrida correspondida | `structure:event_<categoria>` |
| qualquer outra camada ativada | `structure:layer_<categoria>` |

O resumo conta-as: `switched-on layers: <n> copies in <m> (<nomes das camadas>)`.

### Modelos já em coordenadas do mundo {#models-already-in-world-coordinates}

Alguns tipos de modelo não estão em nenhum ficheiro de colocação. As suas malhas trazem a sua própria posição no mundo, como o terreno, por isso nada precisa de as colocar:

| Pasta sob `scene\models\` | O que é | Parte |
|---|---|---|
| `plots` | o chão próprio de um local: o piso e o relvado de um estádio, um recinto de festival, uma praça | `ground:venue` |
| `plinths` (e qualquer modelo chamado `floor`, `ground` ou `road`) | chão com que uma rua é decorada: floreiras, degraus, o empedrado de um parque | `ground:plinths` |
| `hda_infrastructure` (pontes) | pontes construídas proceduralmente | `structure:bridges` |

- Um modelo conta como estando em coordenadas do mundo quando o centro da sua caixa fica a mais de **300 m** (`WORLD_REACH`) da sua própria origem. Os modelos colocados pelos ficheiros de colocação ficam a alguns centenas de metros da sua origem.
- Não desenhados: oclusores, cabos esticados ao longo das estradas, o fundo do mar, os telhados e oclusores de edifícios modulares (os stand-ins desenham esses edifícios), e volumes de colisão e de água.
- Cada um é lido da caixa das suas malhas (uma leitura do cabeçalho), alguns segundos para um mapa inteiro, uma vez por execução.
- As partes de chão nunca são desenhadas mais grosseiras e nunca são deixadas de fora para caber no orçamento, como os lancis.

**Um local é cortado inteiro.** Quando a condução toca o chão próprio de um local (`ground:venue`), o corredor é alargado até à pegada inteira desse chão mais `--margin`, para que as bancadas, muros e barreiras à volta de um estádio venham com ele, e não só a faixa que as voltas usaram. A consola escreve `through a venue (<nomes dos modelos>): cutting all of its ground, <n> km2`. Os plinths não alargam o corte.

### Detalhe e orçamento {#detail-and-the-budget}

As faixas de distância, o orçamento e as cópias que saem quando o orçamento é pequeno estão em [Níveis de detalhe e o orçamento](detail-budget.md).

### Resumo da colocação {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## A camada própria da corrida {#the-races-own-layer}

Muitas corridas põem coisas que não existem no mundo de conduta livre: muros e vedações de betão que fecham estradas laterais, pilhas de pneus, tendas, um pórtico de partida, bancadas, bandeiras, faixas. Cada corrida lista-as na sua definição de rota (`route<id>_<map>.rtd` em `routedefinitions.zip`, XML simples num zip simples):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **O que é acrescentado.** Cada instância é colocada como uma cópia de um ficheiro de colocação. Os 16 números da transformação são quatro linhas: os eixos x, y e z do modelo (cada um à escala) e a sua posição em metros do jogo. A terceira linha é o produto vetorial das duas primeiras. `Material` é a variante que a cópia usa. A parte é `structure:event_<kind>`, onde `<kind>` é a pasta sob `scene\models\` (barriers, props, infrastructure, signs; qualquer outra conta como props), e o nó traz os extras glTF `{"layer": "event", "route": <id>}`.
- **O que é retirado.** Uma cópia do mundo livre que está a menos de **0,1 m** da posição de um objeto oculto é deixada de fora. Um objeto oculto na origem é um modelo em coordenadas do mundo; o seu GUID de instância é procurado no `AssetManifest.xml` da pista (a lista `<Models>`: a origem de um modelo, depois os GUIDs das suas cópias) para o nomear.
- **O chão que a corrida oculta é mantido.** Uma corrida que oculta o chão de um local põe a sua própria superfície aí. Quando essa superfície não está entre os modelos que a pista traz, o chão oculto fica, como a coisa mais próxima do que se conduz por cima, e o resumo diz isso (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Não desenhado, mas contado.** Marcadores de espetadores (`crowd_proxies`: o jogo desenha a multidão como sprites a partir deles) e splines de colisão (`.splinecol`). A consola lista-os: `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Modelos de rota que a pista não traz (brilhos de luz, alguns sinais, conteúdo que o jogo carrega em streaming) são indicados em `placed names have no model in the archives`.

Só as cópias dentro do corredor são colocadas, como para tudo o resto.

## Escrever o ficheiro {#writing-the-file}

As partes são escritas nesta ordem: por tile `terrain`, `verge`, `road` (cada uma com a imagem do tile), depois `water`, `tyre marks`, `markings` (planas, as duas últimas elevadas), depois cada parte colocada ordenada pelo nome. As coordenadas são as do próprio jogo (metros, Y para cima). Veja [Formato de saída](output-format.md).

O ficheiro diz o que contém nos `asset.extras` do glTF:

| Campo | Significado |
|---|---|
| `course_format` | `2`: a camada própria da corrida, os locais e os modelos em coordenadas do mundo estão lá. [`courses`](commands.md#courses) exporta de novo um ficheiro com um número inferior (ou sem número) |
| `route` | o id da rota correspondida, ou `null` |
| `event_copies`, `event_kinds` | quantas cópias da camada própria da corrida foram colocadas, e os seus tipos |
| `hidden` | cópias do mundo livre deixadas de fora porque a corrida as retira |
| `venue` | os modelos de chão de locais por onde a condução passa |
| `layers` | as camadas ativadas colocadas |

## Quanto custa {#what-it-costs}

Ordens de grandeza aproximadas:

| Percurso | Resultado |
|---|---|
| um circuito curto de campo | algumas centenas de milhares de triângulos de terreno, mais de um milhão colocados; segundos, menos de 100 MB |
| um sprint longo de ponto a ponto | o corredor é uma pequena fração da caixa à sua volta; cerca de um minuto, algumas centenas de MB |
| um circuito urbano | milhares de barreiras, adereços e sinais, e edifícios inteiros; com o orçamento automático até várias centenas de MB |

Um quilómetro quadrado de terreno de mundo aberto são cerca de um milhão de triângulos.

## Verificações que o sustentam {#checks-behind-it}

São medições feitas enquanto o leitor era escrito, como indicado no código-fonte. Não são repetidas pelos testes, a menos que o jogo esteja instalado.

- No circuito de teste, o carro fica cerca da sua altura de marcha acima do chão extraído (mediana abaixo de 0,2 m).
- Cada tile amostrado cai dentro do quadrado de 512 m que o seu nome prevê.
- Colocações consecutivas de guardas de proteção ficam exatamente a 4 m umas das outras, e a maioria das extremidades de guardas fica a menos de 5 cm do início da seguinte.
- Os lancis ficam uns centímetros acima do chão extraído, com a face para cima, a menos de 5 m da condução (também um teste do jogo instalado, veja [Desenvolvimento](development.md)).

## Não desenhado {#not-drawn}

- Árvores e arbustos, a menos que `--trees`. Relva e multidões nunca (o jogo desenha-as como sprites).
- Modelos próprios de uma corrida que a pista não traz (veja [A camada própria da corrida](#the-races-own-layer)).
- Materiais de decalque projetado em modelos.
- Impressões de sinais misturadas com alfa sobre a sua placa ficam opacas.
- A cor do chão é uma reconstrução de onde ficam o asfalto, a relva e o bosque, não os materiais de terreno do próprio jogo.
