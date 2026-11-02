"""Shared native hover clock; mouse focus stays separate from Tab focus."""
import time
from PySide6.QtCore import QObject, QEvent, QTimer, Qt


class ActionInteractions(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.entries = {}
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.tick)

    def register(self, widget, card=False, smooth_hover=False):
        if not card:
            widget.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        widget.setProperty("yoinkSmoothHover", smooth_hover)
        if smooth_hover:
            widget.setStyleSheet(widget.styleSheet() + "\nQPushButton:hover:enabled { background: #1B2340; }\nQPushButton:pressed:enabled { background: #4D7CFE; color: white; }")
        self.entries[widget] = [widget.styleSheet(), 0.0, False, 0.0, card]
        widget.installEventFilter(self)
        widget.destroyed.connect(lambda: self.entries.pop(widget, None))

    def eventFilter(self, obj, event):
        entry = self.entries.get(obj)
        if entry is not None:
            if event.type() == QEvent.Type.EnabledChange and not obj.isEnabled():
                entry[1:4] = [0.0, False, 0.0]
                obj.setStyleSheet(entry[0])
                return False
            if not obj.isEnabled():
                return False
            if event.type() == QEvent.Type.Enter:
                entry[2] = True
                self.timer.start()
            elif event.type() == QEvent.Type.Leave:
                entry[2] = False
                entry[3] = time.monotonic() + .125
                self.timer.start()
        return False

    def tick(self):
        active = False
        now = time.monotonic()
        for widget, entry in list(self.entries.items()):
            if not widget.isEnabled():
                continue
            base, value, inside, deadline, card = entry
            target = 1.0 if inside or now < deadline else 0.0
            updated = min(1.0, value + .16) if target else max(0.0, value - .09)
            if updated != value:
                entry[1] = updated
                red, green, blue = [round(a + (b-a)*updated) for a,b in ((27,37),(35,47),(64,85))]
                if updated == 0:
                    widget.setStyleSheet(base)
                    continue
                if card:
                    color = [round(a+(b-a)*updated) for a,b in ((48,77),(49,124),(55,254))]
                    widget.setStyleSheet(base + f"\nQFrame#ResultPartCard {{ border: 1px solid rgb({color[0]},{color[1]},{color[2]}); }}")
                    active = True
                    continue
                selector = "QPushButton, QPushButton:hover:enabled" if widget.property("yoinkSmoothHover") else "QPushButton"
                pressed = "QPushButton:pressed:enabled" if widget.property("yoinkSmoothHover") else "QPushButton:pressed"
                widget.setStyleSheet(base + f"\n{selector} {{ background: rgb({red},{green},{blue}); border: 1px solid #303137; border-radius: 7px; }}\nQPushButton:focus {{ border-color: #7FA0FF; }}\n{pressed} {{ background: #4D7CFE; color: white; border-color: #4D7CFE; }}")
            active |= inside and updated < 1 or not inside and (updated > 0 or now < deadline)
        if not active:
            self.timer.stop()

    def clear(self):
        self.timer.stop()
        for widget, entry in list(self.entries.items()):
            widget.setStyleSheet(entry[0])
            entry[1:4] = [0.0, False, 0.0]
