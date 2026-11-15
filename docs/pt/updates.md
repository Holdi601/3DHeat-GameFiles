---
title: "Atualizações"
nav_order: 13
lang: "pt"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Atualizações {#updates}

O 3DHeat GameFiles verifica as versões publicadas deste repositório no GitHub quando arranca, diz quando há uma versão mais nova e oferece-se para atualizar. Os seus próprios ficheiros (voltas, exportações) nunca são tocados.

Fonte: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
A versão instalada é o ficheiro [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) do repositório.

## A verificação no arranque {#the-check-at-start-up}

Cada execução de `python -m heat3d_gamefiles ...` chama a verificação antes de analisar os seus argumentos:

- Pergunta a `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`, com um limite de **5 segundos**.
- A resposta fica em cache durante **6 horas** em `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (ou `~/.cache/3DHeat/...` sem `LOCALAPPDATA`). Durante esse tempo não é feito nenhum pedido. "Ainda não há versão" (HTTP 404) também fica em cache.
- Sem ligação, com limite de pedidos atingido ou atrás de um proxy, a verificação simplesmente retorna e a ferramenta corre na versão que tem.
- Se a etiqueta da versão mais recente (`v1.2.3` ou `1.2.3`; o que vier depois de `-` ou `+` é ignorado) for mais nova do que `VERSION`, escreve no stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **Num terminal** (stdin e stderr são ambos um TTY) pergunta `Update now? [Y/n]`. Enter, `y`, `yes`, `j` ou `ja` atualizam. Depois de uma atualização bem-sucedida, o **mesmo comando é iniciado de novo** no código novo, e o seu código de saída é passado adiante.
- **Sem terminal** (uma execução agendada, um pipe) apenas imprime ``Run `python -m heat3d_update` in <folder> to update.`` e continua.

## Atualizar a pedido {#updating-on-request}

```
python -m heat3d_update          # atualiza para a versão mais recente, se existir
python -m heat3d_update --check  # diz apenas se há uma versão mais nova
```

Isto pergunta sempre ao GitHub (sem cache). Imprime `Up to date: 1.0.1.`, `No release found (...)`, ou o que fez. O código de saída é 1 se a atualização não puder ser aplicada.

## Como uma atualização é aplicada {#how-an-update-is-applied}

| Instalado como | Atualização |
|---|---|
| um **clone git** (uma pasta `.git` e o `git` no PATH) | `git pull --ff-only`. **Recusada** enquanto os ficheiros versionados tiverem alterações locais: "this checkout has local changes; commit or stash them, then run `git pull`". Os ficheiros não versionados não bloqueiam |
| uma **cópia descarregada** | o ficheiro de código-fonte da versão (`zipball_url`) é descarregado e descompactado numa pasta temporária, ignorando qualquer caminho que saia dela; o seu `VERSION` tem de ser igual à versão da release, senão nada é copiado; depois os seus ficheiros são copiados por cima desta pasta |

Ao copiar a partir de um ficheiro, os ficheiros que não fazem parte da versão (voltas, exportações, ambientes virtuais, tudo o que foi criado localmente) ficam intactos. A atualização também tenta apagar os módulos `.py` que uma versão retirou dos seus pacotes, para que um módulo antigo não tape o seu substituto. Procura pacotes `heat3d_*` na raiz do ficheiro e uma pasta abaixo, e remove os ficheiros `.py` que a versão já não tem.

## Desligar {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Qualquer valor diferente de vazio, `0`, `false` ou `no` desliga tanto a verificação de arranque como a oferta. O `python -m heat3d_update` continua a funcionar quando executado à mão.
