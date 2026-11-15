---
title: Comandos
nav_order: 2
lang: "pt"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Comandos {#commands}

Cada comando é executado como `python -m heat3d_gamefiles <verbo> ...` a partir da pasta do repositório. Os verbos estão na ordem em que normalmente os precisa: o que é este ficheiro, o que tem lá dentro, dê-me aquilo, e transforme uma volta num percurso.

| Verbo | Recebe | Faz |
|---|---|---|
| [`identify`](#identify) | qualquer ficheiro | indica o formato do contentor, lendo os seus bytes |
| [`list`](#list) | um `.pak` ou `.utoc` do Unreal, um `.vpk` do Source 2, um `.minizip` do ForzaTech, ou um zip | lista as suas entradas |
| [`extract`](#extract) | o mesmo | escreve uma entrada no disco |
| [`meshes`](#meshes) | um `SerializedFile` do Unity | lista e verifica as suas malhas |
| [`course`](#course) | uma volta | exporta o percurso à volta dela (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | uma biblioteca de voltas gravadas | executa `course` em cada percurso dela (Forza) |
| [`races`](#races) | um Forza instalado | lista cada corrida que o jogo define: o que acrescenta, o que esconde, os locais, o estado da sua exportação |
| [`terrain`](#terrain) | uma pasta de pista do Forza | recorta uma região por coordenadas do mundo |
| [`levels`](#levels-and-level-frostbite) | um jogo Frostbite instalado (Battlefield 6) | lista os seus níveis |
| [`level`](#levels-and-level-frostbite) | o nome de um nível | exporta o nível: terreno, malhas colocadas, e opcionalmente os seus mapas de cor (Battlefield 6) |
| [`cars`](#cars) | um Forza instalado | todos os carros em baixo detalhe, num só ficheiro para o separador de corrida do visualizador |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | um jogo Unreal 5 | lista os seus mapas World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | o nome de um mapa | exporta o mapa: paisagem, estruturas HLOD, água |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | um Arma Reforger instalado | lista os seus mundos |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | o nome de um mundo | exporta o mundo: terreno nas suas cores, o mar, edifícios como caixas |

**Como ler os exemplos:** `<x>` quer dizer que deve substituir pelo seu próprio valor, sem os parênteses angulares; `[...]` é opcional; ponha um caminho com espaços entre "aspas duplas", por exemplo `"C:\Games\My Game"`. Novo nisto? Veja [Antes de começar](before-you-start.md). A ajuda completa (`--help`) de cada verbo está na [Referência de comandos](../cli-reference.md).

Sempre que o programa arranca, pode verificar primeiro se há uma versão mais recente. Veja [Atualizações](updates.md). `HEAT3D_NO_UPDATE=1` desliga essa verificação.

Fonte: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Páginas passo a passo: [Inspecionar ficheiros](inspecting-archives.md), [Exportação de percursos](course-export.md),
[Níveis inteiros](whole-levels.md), [Carros do Forza](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Códigos de saída {#exit-codes}

| Código | Significado |
|---|---|
| 0 | sucesso |
| 1 | o trabalho falhou (volta ilegível, jogo não encontrado, nada para exportar, um percurso em `courses` falhou; para `list` e `extract`, um ficheiro que não é nenhum dos ficheiros que estes lêem, ou um que não pode ser aberto ou lido - um `.pak` cifrado sem `--key`, um contentor IoStore cifrado - ou uma entrada que não está no ficheiro) |
| 2 | argumentos errados (argparse), um caminho que não existe, uma `--key` que não tem 64 dígitos hexadecimais, ou `terrain` dado com ambos ou nenhum de `--box` e `--route` |

As falhas de `list` e `extract` são cada uma uma linha na saída de erro padrão, e não um rasto de erro (traceback) do Python.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <caminho>
```

Isto lê o ficheiro e diz qual é o contentor. Não se guia pela extensão (a única exceção é um `.ucas`, abaixo). Experimenta os formatos por esta ordem e para no primeiro que consegue ler:

1. **Unreal `.pak`**: um rodapé com o marcador do pak nos últimos 1.024 bytes. Mostra a versão, a posição e o tamanho do índice, se o índice está cifrado, e os métodos de compressão.
2. **Unreal IoStore `.utoc`**: o marcador do IoStore no início. Mostra a versão, o número de blocos e se o contentor está cifrado; se não estiver, o número de ficheiros que o seu diretório indica (e sob que ponto de montagem), os métodos de compressão, e se o seu `.ucas` está ao lado. Um `.ucas` não tem cabeçalho próprio, por isso é reconhecido pelo `.utoc` com o mesmo nome ao lado dele, e `identify` indica esse ficheiro.
3. **ForzaTech `.minizip`**: o marcador `PGZP`. Mostra a versão, o número de entradas e de segmentos, e se o `ChunkContentsMiniZip<n>.txt` que nomeia as entradas está ao lado (e, se estiver, se nomeia tantas quantas existem).
4. **zip**: um cabeçalho de ficheiro local do zip no início. Mostra o número de entradas, as seis extensões mais comuns, e os nomes dos níveis quando as entradas estão em `levels/<nome>/`, como num ficheiro de nível do BeamNG.drive.
5. **Unity**: um pacote `UnityFS` (mostra a versão do motor e o número de entradas) ou um `SerializedFile` simples (mostra o formato, a versão do motor, o número de objetos e as seis classes mais comuns).
6. **Frostbite `.toc`**: mostra o tipo (`plain` ou `signed`), onde começa a árvore, e ou o número de recursos (secção binária de tabela) ou o número de superpacotes (árvore DbObject).
7. **Source 2 `.vpk`**: mostra a versão, o número de entradas e a primeira malha de navegação `.nav`, se o ficheiro tiver uma.
8. **BeamNG `.cdae`**: forma versão 31 que se consegue ler. Mostra o número de malhas, o número de níveis de detalhe desenhados e os primeiros materiais.
9. **BeamNG `.ter`**: não tem marcador, por isso tudo tem de bater certo - um lado de 2 a 16.384, esse número de alturas e bytes de camada ao quadrado, e depois de 1 a 255 nomes de camada imprimíveis. Mostra a versão, o tamanho e os nomes das camadas.
10. **ForzaTech `.modelbin`**: mostra a versão, o número de blocos e as seis etiquetas de bloco mais comuns. O conteúdo dos blocos não é descodificado aqui.

Os formatos com marcador próprio (2 a 4) vêm antes do Unity e do Frostbite, cujas verificações leem o ficheiro inteiro: um ficheiro do Forza tem dezenas de gigabytes.

Se nenhum corresponder, escreve `not a format this tool reads` e a última razão. Essa razão vem da verificação do ForzaTech.

Exemplo (dados sintéticos):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <arquivo> [--filter TEXTO] [--limit N] [--key HEX]
```

| Opção | Por omissão | Significado |
|---|---|---|
| `<arquivo>` | obrigatório | um `.pak` do Unreal; um `.utoc` do IoStore (ou o `.ucas` ao lado); um `.vpk` do Source 2 (para VPK divididos, o `_dir.vpk`); um `.minizip` do ForzaTech; um zip, como os ficheiros de nível e de conteúdo do BeamNG |
| `--filter TEXTO` | nenhum | só os caminhos que contêm TEXTO, sem distinguir maiúsculas |
| `--limit N` | 50 | escreve no máximo N entradas (o total é sempre escrito) |
| `--key HEX` | nenhum | uma chave AES-256 que já tem, com 64 dígitos hexadecimais, com ou sem `0x`. Só um `.pak` cifrado a usa. Qualquer valor que não tenha 64 dígitos hexadecimais é recusado antes de o ficheiro ser aberto (código de saída 2) |

A ferramenta decide o formato pelos bytes: um índice IoStore, um `.minizip` e um VPK pela assinatura com que começam, um zip pelo seu cabeçalho de ficheiro local, e um `.pak` pelo rodapé no fim. Um `.ucas` não tem cabeçalho e é aberto pelo `.utoc` com o mesmo nome. Um ficheiro que não é nenhum destes é recusado com `<ficheiro> is not an archive list and extract read (...)`. Um que é, mas não pode ser aberto, é recusado com a razão do leitor: um pak cifrado sem `--key`, um contentor IoStore cifrado, uma versão de pak que não consegue ler. Em qualquer dos casos é uma linha e código de saída 1.

Cada linha mostra o tamanho descomprimido, o método de compressão e o caminho:

| Ficheiro | Método | Caminhos |
|---|---|---|
| `.pak` | `none`, ou o nome que vem no rodapé (`Zlib`, `Oodle`, `Gzip`...) | com o ponto de montagem do ficheiro, por exemplo `../../../Game/Content/...` |
| `.utoc` do IoStore | `none`, ou o método do contentor (`Oodle`, `Zlib`...), tal como o seu primeiro bloco está guardado | com o ponto de montagem, por exemplo `../../../<Projeto>/Content/...`. Um contentor sem índice de diretório não indica ficheiros e é recusado |
| `.vpk` | sempre `stored` | como está no diretório |
| `.minizip` | `lz4`, `deflate` ou `stored` | como o `ChunkContentsMiniZip<n>.txt` ao lado de `GeoChunk<n>.minizip` os escreve, sem o prefixo da máquina de compilação (barras invertidas, como o jogo as escreve). O ficheiro não guarda nomes, por isso sem esse ficheiro as entradas são `#0`, `#1`... Uma lista cujo número de linhas não coincide com o das entradas é recusada: as duas não pertencem uma à outra |
| zip | `stored`, `deflate`, ... | como está guardado; as pastas não são listadas |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <arquivo> <entrada> [--out FICHEIRO] [--key HEX]
```

| Opção | Por omissão | Significado |
|---|---|---|
| `<arquivo>` | obrigatório | como em `list` |
| `<entrada>` | obrigatório | o caminho exatamente como `list` o escreve (sensível a maiúsculas); num `.minizip`, `#<número>` também funciona |
| `--out FICHEIRO` | o nome do ficheiro da entrada (depois da última `/` ou `\`), na pasta atual | onde escrever; as pastas-mãe são criadas |
| `--key HEX` | nenhum | como em `list` |

A entrada é decifrada (pak, com uma chave), descomprimida e escrita. Imprime `<bytes> bytes -> <ficheiro>`. Se o caminho não estiver no ficheiro, o comando termina com código 1. Também termina assim uma entrada que não pode ser lida (uma entrada cifrada sem chave, ou comprimida em Oodle sem a biblioteca Oodle), com a razão numa linha. Uma entrada VPK não é verificada contra o seu CRC aqui. O leitor tem um método `verify()` para isso (veja [VPK do Source 2](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <ficheiro .assets do unity> [--limit N]
```

| Opção | Por omissão | Significado |
|---|---|---|
| `<caminho>` | obrigatório | um `SerializedFile` simples do Unity (`sharedassets0.assets`, `level0`...), não um pacote |
| `--limit N` | 25 | descodifica e escreve no máximo N malhas |

Isto escreve o número de objetos `Mesh` e depois uma linha por malha: o nome (os primeiros 40 caracteres), o número de vértices e de triângulos, e `ok` ou `BOUNDS DISAGREE`. `BOUNDS DISAGREE` quer dizer que os vértices descodificados não reproduzem a caixa delimitadora que o Unity guardou para a malha, dentro de 2% do tamanho da caixa. É a verificação do próprio leitor (veja [Unity](reader-unity.md)). Uma malha que não pode ser lida é indicada com a razão e conta para o limite. Os dados de vértices de um ficheiro `.resS` são lidos da pasta onde está o contentor.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <volta> [-o FICHEIRO] [opções]
```

Isto exporta o percurso à volta de uma volta: o chão numa faixa de cada lado da condução, e o que está em cima dele, num só `.glb`. A ferramenta descobre o resto sozinha: qual jogo, qual cópia instalada, qual pista, nível ou etapa, e (para o Assetto Corsa Rally) em que sentido estão os eixos. Veja [Exportação de percursos](course-export.md).

`<volta>` pode ser qualquer um destes (detalhes em [Entradas de voltas](lap-inputs.md)):

- um ficheiro de volta: JSON de rota, JSON de volta do FH Companion, JSON `heat3d-lap`, `.npz`, ou `.csv` com as colunas x, y, z
- uma pasta de ficheiros de volta, pesquisada recursivamente (um percurso gravado inteiro)
- um **nome** de percurso, procurado na biblioteca de voltas do FH Companion em `%LOCALAPPDATA%\FHCompanion\laps`

### Opções {#options}

| Opção | Por omissão | Jogos | Significado |
|---|---|---|---|
| `-o`, `--out FICHEIRO` | `<nome do percurso>.glb` na pasta atual | todos | onde escrever; o nome passa a minúsculas, e sequências de outros caracteres passam a `_` |
| `--game {forza,beamng,acrally}` | o que indicar o ficheiro de volta, senão `forza` | todos | de que jogo é a volta |
| `--margin M` | 80 | todos | metros de chão mantidos de cada lado da condução |
| `--texture-size {2048,1024,512}` | 2048 | todos | pixels de textura do chão por cada pedaço de 512 m (2048 = 25 cm por pixel) |
| `--no-textures` | desligada | todos | só cores lisas: um ficheiro muito mais pequeno. No Forza isto também salta a divisão entre estrada e berma (veja abaixo) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | de que estação são os mapas do chão e as texturas dos modelos |
| `--no-placed` | desligada | todos | só o terreno: sem lancis, barreiras, sinais, edifícios. No BeamNG, as superfícies de condução modeladas como malhas continuam a ser mantidas |
| `--trees` | desligada | todos | coloca também a vegetação (Forza: árvores, arbustos e objetos destrutíveis; BeamNG: árvores; AC Rally: árvores e a folhagem instanciada) |
| `--detail-budget N` | automático | todos | um teto de triângulos para tudo o que é colocado; veja [Níveis de detalhe e o orçamento](detail-budget.md) |
| `--track DIR` | pesquisada | Forza | a pasta da pista (em `media\Tracks`, com `GeoChunk0.minizip`), se a instalação do jogo não deve ser pesquisada |
| `--level NOME` | encontrado pela volta | BeamNG, AC Rally | o nível (nome da pasta do BeamNG) ou a etapa (nome do mapa do AC Rally), sem distinguir maiúsculas |
| `--install DIR` | pesquisada nas bibliotecas do Steam | BeamNG, AC Rally | BeamNG: a pasta que tem `gameengine.zip`. AC Rally: a pasta do jogo, ou a sua `acr\Content\Paks` / `Content\Paks` |

As opções que não se aplicam a um jogo são ignoradas sem aviso. Por exemplo, `--season` não faz nada no BeamNG e no AC Rally, e `--track` também não faz nada nesses jogos.

### Qual jogo {#which-game}

O jogo é escolhido por `--game`, depois pelo campo `game` de um ficheiro `heat3d-lap` (ou da linha de descrição `# {...}` de um CSV), e por omissão é o Forza. Uma pasta fica com o jogo que os seus ficheiros indicam, quando indicam só um; um ficheiro que não indica nenhum (uma volta do FH Companion, `course.json`, um CSV sem linha de descrição) não conta (veja [Entradas de voltas](lap-inputs.md)).

| Valor | Exportação |
|---|---|
| começa por `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` ou `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | recusado: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | recusado: "tracks ship in a protected format that is not a file-extraction target" |
| qualquer outro | recusado: "there is no course reader for <jogo> yet" |

Uma recusa também sugere as alternativas: reconstruir o percurso a partir do jogo (3DHeat GameCapture), ou analisar as voltas sem percurso, porque o separador Análise de corrida do visualizador desenha uma estrada a partir delas.

### Exemplos {#examples}

```
# Um percurso da biblioteca do FH Companion, pelo nome
python -m heat3d_gamefiles course "Example Circuit"

# Um ficheiro de volta, uma faixa mais estreita, um ficheiro mais pequeno
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Texturas de inverno, com árvores
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Um teto rígido de 500.000 triângulos colocados
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Uma pasta de pista dada diretamente (jogo instalado fora do Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: indicar o nível, apontar para a instalação
python -m heat3d_gamefiles course beamng_lap.json --level <pasta do nível> --install "D:\Games\BeamNG.drive"

# AC Rally, com um CSV de volta simples que não indica o jogo
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Exemplo de saída (Forza, números sintéticos):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<pasta do jogo>" -o forza.h3dcars
```

Todos os carros de um Forza instalado, no baixo detalhe próprio do jogo, num só ficheiro para o separador de corrida do visualizador: o modelo `ProxyLOD` que cada ficheiro de carro em `media/Cars` traz, com cerca de 900 triângulos, com o número do carro tal como a telemetria o indica, a sua marca, a etiqueta do modelo e o ano a partir do nome do ficheiro, e as suas rodas e luzes traseiras. Demora segundos e escreve cerca de 5 MB. Execute de novo quando o jogo receber carros novos. Um ficheiro sem esse modelo (um adereço de trânsito) é indicado e deixado de fora. O formato está em [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

As formas estão em metros, os do próprio jogo: 1:1 com o carro. O ficheiro contém conteúdo do jogo, por isso serve para a máquina onde foi feito, não para passar a outros.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o PASTA] [opções]
```

Isto executa a exportação `course` do Forza em cada pasta de percurso de uma biblioteca de voltas gravadas, escrevendo um `<nome>.glb` por cada uma. É só para o Forza. Chama diretamente a exportação do Forza e não lê `--game`, `--level` nem `--install`.

| Opção | Por omissão | Significado |
|---|---|---|
| `-o`, `--out PASTA` | `courses` | a pasta onde escrever (criada se não existir) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | a biblioteca de voltas |
| `--only TEXTO [TEXTO ...]` | todos | só os percursos cujos nomes de pasta contêm um destes (sem distinguir maiúsculas) |
| `--force` | desligada | exporta de novo o que já tem um `.glb` |
| `--track DIR` | pesquisada | como em `course` |
| `--margin M` | 80 | como em `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | como em `course` |

O que conta como pasta de percurso: uma subpasta direta da biblioteca cujo nome contém ` (course_`, que é como o FH Companion os nomeia, por exemplo `Example Circuit (course_1200_3400_to_1175_3400)`. A parte a partir de ` (course_` é retirada do nome.

Como uma execução se comporta:

- Um percurso cujo `.glb` já existe é saltado (`kept`) a menos que se dê `--force`, por isso uma execução interrompida continua de onde parou.
- Um `.glb` escrito por uma versão antiga, sem a camada de corrida e os locais (o seu `asset.extras.course_format` está em falta ou é inferior ao atual), é exportado de novo, como se `--force` fosse dado só para ele.
- Duas pastas de percurso com o mesmo nome antes de ` (course_` (um gravador que deu a um percurso novo o nome de um antigo) não se sobrepõem: a pasta criada primeiro fica com `<nome>.glb`, a outra é escrita como `<nome>_<início>.glb`, onde `<início>` é o ponto de partida, com os sinais de menos como `m` (por exemplo `example_circuit_m120_m340.glb`).
- Um percurso que falha (voltas ilegíveis, memória esgotada, sem terreno...) é indicado como `FAILED`, e a execução continua.
- No fim imprime uma tabela com o estado, o tamanho em MB, os segundos gastos e o nome, depois `<n> of <total> courses in <pasta>`.
- O código de saída é 1 se algum percurso tiver falhado.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o PASTA] [--markdown FICHEIRO] [opções]
```

Lista cada corrida que um Forza instalado define, a partir das suas definições de rota (veja [Exportação de percursos do Forza Horizon](course-forza-horizon.md#which-race)), e verifica as exportações numa pasta `courses` contra elas. Lê o jogo e a biblioteca de voltas; não escreve nada, a não ser a tabela opcional.

| Opção | Por omissão | Significado |
|---|---|---|
| `-o`, `--out PASTA` | `courses` | a pasta onde `courses` escreve, cujos ficheiros são verificados |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | a biblioteca de voltas |
| `--track DIR` | pesquisada | a pasta da pista, se não for a do jogo instalado |
| `--markdown FICHEIRO` | nenhum | escreve também a tabela aí, em Markdown |

Uma linha por corrida, e uma por cada percurso gravado feito nela:

| Coluna | Significado |
|---|---|
| route | o número da rota |
| course | o percurso gravado que lhe corresponde, se existir |
| own assets | cópias que a corrida acrescenta ao mundo de conduta livre |
| drawn | dessas, as cópias cujo modelo a pista traz |
| kinds | as cópias acrescentadas por tipo (barriers, props, decals, infrastructure, ...) |
| not geometry | marcadores de espetadores e splines de colisão, contados |
| hidden | objetos do mundo livre que a corrida remove |
| venue | os modelos de chão de locais que a linha de IA da corrida passa a menos de 10 m |
| export | `current`, `older format` (exportado de novo por `courses`), `not exported`, ou vazio para uma corrida sem percurso gravado |

Termina com uma contagem: `<n> races: <a> with assets of their own, <v> through a venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <pasta da pista> -o FICHEIRO (--box X0 Z0 X1 Z1 | --route FICHEIRO) [opções]
```

Este é o recorte do Forza com tudo especificado à mão: dá a pasta da pista e uma região, não uma volta. É útil quando a área que quer é uma caixa e não uma condução.

| Opção | Por omissão | Significado |
|---|---|---|
| `<caminho>` | obrigatório | uma pasta de pista do Forza em `media\Tracks` (com `GeoChunk*.minizip`) |
| `-o`, `--out FICHEIRO` | obrigatório | o `.glb` a escrever |
| `--box X0 Z0 X1 Z1` | | a região, em metros do jogo (x e z, como a telemetria os indica); cantos em qualquer ordem |
| `--route FICHEIRO` | | um JSON de rota com `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, como o `heat3d_capture route` e o `heat3d_capture laps` escrevem; lido como UTF-8, com ou sem marca de ordem de bytes |
| `--margin M` | **100** | metros acrescentados em volta dos limites de uma rota, e a largura do corredor quando a rota tem uma linha |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | como em `course` |

Dê exatamente um de `--box` e `--route`, senão o código de saída é 2. Com `--route`, o recorte são os `bounds` da rota (`min`/`max`, x e z) alargados pela margem. Se o ficheiro também tiver pelo menos 10 posições, o recorte estreita-se para um corredor de `--margin` metros à volta delas, e os modelos colocados recebem o seu detalhe pela distância a essa linha. Com `--box`, a caixa inteira é mantida, e o detalhe vai para o que está mais perto do centro da caixa.

A altura nunca faz parte do recorte. Uma caixa fora do mapa, ou no mar, dá "no terrain there" (código de saída 1), e não um erro sobre coordenadas.

```
python -m heat3d_gamefiles terrain "<jogo>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<jogo>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels e level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install PASTA]
python -m heat3d_gamefiles level <nível> [-o FICHEIRO] [--install PASTA] [--textures [PIXELS]]
                                 [--ground-texture [METROS]] [--ground-spacing METROS]
                                 [--navmesh] [--detail-budget N] [--skip TEXTO ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` lista os níveis que um jogo Frostbite instalado traz, pelo nome da sua tabela (`levels/<nível>/<nível>.toc`), com o tamanho e de onde vem: `Data` para o jogo base, `Update/<pacote>` para uma atualização, e quantas tabelas de alta resolução lhe acrescentam. Um nível que uma atualização traz tem uma pequena tabela de blocos que também existe no jogo base; a tabela com os pacotes do nível é o nível (veja [Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` exporta um: o campo de alturas do terreno, cada malha que os grupos de modelos estáticos do nível colocam, os objetos colocados um a um, onde estão, e o cenário de fundo do terreno em volta do mapa. Com `--textures`, cada superfície traz o seu mapa de cor; com `--navmesh`, também vêm as superfícies onde os soldados andam. Como é lido está em [Frostbite](reader-frostbite.md).

| Opção | Por omissão | Significado |
|---|---|---|
| `<nível>` | obrigatório | um nome como `levels` o escreve, uma parte única de um, ou o caminho da `.toc` de um nível |
| `-o`, `--out FICHEIRO` | `<nível>.glb` | o `.glb` a escrever |
| `--install PASTA` | o primeiro jogo do Steam cujo `Data` tem um `layout.toc` | a pasta do jogo |
| `--textures [PIXELS]` | desligada; 512 quando dado sem tamanho | escreve o mapa de cor de cada superfície, o maior mip não maior que PIXELS de lado, e as suas coordenadas de textura tal como o jogo as tem, com um amostrador que repete (veja [Formato de saída](output-format.md)). O campo de alturas recebe o mapa de cor do cenário de fundo do terreno onde esse mapa o cobre, senão a cor média dos materiais de superfície do terreno, senão a cor média do cenário de fundo à sua volta. Desligada, cada parte é uma cor lisa |
| `--ground-texture [METROS]` | desligada; 0,5 quando dado sem tamanho | grava as decalques do terreno — estradas, pistas de aterragem, placas, marcações pintadas — sobre a cor do chão, multiplicada pelo mapa de cor do terreno onde o nível o tem, na cor do campo de alturas, METROS por pixel, em pedaços de no máximo 4.096 pixels (`ground:terrain x<x> z<z>`). Funciona com ou sem `--textures` |
| `--navmesh` | desligada | acrescenta a malha de navegação do nível para o seu agente mais pequeno, o soldado (1,8 m de altura, 0,4 m de largura), como a parte `nav:walkable`: o chão, os pisos, as escadas e os telhados onde um soldado pode chegar, sem as ligações (saltos, escadas, saltos por cima) entre eles |
| `--ground-spacing METROS` | 4 | o espaçamento mais fino do campo de alturas; nós mais finos do que isto são amostrados mais grosseiramente. 0 deixa o campo de alturas de fora |
| `--detail-budget N` | cada cópia no seu nível mais grosseiro, mais um quarto, pelo menos 1.500.000 | um teto de triângulos. As malhas que mais custam perdem um nível de detalhe de cada vez até caberem; se nem os níveis mais grosseiros bastarem, as cópias mais pequenas são deixadas de fora primeiro. O cenário de fundo do terreno nunca é tornado mais grosseiro nem deixado de fora |
| `--skip TEXTO` | | deixa de fora os grupos de modelos estáticos cujo nome de partição contém TEXTO; repita para vários. A camada de um modo de jogo, por exemplo |
| `--by-mesh` | desligada | para descobrir o que é uma parte: uma parte por malha de origem e material, com o nome `<parte> \| <malha> \| <material>`; um ficheiro muito maior |
| `--clamped-uvs` | desligada | para um renderizador que não consegue repetir uma textura: corta cada triângulo texturizado em pedaços cujas coordenadas ficam entre 0 e 1, e desenha um triângulo que precisaria de mais de 4 pedaços com a cor média da sua textura, numa parte `<parte> (average colour)` |

Escreve os grupos e quantas cópias cada um colocou, as malhas que deixou de fora e porquê, os triângulos por parte (e com `--textures` quantas texturas, e quantas secções encontraram o seu mapa de cor), o que é o chão, e com `--navmesh` quantos blocos de navegação foram lidos. Nada é escrito sobre o nível para além da geometria: sem nomes, sem metadados (veja [Formato de saída](output-format.md)).

O orçamento do terreno é separado: o campo de alturas e o cenário de fundo nunca são tornados mais grosseiros por `--detail-budget`; `--ground-spacing` dimensiona o campo de alturas.

Um nível inteiro é grande: tipicamente mais de dez milhões de triângulos e várias centenas de MB. `--textures` acrescenta um pouco ao ficheiro; um nível cheio de árvores pode chegar a cerca de 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8` leva um nível a cerca de um terço disso.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <nível> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <nível> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <nível> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps e ue-map (Unreal 5, World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <jogo>
python -m heat3d_gamefiles ue-map  <jogo> <mapa> [-o FICHEIRO] [--ground-spacing METROS] [--no-structures] [--no-water]
```

`<jogo>` é a pasta do jogo, a sua `Content/Paks`, ou o nome da sua pasta numa biblioteca do Steam (`"<nome da pasta do jogo no Steam>"`). `ue-maps` lista cada mapa que tem células World Partition já compiladas ao lado. `ue-map` exporta um como `ground:<mapa>` (a paisagem), `structure:<mapa>` (as malhas HLOD fundidas do mapa) e `water:<mapa>` (os seus corpos de água onde estão acima do chão), em **centímetros** do Unreal com Y e Z trocados - a única exportação que não está em metros. Como cada uma é lida e verificada: [Mapas do Unreal 5](level-unreal-world-partition.md).

| Opção | Por omissão | Significado |
|---|---|---|
| `<mapa>` | obrigatório | um nome como `ue-maps` o escreve, ou uma parte única de um |
| `-o`, `--out FICHEIRO` | `<mapa>.glb` | o `.glb` a escrever |
| `--ground-spacing METROS` | 2 | o espaçamento de vértices da paisagem no ficheiro, arredondado para um número inteiro de quadrados próprios |
| `--no-structures`, `--no-water` | | deixa essa parte de fora |

Escreve os triângulos por parte, quantos componentes de paisagem foram lidos e quantos dos vértices que guardam duas vezes não batem certo. Um mapa de 3 km a 2 m tem cerca de 4,6 milhões de triângulos de chão.

## enfusion-worlds e enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install PASTA]
python -m heat3d_gamefiles enfusion-world <mundo> [-o FICHEIRO] [--install PASTA] [--ground-spacing METROS]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` lista cada mundo com um terreno, pela sua pasta em `worlds/`. `enfusion-world` exporta um: `ground:<mundo>` (o terreno, nas cores dos seus blocos de supertextura), `water:<mundo>` (o mar, à altura zero) e `structure:<mundo>` (a caixa de cada modelo colocado), em metros do próprio jogo - x a leste, y para cima, z a norte. Como cada um é lido e verificado: [Mundos do Arma Reforger](level-arma-reforger.md).

| Opção | Por omissão | Significado |
|---|---|---|
| `<mundo>` | obrigatório | um mundo como `enfusion-worlds` o escreve |
| `-o`, `--out FICHEIRO` | `<mundo>.glb` | o `.glb` a escrever |
| `--install PASTA` | a biblioteca do Steam que tem o jogo | a pasta do jogo |
| `--ground-spacing METROS` | 2 (o do próprio terreno) | o espaçamento de vértices do terreno no ficheiro |
| `--texture-size PIXELS` | 4096 | o lado maior da imagem de cor do chão; 0 para cor lisa |
| `--no-structures` | | deixa de fora os modelos colocados |
| `--trees` | desligada | coloca também árvores e outra vegetação, como caixas |

Escreve os triângulos por parte, quantos vértices de borda de bloco não batem certo, quantas entidades o ficheiro do mundo tem e quantas caixas foram colocadas, e o que foi deixado de fora e porquê.

## Variáveis de ambiente {#environment-variables}

| Variável | Efeito |
|---|---|
| `HEAT3D_OODLE` | caminho para um `oo2core_*_win64.dll`, ou uma pasta que o contenha; veja [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | qualquer valor diferente de vazio, `0`, `false`, `no` desliga a verificação de atualizações; veja [Atualizações](updates.md) |
| `LOCALAPPDATA` | onde se procuram a biblioteca do FH Companion, a pasta de utilizador do BeamNG e a cache de atualizações |
| `HEAT3D_COURSE` | só para testes: o percurso que o teste de lancis de jogo instalado usa; veja [Desenvolvimento](development.md) |
