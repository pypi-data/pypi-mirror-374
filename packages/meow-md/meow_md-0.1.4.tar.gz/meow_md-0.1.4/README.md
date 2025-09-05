# meow

**meow** is a terminal markdown viewer written in python and inspired by [glow](https://github.com/charmbracelet/glow). it's just a `cat` with [Rich](https://github.com/Textualize/rich), though, no file browsing! (yet?)

## features

- uses `LS_COLORS`
- syntax highlighting in fenced codeblocks
- styled lists, headers, blockquotes, and **bold** and *italics*

### gripes / future

- [ ] make the checkboxes cuter! glow-style `[ ]` / `[-]` / `[x]`
- [ ] tables...

## installation

install directly from [pypi](https://pypi.org/project/meow-md):

```bash
pip install --user meow-md  # if you use pip
pipx install meow-md        # if you use pipx
```

or build from source:

```bash
git clone https://codeberg.org/sailorfe/meow.git
cd meow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## usage

```bash
meow README.md
```
