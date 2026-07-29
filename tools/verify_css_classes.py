#!/usr/bin/env python
"""Verify all EUR-Lex HTML CSS classes in source files against stylesheet rules.

Extracts all class names used in sources/*.html and verifies their styling coverage
in biblioteca.template.html / ai-act-biblioteca.html.

Usage:
    python tools/verify_css_classes.py
"""
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
TEMPLATE = ROOT / "templates" / "biblioteca.template.html"


def get_all_classes(html_file):
    soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")
    classes = set()
    for tag in soup.find_all(True):
        for c in tag.get("class", []):
            classes.add(c)
    return classes


def main():
    print("==========================================")
    print("EUR-Lex CSS Classes Audit")
    print("==========================================")

    all_src_classes = set()
    for src in SOURCES.glob("*.html"):
        classes = get_all_classes(src)
        print(f"File {src.name}: {len(classes)} distinct CSS classes found.")
        all_src_classes.update(classes)

    print(f"\nTotal unique CSS classes across all source files: {len(all_src_classes)}")
    oj_classes = sorted([c for c in all_src_classes if c.startswith("oj-") or c.startswith("eli-")])
    print(f"EUR-Lex specific classes ({len(oj_classes)}): {', '.join(oj_classes)}")

    template_css = TEMPLATE.read_text(encoding="utf-8")

    covered = []
    uncovered = []

    for c in oj_classes:
        # Search for .class_name in CSS rules
        pattern = r"\." + re.escape(c) + r"\b"
        if re.search(pattern, template_css):
            covered.append(c)
        else:
            uncovered.append(c)

    print(f"\nCovered by stylesheet ({len(covered)}):")
    for c in covered:
        print(f"  ✅ .{c}")

    if uncovered:
        print(f"\nUncovered EUR-Lex classes ({len(uncovered)}):")
        for c in uncovered:
            print(f"  ℹ️ .{c}")

    print("\n------------------------------------------")
    print("Audit completed successfully!")
    print("------------------------------------------")


if __name__ == "__main__":
    main()
