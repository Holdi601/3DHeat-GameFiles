---
title: "Ako začať"
nav_order: 2
lang: "sk"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Ako začať {#before-you-start}

Nikdy ste nepracovali s príkazovým riadkom? Táto stránka vás za asi desať minút
dostane od nuly k funkčnému nástroju. Príkazy píšete do okna, ktoré sa volá **terminál**, a
nástroj odpovedá textom.

## 1. Nainštalujte Python {#install-python}

1. Choďte na [python.org/downloads](https://www.python.org/downloads/) a stiahnite
   **Python 3.10 alebo novší**.
2. Spustite inštalátor. Na jeho prvej obrazovke zaškrtnite **„Add python.exe to PATH“**
   a potom kliknite na **Install Now**.

## 2. Získajte nástroj {#get-the-tool}

- **S gitom:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Bez gitu:** na [stránke GitHub](https://github.com/Holdi601/3DHeat-GameFiles)
  kliknite na zelené tlačidlo **Code** a potom na **Download ZIP** a rozbaľte ho.

## 3. Otvorte terminál v priečinku nástroja {#open-a-terminal-in-the-tools-folder}

- V Prieskumníkovi otvorte priečinok, ktorý obsahuje `README.md`. Kliknite na panel
  s adresou, napíšte `cmd` a stlačte Enter. Otvorí sa čierne okno, už v tom priečinku.
- Alebo otvorte **Windows Terminal** a prejdite tam príkazom `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Nainštalujte, čo nástroj potrebuje {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Mali by ste vidieť riadky končiace na `Successfully installed ...`.

## 5. Overte, že funguje {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Mali by ste vidieť `usage: heat3d_gamefiles [-h]` a zoznam príkazov (`identify`,
`list`, `extract`, `course`, ...). To znamená úspech: nástroj je pripravený.

## Čítanie príkladov {#reading-the-examples}

- `<something>` je **zástupný znak**: namiesto neho napíšte svoju hodnotu, bez
  uhlových zátvoriek. `<lap file>` sa napríklad zmení na `laps\my_lap.json`.
- `[--option]` v hranatých zátvorkách je **voliteľné**: vynechajte ho, ak ho nepotrebujete.
- Cesta s medzerami potrebuje **dvojité úvodzovky**: `"C:\My Games\lap.json"`.
- Každý príkaz spúšťajte v priečinku nástroja (krok 3).

## Keď niečo nevyjde {#when-something-goes-wrong}

| Vidíte | Čo robiť |
|---|---|
| `'python' is not recognized` | Python nie je nainštalovaný alebo nebolo zaškrtnuté „Add python.exe to PATH“. Spustite inštalátor znova, zaškrtnite to a potom otvorte nový terminál. |
| `No module named heat3d_gamefiles` | Terminál je v zlom priečinku. Prejdite príkazom `cd` do priečinka, ktorý obsahuje `README.md`. |
| `No module named numpy` (alebo iný názov) | Krok 4 sa preskočil. Spustite `pip install -r requirements.txt`. |
| `can't open file` / `not found` s cestou | Cesta má medzery a nemá úvodzovky, alebo je v nej preklep. Dajte ju do dvojitých úvodzoviek. |

Ďalšie hlásenia a ich riešenia: [Riešenie problémov](troubleshooting.md).
