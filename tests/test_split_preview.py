"""Offline regressions for split modes, idle validation and Preview isolation."""
import copy
import re
import unittest
from unittest.mock import patch

from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QTextBrowser

from test_phase2a import APP, URL, advance, until
from formatter import format_markdown, split_parts_by_message_count
from gui.main_window import MainWindow
from gui.preview import PreviewRoleSelector
import gui.preview as preview


FULL = {
    'platform': 'chatgpt', 'title': 'Example', 'url': URL,
    'messages': [{'id': str(i), 'role': 'user' if i % 2 else 'assistant',
                  'text': f'Unique message {i}\n\n**Markdown**'} for i in range(1, 11)],
}


class MessageCountTests(unittest.TestCase):
    def test_boundaries_and_numbering(self):
        for size, counts in ((2, [2]*5), (3, [3, 3, 3, 1]), (1, [1]*10), (20, [10])):
            with self.subTest(size=size):
                parts = split_parts_by_message_count(FULL, size)
                self.assertEqual([len(re.findall(r'### \[msg ', p)) for p in parts], counts)
                self.assertEqual('\n\n---\n\n'.join(parts), format_markdown(FULL))
        self.assertEqual(split_parts_by_message_count({'messages': []}, 3), [])
        for invalid in (0, -1, 1.5, '3', True, None):
            with self.assertRaises(ValueError):
                split_parts_by_message_count(FULL, invalid)


class FormPreviewTests(unittest.TestCase):
    def setUp(self):
        update = patch('gui.updates.UpdateChecker.check')
        update.start()
        self.addCleanup(update.stop)
        self.w = MainWindow()
        self.w.show()
        advance(10)

    def tearDown(self):
        until(lambda: not self.w._extraction_threads and not self.w._preload_threads)
        self.w._stop_input_shake()
        self.w._closing = True
        self.w._finish_shutdown()
        self.w.deleteLater()
        advance(10)

    def test_defaults_idle_validation_shake_and_valid_start(self):
        w = self.w
        self.assertEqual(w.split_selector.currentText(), 'Number of Parts')
        self.assertEqual(w.split_value.text(), '')
        self.assertEqual(w.split_value.placeholderText(), '[ enter number of parts ]')
        self.assertTrue(w.extract_button.isEnabled())
        origin = w.pos()
        with patch.object(w, '_start_extraction') as start, patch.object(w, '_start_preload') as preload:
            w.extract_button.click()
            self.assertIn('Enter a shared', w.url_error.text())
            self.assertFalse(w.split_value.property('splitValid'))
            self.assertIs(w._input_shake[1], w.url_input)
            advance(210)
            self.assertEqual(w.pos(), origin)
            self.assertIsNone(w._input_shake)
            start.assert_not_called()
            preload.assert_not_called()
            w.url_input.setText(URL)
            for mode in ('Number of Parts', 'Messages per Part'):
                w.split_selector._select(mode)
                for value in ('', '0', '-1', 'bad', '1.5'):
                    w.split_value.setText(value)
                    w.extract_button.click()
                    self.assertIs(w._input_shake[1], w.split_value)
                    self.assertIsNone(w._operation_settings)
                    self.assertTrue(w.extract_button.isEnabled())
                    start.assert_not_called()
            w.split_value.setText('3')
            w.extract_button.click()
            start.assert_called_once()
            self.assertEqual(w._operation_settings, (URL, 'assistant', 'Messages per Part', '3'))
            self.assertFalse(w.extract_button.isEnabled())
            self.assertTrue(w.extract_button._processing)

    def test_three_modes_route_and_reset_defaults(self):
        w = self.w
        w.split_selector._show_popup()
        self.assertEqual([b.text() for b in w.split_selector.option_buttons],
                         ['Character Limit', 'Number of Parts', 'Messages per Part'])
        w.split_selector._hide_popup()
        for radio, mode in ((w.ai_radio, 'assistant'), (w.user_radio, 'user'), (w.both_radio, 'both')):
            w.url_input.setText(URL)
            radio.setChecked(True)
            w.split_selector._select('Messages per Part')
            self.assertEqual(w.split_value.placeholderText(), '[ enter messages per part ]')
            w.split_value.setText('3')
            w._preloaded_extraction = {'full_conversation': FULL}
            w._preloaded_version = w._preload_version
            with patch('gui.extraction_worker.extract_conversation') as network:
                w.extract_button.click()
                until(lambda: not w._extraction_threads)
                advance(400)
                network.assert_not_called()
            selected = {**FULL, 'messages': [m for m in FULL['messages'] if mode == 'both' or m['role'] == mode]}
            self.assertEqual(w._parts, split_parts_by_message_count(selected, 3))
            w._reset_results_session()
            advance(350)
            self.assertEqual(w.split_selector.currentText(), 'Number of Parts')
            self.assertEqual(w.split_value.text(), '')
            self.assertTrue(w.extract_button.isEnabled())

    def test_preview_full_source_filter_and_output_independence(self):
        w = self.w
        w._conversation = copy.deepcopy(FULL)
        w._parts = ['unchanged output']
        w.scratchpad.setPlainText('keep my notes')
        errors = []
        for mode in ('assistant', 'user', 'both'):
            w._extraction_mode = mode
            w._extracted_conversation = {**FULL, 'messages': [m for m in FULL['messages'] if mode == 'both' or m['role'] == mode]}
            before = copy.deepcopy((w._conversation, w._extracted_conversation, w._parts))
            def inspect():
                dialog = APP.activeModalWidget()
                try:
                    selector = dialog.findChild(PreviewRoleSelector)
                    browser = dialog.findChild(QTextBrowser)
                    self.assertEqual(selector.current_role, 'all')
                    self.assertEqual(selector.animation.duration(), 180)
                    all_document = browser.document()
                    conversion_count = convert.call_count
                    self.assertEqual(conversion_count, len(FULL['messages']))
                    for role, button in list(zip(selector.ROLES, selector.buttons)) * 2:
                        button.click()
                        text = browser.toPlainText()
                        expected = [i for i, m in enumerate(FULL['messages'], 1) if role == 'all' or m['role'] == role]
                        self.assertEqual([int(n) for n in re.findall(r'\[msg (\d+)\]', text)], expected)
                        block = browser.document().begin()
                        while block.isValid():
                            if '[msg ' in block.text():
                                user = 'The User' in block.text()
                                alignment = block.blockFormat().alignment()
                                self.assertTrue(alignment & (Qt.AlignmentFlag.AlignRight if user else Qt.AlignmentFlag.AlignLeft))
                                fragment = block.begin().fragment()
                                self.assertEqual(fragment.charFormat().foreground().color().name(), '#4d7cfe')
                            if 'Unique message' in block.text():
                                self.assertFalse(block.blockFormat().alignment() & Qt.AlignmentFlag.AlignRight)
                            block = block.next()
                        self.assertEqual((w._conversation, w._extracted_conversation, w._parts), before)
                        self.assertEqual(w.scratchpad.toPlainText(), 'keep my notes')
                        self.assertEqual(convert.call_count, conversion_count)
                        if role == 'all':
                            self.assertIs(browser.document(), all_document)
                except Exception as error:
                    errors.append(error)
                finally:
                    dialog.accept()
            with patch('gui.preview.markdown.markdown', wraps=preview.markdown.markdown) as convert:
                QTimer.singleShot(10, inspect)
                w._preview_entire_thread()
        if errors:
            raise errors[0]
