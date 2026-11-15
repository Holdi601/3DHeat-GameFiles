---
title: Regras e licenças
nav_order: 12
lang: "pt"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Regras e licenças {#rules-and-licences}

Três regras moldam a ferramenta inteira. São decisões de projeto, não apenas avisos legais.
O texto completo está em [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Esta página é um registo do que as licenças dizem, não aconselhamento jurídico.

## 1. Nenhuma chave: nenhuma incluída, nenhuma recuperada {#1-no-keys-none-shipped-none-recovered}

**Ela lê contêineres.** Analisar um formato de contêiner é manipulação comum de ficheiros, e
FModel, UModel e AssetRipper a fazem às claras há anos. Nada em analisar um contêiner é, em
si, uma forma de burlar proteção.

**A linha que importa é a cifragem, e ela é traçada dentro da ferramenta.** Uma ferramenta
cujo propósito é derrubar um controlo de acesso está ela mesma no alcance das leis contra
burla (DMCA §1201(a)(2) alcança tecnologias, não só atos), mesmo que ninguém distribua sequer
um ficheiro extraído. Então:

- **Nenhuma chave incluída.** Não há chave no código nem nos dados.
- **Nenhuma recuperação de chave.** Nada procura uma chave dentro de um executável, e nada lê
  a memória de outro processo.
- **Uma chave já disponível, ou nenhuma.** Um `.pak` do Unreal cifrado só abre com
  `--key <hex>` (em Python, `PakArchive(path, aes_key=...)`). O `pak.py` não tem nenhum caminho
  de código que obtenha uma chave. Um contêiner IoStore cifrado é recusado de vez.
- **Ofuscação também não é implementada.** As tabelas ofuscadas com XOR do Frostbite guardam a
  sua chave no próprio ficheiro, então são ofuscação, e não um controlo de acesso. Mesmo assim
  são detetadas e recusadas, porque nenhum ficheiro disponível usa essa forma e não haveria
  com o que verificar uma implementação. O pacote com chave do Assetto Corsa EVO é recusado pelo
  mesmo motivo que existe a regra de chaves.
- **Ficheiros cifrados ficam fechados.** O sistema de ficheiros inicial do Battlefield 6,
  que guarda a biblioteca de tipos do jogo, é cifrado e não é lido. A exportação de nível
  trabalha com os ficheiros que não são cifrados, e monta os dois tipos de que precisa a
  partir dos dados.
- **Nada se injeta num processo de jogo.** A telemetria vem de fontes que os próprios jogos
  publicam, e a captura usa APIs públicas de gravação de ecrã (nas outras ferramentas do 3DHeat).
  Injeção num título com anticheat põe em risco a conta de quem a executa.

Todo ficheiro testado até agora não é cifrado.

## 2. Seus próprios ficheiros, sua responsabilidade {#2-your-own-files-your-responsibility}

A ferramenta lê os ficheiros de jogo **instalados na sua máquina**. Ela nunca transfere conteúdo
de jogo.

O que se aponta para ela continua a ser da responsabilidade de quem a usa. Os jogos têm os próprios termos
de licença, e os EULAs costumam proibir a engenharia reversa. São contratos exigíveis, e a
obrigação recai sobre quem executa a ferramenta, em qualquer jogo. Nenhuma escolha de projeto aqui
a elimina. O caso legítimo mais claro é um programador lendo a build do próprio estúdio: um
título de outra equipa, um ramo antigo, uma build de um parceiro.

## 3. A saída não é para redistribuição {#3-output-is-not-for-redistribution}

O que sai é geometria para **contexto espacial**: o solo, a estrada e o que fica ao lado dela,
reduzidos a um orçamento, para que as voltas possam ser analisadas no lugar. É a menor parte do
que um ficheiro guarda, e ainda assim é conteúdo da editora do jogo.

- Guarde os `.glb` exportados, e as texturas dentro deles, para a sua própria análise.
- Não publique, partilhe nem venda percursos, níveis, modelos ou texturas exportados.
- O `.gitignore` do repositório mantém ficheiros de jogo, exportações, voltas e gravações fora
  do controlo de versão, por pasta e por tipo de ficheiro (`*.glb`, `*.pak`, `*.minizip`,
  `*.utoc`, `*.png`, `*.lap.json` e outros).

## O Oodle é encontrado, não incluído {#oodle-is-found-not-bundled}

O Oodle (RAD Game Tools, hoje Epic) é proprietário e não tem build redistribuível.
`oo2core_*.dll` é licenciado ao produto que o distribui. Por isso o `oodle.py` carrega uma
biblioteca já presente na máquina, em vez de trazer uma. É o arranjo que a licença prevê, e o
mesmo que o FModel e o UModel usam. Veja [Oodle](reader-oodle.md).

## Os formatos em si {#the-formats-themselves}

- `.pak`, IoStore, o `SerializedFile` do Unity, os `.toc` do Frostbite e os formatos do
  ForzaTech não são documentados. Lê-los é engenharia reversa de um contêiner. Nenhum dos
  leitores aqui deriva do código-fonte de outro projeto. Para o Frostbite, descrições públicas
  de versões antigas (as ferramentas de modding Frosty, uma nota de formato de Need for Speed
  Heat, uma palestra da GDC) forneceram nomes de campos e um mapa do que procurar. Nenhum código
  foi copiado; cada deslocamento foi medido nos ficheiros (veja
  [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Níveis extraídos são para o seu próprio uso. A ferramenta os grava no seu disco e em mais
  nenhum lugar; não os publique.
- O BeamNG publica o layout do seu `.cdae`, e o leitor o segue.
- A Valve documenta o VPK.
- As propriedades em dados cozidos do Unreal 5 precisam da lista de propriedades de cada classe.
  As listas em `unversioned.py` são **só nomes e tipos**, factos sobre o formato, como um ficheiro
  de mapeamento de interoperabilidade guarda. Foram derivadas dos cabeçalhos do Unreal Engine
  que a Epic disponibiliza a quem tem uma conta vinculada, e verificadas com os dados distribuídos.
  Nenhum código-fonte do motor é incluído ou necessário.

## A licença desta ferramenta {#this-tools-licence}

Tudo escrito para este repositório está sob a **licença MIT**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): use, altere,
distribua, comercialmente ou não.

Pacotes de terceiros, todos permissivos, então o exportador não traz nenhuma restrição própria:

| Pacote | Licença | Usado para |
|---|---|---|
| numpy | BSD-3-Clause | descodificação de malhas |
| cryptography | Apache-2.0 / BSD-3-Clause | só ficheiros cuja chave já está disponível |
| lz4 | BSD-3-Clause | ficheiros do Forza, alguns bundles do Unity, blocos LZ4 do IoStore |
| Pillow | MIT-CMU (HPND) | texturas com blocos comprimidos, saída JPEG |
| msgpack | Apache-2.0 | `.cdae` do BeamNG |
| zstandard | BSD-3-Clause | os poucos `.cdae` comprimidos com zstd, blocos zstd do Frostbite |
| pytest | MIT | só desenvolvimento |

As licenças foram lidas nos metadados dos pacotes em setembro de 2026. Quando os termos de um
componente mudaram depois disso, vale a fonte.
