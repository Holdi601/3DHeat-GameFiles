---
title: Solução de problemas
nav_order: 11
lang: "pt"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Solução de problemas {#troubleshooting}

As mensagens que a ferramenta imprime quando algo a para, o que cada uma significa e o que
fazer. As mensagens são citadas do código, com os marcadores entre colchetes angulares.

## Antes mesmo de a ferramenta começar {#before-the-tool-even-starts}

| O que aparece | Faça |
|---|---|
| `'python' is not recognized` | instale o Python 3.10 ou mais recente e marque "Add python.exe to PATH"; abra um terminal novo ([Antes de começar](before-you-start.md)) |
| `No module named heat3d_gamefiles` | o terminal está na pasta errada: use `cd` para a pasta que tem o `README.md` |
| `No module named numpy` (ou outro pacote) | execute `pip install -r requirements.txt` |
| um caminho com espaços é cortado, ou `unrecognized arguments` | coloque o caminho entre aspas duplas: `"C:\My Games\lap.json"` |

## Achar o jogo {#finding-the-game}

| Mensagem | Significado | Faça |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | nenhuma biblioteca da Steam nem `C:\XboxGames` tem um jogo com `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | as coordenadas da volta não estão em nenhuma pista instalada | verifique se a volta é deste jogo; passe `--track` se a pista estiver em outro lugar |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | há tiles perto da caixa, mas nenhum que cubra a pilotagem no corredor | o mesmo que acima |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | a pasta não tem nenhum `.utoc` que abra | aponte `--install` para a pasta com os ficheiros `.utoc` |

## Achar o lugar {#finding-the-place}

| Mensagem | Significado | Faça |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: nenhum nível chegou a 30% | `--level <name>`; verifique se a volta está no referencial do visualizador |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` não bateu com nada | use um dos nomes de pasta listados |
| `<level> has no scene (no main/*.level.json and no .mis)` | a pasta do nível não tem ficheiros de cena | um nível ou mod quebrado ou incompleto |
| `no terrain of <level> lies along the driving.` | BeamNG: o corredor não tem quadrados de terreno | nível errado, ou um nível sem terreno onde a volta passa |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: nenhuma etapa e referencial chegou a 50% | `--level <stage>`; verifique se as posições da volta estão em metros com y para cima |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` não bateu com nada | use um dos nomes listados |
| `no ground of <stage> lies along the driving.` | AC Rally: nenhum tile de solo no corredor | etapa errada |

## A volta {#the-lap}

| Mensagem | Faça |
|---|---|
| `<file> is not a lap this can read. ...` | dê um formato suportado, veja [Entradas de volta](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | o JSON não é uma volta |
| `<file> has no x, y and z columns` | nomeie as colunas do CSV como `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | verifique o nome, ou passe um ficheiro |
| `'<name>' matches 3 courses: ...` | use um pedaço maior do nome |
| `<name> holds no driving` | a volta tem menos de duas amostras |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` precisa de um JSON de rota com `bounds`, como `heat3d_capture route` e `laps` gravam; um ficheiro de volta é para o `course` |
| `give exactly one of --box and --route` | `terrain` precisa de uma região só |
| `no course export for this lap: <reason>.` | o jogo não é suportado, veja [Limites e lacunas conhecidas](limits-and-known-gaps.md) |

## Ficheiros {#archives}

| Mensagem | Significado |
|---|---|
| `no Oodle library found. ...` | defina `HEAT3D_OODLE`, veja [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | um pak cifrado: `--key <hex>` se a chave estiver disponível. Não há outra forma |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | a chave tem 32 bytes escritos como 64 dígitos hexadecimais, `0x` opcional (código de saída 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | não é nenhum desses; `identify` diz o que é. Um contêiner do Unity usa `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | um contêiner IoStore cifrado. Ele não pode ser lido |
| `pak version <n>; this reader handles 8-12` | um formato de pak mais antigo ou mais novo |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | a partir do Python: tente o `.utoc`, que `list` e `extract` também aceitam |
| `<file> has no directory index, so its chunks carry no names to list` | um contêiner IoStore que não nomeia ficheiros; os seus chunks só são alcançados por outros pacotes |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | o `ChunkContentsMiniZip<n>.txt` ao lado do ficheiro é de outra build ou de outro ficheiro; sem ele, as entradas são listadas pelo número |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | os nomes foram embaralhados por hash na construção |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | uma tabela do Frostbite na forma ofuscada |
| `no Frostbite game found in a Steam library; give --install` | `levels` ou `level` não acharam um jogo Steam cujo `Data` tenha um `layout.toc`; passe a pasta do jogo |
| `no level called '<name>'; did you mean one of ...?` | o nome não bateu com a tabela de nenhum nível, ou bateu com vários; `levels` lista todos |
| `nothing was placed: no static model group was recognised` | os membros de grupo do nível têm uma assinatura de tipo diferente, depois de uma atualização do jogo ou em outro jogo Frostbite; o layout precisa ser medido de novo |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | uma malha Unity comprimida |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | mantenha o `.resS` ao lado do `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | uma build mais antiga do Unity |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` apanha um contêiner avulso |
| `texture format <n> has not been identified; refusing to guess` | um formato de textura do Forza ainda não visto |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | mantenha as partes de um VPK dividido juntas |

## Exportações que saem erradas {#exports-that-come-out-wrong}

| Sintoma | Causa provável |
|---|---|
| o percurso está deslocado da volta no visualizador | a volta e a exportação usam referenciais diferentes: verifique `--game` (uma volta do BeamNG lida como Forza, por exemplo) |
| nenhum berma num percurso do Forza | `--no-textures`, ou o tile não tinha mapas para aquela `--season` (a consola diz `N without maps`) |
| um tile do Forza em cores chapadas | os seus mapas de solo estão a faltar para a estação |
| muito menos objetos colocados do que o esperado | um `--detail-budget` explícito pequeno demais; o resumo diz quantas cópias foram deixadas de fora |
| o ficheiro é muito grande (centenas de MB) | um corredor urbano sob o orçamento automático; use `--detail-budget`, `--texture-size 1024` ou `--margin 40` |
| cercas em falta | superfícies vazadas são deixadas de fora de propósito (o resumo as nomeia) |
| `N meshes could not be read` | alguns modelos usam um formato que o leitor recusa; o resto é exportado mesmo assim |
| `N of M components could not be read` (AC Rally) | um patch do jogo pode ter mudado os slots de propriedades; por favor, informe |
