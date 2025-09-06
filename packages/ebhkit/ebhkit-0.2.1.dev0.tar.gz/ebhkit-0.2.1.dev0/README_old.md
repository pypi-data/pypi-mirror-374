# hkit
A tiny collection of reusable helper utilities.

## Popular Command

# ایجاد و فعال‌سازی محیط مجازی (مثال با venv)
python -m venv .venv
source .venv/bin/activate 

.venv\\Scripts\\activate


# نصب وابستگی‌های dev (اختیاری)
pip install -U pip pytest ruff black isort

pip install -r requirements-dev.txt
# نصب پکیج به‌صورت editable برای توسعه
pip install -e .


# اجرای تست‌ها
pytest

pytest tests/file/test_read_text_file.py

pytest -k "test_unicode_decode_error"

# Coverage

pytest --cov=src/hkit --cov-report=term-missing

pytest --cov=src/hkit --cov-report=html

# قالب‌بندی و لینت
black src tests && isort src tests && ruff check src tests

Report:
ruff check src tests

Fix:
ruff check src tests --fix

ruff check src tests --unsafe-fixes
Black:
ruff format src tests

Alternative to isort
ruff check src tests --select I --fix

# Documentation

mkdocs serve

http://127.0.0.1:8000/

mkdocs build



mkdocs gh-deploy

---

# Git commit with tag

git status
git add -A
git commit -m ":tada:Initial Commit"
git tag -a v0.1.0 -m "Release v0.1.0"
git push
git push origin v0.1.0
git push --tags


## 8) ساخت بسته و انتشار
### 8.1) ساخت بسته (wheel + sdist)
```bash
python -m pip install --upgrade build twine
python -m build
```
خروجی‌ها در پوشهٔ `dist/` ساخته می‌شوند.

embeddable 

python -m pip install --upgrade pip setuptools wheel build
python -m build --no-isolation


### Delete old build

rmdir dist -Recurse -Force -ErrorAction Ignore
rmdir build -Recurse -Force -ErrorAction Ignore
Get-ChildItem -Filter *.egg-info -Recurse | Remove-Item -Recurse -Force -ErrorAction Ignore

### 8.2) انتشار در TestPyPI (برای تمرین)
```bash
python -m twine upload --repository testpypi dist/*

4) تست نصب محلی
python -m pip install -U dist/mypackage-0.1.0-py3-none-any.whl
# یا نصب قابل ویرایش برای توسعه:
python -m pip install -e .


```
سپس نصب تستی:
```bash
pip install -i https://test.pypi.org/simple/ myhelpers
```

### 8.3) انتشار در PyPI اصلی
```bash
twine check dist/*

```

$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmcCJDhjYTFjYmZjLTA2ZjctNGFlZi1iNjEwLWRjNmYxOTBmZTRjYQACKlszLCIzOTMxOTNjYi0yYTk0LTQxMTEtOTNjYy0xMzdkMTY0YWMyN2UiXQAABiBGgMJehqMmtRAWvYkJK6LHCEHGdfonEW4SHb-MtGtexg"

twine upload dist/*
twine upload dist/ebhkit-0.1.0*
