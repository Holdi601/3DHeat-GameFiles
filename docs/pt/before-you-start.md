---
title: Antes de começar
nav_order: 2
lang: pt
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Antes de começar {#before-you-start}

Nunca usou a linha de comando? Esta página leva você do zero a uma ferramenta funcionando em
cerca de dez minutos. Você digita comandos em uma janela chamada **terminal**, e
a ferramenta responde com texto.

## 1. Instalar o Python {#install-python}

1. Vá a [python.org/downloads](https://www.python.org/downloads/) e baixe o
   **Python 3.10 ou mais recente**.
2. Execute o instalador. Na primeira tela, marque **"Add python.exe to PATH"**,
   depois clique em **Install Now**.

## 2. Obter a ferramenta {#get-the-tool}

- **Com o git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Sem o git:** na [página do GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  clique no botão verde **Code** e depois em **Download ZIP**, e descompacte.

## 3. Abrir um terminal na pasta da ferramenta {#open-a-terminal-in-the-tools-folder}

- No Explorador de Arquivos, abra a pasta que contém o `README.md`. Clique na barra de
  endereço, digite `cmd` e pressione Enter. Abre uma janela preta, já nessa pasta.
- Ou abra o **Terminal do Windows** e vá até lá com `cd`:

  ```
  cd "C:\Users\voce\Downloads\3DHeat-GameFiles"
  ```

## 4. Instalar o que a ferramenta precisa {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Você deve ver linhas terminando em `Successfully installed ...`.

## 5. Conferir se funciona {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Você deve ver `usage: heat3d_gamefiles [-h]` e uma lista de verbos (`identify`,
`list`, `extract`, `course`, ...). Isso é sucesso: a ferramenta está pronta.

## Como ler os exemplos {#reading-the-examples}

- `<algo>` é um **marcador**: digite o seu próprio valor no lugar, sem os
  sinais de menor e maior. `<lap file>` vira, por exemplo, `laps\minha_volta.json`.
- `[--opção]` entre colchetes é **opcional**: deixe de fora se não precisar.
- Um caminho com espaços precisa de **aspas duplas**: `"C:\Meus Jogos\volta.json"`.
- Execute todo comando na pasta da ferramenta (passo 3).

## Quando algo dá errado {#when-something-goes-wrong}

| Você vê | O que fazer |
|---|---|
| `'python' is not recognized` | O Python não está instalado, ou "Add to PATH" não foi marcado. Execute o instalador de novo, marque a opção e depois abra um novo terminal. |
| `No module named heat3d_gamefiles` | O terminal está na pasta errada. Use `cd` para ir à pasta que contém o `README.md`. |
| `No module named numpy` (ou outro nome) | O passo 4 foi pulado. Execute `pip install -r requirements.txt`. |
| `can't open file` / `not found` com um caminho | O caminho tem espaços e não tem aspas, ou tem um erro de digitação. Coloque-o entre aspas duplas. |

Mais mensagens e as suas soluções: [Solução de problemas](../troubleshooting.md).
