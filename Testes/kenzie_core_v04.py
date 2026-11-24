"""Kenzie Core v0.4 - original event-driven visual core, separated for GUI integration."""
import math
import random
from dataclasses import dataclass
from PySide6.QtCore import Qt, QTimer, QPointF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QRadialGradient, QFont
from PySide6.QtWidgets import QWidget


STATES = {
    "IDLE": (0.18, QColor(92, 126, 255)),
    "THINKING": (0.52, QColor(123, 106, 255)),
    "EXECUTING": (0.88, QColor(52, 210, 255)),
    "SUCCESS": (0.70, QColor(92, 255, 195)),
    "ERROR": (0.78, QColor(255, 93, 132)),
}
EVENT_MAP = {
    "idle": "IDLE", "standby": "IDLE", "ready": "IDLE",
    "thinking": "THINKING", "think_start": "THINKING", "ai_start": "THINKING",
    "executing": "EXECUTING", "execution_start": "EXECUTING",
    "tool_start": "EXECUTING", "working": "EXECUTING",
    "success": "SUCCESS", "completed": "SUCCESS", "task_complete": "SUCCESS",
    "error": "ERROR", "failed": "ERROR", "failure": "ERROR",
}

@dataclass
class Particle:
    angle: float
    radius: float
    speed: float
    plane: int
    size: float
    alpha: float
    phase: float


class KenzieCore(QWidget):
    stateChanged = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(0, 0)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.state = "IDLE"
        self.last_event = "idle"
        self.last_event_detail = "Core ready"
        self.target_intensity, self.target_color = STATES[self.state]
        self.intensity = self.target_intensity
        self.color = QColor(self.target_color)
        self.elapsed = 0.0
        self.rng = random.Random(31)
        self.stars = [(self.rng.random(), self.rng.random(), self.rng.uniform(.35, 1.0)) for _ in range(90)]
        self.particles = []
        for _ in range(155):
            plane = self.rng.choice((0, 1, 2))
            self.particles.append(Particle(
                angle=self.rng.uniform(0, math.tau), radius=self.rng.uniform(.34, .95),
                speed=self.rng.uniform(.18, .85) * (-1 if self.rng.random() < .32 else 1),
                plane=plane, size=self.rng.uniform(.7, 2.4), alpha=self.rng.uniform(.28, .85),
                phase=self.rng.uniform(0, math.tau)))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

    def set_state(self, state, detail=None):
        state = str(state).strip().upper()
        if state not in STATES:
            return False
        self.state = state
        self.last_event = state.lower()
        self.last_event_detail = str(detail)[:90] if detail else state.title()
        self.target_intensity, self.target_color = STATES[state]
        self.stateChanged.emit(state, self.last_event)
        self.update()
        return True

    def mudar_estado(self, estado):
        """Compatibilidade com o Kenzie.py antigo; modos de sistema ficam IDLE."""
        key = str(estado).strip().upper()
        if key in ("THINKING", "EXECUTING", "SUCCESS", "ERROR"):
            return self.set_state(key)
        return self.set_event("idle", {"message": key.title() if key else "Idle"})


    def set_event(self, event, payload=None):
        key = str(event).strip().lower().replace(" ", "_")
        state = EVENT_MAP.get(key)
        if not state:
            return False
        detail = None
        if isinstance(payload, dict):
            detail = payload.get("tool") or payload.get("task") or payload.get("message")
        elif payload is not None:
            detail = str(payload)
        self.last_event = key
        accepted = self.set_state(state, detail or key.replace("_", " ").title())
        self.last_event = key
        return accepted


    def tick(self):
        dt = 1 / 60
        self.elapsed += dt
        blend = 0.045
        self.intensity += (self.target_intensity - self.intensity) * blend
        r, g, b = self.color.red(), self.color.green(), self.color.blue()
        tr, tg, tb = self.target_color.red(), self.target_color.green(), self.target_color.blue()
        self.color = QColor(int(r + (tr-r)*blend), int(g+(tg-g)*blend), int(b+(tb-b)*blend))
        for p in self.particles:
            p.angle += p.speed * (0.45 + self.intensity * 1.8) * dt
        self.update()


    def paintEvent(self, event):
        w, h = self.width(), self.height()
        cx, cy = w * .5, h * .49
        base = min(w, h) * .34
        radius = base * (1.0 + .025 * math.sin(self.elapsed * (1.6 + self.intensity)))
        pulse = 1.0 + .035 * math.sin(self.elapsed * (1.4 + self.intensity * 2.0))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), QColor(5, 7, 13))
        for sx, sy, brightness in self.stars:
            x, y = sx*w, sy*h
            dx, dy = x-cx, y-cy
            d = math.hypot(dx, dy)
            if d < radius * 2.7 and d > radius * .45:
                bend = (radius * .20) / max(d, 1) * (1.0 - min(d/(radius*2.7), 1))
                x += -dy * bend
                y += dx * bend
            alpha = int(22 + 58 * brightness)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(170, 190, 235, alpha))
            painter.drawEllipse(QPointF(x, y), .7 + brightness*1.1, .7 + brightness*1.1)
        glow = QRadialGradient(QPointF(cx, cy), radius * 2.7)
        glow.setColorAt(0.0, QColor(self.color.red(), self.color.green(), self.color.blue(), int(34 + 32*self.intensity)))
        glow.setColorAt(.34, QColor(self.color.red(), self.color.green(), self.color.blue(), 22))
        glow.setColorAt(1.0, QColor(5, 7, 13, 0))
        painter.setBrush(glow); painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), radius*2.7, radius*2.7)
        self.draw_particle_plane(painter, cx, cy, radius, plane=0, foreground=False)
        self.draw_accretion_band(painter, cx, cy, radius, -17, 1.0, 1.0, 0.30, 0)
        self.draw_accretion_band(painter, cx, cy, radius, 26, .78, .67, 0.22, 1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(1, 2, 6))
        painter.drawEllipse(QPointF(cx, cy), radius*.60, radius*.60)
        rim = QRadialGradient(QPointF(cx, cy), radius*.75)
        rim.setColorAt(.78, QColor(2, 3, 8, 0))
        rim.setColorAt(.94, QColor(self.color.red(), self.color.green(), self.color.blue(), int(40+65*self.intensity)))
        rim.setColorAt(1.0, QColor(self.color.red(), self.color.green(), self.color.blue(), 0))
        painter.setBrush(rim)
        painter.drawEllipse(QPointF(cx, cy), radius*.76, radius*.76)
        self.draw_particle_plane(painter, cx, cy, radius, plane=2, foreground=True)
        center_glow = QRadialGradient(QPointF(cx, cy), radius*.48*pulse)
        center_glow.setColorAt(0.0, QColor(self.color.red(), self.color.green(), self.color.blue(), int(40+42*self.intensity)))
        center_glow.setColorAt(.55, QColor(self.color.red(), self.color.green(), self.color.blue(), 18))
        center_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(center_glow); painter.drawEllipse(QPointF(cx, cy), radius*.48*pulse, radius*.48*pulse)
        painter.setPen(QColor(175, 190, 220, 150)); painter.setFont(QFont("Consolas", 10))
        painter.drawText(24, 30, "KENZIE // CORE v0.4")
        painter.setPen(QColor(self.color.red(), self.color.green(), self.color.blue(), 220))
        painter.drawText(24, h-40, f"STATE: {self.state}    INTENSITY: {self.intensity:.2f}")
        painter.setPen(QColor(150, 165, 190, 150))
        painter.drawText(24, h-22, f"EVENT: {self.last_event_detail[:54]}")
        painter.end()


    def draw_particle_plane(self, painter, cx, cy, radius, plane, foreground):
        tilt = (-.48, .22, .57)[plane]
        squash = (.42, .68, .36)[plane]
        scale = (1.12, .90, .82)[plane]
        for p in self.particles:
            if p.plane != plane:
                continue
            radial = radius * p.radius * scale
            ang = p.angle + p.phase*.04
            x = cx + math.cos(ang) * radial
            y = cy + math.sin(ang) * radial * squash + math.cos(ang)*radial*tilt*.16
            dist = math.hypot(x-cx, y-cy)
            if dist < radius*1.35:
                k = (radius*1.35-dist)/(radius*1.35)
                x += -(y-cy) * .075*k
                y += (x-cx) * .075*k
            twinkle = .72 + .28*math.sin(self.elapsed*3.0+p.phase)
            alpha = int(255*p.alpha*twinkle*(0.55 + self.intensity*.45))
            col = QColor(self.color); col.setAlpha(max(20, min(255, alpha)))
            painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(col)
            size = p.size * (1.0 + .45*self.intensity)
            painter.drawEllipse(QPointF(x, y), size, size)
            if foreground and p.size > 1.45:
                trail = QColor(col); trail.setAlpha(int(alpha*.20))
                painter.setPen(QPen(trail, max(.6, size*.45)))
                painter.drawLine(QPointF(x, y), QPointF(x-math.cos(ang)*size*3, y-math.sin(ang)*size*3))

    def draw_accretion_band(self, painter, cx, cy, radius, tilt_degrees, speed, width, alpha, band):
        tilt = math.radians(tilt_degrees)
        rotation = self.elapsed * speed * (0.38 + self.intensity*1.25) * (1 if band == 0 else -1)
        inner = radius * (0.72 if band == 0 else 0.90)
        outer = radius * (1.65 if band == 0 else 1.42)
        segments = 180
        for i in range(segments):
            a1 = (i/segments)*math.tau + rotation
            a2 = ((i+1)/segments)*math.tau + rotation
            mid = (a1+a2)*.5
            mix = .5 + .5*math.sin(mid*3.0 + self.elapsed*1.4 + band*2)
            c = QColor(self.color)
            c.setRed(min(255, int(c.red()*(.68+.45*mix))))
            c.setGreen(min(255, int(c.green()*(.74+.36*mix))))
            c.setBlue(min(255, int(c.blue()*(.78+.38*mix))))
            c.setAlpha(int(30 + 100*alpha*(.6+.4*mix)*(0.45+self.intensity)))
            painter.setPen(QPen(c, max(1.2, radius*width*.035), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            x1, y1 = cx+math.cos(a1)*outer, cy+math.sin(a1)*outer*math.cos(tilt)
            x2, y2 = cx+math.cos(a2)*outer, cy+math.sin(a2)*outer*math.cos(tilt)
            painter.drawLine(QPointF(x1,y1), QPointF(x2,y2))
            if i % 2 == 0:
                c2 = QColor(c); c2.setAlpha(int(c.alpha()*.50))
                painter.setPen(QPen(c2, max(1.0, radius*width*.08)))
                x3, y3 = cx+math.cos(a1)*inner, cy+math.sin(a1)*inner*math.cos(tilt)
                x4, y4 = cx+math.cos(a2)*inner, cy+math.sin(a2)*inner*math.cos(tilt)
                painter.drawLine(QPointF(x3,y3), QPointF(x4,y4))
