# himalay-cherukuri.github.io

Personal site of **Himalay Cherukuri**, served free by GitHub Pages at
<https://himalay-cherukuri.github.io>. It's plain static HTML, CSS and JS with no server, no framework
and no build step on GitHub. Everything you see is already committed.

## What's here

| Path | What it is |
|---|---|
| `index.html` | Personal home page: intro and the **Library**. The cards are generated from `assets/library.json`. |
| `arthashastra/` | Kautilya's *Arthashastra* (R. Shamasastry, 1915, public domain): 15 book pages, 150 chapter pages, an index of terms (1,848 term pages), search. |
| `assets/library.json` | The home-page Library. One book per line. |
| `assets/site.css`, `assets/site.js` | Shared, hand-written styles and behaviour: light/dark theme, mobile drawer, scroll-spy, copy-link, client-side search. |
| `*/search_index.json` | Prebuilt search index per section, loaded only when someone searches. |
| `tools/build.py` | The generator. It rebuilds every generated page from `_source/`. Uses only the Python 3 standard library. |
| `_source/arthashastra/` | `map.json` and `tags.json` from the Arthashastra breakdown pipeline, plus `DESIGN_SPEC.md`. |
| `404.html` | Not-found page. |
| `.nojekyll` | Tells GitHub Pages to serve files as-is (no Jekyll). |

## Rebuild

```bash
python3 tools/build.py            # regenerate index.html, 404.html, arthashastra/
python3 -m http.server 8000       # preview at http://localhost:8000
```

Then commit and push. GitHub Pages republishes within a minute or two.
Search needs the site served over http(s). Opening files straight from disk (`file://`) blocks the index fetch.

## Edit the home page intro

The intro text lives in `build_home()` in `tools/build.py`. Look for `EDIT ME`. Edit it there and rebuild,
so the next rebuild doesn't overwrite your change.

## Add a book to the Library

The home page lists whatever is in `assets/library.json`, in order. Each book is one line:

```json
{"title": "Title", "description": "One line about the book.", "href": "/path/to/the/book/"}
```

Add a line, then run `python3 tools/build.py` (or at least let `build_home()` rewrite `index.html`) and commit.
The card title, description, and link all come from that line.

## Add a new generated section (e.g. another book built from source)

1. Put the data in `_source/<key>/`. Any JSON or Markdown you like works.
2. In `tools/build.py`, write `build_<key>()`. Copy `build_arthashastra()` as a starting point. Use `page(...)` for the shared
   shell (header, sidebar, TOC, prev/next) and write a `search_index.json` of
   `{"h": title, "c": context, "t": text, "u": url-relative-to-section}` entries to get search for free.
3. Add `{"key": "<key>", "enabled": True}` to `SECTIONS`.
4. Add a line to `assets/library.json` so the book appears on the home page.
5. Run `python3 tools/build.py`, preview, commit.

To publish a plain page with no generator at all, drop an `.html` file anywhere. It's live on the next push.

## Public vs private

Everything in this repo is public, because GitHub Pages sites on a free account are public — including `_source/`.
Only put texts here that you have the right to publish. Keep private material in separate **private** repositories.
They never appear on the site.

## Notes on the texts

* Arthashastra page numbers (`p.N`) refer to the source PDF used by the breakdown pipeline.
