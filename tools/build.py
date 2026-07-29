#!/usr/bin/env python
"""Assemble ai-act-biblioteca.html from the template and the extracted
regulation/omnibus JSON data.

Usage:
    python tools/build.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "biblioteca.template.html"
OUTPUT = ROOT / "ai-act-biblioteca.html"
MARKER = "/*__LIBRARY_DATA__*/"


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def main():
    reg_it = load("regulation_it.json")
    reg_en = load("regulation_en.json")
    omnibus_en = load("omnibus_en.json")

    data_js = (
        "const LIBRARY_DATA = "
        + json.dumps({"it": reg_it, "en": reg_en}, ensure_ascii=False)
        + ";\nconst OMNIBUS_DATA = "
        + json.dumps({"en": omnibus_en}, ensure_ascii=False)
        + ";"
    )

    template = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in template:
        raise SystemExit(f"marker {MARKER} not found in template")
    output = template.replace(MARKER, data_js)
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
