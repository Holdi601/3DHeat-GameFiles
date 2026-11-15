---
title: "Oodle"
nav_order: 3
lang: "pt"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: encontrado, não incluído {#oodle-found-not-bundled}

A maior parte do conteúdo Unreal distribuído, e alguns payloads Frostbite, é comprimida com **Oodle** (RAD Game Tools, agora Epic). O Oodle é proprietário. Não existe uma versão redistribuível nem uma implementação em Python, e o `oo2core_*.dll` está licenciado ao produto que o distribui. Por isso, esta ferramenta **encontra uma cópia que já está na sua máquina e carrega-a**. Nunca traz uma consigo. O FModel e o UModel funcionam da mesma forma.

Fonte: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Onde procura {#where-it-looks}

Ganha o primeiro ficheiro que existir, nesta ordem:

1. Um caminho explícito passado por quem chama (API Python).
2. `HEAT3D_OODLE`: um caminho para a DLL, ou para uma pasta que a contenha.
3. Uma pesquisa rasa, com um nível de profundidade, em
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - o `steamapps\common` de cada biblioteca do Steam

   Para cada pasta filha `<jogo>`, verifica `<jogo>`, `<jogo>\Engine\Binaries\ThirdParty\Oodle\Win64` e `<jogo>\Engine\Binaries\Win64`.

Nomes de ficheiro testados, do mais recente para o mais antigo: de `oo2core_9_win64.dll` até `oo2core_3_win64.dll`. O formato é retrocompatível, por isso uma biblioteca mais antiga normalmente ainda funciona.

A pesquisa não é, de propósito, uma varredura recursiva de todos os discos, que levaria minutos. Se não encontrar nada, defina `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Uma pasta funciona tão bem como o próprio ficheiro: os nomes de DLL indicados acima são testados dentro dela.

Uma instalação do Unreal Engine traz uma em `Engine\Binaries\ThirdParty\Oodle`, que é a fonte mais limpa para um programador. Muitos jogos trazem uma ao lado do seu executável. Os jogos Unreal 5 costumam ligar o Oodle estaticamente e não trazem DLL, por isso a cópia encontrada pode pertencer a outro jogo que não o ficheiro que está a ser lido. O formato é o mesmo, em qualquer dos casos.

## Como é chamado {#how-it-is-called}

O `OodleLZ_Decompress` é chamado através de `ctypes` com o comprimento de saída esperado (o índice do ficheiro sabe sempre esse valor, e o Oodle não o consegue deduzir), com a descodificação resistente a dados corrompidos ligada (a entrada não é de confiança), sem verificação CRC (o SHA-1 do próprio pak já cobre os bytes) e sem threads. Um resultado com o comprimento errado é um erro. A biblioteca é carregada uma vez por execução.

## Quando não existe nenhuma {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Uma entrada que não pode ser descomprimida é um erro, nunca lixo plausível.

O carregador só funciona no Windows (procura `*_win64.dll`). As bibliotecas do Linux e do macOS não são procuradas.
