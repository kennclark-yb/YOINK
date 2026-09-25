"""Application-wide presentation; paths work in source and PyInstaller layouts."""
import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase, QIcon


ASSETS = Path(__file__).resolve().parent.parent / "assets"


def configure_application(app):
    if app.property("yoinkConfigured"):
        return

    app.setApplicationName("YOINK")
    app.setApplicationDisplayName("YOINK — The ChatSnatcher")
    # Give Windows a stable taskbar identity instead of inheriting python.exe's.
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("YOINK.ChatSnatcher")

    for weight in ("Regular", "SemiBold", "Bold"):
        # Register bytes so Windows and offscreen Qt use the same font loader.
        font_data = (ASSETS / "fonts" / f"Inter-{weight}.ttf").read_bytes()
        font_id = QFontDatabase.addApplicationFontFromData(font_data)
        if font_id < 0:
            raise RuntimeError(f"Cannot load bundled Inter {weight} font")

    # Change only the family: widget styles retain their existing sizes/weights.
    # QTextBrowser uses this same Qt font database, including its HTML Preview.
    font = app.font()
    font.setFamilies(["Inter", "Segoe UI", "sans-serif"])
    app.setFont(font)
    app.setWindowIcon(QIcon(str(ASSETS / "icon" / "yoink.ico")))
    app.setProperty("yoinkConfigured", True)
