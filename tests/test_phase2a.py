"""Offscreen interaction regressions; no network or real shared chats required."""
import os
import time
import sys
import unittest
from contextlib import chdir
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6.QtWidgets import QApplication, QPushButton

from extract import ExtractionError
from gui.main_window import MainWindow
from gui.shutdown_screen import ShutdownScreen


APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)
URL = "https://chatgpt.com/share/phase2a-test"
CONVERSATION = {
    "platform": "chatgpt", "title": "Interaction check", "url": URL,
    "messages": [{"id": "1", "role": "assistant", "text": "Hello"}],
}
EXTRACTION = {"full_conversation": CONVERSATION, "conversation": CONVERSATION}


def advance(milliseconds):
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()


def until(predicate, timeout=3000):
    deadline = time.monotonic() + timeout / 1000
    while not predicate() and time.monotonic() < deadline:
        advance(10)
    if not predicate():
        raise AssertionError("Timed out waiting for Qt state")


class InteractionTests(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        APP.processEvents()
        self.window.url_input.clearFocus()

    def tearDown(self):
        w = self.window
        until(lambda: not w._preload_threads)
        if hasattr(w, "_extraction_threads"):
            until(lambda: not w._extraction_threads)
        w._close_after_results = False
        w._closing = True
        w._finish_shutdown()
        w.deleteLater()
        QTest.qWait(20)

    def prepare_url(self):
        self.window.url_input.setText(URL)
        self.window._validate_url()

    def test_pending_preload_failure_becomes_retry(self):
        def fail(*args):
            time.sleep(0.04)
            raise ExtractionError("Test page failed to load")

        w = self.window
        self.prepare_url()
        with patch("gui.preload_worker.extract_conversation", side_effect=fail):
            w._start_preload(URL)
            w._extract_conversation()
            self.assertTrue(w._waiting_for_preload)
            until(lambda: not w._preload_threads)
        self.assertFalse(w._waiting_for_preload)
        self.assertFalse(w.extract_button._processing)
        self.assertTrue(w.url_input.isEnabled())
        self.assertEqual(w.extract_button.text(), "RETRY")
        self.assertIn("failed to load", w.extraction_error.text())
        with patch("gui.extraction_worker.extract_conversation", return_value=EXTRACTION) as fallback:
            w._extract_conversation()
            until(lambda: not w.results_panel.isHidden())
            QTest.qWait(400)
            fallback.assert_called_once_with(URL, "assistant")

    def test_no_preload_uses_existing_fallback(self):
        self.prepare_url()
        with patch("gui.extraction_worker.extract_conversation", return_value=EXTRACTION) as fallback:
            self.window._extract_conversation()
            until(lambda: not self.window.results_panel.isHidden())
            QTest.qWait(400)
            fallback.assert_called_once()

    def test_preload_cannot_restart_extraction_after_close(self):
        def delayed(*args):
            time.sleep(0.08)
            return EXTRACTION

        w = self.window
        self.prepare_url()
        with patch("gui.preload_worker.extract_conversation", side_effect=delayed):
            w._start_preload(URL)
            w._extract_conversation()
            with patch.object(w, "_start_extraction") as restart:
                w.close()
                until(lambda: not w._preload_threads)
                restart.assert_not_called()

    def test_shutdown_waits_for_extraction_and_suppresses_late_results(self):
        def delayed(*args):
            time.sleep(1.5)
            return EXTRACTION

        w = self.window
        self.prepare_url()
        finished = []
        with patch("gui.extraction_worker.extract_conversation", side_effect=delayed):
            w._extract_conversation()
            w._extraction_thread.finished.connect(lambda: finished.append(True))
            with patch.object(w, "_finish_shutdown") as close, patch.object(w, "_show_results") as results:
                w.close()
                advance(1250)
                premature_close = close.called
                until(lambda: finished)
                self.assertFalse(premature_close, "Shutdown tried to finish while extraction was running")
                results.assert_not_called()
                close.assert_called_once()

    def test_close_with_only_preload_waits_for_thread(self):
        def delayed(*args):
            time.sleep(0.1)
            return EXTRACTION

        w = self.window
        self.prepare_url()
        with patch("gui.preload_worker.extract_conversation", side_effect=delayed):
            w._start_preload(URL)
            w.close()
            self.assertTrue(w.isVisible())
            self.assertTrue(w._closing)
            self.assertIsNotNone(w._shutdown_screen)
            w.close()
            self.assertTrue(w.isVisible())
            until(lambda: not w._preload_threads)
        self.assertFalse(w.isVisible())

    def test_close_results_retreats_before_shutdown(self):
        w = self.window
        self.prepare_url()
        with patch("gui.extraction_worker.extract_conversation", return_value=EXTRACTION):
            w._extract_conversation()
            until(lambda: not w.results_panel.isHidden())
            advance(400)
        center = w.geometry().center()
        w.close()
        animation = w._results_animation
        w.close()
        self.assertIs(animation, w._results_animation)
        self.assertIsNone(w._shutdown_screen)
        advance(100)
        self.assertIsNone(w._shutdown_screen)
        advance(250)
        self.assertTrue(w.results_panel.isHidden())
        self.assertEqual(w.size(), w._startup_size)
        self.assertEqual(w.geometry().center(), center)
        self.assertIsNotNone(w._shutdown_screen)
        until(lambda: not w.isVisible())

    def test_button_disabled_focus_and_keyboard_press_states(self):
        button = self.window.extract_button
        disabled_image = button.grab().toImage()
        self.assertEqual(button.cursor().shape(), Qt.CursorShape.ArrowCursor)
        button.setEnabled(True)
        button.clearFocus()
        enabled_image = button.grab().toImage()
        self.assertNotEqual(disabled_image, enabled_image)
        button.setFocus()
        focus_image = button.grab().toImage()
        self.assertNotEqual(enabled_image, focus_image)
        QTest.keyPress(button, Qt.Key.Key_Space)
        self.assertTrue(button._pressed)
        self.assertNotEqual(focus_image, button.grab().toImage())
        QTest.keyRelease(button, Qt.Key.Key_Space)
        self.assertFalse(button._pressed)
        button.set_processing(True)
        self.assertFalse(button.isEnabled())
        self.assertTrue(button._fake_progress_timer.isActive())
        self.assertTrue(button._loading_text_timer.isActive())
        self.assertEqual(button._loading_text_timer.interval(), 1400)
        self.assertEqual(button._animation.duration(), 250)
        button.set_processing(False)

    def show_sample_results(self):
        w = self.window
        self.prepare_url()
        w._preloaded_extraction = EXTRACTION
        w._preloaded_version = w._preload_version
        w._extract_conversation()
        until(lambda: not w.results_panel.isHidden())
        advance(400)

    def test_reset_keeps_content_until_retreat_then_starts_fresh(self):
        w = self.window
        self.show_sample_results()
        old_version = w._preload_version
        original_count = w.results_container_layout.count()
        w._reset_results_session()
        self.assertEqual(w.results_container_layout.count(), original_count)
        self.assertFalse(w.copy_all_button.isEnabled())
        self.assertFalse(w.preview_button.isEnabled())
        self.assertFalse(w.extract_another_button.isEnabled())
        self.assertIsNotNone(w._conversation)
        advance(350)
        self.assertEqual(w.url_input.text(), "")
        self.assertTrue(w.url_input.hasFocus())
        self.assertIsNone(w._conversation)
        self.assertIsNone(w._preloaded_extraction)
        self.assertGreater(w._preload_version, old_version)
        w._preload_finished(old_version, EXTRACTION)
        self.assertIsNone(w._preloaded_extraction)
        self.assertFalse(w.extract_button.isEnabled())
        self.assertTrue(w.results_panel.isHidden())

    def test_repeated_copy_extends_confirmation(self):
        w = self.window
        self.show_sample_results()
        part = w.results_container.findChild(QPushButton)
        w.copy_all_button.click()
        part.click()
        advance(450)
        w.copy_all_button.click()
        part.click()
        advance(350)
        self.assertEqual(w.copy_all_button.text(), "COPIED")
        self.assertEqual(part.text(), "✔")
        self.assertEqual(APP.clipboard().text(), w._parts[0])
        advance(750)
        self.assertEqual(w.copy_all_button.text(), "COPY ALL")
        self.assertEqual(part.text(), "⧉")

    def test_copy_then_reset_does_not_call_deleted_button(self):
        w = self.window
        self.show_sample_results()
        errors = []
        with patch.object(sys, "excepthook", side_effect=lambda *args: errors.append(args)):
            w.results_container.findChild(QPushButton).click()
            w._reset_results_session()
            advance(1150)
        self.assertEqual(errors, [])

    def test_settings_are_committed_while_waiting_for_preload(self):
        def delayed(*args):
            time.sleep(0.08)
            return EXTRACTION

        w = self.window
        self.prepare_url()
        w.both_radio.setChecked(True)
        w.split_value.setText("1234")
        w.split_selector._show_popup()
        with patch("gui.preload_worker.extract_conversation", side_effect=delayed):
            w._start_preload(URL)
            w._extract_conversation()
            self.assertEqual(w._operation_settings, (URL, "both", "Character Limit", "1234"))
            self.assertTrue(w._waiting_for_preload)
            self.assertTrue(w.split_selector.popup.isHidden())
            for control in (w.url_input, w.ai_radio, w.user_radio, w.both_radio, w.split_selector, w.split_value):
                self.assertFalse(control.isEnabled())
            until(lambda: not w.results_panel.isHidden())
            advance(400)
        self.assertEqual(w._extraction_mode, "both")
        self.assertFalse(w.split_value.isEnabled())
        w._reset_results_session()
        advance(350)
        for control in (w.url_input, w.ai_radio, w.user_radio, w.both_radio, w.split_selector, w.split_value):
            self.assertTrue(control.isEnabled())

    def test_extraction_error_restores_settings(self):
        self.prepare_url()
        w = self.window
        with patch("gui.extraction_worker.extract_conversation", side_effect=ExtractionError("Failed")):
            w._extract_conversation()
            self.assertFalse(w.split_value.isEnabled())
            until(lambda: not w._extraction_threads)
        self.assertIsNone(w._operation_settings)
        self.assertEqual(w.extract_button.text(), "RETRY")
        for control in (w.url_input, w.ai_radio, w.user_radio, w.both_radio, w.split_selector, w.split_value):
            self.assertTrue(control.isEnabled())

    def test_url_edits_clear_stale_feedback_and_eligibility(self):
        w = self.window
        self.prepare_url()
        self.assertTrue(w.extract_button.isEnabled())
        w.url_input.setText("broken")
        self.assertFalse(w.extract_button.isEnabled())
        self.assertEqual(w.url_error.text().strip(), "")
        w._validate_url()
        self.assertEqual(w.url_error.text(), "Invalid URL.")
        w.url_input.setText("https://")
        self.assertEqual(w.url_error.text().strip(), "")
        self.assertIsNone(w.url_input.property("urlValid"))
        w.url_input.clear()
        w._validate_url()
        self.assertIsNone(w.url_input.property("urlValid"))
        self.assertFalse(w.extract_button.isEnabled())

    def test_url_formats_keep_codex_share_unsupported(self):
        w = self.window
        for url in ("https://chatgpt.com/s/cx_test", "https://example.com/share/test"):
            w.url_input.setText(url)
            w._validate_url()
            self.assertFalse(w.url_input.property("urlValid"))
            self.assertIn("Unsupported platform", w.url_error.text())
        with patch.object(w, "_start_preload") as preload:
            w.url_input.setText(URL)
            w.url_input.editingFinished.emit()
            self.assertTrue(w.url_input.property("urlValid"))
            preload.assert_called_once_with(URL)

    def test_split_errors_are_caught_before_loading(self):
        w = self.window
        self.prepare_url()
        w.split_selector._select("Number of Parts")
        with patch.object(w, "_start_extraction") as start:
            for value in ("", "0", "-1", "1000000", "invalid"):
                w.split_value.setText(value)
                w._extract_conversation()
                start.assert_not_called()
                self.assertFalse(w.extract_button._processing)
                self.assertIsNone(w._operation_settings)
                self.assertTrue(w.split_value.hasFocus())
                self.assertTrue(w.extraction_error.isVisible())
                self.assertFalse(w.extract_button._recovery)

    def test_empty_character_limit_keeps_default(self):
        w = self.window
        self.prepare_url()
        self.assertEqual(w.split_value.text(), "")
        with patch("gui.extraction_worker.extract_conversation", return_value=EXTRACTION), patch(
            "gui.extraction_worker.split_parts", return_value=["Hello"]
        ) as split:
            w._extract_conversation()
            until(lambda: not w._extraction_threads)
            split.assert_called_once_with(CONVERSATION, max_chars=9000)
        advance(400)

    def test_split_error_clears_on_correction_and_worker_still_validates(self):
        w = self.window
        self.prepare_url()
        w.split_selector._select("Number of Parts")
        w._extract_conversation()
        self.assertFalse(w.split_value.property("splitValid"))
        self.assertTrue(w.extraction_error.property("inputError"))
        w.split_value.setText("2")
        self.assertIsNone(w.split_value.property("splitValid"))
        self.assertFalse(w.extraction_error.isVisible())
        self.assertIsNone(w.extraction_error.property("inputError"))
        with patch("gui.extraction_worker.extract_conversation", return_value=EXTRACTION):
            w._extract_conversation()
            until(lambda: not w._extraction_threads)
        # Two parts cannot be made from one message: worker safeguard remains.
        self.assertIn("number of messages", w.extraction_error.text())
        self.assertEqual(w.extract_button.text(), "RETRY")
        self.assertFalse(w.extraction_error.property("inputError"))

    def test_invalid_character_limit_is_not_treated_as_empty_default(self):
        w = self.window
        self.prepare_url()
        with patch.object(w, "_start_extraction") as start:
            for value in ("0", "-10", "1000000", "invalid"):
                w.split_value.setText(value)
                w._extract_conversation()
                self.assertFalse(w.extract_button._processing)
                self.assertFalse(w.extract_button._recovery)
                self.assertTrue(w.split_value.hasFocus())
            start.assert_not_called()
        w.split_value.clear()
        self.assertFalse(w.extraction_error.isVisible())
        self.assertIn("9000", w.split_value.placeholderText())

    def test_hover_reversal_starts_at_current_visual_value(self):
        button = self.window.extract_button
        button.setEnabled(True)
        button.set_hover_progress(0.65)
        button._animate_to(0.0)
        self.assertAlmostEqual(button.get_hover_progress(), 0.65)
        self.assertEqual(button._animation.duration(), 250)
        advance(80)
        current = button.get_hover_progress()
        self.assertLess(current, 0.65)
        button._animate_to(1.0)
        self.assertAlmostEqual(button.get_hover_progress(), current)

    def test_reselecting_split_mode_keeps_numeric_value(self):
        w = self.window
        w.split_value.setText("1234")
        w.split_selector._select("Character Limit")
        self.assertEqual(w.split_value.text(), "1234")
        w.split_selector._select("Number of Parts")
        self.assertEqual(w.split_value.text(), "")
        w.split_selector._show_popup()
        for button in w.split_selector.option_buttons:
            self.assertEqual(button.cursor().shape(), Qt.CursorShape.PointingHandCursor)
        w.split_selector._hide_popup()

    def test_shutdown_asset_loads_from_another_working_directory(self):
        with chdir(Path(__file__).resolve().parent):
            screen = ShutdownScreen()
            try:
                self.assertTrue(screen._movie.isValid())
                self.assertTrue(Path(screen._movie.fileName()).is_absolute())
            finally:
                screen._movie.stop()
                screen.deleteLater()

    def test_retry_during_failed_preload_teardown_does_not_wait_again(self):
        def fail(*args):
            time.sleep(0.04)
            raise ExtractionError("Failed preload")

        w = self.window
        self.prepare_url()
        original_error = w._extraction_error

        def retry_immediately(message):
            original_error(message)
            w._extract_conversation()

        with patch("gui.preload_worker.extract_conversation", side_effect=fail), patch(
            "gui.extraction_worker.extract_conversation", return_value=EXTRACTION
        ) as fallback, patch.object(w, "_extraction_error", side_effect=retry_immediately):
            w._start_preload(URL)
            w._extract_conversation()
            until(lambda: not w._preload_threads)
            until(lambda: not w._extraction_threads)
            self.assertFalse(w._waiting_for_preload)
            fallback.assert_called_once()
        advance(400)

    def test_modes_and_split_settings_reach_existing_worker_unchanged(self):
        w = self.window
        full = {
            **CONVERSATION,
            "messages": [
                {"id": str(index), "role": role, "text": text}
                for index, (role, text) in enumerate([
                    ("user", "First question"), ("assistant", "First answer"),
                    ("user", "Second question"), ("assistant", "Second answer"),
                ])
            ],
        }
        for radio, mode in ((w.ai_radio, "assistant"), (w.user_radio, "user"), (w.both_radio, "both")):
            for split_mode, value in (("Character Limit", "10"), ("Number of Parts", "2")):
                with self.subTest(mode=mode, split=split_mode):
                    self.prepare_url()
                    radio.setChecked(True)
                    w.split_selector._select(split_mode)
                    w.split_value.setText(value)
                    w._preloaded_extraction = {"full_conversation": full}
                    w._preloaded_version = w._preload_version
                    with patch("gui.extraction_worker.extract_conversation") as fallback:
                        w._extract_conversation()
                        until(lambda: not w._extraction_threads)
                        advance(400)
                        fallback.assert_not_called()
                    expected = [m for m in full["messages"] if mode == "both" or m["role"] == mode]
                    self.assertEqual(w._extracted_conversation["messages"], expected)
                    self.assertEqual(w._conversation, full)
                    self.assertEqual(len(w._parts), 2 if split_mode == "Number of Parts" else len(expected))
                    w.copy_all_button.click()
                    self.assertEqual(APP.clipboard().text(), "\n\n".join(w._parts))
                    w._reset_results_session()
                    advance(350)

    def test_geometry_stays_centered_during_repeated_open_and_reset(self):
        w = self.window
        for x, y in ((350, 150), (750, 200), (-650, 80)):
            w.move(x, y)
            APP.processEvents()
            original = w.geometry()
            center = (2 * original.x() + original.width(), 2 * original.y() + original.height())
            self.prepare_url()
            w._preloaded_extraction = EXTRACTION
            w._preloaded_version = w._preload_version
            w._extract_conversation()
            until(lambda: not w.results_panel.isHidden())
            for opening in (True, False):
                if not opening:
                    w._reset_results_session()
                widths = []
                cards = []
                for _ in range(40):
                    advance(10)
                    geometry = w.geometry()
                    self.assertLessEqual(abs(2 * geometry.x() + geometry.width() - center[0]), 1)
                    self.assertLessEqual(abs(2 * geometry.y() + geometry.height() - center[1]), 1)
                    self.assertEqual(w.card.x(), 14)
                    widths.append(geometry.width())
                    cards.append(w.card.width())
                self.assertLessEqual(max(cards) - min(cards), 1)
                self.assertTrue(all(b >= a if opening else b <= a for a, b in zip(widths, widths[1:])))
            self.assertEqual(w.geometry(), original)

    def test_close_during_existing_retreat_does_not_restart_animation(self):
        w = self.window
        self.show_sample_results()
        w._reset_results_session()
        animation = w._results_animation
        advance(80)
        w.close()
        self.assertIs(animation, w._results_animation)
        self.assertIsNone(w._shutdown_screen)
        advance(270)
        self.assertTrue(w._closing)
        self.assertTrue(w.results_panel.isHidden())
        self.assertIsNotNone(w._shutdown_screen)

    def test_late_preload_error_during_shutdown_does_not_show_retry(self):
        def delayed_failure(*args):
            time.sleep(0.08)
            raise ExtractionError("Failed after close")

        w = self.window
        self.prepare_url()
        with patch("gui.preload_worker.extract_conversation", side_effect=delayed_failure):
            w._start_preload(URL)
            w._extract_conversation()
            with patch.object(w, "_extraction_error") as error:
                w.close()
                until(lambda: not w._preload_threads)
                error.assert_not_called()
        self.assertFalse(w.isVisible())


if __name__ == "__main__":
    unittest.main()
