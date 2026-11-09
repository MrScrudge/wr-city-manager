"""W&R City Manager — overlay calculator in the game's window style (always on top).
Tab «Міста»: cities -> objects (buildings) with count, productivity, production, needs, workers С/В (3 shifts),
             per-city extra panel (houses, bus stops, fields). Needs per 1000 residents: in every city row, under the cities and in the calculator."""
import os, sys, json, math, re, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wr_paths                                                          # noqa: E402  (where the assets live)
CM = HERE                                                                # exports and shortcuts go next to the program
APP_ID = 'MrScrudge.WRCalculator'          # the same id on the process, its window and the shortcut: one taskbar button
import zlib
SINGLE_NAME = 'MrScrudge.WRCityManager.single.%08x' % zlib.crc32(os.path.normcase(HERE).encode('utf-8', 'replace'))   # one running copy per program folder: the 2nd start of the same copy just shows the 1st
READY = None                               # created when the window is up: the gear (its own process) then fades out


def _links_child():
    """«--setup» (the launcher .bat passes it): the shortcuts are renewed by a small separate process of their own"""
    try:
        import subprocess
        exe = sys.executable
        if sys.platform == 'win32' and os.path.exists(os.path.join(os.path.dirname(exe), 'pythonw.exe')):
            exe = os.path.join(os.path.dirname(exe), 'pythonw.exe')
        subprocess.Popen([exe, os.path.abspath(__file__), '--make-links', '--setup'],
                         creationflags=0x08000000 if sys.platform == 'win32' else 0, close_fds=True)
    except Exception:
        pass
if __name__ == '__main__' and '--make-links' not in sys.argv:          # the gear first, in its own process: it turns smoothly
    try:                                                                 # already running? then just bring that window forward
        from PySide6.QtNetwork import QLocalSocket
        _sock = QLocalSocket(); _sock.connectToServer(SINGLE_NAME)
        if _sock.waitForConnected(500):
            _sock.write(b'show'); _sock.flush(); _sock.waitForBytesWritten(500); _sock.disconnectFromServer()
            if '--setup' in sys.argv:
                _links_child()                                   # already running: the shortcuts are still renewed
                import time; time.sleep(0.3)
            sys.exit(0)
    except Exception:
        pass
    try:                                                                 # however busy the loading below is
        import subprocess, tempfile
        READY = os.path.join(tempfile.gettempdir(), f'wrcm_ready_{os.getpid()}')
        _exe = sys.executable
        if sys.platform == 'win32' and os.path.exists(os.path.join(os.path.dirname(_exe), 'pythonw.exe')):
            _exe = os.path.join(os.path.dirname(_exe), 'pythonw.exe')
        subprocess.Popen([_exe, os.path.join(HERE, 'splash.py'), '--ready', READY, '--parent', str(os.getpid())],
                         creationflags=0x08000000 if sys.platform == 'win32' else 0, close_fds=True)
    except Exception:
        READY = None


import numpy as np                                                       # noqa: E402
from PIL import Image                                                    # noqa: E402
import wr_gui as gui                                                               # noqa: E402  (game window texture, resource names)
import lang                                                              # noqa: E402  (UI languages)
from lang import tr                                                      # noqa: E402


def _install_fast_fit():
    """gui.window() makes the window texture with repeated big concatenations (it is made again at every step of a resize);
    the same pixels are made here in one pass, about 3x faster. Anything unusual falls back to the original function."""
    orig = getattr(gui, '_fit_axis', None); sl = getattr(gui, '_sl', None)
    if orig is None or sl is None or hasattr(gui, '_fit_axis_orig'):
        return
    gui._fit_axis_orig = orig

    def fit_axis(A, target, keepA, keepB, axis, f=24):
        head, tail, fill = sl(A, 0, keepA, axis), sl(A, keepB, A.shape[axis], axis), sl(A, keepA, keepB, axis)
        hl, tl, P = head.shape[axis], tail.shape[axis], fill.shape[axis]
        need = target - hl - tl
        if need < 0 or hl < f or tl < f or P < 2 * f or A.dtype != np.float32 or A.ndim != 3:
            return orig(A, target, keepA, keepB, axis, f)
        r = np.linspace(0, 1, f, dtype=np.float32)
        r = r[:, None, None] if axis == 0 else r[None, :, None]

        def shape(n):
            s = list(A.shape); s[axis] = n; return s
        L = need + 2 * f
        n = 1 if P >= L else 1 + -(-(L - P) // (P - f))              # pieces: fill | flipped fill | fill ... joined by f-row seams
        mid = np.empty(shape(P + (n - 1) * (P - f)), np.float32)
        sl(mid, 0, P, axis)[...] = fill
        pos = P
        for k in range(1, n):
            piece = np.flip(fill, axis) if k % 2 == 1 else fill
            sl(mid, pos - f, pos, axis)[...] = sl(mid, pos - f, pos, axis) * (1 - r) + sl(piece, 0, f, axis) * r
            sl(mid, pos, pos + P - f, axis)[...] = sl(piece, f, P, axis)
            pos += P - f
        out = np.empty(shape(target), np.float32)
        sl(out, 0, hl - f, axis)[...] = sl(head, 0, hl - f, axis)
        sl(out, hl - f, hl, axis)[...] = sl(head, hl - f, hl, axis) * (1 - r) + sl(mid, 0, f, axis) * r
        sl(out, hl, hl + need, axis)[...] = sl(mid, f, f + need, axis)
        sl(out, hl + need, hl + need + f, axis)[...] = sl(mid, L - f, L, axis) * (1 - r) + sl(tail, 0, f, axis) * r
        sl(out, hl + need + f, target, axis)[...] = sl(tail, f, tl, axis)
        return out
    gui._fit_axis = fit_axis


_install_fast_fit()
from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QRect, QSize, Signal, QEvent, QAbstractNativeEventFilter      # noqa: E402
from PySide6.QtGui import (QImage, QPixmap, QPainter, QIcon, QFontDatabase, QFont, QCursor, QValidator, QGuiApplication,
                           QColor, QPen, QFontMetrics, QShortcut, QKeySequence, QPolygonF, QRegion)
from PIL import ImageDraw, ImageFilter
from PySide6.QtCore import QLocale, QUrl  # noqa: E402
from PySide6.QtCore import QPropertyAnimation, QEasingCurve  # noqa: E402
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,  # noqa: E402
                               QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QScrollArea, QFrame,
                               QStackedWidget, QDialog, QMessageBox, QSizeGrip, QCompleter, QListWidget,
                               QListWidgetItem, QToolButton, QToolTip, QGraphicsOpacityEffect)

DATA = os.path.join(HERE, 'data.json')
APP_NAME = 'W&R City Manager'                               # the same in every language
OLD_LINK = 'W&R Калькулятор.lnk'                            # the shortcut name before the rename
CATALOG_ADD = os.path.join(HERE, 'catalog_add.json')       # buildings handed over from outside: merged into «Мої об'єкти» once
GAME = wr_paths.game_dir()                                  # the game's icons: unpacked from assets/game_assets.zip once
ICONS = os.path.join(HERE, 'assets')                        # the program's own icons
EDITOR = os.path.join(GAME, 'editor')                       # game building icons
GI = os.path.join(GAME, 'gameicons')                        # game resource icons
INK, RED, MAROON, PAPER = '#2d231e', '#bc0000', '#923c38', '#faf4ea'
RES_NAME = dict(gui.RES_UA)
RES_NAME.update({'plants': 'Збіжжя', 'boards': 'Деревина', 'wood': 'Ліс-кругляк', 'gravel': 'Гравій', 'rawgravel': 'Камінь',
                 'rawcoal': 'Вугільна руда', 'uranium': 'Уранова руда', 'yellowcake': 'Оксид урану', 'uf6': 'Фторид урану',
                 'plastics': 'Пластмаса', 'ecomponents': 'Електродеталі', 'mcomponents': 'Механічні деталі', 'food': 'Хліб', 'eletric': 'Електроенергія', 'water': 'Вода', 'usagewater': 'Стічні води',
                 'waste_mixed': 'Сміття', 'heat': 'Тепло', 'workers': 'Випускники / працівники'})
DEFAULT_RATES = [['eletronics', 10], ['food', 140], ['meat', 30], ['clothes', 5], ['alcohol', 12]]
DEFAULT_UTIL = [['eletric', 0], ['water', 0], ['usagewater', 0], ['waste_mixed', 0], ['heat', 0]]   # values: user will give later
ICON_WORDS = [  # Ukrainian keyword -> game editor icon; most specific first
    (('смітт', 'електро'), 'tool_incinerator_powerplant'), (('смітт', 'тепло'), 'tool_incinerator_heat'),
    (('сміт', 'спал'), 'tool_incinerator_powerplant'),
    ('переробки сталі', 'tool_waste_steelrecycling'), ('буд смітт', 'tool_waste_gravelrecycling'),
    ('пластик', 'tool_waste_plasticrecycling'), ('алюмін', 'tool_waste_aluminiumrecycling'), ('відход', 'tool_waste_generalseparation'),
    ('тв ', 'tool_televizia'), ('телест', 'tool_televizia'), ('радіо', 'tool_rozhlas'), ('залізнич', 'tool_rail_construction_office'),
    ('адміністрац', 'tool_cityhall'), ('спорт', 'tool_playground_football'), ('кіно', 'tool_kino'), ('розваг', 'tool_co_ferris_wheel'),
    ('парк', 'tool_fountain1'), ('сто ', 'tool_technical_services_big'), ('техобсл', 'tool_technical_services'),
    ('школ', 'tool_school'), ('лікарн', 'tool_hospital'), ('садок', 'tool_kindergarten'), ('дитбуд', 'tool_orphanage'),
    ('продукт', 'tool_shop_grocerystore'), ('магазин', 'tool_shop_grocerystore'), ('пивн', 'tool_pub'), ('паб', 'tool_pub'),
    ('поліц', 'tool_police'), ('держбезпек', 'tool_secretpolice'), ('кдб', 'tool_secretpolice'), ('пожеж', 'tool_firestation'),
    ('мед', 'tool_university_medical'), ('універ', 'tool_university_soviet'), ('аес', 'tool_powerplant_nuclear_double'),
    ('тес', 'tool_powerplant_coal'), ('електростанц', 'tool_powerplant_coal'), ('теплоцентр', 'tool_heating_endstation_big'),
    ('тепло', 'tool_heating_end_station'), ('хліб', 'tool_food_factory'), ('цегел', 'tool_brick_factory'), ('панел', 'tool_panels_factory'),
    ('цемент', 'tool_cement_plant'), ('стал', 'tool_steel_mill'), ('алкогол', 'tool_distillery'),
    ('електродетал', 'tool_eletronic_components_factory'), ('електрон', 'tool_eletronic_factory'),
    ('механ', 'tool_mechanical_components_factory'), ('гравій', 'tool_gravel_processing_small'), ('лісопил', 'tool_sawmill'),
    ('водопідгот', 'tool_water_treatment_big'), ('свердлов', 'tool_water_well'), ("в'язниц", 'tool_prison'), ('вязниц', 'tool_prison'),
    ('суд', 'tool_court'), ('готел', 'tool_hotel'), ('асфальт', 'tool_asphalt_plant'), ('бетон', 'tool_concrete_plant'),
    ('аеропорт', 'tool_airport_terminal'), ('танков', 'tool_production_vehicle'), ('трамвай', 'tool_tram_depo_big'),
    ('техніки', 'tool_production_vehicle'), ('зупин', 'tool_busstop'), ('ферм', 'tool_farm'), ('поле', 'tool_field_big'), ('поля', 'tool_field_big')]


# ------------------------------------------------------------------ helpers
def fmt(v):
    """7 000 / 1 200,5 / 2,25 / 0,016 — more decimals for small numbers, no trailing zeros"""
    if v is None:
        return '—'
    if abs(v - round(v)) < 1e-9:
        return f'{int(round(v)):,}'.replace(',', ' ')
    d = 1 if abs(v) >= 10 else 2 if abs(v) >= 1 else 3
    t = f'{v:,.{d}f}'
    if '.' in t:
        t = t.rstrip('0').rstrip('.')
    return t.replace(',', ' ').replace('.', ',')


_PIX = {}


def pix(path, h):
    key = (path, h)
    if key not in _PIX:
        if not path or not os.path.exists(path):
            _PIX[key] = QPixmap()
        else:
            p = QPixmap(path)
            _PIX[key] = p.scaledToHeight(h, Qt.SmoothTransformation) if not p.isNull() else p
    return _PIX[key]


def res_icon(key):
    for p in (os.path.join(GI, f'{key}.png'), os.path.join(ICONS, f'{key}.png'), os.path.join(GI, 'ui', f'{key}.png')):
        if os.path.exists(p):
            return p
    return None


def guess_icon(name):
    """building name -> editor icon file name (stored as a bare file name in data.json)"""
    n = (name or '').lower()
    for w, f in ICON_WORDS:
        ok = all(x in n for x in w) if isinstance(w, tuple) else w in n
        if ok and os.path.exists(os.path.join(EDITOR, f + '.png')):
            return f + '.png'
    return None


def icon_path(f):
    if not f:
        return None
    p = f if os.path.isabs(f) else os.path.join(EDITOR, f)
    return p if os.path.exists(p) else None


def pil_to_qimage(im):
    im = im.convert('RGBA')
    return QImage(im.tobytes(), im.width, im.height, QImage.Format_RGBA8888).copy()


def parse_name(raw):
    """'Пожежна частина 5х' -> ('Пожежна частина', 5); 'Спорт х10' -> ('Спорт', 10)"""
    m = re.search(r'\s*(?:(\d+)\s*[хxXХ]|[хxXХ]\s*(\d+))\s*$', raw)
    if m:
        return raw[:m.start()].strip(), int(m.group(1) or m.group(2))
    return raw.strip(), 1


# ------------------------------------------------------------------ data
LVIV = [('Танковий завод', 1000, 1000), ('Трамвайний завод', 1200, 300), ('Цегельний завод', 660, 0), ('Панельний завод', 660, 0),
        ('Цементний завод', 100, 0), ('Гравійний завод', 150, 0), ('Завод переробки буд сміття 2х', 90, 0),
        ('Завод з переробки пластику 2х', 120, 0), ('Завод з переробки сталі', 90, 0), ('Завод з переробки Алюмінію', 75, 0),
        ('Завод з переробки н відходів', 100, 0), ('Сміттєспалювальна електростанція', 60, 0), ('Сміттєспалювальна теплостанція', 50, 0),
        ('Хлібзавод', 660, 0), ('Переробка техніки', 150, 0), ('ТЕС 2х', 180, 0), ('Теплоцентраль 2х', 400, 0), ('Лісопильний завод', 100, 0),
        ('Алкогольний завод', 500, 0), ('Завод електродеталей', 450, 0), ('Завод Електроніки', 450, 0), ('Аеропорт', 0, 75),
        ('Водопідготовка 5х', 150, 0), ('Свердловина', 30, 0), ('Продуктові магазини 19х', 1800, 0), ('Пивнуха 9х', 300, 0),
        ('Кінотеатр 9х', 500, 0), ('Розваги 20х', 500, 0), ('Спорт (Зал і поля) х10', 1000, 0), ('Пожежна частина 5х', 800, 0),
        ('Лікарня 9х', 900, 900), ('Садок 16х', 1400, 0), ('Школа 8х', 1200, 1200), ('Дитбудинок 8х', 1200, 0),
        ('Університет', 230, 230, 150), ('Штаб', 900, 900, 300), ('Поліція 10х', 300, 500), ('Мед універ', 150, 150, 300),
        ("В'язниця", 250, 0), ('ТВ Вишка та Телестанція', 100, 220), ('Радіостанція 5х', 550, 550), ('Сто велике 4х', 1000, 0),
        ('Пошта 9х', 500, 0), ('Держбезпека', 0, 120), ('Залізнична буд. кантора', 180, 0), ('Міська Адміністрація', 75, 0),
        ('Парк', 100, 0), ('Суд', 150, 100), ('Асфальт та Бетон', 30, 0), ('Готелі', 250, 0)]
EXTRA0 = dict(c_house=197, b_house=196, stop_people=1000, enterprises=0)


def new_obj(name='', count=1, c=0, b=0, prod=100, production=None, needs=None):
    return dict(id=uuid.uuid4().hex[:8], name=name, count=count, prod=prod, production=production or [], needs=needs or [], c=c, b=b)


def city_pop(c):
    """population of a city = its Total (С + В for 3 shifts), always computed from the buildings"""
    return int(round(sum((o['c'] + o['b']) * max(1, o['count']) for o in c['objects'])))


def new_city(name='Нове місто', pop=0):
    return dict(id=uuid.uuid4().hex[:8], name=name, pop=pop, open=False, extra_open=False, objects=[], extra=dict(EXTRA0))


def default_data():
    """a fresh start: one empty city and the starter list of buildings («Мої об'єкти»)"""
    catalog = {}
    for row in LVIV:
        nm, cnt = parse_name(row[0])
        prodlist = [['workers', row[3]]] if len(row) > 3 else []
        catalog[nm] = dict(c=row[1] / cnt, b=row[2] / cnt, production=prodlist, needs=[])
    return dict(cities=[new_city()], catalog=catalog, rates=[list(r) for r in DEFAULT_RATES],
                util_rates=[list(r) for r in DEFAULT_UTIL], res_rows=[],
                settings=dict(cb_v=2, pinned=True, one_shift=False, tab=0, geom=None, collapsed=False))


def backup_data():
    """a copy of data.json once a day in backups; the last 14 days are kept"""
    try:
        import time, shutil
        if not os.path.exists(DATA):
            return
        bk = os.path.join(os.path.dirname(DATA), 'backups'); os.makedirs(bk, exist_ok=True)
        dst = os.path.join(bk, time.strftime('data_%Y-%m-%d.json'))
        if not os.path.exists(dst):
            shutil.copy2(DATA, dst)
        for f in sorted(f for f in os.listdir(bk) if f.startswith('data_') and f.endswith('.json'))[:-14]:
            os.remove(os.path.join(bk, f))
    except Exception:
        pass


def load():
    try:
        d = json.load(open(DATA, encoding='utf-8'))
        ukeys = {k for k, _ in DEFAULT_UTIL}                  # older files kept utilities among the goods
        if 'util_rates' not in d:
            d['util_rates'] = [r for r in d.get('rates', []) if r[0] in ukeys] or [list(r) for r in DEFAULT_UTIL]
        st0 = d.setdefault('settings', {})
        if st0.get('rates_custom') and d.get('rates'):          # edited with the pencil of the calculator
            d['rates'] = [list(r) for r in d['rates']]
        else:
            d['rates'] = [list(r) for r in DEFAULT_RATES]
        if st0.get('tab_v') != 2:                               # old tabs: 0 cities, 1 per 1000, 2 my buildings
            st0['tab'] = {0: 0, 1: 0, 2: 1}.get(st0.get('tab', 0), 0); st0['tab_v'] = 2
        if st0.get('cb_v') != 2:                                # С/В were row totals: make them per building
            for c in d.get('cities', []):
                for o in c['objects']:
                    n = max(1, o.get('count', 1)); o['c'] = o.get('c', 0) / n; o['b'] = o.get('b', 0) / n
            for e in d.get('catalog', {}).values():
                n = max(1, e.get('count', 1)); e['c'] = e.get('c', 0) / n; e['b'] = e.get('b', 0) / n
            st0['cb_v'] = 2
        used = {o['name'] for c in d.get('cities', []) for o in c['objects']}
        cat = d.get('catalog', {})
        if st0.get('cat_clean') != 1:                           # once: 'Хіміч', 'Хімічн', ... left by saving on every keystroke
            for n in [n for n in cat if n not in used and any(m != n and m.startswith(n) for m in cat)
                      and not cat[n].get('production') and not cat[n].get('c')]:
                del cat[n]
            st0['cat_clean'] = 1
        if os.path.exists(CATALOG_ADD):                         # new buildings go to the end of the list, existing names stay as they are
            try:
                add = json.load(open(CATALOG_ADD, encoding='utf-8'))
                have = {k.lower() for k in cat}
                for k, e in add.items():
                    if k.lower() not in have:
                        cat[k] = e
                os.replace(CATALOG_ADD, CATALOG_ADD[:-5] + '.done.json')
                d['_merged'] = True
            except Exception:
                pass
        for e in cat.values():
            e.pop('icon', None)                                 # old automatic icons: one common icon unless the user picks one
        for k, e in cat.items():                                # English / German names of the templates, editable later
            if 'names' not in e and k in lang.OBJ:
                e['names'] = dict(en=lang.OBJ[k][0], de=lang.OBJ[k][1])
        d.get('settings', {})['collapsed'] = False
        for k in ('mode', 'mini_pos'):
            d.get('settings', {}).pop(k, None)
        for c in d.get('cities', []):
            c.setdefault('extra', dict(EXTRA0))
            for k, v in EXTRA0.items():
                c['extra'].setdefault(k, v)
        return d
    except Exception:
        return default_data()


# ------------------------------------------------------------------ styling
QSS = f"""
* {{ font-family: Arimo; font-size: 13px; color: {INK}; }}
QLabel#h1 {{ font-size: 15px; font-weight: bold; color: {RED}; }}
QLabel#big {{ font-size: 15px; font-weight: bold; }}
QLabel#red {{ color: {RED}; font-weight: bold; }}
QLabel#hint {{ color: #7a6a5a; font-size: 12px; }}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{ background: {PAPER}; border: 1px solid #a08c78; border-radius: 3px; padding: 2px 4px; min-height: 20px; }}
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 0px; border: none; image: none; }}
QSpinBox:read-only, QDoubleSpinBox:read-only {{ background: #efe6d8; color: #6a5a4a; }}
QComboBox QAbstractItemView {{ background: {PAPER}; selection-background-color: #e2cdb0; selection-color: {INK}; }}
QPushButton {{ background: {MAROON}; color: white; border: 1px solid #5a2020; border-radius: 3px; padding: 4px 10px; font-weight: bold; }}
QPushButton:hover {{ background: #a84a44; }}
QPushButton#ghost {{ background: transparent; color: {MAROON}; border: 1px solid #c8b39a; }}
QPushButton#ghost:hover {{ background: #efe2cf; }}
QPushButton#tab {{ background: #9b9893; color: #f3efe8; border: 1px solid #77736d; border-bottom: none; padding: 6px 18px; font-size: 14px;
                   border-top-left-radius: 4px; border-top-right-radius: 4px; }}
QPushButton#tab:hover {{ background: #a84a44; color: white; border-color: #5a2020; }}
QPushButton#tab:checked {{ background: {MAROON}; color: white; border-color: #5a2020; }}
QFrame#vline {{ background: {MAROON}; }}
QPushButton#seg {{ background: #9b9893; color: #f3efe8; border: 1px solid #77736d; padding: 3px 10px; font-size: 12px; border-radius: 3px; }}
QPushButton#seg:hover {{ background: #a84a44; color: white; }}
QPushButton#seg:checked {{ background: {MAROON}; color: white; border-color: #5a2020; }}
QPushButton#lang {{ background: #9b9893; color: #f3efe8; border: 1px solid #77736d; padding: 2px 7px; font-size: 11px; border-radius: 3px; }}
QPushButton#lang:hover {{ background: #a84a44; color: white; }}
QPushButton#lang:checked {{ background: {MAROON}; color: white; border-color: #5a2020; }}
QLabel#shift {{ color: #6a5a4a; font-weight: bold; }}
QPushButton#res {{ background: {PAPER}; color: {INK}; border: 1px solid #a08c78; font-weight: normal; padding: 2px 6px; text-align: left; }}
QPushButton#res:hover {{ background: #efe2cf; }}
QToolButton {{ background: transparent; border: none; color: {MAROON}; font-weight: bold; font-size: 15px; }}
QPushButton#hdr {{ background: transparent; border: none; color: {RED}; font-weight: bold; font-size: 12px; padding: 0; text-align: left; }}
QPushButton#hdr:hover {{ color: #e01010; text-decoration: underline; }}
QToolButton#save {{ border: 1px solid transparent; border-radius: 4px; padding: 1px; }}
QToolButton#save:hover {{ background: rgba(146, 60, 56, 30); border-color: #c8b39a; }}
QToolButton#del {{ border: 1px solid transparent; border-radius: 4px; padding: 1px 4px; }}
QToolButton#del:hover {{ color: #e01010; background: rgba(224, 16, 16, 40); border-color: #e3a3a3; }}
QToolButton#map {{ border: 1px solid transparent; border-radius: 4px; padding: 1px 4px; }}
QToolButton#map:hover {{ background: rgba(146, 60, 56, 30); border-color: #c8b39a; }}
QFrame#toast {{ background: rgba(255, 250, 240, 235); border: 2px solid {MAROON}; border-radius: 6px; }}
QFrame#toast[bad="true"] {{ border-color: #d01010; }}
QFrame#card {{ background: rgba(255, 250, 240, 120); border: 1px solid #c8b39a; border-radius: 6px; }}
QFrame#side {{ background: rgba(240, 228, 210, 200); border: 1px solid #c8b39a; border-radius: 6px; }}
QFrame#rule {{ background: {RED}; max-height: 2px; min-height: 2px; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
QCheckBox {{ spacing: 6px; }}
QScrollBar:vertical {{ background: #eadfcd; width: 12px; }} QScrollBar::handle:vertical {{ background: #b8a080; border-radius: 5px; min-height: 30px; }}
"""


class _NoWheel:
    """scrolling the list must not change values: the wheel works only in a focused field"""
    def wheelEvent(self, e):
        if self.hasFocus():
            super().wheelEvent(e)
        else:
            e.ignore()


def group(digits):
    """'650000' -> '650 000' (plain space, independent of the Windows locale and font)"""
    neg = digits.startswith('-')
    d = digits.lstrip('-')
    out = ''
    while len(d) > 3:
        out = ' ' + d[-3:] + out
        d = d[:-3]
    return ('-' if neg else '') + d + out


def num_text(v, dec=0):
    """1200 -> '1 200', 1200.5 -> '1 200,5', 10.00 -> '10' (no trailing zeros)"""
    t = f'{v:.{dec}f}' if dec else str(int(round(v)))
    ip, _, fp = t.partition('.')
    fp = fp.rstrip('0')
    return group(ip) + (',' + fp if fp else '')


def num_clean(t):
    return re.sub(r'[^0-9,.]', '', t).replace('.', ',')


class _Grouped(_NoWheel):
    """thousands separator shown always, also live while typing; dot or comma for decimals"""
    def _setup(self):
        self.setKeyboardTracking(True)
        self.lineEdit().textEdited.connect(self._live)

    def _dec(self):
        return self.decimals() if isinstance(self, QDoubleSpinBox) else 0

    def textFromValue(self, v):
        return num_text(v, self._dec())

    def valueFromText(self, t):
        c = num_clean(t)
        ip, _, fp = c.partition(',')
        try:
            v = float((ip or '0') + '.' + (fp or '0'))
        except ValueError:
            v = 0.0
        return v if self._dec() else int(round(v))

    def validate(self, t, pos):
        c = num_clean(t)
        if c.count(',') > (1 if self._dec() else 0):
            return (QValidator.Invalid, t, pos)
        if c in ('', ','):
            return (QValidator.Intermediate, t, pos)
        ip, _, fp = c.partition(',')
        if len(fp) > self._dec():
            return (QValidator.Invalid, t, pos)
        if self.valueFromText(t) > self.maximum():
            return (QValidator.Invalid, t, pos)
        return (QValidator.Acceptable, t, pos)

    def fixup(self, t):
        return num_text(self.valueFromText(t), self._dec()) + self.suffix()

    def _live(self, t):
        le = self.lineEdit(); pos = le.cursorPosition()
        sfx = self.suffix()
        body = t[:-len(sfx)] if sfx and t.endswith(sfx) else t
        keep = len(num_clean(body[:pos]))                    # digits/commas left of the cursor
        c = num_clean(body)
        ip, comma, fp = c.partition(',')
        new = group(ip.lstrip('0') or ('0' if ip else '')) + (',' + fp if comma else '')
        if new + sfx == t:
            return
        le.setText(new + sfx)
        n = 0; cur = len(new)
        for i, ch in enumerate(new):
            if n == keep:
                cur = i; break
            if ch != ' ':
                n += 1
        le.setCursorPosition(cur if keep < n or n == keep else len(new))


class NumSpin(_Grouped, QSpinBox):
    def __init__(self):
        super().__init__(); self._setup()


class DNumSpin(_Grouped, QDoubleSpinBox):
    def __init__(self):
        super().__init__(); self._setup()


class Combo(_NoWheel, QComboBox):
    pass


def spin(maxv=10 ** 9, dec=0, val=0, w=None):
    # NB: QSS + NoButtons squeezes the text to 1 px in Qt6, so the arrows stay but get width 0 in the QSS
    s = DNumSpin() if dec else NumSpin()
    s.setFocusPolicy(Qt.StrongFocus)
    if dec:
        s.setDecimals(dec)
    s.setRange(0, maxv)
    s.setValue(val)
    s.setAlignment(Qt.AlignRight)
    if w:
        s.setFixedWidth(w)
    return s


def RN(key):
    """resource name in the current UI language"""
    return lang.res_name(key, RES_NAME)


EDU_C = os.path.join(EDITOR, 'tool_worker_relocate.png')             # game icon: workers (secondary education)
EDU_B = os.path.join(EDITOR, 'tool_worker_relocate_educated.png')    # game icon: worker with a graduation cap (higher)
TOT_ICON = os.path.join(GI, 'ui', 'residential_workers.png')
CITY_ICON = os.path.join(GI, 'ui', 'city.png')
TRASH, TRASH_RED = os.path.join(ICONS, 'trash.png'), os.path.join(ICONS, 'trash_red.png')
CAPTURES = os.path.join(HERE, 'captures')                                # every pipette shot is kept here for tuning
BUILDING_ICON = os.path.join(ICONS, 'building.png')                     # one icon for every building (user's wish)
PIPETTE_ICON = os.path.join(ICONS, 'pipette.png')
SAVE_ICON, SAVE_ICON_HOT = os.path.join(ICONS, 'save.png'), os.path.join(ICONS, 'save_hot.png')
MAP_ICON, MAP_ICON_HOT = os.path.join(GAME, 'ui', 'map_icon.png'), os.path.join(GAME, 'ui', 'map_hot.png')   # map_hot.png is optional: without it the hover look is a red tint
CALC_ICON = os.path.join(ICONS, 'calc.png')
HOTKEY_ID, HOTKEY_TEXT = 0x5752, 'Ctrl+Shift+K'                        # show / hide the calculator from anywhere, also inside the game
OWN_ICONS = os.path.join(HERE, 'icons_own')                             # the user's own building icons (48x48 PNG)
UA_ABC = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'


def sort_key(s):
    """alphabetical order that knows Ukrainian (і, ї, є, ґ in their places) and German umlauts"""
    out = []
    for ch in (s or '').lower():
        if ch in "'’ʼ`":
            continue
        ch = {'ä': 'a', 'ö': 'o', 'ü': 'u', 'ß': 's', 'é': 'e'}.get(ch, ch)
        i = UA_ABC.find(ch)
        out.append((0, 0) if ch.isspace() else (0, ord(ch)) if ch.isdigit() else (2, i) if i >= 0
                   else (1, ord(ch)) if 'a' <= ch <= 'z' else (3, ord(ch)))
    return out


def is_field(o):
    """a field: two harvests — with fertiliser (production + needs) and without (plain, no needs)"""
    return (o or {}).get('plain') is not None


def eff_lists(o, fert=None):
    """production and needs that count: an unfertilised field gives the smaller harvest and needs nothing"""
    fert = o.get('fert', True) if fert is None else fert
    if is_field(o) and not fert:
        return o.get('plain') or [], []
    return o.get('production') or [], o.get('needs') or []


def fert_icon(on):
    p = res_icon('fertiliser')
    ic = QIcon(pix(p, 24)) if p else QIcon()
    return ic if on or ic.isNull() else QIcon(ic.pixmap(24, 24, QIcon.Disabled))


def show_res(btn, items, k, period):
    """resource button: first resource with its icon and amount, the rest in the tooltip"""
    if not items:
        btn.setText('—'); btn.setIcon(QIcon()); btn.setToolTip(tr('Натисни, щоб вказати')); return
    r, a = items[0]; p = res_icon(r)
    btn.setIcon(QIcon(pix(p, 20)) if p else QIcon())
    btn.setText(fmt(a * k) + (f'  +{len(items) - 1}' if len(items) > 1 else ''))
    btn.setToolTip('\n'.join(f"{RN(r_)}: {fmt(a_ * k)} {tr(PERIOD_UNIT[period])}" for r_, a_ in items))


def obj_icon(entry):
    """icon of a building from «Мої об'єкти»: game building, game resource or own PNG; else the common building icon"""
    f = (entry or {}).get('ico')                                 # chosen by the user in «Мої об'єкти»
    p = None
    if f:
        if f.startswith('res:'):
            p = res_icon(f[4:])
        elif f.startswith('own/'):
            p = os.path.join(OWN_ICONS, f[4:])
            p = p if os.path.exists(p) else None
        else:
            p = icon_path(f)
    return p or BUILDING_ICON


PERIODS = [('day', 'за трудодень', 365), ('month', 'за місяць', 12), ('year', 'за рік', 1)]
PERIOD_UNIT = {'day': '/ день', 'month': '/ місяць', 'year': '/ рік'}


class PeriodSwitch(QWidget):
    """за трудодень | за місяць | за рік — one shared setting for both tabs"""
    def __init__(self, app):
        super().__init__(); self.app = app
        hl = QHBoxLayout(self); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(2)
        self.btns = {}
        for key, label, _ in PERIODS:
            b = QPushButton(tr(label)); b.setObjectName('seg'); b.setCheckable(True); b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, k=key: app.set_period(k)); hl.addWidget(b); self.btns[key] = b
        self.sync()

    def sync(self):
        cur = self.app.period()
        for k, b in self.btns.items():
            b.setChecked(k == cur)


class ShiftSwitch(QWidget):
    """1 зміна | 3 зміни"""
    def __init__(self, app):
        super().__init__(); self.app = app
        hl = QHBoxLayout(self); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(2)
        self.b1 = QPushButton(tr('1 зміна')); self.b3 = QPushButton(tr('3 зміни'))
        for b, one in ((self.b1, True), (self.b3, False)):
            b.setObjectName('seg'); b.setCheckable(True); b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, o=one: app.set_one_shift(o)); hl.addWidget(b)
        self.sync()

    def sync(self):
        one = self.app.one_shift(); self.b1.setChecked(one); self.b3.setChecked(not one)


def vline():
    f = QFrame(); f.setObjectName('vline'); f.setFixedWidth(2); f.setFixedHeight(28)
    return f


class DelButton(QToolButton):
    """delete button (✕ or a trash can) that lights up red under the mouse"""
    def __init__(self, tip='', trash=False):
        super().__init__(); self.setObjectName('del'); self.setCursor(Qt.PointingHandCursor); self.setToolTip(tip)
        self.trash = trash
        if trash:
            self.ic = (QIcon(pix(TRASH, 20)), QIcon(pix(TRASH_RED, 20))); self.setIcon(self.ic[0]); self.setIconSize(QSize(20, 20))
        else:
            self.setText('✕')

    def enterEvent(self, e):
        if self.trash:
            self.setIcon(self.ic[1])
        super().enterEvent(e)

    def leaveEvent(self, e):
        if self.trash:
            self.setIcon(self.ic[0])
        super().leaveEvent(e)


def pack_keys():
    """the resources the program offers (assets/resource_pack.json); their icons come from the game icons"""
    try:
        return json.load(open(os.path.join(HERE, 'assets', 'resource_pack.json'), encoding='utf-8')) or None
    except (OSError, ValueError):
        return None


def res_combo(cur=None):
    cb = Combo(); cb.setFocusPolicy(Qt.StrongFocus)
    keys = set(pack_keys() or RES_NAME)
    if cur:
        keys.add(cur)
    keys = sorted(keys, key=RN)
    for k in keys:
        p = res_icon(k)
        cb.addItem(QIcon(pix(p, 22)) if p else QIcon(), RN(k), k)
    cb.setIconSize(QSize(20, 20))
    if cur in keys:
        cb.setCurrentIndex(keys.index(cur))
    return cb


def icon_label(path, h, tip=''):
    l = QLabel(); l.setPixmap(pix(path, h)); l.setToolTip(tip)
    return l


class Stats(QWidget):
    """[icon] С 21 790   [icon] В 6 245   [icon] Разом: 28 035"""
    def __init__(self, h=22, big=True):
        super().__init__()
        hl = QHBoxLayout(self); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(4)
        self.v = []
        for path, letter, tip in ((EDU_C, tr('С'), tr('Середня освіта')), (EDU_B, tr('В'), tr('Вища освіта')),
                                  (TOT_ICON, tr('Разом:'), tr('Разом'))):
            hl.addWidget(icon_label(path, h, tip))
            l = QLabel(); l.setObjectName('big' if big else ''); l.setToolTip(tip)
            if not big:
                l.setStyleSheet('font-weight: bold;')
            hl.addWidget(l); hl.addSpacing(10)
            self.v.append((letter, l))
        self.sfx = QLabel(); self.sfx.setObjectName('hint'); hl.addWidget(self.sfx)

    def set(self, c, b, one):
        k = 3 if one else 1
        for (letter, l), val in zip(self.v, (c, b, c + b)):
            l.setText(f'{letter} {fmt(val / k)}')
        self.sfx.setText(tr('(1 зміна)') if one else '')


def map_pixmap(h, hot=False):
    """a small folded map with a pin, drawn in code (map.png / map_hot.png next to the program replace it)"""
    if hot and os.path.exists(MAP_ICON_HOT):
        return pix(MAP_ICON_HOT, h)
    if os.path.exists(MAP_ICON):
        base = pix(MAP_ICON, h)
        if not hot or base.isNull():
            return base
        pm = QPixmap(base); p = QPainter(pm); p.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        p.fillRect(pm.rect(), QColor(188, 0, 0, 80)); p.end()                 # same icon, tinted red under the mouse
        return pm
    k = 2; pm = QPixmap(h * k, h * k); pm.fill(Qt.transparent); pm.setDevicePixelRatio(k)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing); p.scale(h / 20.0, h / 20.0)
    line = QColor('#bc0000' if hot else '#6b5646'); paper = (QColor('#f7e4dc'), QColor('#efcfc4')) if hot else (QColor('#f4ead8'), QColor('#e6d6bb'))
    xs = (1.5, 7, 13, 18.5); top = (5, 3, 5, 3); bot = (17, 15, 17, 15)
    p.setPen(QPen(line, 1.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    for i in range(3):
        poly = QPolygonF([QPointF(xs[i], top[i]), QPointF(xs[i + 1], top[i + 1]), QPointF(xs[i + 1], bot[i + 1]), QPointF(xs[i], bot[i])])
        p.setBrush(paper[i % 2]); p.drawPolygon(poly)
    p.setPen(QPen(QColor('#7a1410'), 1)); p.setBrush(QColor('#d6261c'))
    p.drawEllipse(QPointF(10, 8.2), 2.3, 2.3)
    p.setPen(Qt.NoPen); p.setBrush(QColor('#fff4e6')); p.drawEllipse(QPointF(10, 8.2), 0.8, 0.8)
    p.end()
    return pm


class MapButton(QToolButton):
    """map icon next to the trash can (opens the city in «Планувальник»), lights up under the mouse"""
    def __init__(self, tip=''):
        super().__init__(); self.setObjectName('map'); self.setCursor(Qt.PointingHandCursor); self.setToolTip(tip)
        self.ic = (QIcon(map_pixmap(20)), QIcon(map_pixmap(20, True))); self.setIcon(self.ic[0]); self.setIconSize(QSize(20, 20))

    def enterEvent(self, e):
        self.setIcon(self.ic[1]); super().enterEvent(e)

    def leaveEvent(self, e):
        self.setIcon(self.ic[0]); super().leaveEvent(e)


class ResStrip(QWidget):
    """[icon] 4 388  [icon] 940 ...  — what a population needs, by the rates per 1000 residents (zero rates are left out)"""
    def __init__(self, app, h=20):
        super().__init__(); self.app = app; self.h = h; self.sig = None; self.cells = []
        self.hl = QHBoxLayout(self); self.hl.setContentsMargins(0, 0, 0, 0); self.hl.setSpacing(4)

    def rates(self):
        d = self.app.data
        return [(r, v) for r, v in list(d['rates']) + list(d['util_rates']) if v > 0]

    def rebuild(self, rates):
        while self.hl.count():
            w = self.hl.takeAt(0).widget()
            if w:
                w.hide(); w.deleteLater()
        self.cells = []
        for r, v in rates:
            self.hl.addWidget(icon_label(res_icon(r), self.h, RN(r)))
            l = QLabel(); l.setToolTip(RN(r)); l.setStyleSheet('font-weight: bold;'); self.hl.addWidget(l); self.hl.addSpacing(8)
            self.cells.append((v, l))

    def set_pop(self, pop):
        rates = self.rates()
        if rates != self.sig:
            self.sig = rates; self.rebuild(rates)
        div = self.app.period_div()
        for v, l in self.cells:
            l.setText(fmt(pop / 1000.0 * v / div))


class RatesDialog(QDialog):
    """the pencil: own rates per 1000 residents (per year) for goods and utilities"""
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.setWindowTitle(tr('Норми на 1000 жителів'))
        self.setStyleSheet(QSS + 'QDialog { background: #f3e9d9; }')
        v = QVBoxLayout(self)
        h = QLabel(tr('Норми на 1000 жителів (на рік)')); h.setObjectName('h1'); v.addWidget(h)
        note = QLabel(tr('Впиши свої числа: калькулятор і міста порахують за ними. Нуль — ресурс не показується.'))
        note.setObjectName('hint'); note.setWordWrap(True); v.addWidget(note)
        self.sp = {'rates': [], 'util_rates': []}
        for key, title in (('rates', tr('Продукти та товари')), ('util_rates', tr('Комунальні'))):
            l = QLabel(title); l.setObjectName('h1'); v.addWidget(l)
            g = QGridLayout(); g.setHorizontalSpacing(8); g.setVerticalSpacing(3)
            for i, (r, val) in enumerate(app.data[key]):
                g.addWidget(icon_label(res_icon(r), 22), i, 0); g.addWidget(QLabel(RN(r)), i, 1)
                s_ = spin(10 ** 7, 2, float(val), 100); g.addWidget(s_, i, 2); self.sp[key].append(s_)
            g.setColumnStretch(1, 1); v.addLayout(g)
        hb = QHBoxLayout()
        rb = QPushButton(tr('Типові норми')); rb.setObjectName('ghost'); rb.clicked.connect(self.defaults); hb.addWidget(rb)
        hb.addStretch()
        ok = QPushButton(tr('Готово')); ok.clicked.connect(self.accept); hb.addWidget(ok)
        v.addLayout(hb)
        self.resize(420, 120 + 30 * (len(self.sp['rates']) + len(self.sp['util_rates'])))

    def defaults(self):
        for key, dflt in (('rates', DEFAULT_RATES), ('util_rates', DEFAULT_UTIL)):
            for s_, (_, val) in zip(self.sp[key], dflt):
                s_.setValue(float(val))

    def accept(self):
        d = self.app.data
        for key in ('rates', 'util_rates'):
            for s_, item in zip(self.sp[key], d[key]):
                item[1] = s_.value()
        d['settings']['rates_custom'] = True
        super().accept(); self.app.rates_changed()


class PopCalc(QWidget):
    """calculator left of the save button: any number of residents -> what they need (rates per 1000 residents).
    «?» shows the formula, the pencil edits the rates, the ✕ in the result panel resets the number to 0"""
    def __init__(self, app, parent):
        super().__init__(parent); self.app = app
        st = app.data['settings']
        hl = QHBoxLayout(self); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(3)
        hl.addWidget(icon_label(CALC_ICON, 24, tr('Калькулятор населення')))
        self.sp = spin(10 ** 9, 0, int(st.get('calc_pop', 0)), 112); self.sp.setToolTip(tr('Скільки жителів порахувати'))
        self.sp.valueChanged.connect(self.on_pop); hl.addWidget(self.sp)
        self.q = self._btn('?', tr('Формула розрахунку'), self.show_formula); hl.addWidget(self.q)
        self.pen = self._btn('✎', tr('Змінити норми на 1000 жителів'), self.edit_rates); hl.addWidget(self.pen)
        self.panel = QFrame(parent); self.panel.setObjectName('toast')
        self.pv = QVBoxLayout(self.panel); self.pv.setContentsMargins(10, 8, 12, 10); self.pv.setSpacing(3)
        th = QHBoxLayout(); th.setSpacing(10)
        self.title = QLabel(); self.title.setObjectName('h1'); th.addWidget(self.title); th.addStretch(1)
        x = DelButton(tr('Скинути до нуля')); x.clicked.connect(lambda: self.sp.setValue(0)); th.addWidget(x, 0, Qt.AlignTop)
        self.pv.addLayout(th)
        self.grid = QGridLayout(); self.grid.setHorizontalSpacing(8); self.grid.setVerticalSpacing(3); self.pv.addLayout(self.grid)
        self.cells = []; self.sig = None
        self.refresh()

    def _btn(self, text, tip, fn):
        b = QToolButton(); b.setText(text); b.setToolTip(tip); b.setCursor(Qt.PointingHandCursor); b.clicked.connect(fn)
        return b

    def on_pop(self, v):
        self.app.data['settings']['calc_pop'] = int(v); self.refresh(); self.app.save_soon()

    def rates_all(self):
        d = self.app.data
        return [(r, v) for r, v in list(d['rates']) + list(d['util_rates'])]

    def refresh(self):
        p = self.sp.value(); div = self.app.period_div()
        per = tr({k: lbl for k, lbl, _ in PERIODS}[self.app.period()])
        self.title.setText(f"{fmt(p)} {tr('жителів')} — {per}")
        rates = [(r, v) for r, v in self.rates_all() if v > 0]
        if rates != self.sig:                                   # rebuild the rows only when the rates changed
            self.sig = rates
            while self.grid.count():
                w = self.grid.takeAt(0).widget()
                if w:
                    w.hide(); w.deleteLater()
            self.cells = []
            for i, (r, v) in enumerate(rates):
                self.grid.addWidget(icon_label(res_icon(r), 20), i, 0); self.grid.addWidget(QLabel(RN(r)), i, 1)
                o = QLabel(); o.setObjectName('red'); o.setAlignment(Qt.AlignRight | Qt.AlignVCenter); o.setMinimumWidth(90)
                self.grid.addWidget(o, i, 2); self.cells.append((v, o))
        for v, o in self.cells:
            o.setText(fmt(p / 1000.0 * v / div))
        self.panel.setVisible(p > 0 and bool(rates))
        self.panel.adjustSize(); self.place_panel()

    def place(self, save):
        """left of the save button, same height"""
        sz = self.sizeHint(); self.resize(sz)
        self.move(save.x() - sz.width() - 10, save.y() + (save.height() - sz.height()) // 2)
        self.raise_(); self.show(); self.place_panel()

    def place_panel(self):
        self.panel.move(max(0, self.x() + self.width() - self.panel.width()), self.y() + self.height() + 4)
        self.panel.raise_()

    def show_formula(self):
        app = self.app; p = self.sp.value(); div = app.period_div()
        per = tr({k: lbl for k, lbl, _ in PERIODS}[app.period()])
        rows = ''.join(f'<tr><td>{RN(r)}</td><td align="right">&nbsp;&nbsp;{fmt(v)}</td>'
                       f'<td align="right">&nbsp;&nbsp;<b>{fmt(p / 1000.0 * v / div)}</b></td></tr>' for r, v in self.rates_all())
        html = (f"<p><b>{tr('Кількість = Населення ÷ 1000 × Норма на 1000 жителів (за рік) ÷ Період')}</b></p>"
                f"<p>{tr('Період: рік — 1, місяць — 12, трудодень — 365.')}</p>"
                f"<p>{tr('Зараз')}: {fmt(p)} {tr('жителів')}, {per} (÷ {div})</p>"
                f"<table><tr><th align='left'>{tr('Ресурс')}</th><th align='right'>&nbsp;&nbsp;{tr('Норма на 1000 (за рік)')}</th>"
                f"<th align='right'>&nbsp;&nbsp;{tr('Результат')}</th></tr>{rows}</table>")
        m = QMessageBox(app); m.setWindowTitle(tr('Формула розрахунку')); m.setTextFormat(Qt.RichText); m.setText(html)
        m.setStyleSheet(QSS + 'QMessageBox { background: #f3e9d9; }'); m.exec()

    def edit_rates(self):
        RatesDialog(self.app).exec()


class PlannerTab(QWidget):
    """«Планувальник»: the city map editor (calc/planner/index.html) in an embedded browser view (Qt WebEngine).
    Its cities ARE the cities of the «Міста» tab (matched by id); blocks are kept in data.json under 'planner'.
    program -> page: CM.apply({...}); page -> program: polled with CM.take() (changes and «save as PNG / PDF» requests)."""
    PAGE = os.path.join(HERE, 'planner', 'index.html')

    def __init__(self, app):
        super().__init__(); self.app = app
        self.view = None; self.failed = False; self.loaded = False; self.ready = False; self.want = None; self._fresh = False
        self.box = QVBoxLayout(self); self.box.setContentsMargins(0, 0, 0, 0)     # the browser view is made on first use: the start-up stays as fast as before

    def _make_view(self):
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
            self.profile = QWebEngineProfile(self)                  # no name = off the record: nothing is written to disk
            self.web_page = QWebEnginePage(self.profile, self)
            self.web_page.setBackgroundColor(QColor('#f1e6cf'))
            view = QWebEngineView(); view.setPage(self.web_page)
            view.setContextMenuPolicy(Qt.NoContextMenu)
        except Exception:
            self.failed = True
            lb = QLabel(tr('Для вкладки «Планувальник» потрібен модуль PySide6 WebEngine. Закрий програму і запусти «W&R City Manager.bat» — він доставить його.'))
            lb.setWordWrap(True); lb.setAlignment(Qt.AlignCenter); self.box.addWidget(lb)
            return
        self.view = view; self.box.addWidget(view)
        view.hide()                                              # shown only when the page has drawn itself: no white / half-drawn flash
        view.loadFinished.connect(self._loaded)
        self.timer = QTimer(self); self.timer.setInterval(1500); self.timer.timeout.connect(self.pull)

    def run(self, js, cb=None):
        if self.view is None:
            return
        if cb is None:
            self.web_page.runJavaScript(js)
        else:
            self.web_page.runJavaScript(js, cb)

    def showEvent(self, e):
        super().showEvent(e); self.activate(); self._fade_in()

    def hideEvent(self, e):
        super().hideEvent(e); self.pull()

    def activate(self, cid=None):
        """first use loads the page; every use hands over the current list of cities (and opens city cid)"""
        if cid:
            self.want = cid
        if self.view is None and not self.failed:
            self._make_view()
        if self.view is None:
            return
        if not self.loaded:
            self.loaded = True
            url = QUrl.fromLocalFile(self.PAGE); url.setQuery('host=1&lang=' + lang.L)
            self.web_page.setBackgroundColor(QColor(self.paper()))
            self.view.load(url)
        elif self.ready:
            self._push(False)

    def _loaded(self, ok):
        if not ok:
            self.loaded = False; return
        self.ready = True; self.web_page.setBackgroundColor(QColor(self.paper())); self._push(True); self.timer.start()
        self._fresh = True; self._css('none', 0)                 # the page starts invisible: the paper colour shows until it fades in
        QTimer.singleShot(350, self._reveal)
        QTimer.singleShot(5000, self._fade_in)                   # safety: the page never stays invisible

    def _reveal(self):
        if self.view is not None:
            self.view.show(); self._fade_in()

    def _css(self, transition, opacity):
        self.run("(function(){var s=document.documentElement.style;s.transition='%s';s.opacity='%s'})()" % (transition, opacity))

    def _fade_in(self):
        """the first time the page is on screen it comes out of the paper colour instead of popping in"""
        if self._fresh and self.ready and self.view is not None and self.isVisible():
            self._fresh = False
            QTimer.singleShot(70, lambda: self._css('opacity 240ms ease', 1))

    def relang(self):
        """the window language changed: the page follows it without being reloaded (so it never blinks)"""
        if self.view is not None and self.ready:
            self._push(False)

    def prewarm(self):
        """shortly after start-up the page is loaded in the background, so the first switch to the tab is instant"""
        if self.view is None and not self.failed and not self.loaded:
            self.activate()

    def paper(self):
        """average colour of the window's paper texture under this tab: the page uses it as its background (no light patch, no flash)"""
        try:
            bg = getattr(self.app, '_bg', None)
            if bg is None or bg.isNull():
                return '#f3e9d9'
            img = bg.toImage(); dpr = bg.devicePixelRatio() or 1.0
            o = self.mapTo(self.app, QPoint(0, 0)); w, h = max(1, self.width()), max(1, self.height())
            r = g = b = n = 0
            for i in range(1, 8):
                for j in range(1, 8):
                    x, y = int((o.x() + w * i / 8.0) * dpr), int((o.y() + h * j / 8.0) * dpr)
                    if 0 <= x < img.width() and 0 <= y < img.height():
                        c = img.pixelColor(x, y); r += c.red(); g += c.green(); b += c.blue(); n += 1
            if n:
                return '#%02x%02x%02x' % (r // n, g // n, b // n)
        except Exception:
            pass
        return '#f3e9d9'

    def _push(self, first):
        pl = self.app.data.setdefault('planner', {'cities': {}, 'opts': {}})
        cities = [{'id': c['id'], 'name': c['name']} for c in self.app.data['cities']]
        key = (lang.L, json.dumps(cities))
        if not first and not self.want and key == getattr(self, '_sent', None):
            return                                              # nothing new: the page is left alone (no repaint)
        self._sent = key
        msg = {'cities': cities, 'cur': self.want, 'lang': lang.L, 'bg': self.paper()}
        if first:
            msg['planner'] = pl
            if not self.want:
                msg['cur'] = pl.get('cur')
        self.want = None
        self.run('CM.apply(%s)' % json.dumps(msg))

    def pull(self):
        if self.ready:
            self.run('window.CM && CM.take()', self._got)

    def flush(self):
        """before the window closes: take the last changes (waits up to ~1 s for the page)"""
        if not self.ready:
            return
        from PySide6.QtCore import QEventLoop
        loop = QEventLoop(); got = []
        self.run('window.CM && CM.take()', lambda r: (got.append(r), loop.quit()))
        QTimer.singleShot(1000, loop.quit); loop.exec(QEventLoop.ExcludeUserInputEvents)      # no clicks get in while it waits
        if got:
            self._got(got[0])

    def _got(self, res):
        if not res:
            return
        try:
            d = json.loads(res)
        except Exception:
            return
        pl = self.app.data.setdefault('planner', {'cities': {}, 'opts': {}})
        ids = {c['id'] for c in self.app.data['cities']}
        for cid, c in d.get('cities', {}).items():
            if cid in ids:
                pl.setdefault('cities', {})[cid] = c
        if d.get('opts'):
            pl['opts'] = d['opts']
        if d.get('cur') in ids:
            pl['cur'] = d['cur']
        if d.get('cities') or d.get('opts'):
            self.app.save_soon()
        if d.get('export'):
            QTimer.singleShot(0, lambda e=d['export']: self.save_export(e))

    def save_export(self, ex):
        """the page hands over a PNG of the map: save it as PNG or PDF"""
        from PySide6.QtWidgets import QFileDialog
        import base64, io, time
        pdf = ex.get('kind') == 'pdf'
        name = re.sub(r'[\\/:*?"<>|]', '_', str(ex.get('name') or 'city'))
        base = os.path.join(CM, name + time.strftime(' %Y-%m-%d') + ('.pdf' if pdf else '.png'))
        path, _ = QFileDialog.getSaveFileName(self.app, tr('Зберегти карту'), base, 'PDF (*.pdf)' if pdf else 'PNG (*.png)')
        if not path:
            return
        try:
            raw = base64.b64decode(str(ex['data']).split(',', 1)[1])
            if pdf:
                if not path.lower().endswith('.pdf'):
                    path += '.pdf'
                Image.open(io.BytesIO(raw)).convert('RGB').save(path, 'PDF', resolution=150.0)
            else:
                if not path.lower().endswith('.png'):
                    path += '.png'
                with open(path, 'wb') as f:
                    f.write(raw)
        except Exception as e:
            QMessageBox.warning(self.app, tr('Зберегти карту'), tr('Не вдалося зберегти: {e}').format(e=e)); return
        from PySide6.QtGui import QDesktopServices
        self.app.toast.on_check = lambda p=path: QDesktopServices.openUrl(QUrl.fromLocalFile(p))
        self.app.toast.show_msg(tr('Збережено: {p}').format(p=path), icon=SAVE_ICON, button=tr('Відкрити'))


# ------------------------------------------------------------------ dialogs
class ResListDialog(QDialog):
    """edit a list of [resource, amount per year]"""
    def __init__(self, title, items, parent=None, yearly=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(QSS + 'QDialog { background: #f3e9d9; }')
        self.rows = []; self.k = 1.0 if yearly else 365.0             # fields are entered per year, buildings per workday
        v = QVBoxLayout(self)
        h = QLabel((tr('{t} — за рік, 1 поле') if yearly else tr('{t} — за 1 трудодень, 1 будівля при 100%')).format(t=title))
        h.setObjectName('h1'); v.addWidget(h)
        note = QLabel(tr('Для поля вводь урожай і добрива за рік.') if yearly else
                      tr('Вводь число за одну зміну — як «за 1 трудодень» у вікні гри. За місяць і рік програма порахує сама.'))
        note.setObjectName('red'); note.setWordWrap(True); v.addWidget(note)
        self.box = QVBoxLayout(); v.addLayout(self.box)
        for r, a in items:
            self.add(r, a / self.k)
        hb = QHBoxLayout()
        b = QPushButton(tr('+ Ресурс')); b.setObjectName('ghost'); b.clicked.connect(lambda: self.add('food', 0)); hb.addWidget(b)
        hb.addStretch()
        ok = QPushButton(tr('Готово')); ok.clicked.connect(self.accept); hb.addWidget(ok)
        v.addLayout(hb)
        self.resize(480, 150 + 40 * max(1, len(items)))

    def add(self, r, a):
        w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0, 0, 0, 0)
        cb = res_combo(r); sp = spin(10 ** 9, 3, float(a), 120)
        x = DelButton(); h.addWidget(cb, 1); h.addWidget(sp); h.addWidget(x)
        row = (w, cb, sp)
        x.clicked.connect(lambda: (self.rows.remove(row), w.hide(), w.deleteLater()))
        self.rows.append(row); self.box.addWidget(w)

    def result_items(self):
        return [[cb.currentData(), round(sp.value() * self.k, 3)] for _, cb, sp in self.rows if sp.value() > 0]


class IconPicker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Іконка будівлі'))
        self.setStyleSheet(QSS + 'QDialog { background: #f3e9d9; } QListWidget { background: #faf4ea; }')
        self.choice = None
        v = QVBoxLayout(self)
        self.q = QLineEdit(); self.q.setPlaceholderText(tr('пошук англійською: school, factory, power…')); v.addWidget(self.q)
        self.lst = QListWidget(); self.lst.setViewMode(QListWidget.IconMode); self.lst.setIconSize(QSize(56, 56))
        self.lst.setGridSize(QSize(92, 92)); self.lst.setResizeMode(QListWidget.Adjust); v.addWidget(self.lst)
        self.files = sorted(f for f in os.listdir(EDITOR) if f.startswith('tool_') and f.endswith('.png')) if os.path.isdir(EDITOR) else []
        self._todo = []
        self.q.textChanged.connect(self.fill); self.fill('')
        self.lst.itemDoubleClicked.connect(self.pick)
        self.resize(720, 520)

    def fill(self, t):
        self.lst.clear(); self._todo = []
        for f in self.files:
            if t.lower() in f.lower():
                it = QListWidgetItem(f[5:-4].replace('_', ' ')[:16])
                it.setData(Qt.UserRole, f); self.lst.addItem(it); self._todo.append((it, os.path.join(EDITOR, f), 56))
        self._todo.reverse(); self.icons()

    def icons(self):
        """the icons come in batches: the picker opens at once and the first rows have theirs a moment later"""
        n = 24
        while self._todo and n:
            it, p, h = self._todo.pop(); n -= 1
            try:
                it.setIcon(QIcon(pix(p, h)))
            except RuntimeError:                              # the list was cleared meanwhile
                self._todo = []; return
        if self._todo:
            QTimer.singleShot(0, self.icons)

    def pick(self, it):
        self.choice = it.data(Qt.UserRole); self.accept()


# ------------------------------------------------------------------ pipette (read a building window from the game)
def qimage_to_pil(qi):
    qi = qi.convertToFormat(QImage.Format_RGBA8888)
    return Image.frombuffer('RGBA', (qi.width(), qi.height()), bytes(qi.constBits()), 'raw', 'RGBA', qi.bytesPerLine(), 1).convert('RGB')


class Snipper(QWidget):
    """frozen full-screen shot of one monitor; drag a rectangle around the building window, Esc cancels"""
    done = Signal(object)

    def __init__(self, screen):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.pm = screen.grabWindow(0)
        self.dpr = self.pm.devicePixelRatio() or 1.0
        self.setGeometry(screen.geometry())
        self.setCursor(Qt.CrossCursor); self.setMouseTracking(True)
        self.origin = None; self.sel = QRect(); self.sent = False

    def paintEvent(self, e):
        p = QPainter(self)
        p.drawPixmap(self.rect(), self.pm)
        p.fillRect(self.rect(), QColor(0, 0, 0, 120))
        r = self.sel.normalized()
        if r.width() > 2 and r.height() > 2:
            d = self.dpr
            p.drawPixmap(r, self.pm, QRect(int(r.x() * d), int(r.y() * d), int(r.width() * d), int(r.height() * d)))
            p.setPen(QPen(QColor(230, 40, 30), 2)); p.drawRect(r)
        f = QFont('Arimo', 13); f.setBold(True); p.setFont(f)
        msg = tr('Обведи мишкою вікно будівлі в грі. Esc — скасувати.')
        w = p.fontMetrics().horizontalAdvance(msg) + 40
        box = QRect((self.width() - w) // 2, 24, w, 40)
        p.fillRect(box, QColor(146, 60, 56, 235)); p.setPen(QColor(255, 255, 255)); p.drawText(box, Qt.AlignCenter, msg)

    def mousePressEvent(self, e):
        self.origin = e.position().toPoint(); self.sel = QRect(self.origin, self.origin); self.update()

    def mouseMoveEvent(self, e):
        if self.origin is not None:
            self.sel = QRect(self.origin, e.position().toPoint()); self.update()

    def mouseReleaseEvent(self, e):
        r = self.sel.normalized(); d = self.dpr
        img = None
        if r.width() > 20 and r.height() > 20:
            crop = self.pm.copy(QRect(int(r.x() * d), int(r.y() * d), int(r.width() * d), int(r.height() * d)))
            img = qimage_to_pil(crop.toImage())
        self.finish(img)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.finish(None)

    def finish(self, img):
        if not self.sent:
            self.sent = True; self.done.emit(img)
        self.close()


class PipetteDialog(QDialog):
    """shows what was read; per workday values -> per year (x365); water and electricity unchecked by default"""
    def __init__(self, parent, img, result):
        super().__init__(parent)
        self.setWindowTitle(tr('Піпетка — що знайдено'))
        self.setStyleSheet(QSS + 'QDialog { background: #f3e9d9; }')
        self.lists = {}
        h = QHBoxLayout(self)
        th = QLabel(); q = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format_RGB888).copy()
        th.setPixmap(QPixmap.fromImage(q).scaled(380, 520, Qt.KeepAspectRatio, Qt.SmoothTransformation)); th.setAlignment(Qt.AlignTop)
        h.addWidget(th)
        v = QVBoxLayout(); h.addLayout(v, 1)
        import pipette as PP
        for key, title in (('production', tr('Виробництво за трудодень')), ('needs', tr('Потреби за трудодень'))):
            l = QLabel(title); l.setObjectName('h1'); v.addWidget(l)
            box = QVBoxLayout(); v.addLayout(box); self.lists[key] = (box, [])
            for it in result.get(key, []):
                self.add(key, it['key'], it['value'], it['key'] not in PP.UTILITY)
            b = QPushButton(tr('+ Ресурс')); b.setObjectName('ghost'); b.clicked.connect(lambda _, k=key: self.add(k, 'food', 0, True))
            v.addWidget(b, 0, Qt.AlignLeft)
        l = QLabel(tr('Люди')); l.setObjectName('h1'); v.addWidget(l)
        sg = QGridLayout(); v.addLayout(sg); self.staff_sp = {}
        for i, (key, label, icon) in enumerate((('workers', tr('Трудівники (1 зміна)'), EDU_C), ('engineers', tr('Інженери (1 зміна)'), EDU_B))):
            sg.addWidget(icon_label(icon, 20), i, 0); sg.addWidget(QLabel(label), i, 1)
            sp_ = spin(10 ** 6, 0, result.get(key) or 0, 90); sg.addWidget(sp_, i, 2); self.staff_sp[key] = sp_
        if not result.get('production') and not result.get('needs'):
            n = QLabel(tr('Нічого не знайдено. Обведи вікно разом з рядками виробництва і споживання.')); n.setObjectName('red'); n.setWordWrap(True)
            v.addWidget(n)
        hint = QLabel(tr('Рік = значення × 365 днів. Продуктивність % і кількість будівель задаються в таблиці. Вода й електрика за замовчуванням не враховуються.'))
        hint.setObjectName('hint'); hint.setWordWrap(True); v.addWidget(hint)
        v.addStretch()
        hb = QHBoxLayout(); hb.addStretch()
        c = QPushButton(tr('Скасувати')); c.setObjectName('ghost'); c.clicked.connect(self.reject); hb.addWidget(c)
        ok = QPushButton(tr('Записати в рядок')); ok.clicked.connect(self.accept); hb.addWidget(ok)
        v.addLayout(hb)
        self.resize(900, 560)

    def add(self, key, res, value, on):
        box, rows = self.lists[key]
        w = QWidget(); hl = QHBoxLayout(w); hl.setContentsMargins(0, 0, 0, 0)
        chk = QCheckBox(); chk.setChecked(on); hl.addWidget(chk)
        cb = res_combo(res); hl.addWidget(cb, 1)
        sp = spin(10 ** 8, 3, float(value), 100); hl.addWidget(sp)
        yr = QLabel(); yr.setMinimumWidth(120); hl.addWidget(yr)
        x = DelButton(); hl.addWidget(x)
        upd = lambda *_: yr.setText(tr('→ {v} / рік').format(v=fmt(sp.value() * 365)))
        sp.valueChanged.connect(upd); upd()
        row = (w, chk, cb, sp)
        x.clicked.connect(lambda: (rows.remove(row), w.hide(), w.deleteLater()))
        rows.append(row); box.addWidget(w)

    def values(self, key):
        return [[cb.currentData(), round(sp.value() * 365, 3)] for _, chk, cb, sp in self.lists[key][1] if chk.isChecked() and sp.value() > 0]

    def staff(self):
        return {k: int(sp.value()) for k, sp in self.staff_sp.items() if sp.value() > 0}


def planner_help_icons():
    """small icons for the Planner part of the instruction: map, «+» button, eye, library plate; drawn in code, saved to a temp folder"""
    import tempfile
    d = os.path.join(tempfile.gettempdir(), 'wr_calc_help'); out = {}
    try:
        os.makedirs(d, exist_ok=True)
        S = 40

        def new():
            pm = QPixmap(S, S); pm.fill(Qt.transparent)
            p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing); return pm, p

        def done(n, pm, p):
            p.end(); f = os.path.join(d, n + '.png'); pm.save(f, 'PNG'); out[n] = f

        out_map = os.path.join(d, 'map.png'); map_pixmap(20).save(out_map, 'PNG'); out['map'] = out_map
        pm, p = new()                                            # the «+» button of the library
        p.setPen(QPen(QColor('#b48f5a'), 2)); p.setBrush(QColor('#f6e8c6')); p.drawRoundedRect(3, 3, S - 6, S - 6, 6, 6)
        p.setPen(QPen(QColor('#8f3430'), 4, Qt.SolidLine, Qt.RoundCap)); p.drawLine(12, 20, 28, 20); p.drawLine(20, 12, 20, 28); done('plus', pm, p)
        pm, p = new()                                            # eye
        p.setPen(QPen(QColor('#4a2c1a'), 3, Qt.SolidLine, Qt.RoundCap)); p.setBrush(Qt.NoBrush); p.drawEllipse(QPointF(20, 20), 16, 9)
        p.setBrush(QColor('#4a2c1a')); p.drawEllipse(QPointF(20, 20), 4.5, 4.5); done('eye', pm, p)
        for n, col in (('plate_blue', '#3b86c4'), ('plate_red', '#d4202a'), ('plate_purple', '#5b3a8a')):   # coloured block plates with a white glyph
            pm, p = new(); p.setPen(QPen(QColor('#0006'), 1.5)); p.setBrush(QColor(col)); p.drawRoundedRect(3, 3, S - 6, S - 6, 6, 6)
            p.setPen(Qt.NoPen); p.setBrush(QColor('white'))
            if n == 'plate_blue':
                p.drawPolygon(QPolygonF([QPointF(20, 9), QPointF(30, 24), QPointF(10, 24)])); p.drawEllipse(QPointF(20, 25), 7.5, 7.5)
            elif n == 'plate_red':
                p.drawEllipse(QPointF(20, 20), 12, 12); p.setBrush(QColor(col)); p.drawRect(13, 14, 3, 12); p.drawRect(24, 14, 3, 12); p.drawPolygon(QPolygonF([QPointF(16, 14), QPointF(20, 21), QPointF(24, 14), QPointF(24, 18), QPointF(20, 25), QPointF(16, 18)]))
            else:
                p.drawRect(7, 15, 26, 10); p.setBrush(QColor(col)); p.drawRect(10, 19, 20, 2)
            done(n, pm, p)
    except Exception:
        pass
    return out


def help_with_icons():
    """instruction text with [[name]] replaced by the same icons the program shows"""
    hd = os.path.join(HERE, 'help')
    icons = {n: os.path.join(hd, n + '.png') for n in ('minus', 'pin_on', 'pin_off', 'close', 'help')}
    icons.update(trash=TRASH, trash_red=TRASH_RED, pipette=PIPETTE_ICON, building=BUILDING_ICON, city=CITY_ICON,
                 edu_c=EDU_C, edu_b=EDU_B, total=TOT_ICON, save=SAVE_ICON)
    chips = {'minus', 'pin_on', 'pin_off', 'close', 'help'}
    icons.update(planner_help_icons())

    def img(m):
        n = m.group(1)
        p = icons.get(n) or res_icon(n)
        if not p or not os.path.exists(p):
            return ''
        pm = QPixmap(p); h = 24 if n in chips else 20
        w = max(1, round(pm.width() * h / max(1, pm.height())))
        return f'<img src="{QUrl.fromLocalFile(p).toString()}" width="{w}" height="{h}">'
    return re.sub(r'\[\[(\w+)\]\]', img, lang.help_html())


class HelpDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(tr('Інструкція'))
        self.setStyleSheet(QSS + 'QDialog { background: #f3e9d9; }')
        v = QVBoxLayout(self)
        sc = QScrollArea(); sc.setWidgetResizable(True); v.addWidget(sc)
        l = QLabel(help_with_icons()); l.setWordWrap(True); l.setTextFormat(Qt.RichText); l.setAlignment(Qt.AlignTop)
        l.setContentsMargins(10, 6, 10, 6); sc.setWidget(l)
        b = QPushButton(tr('Готово')); b.clicked.connect(self.accept); v.addWidget(b, 0, Qt.AlignRight)
        self.resize(640, 640)


class Powered(QLabel):
    """«Powered by Mr.Scrudge» at the bottom: lights up yellow under the mouse and opens the author's Telegram"""
    URL = 'https://t.me/andrii_kon'

    def __init__(self):
        super().__init__('Powered by Mr.Scrudge'); self.setObjectName('powered')
        self.setCursor(Qt.PointingHandCursor); self.setToolTip(self.URL); self.hot(False)

    def hot(self, on):
        fg, bg = ('#ffd84a', MAROON) if on else ('#8a7a6a', 'transparent')
        self.setStyleSheet(f'QLabel#powered {{ color: {fg}; background: {bg}; border-radius: 4px; padding: 1px 7px;'
                           f' font-size: 11px; font-weight: bold; }}')

    def enterEvent(self, e):
        self.hot(True); super().enterEvent(e)

    def leaveEvent(self, e):
        self.hot(False); super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl(self.URL))


class Toast(QFrame):
    """short note at the bottom of the calculator: what the pipette wrote; «Перевірити» opens the editable list"""
    def __init__(self, parent):
        super().__init__(parent); self.setObjectName('toast'); self.hide()
        h = QHBoxLayout(self); h.setContentsMargins(10, 6, 6, 6)
        self.icon = icon_label(PIPETTE_ICON, 22); h.addWidget(self.icon)
        self.text = QLabel(); self.text.setWordWrap(True); h.addWidget(self.text, 1)
        self.btn = QPushButton(tr('Перевірити')); self.btn.setObjectName('ghost'); h.addWidget(self.btn)
        x = DelButton(); x.clicked.connect(self.hide); h.addWidget(x)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.hide)
        self.on_check = None
        self.btn.clicked.connect(lambda: (self.hide(), self.on_check and self.on_check()))

    def show_msg(self, html, bad=False, secs=12, icon=None, button=None):
        """button: text of the action button (default «Перевірити»), '' hides it"""
        self.setProperty('bad', bad); self.style().unpolish(self); self.style().polish(self)
        self.icon.setPixmap(pix(icon or PIPETTE_ICON, 22))
        b = tr('Перевірити') if button is None else button
        self.btn.setText(b); self.btn.setVisible(bool(b))
        self.text.setText(html); self.show(); self.raise_(); self.timer.start(secs * 1000)


# ------------------------------------------------------------------ tab 1: cities
def set_pip(btn, needs_btn, fert):
    """fert None: a building — the pipette; True / False: a field — fertiliser on / off"""
    if fert is None:
        btn.setIcon(QIcon(pix(PIPETTE_ICON, 24)))
        btn.setToolTip(tr('Піпетка: обведи у грі вікно будівлі — програма зчитає виробництво й потреби'))
        needs_btn.setEnabled(True)
    else:
        btn.setIcon(fert_icon(fert))
        btn.setToolTip(tr('З добривами — натисни, щоб без добрив') if fert else tr('Без добрив — натисни, щоб з добривами'))
        needs_btn.setEnabled(fert)


class ObjRow:
    """one object (building) line inside a city"""
    @staticmethod
    def cols():
        return ['', tr("Об'єкт"), tr('К-сть'), tr('Продукт. %'), tr('Виробництво'), tr('Потреби'), '',
                tr('С (3 зміни)'), tr('В (3 зміни)'), tr('Разом'), '']

    def __init__(self, card, obj):
        self.card, self.o = card, obj
        app = card.app
        self.icon = icon_label(obj_icon(app.data['catalog'].get(obj['name'])), 26)
        self.name = Combo(); self.name.setFocusPolicy(Qt.StrongFocus); self.name.setEditable(True); self.name.setInsertPolicy(QComboBox.NoInsert)
        self.name.setMinimumWidth(190); self._names_v = None; self.fill_names()
        self.name.completer().setCompletionMode(QCompleter.PopupCompletion); self.name.completer().setFilterMode(Qt.MatchContains)
        self.count = spin(9999, 0, obj['count'], 52)
        self.prod = spin(500, 0, obj['prod'], 58); self.prod.setSuffix(' %')
        self.production = QPushButton(); self.production.setObjectName('res')
        self.needs = QPushButton(); self.needs.setObjectName('res')
        self.pip = QToolButton(); self.pip.setIcon(QIcon(pix(PIPETTE_ICON, 24))); self.pip.setIconSize(QSize(24, 24))
        self.pip.setCursor(Qt.PointingHandCursor)
        self.pip.clicked.connect(self.on_pip)
        self.c = spin(10 ** 7, 0, obj['c'], 74); self.b = spin(10 ** 7, 0, obj['b'], 74)
        self.tot = QLabel(); self.tot.setAlignment(Qt.AlignRight | Qt.AlignVCenter); self.tot.setMinimumWidth(60); self.tot.setObjectName('big')
        self.rm = DelButton(tr("Прибрати об'єкт"))
        self.widgets = [self.icon, self.name, self.count, self.prod, self.production, self.needs, self.pip, self.c, self.b, self.tot, self.rm]
        self.name.lineEdit().editingFinished.connect(lambda: self.on_name(self.name.currentText()))
        self.name.activated.connect(lambda i: self.on_key(self.name.itemData(i) or self.name.currentText()))
        self.count.valueChanged.connect(self.on_count)
        self.prod.valueChanged.connect(self.on_prod)
        self.c.valueChanged.connect(lambda v: self.on_cb('c', v))
        self.b.valueChanged.connect(lambda v: self.on_cb('b', v))
        self.production.clicked.connect(lambda: self.edit_list('production', tr('Виробництво')))
        self.needs.clicked.connect(lambda: self.edit_list('needs', tr('Потреби')))
        self.rm.clicked.connect(lambda: card.remove_obj(self))
        self.refresh()

    def fill_names(self):
        """building list in the current language (text = name shown, data = the key in «Мої об'єкти»)"""
        app = self.card.app
        if self._names_v == app.names_v and not self.name.hasFocus():
            return self.show_name()
        self.name.blockSignals(True); self.name.clear()
        for d, k in app.sorted_names():
            self.name.addItem(d, k)
        self.name.blockSignals(False); self._names_v = app.names_v
        self.show_name()

    def show_name(self):
        app = self.card.app; d = app.obj_disp(self.o['name'])
        self.name.blockSignals(True)
        i = self.name.findData(self.o['name'])
        if i >= 0:
            self.name.setCurrentIndex(i)
        if self.name.currentText() != d:
            self.name.setEditText(d)
        self.name.blockSignals(False)
        self.icon.setPixmap(pix(obj_icon(app.data['catalog'].get(self.o['name'])), 26))

    def refresh(self):
        o, one = self.o, self.card.app.one_shift()
        k = self.factor() / self.card.app.period_div()
        prod, need = eff_lists(o)
        show_res(self.production, prod, k, self.card.app.period()); show_res(self.needs, need, k, self.card.app.period())
        set_pip(self.pip, self.needs, o.get('fert', True) if is_field(o) else None)
        n = max(1, o['count'])
        for s_, key in ((self.c, 'c'), (self.b, 'b')):
            tot = o[key] * n
            s_.blockSignals(True)
            if one:
                s_.setReadOnly(True); s_.setValue(int(round(tot / 3)))
            else:
                s_.setReadOnly(False); s_.setValue(int(round(tot)))
            s_.blockSignals(False)
        t = (o['c'] + o['b']) * n
        self.tot.setText(fmt(t / 3 if one else t))

    def on_pip(self):
        if is_field(self.o):                                         # a field: with / without fertiliser
            self.o['fert'] = not self.o.get('fert', True); self.refresh(); self.card.changed()
        else:
            self.card.app.start_pipette(self)

    def factor(self):
        """stored values are per year for ONE building at 100 %; the table shows them x productivity x count"""
        return self.o['prod'] / 100.0 * max(1, self.o['count'])

    def title(self):
        return self.card.app.obj_disp(self.o['name']) or tr("Об'єкт")

    def apply_pipette(self, production, needs, staff):
        """what the pipette read: per-building lists and people per shift (x3 for three shifts)"""
        if production or needs:
            self.o['production'], self.o['needs'] = production, needs
        if staff.get('workers') is not None:
            self.o['c'] = staff['workers'] * 3
        if staff.get('engineers') is not None:
            self.o['b'] = staff['engineers'] * 3
        self.remember(); self.refresh(); self.card.changed()

    def on_name(self, t):
        self.on_key(self.card.app.obj_key(t))

    def on_key(self, t):
        t = (t or '').strip()
        if t == self.o['name']:
            if self.name.currentText() != self.card.app.obj_disp(t):
                self.show_name()
            return
        self.o['name'] = t
        cat = self.card.app.data['catalog'].get(self.o['name'])
        if cat:                                             # known building: take its values from «Мої об'єкти»
            self.o.update(c=cat.get('c', 0), b=cat.get('b', 0),
                          production=[list(x) for x in cat.get('production', [])], needs=[list(x) for x in cat.get('needs', [])])
            if is_field(cat):
                self.o['plain'] = [list(x) for x in cat['plain']]
            else:
                self.o.pop('plain', None)
        self.remember(); self.refresh(); self.card.changed()
        self.card.app.catalog_names_changed()

    def on_count(self, v):
        self.o['count'] = v; self.refresh(); self.card.changed()          # totals scale, per-building values stay

    def on_prod(self, v):
        self.o['prod'] = v; self.refresh(); self.card.changed()

    def on_cb(self, key, v):
        if self.card.app.one_shift():
            return
        self.o[key] = v / max(1, self.o['count'])                       # typed as the row total
        self.remember(); self.refresh(); self.card.changed()

    def remember(self):
        """the building's definition goes to «Мої об'єкти» and to every other row with the same name"""
        o = self.o
        if o['name']:
            self.card.app.store_object(o['name'], o, source=self)

    def edit_list(self, key, title):
        if key == 'production' and is_field(self.o) and not self.o.get('fert', True):
            key = 'plain'                                            # the harvest without fertiliser
        dlg = ResListDialog(title, self.o.get(key, []), self.card.app, yearly=is_field(self.o))
        if dlg.exec():
            self.o[key] = dlg.result_items(); self.remember(); self.refresh(); self.card.changed()



class CityCard(QFrame):
    def __init__(self, app, city):
        super().__init__(); self.setObjectName('card')
        self.app, self.city = app, city
        self.rows = []
        v = QVBoxLayout(self); v.setContentsMargins(8, 6, 8, 8); v.setSpacing(4)
        # header
        hd = QHBoxLayout()
        self.tog = QToolButton(); self.tog.clicked.connect(self.toggle); hd.addWidget(self.tog)
        hd.addWidget(icon_label(CITY_ICON, 26))
        self.name = QLineEdit(city['name']); self.name.setFixedWidth(180); self.name.setStyleSheet('font-weight: bold; font-size: 14px;')
        self.name.textChanged.connect(self.on_name); hd.addWidget(self.name)
        hd.addSpacing(14)
        self.stats = Stats(20, big=False); hd.addWidget(self.stats)
        hd.addSpacing(18)
        self.strip = ResStrip(app, 20); hd.addWidget(self.strip)
        hd.addStretch(1)
        self.map_btn = MapButton(tr('Карта')); hd.addWidget(self.map_btn)
        self.map_btn.clicked.connect(lambda: self.app.open_planner(self.city['id']))
        rm = DelButton(tr('Видалити місто'), trash=True); rm.clicked.connect(self.delete); hd.addWidget(rm)
        v.addLayout(hd)
        # body: objects grid + side panel
        self.body = QWidget(); bl = QHBoxLayout(self.body); bl.setContentsMargins(0, 4, 0, 0)
        left = QVBoxLayout(); bl.addLayout(left, 1)
        tb = QHBoxLayout()
        add = QPushButton(tr("+ Додати об'єкт")); add.setObjectName('ghost'); add.clicked.connect(self.add_obj); tb.addWidget(add)
        tb.addStretch(); left.addLayout(tb)
        self.grid = QGridLayout(); self.grid.setHorizontalSpacing(6); self.grid.setVerticalSpacing(3)
        self.grid.setColumnStretch(1, 1)                      # spare width goes to the building name, not between columns
        for i, t in enumerate(ObjRow.cols()):
            box = QWidget(); hl = QHBoxLayout(box); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(3)
            if i in (7, 8):
                hl.addWidget(icon_label(EDU_C if i == 7 else EDU_B, 18))
            l = QLabel(t); l.setObjectName('h1' if t else ''); l.setStyleSheet('font-size: 12px;'); hl.addWidget(l); hl.addStretch()
            self.grid.addWidget(box, 0, i)
        left.addLayout(self.grid)
        rule = QFrame(); rule.setObjectName('rule'); left.addWidget(rule)
        fb = QHBoxLayout()
        fb.addStretch()
        fg = QGridLayout(); fg.setHorizontalSpacing(14); fg.setVerticalSpacing(2)   # two footer lines: 1 shift and 3 shifts
        self.foot = []
        for r, (shift_lbl, k) in enumerate(((tr('(1 зміна)').strip('()'), 3), (tr('С (3 зміни)').split('(')[-1].rstrip(')'), 1))):
            sl = QLabel(shift_lbl + ':'); sl.setObjectName('shift'); fg.addWidget(sl, r, 0)
            cells = []
            for j, (path, tip) in enumerate(((EDU_C, tr('Середня освіта')), (EDU_B, tr('Вища освіта')), (TOT_ICON, tr('Разом')))):
                fg.addWidget(icon_label(path, 18, tip), r, 1 + j * 2)
                l = QLabel(); l.setObjectName('big'); l.setToolTip(tip); l.setAlignment(Qt.AlignRight | Qt.AlignVCenter); l.setMinimumWidth(70)
                fg.addWidget(l, r, 2 + j * 2); cells.append(l)
            self.foot.append((k, cells))
        fb.addLayout(fg)
        left.addLayout(fb)
        # side panel (extra calculations), mostly collapsed
        self.side_btn = QToolButton(); self.side_btn.setToolTip(tr('Додатково: будинки, зупинки')); self.side_btn.clicked.connect(self.toggle_side)
        self.side_btn.setStyleSheet('font-size: 13px;')
        bl.addWidget(self.side_btn, 0, Qt.AlignTop)
        self.side = QFrame(); self.side.setObjectName('side'); self.side.setFixedWidth(290); bl.addWidget(self.side, 0, Qt.AlignTop)
        self.build_side()
        v.addWidget(self.body)
        for o in city['objects']:
            self._add_row(o)
        self.apply_open(); self.update_sums()

    # ----- side panel
    def build_side(self):
        e = self.city['extra']
        g = QGridLayout(self.side); g.setContentsMargins(10, 8, 10, 10); g.setVerticalSpacing(4)
        r = 0

        def head(t):
            nonlocal r
            l = QLabel(t); l.setObjectName('h1'); g.addWidget(l, r, 0, 1, 3); r += 1

        def param(label, key, dec=0, maxv=10 ** 7):
            nonlocal r
            g.addWidget(QLabel(label), r, 0, 1, 2)
            s_ = spin(maxv, dec, e[key], 80); g.addWidget(s_, r, 2)
            s_.valueChanged.connect(lambda val, k=key: (e.__setitem__(k, val), self.update_sums(), self.app.save_soon())); r += 1
            return s_

        def out(label):
            nonlocal r
            g.addWidget(QLabel(label), r, 0, 1, 2); l = QLabel('—'); l.setObjectName('red'); l.setAlignment(Qt.AlignRight)
            g.addWidget(l, r, 2); r += 1
            return l
        head(tr('Житлові будинки'))
        param(tr('Працівників С на будинок'), 'c_house')
        param(tr('Працівників В на будинок'), 'b_house')
        self.o_hc = out(tr('Будинків для С')); self.o_hb = out(tr('Будинків для В'))
        head(tr('Зупинки'))
        param(tr('Жителів на 1 посадку'), 'stop_people')
        param(tr('Підприємств'), 'enterprises', 0, 10 ** 5)
        hint = QLabel(tr('1–2 зупинки на посадку і 1–2 на підприємство')); hint.setObjectName('hint'); hint.setWordWrap(True)
        g.addWidget(hint, r, 0, 1, 3); r += 1
        self.o_board = out(tr('Посадок'))
        self.o_stops = out(tr('Потрібно зупинок'))

    def toggle_side(self):
        self.city['extra_open'] = not self.city.get('extra_open'); self.apply_open(); self.app.save_soon()

    # ----- rows
    def _add_row(self, o):
        row = ObjRow(self, o); self.rows.append(row)
        r = len(self.rows)
        for i, w in enumerate(row.widgets):
            self.grid.addWidget(w, r, i)

    def add_obj(self):
        o = new_obj(); self.city['objects'].append(o); self._add_row(o); self.changed()
        row = self.rows[-1]
        QTimer.singleShot(0, lambda: (self.app.cities.scroll.ensureWidgetVisible(row.name), row.name.setFocus()))

    def remove_obj(self, row):
        idx = self.city['objects'].index(row.o)
        self.app.push_undo(('obj', self.city['id'], idx, row.o), row.title())
        self.city['objects'].remove(row.o)
        for w in row.widgets:
            self.grid.removeWidget(w); w.hide(); w.deleteLater()
        self.rows.remove(row)
        self.repack(); self.changed()

    def insert_row(self, idx, o):
        row = ObjRow(self, o); self.rows.insert(idx, row); self.repack()

    def repack(self):
        for rw in self.rows:
            for w in rw.widgets:
                self.grid.removeWidget(w)
        for i, rw in enumerate(self.rows, 1):              # row 0 is the header
            for j, w in enumerate(rw.widgets):
                self.grid.addWidget(w, i, j)

    def refresh_rows(self):
        for r in self.rows:
            r.refresh()
        self.update_sums()

    # ----- header actions
    def on_name(self, t):
        self.city['name'] = t; self.app.cities_changed()

    def toggle(self):
        self.city['open'] = not self.city['open']; self.apply_open(); self.app.save_soon()

    def apply_open(self):
        op = self.city['open']
        self.tog.setText('▾' if op else '▸'); self.body.setVisible(op)
        so = self.city.get('extra_open', False)
        self.side.setVisible(so); self.side_btn.setText('◂' if so else tr('Додатково ▸'))

    def delete(self):
        if QMessageBox.question(self.app, tr('Видалити місто'), tr("Видалити «{n}» разом з усіма об'єктами?").format(n=self.city['name'])) == QMessageBox.Yes:
            self.app.remove_city(self)

    def totals(self):
        objs = self.city['objects']
        return (sum(o['c'] * max(1, o['count']) for o in objs), sum(o['b'] * max(1, o['count']) for o in objs))

    def update_sums(self):
        c, b = self.totals()
        self.stats.set(c, b, self.app.one_shift())
        self.strip.set_pop(city_pop(self.city))
        for k, cells in self.foot:
            for l, val in zip(cells, (c, b, c + b)):
                l.setText(fmt(val / k))
        e = self.city['extra']
        self.o_hc.setText(fmt(math.ceil(c / e['c_house'])) if e['c_house'] else '—')
        self.o_hb.setText(fmt(math.ceil(b / e['b_house'])) if e['b_house'] else '—')
        board = math.ceil(city_pop(self.city) / e['stop_people']) if e['stop_people'] else 0
        n = board + e.get('enterprises', 0)                          # 1-2 stops per boarding place and per enterprise
        self.o_board.setText(fmt(board))
        self.o_stops.setText(f'{fmt(n)} – {fmt(2 * n)}' if n else '—')

    def changed(self):
        self.update_sums(); self.app.cities_changed()


class CitiesTab(QWidget):
    def __init__(self, app):
        super().__init__(); self.app = app; self._cards = []; self._built = False
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        b = QPushButton(tr('+ Додати місто')); b.clicked.connect(self.add_city); top.addWidget(b)
        top.addSpacing(10); top.addWidget(vline()); top.addSpacing(10)
        self.shift = ShiftSwitch(app); top.addWidget(self.shift)
        top.addSpacing(10); top.addWidget(vline()); top.addSpacing(10)
        self.period = PeriodSwitch(app); top.addWidget(self.period)
        top.addStretch()
        v.addLayout(top)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.inner = QWidget(); self.box = QVBoxLayout(self.inner); self.box.setContentsMargins(0, 4, 6, 4); self.box.addStretch()
        self.scroll.setWidget(self.inner); v.addWidget(self.scroll, 1)
        # totals of all cities: bottom right, under a dividing line (user's layout)
        rule = QFrame(); rule.setObjectName('rule'); v.addWidget(rule)
        bot = QHBoxLayout(); bot.setContentsMargins(0, 2, 6, 0)
        self.stats = Stats(24); self.stats.setToolTip(tr('Усі міста: середня + вища освіта, одна чи три зміни')); bot.addWidget(self.stats)
        bot.addSpacing(18)
        self.strip = ResStrip(app, 24); bot.addWidget(self.strip)
        bot.addStretch()
        v.addLayout(bot)

    @property
    def cards(self):
        """the city cards; they are made the first time somebody needs them (the tab is shown, or the code works with the rows)"""
        self.ensure_built()
        return self._cards

    def ensure_built(self):
        if self._built:
            return
        self._built = True
        for c in self.app.data['cities']:
            self._add_card(c)
        self.update_total()

    def _add_card(self, c):
        card = CityCard(self.app, c); self.cards.append(card); self.box.insertWidget(self.box.count() - 1, card)

    def add_city(self):
        c = new_city(tr('Місто {n}').format(n=len(self.app.data['cities']) + 1)); c['open'] = True
        self.app.data['cities'].append(c); self._add_card(c); self.app.cities_changed()
        self.cards[-1].name.setFocus(); self.cards[-1].name.selectAll()

    def update_total(self):
        pop = sum(city_pop(c) for c in self.app.data['cities'])
        self.strip.set_pop(pop)
        cs = [cd.totals() for cd in self.cards]
        self.stats.set(sum(x[0] for x in cs), sum(x[1] for x in cs), self.app.one_shift())

    def insert_card(self, idx, c):
        if not self._built:
            return                                           # not made yet: it is made from the data, which has the city
        card = CityCard(self.app, c); self.cards.insert(idx, card); self.box.insertWidget(idx, card)


# ------------------------------------------------------------------ tab 3: my buildings (the catalog)
COLW = dict(icon=34, prod=150, need=150, pip=30, c=110, b=110, tot=84, rm=30)     # shared by the sticky header and the rows


def fixed(w, width, align=Qt.AlignLeft):
    """w inside a box of a fixed width, so the sticky header and the rows line up"""
    box = QWidget(); box.setFixedWidth(width)
    hl = QHBoxLayout(box); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(0)
    if align & Qt.AlignRight:
        hl.addStretch()
    hl.addWidget(w)
    if not align & Qt.AlignRight:
        hl.addStretch()
    return box


class ObjIconPicker(QDialog):
    """icon for a building: a game building, a game resource, or the user's own PNG (stored as 48x48 like the game icons)"""
    NOT_BUILDINGS = ('tool_worker_', 'tool_line_', 'tool_make_city', 'tool_eletric_', 'tool_pipe', 'tool_road_',
                    'tool_cableway', 'tool_afgan_', 'tool_afghan_', 'tool_fjord_', 'tool_jungle_', 'tool_palma',
                    'tool_tallkriak', 'tool_leafkriak', 'tool_tree_', 'tool_area_', 'tool_assign_', 'tool_bojka',
                    'tool_border_', 'tool_building_add', 'tool_building_copy', 'tool_building_distribution',
                    'tool_building_near_road', 'tool_christmas_', 'tool_conveyor', 'tool_bulk_engin', 'tool_create_',
                    'tool_crossroad_', 'tool_erase_', 'tool_paint_', 'tool_terrain_', 'tool_factoryconnection',
                    'tool_forklift_crossing', 'tool_foreign_', 'tool_group_', 'tool_join_hub', 'tool_namepoint',
                    'tool_pick_tool', 'tool_random_selected', 'tool_measurement', 'tool_pollution_meter', 'tool_dozimeter',
                    'tool_fence_', 'tool_gate_', 'tool_heating_pipe', 'tool_sewagepipe', 'tool_waterpipe',
                    'tool_rail_bridge', 'tool_rail_concrete', 'tool_rail_destroy', 'tool_rail_eletric', 'tool_rail_metro',
                    'tool_rail_semaphore', 'tool_rail_tunel', 'tool_rail_wood', 'tool_second_road_', 'tool_pedestrian',
                    'tool_vehicle_', 'tool_water_switch', 'tool_water_to_water', 'tool_water_square', 'tool_water_source',
                    'tool_sewage_switch', 'tool_airport_road_connection', 'tool_firestation_addfire', 'tool_bulk.png')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Іконка об'єкта"))
        self.setStyleSheet(QSS + 'QDialog { background: #f3e9d9; } QListWidget { background: #faf4ea; border: 1px solid #c8b39a; }')
        self.choice = None
        v = QVBoxLayout(self)
        top = QHBoxLayout()
        self.q = QLineEdit(); self.q.setPlaceholderText(tr('Пошук…')); self.q.setClearButtonEnabled(True); top.addWidget(self.q, 1)
        own = QPushButton(tr('Своя картинка PNG…')); own.clicked.connect(self.own); top.addWidget(own)
        std = QPushButton(tr('Стандартна іконка')); std.setObjectName('ghost'); std.clicked.connect(lambda: self.finish('')); top.addWidget(std)
        v.addLayout(top)
        hint = QLabel(tr('Подвійний клік — вибрати')); hint.setObjectName('hint'); v.addWidget(hint)
        self.lists = []; self._todo = []; per_list = []
        for title, items in ((tr('Будівлі гри'), self.buildings()), (tr('Ресурси гри'), self.resources())):
            h = QLabel(title); h.setObjectName('h1'); v.addWidget(h)
            lst = QListWidget(); lst.setViewMode(QListWidget.IconMode); lst.setIconSize(QSize(48, 48)); lst.setGridSize(QSize(100, 86))
            lst.setResizeMode(QListWidget.Adjust); lst.setMovement(QListWidget.Static); lst.setWordWrap(True)
            todo = []
            for path, label, val in items:
                it = QListWidgetItem(label); it.setData(Qt.UserRole, val); it.setToolTip(label); lst.addItem(it); todo.append((it, path, 48))
            per_list.append(todo)
            lst.itemDoubleClicked.connect(lambda it: self.finish(it.data(Qt.UserRole)))
            v.addWidget(lst, 2 if not self.lists else 1); self.lists.append(lst)
        from itertools import zip_longest
        self._todo = [x for pair in zip_longest(*per_list) for x in pair if x]       # both lists get their first icons first
        self._todo.reverse(); self.icons()
        self.q.textChanged.connect(self.filter)
        self.resize(780, 620)

    def icons(self):
        """the icons come in batches: the picker opens at once and the first rows have theirs a moment later"""
        n = 24
        while self._todo and n:
            it, p, h = self._todo.pop(); n -= 1
            try:
                it.setIcon(QIcon(pix(p, h)))
            except RuntimeError:
                self._todo = []; return
        if self._todo:
            QTimer.singleShot(0, self.icons)

    def buildings(self):
        fs = sorted(f for f in os.listdir(EDITOR) if f.startswith('tool_') and f.endswith('.png')
                    and not f.startswith(self.NOT_BUILDINGS)) if os.path.isdir(EDITOR) else []
        return [(os.path.join(EDITOR, f), f[5:-4].replace('_', ' '), f) for f in fs]

    @staticmethod
    def resources():
        out = []
        for k in sorted(pack_keys() or [], key=lambda k_: sort_key(RN(k_))):
            p = res_icon(k)
            if p:
                out.append((p, RN(k), 'res:' + k))
        return out

    def filter(self, t):
        t = t.strip().lower()
        for lst in self.lists:
            for i in range(lst.count()):
                it = lst.item(i); it.setHidden(bool(t) and t not in it.text().lower() and t not in str(it.data(Qt.UserRole)).lower())

    def own(self):
        from PySide6.QtWidgets import QFileDialog
        f, _ = QFileDialog.getOpenFileName(self, tr('Своя картинка PNG…'), os.path.expanduser('~'),
                                           'PNG (*.png);;Images (*.png *.jpg *.jpeg *.webp *.bmp)')
        if not f:
            return
        try:
            im = Image.open(f).convert('RGBA')
            bb = im.getchannel('A').getbbox()
            if bb:
                im = im.crop(bb)
            im.thumbnail((48, 48), Image.LANCZOS)                          # the size of the game's resource icons
            out = Image.new('RGBA', (48, 48), (0, 0, 0, 0)); out.alpha_composite(im, ((48 - im.width) // 2, (48 - im.height) // 2))
            os.makedirs(OWN_ICONS, exist_ok=True)
            name = uuid.uuid4().hex[:10] + '.png'; out.save(os.path.join(OWN_ICONS, name))
        except Exception:
            QMessageBox.warning(self, tr("Іконка об'єкта"), tr('Не вдалося відкрити картинку.')); return
        self.finish('own/' + name)

    def finish(self, val):
        self.choice = val; self.accept()


class CatalogRow:
    """one building definition: values for 1 building, people for 3 shifts (or 1 shift when that is switched on)"""
    def __init__(self, tab, name):
        self.tab, self.app, self.name = tab, tab.app, name
        self.w = QWidget(); hl = QHBoxLayout(self.w); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(6)
        self.ic = QToolButton(); self.ic.setIconSize(QSize(26, 26)); self.ic.setCursor(Qt.PointingHandCursor)
        self.ic.setToolTip(tr('Натисни, щоб змінити іконку')); self.ic.clicked.connect(self.pick_icon); self.ic.setFixedWidth(COLW['icon'])
        self.edit = QLineEdit(self.app.obj_disp(name)); self.edit.setMinimumWidth(200); self.edit.editingFinished.connect(self.rename)
        self.production = QPushButton(); self.production.setObjectName('res'); self.production.setFixedWidth(COLW['prod'])
        self.needs = QPushButton(); self.needs.setObjectName('res'); self.needs.setFixedWidth(COLW['need'])
        self.pip = QToolButton(); self.pip.setIcon(QIcon(pix(PIPETTE_ICON, 24))); self.pip.setIconSize(QSize(24, 24))
        self.pip.setCursor(Qt.PointingHandCursor); self.pip.setFixedWidth(COLW['pip'])
        self.fert = True                                              # a field: which harvest is shown and edited
        self.pip.clicked.connect(self.on_pip)
        self.c = spin(10 ** 7, 0, 0, 84); self.b = spin(10 ** 7, 0, 0, 84); cbw = tab.cbw
        self.c.valueChanged.connect(lambda v: self.set_val('c', v)); self.b.valueChanged.connect(lambda v: self.set_val('b', v))
        self.tot = QLabel(); self.tot.setObjectName('big'); self.tot.setAlignment(Qt.AlignRight | Qt.AlignVCenter); self.tot.setFixedWidth(COLW['tot'])
        self.rm = DelButton(tr("Прибрати об'єкт")); self.rm.clicked.connect(self.delete); self.rm.setFixedWidth(COLW['rm'])
        self.production.clicked.connect(lambda: self.edit_list('production', tr('Виробництво')))
        self.needs.clicked.connect(lambda: self.edit_list('needs', tr('Потреби')))
        for wd in (self.ic, self.edit, self.production, self.needs, self.pip, fixed(self.c, cbw, Qt.AlignRight),
                   fixed(self.b, cbw, Qt.AlignRight), self.tot, self.rm):
            hl.addWidget(wd, 1 if wd is self.edit else 0)
        self.refresh()

    def entry(self):
        return self.app.data['catalog'].setdefault(self.name, dict(c=0, b=0, production=[], needs=[]))

    def title(self):
        return self.app.obj_disp(self.name)

    def total(self):
        e = self.entry()
        return e.get('c', 0) + e.get('b', 0)

    def refresh(self):
        e = self.entry(); k = 1.0 / self.app.period_div(); one = self.app.one_shift()
        prod, need = eff_lists(e, self.fert)
        show_res(self.production, prod, k, self.app.period()); show_res(self.needs, need, k, self.app.period())
        set_pip(self.pip, self.needs, self.fert if is_field(e) else None)
        for s_, key in ((self.c, 'c'), (self.b, 'b')):
            s_.blockSignals(True); s_.setReadOnly(one)
            s_.setValue(int(round(e.get(key, 0) / (3 if one else 1)))); s_.blockSignals(False)
        t = self.total()
        self.tot.setText(fmt(t / 3 if one else t))
        self.ic.setIcon(QIcon(pix(obj_icon(e), 26)))
        d = self.app.obj_disp(self.name)
        if not self.edit.hasFocus() and self.edit.text() != d:
            self.edit.setText(d)

    def store(self):
        self.app.store_object(self.name, self.entry(), source=self)

    def set_val(self, key, v):
        if self.app.one_shift():
            return                                           # one shift is a view: people are kept for 3 shifts
        self.entry()[key] = v; self.refresh(); self.store()

    def on_pip(self):
        if is_field(self.entry()):
            self.fert = not self.fert; self.refresh()
        else:
            self.app.start_pipette(self)

    def edit_list(self, key, title):
        e = self.entry()
        if key == 'production' and is_field(e) and not self.fert:
            key = 'plain'
        dlg = ResListDialog(title, e.get(key, []), self.app, yearly=is_field(e))
        if dlg.exec():
            e[key] = dlg.result_items(); self.refresh(); self.store()

    def apply_pipette(self, production, needs, staff):
        e = self.entry()
        if production or needs:
            e['production'], e['needs'] = production, needs
        if staff.get('workers') is not None:
            e['c'] = staff['workers'] * 3
        if staff.get('engineers') is not None:
            e['b'] = staff['engineers'] * 3
        self.refresh(); self.store()

    def pick_icon(self):
        dlg = ObjIconPicker(self.app)
        if dlg.exec():
            e = self.entry()
            if dlg.choice:
                e['ico'] = dlg.choice
            else:
                e.pop('ico', None)
            self.refresh(); self.app.icon_changed(self.name)

    def rename(self):
        new = self.edit.text().strip(); cur = self.app.obj_disp(self.name)
        if not new or new == cur:
            self.edit.setText(cur); return
        cat = self.app.data['catalog']
        if any(k != self.name and new.lower() in (k.lower(), self.app.obj_disp(k).lower()) for k in cat):
            self.edit.setText(cur)                           # first: a second editingFinished must find nothing to do
            QMessageBox.information(self.app, tr("Мої об'єкти"), tr("Об'єкт «{n}» уже є.").format(n=new)); return
        if lang.L == 'uk':                                   # the Ukrainian name is the key: keep the place in the list
            items = list(cat.items()); cat.clear(); cat.update((new if k == self.name else k, v) for k, v in items)
            self.tab.rows[new] = self.tab.rows.pop(self.name)
            self.tab.new_keys = [new if k == self.name else k for k in self.tab.new_keys]
            old, self.name = self.name, new
            self.app.rename_object(old, new)
        else:                                                # English / German: the user's own translation
            cat[self.name].setdefault('names', {})[lang.L] = new
            self.app.catalog_names_changed(); self.app.save_soon()

    def delete(self):
        if QMessageBox.question(self.app, tr("Мої об'єкти"), tr("Прибрати «{n}» зі списку об'єктів?").format(n=self.title())) == QMessageBox.Yes:
            cat = self.app.data['catalog']
            self.app.push_undo(('cat', list(cat).index(self.name), self.name, cat[self.name]), self.title())
            cat.pop(self.name, None); self.tab.rebuild(); self.app.catalog_names_changed(); self.app.save_soon()


class CatalogTab(QWidget):
    def __init__(self, app):
        super().__init__(); self.app = app; self._rows = {}; self._built = False; self.new_keys = []
        self.sort = list(app.data['settings'].get('cat_sort') or [None, True])
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(4)
        top = QHBoxLayout()
        add = QPushButton(tr("+ Додати об'єкт")); add.clicked.connect(self.add); top.addWidget(add)
        top.addSpacing(10); top.addWidget(vline()); top.addSpacing(10)
        self.shift = ShiftSwitch(app); top.addWidget(self.shift)
        top.addSpacing(10); top.addWidget(vline()); top.addSpacing(10)
        self.period = PeriodSwitch(app); top.addWidget(self.period)
        top.addSpacing(10); top.addWidget(vline()); top.addSpacing(10)
        self.search = QLineEdit(); self.search.setPlaceholderText(tr('Пошук…')); self.search.setClearButtonEnabled(True)
        self.search.setFixedWidth(220); self.search.textChanged.connect(lambda _: self.apply_view()); top.addWidget(self.search)
        top.addStretch()
        v.addLayout(top)
        tl = QHBoxLayout()
        h = QLabel(tr("Мої об'єкти — значення на 1 будівлю")); h.setObjectName('h1'); tl.addWidget(h); tl.addSpacing(12)
        hint = QLabel(tr("Зміни тут оновлюють цей об'єкт у всіх містах.")); hint.setObjectName('hint'); tl.addWidget(hint); tl.addStretch()
        v.addLayout(tl)
        # header row: outside the scroll area, so it stays while the list scrolls
        f = QFont('Arimo'); f.setPixelSize(12); f.setBold(True); fm = QFontMetrics(f)
        self.cbw = max(COLW['c'], 26 + max(fm.horizontalAdvance(tr(t)) for t in ('С (3 зміни)', 'С (1 зміна)', 'В (3 зміни)', 'В (1 зміна)')))
        self.hdr = QWidget(); hh = QHBoxLayout(self.hdr); hh.setContentsMargins(0, 2, 8 + 12, 0); hh.setSpacing(6)

        def lab(t, icon=None):
            box = QWidget(); bl = QHBoxLayout(box); bl.setContentsMargins(0, 0, 0, 0); bl.setSpacing(3)
            if icon:
                bl.addWidget(icon_label(icon, 18))
            l = QLabel(t); l.setObjectName('h1'); l.setStyleSheet('font-size: 12px;'); bl.addWidget(l); bl.addStretch()
            return box, l

        def sorter(what, tip):
            b = QPushButton(); b.setObjectName('hdr'); b.setCursor(Qt.PointingHandCursor)
            b.setToolTip(tip + '\n' + tr('Натисни ще раз — зворотний порядок, ще раз — мій порядок'))
            b.clicked.connect(lambda: self.toggle_sort(what))
            return b
        self.h_name = sorter('name', tr('Сортувати за назвою')); self.h_tot = sorter('total', tr('Сортувати за кількістю людей'))
        prod_box, _ = lab(tr('Виробництво')); need_box, _ = lab(tr('Потреби'))
        c_box, self.h_c = lab('', EDU_C); b_box, self.h_b = lab('', EDU_B)
        for wd, wdt in ((QWidget(), COLW['icon']), (self.h_name, None), (prod_box, COLW['prod']), (need_box, COLW['need']),
                        (QWidget(), COLW['pip']), (c_box, self.cbw), (b_box, self.cbw), (self.h_tot, COLW['tot']), (QWidget(), COLW['rm'])):
            if wdt:
                wd.setFixedWidth(wdt)
            hh.addWidget(wd, 0 if wdt else 1)
        v.addWidget(self.hdr)
        rule = QFrame(); rule.setObjectName('rule'); v.addWidget(rule)
        self.sc = QScrollArea(); self.sc.setWidgetResizable(True); self.sc.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        inner = QWidget(); self.box = QVBoxLayout(inner); self.box.setContentsMargins(0, 3, 8, 4); self.box.setSpacing(3)
        self.box.addStretch()
        self.sc.setWidget(inner); v.addWidget(self.sc, 1)

    @property
    def rows(self):
        """the rows of the list; made the first time somebody needs them (the tab is shown, or the code works with the rows)"""
        self.ensure_built()
        return self._rows

    def ensure_built(self):
        if self._built:
            return
        self._built = True
        self.rebuild()

    def disp(self, key):
        return self.app.obj_disp(key)

    def update_header(self):
        key, first = self.sort
        arrow = lambda w: ((' ▼' if first else ' ▲') if key == w else '')
        self.h_name.setText(tr('Назва') + arrow('name')); self.h_tot.setText(tr('Разом') + arrow('total'))
        one = self.app.one_shift()
        self.h_c.setText(tr('С (1 зміна)') if one else tr('С (3 зміни)'))
        self.h_b.setText(tr('В (1 зміна)') if one else tr('В (3 зміни)'))

    def toggle_sort(self, what):
        key, first = self.sort
        self.sort = [what, True] if key != what else [what, False] if first else [None, True]
        self.new_keys = []
        self.app.data['settings']['cat_sort'] = self.sort; self.app.save_soon()
        self.update_header(); self.apply_view()

    def order(self):
        cat = self.app.data['catalog']
        keys = [k for k in cat if k not in self.new_keys]           # own order = the order they were added
        key, first = self.sort
        if key == 'name':
            keys.sort(key=lambda k: sort_key(self.disp(k)), reverse=not first)        # ▼ А→Я
        elif key == 'total':
            keys.sort(key=lambda k: cat[k].get('c', 0) + cat[k].get('b', 0), reverse=first)   # ▼ most people first
        return keys + [k for k in self.new_keys if k in cat]        # just added: at the bottom

    def apply_view(self):
        q = self.search.text().strip().lower()
        while self.box.count() > 1:
            self.box.takeAt(0)
        for i, k in enumerate(self.order()):
            row = self.rows.get(k)
            if row is None:
                continue
            self.box.insertWidget(i, row.w)
            row.w.setVisible(not q or q in self.disp(k).lower() or q in k.lower())

    def rebuild(self):
        cat = self.app.data['catalog']
        for k in list(self.rows):
            if k not in cat:
                r = self.rows.pop(k); r.w.hide(); r.w.deleteLater()
        for k in cat:
            if k in self.rows:
                self.rows[k].refresh()
            else:
                self.rows[k] = CatalogRow(self, k)
        self.update_header(); self.apply_view()

    def refresh_name(self, name):
        row = self.rows.get(name)
        if row is None:
            self.rebuild()
        else:
            row.refresh()

    def refresh_all(self):
        for r in self.rows.values():
            r.refresh()
        self.update_header()

    def add(self):
        cat = self.app.data['catalog']; n = 1
        taken = {k.lower() for k in cat} | {self.disp(k).lower() for k in cat}
        while tr("Новий об'єкт {n}").format(n=n).lower() in taken:
            n += 1
        name = tr("Новий об'єкт {n}").format(n=n)
        cat[name] = dict(c=0, b=0, production=[], needs=[])          # dicts keep order: a new one goes to the end
        self.new_keys.append(name)
        self.search.blockSignals(True); self.search.clear(); self.search.blockSignals(False)
        self.rebuild(); self.app.catalog_names_changed(); self.app.save_soon()
        row = self.rows[name]

        def focus():
            self.sc.ensureWidgetVisible(row.w); row.edit.setFocus(); row.edit.selectAll()
        QTimer.singleShot(0, focus)


# ------------------------------------------------------------------ Windows: keep the game from getting our clicks
def _user32():
    import ctypes
    from ctypes import wintypes
    u = ctypes.windll.user32
    u.GetForegroundWindow.restype = wintypes.HWND
    u.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    u.GetWindowThreadProcessId.restype = wintypes.DWORD
    u.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
    for f in (u.SetForegroundWindow, u.BringWindowToTop, u.SetFocus, u.SetActiveWindow, u.IsWindow):
        f.argtypes = [wintypes.HWND]
    return u, ctypes, wintypes


def _is_game(u, ctypes, wintypes, fg, pid):
    """the window in front is the game: the W&R executable, or any window covering its whole monitor (borderless game)"""
    try:
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)                       # PROCESS_QUERY_LIMITED_INFORMATION
        if h:
            buf = ctypes.create_unicode_buffer(520); n = wintypes.DWORD(520)
            ok = k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)); k.CloseHandle(h)
            exe = os.path.basename(buf.value).lower() if ok else ''
            if 'soviet' in exe or 'republic' in exe:
                return True
            if exe in ('explorer.exe', 'pythonw.exe', 'python.exe'):
                return False
        class MONITORINFO(ctypes.Structure):
            _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', wintypes.RECT), ('rcWork', wintypes.RECT), ('dwFlags', wintypes.DWORD)]
        u.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]; u.MonitorFromWindow.restype = wintypes.HANDLE
        u.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.c_void_p]; u.GetWindowRect.argtypes = [wintypes.HWND, ctypes.c_void_p]
        r = wintypes.RECT(); u.GetWindowRect(fg, ctypes.byref(r))
        mi = MONITORINFO(); mi.cbSize = ctypes.sizeof(MONITORINFO)
        u.GetMonitorInfoW(u.MonitorFromWindow(fg, 2), ctypes.byref(mi))
        m = mi.rcMonitor
        return r.left <= m.left and r.top <= m.top and r.right >= m.right and r.bottom >= m.bottom
    except Exception:
        return False


def win_take_foreground(hwnd):
    """make our window the active one while the GAME holds the focus (a game in front reads the mouse
    directly, so a click on the calculator would also land in the game) -> the window that had the focus"""
    try:
        u, ctypes, wintypes = _user32()
        fg = u.GetForegroundWindow()
        if not fg or fg == hwnd:
            return None
        pid = wintypes.DWORD(0)
        t_fg = u.GetWindowThreadProcessId(fg, ctypes.byref(pid))
        if pid.value == os.getpid() or not _is_game(u, ctypes, wintypes, fg, pid.value):
            return None                                      # our own dialog, or a browser etc.: leave it alone
        t_me = ctypes.windll.kernel32.GetCurrentThreadId()
        attached = bool(t_fg) and t_fg != t_me and bool(u.AttachThreadInput(t_me, t_fg, True))
        u.BringWindowToTop(hwnd); u.SetForegroundWindow(hwnd); u.SetActiveWindow(hwnd); u.SetFocus(hwnd)
        if attached:
            u.AttachThreadInput(t_me, t_fg, False)
        return fg
    except Exception:
        return None


def win_give_foreground(hwnd):
    try:
        u, _, _ = _user32()
        if hwnd and u.IsWindow(hwnd):
            u.SetForegroundWindow(hwnd)
    except Exception:
        pass


# ------------------------------------------------------------------ Windows: own app identity on the taskbar
_WS = None


def _winshell():
    """ctypes COM helpers (no extra packages): GUID, PROPERTYKEY, PROPVARIANT and vtable calls"""
    global _WS
    if _WS is None:
        import ctypes
        from ctypes import wintypes
        from types import SimpleNamespace

        class GUID(ctypes.Structure):
            _fields_ = [('Data1', wintypes.DWORD), ('Data2', wintypes.WORD), ('Data3', wintypes.WORD), ('Data4', ctypes.c_ubyte * 8)]

        class PROPERTYKEY(ctypes.Structure):
            _fields_ = [('fmtid', GUID), ('pid', wintypes.DWORD)]

        class PROPVARIANT(ctypes.Structure):
            _fields_ = [('vt', ctypes.c_ushort), ('r1', ctypes.c_ushort), ('r2', ctypes.c_ushort), ('r3', ctypes.c_ushort),
                        ('pwszVal', ctypes.c_wchar_p), ('pad', ctypes.c_void_p)]

        def guid(text):
            g = GUID(); ctypes.oledll.ole32.CLSIDFromString(ctypes.c_wchar_p(text), ctypes.byref(g))
            return g

        def method(obj, index, *argtypes):
            vtbl = ctypes.cast(obj, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
            return ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, *argtypes)(vtbl[index])
        _WS = SimpleNamespace(c=ctypes, GUID=GUID, PROPERTYKEY=PROPERTYKEY, PROPVARIANT=PROPVARIANT, guid=guid, method=method,
                              IID_PS='{886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99}', FMT_AUMID='{9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}')
    return _WS


def _set_aumid_props(store, items):
    """IPropertyStore::SetValue for System.AppUserModel.* (pid -> text), then Commit"""
    W = _winshell(); c = W.c
    fmt = W.guid(W.FMT_AUMID)
    set_value = W.method(store, 6, c.POINTER(W.PROPERTYKEY), c.POINTER(W.PROPVARIANT))
    for pid, text in items:
        key = W.PROPERTYKEY(fmt, pid); pv = W.PROPVARIANT(); pv.vt = 31; pv.pwszVal = text      # VT_LPWSTR
        set_value(store, c.byref(key), c.byref(pv))
    W.method(store, 7)(store)                                                                    # Commit


def _release(obj):
    try:
        _winshell().method(obj, 2)(obj)
    except Exception:
        pass


def relaunch_parts():
    pyw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
    return (pyw if os.path.exists(pyw) else sys.executable), os.path.abspath(__file__), os.path.join(ICONS, 'calc.ico')


def win_set_process_id():
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ctypes.c_wchar_p(APP_ID))
    except Exception:
        pass


def win_set_window_identity(hwnd):
    """pinning the running calculator from the taskbar pins the calculator (not bare Python), with its name and icon"""
    W = _winshell(); c = W.c
    store = c.c_void_p()
    c.oledll.shell32.SHGetPropertyStoreForWindow(c.c_void_p(hwnd), c.byref(W.guid(W.IID_PS)), c.byref(store))
    try:
        pyw, script, ico = relaunch_parts()
        _set_aumid_props(store, [(5, APP_ID), (2, f'"{pyw}" "{script}"'), (4, APP_NAME), (3, f'{ico},0')])
    finally:
        _release(store)


def win_make_link(path):
    """«W&R City Manager.lnk»: pythonw.exe + wr_calc.py, our icon and the same app id as the window"""
    W = _winshell(); c = W.c
    pyw, script, ico = relaunch_parts()
    try:
        c.oledll.ole32.CoInitialize(None)
    except OSError:
        pass
    link = c.c_void_p()
    c.oledll.ole32.CoCreateInstance(c.byref(W.guid('{00021401-0000-0000-C000-000000000046}')), None, 1,
                                    c.byref(W.guid('{000214F9-0000-0000-C000-000000000046}')), c.byref(link))
    try:
        W.method(link, 20, c.c_wchar_p)(link, pyw)                                              # SetPath
        W.method(link, 11, c.c_wchar_p)(link, f'"{script}"')                                    # SetArguments
        W.method(link, 9, c.c_wchar_p)(link, HERE)                                              # SetWorkingDirectory
        W.method(link, 17, c.c_wchar_p, c.c_int)(link, ico, 0)                                  # SetIconLocation
        W.method(link, 7, c.c_wchar_p)(link, APP_NAME + ' — calculator over the game')                    # SetDescription
        qi = W.method(link, 0, c.POINTER(W.GUID), c.POINTER(c.c_void_p))
        store = c.c_void_p(); qi(link, c.byref(W.guid(W.IID_PS)), c.byref(store))
        try:
            _set_aumid_props(store, [(5, APP_ID)])
        finally:
            _release(store)
        pf = c.c_void_p(); qi(link, c.byref(W.guid('{0000010b-0000-0000-C000-000000000046}')), c.byref(pf))
        try:
            W.method(pf, 6, c.c_wchar_p, c.c_int)(pf, path, 1)                                   # IPersistFile::Save
        finally:
            _release(pf)
    finally:
        _release(link)


def _links_log(msg):
    """what the shortcut maker did (make_links.log next to the program): it runs without a window, so this is the only trace"""
    try:
        import time
        p = os.path.join(HERE, 'make_links.log')
        old = open(p, encoding='utf-8').read()[-6000:] if os.path.exists(p) else ''
        with open(p, 'w', encoding='utf-8') as f:
            f.write(old + time.strftime('%Y-%m-%d %H:%M:%S ') + msg + '\n')
    except Exception:
        pass


def make_links_cli(argv):
    """«pythonw wr_calc.py --make-links [--desktop] [--update-desktop]» — runs in its own process, so a failure here
    never touches the calculator; falls back to the PowerShell script"""
    name = APP_NAME + '.lnk'
    try:
        import ctypes
        from ctypes import wintypes
        buf = ctypes.create_unicode_buffer(520)
        ctypes.windll.shell32.SHGetFolderPathW(None, 0x10, None, 0, buf)                        # CSIDL_DESKTOPDIRECTORY (OneDrive too)
        desktop = buf.value or os.path.join(os.path.expanduser('~'), 'Desktop')
    except Exception:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    targets = []
    if '--desktop' in argv:
        targets.append(os.path.join(desktop, name))
    else:
        targets.append(os.path.join(CM, name))
        if ('--also-desktop' in argv or ('--setup' in argv and not os.path.exists(os.path.join(desktop, name)))
                or ('--update-desktop' in argv and any(os.path.exists(os.path.join(desktop, n)) for n in (name, OLD_LINK)))):
            targets.append(os.path.join(desktop, name))
    _links_log('args %s | desktop folder %s | targets %s' % (argv[1:], desktop, targets))
    for t in targets:
        try:
            win_make_link(t); print('OK', t)
            if not os.path.exists(t):
                raise OSError('the shortcut file is not there after saving')
            _links_log('OK ' + t)
            old = os.path.join(os.path.dirname(t), OLD_LINK)
            if os.path.exists(old):
                os.remove(old)                                   # our own shortcut under the old name
        except Exception as ex:
            print('COM failed:', ex); _links_log('COM failed for %s: %r' % (t, ex))
            import subprocess
            pyw, _, _ = relaunch_parts()
            args = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(HERE, 'make_shortcut.ps1'), '-Py', pyw]
            if t.startswith(CM):
                args.insert(-2, '-Here')
            try:
                subprocess.call(args, creationflags=0x08000000)
                _links_log('PowerShell for %s -> shortcut there: %s' % (t, os.path.exists(t)))
            except Exception as ex2:
                print('PowerShell failed:', ex2); _links_log('PowerShell failed for %s: %r' % (t, ex2))


# ------------------------------------------------------------------ export writers
def write_xlsx(path, sheets):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
    wb = Workbook(); wb.remove(wb.active)
    maroon, white = '923C38', 'FFFFFF'
    for sh in sheets:
        ws = wb.create_sheet(re.sub(r'[\[\]:*?/\\]', '', sh['title'])[:31])
        widths = {}; head_row = None
        for i, (style, cells) in enumerate(sh['rows'], 1):
            for j, v in enumerate(cells, 1):
                c = ws.cell(row=i, column=j, value=v)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    c.number_format = '#,##0' if float(v).is_integer() else '#,##0.0##'
                if style == 'title':
                    c.font = Font(bold=True, size=13, color=maroon)
                elif style == 'head':
                    c.font = Font(bold=True, color=white); c.fill = PatternFill('solid', fgColor=maroon)
                    c.alignment = Alignment(wrap_text=True, vertical='center')
                elif style == 'city':
                    c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='E2CDB0')
                elif style == 'total':
                    c.font = Font(bold=True); c.border = Border(top=Side(style='thin', color=maroon))
                if style != 'title':
                    n = len(fmt(v)) if isinstance(v, (int, float)) else len(str(v or ''))
                    widths[j] = max(widths.get(j, 0), min(n, 60))
            if style == 'head':
                head_row = i
                for j in range(len(cells) + 1, ws.max_column + 1):
                    ws.cell(row=i, column=j).fill = PatternFill('solid', fgColor=maroon)
        for j, w in widths.items():
            ws.column_dimensions[get_column_letter(j)].width = max(8, w + 2)
        if head_row:
            ws.freeze_panes = ws.cell(row=head_row + 1, column=1)
            ws.auto_filter.ref = f'A{head_row}:{get_column_letter(ws.max_column)}{ws.max_row}'
    wb.save(path)


def write_csv(path, sheets):
    import csv
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        for sh in sheets:
            for _, cells in sh['rows']:
                w.writerow([str(v).replace('.', ',') if isinstance(v, float) else v for v in cells])
            w.writerow([])


# ------------------------------------------------------------------ focus guard (main window)
class FocusGuard:
    """mouse resting on the window: it takes the focus from the game, so clicks and the wheel stay here.
    Only when the mouse stops (as before a click): a mouse just passing over must not switch focus —
    every switch makes the game stutter."""
    def guard_init(self):
        self._prev_fg = None; self._touched = False; self._trail = []
        self._hover = QTimer(self); self._hover.timeout.connect(self._hover_tick)

    def enterEvent(self, e):
        super().enterEvent(e)
        if sys.platform == 'win32':
            self._trail = []; self._hover.start(50)

    def _hover_tick(self):
        p = QCursor.pos()
        if not self.frameGeometry().contains(p):
            self._hover.stop(); return
        self._trail = (self._trail + [p])[-4:]                      # the last ~150-200 ms
        if len(self._trail) < 4 or max(abs(q.x() - p.x()) + abs(q.y() - p.y()) for q in self._trail) > 10:
            return
        self._hover.stop()
        prev = win_take_foreground(int(self.winId()))
        if prev:                                                    # None: we already had it, or the game is not in front
            self._prev_fg = prev; self._touched = False
            QApplication.instance().installEventFilter(self)        # watch for a click / key / wheel only while it matters

    def leaveEvent(self, e):
        super().leaveEvent(e)
        if sys.platform == 'win32' and self._prev_fg:
            QTimer.singleShot(300, self._give_back)

    def _give_back(self):
        """the mouse rested here but nothing was clicked, typed or scrolled: the game gets its focus back"""
        if not self._prev_fg or self._touched or self.frameGeometry().contains(QCursor.pos()):
            return
        if QApplication.activePopupWidget() or QApplication.activeModalWidget():
            return
        win_give_foreground(self._prev_fg); self._prev_fg = None
        QApplication.instance().removeEventFilter(self)



class HotkeyFilter(QAbstractNativeEventFilter):
    """WM_HOTKEY of the global hotkey (registered for the main thread)"""
    def __init__(self, cb):
        super().__init__(); self.cb = cb

    def nativeEventFilter(self, etype, message):
        try:
            if bytes(etype) in (b'windows_dispatcher_MSG', b'windows_generic_MSG'):
                from ctypes import wintypes
                msg = wintypes.MSG.from_address(int(message))
                if msg.message == 0x0312 and msg.wParam == HOTKEY_ID:
                    QTimer.singleShot(0, self.cb)
                    return True, 0
        except Exception:
            pass
        return False, 0


# ------------------------------------------------------------------ main window (game window texture)
class Main(FocusGuard, QWidget):
    # title-bar buttons on the game texture, as offsets from the right edge (measured): x from..to, rows
    BTN = dict(minus=(146, 116), pin=(94, 70), close=(47, 28))
    BTN_Y = (44, 70)
    TACK_AT = (40, 35)                                         # where the needle of the red push-pin enters: from the right edge, from the top

    def __init__(self):
        super().__init__()
        backup_data()                                           # before anything is changed
        self.data = load()
        pl = self.data.get('planner')
        if isinstance(pl, dict):                                 # map data of cities that no longer exist
            ids = {c['id'] for c in self.data['cities']}
            pl['cities'] = {k: v for k, v in pl.get('cities', {}).items() if k in ids}
        st = self.data['settings']
        lang.set_lang(st.get('lang', 'uk'))
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)     # lets Windows minimize/restore it from the taskbar
        self.setWindowFlag(Qt.WindowSystemMenuHint, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, st.get('pinned', True))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        ico = os.path.join(ICONS, 'calc.png')
        if os.path.exists(ico):
            self.setWindowIcon(QIcon(ico))
        self.setStyleSheet(QSS)
        T = gui._tex()
        im, _, inner = gui.window(400, 400, 'x')
        self.dw, self.dh = im.width - 400, im.height - 400
        self.bar_b = T['bar_b'] if T else 78
        self.inner = inner
        self._bg = None; self._bg_key = None; self._drag = None
        A = T['a'] if T else None
        self.edge_r = (A.shape[1] - T['paper_r']) if T else 20
        self.edge_b = (A.shape[0] - T['paper_b']) if T else 20
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(inner[0] + 8, self.bar_b + 6, self.edge_r + 16, self.edge_b + 14)
        self.body = None
        self.grip = QSizeGrip(self); self.grip.resize(18, 18)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.save)
        self.names_v = 0; self.guard_init(); self.tray = None; self.undo_stack = []
        self.build_body()
        g = st.get('geom')
        if g:
            self.resize(g[2], g[3])                             # the saved size, but always in the middle of the screen
        else:
            self.resize(1180, 760)
        self.center_on_screen()
        self.setMinimumSize(720, 360)
        self.collapsed = False; self._full_h = self.height()
        if self.data.pop('_merged', False):
            self.save()                                         # the merged buildings are kept even if the app is killed
        QTimer.singleShot(1500, self.ensure_shortcut)
        QTimer.singleShot(300, self.apply_identity)
        self._bk = QTimer(self); self._bk.timeout.connect(backup_data); self._bk.start(3600 * 1000)   # a new day while running
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)    # shown by the hotkey: the game keeps its focus
        QShortcut(QKeySequence.Undo, self, activated=self.undo_key)
        self.register_hotkey(); self.make_tray()

    # ----- content (rebuilt on language change)
    def build_body(self, flush=True):
        self.setUpdatesEnabled(False)
        try:
            self._build_body(flush)
        finally:
            self.setUpdatesEnabled(True); self.update()

    def _build_body(self, flush=True):
        """the first call makes the frame of the window (tab row, page stack, status line), every call makes the texts, pages and
        buttons in it. On a language change the frame, the page stack and the planner (a browser view) are NOT remade: a browser view
        that is hidden, given another parent or resized (even for a moment) redraws itself and blinks"""
        if self.body is not None and flush:
            try:
                self.planner.flush()
            except Exception:
                pass
        lay = self.body.layout() if self.body is not None else None
        if lay is not None:
            lay.setEnabled(False)                                    # the layout is worked out once, at the end: no in-between sizes
        try:
            self._fill_body()
        finally:
            if lay is not None:
                lay.setEnabled(True); lay.invalidate(); lay.activate()
        if lay is None:
            self._bg_key = None                                      # the window texture does not depend on the language
        self.update()
        QTimer.singleShot(0, self.place_save)

    def _fill_body(self):
        first = self.body is None; old = ()
        st = self.data['settings']
        self.setWindowTitle(APP_NAME)
        if first:
            self.body = QWidget(); bv = QVBoxLayout(self.body); bv.setContentsMargins(0, 0, 0, 0)
            self.tabs_l = QHBoxLayout(); self.tabs_l.setSpacing(4); bv.addLayout(self.tabs_l)
            self.stack = QStackedWidget(); bv.addWidget(self.stack, 1)
            self.toast_l = QVBoxLayout(); self.toast_l.setContentsMargins(0, 0, 0, 0); bv.addLayout(self.toast_l)
            self.foot_l = QHBoxLayout(); self.foot_l.setContentsMargins(0, 2, 0, 0); bv.addLayout(self.foot_l)
            self.planner = PlannerTab(self)
            self._trash = []; self._trash_t = QTimer(self); self._trash_t.timeout.connect(self._reap_tick)
            self._idle_t = QTimer(self); self._idle_t.setSingleShot(True); self._idle_t.timeout.connect(self._idle_build)
            self.root.addWidget(self.body)
        else:
            def drop(w):
                if w is not None:
                    w.hide(); w.deleteLater()

            def clear(lay):                                          # delete everything a layout holds, the layout itself stays
                while lay.count():
                    it = lay.takeAt(0)
                    if it.widget() is not None:
                        drop(it.widget())
            clear(self.tabs_l); clear(self.toast_l); clear(self.foot_l)
            drop(getattr(self.calc, 'panel', None)); drop(self.calc); drop(self.save_btn)
            old = (self.cities, self.catalog_tab)                    # the planner page stays in the stack; these leave it after the new pages are in
        self.tb = []
        for i, t in enumerate((tr('Міста'), tr("Мої об'єкти"), tr('Планувальник'))):
            b = QPushButton(t); b.setObjectName('tab'); b.setCheckable(True); b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, i_=i: self.set_tab(i_))
            self.tabs_l.addWidget(b); self.tb.append(b)
        self.tabs_l.addStretch()
        self.tabs_l.addSpacing(10)
        self.lang_btns = []
        for code, label in lang.LANGS:
            b = QPushButton(label); b.setObjectName('lang'); b.setCheckable(True); b.setChecked(code == lang.L)
            b.setCursor(Qt.PointingHandCursor); b.clicked.connect(lambda _, c=code: self.set_lang(c)); self.tabs_l.addWidget(b)
            self.lang_btns.append(b)
        self.toast = Toast(self.body); self.toast_l.addWidget(self.toast)
        self.powered = Powered(); self.foot_l.addWidget(self.powered); self.foot_l.addStretch()
        for w in self.tb + self.lang_btns + [self.powered]:
            w.show()                                                 # a new widget is shown only a moment later: the layout must count it now
        self.cities = CitiesTab(self); self.catalog_tab = CatalogTab(self)
        self.stack.insertWidget(0, self.cities); self.stack.insertWidget(1, self.catalog_tab)
        if first:
            self.stack.addWidget(self.planner)
        else:
            if self.stack.currentWidget() in old:                    # removing the current page would show the planner (and make its browser view) for a moment
                self.stack.setCurrentWidget(self.cities)
            for w in old:
                self.stack.removeWidget(w); self.reap(w)
        self.save_btn = QToolButton(self.body); self.save_btn.setObjectName('save'); self.save_btn.setAutoRaise(True)
        ic = QIcon(pix(SAVE_ICON, 24)); ic.addPixmap(pix(SAVE_ICON_HOT, 24), QIcon.Active)
        self.save_btn.setIcon(ic); self.save_btn.setIconSize(QSize(24, 24)); self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setToolTip(tr('Зберегти в таблицю (Excel)')); self.save_btn.clicked.connect(self.export_table)
        self.calc = PopCalc(self, self.body)
        self.set_tab(st.get('tab', 0))
        if not first:
            self.planner.relang()                                    # the page follows the language without being reloaded
        self._idle_n = 0; self._idle_t.start(900 if first else 450)   # (re)starts: one pending call only

    # ----- the page that is not on screen is made a moment later; a replaced page is taken apart in small steps
    def reap(self, w):
        """a replaced page holds ~1500 widgets: deleting them all at once stalls the window, so it is done a few at a time"""
        w.hide(); self._trash.append(w)
        if getattr(self, '_fade', None) is None and not self._trash_t.isActive():       # not while a switch is fading (see fade_end)
            self._trash_t.start(12)

    def _reap_tick(self):
        if getattr(self, '_fade', None) is not None:
            self._trash_t.stop(); return
        budget = 80
        while self._trash and budget > 0:
            ws = self._trash[0]
            if not isinstance(ws, list):                             # first time: the page and everything inside it, parents first
                try:
                    ws = [ws] + ws.findChildren(QWidget)
                except RuntimeError:
                    ws = []
                self._trash[0] = ws
            while ws and budget > 0:
                x = ws.pop(); budget -= 1                            # children first
                try:
                    x.deleteLater()
                except RuntimeError:
                    pass
            if not ws:
                self._trash.pop(0)
        if not self._trash:
            self._trash_t.stop()

    def _idle_build(self):
        """the tab that is not on screen is made and styled in small steps shortly after the one on screen"""
        pos = QCursor.pos()                                          # only while nobody is working with the window: not during a
        busy = getattr(self, '_fade', None) is not None or QApplication.mouseButtons() != Qt.NoButton        # fade or a click;
        moving = pos != getattr(self, '_idle_pos', None); self._idle_pos = pos                               # a moving mouse is waited out ~1.5 s
        if busy or (moving and getattr(self, '_idle_n', 0) < 6):
            if moving and not busy:
                self._idle_n = getattr(self, '_idle_n', 0) + 1
            self._idle_t.start(250); return
        cur = self.stack.currentIndex()
        pages = ((0, self.cities), (1, self.catalog_tab))
        for i, pg in pages:
            if not pg._built:
                pg.ensure_built(); self._idle_t.start(80); return
        for i, pg in pages:
            if i != cur and not getattr(pg, '_styled', False):
                pg._styled = True; pg.ensurePolished(); self._idle_t.start(80); return

    def prebuild(self):
        """before the window is first shown (the gear still turns): both pages are made and styled, and (Windows) the browser view
        of the planner too. A window that gets a browser view AFTER it is on screen has to change its kind of surface (Windows re-creates
        it = one blink and a stall on the first planner click); with the view made first it never does. If the program ever dies while
        the view is being made, `view_try` stays set and the next starts make the view the old way (after the window is shown)."""
        st = self.data['settings']
        try:
            self.cities.ensure_built(); self.catalog_tab.ensure_built()
            for pg in (self.cities, self.catalog_tab):
                pg._styled = True; pg.ensurePolished()
        except Exception:
            pass
        if sys.platform == 'win32' and not st.get('view_try'):
            st['view_try'] = 1; self.save()
            QTimer.singleShot(15000, self._view_ok)
            try:
                self.planner.prewarm()
            except Exception:
                pass
        self._idle_t.stop()

    def _view_ok(self):
        self.data['settings'].pop('view_try', None); self.save_soon()

    def place_save(self):
        """the save button sits right under the language switch"""
        if not getattr(self, 'lang_btns', None):
            return
        g = self.lang_btns[-1].geometry(); sz = self.save_btn.sizeHint(); self.save_btn.resize(sz)
        self.save_btn.move(g.right() - sz.width() + 2, g.bottom() + 5); self.save_btn.raise_(); self.save_btn.show()
        if getattr(self, 'calc', None) is not None:
            self.calc.place(self.save_btn)

    # ----- export: everything as a spreadsheet (current language and period)
    def export_sheets(self):
        d = self.data; div = self.period_div(); per = tr({k: lbl for k, lbl, _ in PERIODS}[self.period()])
        title = lambda t: ('title', [t, '', tr('Період') + ': ' + per])
        R = lambda v: round(v, 3)

        def res_text(items, k):
            return '; '.join(f'{RN(r)} {fmt(a * k)}' for r, a in items)
        # 1. cities and their buildings
        rows = [title(tr('Міста')), (None, []),
                ('head', [tr('Місто'), tr("Об'єкт"), tr('К-сть'), tr('Продукт. %'), tr('Виробництво'), tr('Потреби'),
                          tr('С (3 зміни)'), tr('В (3 зміни)'), tr('Разом (3 зміни)'), tr('С (1 зміна)'), tr('В (1 зміна)'), tr('Разом (1 зміна)')])]
        AC = AB = 0
        for c in d['cities']:
            rows.append(('city', [c['name'], f"{tr('Населення:')} {fmt(city_pop(c))}"]))
            C = B = 0
            for o in c['objects']:
                n = max(1, o['count']); k = o['prod'] / 100.0 * n / div
                oc, ob = o['c'] * n, o['b'] * n; C += oc; B += ob
                pr, nd = eff_lists(o)
                rows.append((None, [c['name'], self.obj_disp(o['name']), o['count'], o['prod'], res_text(pr, k),
                                    res_text(nd, k), R(oc), R(ob), R(oc + ob), R(oc / 3), R(ob / 3), R((oc + ob) / 3)]))
            rows.append(('total', ['', tr('Усього по місту'), '', '', '', '', R(C), R(B), R(C + B), R(C / 3), R(B / 3), R((C + B) / 3)]))
            AC += C; AB += B
        rows.append(('total', [tr('Усі міста'), f"{tr('Населення всіх міст:')} {fmt(sum(city_pop(c) for c in d['cities']))}",
                               '', '', '', '', R(AC), R(AB), R(AC + AB), R(AC / 3), R(AB / 3), R((AC + AB) / 3)]))
        sheets = [dict(title=tr('Міста'), rows=rows)]
        # 2. resource balance per city
        rows = [title(tr('Баланс ресурсів')), (None, []),
                ('head', [tr('Місто'), tr('Ресурс'), tr('Виробництво'), tr('Потреби'), tr('Різниця')])]
        for c in d['cities']:
            bal = {}
            for o in c['objects']:
                k = o['prod'] / 100.0 * max(1, o['count']) / div
                for i, lst in enumerate(eff_lists(o)):
                    for r, a in lst:
                        bal.setdefault(r, [0.0, 0.0])[i] += a * k
            if not bal:
                continue
            rows.append(('city', [c['name']]))
            for r in sorted(bal, key=lambda r_: sort_key(RN(r_))):
                p, q = bal[r]
                rows.append((None, [c['name'], RN(r), R(p), R(q), R(p - q)]))
        sheets.append(dict(title=tr('Баланс ресурсів'), rows=rows))
        # 3. needs per 1000 residents (by the rates, for every city and for all cities)
        G, U = d['rates'], d['util_rates']
        rows = [title(tr('Ресурси на 1000 жителів')), (None, []),
                ('head', [tr('Місто'), tr('Населення')] + [RN(r) for r, _ in G] + [tr('Комунальні') + ': ' + RN(r) for r, _ in U])]
        for c in d['cities']:
            p = city_pop(c)
            rows.append((None, [c['name'], p] + [R(p / 1000.0 * x / div) for _, x in G + U]))
        allp = sum(city_pop(c) for c in d['cities'])
        rows.append(('total', [tr('Усі міста'), allp] + [R(allp / 1000.0 * x / div) for _, x in G + U]))
        sheets.append(dict(title=tr('Ресурси на 1000 жителів'), rows=rows))
        # 4. my buildings (as ordered on the tab), values for 1 building at 100 %
        rows = [title(tr("Мої об'єкти — значення на 1 будівлю")), (None, []),
                ('head', [tr('Назва'), tr('Виробництво'), tr('Потреби'), tr('С (3 зміни)'), tr('В (3 зміни)'), tr('Разом (3 зміни)'),
                          tr('С (1 зміна)'), tr('В (1 зміна)'), tr('Разом (1 зміна)')])]
        cat = d['catalog']
        for k in self.catalog_tab.order():
            e = cat[k]; ec, eb = e.get('c', 0), e.get('b', 0)
            rows.append((None, [self.obj_disp(k), res_text(e.get('production', []), 1.0 / div), res_text(e.get('needs', []), 1.0 / div),
                                R(ec), R(eb), R(ec + eb), R(ec / 3), R(eb / 3), R((ec + eb) / 3)]))
        sheets.append(dict(title=tr("Мої об'єкти"), rows=rows))
        return sheets

    def export_table(self):
        from PySide6.QtWidgets import QFileDialog
        import time
        try:
            import openpyxl  # noqa: F401
            xlsx = True
        except ImportError:
            xlsx = False
        base = os.path.join(CM, APP_NAME + time.strftime(' %Y-%m-%d') + ('.xlsx' if xlsx else '.csv'))
        path, _ = QFileDialog.getSaveFileName(self, tr('Зберегти таблицю'), base, 'Excel (*.xlsx);;CSV (*.csv)' if xlsx else 'CSV (*.csv)')
        if not path:
            return
        try:
            sheets = self.export_sheets()
            if xlsx and not path.lower().endswith('.csv'):
                if not path.lower().endswith('.xlsx'):
                    path += '.xlsx'
                write_xlsx(path, sheets); msg = tr('Збережено: {p}').format(p=path)
            else:
                if not path.lower().endswith('.csv'):
                    path = os.path.splitext(path)[0] + '.csv'
                write_csv(path, sheets)
                msg = (tr('Збережено: {p}') if xlsx else
                       tr('Модуль Excel не встановлено — збережено як CSV (теж відкривається в Excel): {p}')).format(p=path)
        except Exception as ex:
            QMessageBox.warning(self, tr('Зберегти таблицю'), tr('Не вдалося зберегти: {e}').format(e=ex)); return
        from PySide6.QtGui import QDesktopServices
        self.toast.on_check = lambda p=path: QDesktopServices.openUrl(QUrl.fromLocalFile(p))
        self.toast.show_msg(msg, icon=SAVE_ICON, button=tr('Відкрити'))

    def set_lang(self, code):
        if code == lang.L:
            for b in self.body.findChildren(QPushButton, 'lang'):
                b.setChecked(b.text() == dict(lang.LANGS)[code])
            return
        self.data['settings']['lang'] = code; lang.set_lang(code)
        self.save(); self.smooth(lambda: self.build_body(flush=False), self.body, freeze=False)   # the planner page is not rebuilt: nothing to take from it
        if self.tray is not None:
            self.make_tray()
        if self.collapsed:
            self.body.hide()

    # ----- pipette: hide, grab the screen under the mouse, read, confirm
    def start_pipette(self, target):
        self._pip_row = target                                    # a city row or a «Мої об'єкти» row
        QTimer.singleShot(60, self._snip)                         # the calculator stays visible (user's wish)

    def _snip(self):
        scr = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        self._snipper = Snipper(scr); self._snipper.done.connect(self._snipped)
        self._snipper.setGeometry(scr.geometry()); self._snipper.show(); self._snipper.raise_(); self._snipper.activateWindow()

    _pip_done = Signal(object, object, object, object)

    def _snipped(self, img):
        self.raise_()
        row = getattr(self, '_pip_row', None)
        if img is None or row is None or getattr(self, '_pip_busy', False):
            return
        self._pip_busy = True
        if not getattr(self, '_pip_wired', False):
            self._pip_done.connect(self._pip_finished); self._pip_wired = True
        QApplication.setOverrideCursor(Qt.WaitCursor)

        def work():                                               # the reading takes a second or so: not on the window's own thread
            result = err = None
            try:
                import pipette as PP
                result = PP.read_building(img)
            except BaseException as ex:                           # never lose the app because of a bad read
                err = ex
            try:
                self._pip_done.emit(img, result, err, row)         # queued: the slot below runs on the window's thread
            except RuntimeError:                                  # the window is gone
                pass
        import threading
        threading.Thread(target=work, daemon=True).start()

    def _pip_finished(self, img, result, err, row):
        self._pip_busy = False
        QApplication.restoreOverrideCursor()
        if isinstance(err, ImportError):
            QMessageBox.warning(self, tr('Піпетка — що знайдено'),
                                tr('Модуль розпізнавання ще не встановлений. Закрий програму і запусти «W&R City Manager.bat» — він доставить його.'))
            return
        if err is not None:
            QMessageBox.warning(self, tr('Піпетка — що знайдено'), tr('Не вдалося прочитати: {e}').format(e=err))
            return
        self.keep_capture(img, result, row)
        prod = [[it['key'], round(it['value'] * 365, 3)] for it in result['production']]
        need = [[it['key'], round(it['value'] * 365, 3)] for it in result['needs']]
        staff = {k: result[k] for k in ('workers', 'engineers') if result.get(k)}
        try:
            if prod or need or staff:
                row.apply_pipette(prod, need, staff)
            self.pipette_note(row, img, result, prod, need, staff)
        except RuntimeError:                                      # the row was replaced meanwhile (language change): the shot is kept
            pass

    def pipette_note(self, row, img, result, prod, need, staff=None):
        def part(title, items):
            if not items:
                return ''
            return f"<b>{title}:</b> " + ', '.join(f"{RN(k)} {fmt(v)}" for k, v in items)
        name = row.title(); staff = staff or {}
        if prod or need or staff:
            ppl = ''
            if staff:
                ppl = '<b>' + tr('Люди') + ':</b> ' + ', '.join(
                    f"{lbl} {staff[k]} × 3 = {fmt(staff[k] * 3)}" for k, lbl in (('workers', tr('С')), ('engineers', tr('В'))) if k in staff)
            html = tr('Записано в «{n}» (на рік, 1 будівля при 100%)').format(n=name) + '<br>' + \
                '&nbsp;&nbsp;'.join(x for x in (part(tr('Виробництво'), prod), part(tr('Потреби'), need), ppl) if x)
            bad = False
        else:
            html = tr('Нічого не знайдено. Обведи вікно разом з рядками виробництва і споживання.'); bad = True

        def check():
            dlg = PipetteDialog(self, img, result)
            if dlg.exec():
                row.apply_pipette(dlg.values('production'), dlg.values('needs'), dlg.staff())
        self.toast.on_check = check
        self.toast.show_msg(html, bad)

    def keep_capture(self, img, result, row):
        """save the shot and what was read: lets us tune recognition on real windows"""
        try:
            import time
            os.makedirs(CAPTURES, exist_ok=True)
            stem = os.path.join(CAPTURES, time.strftime('%Y%m%d_%H%M%S'))
            img.save(stem + '.png')
            slim = {k: [{kk: it[kk] for kk in ('key', 'value', 'score', 'icon_key', 'name_key', 'text')} for it in result[k]]
                    for k in ('production', 'needs')}
            slim['lines'] = result.get('lines', []); slim['row'] = row.title()
            slim['staff'] = {k: result.get(k) for k in ('workers', 'engineers')}
            json.dump(slim, open(stem + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
            shots = sorted(f for f in os.listdir(CAPTURES) if f.endswith('.png'))
            for f in shots[:-40]:                                   # keep the last 40
                for ext in ('.png', '.json'):
                    try:
                        os.remove(os.path.join(CAPTURES, f[:-4] + ext))
                    except OSError:
                        pass
        except Exception:
            pass

    # ----- period: per workday / month / year
    def period(self):
        return self.data['settings'].get('period', 'year')

    def period_div(self):
        return {k: d for k, _, d in PERIODS}[self.period()]

    def set_period(self, key):
        self.data['settings']['period'] = key
        for card in self.cities.cards:
            card.refresh_rows()
        self.cities.update_total(); self.calc.refresh(); self.catalog_tab.refresh_all()
        self.cities.period.sync(); self.catalog_tab.period.sync(); self.save_soon()

    def set_one_shift(self, on):
        self.data['settings']['one_shift'] = on
        for card in self.cities.cards:
            card.refresh_rows()
        self.catalog_tab.refresh_all()
        self.cities.update_total(); self.cities.shift.sync(); self.catalog_tab.shift.sync(); self.save_soon()

    # ----- building names: the key is the Ukrainian name; English / German are shown when that language is on
    def obj_disp(self, key):
        return lang.obj_name(key, self.data['catalog'].get(key))

    def sorted_names(self):
        """(shown name, key) of every building, alphabetical — made once and shared by all rows"""
        tag = (self.names_v, lang.L, len(self.data['catalog']))
        if getattr(self, '_sn_tag', None) != tag:
            cat = self.data['catalog']
            self._sn = sorted(((self.obj_disp(k), k) for k in cat), key=lambda x: sort_key(x[0])); self._sn_tag = tag
        return self._sn

    def obj_key(self, text):
        t = (text or '').strip(); cat = self.data['catalog']
        if not t or t in cat:
            return t
        tl = t.lower()
        for k, e in cat.items():
            if k.lower() == tl or lang.obj_name(k, e).lower() == tl:
                return k
        return t

    def icon_changed(self, name):
        for card in self.cities.cards:
            for r in card.rows:
                if r.o['name'] == name:
                    r.show_name()
        self.save_soon()

    # ----- «Мої об'єкти»: one definition per building, shared by every row with that name
    def store_object(self, name, vals, source=None):
        cat = self.data['catalog'].setdefault(name, {})
        cat.update(c=vals.get('c', 0), b=vals.get('b', 0),
                   production=[list(x) for x in vals.get('production', [])], needs=[list(x) for x in vals.get('needs', [])])
        if is_field(vals):
            cat['plain'] = [list(x) for x in vals['plain']]
        for card in self.cities.cards:
            hit = False
            for r in card.rows:
                if r is not source and r.o['name'] == name:
                    r.o.update(c=cat['c'], b=cat['b'], production=[list(x) for x in cat['production']],
                               needs=[list(x) for x in cat['needs']])
                    if is_field(cat):
                        r.o['plain'] = [list(x) for x in cat['plain']]
                    r.refresh(); hit = True
            if hit:
                card.update_sums()
        if not isinstance(source, CatalogRow):
            self.catalog_tab.refresh_name(name)
        self.cities.update_total(); self.save_soon()

    def rename_object(self, old, new):
        for card in self.cities.cards:
            for r in card.rows:
                if r.o['name'] == old:
                    r.o['name'] = new
        self.catalog_names_changed(); self.save_soon()

    # ----- helpers used by tabs
    def one_shift(self):
        return self.data['settings'].get('one_shift', False)

    def cities_changed(self):
        self.cities.update_total(); self.save_soon()

    def rates_changed(self):
        """the rates per 1000 residents were edited with the pencil"""
        for card in self.cities.cards:
            card.update_sums()
        self.cities.update_total(); self.calc.refresh(); self.save_soon()

    def remove_city(self, card):
        self.push_undo(('city', self.data['cities'].index(card.city), card.city), card.city['name'])
        self.data['cities'].remove(card.city); self.cities.cards.remove(card); card.hide(); card.deleteLater(); self.cities_changed()

    # ----- smooth switching: the area that changes is covered by a snapshot of itself while it is rebuilt, then the snapshot fades out
    FADE_MS = 160

    def smooth(self, change, area, freeze=True):
        """run change() (a page switch, a rebuild) behind a snapshot of `area`; then the snapshot fades out over the new content:
        no half-drawn or blank frames, no blink"""
        if getattr(self, '_smoothing', False):                     # a switch made while another one is running (a rebuild sets the tab again)
            return change()
        self.fade_end()
        bg = getattr(self, '_bg', None)
        if (area is None or bg is None or not self.isVisible() or self.isMinimized() or getattr(self, 'collapsed', False)
                or not area.isVisible()):
            return change()
        def web_rect():                                            # where the live browser view is on screen (None: not on screen)
            pl = getattr(self, 'planner', None)
            v = getattr(pl, 'view', None) if pl is not None else None
            if v is None or not pl.isVisible() or not v.isVisible():
                return None
            return QRect(v.mapTo(self, QPoint(0, 0)), v.size())
        try:
            rect = QRect(area.mapTo(self, QPoint(0, 0)), area.size()).intersected(self.rect())
            hole = web_rect()
            hole = hole.intersected(rect) if hole is not None else None
            if hole is not None and not hole.isEmpty():
                # a browser view cannot be grabbed: everything but the view is drawn, the view's place is the paper
                dpr = self.devicePixelRatioF()
                pm = QPixmap(round(rect.width() * dpr), round(rect.height() * dpr)); pm.setDevicePixelRatio(dpr); pm.fill(Qt.transparent)
                self.render(pm, QPoint(), QRegion(rect) - QRegion(hole))
                pp = QPainter(pm); pp.drawPixmap(hole.topLeft() - rect.topLeft(), bg.copy(hole)); pp.end()
            else:
                hole = None; pm = self.grab(rect)
            if rect.isEmpty() or pm.isNull():
                return change()
            ov = QLabel(self); ov.setPixmap(pm); ov.setScaledContents(True); ov.setGeometry(rect)
            ov.setAttribute(Qt.WA_TransparentForMouseEvents, True); ov.show(); ov.raise_()
        except Exception:
            return change()
        self._fade = (ov, None); self._smoothing = True
        if freeze:
            self.setUpdatesEnabled(False)
        try:
            change()
        except BaseException:
            self.fade_end(); raise
        finally:
            self._smoothing = False
            if freeze:
                self.setUpdatesEnabled(True)
        h2 = web_rect() if hole is not None else None
        if h2 is not None:                                         # the browser view stays on screen (language change): never cover it
            h2 = h2.intersected(rect)
            if not h2.isEmpty():
                ov.setMask(QRegion(QRect(QPoint(0, 0), rect.size())) - QRegion(h2.translated(-rect.topLeft())))
        ov.raise_(); self.repaint()                                # the new content is drawn under the snapshot first
        eff = QGraphicsOpacityEffect(ov); eff.setOpacity(1.0); ov.setGraphicsEffect(eff)
        an = QPropertyAnimation(eff, b'opacity', ov); an.setDuration(self.FADE_MS); an.setStartValue(1.0); an.setEndValue(0.0)
        an.setEasingCurve(QEasingCurve.InOutQuad); an.finished.connect(self.fade_end)
        self._fade = (ov, an); an.start()

    def fade_end(self):
        f = getattr(self, '_fade', None); self._fade = None
        if isinstance(f, tuple):                                   # only our own snapshot (overlay, animation)
            try:
                if f[1] is not None:
                    f[1].stop()
                f[0].hide(); f[0].deleteLater()
            except RuntimeError:                                   # already deleted with its parent
                pass
        if getattr(self, '_trash', None) and not self._trash_t.isActive():
            self._trash_t.start(12)                                  # the old pages are taken apart now

    def set_tab(self, i):
        def switch():
            if i == 0:
                self.cities.ensure_built()
            elif i == 1:
                self.catalog_tab.ensure_built()
            self.stack.setCurrentIndex(i)
            for j, b in enumerate(self.tb):
                b.setChecked(i == j)
        if i == self.stack.currentIndex():
            switch()
        else:
            self.smooth(switch, self.stack)
        self.data['settings']['tab'] = i; self.save_soon()

    def save_soon(self):
        self.timer.start(600)

    def save(self):
        st = self.data['settings']
        g = self.geometry(); st['geom'] = [g.x(), g.y(), g.width(), self._full_h if getattr(self, 'collapsed', False) else g.height()]
        st['collapsed'] = getattr(self, 'collapsed', False); st.pop('opacity', None)
        tmp = DATA + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, DATA)

    # ----- window chrome: game texture with our own title-bar buttons
    def _pin_sprite(self):
        """the game's pin icon cut out of the texture (alpha from brightness over the maroon bar)"""
        if getattr(self, '_pin', None) is None:
            im, _, _ = gui.window(900, 400, 'x'); a = np.asarray(im).astype(np.float32); W = a.shape[1]
            y0, y1 = self.BTN_Y
            bgl = a[y0:y1, W - 420:W - 330, :3].mean(2).mean()
            r0, r1 = self.BTN['pin']
            p = a[y0:y1, W - r0 - 3:W - r1 + 3, :3]
            lum = p.mean(2)
            al = np.clip((lum - bgl - 10) / max(1.0, lum.max() - bgl - 10), 0, 1)
            col = p[al > 0.85].mean(0) if (al > 0.85).any() else np.array([240, 205, 195], np.float32)
            self._pin = (al, col)
        return self._pin

    def _tack_drawn(self):
        """fallback when pin_tack.png is missing: a red push-pin drawn in code: (image, (x, y) of the needle tip in it)"""
        if getattr(self, '_tkd', None) is None:
            K, R = 6, 44                                             # supersampling; the needle tip is the centre of a 2R x 2R canvas
            c0 = R * K
            cv = Image.new('RGBA', (2 * R * K, 2 * R * K), (0, 0, 0, 0)); d = ImageDraw.Draw(cv)

            def P(x, y):
                return (c0 + x * K, c0 + y * K)

            def B(x0, y0, x1, y1):
                return (c0 + x0 * K, c0 + y0 * K, c0 + x1 * K, c0 + y1 * K)
            # the pin stands straight (head up), all numbers are pixels relative to the tip
            d.polygon([P(-1.0, -10), P(1.0, -10), P(0, 0)], fill=(206, 208, 214, 255))                 # steel needle
            d.polygon([P(0.2, -10), P(1.0, -10), P(0, 0)], fill=(140, 143, 152, 255))
            d.rounded_rectangle(B(-7, -14, 7, -9.5), radius=1.6 * K, fill=(104, 4, 8, 255))            # base ring
            d.polygon([P(-4.4, -25), P(4.4, -25), P(5.6, -13), P(-5.6, -13)], fill=(150, 8, 12, 255))   # stem
            d.polygon([P(1.6, -25), P(4.4, -25), P(5.6, -13), P(2.6, -13)], fill=(108, 5, 9, 255))      # its shaded side
            d.polygon([P(-3.2, -24), P(-1.8, -24), P(-2.4, -14), P(-3.8, -14)], fill=(226, 84, 74, 255))   # its shine
            d.rounded_rectangle(B(-10, -32, 10, -23), radius=2.6 * K, fill=(118, 5, 9, 255))            # cap, side
            d.ellipse(B(-10, -35.5, 10, -27), fill=(178, 14, 16, 255))                                  # cap, top face
            d.ellipse(B(-6.6, -34.0, 2.0, -30.2), fill=(226, 100, 90, 255))                             # shine on the top
            cv = cv.rotate(-38, resample=Image.BICUBIC, center=(c0, c0))                               # leaning to the right
            small = cv.resize((2 * R, 2 * R), Image.LANCZOS)
            sh = Image.new('RGBA', small.size, (0, 0, 0, 0))
            sh.putalpha(small.getchannel('A').filter(ImageFilter.GaussianBlur(1.8)).point(lambda v: int(v * 0.42)))   # soft shadow on the paper
            out = Image.new('RGBA', small.size, (0, 0, 0, 0))
            out.alpha_composite(sh, (2, 3)); out.alpha_composite(small)
            bb = out.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox() or (0, 0, out.width, out.height)
            bb = (max(0, bb[0] - 1), max(0, bb[1] - 1), min(out.width, bb[2] + 1), min(out.height, bb[3] + 1))
            self._tkd = (out.crop(bb), (R - bb[0], R - bb[1]))
        return self._tkd

    TACK_FILE = 'pin_tack.png'                                 # the game's red push-pin (128 x 128, head up-right, needle down-left)
    TACK_NEEDLE = (27, 114)                                    # the needle tip in that file
    TACK_PX = 34                                               # height of the pin on screen, px

    def _tack_game(self):
        try:
            im = Image.open(os.path.join(GAME, 'ui', self.TACK_FILE)).convert('RGBA')
        except Exception:
            return None
        bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
        if not bb:
            return None
        k = self.TACK_PX / float(bb[3] - bb[1])
        pad = 6
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        tip = (round(self.TACK_NEEDLE[0] * k) + pad, round(self.TACK_NEEDLE[1] * k) + pad)
        out = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        sh.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(1.6)).point(lambda v: int(v * 0.30)))   # soft shadow on the paper
        out.alpha_composite(sh, (pad + 2, pad + 3)); out.alpha_composite(im, (pad, pad))
        bb = out.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
        return out.crop(bb), (tip[0] - bb[0], tip[1] - bb[1])

    def _tack(self):
        """the red push-pin that sits in the corner of a pinned window: (image, (x, y) of the needle tip in it)"""
        if getattr(self, '_tk', None) is None:
            self._tk = self._tack_game() or self._tack_drawn()
        return self._tk

    def chrome(self, W_, H_):
        """game window texture of W_ x H_ (below ~360 px the texture loses its title bar, so a tall render is cut:
        title bar on top + torn bottom edge); the eye and pin of the texture are replaced by «–/+» and a live pin"""
        w = max(120, W_ - self.dw)
        if H_ >= 360:
            im, _, _ = gui.window(w, H_ - self.dh, APP_NAME)
            a = np.array(im)                                 # 8-bit already: no float round trip (same pixels)
        else:
            im, _, _ = gui.window(w, 400, APP_NAME)
            b = np.asarray(im).astype(np.float32)
            bot = self.edge_b + 14; top = max(self.bar_b + 6, H_ - bot)
            f = min(10, top - self.bar_b - 2)
            A, B = b[:top], b[b.shape[0] - bot - f:]
            r = np.linspace(0, 1, f, dtype=np.float32)[:, None, None]
            a = np.concatenate([A[:top - f], A[top - f:] * (1 - r) + B[:f] * r, B[f:]], 0)
        Wd = a.shape[1]; y0, y1 = self.BTN_Y
        for key in ('minus', 'pin'):                     # erase the texture icons with a clean piece of the bar
            r0, r1 = self.BTN[key]; ww = r0 - r1 + 8
            a[y0 - 2:y1 + 2, Wd - r0 - 4:Wd - r0 - 4 + ww] = a[y0 - 2:y1 + 2, Wd - 430:Wd - 430 + ww]
        al, col = self._pin_sprite()
        out = Image.fromarray(a if a.dtype == np.uint8 else a.clip(0, 255).astype(np.uint8), 'RGBA')
        d = ImageDraw.Draw(out)
        # «–» collapse / «+» expand, same colour as the game icons
        cx = Wd - (self.BTN['minus'][0] + self.BTN['minus'][1]) // 2; cy = (y0 + y1) // 2
        c = tuple(int(x) for x in col)
        d.rounded_rectangle((cx - 11, cy - 2, cx + 11, cy + 3), radius=2, fill=c)
        if self.collapsed:
            d.rounded_rectangle((cx - 2, cy - 11, cx + 3, cy + 12), radius=2, fill=c)
        # pin: the game's pin icon in the title bar (the same in both states); a pinned window also gets the game's red push-pin
        # stuck into its top-right corner
        pinned = self.data['settings'].get('pinned', True)
        spr = np.zeros(al.shape + (4,), np.uint8)
        spr[..., :3] = c; spr[..., 3] = (al * 255).astype(np.uint8)
        sp = Image.fromarray(spr, 'RGBA')
        px = Wd - (self.BTN['pin'][0] + self.BTN['pin'][1]) // 2 - sp.width // 2
        out.alpha_composite(sp, (px, cy - sp.height // 2))
        if pinned:
            tk, (tx, ty) = self._tack()
            x, y = Wd - self.TACK_AT[0] - tx, self.TACK_AT[1] - ty
            if y < 0:
                tk = tk.crop((0, -y, tk.width, tk.height)); y = 0
            out.alpha_composite(tk, (max(0, x), y))
        # «?» right after the title text: help
        lum = a[y0:y1, :Wd - 200, :3].astype(np.float32).mean(2); base = np.median(lum)
        cols = np.where((lum > base + 60).any(0))[0]
        tx = int(cols.max()) if len(cols) else 300
        hx = tx + 26; self._help_cx = hx
        d.ellipse((hx - 12, cy - 12, hx + 12, cy + 12), outline=c, width=2)
        try:
            from PIL import ImageFont
            fnt = ImageFont.truetype(os.path.join(wr_paths.FONTS, 'Arimo-700.ttf'), 18)
            d.text((hx, cy + 1), '?', font=fnt, fill=c, anchor='mm')
        except Exception:
            d.text((hx - 3, cy - 6), '?', fill=c)
        return out

    def paintEvent(self, e):
        key = (self.width(), self.height(), self.collapsed if hasattr(self, 'collapsed') else False,
               self.data['settings'].get('pinned', True))                 # the window texture does not depend on the language
        if self._bg_key != key:
            self._bg = QPixmap.fromImage(pil_to_qimage(self.chrome(self.width(), self.height()))); self._bg_key = key
        p = QPainter(self); p.drawPixmap(0, 0, self._bg)

    def resizeEvent(self, e):
        self.grip.move(self.width() - self.edge_r - 20, self.height() - self.edge_b - 20)
        super().resizeEvent(e)
        QTimer.singleShot(0, self.place_save)

    def set_on_top(self, on):
        """keep the window above all others (or not). On Windows only the z-order of the existing window changes: setting the Qt
        window flag re-creates the native window, which blinks (and blanks the browser view of the planner)"""
        if sys.platform == 'win32':
            try:
                import ctypes
                H = ctypes.c_void_p                                  # window handles are pointer-sized; nothing global (argtypes) is changed
                if ctypes.windll.user32.SetWindowPos(H(int(self.winId())), H(-1 if on else -2), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010):
                    return                                           # HWND_TOPMOST / HWND_NOTOPMOST; no size, no move, no activation
            except Exception:
                pass
        self.setWindowFlag(Qt.WindowStaysOnTopHint, on); self.show()
        QTimer.singleShot(100, self.apply_identity)                 # the window was re-created

    def title_button(self, pos):
        x, y = pos.x(), pos.y()
        if not (self.bar_b - 46 <= y <= self.bar_b):
            return None
        r = self.width() - x
        for key, (r0, r1) in self.BTN.items():
            if r1 - 6 <= r <= r0 + 6:
                return key
        if abs(x - getattr(self, '_help_cx', -100)) <= 15:
            return 'help'
        return 'bar'

    def mousePressEvent(self, e):
        b = self.title_button(e.position().toPoint())
        if b == 'close':
            self.close()
        elif b == 'pin':
            on = not self.data['settings'].get('pinned', True); self.data['settings']['pinned'] = on
            self.set_on_top(on); self.update(); self.save_soon()
        elif b == 'minus':
            self.showMinimized()
        elif b == 'help':
            HelpDialog(self).exec()
        elif b == 'bar':
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag is not None:
            self.move(e.globalPosition().toPoint() - self._drag); return
        b = self.title_button(e.position().toPoint())
        if b in ('help', 'close', 'minus', 'pin'):
            key = (b, self.data['settings'].get('pinned', True))
            if key != getattr(self, '_tip_key', None) or not QToolTip.isVisible():       # not again on every mouse move
                self._tip_key = key
                tips = dict(help=tr('Інструкція'), close=tr('Закрити'), minus=tr('Згорнути'),
                            pin=tr('Закріплено поверх усіх вікон — натисни, щоб відкріпити') if key[1]
                            else tr('Закріпити поверх усіх вікон'))
                QToolTip.showText(e.globalPosition().toPoint(), tips[b], self)
            self.setCursor(Qt.PointingHandCursor)
        else:
            self._tip_key = None; QToolTip.hideText(); self.unsetCursor()

    def mouseReleaseEvent(self, e):
        if self._drag is not None:
            self._drag = None; self.save_soon()

    def catalog_names_changed(self):
        """a building was added, renamed or translated: refresh every row's list and «Мої об'єкти»"""
        self.names_v += 1
        for card in self.cities.cards:
            for r in card.rows:
                r.fill_names()
        if hasattr(self, 'catalog_tab'):
            if set(self.catalog_tab.rows) != set(self.data['catalog']):
                self.catalog_tab.rebuild()
            else:
                self.catalog_tab.refresh_all()

    def ensure_shortcut(self):
        """once: (re)create «W&R City Manager.lnk» in the CM folder (and renew the desktop one).
        The shortcut starts pythonw.exe with this script: Windows pins such a shortcut to the taskbar, a .bat it does not"""
        st = self.data['settings']
        if sys.platform == 'win32' and '--setup' in sys.argv:        # started by the launcher .bat: renewed every time, the desktop one is made if missing
            _links_child(); st['lnk_v'] = 4; st['desk_v'] = 1; self.save_soon()
            return
        if sys.platform != 'win32' or (st.get('lnk_v') == 4 and st.get('desk_v') == 1):
            return
        try:
            import subprocess
            pyw, script, _ = relaunch_parts()
            args = [pyw, script, '--make-links', '--update-desktop']
            if st.get('desk_v') != 1:
                args.append('--also-desktop')                    # once: the desktop shortcut is made right away (later it is only renewed if it exists)
            subprocess.Popen(args, creationflags=0x08000000)   # its own process
            st['lnk_v'] = 4; st['desk_v'] = 1; self.save_soon()
        except Exception:
            pass

    def apply_identity(self):
        """own taskbar identity for the window; if this ever crashed the app, it is not tried again"""
        if sys.platform != 'win32':
            return
        st = self.data['settings']
        if st.get('ident_try') and not st.get('ident_ok'):
            return
        if not st.get('ident_ok'):
            st['ident_try'] = 1; self.save()
        try:
            win_set_window_identity(int(self.winId()))
        except Exception:
            pass
        if not st.get('ident_ok'):
            st['ident_ok'] = 1; self.save_soon()

    def toggle_collapse(self):
        if not self.collapsed:
            self._full_h = self.height(); self.body.hide(); self.grip.hide()
            self.setMinimumHeight(0); self.collapsed = True; self.resize(self.width(), self.bar_b + self.edge_b + 22)
        else:
            self.body.show(); self.grip.show(); self.collapsed = False
            self.setMinimumHeight(360); self.resize(self.width(), max(360, self._full_h))
        self.update(); self.save_soon()

    def eventFilter(self, obj, ev):
        if ev.type() in (QEvent.MouseButtonPress, QEvent.Wheel, QEvent.KeyPress):
            self._touched = True                                    # the focus stays with the calculator: no need to watch more
            QApplication.instance().removeEventFilter(self)
        return False

    # ----- hotkey and tray
    def register_hotkey(self):
        if sys.platform != 'win32':
            return
        try:
            import ctypes
            if ctypes.windll.user32.RegisterHotKey(None, HOTKEY_ID, 0x0002 | 0x0004 | 0x4000, 0x4B):   # Ctrl+Shift+K, no repeat
                self._hk = HotkeyFilter(self.toggle_visible); QApplication.instance().installNativeEventFilter(self._hk)
        except Exception:
            pass

    def make_tray(self):
        from PySide6.QtWidgets import QSystemTrayIcon, QMenu
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        if self.tray is None:
            self.tray = QSystemTrayIcon(QIcon(os.path.join(ICONS, 'calc.png')), self)
            self.tray.activated.connect(lambda r: self.toggle_visible() if r == QSystemTrayIcon.Trigger else None)
        m = QMenu(); m.setStyleSheet(QSS)
        m.addAction(tr('сховати / показати').capitalize() + f'   {HOTKEY_TEXT}', self.toggle_visible)
        m.addSeparator(); m.addAction(tr('Закрити'), self.close)
        self._tray_menu = m; self.tray.setContextMenu(m)
        self.tray.setToolTip(APP_NAME + f'  ·  {HOTKEY_TEXT}'); self.tray.show()

    def show_front(self):
        """a second start of the program (shortcut clicked again): show the running window, do not open another"""
        self.showNormal(); self.raise_(); self.activateWindow()
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.user32.SetForegroundWindow(int(self.winId()))
            except Exception:
                pass

    def toggle_visible(self):
        """hotkey / tray: hide or show the calculator without taking the focus from the game"""
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.showNormal(); self.raise_()

    # ----- undo of deletions (Ctrl+Z or «Скасувати» in the note)
    def push_undo(self, rec, label):
        self.undo_stack.append(rec); del self.undo_stack[:-20]
        self.toast.on_check = self.undo
        self.toast.show_msg(tr('Видалено «{n}».').format(n=label) + ' ' + tr('Ctrl+Z — повернути.'), icon=TRASH, button=tr('Скасувати'))

    def center_on_screen(self):
        scr = QGuiApplication.primaryScreen()
        if scr is None:
            return
        a = scr.availableGeometry(); w, h = min(self.width(), a.width()), min(self.height(), a.height())
        self.setGeometry(a.x() + (a.width() - w) // 2, a.y() + (a.height() - h) // 2, w, h)

    def undo_key(self):
        """Ctrl+Z: on the «Планувальник» tab it undoes the map, elsewhere the deleted city / building"""
        if self.stack.currentIndex() == 2 and self.planner.view is not None:
            self.planner.run('window.CM && CM.undo()')
        else:
            self.undo()

    def open_planner(self, cid):
        """the map icon of a city: open the «Планувальник» tab with that city"""
        self.set_tab(2); self.planner.activate(cid)

    def undo(self):
        if not self.undo_stack:
            self.toast.show_msg(tr('Нічого скасовувати.'), icon=TRASH, button='', secs=3); return
        rec = self.undo_stack.pop(); d = self.data
        if rec[0] == 'city':
            _, idx, city = rec
            idx = min(idx, len(d['cities'])); d['cities'].insert(idx, city); self.cities.insert_card(idx, city)
            self.cities_changed(); name = city['name']
        elif rec[0] == 'obj':
            _, cid, idx, o = rec
            card = next((c for c in self.cities.cards if c.city['id'] == cid), None)
            if card is None:
                return self.undo()                               # its city is gone too
            idx = min(idx, len(card.city['objects'])); card.city['objects'].insert(idx, o); card.insert_row(idx, o)
            card.changed(); name = self.obj_disp(o['name']) or tr("Об'єкт")
        else:
            _, idx, name, e = rec
            items = list(d['catalog'].items()); items.insert(min(idx, len(items)), (name, e))
            d['catalog'].clear(); d['catalog'].update(items)
            self.catalog_tab.rebuild(); self.catalog_names_changed(); name = self.obj_disp(name)
        self.toast.show_msg(tr('Повернуто «{n}».').format(n=name), icon=TRASH, button='', secs=5)
        self.save_soon()

    def closeEvent(self, e):
        try:
            self.planner.flush()
        except Exception:
            pass
        self.save()
        if self.tray is not None:
            self.tray.hide()
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID)
            except Exception:
                pass
        super().closeEvent(e)
        QApplication.quit()


def main():
    if '--make-links' in sys.argv:
        make_links_cli(sys.argv); return
    if sys.platform == 'win32':
        win_set_process_id()                                     # before any window: the calculator is its own app on the taskbar
    from PySide6.QtCore import QCoreApplication
    try:
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)      # needed by Qt WebEngine («Планувальник»)
    except Exception:
        pass
    app = QApplication.instance() or QApplication(sys.argv)
    for f in ('Arimo-400.ttf', 'Arimo-700.ttf'):
        p = os.path.join(wr_paths.FONTS, f)
        if os.path.exists(p):
            QFontDatabase.addApplicationFont(p)
    app.setFont(QFont('Arimo', 10))
    app.setQuitOnLastWindowClosed(False)                       # hidden by the hotkey it keeps running (tray icon)
    from PySide6.QtNetwork import QLocalServer, QLocalSocket
    server = QLocalServer()
    if not server.listen(SINGLE_NAME):                           # name taken: a copy is running (or left a stale socket)
        probe = QLocalSocket(); probe.connectToServer(SINGLE_NAME)
        if probe.waitForConnected(500):
            probe.write(b'show'); probe.flush(); probe.waitForBytesWritten(500)
            return
        QLocalServer.removeServer(SINGLE_NAME); server.listen(SINGLE_NAME)
    w = Main()
    w._single_server = server

    def _on_second_start():
        conn = server.nextPendingConnection()
        if conn is not None:
            conn.readyRead.connect(conn.readAll); conn.disconnected.connect(conn.deleteLater)
        w.show_front()
    server.newConnection.connect(_on_second_start)
    w.prebuild()                                                 # everything is made while the gear still turns ...
    w.show(); app.processEvents()                                # ... so the window appears at once and complete (no opacity fade: it made Windows blink)
    if READY:
        try:
            open(READY, 'w').close()
        except OSError:
            pass
    QTimer.singleShot(1800, lambda: getattr(w, 'planner', None) is not None and w.planner.prewarm())
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
