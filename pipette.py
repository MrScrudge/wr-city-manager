"""Pipette for W&R Калькулятор: grab a screen area with a building window from the game, read
'production per workday' and 'consumption' (resource icons + numbers), convert to per year.

Reading:  OCR (RapidOCR, numbers and English text) -> item boxes that start with a number and have a resource icon on their
          left; the icon is classified against the game's resource icons; English names ('of Crops') are used when present.
Sections: every item belongs to the nearest RED header above it (game headers are red in any UI language);
          'consum'/'спожив' -> needs, otherwise the first header with items = production, the next = needs.
"""
import os, re, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
import wr_paths                                                          # noqa: E402  (the game's icons: wr_paths.game_dir())
GI = os.path.join(wr_paths.game_dir(), 'gameicons')
SKIP_ICONS = {'workers', 'colorwater'}
UTILITY = {'water', 'eletric', 'heat', 'usagewater'}                 # shown, but not counted by default (user: only resources)

EN = {  # English game names -> resource id
    'alcohol': 'alcohol', 'crops': 'plants', 'plants': 'plants', 'water': 'water', 'clean water': 'water', 'power': 'eletric',
    'electricity': 'eletric', 'heat': 'heat', 'heating': 'heat', 'food': 'food', 'meat': 'meat', 'clothes': 'clothes',
    'fabric': 'fabric', 'livestock': 'livestock', 'electronics': 'eletronics', 'electrical components': 'ecomponents',
    'electronic components': 'ecomponents', 'electric components': 'ecomponents', 'mechanical components': 'mcomponents',
    'steel': 'steel', 'iron ore': 'iron', 'iron': 'iron', 'raw iron': 'rawiron', 'raw iron ore': 'rawiron', 'coal': 'coal',
    'raw coal': 'rawcoal', 'gravel': 'gravel', 'raw gravel': 'rawgravel', 'concrete': 'concrete', 'cement': 'cement',
    'bricks': 'bricks', 'boards': 'boards', 'wood': 'wood', 'prefab panels': 'prefabpanels', 'prefabricated panels': 'prefabpanels',
    'asphalt': 'asphalt', 'bitumen': 'bitumen', 'oil': 'oil', 'crude oil': 'oil', 'fuel': 'fuel', 'chemicals': 'chemicals',
    'plastics': 'plastics', 'plastic': 'plastics', 'aluminium': 'aluminium', 'aluminum': 'aluminium', 'alumina': 'alumina',
    'bauxite': 'bauxite', 'raw bauxite': 'rawbauxite', 'uranium': 'uranium', 'uranium ore': 'uranium', 'yellowcake': 'yellowcake',
    'uf6': 'uf6', 'nuclear fuel': 'nuclearfuel', 'spent nuclear fuel': 'nuclearfuelburned', 'nuclear waste': 'nuclearfuelburned',
    'explosives': 'explosives', 'fertilizer': 'fertiliser', 'fertiliser': 'fertiliser', 'liquid fertilizer': 'fertiliser_liquid',
    'vehicles': 'vehicles', 'sewage': 'usagewater', 'waste water': 'usagewater', 'wastewater': 'usagewater',
    'waste': 'waste_mixed', 'mixed waste': 'waste_mixed', 'toxic waste': 'waste_toxic', 'ash': 'waste_ash',
}

_OCR = None
_TPL = None
PACK_FILE = os.path.join(HERE, 'assets', 'resource_pack.json')       # names of the resources buildings use
ICON_DIRS = [GI]                                                    # their icons are the game's resource icons
IGNORE_KNOWN = ('water', 'eletric', 'heat', 'usagewater')           # recognised only to be left out
NOT_RESOURCES = {'workers', 'colorwater', 'bus', 'busstop'}


def ocr_engine():
    global _OCR
    if _OCR is None:
        from rapidocr_onnxruntime import RapidOCR          # installed by the launcher; imported lazily
        _OCR = RapidOCR()
    return _OCR


def templates():
    """resource id -> RGBA icon (trimmed), from the game's resource icons (only those named in resource_pack.json)"""
    global _TPL
    if _TPL is None:
        _TPL = {}
        allowed = None
        try:
            allowed = set(json.load(open(PACK_FILE, encoding='utf-8'))) | set(IGNORE_KNOWN)
        except (OSError, ValueError):
            pass
        for d in ICON_DIRS:
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                k = f[:-4]
                if allowed is not None and k not in allowed:
                    continue
                if f.endswith('.png') and k not in NOT_RESOURCES and k not in _TPL:
                    im = Image.open(os.path.join(d, f)).convert('RGBA')
                    bb = im.getbbox()
                    if bb:
                        _TPL[k] = im.crop(bb)
    return _TPL


_SCALED = {}


def scaled(key, h, bg):
    """icon scaled to height h and composited over the window background colour bg (no alpha left)"""
    ck = (key, h, tuple(int(c) // 8 for c in bg))
    if ck not in _SCALED:
        t = templates()[key]
        k = h / max(t.size)
        tp = t.resize((max(4, round(t.width * k)), max(4, round(t.height * k))), Image.LANCZOS)
        a = np.asarray(tp).astype(np.float32)
        al = a[..., 3:4] / 255.0
        _SCALED[ck] = np.ascontiguousarray((a[..., :3] * al + np.array(bg, np.float32) * (1 - al)).clip(0, 255).astype(np.uint8))
    return _SCALED[ck]


ICON_OK = 0.84          # measured on game windows: real icons 0.86-0.96, look-alikes (UI grey boxes) <= 0.79


def find_icons(img, y0, y1, h_text, thr=ICON_OK):
    """all resource icons in the horizontal band [y0, y1) -> [(x, w, key, score)] left to right"""
    import cv2
    H, W = img.shape[:2]
    y0, y1 = max(0, y0), min(H, y1)
    band = np.ascontiguousarray(img[y0:y1])
    bg = np.median(band.reshape(-1, 3), 0)
    sizes = sorted({max(8, int(round(h_text * f))) for f in (0.85, 0.95, 1.05, 1.2, 1.35, 1.5)})
    cand = []
    for key in templates():
        for h in sizes:
            if h > band.shape[0]:
                continue
            t = scaled(key, h, bg)
            if t.shape[1] >= band.shape[1]:
                continue
            r = cv2.matchTemplate(band, t, cv2.TM_CCOEFF_NORMED)
            col = r.max(0)
            idx = np.where(col >= thr)[0]
            for x in idx:                                    # local maxima along x
                lo, hi = max(0, x - h // 2), min(len(col), x + h // 2 + 1)
                if col[x] >= col[lo:hi].max():
                    cand.append((float(col[x]), int(x), t.shape[1], key))
    cand.sort(reverse=True)
    kept = []
    for sc, x, w, key in cand:                               # non-maximum suppression
        if all(x + w <= kx + 2 or x >= kx + kw - 2 for _, kx, kw, _ in kept):
            kept.append((sc, x, w, key))
    return sorted(((x, w, key, sc) for sc, x, w, key in kept))


def ink_is_red(img, box):
    x0, y0, x1, y1 = box
    p = img[y0:y1, x0:x1].astype(int)
    if p.size == 0:
        return False
    lum = p.mean(2)
    ink = p[lum < np.percentile(lum, 25)]
    if len(ink) < 5:
        return False
    r, g, b = ink.mean(0)
    return r > g + 45 and r > b + 45


NUM = re.compile(r'^\s*[^\w]?\s*(\d+(?:[.,]\d+)?)')


def parse_value(txt):
    m = NUM.match(txt)
    if not m:
        return None
    try:
        return float(m.group(1).replace(',', '.'))
    except ValueError:
        return None


def en_name(txt):
    """English resource name after the number ('6.0t of Alcohol'); OCR often drops spaces, so match inside the text"""
    t = re.sub(r'[^a-z]', '', txt.lower())
    m = re.search(r'o[ft1](.+)$', t)
    tail = m.group(1) if m else ''
    for k in sorted(EN, key=len, reverse=True):
        kk = k.replace(' ', '')
        if tail.startswith(kk) or (len(kk) >= 5 and kk in t):
            return EN[k]
    return None


def fix_zero(t):
    """OCR reads 0 as O/o next to digits: 'O.4OT' -> '0.40T'"""
    t = re.sub(r'[Oo](?=[.,]?\d)', '0', t)
    return re.sub(r'(?<=[\d.,])[Oo]', '0', t)


def numbers_in(box):
    """numbers inside one OCR box with their approximate x (OCR returns a whole phrase per box)"""
    t = fix_zero(box['t']); n = max(1, len(t))
    out = []
    for m in re.finditer(r'\d+(?:[.,]\d+)?', t):
        if m.start() > 0 and t[m.start() - 1].isalpha():
            continue                                         # '3' of 'm3', '1' of a misread letter: not a quantity
        x = box['x0'] + (box['x1'] - box['x0']) * (m.start() + 0.3) / n
        nxt = re.search(r'\d', t[m.end():])
        tail = t[m.end(): m.end() + nxt.start()] if nxt else t[m.end():]
        first = t[:m.start()].strip(' :.,;-_|') == ''
        out.append(dict(x=x, value=float(m.group(0).replace(',', '.')), tail=tail, first=first))
    return out


def red_bands(img):
    """rows of red header text, by colour -> [(y0, y1)]"""
    a = img.astype(int)
    red = (a[..., 0] > 140) & (a[..., 1] < 95) & (a[..., 2] < 95)
    W = img.shape[1]
    cnt = red.sum(1)
    xs = [np.where(r)[0] for r in red]
    rows = np.array([c >= 8 and (x.max() - x.min()) >= 0.3 * W for c, x in zip(cnt, xs)])   # long red text, not a red icon
    bands, y = [], 0
    while y < len(rows):
        if rows[y]:
            y0 = y
            while y < len(rows) and rows[y]:
                y += 1
            if y - y0 >= 4:
                bands.append((y0, y))
        y += 1
    return bands


def overlap(a, b):
    """share of the smaller box covered by the other"""
    w = min(a[2], b[2]) - max(a[0], b[0]); h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    return w * h / max(1, min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])))


def red_text_bottom(img, h):
    """last row that really has red letters inside header box h"""
    a = img[h['y0']:h['y1'] + 1].astype(int)
    if a.size == 0:
        return h['y1']
    red = (a[..., 0] > 140) & (a[..., 1] < 110) & (a[..., 2] < 110)
    rows = np.where(red.sum(1) >= 3)[0]
    return h['y0'] + int(rows.max()) if len(rows) else h['y1']


ICON_MIN = 0.72         # blob-vs-icon score: real icons 0.90-0.99 on the user's windows, look-alikes <= 0.74


def letter_h(img, box, xa, xb):
    """real height of the dark glyphs inside an OCR box between xa and xb (the OCR box itself is padded)"""
    x0, y0, x1, y1 = box
    xa, xb = max(x0, int(xa)), min(x1, int(xb))
    p = img[y0:y1 + 1, xa:xb].astype(int)
    if p.size == 0:
        return max(4, y1 - y0)
    lum = p.mean(2)
    dark = lum < min(110, np.percentile(lum, 95) - 70)
    rows = np.where(dark.sum(1) >= 1)[0]
    if len(rows) < 3:
        return max(4, y1 - y0)
    return int(rows.max() - rows.min() + 1)


def icon_blob(img, bg, x_num, y0, y1, ht, top_limit=0, bottom_limit=None, lh=None):
    """the icon left of a number: the nearest blob taller than the letters, inside its own row -> (x0, y0, x1, y1) or None.
    top_limit / bottom_limit cut the search at the header above and halfway to the neighbouring rows,
    so icons of two rows that touch are not taken as one blob"""
    import cv2
    H, W = img.shape[:2]
    cy = (y0 + y1) / 2
    lh = lh or ht
    X0, X1 = max(0, int(x_num - 4.0 * ht)), max(0, int(x_num) - 1)
    Y0, Y1 = max(0, int(cy - 1.2 * ht), int(top_limit)), min(H, int(cy + 1.2 * ht))   # icons are <= ~2.3x the letters
    if bottom_limit is not None:
        Y1 = min(Y1, int(bottom_limit))
    if X1 - X0 < 6 or Y1 - Y0 < 6:
        return None
    reg = img[Y0:Y1, X0:X1].astype(int)
    m = (np.sqrt(((reg - bg) ** 2).sum(2)) > 38).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    best = None
    for i in range(1, n):
        x, y, ww, hh, area = stats[i]
        if hh < 1.4 * lh or ww < 0.6 * lh or area < 0.25 * hh * ww:
            continue                                         # letters and thin lines are not icons
        if best is None or x + ww > best[0] + best[2]:       # the blob closest to the number
            best = (x, y, ww, hh)
    if best is None:
        return None
    x, y, ww, hh = best
    return (X0 + int(x), Y0 + int(y), X0 + int(x + ww), Y0 + int(y + hh))


def classify_blob(img, box, bg, ht=None):
    """compare the icon blob with every allowed game icon -> [(score, key, rect)] best first.
    score = 0.5 * shape correlation + 0.5 * colour agreement, both at the best position and size;
    rect = where that icon was found (the blob itself may hold a piece of a neighbour)"""
    import cv2
    x0, y0, x1, y1 = box
    H, W = img.shape[:2]
    pad = 3
    ax, ay = max(0, x0 - pad), max(0, y0 - pad)
    area = np.ascontiguousarray(img[ay:min(H, y1 + pad), ax:min(W, x1 + pad)])
    af = area.astype(np.float32)
    big = max(y1 - y0, x1 - x0)                              # icons are scaled by their longer side
    sizes = {int(round(big * f)) for f in (0.6, 0.72, 0.84, 0.92, 1.0, 1.06, 1.12)}
    sizes |= {int(round((y1 - y0) * f)) for f in (0.84, 1.0, 1.1)}
    if ht:
        sizes |= {int(round(ht * f)) for f in (1.3, 1.45, 1.6, 1.75, 1.9, 2.05, 2.2, 2.35, 2.5)}
    sizes = sorted(x for x in sizes if 6 <= x <= max(area.shape[:2]))
    out = []
    for key in templates():
        best = (-1.0, None)
        for hh in sizes:
            t = scaled(key, hh, bg)
            if t.shape[0] > area.shape[0] or t.shape[1] > area.shape[1]:
                continue
            r = cv2.matchTemplate(area, t, cv2.TM_CCOEFF_NORMED)
            _, ncc, _, (mx, my) = cv2.minMaxLoc(r)
            patch = af[my:my + t.shape[0], mx:mx + t.shape[1]]
            col = 1.0 - min(1.0, float(np.abs(patch - t.astype(np.float32)).mean()) / 60.0)
            sc = 0.5 * ncc + 0.5 * col
            if sc > best[0]:
                best = (sc, (ax + mx, ay + my, ax + mx + t.shape[1], ay + my + t.shape[0]))
        out.append((best[0], key, best[1] or box))
    out.sort(key=lambda o: -o[0])
    return out


STAFF_C = ('tpyai', 'tpyib', 'tpydi', 'tpyдi', 'трудів', 'worker')          # «трудівники» = secondary education (С)
STAFF_B = ('hkehep', 'kehep', 'xehep', 'ehepib', 'нкehep', 'інжен', 'engineer')        # «інженери» = higher education (В)


def read_staff(boxes):
    """max workers / engineers per shift from 'Поточне число трудівників: 0 / 400 (макс.: 400)' -> dict"""
    out = {}
    for b in boxes:
        t = b['t'].lower()
        kind = 'workers' if any(k in t for k in STAFF_C) else 'engineers' if any(k in t for k in STAFF_B) else None
        if not kind or kind in out:
            continue
        h = max(4, b['y1'] - b['y0'])                        # the numbers may be a separate box on the same row
        row = ' '.join(x['t'] for x in sorted(boxes, key=lambda x: x['x0'])
                       if abs((x['y0'] + x['y1']) / 2 - (b['y0'] + b['y1']) / 2) < 0.6 * h and x['x0'] >= b['x0'])
        row = fix_zero(row).lower()
        m = re.search(r'(?:makc|max|макс)[^\d]*(\d+)', row) or re.search(r'\d+\s*/\s*(\d+)', row)
        if m:
            out[kind] = int(m.group(1))
    return out


def read_building(pil, keep_utility=False, debug=False):
    """-> dict(production=[{key,value,score,name_key}], needs=[...], lines=[(y,x,text)])"""
    im = pil.convert('RGB')
    k = 2 if im.width < 1400 else 1                      # small game text reads much better at 2x
    big = im.resize((im.width * k, im.height * k), Image.LANCZOS) if k > 1 else im
    res, _ = ocr_engine()(np.asarray(big))
    img = np.asarray(im)
    bg = np.median(img.reshape(-1, 3), 0)
    boxes = []
    for box, txt, conf in res or []:
        xs = [p[0] / k for p in box]; ys = [p[1] / k for p in box]
        boxes.append(dict(x0=int(min(xs)), y0=int(min(ys)), x1=int(max(xs)), y1=int(max(ys)), t=txt))
    boxes.sort(key=lambda b: (b['y0'], b['x0']))
    for b in boxes:
        b['red'] = ink_is_red(img, (b['x0'], b['y0'], b['x1'], b['y1']))
    heads = [b for b in boxes if b['red']]
    for y0_, y1_ in red_bands(img):                          # headers the OCR skipped
        if not any(h['y0'] - 4 <= (y0_ + y1_) / 2 <= h['y1'] + 4 for h in heads):
            heads.append(dict(x0=0, y0=y0_, x1=img.shape[1], y1=y1_, t='', red=True))
    heads.sort(key=lambda h: h['y0'])
    numbered = [b for b in boxes if not b['red'] and re.search(r'\d', b['t'])]
    items = []
    for b in numbered:
        ht = max(6, b['y1'] - b['y0'])
        cy = (b['y0'] + b['y1']) / 2
        for n in numbers_in(b):
            if n['value'] <= 0 or n['tail'].lstrip().startswith('%'):
                continue
            above = [red_text_bottom(img, h) for h in heads if h['y1'] <= b['y0'] + 2]
            top, bottom = (max(above) + 1) if above else 0, None
            xa = n['x'] - 4.0 * ht
            for o in numbered:                               # rows above / below in the same column: split halfway
                if o is b or o['x1'] < xa or o['x0'] > n['x'] + 3 * ht:
                    continue
                oc = (o['y0'] + o['y1']) / 2
                if 0.5 * ht < cy - oc < 3.0 * ht:
                    top = max(top, (cy + oc) / 2)
                elif 0.5 * ht < oc - cy < 3.0 * ht:
                    bottom = (cy + oc) / 2 if bottom is None else min(bottom, (cy + oc) / 2)
            bx = (b['x0'], b['y0'], b['x1'], b['y1'])
            lh = letter_h(img, bx, n['x'] - 0.3 * ht, n['x'] + 1.2 * ht)
            blob = icon_blob(img, bg, n['x'] - 0.15 * ht, b['y0'], b['y1'], ht, top_limit=top, bottom_limit=bottom, lh=lh)
            if blob is None and n['first']:                  # OCR sometimes takes the icon into the text box: look inside its start
                xs = b['x0'] + 2.5 * ht
                lh2 = letter_h(img, bx, b['x0'] + 0.45 * (b['x1'] - b['x0']), b['x1'])
                cand = icon_blob(img, bg, xs, b['y0'], b['y1'], ht, top_limit=top, bottom_limit=bottom, lh=lh2)
                if cand is not None and cand[0] <= b['x0'] + 1.0 * ht and cand[2] < xs:
                    blob = cand; n['x'] = max(n['x'], cand[2] + 1)
            if blob is None or n['x'] - blob[2] > 2.0 * ht:      # the number must sit right after its icon
                continue
            ranked = classify_blob(img, blob, bg, ht)
            sc, key, rect = ranked[0]
            margin = sc - ranked[1][0] if len(ranked) > 1 else sc
            if debug:
                print('   ', round(n['value'], 3), 'blob', blob, 'lh', lh, 'top:', [(k_, round(s_, 2)) for s_, k_, _ in ranked[:3]])
            if any(overlap(rect, it['blob']) > 0.6 for it in items):
                continue                                     # one icon -> one quantity
            nk = en_name(n['tail'])
            if not (sc >= ICON_MIN or (sc >= 0.6 and margin >= 0.1)) and not nk:
                continue                                     # not confident: better nothing than a wrong resource
            items.append(dict(key=nk if (nk and sc < 0.75) else key, value=n['value'], score=sc, icon_key=key, name_key=nk,
                              y=b['y0'], x=blob[0], text=n['tail'], blob=rect))
    if not keep_utility:
        items = [it for it in items if it['key'] not in UTILITY]
    groups = {}
    for it in items:
        hs = [h for h in heads if h['y1'] <= it['y'] + 3]
        h = hs[-1] if hs else None
        groups.setdefault(id(h), dict(head=h, items=[]))['items'].append(it)
    out = dict(production=[], needs=[], lines=[(b['y0'], b['x0'], b['t']) for b in boxes])
    out.update(read_staff(boxes))
    order = sorted(groups.values(), key=lambda g: g['items'][0]['y'])
    for i, g in enumerate(order):
        t = (g['head']['t'] if g['head'] else '').lower()
        consum = any(w in t for w in ('consum', 'спожив', 'cnox', 'cnok', 'cnoж', 'need', 'потреб'))
        produc = any(w in t for w in ('per workday', 'workday', 'трудод', 'tpyao', 'добов'))
        target = 'needs' if consum else 'production' if produc else ('production' if i == 0 else 'needs')
        out[target].extend(g['items'])
    return out
