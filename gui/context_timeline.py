"""Virtualized message-sequence pills. Selection always belongs to ContextSelection."""
from bisect import bisect_right

from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from context_selection import ContextSelection


class MessageTimeline(QWidget):
    selectionChanged = Signal(object)
    navigationChanged = Signal()
    cursorChanged = Signal(int)

    def __init__(self, count, parent=None):
        super().__init__(parent)
        self.selection = ContextSelection(count)
        self.first = 0
        self.pitch = 12
        self.fit_all = True
        self._press_point = None
        self._moved = False
        self._click_base = None
        self.cursor = 0
        self.hover = None
        self._keyboard_focus = False
        self._drag = None
        self._edge = 0
        self._starts = ()
        self.last_painted_count = 0
        self.setMinimumHeight(68)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAccessibleName("Message timeline")
        self.setAccessibleDescription(
            "Left and Right navigate messages; Home and End jump. Space or Enter selects; "
            "Ctrl+0 fits all; Ctrl+= and Ctrl+- zoom. Control adds. Drag replaces; Control-drag adds. Drag upper boundary handles to adjust.")
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setInterval(45)
        self._scroll_timer.timeout.connect(self._autoscroll)

    @property
    def capacity(self):
        if self.fit_all:
            return max(1, self.selection.message_count)
        return min(max(1, self.selection.message_count), max(1, self.width() // self.pitch))

    @property
    def cell_width(self):
        # Spread a fitting conversation across A–B, while retaining slim pills.
        return self.width() / self.capacity if self.fit_all else max(self.pitch, self.width() / self.capacity)

    @property
    def visible_positions(self):
        return range(self.first, min(self.selection.message_count, self.first + self.capacity))

    def pill_rect(self, position):
        width = min(5, self.cell_width * .65)
        return QRectF((position - self.first) * self.cell_width + (self.cell_width - width) / 2,
                      32, width, 22)

    def hit_test(self, point, clamp=False):
        if not self.selection.message_count:
            return None
        slot = int(point.x() // self.cell_width)
        if clamp:
            slot = max(0, min(self.capacity - 1, slot))
        elif not (0 <= point.x() < self.width() and 8 <= point.y() <= 68):
            return None
        slot = max(0, min(self.capacity - 1, slot))
        position = self.first + slot
        return position if position < self.selection.message_count else (
            self.selection.message_count - 1 if clamp else None)

    def set_selection(self, selection):
        if selection == self.selection:
            return
        self.selection = selection
        self._starts = tuple(r.start for r in selection.ranges)
        self.update()
        self.selectionChanged.emit(selection)

    def set_first(self, first):
        first = max(0, min(first, max(0, self.selection.message_count - self.capacity)))
        if first != self.first:
            self.first = first
            self.update()
            self.navigationChanged.emit()

    def zoom(self, delta):
        self.fit_all = False
        self.pitch = max(10, min(28, self.pitch + delta))
        self.set_first(self.first)
        self.navigationChanged.emit()
        self.update()

    def ensure_visible(self, position):
        if position < self.first:
            self.set_first(position)
        elif position >= self.first + self.capacity:
            self.set_first(position - self.capacity + 1)

    def resizeEvent(self, event):
        self.set_first(self.first)
        self.navigationChanged.emit()
        super().resizeEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor("#929AAA"))
        p.drawText(0,15,"Beginning")
        p.drawText(self.width()//2-5,15,"→")
        p.drawText(self.width()-p.fontMetrics().horizontalAdvance("End"),15,"End")
        self.last_painted_count = 0
        step = max(1, int(1 / max(.000001,self.cell_width)))
        for position in range(self.first, min(self.selection.message_count,self.first+self.capacity),step):
            self.last_painted_count += 1
            index = bisect_right(self._starts, position) - 1
            item = self.selection.ranges[index] if index >= 0 else None
            end = min(position+step,self.selection.message_count)
            index = bisect_right(self._starts,end-1)-1
            item = self.selection.ranges[index] if index >= 0 else None
            selected = item is not None and item.end > position
            rect = self.pill_rect(position)
            if step>1:rect.setWidth(max(1,step*self.cell_width))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#4D7CFE" if selected else "#2B3245"))
            if position == self.hover:
                p.setBrush(QColor("#789BFF" if selected else "#485777"))
            p.drawRoundedRect(rect, 2.5, 2.5)
            if selected and position in (item.start, item.end - 1):
                p.setPen(QPen(QColor("#B3C7FF"), 1))
                p.setBrush(QColor("#8AA9FF"))
                p.drawRoundedRect(QRectF(rect.x() - 1, 22, 7, 6), 2, 2)
                p.drawLine(rect.bottomLeft(), rect.bottomRight())
            if self.hasFocus() and self._keyboard_focus and position == self.cursor:
                p.setPen(QPen(QColor("#D4DFFF"), 1))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawLine(rect.left()-1, 62, rect.right()+1, 62)
        p.setPen(QColor("#929AAA"))
        if self.selection.message_count:
            last = min(self.first + self.capacity, self.selection.message_count)
            if step > 1:
                p.drawText(0, 79, f"Grouped overview · ~{step} messages/pixel; zoom in for precision")
        else:
            p.drawText(0, 79, "No source messages")

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        position = self.hit_test(event.position())
        if position is None:
            return
        self._keyboard_focus = False
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.cursor = position
        self.cursorChanged.emit(position)
        # Freeze additive intent at press: releasing Ctrl never changes the gesture.
        additive = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        base = self.selection
        self._click_base = base
        self._press_point = event.position()
        self._moved = False
        anchor = position
        if not additive and event.position().y() < 32:
            for item in base.ranges:
                if position in (item.start, item.end - 1):
                    anchor = item.end - 1 if position == item.start else item.start
                    base = base.remove(item.start, item.end)
                    additive = True
                    break
        self._drag = (anchor, base, additive)

    def _extend(self, position):
        if self._drag is None:
            return
        anchor, base, additive = self._drag
        method = base.add if additive else base.replace
        self.set_selection(method(min(anchor, position), max(anchor, position) + 1))

    def mouseMoveEvent(self, event):
        self.hover = self.hit_test(event.position())
        if self._drag:
            self._moved |= (event.position()-self._press_point).manhattanLength() >= 4
            if not self._moved:return
            self._edge = -1 if event.position().x() < 0 else (
                1 if event.position().x() >= self.capacity * self.cell_width else 0)
            self._extend(self.hit_test(event.position(), clamp=True))
            if self._edge:
                self._scroll_timer.start()
            else:
                self._scroll_timer.stop()
        if self.hover is not None:
            self.setToolTip(f"Message {self.hover + 1:,}")
        self.update()

    def _autoscroll(self):
        self.set_first(self.first + self._edge)
        position = self.first if self._edge < 0 else min(
            self.selection.message_count - 1, self.first + self.capacity - 1)
        self._extend(position)

    def mouseReleaseEvent(self, event):
        if self._drag and event.button() == Qt.MouseButton.LeftButton:
            position = self.hit_test(event.position(), clamp=True)
            if self._moved:
                self._extend(position)
            else:
                additive = self._drag[2]
                base = self._click_base
                selected = any(r.start <= position < r.end for r in base.ranges)
                self.set_selection(base.remove(position,position+1) if selected and not additive
                                   else base.select_message(position,add=additive))
            self._drag = None
            self._scroll_timer.stop()

    def hideEvent(self, event):
        self._drag = None
        self._scroll_timer.stop()
        super().hideEvent(event)

    def leaveEvent(self, event):
        self.hover = None
        self.update()

    def focusInEvent(self, event):
        self._keyboard_focus = event.reason() in (Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason, Qt.FocusReason.ShortcutFocusReason)
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() or event.angleDelta().x()
        self.set_first(self.first + (-3 if delta > 0 else 3))
        event.accept()

    def keyPressEvent(self, event):
        self._keyboard_focus = True
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Home, Qt.Key.Key_End):
            if not self.selection.message_count:
                return
            self.cursor = (0 if key == Qt.Key.Key_Home else self.selection.message_count - 1
                           if key == Qt.Key.Key_End else max(0, min(self.selection.message_count - 1,
                           self.cursor + (1 if key == Qt.Key.Key_Right else -1))))
            self.ensure_visible(self.cursor)
            self.cursorChanged.emit(self.cursor)
            self.update()
            event.accept()
        elif key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.selection.message_count:
                self.set_selection(self.selection.select_message(self.cursor, add=bool(
                    event.modifiers() & Qt.KeyboardModifier.ControlModifier)))
            event.accept()
        else:
            super().keyPressEvent(event)
