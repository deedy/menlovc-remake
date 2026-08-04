#!/usr/bin/env python3
"""Generate index.html — minimal ink-on-paper landing page for the Menlo Ventures team."""
import json, os, html

partners = json.load(open('partners.json'))
rest = json.load(open('team-rest.json'))

ORDER = ['matt-murphy', 'venky-ganesan', 'shawn-carolan',
         'tim-tully', 'matt-kraning', 'deedy-das',
         'amy-wu-martin', 'joff-redfern', 'croom-beatty',
         'jp-sanday', 'rama-sekhar', 'steve-sloane',
         'greg-yap']
partners.sort(key=lambda p: ORDER.index(p['slug']))

MANAGING = {'matt-murphy', 'venky-ganesan', 'shawn-carolan'}
for p in partners:
    p['category'] = 'partners'
    p['title'] = 'Managing Partner' if p['slug'] in MANAGING else 'Partner'

CATEGORIES = [('partners', 'Partners'), ('investors', 'Investors'),
              ('platform', 'Platform'), ('operations', 'Operations'),
              ('advisors', 'Advisors')]

# explicit row ordering per category (grid is 3 columns on desktop)
CAT_ORDER = {
    'investors': ['johnny-hu', 'derek-xiao', 'cc-gong',
                  'ryan-hand', 'sabrina-lu', 'sam-borja',
                  'ishika-chawla'],
    'platform': ['jordan-ormont', 'houman-haghighi', 'tiffany-spencer',
                 'kayla-hinderscheid', 'bryan-eglan', 'kandace-elam',
                 'darcy-yee'],
    'operations': ['kirsten-mello', 'deborah-carrillo', 'brent-fellows'],
    'advisors': ['h-dubose-montgomery',
                 'doug-carlisle', 'john-jarve', 'mark-siegel',
                 'naomi-pilosof-ionita', 'tyler-sosin', 'greg-rudin'],
}

TITLE_OVERRIDES = {
    'houman-haghighi': 'Partner, Business Development',
    'tiffany-spencer': 'Head, Marketing',
    'kayla-hinderscheid': 'Head, Network',
    'bryan-eglan': 'Business Development',
    'kandace-elam': 'Talent',
    'darcy-yee': 'Marketing',
    'kirsten-mello': 'Partner, CFO',
    'deborah-carrillo': 'Partner, General Counsel',
    'brent-fellows': 'Finance',
}

SHOW_LOGOS = {'partners'}  # investment logos only on the Partners tab

# advisors: first card (DuBose) alone and centered on its own row
FIRST_CENTER = {'advisors'}

NAME_OVERRIDES = {
    'johnny-hu': 'Johnny Hu',
    'cc-gong': 'CC Gong',
}

people = partners + rest
for p in people:
    p['title'] = TITLE_OVERRIDES.get(p['slug'], p['title'])
    p['name'] = NAME_OVERRIDES.get(p['slug'], p['name'])
by_cat = {key: [p for p in people if p['category'] == key] for key, _ in CATEGORIES}
for key, order in CAT_ORDER.items():
    by_cat[key].sort(key=lambda p: order.index(p['slug']))

# partner-titled folks from other groups also close out the Partners tab
PARTNERS_EXTRA = ['jordan-ormont', 'kirsten-mello',
                  'houman-haghighi', 'deborah-carrillo', 'h-dubose-montgomery']
slug_map = {p['slug']: p for p in people}
by_cat['partners'] += [slug_map[s] for s in PARTNERS_EXTRA]

# scraped per-partner portfolio data (see scripts/ + scratchpad pipeline)
PROFILE_DATA = json.load(open('partner-profiles.json'))
HAS_PROFILE = set(PROFILE_DATA) | {'matt-murphy'}

# logos whose filled/dark artwork blacks out under brightness(0): show grayscale instead
RAW_LOGOS = {'unstructured.png', 'rivet.png', 'typeface.png', 'Trove_logo-1.png',
             'cartwheel.png', 'fleetsmith.png', 'eve.svg', 'everlaw.svg',
             'heap-1.svg', 'openhands.svg'}


def card(p, i, show_logos=True):
    name = html.escape(p['name'])
    role = html.escape(p['title'])
    logos = []
    if show_logos:
        for c in p['companies'][:6]:
            if not c.get('logo_local'):
                continue
            fname = os.path.basename(c['logo_local'])
            cname = html.escape(c['name'])
            raw = ' class="raw"' if fname in RAW_LOGOS else ''
            logos.append(f'        <li><img{raw} src="assets/logos/{fname}" alt="{cname}" title="{cname}" loading="lazy"></li>')
    inv_block = ''
    if logos:
        inv_block = (f'\n        <ul class="investments" aria-label="Selected investments of {name}">\n'
                     + '\n'.join(logos) + '\n        </ul>')
    hover_path = f"assets/partners/{p['slug']}-hover.jpg"
    hover_html = (f'\n          <img class="alt" src="{hover_path}" alt="" aria-hidden="true" loading="lazy">'
                  if os.path.exists(hover_path) else '')
    managing = ' managing' if p['title'] == 'Managing Partner' else ''
    body = f'''<figure class="portrait">
          <img src="assets/partners/{p['slug']}.jpg" alt="Ink line portrait of {name}" loading="lazy">{hover_html}
        </figure>
        <h2 class="name">{name}</h2>'''
    if p['slug'] in HAS_PROFILE:
        body = f'<a class="card-link" href="team/{p["slug"]}/">{body}</a>'
    return f'''      <article class="partner{managing}" style="--i:{i}">
        {body}
        <p class="role">{role}</p>{inv_block}
      </article>'''


grids = []
for key, label in CATEGORIES:
    members = by_cat[key]
    cards_html = '\n'.join(card(p, i, key in SHOW_LOGOS) for i, p in enumerate(members))
    if key in FIRST_CENTER:
        layout = ' first-center'
    elif len(members) % 3 == 1:
        layout = ' center-last'
    else:
        layout = ''
    hidden = '' if key == 'partners' else ' is-hidden'
    grids.append(f'    <div class="grid{layout}{hidden}" data-cat="{key}">\n{cards_html}\n    </div>')
grids_html = '\n'.join(grids)

# hero logo grid. Valuations and acquisition figures load from the gitignored
# valuations.json — committed source and deployed pages carry no dollar figures.
FOLIO = [
    dict(name='Anthropic', logo='anthropic.svg', note='Partnered at C, Led the D', url='https://www.anthropic.com'),
    dict(name='OpenRouter', logo='openrouter2026.svg', note='Partnered at Seed, Led the A', url='https://openrouter.ai'),
    dict(name='Lovable', logo='lovable.svg', note='Led the B', url='https://lovable.dev'),
    dict(name='Suno', logo='suno.svg', note='Led the C', url='https://suno.com'),
    dict(name='Wispr Flow', logo='wispr_flow.svg', note='Led the Seed, A', url='https://wisprflow.ai'),
    dict(name='Higgsfield', logo='higgsfield.webp', note='Led the Seed', url='https://higgsfield.ai'),
    dict(name='Gimlet', logo='gimlet_labs.png', note='Led the A', url='https://gimletlabs.ai'),
    dict(name='Uber', logo='uber.png', note='Led the B', url='https://www.uber.com', is_public=True),
    dict(name='Mercor', logo='mercor.png', note='Partnered at B', url='https://mercor.com', desktop_only=True),
    dict(name='Chai Discovery', logo='chai_discovery.svg', note='Led the A', url='https://www.chaidiscovery.com', desktop_only=True),
    dict(name='Databricks', logo='databricks.png', note='Bought Neon', url='https://www.databricks.com', desktop_only=True),
    dict(name='Cursor', logo='cursor.svg', note='Bought Graphite', url='https://cursor.com', desktop_only=True),
    dict(name='Modal', logo='modal.svg', note='Partnered at C', url='https://modal.com', desktop_only=True),
    dict(name='Skild AI', logo='skild_ai.png', note='Partnered at A', url='https://www.skild.ai', desktop_only=True),
    dict(name='Xaira', logo='xaira_black.png', note='Partnered at Seed', url='https://xaira.com', desktop_only=True),
    dict(name='Chime', logo='chime.svg', note='Led the C', url='https://www.chime.com', is_public=True, desktop_only=True),
]

# sensitive figures: gitignored sidecar, absent on fresh clones
try:
    _VALS = json.load(open('valuations.json'))
except FileNotFoundError:
    _VALS = {'folio': {}, 'last': {}}
FOLIO_VALS = _VALS.get('folio', {})


def folio_grid(with_valuations):
    items = []
    for c in FOLIO:
        fv = FOLIO_VALS.get(c['name'], {})
        note = fv.get('note_local', c['note']) if with_valuations else c['note']
        note_html = html.escape(note).replace(', ', ' <span class="dot">&middot;</span> ')
        val_html = ''
        if with_valuations and fv.get('val'):
            pub = ' <sup class="pub" title="Public company">&#9650;</sup>' if c.get('is_public') else ''
            val_html = f'\n        <span class="folio-val">{html.escape(fv["val"])}{pub}</span>'
        cls = ' class="desktop-only"' if c.get('desktop_only') else ''
        items.append(f'''      <li{cls}><a href="{c['url']}" target="_blank" rel="noopener">
        <img src="assets/logos/{c['logo']}" alt="{html.escape(c['name'])}" loading="lazy">
        <span class="folio-round">{note_html}</span>{val_html}
      </a></li>''')
    return '\n'.join(items)


folio_html = folio_grid(with_valuations=False)
folio_html_local = folio_grid(with_valuations=True)

SHORT_LABELS = {'operations': 'Ops'}  # compact label used on narrow screens

def tab_label(key, label):
    short = SHORT_LABELS.get(key)
    if not short:
        return label
    return f'<span class="tab-full">{label}</span><span class="tab-short">{short}</span>'

tabs_html = '\n'.join(
    f'      <button class="tab{" is-active" if key == "partners" else ""}" data-cat="{key}" role="tab" '
    f'aria-selected="{"true" if key == "partners" else "false"}">{tab_label(key, label)}</button>'
    for key, label in CATEGORIES)

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Menlo Ventures — The Team</title>
<meta name="description" content="Menlo Ventures. Venture capital since 1976. The team and the companies they back.">
<meta property="og:type" content="website">
<meta property="og:title" content="Menlo Ventures">
<meta property="og:description" content="Venture capital since 1976. Menlo Park &middot; San Francisco.">
<meta property="og:url" content="https://deedy.github.io/menlovc-remake/">
<meta property="og:image" content="https://deedy.github.io/menlovc-remake/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Menlo Ventures">
<meta name="twitter:description" content="Venture capital since 1976. Menlo Park &middot; San Francisco.">
<meta name="twitter:image" content="https://deedy.github.io/menlovc-remake/assets/og.png">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='white'/%3E%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='22' text-anchor='middle' fill='%23FF8304'%3EM%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=IBM+Plex+Mono:wght@400;500&family=Mulish:wght@500;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #0a0a0a;
    --accent: #FF8304;
    --paper: #ffffff;
    --hairline: rgba(10, 10, 10, 0.18);
    --faint: rgba(10, 10, 10, 0.55);
    --serif: "Instrument Serif", Georgia, "Times New Roman", serif;
    --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
    --sans: "Mulish", "Proxima Nova", Roboto, "Helvetica Neue", sans-serif;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  ::selection {{ background: var(--accent); color: #fff; }}

  :focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}

  html {{ scroll-behavior: smooth; }}

  body {{
    background: var(--paper);
    color: var(--ink);
    font-family: var(--serif);
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }}

  .eyebrow {{
    font-family: var(--mono);
    font-size: 8px;
    font-weight: 500;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--faint);
  }}

  /* ---------- hero ---------- */
  .hero {{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 48px 18px 30px;
    text-align: center;
  }}

  .hero > * {{
    opacity: 0;
    animation: rise 0.9s cubic-bezier(0.19, 1, 0.22, 1) forwards;
  }}
  .hero > :nth-child(1) {{ animation-delay: 0.10s; }}
  .hero > :nth-child(2) {{ animation-delay: 0.25s; }}
  .hero > :nth-child(3) {{ animation-delay: 0.40s; }}
  .hero > :nth-child(4) {{ animation-delay: 0.52s; }}

  .wordmark {{
    width: min(255px, 54vw);
    height: auto;
    display: block;
  }}

  .est {{
    margin-top: 20px;
    color: var(--ink);
  }}

  .cities {{
    margin-top: 9px;
  }}

  .byline {{
    margin-top: 24px;
    font-family: var(--sans);
    font-weight: 500;
    font-size: clamp(14px, 1.6vw, 16px);
    letter-spacing: 0.015em;
    color: var(--ink);
    max-width: 44em;
  }}
  .byline span {{ color: var(--accent); }}

  .dot {{ color: var(--accent); }}

  /* ---------- hero logo grid ---------- */
  .folio {{
    max-width: 760px;
    margin: 0 auto;
    padding: 4px 24px 30px;
    opacity: 0;
    animation: rise 0.9s cubic-bezier(0.19, 1, 0.22, 1) 0.5s forwards;
  }}
  .folio-grid {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px 36px;
  }}
  .folio-grid li {{ min-width: 0; }}
  .folio-grid a {{
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 66px;
    padding-bottom: 32px;
    text-decoration: none;
  }}
  .folio-grid img {{
    max-height: 17px;
    max-width: 82%;
    width: auto;
    height: auto;
    object-fit: contain;
    filter: brightness(0);
    opacity: 0.55;
    transition: filter 0.35s ease, opacity 0.35s ease, transform 0.35s ease;
  }}
  .folio-grid a:hover img {{
    filter: none;
    opacity: 1;
    transform: translateY(-3px);
  }}
  .folio-round {{
    position: absolute;
    bottom: 19px;
    left: 0;
    right: 0;
    text-align: center;
    font-family: var(--mono);
    font-size: 7px;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--faint);
    white-space: nowrap;
    opacity: 0;
    transform: translateY(3px);
    transition: opacity 0.35s ease, transform 0.35s ease;
  }}
  .folio-grid a:hover .folio-round {{
    opacity: 1;
    transform: none;
  }}
  .folio-val {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    font-family: var(--sans);
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--ink);
    white-space: nowrap;
    opacity: 0;
    transform: translateY(3px);
    transition: opacity 0.35s ease 0.05s, transform 0.35s ease 0.05s;
  }}
  .folio-grid a:hover .folio-val {{
    opacity: 1;
    transform: none;
  }}
  .pub {{
    color: var(--accent);
    font-size: 5px;
    vertical-align: 2px;
  }}
  .see-portfolio {{
    text-align: center;
    margin-top: 4px;
  }}
  .see-portfolio a {{
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    font-family: var(--mono);
    font-size: 7.5px;
    font-weight: 500;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: rgba(10, 10, 10, 0.4);
    text-decoration: none;
    transition: color 0.3s ease;
  }}
  .see-portfolio a:hover {{ color: var(--ink); }}
  .see-portfolio .chev {{
    transition: transform 0.3s ease;
  }}
  .see-portfolio a:hover .chev {{ transform: translateY(2px); }}

  /* ---------- category tabs ---------- */
  .tabs {{
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px 25px;
    padding: 6px 18px 30px;
    opacity: 0;
    animation: rise 0.9s cubic-bezier(0.19, 1, 0.22, 1) 0.6s forwards;
  }}
  .tab {{
    appearance: none;
    background: none;
    border: none;
    cursor: pointer;
    font-family: var(--mono);
    font-size: 8px;
    font-weight: 500;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--faint);
    padding: 4px 2px 6px;
    border-bottom: 1px solid transparent;
    transition: color 0.3s ease, border-color 0.3s ease;
  }}
  .tab:hover {{ color: var(--ink); }}
  .tab.is-active {{
    color: var(--ink);
    border-bottom-color: var(--accent);
  }}
  .tab-short {{ display: none; }}

  @keyframes rise {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: none; }}
  }}

  /* ---------- team grid ---------- */
  .partners {{
    max-width: 930px;
    margin: 0 auto;
    padding: 0 24px 90px;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    column-gap: 42px;
    row-gap: 36px;
  }}
  .grid.is-hidden {{ display: none; }}

  .partner {{
    min-width: 0;
    opacity: 0;
    animation: rise 0.9s cubic-bezier(0.19, 1, 0.22, 1) forwards;
    animation-delay: calc(0.5s + var(--i) * 0.06s);
  }}
  body.tabs-used .partner {{
    animation-delay: calc(var(--i) * 0.04s);
  }}

  .portrait {{
    position: relative;
    aspect-ratio: 1 / 1;
    overflow: hidden;
    background: var(--paper);
  }}
  .portrait img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scale(1.02);
    transition: transform 1.1s cubic-bezier(0.19, 1, 0.22, 1);
  }}
  .portrait img.alt {{
    position: absolute;
    inset: 0;
    opacity: 0;
    transition: opacity 0.5s ease, transform 1.1s cubic-bezier(0.19, 1, 0.22, 1);
  }}
  .partner:hover .portrait img {{ transform: scale(1.07); }}
  .partner:hover .portrait img.alt {{ opacity: 1; }}

  /* managing partners open in watercolor; first hover anywhere dismisses it for good */
  body:not(.grid-touched) .partner.managing .portrait img.alt {{ opacity: 1; }}
  body:not(.grid-touched) .partner.managing .role {{ color: var(--accent); }}

  .card-link {{
    display: block;
    color: inherit;
    text-decoration: none;
  }}

  .name {{
    font-size: 22px;
    font-weight: 400;
    letter-spacing: 0.01em;
    margin-top: 10px;
    line-height: 1.1;
    text-align: center;
  }}

  .role {{
    font-family: var(--mono);
    font-size: 8px;
    font-weight: 500;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--faint);
    margin-top: 5px;
    text-align: center;
    transition: color 0.5s ease;
  }}
  .partner:hover .role {{ color: var(--accent); }}

  .investments {{
    list-style: none;
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: 10px;
    margin-top: 12px;
    height: 22px;
  }}
  .investments li {{
    flex: 1 1 0;
    min-width: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: flex-grow 0.35s cubic-bezier(0.19, 1, 0.22, 1);
  }}
  .investments li:hover {{ flex-grow: 3; }}
  .investments img {{
    display: block;
    width: auto;
    height: auto;
    max-height: 10px;
    max-width: 100%;
    object-fit: contain;
    filter: brightness(0);
    opacity: 0.7;
    transition: opacity 0.3s ease, max-height 0.35s cubic-bezier(0.19, 1, 0.22, 1);
  }}
  .investments li:hover img {{
    opacity: 1;
    max-height: 22px;
  }}
  .investments img.raw {{ filter: grayscale(1); }}

  /* grid shows 3 columns from ~770px up; center lone cards there */
  @media (min-width: 770px) {{
    .grid.center-last > .partner:last-child {{ grid-column: 2; }}
    .grid.first-center > .partner:first-child {{ grid-column: 2; }}
    .grid.first-center > .partner:nth-child(2) {{ grid-column: 1; }}
  }}

  @media (max-width: 640px) {{
    .grid {{
      grid-template-columns: repeat(2, 1fr);
      column-gap: 24px;
      row-gap: 30px;
    }}
    .partners {{ padding: 0 16px 70px; }}
    .name {{ font-size: 17px; }}
    .tabs {{
      flex-wrap: nowrap;
      gap: 16px;
      white-space: nowrap;
    }}
    .tab-full {{ display: none; }}
    .tab-short {{ display: inline; }}
    .folio-grid {{
      grid-template-columns: repeat(2, 1fr);
      gap: 4px 20px;
    }}
    .folio-grid li.desktop-only {{ display: none; }}
    .folio-grid a {{ height: 56px; }}
    .folio-grid img {{ max-height: 15px; }}
    .folio-round {{ font-size: 6px; letter-spacing: 0.18em; }}
    .investments {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px 12px;
      padding: 0 10px;
    }}
    .investments img {{ max-height: 9px; }}
  }}

  @media (prefers-reduced-motion: reduce) {{
    .hero > *, .partner, .tabs {{ animation: none; opacity: 1; }}
    .portrait img, .investments img {{ transition: none; }}
  }}
</style>
</head>
<body>

  <header class="hero">
    <img class="wordmark" src="assets/menlo-logo.png" alt="Menlo Ventures">
    <p class="eyebrow est">Est. 1976</p>
    <p class="eyebrow cities">Menlo Park &nbsp;<span class="dot">&middot;</span>&nbsp; San Francisco</p>
    <p class="byline">We raised <span>~$3B</span> to lead rounds in era-defining startups from Seed to Series&nbsp;D</p>
  </header>

  <section class="folio" aria-label="Selected investments">
    <ul class="folio-grid">
{folio_html}
    </ul>
    <p class="see-portfolio"><a href="portfolio/">
      <span>See entire portfolio</span>
      <svg class="chev" width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </a></p>
  </section>

  <nav class="tabs" role="tablist" aria-label="Team categories">
{tabs_html}
  </nav>

  <main class="partners" id="partners">
{grids_html}
  </main>

  <script>
    // managing partners rest in watercolor only until the first card hover
    const grids = document.querySelector('.partners');
    const dismissIntro = (e) => {{
      if (e.target.closest('.partner')) {{
        document.body.classList.add('grid-touched');
        grids.removeEventListener('mouseover', dismissIntro);
      }}
    }};
    grids.addEventListener('mouseover', dismissIntro);

    document.querySelectorAll('.tab').forEach((btn) => {{
      btn.addEventListener('click', () => {{
        document.body.classList.add('tabs-used');
        document.querySelectorAll('.tab').forEach((b) => {{
          b.classList.toggle('is-active', b === btn);
          b.setAttribute('aria-selected', b === btn ? 'true' : 'false');
        }});
        document.querySelectorAll('.grid').forEach((g) => {{
          g.classList.toggle('is-hidden', g.dataset.cat !== btn.dataset.cat);
        }});
      }});
    }});
  </script>

</body>
</html>
'''

open('index.html', 'w').write(page)
# local.html (gitignored): same page with valuations rendered into the folio grid
open('local.html', 'w').write(page.replace(folio_html, folio_html_local))

# /portfolio/ stub — same head and hero, content to come
head_p = page.split('<head>', 1)[1].split('</head>', 1)[0]
head_p = head_p.replace('<title>Menlo Ventures — The Team</title>',
                        '<title>Menlo Ventures — Portfolio</title>')
hero_p = page.split('<header class="hero">', 1)[1].split('</header>', 1)[0]
hero_p = hero_p.replace('src="assets/', 'src="../assets/')
hero_p = hero_p.replace(
    '<img class="wordmark" src="../assets/menlo-logo.png" alt="Menlo Ventures">',
    '<a href="../" aria-label="Back to home"><img class="wordmark" src="../assets/menlo-logo.png" alt="Menlo Ventures"></a>')

portfolio_page = f'''<!doctype html>
<html lang="en">
<head>{head_p}</head>
<body>

  <header class="hero">{hero_p}</header>

  <main class="partners" id="portfolio">
  </main>

</body>
</html>
'''
os.makedirs('portfolio', exist_ok=True)
open('portfolio/index.html', 'w').write(portfolio_page)

# ---------------------------------------------------------------------------
# team member profile pages — /team/<slug>/
# investments ordered by importance + recency; the top rows land above the fold
PROFILES = {
    'matt-murphy': dict(
        blurb=(
            "Matt leads Menlo&rsquo;s AI practice, investing across AI infrastructure "
            "and AI-native software. He joined the firm in 2015 after fifteen years as "
            "a general partner at Kleiner Perkins, where he was a board observer at "
            "Google from first investment through IPO and launched the $200M iFund in "
            "partnership with Apple."
        ),
        investments=[
            dict(name='Anthropic', logo='anthropic.svg', founded='2021', stage='Partnered at C &middot; Led the D', partnered='2023', about='AI safety and research company building reliable, interpretable AI systems &mdash; maker of Claude.'),
            dict(name='Lovable', logo='lovable.svg', founded='2023', stage='Led the B', partnered='2025', about='AI-powered development platform that turns ideas into working software.'),
            dict(name='Legora', logo='legora.svg', founded='2023', stage='Partnered at D', partnered='2026', about='Collaborative AI workspace for the world&rsquo;s leading law firms.'),
            dict(name='Semgrep', logo='semgrep.svg', founded='2017', stage='Partnered at D', partnered='2024', about='AppSec platform securing cloud-native applications at scale.'),
            dict(name='Carta', logo='Carta-Logo-200px.svg', founded='2012', stage='Partnered at C', partnered='2017', about='Equity management platform for founders, investors, and employees.'),
            dict(name='Harness', logo='harness.png', founded='2016', stage='Led the A', partnered='2017', about='AI-native software delivery platform for modern engineering teams.'),
            dict(name='Benchling', logo='benchling.svg', founded='2012', stage='Partnered at C', partnered='2019', about='Life-sciences R&amp;D cloud powering modern biotech discovery.'),
            dict(name='Typeface', logo='typeface.png', founded='2022', stage='Partnered at A', partnered='2023', about='Enterprise generative-AI platform for on-brand content creation.'),
            # --- below the fold: revealed by "See more" ---
            dict(name='OpenRouter', logo='openrouter2026.svg', founded='2023', stage='Partnered at Seed &middot; Led the A', partnered='2025', about='Unified API gateway for hundreds of frontier and open AI models.', more=True),
            dict(name='Skild AI', logo='skild_ai.png', founded='2023', stage='Partnered at A', partnered='2024', about='General-purpose AI grounded in the physical world &mdash; robotics foundation models.', more=True),
            dict(name='True Anomaly', logo='true_anomaly.webp', founded='2022', stage='Partnered at B', partnered='2023', about='Hardware and software systems for space security and sustainability.', more=True),
            dict(name='Armadin', logo='armadin-scaled.png', founded='2025', stage='Partnered at A', partnered='2026', about='AI-native cyber attacker that autonomously tests defenses before real threats do.', more=True),
            dict(name='Grow Therapy', logo='grow_therapy.png', founded='2020', stage='Partnered at D', partnered='2025', about='Mental healthcare platform making insurance-covered therapy accessible.', more=True),
            dict(name='Netlify', logo='netlify-e1679354589818.png', founded='2014', stage='Partnered at C', partnered='2024', about='All-in-one platform for automating modern web projects at global scale.', more=True),
            dict(name='Mimic', logo='mimic.png', founded='2023', stage='Partnered at Seed', partnered='2024', about='Enterprise defense system built to combat ransomware and cyber extortion.', more=True),
            dict(name='Envoy', logo='Envoy-1.svg', founded='2013', stage='Partnered at B', partnered='2018', about='Workplace platform for desk booking, visitors, and connected offices.', more=True),
            dict(name='Clarifai', logo='clarifai.png', founded='2013', stage='Partnered at B', partnered='2016', about='AI platform for visual recognition and full-lifecycle model development.', more=True),
            dict(name='Observable', logo='observable.png', founded='2016', stage='Partnered at B', partnered='2021', about='Web-based platform for collaborative data visualization and exploration.', more=True),
            dict(name='Hover', logo='hover.svg', founded='2011', stage='Partnered at C', partnered='2019', about='Turns smartphone photos of any property into an interactive 3D model.', more=True),
            dict(name='Alloy', logo='alloy.svg', founded='2016', stage='Partnered at A', partnered='2021', about='Supply and demand synchronization platform for consumer goods.', more=True),
            dict(name='Relyance AI', logo='relyance.png', founded='2020', stage='Partnered at A', partnered='2021', about='Privacy, data governance, and compliance in a single platform.', more=True),
            dict(name='Vivun', logo='vivun.png', founded='2018', stage='Partnered at B', partnered='2020', about='AI-powered platform connecting sales with product teams.', more=True),
            dict(name='Zylo', logo='zylo.svg', founded='2016', stage='Partnered at B', partnered='2019', about='Enterprise SaaS management and spend optimization platform.', more=True),
            dict(name='Heap', logo='heap-1.svg', founded='2013', stage='Partnered at A &middot; Acq. by Contentsquare', partnered='2016', about='Digital insights platform combining quantitative and qualitative analytics.', more=True),
            dict(name='6 River Systems', logo='6_river.png', founded='2015', stage='Partnered at B &middot; Acq. by Shopify', partnered='2018', about='Autonomous mobile robots making warehouse fulfillment more efficient.', more=True),
            dict(name='Airbase', logo='airbase-1.png', founded='2017', stage='Partnered at B &middot; Acq. by Paylocity', partnered='2021', about='Spend management platform automating accounting workflows.', more=True),
            dict(name='Canvas', logo='canvas.svg', founded='2017', stage='Partnered at B &middot; Acq. by JLG', partnered='2021', about='Construction robotics using machine learning to install drywall.', more=True),
            dict(name='Cleanlab', logo='cleanlab.png', founded='2021', stage='Partnered at A &middot; Acq. by Handshake', partnered='2023', about='Automated data curation for LLMs and the modern AI stack.', more=True),
            dict(name='FireHydrant', logo='firehydrant.png', founded='2018', stage='Partnered at A &middot; Acq. by Freshworks', partnered='2020', about='Incident response tooling for modern operations teams.', more=True),
            dict(name='Scout RFP', logo='scout.png', founded='2013', stage='Partnered at B &middot; Acq. by Workday', partnered='2017', about='Cloud-based strategic sourcing for smarter purchasing decisions.', more=True),
            dict(name='Usermind', logo='usermind.png', founded='2013', stage='Partnered at B &middot; Acq. by Qualtrics', partnered='2015', about='Unified platform for orchestrating business operations.', more=True),
            dict(name='Veriflow', logo='veriflow.png', founded='2013', stage='Partnered at A &middot; Acq. by VMware', partnered='2016', about='Brought formal verification to network infrastructure.', more=True),
        ],
    ),
}

# hand-written career blurbs (no investment name-dropping) for the scraped profiles
BLURBS = {
    'venky-ganesan': "Venky invests in AI-native software, cybersecurity, and AI infrastructure. Before Menlo he was a managing partner at Globespan Capital Partners, where he led early investments in Palo Alto Networks and Upwork, and he has spent two decades on the boards of category-defining security and consumer companies.",
    'shawn-carolan': "Shawn is an early-stage investor focused on the &ldquo;utilitarian consumer&rdquo; &mdash; better, faster, cheaper ways to move through life. An electrical engineer by training, he has spent two decades at Menlo turning emerging platform shifts into household names.",
    'tim-tully': "Tim is a technologist and developer at heart, investing in AI/ML, the modern data stack, and next-generation cloud. Before Menlo he was CTO of Splunk and spent more than a decade leading engineering at Yahoo.",
    'matt-kraning': "Matt focuses on AI, national defense, robotics, and cybersecurity. He co-founded and was CTO of Expanse, acquired by Palo Alto Networks for $1.25B, then oversaw generative-AI development across the company. Earlier he worked at DARPA, deploying to Afghanistan as lead data scientist; he holds a Ph.D. in electrical engineering from Stanford.",
    'deedy-das': "Deedy invests in early-stage AI/ML, next-generation infrastructure, and enterprise software. He was on the founding team of Glean, rising from engineer to creator and product lead of Glean Assistant, after earlier engineering roles at large public companies.",
    'amy-wu-martin': "Amy leads Menlo&rsquo;s consumer technology and gaming practice, backing founders at the forefront of platform shifts. She previously invested in Web3 and gaming at FTX Ventures and led consumer investments at Lightspeed.",
    'joff-redfern': "Joff was Chief Product Officer at Atlassian, leading Jira, Confluence, and Trello. Before that he spent seven years at LinkedIn building the mobile team as the company scaled from 450 people through IPO to more than 10,000.",
    'jp-sanday': "JP invests in enterprise AI applications, vertical AI, and digital health &mdash; companies embedding intelligence directly into high-value industry workflows, automating labor and unlocking proprietary data.",
    'rama-sekhar': "Rama focuses on cybersecurity, AI, and cloud infrastructure. He joined Menlo after 15 years at Norwest Venture Partners and earlier roles at Comcast Ventures and Cisco, where he began his career as a systems engineer.",
    'steve-sloane': "Steve leads investments from Menlo&rsquo;s Inflection Fund, targeting fast-growing Series B and C companies in AI-powered vertical SaaS and supply chain. He joined Menlo in 2015 and became a partner in 2019, after growth-stage investing at Insight and founding a YC-backed startup.",
    'croom-beatty': "Croom focuses on application-layer AI across financial technology, healthcare IT, and vertical software. Before joining Menlo in 2017 he worked in strategy at Payoneer, where he launched and ran the company&rsquo;s first credit business.",
    'greg-yap': "Greg invests in life science and healthcare &mdash; novel therapeutic platforms, digital health, and transformative technologies. He came to venture after 20 years as an operator and executive in genomics, most recently as entrepreneur-in-residence at Illumina Ventures.",
    'jordan-ormont': "Jordan leads talent strategy, building Menlo&rsquo;s network of next-generation entrepreneurs and executives. He has spent 20 years coaching CEOs and founders on building world-class teams and boards, previously shaping talent strategy as a senior partner at Kleiner Perkins.",
    'kirsten-mello': "Kirsten joined Menlo in 1999 and has been the firm&rsquo;s Chief Financial Officer since 2008, overseeing finance, investor relations, compliance, and operations. She began her career at Ernst &amp; Young, serving Silicon Valley technology clients from startups to public companies.",
    'houman-haghighi': "Houman accelerates growth for Menlo&rsquo;s portfolio companies through strategic partnerships, customer engagements, and follow-on financing. He spent 15 years at Qualcomm across engineering and product &mdash; including Whispernet, the technology behind Amazon Kindle&rsquo;s book delivery &mdash; and led business development for Qualcomm Ventures.",
    'deborah-carrillo': "Deborah is Menlo&rsquo;s General Counsel, advising the firm across investments, exits, fundraising, fund structuring, and compliance. She joined from Pillsbury Winthrop Shaw Pittman, where she represented startups, venture funds &mdash; and Menlo itself &mdash; as outside counsel.",
    'h-dubose-montgomery': "DuBose co-founded Menlo Ventures in 1976 and for nearly four decades led the firm&rsquo;s investments across medical and information technology, guiding it through every technology cycle from the microprocessor to the internet.",
}

for _slug, _data in PROFILE_DATA.items():
    PROFILES[_slug] = dict(blurb=BLURBS[_slug], investments=_data['investments'])

# hand corrections layered over the scraped data
STAGE_OVERRIDES = {
    'deedy-das': {
        'OpenRouter': 'Partnered at Seed &middot; Led the A',
        'Wispr Flow': 'Led the A',
        'Inception': 'Led the Seed',
        'Goodfire': 'Partnered at Seed &middot; Led the A',
    },
}
EXTRA_INVESTMENTS = {
    'deedy-das': [dict(name='Pangram', logo='pangram.png', founded='2023', stage='Led the Seed',
                       partnered='2026', about='AI-text detection that identifies AI-generated writing with state-of-the-art accuracy.')],
}
ROW_ORDER = {
    'deedy-das': ['Modal', 'Pangram', 'OpenRouter', 'Wispr Flow', 'Goodfire', 'Inception',
                  'Ndea', 'Prime Intellect', 'Fintool'],
}
for _slug, _ov in STAGE_OVERRIDES.items():
    for _row in PROFILES[_slug]['investments']:
        if _row['name'] in _ov:
            _row['stage'] = _ov[_row['name']]
for _slug, _extra in EXTRA_INVESTMENTS.items():
    PROFILES[_slug]['investments'] += _extra
for _slug, _order in ROW_ORDER.items():
    PROFILES[_slug]['investments'].sort(
        key=lambda r: _order.index(r['name']) if r['name'] in _order else len(_order))


# ---- Last Valuation column -------------------------------------------------
# Column renders only when the gitignored valuations.json is present, and only
# into the gitignored team/<slug>/local.html variants.
SHOW_LAST_VALUATION = bool(_VALS.get('last'))
LAST_VALUATIONS = _VALS.get('last', {})

# companies each partner led (board seat) — from their own menlovc.com bios,
# plus well-documented Menlo-led rounds. Everything else stays "Partnered".
LED = {
    'matt-murphy': {'Legora', 'Semgrep', 'Carta', 'Benchling', 'True Anomaly',
                    'Armadin', 'Grow Therapy', 'Netlify', 'Mimic', 'Envoy', 'Clarifai',
                    'Observable', 'Hover', 'Alloy', 'Relyance AI', 'Vivun', 'Zylo',
                    'Heap', '6 River Systems', 'Airbase', 'Canvas', 'Cleanlab',
                    'FireHydrant', 'Scout RFP', 'Usermind', 'Veriflow'},
    'venky-ganesan': {'Abnormal AI', 'Unravel', 'BitSight', 'Poshmark', 'Rover',
                      'Palo Alto Networks'},
    'shawn-carolan': {'Uber', 'Chime', 'Roku', 'JUMP'},
    'tim-tully': {'Neon', 'Eve', 'Pinecone'},
    'amy-wu-martin': {'ShopMy', 'Alta'},
    'jp-sanday': {'CollegeVine', 'Solace', 'OfferFit', 'H1', 'CodeSignal', 'Qualio'},
    'greg-yap': {'Cartwheel', 'Ophelia', 'Genesis Molecular AI', 'Delfi Diagnostics',
                 'Encoded Therapeutics', 'H1', 'Vilya', 'Xaira'},
    'croom-beatty': {'Abacus', 'NationGraph', 'Numeric', 'Prodigal', 'Finch', 'Arch'},
    'steve-sloane': {'Enable', 'Eleos Health', 'Chime', '6 River Systems'},
}

# user-established stage facts that also imply "led"
LED.setdefault('amy-wu-martin', set()).add('Suno')
LED.setdefault('amy-wu-martin', set()).add('Higgsfield')

for _slug, _names in LED.items():
    if _slug not in PROFILES:
        continue
    for _row in PROFILES[_slug]['investments']:
        if _row['name'] in _names and _row['stage'].startswith('Partnered at '):
            _row['stage'] = _row['stage'].replace('Partnered at ', 'Led the ', 1)
        elif _row['name'] in _names and _row['stage'].startswith('Partnered ('):
            _row['stage'] = _row['stage'].replace('Partnered (', 'Led (', 1)


# curated one-liners — complete sentences that fit the About column
ABOUTS = {
    '6 River Systems': 'Autonomous mobile robots that make warehouse fulfillment more efficient.',
    'AVI Networks': 'Software load balancing for enterprise and cloud applications.',
    'Abacus': 'Intelligent document processing that ends manual data entry for tax firms.',
    'Abnormal AI': 'AI-native email security that stops human-targeted attacks.',
    'Alta': 'A personal AI stylist for stress-free, well-dressed mornings.',
    'Arch': 'Digital admin infrastructure for managing private investments.',
    'Atta': 'AI agents for modeling data, finding patterns, and forecasting.',
    'Axiom': 'Building a self-improving AI reasoner, starting with mathematics.',
    'BeHeard': 'Turns boring surveys into continuous conversations with brands.',
    'Benchling': 'The R&amp;D cloud powering modern life-science discovery.',
    'BitSight': 'Objective, evidence-based security ratings for managing cyber risk.',
    'Brain Jar Games': 'AAA veterans crafting vibrant games players love to share.',
    'Cartwheel': 'Tech-enabled youth mental health care for schools and families.',
    'Chime': 'Fee-free banking that helps members save automatically.',
    'CloudTrucks': 'Helps owner-operators book loads instantly and get paid faster.',
    'CodeSignal': 'AI-native skills platform for hiring, training, and growing talent.',
    'CollegeVine': 'AI agents that streamline university operations and recruitment.',
    'Delfi Diagnostics': 'Early cancer detection from blood using machine learning.',
    'Delphi': 'Turns your expertise into a 24/7 digital mind that teaches and advises.',
    'Eleos Health': 'Clinical AI that turns behavioral-health conversations into documentation.',
    'Enable': 'Collaborative rebate management for B2B trading partners.',
    'Encoded Therapeutics': 'Precision gene therapies driven by genomics.',
    'Eve': 'Legal AI built for the full plaintiff case lifecycle.',
    'Finch': 'One API for payroll and HR systems across hundreds of providers.',
    'Fintool': 'A financial copilot for public-equity investors.',
    'Flapping Airplanes': 'Foundational AI research lab focused on data efficiency.',
    'Fleet AI': 'Simulated worlds for understanding and shaping AI behavior.',
    'Genesis Molecular AI': 'Foundation models unlocking a new era of drug design.',
    'Gimlet Labs': 'Serverless inference for AI agents, from scheduling to optimization.',
    'Good Job Games': 'Fun, challenging games crafted with attention to perfection.',
    'Goodfire': 'AI interpretability lab designing understandable AI systems.',
    'Graphite': 'AI developer platform for smaller, faster code reviews.',
    'H1': 'Health data platform connecting medicine&rsquo;s development lifecycle.',
    'Harness': 'AI-native software delivery for modern engineering teams.',
    'Heaviside Industries': 'Precise, affordable autonomous drones across air, land, and sea.',
    'Higgsfield': 'Video AI democratizing social content creation.',
    'Inception': 'Diffusion-based LLMs that are faster and more efficient.',
    'Lovable': 'Turns natural language into production-ready web applications.',
    'Medra': 'Physical AI systems collecting life-science data at superhuman scale.',
    'Mercor': 'AI-powered hiring that matches talent to the right opportunities.',
    'Modal': 'Serverless compute for ML and other intensive workloads.',
    'Monarch': 'Money management for planning, budgeting, and tracking goals.',
    'NationGraph': 'AI sales intelligence for winning public-sector business.',
    'Ndea': 'Frontier AI blending pattern recognition with formal reasoning.',
    'Neon': 'Serverless Postgres built for edge and AI workloads.',
    'Numeric': 'AI accounting automation that takes busywork off accountants&rsquo; plates.',
    'Observe.AI': 'Conversation intelligence for analyzing every customer service call.',
    'OfferFit': 'Automated ML experimentation for lifecycle marketers.',
    'Okthx': 'A coordination assistant that handles scheduling for working parents.',
    'OpenHands AI': 'Open-source platform for autonomous software engineering.',
    'OpenRouter': 'One API for hundreds of frontier and open AI models.',
    'OpenSpace': '360&deg; photo documentation and insights for construction sites.',
    'Ophelia': 'Private, affordable addiction treatment via telemedicine.',
    'Peregrine': 'Data integration and analysis software for public safety.',
    'Phylo': 'Agentic intelligence accelerating biomedical discovery.',
    'Pinecone': 'Managed vector database powering high-performance AI apps.',
    'Poshmark': 'Social marketplace for new and secondhand fashion.',
    'Prime Intellect': 'Democratizing AI development with global compute and training.',
    'Prodigal': 'Conversational AI insights for lenders and collections.',
    'Recursion': 'Industrializing drug discovery with automation and ML.',
    'Redfin': 'Technology-powered real estate brokerage.',
    'Rivet Health': 'Healthcare payments software that helps practices get paid.',
    'Roku': 'The streaming-TV platform connecting viewers, content, and advertisers.',
    'Rover': 'Connects pet parents with trusted sitters and dog walkers.',
    'RunSybil': 'AI-powered offensive security that continuously tests your defenses.',
    'Sana': 'AI learning platform for finding and sharing organizational knowledge.',
    'Scout RFP': 'Cloud strategic sourcing that streamlines supplier selection.',
    'ShipBob': 'Fast, affordable e-commerce fulfillment for DTC brands.',
    'ShopMy': 'Where brands, creators, and consumers meet to shop trusted picks.',
    'Slingshot AI': 'AI research expanding global access to mental healthcare.',
    'Solace': 'Connects Medicare patients with certified healthcare advocates.',
    'Squint': 'Manufacturing intelligence that lowers downtime on the factory floor.',
    'Suno': 'AI music creation for everyone &mdash; interactive, social, participatory.',
    'Trove AI': 'AI agents that supercharge research and drafting for private equity.',
    'Unravel': 'Full-stack performance intelligence for big-data operations.',
    'Unstructured': 'Transforms messy files into LLM-ready structured data.',
    'Westmag': 'American-made drone motors and robot actuators.',
    'WisdomAI': 'Conversational AI for expert-level insights from business data.',
    'Wispr Flow': 'A voice keyboard with effortless AI dictation in every app.',
    'Zafran Security': 'AI-native threat exposure management for security teams.',
}

SOCIALS = json.load(open('partner-socials.json'))
EMAIL_FIRST = {'h-dubose-montgomery': 'dubose'}

ICON_LI = '<svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z"/></svg>'
ICON_X = '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.66l-5.21-6.82-5.97 6.82H1.67l7.73-8.84L1.25 2.25h6.83l4.71 6.23 5.45-6.23zm-1.16 17.52h1.83L7.08 4.13H5.12l11.96 15.64z"/></svg>'
ICON_MAIL = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M3.5 6.5 12 13l8.5-6.5"/></svg>'


def social_row(slug):
    s = SOCIALS.get(slug, {})
    first = EMAIL_FIRST.get(slug, slug.split('-')[0])
    links = []
    if s.get('linkedin'):
        links.append(f'<a href="{s["linkedin"]}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICON_LI}</a>')
    if s.get('x'):
        links.append(f'<a href="{s["x"]}" target="_blank" rel="noopener" aria-label="X">{ICON_X}</a>')
    links.append(f'<a href="mailto:{first}@menlovc.com" aria-label="Email">{ICON_MAIL}</a>')
    return '<div class="p-social">' + '\n        '.join(links) + '</div>'


def clip_about(text, limit=95):
    plain = text
    if len(plain) <= limit:
        return text
    cut = plain[:limit].rsplit(' ', 1)[0].rstrip(',;:')
    return cut + '&hellip;'

PROFILE_CSS = '''<style>
  .pnav { text-align: center; padding: 30px 24px 6px; }
  .pnav img { width: 120px; height: auto; }
  .profile {
    max-width: 980px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 0.92fr 1.08fr;
    gap: 48px;
    align-items: center;
    padding: 24px 24px 20px;
  }
  .p-photo {
    margin-left: -46px;
    opacity: 0;
    animation: rise 0.9s cubic-bezier(0.19, 1, 0.22, 1) 0.15s forwards;
  }
  .p-photo img { width: 100%; height: auto; display: block; }
  .p-info { opacity: 0; animation: rise 0.9s cubic-bezier(0.19, 1, 0.22, 1) 0.3s forwards; }
  .p-name {
    font-family: var(--serif);
    font-weight: 400;
    font-size: clamp(34px, 4.4vw, 48px);
    line-height: 1.05;
    margin-top: 8px;
  }
  .p-blurb {
    margin-top: 18px;
    font-family: var(--sans);
    font-weight: 500;
    font-size: 14px;
    line-height: 1.65;
    color: rgba(10, 10, 10, 0.78);
    max-width: 30em;
  }
  .p-table-wrap {
    max-width: 980px;
    margin: 0 auto;
    padding: 18px 24px 90px;
    overflow-x: auto;
    opacity: 0;
    animation: rise 0.9s cubic-bezier(0.19, 1, 0.22, 1) 0.45s forwards;
  }
  .p-table { width: 100%; min-width: 680px; border-collapse: collapse; }
  .p-table th {
    font-family: var(--mono);
    font-size: 8px;
    font-weight: 500;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--faint);
    text-align: left;
    padding: 10px 14px 10px 4px;
    border-bottom: 1px solid var(--ink);
  }
  .p-table td {
    padding: 16px 14px 16px 4px;
    border-bottom: 1px solid var(--hairline);
    vertical-align: middle;
  }
  .p-logo img {
    display: block;
    max-height: 22px;
    max-width: 118px;
    width: auto;
    height: auto;
    filter: brightness(0);
    opacity: 0.8;
    transition: filter 0.3s ease, opacity 0.3s ease;
  }
  .p-table tr:hover .p-logo img { filter: none; opacity: 1; }
  .p-year { font-family: var(--mono); font-size: 10px; color: var(--faint); white-space: nowrap; }
  .p-stage { font-family: var(--sans); font-size: 12px; font-weight: 700; white-space: nowrap; }
  .p-stage .dot { color: var(--accent); }
  .p-about { font-family: var(--sans); font-size: 12.5px; font-weight: 500; line-height: 1.5; color: rgba(10, 10, 10, 0.62); max-width: 330px; }
  .p-table tr.more-row.is-hidden { display: none; }
  .p-val { font-family: var(--sans); font-size: 11.5px; font-weight: 700; letter-spacing: 0.04em; white-space: nowrap; padding-right: 14px; }
  .p-logo img.raw { filter: grayscale(1); opacity: 0.9; }
  .p-social { display: flex; gap: 15px; align-items: center; margin-top: 20px; }
  .p-social a { color: rgba(10, 10, 10, 0.4); display: inline-flex; transition: color 0.3s ease; }
  .p-social a:hover { color: var(--accent); }
  @media (max-width: 760px) { .p-social { justify-content: center; } }
  .p-more { margin-top: 22px; }
  @media (max-width: 760px) {
    .profile { grid-template-columns: 1fr; gap: 8px; padding-top: 8px; }
    .p-photo { margin-left: 0; max-width: 320px; justify-self: center; }
    .p-info { text-align: center; }
    .p-blurb { margin-left: auto; margin-right: auto; }
  }
</style>'''


def profile_page(slug, person, prof, with_val=False):
    name = html.escape(person['name'])
    rows = []
    has_more = False
    for c in prof['investments']:
        cls = ''
        if c.get('more'):
            cls = ' class="more-row is-hidden"'
            has_more = True
        img_cls = ' class="raw"' if c['logo'] in RAW_LOGOS else ''
        about = ABOUTS.get(c['name'], c['about'])
        val_td = ''
        if with_val:
            val_td = f'\n          <td class="p-val">{LAST_VALUATIONS.get(c["name"], "&mdash;")}</td>'
        rows.append(f'''        <tr{cls}>
          <td class="p-logo"><img{img_cls} src="../../assets/logos/{c['logo']}" alt="{html.escape(c['name'])}" title="{html.escape(c['name'])}"></td>
          <td class="p-year">{c['founded']}</td>
          <td class="p-stage">{c['stage'].replace(' &middot; ', ' <span class="dot">&middot;</span> ')}</td>
          <td class="p-year">{c['partnered']}</td>{val_td}
          <td class="p-about">{clip_about(about)}</td>
        </tr>''')
    rows_html = '\n'.join(rows)
    more_html = ''
    if has_more:
        more_html = '''
    <p class="see-portfolio p-more"><a href="#" id="seeMore">
      <span>See more</span>
      <svg class="chev" width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </a></p>
    <script>
      document.getElementById('seeMore').addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.p-table tr.more-row').forEach((r) => r.classList.remove('is-hidden'));
        e.currentTarget.closest('.p-more').remove();
      });
    </script>'''
    table_html = ''
    if rows:
        table_html = f'''
  <section class="p-table-wrap">
    <table class="p-table">
      <thead>
        <tr><th>Company</th><th>Founded</th><th>Stage</th><th>Partnered</th>{'<th>Last Val.</th>' if with_val else ''}<th>About</th></tr>
      </thead>
      <tbody>
{rows_html}
      </tbody>
    </table>{more_html}
  </section>'''
    head_t = head_p.replace('<title>Menlo Ventures — Portfolio</title>',
                            f'<title>{name} — Menlo Ventures</title>')
    return f'''<!doctype html>
<html lang="en">
<head>{head_t}
{PROFILE_CSS}</head>
<body>

  <header class="pnav">
    <a href="../../" aria-label="Back to home"><img src="../../assets/menlo-logo.png" alt="Menlo Ventures"></a>
  </header>

  <section class="profile">
    <figure class="p-photo">
      <img src="../../assets/partners/{slug}-hover.jpg" alt="Watercolor portrait of {name}">
    </figure>
    <div class="p-info">
      <p class="eyebrow">{html.escape(person['title'])}</p>
      <h1 class="p-name">{name}</h1>
      <p class="p-blurb">{prof['blurb']}</p>
      {social_row(slug)}
    </div>
  </section>

{table_html}

</body>
</html>
'''


for slug, prof in PROFILES.items():
    person = slug_map[slug]
    os.makedirs(f'team/{slug}', exist_ok=True)
    open(f'team/{slug}/index.html', 'w').write(profile_page(slug, person, prof))
    if SHOW_LAST_VALUATION:
        open(f'team/{slug}/local.html', 'w').write(profile_page(slug, person, prof, with_val=True))
print(f'{len(PROFILES)} profile pages written (+ local valuation variants: {SHOW_LAST_VALUATION})')
total = sum(len(v) for v in by_cat.values())
print(f'index.html + local.html written — {total} people: ' +
      ', '.join(f'{label} {len(by_cat[key])}' for key, label in CATEGORIES))
