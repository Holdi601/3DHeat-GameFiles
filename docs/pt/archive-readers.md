---
title: Leitores de ficheiros
nav_order: 9
lang: "pt"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Leitores de ficheiros {#archive-readers}

Um **contêiner** (ou ficheiro) é um ficheiro grande em que um jogo empacota muitos
ficheiros. Um **CRC** ou hash é uma impressão digital curta de alguns bytes: se
ela bate, os bytes foram lidos corretamente. Uma **caixa delimitadora** é a menor
caixa em volta de um modelo.

Por trás dos comandos há leitores para os contêineres que os jogos usam. Os
formatos deles não são documentados, com exceção do VPK da Valve e do `.cdae` do
BeamNG. Por isso, "suportado" precisa significar **verificado com ficheiros
reais**, e não apenas "não travou". Cada leitor se verifica com algo que o formato
garante: um hash, um CRC, uma cadeia de deslocamentos que precisa fechar, uma
caixa delimitadora guardada. Quando uma verificação falha, o leitor recusa com
uma mensagem em vez de adivinhar. Uma malha errada parece certa até alguém a
colocar ao lado da pista.

| Leitor | Módulo | Lê | Não lê | Chamado por |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versões 8 a 12: índice, entradas, blocos Zlib/Gzip/Oodle, AES com uma chave fornecida | versões anteriores à 8, índices só com hash de caminho, entradas do overflow, conteúdo de recursos | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, verificado na v8), pacotes zen, propriedades sem versão de algumas classes de componentes, malhas estáticas já cozidas, texturas, texturas virtuais em streaming | contêineres cifrados, pacotes versionados, malhas só Nanite, propriedades de outras classes | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | blocos Oodle por meio de uma biblioteca que já está na máquina | qualquer coisa sem essa biblioteca; ela nunca é incluída na ferramenta | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` formato 22 ou mais (Unity 2020 a 6000), pacotes `UnityFS`, malhas sem compressão, incluindo `.resS` | formatos anteriores a 2020, árvores de tipos embutidas, malhas comprimidas, qualquer classe que não seja `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | tabelas `.toc` de árvores DbObject e tabelas binárias de secções, pacotes de instalação, localizações de chunks, bundles embutidos e seus manifestos, partições RIFF EBX, malhas MeshSet, o heightfield do terreno, texturas BC1/BC3/BC7 e seus blocos de shader, posicionamento de grupos de modelos estáticos | tabelas ofuscadas com XOR, a cor do terreno perto do chão e seus buracos, mapas de normais, alfa que não seja de recorte | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versões 1 e 2, ficheiros divididos, dados de pré-carga, verificação de CRC | recursos compilados (`.vmdl_c`, `.vtex_c`), o formato da malha de navegação do CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, sem compressão), geometria `.modelbin`, texturas `.pb` (BC1, BC7, RGBA), posicionamentos `.pgeo`, hashes de textura dos materiais | outros formatos de vértice e de índice, outros formatos de textura, camadas de material do shader do terreno | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` e `extract` (`.minizip`) |
| [Ficheiros do BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | o sistema de ficheiros montado dos zips, cenas em JSON e TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiais | malhas com skinning e de decalque, sequências animadas, cobertura procedural do solo | `course` (BeamNG), `identify` (zips, `.cdae`, `.ter`), `list` e `extract` (zips) |

## Regras que todo leitor segue {#rules-every-reader-follows}

- **Nenhuma chave vem junto, nenhuma é recuperada.** Um ficheiro cifrado só
  abre com uma chave passada (Unreal `.pak`, `--key`). Um contêiner
  IoStore cifrado é recusado. Nada procura uma chave dentro de um
  executável, nem lê a memória de outro processo. Veja
  [Regras e licenças](rules-and-licences.md).
- **Nenhum código proprietário incluído.** O Oodle é carregado de um jogo ou de
  um motor já instalado na máquina.
- **Recuse em vez de adivinhar.** Uma versão, um codec, um formato de vértice ou
  de textura desconhecido gera um erro específico, como:
  `texture format 42 has not been identified; refusing to guess`
- **Somente leitura.** Nenhum leitor grava dentro de uma pasta de jogo. As
  exportações vão para o lugar indicado.

## O que significa "verificado" {#what-verified-meant}

Os números de verificação citados nestas páginas vêm das docstrings dos módulos.
Eles foram medidos em jogos instalados enquanto cada leitor era escrito. Os
testes sintéticos (veja [Desenvolvimento](development.md)) fixam os layouts dos
campos. Os testes com jogos instalados repetem algumas verificações quando o
jogo está na máquina, e são saltados quando não está. Os números que nenhum teste
cobre não foram verificados de novo desde então.
