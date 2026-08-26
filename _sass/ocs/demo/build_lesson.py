#!/usr/bin/env python3
"""Build a realistic OCS lesson page using ONLY the design system.

This is the proof that the tokens and components compose into a real page, not
just a swatch catalogue. Every class on this page comes from _sass/ocs -- the
only page-level CSS is the three-column shell, which is layout, not styling.
"""
import pathlib

HERE = pathlib.Path(__file__).parent
CSS = pathlib.Path("/tmp/ocs_full.css").read_text()
JS = pathlib.Path("/Users/samarthvaka/ocs-chatbot/pages/assets/js/ocs.js").read_text()
JS = JS.replace("</script>", "<\\/script>")
LOGO = (HERE / "logo_b64.txt").read_text().strip()

I = {
    "book":  '<path d="M2.5 3h4a2 2 0 0 1 2 2v8a1.5 1.5 0 0 0-1.5-1.5h-4.5z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M13.5 3h-4a2 2 0 0 0-2 2v8a1.5 1.5 0 0 1 1.5-1.5h4.5z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>',
    "code":  '<path d="M6 4 2.5 8 6 12M10 4l3.5 4-3.5 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
    "check": '<path d="M3 8.5 6.5 12 13 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
    "flask": '<path d="M6.5 2v4L3 12.5A1 1 0 0 0 3.9 14h8.2a1 1 0 0 0 .9-1.5L9.5 6V2M5.5 2h5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>',
    "warn":  '<path d="M8 2.5 14.5 13.5h-13z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M8 6.6v3M8 11.4v.7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
    "info":  '<circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 7.2v4M8 4.9v.9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
    "search":'<circle cx="7" cy="7" r="4.3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="m10.3 10.3 3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">{I[name]}</svg>'


SIDE = [
    ("Getting started", [("Setup", False), ("Your first endpoint", False)]),
    ("Spring Boot", [("Controllers", False), ("Request mapping", True), ("Persistence with JPA", False), ("Testing", False)]),
    ("Deploying", [("Docker", False), ("Nginx", False)]),
]


def sidebar():
    out = []
    for section, links in SIDE:
        out.append(f'<p class="ocs-sidenav__section">{section}</p>')
        for label, current in links:
            cur = ' aria-current="page"' if current else ""
            out.append(f'<a class="ocs-sidenav__link" href="#main"{cur}>{icon("book")}{label}</a>')
    return "\n        ".join(out)


HTML = f"""<title>Request Mapping in Spring</title>
<!-- Required: without this a phone lays the page out at 980px and renders it zoomed out.
     Harmless if the host wrapper already supplies one -- the first declaration wins. -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{CSS}

/* ---- page shell only: layout, not styling. Everything visual is a token. ---- */
body {{
  margin: 0;
  background: var(--ocs-surface-base);
  color: var(--ocs-text);
  font-family: var(--ocs-font-sans);
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}
.shell {{ display: grid; grid-template-columns: 250px minmax(0, 1fr) 260px; gap: 0;
  max-width: 1500px; margin: 0 auto; align-items: start; }}
.shell > aside {{ position: sticky; top: 0; max-height: 100dvh; overflow-y: auto;
  border-inline-end: 1px solid var(--ocs-border); }}
.shell > .rail {{ position: sticky; top: 0; padding: 1.5rem 1.25rem;
  border-inline-start: 1px solid var(--ocs-border); border-inline-end: 0;
  display: flex; flex-direction: column; gap: 1rem; }}
.doc {{ padding: 2rem 2.5rem 5rem; max-width: 74ch; }}
.doc h1 {{ font-size: 2rem; font-weight: 600; letter-spacing: -0.02em;
  line-height: 1.2; margin: .75rem 0 .5rem; text-wrap: balance; }}
.doc h2 {{ font-size: 1.25rem; font-weight: 600; margin: 2.25rem 0 .75rem;
  padding-block-start: 1.25rem; border-block-start: 1px solid var(--ocs-border-subtle); }}
.doc p {{ color: var(--ocs-text-secondary); }}
.doc ul {{ color: var(--ocs-text-secondary); padding-inline-start: 1.25rem; }}
.doc li {{ margin-block: .35rem; }}
.doc .meta {{ display: flex; gap: .75rem; align-items: center; flex-wrap: wrap;
  color: var(--ocs-text-muted); font-size: .8125rem; margin-bottom: 1.5rem; }}
@media (max-width: 1180px) {{
  .shell {{ grid-template-columns: 220px minmax(0,1fr); }}
  .shell > .rail {{ display: none; }}
}}
@media (max-width: 820px) {{
  .shell {{ grid-template-columns: 1fr; }}
  .shell > aside {{ position: static; max-height: none;
    border-inline-end: 0; border-block-end: 1px solid var(--ocs-border); }}
  .doc {{ padding: 1.5rem 1.25rem 4rem; }}
}}
</style>

<a class="ocs-skip-link" href="#main">Skip to content</a>

<nav class="ocs-topbar" aria-label="Primary">
  <a class="ocs-topbar__brand" href="#main">
    <img src="data:image/png;base64,{LOGO}" alt="" width="28" height="28"
         style="border-radius:6px;background:#fff;padding:2px">
    <span class="ocs-topbar__brand-text">Open Coding Society</span>
  </a>
  <div class="ocs-topbar__nav">
    <a class="ocs-topbar__link" href="#main" aria-current="page">Docs</a>
    <a class="ocs-topbar__link" href="#main">Projects</a>
    <a class="ocs-topbar__link" href="#main">Community</a>
  </div>
  <div class="ocs-topbar__actions">
    <button class="ocs-btn ocs-btn--ghost ocs-btn--icon ocs-btn--sm" aria-label="Search">{icon("search")}</button>
    <button class="ocs-btn ocs-btn--secondary ocs-btn--sm" popovertarget="acct-menu">
      <span class="ocs-avatar ocs-avatar--sm" aria-hidden="true">SV</span> Account
    </button>
    <div class="ocs-menu" id="acct-menu" popover role="menu">
      <p class="ocs-menu__label">Signed in as svaka2000</p>
      <button class="ocs-menu__item" role="menuitem">Profile</button>
      <button class="ocs-menu__item" role="menuitem">My progress<kbd>P</kbd></button>
      <button class="ocs-menu__item" role="menuitem">Settings</button>
      <hr class="ocs-menu__sep">
      <button class="ocs-menu__item ocs-menu__item--danger" role="menuitem">Sign out</button>
    </div>
  </div>
</nav>

<div class="shell">

  <aside>
    <nav class="ocs-sidenav" aria-label="Course">
      {sidebar()}
    </nav>
  </aside>

  <main id="main" class="doc">
    <nav aria-label="Breadcrumb">
      <ol class="ocs-breadcrumb">
        <li><a href="#main">Docs</a></li>
        <li><a href="#main">Spring Boot</a></li>
        <li><span aria-current="page">Request mapping</span></li>
      </ol>
    </nav>

    <h1>Request mapping</h1>
    <div class="meta">
      <span class="ocs-badge ocs-badge--brand">Lesson 4 of 8</span>
      <span class="ocs-badge ocs-badge--neutral">12 min read</span>
      <span>Updated 2 days ago</span>
    </div>

    <p>
      A controller is only useful once Spring knows which URLs should reach it.
      That wiring is done with <code class="ocs-code-inline">@RequestMapping</code>
      and its shorthands. By the end of this lesson you will be able to route a
      request to a method, read values out of the path, and return JSON.
    </p>

    <div class="ocs-alert ocs-alert--info" role="status">
      {icon("info", "ocs-alert__icon")}
      <div class="ocs-alert__content">
        <p class="ocs-alert__title">Before you start</p>
        <p>Finish <a href="#main">Controllers</a> first &mdash; this lesson assumes you already have a running app on port 8585.</p>
      </div>
    </div>

    <h2>Mapping a method to a URL</h2>
    <p>
      Put <code class="ocs-code-inline">@RestController</code> on the class and a
      mapping annotation on each method. The class-level
      <code class="ocs-code-inline">@RequestMapping</code> becomes a prefix for
      everything inside it.
    </p>

    <figure class="ocs-code">
      <figcaption class="ocs-code__head">
        <span class="ocs-code__lang">ProjectController.java</span>
        <button class="ocs-btn ocs-btn--ghost ocs-btn--sm">Copy</button>
      </figcaption>
      <pre class="ocs-code__body" tabindex="0"><code>@RestController
@RequestMapping("/api/projects")
public class ProjectController {{

    private final ProjectRepository repo;

    ProjectController(ProjectRepository repo) {{
        this.repo = repo;
    }}

    @GetMapping                       // GET /api/projects
    public List&lt;Project&gt; all() {{
        return repo.findAll();
    }}

    @GetMapping("/{{id}}")              // GET /api/projects/42
    public ResponseEntity&lt;Project&gt; one(@PathVariable Long id) {{
        return repo.findById(id)
                   .map(ResponseEntity::ok)
                   .orElse(ResponseEntity.notFound().build());
    }}
}}</code></pre>
    </figure>

    <div class="ocs-alert ocs-alert--warning" role="status">
      {icon("warn", "ocs-alert__icon")}
      <div class="ocs-alert__content">
        <p class="ocs-alert__title">Watch the return type</p>
        <p>Returning the entity directly sends a 200 even when nothing was found. Wrap it in <code class="ocs-code-inline">ResponseEntity</code> so a missing row becomes a real 404.</p>
      </div>
    </div>

    <h2>The shorthand annotations</h2>
    <p>Each HTTP verb has its own annotation. They are all just
       <code class="ocs-code-inline">@RequestMapping</code> with the method pre-set.</p>

    <div class="ocs-table-wrap" role="region" aria-label="Mapping annotations">
      <table class="ocs-table ocs-table--striped">
        <thead>
          <tr><th scope="col">Annotation</th><th scope="col">Verb</th><th scope="col">Typical use</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row"><code class="ocs-code-inline">@GetMapping</code></th><td>GET</td><td>Read a resource</td></tr>
          <tr><th scope="row"><code class="ocs-code-inline">@PostMapping</code></th><td>POST</td><td>Create a resource</td></tr>
          <tr><th scope="row"><code class="ocs-code-inline">@PutMapping</code></th><td>PUT</td><td>Replace a resource</td></tr>
          <tr><th scope="row"><code class="ocs-code-inline">@DeleteMapping</code></th><td>DELETE</td><td>Remove a resource</td></tr>
        </tbody>
      </table>
    </div>

    <h2>Try it</h2>
    <p>Start the app, then hit the endpoint. You should get an empty JSON array back.</p>

    <figure class="ocs-code">
      <figcaption class="ocs-code__head">
        <span class="ocs-code__lang">Terminal</span>
        <button class="ocs-btn ocs-btn--ghost ocs-btn--sm">Copy</button>
      </figcaption>
      <pre class="ocs-code__body" tabindex="0"><code>./mvnw spring-boot:run
curl http://127.0.0.1:8585/api/projects</code></pre>
    </figure>

    <div class="ocs-alert ocs-alert--success" role="status">
      {icon("check", "ocs-alert__icon")}
      <div class="ocs-alert__content">
        <p class="ocs-alert__title">Checkpoint</p>
        <p>If you saw <code class="ocs-code-inline">[]</code>, the route is wired. Press <kbd class="ocs-kbd">Ctrl</kbd> <kbd class="ocs-kbd">C</kbd> to stop the server.</p>
      </div>
    </div>

    <h2>Check your understanding</h2>
    <div class="ocs-fieldset" role="group" aria-labelledby="q1">
      <p id="q1" style="margin:0 0 .75rem;font-weight:600">Which annotation maps a GET request to a method?</p>
      <div class="ocs-stack" style="--ocs-stack-gap:.5rem">
        <label class="ocs-check"><input type="radio" name="q1"> <span><code class="ocs-code-inline">@PostMapping</code></span></label>
        <label class="ocs-check"><input type="radio" name="q1"> <span><code class="ocs-code-inline">@GetMapping</code></span></label>
        <label class="ocs-check"><input type="radio" name="q1"> <span><code class="ocs-code-inline">@PathVariable</code></span></label>
      </div>
      <div class="ocs-cluster" style="margin-top:1rem">
        <button class="ocs-btn ocs-btn--primary" onclick="OCS.toast({{variant:'success',title:'Correct',message:'@GetMapping handles GET requests.'}})">Check answer</button>
        <button class="ocs-btn ocs-btn--ghost">Show hint</button>
      </div>
    </div>

    <div class="ocs-split" style="margin-top:2.5rem">
      <button class="ocs-btn ocs-btn--secondary">&larr; Controllers</button>
      <button class="ocs-btn ocs-btn--primary" onclick="OCS.toast({{variant:'success',title:'Lesson complete',message:'Persistence with JPA unlocked.'}})">
        Mark complete &rarr;
      </button>
    </div>
  </main>

  <div class="rail">
    <div class="ocs-card ocs-card--stat">
      <span class="ocs-card__stat-label">Course progress</span>
      <span class="ocs-card__stat-value">50%</span>
      <div class="ocs-progress ocs-progress--success" role="progressbar"
           aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"
           aria-label="Course progress" style="margin-top:.6rem">
        <div class="ocs-progress__bar" style="width:50%"></div>
      </div>
      <p class="ocs-help" style="margin-top:.5rem">4 of 8 lessons complete</p>
    </div>

    <div class="ocs-card">
      <div class="ocs-card__header"><h3 class="ocs-card__title" style="font-size:.9rem">On this page</h3></div>
      <div class="ocs-card__body" style="padding-top:.5rem">
        <nav class="ocs-sidenav" aria-label="On this page" style="padding:0;gap:0">
          <a class="ocs-sidenav__link" href="#main" aria-current="true">Mapping a method</a>
          <a class="ocs-sidenav__link" href="#main">Shorthand annotations</a>
          <a class="ocs-sidenav__link" href="#main">Try it</a>
          <a class="ocs-sidenav__link" href="#main">Check your understanding</a>
        </nav>
      </div>
    </div>

    <div class="ocs-card">
      <div class="ocs-card__body">
        <p class="ocs-card__stat-label" style="margin-bottom:.4rem">Up next</p>
        <p style="margin:0 0 .75rem;font-weight:600">Persistence with JPA</p>
        <div class="ocs-cluster">{icon("flask")}<span class="ocs-help">18 min</span></div>
      </div>
    </div>
  </div>

</div>

<script>
{JS}
</script>
"""

out = HERE / "lesson.html"
out.write_text(HTML)
print(f"wrote {out} ({len(HTML):,} bytes)")
non_ascii = sorted(set(c for c in HTML if ord(c) > 127))
print("non-ascii:", non_ascii or "NONE")
