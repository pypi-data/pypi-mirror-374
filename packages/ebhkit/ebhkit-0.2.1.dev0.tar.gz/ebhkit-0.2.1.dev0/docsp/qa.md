
# Prompt for code completation

Complete and edit the given function. Focus on the function itself. I don't want extra functions.
Infer its purpose and functionality based on its structure and naming conventions. 
The code you generate must:
- Follow standard coding conventions (PEP8 for Python or the relevant language standard).
- Use clear, meaningful, and consistent naming for variables and functions.
- Include comprehensive documentation (docstrings (google style) include Examples  and Raises for functions and classes + explanatory comments in key parts).
- Be readable and maintainable.
- Include error handling and basic tests (unit tests or usage examples) if applicable. Also mention the name of the test file (test file name structure)
- The function is written in a separate file with the same name as the function and the test should be written in a separate file.
<!-- - Be optimized and simple, not overly complicated. -->
- Implement a proper logging mechanism instead of using print statements, following best practices for the given language.
- If an external function is used in it, then the function is complete, for example, it has error handling.
- Output a full, complete, and executable code snippet.

Here is the incomplete code:
```python
[Insert the incomplete code here]
```

# Import Tips
بله—می‌شود «برای هر فانکشن یک فایل» داشته باشی و در عین حال کاری کنی که مصرف‌کننده فقط از سطح **دایرکتوری (پکیج)** ایمپورت کند. نکته: با `__all__` می‌توانی **API عمومی** را کنترل کنی و با `__init__.py` آن‌ها را **re-export** کنی. امّا یادت باشد `__all__` فقط روی `from pkg import *` اثر دارد؛ جلوی `import pkg.submod` را ذاتاً نمی‌گیرد. (می‌توانی «غیرداستانه»‌اش کنی، نه کاملاً غیرممکن.)

## الگوی ساده و صریح (پیشنهادی)

ساختار:

```
mypkg/
├─ __init__.py
├─ add.py          # هر فایل = یک فانکشن
├─ slugify.py
└─ _internal.py    # خصوصی (با آندرلاین)
```

`add.py`:

```python
__all__ = ["add"]

def add(a: int, b: int) -> int:
    return a + b
```

`slugify.py`:

```python
__all__ = ["slugify"]

def slugify(s: str) -> str:
    ...
```

`__init__.py` (re-export):

```python
from .add import add
from .slugify import slugify

__all__ = ["add", "slugify"]  # فقط این‌ها از سطح پکیج عمومی‌اند
```

حالا کاربر استفاده می‌کند:

```python
from mypkg import add, slugify   # ✅
# از نگاه او نیازی به دانستن فایل‌های زیرمجموعه نیست
```

> نکته: فایل‌هایی که با آندرلاین شروع می‌شوند (مثل `_internal.py`) تلویحاً **private** هستند و معمولاً در `__all__` قرار نمی‌گیرند.

---

## الگوی خودکار (گردآوری داینامیک)

اگر فایل زیاد داری و نمی‌خواهی هر بار `__init__.py` را دستی به‌روزرسانی کنی:

`__init__.py`:

```python
import importlib
import pkgutil

__all__ = []

# روی همهٔ ماژول‌های همین پکیج loop می‌زنیم
for _finder, _name, _ispkg in pkgutil.iter_modules(__path__):
    if _name.startswith("_"):
        continue
    mod = importlib.import_module(f".{_name}", __name__)
    public = getattr(mod, "__all__", [])
    # هر چیزی که خود ماژول عمومی کرده را re-export کن
    for sym in public:
        globals()[sym] = getattr(mod, sym)
    __all__.extend(public)
```

* هر ماژولِ تک‌تابعی، `__all__` خودش را تعیین می‌کند.
* `__init__.py` همه‌ی آن نام‌ها را **به سطح پکیج** re-export می‌کند.

**عیب‌ها:** کمی هزینهٔ import بالاتر، و ابزارهای استاتیک (IDE/mypy) ممکن است «کمتر قابل پیش‌بینی» ببینند.

---

## الگوی تنبل (Lazy) با PEP 562

اگر می‌خواهی ایمپورت‌ها تنبل باشند، می‌توانی از `__getattr__` در سطح پکیج استفاده کنی:

`__init__.py`:

```python
import importlib

# نام عمومی -> ماژول میزبان
_exports = {
    "add": "add",
    "slugify": "slugify",
}
__all__ = list(_exports.keys())

def __getattr__(name: str):
    if name in _exports:
        mod = importlib.import_module(f".{_exports[name]}", __name__)
        obj = getattr(mod, name)
        globals()[name] = obj   # کش کن برای دفعات بعد
        return obj
    raise AttributeError(name)

def __dir__():
    return sorted(list(globals().keys()) + __all__)
```

**مزیت:** ماژول‌های زیرمجموعه وقتی واقعاً لازم شدند بارگذاری می‌شوند.
**هشدار:** برخی ابزارهای تایپ/IDE ممکن است برای تکمیل خودکار سخت‌گیر باشند. برای سازگاری بهتر:

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .add import add
    from .slugify import slugify
```

---

## آیا می‌توان کاملاً جلوی `import mypkg.add` را گرفت؟

نه، به‌طور کامل نه. اگر فایل فیزیکی هست، پایتون می‌تواند مستقیماً ایمپورتش کند. کارهای ممکن:

* نام‌گذاری خصوصی: `_add.py` و مستندسازی نکردنش.
* فقط نام‌های عمومی را در `__all__` و README معرفی کن.
* در پروژه‌های بزرگ‌تر، زیرپکیج `internal/` بساز و بگو **API پایدار نیست**.

---

## جمع‌بندی پیشنهادی

* اگر سادگی و شفافیت می‌خواهی: **الگوی صریح** (re-export دستی در `__init__.py`) بهترین است.
* اگر تعداد فایل‌ها زیاد است و حوصلهٔ به‌روزرسانی دستی نداری: **گردآوری داینامیک**.
* اگر پرفورمنس import مهم است: **الگوی Lazy** با `__getattr__` (+ `TYPE_CHECKING` برای IDE).

اگر نام نهایی پکیجت را بدهی (مثلاً `simurgh` یا `athena-utils`)، همین ساختار را دقیقاً برای تو تولید می‌کنم و در Canvas می‌گذارم.
