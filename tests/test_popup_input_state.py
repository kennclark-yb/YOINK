"""Regression coverage for the native popup press/drag state boundary."""
import unittest
from unittest.mock import Mock, patch
from PySide6.QtCore import QPoint, QPointF, Qt, QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from test_phase2a import APP, advance
from gui.main_window import MainWindow


class PopupInputStateTests(unittest.TestCase):
    def setUp(self):
        self.update = patch('gui.updates.UpdateChecker.check')
        self.update.start()
        self.w = MainWindow()
        self.w.show()
        advance(20)

    def tearDown(self):
        self.w._closing = True
        self.w._finish_shutdown()
        self.w.deleteLater()
        advance(20)
        self.update.stop()

    def test_selector_open_press_does_not_reach_background_drag_handler(self):
        selector = self.w.split_selector
        handle = Mock()
        with patch.object(self.w, 'windowHandle', return_value=handle):
            QTest.mouseClick(selector, Qt.MouseButton.LeftButton)
            self.assertTrue(selector.popup.isVisible())
            handle.startSystemMove.assert_not_called()
        self.assertIsNone(self.w.background._drag_origin)

    def test_stationary_outside_dismissal_keeps_release_in_qt(self):
        w = self.w
        w.split_selector._show_popup()
        handle = Mock()
        with patch.object(w, 'windowHandle', return_value=handle):
            QTest.mouseClick(w.card, Qt.MouseButton.LeftButton, pos=QPoint(10, 150))
            advance(180)
        self.assertFalse(w.split_selector.popup.isVisible())
        handle.startSystemMove.assert_not_called()
        self.assertIsNone(w.background._drag_origin)

    def test_background_still_starts_native_move_for_an_actual_drag(self):
        background = self.w.background
        handle = Mock()
        with patch.object(self.w, 'windowHandle', return_value=handle):
            QTest.mousePress(background, Qt.MouseButton.LeftButton, pos=QPoint(24, 180))
            handle.startSystemMove.assert_not_called()
            distance = APP.startDragDistance()
            point = QPointF(24 + distance + 2, 180)
            event = QMouseEvent(QEvent.Type.MouseMove, point, point,
                                Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton,
                                Qt.KeyboardModifier.NoModifier)
            APP.sendEvent(background, event)
            handle.startSystemMove.assert_called_once()
            self.assertIsNone(background._drag_origin)
            APP.sendEvent(background, event)
            handle.startSystemMove.assert_called_once()
            QTest.mouseRelease(background, Qt.MouseButton.LeftButton, pos=point.toPoint())

    def test_option_selection_and_keyboard_activation_after_reopen(self):
        selector = self.w.split_selector
        for option in selector.options:
            QTest.mouseClick(selector, Qt.MouseButton.LeftButton)
            button = selector.option_buttons[selector.options.index(option)]
            button.setFocus(Qt.FocusReason.TabFocusReason)
            QTest.keyClick(button, Qt.Key.Key_Space)
            advance(180)
            self.assertEqual(selector.currentText(), option)
            self.assertFalse(selector.popup.isVisible())
