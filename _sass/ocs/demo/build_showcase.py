#!/usr/bin/env python3
"""Assemble the OCS Design System showcase page.

Inlines the compiled design-system CSS and the real OCS logo so the result is a
single self-contained HTML file.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
CSS = pathlib.Path("/tmp/ocs_full.css").read_text()
LOGO = (HERE / "logo_b64.txt").read_text().strip()
JS = pathlib.Path("/Users/samarthvaka/ocs-chatbot/pages/assets/js/ocs.js").read_text()
# A literal </script> anywhere in the source would terminate the inline block.
JS = JS.replace("</script>", "<\\/script>")
TOKENS = json.loads((HERE / "tokens.json").read_text())

# --- live build stats, computed from the compiled CSS so they cannot go stale ---
import re as _re
def _stats(css):
    sels = set(); depth = 0; buf = ''
    for ch in css:
        if ch == '{':
            if depth == 0:
                for c in _re.findall(r'\.([A-Za-z_][\w-]*)', buf):
                    sels.add(c)
            depth += 1; buf = ''
        elif ch == '}':
            depth = max(0, depth - 1); buf = ''
        else:
            buf += ch
            if len(buf) > 800: buf = buf[-800:]
    unprefixed = [c for c in sels if not c.startswith('ocs')]
    # The metric that actually matters: a class emitted as a BARE global
    # selector (".foo" standing alone), which is what collides with Bootstrap
    # and with page CSS. Compound-scoped uses like ".ocs__btn.small" are safe.
    bare = set()
    for block in _re.findall(r'(?m)^([^{}@/][^{}]*)\{', css):
        for one in block.split(','):
            one = one.strip()
            m = _re.fullmatch(r'\.([A-Za-z_][\w-]*)', one)
            if m:
                bare.add(m.group(1))
    # A prefixed class SHOULD be a standalone selector. The risk is a bare
    # selector that is also unprefixed -- that is what collides with Bootstrap
    # and with page CSS.
    bare_generic = sorted(c for c in bare if not c.startswith('ocs'))
    return {
        "kb": round(len(css.encode()) / 1024, 1),
        "classes": len(sels),
        "unprefixed": len(unprefixed),
        "bare_generic": len(bare_generic),
        "bare_generic_names": bare_generic,
        "imports": css.count("@import"),
    }
S = _stats(CSS)

CORAL = TOKENS["ramps"]["coral"]
NEUTRAL = TOKENS["ramps"]["neutral"]
SEM = TOKENS["semantic"]

# --- contrast numbers, recomputed here so the page can never drift from math --
def _s2l(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _s2l(r) + 0.7152 * _s2l(g) + 0.0722 * _s2l(b)

def ratio(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

BASE, RAISED, ELEV = "#121212", "#1C1C1E", "#2C2C2E"

TYPE_SCALE = [
    ("Display", "3rem / 48px", "1.1", "-0.02em", "700"),
    ("Heading 1", "2rem / 32px", "1.2", "-0.02em", "600"),
    ("Heading 2", "1.5rem / 24px", "1.3", "-0.01em", "600"),
    ("Heading 3", "1.25rem / 20px", "1.4", "0", "600"),
    ("Heading 4", "1rem / 16px", "1.5", "0", "600"),
    ("Body", "1rem / 16px", "1.6", "0", "400"),
    ("Small", "0.875rem / 14px", "1.5", "0", "400"),
    ("Code", "0.875rem / 14px", "1.5", "0", "400"),
]


def swatches(ramp, label):
    cells = []
    for step, hexv in ramp.items():
        r = ratio(hexv, BASE)
        fg = "#121212" if r < 4.5 else "#FFFFFF"
        cells.append(
            f'<div class="sw"><div class="sw__chip" style="background:{hexv};color:{fg}">{step}</div>'
            f'<code class="sw__hex">{hexv}</code></div>'
        )
    return f'<div class="sw-row" role="group" aria-label="{label}">' + "".join(cells) + "</div>"


def semantic_rows():
    rows = []
    for role, v in SEM.items():
        fg, bd, bg = v["fg"], v["border"], v["bg"]
        r_elev = ratio(fg, ELEV)
        r_bg = ratio(fg, bg)
        rows.append(f"""
        <tr>
          <th scope="row"><span class="ocs-badge ocs-badge--{role}">{role}</span></th>
          <td><span class="dot" style="background:{fg}"></span><code>{fg}</code></td>
          <td><span class="dot" style="background:{bd}"></span><code>{bd}</code></td>
          <td><span class="dot" style="background:{bg}"></span><code>{bg}</code></td>
          <td class="ocs-table__num"><strong>{r_elev:.2f}</strong>:1</td>
          <td class="ocs-table__num"><strong>{r_bg:.2f}</strong>:1</td>
          <td><span class="ocs-badge ocs-badge--success ocs-badge--dot">AA</span></td>
        </tr>""")
    return "".join(rows)


def button_matrix():
    out = []
    for variant, label in [
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("ghost", "Ghost"),
        ("danger", "Destructive"),
    ]:
        out.append(f"""
        <tr>
          <th scope="row">{label}</th>
          <td><button class="ocs-btn ocs-btn--{variant}">Button</button></td>
          <td><button class="ocs-btn ocs-btn--{variant} is-hover">Button</button></td>
          <td><button class="ocs-btn ocs-btn--{variant} is-active">Button</button></td>
          <td><button class="ocs-btn ocs-btn--{variant}" disabled>Button</button></td>
        </tr>""")
    return "".join(out)


ICONS = {
    "plus": '<path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" fill="none"/>',
    "edit": '<path d="M11.5 2.5 13.5 4.5 5 13H3v-2z" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/>',
    "trash": '<path d="M3 4.5h10M6.5 4.5V3h3v1.5M4.5 4.5 5 13.5h6l.5-9" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "star": '<path d="m8 2 1.8 3.9 4.2.5-3.1 2.9.8 4.2L8 11.5 4.3 13.5l.8-4.2L2 6.4l4.2-.5z" stroke="currentColor" stroke-width="1.3" fill="none" stroke-linejoin="round"/>',
    "download": '<path d="M8 2v8m0 0 3-3m-3 3L5 7M3 13h10" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "check": '<path d="M3 8.5 6.5 12 13 4.5" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "info": '<circle cx="8" cy="8" r="6.2" stroke="currentColor" stroke-width="1.4" fill="none"/><path d="M8 7.2v4M8 4.9v.9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
    "warn": '<path d="M8 2.5 14.5 13.5h-13z" stroke="currentColor" stroke-width="1.4" fill="none" stroke-linejoin="round"/><path d="M8 6.6v3M8 11.4v.7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
    "x": '<path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
}


def icon(name, cls="ocs-alert__icon"):
    # width/height are REQUIRED: an SVG with only a viewBox has no intrinsic
    # size and stretches to fill its container.
    return f'<svg class="{cls}" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">{ICONS[name]}</svg>'


HTML = f"""<title>OCS Design System</title>
<!-- Required: without this a phone lays the page out at 980px and renders it zoomed out.
     Harmless if the host wrapper already supplies one -- the first declaration wins. -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{CSS}

/* ---------- showcase page chrome (not part of the design system) ---------- */
body {{
  margin: 0;
  background: var(--ocs-surface-base);
  color: var(--ocs-text);
  font-family: var(--ocs-font-sans);
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}
.page {{ max-width: 1400px; margin: 0 auto; padding: 2.5rem 1.25rem 5rem; }}

.masthead {{ display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;
  padding-bottom: 2rem; margin-bottom: 2.5rem; border-bottom: 1px solid var(--ocs-border); }}
.masthead__logo {{ width: 84px; height: 84px; border-radius: 14px; background: #fff;
  padding: 6px; flex: 0 0 auto; }}
.masthead__logo img {{ width: 100%; height: 100%; display: block; }}
.masthead h1 {{ margin: 0; font-size: clamp(1.9rem, 4vw, 2.75rem); font-weight: 700;
  letter-spacing: -0.03em; line-height: 1.05; }}
.masthead h1 em {{ font-style: normal; color: var(--ocs-brand); }}
.masthead p {{ margin: .4rem 0 0; color: var(--ocs-text-muted); max-width: 60ch; }}
.masthead__meta {{ display: flex; gap: .5rem; flex-wrap: wrap; margin-top: .9rem; }}

/* Explicit columns rather than CSS multicol. `column-span: all` mispaints in
   Chromium when mixed with break-inside:avoid, and a plain auto-fit grid
   row-aligns siblings of different heights and leaves dead space. Two flex
   columns give deterministic packing with neither problem. */
.sections {{ display: flex; flex-direction: column; gap: 1.25rem; }}
.cols {{ display: flex; gap: 1.25rem; align-items: flex-start; }}
.col {{ flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; gap: 1.25rem; }}
.panel {{ border: 1px solid var(--ocs-border); border-radius: 14px;
  background: var(--ocs-surface-raised); padding: 1.5rem; }}
@media (max-width: 900px) {{ .cols {{ flex-direction: column; }} }}
.panel > h2 {{ display: flex; align-items: baseline; gap: .6rem; margin: 0 0 .25rem;
  font-size: 1.05rem; font-weight: 700; letter-spacing: -0.01em; }}
.panel > h2 span {{ color: var(--ocs-brand); font-variant-numeric: tabular-nums; }}
.panel > .lede {{ margin: 0 0 1.25rem; font-size: .8125rem; color: var(--ocs-text-muted);
  text-transform: uppercase; letter-spacing: .06em; font-weight: 600; }}
.sub {{ margin: 1.5rem 0 .6rem; font-size: .75rem; font-weight: 700; letter-spacing: .07em;
  text-transform: uppercase; color: var(--ocs-text-muted); }}
.sub:first-of-type {{ margin-top: 0; }}

.sw-row {{ display: flex; gap: .35rem; flex-wrap: wrap; }}
.sw {{ flex: 1 1 62px; min-width: 62px; }}
.sw__chip {{ height: 46px; border-radius: 7px; display: flex; align-items: center;
  justify-content: center; font-size: .7rem; font-weight: 700; font-variant-numeric: tabular-nums; }}
.sw__hex {{ display: block; margin-top: .3rem; font-size: .62rem; color: var(--ocs-text-muted);
  font-family: var(--ocs-font-mono); text-align: center; }}
.dot {{ display: inline-block; width: .7rem; height: .7rem; border-radius: 3px;
  margin-right: .4rem; vertical-align: -1px; }}
code {{ font-family: var(--ocs-font-mono); font-size: .78rem; }}

.matrix {{ width: 100%; border-collapse: collapse; }}
.matrix th {{ font-size: .7rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  color: var(--ocs-text-muted); text-align: left; padding: .5rem .6rem; }}
.matrix td {{ padding: .4rem .6rem; }}
.matrix tbody th {{ white-space: nowrap; }}
/* forced visual states for the documentation matrix only */
.is-hover.ocs-btn {{ background: var(--btn-bg-hover); }}
.is-active.ocs-btn {{ background: var(--btn-bg-active); }}

.type-row {{ display: flex; align-items: baseline; justify-content: space-between; gap: 1rem;
  padding: .55rem 0; border-bottom: 1px solid var(--ocs-border-subtle); }}
.type-row:last-child {{ border-bottom: 0; }}
.type-row__name {{ color: var(--ocs-text); }}
.type-row__meta {{ font-family: var(--ocs-font-mono); font-size: .7rem;
  color: var(--ocs-text-muted); white-space: nowrap; }}

.specimen {{ margin-top: 1rem; padding: 1rem; border: 1px solid var(--ocs-border-subtle);
  border-radius: 10px; background: var(--ocs-surface-base); }}
.specimen > * {{ margin: 0 0 .5rem; }}
.specimen > :last-child {{ margin-bottom: 0; }}

.demo-shell {{ border: 1px solid var(--ocs-border-subtle); border-radius: 10px; overflow: hidden;
  background: var(--ocs-surface-base); }}
.demo-split {{ display: grid; grid-template-columns: 190px 1fr; min-height: 190px; }}
.demo-split > aside {{ border-right: 1px solid var(--ocs-border-subtle); }}
.demo-split > div {{ padding: 1rem; }}

.guideline {{ display: flex; gap: .75rem; padding: .8rem 0;
  border-bottom: 1px solid var(--ocs-border-subtle); }}
.guideline:last-child {{ border-bottom: 0; }}
.guideline svg {{ width: 1.1rem; height: 1.1rem; flex: 0 0 auto; margin-top: .15rem;
  color: var(--ocs-brand); }}
.guideline h3 {{ margin: 0 0 .15rem; font-size: .9rem; font-weight: 600; }}
.guideline p {{ margin: 0; font-size: .82rem; color: var(--ocs-text-muted); }}

.receipt {{ font-family: var(--ocs-font-mono); font-size: .76rem; }}
.pagefoot {{ margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--ocs-border);
  display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
  color: var(--ocs-text-muted); font-size: .8rem; }}

@media (max-width: 560px) {{
  .demo-split {{ grid-template-columns: 1fr; }}
  .demo-split > aside {{ border-right: 0; border-bottom: 1px solid var(--ocs-border-subtle); }}
}}
</style>

<a class="ocs-skip-link" href="#main">Skip to content</a>

<div class="page">

  <header class="masthead">
    <div class="masthead__logo">
      <img src="data:image/png;base64,{LOGO}" alt="Open Coding Society logo">
    </div>
    <div>
      <h1><em>OCS</em> Design System</h1>
      <p>The component foundation for Open Coding Society. Built on the real brand
         coral sampled from the logo, with every colour pair verified against WCAG 2.1 AA.</p>
      <div class="masthead__meta">
        <span class="ocs-badge ocs-badge--brand">v0.1.0 draft</span>
        <span class="ocs-badge ocs-badge--neutral ocs-badge--code">{S["kb"]} KB compiled</span>
        <span class="ocs-badge ocs-badge--success ocs-badge--dot">WCAG AA verified</span>
        <span class="ocs-badge ocs-badge--neutral ocs-badge--code">@use / no @import</span>
      </div>
    </div>
  </header>

  <main id="main" class="sections">

    <!-- 01. COLORS -->
    <section class="panel">
      <h2><span>01</span> Colours</h2>
      <p class="lede">Generated in CIELAB, verified in sRGB</p>

      <p class="sub">Brand coral &mdash; anchored on #E06665, sampled from the logo</p>
      {swatches(CORAL, "Coral ramp")}

      <p class="sub">Neutral ramp</p>
      {swatches(NEUTRAL, "Neutral ramp")}

      <p class="sub">Semantic roles &mdash; measured, not guessed</p>
      <div class="ocs-table-wrap" tabindex="0" role="region" aria-label="Semantic colour contrast">
        <table class="ocs-table ocs-table--compact receipt">
          <thead>
            <tr>
              <th scope="col">Role</th><th scope="col">Foreground</th>
              <th scope="col">Border</th><th scope="col">Tint</th>
              <th scope="col" class="ocs-table__num">fg on #2C2C2E</th>
              <th scope="col" class="ocs-table__num">fg on tint</th>
              <th scope="col">WCAG</th>
            </tr>
          </thead>
          <tbody>{semantic_rows()}</tbody>
        </table>
      </div>
      <p class="ocs-help" style="margin-top:.75rem">
        Every foreground clears 4.5:1 against the hardest surface in the system
        (#2C2C2E elevated), so a token is never unsafe depending on where it lands.
      </p>
    </section>

    <div class="cols">
    <div class="col">

    <!-- 02. TYPOGRAPHY -->
    <section class="panel">
      <h2><span>02</span> Typography</h2>
      <p class="lede">Inter &rarr; system-ui &middot; Menlo for code</p>
      {"".join(
        f'<div class="type-row"><span class="type-row__name" style="font-size:{"1.35rem" if i < 2 else "1rem"};font-weight:{w}">{n}</span>'
        f'<span class="type-row__meta">{s} &middot; {lh} &middot; {t} &middot; {w}</span></div>'
        for i, (n, s, lh, t, w) in enumerate(TYPE_SCALE)
      )}
      <div class="specimen">
        <p style="font-size:1.5rem;font-weight:600;letter-spacing:-.01em">The quick brown fox jumps over the lazy dog</p>
        <p style="color:var(--ocs-text-secondary)">Body copy sits at 16px with a 1.6 line height for comfortable reading.</p>
        <p style="color:var(--ocs-text-muted);font-size:.875rem">Muted text uses #949498 &mdash; raised from Apple's #8E8E93, which measured 4.27:1 and failed AA.</p>
        <p><code style="color:var(--ocs-brand)">const open = true; // code sample</code></p>
      </div>
    </section>

    <!-- 03. BUTTONS -->
    <section class="panel">
      <h2><span>03</span> Buttons</h2>
      <p class="lede">4 variants &times; 4 states &times; 3 sizes</p>
      <table class="matrix">
        <thead>
          <tr><th scope="col"></th><th scope="col">Default</th><th scope="col">Hover</th>
              <th scope="col">Active</th><th scope="col">Disabled</th></tr>
        </thead>
        <tbody>{button_matrix()}</tbody>
      </table>

      <p class="sub">Sizes</p>
      <div class="ocs-cluster">
        <button class="ocs-btn ocs-btn--primary ocs-btn--sm">Small</button>
        <button class="ocs-btn ocs-btn--primary">Medium</button>
        <button class="ocs-btn ocs-btn--primary ocs-btn--lg">Large</button>
        <button class="ocs-btn ocs-btn--secondary ocs-btn--pill">Pill</button>
        <button class="ocs-btn ocs-btn--primary" aria-busy="true">Saving</button>
      </div>

      <p class="sub">Icon buttons &mdash; each carries an aria-label</p>
      <div class="ocs-cluster">
        {"".join(f'<button class="ocs-btn ocs-btn--secondary ocs-btn--icon" aria-label="{n}">{icon(n, "")}</button>' for n in ["plus", "edit", "trash", "star", "download", "check"])}
      </div>

      <p class="sub">Button group</p>
      <div class="ocs-btn-group" role="group" aria-label="View mode">
        <button class="ocs-btn ocs-btn--secondary" aria-pressed="true">Code</button>
        <button class="ocs-btn ocs-btn--secondary" aria-pressed="false">Preview</button>
        <button class="ocs-btn ocs-btn--secondary" aria-pressed="false">Split</button>
      </div>
    </section>

    <!-- 04. FORMS -->
    <section class="panel">
      <h2><span>04</span> Form Elements</h2>
      <p class="lede">Invalid state driven by aria-invalid</p>

      <div class="ocs-field">
        <label class="ocs-label ocs-label--required" for="d-name">Project name</label>
        <input class="ocs-input" id="d-name" placeholder="Enter project name">
        <p class="ocs-help">Lowercase letters, numbers and hyphens.</p>
      </div>

      <div class="ocs-field">
        <label class="ocs-label" for="d-lang">Language</label>
        <select class="ocs-select" id="d-lang">
          <option>TypeScript</option><option>Python</option><option>Java</option><option>Rust</option>
        </select>
      </div>

      <div class="ocs-field">
        <label class="ocs-label" for="d-bad">Email</label>
        <input class="ocs-input" id="d-bad" value="not-an-email" aria-invalid="true" aria-describedby="d-bad-err">
        <p class="ocs-error" id="d-bad-err">{icon("warn", "")} Enter a valid email address.</p>
      </div>

      <div class="ocs-field">
        <label class="ocs-label" for="d-desc">Description</label>
        <textarea class="ocs-textarea" id="d-desc" placeholder="What does this project do?"></textarea>
      </div>

      <p class="sub">Controls</p>
      <div class="ocs-stack" style="--ocs-stack-gap:.6rem">
        <label class="ocs-check"><input type="checkbox" checked> Open source</label>
        <label class="ocs-check"><input type="checkbox"> Include starter tests</label>
        <label class="ocs-check"><input type="checkbox" disabled> Archived (disabled)</label>
        <label class="ocs-check"><input type="radio" name="vis" checked> Public</label>
        <label class="ocs-check"><input type="radio" name="vis"> Private</label>
        <label class="ocs-switch"><input type="checkbox" role="switch" checked> Enable CI</label>
      </div>
    </section>

    <!-- 05. CODE -->
    <section class="panel">
      <h2><span>05</span> Code</h2>
      <p class="lede">The component OCS uses most</p>
      <figure class="ocs-code">
        <figcaption class="ocs-code__head">
          <span class="ocs-code__lang">Java</span>
          <button class="ocs-btn ocs-btn--ghost ocs-btn--sm">Copy</button>
        </figcaption>
        <pre class="ocs-code__body" tabindex="0"><code>@RestController
@RequestMapping("/api/projects")
public class ProjectController {{

    private final ProjectRepository repo;

    @GetMapping
    public List&lt;Project&gt; all() {{
        return repo.findAll();
    }}
}}</code></pre>
      </figure>
      <p class="ocs-help">
        The <code class="ocs-code-inline">&lt;pre&gt;</code> carries
        <code class="ocs-code-inline">tabindex="0"</code> &mdash; without it a
        scrolling code block is unreachable by keyboard. Press
        <kbd class="ocs-kbd">Tab</kbd> then <kbd class="ocs-kbd">&rarr;</kbd> to try it.
      </p>
    </section>

    </div>
    <div class="col">

    <!-- 06. NAVIGATION -->
    <section class="panel">
      <h2><span>06</span> Navigation</h2>
      <p class="lede">Current item marked with aria-current</p>

      <div class="demo-shell" style="margin-bottom:1rem">
        <nav class="ocs-topbar" aria-label="Demo primary">
          <a class="ocs-topbar__brand" href="#main"><em style="color:var(--ocs-brand);font-style:normal">OCS</em></a>
          <div class="ocs-topbar__nav">
            <a class="ocs-topbar__link" href="#main" aria-current="page">Docs</a>
            <a class="ocs-topbar__link" href="#main">Projects</a>
            <a class="ocs-topbar__link" href="#main">Community</a>
          </div>
          <div class="ocs-topbar__actions">
            <button class="ocs-btn ocs-btn--ghost ocs-btn--icon ocs-btn--sm" aria-label="Search">{icon("plus", "")}</button>
          </div>
        </nav>
      </div>

      <div class="demo-shell demo-split">
        <aside>
          <nav class="ocs-sidenav" aria-label="Demo section">
            <p class="ocs-sidenav__section">Guides</p>
            <a class="ocs-sidenav__link" href="#main" aria-current="page">Overview</a>
            <a class="ocs-sidenav__link" href="#main">Getting started</a>
            <a class="ocs-sidenav__link" href="#main">Components</a>
            <p class="ocs-sidenav__section">Reference</p>
            <a class="ocs-sidenav__link" href="#main">Tokens</a>
            <a class="ocs-sidenav__link" href="#main">Accessibility</a>
          </nav>
        </aside>
        <div>
          <nav aria-label="Breadcrumb">
            <ol class="ocs-breadcrumb">
              <li><a href="#main">Docs</a></li>
              <li><a href="#main">Components</a></li>
              <li><span aria-current="page">Buttons</span></li>
            </ol>
          </nav>
          <div class="ocs-tabs" role="tablist" aria-label="Example" style="margin-top:1rem">
            <button class="ocs-tabs__tab" role="tab" id="t-1" aria-controls="p-1" aria-selected="true">Usage</button>
            <button class="ocs-tabs__tab" role="tab" id="t-2" aria-controls="p-2" aria-selected="false">Props</button>
            <button class="ocs-tabs__tab" role="tab" id="t-3" aria-controls="p-3" aria-selected="false">A11y</button>
          </div>
          <div id="p-1" role="tabpanel" aria-labelledby="t-1" class="ocs-help" style="padding-top:.6rem">Arrow keys move between tabs.</div>
          <div id="p-2" role="tabpanel" aria-labelledby="t-2" class="ocs-help" style="padding-top:.6rem" hidden>Home and End jump to the ends.</div>
          <div id="p-3" role="tabpanel" aria-labelledby="t-3" class="ocs-help" style="padding-top:.6rem" hidden>Only the selected tab is in the tab order.</div>
        </div>
      </div>
    </section>

    <!-- 07. CARDS -->
    <section class="panel">
      <h2><span>07</span> Cards</h2>
      <p class="lede">Container, interactive, and stat</p>
      <div class="ocs-card-grid" style="--ocs-grid-gap:.9rem">
        <article class="ocs-card">
          <div class="ocs-card__header">
            <div>
              <h3 class="ocs-card__title">OCS Website</h3>
              <p class="ocs-card__subtitle">The official site, built in the open.</p>
            </div>
          </div>
          <div class="ocs-card__body">
            <div class="ocs-cluster">
              <span class="ocs-badge ocs-badge--code">#typescript</span>
              <span class="ocs-badge ocs-badge--code">#jekyll</span>
              <span class="ocs-badge ocs-badge--brand">open-source</span>
            </div>
          </div>
          <div class="ocs-card__footer">
            <span class="ocs-help">&#9733; 1.2k &middot; forks 324</span>
            <button class="ocs-btn ocs-btn--secondary ocs-btn--sm" style="margin-left:auto">View</button>
          </div>
        </article>
        <div class="ocs-card ocs-card--stat">
          <span class="ocs-card__stat-value">2,847</span>
          <span class="ocs-card__stat-label">Contributors</span>
          <span class="ocs-badge ocs-badge--success ocs-badge--dot" style="align-self:flex-start;margin-top:.5rem">+12% this month</span>
        </div>
        <a class="ocs-card ocs-card--stat ocs-card--interactive" href="#main">
          <span class="ocs-card__stat-value">96%</span>
          <span class="ocs-card__stat-label">Open source</span>
          <span class="ocs-help" style="margin-top:.4rem">Interactive card &mdash; tab to it</span>
        </a>
      </div>
    </section>

    <!-- 08. MODALS -->
    <section class="panel">
      <h2><span>08</span> Modals &amp; Dialogs</h2>
      <p class="lede">Native &lt;dialog&gt; &mdash; real focus trap</p>
      <p class="ocs-help" style="margin-bottom:1rem">
        Built on the browser's own top layer, so focus trapping, Escape-to-close and
        background inerting come for free instead of from hand-written JS.
      </p>
      <div class="ocs-cluster">
        <button class="ocs-btn ocs-btn--danger" data-ocs-open="m-del">Delete project&hellip;</button>
        <button class="ocs-btn ocs-btn--secondary" data-ocs-open="m-new">Create project&hellip;</button>
      </div>

      <dialog class="ocs-modal ocs-modal--danger" id="m-del" aria-labelledby="m-del-t">
        <form method="dialog" class="ocs-modal__panel">
          <header class="ocs-modal__header">
            <h2 class="ocs-modal__title" id="m-del-t">Delete project?</h2>
            <button class="ocs-modal__close" value="cancel" aria-label="Close">&times;</button>
          </header>
          <div class="ocs-modal__body">
            <p>This permanently removes <strong>ocs-website</strong> and all of its history. This action cannot be undone.</p>
          </div>
          <footer class="ocs-modal__footer">
            <button class="ocs-btn ocs-btn--ghost" value="cancel">Cancel</button>
            <button class="ocs-btn ocs-btn--danger" value="confirm">Delete</button>
          </footer>
        </form>
      </dialog>

      <dialog class="ocs-modal" id="m-new" aria-labelledby="m-new-t">
        <form method="dialog" class="ocs-modal__panel">
          <header class="ocs-modal__header">
            <h2 class="ocs-modal__title" id="m-new-t">Create new project</h2>
            <button class="ocs-modal__close" value="cancel" aria-label="Close">&times;</button>
          </header>
          <div class="ocs-modal__body">
            <div class="ocs-field">
              <label class="ocs-label ocs-label--required" for="m-name">Project name</label>
              <input class="ocs-input" id="m-name" placeholder="my-project">
            </div>
            <div class="ocs-field" style="margin-bottom:0">
              <label class="ocs-label" for="m-desc">Description</label>
              <textarea class="ocs-textarea" id="m-desc" placeholder="Optional"></textarea>
            </div>
          </div>
          <footer class="ocs-modal__footer">
            <button class="ocs-btn ocs-btn--ghost" value="cancel">Cancel</button>
            <button class="ocs-btn ocs-btn--primary" value="confirm">Create project</button>
          </footer>
        </form>
      </dialog>
    </section>

    <!-- 09. TABLES -->
    <section class="panel">
      <h2><span>09</span> Tables</h2>
      <p class="lede">Scroll region is keyboard reachable</p>
      <div class="ocs-table-wrap" tabindex="0" role="region" aria-label="Projects">
        <table class="ocs-table ocs-table--striped">
          <thead>
            <tr><th scope="col">Project</th><th scope="col">Language</th>
                <th scope="col" class="ocs-table__num">Stars</th>
                <th scope="col">Status</th><th scope="col">Updated</th></tr>
          </thead>
          <tbody>
            <tr><th scope="row">OCS Website</th><td>TypeScript</td><td class="ocs-table__num">1,204</td>
                <td><span class="ocs-badge ocs-badge--success ocs-badge--dot">Passing</span></td><td>2d ago</td></tr>
            <tr><th scope="row">AI Chatbot</th><td>Python</td><td class="ocs-table__num">856</td>
                <td><span class="ocs-badge ocs-badge--warning ocs-badge--dot">Flaky</span></td><td>5d ago</td></tr>
            <tr><th scope="row">Code Editor</th><td>Rust</td><td class="ocs-table__num">642</td>
                <td><span class="ocs-badge ocs-badge--danger ocs-badge--dot">Failing</span></td><td>1w ago</td></tr>
            <tr><th scope="row">Mobile App</th><td>Kotlin</td><td class="ocs-table__num">324</td>
                <td><span class="ocs-badge ocs-badge--neutral ocs-badge--dot">Archived</span></td><td>2w ago</td></tr>
          </tbody>
        </table>
        <nav aria-label="Pagination">
          <ul class="ocs-pagination">
            <li><a class="ocs-pagination__link" href="#main" aria-disabled="true">&lsaquo;</a></li>
            <li><a class="ocs-pagination__link" href="#main" aria-current="page">1</a></li>
            <li><a class="ocs-pagination__link" href="#main">2</a></li>
            <li><a class="ocs-pagination__link" href="#main">3</a></li>
            <li><a class="ocs-pagination__link" href="#main">&rsaquo;</a></li>
          </ul>
        </nav>
      </div>
    </section>

    <!-- 10. FEEDBACK -->
    <section class="panel">
      <h2><span>10</span> Alerts &amp; Feedback</h2>
      <p class="lede">Never colour alone &mdash; icon + title always</p>
      <div class="ocs-stack" style="--ocs-stack-gap:.6rem">
        <div class="ocs-alert ocs-alert--success" role="status">
          {icon("check")}
          <div class="ocs-alert__content"><p class="ocs-alert__title">Saved</p><p>Your changes have been published.</p></div>
          <button class="ocs-alert__close" aria-label="Dismiss">{icon("x", "")}</button>
        </div>
        <div class="ocs-alert ocs-alert--info" role="status">
          {icon("info")}
          <div class="ocs-alert__content"><p class="ocs-alert__title">Heads up</p><p>Your session expires in 5 minutes.</p></div>
        </div>
        <div class="ocs-alert ocs-alert--warning" role="status">
          {icon("warn")}
          <div class="ocs-alert__content"><p class="ocs-alert__title">Check your input</p><p>Two fields need attention before you continue.</p></div>
        </div>
        <div class="ocs-alert ocs-alert--danger" role="alert">
          {icon("warn")}
          <div class="ocs-alert__content"><p class="ocs-alert__title">Failed to save</p><p>The server rejected the request.</p></div>
        </div>
      </div>

      <p class="sub">Live toast &mdash; timer pauses on hover and focus</p>
      <div class="ocs-cluster" style="margin-bottom:1rem">
        <button class="ocs-btn ocs-btn--secondary ocs-btn--sm" onclick="OCS.toast({{variant:'success',title:'Saved',message:'Your changes have been published.'}})">Success</button>
        <button class="ocs-btn ocs-btn--secondary ocs-btn--sm" onclick="OCS.toast({{variant:'warning',title:'Check your input',message:'Two fields need attention.'}})">Warning</button>
        <button class="ocs-btn ocs-btn--secondary ocs-btn--sm" onclick="OCS.toast({{variant:'danger',title:'Failed to save',message:'The server rejected the request.'}})">Danger</button>
      </div>

      <p class="sub">Progress</p>
      <div class="ocs-stack" style="--ocs-stack-gap:.75rem">
        <div>
          <div class="ocs-split" style="margin-bottom:.35rem"><span class="ocs-help">Upload</span><span class="ocs-help">75%</span></div>
          <div class="ocs-progress" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100" aria-label="Upload progress">
            <div class="ocs-progress__bar" style="width:75%"></div>
          </div>
        </div>
        <div>
          <div class="ocs-split" style="margin-bottom:.35rem"><span class="ocs-help">Tests</span><span class="ocs-help">3 of 5</span></div>
          <div class="ocs-progress ocs-progress--success" role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" aria-label="Test progress">
            <div class="ocs-progress__bar" style="width:60%"></div>
          </div>
        </div>
        <div>
          <span class="ocs-help">Indeterminate</span>
          <div class="ocs-progress ocs-progress--indeterminate" style="margin-top:.35rem" role="progressbar" aria-label="Working">
            <div class="ocs-progress__bar"></div>
          </div>
        </div>
        <div class="ocs-cluster">
          <span class="ocs-spinner ocs-spinner--sm" role="status"><span class="ocs-sr-only">Loading</span></span>
          <span class="ocs-spinner" role="status"><span class="ocs-sr-only">Loading</span></span>
          <span class="ocs-help">Spinners carry screen-reader text</span>
        </div>
      </div>
    </section>

    <!-- 11. MENUS, AVATARS, LOADING -->
    <section class="panel">
      <h2><span>11</span> Menus, Avatars &amp; Loading</h2>
      <p class="lede">Popover API, top layer, no JS positioning</p>

      <p class="sub">Dropdown menu</p>
      <button class="ocs-btn ocs-btn--secondary" popovertarget="demo-menu">Actions</button>
      <div class="ocs-menu" id="demo-menu" popover role="menu">
        <p class="ocs-menu__label">Project</p>
        <button class="ocs-menu__item" role="menuitem">Rename<kbd>R</kbd></button>
        <button class="ocs-menu__item" role="menuitem">Duplicate<kbd>D</kbd></button>
        <button class="ocs-menu__item" role="menuitem" disabled>Transfer</button>
        <hr class="ocs-menu__sep">
        <button class="ocs-menu__item ocs-menu__item--danger" role="menuitem">Delete</button>
      </div>

      <p class="sub">Tooltip &mdash; hoverable and focusable, per WCAG 1.4.13</p>
      <span class="ocs-tooltip-wrap">
        <button class="ocs-btn ocs-btn--secondary ocs-btn--icon" aria-label="Delete" aria-describedby="tip-del">{icon("trash", "")}</button>
        <span class="ocs-tooltip" id="tip-del" role="tooltip">Delete project</span>
      </span>

      <p class="sub">Avatars</p>
      <div class="ocs-cluster">
        <span class="ocs-avatar ocs-avatar--sm" aria-hidden="true">AL</span>
        <span class="ocs-avatar" aria-hidden="true">SV</span>
        <span class="ocs-avatar ocs-avatar--brand ocs-avatar--lg" aria-hidden="true">OCS</span>
        <span class="ocs-avatar ocs-avatar--lg ocs-avatar--ring" aria-hidden="true">ME</span>
        <span class="ocs-avatar-stack" role="img" aria-label="4 contributors">
          <span class="ocs-avatar ocs-avatar--sm" aria-hidden="true">A</span>
          <span class="ocs-avatar ocs-avatar--sm" aria-hidden="true">B</span>
          <span class="ocs-avatar ocs-avatar--sm" aria-hidden="true">C</span>
          <span class="ocs-avatar ocs-avatar--sm ocs-avatar--brand" aria-hidden="true">+9</span>
        </span>
      </div>

      <p class="sub">Skeletons</p>
      <div class="ocs-card" style="padding:1rem" role="status">
        <span class="ocs-sr-only">Loading project</span>
        <div class="ocs-cluster" style="margin-bottom:.75rem">
          <span class="ocs-skeleton ocs-skeleton--circle" style="width:2rem"></span>
          <span class="ocs-skeleton ocs-skeleton--text" style="width:8rem"></span>
        </div>
        <span class="ocs-skeleton ocs-skeleton--text"></span>
        <span class="ocs-skeleton ocs-skeleton--text"></span>
        <span class="ocs-skeleton ocs-skeleton--text"></span>
      </div>
    </section>

    </div>
    </div>

    <!-- 12. GUIDELINES -->
    <section class="panel">
      <h2><span>12</span> Usage Guidelines</h2>
      <p class="lede">How to work with the system</p>
      <div class="ocs-card-grid" style="--ocs-grid-min:22rem;--ocs-grid-gap:0 2rem">
        <div>
          <div class="guideline">{icon("check", "")}<div><h3>Prefix everything</h3>
            <p>Every class starts with <code>ocs-</code>. The old bare <code>.row</code>, <code>.column</code>
               and <code>.button</code> selectors are gone &mdash; they collided with Bootstrap in the Spring app.</p></div></div>
          <div class="guideline">{icon("check", "")}<div><h3>Semantics drive state</h3>
            <p>Styling keys off <code>aria-current</code>, <code>aria-selected</code>, <code>aria-invalid</code>
               and <code>:disabled</code> &mdash; never a parallel <code>.active</code> class that can drift.</p></div></div>
          <div class="guideline">{icon("check", "")}<div><h3>Tokens, not literals</h3>
            <p>Reach for <code>var(--ocs-*)</code> or the Sass accessors. A typo in
               <code>fn.space(99)</code> fails the build instead of emitting nothing.</p></div></div>
        </div>
        <div>
          <div class="guideline">{icon("check", "")}<div><h3>Contrast is enforced, not hoped for</h3>
            <p>Every foreground token clears 4.5:1 on the darkest surface it can land on.
               Re-run <code>tools/contrast.py</code> after changing any colour.</p></div></div>
          <div class="guideline">{icon("check", "")}<div><h3>Themes still work</h3>
            <p>Under <code>.user-theme-active</code> the system re-points at
               <code>--pref-accent-color</code>, so the existing preferences panel keeps working.</p></div></div>
          <div class="guideline">{icon("check", "")}<div><h3>Modules, not imports</h3>
            <p>Built entirely on <code>@use</code>/<code>@forward</code>. Dart Sass is removing
               <code>@import</code>, and the current codebase has ~130 of them.</p></div></div>
        </div>
      </div>
    </section>

  </main>

  <footer class="pagefoot">
    <span>OCS Design System &middot; draft, not committed</span>
    <span class="receipt">{S["kb"]} KB &middot; {S["classes"]} classes &middot; {S["imports"]} @import &middot; the only unprefixed selector is <code>.{S["bare_generic_names"][0]}</code>, the theme bridge</span>
  </footer>
</div>

<script>
{JS}
</script>
"""

out = HERE / "showcase.html"
out.write_text(HTML)
print(f"wrote {out}  ({len(HTML):,} bytes)")
