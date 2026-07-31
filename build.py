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

tabs_html = '\n'.join(
    f'      <button class="tab{" is-active" if key == "partners" else ""}" data-cat="{key}" role="tab" '
    f'aria-selected="{"true" if key == "partners" else "false"}">{label}</button>'
    for key, label in CATEGORIES)

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Menlo Ventures — The Team</title>
<meta name="description" content="Menlo Ventures. Venture capital since 1976. The team and the companies they back.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='white'/%3E%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='22' text-anchor='middle' fill='black'%3EM%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #0a0a0a;
    --paper: #ffffff;
    --hairline: rgba(10, 10, 10, 0.18);
    --faint: rgba(10, 10, 10, 0.55);
    --serif: "Instrument Serif", Georgia, "Times New Roman", serif;
    --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  html {{ scroll-behavior: smooth; }}

  body {{
    background: var(--paper);
    color: var(--ink);
    font-family: var(--serif);
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }}

  /* ---------- paper grain ---------- */
  body::after {{
    content: "";
    position: fixed;
    inset: 0;
    z-index: 40;
    pointer-events: none;
    opacity: 0.05;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='240' height='240' filter='url(%23n)'/%3E%3C/svg%3E");
  }}

  .eyebrow {{
    font-family: var(--mono);
    font-size: 11px;
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
    padding: 64px 24px 40px;
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
    width: min(340px, 72vw);
    height: auto;
    display: block;
  }}

  .est {{
    margin-top: 26px;
    color: var(--ink);
  }}

  .cities {{
    margin-top: 12px;
  }}

  /* ---------- category tabs ---------- */
  .tabs {{
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 14px 34px;
    padding: 8px 24px 40px;
    opacity: 0;
    animation: rise 0.9s cubic-bezier(0.19, 1, 0.22, 1) 0.5s forwards;
  }}
  .tab {{
    appearance: none;
    background: none;
    border: none;
    cursor: pointer;
    font-family: var(--mono);
    font-size: 11px;
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
    border-bottom-color: var(--ink);
  }}

  @keyframes rise {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: none; }}
  }}

  /* ---------- team grid ---------- */
  .partners {{
    max-width: 1240px;
    margin: 0 auto;
    padding: 0 32px 120px;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    column-gap: 56px;
    row-gap: 48px;
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
    filter: grayscale(1) contrast(1.04);
  }}
  .portrait img.alt {{
    position: absolute;
    inset: 0;
    opacity: 0;
    filter: none;
    transition: opacity 0.5s ease, transform 1.1s cubic-bezier(0.19, 1, 0.22, 1);
  }}
  .partner:hover .portrait img {{ transform: scale(1.07); }}
  .partner:hover .portrait img.alt {{ opacity: 1; }}

  .name {{
    font-size: 30px;
    font-weight: 400;
    letter-spacing: 0.01em;
    margin-top: 14px;
    line-height: 1.1;
    text-align: center;
  }}

  .role {{
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--faint);
    margin-top: 7px;
    text-align: center;
  }}

  .investments {{
    list-style: none;
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: 14px;
    margin-top: 16px;
    min-height: 22px;
  }}
  .investments li {{
    flex: 1 1 0;
    min-width: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .investments img {{
    display: block;
    width: auto;
    height: auto;
    max-height: 14px;
    max-width: 100%;
    object-fit: contain;
    filter: brightness(0);
    opacity: 0.7;
    transition: opacity 0.3s ease;
  }}
  .investments li:hover img {{ opacity: 1; }}

  /* ---------- footer ---------- */
  footer {{
    border-top: 1px solid var(--ink);
    max-width: 1240px;
    margin: 0 auto;
    padding: 20px 32px 60px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 16px;
    flex-wrap: wrap;
  }}
  footer .colophon {{
    font-style: italic;
    font-size: 15px;
    color: var(--faint);
  }}

  /* grid shows 3 columns from ~1017px up; center lone cards there */
  @media (min-width: 1017px) {{
    .grid.center-last > .partner:last-child {{ grid-column: 2; }}
    .grid.first-center > .partner:first-child {{ grid-column: 2; }}
    .grid.first-center > .partner:nth-child(2) {{ grid-column: 1; }}
  }}

  @media (max-width: 640px) {{
    .grid {{ row-gap: 44px; }}
    .partners {{ padding: 0 20px 100px; }}
    footer {{ padding: 20px 20px 48px; }}
    .name {{ font-size: 26px; }}
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
    <p class="eyebrow cities">Menlo Park, California &nbsp;&middot;&nbsp; San Francisco, California</p>
  </header>

  <nav class="tabs" role="tablist" aria-label="Team categories">
{tabs_html}
  </nav>

  <main class="partners" id="partners">
{grids_html}
  </main>

  <footer>
    <p class="eyebrow">Menlo Ventures</p>
    <p class="colophon">Portraits drawn in ink, after the originals. A draft study.</p>
  </footer>

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
total = sum(len(v) for v in by_cat.values())
print(f'index.html written — {total} people: ' +
      ', '.join(f'{label} {len(by_cat[key])}' for key, label in CATEGORIES))
