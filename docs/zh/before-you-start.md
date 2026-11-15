---
title: 开始之前
nav_order: 2
lang: "zh"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# 开始之前 {#before-you-start}

第一次使用命令行？本页带你从零开始，用大约十分钟完成工具的配置，并运行第一条命令。你需要在一个名为**终端**的窗口中输入命令，工具会以文字回应。

## 1. 安装 Python {#install-python}

1. 前往 [python.org/downloads](https://www.python.org/downloads/)，下载 **Python 3.10 或更高版本**。
2. 运行安装程序。在第一个界面，勾选 **“Add python.exe to PATH”**，然后点击 **Install Now**。

## 2. 获取工具 {#get-the-tool}

- **使用 git：** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **不使用 git：** 在 [GitHub 页面](https://github.com/Holdi601/3DHeat-GameFiles) 上，
  点击绿色的 **Code** 按钮，然后点击 **Download ZIP**，并解压。

## 3. 在工具的文件夹中打开终端 {#open-a-terminal-in-the-tools-folder}

- 在文件资源管理器中，打开包含 `README.md` 的文件夹。点击地址栏，输入 `cmd` 并按回车。一个黑色的窗口会打开，并且已经位于该文件夹中。
- 或者打开 **Windows Terminal**，用 `cd` 进入该文件夹：

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. 安装工具所需的软件包 {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

结束时你应该会看到以 `Successfully installed ...` 结尾的行。

## 5. 检查工具是否正常工作 {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

你应该会看到 `usage: heat3d_gamefiles [-h]`，以及动词列表（`identify`、
`list`、`extract`、`course` 等）。这就表示成功：工具已经准备就绪。

## 阅读示例 {#reading-the-examples}

- `<something>` 是**占位符**：请输入你自己的值，不要保留尖括号。例如，`<lap file>` 会变成 `laps\my_lap.json`。
- 方括号中的 `[--option]` 是**可选项**：如果不需要，可以省略。
- 包含空格的路径需要用**双引号**：`"C:\My Games\lap.json"`。
- 每条命令都要在工具的文件夹中运行（第 3 步）。

## 出现问题时 {#when-something-goes-wrong}

| 你看到的 | 怎么办 |
|---|---|
| `'python' is not recognized` | 未安装 Python，或者没有勾选 “Add to PATH”。重新运行安装程序并勾选它，然后打开一个新的终端。 |
| `No module named heat3d_gamefiles` | 终端位于错误的文件夹。用 `cd` 进入包含 `README.md` 的文件夹。 |
| `No module named numpy`（或其他名称） | 跳过了第 4 步。运行 `pip install -r requirements.txt`。 |
| 路径后出现 `can't open file` / `not found` | 路径中有空格却没有加引号，或者拼写有误。请把它放在双引号中。 |

更多信息及其解决方法：[故障排除](../troubleshooting.md)。
