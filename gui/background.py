from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from .styles import WINDOW_BG, ACCENT


class Background(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(0, 0, -1, -1)

        # Rounded outer shape
        path = QPainterPath()
        path.addRoundedRect(rect, 18, 18)

        painter.setClipPath(path)

        # Base background
        painter.fillPath(path, QColor(WINDOW_BG))

        # Large ambient cobalt glow
        glow = QColor(ACCENT)
        glow.setAlpha(28)

        gradient = painter
        gradient.setPen(Qt.PenStyle.NoPen)

        # Soft layered glow
        for i in range(7):
            margin = i * 45
            glow_rect = rect.adjusted(
                -margin,
                -margin,
                margin,
                margin,
            )

            glow_color = QColor(ACCENT)
            glow_color.setAlpha(max(0, 24 - i * 3))

            painter.setBrush(glow_color)
            painter.drawEllipse(
                glow_rect.left() - 180,
                glow_rect.top() - 180,
                glow_rect.width() // 2,
                glow_rect.height() // 2,
            )

        # Restore clipping before border
        painter.setClipping(False)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#292B31"), 1))
        painter.drawPath(path)