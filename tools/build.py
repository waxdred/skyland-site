#!/usr/bin/env python3
"""Builds the site: wraps each page of src/ in the shared layout, and writes the commands
reference from skyland's man pages (docs/aerospace-*.adoc in the skyland repo).

    python3 tools/build.py [path/to/skyland]     # default: ../skyland

The output (index.html, install.html, docs/*.html) is committed: GitHub Pages serves the
repo as it is, no build step there. A page in src/ starts with `<!-- title: ... -->` and
optionally `<!-- description: ... -->`; docs pages get the docs sidebar.
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKYLAND = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "skyland").resolve()
REPO = "https://github.com/waxdred/skyland"

DOCS_NAV = [
    ("Start", [("docs/index.html", "Overview"), ("install.html", "Install"), ("docs/coming-from-hyprland.html", "Coming from Hyprland")]),
    ("Use", [("docs/configuration.html", "Configuration"), ("docs/keybindings.html", "Keybindings"), ("docs/commands.html", "Commands")]),
    ("Ecosystem", [("docs/skylandbar.html", "skylandbar"), ("docs/cyberdeck.html", "cyberdeck")]),
    ("Reference", [("docs/compatibility.html", "Compatibility"), ("docs/troubleshooting.html", "Troubleshooting")]),
]


def layout(path: str, title: str, description: str, body: str) -> str:
    depth = path.count("/")
    up = "../" * depth
    is_docs = path.startswith("docs/") or path == "install.html"

    def nav_link(target: str, label: str, cls: str = "") -> str:
        active = " active" if target == path or (target == "docs/index.html" and path.startswith("docs/")) else ""
        return f'<a class="{cls}{active}" href="{up}{target}">{label}</a>'

    if is_docs:
        side = []
        for group, links in DOCS_NAV:
            side.append(f"<h4>{group}</h4>")
            side += [f'<a class="{"active" if t == path else ""}" href="{up}{t}">{label}</a>' for t, label in links]
        body = f'<div class="docs"><aside>{"".join(side)}</aside><article>{body}</article></div>'
    else:
        body = f"<main>{body}</main>"
    full_title = "skyland: Hyprland on macOS" if path == "index.html" else f"{title} · skyland"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="https://waxdred.github.io/skyland-site/assets/img/desktop-v3.jpg">
<meta name="theme-color" content="#181926">
<link rel="icon" href="{up}assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="{up}assets/site.css">
<script src="{up}assets/site.js"></script>
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="{up}index.html"><img src="{up}assets/img/icon.png" alt="">skyland</a>
<nav class="links">
{nav_link("index.html#features", "Features", "hide-sm")}
{nav_link("install.html", "Install")}
{nav_link("docs/index.html", "Docs")}
<a href="{REPO}">GitHub</a>
<button class="theme-toggle" type="button" aria-label="Light or dark">◐</button>
</nav>
</div></header>
{body}
<footer><div class="wrap">
<span>skyland is MIT licensed, a fork of <a href="https://github.com/nikitabobko/AeroSpace">AeroSpace</a>. Not affiliated with Apple or Hyprland.</span>
<span><a href="{REPO}">skyland</a> · <a href="https://github.com/waxdred/skylandBar">skylandbar</a> · <a href="https://github.com/waxdred/skyland-cyberdeck">cyberdeck</a> · <a href="{REPO}/releases">Releases</a></span>
</div></footer>
</body>
</html>
"""


# ---------------------------------------------------------------- commands from the man pages

def inline(text: str) -> str:
    """AsciiDoc inline markup we use: `code`, *bold*, _em_, links, {manpurpose}."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"(https?://[^\s\[]+)\[([^\]]*)\]", lambda m: f'<a href="{m[1]}">{m[2] or m[1]}</a>', text)
    text = re.sub(r"link:([^\s\[]+)\[([^\]]*)\]", lambda m: f'<a href="{m[1]}">{m[2]}</a>', text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"<em>\1</em>", text)
    return text


def body_html(lines: list[str]) -> str:
    """The body of a man page: paragraphs, `term::` definitions, ---- listings, * lists."""
    out, para, i = [], [], 0
    dl_open = False

    def flush():
        nonlocal para
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []

    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("//") or line.startswith("include::") or line.startswith(":") or line in ("[source]", "[verse]") or re.match(r"^\[source,.*\]$", line):
            i += 1
            continue
        if line in ("----", "...."):
            flush()
            block = []
            i += 1
            while i < len(lines) and lines[i].rstrip() != line:
                block.append(lines[i].rstrip("\n"))
                i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(block))}</code></pre>")
            i += 1
            continue
        m = re.match(r"^(.+?)::\s*(.*)$", line)
        if m and not line.startswith(" "):
            flush()
            if not dl_open:
                out.append("<dl>")
                dl_open = True
            out.append(f"<dt>{html.escape(m[1])}</dt>")
            desc = [m[2]] if m[2] else []
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^.+?::", lines[i]) and not lines[i].startswith("//"):
                desc.append(lines[i].strip())
                i += 1
            out.append(f"<dd>{inline(' '.join(desc))}</dd>")
            continue
        if dl_open and not line:
            # a blank line inside a definition list keeps it open until something else
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and re.match(r"^.+?::", lines[j]):
                i = j
                continue
            out.append("</dl>")
            dl_open = False
        if line.startswith("* "):
            flush()
            items = []
            while i < len(lines) and lines[i].startswith("* "):
                item = [lines[i][2:].strip()]
                i += 1
                # an item goes on over the next lines until a blank line or the next item
                while i < len(lines) and lines[i].strip() and not lines[i].startswith("* ") and not lines[i].startswith("//"):
                    item.append(lines[i].strip())
                    i += 1
                items.append(f"<li>{inline(' '.join(item))}</li>")
            out.append(f"<ul>{''.join(items)}</ul>")
            continue
        if not line:
            flush()
        elif line.startswith("== "):
            flush()
        else:
            para.append(line)
        i += 1
    flush()
    if dl_open:
        out.append("</dl>")
    return "\n".join(out)


def tagged(text: str, tag: str) -> list[str]:
    m = re.search(rf"// tag::{tag}\[\]\n(.*?)// end::{tag}\[\]", text, re.S)
    return m[1].splitlines() if m else []


def commands_page() -> str:
    pages = sorted(SKYLAND.glob("docs/aerospace-*.adoc"))
    if not pages:
        sys.exit(f"no man pages in {SKYLAND}/docs (pass the skyland repo path)")
    cards, index = [], []
    for page in pages:
        text = page.read_text()
        name = page.stem.removeprefix("aerospace-")
        purpose = next((l.split(":manpurpose:", 1)[1].strip() for l in tagged(text, "purpose") if ":manpurpose:" in l), "")
        synopsis = "\n".join(l for l in tagged(text, "synopsis") if l.strip()).replace("aerospace ", "skyland ")
        raw = body_html(tagged(text, "body"))
        # most bodies start with the purpose ({manpurpose}): shown once, under the synopsis
        lead = "" if "{manpurpose}" in raw else f'<p class="purpose">{inline(purpose)}</p>'
        body = raw.replace("{manpurpose}", inline(purpose))
        index.append(f'<a href="#{name}"><code>{name}</code></a>')
        cards.append(f'<section class="cmd card" id="{name}"><h3>{name}</h3>{lead}'
                     f'<pre><code>{html.escape(synopsis)}</code></pre>{body}</section>')
    return f"""<!-- title: Commands -->
<!-- description: Every skyland command: workspaces, layouts, windows, groups, scratchpads, overview, switcher, window rules. -->
<h1>Commands</h1>
<p>Every window manager command, as you call it from a shell, a script or a binding
(<code>alt-g = 'layout accordion'</code>). In a terminal, <code>skyland &lt;command&gt; --help</code> prints the same.
skyland keeps AeroSpace's commands and adds its own (master, overview, switcher, scratchpad, pin, window-rule, group-focus, settings...).</p>
<input id="command-filter" class="search" type="search" placeholder="Filter commands (name, option, word)">
<p style="line-height:2.1">{" ".join(index)}</p>
{"".join(cards)}
<p>Generated from <a href="{REPO}/tree/main/docs">the man pages in the skyland repo</a>.</p>
"""


# ---------------------------------------------------------------- pages

def build():
    sources = {p.relative_to(ROOT / "src").as_posix(): p.read_text() for p in (ROOT / "src").rglob("*.html")}
    sources["docs/commands.html"] = commands_page()
    for path, text in sorted(sources.items()):
        title = re.search(r"<!-- title: (.*?) -->", text)
        description = re.search(r"<!-- description: (.*?) -->", text)
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(layout(path, title[1] if title else "skyland",
                              description[1] if description else "A Hyprland-like tiling window manager for macOS.", text))
        print("wrote", path)


build()
