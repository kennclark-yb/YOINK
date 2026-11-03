"""Aligned bracket rendering for the Results utility column."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QPushButton, QStyle, QStyleOptionButton

def draw_brackets(painter, rect, text):
    if not (text.startswith("[ ") and text.endswith(" ]")):
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        return
    left, right = rect.left() + 4, rect.right() - 4
    metrics = painter.fontMetrics()
    painter.drawText(QRectF(left, rect.top(), 6, rect.height()), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "[")
    painter.drawText(QRectF(right-6, rect.top(), 6, rect.height()), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "]")
    painter.drawText(QRectF(left+6, rect.top(), right-left-12, rect.height()), Qt.AlignmentFlag.AlignCenter, text[2:-2])

class BracketButton(QPushButton):
    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.text = ""
        painter = QPainter(self)
        self.style().drawControl(QStyle.ControlElement.CE_PushButton, option, painter, self)
        color = option.palette.buttonText().color()
        painter.setPen(color)
        draw_brackets(painter, QRectF(self.rect()).adjusted(0, 0, -1, -1), self.text())
