#!/usr/bin/env python
"""Extract recitals, articles and annexes from an EUR-Lex 'OJ HTML' page
(as served for Regulation (EU) 2024/1689 and (EU) 2026/1744) into JSON.

The source files are Wayback Machine snapshots of the official EUR-Lex
HTML view, which uses a consistent semantic structure regardless of
language: recitals live in <div id="rct_N">, articles in <div id="art_N">,
annexes in <div id="anx_<ROMAN>">.

Usage:
    python tools/extract.py <source.html> <output.json>
"""
import json
import re
import sys

from bs4 import BeautifulSoup, Tag

RECITAL_ID_RE = re.compile(r"^rct_\d+$")
ARTICLE_ID_RE = re.compile(r"^art_\d+$")
ANNEX_ID_RE = re.compile(r"^anx_[IVXLC]+$")
ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def clean_fragment(tag: Tag) -> str:
    """Return sanitised inner HTML of `tag` for standalone embedding.

    - Strips <script>/<style> (defensive; none expected inside content).
    - Unwraps <a> tags (keeps the link text, drops the href) since the
      original hrefs are intra-EUR-Lex or Wayback-relative and would be
      broken or misleading inside a standalone offline file.
    - Collapses the EUR-Lex numbering padding (runs of non-breaking
      spaces used to align "1.   Text") down to a single space, and
      normalises remaining non-breaking spaces to regular spaces.
    """
    frag = BeautifulSoup(str(tag), "html.parser")
    for bad in frag.find_all(["script", "style"]):
        bad.decompose()
    for note in frag.find_all("span", class_="oj-note-tag"):
        note.decompose()
    for a in frag.find_all("a"):
        a.unwrap()
    html = str(frag)
    html = html.replace("\xa0\xa0\xa0", " ").replace("\xa0\xa0", " ").replace("\xa0", " ")
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n\s*\n+", "\n", html)
    return html.strip()


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def roman_to_int(r: str) -> int:
    total = 0
    for i, ch in enumerate(r):
        v = ROMAN_VALUES[ch]
        if i + 1 < len(r) and ROMAN_VALUES[r[i + 1]] > v:
            total -= v
        else:
            total += v
    return total


def extract_recitals(soup: BeautifulSoup) -> list:
    recitals = []
    for div in soup.find_all("div", id=RECITAL_ID_RE):
        num = int(div["id"].split("_")[1])
        recitals.append({"num": num, "html": clean_fragment(div)})
    recitals.sort(key=lambda r: r["num"])
    return recitals


def extract_articles(soup: BeautifulSoup) -> list:
    articles = []
    for div in soup.find_all("div", id=ARTICLE_ID_RE):
        num = int(div["id"].split("_")[1])
        title_p = div.select_one(".eli-title .oj-sti-art")
        title = clean_text(title_p.get_text()) if title_p else ""
        body_parts = []
        for child in div.find_all(recursive=False):
            if not isinstance(child, Tag):
                continue
            classes = child.get("class") or []
            if "eli-title" in classes or "oj-ti-art" in classes:
                continue
            body_parts.append(clean_fragment(child))
        articles.append({"num": num, "title": title, "html": "\n".join(body_parts)})
    articles.sort(key=lambda a: a["num"])
    return articles


def extract_annexes(soup: BeautifulSoup) -> list:
    annexes = []
    for div in soup.find_all("div", id=ANNEX_ID_RE):
        roman = div["id"].split("_", 1)[1]
        doc_titles = [
            c for c in div.find_all("p", recursive=False)
            if "oj-doc-ti" in (c.get("class") or [])
        ]
        title = clean_text(doc_titles[1].get_text()) if len(doc_titles) > 1 else ""
        body_parts = []
        skipped = 0
        for child in div.find_all(recursive=False):
            if (
                skipped < 2
                and getattr(child, "name", None) == "p"
                and "oj-doc-ti" in (child.get("class") or [])
            ):
                skipped += 1
                continue
            if not isinstance(child, Tag):
                continue
            body_parts.append(clean_fragment(child))
        annexes.append({"num": roman, "title": title, "html": "\n".join(body_parts)})
    annexes.sort(key=lambda a: roman_to_int(a["num"]))
    return annexes


def extract(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    return {
        "recitals": extract_recitals(soup),
        "articles": extract_articles(soup),
        "annexes": extract_annexes(soup),
    }


def main():
    if len(sys.argv) != 3:
        print("usage: python extract.py <source.html> <output.json>")
        sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]
    html = open(src, encoding="utf-8").read()
    data = extract(html)
    print(
        f"{src}: {len(data['recitals'])} recitals, "
        f"{len(data['articles'])} articles, {len(data['annexes'])} annexes"
    )
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
