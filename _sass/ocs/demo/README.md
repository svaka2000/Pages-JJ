# Demos

Two self-contained pages, built from the compiled design system. Open either
file directly in a browser -- they inline their own CSS, JS and logo, so they
need no server.

| File | What it shows |
|---|---|
| `component-reference.html` | Every component, every state, plus the measured contrast table |
| `lesson-page.html` | A realistic OCS lesson page built only from the system |

`lesson-page.html` is the one that matters: it is the proof that the tokens and
components compose into real UI rather than a swatch catalogue. Its only
page-level CSS is the three-column shell; everything visual comes from tokens.

## Rebuilding

These are generated. Regenerate after any change to the SCSS or to `ocs.js`:

```
sass --load-path=_sass --no-source-map <entry>.scss /tmp/ocs_full.css
python3 build_showcase.py
python3 build_lesson.py
```

The page stats (size, class count, `@import` count) are computed from the
compiled CSS at build time, so they cannot drift from what actually shipped.

## Palette provenance

`ramp.py`, `ramp2.py` and `fixtint.py` are the scripts that generated the
colour ramps and solved the semantic triplets. They are kept so the palette can
be re-derived rather than hand-edited -- which is exactly the failure mode that
left `_sass/root-color-map.scss` orphaned from a generator that no longer
exists.

`../tools/contrast.py` is the gate: it parses `_tokens.scss` and exits non-zero
if any contrast guarantee is violated.
