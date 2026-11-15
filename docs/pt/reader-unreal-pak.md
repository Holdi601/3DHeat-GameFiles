---
title: Unreal .pak
nav_order: 1
lang: "pt"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Lista e extrai** ficheiros `.pak` do Unreal 4.22 a 5.x: versões 8, 9, 10, 11 e 12,
compressão Zlib, Gzip e Oodle, e ficheiros cifrados quando a chave AES é fornecida.
Não interpreta o que extrai (`.uasset`, `.umap`).

Fonte: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Comandos: `identify`, `list`, `extract` (veja [Comandos](commands.md)).

## Layout {#layout}

O rodapé fica no fim do ficheiro e é achado pesquisando os últimos 1.024 bytes pelo magic
`0x5A6F12E1`. A ordem dos seus campos importa:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

A flag de cifragem fica **antes** do magic. Se for tirada de depois do magic, cai no "Z"
de "Zlib". Aí todo ficheiro se declara cifrado, e todo nome de método perde a primeira
letra ("lib", "odle"), uma falha silenciosa e plausível. A versão é o byte baixo, porque builds
de "índice congelado" põem um bit alto.

O índice traz o ponto de montagem, o índice de hash de caminho, o índice completo de
diretórios e um bloco de **entradas codificadas**: uma forma em bits empacotados em que uma
palavra de flags diz quais números são de 32 bits, o método de compressão (6 bits), se a
entrada é cifrada, a quantidade de blocos (16 bits) e o tamanho do bloco em unidades de
2.048 (6 bits). O tamanho de bloco todo nuns é um escape: o tamanho real vem num u32
**antes** do deslocamento. Num ficheiro grande, lê-lo depois dos tamanhos deslocou 7% das
entradas em quatro bytes e lhes deu deslocamentos na casa dos exabytes.

O registo completo de cada entrada se repete logo antes do seu conteúdo, então o conteúdo
começa após `8+8+8+20+4+1+4` bytes, mais `4 + 16 x blocks` quando comprimido. Blocos
cifrados são preenchidos até 16 bytes.

## O que é lido e o que é recusado {#what-it-reads-and-what-it-refuses}

| Caso | Resultado |
|---|---|
| versões 8-12 | lido |
| qualquer outra versão | `pak version N; this reader handles 8-12` (versões anteriores guardam uma lista plana de registos, e não havia ficheiro para testar) |
| sem magic de rodapé | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| índice fora do ficheiro | recusado: o rodapé não se leu como afirma |
| índice só de hash de caminho | recusado: os nomes dos ficheiros foram embaralhados por hash na construção e não podem ser recuperados |
| entradas na lista de overflow do índice (diretório com deslocamento -1) | saltadas, não inventadas |
| índice cifrado, sem chave | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Na linha de comando, uma linha e código de saída 1 |
| entrada cifrada, sem chave | `EncryptedPak` na leitura |
| métodos Zlib, Gzip, Oodle | descomprimidos (o Oodle precisa de uma biblioteca, veja [Oodle](reader-oodle.md)) |
| qualquer outro método | `compression method '...' is not supported` |

## Chaves {#keys}

`--key` em `list` e `extract` recebe uma chave AES-256 já disponível, como 64 dígitos
hexadecimais, com ou sem `0x`. Qualquer outra coisa é recusada antes de o ficheiro ser aberto,
com código de saída 2. A decifragem é AES-256-ECB pelo pacote `cryptography`. Não existe
caminho de código que obtenha uma chave: nenhuma chave incluída, nenhuma busca em executáveis,
nenhuma leitura de memória. Veja [Regras e licenças](rules-and-licences.md).

## Verificado {#verified}

Contra ficheiros distribuídos de mais de um jogo, cada entrada, inclusive num ficheiro muito
grande, bateu com o SHA-1 que o Unreal grava antes de cada conteúdo. Esse hash cobre os bytes
como guardados, então uma correspondência significa que a descodificação do índice, o
deslocamento do conteúdo e cada fronteira de bloco comprimido estavam certos. Os testes com
jogo instalado (`test_pak.py`) repetem isso em até quatro pacotes não cifrados
encontrados em `steamapps\common\*\...\Content\Paks`. Eles verificam se o deslocamento de cada
entrada cai dentro do ficheiro, e se o SHA-1 bate numa amostra aleatória de 150 entradas por
ficheiro.
