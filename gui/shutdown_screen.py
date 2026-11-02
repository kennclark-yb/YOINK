"""Production shutdown: blue CRT and one original randomized closing message."""
import random
from PySide6.QtCore import Qt
from .shutdown_crt import CrtShutdownSurface

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


class ShutdownScreen(CrtShutdownSurface):
    def __init__(self):
        super().__init__(random.choice(EXIT_MESSAGES))
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
