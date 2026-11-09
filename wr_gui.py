"""Game-styled window for W&R City Manager: the game's own window texture (from assets/game_assets.zip) or, without it,
a drawn look-alike; plus the Ukrainian resource names. A trimmed copy of the montage kit's gui.py."""
import os
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import wr_paths

S = 1.6  # scale vs. native game UI at 1080p
FONT_R = os.path.join(wr_paths.FONTS, 'Arimo-400.ttf')
FONT_B = os.path.join(wr_paths.FONTS, 'Arimo-700.ttf')

C = dict(
    body=(236, 226, 214), edge=(222, 202, 182), border=(97, 80, 61),
    title=(146, 60, 56), title_top=(160, 78, 72), title_bot=(128, 50, 47),
    title_line=(238, 179, 172), title_icon=(236, 214, 208),
    text=(24, 14, 6), red=(158, 22, 20), warn=(196, 18, 16),
    redbar=(188, 0, 0), redbar_dk=(150, 0, 0), bar_border=(222, 188, 140),
    bar_bg=(250, 236, 210), field=(245, 234, 214), field_border=(212, 182, 146),
    muted=(112, 98, 86), green=(38, 128, 36), check=(40, 30, 20),
    box=(250, 238, 216), box_border=(176, 150, 120),
)


@lru_cache(maxsize=64)
def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, int(round(size)))


def fs(px):
    """native game px -> overlay px"""
    return int(round(px * S))


# ---------------------------------------------------------------- paper
_rng = np.random.default_rng(7)


def _make_paper(w=1400, h=1200):
    base = np.zeros((h, w, 3), np.float32)
    base[:] = C['body']
    low = _rng.normal(0, 1, (h // 40 + 2, w // 40 + 2)).astype(np.float32)
    low = np.array(Image.fromarray(low).resize((w, h), Image.BICUBIC))
    mid = _rng.normal(0, 1, (h // 8 + 2, w // 8 + 2)).astype(np.float32)
    mid = np.array(Image.fromarray(mid).resize((w, h), Image.BICUBIC))
    grain = _rng.normal(0, 1, (h, w)).astype(np.float32)
    n = low * 3.2 + mid * 1.6 + grain * 1.6
    base += n[..., None] * np.array([1.0, 0.95, 0.9], np.float32)
    return base


PAPER = _make_paper()


def paper(w, h):
    a = PAPER[:h, :w].copy()
    # darker, warmer edges like aged paper
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy])
    k = np.clip(1 - d / fs(14), 0, 1) ** 2
    edge = np.array(C['edge'], np.float32) - np.array(C['body'], np.float32)
    a += k[..., None] * edge[None, None, :]
    return np.clip(a, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- window
TITLE_H = fs(26)
TS = 0.86          # content text size relative to the old drawn style (matches the game's body text)


def window(w, h, title, alpha=0.96):
    """Return (RGBA image, ImageDraw, content_origin_y)."""
    pad = 18  # room for shadow
    W, H = w + pad * 2, h + pad * 2
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # soft shadow
    sh = Image.new('L', (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad + 3, pad + 6, pad + w + 3, pad + h + 6), 6, fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    im.paste((0, 0, 0, 255), (0, 0), sh)
    body = Image.fromarray(paper(w, h)).convert('RGBA')
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), 5, fill=int(255 * alpha))
    im.paste(body, (pad, pad), mask)
    d = ImageDraw.Draw(im)
    # title bar with subtle vertical gradient
    x0, y0, x1 = pad + fs(3), pad + fs(4), pad + w - fs(3)
    y1 = y0 + TITLE_H
    for i in range(TITLE_H):
        t = i / max(1, TITLE_H - 1)
        if t < 0.15:
            c = C['title_top']
        else:
            tt = (t - 0.15) / 0.85
            c = tuple(int(C['title'][k] * (1 - tt) + C['title_bot'][k] * tt) for k in range(3))
        d.line((x0, y0 + i, x1, y0 + i), fill=c + (255,))
    d.line((x0, y1, x1, y1), fill=C['title_line'] + (255,), width=1)
    # title text
    d.text((x0 + fs(7), y0 + TITLE_H / 2), title, font=font(fs(16.5)), fill=(255, 255, 255, 255), anchor='lm')
    # icons: eye, pin, close
    ic = C['title_icon'] + (255,)
    cy = y0 + TITLE_H / 2
    xc = x1 - fs(11)
    r = fs(5)
    d.line((xc - r, cy - r, xc + r, cy + r), fill=ic, width=fs(2.4))
    d.line((xc - r, cy + r, xc + r, cy - r), fill=ic, width=fs(2.4))
    xp = xc - fs(25)
    d.line((xp - fs(6), cy, xp + fs(3), cy), fill=ic, width=fs(1.6))
    d.rectangle((xp + fs(2), cy - fs(4), xp + fs(6), cy + fs(4)), fill=ic)
    d.line((xp + fs(6), cy, xp + fs(8), cy), fill=ic, width=fs(1.6))
    xe = xp - fs(26)
    d.ellipse((xe - fs(8), cy - fs(4.5), xe + fs(8), cy + fs(4.5)), outline=ic, width=fs(1.4))
    d.ellipse((xe - fs(2.6), cy - fs(2.6), xe + fs(2.6), cy + fs(2.6)), fill=ic)
    # thin outer frame
    d.rounded_rectangle((pad, pad, pad + w - 1, pad + h - 1), 5, outline=C['border'] + (150,), width=1)
    return im, d, (pad, y1 + pad - pad)  # content origin (x_pad, y below title)



# ---------------------------------------------------------------- textured window built from a real game screenshot
import json as _json, os as _os

_window_drawn = window
_TEX = None


def _tex():
    global _TEX
    if _TEX is None:
        gd = wr_paths.game_dir()
        p, mp = os.path.join(gd, 'ui', 'window_tex.png'), os.path.join(gd, 'ui', 'meta.json')
        if not (_os.path.exists(p) and _os.path.exists(mp)):
            return None
        m = _json.load(open(mp, encoding='utf-8'))
        k = TITLE_H / (m['bar'][3] - m['bar'][2] + 1)
        im = Image.open(p)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        cx, cy = m['crop']
        sx = lambda v: round((v - cx) * k)
        sy = lambda v: round((v - cy) * k)
        _TEX = dict(a=np.asarray(im).astype(np.float32), cap=m['cap'] * k,
                    paper_l=sx(m['paper'][0]), paper_r=sx(m['paper'][1]), paper_t=sy(m['paper'][2]), paper_b=sy(m['paper'][3]),
                    bar_b=sy(m['bar'][3] + 1), title_x=sx(m['title_x']), title_base=sy(m['title_base']), icons_x=sx(m['icons_x']),
                    keepL=sx(m['keepL']), keepR=sx(m['keepR']), keepT=sy(m['keepT']), keepB=sy(m['keepB']))
    return _TEX


def _sl(a, i, j, axis):
    return a[i:j] if axis == 0 else a[:, i:j]


def _join(X, Y, f, axis):
    f = min(f, X.shape[axis], Y.shape[axis])
    if f <= 0:
        return np.concatenate([X, Y], axis)
    r = np.linspace(0, 1, f, dtype=np.float32)
    r = r[:, None, None] if axis == 0 else r[None, :, None]
    mid = _sl(X, X.shape[axis] - f, X.shape[axis], axis) * (1 - r) + _sl(Y, 0, f, axis) * r
    return np.concatenate([_sl(X, 0, X.shape[axis] - f, axis), mid, _sl(Y, f, Y.shape[axis], axis)], axis)


def _fit_axis(A, target, keepA, keepB, axis, f=24):
    """Resize along one axis without stretching: keep head [0:keepA] and tail [keepB:],
    crop or mirror-tile the middle, with feathered seams."""
    head, tail, fill = _sl(A, 0, keepA, axis), _sl(A, keepB, A.shape[axis], axis), _sl(A, keepA, keepB, axis)
    need = target - head.shape[axis] - tail.shape[axis]
    if need < 0:
        head = _sl(head, 0, max(f + 1, head.shape[axis] + need + f), axis)
        return _join(head, tail, f, axis)
    mid, flip = fill, True
    while mid.shape[axis] < need + 2 * f:
        mid = _join(mid, np.flip(fill, axis) if flip else fill, f, axis)
        flip = not flip
    return _join(_join(head, _sl(mid, 0, need + 2 * f, axis), f, axis), tail, f, axis)


def window(w, h, title, alpha=0.96):
    T = _tex()
    if T is None:
        return _window_drawn(w, h, title, alpha)
    A = T['a']
    tw = T['paper_l'] + w + (A.shape[1] - T['paper_r'])
    th = T['paper_t'] + h + (A.shape[0] - T['paper_b'])
    B = _fit_axis(A, tw, T['keepL'], T['keepR'], 1)
    B = _fit_axis(B, th, T['keepT'], T['keepB'], 0)
    im = Image.fromarray(B.clip(0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    f = font(T['cap'] / 0.716)                      # Arimo cap height = 0.716 em -> same letter size as the game
    maxw = (B.shape[1] - (A.shape[1] - T['icons_x'])) - T['title_x'] - 10
    t = title
    if f.getlength(t) > maxw:                        # the game truncates long titles with an ellipsis
        while t and f.getlength(t + '…') > maxw:
            t = t[:-1]
        t = t.rstrip() + '…'
    d.text((T['title_x'], T['title_base']), t, font=f, fill=(255, 255, 255, 255), anchor='ls')
    return im, d, (T['paper_l'] + fs(5), T['bar_b'])      # small inner margin from the torn edge



RES_UA = {
    'airplanes': 'Літаки', 'alcohol': 'Алкоголь', 'alumina': 'Глинозем', 'aluminium': 'Алюміній', 'asphalt': 'Асфальт',
    'bauxite': 'Боксит', 'bitumen': 'Бітум', 'boards': 'Дошки', 'bricks': 'Цегла', 'cement': 'Цемент',
    'chemicals': 'Хімікати', 'clothes': 'Одяг', 'coal': 'Вугілля', 'colorwater': '? (біла крапля)', 'concrete': 'Бетон',
    'ecomponents': 'Електронні компоненти', 'eletric': 'Електроенергія', 'eletronics': 'Електроніка',
    'explosives': 'Вибухівка', 'fabric': 'Тканина', 'fertiliser': 'Штучне добриво', 'fertiliser_liquid': 'Рідке добриво',
    'food': 'Продукти', 'fuel': 'Паливо', 'gravel': 'Щебінь', 'heat': 'Тепло', 'helicopters': 'Гелікоптери',
    'iron': 'Залізна руда', 'livestock': 'Худоба', 'mcomponents': 'Механічні компоненти', 'meat': "М'ясо",
    'nuclearfuel': 'Ядерне паливо', 'nuclearfuelburned': 'Ядерні відходи', 'oil': 'Нафта', 'plants': 'Рослини',
    'plastics': 'Пластик', 'prefabpanels': 'Збірні панелі', 'rawbauxite': 'Сирий боксит', 'rawcoal': 'Сире вугілля',
    'rawgravel': 'Сирий гравій', 'rawiron': 'Сира залізна руда', 'service_material': 'Обслуговування та ремонт',
    'ships': 'Кораблі', 'steel': 'Сталь', 'trains': 'Поїзди', 'uf6': 'Гексафторид урану', 'uranium': 'Уран',
    'usagewater': 'Стічні води', 'vehicles': 'Автотранспорт', 'waste_aluminium': 'Алюмінієві відходи',
    'waste_ash': 'Зола', 'waste_bio': 'Біовідходи', 'waste_burnable': 'Горючі відходи', 'waste_gravel': 'Відходи гравію',
    'waste_mixed': 'Змішані відходи', 'waste_other': 'Інші відходи', 'waste_plastic': 'Пластикові відходи',
    'waste_steel': 'Сталеві відходи', 'waste_toxic': 'Токсичні відходи', 'water': 'Чиста вода', 'wood': 'Деревина',
    'workers': 'Трудівники', 'yellowcake': 'Жовтий кек',
}
