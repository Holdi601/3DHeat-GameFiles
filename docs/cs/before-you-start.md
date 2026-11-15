---
title: "Než začnete"
nav_order: 2
lang: "cs"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Než začnete {#before-you-start}

Nikdy jste nepracovali s příkazovým řádkem? Tato stránka vás provede od nuly až k funkčnímu nástroji
zhruba za deset minut. Píšete příkazy do okna, kterému se říká **terminál**, a nástroj
odpovídá textem.

## 1. Nainstalujte Python {#install-python}

1. Přejděte na [python.org/downloads](https://www.python.org/downloads/) a stáhněte
   **Python 3.10 nebo novější**.
2. Spusťte instalátor. Na první obrazovce zaškrtněte **„Add python.exe to PATH“**
   a pak klikněte na **Install Now**.

## 2. Získejte nástroj {#get-the-tool}

- **S gitem:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Bez gitu:** na [stránce GitHubu](https://github.com/Holdi601/3DHeat-GameFiles)
  klikněte na zelené tlačítko **Code**, pak na **Download ZIP** a rozbalte ho.

## 3. Otevřete terminál ve složce nástroje {#open-a-terminal-in-the-tools-folder}

- V Průzkumníkovi otevřete složku, která obsahuje `README.md`. Klikněte do adresního
  řádku, napište `cmd` a stiskněte Enter. Otevře se černé okno, které už bude v této složce.
- Nebo otevřete **Windows Terminal** a přejděte tam příkazem `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Nainstalujte, co nástroj potřebuje {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Měli byste vidět řádky končící na `Successfully installed ...`.

## 5. Ověřte, že to funguje {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Měli byste vidět `usage: heat3d_gamefiles [-h]` a seznam příkazů (`identify`,
`list`, `extract`, `course`, ...). To znamená úspěch: nástroj je připraven.

## Jak číst příklady {#reading-the-examples}

- `<něco>` je **zástupný text**: místo něj napište svou hodnotu, bez
  lomených závorek. `<lap file>` se tedy změní například na `laps\my_lap.json`.
- `[--option]` v hranatých závorkách je **volitelné**: vynechte ho, pokud ho nepotřebujete.
- Cesta s mezerami potřebuje **uvozovky**: `"C:\My Games\lap.json"`.
- Každý příkaz spouštějte ve složce nástroje (krok 3).

## Když se něco pokazí {#when-something-goes-wrong}

| Zobrazí se | Co dělat |
|---|---|
| `'python' is not recognized` | Python není nainstalován, nebo nebylo zaškrtnuto „Add to PATH“. Spusťte instalátor znovu, zaškrtněte to a pak otevřete nový terminál. |
| `No module named heat3d_gamefiles` | Terminál je ve špatné složce. Použijte `cd` a přejděte do složky, která obsahuje `README.md`. |
| `No module named numpy` (nebo jiný název) | Krok 4 se vynechal. Spusťte `pip install -r requirements.txt`. |
| `can't open file` / `not found` s cestou | Cesta má mezery a nemá uvozovky, nebo je v ní překlep. Dejte ji do uvozovek. |

Další hlášení a jejich opravy: [Řešení potíží](../troubleshooting.md).
