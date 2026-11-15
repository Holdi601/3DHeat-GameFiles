---
title: "始める前に"
nav_order: 2
lang: "ja"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# 始める前に {#before-you-start}

コマンドラインは初めてですか？ このページは、ゼロから動くツールまでを約10分で案内します。コマンドを **ターミナル** と呼ばれるウィンドウに入力すると、ツールがテキストで答えます。

## 1. Pythonをインストール {#install-python}

1. [python.org/downloads](https://www.python.org/downloads/) を開き、**Python 3.10 以降** をダウンロードします。
2. インストーラーを実行します。最初の画面で **「Add python.exe to PATH」** にチェックを入れてから、**Install Now** をクリックします。

## 2. ツールを入手 {#get-the-tool}

- **gitを使う場合:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **gitを使わない場合:** [GitHubのページ](https://github.com/Holdi601/3DHeat-GameFiles) で、緑色の **Code** ボタン、次に **Download ZIP** をクリックし、展開します。

## 3. ツールのフォルダーでターミナルを開く {#open-a-terminal-in-the-tools-folder}

- エクスプローラーで `README.md` があるフォルダーを開きます。アドレスバーをクリックし、`cmd` と入力してEnterを押します。そのフォルダーがすでに開かれた、黒いウィンドウが開きます。
- または **Windows ターミナル** を開き、`cd` で移動します:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. ツールに必要なものをインストール {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

`Successfully installed ...` で終わる行が表示されるはずです。

## 5. 動作を確認 {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

`usage: heat3d_gamefiles [-h]` と、動詞の一覧（`identify`、`list`、`extract`、`course` など）が表示されるはずです。これが成功です。ツールの準備ができました。

## 例の読み方 {#reading-the-examples}

- `<何か>` は **置き換え用の場所** です。山括弧を付けずに、自分の値を入力します。たとえば `<lap file>` は `laps\my_lap.json` などになります。
- 角括弧の `[--option]` は **省略可能** です。必要なければ省いてください。
- スペースを含むパスには **二重引用符** が必要です: `"C:\My Games\lap.json"`。
- すべてのコマンドは、ツールのフォルダー（手順3）で実行してください。

## うまくいかないとき {#when-something-goes-wrong}

| 表示 | 対処 |
|---|---|
| `'python' is not recognized` | Pythonが入っていないか、「Add to PATH」にチェックが入っていません。インストーラーをもう一度実行してチェックを入れ、新しいターミナルを開いてください。 |
| `No module named heat3d_gamefiles` | ターミナルが違うフォルダーにいます。`README.md` があるフォルダーへ `cd` で移動してください。 |
| `No module named numpy`（または別の名前） | 手順4が飛ばされています。`pip install -r requirements.txt` を実行してください。 |
| パス付きの `can't open file` / `not found` | パスにスペースがあるのに引用符がないか、綴りの間違いです。二重引用符で囲んでください。 |

ほかのメッセージとその対処: [トラブルシューティング](../troubleshooting.md)。
