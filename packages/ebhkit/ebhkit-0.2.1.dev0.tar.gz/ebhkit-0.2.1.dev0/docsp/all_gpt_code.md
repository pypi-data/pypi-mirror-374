در این سند، یک اسکلت کامل و مینیمال برای ساخت یک پکیج پایتونی جهت قرار دادن توابع کمکی (helper) آماده است. می‌توانید نام پکیج، توضیحات و توابع نمونه را مطابق نیاز خودتان عوض کنید.

---

## 1) ساختار پوشه‌ها (src-layout)
```
myhelpers/
├─ src/
│  └─ myhelpers/
│     ├─ __init__.py
│     ├─ string.py
│     ├─ datetime_.py
│     └─ typing_.py
├─ tests/
│  ├─ __init__.py
│  ├─ test_string.py
│  └─ test_datetime.py
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ .gitignore
└─ .github/
   └─ workflows/
      └─ ci.yml
```

> نکته: «src-layout» در مدیریت import و جلوگیری از import تصادفی از ریشهٔ مخزن در زمان تست کمک می‌کند.

---

## 2) فایل `pyproject.toml` (استاندارد PEP 621)
```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myhelpers"                     # نام بسته (منحصربه‌فرد در PyPI)
version = "0.1.0"                      # نسخهٔ اولیه
description = "A tiny collection of reusable helper utilities."
readme = "README.md"
requires-python = ">=3.9"
license = { file = "LICENSE" }
authors = [
  { name = "Your Name", email = "you@example.com" }
]
keywords = ["helpers", "utilities", "toolkit"]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.9",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
]

# وابستگی‌های زمان اجرا (در صورت نیاز)
# dependencies = [
#   "python-slugify>=8",
# ]

[project.urls]
Homepage = "https://github.com/yourname/myhelpers"
Issues = "https://github.com/yourname/myhelpers/issues"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q"
testpaths = ["tests"]

[tool.black]
line-length = 100

[tool.isort]
profile = "black"

[tool.ruff]
line-length = 100
select = ["E","F","I","B","UP"]
ignore = []

```

> اگر می‌خواهید نسخه‌دهی خودکار بر اساس تگ‌های Git داشته باشید، می‌توانید به‌جای فیلد `version` از ابزار `setuptools_scm` استفاده کنید.

نمونهٔ جایگزین (اختیاری):
```toml
[build-system]
requires = ["setuptools>=69", "setuptools-scm>=8", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
version_scheme = "post-release"
local_scheme = "no-local-version"
```

---

## 3) کد پکیج
### 3.1) `src/myhelpers/__init__.py`
```python
"""myhelpers - A tiny collection of helper utilities.

در اینجا هر چیزی را که می‌خواهید به API سطح پکیج صادر شود ایمپورت کنید.
"""
from .string import slugify_simple, dedent_trim
from .datetime_ import utcnow_iso, parse_iso

__all__ = [
    "slugify_simple",
    "dedent_trim",
    "utcnow_iso",
    "parse_iso",
]

# نسخه را هم اینجا نگه داریم تا در زمان اجرا در دسترس باشد
__version__ = "0.1.0"
```

### 3.2) `src/myhelpers/string.py`
```python
from __future__ import annotations
import re
import textwrap

_slug_re = re.compile(r"[^a-z0-9]+")


def slugify_simple(s: str) -> str:
    """ساخت یک اسلاگ ساده انگلیسی با حذف نویسه‌های غیرمجاز.

    مثال: "Hello, World!" -> "hello-world"
    توجه: برای پشتیبانی زبانی قوی‌تر می‌توانید بسته‌هایی مثل `python-slugify` اضافه کنید.
    """
    s = s.strip().lower()
    s = _slug_re.sub("-", s)
    return s.strip("-")


def dedent_trim(s: str) -> str:
    """حذف اینتند اضافی و برش فاصله‌های پیش/پس از متن چندخطی."""
    return textwrap.dedent(s).strip()
```

### 3.3) `src/myhelpers/datetime_.py`
```python
from __future__ import annotations
from datetime import datetime, timezone


def utcnow_iso() -> str:
    """زمان فعلی به‌صورت ISO-8601 با زون UTC."""
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str) -> datetime:
    """تبدیل رشتهٔ ISO-8601 به datetime آگاه به منطقهٔ زمانی.

    از `datetime.fromisoformat` استفاده می‌کند و اگر زون نداشته باشد، آن را UTC در نظر می‌گیرد.
    """
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
```

### 3.4) (اختیاری) `src/myhelpers/typing_.py`
```python
from __future__ import annotations
from typing import TypeVar, Callable, Iterable, Iterator

T = TypeVar("T")


def chunked(iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    """تقسیم یک iterable به قطعات با اندازهٔ ثابت."""
    chunk: list[T] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
```

---

## 4) تست‌ها
### 4.1) `tests/test_string.py`
```python
from myhelpers import slugify_simple, dedent_trim


def test_slugify_simple():
    assert slugify_simple("Hello, World!") == "hello-world"
    assert slugify_simple("  A  B   ") == "a-b"


def test_dedent_trim():
    s = """
        line1
          line2
    """
    out = dedent_trim(s)
    assert out.splitlines()[0] == "line1"
```

### 4.2) `tests/test_datetime.py`
```python
from myhelpers import utcnow_iso, parse_iso


def test_utcnow_iso_roundtrip():
    s = utcnow_iso()
    dt = parse_iso(s)
    assert dt.tzinfo is not None
```

---

## 5) فایل‌های متنی
### 5.1) `README.md`
```markdown
# myhelpers

A tiny collection of reusable helper utilities.

## Installation
```bash
pip install myhelpers
```

## Usage
```python
from myhelpers import slugify_simple, utcnow_iso

print(slugify_simple("Hello, World!"))  # -> "hello-world"
print(utcnow_iso())
```
```

### 5.2) `LICENSE`

متن مجوز دلخواه (مثلاً MIT):
```text
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
... (متن کامل مجوز MIT) ...
```

### 5.3) `.gitignore`
```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.dist/
.build/

# Envs
.env
.venv/
venv/

# IDE
.vscode/
.idea/
```

---

## 6) CI ساده (GitHub Actions): `.github/workflows/ci.yml`
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install --upgrade pip
      - run: pip install -e .
      - run: pip install pytest ruff black
      - run: ruff check src tests
      - run: black --check src tests
      - run: pytest
```

---

## 7) دستورات رایج توسعه
```bash
# ایجاد و فعال‌سازی محیط مجازی (مثال با venv)
python -m venv .venv
source .venv/bin/activate     # در ویندوز: .venv\\Scripts\\activate

# نصب وابستگی‌های dev (اختیاری)
pip install -U pip pytest ruff black isort

# نصب پکیج به‌صورت editable برای توسعه
pip install -e .

# اجرای تست‌ها
pytest

# قالب‌بندی و لینت
black src tests && isort src tests && ruff check src tests
```

---

## 8) ساخت بسته و انتشار
### 8.1) ساخت بسته (wheel + sdist)
```bash
python -m pip install --upgrade build twine
python -m build
```
خروجی‌ها در پوشهٔ `dist/` ساخته می‌شوند.

### 8.2) انتشار در TestPyPI (برای تمرین)
```bash
python -m twine upload --repository testpypi dist/*
```
سپس نصب تستی:
```bash
pip install -i https://test.pypi.org/simple/ myhelpers
```

### 8.3) انتشار در PyPI اصلی
```bash
python -m twine upload dist/*
```

> اگر نمی‌خواهید عمومی کنید، می‌توانید پکیج را «خصوصی» نگه دارید و مستقیماً از Git نصب کنید:
```bash
pip install git+https://github.com/yourname/myhelpers@v0.1.0
```

---

## 9) استفاده از پکیج در سایر پروژه‌ها
در پروژهٔ دیگر:
```bash
pip install myhelpers  # یا نصب از Git/TestPyPI
```
سپس:
```python
from myhelpers import slugify_simple, utcnow_iso
print(slugify_simple("سلام دنیا"))
print(utcnow_iso())
```

---

## 10) نکات نسخه‌دهی و انتشار
- از Semantic Versioning پیروی کنید: MAJOR.MINOR.PATCH
- قبل از انتشار، `pytest` و لینت‌ها را پاس کنید.
- CHANGELOG نگه دارید (می‌توانید `Keep a Changelog` را الگو قرار دهید).
- برای نسخه‌دهی خودکار از `setuptools_scm` استفاده کنید تا نسخه از تگ Git خوانده شود.

---

## 11) گسترش‌های پیشنهادی
- افزودن زیرپکیج‌ها (مثلاً `myhelpers/fs.py`, `myhelpers/http.py`).
- افزودن type hints کامل و `py.typed` برای سازگاری کامل با mypy/pyright:
  - فایل خالی `src/myhelpers/py.typed` بسازید و در `pyproject.toml` بخش `tool.setuptools`، آن را به‌عنوان data-files اضافه کنید:

```toml
[tool.setuptools.package-data]
myhelpers = ["py.typed"]
```

- اگر توابع شما به پکیج‌های خارجی وابسته‌اند، آن‌ها را در `dependencies` اضافه کنید یا به‌صورت `optional-dependencies` گروه‌بندی کنید:

```toml
[project.optional-dependencies]
http = ["httpx>=0.27", "tenacity>=8"]
cli = ["typer>=0.12", "rich>=13"]
```

سپس کاربران می‌توانند نصب انتخابی داشته باشند:
```bash
pip install myhelpers[http,cli]
```

---

### چک‌لیست سریع
- [ ] نام پکیج نهایی را انتخاب و در `pyproject.toml` بگذارید.
- [ ] مجوز و README را اصلاح کنید.
- [ ] توابع واقعی خود را در ماژول‌ها قرار دهید.
- [ ] تست‌ها را بنویسید و اجرا کنید.
- [ ] نسخه را به‌روز کنید و انتشار بدهید.

پایان. اگر دوست دارید همین حالا نام پکیج را بگویید تا این اسکلت را با نام و جزئیات شما سفارشی‌سازی کنم. همچنین می‌توانیم توابع اولیهٔ دلخواه‌تان را هم اضافه کنیم (مثلاً کار با تاریخ جلالی، فایل، HTTP و …).

