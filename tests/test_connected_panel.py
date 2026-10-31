"""Synthetic native interaction and compact-card regressions."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import QPushButton
from test_phase2a import APP, advance
from gui.main_window import MainWindow


class ConnectedTests(unittest.TestCase):
    def setUp(self):
        self.check = patch("gui.updates.UpdateChecker.check")
        self.check.start()
        self.w = MainWindow()
        self.w.show()
        advance(20)

    def tearDown(self):
        self.w._closing = True
        self.w._finish_shutdown()
        self.w.deleteLater()
        advance(20)
        self.check.stop()

    def test_card_stays_compact_and_actions_use_tab_focus(self):
        w = self.w
        height = w.card.height()
        w.resize(w.width() + 300, w.height() + 180)
        advance(20)
        self.assertEqual(w.card.height(), height)
        for action in (w.preview_button, w.scratchpad_button, w.scratchpad_undo_button,
                       w.copy_all_button, w.extract_another_button):
            self.assertEqual(action.focusPolicy(), Qt.FocusPolicy.TabFocus)

    def test_icon_equivalence_and_hover_reentry(self):
        w = self.w
        w._parts = ["synthetic part"]
        w._build_result_cards()
        arrow = w.results_container.findChild(QPushButton, "AppendPartButton")
        copy = w.results_container.findChild(QPushButton, "CopyPartButton")
        self.assertEqual(arrow.styleSheet(), copy.styleSheet())
        helper = w._action_interactions
        APP.sendEvent(arrow, QEvent(QEvent.Type.Enter))
        advance(120)
        self.assertGreater(helper.entries[arrow][1], 0)
        APP.sendEvent(arrow, QEvent(QEvent.Type.Leave))
        advance(60)
        self.assertGreater(helper.entries[arrow][1], 0)
        APP.sendEvent(arrow, QEvent(QEvent.Type.Enter))
        advance(50)
        self.assertGreater(helper.entries[arrow][1], 0)
        APP.sendEvent(arrow, QEvent(QEvent.Type.Leave))
        advance(400)
        self.assertEqual(helper.entries[arrow][1], 0)
        self.assertEqual(arrow.styleSheet(), helper.entries[arrow][0])

    def test_card_border_fade_restores_original_and_reset_stops_clock(self):
        w = self.w
        w._parts = ["Synthetic"]
        w._build_result_cards()
        card = w.results_container.findChild(QPushButton, "AppendPartButton").parentWidget()
        helper = w._action_interactions
        base = card.styleSheet()
        APP.sendEvent(card, QEvent(QEvent.Type.Enter))
        advance(120)
        self.assertNotEqual(card.styleSheet(), base)
        # Child entry does not terminate the containing card's hover state.
        child = card.findChild(QPushButton, "AppendPartButton")
        APP.sendEvent(child, QEvent(QEvent.Type.Enter))
        self.assertTrue(helper.entries[card][2])
        APP.sendEvent(child, QEvent(QEvent.Type.Leave))
        APP.sendEvent(card, QEvent(QEvent.Type.Leave))
        advance(60)
        self.assertNotEqual(card.styleSheet(), base)
        advance(400)
        self.assertEqual(card.styleSheet(), base)
        helper.clear()
        self.assertFalse(helper.timer.isActive())
