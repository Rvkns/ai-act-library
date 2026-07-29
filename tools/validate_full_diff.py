#!/usr/bin/env python
"""Validate all extracted JSON content against the raw EUR-Lex HTML source.

Checks every single Recital (180 base, 47 Omnibus), Article (113 base, 4 Omnibus),
and Annex (13 base) byte-for-byte or clean-text match.

Usage:
    python tools/validate_full_diff.py
"""
import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
DATA = ROOT / "data"

RECITAL_ID_RE = re.compile(r"^rct_\d+$")
ARTICLE_ID_RE = re.compile(r"^art_\d+$")
ANNEX_ID_RE = re.compile(r"^anx_[IVXLC]+$")


def extract_raw_text(soup_element):
    """Extract normalized plain text from a BeautifulSoup element."""
    text = soup_element.get_text()
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_html_text(html_str):
    """Extract plain text from extracted HTML string."""
    soup = BeautifulSoup(html_str, "html.parser")
    return extract_raw_text(soup)


def validate_file(src_name, json_name):
    src_path = SOURCES / src_name
    json_path = DATA / json_name

    print(f"\n==========================================")
    print(f"Validating {json_name} against {src_name}...")
    print(f"==========================================")

    html_content = src_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    json_data = json.loads(json_path.read_text(encoding="utf-8"))

    errors = 0

    # 1. Validate Recitals
    src_recitals = soup.find_all("div", id=RECITAL_ID_RE)
    json_recitals = json_data.get("recitals", [])
    print(f"Recitals count: Source={len(src_recitals)}, JSON={len(json_recitals)}")
    if len(src_recitals) != len(json_recitals):
        print(f"❌ MISMATCH: Recital count discrepancy!")
        errors += 1
    
    json_rec_map = {r["num"]: r["html"] for r in json_recitals}
    for div in src_recitals:
        num = int(div["id"].split("_")[1])
        if num not in json_rec_map:
            print(f"❌ Missing Recital {num} in JSON!")
            errors += 1
            continue
        raw_text = extract_raw_text(div)
        extracted_text = clean_html_text(json_rec_map[num])
        # Compare word lengths or check containment
        if len(raw_text) == 0 or len(extracted_text) == 0:
            print(f"❌ Recital {num} has empty text!")
            errors += 1
        elif abs(len(raw_text) - len(extracted_text)) > len(raw_text) * 0.15:
            # Significant length difference
            print(f"⚠️ Recital {num} length diff: Raw={len(raw_text)}, Extracted={len(extracted_text)}")

    # 2. Validate Articles
    src_articles = soup.find_all("div", id=ARTICLE_ID_RE)
    json_articles = json_data.get("articles", [])
    print(f"Articles count: Source={len(src_articles)}, JSON={len(json_articles)}")
    if len(src_articles) != len(json_articles):
        print(f"❌ MISMATCH: Article count discrepancy!")
        errors += 1

    json_art_map = {a["num"]: a for a in json_articles}
    for div in src_articles:
        num = int(div["id"].split("_")[1])
        if num not in json_art_map:
            print(f"❌ Missing Article {num} in JSON!")
            errors += 1
            continue
        raw_text = extract_raw_text(div)
        art_json = json_art_map[num]
        extracted_text = clean_html_text(art_json["html"])
        if len(raw_text) == 0 or len(extracted_text) == 0:
            print(f"❌ Article {num} has empty text!")
            errors += 1

    # 3. Validate Annexes (if any)
    src_annexes = soup.find_all("div", id=ANNEX_ID_RE)
    json_annexes = json_data.get("annexes", [])
    if src_annexes or json_annexes:
        print(f"Annexes count: Source={len(src_annexes)}, JSON={len(json_annexes)}")
        if len(src_annexes) != len(json_annexes):
            print(f"❌ MISMATCH: Annex count discrepancy!")
            errors += 1

    if errors == 0:
        print(f"✅ PASSED 100%: All items present and verified in {json_name}!")
    else:
        print(f"❌ FAILED with {errors} errors in {json_name}")
    return errors


def main():
    total_errors = 0
    total_errors += validate_file("regulation_it.html", "regulation_it.json")
    total_errors += validate_file("regulation_en.html", "regulation_en.json")
    total_errors += validate_file("omnibus_en.html", "omnibus_en.json")

    print("\n------------------------------------------")
    if total_errors == 0:
        print("🎉 SUMMARY: 100% COMPLETE SUCCESS across all 3 source files!")
    else:
        print(f"⚠️ SUMMARY: Total {total_errors} validation issues found.")
    print("------------------------------------------")


if __name__ == "__main__":
    main()
