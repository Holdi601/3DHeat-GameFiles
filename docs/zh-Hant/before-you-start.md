---
title: "開始之前"
nav_order: 2
lang: zh-Hant
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# 開始之前 {#before-you-start}

第一次使用命令列？這一頁會帶你從零開始，約十分鐘即可讓工具運作。你在一個稱為**終端機**的視窗中輸入命令，工具會以文字回應。

## 1. 安裝 Python {#install-python}

1. 前往 [python.org/downloads](https://www.python.org/downloads/)，下載 **Python 3.10 或更新版本**。
2. 執行安裝程式。在第一個畫面勾選 **"Add python.exe to PATH"**，
   然後按 **Install Now**。

## 2. 取得工具 {#get-the-tool}

- **使用 git：** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **不使用 git：** 在 [GitHub 頁面](https://github.com/Holdi601/3DHeat-GameFiles)上，
  按綠色的 **Code** 按鈕，再按 **Download ZIP**，然後解壓縮。

## 3. 在工具的資料夾中開啟終端機 {#open-a-terminal-in-the-tools-folder}

- 在檔案總管中，開啟含有 `README.md` 的資料夾。點一下網址列，
  輸入 `cmd` 再按 Enter。會開啟一個黑色視窗，已經位於該資料夾中。
- 或者開啟 **Windows Terminal**，再用 `cd` 前往該資料夾：

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. 安裝工具所需的套件 {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

你應該會看到以 `Successfully installed ...` 結尾的行。

## 5. 確認工具可以運作 {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

你應該會看到 `usage: heat3d_gamefiles [-h]` 以及動詞清單（`identify`、
`list`、`extract`、`course`……）。這就表示成功：工具已經準備好了。

## 閱讀範例 {#reading-the-examples}

- `<something>` 是**佔位符**：請改輸入你自己的值，不要輸入角括號。例如 `<lap file>` 會變成 `laps\my_lap.json`。
- 方括號中的 `[--option]` 是**選用**：若不需要，可以省略。
- 含有空格的路徑需要**雙引號**：`"C:\My Games\lap.json"`。
- 請在工具的資料夾中執行每一個命令（第 3 步）。

## 出問題時 {#when-something-goes-wrong}

| 你看到的 | 該怎麼做 |
|---|---|
| `'python' is not recognized` | 尚未安裝 Python，或沒有勾選 "Add to PATH"。請重新執行安裝程式並勾選，然後開啟新的終端機。 |
| `No module named heat3d_gamefiles` | 終端機位於錯誤的資料夾。請 `cd` 到含有 `README.md` 的資料夾。 |
| `No module named numpy`（或其他名稱） | 略過了第 4 步。請執行 `pip install -r requirements.txt`。 |
| `can't open file` / 路徑出現 `not found` | 路徑含有空格卻沒有加引號，或是打錯字。請用雙引號括起來。 |

更多訊息及其解決方法：[疑難排解](../troubleshooting.md)。
