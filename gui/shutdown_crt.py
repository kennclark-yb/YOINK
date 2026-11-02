"""Reusable 220 × 140 CRT renderer; the caller supplies one shutdown quip.

The established animated surface and native text rendering come from the CRT
prototype. The title uses procedural block glyphs, with no redistributed font.
"""
import os
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import (
    QColor, QFont, QFontDatabase, QLinearGradient, QMovie,
    QPainter, QPainterPath, QPainterPathStroker, QPen,
)
from PySide6.QtWidgets import QWidget

CRT_ASSET = Path(__file__).resolve().parents[1]/'assets/shutdown_system_optional.gif'

# Purpose-built five-column, seven-row terminal glyphs. Adjacent cells are
# united into solid faces before beveling, so no internal cell seams are drawn.
TITLE_GLYPHS = {
    'S': ('11111','10000','10000','11111','00001','00001','11111'),
    'Y': ('10001','10001','01010','00100','00100','00100','00100'),
    'T': ('11111','00100','00100','00100','00100','00100','00100'),
    'E': ('11111','10000','10000','11110','10000','10000','11111'),
    'M': ('10001','11011','10101','10101','10001','10001','10001'),
    'H': ('10001','10001','10001','11111','10001','10001','10001'),
    'U': ('10001','10001','10001','10001','10001','10001','01110'),
    'D': ('11110','10001','10001','10001','10001','10001','11110'),
    'O': ('01110','10001','10001','10001','10001','10001','01110'),
    'W': ('10001','10001','10001','10101','10101','10101','01010'),
    'N': ('10001','11001','11001','10101','10011','10011','10001'),
}


class CrtShutdownSurface(QWidget):
    TITLE_WORDS = ('SYSTEM', 'SHUTDOWN')
    TITLE_CELL = 3.5
    QUIP_RECT = QRectF(13, 104, 194, 18)

    def __init__(self, quip, parent=None):
        super().__init__(parent)
        # Offscreen Qt exposes no Windows system fonts until registration.
        # Load installed faces only; no font is copied or shipped with YOINK.
        if 'Consolas' not in QFontDatabase.families():
            font_dir = Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts'
            for name in ('consola.ttf', 'consolab.ttf'):
                if (font_dir/name).is_file():
                    QFontDatabase.addApplicationFont(str(font_dir/name))
        self.setObjectName('ShutdownCrt')
        self.setFixedSize(220, 140)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.quip = quip
        self.setAccessibleName('System shutdown')
        self.setAccessibleDescription(quip)
        self._title_paths = tuple(self.title_path(word, top) for word, top in zip(self.TITLE_WORDS, (22, 60)))
        self._movie = QMovie(str(CRT_ASSET), parent=self)
        self._movie.frameChanged.connect(self._frame_changed)
        self._movie.start()

    @staticmethod
    def terminal_font(size=10):
        font = QFont()
        font.setFamilies(['Consolas', 'Cascadia Mono', 'Courier New', 'monospace'])
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPixelSize(size)
        return font

    @classmethod
    def title_path(cls, word, top):
        cell = cls.TITLE_CELL
        width = (len(word)*6-1)*cell
        left = (220-width)/2
        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        for index, char in enumerate(word):
            for row, pixels in enumerate(TITLE_GLYPHS[char]):
                for column, enabled in enumerate(pixels):
                    if enabled == '1':
                        path.addRect(QRectF(left+(index*6+column)*cell, top+row*cell, cell, cell))
        face = path.simplified()
        # Widen the joined blocks into substantial faces before beveling.
        # This keeps the title bold at 220 px rather than reading as an outline.
        stroke = QPainterPathStroker()
        stroke.setWidth(1.0)
        stroke.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        return face.united(stroke.createStroke(face)).simplified()

    def _frame_changed(self, _frame):
        self.update()

    def _title(self, painter, face):
        painter.setPen(QPen(QColor(53, 131, 211, 28), 2.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(face)
        painter.setPen(QPen(QColor('#214776'), .7))
        painter.setBrush(QColor('#102a4b'))
        painter.drawPath(face.translated(1.5, 2.0))
        gradient = QLinearGradient(face.boundingRect().topLeft(), face.boundingRect().bottomLeft())
        gradient.setColorAt(0, QColor('#70b8ec'))
        gradient.setColorAt(.48, QColor('#458ed0'))
        gradient.setColorAt(1, QColor('#285d9c'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawPath(face)
        # Narrow top/left light and bottom/right shade form the face bevel.
        painter.fillPath(face.subtracted(face.translated(.65, .65)), QColor(146, 205, 244, 190))
        painter.fillPath(face.subtracted(face.translated(-.65, -.65)), QColor(13, 40, 77, 190))

    def _quip(self, painter):
        painter.setFont(self.terminal_font())
        flags = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        painter.setPen(QColor(137, 183, 211, 30))
        for dx, dy in ((-.5, 0), (.5, 0), (0, -.5), (0, .5)):
            painter.drawText(self.QUIP_RECT.translated(dx, dy), flags, self.quip)
        painter.setPen(QColor('#89b7d3'))
        painter.drawText(self.QUIP_RECT, flags, self.quip)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(self.rect()), 3, 3)
        painter.setClipPath(clip)
        painter.fillRect(self.rect(), QColor('#080d10'))
        pixmap = self._movie.currentPixmap()
        if not pixmap.isNull():
            painter.drawPixmap(QRectF(self.rect()), pixmap, QRectF(pixmap.rect()))
        for face in self._title_paths:
            self._title(painter, face)
        self._quip(painter)
        # Keep the established persistent raster crossing both surface and text.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 3, 6, 24))
        for y in range(1, 140, 2):
            painter.drawRect(QRectF(0, y, 220, .35))

    def closeEvent(self, event):
        self._movie.stop()
        super().closeEvent(event)
