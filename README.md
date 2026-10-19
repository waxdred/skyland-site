# skyland-site

The website of [skyland](https://github.com/waxdred/skyland): https://waxdred.github.io/skyland-site/

Plain HTML and CSS, served by GitHub Pages as it is. Pages are written in `src/`
(content only); `tools/build.py` wraps them in the shared layout and writes the commands
reference from skyland's man pages:

```sh
python3 tools/build.py ../skyland   # path to a skyland checkout (its docs/aerospace-*.adoc)
python3 -m http.server 8765         # preview at http://localhost:8765
```

Commit the generated `index.html`, `install.html` and `docs/*.html` with their sources.
