---
title: Unreal 5 IoStore
nav_order: 2
lang: "pt"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

O Unreal 5 traz a maior parte do conteúdo em contêineres **IoStore**: um sumário `.utoc` e
os dados `.ucas` que ele indexa. Um `.pak` ainda existe, mas guarda pouco mais do que um
rodapé. Os leitores aqui vão do contêiner até à geometria e os pixels, até onde um percurso
precisa. Foram construídos e verificados no Assetto Corsa Rally (Unreal 5.6.1, modificado) e
são acedidos pela exportação de percurso do [Assetto Corsa Rally](course-assetto-corsa-rally.md).
O `identify`, o `list` e o `extract` aceitam um `.utoc` (ou o `.ucas` ao lado dele): os
ficheiros que o seu diretório nomeia, pelo seu caminho sob o ponto de montagem. Um contêiner
sem índice de diretório não nomeia ficheiros e não é listado.

| Camada | Módulo |
|---|---|
| contêineres e o armazenamento | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| pacotes "zen" cozidos | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| dados de propriedades sem versão | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| malhas estáticas | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| texturas e texturas virtuais | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Contêineres (`.utoc`, `.ucas`) {#containers-utoc-ucas}

O sumário, versão 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Versões anteriores à 5 são recusadas. Só a versão 8 foi verificada em ficheiros reais.
- **Contêineres cifrados são recusados**: "<file> is encrypted. This tool holds no
  keys and recovers none." Nenhuma chave pode ser passada para o IoStore.
- Métodos de bloco: sem compressão, `oodle` (por meio do [Oodle](reader-oodle.md)), `zlib`,
  `lz4`. Qualquer outro é recusado.
- Partições além da primeira ficam em `<name>_s<n>.ucas`.

O **armazenamento** abre todo `.utoc` da pasta `Paks` do jogo e indexa cada caminho de
pacote, sem diferenciar maiúsculas de minúsculas. Os contêineres que falham ao abrir são
saltados. `global.utoc` fornece os objetos de script (as classes C++). Os dados em bulk de um
pacote (`.ubulk`) são achados como o chunk de mesmo id e tipo `BULK_DATA`, em qualquer
contêiner que o tenha.

Verificado: todo contêiner do jogo instalado e todo caminho de pacote nele.

## Pacotes zen {#zen-packages}

Um pacote cozido é um cabeçalho (nomes, imports, exports, bundles de exports, tabelas de
dependência, nomes de pacotes importados) seguido dos dados serializados de cada export.
Os objetos se referem uns aos outros por um `FPackageObjectIndex` de 64 bits cujos dois bits
altos dizem o que ele é: um export deste pacote, um objeto de script, um import de outro
pacote (qual pacote, e o export por um hash do seu caminho), ou nulo.

- O layout do sumário mudou na 5.3 (bundles de dependência e nomes de pacotes importados) e
  de novo na 5.6 (dois deslocamentos a mais). Os dois layouts são tentados, e fica o que
  consegue ler a tabela de nomes, então a versão não precisa ser conhecida.
- Pacotes **versionados** (no estilo não cozido) são recusados.
- Nomes de pacotes importados trazem um número. Um pacote `_Terrain` numerado 1 é o ficheiro
  `_Terrain_0`.
- Nomes `/Game/...` são mapeados para a pasta `Content` do projeto no armazenamento.
- Referências são seguidas entre pacotes casando o hash público do export.

Verificado: toda célula de toda etapa abre.

## Propriedades sem versão {#unversioned-properties}

Exports cozidos do Unreal 5 não nomeiam as suas propriedades. Um export começa com um
cabeçalho de sequências, "pule tantos slots, depois tantos presentes", e uma máscara que diz
quais dos presentes são zero e não trazem bytes. Os valores vêm em seguida, na ordem de
propriedades da classe. Ler isso exige o **esquema** de cada classe: a sua lista de
propriedades, exatamente na ordem em que o motor a monta (primeiro as próprias, depois as do
pai, um slot por elemento de array estático, deixando de fora as propriedades só do editor).

Esquemas são embutidos para as classes que um percurso precisa:

| Classe | Cadeia |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | as cadeias ISM (presentes, mas não usadas pela exportação de percurso, porque esta versão as reorganizou) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Eles também cobrem as structs que estes guardam (`FBodyInstance`, respostas de colisão e
outras). Tipos de valor são lidos por codificação: números de tamanho fixo e vetores
(`FVector`, `FRotator` como double, `FTransform`...), `FName`, enums (um byte), referências a
objetos (índice de pacote i32), caminhos de objeto suave, arrays, structs aninhadas e
delegates multicast (saltados).

Os esquemas são **só nomes e tipos de propriedades**, derivados dos cabeçalhos do Unreal
Engine 5.6.1 (que a Epic disponibiliza a quem tem uma conta vinculada). Nenhum código do motor
é incluído. Esta versão tem **dois slots a mais em `UPrimitiveComponent`** do que os
cabeçalhos, e **um a mais no volume de textura virtual**, achados pelos dados e marcados como
`(unknown)`. Um valor presente num desses slots é um erro, não um palpite. Um slot além do
fim de um esquema, ou um tipo desconhecido, lança `PropertyError`.

Verificado: todo componente de malha estática e de cena de toda etapa descodifica, terminando
exatamente no fim nativo da sua classe. Um patch do jogo pode mover os slots. O leitor então
lança um erro, e o percurso informa quantos componentes falharam.

## Malhas estáticas {#static-meshes}

Um export `UStaticMesh` é as suas propriedades seguidas de dados nativos. As propriedades não
são necessárias para a geometria e não são lidas. A parte nativa é achada pelo seu início
fixo: um flag de GUID zero, dois bytes de flags de tira, `bCooked = 1`, e o índice do export
`BodySetup` da própria malha. Ela é então lida na ordem em que `UStaticMesh::Serialize` e
`FStaticMeshRenderData::Serialize` a escrevem para uma malha **cozida, não Nanite**:

- até 16 níveis de detalhe, cada um com as suas secções (material, primeiro índice, contagem
  de triângulos), limites e, quando **inline**: o buffer de posições (float32 x 3), tangentes,
  UVs (todos os canais, em meia ou plena precisão), cores e o buffer de índices (16 ou 32
  bits);
- o que vem depois (buffers de índices invertidos e de profundidade, dados de ray tracing,
  amostradores ponderados por área) é saltado para chegar ao próximo nível.

Um nível que não é guardado inline encerra a lista. Uma malha sem nenhum é recusada.
As posições são as do Unreal: centímetros, X para a frente, Y para a direita, Z para cima.

Verificado: quase toda malha amostrada descodifica (o resto é esquelético), e a extensão
descodificada de um tile de estrada bate com os limites que ele guarda.

## Texturas {#textures}

Um export `Texture2D` é as suas propriedades e depois os seus dados de plataforma cozidos: o
nome do formato de pixel, o tamanho e uma tabela de níveis de mip, cada um apontando para o
**mapa de dados em bulk** do pacote (deslocamento, tamanho, flags; inline no export quando a
flag `0x40` está marcada, senão no `.ubulk`). Os dados de plataforma são achados pela sua
própria forma, e não saltando as propriedades, então o layout de propriedades da classe de
textura não importa. O primeiro mip não maior que o tamanho pedido é descodificado.

| Formato do Unreal | Descodificado como |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | RGBA de 8 bits |
| `PF_G8` | cinza de 8 bits |

Verificado: uma imagem de satélite DXT5 de 4096 px cujos treze níveis são exatamente os
tamanhos das entradas em bulk.

## Texturas virtuais em streaming {#streaming-virtual-textures}

Uma `VirtualTexture2D` cozida é formada por tiles quadrados com borda, por nível de detalhe,
endereçados por **código Morton** (x nos bits pares), guardados em chunks dos dados em bulk
do pacote. O layout é lido como `FVirtualTextureBuiltData::Serialize` o escreve no Unreal
5.6: camadas, tamanho do tile, borda, tabelas de endereço de tiles por mip, formatos das
camadas, e o chunk *n* como a entrada em bulk *n*. Uma região da textura é montada tile por
tile, sem as bordas, a partir do nível cuja resolução é a mais próxima do tamanho pedido. Só a
primeira camada é lida, e só nos formatos acima.

Verificado: os tiles de um chunk de textura virtual são contabilizados até ao byte.
