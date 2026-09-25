import random
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

EXIT_MESSAGES = [
    "Feeding data into dumpster.",
    "Sweeping crumbs under rug.",
    "Burying evidence.",
    "Flushing temp files.",
    "Releasing captive hamsters.",
    "Turning off lights.",
    "Yeeting cache into abyss.",
    "Tucking RAM into bed.",
    "Wiping digital fingerprints.",
    "Scramming before server notices.",
    "Feeding paper shredder.",
    "Setting RAM to zero.",
    "Burning bridges and logs.",
    "Returning borrowed bytes.",
    "Throwing trash out window.",
    "Deleting digital paper trail.",
    "Ejecting seat.",
    "Hiding secrets from OS.",
    "Sending data to farm upstate.",
    "Vaporizing leftovers.",
    "Sweeping floor.",
    "Self-destruct sequence finished.",
]

class ShutdownScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedSize(280, 180)

        frame = QFrame(self)
        frame.setObjectName("ShutdownFrame")
        frame.setStyleSheet(
            """
            QFrame#ShutdownFrame {
                background: #15161A;
                border: 1px solid #303137;
                border-radius: 18px;
            }

            QLabel#ShutdownGraphic {
                color: #F2F2F4;
                font-size: 42px;
            }

            QLabel#ShutdownMessage {
                color: #B8BAC2;
                font-size: 11px;
                font-weight: 600;
            }
            """
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        graphic = QLabel()
        graphic.setObjectName("ShutdownGraphic")
        graphic.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        asset_path = Path(__file__).resolve().parent.parent / "assets" / "shutdown.gif"
        self._movie = QMovie(str(asset_path))
        self._movie.setScaledSize(
            QSize(220, 140)
        )

        graphic.setMovie(self._movie)
        self._movie.start()

        message = QLabel(
            random.choice(EXIT_MESSAGES)
        )
        message.setObjectName("ShutdownMessage")
        message.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addStretch()
        layout.addWidget(graphic)
        layout.addWidget(message)
        layout.addStretch()

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(frame)
