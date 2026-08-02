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
    managing = ' managing' if p['title'] == 'Managing Partner' else ''
    return f'''      <article class="partner{managing}" style="--i:{i}">
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

# hero logo grid. `val` and `note_local` render ONLY into local.html (gitignored) —
# no dollar figure ever reaches the deployed index.html.
FOLIO = [
    dict(name='Anthropic', logo='anthropic.svg', note='Partnered at C, Led the D', url='https://www.anthropic.com', val='$965B'),
    dict(name='OpenRouter', logo='openrouter2026.svg', note='Partnered at Seed, Led the A', url='https://openrouter.ai', val='Acq. by Stripe at $8B'),
    dict(name='Lovable', logo='lovable.svg', note='Led the B', url='https://lovable.dev', val='$13B'),
    dict(name='Suno', logo='suno.svg', note='Led the C', url='https://suno.com', val='$5.4B'),
    dict(name='Wispr Flow', logo='wispr_flow.svg', note='Led the Seed, A', url='https://wisprflow.ai', val='$2B'),
    dict(name='Higgsfield', logo='higgsfield.webp', note='Led the Seed', url='https://higgsfield.ai', val='$5B'),
    dict(name='Gimlet', logo='gimlet_labs.png', note='Led the A', url='https://gimletlabs.ai', val='$3.5B'),
    dict(name='Uber', logo='uber.png', note='Led the B', url='https://www.uber.com', val='$100B+', is_public=True),
    dict(name='Mercor', logo='mercor.png', note='Partnered at B', url='https://mercor.com', val='$20B', desktop_only=True),
    dict(name='Chai Discovery', logo='chai_discovery.svg', note='Led the A', url='https://www.chaidiscovery.com', val='$3.8B', desktop_only=True),
    dict(name='Databricks', logo='databricks.png', note='Bought Neon', note_local='Bought Neon for $1B', url='https://www.databricks.com', val='~$134B', desktop_only=True),
    dict(name='Cursor', logo='cursor.svg', note='Bought Graphite', note_local='Bought Graphite for ~$1B', url='https://cursor.com', val='~$29B', desktop_only=True),
]


def folio_grid(with_valuations):
    items = []
    for c in FOLIO:
        note = c.get('note_local', c['note']) if with_valuations else c['note']
        note_html = html.escape(note).replace(', ', ' <span class="dot">&middot;</span> ')
        val_html = ''
        if with_valuations and c.get('val'):
            pub = ' <sup class="pub" title="Public company">&#9650;</sup>' if c.get('is_public') else ''
            val_html = f'\n        <span class="folio-val">{html.escape(c["val"])}{pub}</span>'
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
total = sum(len(v) for v in by_cat.values())
print(f'index.html + local.html written — {total} people: ' +
      ', '.join(f'{label} {len(by_cat[key])}' for key, label in CATEGORIES))
