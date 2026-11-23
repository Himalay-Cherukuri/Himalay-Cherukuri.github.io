#!/usr/bin/env python3
"""
Static site generator for himalay-cherukuri.github.io

    python3 tools/build.py            # rebuild every section

Reads data from _source/<section>/ and writes plain HTML into the repo root:
    index.html, 404.html, arthashastra/**
Hand-written files (assets/site.css, assets/site.js, README.md) are never touched.
No dependencies beyond the Python 3 standard library.
"""
import json, re, shutil, sys, html, unicodedata
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_source"
OWNER = "Himalay Cherukuri"
GH_USER = "Himalay-Cherukuri"
YEAR = date.today().year
ASSET_VER = "2"

# ---------------------------------------------------------------- sections
# To add a section: write a build_<name>() below, append it here, and add a
# card in HOME_CARDS. 'enabled' False keeps it out of the generated site.
SECTIONS = [
    {"key": "arthashastra", "enabled": True},
]

def esc(s): return html.escape(str(s), quote=True)

def slugify(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = re.sub(r"[\u0300-\u036f]", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "term"

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

PAGES = {}
def count(sec): PAGES[sec] = PAGES.get(sec, 0) + 1

# ---------------------------------------------------------------- shell
def page(*, root, title, heading="", body_html, section="", secroot="", brand_sub="",
         sidebar="", toc="", breadcrumbs="", meta_line="", prev_link="", next_link="",
         page_type="page", search=True, description="", lang="en", search_extra=""):
    has_side = bool(sidebar)
    has_toc = bool(toc)
    shell_cls = "shell" + ("" if has_side else " no-side") + ("" if has_toc or not has_side else " no-toc")
    search_form = ""
    if search and section:
        search_form = (f'<form class="header-search" action="{secroot}search.html" role="search">'
                       f'<input type="search" name="q" placeholder="Search {esc(brand_sub)}…  ( / )" aria-label="Search {esc(brand_sub)}">{search_extra}</form>')
    brand = f'<a class="brand" href="{root}index.html">{OWNER}</a>'
    if brand_sub:
        brand += f'<span class="sep" aria-hidden="true">/</span><a class="brand" href="{secroot}index.html"><small style="margin:0">{esc(brand_sub)}</small></a>'
    menu = ('<button class="icon-btn menu-btn" id="menu-btn" aria-label="Open contents" aria-expanded="false" aria-controls="sidebar">☰</button>'
            if has_side else "")
    pagers = ""
    if prev_link or next_link:
        pagers = f'<nav class="pagers" aria-label="Previous and next">{prev_link or "<span></span>"}{next_link or "<span></span>"}</nav>'
    side = f'<aside class="sidebar" id="sidebar" aria-label="Contents">{sidebar}</aside><div class="backdrop"></div>' if has_side else ""
    tocc = f'<aside class="toc-col" aria-label="On this page"><h2>On this page</h2>{toc}</aside>' if has_toc else ""
    h1 = f"<h1>{heading}</h1>" if heading else ""
    meta = f'<p class="meta-line">{meta_line}</p>' if meta_line else ""
    desc = f'<meta name="description" content="{esc(description)}">' if description else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>{desc}
<script>try{{var t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t;else if(matchMedia("(prefers-color-scheme: dark)").matches)document.documentElement.dataset.theme="dark"}}catch(e){{}}</script>
<link rel="stylesheet" href="{root}assets/site.css?v={ASSET_VER}">
</head>
<body data-page-type="{page_type}" data-section="{section}" data-root="{root}" data-secroot="{secroot}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
{menu}{brand}
{search_form}
<button class="icon-btn" id="theme-toggle" aria-label="Toggle theme">☾</button>
</header>
<div class="{shell_cls}">
{side}
<main id="main" class="content" tabindex="-1">
<div class="reading">
{breadcrumbs}{h1}{meta}
{body_html}
{pagers}
</div>
</main>
{tocc}
</div>
<footer class="site-footer">© {YEAR} {OWNER} · <a href="{root}index.html">Home</a> · <a href="https://github.com/{GH_USER}">GitHub</a></footer>
<script src="{root}assets/site.js?v={ASSET_VER}" defer></script>
</body>
</html>
"""

def crumbs(items):
    out = []
    for i, (label, href) in enumerate(items):
        if i == len(items) - 1:
            out.append(f'<li aria-current="page">{label}</li>')
        else:
            out.append(f'<li><a href="{href}">{label}</a></li>')
    return '<ol class="breadcrumbs">' + "".join(out) + "</ol>"

def pager(cls, href, small, label):
    arrow_l, arrow_r = ("← ", "") if cls == "prev" else ("", " →")
    return f'<a class="pager {cls}" href="{href}" rel="{cls}"><small>{small}</small>{arrow_l}{label}{arrow_r}</a>'

def search_page(section, brand_sub, sidebar_fn, root, note=""):
    body = (f'<div class="search-page"><label for="q" class="meta-line" style="display:block">Search the full text{note}. Matching ignores case and diacritics; all words must match.</label>'
            f'<input id="q" type="search" autocomplete="off" placeholder="e.g. king, duty, surrender" autofocus>'
            f'<p class="search-status" id="search-status" aria-live="polite"></p><ul class="results" id="results"></ul></div>')
    return page(root=root, secroot="", section=section, brand_sub=brand_sub, title=f"Search · {brand_sub}",
                heading="Search", body_html=body, sidebar=sidebar_fn(""), page_type="search",
                breadcrumbs=crumbs([("Home", root + "index.html"), (brand_sub, "index.html"), ("Search", "")]))

# ================================================================ ARTHASHASTRA
def build_arthashastra():
    sec = "arthashastra"; OUT = ROOT / sec; NAME = "Arthashastra"
    data = json.loads((SRC / sec / "map.json").read_text(encoding="utf-8"))
    tags = json.loads((SRC / sec / "tags.json").read_text(encoding="utf-8"))
    books = data["books"]; counts = data["meta"]["counts"]

    def book_dir(b): return f'B{b["num"]:02d}_{b["slug"]}'
    def ch_file(c): return f'C{c["num"]:02d}_{c["slug"]}.html'
    chapters = [(b, c) for b in books for c in b["chapters"]]
    chapters.sort(key=lambda x: x[1]["global_seq"])
    para_info = {}
    for b, c in chapters:
        for t in c["topics"]:
            for p in t["paragraphs"]:
                para_info[p["id"]] = (b, c, p)

    # term slugs (unique per category)
    term_slug = {}
    for cat, terms in tags.items():
        used = set()
        for term in terms:
            s = slugify(term); base = s; n = 2
            while s in used: s = f"{base}-{n}"; n += 1
            used.add(s); term_slug[(cat, term)] = s

    def sidebar(sr, cur_book=None, cur_ch=None):
        out = [f'<a class="side-title" href="{sr}index.html">Kautilya’s Arthashastra</a><nav><ul class="tree">']
        for b in books:
            op = " is-open" if cur_book and b["id"] == cur_book else ""
            out.append(f'<li class="book{op}" data-id="{b["id"]}"><button type="button" aria-expanded="{"true" if op else "false"}">{b["roman"]} · {esc(b["title"])}</button><ul>')
            out.append(f'<li class="chapter{" is-current" if cur_book==b["id"] and not cur_ch else ""}"><a href="{sr}{book_dir(b)}/index.html">Book overview</a></li>')
            for c in b["chapters"]:
                cc = " is-current" if cur_ch == c["id"] else ""
                out.append(f'<li class="chapter{cc}"><a href="{sr}{book_dir(b)}/{ch_file(c)}">{c["roman"]} · {esc(c["title"])}</a></li>')
            out.append("</ul></li>")
        out.append(f'</ul></nav><p style="margin-top:1rem"><a href="{sr}tags/index.html">Index of terms</a> · <a href="{sr}search.html">Search</a></p>')
        return "".join(out)

    def chip(cat, term, sr, n=None):
        cnt = f" <span>{n}</span>" if n is not None else ""
        return f'<a class="chip chip--{cat}" href="{sr}tags/{cat}/{term_slug[(cat, term)]}.html">{esc(term)}{cnt}</a>'

    if OUT.exists(): shutil.rmtree(OUT)
    root = "../"
    # section home
    cards = []
    for b in books:
        cards.append(f'<a class="card" href="{book_dir(b)}/index.html"><div class="kicker">Book {b["roman"]}</div><h3>{esc(b["title"])}</h3>'
                     f'<div class="meta"><span>{len(b["chapters"])} chapters</span><span>pp. {b["page_start"]}–{b["page_end"]}</span></div></a>')
    cn = counts
    body = f"""<p>A study and reference edition of <em>Kautilya’s Arthashastra</em> in R. Shamasastry’s 1915 English translation (public domain).
The text is organised as <b>Book › Chapter › Topic › Paragraph</b>; every paragraph has a stable ID (e.g. <code>B01.C02.T1.P001</code>) you can link to or cite.
Hover a paragraph to see its tagged terms, or browse the <a href="tags/index.html">index of terms</a>.</p>
<div class="counts"><span><b>{cn['books']}</b> books</span><span><b>{cn['chapters']}</b> chapters</span><span><b>{cn['topics']}</b> topics</span><span><b>{cn['paragraphs']:,}</b> paragraphs</span><span><b>{cn['tag_terms']:,}</b> indexed terms</span></div>
<p class="meta-line">Keyboard: <kbd>/</kbd> search · <kbd>[</kbd> / <kbd>]</kbd> previous / next chapter.</p>
<div class="grid">{''.join(cards)}</div>"""
    write(OUT / "index.html", page(root=root, secroot="", section=sec, brand_sub=NAME, title="Kautilya’s Arthashastra · " + OWNER,
          heading="Kautilya’s Arthashastra", meta_line="Translated by R. Shamasastry (1915)", body_html=body,
          sidebar=sidebar(""), page_type="home", breadcrumbs=crumbs([("Home", "../index.html"), (NAME, "")]),
          description="Kautilya's Arthashastra, R. Shamasastry translation, browsable by book, chapter and topic.")); count(sec)

    # book pages
    for b in books:
        sr = "../"; root = "../../"
        lis = "".join(f'<li id="{c["id"]}"><span class="num">{c["roman"]}</span><a href="{ch_file(c)}">{esc(c["title"])}</a><span class="sub">{len(c["topics"])} topic{"s" if len(c["topics"])!=1 else ""} · pp. {c["page_start"]}–{c["page_end"]}</span></li>' for c in b["chapters"])
        toc = '<ul class="toc">' + "".join(f'<li><a href="#{c["id"]}">{c["roman"]} · {esc(c["title"])}</a></li>' for c in b["chapters"]) + "</ul>"
        bi = books.index(b)
        prev = pager("prev", f'{sr}{book_dir(books[bi-1])}/index.html', "Previous book", f'Book {books[bi-1]["roman"]}') if bi > 0 else ""
        nxt = pager("next", f'{sr}{book_dir(books[bi+1])}/index.html', "Next book", f'Book {books[bi+1]["roman"]}') if bi < len(books)-1 else ""
        write(OUT / book_dir(b) / "index.html", page(root=root, secroot=sr, section=sec, brand_sub=NAME,
              title=f'Book {b["roman"]}: {b["title"]} · Arthashastra', heading=f'Book {b["roman"]}: {esc(b["title"])}',
              meta_line=f'{b["id"]} · {len(b["chapters"])} chapters · pp. {b["page_start"]}–{b["page_end"]}',
              body_html=f'<ol class="list-plain">{lis}</ol>', sidebar=sidebar(sr, b["id"]), toc=toc, page_type="book",
              breadcrumbs=crumbs([("Home", root + "index.html"), (NAME, sr + "index.html"), (f'Book {b["roman"]}', "")]),
              prev_link=prev, next_link=nxt)); count(sec)

    # chapter pages
    for i, (b, c) in enumerate(chapters):
        sr = "../"; root = "../../"
        parts = []; agg = {}
        for t in c["topics"]:
            parts.append(f'<section class="topic" id="{t["id"]}"><h2>{esc(t["title"])}</h2>')
            for p in t["paragraphs"]:
                chips = []
                for cat, terms in (p.get("tags") or {}).items():
                    for term in terms:
                        if (cat, term) in term_slug:
                            chips.append(chip(cat, term, sr)); agg[(cat, term)] = agg.get((cat, term), 0) + 1
                chips_html = f'<span class="para-tags">{"".join(chips)}</span>' if chips else ""
                short = p["id"].rsplit(".", 1)[-1]
                parts.append(f'<p class="para para--{p["type"]}" id="{p["id"]}" data-page="{p["page_start"]}"><a class="para-id" href="#{p["id"]}" title="Copy link to {p["id"]}">{short}</a>'
                             f'{esc(p["text"])}<span class="para-page">p.{p["page_start"]}</span>{chips_html}</p>')
            parts.append("</section>")
        top = sorted(agg.items(), key=lambda kv: -kv[1])[:40]
        if top:
            parts.append('<div class="chapter-tags"><h3>Terms in this chapter</h3>' + "".join(chip(cat, term, sr, n) for (cat, term), n in top) + "</div>")
        toolbar = '<div class="toolbar"><button class="icon-btn" id="tags-toggle" aria-pressed="false">Show tags</button></div>'
        toc = '<ul class="toc">' + "".join(f'<li><a href="#{t["id"]}">{esc(t["title"])}</a></li>' for t in c["topics"]) + "</ul>"
        prev = nxt = ""
        if i > 0:
            pb, pc = chapters[i-1]; prev = pager("prev", f'{sr}{book_dir(pb)}/{ch_file(pc)}', f'Book {pb["roman"]} · Chapter {pc["roman"]}', esc(pc["title"]))
        if i < len(chapters)-1:
            nb, nc = chapters[i+1]; nxt = pager("next", f'{sr}{book_dir(nb)}/{ch_file(nc)}', f'Book {nb["roman"]} · Chapter {nc["roman"]}', esc(nc["title"]))
        write(OUT / book_dir(b) / ch_file(c), page(root=root, secroot=sr, section=sec, brand_sub=NAME,
              title=f'Chapter {c["roman"]}: {c["title"]} · Book {b["roman"]} · Arthashastra', heading=f'Chapter {c["roman"]}: {esc(c["title"])}',
              meta_line=f'{c["id"]} · Book {b["roman"]}: {esc(b["title"])} · p. {c["page_start"]}–{c["page_end"]}',
              body_html=toolbar + "".join(parts), sidebar=sidebar(sr, b["id"], c["id"]), toc=toc, page_type="chapter",
              breadcrumbs=crumbs([("Home", root + "index.html"), (NAME, sr + "index.html"), (f'Book {b["roman"]}', f"index.html"), (f'Chapter {c["roman"]}', "")]),
              prev_link=prev, next_link=nxt)); count(sec)

    # tags
    CAT_LABEL = {"office": "Offices & roles", "sanskrit": "Sanskrit terms", "number": "Numbers", "amount": "Amounts", "unit": "Units", "penalty": "Penalties"}
    blocks = []
    for cat, terms in tags.items():
        items = sorted(terms.items(), key=lambda kv: kv[0].lower())
        blocks.append(f'<section class="tag-cat" id="cat-{cat}"><h2>{CAT_LABEL.get(cat, cat.title())} <small class="meta-line">({len(items)})</small></h2>'
                      + "".join(chip(cat, term, "../", v["count"]) for term, v in items) + "</section>")
    toc = '<ul class="toc">' + "".join(f'<li><a href="#cat-{cat}">{CAT_LABEL.get(cat, cat)}</a></li>' for cat in tags) + "</ul>"
    write(OUT / "tags" / "index.html", page(root="../../", secroot="../", section=sec, brand_sub=NAME, title="Index of terms · Arthashastra",
          heading="Index of terms", meta_line=f"{sum(len(t) for t in tags.values()):,} terms in {len(tags)} categories", body_html="".join(blocks),
          sidebar=sidebar("../"), toc=toc, page_type="term",
          breadcrumbs=crumbs([("Home", "../../index.html"), (NAME, "../index.html"), ("Terms", "")]))); count(sec)
    for cat, terms in tags.items():
        for term, v in terms.items():
            sr = "../../"; root = "../../../"
            lis = []
            for pid in v["paragraphs"]:
                if pid not in para_info: continue
                b, c, p = para_info[pid]
                snip = p["text"][:220] + ("…" if len(p["text"]) > 220 else "")
                lis.append(f'<li><a href="{sr}{book_dir(b)}/{ch_file(c)}#{pid}">{pid}</a> <span class="sub">Book {b["roman"]} · {esc(c["title"])}</span><span class="snip">{esc(snip)}</span></li>')
            write(OUT / "tags" / cat / f"{term_slug[(cat, term)]}.html", page(root=root, secroot=sr, section=sec, brand_sub=NAME,
                  title=f"{term} · {CAT_LABEL.get(cat, cat)} · Arthashastra", heading=esc(term),
                  meta_line=f'{CAT_LABEL.get(cat, cat)} · appears {v["count"]} time{"s" if v["count"]!=1 else ""}',
                  body_html=f'<ul class="list-plain ref-list">{"".join(lis)}</ul>', page_type="term",
                  breadcrumbs=crumbs([("Home", root + "index.html"), (NAME, sr + "index.html"), ("Terms", sr + "tags/index.html"), (esc(term), "")]))); count(sec)

    # search
    write(OUT / "search.html", search_page(sec, NAME, sidebar, "../")); count(sec)
    idx = []
    for b, c in chapters:
        for t in c["topics"]:
            for p in t["paragraphs"]:
                idx.append({"id": p["id"], "h": f'{c["title"]} · {p["id"].rsplit(".",1)[-1]}', "c": f'Book {b["roman"]} · Ch. {c["roman"]} · {p["id"]}',
                            "t": p["text"], "u": f'{book_dir(b)}/{ch_file(c)}#{p["id"]}'})
    for cat, terms in tags.items():
        for term in terms:
            idx.insert(0, {"id": f"tag:{cat}:{term}", "k": "tag", "h": term, "c": f"Term · {CAT_LABEL.get(cat, cat)}", "t": term,
                           "u": f"tags/{cat}/{term_slug[(cat, term)]}.html"})
    write(OUT / "search_index.json", json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    return {"chapters": len(chapters), "books": len(books), "terms": sum(len(t) for t in tags.values())}

# ================================================================ HOME
HOME_CARDS = {
    "arthashastra": ('arthashastra/index.html', "Classical text", "Kautilya’s Arthashastra",
                     "The ancient Indian treatise on statecraft, economics and military strategy — R. Shamasastry’s 1915 translation, organised into 15 books, 150 chapters and 3,351 citable paragraphs with an index of terms.",
                     ["15 books", "150 chapters", "Index of terms"]),
}

def build_home(enabled):
    cards = []
    for key in enabled:
        href, kicker, title, desc, meta = HOME_CARDS[key]
        cards.append(f'<a class="card feature" href="{href}"><div class="kicker">{kicker}</div><h3>{title}</h3><p>{desc}</p>'
                     f'<div class="meta">{"".join(f"<span>{m}</span>" for m in meta)}</div></a>')
    body = f"""<div class="hero">
<h1>{OWNER}</h1>
<p class="lede">Welcome — this is my corner of the web. <!-- EDIT ME: replace this with a short intro about yourself --> I use it to publish things I’m reading, studying and building.</p>
</div>
<h2 class="section-title">Library</h2>
<div class="feature-grid">{''.join(cards)}</div>
<h2 class="section-title">Projects <a href="https://github.com/{GH_USER}?tab=repositories">All on GitHub →</a></h2>
<div class="grid" id="projects" data-user="{GH_USER}"><p>Loading public repositories…</p></div>
<noscript><p><a href="https://github.com/{GH_USER}?tab=repositories">See my repositories on GitHub</a>.</p></noscript>"""
    html_ = page(root="", title=OWNER, body_html=body, page_type="home", search=False,
                 description=f"{OWNER} — reading library and projects.")
    html_ = html_.replace('<div class="shell no-side">', '<div class="home">').replace('<div class="reading">', '<div>')
    write(ROOT / "index.html", html_); count("home")
    nf = page(root="/", title="Page not found · " + OWNER, heading="Page not found",
              body_html='<p>That page doesn’t exist (any more). Try the <a href="/index.html">home page</a>.</p>', search=False)
    write(ROOT / "404.html", nf); count("home")

if __name__ == "__main__":
    enabled = [s["key"] for s in SECTIONS if s["enabled"]]
    for s in SECTIONS:
        if not s["enabled"] and (ROOT / s["key"]).exists():
            shutil.rmtree(ROOT / s["key"]); print(f"removed disabled section {s['key']}/")
    stats = {}
    for key in enabled:
        stats[key] = globals()[f"build_{key}"]()
    build_home(enabled)
    print("pages written:", PAGES)
    print("stats:", stats)
