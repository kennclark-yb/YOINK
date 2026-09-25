"""Focused visual/keyboard checks for the small YOINK polish pass."""
import os
from pathlib import Path
import unittest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog, QVBoxLayout

from test_phase2a import APP, advance
from gui.application import configure_application
from gui.preview import PreviewRoleSelector
from gui.update_dialog import UpdateDialog


def capture(widget, name):
    # Optional local QA output, never written to the repository by default.
    directory = os.environ.get('YOINK_POLISH_CAPTURE_DIR')
    if directory:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        widget.grab().save(str(path / name))


class PolishTests(unittest.TestCase):
    def test_segment_mouse_and_keyboard_focus(self):
        configure_application(APP)
        dialog = QDialog()
        dialog.setStyleSheet('QDialog { background: #15161A; }')
        selector = PreviewRoleSelector()
        QVBoxLayout(dialog).addWidget(selector)
        dialog.show()
        dialog.activateWindow()
        advance(20)
        try:
            ai = selector.buttons[1]
            QTest.mouseClick(ai, Qt.MouseButton.LeftButton)
            advance(200)
            self.assertEqual(selector.current_role, 'assistant')
            self.assertFalse(ai.autoDefault())
            self.assertFalse(ai.keyboard_focus)
            capture(dialog, 'preview-mouse.png')
            ai.setFocus(Qt.FocusReason.TabFocusReason)
            QTest.keyClick(ai, Qt.Key.Key_Tab)
            user = selector.buttons[2]
            self.assertTrue(user.hasFocus())
            self.assertTrue(user.keyboard_focus)
            capture(dialog, 'preview-keyboard.png')
            QTest.keyClick(user, Qt.Key.Key_Space)
            advance(200)
            self.assertEqual(selector.current_role, 'user')
            self.assertEqual(selector.pill.geometry(), selector._pill_rect(2))
            QTest.mouseClick(user, Qt.MouseButton.LeftButton)
            self.assertFalse(user.keyboard_focus)
        finally:
            dialog.close()
            dialog.deleteLater()

    def test_update_dialog_layouts(self):
        configure_application(APP)
        parent = QDialog()
        parent.setGeometry(200, 200, 780, 440)
        parent.show()
        try:
            for state, message, actions in (
                ('current', 'YOINK is up to date (v1.0.0).', [('OK', None)]),
                ('failure', "Couldn't check for updates. Check your connection and try Ctrl+U again later.", [('OK', None)]),
                ('newer', 'YOINK v1.1.0 is available.', [('View Release', None), ('Later', None)]),
            ):
                dialog = UpdateDialog(parent, message, actions)
                dialog.show()
                advance(10)
                self.assertFalse(dialog.isModal())
                self.assertIsNone(APP.activeModalWidget())
                self.assertEqual(dialog.frameGeometry().center(), parent.frameGeometry().center())
                self.assertLess(dialog.height(), 240)
                self.assertFalse(dialog.windowIcon().isNull())
                capture(dialog, f'update-{state}.png')
                QTest.keyClick(dialog, Qt.Key.Key_Escape)
                self.assertFalse(dialog.isVisible())
        finally:
            parent.close()
            parent.deleteLater()
