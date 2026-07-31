#!/usr/bin/env python3
"""Portrait stylizer for the Menlo team page, via Gemini nano banana pro.

Usage: python3 scripts/stylize.py <mode> <src.jpg> <dst.jpg> [color_ref.jpg]

Modes:
  clean           photo -> black ink anime line art (no solid black fills)
  clean-nobg      same, but strips desks/laptops/doors/background objects
  inverse         line art -> solid black figure with white interior lines
  remove-objects  surgical edit: erase leftover object lines, change nothing else
  color           line art + original photo (4th arg) -> watercolor hover variant

Reads GEMINI_API_KEY from the repo's .env (gitignored). Resize sources to
~900px first (sips -Z 900). Outputs are JPEG regardless of extension.

Post-process every output before installing into assets/partners/:
  1. white/black-point normalization (line art: L 30/235; color: RGB 20/240)
  2. border-connected flood-fill to force pure #FFFFFF backgrounds
Hover variants use the <slug>-hover.jpg convention; build.py picks them up.
"""
import base64, json, os, subprocess, sys, time

ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')
API_KEY = None
with open(ENV_PATH) as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            API_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
assert API_KEY, f'GEMINI_API_KEY not found in {ENV_PATH}'

MODEL = 'gemini-3-pro-image-preview'
URL = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent'

PROMPTS = {
    'clean': (
        "Redraw this exact portrait as minimalist anime line art. "
        "Requirements: pure white background (#FFFFFF), clean confident dark black ink "
        "lines only — no color, no gray shading, no crosshatching, no screentones. "
        "CRITICAL: absolutely no solid black filled areas anywhere. Hair must be drawn "
        "as white with sparse individual black line strokes for structure — never filled in. "
        "Preserve the person's likeness faithfully: face shape, hairstyle, glasses if any, "
        "expression, and pose. Elegant Japanese manga pen-and-ink style, sparse lines, "
        "lots of white space."
    ),
    'inverse': (
        "Transform this black-line-on-white ink drawing into its exact negative twin: "
        "fill the entire figure — hair, face, skin, clothing — with solid black ink, and "
        "redraw every interior detail line (facial features, hair strands, clothing folds) "
        "as clean white lines on the black figure. The background outside the figure's "
        "silhouette must remain pure white (#FFFFFF) — no frame, no border, no background "
        "shapes, no vignette. Keep the composition, pose, scale, and every contour exactly "
        "identical to the input image so the two images overlay perfectly. "
        "Striking minimalist white-on-black ink style."
    ),
    'clean-nobg': (
        "Redraw this exact portrait as minimalist anime line art. "
        "Requirements: pure white background (#FFFFFF), clean confident dark black ink "
        "lines only — no color, no gray shading, no crosshatching, no screentones. "
        "CRITICAL: draw ONLY the person — absolutely no background or foreground objects: "
        "no door, no walls, no furniture, no desk, no table, no chair, no laptop, no "
        "computer, no notebook, no lines or shapes behind or in front of the figure. "
        "The figure stands alone on empty white. No solid black filled areas; hair drawn "
        "as sparse individual line strokes. Preserve the person's likeness faithfully: "
        "face shape, hairstyle, glasses if any, expression, and pose. Elegant Japanese "
        "manga pen-and-ink style, sparse lines, lots of white space."
    ),
    'remove-objects': (
        "This is a black-and-white ink line drawing of a person. Edit it to remove every "
        "remaining non-person element: any laptop edge, screen corner, table edge, desk "
        "line, or stray diagonal line in the corners, at the bottom, or in front of the "
        "figure. Seamlessly close or extend the figure's contour lines where an object "
        "overlapped them. Change absolutely nothing else — identical face, pose, "
        "hairstyle, clothing, line weight, and composition, pure white background."
    ),
    'color': (
        "The first image is a black-and-white anime line drawing. The second image is the "
        "original photograph of the same person, provided only as a color reference. "
        "Color the line drawing in a soft, muted watercolor-anime style: delicate flat "
        "washes of color for skin, hair, and clothing, matching the real colors from the "
        "photograph but softened and desaturated — gentle, airy, elegant. Keep every black "
        "ink line, the composition, pose, scale, and all contours exactly identical to the "
        "first image so the two overlay perfectly. The background outside the figure must "
        "remain pure white (#FFFFFF) — no frame, no border, no background washes, no shadow. "
        "Understated Japanese watercolor illustration style, lots of white space."
    ),
}

def stylize(mode, src, dst, ref=None, retries=3):
    parts = [{'text': PROMPTS[mode]},
             {'inline_data': {'mime_type': 'image/jpeg',
                              'data': base64.b64encode(open(src, 'rb').read()).decode()}}]
    if ref:
        parts.append({'inline_data': {'mime_type': 'image/jpeg',
                                      'data': base64.b64encode(open(ref, 'rb').read()).decode()}})
    payload = {
        'contents': [{'parts': parts}],
        'generationConfig': {
            'responseModalities': ['IMAGE'],
            'imageConfig': {'aspectRatio': '1:1', 'imageSize': '1K'},
        },
    }
    pf = dst + '.payload.json'
    json.dump(payload, open(pf, 'w'))
    for attempt in range(retries):
        r = subprocess.run(
            ['curl', '-s', '-X', 'POST', URL,
             '-H', 'Content-Type: application/json',
             '-H', f'x-goog-api-key: {API_KEY}',
             '-d', f'@{pf}'],
            capture_output=True, timeout=300)
        try:
            resp = json.loads(r.stdout)
        except json.JSONDecodeError:
            time.sleep(5); continue
        if 'error' in resp:
            print(f"{src}: API error {resp['error'].get('code')}: {resp['error'].get('message','')[:200]}", file=sys.stderr)
            time.sleep(10 * (attempt + 1)); continue
        parts = resp.get('candidates', [{}])[0].get('content', {}).get('parts', [])
        img = next((p['inlineData'] for p in parts if 'inlineData' in p), None)
        if img:
            open(dst, 'wb').write(base64.b64decode(img['data']))
            os.remove(pf)
            return True
        print(f'{src}: no image: {json.dumps(resp)[:300]}', file=sys.stderr)
        time.sleep(5)
    return False

if __name__ == '__main__':
    mode, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    ref = sys.argv[4] if len(sys.argv) > 4 else None
    if stylize(mode, src, dst, ref):
        print(f'ok {dst}')
    else:
        print(f'FAILED {src}')
        sys.exit(1)
