from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from .styles import TEXT, MUTED, HOVER_BG, DANGER
from .application import ASSETS


class TitleBar(QFrame):
    HEIGHT = 28

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
        self.maximize_button = self._create_button("□")
        self.close_button = self._create_button("×", danger=True)

        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

        self.minimize_button.clicked.connect(self.window.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize)
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

    def toggle_maximize(self):
        if self.window.isMaximized():
            self.window.showNormal()
            self.maximize_button.setText("□")
        else:
            self.window.showMaximized()
            self.maximize_button.setText("❐")

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()

        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.window.windowHandle()

            if handle:
                handle.startSystemMove()

        super().mousePressEvent(event)
