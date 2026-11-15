---
title: Ficheiros do BeamNG
nav_order: 8
lang: "pt"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Ficheiros do BeamNG: ficheiros de nível, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

O BeamNG.drive traz ficheiros zip simples, então não há contêiner a fazer engenharia
reversa. O trabalho está em ler um nível **da maneira que o jogo lê**: montar os ficheiros
num único sistema de ficheiros, seguir os ficheiros de cena e descodificar o terreno e
as formas compiladas. Estes leitores são acedidos pela exportação de percurso do
[BeamNG.drive](course-beamng.md). O `identify` também reconhece um zip de nível, um
`.cdae` e um `.ter`, e `list` e `extract` aceitam qualquer um dos zips.

Fontes: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## O sistema de ficheiros montado {#the-mounted-file-system}

`Files.of_install(game)` monta um único índice sem diferenciar maiúsculas de
minúsculas sobre o `gameengine.zip`, os zips de `content` (exceto veículos e sons) e os
mods do utilizador (`mods\*.zip`, `mods\unpacked\*`, e uma pasta `levels` do utilizador). Os
acréscimos posteriores substituem os anteriores, como no jogo. As buscas ignoram
maiúsculas porque as próprias referências dos níveis não batem com os zips nesse ponto
(`.DAE` para um `.dae`). Detalhes em [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` acha um caminho da maneira que o jogo acha: como foi dado, relativo ao ficheiro
que o citou, `x.png` como `x.dds`, `x.dae` como `x.cdae` (preferido), e por meio de um
ficheiro JSON `x.png.link` cujo `path` aponta para dentro de `/assets`.

## Ficheiros de cena {#scene-files}

| Origem | Formato | O que é lido |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | um objeto JSON por linha, ou um único array ou mapa JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | as mesmas classes, para níveis mais antigos sem `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript ou JSON | filhos colocados em relação ao prefab, até 8 níveis de profundidade |
| `levels\<name>\forest\*.forest4.json` | uma instância por linha | tipadas pelos registos `TSForestItemData` em `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | o título do nível (as chaves de tradução são ignoradas) |

**Transformações.** `rotationMatrix` são nove números cujas **linhas** são os eixos
próprios do objeto no mundo. Secções de guard-rail encadeadas ao longo de uma estrada
seguem a linha 0 (92%), e a linha de cima inclina com a inclinação da estrada. Prefabs
mais antigos dão `rotation = "x y z degrees"`, uma volta destrógira por esse ângulo (92%
das correntes de trilho se alinham com ela, 19% com o sentido oposto). A escala multiplica
as linhas, e `position` (ou `pos`) é a última linha. A transformação de um filho de prefab
é composta com a do prefab. O `groupPosition` do prefab é um pivô de editor e **não** é
subtraído: um prefab de carrinho só fica sobre o chão sem ele.

Números do TorqueScript são lidos com um padrão tolerante, porque alguns prefabs
distribuídos escrevem valores como `-0.99563-0.0` sem espaço.

## Terreno: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Altura em metros: `position.z + h * maxHeight / 65535`, com `position`,
  `squareSize` e `maxHeight` do `TerrainBlock` (padrões 0, 1 e 2048).
- As linhas correm ao longo de +y. O ponto de grade (i, j) fica em
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- A camada 255 é um buraco.

Verificado: os nós de estrada ficam sobre o terreno a 1-2 cm (mediana) em três níveis.
`h / 32`, ou a outra ordem de eixos, erra por dezenas a centenas de metros.

## Materiais {#materials}

Todo `*.materials.json` fora de `levels\`, mais o do nível atual, indexado por `mapTo`,
`name` e chave:

| Classe | Campos usados |
|---|---|
| `Material`, `CustomMaterial` | mapa de cor (`baseColorMap`, `colorMap` ou `diffuseMap`, primeiro estágio), fator de cor, mapa e fator de opacidade, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | mapa base e `diffuseSize`, mapa de detalhe, tamanho e força, mapa macro, tamanho e força, `groundmodelName`, `annotation` |

As imagens são descodificadas com o Pillow (DDS, PNG e assim por diante), usando um
rascunho de tamanho reduzido quando possível, e guardadas em cache por tamanho. Uma
textura ilegível cai para cor chapada.

## Formas compiladas: `.cdae` {#compiled-shapes-cdae}

`.cdae` é o cache próprio do jogo de cada ficheiro Collada, escrito como MessagePack. O
layout é **documentado pelo BeamNG** (documentation.beamng.com/modding/file_formats/cdae/)
e o leitor o segue:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

O que é lido: limites, nós, objetos, `details` (níveis de detalhe), rotações padrão dos
nós (`Quat16`) e translações, cada vértice, UV, normal, cor, primitiva e índice de
cada malha, e os nomes de material. Os nomes de material são achados no fim do fluxo,
porque as sequências de um adereço animado vêm antes deles, num formato que não é
documentado.

Duas coisas que a documentação não detalha, estabelecidas comparando com os ficheiros
`.dae` de onde as formas foram feitas:

- **As rotações dos nós são as do Torque.** Um `Quat16` lido da maneira de livro gira ao
  contrário. A sua matriz precisa ser **transposta**. Com isso, os limites do mundo de
  cada nó batem com o Collada até ao milímetro. Sem isso, ficam 38 cm fora na mediana.
- **Unidades e eixos já estão aplicados.** Um Collada feito em centímetros ou com Y para
  cima sai do cache em metros, com Z para cima.

Os níveis de detalhe são os `details` com tamanho não negativo, do maior para o menor.
Tamanhos negativos são malhas de colisão e de linha de visão, nunca desenhadas. Objetos
chamados `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` ou `imposter`
nunca são desenhados. Só malhas padrão e ordenadas são desenhadas. Malhas com skinning
(personagens, veículos) e malhas de decalque não são. Tiras e leques de triângulos são
desenrolados, e as faces são reenroladas para concordar com as normais guardadas, o que
o enrolamento do próprio Torque não garante.

Verificado: quase toda forma distribuída é lida. As outras duas são de uma versão antiga.

## Alternativa Collada: `.dae` {#collada-fallback-dae}

Para formas sem `.cdae` (mods, e a forma rara cujo cache é mais antigo), o ficheiro
Collada é lido da maneira que o importador do Torque lê, no mesmo estruturado:

- Níveis de detalhe pela convenção de nomes do Torque: o número no fim do nome do nó de
  malha é o tamanho em pixels em que ela é desenhada (`barrier75`, `barrier40`). Um número
  negativo, ou um nome `collision`/`Colmesh`/`LOS`/`nulldetail`, nunca é desenhado. Uma
  forma sem a convenção tem um só nível.
- Unidades a partir de `<unit meter>`, e Y para cima convertido para Z para cima.
- UVs invertidos para a convenção do cache (v corre para baixo na imagem).

Conferido com o `.cdae` do próprio jogo dos mesmos ficheiros: quase todos os limites
amostrados batem dentro de 1 cm, 583 com a mesma contagem de triângulos, 94% dos UVs dos
materiais idênticos. O teste com jogo instalado exige que 90% de até 60 pares de formas do
ficheiro de arte partilhado concordem dentro de 1 cm.

## Não lido {#not-read}

- Cobertura do solo (relva procedural) e qualquer coisa gerada em tempo de execução.
- Sequências animadas e skinning.
- Veículos e sons (nunca são montados).
