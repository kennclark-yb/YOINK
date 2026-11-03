"""Contained, animated DOCFATHER teaser action."""
import math
import os
import time

from PySide6.QtCore import Property, QEasingCurve, QEvent, QPropertyAnimation, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QPushButton


class DocfatherButton(QPushButton):
    NORMAL = "CONSULT THE DOCFATHER"
    HOVER = "STATE YOUR CASE."
    CLICK = "THE DOCFATHER IS STILL OUT."
    HOVER_FILL = .625
    HOLD_MS = 1750

    def __init__(self):
        super().__init__(self.NORMAL)
        self.setAccessibleName(self.NORMAL)
        self.setAccessibleDescription("THE DOCFATHER is coming soon.")
        self.setToolTip("THE DOCFATHER is coming soon")
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self._fill = 0.0
        self._inside = False
        self._holding = False
        self._phase = 0.0
        self._last_tick = 0.0
        self._watched_window = None
        self._animation = QPropertyAnimation(self, b"portalFill", self)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._wave_timer = QTimer(self)
        self._wave_timer.setInterval(40)
        self._wave_timer.timeout.connect(self._advance_wave)
        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._end_hold)
        self.clicked.connect(self._activate)

    def _get_fill(self):
        return self._fill

    def _set_fill(self, value):
        self._fill = max(0.0, min(1.0, value))
        self.update()

    portalFill = Property(float, _get_fill, _set_fill)

    @staticmethod
    def _reduced_motion():
        return os.environ.get("YOINK_REDUCED_MOTION") == "1"

    def _animate(self, target, duration=250):
        self._animation.stop()
        if self._reduced_motion() or not self.isVisible():
            self._set_fill(target)
            return
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._fill)
        self._animation.setEndValue(target)
        self._animation.start()

    def _sync_wave_timer(self):
        active = (self._inside and not self._holding and self.isEnabled()
                  and self.isVisible() and self.window().isActiveWindow()
                  and not self._reduced_motion())
        if active and not self._wave_timer.isActive():
            self._last_tick = time.monotonic()
            self._wave_timer.start()
        elif not active:
            self._wave_timer.stop()

    def _advance_wave(self):
        self._sync_wave_timer()
        if not self._wave_timer.isActive():
            return
        now = time.monotonic()
        self._phase = (self._phase + min(now - self._last_tick, .1)) % 10000
        self._last_tick = now
        self.update()

    def _wave_height(self, x):
        # Opposing currents have distinct wavelengths and speeds. Their summed
        # amplitudes bound the surface between 50% and 75% of button height.
        return (.075 * math.sin(2 * math.pi * (1.3 * x - .31625 * self._phase))
                + .05 * math.sin(2 * math.pi * (2.4 * x + .20075 * self._phase + .18)))

    def _activate(self):
        self._holding = True
        self.setText(self.CLICK)
        self._sync_wave_timer()
        self._animate(1.0, 180)
        self._hold_timer.start(self.HOLD_MS)

    def _end_hold(self):
        self._holding = False
        self.setText(self.HOVER if self._inside and self.isEnabled() else self.NORMAL)
        self._animate(self.HOVER_FILL if self._inside and self.isEnabled() else 0.0)
        self._sync_wave_timer()

    def _reset(self):
        self._inside = False
        self._holding = False
        self._wave_timer.stop()
        self._hold_timer.stop()
        self._animation.stop()
        self.setText(self.NORMAL)
        self._set_fill(0.0)

    def showEvent(self, event):
        super().showEvent(event)
        window = self.window()
        if self._watched_window is not window:
            if self._watched_window is not None:
                self._watched_window.removeEventFilter(self)
            self._watched_window = window
            window.installEventFilter(self)
        self._sync_wave_timer()

    def hideEvent(self, event):
        self._reset()
        super().hideEvent(event)

    def eventFilter(self, obj, event):
        if obj is self._watched_window:
            if event.type() == QEvent.Type.WindowDeactivate:
                self._wave_timer.stop()
            elif event.type() == QEvent.Type.WindowActivate:
                QTimer.singleShot(0, self._sync_wave_timer)
        return super().eventFilter(obj, event)

    def enterEvent(self, event):
        self._inside = True
        if self.isEnabled() and not self._holding:
            self.setText(self.HOVER)
            self._animate(self.HOVER_FILL)
        self._sync_wave_timer()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._inside = False
        if not self._holding:
            self.setText(self.NORMAL)
            self._animate(0.0)
        self._sync_wave_timer()
        super().leaveEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.EnabledChange:
            if not self.isEnabled():
                self._reset()
            self.setCursor(Qt.CursorShape.PointingHandCursor if self.isEnabled() else Qt.CursorShape.ArrowCursor)
        super().changeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Reserve two pixels inside the existing widget for a restrained glow.
        rect = QRectF(self.rect()).adjusted(2.5, 2.5, -2.5, -2.5)
        outline = QPainterPath()
        outline.addRoundedRect(rect, 9, 9)
        if self.isEnabled() and self._fill > 0:
            glow = min(1.0, self._fill / self.HOVER_FILL)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(210, 158, 53, round(38 * glow)), 5))
            painter.drawPath(outline)
            painter.setPen(QPen(QColor(218, 167, 62, round(62 * glow)), 3))
            painter.drawPath(outline)
        mix = min(1.0, self._fill / self.HOVER_FILL) if self.isEnabled() else 0.0
        base = QColor(*(round(a + (b-a)*mix) for a,b in zip((229,229,231),(23,34,56)))) if self.isEnabled() else QColor("#25262C")
        painter.fillPath(outline, base)
        liquid = QPainterPath()
        edge = QPainterPath()
        if self.isEnabled() and self._fill > 0:
            # Fade wave amplitude near the empty and fully filled endpoints.
            strength = min(1.0, self._fill / self.HOVER_FILL,
                           (1.0 - self._fill) / (1.0 - self.HOVER_FILL))
            for i in range(81):
                x = i / 80
                y = rect.bottom() - rect.height() * (self._fill + strength * self._wave_height(x))
                px = rect.left() + x * rect.width()
                if i == 0:
                    liquid.moveTo(px, y)
                    edge.moveTo(px, y)
                else:
                    liquid.lineTo(px, y)
                    edge.lineTo(px, y)
            liquid.lineTo(rect.right(), rect.bottom())
            liquid.lineTo(rect.left(), rect.bottom())
            liquid.closeSubpath()
            painter.save()
            painter.setClipPath(outline)
            gold = QLinearGradient(0, rect.top(), 0, rect.bottom())
            gold.setColorAt(0, QColor("#F6D279"))
            gold.setColorAt(.55, QColor("#DDAF4A"))
            gold.setColorAt(1, QColor("#B88A31"))
            painter.fillPath(liquid, gold)
            highlight = QLinearGradient(rect.left(), 0, rect.right(), 0)
            highlight.setColorAt(0, QColor(255, 239, 161, 0))
            highlight.setColorAt(.35, QColor(255, 239, 161, 150))
            highlight.setColorAt(.6, QColor(255, 239, 161, 30))
            highlight.setColorAt(.8, QColor(255, 239, 161, 115))
            highlight.setColorAt(1, QColor(255, 239, 161, 0))
            if self._fill < .99:
                painter.setPen(QPen(highlight, 1.2))
                painter.drawPath(edge)
            painter.restore()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#B88932" if self.isEnabled() else "#555861"), 1))
        painter.drawPath(outline)
        if self.hasFocus() and self.isEnabled():
            focus = QPainterPath()
            focus.addRoundedRect(rect.adjusted(2, 2, -2, -2), 7, 7)
            painter.setPen(QPen(QColor("#4D7CFE"), 1.5))
            painter.drawPath(focus)
        painter.setPen(QColor("#FFF5DB" if mix > .55 else "#273041") if self.isEnabled() else QColor("#8A8D96"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        if self.isEnabled() and self._fill:
            painter.save()
            painter.setClipPath(outline.intersected(liquid))
            painter.setPen(QColor("#273041"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
            painter.restore()
