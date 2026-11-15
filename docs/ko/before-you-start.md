---
title: 시작하기 전에
nav_order: 2
lang: ko
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# 시작하기 전에 {#before-you-start}

명령줄이 처음이신가요? 이 페이지는 약 10분 만에 아무것도 없는 상태에서 작동하는 도구까지 안내합니다. **터미널**이라고 부르는 창에 명령을 입력하면, 도구가 글자로 답합니다.

## 1. Python 설치 {#install-python}

1. [python.org/downloads](https://www.python.org/downloads/)에 가서 **Python 3.10 이상**을 내려받으세요.
2. 설치 프로그램을 실행하세요. 첫 화면에서 **"Add python.exe to PATH"**를 체크한 다음 **Install Now**를 누르세요.

## 2. 도구 받기 {#get-the-tool}

- **git을 쓸 때:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **git 없이:** [GitHub 페이지](https://github.com/Holdi601/3DHeat-GameFiles)에서 초록색 **Code** 버튼을 누르고 **Download ZIP**을 선택한 뒤, 압축을 푸세요.

## 3. 도구의 폴더에서 터미널 열기 {#open-a-terminal-in-the-tools-folder}

- 파일 탐색기에서 `README.md`가 있는 폴더를 여세요. 주소창을 클릭하고 `cmd`를 입력한 뒤 Enter를 누르세요. 검은 창이 열리는데, 이미 그 폴더에 들어가 있습니다.
- 또는 **Windows 터미널**을 열고 `cd`로 그 폴더에 가세요:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. 도구에 필요한 것 설치 {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

`Successfully installed ...`로 끝나는 줄들이 보여야 합니다.

## 5. 제대로 작동하는지 확인 {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

`usage: heat3d_gamefiles [-h]`와 동사(`identify`, `list`, `extract`, `course`, ...) 목록이 보이면 성공입니다. 도구가 준비된 것입니다.

## 예시 읽는 법 {#reading-the-examples}

- `<something>`은 **자리 표시자**입니다. 꺾쇠괄호 없이 본인의 값을 입력하세요. 예를 들어 `<lap file>`은 `laps\my_lap.json`이 됩니다.
- 대괄호 안의 `[--option]`은 **선택 사항**입니다. 필요 없으면 생략하세요.
- 공백이 있는 경로에는 **큰따옴표**가 필요합니다: `"C:\My Games\lap.json"`.
- 모든 명령은 도구의 폴더에서 실행하세요(3단계).

## 문제가 생겼을 때 {#when-something-goes-wrong}

| 보이는 것 | 할 일 |
|---|---|
| `'python' is not recognized` | Python이 설치되지 않았거나 "Add to PATH"를 체크하지 않은 것입니다. 설치 프로그램을 다시 실행해 체크하고, 새 터미널을 여세요. |
| `No module named heat3d_gamefiles` | 터미널이 잘못된 폴더에 있습니다. `README.md`가 있는 폴더로 `cd` 하세요. |
| `No module named numpy` (또는 다른 이름) | 4단계를 건너뛰었습니다. `pip install -r requirements.txt`를 실행하세요. |
| 경로와 함께 `can't open file` / `not found` | 경로에 공백이 있는데 따옴표가 없거나, 오타가 있습니다. 큰따옴표로 감싸세요. |

더 많은 메시지와 그 해결 방법: [문제 해결](../troubleshooting.md).
