from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from .styles import TEXT, MUTED, HOVER_BG, DANGER
from .application import ASSETS


class TitleBar(QFrame):
    HEIGHT = 24

    def __init__(self, window):
        super().__init__(window)

        self.window = window
        self.setFixedHeight(self.HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 4, 0)
        layout.setSpacing(3)

        self.icon = QLabel()
        self.icon.setFixedSize(18, 18)
        self.icon.setPixmap(QIcon(str(ASSETS / "icon" / "yoink.ico")).pixmap(18, 18))
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(self.icon)

        self.title = QLabel("YOINK — The ChatSnatcher")
        self.title.setStyleSheet(
            f"""
            QLabel {{
                color: {TEXT};
                font-size: 12px;
                font-weight: 600;
            }}
            """
        )

        layout.addWidget(self.title)
        layout.addStretch()

        self.minimize_button = self._create_button("—")
        self.close_button = self._create_button("×", danger=True)
        self.minimize_button.setAccessibleName("Minimize")
        self.minimize_button.setToolTip("Minimize")
        self.close_button.setStyleSheet("""
            QPushButton { color: #E33258; background: transparent; border: 1px solid transparent; border-radius: 6px; font-size: 20px; font-weight: 700; }
            QPushButton:hover { color: #FF6685; background: rgba(160, 20, 55, 65); }
            QPushButton:pressed { color: white; background: #BB2345; }
            QPushButton:focus { border: 1px solid #FF6685; }
        """)
        self.close_button.setAccessibleName("Close")
        self.close_button.setToolTip("Close")

        layout.addWidget(self.minimize_button)
        layout.addWidget(self.close_button)

        self.minimize_button.clicked.connect(self.window.showMinimized)
        self.close_button.clicked.connect(self.window.close)

    def _create_button(self, text, danger=False):
        button = QPushButton(text)
        button.setFixedSize(28, 22)

        hover = DANGER if danger else HOVER_BG
        text_color = "#FFFFFF" if danger else MUTED

        button.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: {text_color};
                border: none;
                border-radius: 6px;
                font-size: 14px;
                padding: 0;
            }}

            QPushButton:hover {{
                background: {hover};
                color: #FFFFFF;
            }}
            """
        )

        return button

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.window.windowHandle()

            if handle:
                handle.startSystemMove()

        super().mousePressEvent(event)
