---
title: "Manutenção: a lista de verificação da versão"
nav_order: 99
lang: "pt"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Manutenção: a lista de verificação da versão {#maintaining-the-release-checklist}

Antes de marcar uma versão (`v` + o número em `VERSION`), percorra esta lista pela ordem. Ela mantém as páginas, as imagens e as traduções fiéis ao código.

1. **Gere de novo as páginas geradas.**
   - `python tools/gen_docs_reference.py` reescreve a [Referência de comandos](../cli-reference.md) a partir do `--help` do próprio programa. `python tools/gen_docs_reference.py --check` sai com código 1 enquanto a página commitada estiver desatualizada.
   - `python tools/docs_diagrams.py --strings` redesenha os diagramas em `docs/assets/img/` e reescreve `docs/assets/i18n/en.json`, a lista de cada rótulo de diagrama a traduzir.
2. **Liste o que mudou desde a última versão:** `git log --oneline v<último VERSION>..HEAD`. Cada novo verbo, opção, campo de saída ou comportamento precisa de uma linha no `CHANGELOG.md` e de uma linha na sua tabela **Docs**, indicando a página que o explica. Atualize essa página.
3. **Peça uma revisão independente** das páginas e imagens alteradas, por alguém (ou um agente) que não as escreveu, lendo como três pessoas: um principiante que nunca usou um terminal, uma criança de 8 anos e um profissional. Os diagramas também são revistos: legíveis na largura da página, rótulos corretos, cores explicadas.
4. **Corrija o que a revisão encontrar** e depois confirme que nenhum dado real do jogo escapou: nenhum nome de mapa, nível ou jogador, nenhum número de gravações ou instalações reais (use marcadores como `<map>` ou "o nível de teste").
5. **Traduza de novo as páginas alteradas.** Cada página traduzida regista o hash da página inglesa de onde foi feita; as páginas cuja origem inglesa mudou são traduzidas de novo, e os rótulos dos diagramas com elas. Depois, reveja cada idioma: claro para os mesmos três leitores, rótulos corretos, palavras que coincidem com a interface do próprio visualizador nesse idioma.
6. **Publique só com a autorização do utilizador.** Nada é publicado nem marcado antes de o dono dizer que pode.

## Traduções: os comandos {#translations-the-commands}

O site está traduzido para os 40 idiomas do visualizador 3DHeat: o inglês está em `docs/`, cada outro idioma em `docs/<lang>/`, com os mesmos nomes de ficheiro. O `tools/docs_i18n.py` faz a contabilidade:

```bash
python tools/docs_i18n.py hashes             # depois de qualquer alteração em inglês: regista o hash de cada página
python tools/docs_i18n.py svg-strings        # depois de qualquer alteração numa imagem: os rótulos a traduzir
python tools/docs_i18n.py status             # por idioma: atuais, desatualizadas, páginas em falta
python tools/docs_i18n.py todo --lang de     # as páginas em alemão a (re)traduzir
python tools/docs_i18n.py svg-build --lang de    # as imagens em alemão a partir de docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # marca as páginas em alemão com o hash inglês
python tools/docs_i18n.py check              # sai com código 1 quando hashes ou rótulos estão obsoletos
```

Traduza apenas o que o `todo` lista: mantenha o Markdown, as ligações, o código, os nomes de ficheiros e de colunas; traduza os títulos e as descrições das imagens; e use as palavras do próprio visualizador 3DHeat para os seus botões e painéis (em `src/i18n/locales/<lang>/`). As páginas de referência geradas e as imagens de terminal continuam em inglês. No site, uma tradução desatualizada diz isso e liga à página inglesa; uma tradução em falta recorre ao inglês. O menu de idiomas do cabeçalho e o redirecionamento da página inicial, conforme o idioma do navegador, vêm de `docs/_includes/`.
