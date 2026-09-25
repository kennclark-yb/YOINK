"""Focused, offline checks of session notes and release checks."""
import unittest
from unittest.mock import Mock, patch

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtTest import QTest
from PySide6.QtNetwork import QNetworkReply

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
        for tag in ('v0.9.0', 'v1.0.0', 'v1.0.0+build'):
            self.assertIsNone(newer_release({'tag_name': tag}))
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
        self.assertEqual(w.scratchpad.toPlainText(), '')
        until(lambda: not w.isVisible())

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
