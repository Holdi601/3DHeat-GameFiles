---
title: "Carros do Forza"
nav_order: 6
lang: "pt"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Carros do Forza: `cars` {#forza-cars-cars}

Grava todos os carros de um Forza instalado, no nível de detalhe baixo do próprio jogo, num único ficheiro para o separador Análise de corrida do visualizador (ela desenha um carro por cada volta feita). Assim, cada carro gravado é desenhado na sua própria forma e no seu tamanho real.

![cars --help](../assets/img/cars-help.svg)

## Passo a passo {#step-by-step}

1. **Execute** com o jogo instalado (ele é encontrado nas bibliotecas do Steam e em `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Ou indique a pasta do jogo:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<pasta do Forza>" -o forza.h3dcars
   ```

2. **Carregue-o no visualizador**: **Carregar ficheiro de carros…** nas definições de visualização, ou solte o ficheiro no separador Análise de corrida; ele fica nesse navegador. As voltas cujo número de carro está no ficheiro passam a ser desenhadas como esse próprio carro (veja a [documentação da repetição de corrida](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars) do visualizador).

3. **Execute de novo** quando o jogo ganhar carros novos. Demora segundos e escreve cerca de 5 MB.

## Opções {#options}

| Opção | Predefinido | Significado |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | o ficheiro a escrever |
| `--game FOLDER` | o jogo instalado encontrado | a pasta do jogo |

## O que há no ficheiro {#what-is-in-the-file}

Para cada ficheiro de carro em `media/Cars`: o modelo `ProxyLOD` que ele traz (cerca de 900 triângulos), o número do carro tal como a telemetria o indica, a marca, a etiqueta do modelo e o ano a partir do nome do ficheiro, e as rodas e as luzes traseiras. As formas estão em metros, na escala 1:1 do carro. Um ficheiro sem tal modelo (um adereço de tráfego) é identificado e deixado de fora.

O ficheiro é feito para o visualizador 3DHeat; o seu formato, para quem o quiser ler noutro lugar ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Parte | Formato |
|---|---|
| ficheiro inteiro | comprimido em gzip |
| marca | os 8 bytes `H3DCARS1` |
| tamanho do cabeçalho | u32 little-endian |
| cabeçalho | JSON em UTF-8: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| enchimento | espaços até um múltiplo de 4 bytes |
| dados | por carro: vértices como três i16 cada (milímetros; x para a direita, y para cima, z para a frente), depois triângulos como três u16 cada |

Cada entrada de `cars`: `key`, `ordinals` (os números do carro tal como a telemetria os indica), `make`, `model`, `year`, `height` e `length` (m), `wheels` (por executa `[x, y, z, radius]`, m), `lights` (pontos das luzes traseiras `[x, y, z]`, m), e `vertexAt`, `vertices`, `faceAt`, `faces` (deslocamentos em bytes a partir do início dos dados, e contagens).

O ficheiro contém conteúdo do jogo: serve para a máquina onde foi feito, não para ser passado a outros ([Regras e licenças](rules-and-licences.md)).
