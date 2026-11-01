"""Accepted static artwork with an opaque plain-background diagnostic fallback."""
import os
import logging

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QWidget
from .styles import WINDOW_BG
from .application import ASSETS


class Background(QWidget):
    def __init__(self):
        super().__init__()
        self.preview_enabled = os.environ.get("YOINK_STATIC_BG_PREVIEW") != "0"
        self.panel_opacity = os.environ.get("YOINK_PANEL_OPACITY", "84")
        if self.panel_opacity not in ("78", "84", "90"):
            self.panel_opacity = "84"
        self.panel_alpha = round(255 * int(self.panel_opacity) / 100)
        self._cache = QImage()
        self._cache_key = None
        self._image = QImage()
        self.asset_error = None
        if self.preview_enabled:
            path = ASSETS / "static_grain_option3.png"
            if not self._image.load(str(path)):
                self.asset_error = f"Cannot load static background asset: {path}"
                logging.getLogger(__name__).error(self.asset_error)
                # Restore opaque plain surfaces when artwork is unavailable.
                self.preview_enabled = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = self.window()._outer_window_path()
        painter.fillPath(path, QColor(WINDOW_BG))
        if self.preview_enabled and not self._image.isNull():
            painter.setClipPath(path)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            # Fit the full abstract composition to normalized window coordinates.
            # No cover zoom/crop: opposing corners remain visible at either aspect.
            # Cache at physical resolution until geometry or display scaling changes.
            dpr = self.devicePixelRatioF()
            key = (self.width(), self.height(), dpr)
            if key != self._cache_key:
                self._cache = self._image.scaled(
                    round(self.width() * dpr), round(self.height() * dpr),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                self._cache.setDevicePixelRatio(dpr)
                self._cache_key = key
            x = (self.width() - self._cache.width() / dpr) / 2
            y = (self.height() - self._cache.height() / dpr) / 2
            painter.drawImage(QPointF(x, y), self._cache)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.window().windowHandle()
            if handle:
                handle.startSystemMove()
        super().mousePressEvent(event)
