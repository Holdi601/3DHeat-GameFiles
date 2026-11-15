---
title: Desenvolvimento
nav_order: 14
lang: "pt"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Desenvolvimento {#development}

## Estrutura {#layout}

```
heat3d_gamefiles/     o pacote: leitores, exportações de percurso, a linha de comando
heat3d_update/        a verificação de versão e o atualizador (veja Atualizações)
tests/                testes sintéticos, fixtures e testes com jogos instalados
docs/                 esta documentação (docs/wiki é gerada a partir dela)
VERSION               a versão instalada, comparada com as releases do GitHub
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Mapa dos módulos {#module-map}

| Módulo | O que faz |
|---|---|
| `__main__.py` | executa a verificação de atualização e depois `cli.main()` |
| `cli.py` | os verbos, `identify`, o despacho de ficheiros, o gravador de percurso do Forza |
| `lapinput.py` | todos os formatos de volta em posições; busca de biblioteca do FH Companion |
| `corridor.py` | a faixa dos dois lados da pilotagem, como uma raster de 4 m |
| `surfaces.py` | os tipos de solo, os nomes e cores das partes |
| `glb.py` | o gravador de `.glb` (partes, normais, cores, texturas, quantização) |
| `courseexport.py` | Forza: UVs planares dos tiles, divisão estrada/berma, assar o solo, elevação dos decalques |
| `forzainstall.py` | bibliotecas da Steam e do Xbox; a pista do Forza a que uma caixa pertence |
| `minizip.py` | ficheiros `.minizip` do ForzaTech e suas listas de nomes |
| `forzatech.py` | `.modelbin`: chunks, buffers, layouts, submalhas, materiais |
| `forzaterrain.py` | tiles de terreno por lugar; classes de superfície |
| `forzatexture.py` | amostras `.pb`; mapas de tiles; o assamento do solo |
| `forzamaterial.py` | `AssetManifest.xml`; quais cores de textura um modelo usa; estações |
| `forzaplacement.py` | posicionamentos `.pgeo`, níveis de modelo, texturas, recortes, substitutos, o orçamento |
| `beamng.py` | instalação do BeamNG, sistema de ficheiros montado, cena, terreno, materiais |
| `beamngcourse.py` | a exportação de percurso do BeamNG |
| `beamngshape.py` | formas compiladas `.cdae` |
| `beamngcollada.py` | alternativa `.dae` |
| `acrally.py` | instalação do AC Rally, etapas, posicionamento de componentes, volume de textura virtual |
| `acrallycourse.py` | a exportação de percurso do AC Rally: ajuste de referencial, solo, posicionamento |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | pacotes cozidos do Unreal 5 |
| `unversioned.py` | esquemas e leitor de propriedades sem versão |
| `unrealmesh.py` | malhas estáticas cozidas |
| `unrealtexture.py` | texturas e texturas virtuais em streaming |
| `oodle.py` | achar e chamar uma biblioteca Oodle instalada |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | contêineres, bundles e malhas do Unity |
| `frostbite.py` | `.toc` do Frostbite, tabelas de secções, pacotes de instalação, localizações de chunks, payloads |
| `frostbitebundle.py` | bundles embutidos do Frostbite, manifestos de bundles, o catálogo de um nível, a lista de níveis |
| `frostbiteebx.py` | partições RIFF EBX do Frostbite sem uma biblioteca de tipos |
| `frostbitemesh.py` | MeshSet do Frostbite e seus chunks de nível de detalhe |
| `frostbiteterrain.py` | árvore de streaming do terreno do Frostbite, páginas de altura, a malha do solo |
| `frostbitematerial.py` | texturas do Frostbite (mips BC1/BC3/BC7), depósitos de blocos de shader, escolha do mapa de cor |
| `frostbitedecals.py` | decalques do terreno do Frostbite e o assamento do solo |
| `frostbitenav.py` | tiles da malha de navegação do Frostbite: as superfícies caminháveis dos soldados |
| `frostbitelevel.py` | grupos de modelos estáticos do Frostbite, posicionamento, a exportação `level` |
| `vpk.py` | VPK do Source 2 |
| `unreallandscape.py` | componentes de landscape do Unreal 5: mapas de altura na malha do solo (`ue-map`) |
| `unreallevel.py` | mapas World Partition do Unreal 5: listagem, estruturas HLOD, água, a exportação `ue-map` |
| `enfusion.py` | `.pak` do Enfusion, `.edds`, tiles de terreno, `resourceDatabase.rdb` |
| `enfusionworld.py` | mundos do Arma Reforger: ficheiros `.ent`, caixas, a exportação `enfusion-world` |
| `forzacars.py` | todos os carros do Forza em baixo detalhe para `.h3dcars` (`cars`) |

Todos os módulos estão no GitHub, em
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Executar os testes {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` define `testpaths = tests` e `-q`. Dois tipos de teste importam, por
motivos diferentes:

- **Testes sintéticos** montam ficheiros byte a byte e executam em qualquer lugar. Eles
  fixam os layouts de campos que já estiveram errados em algum momento: a base de
  64 bits do segmento `.minizip` e seu preenchimento de alinhamento, o escape do
  tamanho de bloco do pak, o u32 do cabeçalho do Unity entre dois int64, o índice
  `0x7FFF` do VPK, o x dividido da normal do Forza.
- **Testes com jogos instalados** executam com os ficheiros reais quando o jogo está na
  máquina, e **saltam** (não falham) quando não está. São a única coisa que apanha um
  layout que está certo para um ficheiro pequeno e errado para um grande.

### Fixtures {#fixtures}

| Fixture | Monta |
|---|---|
| `tests/forza_fixtures.py` | ficheiros `.minizip` (com a base de 64 bits, preenchimento, codecs misturados), manifestos, modelos `.modelbin` e terreno, amostras `.pb` |
| `tests/beamng_fixtures.py` | uma pequena instalação do BeamNG: `gameengine.zip`, `content`, um zip de nível com um terreno de 64 m, uma faixa de asfalto, um decalque de estrada, um trilho, um prefab, um item de floresta, o mar, materiais e formas `.cdae` no layout documentado |
| `tests/unreal_fixtures.py` | um contêiner IoStore com um diretório, um pacote zen, um bloco de propriedades sem versão |
| `tests/frostbite_fixtures.py` | tabelas, bundles, partições EBX, malhas e páginas de terreno do Frostbite, byte a byte |

### Ficheiros de teste {#test-files}

| Ficheiro | Cobre |
|---|---|
| `test_minizip.py` | leitura de volta, a base de 64 bits, tabelas de bundle pares e ímpares, recusas, o ficheiro de nomes |
| `test_forzatech.py` | a tabela e a cadeia de chunks, recusas; instalado: cadeias e tags dos modelos reais |
| `test_forza_geometry.py` | posicionamento no mundo, layout de vértices, formatos recusados, submalhas, normais e UVs |
| `test_forzaterrain.py` | a grade de tiles (1023 vs 512 m), recorte, extração |
| `test_forzatexture.py` | cabeçalho de amostra, descodificação, a prateleira de texturas, o assamento do solo |
| `test_forzamaterial.py` | o manifesto, os nomes, os hashes de material, a escolha de cor, as estações |
| `test_forzaplacement.py` | o registo `.pgeo`, colocar cópias, níveis, variantes, superfícies vazadas, uma caixa inteira, o orçamento, a cor de substituição, o orçamento automático; instalado: lancis no solo |
| `test_forzainstall.py` | achar o jogo, escolher a pista |
| `test_courseexport.py` | UVs dos tiles, o plano das partes, elevação de decalques |
| `test_course_cli.py` | os verbos `course` e `courses` inteiros numa pista sintética; `terrain --route` com marca de ordem de bytes, e sem `bounds` |
| `test_archive_cli.py` | `identify`, `list` e `extract` em cada ficheiro com leitor (`.pak`, IoStore, `.vpk`, `.minizip` com e sem nomes, zip, `.cdae`, `.ter`); falhas numa linha e um código de saída: um pak cifrado, um contêiner cifrado, um ficheiro que não é ficheiro, um `--key` ruim |
| `test_corridor.py` | a faixa, recortar o terreno com ela |
| `test_lapinput.py` | todos os formatos de volta, a caixa, falhas, busca de nome de percurso, qual jogo é uma pasta |
| `test_surfaces.py` | quais nomes decidem a superfície, quais não, nomes das partes |
| `test_glb.py` | o ficheiro é válido, os nós carregam a classe, recusas, quantização |
| `test_beamng.py` | formas, o nível, categorias, achar o nível a partir de uma volta, o percurso, a alternativa Collada; instalado: `.cdae` vs `.dae`, todos os níveis abrem |
| `test_acrally.py` | contêineres, pacotes, propriedades, transformações, o ajuste de referencial, partes e orçamento dos modelos colocados, texturas virtuais; instalado: etapas e a cor de solo assada |
| `test_pak.py` | rodapé, entradas, o escape de tamanho de bloco, recusas; instalado: deslocamentos e SHA-1 |
| `test_unity.py` | recusas; instalado: a tabela de objetos cobre o ficheiro, strings de versão, limites das malhas |
| `test_frostbite.py` | cabeçalhos com e sem assinatura vs ofuscados, recusas, pacotes de instalação (dois pacotes com o mesmo número de blob); instalado: todas as tabelas, superbundles, cadeias de secções, ids distintos, payloads amostrados do pacote certo |
| `test_frostbitelevel.py` | ids de chunk emparelhados com as próprias localizações, bundles embutidos, manifestos, um MeshSet com secção de sombra e UVs, um membro de grupo, a convenção de transformação, um terreno de dois níveis, escolha de mapa de cor, um chunk de textura sem os mips maiores, o amostrador que repete, registos de decalque, um decalque composto pelo seu alfa, uma folha de decalque perdendo para o mapa próprio de uma superfície, a tabela do nível escolhida entre o jogo base e as suas atualizações, tiles de navegação (superfícies mantidas, ligações deixadas de fora, recusas, malhas de detalhe), texturas que se repetem escritas com as próprias coordenadas, triângulos recortados onde a textura se repete para a saída com fixação, a cor do solo a partir dos materiais de superfície, páginas de máscara (BC4 e sem compressão) posicionadas nos seus quadrantes e recusadas quando as bordas não batem, páginas de mapa de cores posicionadas nos quadrantes e achadas depois das páginas de máscara que a árvore de máscara conta, campos de distância, paletas e máscaras de canal nunca tomados como cor, a tinta de um bloco e um mapa cinza pintado com ela, um vértice de paleta no centro da sua amostra, a grade de inclinação espalhada de volta de forma bilinear, a sobreposição de um objeto desenhada pelo seu desdobramento, o bloco de uma variação identificado pelo seu hash e alcançado por um bloco gémeo, uma folha de letras aplicada pelas suas quarta coordenadas de textura sobre a superfície em que é pintada, a tinta de um decalque lida do seu material e linhas de pista e marcas de pneu desenhadas, mapas de canal único descodificados, malhas destrutíveis marcadas nas suas partes e extras, malhas de blockout, cinemáticas e de iluminação deixadas de fora e um layout de mapa de cores que não é lido, mapas de recorte e seus mascarados, materiais PNG de dois lados, tiles de fundo nomeados pela sua malha; instalado: os decalques de terreno do nível, o catálogo do maior nível, malhas dentro das suas caixas, membros de grupo, vegetação sobre o terreno descodificado |
| `test_vpk.py` | o diretório, recusas, ficheiros divididos; instalado: mapas abrem, CRCs batem, a malha de navegação |
| `test_enfusion.py` | `.pak` do Enfusion, `.edds`, tiles de terreno e ficheiros de mundo; a exportação `enfusion-world` |
| `test_forzacars.py` | o ficheiro `.h3dcars` que o verbo `cars` grava |
| `test_unreallevel.py` | landscapes do Unreal 5, estruturas HLOD, água; a exportação `ue-map` |

## Testes com jogos instalados {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
encontra os jogos para os testes. `steam_common()` lista o `steamapps\common` de
cada biblioteca da Steam (inclusive as pastas da própria Steam), e `installed(*globs)`
devolve os caminhos que batem com qualquer glob dentro deles, recursivamente quando
um glob tem `**`. Cada teste decide o que precisa:

| Teste | Procura | Pula com |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` com índice **sem cifragem**, até 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` em `*/*_Data` ou `*/*/*_Data` que o leitor aceita, até 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, até 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | os circuitos da biblioteca de voltas do FH Companion (início e fim a 50 m), com mais voltas, que `find_track` encontra; ou `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Execute só os testes de um jogo, ou aponte o teste de lancis do Forza para um percurso:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Os testes com jogos instalados leem só dos jogos. Eles não gravam nada nas pastas
dos jogos. As saídas dos testes vão para as pastas temporárias do pytest.

## Convenções {#conventions}

- **Recuse em vez de adivinhar.** Cada leitor lança sua própria exceção
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) com
  uma mensagem que diz o que foi encontrado e por que não foi lido.
- **Verifique com o próprio formato.** Um hash, um CRC, uma cadeia de deslocamentos, uma
  caixa delimitadora guardada, o terreno da pilotagem sobre o solo. Não "não travou".
- **Sem chaves, sem código proprietário incluído.** Veja [Regras e licenças](rules-and-licences.md).
- **Dados confidenciais ficam de fora.** Ficheiros de jogo, exportações, voltas,
  gravações e capturas de ecrã nunca entram no repositório. O `.gitignore` os exclui
  por pasta e por tipo. Os testes usam dados sintéticos e jogos instalados, nunca
  conteúdo de jogo guardado no repositório.
