---
title: BeamNG.drive
nav_order: 2
lang: "pt"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Exportação de percurso: BeamNG.drive {#course-export-beamng-drive}

A exportação do BeamNG lê um nível da maneira como o jogo o monta, e depois escreve o mesmo tipo de ficheiro que a exportação do Forza escreve: o chão por cada quadrado de 512 m com uma textura cozida, a estrada e o chão solto como partes próprias, modelos colocados por categoria, e a água.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <pasta do nível>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Fontes: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (instalação, sistema de ficheiros, cena, terreno, materiais),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (a exportação),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) e
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (formas).
Formatos de ficheiro em detalhe: [Ficheiros do BeamNG](reader-beamng.md).

## O referencial da volta {#the-laps-frame}

A exportação `course` espera posições do BeamNG no **referencial do visualizador**:
`(x, z, -y)` do mundo do BeamNG, com Z para cima, em metros. Essa é a rotação que o gravador de telemetria do 3DHeat aplica. A exportação devolve a volta ao referencial do BeamNG (`(x, -z, y)`), trabalha aí, e escreve tudo outra vez no referencial do visualizador. Isto é uma rotação, não um espelho, por isso nada sai espelhado. Uma volta gravada no referencial bruto do BeamNG não seria colocada corretamente. Isto não foi testado com outros gravadores.

O jogo é tomado como BeamNG quando o ficheiro `heat3d-lap` diz `"game": "beamng"`, ou quando passa `--game beamng`.

## Encontrar a instalação {#finding-the-install}

- `--install <pasta>`: a pasta que contém `gameengine.zip` e `content`.
- Senão, verifica-se a `steamapps\common\BeamNG.drive` de cada biblioteca do Steam, à procura desses dois.
- Se nenhum funcionar: "no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip)."

## O sistema de ficheiros {#the-file-system}

O BeamNG distribui ficheiros zip simples e monta-os num só sistema de ficheiros a que os níveis se referem (`/art/shapes/...`, `/assets/materials/...`). A exportação constrói o mesmo: um único índice sem distinção de maiúsculas sobre

1. `gameengine.zip`,
2. cada `*.zip` em `content`, exceto `content\vehicles\*` e os ficheiros cujos nomes começam por `art_sound` ou `audio`,
3. o conteúdo do utilizador, com o layout mais recente primeiro: em `%LOCALAPPDATA%\BeamNG\BeamNG.drive` e `%LOCALAPPDATA%\BeamNG.drive`, a pasta `current` e a pasta de versão com o número mais alto. De cada uma: `mods\*.zip`, cada pasta em `mods\unpacked`, e a própria pasta do utilizador se tiver uma pasta `levels`.

As adições posteriores ganham, como no jogo, por isso um mod substitui o que sobrepõe. Os mods estão sempre incluídos numa exportação de percurso.

Os caminhos que um nível indica são resolvidos como o jogo os resolve: tal como estão, depois em relação ao ficheiro que os indicou, e para cada um também como o `.dds` para que uma textura foi cozida, o `.cdae` para que um `.dae` foi compilado, ou através de um ficheiro `.link` que aponta para `/assets`.

## Qual nível {#which-level}

Sem `--level`, cada nível é avaliado pela quantidade do percurso que fica sobre ele:

- São usadas até 500 amostras da volta, espaçadas por igual.
- Para o `TerrainBlock` de cada nível, a extensão do terreno é lida dos primeiros cinco bytes do seu ficheiro `.ter`, por isso um nível onde a volta não está por perto não custa nada. Se pelo menos 30% das amostras estiverem dentro da extensão, as alturas são lidas. Uma amostra conta como **sobre** o terreno quando está entre 1 m abaixo e 3 m acima dele (`ON_GROUND`), porque o ponto de referência de um carro é a carroçaria, não os pneus.
- Se nenhum nível chegar a 50%, os níveis são também avaliados pelas suas **estradas**. Alguns níveis continuam para além do seu mapa de alturas (as suas bordas continuam como placas de rocha). Uma amostra está numa estrada quando fica dentro da meia-largura da estrada mais 4 m (pelo menos 6 m) de um segmento `DecalRoad`, e entre 2 m abaixo e 4 m acima dele.
- O melhor nível ganha se tiver pelo menos 30%. Senão, a exportação para e lista os três melhores: "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

A consola escreve `on <nível>: 87% of the lap lies on its terrain` (ou `roads`). `--level` é comparado sem distinguir maiúsculas com os nomes das pastas dos níveis.

## Ler o nível {#reading-the-level}

Do que um nível é feito, cada parte verificada contra os níveis distribuídos (detalhes em [Ficheiros do BeamNG](reader-beamng.md)):

- **Cena**: `levels\<nome>\main\**\*.level.json` (um objeto JSON por linha, ou um array JSON), ou um ficheiro `.mis` para níveis mais antigos. A ferramenta lê os objetos `TSStatic` (modelos colocados, saltando os ocultos), os objetos `Prefab` (aninhados até 8 níveis, `.prefab` do TorqueScript ou `.prefab.json`), os objetos `DecalRoad` (estradas pintadas), `TerrainBlock`, `WaterPlane`, `WaterBlock` e `River`.
- **Itens de floresta**: `levels\<nome>\forest\*.forest4.json`, tipificados pelos registos `managedItemData.json`. Barreiras, vedações e rochas são itens de floresta tantas vezes como as árvores.
- **Terreno**: o campo de alturas `.ter` e o seu mapa de camadas.
- **Materiais**: todos os `*.materials.json` fora de `levels\`, e os deste nível.

## O corredor e os decalques de estrada {#the-corridor-and-the-road-decals}

O corredor é a margem de `--margin` metros à volta da volta, no plano x/y do BeamNG (veja [Exportação de percursos](course-export.md#the-corridor)). Um corredor de alcance de `margem + 60 m` seleciona os candidatos.

Os **decalques de estrada** (`DecalRoad`) são onde estão a maioria das estradas do BeamNG: pintados sobre o terreno, não modelados. Os decalques cuja extensão toca o corredor de alcance são tomados pela ordem de desenho do jogo (`renderPriority` decrescente, depois a ordem do ficheiro), e dispostos como faixas:

- Os nós (x, y, z, largura) são interpolados por uma **spline Catmull-Rom centrípeta** a cada 1 m. A variante uniforme volta sobre si própria onde os nós se juntam numa curva fechada. As estradas em circuito fecham-se.
- Cada borda toma a altura do terreno onde o terreno está a menos de 1,5 m da altura própria da estrada, e mantém a altura da estrada no resto (numa ponte).
- O nome do material decide o que um decalque pinta:

| Tipo | O nome do material corresponde (vence a primeira correspondência) |
|---|---|
| marcas de pneus | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| sobreposição (cosmética) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| marcações | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| solto | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| estrada | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| sobreposição | tudo o resto |

## O chão {#the-ground}

O campo de alturas do terreno dentro do corredor torna-se triângulos:

- Um quadrilátero por quadrado de terreno cujo centro está no corredor. Os quadrados com a camada 255 (buracos) são saltados. Cada quadrilátero são dois triângulos, com a diagonal a alternar como o terreno do Torque o faz.
- As alturas são `position.z + h * maxHeight / 65535`. As normais vêm das diferenças de altura.
- Cada quadrado é classificado pela sua **camada**: o nome da camada com o modelo de chão e a anotação do material do terreno. Palavras de pavimento tornam-no `road`, `grass/forest/rock/moss/leaves/cliff/stone` tornam-no `terrain`, e palavras de solto tornam-no `loose` (gravilha e terra). Tudo o resto é `terrain`.
- Depois, os **decalques de estrada e de solto** sobrepõem-se aos quadrados que cobrem, pela ordem de desenho, por isso o último decalque pintado decide.
- Os vértices são divididos por quadrado de 512 m (`floor(x / 512)`, `floor(y / 512)`), por isso cada parte cabe exatamente numa imagem: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

A consola escreve `what the ground is made of` com as contagens de triângulos por tipo.

### Superfície de condução modelada {#modelled-driving-surface}

Os circuitos do BeamNG são modelos tanto como são terreno. A pista de um autódromo pode ser uma malha com as suas linhas, borracha e lombas como malhas próprias por cima. Por isso, os modelos colocados nas categorias estrada, lancis, berma, adereços e pontes são procurados por superfície de condução. Por material:

| Superfície | Decidida por (primeira correspondência) |
|---|---|
| marcas de pneus | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` no nome, no tipo de chão ou na anotação |
| marcações | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` no nome do material |
| lancis | `rumble`, `kerb`, `curb` |
| estrada | tipo de chão `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, ou o nome contém `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| solto | tipo de chão `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| berma | `sidewalk` |
| (a categoria própria do modelo) | para modelos já classificados como estrada, lancis ou berma |

Desses materiais, os triângulos **voltados para cima** (normal z acima de 0,5) dentro do corredor são retirados do modelo e tornam-se chão. São pintados na textura cozida do bloco e escritos como partes como `ground:road 3_-2 asphalt_light`. As marcações e as marcas de pneus são só pintadas. Os restantes triângulos do modelo ficam com o modelo. Estes modelos nunca são simplificados nem deixados de fora pelo orçamento, porque uma pista grosseira é uma pista errada.

## A textura cozida do chão {#the-baked-ground-texture}

Cada quadrado de 512 m que tem chão recebe uma imagem de `--texture-size` pixels (2048 = 25 cm por pixel), desenhada da maneira como o jogo desenha o seu chão:

1. **Camadas do terreno.** Por pixel, as camadas dos quatro quadrados de terreno à volta são misturadas bilinearmente. Cada camada é colorida como o jogo a colore: o **mapa base** do material esticado sobre `diffuseSize` metros (ou todo o terreno), depois os mapas de **detalhe** e **macro** como sobreposições cinzentas (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutro). As suas predefinições repetem-se a cada 2 m e 60 m, com intensidades 0,5 e 0,3, a menos que o material diga o contrário. Uma camada sem material recebe a cor lisa da sua superfície. A linha 0 do mapa base é o norte.
2. **Decalques de estrada** que são pintados só no terreno, pela ordem de desenho, cada um com a sua própria textura, mapa de opacidade, tom e opacidade, ao longo da faixa. Os níveis distribuídos usam prioridades perto de 12-16 para as bases de asfalto, 10 para as marcações e 4 para a borracha.
3. **Superfície de condução modelada** vista de cima: primeiro as bases, depois as sobreposições, cada uma na textura repetida do próprio modelo a um texel por pixel de cozedura.
4. **Decalques que se projetam também sobre objetos** (`overObjects`), por último.

Com `--no-textures`, nada é cozido: as partes de chão recebem cores lisas, e as marcações e marcas de pneus modeladas tornam-se partes próprias, elevadas **3 cm**.

## Modelos colocados {#placed-models}

Os candidatos são todos os `TSStatic`, filhos de prefab e itens de floresta cuja origem está no corredor de alcance. Um candidato é desenhado se a caixa delimitadora mundial da sua forma toca o corredor.

A **categoria** vem da anotação do próprio nível e do caminho da forma. A primeira regra que corresponder ganha:

| Categoria | Anotação | Caminho ou nome contém |
|---|---|---|
| cenário de fundo (nunca desenhado) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| lancis | | `kerb`, `curb`, `rumble` |
| estrada | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| berma | `SIDEWALK`, `COBBLESTONE` | |
| árvores (só com `--trees`) | `NATURE` | tree, foliage, bush, grass, plant e palavras semelhantes |
| rochas | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barreiras | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| sinais | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| pontes | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infraestrutura | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| edifícios | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| adereços | | tudo o resto |

As **formas** são lidas do `.cdae` compilado, ou do `.dae` do Collada onde não há cache (mods). Uma forma que não pode ser lida é contada: `N copies of M models could not be read`. Materiais com nome ou textura `invisible`, `collision` ou `nodraw` nunca são desenhados.

**Texturas.** Os modelos são agrupados por categoria e material em partes com o nome `structure:<categoria> <material>` (ou `ground:kerbs <material>`). Um grupo recebe a textura de cor do seu material a até **256 px**, só se as suas UV ficarem dentro de 0-1 (98% dos vértices entre -0,02 e 1,02). O visualizador junta as texturas num atlas e não consegue repetir uma. Um grupo cuja textura se repete é desenhado na cor média da textura (ponderada pelo alfa, em sRGB, vezes o tom do material), ou na cor da categoria se não tiver textura.

**Detalhe** segue o esquema comum em [Níveis de detalhe e o orçamento](detail-budget.md). Os níveis de detalhe do BeamNG são os `details` da forma (do maior tamanho em pixels para o menor). Acima do orçamento, saem primeiro as cópias mais distantes. Lancis e modelos com superfície de condução nunca são simplificados nem deixados de fora.

`--no-placed` deixa de fora as estruturas mas continua a manter a superfície de condução modelada. `--trees` acrescenta a categoria das árvores.

## Água {#water}

| Fonte | Desenhada como |
|---|---|
| `WaterPlane` (o mar) | um quadrilátero de 4 m à altura da água por cada célula do corredor onde nenhum terreno chega a essa altura |
| `WaterBlock` | um quadrilátero, o quadrado unitário em z local = 0 na transformação do bloco (por isso a sua escala define o tamanho), se tocar o corredor; se z = 0 é a superfície do bloco não está verificado |
| `River` | uma faixa através dos seus nós, se tocar o corredor |

Toda a água é uma parte plana, `water:water`.

## Não desenhado {#not-drawn}

- Cobertura do chão (relva processual).
- Cenário colocado à volta da borda do mundo (`backdrop` e similares).
- Texturas de modelos que se repetem, que saem como uma cor média (veja acima).
- Formas skinned (veículos, personagens) e malhas de decalque dentro das formas.

## Verificações que o sustentam {#checks-behind-it}

Como indicado no código-fonte, medido nos níveis distribuídos:

- Os nós das estradas ficam sobre o terreno a 1-2 cm (mediana) nos níveis verificados, com `h * maxHeight / 65535` e linhas ao longo de +y. `h / 32` ou a outra ordem dos eixos erram por dezenas a centenas de metros.
- As secções de carril encadeadas ao longo de uma estrada seguem a linha 0 de `rotationMatrix` (a grande maioria).
- A rotação do nó do `.cdae` tem de ser transposta. Com isso, os limites do mundo coincidem com o `.dae` de origem ao milímetro. A forma canónica está errada em 38 cm (mediana).
- Exportado em vários níveis distribuídos de todos os tipos, em segundos a minutos cada um.
