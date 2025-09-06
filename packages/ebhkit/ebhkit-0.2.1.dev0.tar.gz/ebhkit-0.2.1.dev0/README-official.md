# hkit
*Helper KIT*

> 🧰 A tiny collection of reusable helper utilities for Python projects.

`hkit` provides a lightweight set of functions and helpers to simplify repetitive tasks in everyday Python development.

---

## 📦 Installation

From PyPI (once released):

```bash
pip install ebhkit
```

---

## 🚀 Quick Start

Example usage:

```python
from ebhkit import slugify, chunks

print(slugify("Hello World!"))
# hello-world

for part in chunks(range(10), size=3):
    print(part)
# [0, 1, 2]
# [3, 4, 5]
# [6, 7, 8]
# [9]
```

---

## ✨ Features

* 🔠 Text utilities (`slugify`, `truncate`, …)
* 🗂️ List and iterable helpers (`chunks`, `flatten`, …)
* ⏱️ Date and time utilities
* ⚡ Zero heavy dependencies


## 📜 License

This project is licensed under the [MIT License](LICENSE).


