---
title: Entradas de volta
nav_order: 7
lang: "pt"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Entradas de volta {#lap-inputs}

Um **ficheiro de volta** é uma lista de pontos x, y, z: por onde o carro passou. A
forma feita à mão mais rápida é o CSV de [5. Uma tabela `.csv`](#5-a-csv-table)
logo abaixo.

Uma volta diz à exportação de percurso **por onde o carro passou**. Nada mais nela é
usado: velocidade, controlos e forças G pertencem ao lado de telemetria do 3DHeat. A
ferramenta lê posições nos metros do próprio mundo do jogo, além, quando o ficheiro
diz, do jogo e da pista.

Fonte: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## O que o `course` aceita {#what-course-accepts}

O formato é reconhecido olhando o conteúdo do ficheiro, e não o nome, com a exceção de
que `.npz` e `.csv` são reconhecidos pela extensão, e todo o resto é lido como JSON.

### 1. Um documento `heat3d-lap` (qualquer jogo) {#1-a-heat3d-lap-document-any-game}

Gravado pelos gravadores de telemetria do 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y` e `channels.z` são obrigatórios. Linhas em que qualquer
  um dos três não é um número finito são descartadas. Os outros canais são ignorados.
- `game` decide a exportação (veja [Comandos](commands.md#which-game)).
- `track` é usado pelo Assetto Corsa Rally para testar primeiro a etapa indicada.
- Eixos: y é a altura. As voltas do Forza e do AC Rally usam os eixos horizontais do
  jogo como o gravador os escreve. As voltas do BeamNG são esperadas no referencial do
  visualizador, `(x, z, -y)` do mundo de Z para cima do BeamNG (veja
  [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Um ficheiro de rota {#2-a-route-file}

Gravado por `heat3d_capture route` e `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` é uma lista de `[x, y, z]`. Um ficheiro de rota com `bounds` mas sem
posições ainda funciona: os seus dois cantos formam uma linha degenerada, mas uma
caixa utilizável.

### 3. Um ficheiro de volta do FH Companion {#3-an-fh-companion-lap-file}

Os ficheiros de volta por volta da biblioteca gravada pelo FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Um `X`, `Y` ou `Z` ausente é lido como 0. Os ficheiros são gravados com uma marca de
ordem de bytes, então todo JSON é lido como `utf-8-sig`.

### 4. Uma gravação `.npz` {#4-a-npz-recording}

Um ficheiro NumPy com um array `positions` de forma (n, 3).

### 5. Uma tabela `.csv` {#5-a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Colunas chamadas `x`, `y`, `z` (ignorando maiúsculas e espaços em volta) são
  obrigatórias. As outras colunas são ignoradas.
- Linhas que começam com `#` são saltadas. Se a **primeira** linha for `# {json}`, os
  seus `game` e `track` são lidos.
- Linhas que não se leem como números são saltadas.

### 6. Uma pasta {#6-a-folder}

Uma pasta é pesquisada **recursivamente** em busca de ficheiros `.json`, `.npz` e
`.csv`, e todos são concatenados numa única linha de pilotagem. É assim que um
percurso gravado inteiro é guardado: o FH Companion aninha pastas de classe, carro,
ajuste e marcação.

- `course.json` é saltado pelo nome (são metadados, não uma volta).
- Um ficheiro que não pode ser lido é saltado em silêncio. Um ficheiro ruim entre
  centenas não custa os outros.
- O consola informa quantos ficheiros de volta entraram (`12 laps, 18,400 samples`).
- A pasta recebe o jogo que os seus ficheiros indicam, quando eles indicam **apenas
  um**. Um ficheiro que não indica jogo (uma volta do FH Companion, `course.json`, um
  CSV sem a linha de descrição) não conta, então um deles entre as gravações de um
  jogo não tira da pasta o jogo. Ficheiros que indicam dois jogos diferentes são uma
  mistura, e a pasta não recebe nenhum. Uma pasta sem jogo é exportada como Forza, a
  não ser que `--game` diga outra coisa.
- Se nada puder ser lido: "no readable laps under <folder>".

### 7. Um nome de percurso {#7-a-course-name}

Se o argumento não é um ficheiro ou pasta existente, ele é procurado como nome de
percurso na biblioteca do FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. uma pasta cujo nome, sem o sufixo ` (course_...)`, é igual ao nome (sem diferenciar
   maiúsculas de minúsculas);
2. senão, a única pasta cujo nome contém o nome dado.

Assim, `"Example Circuit"` encontra
`Example Circuit (course_1200_3400_to_1175_3400)` sem que ninguém precise saber as
coordenadas. Vários resultados são um erro, que lista todos. Um percurso encontrado
pelo nome não traz jogo, então é exportado como Forza, a não ser que `--game` diga outra coisa.

## O que o `terrain --route` aceita {#what-terrain-route-accepts}

`terrain` precisa do `bounds` do ficheiro de rota (forma 2 acima),
`{"min": [x, y, z], "max": [x, y, z]}`. Sem `bounds`, ele para com
"<file> has no bounds; --route takes a route file with "bounds": {...}". O ficheiro é
lido como UTF-8, com ou sem marca de ordem de bytes, como todo JSON de volta. Se o
mesmo ficheiro também tiver pelo menos 10 posições legíveis pelas regras acima, elas
estreitam o recorte para um corredor e guiam o detalhe.

## Como a volta é usada {#how-the-lap-is-used}

| Uso | Detalhe |
|---|---|
| nome | o nome do ficheiro, ou o nome da pasta sem ` (course_...)`; torna-se o nome padrão do ficheiro de saída |
| distância percorrida | a soma dos intervalos entre amostras consecutivas (impressa como `m driven`; numa pasta, inclui os saltos entre ficheiros) |
| caixa | a extensão de x e z acrescida de `--margin`; a altura nunca é limitada |
| corredor | o x e o z de cada amostra, veja [Exportação do percurso](course-export.md#the-corridor) |
| detalhe | a distância de cada cópia colocada até à amostra mais próxima, veja [Níveis de detalhe e o orçamento](detail-budget.md) |

Uma volta com menos de duas amostras é recusada ("holds no driving").

## Erros {#errors}

| Mensagem | Significado |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | o ficheiro não é JSON (nem `.npz` nem `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON de outro formato |
| `<file> has no x, y and z columns` | um CSV sem esses cabeçalhos |
| `<file> has no positions array` | um `.npz` sem `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | um nome, mas não há biblioteca do FH Companion |
| `'<name>' matches 3 courses: A, B, C` | seja mais específico |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | só para buscas por nome e para `courses` |
