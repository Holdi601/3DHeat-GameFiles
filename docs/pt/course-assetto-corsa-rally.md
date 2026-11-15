---
title: Assetto Corsa Rally
nav_order: 3
lang: "pt"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Exportação do percurso: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

O Assetto Corsa Rally é feito com o Unreal Engine 5 (5.6.1, uma versão modificada)
e entrega o conteúdo em contêineres IoStore. Nenhum deles é cifrado. A
exportação encontra a etapa e a orientação dos eixos a partir da volta. Ela grava
os tiles de solo da própria etapa, divididos em estrada e terreno e com textura
da cor de solo assada da etapa. Os demais modelos são colocados em cores chapadas
por categoria.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Fontes: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (instalação, etapas, posicionamento),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (a exportação).
Os leitores Unreal por baixo estão em [Unreal 5 IoStore](reader-unreal-iostore.md),
e a descompressão em [Oodle](reader-oodle.md).

**Situação:** testado na versão instalada do jogo com voltas geradas num frame
aleatório em cada etapa, e encontrou a etapa e o frame certos todas as vezes.
Nenhuma volta gravada no próprio jogo passou por ele ainda.

## Encontrar a instalação {#finding-the-install}

- `--install <pasta>`: a pasta do jogo, ou a sua `Content\Paks`, ou qualquer pasta
  que tenha ficheiros `.utoc`. A ferramenta verifica `<pasta>`, depois
  `<pasta>\acr\Content\Paks`, depois `<pasta>\Content\Paks`.
- Sem isso, é verificada `steamapps\common\Assetto Corsa Rally` de cada biblioteca
  da Steam, do mesma maneira.
- Cada `.utoc` dessa pasta é aberto como um único armazenamento. Os contêineres
  que falham ao abrir são saltados. Se nenhum abre: "no readable IoStore containers in ...".

A maior parte dos blocos é comprimida com Oodle, e uma biblioteca é procurada na
máquina (todas as bibliotecas da Steam são pesquisadas). Veja [Oodle](reader-oodle.md).

O jogo é tomado como AC Rally quando o ficheiro da volta diz
`"game": "assetto-corsa-rally"` (ou `acrally`), ou quando se passa `--game acrally`.

## O que é uma etapa {#what-a-stage-is}

Uma etapa é um mapa **World Partition**:

- `Content\Levels\<Stage>.umap` posiciona o terreno distante.
- Células cozidas em `Content\Levels\<Stage>\_Generated_\*.umap` posicionam todo o resto.

Um nível conta como etapa se sua pasta de ambiente,
`Content\Environments\<Stage>\`, tiver uma pasta `MeshesTrack`. A ferramenta não
olha o nome dos tiles, porque uma etapa pode dar a eles o nome de uma cidade em vez
do nome do mapa. `--level` é comparado sem diferenciar maiúsculas de minúsculas
com esses nomes de mapa. Um nome errado lista as etapas que existem.

Não há **landscape**. O solo é feito de malhas estáticas:

| Tiles | Caminho | Viram |
|---|---|---|
| tiles da pista, cerca de 175 m, divididos em dois | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` e `..._Terrain_k` | `ground:road` e `ground:terrain` (um tile de pista sem divisão, como um lago congelado, é todo estrada) |
| terreno distante, tiles de 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Ler o posicionamento {#reading-the-placements}

O que posiciona uma malha é um `StaticMeshComponent`: o seu `StaticMesh` e o seu
`RelativeLocation`, `RelativeRotation` e `RelativeScale3D`, cada um relativo ao
componente ao qual está preso (`AttachParent`), até à raiz do ator, que fica no mundo.

- As propriedades são **sem versão**: guardadas pela posição na lista de
  propriedades da classe, e não pelo nome. São lidas com os esquemas de
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (veja [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Um valor igual ao do modelo do componente (o seu arquétipo num Blueprint) não
  é guardado. Por isso os valores do modelo são lidos primeiro, recursivamente, e
  os valores próprios do componente os substituem.
- Componentes com `bVisible = 0` ou `bHiddenInGame = 1` são saltados. Também são
  saltados os meshes cujo caminho contém `respawnwall`, `collision`, `blocker`,
  `invisible`, `/hlod/` ou `_hlod`.
- As rotações usam a `FRotationMatrix` do Unreal (pitch, yaw, roll em graus).
- Duplicatas (o mesmo mesh na mesma transformação, até 0,1 cm) são descartadas.
- Componentes que não podem ser lidos são contados por motivo e informados, por
  exemplo `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Componentes instanciados** (florestas, quase todos) só são lidos com `--trees`.
Esta versão do jogo reorganizou essas classes além dos cabeçalhos do motor, então
as propriedades delas não são lidas. Em vez disso:

- a malha vem da tabela de dependências do pacote, em que cada componente desses
  lista exatamente uma malha estática,
- as instâncias vêm do bloco nativo depois das propriedades
  (`[1][1][128][count]` e depois `count` matrizes 4x4 de double),
- o componente é considerado na raiz do seu ator, que é como os atores de
  vegetação os posicionam.

As coordenadas são do Unreal: centímetros, Z para cima, X para a frente, Y para a
direita, um referencial de mão esquerda.

## Qual etapa, e em que sentido {#which-stage-and-which-way-round}

O referencial da telemetria não é documentado, então não é assumido. Ele é ajustado:

- **Oito referenciais candidatos.** O Z do Unreal (cm) vezes 0,01 torna-se a altura
  (y) da volta. X e Y do Unreal tornam-se x e z da volta, trocados ou não, com qualquer
  um dos sinais, tudo multiplicado por 0,01 para metros.
- **Uma grade de altura da estrada.** Para cada etapa, cada tile de estrada é
  colocado (no seu nível de detalhe mais grosseiro) e o vértice de estrada mais
  alto é guardado por célula de 2 m.
- **Pontuação.** Até 400 amostras da volta, igualmente espaçadas, são levadas para
  o espaço do Unreal por cada referencial. Uma amostra está na estrada quando, entre
  as 3 x 3 células à volta dela, a altura de estrada mais próxima dela fica entre
  1 m abaixo e 3 m acima da amostra (`ON_ROAD`). A pontuação é a parcela das
  amostras que estão na estrada.
- **Vencedor.** O melhor referencial na melhor etapa, se chegar a pelo menos 50%.
  Senão a exportação para: "the lap does not lie on any stage's road in any frame
  (best: ...). Name the stage with --level."
- **Uma volta que diz o nome da pista.** Se o ficheiro da volta tiver um campo
  `track`, uma etapa cujo nome combine de forma aproximada com ele (só letras e
  números, um contendo o outro) é testada primeiro, sozinha, e só é aceita se
  chegar a pelo menos 80%. Senão, todas as etapas são testadas.
- Com `--level`, só essa etapa é testada, nos oito referenciais.

O consola diz, por exemplo,
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Depois tudo é escrito **no referencial da volta**: metros, Y para cima. O sentido
de enrolamento de um triângulo é invertido sempre que uma transformação espelha,
para que as faces continuem apontando para o lado certo.

## O solo {#the-ground}

- O corredor é `--margin` metros em volta da volta, no plano x/z dela.
- Cada tile de solo é colocado no seu nível de detalhe mais fino, e só os
  triângulos que entram no corredor são mantidos.
- Os triângulos são agrupados por tipo (estrada ou terreno) e por quadrado de
  512 m no espaço do Unreal (51.200 cm), cada quadrado com a sua própria imagem.
  As partes recebem nomes como `ground:road 1_-4`. UVs são
  `(unreal_xy - square_origin) / 51200`.
- As normais são calculadas a partir dos triângulos para o ficheiro inteiro.

### A textura do solo {#the-ground-texture}

A não ser que use `--no-textures`, cada quadrado é pintado a partir de duas fontes,
em `--texture-size` pixels:

1. **A cor de solo assada.** O `RuntimeVirtualTextureComponent` do mapa da etapa
   (a sua caixa é `RelativeLocation` como canto e `RelativeScale3D` como tamanho,
   sem rotação) aponta para uma **textura virtual** em streaming, a cor de solo que o
   jogo assou. A região do quadrado é lida dela, no nível cujos pixels ficam mais
   perto do tamanho pedido. São de 13 a 59 cm por pixel, conforme a etapa.
2. **A imagem de satélite** preenche o que a textura virtual deixa preto. Ela é a
   textura `sat*_(b|bc|c|basecolor)` da etapa, na pasta de ambiente, lida em até
   4096 px. O seu posicionamento é achado por um ajuste de mínimos quadrados da
   primeira camada de UV do terreno distante contra x e y do mundo. O ajuste precisa
   ser linear até 0,01 no percentil de 95%, senão a imagem não é usada. Se os UVs do
   terreno distante passarem de 1 (um material que os repete), o mapeamento é
   dividido por dois até caber uma vez.

O consola diz qual foi usada, por exemplo
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Uma etapa sem nenhuma das duas é desenhada em cores chapadas.

## Modelos colocados {#placed-models}

Cada posicionamento que não é um tile de solo é classificado pelo caminho do seu
mesh (vale a primeira correspondência):

| Categoria | O nome do mesh (ou o caminho, para árvores) contém |
|---|---|
| árvores (só com `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| rochas | `rock`, `cliff`, `boulder`, `stone` |
| lancis | `kerb`, `curb` |
| barreiras | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| placas | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| edificações | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infraestrutura | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| objetos de cenário | qualquer outro |

- Uma cópia é considerada se a sua origem estiver no corredor de alcance
  (`margin + 60 m`), e é desenhada se os seus limites tocarem o corredor.
- Os níveis de detalhe seguem [Níveis de detalhe e o orçamento](detail-budget.md):
  faixas de distância, e depois os modelos mais caros descem de nível para caber no
  orçamento. Onde nem os níveis mais grosseiros passam do limite, as cópias mais
  distantes são deixadas de fora, como no BeamNG, até caber. Os lancis mantêm
  o detalhe total e nunca são deixados de fora. O resumo imprime
  `placed on it (N triangles of a B budget)` e, quando alguma cópia foi retirada,
  `N copies left out to fit the budget, the furthest from the driving first`.
- Cada categoria é uma parte em cor chapada: `ground:kerbs` para os lancis, que
  são superfície de rodagem, como no Forza e no BeamNG, e `structure:<categoria>`
  para o resto:

| Categoria | Cor (RGB linear) |
|---|---|
| barreiras | 0.55, 0.52, 0.48 |
| placas | 0.75, 0.72, 0.65 |
| edificações | 0.62, 0.58, 0.52 |
| infraestrutura | 0.48, 0.48, 0.50 |
| rochas | 0.45, 0.43, 0.40 |
| objetos de cenário | 0.55, 0.45, 0.35 |
| árvores | 0.20, 0.32, 0.14 |
| lancis | 0.70, 0.25, 0.22 |

Malhas estáticas que não podem ser lidas (malhas esqueléticas, malhas só Nanite,
níveis que não são guardados inline) são contadas: `N meshes could not be read`.

## Verificações por trás disso {#checks-behind-it}

Conforme o código-fonte, no jogo instalado:

- Toda tabela de conteúdo é lida (versão 8).
- Toda célula de toda etapa abre, e cada componente de malha estática e de cena
  é descodificado terminando exatamente no fim nativo da sua classe.
- Quase toda malha estática amostrada é descodificada (o resto é esquelética). A
  extensão descodificada de um tile de estrada bate com os limites guardados nele.
- Os níveis de mip de uma imagem de satélite têm exatamente os tamanhos das suas
  entradas em bulk.
- Os tiles de um chunk de textura virtual são contabilizados até ao byte, e os
  tiles de estrada caem na estrada que ela mostra.

## Lacunas conhecidas {#known-gaps}

- As propriedades próprias dos componentes instanciados não são lidas (veja
  acima). O posicionamento deles presume a raiz do ator.
- Florestas geradas pelo PCG em tempo de execução não são guardadas nos ficheiros e
  não podem ser exportadas.
- Splines (muros invisíveis de respawn), componentes de decalque e as próprias
  texturas dos modelos colocados não são desenhados. Os modelos ficam em cor chapada.
- `--season` não tem efeito.
- Um patch do jogo pode mover os slots de propriedades. O leitor lança um erro em
  vez de ler errado, e a exportação informa quantos componentes falharam.
