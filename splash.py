"""Start-up splash of W&R City Manager: a red gear in the game's style that spins until the main window is ready.
It runs as its OWN small process (wr_calc.py starts it first thing), so the gear turns smoothly however busy the
program is while it loads. It fades out when wr_calc.py creates the «ready» file, or when wr_calc.py is gone.
    pythonw splash.py --ready <file> --parent <pid>"""
import os, sys, json, math, time
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import (QPainter, QPainterPath, QColor, QRadialGradient, QPen, QFont, QFontDatabase, QGuiApplication,
                           QTransform)
from PySide6.QtWidgets import QApplication, QWidget

HERE = os.path.dirname(os.path.abspath(__file__))
RED, DARK = QColor(214, 38, 28), QColor(58, 10, 8)
FADE_IN, FADE_OUT, MAX_LIFE = 0.22, 0.24, 60.0


def gear_path(r_out, r_in, teeth, hole):
    """cog outline with trapezoid teeth and a round hole in the middle"""
    p = QPainterPath()
    n = teeth * 4
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        r = r_out if (i % 4) in (1, 2) else r_in
        pt = QPointF(r * math.cos(a), r * math.sin(a))
        p.moveTo(pt) if i == 0 else p.lineTo(pt)
    p.closeSubpath()
    h = QPainterPath(); h.addEllipse(QPointF(0, 0), hole, hole)
    return p.subtracted(h)


def parent_alive(pid):
    if not pid:
        return True
    try:
        if sys.platform == 'win32':
            import ctypes
            k = ctypes.windll.kernel32
            h = k.OpenProcess(0x00100000, False, pid)            # SYNCHRONIZE
            if not h:
                return False
            gone = k.WaitForSingleObject(h, 0) == 0
            k.CloseHandle(h)
            return not gone
        os.kill(pid, 0)
        return True
    except Exception:
        return False


class GearSplash(QWidget):
    W, H = 240, 196

    def __init__(self, ready=None, parent_pid=None):
        super().__init__(None, Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True); self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.resize(self.W, self.H)
        self.ready, self.parent_pid = ready, parent_pid
        self.t0 = time.perf_counter(); self.out_at = None; self.last_check = 0.0
        self.gear = gear_path(54, 43, 10, 15)
        self.font = QFont('Arimo', 15); self.font.setBold(True)
        self.timer = QTimer(self); self.timer.setTimerType(Qt.PreciseTimer); self.timer.timeout.connect(self.frame)
        self.timer.start(15)
        self.place()

    def place(self):
        """always the middle of the screen: the main window opens in the middle too"""
        g = QGuiApplication.primaryScreen().availableGeometry()
        self.move(g.center().x() - self.W // 2, g.center().y() - self.H // 2)

    def frame(self):
        now = time.perf_counter()
        if self.out_at is None:
            if (self.ready and os.path.exists(self.ready)) or now - self.t0 > MAX_LIFE:
                self.out_at = now
            elif now - self.last_check > 0.5:
                self.last_check = now
                if not parent_alive(self.parent_pid):                # the program could not start: do not hang around
                    self.out_at = now
        elif now - self.out_at > FADE_OUT:
            self.timer.stop()
            try:
                if self.ready and os.path.exists(self.ready):
                    os.remove(self.ready)
            except OSError:
                pass
            QApplication.quit(); return
        self.update()

    def paintEvent(self, e):
        now = time.perf_counter(); t = now - self.t0
        alpha = min(1.0, t / FADE_IN)
        if self.out_at is not None:
            alpha *= max(0.0, 1.0 - (now - self.out_at) / FADE_OUT)
        k = min(1.0, t / FADE_IN)                                      # grows in softly (ease-out), no jump
        s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setOpacity(alpha)
        p.translate(self.W / 2, 82); p.scale(s, s)
        gear = QTransform().rotate(t * 140).map(self.gear)               # only the teeth turn, the light stays top-left
        p.save(); p.translate(4, 5); p.fillPath(gear, QColor(0, 0, 0, 80)); p.restore()   # shadow
        g = QRadialGradient(QPointF(-14, -16), 70)
        g.setColorAt(0, QColor(240, 92, 70)); g.setColorAt(0.45, RED); g.setColorAt(1, QColor(122, 20, 16))
        p.fillPath(gear, g)
        p.setPen(QPen(DARK, 2.2)); p.drawPath(gear)
        p.setPen(QPen(QColor(255, 190, 170, 150), 2)); p.drawEllipse(QPointF(0, 0), 27, 27)      # inner rim highlight
        p.setPen(QPen(DARK, 2)); p.drawEllipse(QPointF(0, 0), 15, 15)
        p.resetTransform()
        path = QPainterPath(); path.addText(0, 0, self.font, 'W&R City Manager')
        br = path.boundingRect(); path.translate(self.W / 2 - br.width() / 2 - br.x(), 172)
        p.setPen(QPen(DARK, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.drawPath(path)
        p.fillPath(path, QColor(255, 236, 214))


def main():
    a = sys.argv[1:]
    ready = a[a.index('--ready') + 1] if '--ready' in a else None
    parent = int(a[a.index('--parent') + 1]) if '--parent' in a else None
    app = QApplication(sys.argv)
    for f in ('Arimo-400.ttf', 'Arimo-700.ttf'):
        fp = os.path.join(HERE, 'assets', 'fonts', f)
        if os.path.exists(fp):
            QFontDatabase.addApplicationFont(fp)
    s = GearSplash(ready, parent); s.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
