# hkit

A tiny yet powerful collection of reusable helper utilities.
The repository is named **hkit**, but the actual Python package name used for installation and import is **ebhkit**.

---

## 📦 Installation

You can install the package directly from PyPI (after it’s published):

```bash
pip install ebhkit
```

Or, for development, you can install it in editable mode:

```bash
git clone https://github.com/<your-username>/hkit.git
cd hkit
pip install -e .
```

---

## ⚙️ Development Setup

It is recommended to use a virtual environment when developing.

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Activate it:

* On **Linux/macOS**:

  ```bash
  source .venv/bin/activate
  ```

* On **Windows**:

  ```bash
  .venv\Scripts\activate
  ```

### 2. Install dependencies

Upgrade pip and install dev dependencies:

```bash
pip install -U pip pytest ruff black isort
pip install -r requirements-dev.txt
```

Install the package in **editable mode**:

```bash
pip install -e .
```

---

## 🧪 Running Tests

Run the full test suite:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/file/test_read_text_file.py
```

Run tests by keyword expression:

```bash
pytest -k "test_unicode_decode_error"
```

### Test coverage

```bash
pytest --cov=src/hkit --cov-report=term-missing
pytest --cov=src/hkit --cov-report=html
```

---

## 🧹 Code Formatting and Linting

Apply formatting and linting:

```bash
black src tests && isort src tests && ruff check src tests
```

Run checks only:

```bash
ruff check src tests
```

Fix automatically:

```bash
ruff check src tests --fix
ruff check src tests --unsafe-fixes
```

Format with Ruff (alternative to Black + isort):

```bash
ruff format src tests
ruff check src tests --select I --fix
```

---

## 📖 Documentation

This project uses [MkDocs](https://www.mkdocs.org/) for documentation.

Run the documentation locally:

```bash
mkdocs serve
```

Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Build the documentation:

```bash
mkdocs build
```

Deploy to GitHub Pages:

```bash
mkdocs gh-deploy
```

---

## 📝 Git Workflow

### Make a commit with a tag:

```bash
git status
git add -A
git commit -m ":tada: Initial Commit"
git tag -a v0.1.0 -m "Release v0.1.0"
git push
git push origin v0.1.0
git push --tags
```

---

### Complete pipeline with new release:

```bash
pytest
ruff check src tests
git add -A
git commit -m "ebhkit"
git tag -a v0.2.0 -m "Release v0.2.0"
git push
git push origin v0.2.0
git push --tags
```

## 🚀 Packaging and Publishing

### 1. Build the package (wheel + sdist)

```bash
python -m pip install --upgrade build twine
python -m build
```

The output will be created in the `dist/` directory.

Alternative build with isolation disabled:

```bash
python -m pip install --upgrade pip setuptools wheel build
python -m build --no-isolation
```

### 2. Clean old builds (optional)

```powershell
rmdir dist -Recurse -Force -ErrorAction Ignore
rmdir build -Recurse -Force -ErrorAction Ignore
Get-ChildItem -Filter *.egg-info -Recurse | Remove-Item -Recurse -Force -ErrorAction Ignore
```

### 3. Upload to TestPyPI (for testing)

```bash
python -m twine upload --repository testpypi dist/*
```

Install from TestPyPI to test:

```bash
pip install -i https://test.pypi.org/simple/ ebhkit
```

Or install the built wheel directly:

```bash
pip install -U dist/ebhkit-0.1.0-py3-none-any.whl
```

### 4. Upload to PyPI (production)

Before uploading, check the distributions:

```bash
twine check dist/*
```

Then upload:

```bash
python -m twine upload dist/*
```

or upload specific package"
```bash
twine upload dist/ebhkit-0.1.0*
```

