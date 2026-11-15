---
title: Frostbite
nav_order: 5
lang: "pt"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, bundles, malhas e níveis {#frostbite-toc-cas-bundles-meshes-and-levels}

**Lê um nível do Battlefield 6 até ao seu terreno, às suas malhas colocadas e aos seus mapas de cor, e escreve-o como um `.glb`.** Os jogos Frostbite (Battlefield, Need for Speed, Dead Space) guardam o seu conteúdo em blobs `.cas`, descritos por tabelas de conteúdo `.toc`. A tabela de um nível diz quais os bundles que o nível carrega, os bundles nomeiam cada recurso, e os recursos dizem que malha está em cada sítio.

Fontes:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabelas, pacotes, cargas),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bundles e os seus manifestos),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(partições EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(campo de alturas),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(texturas e materiais),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(colocação e exportação).
Comandos: `identify`, `levels`, `level` (veja [Comandos](commands.md#levels-and-level-frostbite)).

Nada disto é documentado pelo jogo. Cada layout abaixo foi lido dos ficheiros e depois confrontado com todos eles, e cada secção diz qual foi a verificação. Onde as ferramentas de modding do Frosty descrevem versões mais antigas de uma estrutura, os nomes dos campos seguem os delas; não foi copiado código de nenhuma (veja [Regras e licenças](rules-and-licences.md)).

## O cabeçalho que parece cifrado e não está {#the-header-that-looks-encrypted-and-is-not}

| Marcador (u32, little-endian) | Significado | Tratamento |
|---|---|---|
| `0x00CED100` | simples: a árvore começa logo | lido |
| `0x01CED100` | assinado: uma assinatura de 556 bytes, depois a árvore **em claro** | lido |
| `0x03CED100` | ofuscado com XOR, com a chave no próprio cabeçalho do ficheiro | detetado e recusado |

A forma assinada é a que o Battlefield atual distribui. Os bytes de alta entropia depois do marcador são uma assinatura, não texto cifrado.

## A árvore DbObject {#the-dbobject-tree}

Uma só estrutura recursiva. Cada campo é um byte de tipo (os cinco bits baixos são o tipo, o bit 7 é "anónimo"), um nome opcional, e um valor. Os contentores trazem o seu comprimento como inteiro de comprimento variável e terminam com um byte zero. `parse_toc` verifica o comprimento de cada contentor, por isso um ficheiro que é lido foi entendido. `layout.toc` está nesta forma.

## Pacotes de instalação {#installation-packages}

Cada localização indica o **pacote de instalação** a que o seu blob pertence. Cada pacote numera os seus blobs a partir de `cas_01`, por isso o número do blob sozinho é ambíguo assim que está mais de um pacote instalado, o que acontece sempre.

- `layout.toc` lista os pacotes em `installManifest.installChunks`, cada um com um `persistentIndex` e um `installBundle` como `Win32/installation/<pacote>`.
- Os blobs do pacote estão nessa pasta, em `Data` para o jogo base ou em `Update/<pack>/Data` para o que veio depois.
- Um registo de localização traz o `persistentIndex` completo de 32 bits: a metade transfere da sua primeira palavra guarda a metade alta, a metade alta da sua segunda palavra guarda a metade transfere; a metade transfere da segunda palavra é o número do blob.

Verificação: cada localização em cada tabela binária de uma instalação resolve para um pacote declarado e cai dentro do blob que indica. Uma versão anterior tomava o primeiro `cas_NN.cas` com o número certo. Um terço das cargas que lia pareciam de alta entropia e eram tomadas por cifradas. Eram os desvios certos no ficheiro errado. Nada encontrado está cifrado.

## A tabela do nível {#the-level-table}

A tabela de um nível (`levels/<nível>/<nível>.toc`) é uma tabela de secções: quinze palavras de cabeçalho big-endian, depois secções colocadas umas a seguir às outras, cujos deslocamentos são indicados e também se podem derivar de duas contagens.

| Secção | Conteúdo |
|---|---|
| bundles | uma tabela de hash (uma palavra cada), depois um registo de 16 bytes por bundle: chave, `0x40000000` \| tamanho, 0, deslocamento |
| tabela de hash dos chunks | uma palavra por chunk |
| chunks | id de 16 bytes (o GUID do chunk com os **bytes invertidos**), depois uma palavra: `0x80000000` \| 4 x o índice da sua localização |
| localizações | quatro palavras big-endian: pacote (dividido), blob, deslocamento, tamanho |

Os ids dos chunks e as localizações estão **em ordens diferentes**. Lê-los na ordem do ficheiro emparelha cada chunk com os bytes de outro chunk, que se descodificam perfeitamente (sobretudo como som) e por isso não parecem errados até uma malha sair como ruído. Verificação: num nível, as palavras de índice são uma permutação de 0 até ao número de chunks menos um.

Os bundles estão guardados em linha depois da tabela de secções. Cada um tem nove palavras de cabeçalho big-endian, depois as suas entradas: oito bytes de deslocamento e tamanho, precedidos de mais oito que indicam o pacote e o blob quando o byte de flags da entrada tem o seu bit mais alto ligado. Verificação: em cada bundle, a última entrada acaba exatamente onde começam os bytes de flags.

### Qual tabela é o nível {#which-table-is-the-level}

Um nível pode ter várias tabelas com o mesmo nome: uma no `Data` do jogo base, uma em cada atualização (`Update/<pack>/Data`) que o traz ou o altera, e uma em cada pacote de alta resolução (`Update/<pack>/Data/Win32/installation/detail/<pacote>/...`). Só algumas têm bundles. Para um nível que uma atualização traz, a tabela do jogo base só tem chunks e nenhum bundle, e a da atualização é o nível; tomar a primeira tabela encontrada não exportava nada dele.

Por isso, o nível é a tabela com mais bundles, ganhando uma camada posterior em caso de empate (primeiro o jogo base, depois as atualizações por ordem de nome), e as tabelas do mesmo nome sem bundles são os seus **suplementos**: os seus chunks são acrescentados aos do nível, porque guardam os maiores mips das suas texturas. Um cabeçalho de textura nomeia esse chunk em +164 (veja [Texturas e materiais](#textures-and-materials)). `levels` indica de onde vem cada nível e quantos suplementos tem.

## Manifestos de bundles {#bundle-manifests}

A primeira entrada de um bundle é o seu manifesto, guardado sem compressão. É o formato binário de bundle dos jogos Frostbite anteriores, com um novo marcador `0xD68E799D`: contagens, SHA-1, registos ebx e res (deslocamento e tamanho do nome), tipos de res, metadados e ids, GUIDs de chunks, cadeias de texto. As restantes entradas do bundle são os ebx, os res e os chunks, por essa ordem. Verificação: as contagens batem com as entradas em cada bundle, e as cadeias de texto começam onde acabam os registos.

Os tipos de recurso são hashes. `0x49B156D4` é MeshSet (cada res desse tipo chama-se `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` lê tudo isto para um nível, em poucos segundos: um nível tem dezenas de bundles e dezenas de milhares de ebx, res e chunks.

## Blocos de carga {#payload-blocks}

```
[tamanho descomprimido : 4] [método : 2] [tamanho comprimido : 2]    big-endian
```

Um tamanho comprimido zero quer dizer guardado sem compressão, desde que descomprima para o mesmo tamanho.

| Palavra de método | Codec |
|---|---|
| `0x0070`, `0x0071` | nenhum |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), a partir da DLL `oo2core` do próprio jogo) |
| outro, com tamanhos iguais | copiado como está |
| outro | recusado |

Lida do pacote certo, cada carga amostrada descodifica.

## Partições EBX {#ebx-partitions}

O EBX guarda tudo o que não são dados em bruto. Cada partição é um ficheiro RIFF: `EBXD` (os dados, alinhados a 16), `EFIX` (GUID da partição, GUIDs de tipo e assinaturas, instância, ponteiro, deslocamentos de importação, de tipo-informação, as importações, e os deslocamentos de matrizes, valores em caixa e cadeias), `EBXX` (a tabela de matrizes: deslocamento, contagem, hash, flags, tipo do elemento). Um campo de ponteiro tem oito bytes: zero é nulo, um valor ímpar é a importação número `value >> 1`, qualquer outro valor é relativo ao campo.

A **biblioteca de tipos não é legível**. O jogo guarda-a no seu sistema de ficheiros inicial, que está cifrado, e este pacote não lhe toca. Os tipos são conhecidos pelo GUID e pela assinatura, que cada partição traz, e os poucos tipos de que a exportação do nível precisa foram desenhados a partir dos dados.

## MeshSet {#meshset}

Uma malha é um res MeshSet (a descrição) e um chunk por nível de detalhe (os buffers).

| Parte | Layout |
|---|---|
| prefixo | quatro palavras: tamanho do cabeçalho (176 ou 192), tamanho do registo de nível (176 a 188), tamanho do registo de secção (368), 0 |
| cabeçalho | caixa delimitadora; seis deslocamentos de nível i64; tipo de malha em `0x6C` (rígida, skinned, composta); contagens de nível e de secção em `0x9C` |
| nível | secções em `+0x08`; cinco listas de desenho em `+0x14` (opaca, transparente, decalque, só profundidade, sombra); formato de índice em `+0x54` (`0x21` u16, `0x2E` u32), bytes de índice e de vértice; GUID do chunk em `+0x74` |
| secção | nome do material; passo do vértice; triângulos, primeiro índice, deslocamento do vértice (em bytes), contagem de vértices em `+0x20`; declaração de vértice em `+0x64`: 16 x (uso, formato, deslocamento, stream), 16 passos de stream, contagens |
| chunk | o buffer de vértices, depois o buffer de índices. Os streams de uma secção seguem uns aos outros; os índices contam a partir do primeiro vértice da secção |

As posições são uso 1, stream 0, deslocamento 0, como quatro halves ou três floats. Só as secções opacas e transparentes são desenhadas. Cada secção chamada `..._shadow` está na lista de sombra e só aí, por isso são as listas que decidem.

Verificação: cada malha de um nível cujos níveis estão guardados em chunks descodifica, e quase todas têm 99% ou mais dos seus vértices dentro da caixa declarada; o resto falha por arredondamento de half-float. Uma caixa descodificada mede cerca de um metro, Y para cima, com as normais a apontar para fora.

## Colocação {#placement}

O pipeline de conteúdo reúne os objetos estáticos de cada sub-nível num **grupo de modelos estáticos**: uma matriz de membros, um por malha, cada um com as suas transformações de instância.

| Tipo (GUID, assinatura) | Layout |
|---|---|
| membro `ad13064e…`, `0xF861A878` | 224 bytes: `+88` matriz de transformações, `+112` o blueprint do objeto (importação), `+160` o recurso da malha (importação) |
| transformação `101dce06…`, `0x5E6D8C37` | 64 bytes: direita, cima, frente, translação, cada um um vec3 preenchido até 16 |

A partição do recurso da malha tem o nome do seu res MeshSet, por isso o GUID da partição da importação dá a malha. Um ponto cai em `x·right + y·up + z·forward + translation`. A transformação do próprio grupo era a identidade em todos os grupos dos níveis verificados, e não é aplicada.

Verificação: num nível, cada membro de cada grupo resolve para uma malha; a maioria das cópias tem uma rotação de determinante 1 com uma milésima de precisão, e o resto está escalado ou espelhado. Os GUIDs e assinaturas de tipo são iguais noutros níveis. Uma atualização do jogo que mude o layout muda a assinatura, e o leitor então não encontra nada em vez de ler mal.

### Objetos colocados um a um {#objects-placed-one-by-one}

O que o pipeline não consegue agrupar - objetos destrutíveis, contentores, detritos - é colocado por **referências de objeto** e **referências de prefab** nas partições do nível:

| Tipo (GUID, assinatura) | Layout |
|---|---|
| referência de objeto `a9a6a6ad…`, `0xC4856BEC` | `+32` a transformação (como acima), `+112` o blueprint do objeto (importação) |
| referência de prefab `117c746e…`, `0xDE3FE9B4` | o mesmo; o blueprint é um prefab, uma partição de mais referências |

Os prefabs aninham-se; uma cópia cai na sua própria transformação vezes a transformação do pai (vetores de linha), até oito níveis. Um blueprint de objeto é desenhado como as malhas que importa, deixando de fora os estados destruídos (`dc_...`). Um prefab agrupado é referenciado pelo seu resto `..._nongroupable_autogen`, para que nada seja desenhado duas vezes.

A travessia começa só a partir dos mundos e camadas do nível. Uma partição cuja primeira instância é um blueprint de prefab (`134919fc…`, `0x0247807D`) é a definição de um prefab, e um nível guarda muitas delas na sua própria pasta, colocadas pelos seus mundos de outras maneiras que não estas referências; percorridas como se fossem um mundo, um prefab põe o seu conteúdo nas coordenadas locais. Isso amontoa centenas de cópias em volta da origem do mundo, bem abaixo do chão. Mundos e camadas têm `a10ebe0f…`, `0xD3D16C3C` como primeira instância.

Os blueprints retirados de jogo não são seguidos: recursos de desenvolvimento e de teste (`game/dev/`, `test/`), o conjunto da cinemática de fim de ronda (`..._gameend_...`: posto em cena abaixo do chão) e o controlador da câmara de morte (`.../deathflow/...`, cujos gadgets ficam na origem do mundo). São reconhecidos pelo caminho do recurso, não pela camada: a mesma camada que tem o conjunto da cinemática pode colocar as paredes e os telhados reais de um nível. Depois das duas regras, nenhuma cópia dos níveis verificados fica a mais de 10 m abaixo do terreno, e as cópias ficam sobre o terreno onde o jogo as mostra.

**Níveis de detalhe que fazem de substituto.** O último nível de detalhe de uma malha pode mudar para um substituto de vista distante com um material próprio: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Uma torre de treliça com dezenas de milhares de triângulos pode acabar numa silhueta de algumas centenas, que o orçamento escolheria e que, de perto, é um espigão sólido. Um nível de detalhe que traz um desses materiais, que o seu nível mais fino não tem, nunca é escolhido; o mais grosseiro da malha é o último real.

## Terreno {#terrain}

Fonte: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

O terreno é um res TerrainStreamingTree (tipo `0x22FE8AC8`) e os chunks que ele nomeia.

| Parte | Layout |
|---|---|
| cabeçalho | 34 bytes; a contagem de nós em 25 |
| árvores raster | um byte de tipo e um u32 de comprimento cada, até um byte de tipo `0xFF`. O tipo 0 é o campo de alturas: amostras por lado em +5 (265), intervalo de altura em +21 (1.280 m), o quadrado de terreno no primeiro registo de nó em +77 (8.192 m no nível verificado). Guarda as caixas delimitadoras dos nós e uma pirâmide min/max de 16 x 16 por nó, não as alturas |
| nós de streaming | a quadtree, em profundidade primeiro: tamanho do chunk e GUID; um segundo chunk opcional; um byte de flags (bit 0: o chunk começa com uma página de alturas); tem filhos. Os filhos na ordem (0,0), (1,0), (1,1), (0,1) |
| página de alturas | os primeiros 265 x 265 u16 do chunk de um nó com flag, linha a linha; altura = valor x 1.280 / 65.535 m; colunas ao longo de x, linhas ao longo de z, a partir do canto baixo do nó; uma margem de 4 amostras, por isso 256 células por nó |

Cada passo foi verificado por si só:

- A análise da quadtree de nós consome o res até ao último byte, com os 529 nós declarados.
- Nós vizinhos partilham exatamente as suas nove colunas de borda, por isso o passo é 256.
- As amostras de um filho em cada outra posição são iguais às do seu pai, com uma margem de 4, e ficam a 90 a 700 unidades de diferença com qualquer outra margem.
- A palavra mais transfere do nível descodifica para a altura mínima da caixa delimitadora, ao centímetro.
- Das oito maneiras como o quadrado poderia assentar no mundo, só x ao longo de x e z ao longo de z põe os objetos colocados sobre ele: metade das cópias amostradas a cerca de 2 m, contra várias vezes isso para qualquer das outras.

Os objetos colocados depois medem o resultado. O ponto mais baixo de cada cópia, contra o terreno por baixo (bilinear, a partir do nó mais fino):

| Colocado | Distância mediana | Mediana com sinal |
|---|---|---|
| árvores e arbustos | bem abaixo de um metro | ligeiramente abaixo da superfície |
| adereços | um ou dois metros | sobre a superfície |
| rochas | cerca de um metro | afundadas cerca de um metro |
| edifícios | vários metros (assentam em fundações) | ligeiramente afundados |

A vegetação é colocada sobre o chão e em mais lado nenhum, o que a torna a verificação mais exigente: as suas origens ficam a uma mediana de 0,07 m da superfície. Os edifícios espalham-se mais porque a categoria inclui paredes, pisos e peças de kit de estruturas de vários andares e subterrâneas. Deslocar o terreno 64 m para o lado faz cair a parte das cópias a menos de 0,5 m de 29% para 10%.

`level` desenha o campo de alturas como `ground:terrain`, cada parte dele a partir do nó mais fino com alturas aí e não mais fina que `--ground-spacing` (4 m por omissão: 3,7 milhões de triângulos para o nível verificado, cujos nós mais finos são de 0,5 m). Peças de resoluções diferentes encontram-se com pequenos degraus; nada os costura.

O chunk de um nó também tem as páginas das máscaras de camadas depois da sua página de alturas, e o seu segundo chunk acaba com o mapa de cor do nó (veja [Camadas do terreno](#terrain-layers)).

## Camadas do terreno {#terrain-layers}

O jogo sombreia o terreno perto de um jogador espalhando materiais de superfície em mosaico através de máscaras pintadas, com um mapa de cor por cima, e desenha decalques (estradas, remendos de asfalto, marcações de pista) por cima. O próprio relato da Frostbite sobre o sistema (Widmark, "Terrain in Battlefield 3", GDC 2012) lista os rasters do terreno como o campo de alturas, máscaras de splatting do sombreador, um mapa de cor "usado como sobreposição por cima do splatting do sombreador", materiais de física, uma máscara de profundidade de destruição, um mapa de albedo para a luz refletida e canais de máscara adicionais; os tiles de um raster trazem uma margem para os algoritmos de renderização. A árvore de streaming dos níveis verificados tem sete árvores raster, dos tipos 0, 1, 2, 4, 5, 7 e 8, cujos cabeçalhos começam pelo tamanho do tile: 265 para o campo de alturas (tipo 0) e o tipo 2, 72 ou 66 para as máscaras (tipo 1), 132 com uma margem de 2 para o mapa de cor (tipo 4), 260 com uma margem de 2 para o tipo 5.

**A lista de camadas.** O res `....layergraphs` do terreno lista uma entrada de 32 bytes por camada, pela ordem em que os registos de máscara as numeram (34 entradas, 34 secções de depósito e índices de camada de 0 a 33 num nível); o id de cada entrada termina com a sua chave de secção no depósito de blocos de sombreador do grafo de camadas (`....layergraphs_shaderblockdepot`), cujo bloco nomeia os mapas da camada: um mapa de cor `_cv`, mapas `_nhs` e `_ao` por superfície, mais mapas partilhados de detalhe e ruído. Muitas camadas não nomeiam mapa nenhum: são fontes que o grafo de camadas lê. A cor de uma camada é a média do seu mapa `_cv`; a escala de repetição não é encontrada. O ativo do terreno termina com uma entrada de cinco bytes por camada (um byte, depois um u32 com o índice da camada ou -1).

**As máscaras.** O raster 1 é a quadtree das máscaras. O seu corpo começa com 59 bytes, o lado da página em 0: 72 onde as páginas são BC4 (72 x 72, 2.592 bytes), 66 onde são de oito bits sem compressão (4.356 bytes). Depois vem um grupo por nó, em profundidade primeiro:

| Parte | Layout |
|---|---|
| grupo | u16; u16 contagem de registos; u32 contagem de páginas; os registos; um byte zero. Um grupo sem registos ocupa 7 bytes no total |
| registo | 33 bytes: u16 camada, u16 hash, a caixa do quadrante (quatro floats), dois bytes de flags, uma pirâmide de presença de 85 bits |

Os registos de um grupo são os quatro quadrantes do seu nó, camada a camada, os quadrantes de cada camada na ordem (0, 0), (1, 0), (1, 1), (0, 1). Um registo com a segunda flag ligada cobre o seu quadrante por inteiro e não tem página; um sem ela tem a página seguinte; um quadrante sem registo de uma camada que o seu grupo nomeia está vazio dessa camada; a primeira flag está desligada exatamente quando a camada continua no próprio grupo do quadrante, um nível abaixo, que a substitui aí. A contagem de páginas é o número de registos com página.

As páginas: as páginas do próprio grupo de um nó de streaming seguem, no seu chunk, a página de alturas, uma secção de 16 bits de 4.358 bytes e um raster de 67 x 67 de oito bits (a partir do início do chunk quando não tem página de alturas); o seu segundo chunk guarda as páginas dos grupos dos seus quatro quadrantes um nível abaixo, os quadrantes na ordem do mapa de cor, depois o próprio mapa de cor. Uma página é os 64 x 64 texels do quadrante, com as linhas ao longo de z e as colunas ao longo de x, com uma margem copiada dos vizinhos: 4 texels numa página BC4, 1 numa sem compressão.

As margens provam a colocação sem juízo: duas páginas de uma camada lado a lado têm de trazer os texels de borda uma da outra. `read_masks` verifica isso para cada par que coloca, e recusa um nível onde menos de 99% concordem. Cerca de um terço dos níveis verificados são lidos, com as margens a concordar; alguns não têm máscaras pintadas; os restantes são recusados, quase todos pela verificação (os chunks dos seus nós guardam mais do que este layout conhece). O chão de um nível recusado toma a cor média dos seus materiais de superfície, e a exportação diz porquê. As margens viradas para um quadrante cheio são 255 e as viradas para um vazio 0.

A secção de 4.358 bytes e o raster de 67 x 67 antes das páginas não são lidos: os seus valores estão numa faixa alta e estreita, sem valores pequenos nem sentinela.

**A cor do chão.** O grafo de camadas mistura as camadas num grafo de sombreador compilado de máscaras, inclinação, altura e ruído, que não é lido. `--ground-texture` colore o chão por uma regra própria, dita aqui como tal:

- as camadas com mapa de cor com nome de distância são os stand-ins de vista distante e ficam de fora;
- as camadas texturizadas que cobrem nove décimos ou mais do terreno são a base. As suas máscaras estão cheias quase em todo o lado, por isso onde cada uma fica é escolha do sombreador, não delas: as que têm nome de rocha ou falésia colorem declives mais inclinados que 40 graus, as que têm nome de gravilha colorem o chão plano (as outras camadas base quando não há nenhuma), misturadas entre 20 e 40 graus pelo declive do campo de alturas (tomado de 4 em 4 m e espalhado bilinearmente pelos texels cozidos: repetido em blocos de 4 m, desenhava a cor rochosa em manchas de bordas duras);
- cada outra camada texturizada é posta sobre a base pela sua própria máscara, pela ordem das camadas;
- o mapa de cor é posto sobre o resultado como o motor o faz, o dobro da cor do chão vezes o mapa, para que o cinzento médio o deixe como está; onde o mapa de cor não tem texels, o chão toma o brilho mediano do mapa, em cinzento.

Comparado com a cor mediana do chão em frames de jogo de três níveis (crominância como vermelho e azul sobre verde): a área de jogo cozida dá 1,00 / 0,69 contra os 1,19 / 0,78 dos frames num, cujas camadas de relva são verdes onde os frames mostram relva seca; 1,19 / 0,82 contra 1,01 / 1,04 noutro, cujo próprio mapa de cor é quente (1,13 / 0,88); e 1,05 / 0,91 contra 0,93 / 0,92 num terceiro sem mapa de cor. Os frames são iluminados e com gradação, por isso isto mede o tom, não o brilho.

**O mapa de cor.** O segundo chunk de um nó tem, depois das páginas de máscara dos grupos dos seus quadrantes, quatro páginas BC7 de 132 x 132 (17.424 bytes cada), uma por quadrante do nó, na ordem (x baixo, z alto), (x alto, z alto), (x alto, z baixo), (x baixo, z baixo). A árvore de máscaras diz quantos bytes ocupam as páginas de máscara, por isso o mapa de cor é encontrado pela contagem, não pelo fim do chunk: num nível os nós mais grosseiros trazem mais quatro dessas páginas depois dele, outro raster numa cor lisa, e ler as últimas quatro páginas do chunk perdia o mapa de cor em nove décimos do terreno. Sem essa contagem o mapa de cor também se perdia nos níveis com páginas de máscara sem compressão, cujas páginas não são um número inteiro de páginas BC4; o mapa de cor de um nível foi de 0,4 para 0,94 do seu terreno. A ordem foi ajustada: contra as bordas de cada campo de alturas de quadrante, cada página dos nós com características corresponde a um quadrante, sem rotação, com 0,3 a 0,54, onde a próxima melhor colocação fica abaixo de 0,2. Assim colocadas, as páginas de um nível juntam-se sem costura nas estradas, água e zonas construídas do nível de teste, a 0,5 m por texel na área de jogo. Onde as camadas fazem o trabalho, o mapa de cor é quase neutro (mediana 110, 107, 104); noutros sítios pode trazer cor forte. Um nível cujos segundos chunks só têm páginas de máscara sem compressão não tem mapa de cor lido. Uma versão anterior deste leitor chamava a estas páginas não geográficas: comparava-as com o mapa de fundo, que pode ser outra paisagem por completo, e colocava cada página no nó inteiro em vez de num quadrante.

**A albedo da luz refletida** foi procurada e não encontrada: os chunks dos nós da raiz e do primeiro nível são páginas de máscara inteiras, e a carga do tipo 5 não é localizada.

**Buracos.** O ativo de terreno de um nível (res tipo `0x1CA38E06`) nomeia três sombreadores: um sombreador de superfície padrão, um sombreador de buracos e um sombreador de fonte padrão. Não se encontrou que camada o sombreador de buracos lê, por isso o campo de alturas não é cortado. Num nível, a malha de navegação pode correr sobre malhas de rocha dezenas de metros abaixo do campo de alturas, onde o jogo as devia ter cortado. Procurado e não encontrado aí: a máscara de uma camada, o raster de 67 x 67, uma altura reservada (nenhuma página de alturas do nível contém 0 ou 65.535) e uma flag de nó (todo o nó abaixo da raiz tem flags 1). O que sobra são os rasters 7 e 8. Ambos têm codificação de comprimento de execução: um byte igual ao anterior é seguido de uma contagem de cópias adicionais (`ff ff 84` são 134 bytes de 255). O 7 (tile 256, uma quadtree completa de cinco níveis, quatro bits por amostra) descodifica para pares de bytes com valores de 0 a 3; o 8 (tile 265) para bytes sobretudo a 255, com os outros valores em séries regulares. Nenhum dos seus tiles está ainda colocado, por isso não se sabe se algum guarda os buracos.

**Os decalques** são lidos e cozidos; veja [Decalques do terreno](#terrain-decals).

## Decalques do terreno {#terrain-decals}

Fonte: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Estradas, pistas de aterragem, placas de betão, linhas e letras pintadas, marcas de pneus: o res `TerrainDecals` (tipo `0x15E1F32E`) guarda-os como geometria plana que o jogo estende sobre o terreno.

| Parte | Layout |
|---|---|
| cabeçalho | em +16 uma contagem de ranhuras n, depois n ranhuras de 16 bytes, depois a contagem de registos |
| registos | um por lote de desenho, um a seguir ao outro, de comprimento variável: 156 bytes de campos fixos - primeiro vértice em +32, contagem de triângulos em +36, mosaico da textura em metros em +44 - depois os bytes de vértices do lote (deslocamento, tamanho), depois uma cauda que nomeia as suas texturas pelos GUIDs de partição dos seus recursos |
| vértices | 32 bytes: x, z (f32), 8 bytes compactados, u, v (f32), r, g, b, a (f16); cada lote é uma lista simples de triângulos |
| índices | u32, a contar do 0 em cada lote; não são necessários |

Verificações:

- os intervalos de vértices dos registos seguem-se uns aos outros sem falhas e cobrem exatamente todos os vértices, e o primeiro vértice de cada registo x 32 é o seu deslocamento;
- lidos assim, os triângulos são decalques compactos (letras, tiras de linha, remendos); lidos com um vértice de desvio, são fatias atravessando o mapa;
- quase todos os lotes nomeiam texturas na sua cauda: um mapa de cor (`_cv`) com um mapa de opacidade (`_op`, canal vermelho), ou, para marcações, uma máscara de canais (`_rgb`).

Depois dos GUIDs de textura, a cauda traz os parâmetros de material do lote, codificados como os de um bloco de sombreador (veja Tons abaixo). A cor de tinta de uma marcação, de uma faixa de pneu ou de uma linha é o float3 com hash `607e`: um 0,64, 0,56, 0,48 arenoso para as faixas de pneu na areia, quase preto para o alcatrão. Os mapas de opacidade são sobretudo do formato 62, um canal a 8 bytes por bloco, lidos como BC4.

Um lote mapeia a sua textura ou pela posição no mundo (u = x, v = z, a textura repetindo-se a cada metros de mosaico: asfalto, betão, gravilha) ou de 0 a 1 através do decalque (uma linha, uma letra, uma faixa de pneu). Os registos são desenhados pela ordem do ficheiro.

**A cozedura.** `level --ground-texture M` pinta, sob a extensão dos decalques e em tiles de no máximo 4.096 pixels, o mapa de cor do fundo (bilinear) e depois cada lote por cima, pela sua opacidade × o alfa do vértice. A cor dos vértices não é usada: alguns vértices de lotes são verde ou azul puros, o que tingia as marcações de um nível dessas cores. Os triângulos do campo de alturas ali tornam-se partes `ground:terrain x<x> z<z>` que levam o tile. Cada lote desenha-se assim:

| Os nomes do lote | Desenhado como |
|---|---|
| um mapa de cor (`_cv`) | o mapa, pela sua opacidade |
| um mapa de multiplicação (`_mult`) e um mapa de opacidade | a tinta (branca onde o material não indica nenhuma) vezes o mapa de multiplicação, pela opacidade: a linha central gasta de uma pista, as linhas de borda e as barras de soleira |
| uma máscara de canais (`_rgb`) | a tinta, senão branco para linhas e letras, escuro para contornos, um escurecimento leve para desgaste, marcas de pneus, manchas, poças e humidade, pela máscara |
| um mapa de opacidade sozinho, com uma tinta | a tinta pela opacidade: faixas de pneu |

Um mapa de variação de estrada não é tinta, mas varia a superfície por baixo dele, a centenas de metros de distância, e não é desenhado, seja qual for a sua tinta: pintado de branco, traçou dois retângulos pálidos de 150 a 250 m nas encostas de um nível. O mapa `_mult` é tomado como o próprio desgaste da tinta, não como um escurecimento do chão por baixo: está quase branco, e a forma da linha está no mapa de opacidade.

Quase todos os lotes são desenhados, em poucos tiles a 0,5 m por pixel; a exportação cresce uns MB e demora uns segundos a mais. Vistos de cima, os acessos, as pistas de táxi e a rede de estradas ficam sob as vedações e edifícios dos complexos e levam às suas entradas.

Desenhados como geometria própria, os decalques precisariam de mistura alfa, que o escritor não suporta, e um desvio acima de um terreno entraria em conflito de profundidade com ele; cozê-los mantém-nos na cor do próprio chão.

## Texturas e materiais {#textures-and-materials}

Fonte: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Um res Texture (tipo `0x6BDE20BA`) é um cabeçalho de 180 bytes: tipo e formato de pixel em +8, largura e altura em +22, contagem de mips em +30, o GUID do chunk em +40, quinze tamanhos de mip em +56. O chunk é a cadeia de mips, do maior para o menor. Alguns chunks não têm os seus maiores mips, que vêm num pacote de alta resolução; o comprimento do chunk diz a partir de que mip começa. O chunk desse pacote é nomeado em +164; é lido a partir dos [suplementos](#which-table-is-the-level) do nível quando se quer um mip que falta ao chunk principal, e o seu comprimento mais o do chunk principal é a cadeia completa.

| Formato | Descodificado como | Prova |
|---|---|---|
| 67, 66 | BC7 (sRGB, linear) | a folha de cor de um tanque de plástico descodifica-se assim; como BC3 os mesmos bytes são ruído |
| 61, 60 | BC3 | uma folha de caixote descodifica-se limpa como BC3, não como BC1 nem BC7 |
| 57, 56, 55 | BC1 | meio byte por pixel |

O recurso da malha não nomeia nenhuma textura. A ligação está nos **depósitos de blocos de sombreador** do nível (res tipo `0x73312045`, um por sub-nível), indexados pelos oito bytes em +0x130 do registo de uma secção de malha:

| Parte | Layout |
|---|---|
| tabela, em 16 | (chave de secção u64, deslocamento do descritor u64), até um deslocamento cair fora do res |
| descritor | (deslocamento do bloco u64, hash u64, tamanho do bloco u64) |
| bloco | os parâmetros de sombreador da secção; cada textura é um registo de 49 bytes: um byte, 16 bytes, o GUID de partição do recurso da textura, o seu GUID de instância |

A chave de secção do caixote aparece uma vez em cada um dos dez depósitos dos sub-níveis que o colocam, e o seu bloco nomeia `t_mil_crate_03_cs` e `_nmt` entre os mapas partilhados de detalhe. Um bloco nomeia cada textura que o sombreador amostra, e não se diz qual é o mapa de cor: é escolhido, uma textura 2D sRGB cujo nome tem a maioria das palavras do nome do material (`M_ConcreteWall_01`: concrete, wall), depois as da malha, depois uma que não seja um detalhe, decalque (`t_de_...`) ou mapa de dano, depois a que menos blocos usam. O bloco de um sinal de estrada nomeia o seu painel `t_com_highwaysignage_01_cs` e uma folha de decalque `t_de_com_highwaysignage_01_ca` com um escudo deitado de lado; ambos correspondem às palavras, e sem a regra do decalque a folha ganhava pelo uso e o sinal mostrava o escudo executado um quarto, em todos os conjuntos de coordenadas de textura que a secção tem. Os campos de distância com sinal (`..._sdf`), as paletas e as máscaras de canais (`_rgb`) nunca são escolhidos, seja qual for o que partilham em palavras (os `_rgba` são: quase todos são cor com alfa, e deixá-los de fora trocou o mapa próprio de um poste de alta tensão e de uma escada por outros sem relação); o atlas de vegetação de um cenário de fundo `..._atlas_a_sdf`, desenhado como cor, mostrava estrelas pretas e brancas nas árvores, a paleta de edifícios de um cenário de fundo era uma confeti de amostras nas paredes, e o vidro partido desenhado pela sua máscara de canais saía ciano. Uma secção cujos únicos candidatos são mapas de detalhe partilhados fica com cor lisa.

**Paletas.** Os edifícios de um cenário de fundo tiram as suas cores de uma paleta, de 256 x 256 texels de amostras de 16 x 16: cada vértice traz quatro bytes (uso `0x1E`) cujos dois primeiros dizem onde, na paleta, está a sua cor, x e y de 0 a 255. `level` desenha essa secção com a paleta como textura, cada vértice no centro da sua amostra. Assim desenhados, os blocos de fundo de um nível saem como paredes pastel, terracota e janelas escuras, onde eram brancos lisos.

**Sobreposições.** Os objetos grandes emparelham uma folha de acabamento através das suas primeiras coordenadas de textura e põem uma sobreposição por cima através das segundas, que ficam entre 0 e 1: um desdobramento do objeto inteiro. A sobreposição (`..._overlay_cs`, com a sua máscara `..._overlay_a`) traz o aspeto do objeto de longe, as faixas vermelhas e a ferrugem de um tanque de óleo; desenhados só com a folha de acabamento, os tanques de um nível saíam como painéis cinzentos. Uma secção cujo bloco nomeia uma sobreposição com a sua máscara, e cujas segundas coordenadas são esse desdobramento, é desenhada com a sobreposição por elas (36 secções nesse nível).

**Tons.** Muitos mapas de cor são cinzentos (as médias dos seus canais a menos de 6% umas das outras): o sombreador pinta-os com cores dos parâmetros do bloco. Depois das suas entradas de textura (49 bytes cada), um bloco lista os seus parâmetros, cada um com uma etiqueta de tipo (`f11af825` um float3, `a5e1f2de` um float4, `c1b1a014` um float, `4a4fc3a1` um inteiro), os bytes de flags `01 80` para um valor, um hash de dois bytes do nome do parâmetro, uma contagem u32, o valor e um id de oito bytes. Os nomes não são guardados. Sete hashes de nome float3 atuam como tons: num nível, três deles guardam uma cor em cerca de 1 bloco em cada 6 cujo mapa é cinzento e quase nunca onde o mapa tem cor própria, e os outros guardam as cores com que um mapa cinzento é pintado quando o nome do material o indica (o friso `..._blue` de uma ponte: 0,047, 0,098, 0,171 contra um neutro de 0,5). Uma família pode ter vários valores, um por canal de uma máscara, a maioria neutros, e um valor com um canal quase vazio (verde puro em fachadas de tijolo) escolhe um canal da máscara em vez de pintar. `level` multiplica um mapa de cor cinzento, em luz linear, pelo primeiro valor de cada família que não é neutro nem esse selector, sobre o seu valor neutro, e guarda o resultado como textura própria; um mapa com cor fica como está. A regra é a do próprio exportador: não se lê qual canal de uma máscara recebe qual tom. Num nível, isto baixou a parte das estruturas desenhadas perto de branco de 19,4% para 3,9%.

**Variações de objeto.** Uma malha é colocada em vários aspetos: uma parede de armazém com uma lista vermelha ou azul e um número diferente pintado, um contentor em verde ou cinzento. Cada cópia colocada nomeia o seu aspeto:

| Onde | Campo |
|---|---|
| membro de grupo de modelos estáticos | +32: uma matriz de um ponteiro por cópia, para uma variação de objeto ou nulo |
| referência de objeto | +120: um ponteiro para uma variação de objeto ou nulo |
| variação de objeto (partição `ov_...`, tipo `235f2a9c...`) | a sua primeira instância +32: o hash de nome u32 da variação |

O aspeto de uma secção numa variação é o bloco de sombreador indexado pela própria chave da secção com o hash da variação somado aos primeiros quatro bytes, como u32 little-endian (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); uma secção sem bloco sob essa chave tem o mesmo aspeto em todas as variações. As bases de dados de variação de malhas do nível (`meshvariationdb_win32`) listam, por malha e hash de variação, os materiais que cada variação toca, mas não as chaves. A regra foi encontrada a partir das próprias chaves e vale para todas as secções com variantes verificadas (as quatro variações de uma parede, três das suas secções cada). O bloco de uma variação traz as suas próprias texturas além dos seus tons: o número pintado na parede é uma folha de letras que o bloco da variação nomeia. Uma grande parte das cópias agrupadas é colocada numa variação.

Um bloco é cozido uma vez para cada conjunto de conteúdo, e a entrada do depósito para uma chave traz um hash deles (o segundo u64 da entrada). Quando uma secção não tem bloco sob a chave da sua variação, a variação ainda lhe chega por um *gémeo*: outra secção cujo bloco por omissão tem o mesmo conteúdo e que tem um. Sem gémeos, uma parede cujos comprimentos partilham um bloco por omissão pode sair em duas cores. Uma secção sem variante própria toma a variante que a maioria dos seus gémeos tem.

**Malhas destrutíveis.** Uma malha que uma partida pode derrubar tem ao lado um ativo de destruição com o seu próprio nome (`.../br_x.destruction` para `.../br_x_mesh`): os edifícios e paredes destrutíveis (`br_`) e muitos adereços. `level` guarda as suas superfícies em partes próprias, com o nome ` (destructible)`, cujos nós glTF levam `{"destructible": true}`. Os seus estados destruídos são as malhas `dc_..._part<N>_mesh` ao lado delas, cada uma centrada na sua própria origem; onde está cada peça fica no ativo de destruição, que não é lido, por isso os estados destruídos não são exportados.

**Deixado de fora.** Secções de materiais de blockout provisórios (`M_Whitebox`: alguns triângulos grandes sem textura que alguns edifícios guardam ao lado das suas superfícies, que saíam de um nível como barbatanas brancas), malhas feitas para cinemáticas (um helicóptero colocado onde a sua cena começa) e auxiliares de luz (planos que bloqueiam a luz, nunca desenhados). Os edifícios de fundo gerados de um nível (`..._generated_blueprints_..._mesh`) são desenhados, mas as suas paredes têm nomes de materiais que só trazem mapas de ruído e os seus vértices não trazem cor, por isso ficam lisos. Quase todas as secções desenhadas recebem um mapa de cor.

**Folhas de letras.** O número pintado numa parede, ou a impressão de um cartaz de uma grua, é uma secção própria cujo mapa de cor é uma folha (`_ca`): o alfa de uma letra sobre tinta sólida, ou uma impressão. As suas primeiras coordenadas de textura põem em mosaico o reboco da parede pelo painel (u de -0,2 a 1,7 numa parede), o que desenha a folha quase duas vezes; o quarto conjunto (`0x24`, senão o terceiro, `0x23`) põe-na exatamente uma vez (u de -1 a 0, v de 1 a 2, com umas milésimas a mais nos níveis de detalhe mais grosseiros). Quando o primeiro conjunto deixa uma cópia da imagem e o quarto ou o terceiro cai dentro de uma, a folha é desenhada através desse, deslocada para 0 a 1. Uma folha com alfa é desenhada 1 cm à frente da superfície onde está pintada, que é desenhada por baixo na outra cor de mapa do bloco, através do primeiro conjunto: sem isso, os texels vazios da folha mostravam o interior da parede. O segundo conjunto é o desdobramento de um objeto para a sua sobreposição e não é usado aqui.

**Mapas recortados.** O quarto canal do mapa de cor significa coisas diferentes segundo o nome do mapa. Em `_cs`, de longe o mais comum (893 dos mapas escolhidos de um nível), é suavidade: 1% do alfa de um mapa mediano fica a 0,1 de 0 ou 1. Em `_cu` (folhas, relva) e `_ca` (cor e alfa) é opacidade: 90% e 87%. Um mapa de cor com nome `..._cu` ou `..._ca` cujo alfa tem pelo menos 75% perto de 0 ou 1, pelo menos 1% abaixo de 0,5 e pelo menos 5% acima é escrito com o seu alfa, como PNG, e o seu material como `alphaMode` MASK do glTF, `alphaCutoff` 0.5, dos dois lados; assim as cartas de folhas mostram folhas, e não os seus cantos pretos. A mapa de folhas de uma árvore não tem alfa nenhum (4 de 255 no máximo): as suas frondes são recortadas pela geometria, e com só as duas primeiras condições a copa inteira era cortada.

As coordenadas de textura são o uso de vértice `0x21`, dois halves (formato 6) ou dois floats (formato 2). As secções trazem até mais três conjuntos (`0x22` a `0x24`) para camadas de decalque e de detalhe. As coordenadas põem-se em mosaico: o lado com nervuras de um contentor vai de -1,6 a 1,8, os azulejos do cenário de fundo do terreno ficam todos fora de 0..1, e num nível 23% dos triângulos texturizados chegam fora de 0..1. São escritas como estão, com um amostrador que repete; o visualizador do 3DHeat envolve cada textura que se repete dentro do seu atlas. Um renderizador que as fixa em vez disso estica as nervuras para o dobro da sua largura, transforma um piso de betão em riscas ao longo de um eixo, e dá às vigas de aço de uma torre a cor da borda da sua textura; para ele, `--clamped-uvs` corta cada triângulo ao longo das linhas onde a sua textura se repete e move cada pedaço para 0..1 (veja [Formato de saída](output-format.md)). Depois disso, 0,03% dos triângulos texturizados, sobre os quais uma textura se repete mais de 16 vezes, chegam fora, e um triângulo que o corte transformaria em mais de 4 pedaços é desenhado na cor média da sua textura: a casca repete-se por cada ramo, e cortada, as árvores de um nível passaram de 6,4 para 24 milhões de triângulos.

O campo de alturas não tem mapa de cor próprio que se possa ler. Onde um dos mapas do cenário de fundo do terreno o cobre, é colorido a partir dele: as coordenadas de textura do cenário de fundo são uma função linear de x e z do mundo (99% dos vértices a menos de 0,001 dela; o mapa cobre um quadrado de 65.536 m, executado um quarto), e a mesma função dá as do campo de alturas. O nível traz os mips desse mapa de 2.048 px para baixo, por isso o campo de alturas recebe 32 m por pixel. A sua rocha escura fica nas encostas: a correlação entre escuridão e declive é 0,48, e no máximo 0,34 para as outras sete orientações.

Num outro nível, o cenário de fundo são oito tiles próximos e oito distantes à volta da área de jogo, cada um repetindo a sua própria textura pelo tile, e nenhum chega ao campo de alturas. Cada textura de fundo é ajustada por si, e quando nenhuma cobre o campo de alturas, toma a cor média que o fundo mostra a menos de um quilómetro do quadrado de terreno, sobre a qual `--ground-texture` coze os decalques. Um material de fundo é aquele cujo nome tem `TerrainBackdrop`, ou `BD_` e `Terrain` (`M_BD_<site>_Terrain..._Near`); ou uma malha de fundo (`bd_..._terrain<site>_04_far_mesh`) que traz um material de terreno simples (`M_<region>_Terrain<site>_04_Far`), que as duas primeiras regras falharam num nível e por isso coloriu o seu chão a partir das superfícies.

Onde nenhum mapa de fundo cobre o campo de alturas, porém, ele toma a cor média das próprias superfícies do terreno antes da média do fundo: os mapas de cor `_cv` que os blocos de sombreador do grafo de camadas nomeiam (27 num nível: areias, cascalhos, solos, relva, betão fendido), cada um calculado pela média, depois a mediana de cada canal, deixando de fora o sombreador de superfície padrão do motor. Um fundo pode ser outra paisagem por completo: num nível, a sua média (95, 99, 80 em sRGB) deu à terra da área de jogo um cinzento que o jogo não mostra. Com `--ground-texture`, essa cor é multiplicada pelo dobro do mapa de cor, o que deixa o cinzento médio como está, e é cozida com os decalques por cima de ambas as extensões, a dos decalques e a do mapa de cor.

Contra o jogo, a cor mediana do chão da área de jogo cozida de cada nível e de frames de jogo (linhas de 55 a 72% da imagem ao lado do HUD, 24 frames cada; sRGB; os frames são iluminados e com gradação, por isso as razões r/g e b/g são a comparação justa):

| Nível | Frames | Média do fundo | Agora |
|---|---|---|---|
| primeiro | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| segundo | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| terceiro | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

O primeiro foi corrigido; os outros dois estavam um pouco mais perto no matiz antes. Uma cor para um nível inteiro não pode estar certa em todo o lado; as máscaras é que estariam.

## Malha de navegação {#navigation-mesh}

Fonte: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Um nível traz uma partição por agente, `<nível>/dbt/<nível>_navmesh_layer_<n>`: num nível, a camada 0 é o soldado (1,8 m de altura, degrau de 0,18 m, raio de 0,4 m) e duas outras são veículos (3,5 e 10 m de altura). Cada partição tem duas matrizes:

| Matriz | Elemento |
|---|---|
| tiles | 28 bytes: u32 0, u32 hash, u32 0, u32 índice do chunk, u16 x do tile, u16 z do tile, u32 deslocamento, u32 tamanho |
| chunks | 20 bytes: o GUID do chunk, u32 tamanho |

Um tile são `size` bytes em `offset` no chunk `chunk index`, em little-endian, e disposto como o Detour (Recast Navigation) com um cabeçalho mais longo:

| Deslocamento | Conteúdo |
|---|---|
| 0 | `VAND`, versão 7 |
| 24 | contagens: polígonos, vértices, ligações, malhas de detalhe, vértices de detalhe, triângulos de detalhe, nós de volume delimitador, ligações fora da malha, o primeiro polígono fora da malha |
| 188 | altura do agente, degrau, raio |
| 200 | a caixa delimitadora do tile, seis floats |
| 232 | vértices: floats x, y, z, coordenadas do mundo |
| próximo limite de 8 bytes | polígonos, 32 bytes: u32, seis índices de vértice u16, seis vizinhos u16, flags u16, a contagem de vértices em +30, em +31 a área (seis bits baixos) e o tipo (os dois altos) |
| depois, compactado | ligações (16 bytes), malhas de detalhe (12: primeiro vértice de detalhe u32, primeiro triângulo de detalhe u32, contagem de vértices e de triângulos u8), vértices de detalhe (três floats), triângulos de detalhe (três índices e flags), nós de volume delimitador (16), ligações fora da malha (80) |

Em cada tile, estes somam ao byte o tamanho do tile, e as malhas de detalhe numeram os polígonos antes do primeiro polígono fora da malha.

Um polígono é plano entre os seus cantos; a sua **malha de detalhe** guarda a altura real da superfície sobre as saliências, rochas e degraus, e é o que se desenha. Um índice de triângulo de detalhe abaixo do número de cantos do polígono é esse canto; senão é o vértice de detalhe `first + index - corners`. Fazer leque com os polígonos põe muito mais triângulos debaixo do terreno e faz fatias longas; com as malhas de detalhe nenhum é mais longo que a diagonal de um tile de 16 m mais o degrau de uma subida.

O tipo 0 é chão, o tipo 2 pequenas manchas íngremes (cerca de 45 graus, um metro quadrado cada), o tipo 1 uma ligação entre superfícies: os seus cantos abrangem 125 m de altura ou mais e ficam fora do tile, alguns na origem. As ligações são deixadas de fora; o resto é desenhado pelas suas malhas de detalhe, ou em leque num tile sem nenhuma.

Verificações: os tamanhos dos chunks somam exatamente os dos tiles; cada vértice de superfície fica dentro da caixa do seu tile, com um metro de margem; quase todos os triângulos olham para cima. Um tile que falha é recusado e contado, e num desses níveis nenhum é aceite.

O que a malha do soldado cobre, visto de cima no nível de teste: o chão, os pisos, as escadas e alguns telhados, e não os topos dos contentores de carga. É o mapa que a IA tem de onde um soldado pode estar, o mais perto que os ficheiros chegam de onde os jogadores estão.

## Não implementado {#not-implemented}

- A lista de camadas do terreno, que mistura as suas camadas de superfície (veja [Camadas do terreno](#terrain-layers)): a cor do chão segue uma regra deste leitor, a partir das máscaras das camadas e do declive do campo de alturas, e os níveis cujas páginas de máscara não encaixam recebem uma só cor.
- Parâmetros de cor de materiais de decalque: as marcações através de máscaras de canais são pintadas numa cor neutra.
- Blueprints de objeto que não são malhas (lógica de jogo, efeitos, sons).
- Estados destruídos de malhas destrutíveis: os lugares das suas peças estão no ativo de destruição, que não é lido.
- As ligações da malha de navegação (saltos, escadas, saltos por cima) e as suas camadas de veículos.
- Níveis de malha guardados em linha no res (10 malhas num nível, gadgets), ossos e partes de malhas skinned e compostas, e normais (calculadas pelo escritor).
- Mapas de normais, rugosidade e outros; alfa que não seja recorte (vidro translúcido e decalques são desenhados opacos).
- Terreno com buracos: um sombreador de buracos é nomeado, mas não se encontrou o que lê (veja [Camadas do terreno](#terrain-layers)), por isso o campo de alturas não é cortado onde o chão percorrível corre por baixo dele.
- Que tom vai com que canal da máscara de um material: um mapa de cor cinzento leva o primeiro tom que não é neutro (veja [Texturas e materiais](#textures-and-materials)).
- Efeitos (caminhos `fx/`) e as malhas de cabos, cujas caixas delimitadoras têm dezenas de quilómetros; ficam de fora e são contadas no resumo.
- A forma de tabela ofuscada com XOR.
