# tests/conftest.py
import importlib.util
import pathlib
import sys

# اگر hkit نصب/در دسترس نبود، src را به sys.path اضافه کن
if importlib.util.find_spec("hkit") is None:
    repo_root = pathlib.Path(__file__).resolve().parents[1]  # روت ریپو
    sys.path.insert(0, str(repo_root / "src"))
