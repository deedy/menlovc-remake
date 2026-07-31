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
            logos.append(f'        <li><img src="assets/logos/{fname}" alt="{cname}" title="{cname}" loading="lazy"></li>')
    inv_block = ''
    if logos:
        inv_block = (f'\n        <ul class="investments" aria-label="Selected investments of {name}">\n'
                     + '\n'.join(logos) + '\n        </ul>')
    hover_path = f"assets/partners/{p['slug']}-hover.jpg"
    hover_html = (f'\n          <img class="alt" src="{hover_path}" alt="" aria-hidden="true" loading="lazy">'
                  if os.path.exists(hover_path) else '')
    return f'''      <article class="partner" style="--i:{i}">
        <figure class="portrait">
          <img src="assets/partners/{p['slug']}.jpg" alt="Ink line portrait of {name}" loading="lazy">{hover_html}
        </figure>
        <h2 class="name">{name}</h2>
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

# hero logo grid: (name, logo file, round note, website, valuation, is_public, desktop_only)
# valuations render ONLY into local.html (gitignored) — never into the deployed index.html
FOLIO = [
    ('Anthropic', 'anthropic.svg', 'Partnered at C, Led the D', 'https://www.anthropic.com', '$965B', False, False),
    ('OpenRouter', 'openrouter2026.svg', 'Partnered at Seed, Led the A', 'https://openrouter.ai', 'Acq. by Stripe at $8B', False, False),
    ('Lovable', 'lovable.svg', 'Led the B', 'https://lovable.dev', '$13B', False, False),
    ('Suno', 'suno.svg', 'Led the C', 'https://suno.com', '$5.4B', False, False),
    ('Wispr Flow', 'wispr_flow.svg', 'Led the Seed, A', 'https://wisprflow.ai', '$2B', False, False),
    ('Higgsfield', 'higgsfield.webp', 'Led the Seed', 'https://higgsfield.ai', '$5B', False, False),
    ('Gimlet', 'gimlet_labs.png', 'Led the A', 'https://gimletlabs.ai', '$3.5B', False, False),
    ('Uber', 'uber.png', 'Led the B', 'https://www.uber.com', '$100B+', True, False),
    ('Mercor', 'mercor.png', 'Partnered at B', 'https://mercor.com', '$20B', False, True),
    ('Chai Discovery', 'chai_discovery.svg', 'Led the A', 'https://www.chaidiscovery.com', '$3.8B', False, True),
    ('Databricks', 'databricks.png', 'Sold Neon', 'https://www.databricks.com', '$1B', False, True),
    ('Cursor', 'cursor.svg', 'Sold Graphite', 'https://cursor.com', '~$1B', False, True),
]


def folio_grid(with_valuations):
    items = []
    for name, logo, note, url, val, is_public, desktop_only in FOLIO:
        note_html = html.escape(note).replace(', ', ' <span class="dot">&middot;</span> ')
        val_html = ''
        if with_valuations and val:
            pub = ' <sup class="pub" title="Public company">&#9650;</sup>' if is_public else ''
            val_html = f'\n        <span class="folio-val">{html.escape(val)}{pub}</span>'
        cls = ' class="desktop-only"' if desktop_only else ''
        items.append(f'''      <li{cls}><a href="{url}" target="_blank" rel="noopener">
        <img src="assets/logos/{logo}" alt="{html.escape(name)}" loading="lazy">
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
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #0a0a0a;
    --accent: #FF8304;
    --paper: #ffffff;
    --hairline: rgba(10, 10, 10, 0.18);
    --faint: rgba(10, 10, 10, 0.55);
    --serif: "Instrument Serif", Georgia, "Times New Roman", serif;
    --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
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
    height: 60px;
    padding-bottom: 24px;
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
    bottom: 12px;
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
    bottom: 1px;
    left: 0;
    right: 0;
    text-align: center;
    font-family: var(--mono);
    font-size: 7px;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
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
    .folio-grid a {{ height: 50px; }}
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
  </header>

  <section class="folio" aria-label="Selected investments">
    <ul class="folio-grid">
{folio_html}
    </ul>
  </section>

  <nav class="tabs" role="tablist" aria-label="Team categories">
{tabs_html}
  </nav>

  <main class="partners" id="partners">
{grids_html}
  </main>

  <script>
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
total = sum(len(v) for v in by_cat.values())
print(f'index.html + local.html written — {total} people: ' +
      ', '.join(f'{label} {len(by_cat[key])}' for key, label in CATEGORIES))
