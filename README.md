# Scripts and Notebooks

* Collects a number of scripts (mostly Python) and Jupyter notebooks
* Setup is blueprint for other Python repositories

## Installation

First, you need to have `Python 3.10` or later installed, as well as `pkg-config`.
If you use `homebrew`:
```bash
brew install pkg-config
```

Make sure that `/opt/homebrew/bin` appears in `PATH` before `/usr/bin` or `/usr/local/bin`.
In order to make all scripts and notebooks work, run:
```bash
python3 -m venv scripts_venv
. scripts_venv/bin/activate
pip install --upgrade pip
pip install -e '.[datasci]'
```

For a minimal installation, replace the last command by:
```bash
pip install -e '.'
```

For development of new scripts, utility code, or notebooks, replace the last
command by:
```bash
pip install -e '.[datasci,dev]'
```

For an installation with all dependencies, replace the last command by:
```bash
pip install -e '.[all]'
```

Do not forget to active the venv `scripts_venv` before running any of the scripts
or notebooks.
