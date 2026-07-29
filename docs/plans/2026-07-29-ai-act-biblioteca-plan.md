# AI Act Biblioteca — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge `ai-act-explorer.html` and `eu_ai_act_guida_vademecum.html` into one
self-contained `ai-act-biblioteca.html` that adds a full bilingual verbatim-text
"Biblioteca" (recitals, articles, annexes of Reg. (EU) 2024/1689, plus the Digital
Omnibus Reg. (EU) 2026/1744 in EN) alongside the existing "Guida" content, with a
library-grade reading UI.

**Architecture:** `ai-act-explorer.html`'s existing single-page JS app (global `state`
object, `UI` i18n dict, `render*()` functions writing into `#main`/`#sidebar`) is
extended, not replaced. A new top-level mode (`state.mode`: `'guide'|'library'`)
switches between the existing Guida shell and a new parallel Biblioteca shell that
renders from data extracted out-of-band from official EUR-Lex text.

**Tech Stack:** Vanilla HTML/CSS/JS (no new runtime dependency — Google Fonts import
only), Python 3 + BeautifulSoup4 for the one-time data-extraction build step.

## Global Constraints

- Final deliverable is a single self-contained HTML file (`ai-act-biblioteca.html`),
  openable offline, no CDN dependency beyond the Google Fonts `@import` already in use.
- Bilingual IT/EN toggle must keep working exactly as today for the Guida; the
  Biblioteca's Regulation text (articles/recitals/annexes) is real bilingual verbatim
  text, switched by the same global toggle. The Digital Omnibus document is EN-only
  and must show an explicit note about the missing official IT text.
- No text is invented or paraphrased for the verbatim library: only the extracted
  EUR-Lex text goes into `data/*.json`, produced by `tools/extract.py`.
- Follow the existing file's exact conventions: CSS custom properties already defined
  in `:root`, the `UI.it` / `UI.en` string-dictionary pattern, `render*()` functions
  returning template strings, one `setLang`-style master re-render entrypoint per mode.

---

## Already completed (validated during design spike)

These are done and verified; listed here for a complete record, not to be redone.

- [x] **Data sourcing.** EUR-Lex blocks direct fetch (AWS WAF `challenge` on both curl
  and WebFetch). Recovered via Wayback Machine snapshots instead:
  - `sources/regulation_it.html` — Reg. 2024/1689 IT, snapshot 2026-07-27.
  - `sources/regulation_en.html` — Reg. 2024/1689 EN, snapshot 2026-07-25.
  - `sources/omnibus_en.html` — Digital Omnibus 2026/1744 EN, snapshot 2026-07-28.
    (IT version of the Omnibus is not archived anywhere reachable; per user decision
    it is included EN-only with an explicit note.)
- [x] **`tools/extract.py`** — parses the EUR-Lex semantic HTML (`div#rct_N`,
  `div#art_N`, `div#anx_<ROMAN>`) into JSON via BeautifulSoup4. Handles both
  structural variants found (numbered-paragraph sub-divs in the base Regulation;
  flat `<p>`/`<table>` children in the Omnibus). Strips footnote-reference spans
  (`oj-note-tag`) and unwraps `<a>` tags (their hrefs are Wayback/EUR-Lex-relative
  and would be dead or misleading in a standalone file).
- [x] **`data/regulation_it.json`** (909 KB), **`data/regulation_en.json`** (852 KB) —
  each verified: 180 recitals, 113 articles, 13 annexes, non-trivial body text on
  every entry, zero leftover footnote markers.
- [x] **`data/omnibus_en.json`** (220 KB) — verified: 4 top-level articles (matches
  the real structure: Art. 1 amends Reg. 2024/1689, Art. 2 amends Reg. 2018/1139,
  Art. 3 amends Reg. 2023/1230, Art. 4 entry into force), 47 recitals, 0 annexes.

---

### Task 1: Build script and template skeleton

**Files:**
- Create: `templates/biblioteca.template.html` (copy of `ai-act-explorer.html` plus
  one data-injection marker and the chapter-range table)
- Create: `tools/build.py`
- Modify: none

**Interfaces:**
- Produces: `ai-act-biblioteca.html` (repo root), rebuildable any time via
  `python tools/build.py`.
- Produces: global JS constants `LIBRARY_DATA` (`{it:{recitals,articles,annexes}, en:{...}}`)
  and `OMNIBUS_DATA` (`{en:{recitals,articles,annexes}}`), available to every later task.
- Produces: `CHAPTER_RANGES` (array of `{id, num, from, to}`) and
  `chapterForArticle(num)` (returns the matching `CHAPTER_RANGES` entry), used by
  Task 3 to group articles by chapter in the Biblioteca sidebar.

- [ ] **Step 1: Copy the explorer file into the template location**

```bash
cp "ai-act-explorer.html" "templates/biblioteca.template.html"
```

- [ ] **Step 2: Insert the data marker and chapter-range table**

In `templates/biblioteca.template.html`, find this exact block (it currently
appears right after the `SCENARIOS` array and right before the `state` declaration):

```js
/* ============================= STATE ============================= */
let state = { lang:'it', roleTab:'provider', filter:'all', query:'' };
```

Replace it with:

```js
/*__LIBRARY_DATA__*/

const CHAPTER_RANGES = [
  {id:'ch1', num:'I', from:1, to:4},
  {id:'ch2', num:'II', from:5, to:5},
  {id:'ch3', num:'III', from:6, to:49},
  {id:'ch4', num:'IV', from:50, to:50},
  {id:'ch5', num:'V', from:51, to:56},
  {id:'ch6', num:'VI', from:57, to:63},
  {id:'ch7', num:'VII', from:64, to:70},
  {id:'ch8', num:'VIII', from:71, to:71},
  {id:'ch9', num:'IX', from:72, to:94},
  {id:'ch10', num:'X', from:95, to:96},
  {id:'ch11', num:'XI', from:97, to:98},
  {id:'ch12', num:'XII', from:99, to:101},
  {id:'ch13', num:'XIII', from:102, to:113}
];
function chapterForArticle(num){
  return CHAPTER_RANGES.find(r => num>=r.from && num<=r.to);
}

/* ============================= STATE ============================= */
let state = { lang:'it', mode:'guide', roleTab:'provider', filter:'all', query:'',
              libSection:'recitals', libArticle:1 };
```

- [ ] **Step 3: Write `tools/build.py`**

```python
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
```

- [ ] **Step 4: Run the build and verify**

```bash
python tools/build.py
```

Expected: prints `wrote .../ai-act-biblioteca.html (N bytes)` with N between
1,800,000 and 2,500,000. Then verify the data is valid embedded JSON:

```bash
python -c "
import re
html = open('ai-act-biblioteca.html', encoding='utf-8').read()
m = re.search(r'const LIBRARY_DATA = (\{.*?\});\n', html, re.S)
import json
data = json.loads(m.group(1))
assert len(data['it']['articles']) == 113
assert len(data['en']['recitals']) == 180
print('LIBRARY_DATA OK')
"
```

Expected output: `LIBRARY_DATA OK`.

- [ ] **Step 5: Commit**

```bash
git add templates/biblioteca.template.html tools/build.py
git commit -m "Add build pipeline assembling the biblioteca HTML from extracted data"
```

(Skip this step if the project is not a git repository — it is not, as of this plan;
just leave the files in place.)

---

### Task 2: Mode toggle (Guida / Biblioteca) and shell restructuring

**Files:**
- Modify: `templates/biblioteca.template.html`

**Interfaces:**
- Consumes: `state.mode` from Task 1.
- Produces: `setMode(mode)` function, `#guideShell` / `#libraryShell` DOM containers,
  `#librarySidebar` / `#libraryMain` mount points that Task 3 renders into.

- [ ] **Step 1: Add UI strings**

Find (near the top of the `UI` object):

```js
    navDash:'Dashboard', navClass:'Strumento di classificazione', navRoles:'Obblighi per ruolo', navChapters:'Capitoli', navAnnex:'Allegati', navScen:'Casi pratici',
```

Add right after it, still inside `UI.it`:

```js
    modeGuide:'Guida', modeLibrary:'Biblioteca', searchLibPh:'Cerca nel testo integrale…',
```

Find the matching English line:

```js
    navDash:'Dashboard', navClass:'Classification tool', navRoles:'Obligations by role', navChapters:'Chapters', navAnnex:'Annexes', navScen:'Common scenarios',
```

Add right after it, still inside `UI.en`:

```js
    modeGuide:'Guide', modeLibrary:'Library', searchLibPh:'Search the full text…',
```

- [ ] **Step 2: Add the mode toggle to the header**

Find:

```html
    <span class="search-count" id="searchCount"></span>
    <div class="langtoggle">
```

Replace with:

```html
    <span class="search-count" id="searchCount"></span>
    <div class="langtoggle" id="modeToggle">
      <button id="btnGuide" class="active"></button>
      <button id="btnLibrary"></button>
    </div>
    <div class="langtoggle">
```

- [ ] **Step 3: Add the search-results dropdown mount point**

Find:

```html
    <div class="searchwrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input id="searchInput" type="text" data-i18n-ph="searchph">
    </div>
```

Replace with:

```html
    <div class="searchwrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input id="searchInput" type="text" data-i18n-ph="searchph">
      <div class="search-results-panel" id="searchResultsPanel"></div>
    </div>
```

- [ ] **Step 4: Split the shell into guide/library containers**

Find:

```html
<div class="shell">
  <nav class="sidebar" id="sidebar"></nav>
  <main id="main"></main>
</div>

<footer id="footer"></footer>
```

Replace with:

```html
<div class="shell" id="guideShell">
  <nav class="sidebar" id="sidebar"></nav>
  <main id="main"></main>
</div>

<div class="shell" id="libraryShell" style="display:none">
  <nav class="sidebar" id="librarySidebar"></nav>
  <main id="libraryMain"></main>
</div>

<footer id="footer"></footer>
```

- [ ] **Step 5: Add CSS for the new elements**

Find the last CSS rule before `</style>`:

```css
.js-hidden{display:none !important;}
```

Add after it:

```css
.search-results-panel{display:none; position:absolute; top:calc(100% + 4px); left:0; right:0; background:var(--card); border:1px solid var(--rule); border-radius:3px; box-shadow:var(--shadow); max-height:320px; overflow-y:auto; z-index:50;}
.search-results-panel.show{display:block;}
.search-result{display:block; width:100%; text-align:left; padding:8px 12px; border:none; border-bottom:1px solid var(--rule); background:transparent; cursor:pointer; font-size:12.5px; color:var(--ink); font-family:'Inter',sans-serif;}
.search-result:last-child{border-bottom:none;}
.search-result:hover{background:var(--paper-2);}
```

- [ ] **Step 6: Implement `setMode` and wire the buttons**

Find:

```js
/* ============================= INIT & EVENTS ============================= */
document.getElementById('btnIT').addEventListener('click', ()=> setLang('it'));
document.getElementById('btnEN').addEventListener('click', ()=> setLang('en'));
function setLang(lang){
  state.lang = lang;
  document.documentElement.lang = lang;
  document.getElementById('btnIT').classList.toggle('active', lang==='it');
  document.getElementById('btnEN').classList.toggle('active', lang==='en');
  document.getElementById('searchInput').placeholder = UI[lang].searchph;
  renderSidebar();
  renderMain();
  renderFooter();
  document.getElementById('searchInput').value = state.query;
}
```

Replace with:

```js
/* ============================= INIT & EVENTS ============================= */
document.getElementById('btnIT').addEventListener('click', ()=> setLang('it'));
document.getElementById('btnEN').addEventListener('click', ()=> setLang('en'));
document.getElementById('btnGuide').addEventListener('click', ()=> setMode('guide'));
document.getElementById('btnLibrary').addEventListener('click', ()=> setMode('library'));

function setMode(mode){
  state.mode = mode;
  document.getElementById('guideShell').style.display = mode==='guide' ? 'flex' : 'none';
  document.getElementById('libraryShell').style.display = mode==='library' ? 'flex' : 'none';
  document.getElementById('btnGuide').classList.toggle('active', mode==='guide');
  document.getElementById('btnLibrary').classList.toggle('active', mode==='library');
  document.getElementById('searchInput').placeholder = mode==='library' ? UI[state.lang].searchLibPh : UI[state.lang].searchph;
  document.getElementById('searchInput').value = '';
  document.getElementById('searchResultsPanel').classList.remove('show');
  state.query = '';
  document.getElementById('searchCount').textContent = '';
  if(mode==='library' && typeof renderLibrary==='function') renderLibrary();
}

function setLang(lang){
  state.lang = lang;
  document.documentElement.lang = lang;
  document.getElementById('btnIT').classList.toggle('active', lang==='it');
  document.getElementById('btnEN').classList.toggle('active', lang==='en');
  document.getElementById('btnGuide').textContent = UI[lang].modeGuide;
  document.getElementById('btnLibrary').textContent = UI[lang].modeLibrary;
  document.getElementById('searchInput').placeholder = state.mode==='library' ? UI[lang].searchLibPh : UI[lang].searchph;
  renderSidebar();
  renderMain();
  renderFooter();
  document.getElementById('searchInput').value = state.query;
  if(state.mode==='library' && typeof renderLibrary==='function') renderLibrary();
}
```

Note: `renderLibrary` does not exist yet (it is added in Task 3) — the
`typeof renderLibrary==='function'` guards let this task run standalone without
a ReferenceError.

- [ ] **Step 7: Build and verify in the browser**

```bash
python tools/build.py
```

Open `ai-act-biblioteca.html` in Chrome (via the claude-in-chrome tool or manually).
Verify:
- Header shows a "GUIDA / BIBLIOTECA" toggle next to "IT / EN".
- Clicking "BIBLIOTECA" hides the dashboard content and shows an empty sidebar/main
  pair (expected — content comes in Task 3); clicking "GUIDA" restores the dashboard.
- No JavaScript errors in the console (check via the browser's console messages).

- [ ] **Step 8: Commit**

```bash
git add templates/biblioteca.template.html
git commit -m "Add Guida/Biblioteca mode toggle and library shell skeleton"
```

---

### Task 3: Biblioteca — recitals and articles views

**Files:**
- Modify: `templates/biblioteca.template.html`

**Interfaces:**
- Consumes: `LIBRARY_DATA`, `CHAPTER_RANGES`, `chapterForArticle()` (Task 1);
  `state.mode`, `setMode()` (Task 2).
- Produces: `renderLibrary()`, `renderLibrarySidebar()`, `renderRecitalsView()`,
  `renderArticleView()`, `bindLibraryNav()` — all consumed by Task 4 (annexes/omnibus
  use the same `renderLibrary()` dispatcher) and Task 5 (cross-links call
  `setMode('library')` after setting `state.libSection`/`state.libArticle`).

- [ ] **Step 1: Add remaining UI strings**

Find (added in Task 2, inside `UI.it`):

```js
    modeGuide:'Guida', modeLibrary:'Biblioteca', searchLibPh:'Cerca nel testo integrale…',
```

Replace with:

```js
    modeGuide:'Guida', modeLibrary:'Biblioteca', searchLibPh:'Cerca nel testo integrale…',
    libRecitals:'Considerando', libRecital:'Considerando', libArticles:'Capi e Articoli', libAnnexes:'Allegati', libOmnibus:'Digital Omnibus 2026/1744',
    libRecitalsDesc:'I considerando espongono le motivazioni del legislatore. Non sono vincolanti, ma aiutano a interpretare gli articoli.',
    libPrev:'← Precedente', libNext:'Successivo →',
```

Find (added in Task 2, inside `UI.en`):

```js
    modeGuide:'Guide', modeLibrary:'Library', searchLibPh:'Search the full text…',
```

Replace with:

```js
    modeGuide:'Guide', modeLibrary:'Library', searchLibPh:'Search the full text…',
    libRecitals:'Recitals', libRecital:'Recital', libArticles:'Chapters and Articles', libAnnexes:'Annexes', libOmnibus:'Digital Omnibus 2026/1744',
    libRecitalsDesc:'Recitals set out the legislator’s reasoning. They are not binding, but help interpret the articles.',
    libPrev:'← Previous', libNext:'Next →',
```

- [ ] **Step 2: Add the library CSS block**

Add after the CSS added in Task 2 (`.search-result:hover{...}`):

```css
.lib-doc-head{margin-bottom:20px;}
.lib-doc-num{font-family:'IBM Plex Mono',monospace; color:var(--rubric); font-size:13px; margin-bottom:4px;}
.lib-doc-title{font-family:'Fraunces',serif; font-size:26px; margin:0; line-height:1.2;}
.lib-breadcrumb{font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--ink-faint); margin-bottom:14px; text-transform:uppercase; letter-spacing:.05em;}
.lib-doc-body{font-family:'Source Serif 4',Georgia,serif; font-size:15.5px; line-height:1.75; color:var(--ink);}
.lib-doc-body p.oj-normal{margin:0 0 12px;}
.lib-doc-body table{border-collapse:collapse; width:100%; margin:0 0 2px;}
.lib-doc-body table td{vertical-align:top; padding:0 0 10px;}
.lib-doc-body table td:first-child{width:36px; padding-right:8px; color:var(--rubric); font-family:'IBM Plex Mono',monospace; font-size:13px;}
.lib-doc-body table table{margin-left:22px;}
.lib-doc-body p.oj-ti-grseq-1{font-weight:600; margin:20px 0 10px; font-family:'Fraunces',serif; font-size:17px;}
.lib-doc-body p.oj-italic{font-style:italic;}
.lib-nav-btns{display:flex; justify-content:space-between; margin-top:36px; padding-top:20px; border-top:1px solid var(--rule);}
.lib-nav-btns button{padding:10px 18px; border:1px solid var(--ink); background:transparent; border-radius:2px; cursor:pointer; font-size:13px; font-family:'Inter',sans-serif; color:var(--ink);}
.lib-nav-btns button:hover:not(:disabled){background:var(--ink); color:var(--paper);}
.lib-nav-btns button:disabled{opacity:.3; cursor:default;}
.lib-accordion{display:flex; flex-direction:column; gap:1px; background:var(--rule); border:1px solid var(--rule); border-radius:3px; overflow:hidden;}
.lib-accordion-item{background:var(--card);}
.lib-accordion-item summary{padding:13px 18px; cursor:pointer; font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:var(--ink-soft); list-style:none;}
.lib-accordion-item summary::-webkit-details-marker{display:none;}
.lib-accordion-item summary::before{content:'+'; margin-right:8px; color:var(--rubric); font-weight:600;}
.lib-accordion-item[open] summary::before{content:'\2013';}
.lib-accordion-item .lib-doc-body{padding:0 18px 20px;}
.lib-chapter{margin-bottom:2px;}
.lib-chapter summary{cursor:pointer; padding:5px 7px; font-size:13px; color:var(--ink-soft); list-style:none; display:flex; gap:8px; align-items:baseline;}
.lib-chapter summary::-webkit-details-marker{display:none;}
.lib-chapter summary .n{font-family:'IBM Plex Mono',monospace; font-size:10.5px; color:var(--rubric); width:20px; flex:0 0 auto;}
.lib-chapter-arts{display:flex; flex-wrap:wrap; gap:4px; padding:6px 0 10px 28px;}
.lib-art-link{padding:3px 7px; border-radius:2px; font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--ink-soft); text-decoration:none; border:1px solid transparent;}
.lib-art-link:hover{background:var(--paper-2);}
.active-lib{background:var(--ink) !important; color:var(--paper) !important;}
.lib-note{background:var(--card); border:1px dashed var(--indigo); border-radius:3px; padding:14px 16px; font-size:13px; color:var(--ink-soft); margin-bottom:20px;}
```

Update the Google Fonts `@import` line (first line inside `<style>`) from:

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
```

to:

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');
```

- [ ] **Step 3: Add the render functions**

Add right before the `/* ============================= INIT & EVENTS ============================= */`
comment:

```js
/* ============================= LIBRARY ============================= */
function renderLibrarySidebar(){
  const L = UI[state.lang];
  const chapterGroups = CHAPTER_RANGES.map(r=>{
    const chap = CHAPTERS.find(c=>c.id===r.id);
    const isOpenChapter = state.libSection==='articles' && state.libArticle>=r.from && state.libArticle<=r.to;
    const nums = [];
    for(let n=r.from; n<=r.to; n++) nums.push(n);
    const links = nums.map(n=>`<a class="lib-art-link ${isOpenChapter && state.libArticle===n?'active-lib':''}" data-lib-article="${n}" href="#">${n}</a>`).join('');
    return `<details class="lib-chapter" ${isOpenChapter?'open':''}>
      <summary><span class="n">${chap.num}</span>${state.lang==='it'?chap.it:chap.en}</summary>
      <div class="lib-chapter-arts">${links}</div>
    </details>`;
  }).join('');
  document.getElementById('librarySidebar').innerHTML = `
    <div class="side-group">
      <a class="side-link ${state.libSection==='recitals'?'active-lib':''}" data-lib-section="recitals" href="#">${L.libRecitals}</a>
    </div>
    <div class="side-group">
      <div class="side-label">${L.libArticles}</div>
      ${chapterGroups}
    </div>
    <div class="side-group">
      <a class="side-link ${state.libSection==='annexes'?'active-lib':''}" data-lib-section="annexes" href="#">${L.libAnnexes}</a>
      <a class="side-link ${state.libSection==='omnibus'?'active-lib':''}" data-lib-section="omnibus" href="#">${L.libOmnibus}</a>
    </div>`;
  document.querySelectorAll('#librarySidebar [data-lib-section]').forEach(el=>{
    el.addEventListener('click', (e)=>{ e.preventDefault(); state.libSection = el.getAttribute('data-lib-section'); renderLibrary(); });
  });
  document.querySelectorAll('#librarySidebar [data-lib-article]').forEach(el=>{
    el.addEventListener('click', (e)=>{ e.preventDefault(); state.libSection='articles'; state.libArticle = parseInt(el.getAttribute('data-lib-article'),10); renderLibrary(); });
  });
}

function renderRecitalsView(){
  const L = UI[state.lang];
  const recitals = LIBRARY_DATA[state.lang].recitals;
  const items = recitals.map(r=>`
    <details class="lib-accordion-item" id="rec-${r.num}">
      <summary>${L.libRecital} ${r.num}</summary>
      <div class="lib-doc-body">${r.html}</div>
    </details>`).join('');
  return `
    <div class="block-head"><span class="block-num">§</span><h2>${L.libRecitals}</h2></div>
    <p class="block-desc">${L.libRecitalsDesc}</p>
    <div class="lib-accordion">${items}</div>`;
}

function renderArticleView(){
  const L = UI[state.lang];
  const arts = LIBRARY_DATA[state.lang].articles;
  const art = arts.find(a=>a.num===state.libArticle) || arts[0];
  const chap = chapterForArticle(art.num);
  const chapObj = CHAPTERS.find(c=>c.id===chap.id);
  const prevNum = art.num>1 ? art.num-1 : null;
  const nextNum = art.num<113 ? art.num+1 : null;
  return `
    <div class="lib-breadcrumb">${chap.num} — ${state.lang==='it'?chapObj.it:chapObj.en}</div>
    <div class="lib-doc-head">
      <div class="lib-doc-num">${state.lang==='it'?'Articolo':'Article'} ${art.num}</div>
      <h2 class="lib-doc-title">${art.title}</h2>
    </div>
    <div class="lib-doc-body">${art.html}</div>
    <div class="lib-nav-btns">
      <button ${prevNum?'':'disabled'} data-lib-article="${prevNum||''}">${L.libPrev}</button>
      <button ${nextNum?'':'disabled'} data-lib-article="${nextNum||''}">${L.libNext}</button>
    </div>`;
}

function bindLibraryNav(){
  document.querySelectorAll('#libraryMain [data-lib-article]').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const n = btn.getAttribute('data-lib-article');
      if(!n) return;
      state.libArticle = parseInt(n,10);
      renderLibrary();
      document.getElementById('libraryMain').scrollIntoView({behavior:'smooth', block:'start'});
    });
  });
}

function renderLibrary(){
  renderLibrarySidebar();
  const root = document.getElementById('libraryMain');
  if(state.libSection==='recitals') root.innerHTML = renderRecitalsView();
  else if(state.libSection==='articles') root.innerHTML = renderArticleView();
  else root.innerHTML = ''; // annexes/omnibus added in Task 4
  bindLibraryNav();
}
```

- [ ] **Step 4: Build and verify**

```bash
python tools/build.py
```

Open in the browser, switch to "BIBLIOTECA". Verify:
- Left sidebar shows "Considerando", 13 collapsible chapter groups under "Capi e
  Articoli" (numbered I–XIII with correct titles), "Allegati" and "Digital Omnibus
  2026/1744" links.
- Clicking "Considerando" shows 180 collapsed rows; expanding "Considerando 1" shows
  text starting with "Lo scopo del presente regolamento…" (IT) — switch to EN and
  confirm it now reads "The purpose of this Regulation…".
- Clicking article "5" under Capo II shows Article 5 with title "Pratiche di IA
  vietate" and body text containing "tecniche subliminali"; the Previous/Next buttons
  move to articles 4 and 6; Previous is disabled on article 1, Next is disabled on
  article 113.
- No console errors.

- [ ] **Step 5: Commit**

```bash
git add templates/biblioteca.template.html
git commit -m "Add Biblioteca recitals and articles reading views"
```

---

### Task 4: Biblioteca — annexes and Digital Omnibus views

**Files:**
- Modify: `templates/biblioteca.template.html`

**Interfaces:**
- Consumes: `LIBRARY_DATA`, `OMNIBUS_DATA`, `renderLibrary()` dispatcher (Task 3).
- Produces: `renderAnnexesView()`, `renderOmnibusView()`, wired into `renderLibrary()`.

- [ ] **Step 1: Add the Omnibus note strings**

Find (added in Task 3, inside `UI.it`):

```js
    libPrev:'← Precedente', libNext:'Successivo →',
```

Replace with:

```js
    libPrev:'← Precedente', libNext:'Successivo →',
    omnibusNote:'Il testo del Digital Omnibus (Regolamento (UE) 2026/1744) è riportato qui solo in inglese: la traduzione ufficiale italiana non risultava ancora pubblicata su EUR-Lex al momento della creazione di questa libreria.',
```

Find (added in Task 3, inside `UI.en`):

```js
    libPrev:'← Previous', libNext:'Next →',
```

Replace with:

```js
    libPrev:'← Previous', libNext:'Next →',
    omnibusNote:'The Digital Omnibus (Regulation (EU) 2026/1744) is shown here in English only: the official Italian translation was not yet published on EUR-Lex when this library was built.',
```

- [ ] **Step 2: Add the two render functions**

Find (added in Task 3):

```js
function renderLibrary(){
  renderLibrarySidebar();
  const root = document.getElementById('libraryMain');
  if(state.libSection==='recitals') root.innerHTML = renderRecitalsView();
  else if(state.libSection==='articles') root.innerHTML = renderArticleView();
  else root.innerHTML = ''; // annexes/omnibus added in Task 4
  bindLibraryNav();
}
```

Replace with:

```js
function renderAnnexesView(){
  const L = UI[state.lang];
  const annexes = LIBRARY_DATA[state.lang].annexes;
  const items = annexes.map(a=>`
    <details class="lib-accordion-item" id="anx-${a.num}">
      <summary>${state.lang==='it'?'Allegato':'Annex'} ${a.num} — ${a.title}</summary>
      <div class="lib-doc-body">${a.html}</div>
    </details>`).join('');
  return `
    <div class="block-head"><span class="block-num">§</span><h2>${L.libAnnexes}</h2></div>
    <div class="lib-accordion">${items}</div>`;
}

function renderOmnibusView(){
  const L = UI[state.lang];
  const arts = OMNIBUS_DATA.en.articles;
  const items = arts.map(a=>`
    <details class="lib-accordion-item" id="omnibus-${a.num}">
      <summary>Article ${a.num} — ${a.title}</summary>
      <div class="lib-doc-body">${a.html}</div>
    </details>`).join('');
  return `
    <div class="block-head"><span class="block-num">§</span><h2>${L.libOmnibus}</h2></div>
    <div class="lib-note">${L.omnibusNote}</div>
    <div class="lib-accordion">${items}</div>`;
}

function renderLibrary(){
  renderLibrarySidebar();
  const root = document.getElementById('libraryMain');
  if(state.libSection==='recitals') root.innerHTML = renderRecitalsView();
  else if(state.libSection==='articles') root.innerHTML = renderArticleView();
  else if(state.libSection==='annexes') root.innerHTML = renderAnnexesView();
  else if(state.libSection==='omnibus') root.innerHTML = renderOmnibusView();
  bindLibraryNav();
}
```

- [ ] **Step 3: Build and verify**

```bash
python tools/build.py
```

In the browser: click "Allegati" — verify 13 collapsible entries I–XIII, expanding
"Allegato III" shows text starting with "I sistemi di IA ad alto rischio…" (IT) and
containing the eight numbered areas (biometria, infrastrutture critiche, ecc.).
Click "Digital Omnibus 2026/1744" — verify the note banner is visible and 4 articles
are listed, all in English regardless of the IT/EN toggle state.

- [ ] **Step 4: Commit**

```bash
git add templates/biblioteca.template.html
git commit -m "Add Biblioteca annexes and Digital Omnibus views"
```

---

### Task 5: Cross-links from Guida article cards to the Biblioteca

**Files:**
- Modify: `templates/biblioteca.template.html`

**Interfaces:**
- Consumes: `setMode()` (Task 2), `state.libSection`/`state.libArticle` (Task 1).
- Produces: `.art-golib` buttons on every Guida article card whose `num` resolves to
  a real article number.

- [ ] **Step 1: Add the link label strings**

Find (added in Task 4, inside `UI.it`):

```js
    omnibusNote:'Il testo del Digital Omnibus (Regolamento (UE) 2026/1744) è riportato qui solo in inglese: la traduzione ufficiale italiana non risultava ancora pubblicata su EUR-Lex al momento della creazione di questa libreria.',
```

Replace with:

```js
    omnibusNote:'Il testo del Digital Omnibus (Regolamento (UE) 2026/1744) è riportato qui solo in inglese: la traduzione ufficiale italiana non risultava ancora pubblicata su EUR-Lex al momento della creazione di questa libreria.',
    goToText:'Testo integrale →',
```

Find (added in Task 4, inside `UI.en`):

```js
    omnibusNote:'The Digital Omnibus (Regulation (EU) 2026/1744) is shown here in English only: the official Italian translation was not yet published on EUR-Lex when this library was built.',
```

Replace with:

```js
    omnibusNote:'The Digital Omnibus (Regulation (EU) 2026/1744) is shown here in English only: the official Italian translation was not yet published on EUR-Lex when this library was built.',
    goToText:'Full text →',
```

- [ ] **Step 2: Add the button to the article-card template**

Find (inside `renderChapters()`):

```js
    const articles = c.articles.map(a=>`
      <div class="art-card" data-tags="${a.tags.join(' ')}" data-search="${(state.lang==='it'?a.it_t+' '+a.it_s:a.en_t+' '+a.en_s).toLowerCase()} ${a.num.toLowerCase()}">
        <div class="art-num">${a.num}</div>
        <div class="art-body">
          <div class="art-title">${state.lang==='it'?a.it_t:a.en_t}</div>
          <div class="art-summary">${state.lang==='it'?a.it_s:a.en_s}</div>
          <div class="art-tags">${a.tags.map(t=>`<span class="tag">${{provider:L.filterProvider,deployer:L.filterDeployer,importer:L.filterImporter,distributor:L.filterDistributor,gpai:L.filterGpai,governance:L.filterGov,general:L.filterGeneral}[t]}</span>`).join('')}</div>
        </div>
      </div>`).join('');
```

Replace with:

```js
    const articles = c.articles.map(a=>{
      const firstNum = parseInt(a.num, 10);
      const goLib = !isNaN(firstNum) ? `<button class="art-golib" data-golib="${firstNum}">${L.goToText}</button>` : '';
      return `
      <div class="art-card" data-tags="${a.tags.join(' ')}" data-search="${(state.lang==='it'?a.it_t+' '+a.it_s:a.en_t+' '+a.en_s).toLowerCase()} ${a.num.toLowerCase()}">
        <div class="art-num">${a.num}</div>
        <div class="art-body">
          <div class="art-title">${state.lang==='it'?a.it_t:a.en_t}</div>
          <div class="art-summary">${state.lang==='it'?a.it_s:a.en_s}</div>
          <div class="art-tags">${a.tags.map(t=>`<span class="tag">${{provider:L.filterProvider,deployer:L.filterDeployer,importer:L.filterImporter,distributor:L.filterDistributor,gpai:L.filterGpai,governance:L.filterGov,general:L.filterGeneral}[t]}</span>`).join('')}</div>
          ${goLib}
        </div>
      </div>`;
    }).join('');
```

- [ ] **Step 3: Add the CSS**

Add to the library CSS block (after `.lib-note{...}`):

```css
.art-golib{display:inline-block; margin-top:10px; padding:4px 10px; border:1px solid var(--rule); border-radius:20px; background:transparent; font-family:'IBM Plex Mono',monospace; font-size:10.5px; color:var(--rubric); cursor:pointer;}
.art-golib:hover{background:var(--rubric); color:#fff; border-color:var(--rubric);}
```

- [ ] **Step 4: Bind the click handler and call it from `renderMain`**

Find:

```js
function renderMain(){
  document.getElementById('main').innerHTML =
    renderHero() + renderTiers() + renderTimeline() + renderPenalties() +
    renderRoles() + renderClassify() + renderChapters() + renderAnnexes() + renderScenarios();
  renderClassifyBox();
  bindRoleTabs();
  bindFilterChips();
  applySearch();
}
```

Replace with:

```js
function renderMain(){
  document.getElementById('main').innerHTML =
    renderHero() + renderTiers() + renderTimeline() + renderPenalties() +
    renderRoles() + renderClassify() + renderChapters() + renderAnnexes() + renderScenarios();
  renderClassifyBox();
  bindRoleTabs();
  bindFilterChips();
  bindGoLib();
  applySearch();
}

function bindGoLib(){
  document.querySelectorAll('.art-golib').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const n = parseInt(btn.getAttribute('data-golib'),10);
      state.libSection = 'articles';
      state.libArticle = n;
      setMode('library');
      window.scrollTo({top:0, behavior:'smooth'});
    });
  });
}
```

- [ ] **Step 5: Build and verify**

```bash
python tools/build.py
```

In the browser, Guida mode: find the Article 5 card under "Capitoli e articoli" →
Capo II, click "Testo integrale →". Verify it switches to Biblioteca mode and opens
directly on Article 5. Try a grouped card too (e.g. the "28–39" notified-bodies card)
and verify it opens Article 28 (the first of the range).

- [ ] **Step 6: Commit**

```bash
git add templates/biblioteca.template.html
git commit -m "Add cross-links from Guida article cards to the Biblioteca"
```

---

### Task 6: Full-text search in the Biblioteca

**Files:**
- Modify: `templates/biblioteca.template.html`

**Interfaces:**
- Consumes: `LIBRARY_DATA`, `renderLibrary()`, `#searchResultsPanel` (Task 2).
- Produces: `applyLibrarySearch()`, `openLibraryResult(type, num, term)`,
  `highlightTerm(root, term)` — self-contained, nothing later depends on them.

- [ ] **Step 1: Route the search input by mode**

Find:

```js
document.getElementById('searchInput').addEventListener('input', (e)=>{
  state.query = e.target.value;
  applySearch();
});
```

Replace with:

```js
document.getElementById('searchInput').addEventListener('input', (e)=>{
  state.query = e.target.value;
  if(state.mode==='library') applyLibrarySearch(); else applySearch();
});
```

- [ ] **Step 2: Add the search-index and highlight functions**

Add right after `bindLibraryNav()` (defined in Task 3):

```js
let libSearchIndex = null;
function stripHtml(html){
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || '';
}
function buildLibSearchIndex(){
  libSearchIndex = {it:[], en:[]};
  ['it','en'].forEach(lang=>{
    const d = LIBRARY_DATA[lang];
    d.articles.forEach(a=>libSearchIndex[lang].push({type:'article', num:a.num, title:a.title, text:(a.title+' '+stripHtml(a.html)).toLowerCase()}));
    d.recitals.forEach(r=>libSearchIndex[lang].push({type:'recital', num:r.num, title:'', text:stripHtml(r.html).toLowerCase()}));
    d.annexes.forEach(a=>libSearchIndex[lang].push({type:'annex', num:a.num, title:a.title, text:(a.title+' '+stripHtml(a.html)).toLowerCase()}));
  });
}
function applyLibrarySearch(){
  const panel = document.getElementById('searchResultsPanel');
  const q = state.query.trim().toLowerCase();
  if(!q){ panel.classList.remove('show'); panel.innerHTML=''; document.getElementById('searchCount').textContent=''; return; }
  if(!libSearchIndex) buildLibSearchIndex();
  const matches = libSearchIndex[state.lang].filter(e=>e.text.includes(q)).slice(0,25);
  document.getElementById('searchCount').textContent = matches.length + ' ' + UI[state.lang].results;
  panel.innerHTML = matches.map(m=>{
    const label = m.type==='article' ? `${state.lang==='it'?'Art.':'Art.'} ${m.num} — ${m.title}` :
                  m.type==='recital' ? `${state.lang==='it'?'Considerando':'Recital'} ${m.num}` :
                  `${state.lang==='it'?'Allegato':'Annex'} ${m.num} — ${m.title}`;
    return `<button class="search-result" data-type="${m.type}" data-num="${m.num}">${label}</button>`;
  }).join('');
  panel.classList.toggle('show', matches.length>0);
  panel.querySelectorAll('.search-result').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      openLibraryResult(btn.getAttribute('data-type'), btn.getAttribute('data-num'), state.query.trim());
      panel.classList.remove('show');
    });
  });
}
function escapeHtml(s){
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function highlightTerm(root, term){
  if(!term) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const re = new RegExp('('+term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')', 'ig');
  const nodes = [];
  let n; while((n = walker.nextNode())) nodes.push(n);
  nodes.forEach(node=>{
    if(!re.test(node.nodeValue)) return;
    re.lastIndex = 0;
    const escaped = escapeHtml(node.nodeValue);
    const span = document.createElement('span');
    span.innerHTML = escaped.replace(re, '<mark>$1</mark>');
    node.parentNode.replaceChild(span, node);
  });
}
function openLibraryResult(type, num, term){
  if(type==='article'){ state.libSection='articles'; state.libArticle=parseInt(num,10); }
  else if(type==='annex'){ state.libSection='annexes'; }
  else if(type==='recital'){ state.libSection='recitals'; }
  renderLibrary();
  requestAnimationFrame(()=>{
    let target = null;
    if(type==='recital') target = document.getElementById('rec-'+num);
    if(type==='annex') target = document.getElementById('anx-'+num);
    if(target){ target.open = true; target.scrollIntoView({behavior:'smooth', block:'start'}); }
    if(term) highlightTerm(document.getElementById('libraryMain'), term);
  });
}
```

- [ ] **Step 3: Build and verify**

```bash
python tools/build.py
```

In the browser, switch to Biblioteca, type "sorveglianza umana" (IT) or "human
oversight" (EN) in the search box. Verify a dropdown appears listing several matches
(at least Article 14 and Article 26). Click a result: verify it opens the right
article/recital/annex and the matched phrase is wrapped in a highlighted `<mark>` in
the rendered text. Clear the search box and verify the dropdown closes.

- [ ] **Step 4: Commit**

```bash
git add templates/biblioteca.template.html
git commit -m "Add full-text search across the Biblioteca"
```

---

### Task 7: Sanctions bar chart in the Guida (salvaged from the vademecum)

**Files:**
- Modify: `templates/biblioteca.template.html`

**Interfaces:**
- Consumes: `PENALTIES` (existing data array), `state.lang`.
- Produces: `renderSanctionsChart()`, called from `renderPenalties()`.

- [ ] **Step 1: Add the render function**

Find:

```js
function renderPenalties(){
  const L = UI[state.lang];
  const cards = PENALTIES.map(p=>`
```

Add immediately before it:

```js
function renderSanctionsChart(){
  const max = 35000000;
  const rows = PENALTIES.map(p=>{
    const val = parseInt(p.amount.replace(/[^\d]/g,''),10);
    const widthPct = (val/max*100).toFixed(1);
    const label = state.lang==='it' ? p.n_it : p.n_en;
    const amount = state.lang==='it' ? p.amount : p.amountEn;
    return `<div class="sanc-row">
      <div class="sanc-label">${label}</div>
      <div class="sanc-bar-track"><div class="sanc-bar" style="width:${widthPct}%"></div></div>
      <div class="sanc-amount">${amount} <span class="sanc-pct">/ ${p.pct}</span></div>
    </div>`;
  }).join('');
  return `<div class="sanc-chart">${rows}</div>`;
}
```

- [ ] **Step 2: Call it from `renderPenalties()`**

Find:

```js
  return `
  <section class="block" id="penalties">
    <div class="block-head"><span class="block-num">${L.s3}</span><h2>${L.s3t}</h2></div>
    <p class="block-desc">${L.s3d}</p>
    <div class="pen-grid">${cards}</div>
```

Replace with:

```js
  return `
  <section class="block" id="penalties">
    <div class="block-head"><span class="block-num">${L.s3}</span><h2>${L.s3t}</h2></div>
    <p class="block-desc">${L.s3d}</p>
    ${renderSanctionsChart()}
    <div class="pen-grid">${cards}</div>
```

- [ ] **Step 3: Add the CSS**

Add to the CSS, after the `.art-golib:hover{...}` rule from Task 5:

```css
.sanc-chart{margin-bottom:26px; display:flex; flex-direction:column; gap:10px;}
.sanc-row{display:grid; grid-template-columns:220px 1fr 150px; align-items:center; gap:12px;}
.sanc-label{font-size:12px; color:var(--ink-soft);}
.sanc-bar-track{background:var(--paper-2); border-radius:20px; height:14px; overflow:hidden;}
.sanc-bar{height:100%; background:var(--rubric); border-radius:20px;}
.sanc-amount{font-family:'IBM Plex Mono',monospace; font-size:12px; text-align:right; white-space:nowrap;}
.sanc-pct{color:var(--ink-faint);}
@media (max-width:700px){ .sanc-row{grid-template-columns:1fr; gap:4px;} }
```

- [ ] **Step 4: Build and verify**

```bash
python tools/build.py
```

In the browser, Guida mode, scroll to "Sanzioni": verify three horizontal bars appear
above the existing penalty cards, proportional to 35M/15M/7.5M, each labelled with the
correct amount and percentage. Resize the window below 700px and confirm the rows
stack vertically without overlapping text.

- [ ] **Step 5: Commit**

```bash
git add templates/biblioteca.template.html
git commit -m "Add sanctions bar chart to the Guida penalties section"
```

---

### Task 8: Final integration pass

**Files:**
- Modify: `templates/biblioteca.template.html` (only if issues are found below)
- Verify: `ai-act-biblioteca.html` (generated)

**Interfaces:** none (this task only verifies end-to-end behaviour; it does not
introduce new functions).

- [ ] **Step 1: Full rebuild**

```bash
python tools/build.py
```

- [ ] **Step 2: Walk the whole app in the browser and check every item**

- IT/EN toggle: switch language while in Guida, then switch to Biblioteca — confirm
  the Biblioteca content (recitals/articles/annexes) is also in the new language, and
  the mode-toggle button labels ("Guida/Biblioteca" vs "Guide/Library") update too.
- Biblioteca → Guida → Biblioteca: confirm `state.libSection`/`state.libArticle` are
  preserved across the round trip (e.g. leave it open on Article 50, switch to Guida
  and back — it should still show Article 50).
- Deep-link round trip: from a Guida card, click "Testo integrale →" for at least one
  article in each of chapters III, V and XII (spanning the three penalty tiers) and
  confirm each opens the correct article.
- Search in both modes: a Guida-mode search still filters the summary cards as before
  (regression check); a Biblioteca-mode search returns results and opens them.
- Omnibus note is visible and only ever shown in English.
- No errors in the browser console across all of the above (check via
  `read_console_messages` if using the claude-in-chrome tool).
- Confirm final file size is reasonable: `ls -la ai-act-biblioteca.html` (~1.8–2.5 MB
  expected — flag if far outside this range, since that would indicate leftover
  duplicated data).

- [ ] **Step 3: Fix any issues found, rebuild, re-check**

If any check in Step 2 fails, fix the specific function in
`templates/biblioteca.template.html` (not the generated file), rebuild, and re-run
the full checklist from the top.

- [ ] **Step 4: Final commit**

```bash
git add templates/biblioteca.template.html ai-act-biblioteca.html
git commit -m "Finish AI Act Biblioteca: verified end-to-end IT/EN, Guida/Biblioteca, search and cross-links"
```

(As noted in Task 1, this project is not a git repository, so `git add`/`git commit`
steps throughout this plan are no-ops for now — just confirm the files are saved on
disk as the deliverable.)
