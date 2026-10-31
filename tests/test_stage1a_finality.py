"""Final Stage 1A Unicode, phrase dwell, controls and frame stability checks."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPushButton
from test_phase2a import APP, advance, EXTRACTION
from gui.main_window import MainWindow
from gui.progress_button import ProgressButton
from gui.scratchpad import ScratchpadEdit


class UnicodeTests(unittest.TestCase):
    def test_each_unicode_case_and_repeated_source_insertions(self):
        for text in ("NBSP: a\u00a0b", "a\u2028b", "a\u2029b", "😀e\u0301👩‍💻",
                     "a\r\nb\rc\n\nend", "\u2029", "", "tail\r\n"):
            with self.subTest(text=ascii(text)):
                e = ScratchpadEdit()
                e.setPlainText("note\u00a0\u2028\n")
                cursor = QTextCursor(e.document())
                cursor.movePosition(QTextCursor.MoveOperation.End)
                e.insert_exact(cursor, text)
                e.insert_exact(cursor, text)
                self.assertEqual(e.exact_text(), "note\u00a0\u2028\n" + text + text)
                e.deleteLater()

    def test_selected_editor_copy_uses_the_same_exact_break_mapping(self):
        e = ScratchpadEdit()
        c = QTextCursor(e.document())
        c.insertText("note 😀\u00a0\n")
        start = c.position()
        text = "😀e\u0301\u00a0x\r\ny\u2028z\u2029end"
        e.insert_exact(c, text)
        c.setPosition(start, QTextCursor.MoveMode.KeepAnchor)
        e.setTextCursor(c)
        e.copy()
        self.assertEqual(APP.clipboard().text(), text)
        self.assertEqual(e.exact_text(), "note 😀\u00a0\n" + text)
        e.deleteLater()

    def test_unverified_source_range_fails_closed(self):
        e = ScratchpadEdit()
        c = QTextCursor(e.document())
        c.insertText("manual\u00a0\u2028")
        reached = []
        e.fidelityBoundaryReached.connect(lambda: reached.append(True))
        # Simulate a Qt insertion conversion outside the supported break map.
        with patch("gui.scratchpad.re.sub", return_value="unexpected conversion"):
            e.insert_exact(c, "source\u2029end")
        self.assertTrue(reached)
        self.assertEqual(e.exact_text(), "manual\u00a0\u2028source\nend")
        self.assertEqual(e._source_breaks, {})
        e.deleteLater()


class PhraseTests(unittest.TestCase):
    def test_dwell_repeated_updates_rotation_completion_and_restart(self):
        b = ProgressButton()
        b._loading_messages = ["first", "second"]
        with patch("gui.progress_button.random.choice", side_effect=lambda choices: choices[0]):
            b.set_processing(True)
            self.assertEqual(b._loading_text_timer.interval(), 2600)
            self.assertEqual(b._loading_text_timer.timerType(), Qt.TimerType.PreciseTimer)
            first = b.text()
            advance(1450)
            b.set_processing(True)
            b.set_progress("fetching", 40)
            self.assertEqual(b.text(), first)
            self.assertLess(b._loading_text_timer.remainingTime(), 1500)
            advance(800)
            self.assertEqual(b.text(), first)
            advance(450)
            self.assertNotEqual(b.text(), first)
            self.assertTrue(b._shimmer_timer.isActive())
            b.set_progress("done", 100)
            self.assertEqual(b.text(), "[ extraction successful ]")
            self.assertFalse(b._loading_text_timer.isActive())
            b.set_processing(False)
            self.assertEqual(b.text(), "EXTRACT")
            b.set_processing(True)
            self.assertTrue(b._loading_text_timer.isActive())
            b.set_processing(False)
        b.deleteLater()


class FinalUITests(unittest.TestCase):
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

    def test_slim_controls_names_and_drag(self):
        w = self.w
        bar = w.title_bar
        self.assertEqual(bar.height(), 24)
        self.assertEqual(bar.findChildren(QPushButton), [bar.minimize_button, bar.close_button])
        for button, name in ((bar.minimize_button, "Minimize"), (bar.close_button, "Close")):
            self.assertEqual(button.accessibleName(), name)
            self.assertTrue(bar.rect().contains(button.geometry()))
            self.assertTrue(button.focusPolicy() & Qt.FocusPolicy.TabFocus)
        with patch.object(w, "windowHandle") as handle:
            from PySide6.QtGui import QMouseEvent
            from PySide6.QtCore import QEvent, QPointF
            event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(30, 10), QPointF(30, 10),
                                Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                                Qt.KeyboardModifier.NoModifier)
            bar.mousePressEvent(event)
            handle.return_value.startSystemMove.assert_called_once()
        with patch.object(w, "showMaximized") as maximize:
            from PySide6.QtTest import QTest
            QTest.mouseDClick(bar, Qt.MouseButton.LeftButton)
            maximize.assert_not_called()
        # Close lifecycle is covered by the existing shutdown tests.
        bar.minimize_button.click()
        self.assertTrue(w.isMinimized())
        w.showNormal()

    def test_shrink_keeps_card_size_and_vertical_anchor_stable(self):
        w = self.w
        original = w.size()
        w._results_work_area = lambda: QRect(-2000, -1500, 6000, 4000)
        w.move(350, 200)
        w._conversation = EXTRACTION["conversation"]
        w._extracted_conversation = w._conversation
        w._extraction_mode = "assistant"
        w._parts = ["Synthetic"] * 12
        w._markdown = "Synthetic"
        w._show_results()
        advance(400)
        self.assertEqual(w.content_layout.spacing(), 16)
        w._reset_results_session()
        animation = w._results_animation
        self.assertEqual(animation.duration(), 300)
        animation.pause()
        frames = []
        for t in range(0, 300, 3):
            animation.setCurrentTime(t)
            p = w.card.mapToGlobal(w.card.rect().topLeft())
            frames.append((w.card.width(), w.card.height(), p.y(), w.width(), w.height()))
        self.assertEqual(len({f[:3] for f in frames}), 1)
        self.assertTrue(all(b[3] <= a[3] and b[4] <= a[4] for a, b in zip(frames, frames[1:])))
        animation.resume()
        advance(50)
        self.assertEqual(w.size(), original)
        self.assertTrue(w.results_panel.isHidden())
