"""Focused, offline checks of session notes and release checks."""
import unittest
from unittest.mock import Mock, patch

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtTest import QTest
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPushButton

from test_phase2a import APP, EXTRACTION, URL, advance, until
from gui.main_window import MainWindow
from gui.updates import UpdateChecker, newer_release, version_key, RELEASES


class VersionTests(unittest.TestCase):
    def test_semver_precedence(self):
        ordered = ['1.0.0-alpha', '1.0.0-alpha.1', '1.0.0-alpha.beta',
                   '1.0.0-beta', '1.0.0-beta.2', '1.0.0-beta.11',
                   '1.0.0-rc.1', '1.0.0', '1.0.1', '1.2.0', '1.10.0', '2.0.0']
        self.assertEqual(sorted(reversed(ordered), key=version_key), ordered)
        self.assertEqual(version_key('v1.0.0+build.12'), version_key('1.0.0'))
        for invalid in ('1.0', '1.01.0', '1.0.0-01', 'garbage', '1.0.0-'):
            with self.assertRaises(ValueError):
                version_key(invalid)

    def test_release_selection_and_official_destination(self):
        for tag in ('v0.9.0', 'v1.0.0', 'v1.1.0', 'v1.1.0+build'):
            self.assertIsNone(newer_release({'tag_name': tag}))
        self.assertEqual(newer_release({'tag_name': 'v1.1.1'}), ('v1.1.1', RELEASES + '/tag/v1.1.1'))
        self.assertIsNone(newer_release({'tag_name': 'v2.0.0-rc.1', 'prerelease': True}))
        self.assertEqual(newer_release({'tag_name': 'v1.10.0', 'html_url': 'https://example.com'}),
                         ('v1.10.0', RELEASES + '/tag/v1.10.0'))


class FakeReply(QObject):
    finished = Signal()

    def __init__(self, body, status=200):
        super().__init__()
        self.body, self.status = body, status
        self.aborted = False

    def error(self):
        return (QNetworkReply.NetworkError.OperationCanceledError if self.aborted
                else QNetworkReply.NetworkError.NoError)

    def attribute(self, key):
        return self.status

    def readAll(self):
        return self.body

    def abort(self):
        self.aborted = True
        self.finished.emit()


class NetworkTests(unittest.TestCase):
    def test_async_completion_failure_timeout_and_manual_adoption(self):
        for body, status, timeout, failed in (
            (b'{"tag_name":"v1.1.0"}', 200, False, False),
            (b'{"tag_name":"v1.0.0"}', 200, False, False),
            (b'{}', 404, False, True),
            (b'{}', 403, False, True),
            (b'not json', 200, False, True),
            (b'[]', 200, False, True),
            (b'{}', 200, True, True),
        ):
            checker = UpdateChecker()
            reply = FakeReply(body, status)
            checker.manager = Mock()
            checker.manager.get.return_value = reply
            received = []
            checker.completed.connect(lambda *args: received.append(args))
            checker.check()
            self.assertEqual(received, [])
            checker.check(manual=True)
            checker.manager.get.assert_called_once()
            if timeout:
                checker.timer.timeout.emit()
                self.assertTrue(reply.aborted)
            else:
                reply.finished.emit()
            self.assertEqual(received[0][0], True)
            self.assertEqual(received[0][2], failed)
            self.assertIsNone(checker.reply)
            self.assertFalse(checker.timer.isActive())
            checker.deleteLater()


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.check_patch = patch.object(UpdateChecker, 'check')
        self.check = self.check_patch.start()
        self.addCleanup(self.check_patch.stop)
        self.window = MainWindow()
        self.window.show()
        advance(10)

    def tearDown(self):
        self.window._closing = True
        self.window._finish_shutdown()
        self.window.deleteLater()
        advance(10)

    def test_scratchpad_copy_hide_reset_and_next_session(self):
        w = self.window
        w.url_input.setText(URL)
        w.split_value.setText('1')
        with patch('gui.extraction_worker.extract_conversation', return_value=EXTRACTION):
            w._extract_conversation()
            until(lambda: not w.results_panel.isHidden())
            advance(400)
        text = 'Selected context\nUnicode: café — ✓\nNext steps'
        w.scratchpad_button.click()
        self.assertTrue(w.scratchpad_dialog.isVisible())
        self.assertFalse(w.results_panel.isAncestorOf(w.scratchpad))
        w.scratchpad.setPlainText(text)
        w.scratchpad_copy.click()
        self.assertEqual(APP.clipboard().text(), text)
        w.scratchpad_dialog.close()
        self.assertFalse(w.scratchpad_dialog.isVisible())
        w.scratchpad_button.click()
        self.assertTrue(w.scratchpad_dialog.isVisible())
        self.assertEqual(w.scratchpad.toPlainText(), text)
        w.results_panel.hide()
        w.results_panel.show()
        self.assertEqual(w.scratchpad.toPlainText(), text)
        w._reset_results_session()
        self.assertFalse(w.scratchpad_dialog.isVisible())
        advance(350)
        self.assertEqual(w.scratchpad.toPlainText(), '')
        w.scratchpad_button.click()
        self.assertFalse(w.scratchpad_dialog.isVisible())
        self.assertEqual(w.scratchpad.toPlainText(), '')
        w.url_input.setText(URL)
        w.split_value.setText('1')
        with patch('gui.extraction_worker.extract_conversation', return_value=EXTRACTION):
            w._extract_conversation()
            until(lambda: not w.results_panel.isHidden())
            advance(400)
        w.scratchpad_button.click()
        self.assertTrue(w.scratchpad_dialog.isVisible())
        self.assertEqual(w.scratchpad.toPlainText(), '')
        w.scratchpad.setPlainText('discard on close')
        w.results_panel.hide()
        w.close()
        until(lambda: not w.isVisible())
        self.assertEqual(w.scratchpad.toPlainText(), '')

    def prepare_parts(self):
        w = self.window
        w.url_input.setText(URL)
        w._conversation = EXTRACTION["conversation"]
        w._parts = ["1. User: café ✓\n2. Assistant: 你好", "3. User: second 🚀"]
        w._build_result_cards()
        w.results_panel.show()
        return w.results_container.findChildren(QPushButton, "AppendPartButton")

    def test_append_fidelity_clipboard_order_and_safe_undo(self):
        w = self.window
        buttons = self.prepare_parts()
        notes = "My notes\nKeep these."
        w.scratchpad.setPlainText(notes)
        APP.clipboard().setText("clipboard stays")
        with patch.object(w.scratchpad_dialog, "show") as show, patch.object(
            w.scratchpad_dialog, "raise_"
        ) as raise_window, patch.object(w.scratchpad_dialog, "activateWindow") as activate, patch.object(
            w.scratchpad_dialog, "close"
        ) as close, patch.object(w.scratchpad, "setFocus") as focus:
            buttons[1].click()
            first = f"{notes}\n\n--- Part 2 · {URL} ---\n{w._parts[1]}"
            self.assertEqual(w.scratchpad.toPlainText(), first)
            buttons[0].click()
            self.assertEqual(w.scratchpad.toPlainText(), first + f"\n\n--- Part 1 · {URL} ---\n{w._parts[0]}")
            self.assertEqual(APP.clipboard().text(), "clipboard stays")
            w.scratchpad_undo_button.click()
            self.assertEqual(w.scratchpad.toPlainText(), first)
            self.assertIn("undone", w.scratchpad_feedback.text())
            for operation in (show, raise_window, activate, close, focus):
                operation.assert_not_called()
        copy = w.results_container.findChildren(QPushButton, "CopyPartButton")[0]
        copy.click()
        self.assertEqual(APP.clipboard().text(), w._parts[0])
        self.assertEqual(w.scratchpad.toPlainText(), first)

    def test_undo_preserves_nonbreaking_spaces_in_notes(self):
        w = self.window
        buttons = self.prepare_parts()
        w.scratchpad.setPlainText("Notes with nonbreaking\u00a0space")
        before = w.scratchpad.document().toRawText()
        buttons[0].click()
        w.scratchpad_undo_button.click()
        self.assertEqual(w.scratchpad.document().toRawText(), before)

    def test_multiple_undo_and_unicode_copy(self):
        w = self.window
        buttons = self.prepare_parts()
        w.scratchpad.setPlainText("notes")
        w._parts = ["A\r\nB\u00a0e\u0301😀\u2028x\u2029y", "second\nline"]
        w._build_result_cards()
        buttons = w.results_container.findChildren(QPushButton, "AppendPartButton")[-2:]
        buttons[0].click()
        buttons[1].click()
        w.scratchpad_copy.click()
        copied = APP.clipboard().text()
        self.assertIn(w._parts[0], copied)
        self.assertIn(w._parts[1], copied)
        w.scratchpad_undo_button.click()
        w.scratchpad_copy.click()
        self.assertIn(w._parts[0], APP.clipboard().text())
        self.assertNotIn(w._parts[1], APP.clipboard().text())
        w.scratchpad_undo_button.click()
        self.assertEqual(w.scratchpad.toPlainText(), "notes")
        self.assertFalse(w.scratchpad_undo_button.isEnabled())

    def test_exact_source_survives_notes_and_edits_within_part(self):
        w = self.window
        self.prepare_parts()
        part = "😀e\u0301\u00a0A\r\nB\u2028C\u2029D\rE\nlast"
        w._parts[0] = part
        w._build_result_cards()
        notes = "before\u00a0😀e\u0301\u2028note\nline"
        w.scratchpad.setPlainText(notes)
        w._append_to_scratchpad(1, part)
        heading = f"{notes}\n\n--- Part 1 · {URL} ---\n"
        self.assertEqual(w._scratchpad_copy_text(), heading + part)
        # Insert notes at the beginning and end, then edit ordinary source text.
        c = QTextCursor(w.scratchpad.document())
        c.insertText("prefix 😀\u00a0\u2028\n")
        c.movePosition(QTextCursor.MoveOperation.End)
        c.insertText("\nmanual tail\u00a0😀")
        c = w.scratchpad.document().find("last")
        c.insertText("edited e\u0301")
        expected = "prefix 😀\u00a0\u2028\n" + heading + part.replace("last", "edited e\u0301") + "\nmanual tail\u00a0😀"
        w.scratchpad_copy.click()
        self.assertEqual(APP.clipboard().text(), expected)
        self.assertFalse(w.scratchpad_undo_button.isEnabled())
        # New appends can still be undone without affecting previous edits.
        w._append_to_scratchpad(2, "next\u2029\u00a0😀")
        self.assertTrue(w._scratchpad_copy_text().endswith("next\u2029\u00a0😀"))
        w._undo_scratchpad_append()
        self.assertEqual(w._scratchpad_copy_text(), expected)
        copy = w.results_container.findChildren(QPushButton, "CopyPartButton")[-2]
        copy.click()
        self.assertEqual(APP.clipboard().text(), part)

    def test_replacing_source_break_has_explicit_local_fallback(self):
        w = self.window
        self.prepare_parts()
        part = "😀a\u2029b\r\nc\u2028d\u00a0e\u0301"
        w._append_to_scratchpad(1, part)
        c = w.scratchpad.document().find("b")
        # Replace just the paragraph break preceding b. Other breaks stay exact.
        c.setPosition(c.selectionStart())
        c.movePosition(QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor)
        c.insertText("\n")
        expected = f"--- Part 1 · {URL} ---\n" + part.replace("\u2029", "\n")
        w.scratchpad_copy.click()
        self.assertEqual(APP.clipboard().text(), expected)
        self.assertIn("including after editor Undo", w.scratchpad_fidelity.text())
        w.scratchpad.undo()
        self.assertEqual(w._scratchpad_copy_text(), expected)
        # A full editor replacement cannot inherit stale source provenance.
        w.scratchpad.setPlainText("manual\u00a0😀\u2028x\u2029y")
        self.assertEqual(w._scratchpad_copy_text(), "manual\u00a0😀\u2028x\ny")
        self.assertFalse(w.scratchpad._source_breaks)

    def test_unverified_append_discloses_editor_fallback(self):
        w = self.window
        self.prepare_parts()
        with patch("gui.scratchpad.re.sub", return_value="unverified"):
            w._append_to_scratchpad(1, "a\u2029b\u00a0😀")
        self.assertEqual(w._scratchpad_copy_text(), f"--- Part 1 · {URL} ---\na\nb\u00a0😀")
        self.assertIn("Source reconstruction unavailable", w.scratchpad_fidelity.text())
        w._undo_scratchpad_append()
        self.assertEqual(w._scratchpad_copy_text(), "")
        w._clear_scratchpad_append_state()
        self.assertEqual(w.scratchpad_fidelity.text(), w.SCRATCHPAD_COPY_NOTE)

    def test_source_copy_is_independent_of_capped_append_undo(self):
        w = self.window
        self.prepare_parts()
        for index in range(1, 103):
            w._append_to_scratchpad(index, f"{index}\u2029x\r\ny\u00a0😀")
        self.assertEqual(len(w._scratchpad_undo), 100)
        self.assertEqual(w._scratchpad_copy_text().count("\u2029"), 102)
        self.assertEqual(w._scratchpad_copy_text().count("\r\n"), 102)
        for _ in range(100):
            w._undo_scratchpad_append()
        self.assertEqual(w._scratchpad_copy_text().count("\u2029"), 2)
        self.assertEqual(w._scratchpad_copy_text().count("\r\n"), 2)

    def test_manual_edits_invalidate_undo_and_duplicate_cooldown(self):
        w = self.window
        buttons = self.prepare_parts()
        with patch("gui.main_window.time.monotonic", side_effect=[10.0, 10.2, 11.0]):
            buttons[0].click()
            once = w.scratchpad.toPlainText()
            buttons[0].click()
            self.assertEqual(w.scratchpad.toPlainText(), once)
            self.assertIn("Wait", w.scratchpad_feedback.text())
            buttons[0].click()
        self.assertEqual(w.scratchpad.toPlainText().count(w._parts[0]), 2)
        w.scratchpad.insertPlainText("manual edit")
        edited = w.scratchpad.toPlainText()
        self.assertFalse(w.scratchpad_undo_button.isEnabled())
        w._undo_scratchpad_append()
        self.assertEqual(w.scratchpad.toPlainText(), edited)
        self.assertIn("edited", w.scratchpad_feedback.text())

    def test_reset_and_shutdown_clear_undo_and_guard_append(self):
        w = self.window
        buttons = self.prepare_parts()
        buttons[0].click()
        self.assertIsNotNone(w._scratchpad_undo)
        w._reset_results_session()
        self.assertFalse(w._scratchpad_undo)
        before = w.scratchpad.toPlainText()
        w._append_to_scratchpad(1, w._parts[0])
        w._undo_scratchpad_append()
        self.assertEqual(w.scratchpad.toPlainText(), before)
        advance(350)
        self.assertEqual(w.scratchpad.toPlainText(), "")
        buttons = self.prepare_parts()
        buttons[0].click()
        w.close()
        self.assertFalse(w._scratchpad_undo)
        before = w.scratchpad.toPlainText()
        w._append_to_scratchpad(1, w._parts[0])
        self.assertEqual(w.scratchpad.toPlainText(), before)
        advance(350)
        self.assertEqual(w.scratchpad.toPlainText(), "")

    def test_update_notifications_and_browser_action(self):
        w = self.window
        self.check.assert_called_once()
        w.activateWindow()
        w.setFocus()
        advance(20)
        QTest.keyClick(w, Qt.Key.Key_U, Qt.KeyboardModifier.ControlModifier)
        self.check.assert_called_with(manual=True)
        for failed in (False, True):
            w._update_checked(False, None, failed)
            self.assertIsNone(w._update_dialog)
            w._update_checked(True, None, failed)
            self.assertIn("Couldn't" if failed else 'up to date', w._update_dialog.message.text())
            self.assertFalse(w._update_dialog.isModal())
            self.assertTrue(w._update_dialog.windowFlags() & Qt.WindowType.FramelessWindowHint)
            self.assertEqual(w._update_dialog.frameGeometry().center(), w.frameGeometry().center())
            self.assertEqual(w._update_dialog.message.alignment(), Qt.AlignmentFlag.AlignCenter)
            button = w._update_dialog.action_buttons[0]
            self.assertLessEqual(abs(button.mapTo(w._update_dialog, button.rect().center()).x()
                                     - w._update_dialog.rect().center().x()), 1)
            w._update_dialog.close()
        release = ('v1.1.0', RELEASES + '/tag/v1.1.0')
        with patch('gui.main_window.QDesktopServices.openUrl') as browser:
            w._update_checked(False, release, False)
            dialog = w._update_dialog
            self.assertFalse(dialog.isModal())
            buttons = dialog.action_buttons
            left = buttons[0].mapTo(dialog, buttons[0].rect().topLeft()).x()
            right = buttons[1].mapTo(dialog, buttons[1].rect().topRight()).x()
            self.assertLessEqual(abs((left + right) / 2 - dialog.rect().center().x()), 1)
            next(b for b in buttons if b.text() == 'Later').click()
            browser.assert_not_called()
            w._update_checked(True, release, False)
            next(b for b in w._update_dialog.action_buttons if b.text() == 'View Release').click()
            self.assertEqual(browser.call_args.args[0].toString(), release[1])
        w._closing = True
        w._update_checked(True, release, False)
        self.assertIsNone(w._update_dialog)
