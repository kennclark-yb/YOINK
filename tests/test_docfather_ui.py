import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)


def advance(ms=20):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def until(predicate):
    deadline = time.monotonic() + 5
    while not predicate() and time.monotonic() < deadline:
        advance()
    assert predicate(), 'Timed out waiting for discovery'


class DocfatherIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.check = patch('gui.updates.UpdateChecker.check')
        self.check.start()
        self.addCleanup(self.check.stop)
        self.w = MainWindow()
        self.w.show()
        self.w._conversation = {'messages': [{'id': 'a', 'role': 'assistant', 'text': 'Hello'}]}
        self.w._extracted_conversation = self.w._conversation
        self.w._extraction_mode = 'both'
        self.w._parts = ['Hello']
        self.w._markdown = 'Hello'
        self.w._show_results()
        advance(400)

    def tearDown(self):
        self.w._closing = True
        self.w._finish_shutdown()
        self.w.deleteLater()
        advance()

    def test_teaser_preserves_state_and_never_launches_intake(self):
        w = self.w
        before = w.geometry()
        APP.clipboard().setText('Clipboard sentinel')
        w.scratchpad.setPlainText('Session notes')
        w._show_scratchpad_feedback('Existing notification')
        w.docfather_button.click()
        advance(300)
        self.assertFalse(hasattr(w, '_show_docfather'))
        self.assertEqual(w.docfather_button.text(), w.docfather_button.CLICK)
        self.assertAlmostEqual(w.docfather_button.portalFill, 1.0, places=2)
        self.assertEqual(w.scratchpad_feedback.text(), 'Existing notification')
        self.assertEqual(w.geometry(), before)
        self.assertEqual(w.scratchpad.toPlainText(), 'Session notes')
        self.assertEqual(APP.clipboard().text(), 'Clipboard sentinel')

    def test_wave_boundaries_and_opposing_motion(self):
        b = self.w.docfather_button
        profiles = []
        for phase in (0, .5, 2, 7, 19):
            b._phase = phase
            values = [b.HOVER_FILL + b._wave_height(i / 400) for i in range(401)]
            self.assertGreaterEqual(min(values), .5)
            self.assertLessEqual(max(values), .75)
            profiles.append(values)
        self.assertGreater(max(abs(a-b) for a,b in zip(profiles[0], profiles[2])), .02)
        self.assertLess(min(min(v) for v in profiles), .53)
        self.assertGreater(max(max(v) for v in profiles), .72)
        # The new profile at phase 1 matches the prior currents at phase 2.75.
        import math
        b._phase = 1.0
        old_at_faster_phase = lambda x: (.075 * math.sin(2 * math.pi * (1.3*x - .115*2.75))
                                        + .05 * math.sin(2 * math.pi * (2.4*x + .073*2.75 + .18)))
        for x in (0, .2, .5, .9, 1):
            self.assertAlmostEqual(b._wave_height(x), old_at_faster_phase(x))

    def test_hover_exit_keyboard_hold_repeat_and_disable(self):
        from PySide6.QtCore import QEvent
        b = self.w.docfather_button
        self.assertEqual(b.accessibleName(), 'CONSULT THE DOCFATHER')
        self.assertIn('coming soon', b.accessibleDescription().lower())
        QApplication.sendEvent(b, QEvent(QEvent.Type.Leave)); advance(300)
        self.assertEqual(b.text(), b.NORMAL)
        self.assertAlmostEqual(b.portalFill, 0.0, places=2)
        QApplication.sendEvent(b, QEvent(QEvent.Type.Enter)); advance(300)
        self.assertEqual(b.text(), 'STATE YOUR CASE.')
        self.assertAlmostEqual(b.portalFill, .625, places=2)
        b.setFocus(); QTest.keyClick(b, Qt.Key.Key_Space)
        self.assertEqual(b.text(), b.CLICK)
        QApplication.sendEvent(b, QEvent(QEvent.Type.Leave))
        advance(900); b.click(); advance(900)
        self.assertEqual(b.text(), b.CLICK)
        advance(950)
        self.assertEqual(b.text(), b.NORMAL)
        advance(300); self.assertAlmostEqual(b.portalFill, 0.0, places=2)
        QApplication.sendEvent(b, QEvent(QEvent.Type.Enter))
        b.click(); b.setEnabled(False)
        self.assertFalse(b._wave_timer.isActive())
        self.assertFalse(b._hold_timer.isActive())
        self.assertEqual(b.text(), b.NORMAL)
        b.setEnabled(True)

    def test_wave_lifecycle_and_reduced_motion(self):
        from PySide6.QtCore import QEvent
        b = self.w.docfather_button
        self.w.activateWindow(); advance(50)
        QApplication.sendEvent(b, QEvent(QEvent.Type.Enter)); advance(100)
        if self.w.isActiveWindow() and not b._reduced_motion():
            self.assertTrue(b._wave_timer.isActive())
            before = b._phase; advance(100); self.assertGreater(b._phase, before)
            QApplication.sendEvent(self.w, QEvent(QEvent.Type.WindowDeactivate))
            self.assertFalse(b._wave_timer.isActive())
            QApplication.sendEvent(self.w, QEvent(QEvent.Type.WindowActivate)); advance(30)
        QApplication.sendEvent(b, QEvent(QEvent.Type.Leave))
        self.assertFalse(b._wave_timer.isActive())
        with patch.dict(os.environ, {'YOINK_REDUCED_MOTION': '1'}):
            QApplication.sendEvent(b, QEvent(QEvent.Type.Enter))
            self.assertEqual(b.portalFill, .625)
            self.assertFalse(b._wave_timer.isActive())
            b.click(); self.assertEqual(b.portalFill, 1.0)
            self.assertEqual(b.text(), b.CLICK)
            b.hide()
            self.assertFalse(b._hold_timer.isActive())
            self.assertEqual(b.text(), b.NORMAL)
            b.show()

    def test_copy_all_uses_primary_style_without_processing(self):
        from gui.progress_button import ProgressButton
        w = self.w
        self.assertIsInstance(w.copy_all_button, ProgressButton)
        self.assertEqual(w.copy_all_button.height(), 32)
        self.assertEqual(w.copy_all_button.text(), '[ COPY ALL ]')
        self.assertEqual(w.copy_all_button.font(), w.preview_button.font())
        for button in (w.preview_button, w.context_picker_button, w.scratchpad_button, w.scratchpad_undo_button):
            self.assertEqual(button.font(), w.preview_button.font())
            self.assertTrue(button.text().startswith('[ ') and button.text().endswith(' ]'))
        self.assertNotIn(w.copy_all_button, w._action_interactions.entries)
        w.copy_all_button.click()
        self.assertEqual(APP.clipboard().text(), 'Hello')
        self.assertEqual(w.copy_all_button.text(), 'COPIED')
        self.assertFalse(w.copy_all_button._processing)
        advance(1100)
        self.assertEqual(w.copy_all_button.text(), '[ COPY ALL ]')
        self.assertLess(w.copy_all_button.mapTo(w.results_panel, w.copy_all_button.rect().center()).y(),
                        w.docfather_button.mapTo(w.results_panel, w.docfather_button.rect().center()).y())


if __name__ == '__main__':
    unittest.main()
