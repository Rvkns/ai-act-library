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


def validate_regulation(data, label):
    """The base Regulation (IT/EN) is known to have 180 recitals, 113
    articles numbered contiguously 1..113, and 13 annexes. A truncated or
    empty JSON file must fail loudly instead of silently producing a
    broken 2MB output file."""
    assert isinstance(data, dict), f"{label}: expected a JSON object"
    for key, expected in (("recitals", 180), ("articles", 113), ("annexes", 13)):
        items = data.get(key)
        assert isinstance(items, list), f"{label}: missing or invalid '{key}'"
        assert len(items) == expected, (
            f"{label}: expected {expected} {key}, got {len(items)}"
        )
    nums = sorted(a["num"] for a in data["articles"])
    assert nums == list(range(1, 114)), (
        f"{label}: articles are not numbered contiguously 1..113 "
        f"(got {nums[:3]}...{nums[-3:]})"
    )


def validate_omnibus(data, label):
    """The Digital Omnibus is known to have 4 articles."""
    assert isinstance(data, dict), f"{label}: expected a JSON object"
    articles = data.get("articles")
    assert isinstance(articles, list), f"{label}: missing or invalid 'articles'"
    assert len(articles) == 4, f"{label}: expected 4 articles, got {len(articles)}"


def main():
    reg_it = load("regulation_it.json")
    reg_en = load("regulation_en.json")
    omnibus_en = load("omnibus_en.json")

    validate_regulation(reg_it, "regulation_it.json")
    validate_regulation(reg_en, "regulation_en.json")
    validate_omnibus(omnibus_en, "omnibus_en.json")

    data_js = (
        "const LIBRARY_DATA = "
        + json.dumps({"it": reg_it, "en": reg_en}, ensure_ascii=False)
        + ";\nconst OMNIBUS_DATA = "
        + json.dumps({"en": omnibus_en}, ensure_ascii=False)
        + ";"
    )
    # json.dumps does not escape '<', so a literal "</script" anywhere in the
    # data would truncate the embedded <script> block and silently produce a
    # broken file. Escape it defensively.
    data_js = data_js.replace("<", "\\u003c")

    template = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in template:
        raise SystemExit(f"marker {MARKER} not found in template")
    output = template.replace(MARKER, data_js)
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
