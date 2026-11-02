"""Standalone view of the production CRT; production never imports tools."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication
from gui.shutdown_screen import ShutdownScreen

# Retain the previous tool's import name for external preview scripts.
OptionalCrtPreview = ShutdownScreen


def main():
    app = QApplication.instance() or QApplication([])
    screen = ShutdownScreen()
    screen.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
