"""Where things live. The program is ONE folder: the code, assets/ (fonts, own icons, game_assets.zip), help/, planner/.
The game's icons and window texture come in a single file, assets/game_assets.zip, and are unpacked once (on the first
start, or when that zip changes) into assets/game/. Without the zip the program still works: no pictures, a drawn window."""
import os
import shutil
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
FONTS = os.path.join(ASSETS, 'fonts')
ZIP = os.path.join(ASSETS, 'game_assets.zip')
_GAME = None


def _stamp(zf):
    return '%x' % zlib.crc32('|'.join(f'{i.filename}:{i.CRC}' for i in zf.infolist()).encode())


def _unpack(zf, dest):
    os.makedirs(dest, exist_ok=True)
    root = os.path.realpath(dest)
    for i in zf.infolist():
        p = os.path.realpath(os.path.join(dest, i.filename))
        if not p.startswith(root + os.sep):          # never write outside the folder
            continue
        if i.is_dir():
            os.makedirs(p, exist_ok=True)
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with zf.open(i) as s, open(p, 'wb') as o:
            shutil.copyfileobj(s, o)


def game_dir():
    """folder with the game's icons (gameicons/, editor/, ui/); unpacked from assets/game_assets.zip when needed"""
    global _GAME
    if _GAME:
        return _GAME
    base = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), '.local', 'share')
    cands = [os.path.join(ASSETS, 'game'), os.path.join(base, 'WR City Manager', 'game')]   # 2nd: when the program folder is read-only
    _GAME = cands[0]
    try:
        zf = zipfile.ZipFile(ZIP)
    except (OSError, zipfile.BadZipFile):
        return _GAME
    with zf:
        st = _stamp(zf)
        for d in cands:
            sf = os.path.join(d, '.stamp')
            try:
                if os.path.exists(sf) and open(sf, encoding='utf-8').read().strip() == st:
                    _GAME = d
                    return d
                _unpack(zf, d)
                with open(sf, 'w', encoding='utf-8') as f:
                    f.write(st)
                _GAME = d
                return d
            except OSError:
                continue
    return _GAME
