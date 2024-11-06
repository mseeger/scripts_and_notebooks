# Scripts and Notebooks

* Collects a number of scripts (mostly Python) and Jupyter notebooks
* Setup is blueprint for other Python repositories

## Installation

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

For an installation with all dependencies, replace the last command by:

```bash
pip install -e '.[all]'
```
