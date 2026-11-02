"""Finite append entrance, stable layout, update and cancellation contracts."""
import os
import unittest
from unittest.mock import patch
from PySide6.QtCore import QPoint, QRect, QAbstractAnimation
from test_phase2a import advance, EXTRACTION
from gui.main_window import MainWindow

class AppendEntranceTests(unittest.TestCase):
    def setUp(self):
        self.check = patch('gui.updates.UpdateChecker.check'); self.check.start()
        self.env = patch.dict(os.environ, {'YOINK_REDUCED_MOTION': '0'}); self.env.start()
        self.w = MainWindow(); self.w.show(); advance(30)
        w = self.w
        w._results_work_area = lambda: QRect(0, 0, 1920, 1032)
        w._conversation = EXTRACTION['conversation']; w._extracted_conversation = w._conversation
        w._extraction_mode = 'both'; w._parts = ['First intact part', 'Second intact part']; w._markdown = 'First'
        w._show_results(); advance(420)

    def tearDown(self):
        w = self.w; w._clear_scratchpad_append_state()
        w._closing = True; w._finish_shutdown(); w.deleteLater(); advance(20)
        self.env.stop(); self.check.stop()

    def test_first_entrance_overshoot_and_settle_without_layout_motion(self):
        w = self.w; label = w.scratchpad_feedback
        stats = [x.geometry() for x in w.results_stat_headings]
        parts = w.results_container.geometry()
        w._append_to_scratchpad(1, w._parts[0]); a = w._feedback_slot.entrance
        self.assertEqual(label.y(), 10)
        a.pause(); a.setCurrentTime(45)
        self.assertGreaterEqual(label.y(), 0); self.assertLess(label.y(), 10)
        a.setCurrentTime(90); self.assertLess(label.y(), 0)
        a.setCurrentTime(220); self.assertEqual(label.y(), 0)
        self.assertEqual(stats, [x.geometry() for x in w.results_stat_headings])
        self.assertEqual(parts, w.results_container.geometry())
        self.assertEqual(w._scratchpad_copy_text().count('First intact part'), 1)

    def test_repeated_success_during_entrance_and_fade_updates_settled(self):
        w = self.w; w._append_to_scratchpad(1, w._parts[0])
        a = w._feedback_slot.entrance; a.pause(); a.setCurrentTime(60)
        w._append_to_scratchpad(2, w._parts[1])
        self.assertEqual(a.state(), QAbstractAnimation.State.Stopped)
        self.assertEqual(w.scratchpad_feedback.y(), 0)
        self.assertIn('Part 2 added', w.scratchpad_feedback.text())
        self.assertTrue(w._feedback_timer.isActive())
        w._fade_scratchpad_feedback(); w._feedback_animation.pause(); w._feedback_animation.setCurrentTime(125)
        self.assertGreater(w._feedback_opacity.opacity(), 0)
        w._append_to_scratchpad(3, 'Third')
        self.assertEqual(a.state(), QAbstractAnimation.State.Stopped)
        self.assertEqual(w._feedback_opacity.opacity(), 1)
        self.assertEqual(w.scratchpad_feedback.y(), 0)
        w._undo_scratchpad_append(); self.assertIn('undone', w.scratchpad_feedback.text())
        self.assertNotIn('Third', w._scratchpad_copy_text())

    def test_duplicate_feedback_and_reset_cancel_both_animations(self):
        w = self.w
        with patch('gui.main_window.time.monotonic', side_effect=[10., 10.1]):
            w._append_to_scratchpad(1, w._parts[0]); before = w._scratchpad_copy_text()
            w._append_to_scratchpad(1, w._parts[0])
        self.assertEqual(w._scratchpad_copy_text(), before)
        self.assertIn('Already added', w.scratchpad_feedback.text())
        self.assertEqual(w.scratchpad_feedback.y(), 0)
        w._reset_results_session()
        self.assertEqual(w._feedback_slot.entrance.state(), QAbstractAnimation.State.Stopped)
        self.assertEqual(w._feedback_animation.state(), QAbstractAnimation.State.Stopped)
        self.assertFalse(w._feedback_timer.isActive())
        self.assertEqual(w._feedback_opacity.opacity(), 0)

    def test_natural_completion_and_next_dismissed_entrance(self):
        w = self.w; w._append_to_scratchpad(1, w._parts[0]); advance(270)
        self.assertEqual(w._feedback_slot.entrance.state(), QAbstractAnimation.State.Stopped)
        self.assertEqual(w.scratchpad_feedback.y(), 0)
        w._fade_scratchpad_feedback(); advance(290)
        self.assertEqual(w._feedback_opacity.opacity(), 0)
        w._append_to_scratchpad(2, w._parts[1]); self.assertEqual(w.scratchpad_feedback.y(), 10)
        w.close()
        self.assertEqual(w._feedback_slot.entrance.state(), QAbstractAnimation.State.Stopped)
        self.assertFalse(w._feedback_timer.isActive())

    def test_reduced_motion_stays_settled(self):
        w = self.w
        with patch.dict(os.environ, {'YOINK_REDUCED_MOTION': '1'}):
            w._append_to_scratchpad(1, w._parts[0])
        self.assertEqual(w.scratchpad_feedback.y(), 0)
        self.assertEqual(w._feedback_slot.entrance.state(), QAbstractAnimation.State.Stopped)
