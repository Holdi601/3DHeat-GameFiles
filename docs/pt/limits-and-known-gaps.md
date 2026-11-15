---
title: Limites e lacunas conhecidas
nav_order: 10
lang: "pt"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Limites e lacunas conhecidas {#limits-and-known-gaps}

O que a ferramenta não faz, o que faz só em parte, e onde o seu comportamento é
irregular. A maioria das lacunas são recusas deliberadas. Descodificar sem um ficheiro
para verificar produz uma saída que parece certa e não está.

## Jogos {#games}

| Jogo | Exportação de percurso | Por que não, ou até onde vai |
|---|---|---|
| Forza Horizon | sim | a cor do solo é uma interpretação (veja abaixo) |
| BeamNG.drive | sim | sem cobertura de solo; texturas repetidas de modelos achatadas |
| Assetto Corsa Rally | sim | modelos em cor chapada; ainda não testado numa volta gravada no jogo |
| Assetto Corsa EVO | **não** | todo o conteúdo está num único pacote ofuscado com uma chave, e esta ferramenta não recupera chaves |
| Battlefield 6 (exportação de nível, `level`) | sim, um nível inteiro | terreno, malhas agrupadas e individualmente colocadas e seus mapas de cor, a malha de navegação dos soldados, folhagem recortada; a cor do solo da área de jogo é grosseira (32 m por pixel, ou uma cor média); sem translucidez nem mapas de normal; malhas destrutíveis marcadas, seus estados destruídos não exportados |
| jogos Unreal 5 World Partition (exportação de mapa, `ue-map`) | sim, um mapa inteiro | o landscape é exato; os edifícios como as malhas HLOD simplificadas do mapa, não os modelos de detalhe total; corpos de água; sem folhagem, decalques nem cor do solo |
| Arma Reforger (exportação de mundo, `enfusion-world`) | sim, um mundo inteiro | o terreno nas suas próprias cores e o mar; edifícios, objetos e pedras como as caixas dos seus modelos, não os seus triângulos; árvores sob pedido (`--trees`), como caixas; sem lagos, rios nem entidades filhas |
| iRacing | **não** | as pistas vêm num formato protegido que não é alvo de extração de ficheiros |
| qualquer outro | **não** | não há leitor de percurso; reconstrua a partir da jogatina com o 3DHeat GameCapture, ou analise as voltas no separador Análise de corrida do visualizador sem um percurso |

## Motores e formatos {#engines-and-formats}

| Formato | Não implementado |
|---|---|
| Unreal `.pak` | versões anteriores à 8; índices só com hash de caminho (os nomes não podem ser recuperados); entradas na lista de overflow do índice (saltadas); descodificação do conteúdo de `.uasset`/`.umap` a partir de um pak |
| Unreal IoStore | contêineres cifrados (recusados, sem opção de chave); listagem de um contêiner sem índice de diretório (ele não nomeia ficheiros); pacotes versionados; malhas só Nanite e não inline; malhas esqueléticas; propriedades de classes sem esquema; propriedades de componentes instanciados (layout mudado na versão do jogo); malhas de spline e componentes de decalque |
| Unity | formatos anteriores a 22 (Unity 2019 e anteriores); ficheiros com árvores de tipos embutidas; malhas comprimidas; toda classe exceto `Mesh`, então nada de transformações, materiais ou cenas; `meshes` num bundle; `list`/`extract` (use `meshes`) |
| Frostbite | tabelas ofuscadas com XOR; o grafo de camadas do terreno (máscaras lidas em cerca de um terço dos níveis verificados); blueprints de objetos que não são malhas (lógica de jogo, efeitos, sons); malhas de nível não guardadas inline; mapas de normal e outros, alfa que não seja de recorte; buracos no terreno; a biblioteca de tipos (cifrada no sistema de ficheiros inicial, não tocada); um comando para listar ou extrair ativos isolados |
| Source 2 | recursos compilados (`.vmdl_c`, `.vtex_c`); a malha de navegação do CS2 (versão 36) |
| ForzaTech | formatos de posição que não sejam quatro shorts escalados; formatos de índice que não sejam u16; códigos de textura que não sejam 0, 9 ou 13; as camadas de material do shader do terreno; tangentes |
| BeamNG | malhas com skinning e de decalque; animação; cobertura procedural do solo; cenário na borda do mundo |
| landscapes do Unreal e mapas World Partition | landscapes cujos mapas de altura vivem nas células cozidas; camadas de edição e buracos; malhas de landscape Nanite; modelos de detalhe total colocados nas células; folhagem; materiais de landscape |
| Enfusion | triângulos de modelos (a geometria `.xob` é comprimida num layout não lido); `.edds` com cabeçalhos anteriores ao DX10; valores de objetos aninhados em ficheiros de mundo (saltados e contados); entidades filhas; lagos e rios gerados; `list`/`extract` num `.pak` |

## Comportamentos que vale conhecer {#behaviour-worth-knowing}

- **A cor do solo do Forza não é a do jogo.** A textura assada é desenhada a partir
  dos mapas de tiles que dizem *onde* estão o asfalto, a relva curta, o terreno
  áspero e a mata. Ela usa cores e sombreamento fixos, porque as camadas de material
  do próprio shader do terreno não são descodificadas.
- **`--no-textures` também tira a berma do Forza.** A divisão asfalto/berma
  usa a máscara de asfalto que vem com os mapas assados. Sem texturas, as faixas de
  estrada ficam inteiras como estrada.
- **Um orçamento informado só pode ser ultrapassado pelos lancis.** Os lancis
  (e os modelos de superfície de rodagem do BeamNG) nunca são simplificados nem deixados
  de fora, em nenhum jogo. Assim, um `--detail-budget` menor do que eles custam é
  ultrapassado só por eles; todo o resto é deixado de fora primeiro. Veja
  [Níveis de detalhe e o orçamento](detail-budget.md).
- **Opções que não se aplicam são ignoradas em silêncio**: `--season` para BeamNG e
  AC Rally, `--track` para BeamNG e AC Rally, `--level`/`--install` para o Forza.
- **A cor do solo de um nível do Battlefield 6 é grosseira longe dos seus decalques.**
  O heightfield é colorido pelo mapa de cor do pano de fundo do terreno, a 32 m por
  pixel no maior mip que o nível traz; onde nenhum mapa de fundo cobre, pela cor média
  dos materiais de superfície do terreno. `--ground-texture` multiplica isso pelo
  mapa de cores do terreno (a 0,5 m por pixel onde o nível tem um) e assa estradas,
  pátios, linhas de pista, marcas de pneu e marcações por cima, na cor de tinta do
  material onde ela está definida e numa cor neutra onde não está; máscaras de variação
  de estrada ficam de fora. O jogo mistura as suas camadas de superfície num grafo de
  shader que não é lido; a exportação dispõe as cores das camadas pelas suas máscaras
  e pela inclinação do heightfield, por uma regra própria, e um nível cujas páginas de
  máscara não se encaixam recebe uma só cor. Cada camada vale a média do seu mapa de
  cor, e não a sua textura. Veja [Frostbite](reader-frostbite.md#terrain-layers).
  Partes do heightfield em resoluções diferentes se encontram com pequenos degraus.
- **A cor de mapa de um objeto do Battlefield 6 é escolhida, não lida.** Um bloco de
  shader nomeia cada textura que amostra, sem dizer qual é a cor; a escolha se faz pelo
  nome (veja [Frostbite](reader-frostbite.md#textures-and-materials)) e pode pegar uma
  folha de acabamento ou de detalhe para uma superfície. Folhas de decalque (`t_de_...`)
  perdem para o mapa próprio da superfície; o decalque de uma placa, desenhado como o
  seu painel, mostrava o seu escudo girado um quarto de volta. Campos de distância,
  paletas e máscaras de canal nunca são tomados. Prédios de fundo são desenhados nas
  cores das suas paletas; mapas cinza recebem a tinta do material por uma regra do
  próprio exportador, já que os nomes dos parâmetros são hashes, e um material que pinta
  um mapa cinza através de uma máscara com várias tintas recebe uma delas.
- **As aberturas do terreno do Battlefield 6 não são cortadas.** Onde o solo caminhável
  de um nível passa sob o heightfield, o jogo deve ter cortado o terreno, e a exportação
  não corta. Foram descartados como onde estão os buracos: as máscaras de camada do
  terreno (nenhuma se concentra ali), a sua grade raster de 67 x 67 nós, um valor de
  altura reservado (nenhuma página de altura tem 0 ou 65.535), as flags dos nós (todas
  iguais), e malhas ou ativos que cortam o solo: o que é colocado sob o solo ali são
  malhas de rocha e de penhasco, e nenhum ativo do nível é nomeado para buracos, túneis
  ou cavernas. Duas árvores raster são descodificadas por contagem de sequências, mas não
  são colocadas, e são o que sobra (veja [Frostbite](reader-frostbite.md#terrain-layers)).
- **Uma variação de objeto do Battlefield 6 alcança uma secção pelos seus gémeos.** A
  variação de uma cópia colocada escolhe os blocos de shader das suas secções pela chave;
  onde uma malha não tem bloco para uma variação, toma-se a variante da secção de outra
  malha com um bloco padrão idêntico (veja [Frostbite](reader-frostbite.md#textures-and-materials)).
  Essa é a regra do exportador; uma secção sem gémeo que varia mantém o seu aspeto padrão.
- **Materiais em camadas do Battlefield 6 são desenhados como a sua base e uma folha.**
  Um painel de parede com letras é desenhado como o seu reboco com a folha de letras por
  cima; as outras camadas do material (sujeira sobreposta pela sua máscara, mapas de
  detalhe e de musgo) não são misturadas.
- **A malha de navegação é a dos bots, não a dos jogadores.** Ela cobre onde um soldado
  consegue andar: o solo, pisos e escadas, e alguns telhados, mas não todo ponto alto.
  As ligações entre superfícies (saltos, escadas, transposições) ficam de fora.
- **Um nível do Battlefield 6 inclui a camada de todos os modos de jogo.** Objetos que só
  um modo coloca podem se sobrepor aos de outro. `--skip` deixa camadas de fora pelo nome.
- **`courses` é só do Forza**, e só apanha pastas de biblioteca chamadas `... (course_...)`.
- **O referencial da volta do BeamNG é presumido**: é o referencial do visualizador
  `(x, z, -y)` que o gravador do 3DHeat escreve. Voltas de outro gravador, no referencial
  cru do BeamNG, não seriam posicionadas.
- **`list` e `extract` apanham os ficheiros, não todos os formatos.** Eles abrem um `.pak`,
  um `.utoc` do IoStore, um `.vpk`, um `.minizip` e um zip. Um contêiner do Unity é lido
  com `meshes`, um nível do Frostbite com `level`, e um `.cdae` ou `.ter` é um ficheiro, e
  não um ficheiro compactado (`identify` o nomeia). Um `.minizip` sem o seu
  `ChunkContentsMiniZip<n>.txt` ao lado é listado pelo número da entrada.
- **Modelos colocados no BeamNG usam texturas repetidas como cores médias**, porque o
  amostrador do `.glb` fixa as bordas e o visualizador empacota as texturas num atlas.
- **Na prática, só Windows.** Caminhos da Steam em `C:\Program Files`, `%LOCALAPPDATA%`,
  `C:\XboxGames`, e um `*_win64.dll` para o Oodle. Outras plataformas não foram testadas.

## Não verificado {#unverified}

- Versões antigas do Python (a ferramenta foi executada com o 3.13).
- Assetto Corsa Rally com uma volta gravada no jogo. Foi testado só com voltas sintéticas
  em referenciais aleatórios.
- Visualizadores glTF que não sejam o visualizador do 3DHeat.
- Se o referencial de cada jogo é de mão esquerda ou direita. A exportação mantém o
  referencial de telemetria de cada jogo, então voltas e percursos se alinham de qualquer
  forma.
- O significado de z = 0 do `WaterBlock` como superfície (BeamNG).
- O posicionamento do Frostbite em jogos que não sejam o Battlefield 6, e no Battlefield 6
  depois de uma atualização que muda o layout do membro do grupo. Nesse caso o leitor não
  encontra grupos e informa isso.
- Se uma exportação do Battlefield 6 se alinha com as posições que o jogo informa. As
  coordenadas são as do próprio jogo, como nos outros jogos, mas nenhuma gravação foi
  sobreposta a uma ainda.
