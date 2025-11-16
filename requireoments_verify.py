import importlib
import re
import sys

reqs = "/opt/valhalla/requirements.txt"
with open(reqs) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        pkg = re.split("[<>=]", line)[0]
        try:
            if pkg.startswith("PyYAML"):
                pkg = "yaml"
            if pkg.startswith("GitPython"):
                pkg = "git"
            importlib.import_module(pkg)
            print(f"[OK] {pkg}")
        except ImportError:
            print(f"[ERROR] Missing module: {pkg}")
            sys.exit(1)
