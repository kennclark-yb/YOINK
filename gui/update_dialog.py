"""Compact YOINK presentation for update results; no update-check logic."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from .application import ASSETS


class UpdateDialog(QDialog):
    def __init__(self, parent, message, actions):
        super().__init__(parent)
        self.setWindowTitle("YOINK updates")
        self.setWindowIcon(QIcon(str(ASSETS / "icon" / "yoink.ico")))
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setModal(False)
        self.setFixedWidth(390)
        self.setStyleSheet("""
            QFrame#UpdateCard {
                background: #15161A; border: 1px solid #303137; border-radius: 12px;
            }
            QLabel { color: #F2F2F4; background: transparent; border: none; }
            QPushButton {
                background: #1B2340; color: #F2F2F4;
                border: 1px solid #303137; border-radius: 7px; padding: 8px 14px;
            }
            QPushButton:hover, QPushButton:focus { border-color: #4D7CFE; }
            QPushButton#UpdateClose { background: transparent; border: none; padding: 0; }
            QPushButton#UpdateClose:hover { background: #FF5C5C; }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        card = QFrame()
        card.setObjectName("UpdateCard")
        outer.addWidget(card)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 18)
        layout.setSpacing(16)
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(self.windowIcon().pixmap(18, 18))
        header.addWidget(icon)
        title = QLabel("YOINK updates")
        title.setStyleSheet("font-size: 12px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        close = QPushButton("×")
        close.setObjectName("UpdateClose")
        close.setAccessibleName("Close update dialog")
        close.setFixedSize(24, 24)
        close.setAutoDefault(False)
        close.clicked.connect(self.reject)
        header.addWidget(close)
        layout.addLayout(header)
        self.message = QLabel(message)
        self.message.setTextFormat(Qt.TextFormat.PlainText)
        self.message.setWordWrap(True)
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message)
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch()
        self.action_buttons = []
        for label, callback in actions:
            button = QPushButton(label)
            button.setAutoDefault(False)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, action=callback: self._choose(action))
            buttons.addWidget(button)
            self.action_buttons.append(button)
        buttons.addStretch()
        layout.addLayout(buttons)

    def _choose(self, action):
        if action is not None:
            action()
        self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.adjustSize()
        position = self.frameGeometry()
        position.moveCenter(self.parentWidget().frameGeometry().center())
        self.move(position.topLeft())
        self.action_buttons[0].setFocus(Qt.FocusReason.OtherFocusReason)
