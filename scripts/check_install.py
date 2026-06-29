from __future__ import annotations

import importlib.util
import platform
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version


PACKAGES = [
    "nautilus-trader",
    "nautilus-ibapi",
    "python-dotenv",
]

MODULES = [
    "nautilus_trader",
    "nautilus_trader.adapters.interactive_brokers",
    "ibapi",
    "dotenv",
]


def print_package_versions() -> None:
    for package in PACKAGES:
        try:
            print(f"{package}: {version(package)}")
        except PackageNotFoundError:
            print(f"{package}: NOT INSTALLED")


def verify_imports() -> int:
    missing = []
    for module_name in MODULES:
        if importlib.util.find_spec(module_name) is None:
            missing.append(module_name)
        else:
            print(f"import ok: {module_name}")

    if missing:
        print("missing imports: " + ", ".join(missing))
        return 1

    return 0


def main() -> int:
    print(f"python: {sys.version.split()[0]}")
    print(f"platform: {platform.platform()}")
    print_package_versions()
    return verify_imports()


if __name__ == "__main__":
    raise SystemExit(main())
