"""Startup/assets and optional live regression checks, also run in frozen QA."""
import os
import sys
import time
import unittest
from pathlib import Path
from contextlib import chdir
from unittest.mock import patch

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QFontInfo, QRawFont, QTextLayout, QTextCursor
from PySide6.QtWidgets import QApplication, QTextBrowser, QPushButton

from gui.application import configure_application, ASSETS
from formatter import format_markdown, split_parts, split_parts_by_count
from test_phase2a import APP, until, advance

configure_application(APP)


class ReleaseStartupTests(unittest.TestCase):
    def test_frozen_browser_is_inside_bundle(self):
        if not getattr(sys, "frozen", False):
            self.skipTest("Frozen-build assertion")
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser_path = Path(playwright.chromium.executable_path).resolve()
            self.assertTrue(browser_path.is_relative_to(Path(sys._MEIPASS).resolve()))
            self.assertTrue(browser_path.is_file())

    def test_older_preload_cannot_replace_newer_session(self):
        from gui.main_window import MainWindow
        from test_phase2a import EXTRACTION, URL
        w = MainWindow()
        w.show()
        def delayed(url, mode):
            time.sleep(0.15 if url.endswith("old") else 0.03)
            return {**EXTRACTION, "source": url}
        try:
            with patch("gui.preload_worker.extract_conversation", side_effect=delayed):
                w.url_input.setText(URL + "old")
                w._start_preload(URL + "old")
                advance(30)  # Let the first UI event start its worker before the next edit.
                w.url_input.setText(URL + "new")
                w._start_preload(URL + "new")
                until(lambda: not w._preload_threads)
            self.assertEqual(w._preloaded_extraction["source"], URL + "new")
            self.assertEqual(w._preloaded_version, w._preload_version)
        finally:
            until(lambda: not w._preload_threads)
            w._closing = True
            w._finish_shutdown()
            w.deleteLater()

    def test_bundled_fonts_icon_and_html_renderer(self):
        with chdir(ASSETS):
            configure_application(APP)
        self.assertEqual(APP.applicationName(), "YOINK")
        self.assertEqual(QFontInfo(APP.font()).family(), "Inter")
        self.assertFalse(APP.windowIcon().isNull())
        for weight in (QFont.Weight.Normal, QFont.Weight.DemiBold, QFont.Weight.Bold):
            font = QFont("Inter", 12, weight)
            self.assertEqual(QFontInfo(font).family(), "Inter")
            self.assertEqual(QRawFont.fromFont(font).weight(), weight)
        browser = QTextBrowser()
        browser.setHtml('<p style="font-family: Inter, Segoe UI, sans-serif">Inter preview text</p>')
        browser.resize(400, 200)
        browser.show()
        APP.processEvents()
        cursor = QTextCursor(browser.document())
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter)
        layout = QTextLayout("Inter preview text", cursor.charFormat().font())
        layout.beginLayout()
        layout.createLine()
        layout.endLayout()
        runs = layout.glyphRuns()
        self.assertTrue(runs)
        self.assertEqual(runs[0].rawFont().familyName(), "Inter")
        browser.close()


@unittest.skipUnless(os.environ.get("YOINK_LIVE_TEST_URL"), "Opt-in live share test")
class LiveReleaseTests(unittest.TestCase):
    def test_live_preload_modes_splits_preview_copy_reset_and_shutdown(self):
        from gui.main_window import MainWindow
        configure_application(APP)
        w = MainWindow()
        w.show()
        url = os.environ["YOINK_LIVE_TEST_URL"]
        try:
            w.split_selector._select("Character Limit")
            w.url_input.setText(url)
            w.url_input.editingFinished.emit()
            self.assertTrue(w._preload_threads)
            w._extract_conversation()
            self.assertTrue(w._waiting_for_preload)
            self.assertFalse(w.url_input.isEnabled())
            until(lambda: not w.results_panel.isHidden() or w.extract_button._recovery, 90000)
            self.assertFalse(w.extract_button._recovery, w.extraction_error.text())
            until(lambda: not w._preload_threads and not w._extraction_threads)
            advance(450)
            full = w._conversation
            self.assertGreater(len(full["messages"]), 1)
            self.assertFalse(any(m["role"] == "assistant" and (
                not m["text"].strip() or m["text"].strip() == "The output of this plugin was redacted."
            ) for m in full["messages"]))
            w._copy_all_parts()
            self.assertEqual(APP.clipboard().text(), "\n\n".join(w._parts))
            copy = next(b for b in w.results_panel.findChildren(QPushButton) if b.toolTip() == "Copy Part 1")
            copy.click()
            self.assertEqual(APP.clipboard().text(), w._parts[0])
            preview_errors = []
            def inspect_preview():
                dialog = APP.activeModalWidget()
                try:
                    browser = dialog.findChild(QTextBrowser)
                    self.assertTrue(browser.toPlainText())
                    self.assertEqual(QFontInfo(browser.font()).family(), "Inter")
                except Exception as error:
                    preview_errors.append(error)
                finally:
                    dialog.accept()
            QTimer.singleShot(100, inspect_preview)
            w._preview_entire_thread()
            self.assertFalse(preview_errors, str(preview_errors))
            w._reset_results_session()
            advance(450)
            self.assertEqual(w.url_input.text(), "")
            self.assertFalse(w._parts)
            # A second real preload must complete before Extract this time.
            w.url_input.setText(url)
            w.url_input.editingFinished.emit()
            until(lambda: not w._preload_threads, 90000)
            self.assertIsNotNone(w._preloaded_extraction)
            for radio, mode, split, value in (
                (w.user_radio, "user", "Number of Parts", "3"),
                (w.both_radio, "both", "Character Limit", "9000"),
            ):
                radio.setChecked(True)
                w.split_selector._select(split)
                w.split_value.setText(value)
                w._extract_conversation()
                until(lambda: not w._extraction_threads)
                advance(450)
                self.assertFalse(w.extract_button._recovery, w.extraction_error.text())
                expected = {**full, "messages": [m for m in full["messages"] if mode == "both" or m["role"] == mode]}
                parts = split_parts_by_count(expected, 3) if split == "Number of Parts" else split_parts(expected, 9000)
                self.assertEqual(w._parts, parts)
                if mode == "user":
                    w._reset_results_session()
                    advance(450)
                    w.url_input.setText(url)
                    w.url_input.editingFinished.emit()
                    until(lambda: not w._preload_threads, 90000)
            w.close()
            self.assertTrue(w._close_after_results)
            until(lambda: w._shutdown_complete, 5000)
            self.assertFalse(w.isVisible())
        finally:
            until(lambda: not w._preload_threads and not w._extraction_threads, 90000)
            w._closing = True
            w._finish_shutdown()
            w.deleteLater()
