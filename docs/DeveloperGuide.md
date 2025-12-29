# Developer Guide

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [Pre-requisites](#pre-requisites)
  - [Go](#go)
  - [Python](#python)
  - [VSCode](#vscode)
- [Using Copilot Prompts](#using-copilot-prompts)
- [Running Code Locally](#running-code-locally)
  - [Running Go Binaries](#running-go-binaries)
  - [Running Python Commands](#running-python-commands)
- [Creating Releases](#creating-releases)
  - [Version And Release Notes](#version-and-release-notes)
  - [Git State Check](#git-state-check)
  - [Creating A Release](#creating-a-release)

<!-- /TOC -->

## Pre-requisites

### Go

go version >= 1.25

### Python

- Python version >= 3.10, preferably using a virtual environment for this
  project:

  ```bash
  # Optional virtual environment steps:
  python3 -m venv $HOME/venv/lmcrec-dev
  . $HOME/venv/lmcrec-dev/bin/activate

  ./lmcpb/tools/py-prerequisites.sh
  ```

- Python files should formatted via:

  ```bash
  ./lmcpb/pyfmt
  ```

- tests should be run using `pytest` (installed by pre-requisites):

  ```bash
  cd lmcpb
  pytest
  ```

### VSCode

If using [VSCode](https://code.visualstudio.com/) then the following extensions are recommended:

- [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
- [Even Better TOML](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)
- [Go](https://marketplace.visualstudio.com/items?itemName=golang.Go)
- [isort](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)
- [Markdown Footnotes](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-footnotes)
- [Markdown TOC & Chapter Number](https://marketplace.visualstudio.com/items?itemName=TakumiI.markdown-toc-num)
- [markdownlint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)
- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Rewrap Revived](https://marketplace.visualstudio.com/items?itemName=dnut.rewrap-revived)
- [Sort lines](https://marketplace.visualstudio.com/items?itemName=Tyriar.sort-lines)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)

Settings can be primed from [.vscode-ref/settings.json](../.vscode-ref/settings.json)

## Using Copilot Prompts

[GitHub
Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) was
used for testing, especially for generating test cases. The prompts are under
the [.github/prompts](../.github/prompts) directory (the standard location).

The prompt file names are `ORIGINAL_FILE_NAME_WITH_EXTENSION.prompt.md`, e.g.
[query_selector_init_test_cases.py.prompt.md](../.github/prompts/query_selector_init_test_cases.py.prompt.md)
for
[query_selector_init_test_cases.py](../lmcpb/tests/query_selector_init_test_cases.py)
file.

Each prompt generated file is headed by 2 comment lines: the path of the prompt
and the model, as per
[copilot-instructions.md](../.github/copilot-instructions.md), e.g.:

```python
# Prompt: .github/prompts/query_selector_init_test_cases.py.prompt.md
# Model: Claude Sonnet 4.5
```

## Running Code Locally

### Running Go Binaries

The local machine may have a different OS and architecture than the target
release platforms, for instance I'm using a `MacBook Air M3` running `macOS
Tahoe 2.62`.

- build:

    ```bash
    cd lmcrec
    ./go-build-all
    ```

- run:
  - have `.../lmc-recorder/lmcrec/scripts` in `PATH`
  - have env `LMCREC_CONFIG` set to the dev config
  - optionally set env `LMCREC_RUNTIME` if the default `$HOME/runtime/lmcrec` is not suitable

### Running Python Commands

- activate the virtual environment (if one is used)
- have `.../mc-recorder/lmcpb/commands` in `PATH`
- share env `LMCREC_CONFIG` and `LMCREC_RUNTIME` with [GO binaries](#running-go-binaries)

## Creating Releases

### Version And Release Notes

The semantic version should be maintained in [semver.txt](../semver.txt) file in
`vMAJ.MIN.PATCH` format.

The release notes should be maintained in [relnotes.txt](../relnotes.txt) file
in the most recent to the oldest order. Each release should be headed by date
and version:

```text
YYYY/MM/DD      vMAJ.MIN.PATCH

Description
```

### Git State Check

The project should be a clean state on the `main` branch, with semver tag applied.

### Creating A Release

- get the the project in a clean state on the `main` branch; verify by running:

    ```bash
    ./check-git-state
    ```

- apply the semver tag:

    ```bash
    ./git-tag-with-semver
    ```

- create the release:

    ```bash
    ./create-release
    ```
