---
title: Sula dtosaíonn tú
nav_order: 2
lang: ga
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Sula dtosaíonn tú {#before-you-start}

An bhfuil tú nua leis an líne ordaithe? Tugann an leathanach seo thú ó rud ar bith go dtí uirlis oibre i
thart ar dheich nóiméad. Clóscríobhann tú orduithe isteach i bhfuinneog ar a dtugtar **teirminéal**, agus
freagraíonn an uirlis le téacs.

## 1. Suiteáil Python {#install-python}

1. Téigh go [python.org/downloads](https://www.python.org/downloads/) agus íoslódáil
   **Python 3.10 nó níos nuaí**.
2. Rith an suiteálaí. Ar a chéad scáileán, cuir tic i **"Add python.exe to PATH"**,
   ansin cliceáil **Install Now**.

## 2. Faigh an uirlis {#get-the-tool}

- **Le git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Gan git:** ar an [leathanach GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  cliceáil an cnaipe glas **Code**, ansin **Download ZIP**, agus dízipeáil é.

## 3. Oscail teirminéal i bhfillteán na huirlise {#open-a-terminal-in-the-tools-folder}

- In File Explorer, oscail an fillteán ina bhfuil `README.md`. Cliceáil an barra
  seoltaí, clóscríobh `cmd` agus brúigh Enter. Osclaíonn fuinneog dhubh, cheana féin sa fhillteán sin.
- Nó oscail **Windows Terminal** agus téigh ann le `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Suiteáil an méid atá ag teastáil ón uirlis {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Ba chóir duit línte a fheiceáil a chríochnaíonn le `Successfully installed ...`.

## 5. Seiceáil go n-oibríonn sé {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Ba chóir duit `usage: heat3d_gamefiles [-h]` agus liosta gníomhairí (verbs) a fheiceáil (`identify`,
`list`, `extract`, `course`, ...). Is é sin an rath: tá an uirlis réidh.

## Na samplaí a léamh {#reading-the-examples}

- Is **ionadchoinneálaí** é `<something>`: clóscríobh do luach féin ina áit, gan na
  lúibíní uilleacha. Éiríonn `<lap file>`, mar shampla, `laps\my_lap.json`.
- Tá `[--option]` idir lúibíní cearnacha **roghnach**: fág ar lár é mura bhfuil sé uait.
- Teastaíonn **comharthaí athfhriotail dúbailte** ó chosán a bhfuil spásanna ann: `"C:\My Games\lap.json"`.
- Rith gach ordú i bhfillteán na huirlise (céim 3).

## Nuair a théann rud éigin cearr {#when-something-goes-wrong}

| Feiceann tú | Cad atá le déanamh |
|---|---|
| `'python' is not recognized` | Níl Python suiteáilte, nó níor cuireadh tic i "Add to PATH". Rith an suiteálaí arís agus cuir tic ann, ansin oscail teirminéal nua. |
| `No module named heat3d_gamefiles` | Tá an teirminéal sa fhillteán mícheart. Úsáid `cd` chun dul go dtí an fillteán ina bhfuil `README.md`. |
| `No module named numpy` (nó ainm eile) | Scipeáladh céim 4. Rith `pip install -r requirements.txt`. |
| `can't open file` / `not found` le cosán | Tá spásanna sa chosán agus gan comharthaí athfhriotail, nó tá botún clóscríobh ann. Cuir idir comharthaí athfhriotail dúbailte é. |

Tuilleadh teachtaireachtaí agus a leasuithe: [Fabhtcheartú](../troubleshooting.md).
