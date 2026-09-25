"""Small, Preview-only role selector and full-conversation HTML rendering."""
import markdown

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QPushButton, QSizePolicy,
                               QStyle, QStyleOptionButton, QStylePainter)


def render_preview_variants(conversation):
    """Prepare all three views in one pass, without renumbering filtered messages."""
    sections = {role: [] for role in ("all", "assistant", "user")}
    for index, message in enumerate(conversation["messages"], 1):
        assistant = message["role"] == "assistant"
        label = "The AI" if assistant else "The User"
        alignment = "left" if assistant else "right"
        header = (f'<h3 align="{alignment}" style="color: #4D7CFE;">'
                  f'[msg {index:03d}] {label}</h3>')
        body = markdown.markdown(message["text"], extensions=["fenced_code", "tables"])
        section = header + body
        sections["all"].append(section)
        if message["role"] in sections:
            sections[message["role"]].append(section)
    return {role: '<hr>'.join(items) or '<p>No messages for this role.</p>'
            for role, items in sections.items()}


class PreviewSegmentButton(QPushButton):
    """Keep keyboard focus visible without native mouse-focus/default rectangles."""
    keyboard_focus = False

    def focusInEvent(self, event):
        self.keyboard_focus = event.reason() in (
            Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason,
            Qt.FocusReason.ShortcutFocusReason,
        )
        super().focusInEvent(event)

    def mousePressEvent(self, event):
        self.keyboard_focus = False
        super().mousePressEvent(event)
        self.update()

    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.state &= ~QStyle.StateFlag.State_HasFocus
        painter = QStylePainter(self)
        painter.drawControl(QStyle.ControlElement.CE_PushButton, option)
        if self.hasFocus() and self.keyboard_focus:
            painter.setRenderHint(painter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor("#8AA9FF"), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(2, 2, -3, -3), 6, 6)


class PreviewRoleSelector(QFrame):
    changed = Signal(str)
    ROLES = ("all", "assistant", "user")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PreviewRoleSelector")
        self.setFixedSize(228, 32)
        self.current_role = "all"
        self.setStyleSheet("""
            QFrame#PreviewRoleSelector {
                background: #0F1012; border: 1px solid #303137; border-radius: 9px;
            }
            QPushButton {
                background: transparent; border: none; color: #92949D;
                font-size: 11px; padding: 0;
            }
            QPushButton[active="true"] { color: #FFFFFF; font-weight: 600; }
        """)
        self.pill = QFrame(self)
        self.pill.setStyleSheet("background: #263B72; border: none; border-radius: 6px;")
        self.pill.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)
        self.buttons = []
        for label, role in zip(("All", "A.I.", "User"), self.ROLES):
            button = PreviewSegmentButton(label)
            button.setAutoDefault(False)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setProperty("active", role == "all")
            button.clicked.connect(lambda checked=False, role=role: self.select(role))
            layout.addWidget(button, 1)
            self.buttons.append(button)
        self.animation = QPropertyAnimation(self.pill, b"geometry", self)
        self.animation.setDuration(180)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pill.setGeometry(self._pill_rect(0))
        self.pill.lower()

    def _pill_rect(self, index):
        width = (self.width() - 6) // 3
        return QRect(3 + width * index, 3, width, self.height() - 6)

    def select(self, role):
        if role == self.current_role:
            return
        index = self.ROLES.index(role)
        self.current_role = role
        self.animation.stop()
        self.animation.setStartValue(self.pill.geometry())
        self.animation.setEndValue(self._pill_rect(index))
        self.animation.start()
        for button, item in zip(self.buttons, self.ROLES):
            button.setProperty("active", item == role)
            button.style().unpolish(button)
            button.style().polish(button)
        self.changed.emit(role)
