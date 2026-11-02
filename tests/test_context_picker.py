"""Synthetic, offline Stage 1C GUI contracts, including the original Results actions."""
import copy
import time
import unittest
from unittest.mock import patch

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent, QShortcut
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPushButton, QLineEdit, QComboBox, QLabel

from test_phase2a import APP, advance
from test_context_selection import conversation
from context_selection import ContextSelection, MessageRange
from gui.context_picker import ContextPicker
from gui.context_timeline import MessageTimeline
from gui.main_window import MainWindow

CTRL = Qt.KeyboardModifier.ControlModifier
NONE = Qt.KeyboardModifier.NoModifier
LEFT = Qt.MouseButton.LeftButton


def point(timeline, position, handle=False):
    r = timeline.pill_rect(position)
    return QPoint(round(r.center().x()), 25 if handle else round(r.center().y()))


def move(timeline, position, modifiers=NONE):
    p = QPointF(point(timeline, position))
    event = QMouseEvent(QEvent.Type.MouseMove, p, p, Qt.MouseButton.NoButton, LEFT, modifiers)
    APP.sendEvent(timeline, event)


def drag(timeline, first, last, additive=False, release_ctrl=False, handle=False):
    QTest.mousePress(timeline, LEFT, CTRL if additive else NONE, point(timeline, first, handle))
    move(timeline, last, NONE if release_ctrl else CTRL if additive else NONE)
    QTest.mouseRelease(timeline, LEFT, NONE, point(timeline, last))
    APP.processEvents()


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.t = MessageTimeline(30)
        self.t.resize(600, 110)
        self.t.show()
        APP.processEvents()

    def tearDown(self):
        self.t.close()
        self.t.deleteLater()
        APP.processEvents()

    def test_pills_order_and_hit_testing(self):
        t = self.t
        self.assertEqual(list(t.visible_positions), list(range(30)))
        self.assertEqual(t.last_painted_count, 30)
        self.assertFalse(t.findChildren(QPushButton))
        for i in range(30):
            self.assertEqual(t.hit_test(point(t, i)), i)
            if i:
                self.assertGreater(t.pill_rect(i).x(), t.pill_rect(i - 1).x())
        self.assertEqual(t.hit_test(QPoint(0, 40)), 0)
        self.assertEqual(t.hit_test(QPoint(t.width()-1, 40)), 29)
        self.assertEqual(t.pill_rect(0).height(), 22)
        self.assertIsNone(t.hit_test(QPoint(30, 5)))

    def test_drag_outside_both_edges_and_return_releases_cleanly(self):
        t=self.t
        QTest.mousePress(t, LEFT, NONE, point(t, 10))
        for x in (-20, 2, t.width()+20, t.width()-2):
            p=QPointF(x, 40)
            event=QMouseEvent(QEvent.Type.MouseMove,p,p,Qt.MouseButton.NoButton,LEFT,NONE)
            APP.sendEvent(t,event)
            self.assertIsNotNone(t._drag)
        p=QPointF(t.width()+20,40)
        APP.sendEvent(t,QMouseEvent(QEvent.Type.MouseButtonRelease,p,p,LEFT,Qt.MouseButton.NoButton,NONE))
        self.assertIsNone(t._drag)
        self.assertFalse(t._scroll_timer.isActive())
        self.assertEqual(t.selection.ranges,(MessageRange(10,30),))

    def test_single_message_click(self):
        QTest.mouseClick(self.t, LEFT, NONE, point(self.t, 7))
        self.assertEqual(self.t.selection.ranges, (MessageRange(7, 8),))

    def test_drag_replaces_and_reverse_drag(self):
        drag(self.t, 2, 6)
        self.assertEqual(self.t.selection.ranges, (MessageRange(2, 7),))
        drag(self.t, 15, 12)
        self.assertEqual(self.t.selection.ranges, (MessageRange(12, 16),))

    def test_ctrl_drag_and_release_retains_then_ordinary_replaces(self):
        drag(self.t, 1, 4)
        drag(self.t, 10, 12, additive=True, release_ctrl=True)
        QTest.keyRelease(self.t, Qt.Key.Key_Control)
        self.assertEqual(self.t.selection.ranges, (MessageRange(1, 5), MessageRange(10, 13)))
        drag(self.t, 20, 21)
        self.assertEqual(self.t.selection.ranges, (MessageRange(20, 22),))

    def test_overlap_and_adjacency(self):
        drag(self.t, 2, 6)
        drag(self.t, 4, 8, additive=True)
        drag(self.t, 9, 11, additive=True)
        self.assertEqual(self.t.selection.ranges, (MessageRange(2, 12),))

    def test_handles_preserve_other_ranges_and_merge(self):
        drag(self.t, 2, 5)
        drag(self.t, 10, 13, additive=True)
        drag(self.t, 10, 8, handle=True)
        self.assertEqual(self.t.selection.ranges, (MessageRange(2, 6), MessageRange(8, 14)))
        drag(self.t, 5, 7, handle=True)
        self.assertEqual(self.t.selection.ranges, (MessageRange(2, 14),))

    def test_keyboard_navigation_selection_and_add(self):
        t = self.t
        t.setFocus()
        QTest.keyClick(t, Qt.Key.Key_Right)
        QTest.keyClick(t, Qt.Key.Key_Space)
        self.assertEqual(t.selection.ranges, (MessageRange(1, 2),))
        QTest.keyClick(t, Qt.Key.Key_End)
        QTest.keyClick(t, Qt.Key.Key_Return, CTRL)
        self.assertEqual(t.selection.ranges, (MessageRange(1, 2), MessageRange(29, 30)))
        self.assertEqual(t.accessibleName(), "Message timeline")
        QTest.keyClick(t, Qt.Key.Key_Home)
        self.assertEqual(t.cursor, 0)

    def test_long_viewport_navigation_zoom_and_bounded_paint(self):
        t = self.t
        t.zoom(0)
        t.set_selection(ContextSelection(100000).replace(99980, 99999))
        start = time.perf_counter()
        for i in range(100):
            t.set_first(i * 997)
            t.repaint()
        elapsed = time.perf_counter() - start
        t.setFocus()
        QTest.keyClick(t, Qt.Key.Key_End)
        self.assertIn(99999, t.visible_positions)
        self.assertEqual(t.hit_test(point(t, 99999)), 99999)
        QTest.keyClick(t, Qt.Key.Key_Space)
        self.assertEqual(t.selection.ranges, (MessageRange(99999, 100000),))
        for _ in range(20):
            t.zoom(-2)
        self.assertEqual(t.pitch, 10)
        t.repaint()
        self.assertLessEqual(t.last_painted_count, t.capacity)
        self.assertLessEqual(t.last_painted_count, 60)
        self.assertLess(elapsed, 5, "100 viewport repaints must remain interactive")
        print(f"TIMELINE_PERF: 100 repaints / 100000 positions: {elapsed:.4f}s; visible={t.last_painted_count}")

    def test_edge_autoscroll_and_hide_stops_drag(self):
        t = self.t
        t.zoom(0)
        t.set_selection(ContextSelection(1000))
        QTest.mousePress(t, LEFT, NONE, point(t, 2))
        p = QPointF(t.width() + 20, 50)
        APP.sendEvent(t, QMouseEvent(QEvent.Type.MouseMove, p, p, Qt.MouseButton.NoButton, LEFT, NONE))
        advance(110)
        self.assertGreater(t.first, 0)
        self.assertGreater(t.selection.selected_count, t.capacity - 2)
        t.hide()
        self.assertFalse(t._scroll_timer.isActive())
        self.assertIsNone(t._drag)


class PickerTests(unittest.TestCase):
    def setUp(self):
        self.source = conversation(20)
        self.before = copy.deepcopy(self.source)
        self.appends = []
        self.d = ContextPicker(self.source, lambda *args: self.appends.append(args))
        self.d.show()
        APP.processEvents()

    def tearDown(self):
        self.assertEqual(self.source, self.before)
        self.d.close()
        self.d.deleteLater()
        APP.processEvents()

    def select(self, first, last, action="replace"):
        self.d.timeline.set_selection(self.d.timeline.selection.select_display(first, last, add=action == "add"))

    def test_empty_no_match_and_direct_output(self):
        d = self.d
        self.assertEqual("[ status ] : no selection", d.status.text())
        self.assertFalse(d.copy_button.isEnabled())
        self.assertFalse(d.append_button.isEnabled())
        self.select(1, 1)
        d.output_role = "assistant"
        d._invalidate()
        self.assertEqual("[ status ] : no matching output messages", d.status.text())
        self.assertFalse(d.preview_button.isEnabled())
        d.output_role = "both"
        d._invalidate()
        self.assertTrue(d.preview_button.isEnabled())
        self.assertTrue(d.copy_button.isEnabled())
        d.copy_button.click()
        expected = d.timeline.selection.resolve(self.source, "both").to_markdown()
        self.assertEqual(APP.clipboard().text(), expected)
        d.append_button.click()
        self.assertEqual(self.appends[-1][1], expected)
        d.preview_button.click()
        self.assertEqual(d.preview_view.toPlainText(), expected)
        self.select(3, 4)
        self.assertTrue(d.copy_button.isEnabled())
        self.assertEqual(d.preview_view.toPlainText(), "")
        self.assertIsNone(d._preview_text)

    def test_compact_surface_exposes_timeline_and_accessible_clear(self):
        d=self.d
        APP.processEvents()
        self.assertTrue(d.timeline.isVisible())
        self.assertTrue(all(value.isVisible() for value in d.summary_values))
        self.assertFalse(hasattr(d,'more'))
        self.assertEqual(d.clear_button.accessibleName(),'Clear Selection')
        self.assertTrue(d.clear_button.isVisible())
        self.assertFalse(d.clear_button.isEnabled())
        self.assertFalse(d.preview_button.isVisible())
        d.timeline.set_selection(d.timeline.selection.replace(1,4))
        self.assertTrue(d.clear_button.isEnabled())
        d.clear_button.click()
        self.assertEqual(d.timeline.selection.selected_count,0)
        self.assertFalse(d.clear_button.isEnabled())

    def test_preset_and_clear_actions_share_an_aligned_row(self):
        d = self.d
        d.resize(500, 300)
        advance(50)
        first, final = d.presets['first_half'], d.presets['final_half']
        clear = d.clear_button
        self.assertEqual(first.geometry().top(), final.geometry().top())
        self.assertEqual(final.geometry().top(), clear.geometry().top())
        self.assertLessEqual(abs(first.width() - final.width()), 1)
        self.assertLess(clear.width(), first.width())
        self.assertLess(first.geometry().right(), final.geometry().left())
        self.assertLess(final.geometry().right(), clear.geometry().left())
    def test_direct_output_cache_refresh_and_no_role_match(self):
        d = self.d
        self.select(3, 5)
        d.copy_button.click()
        first = d.timeline.selection.resolve(self.source, 'both').to_markdown()
        self.assertEqual(APP.clipboard().text(), first)
        d.append_button.click()
        self.assertEqual(self.appends[-1][1], first)
        d.preview_button.click()
        self.assertEqual(d.preview_view.toPlainText(), first)
        self.select(8, 8)
        self.assertIsNone(d._preview_text)
        d.copy_button.click()
        self.assertEqual(APP.clipboard().text(), d.timeline.selection.resolve(self.source, 'both').to_markdown())
        d.output_role = 'user'
        d._invalidate()
        self.assertFalse(d.copy_button.isEnabled())
        self.assertFalse(d.append_button.isEnabled())

    def test_all_presets_odd_even_use_engine(self):
        for count in (5, 8):
            d = ContextPicker(conversation(count), lambda *args: None)
            for name, button in d.presets.items():
                button.click()
                self.assertEqual(d.timeline.selection, ContextSelection(count).preset(name))
            d.deleteLater()

    def test_disconnected_timeline_selection_deselect_and_clear(self):
        d = self.d
        drag(d.timeline, 1, 3)
        drag(d.timeline, 11, 14, additive=True)
        self.assertEqual(d.timeline.selection.ranges, (MessageRange(1, 4), MessageRange(11, 15)))
        QTest.mouseClick(d.timeline, LEFT, NONE, point(d.timeline, 2))
        self.assertEqual(d.timeline.selection.ranges, (MessageRange(1, 2), MessageRange(3, 4), MessageRange(11, 15)))
        d.clear_button.click()
        self.assertEqual(d.timeline.selection.ranges, ())

    def test_role_filter_after_boundaries_original_numbers_copy_and_append(self):
        d = self.d
        self.select(3, 5)
        self.select(10, 12, "add")
        bounds = d.timeline.selection
        d.output_role = "assistant"
        d._invalidate()
        self.assertEqual(d.timeline.selection, bounds)
        d.preview_button.click()
        text = bounds.resolve(self.source, "assistant").to_markdown()
        self.assertEqual(d.preview_view.toPlainText(), text)
        for number in (4, 10, 12):
            self.assertIn(f"[msg {number:03d}]", text)
        self.assertNotIn("[msg 001]", text)
        d.copy_button.click()
        self.assertEqual(APP.clipboard().text(), text)
        d.append_button.click()
        self.assertEqual(self.appends[0][1], text)
        d.output_role = "user"
        d._invalidate()
        self.assertTrue(d.copy_button.isEnabled())
        APP.clipboard().setText("sentinel")
        d.copy_selection()
        self.assertEqual(APP.clipboard().text(), bounds.resolve(self.source, "user").to_markdown())

    def test_no_manual_range_ui_or_ctrl_g_and_keyboard_escape(self):
        d = self.d
        d.activateWindow()
        APP.processEvents()
        self.assertFalse(d.findChildren(QLineEdit))
        self.assertFalse(d.findChildren(QComboBox))
        for name in ('numeric_link', 'advanced', 'start', 'end', 'ranges', 'validation',
                     'replace_button', 'add_button', 'update_button', 'remove_button',
                     '_toggle_numeric', '_numeric', '_load_range', '_remove'):
            self.assertFalse(hasattr(d, name), name)
        self.assertNotIn('Ctrl+G', [s.key().toString() for s in d.findChildren(QShortcut)])
        for widget in [d.timeline, *d.findChildren(QLabel)]:
            text = widget.toolTip() + widget.accessibleDescription()
            if isinstance(widget, QLabel):
                text += widget.text() + widget.accessibleName()
            self.assertNotIn('numeric', text.lower())
            self.assertNotIn('ctrl+g', text.lower())
        before = {id(w) for w in d.findChildren(QPushButton) if w.isVisible()}
        d.timeline.setFocus()
        QTest.keyClick(d.timeline, Qt.Key.Key_G, CTRL)
        APP.processEvents()
        self.assertEqual(before, {id(w) for w in d.findChildren(QPushButton) if w.isVisible()})
        self.assertIs(APP.focusWidget(), d.timeline)
        QTest.keyClick(d.timeline, Qt.Key.Key_Right)
        QTest.keyClick(d.timeline, Qt.Key.Key_Space)
        self.assertEqual(d.timeline.selection.ranges, (MessageRange(1, 2),))
        d.clear_button.setFocus()
        QTest.keyClick(d.clear_button, Qt.Key.Key_Tab)
        self.assertIs(APP.focusWidget(), d.copy_button)
        QTest.keyClick(d, Qt.Key.Key_Escape)
        self.assertFalse(d.isVisible())
        d.show()
        self.assertEqual(d.timeline.selection.ranges, (MessageRange(1, 2),))

    def test_scrolling_surface_keeps_output_actions_reachable(self):
        d = self.d
        self.select(2, 5)
        d.preview()
        d.resize(740, 300)
        APP.processEvents()
        self.assertGreater(d.surface_scroll.verticalScrollBar().maximum(), 0)
        d.surface_scroll.ensureWidgetVisible(d.copy_button)
        APP.processEvents()
        visible = d.copy_button.mapTo(d.surface_scroll.viewport(), QPoint(0, 0))
        self.assertGreaterEqual(visible.y(), 0)
        self.assertLess(visible.y() + d.copy_button.height(), d.surface_scroll.viewport().height() + 1)
        self.assertIn("msg 002", d.preview_view.toPlainText())

    def test_duplicate_append_feedback_does_not_claim_a_second_append(self):
        d = self.d
        self.select(1, 3)
        d.preview()
        d._append = lambda *args: False
        d.append_button.click()
        self.assertIn("[ status ] : already added", d.status.text())

    def test_session_invalidation_guards_saved_callbacks(self):
        self.select(1, 3)
        d = self.d
        d.preview()
        d.invalidate_session()
        APP.clipboard().setText("unchanged")
        d.copy_selection()
        d.append_selection()
        d.preview()
        self.assertEqual(APP.clipboard().text(), "unchanged")
        self.assertEqual(self.appends, [])
        self.assertIsNone(d.source)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.check = patch("gui.updates.UpdateChecker.check")
        self.check.start()
        self.w = MainWindow()
        self.w.show()
        self.source = conversation(20)
        self.w._conversation = self.source
        self.w._extracted_conversation = {"messages": [self.source["messages"][1]]}
        self.w._extraction_mode = "assistant"
        self.w._parts = ["Original intact part 1", "Original intact part 2"]
        self.w._markdown = "Original all parts"
        self.w._show_results()
        advance(400)

    def tearDown(self):
        self.w._discard_context_picker()
        self.w._closing = True
        self.w._finish_shutdown()
        self.w.deleteLater()
        advance(20)
        self.check.stop()

    def test_direct_selection_append_without_preview_preserves_notes_clipboard_and_undo(self):
        w = self.w
        w._show_context_picker()
        d = w._context_picker
        w.scratchpad.setPlainText('Existing notes')
        APP.clipboard().setText('Clipboard sentinel')
        d.timeline.set_selection(d.timeline.selection.replace(2, 5).add(10, 12))
        expected = d.timeline.selection.resolve(w._conversation, d.output_role).to_markdown()
        self.assertIsNone(d._preview_text)
        self.assertTrue(d.append_button.isEnabled())
        d.append_button.click()
        self.assertIn(expected, w._scratchpad_copy_text())
        self.assertTrue(w._scratchpad_copy_text().startswith('Existing notes'))
        self.assertEqual(APP.clipboard().text(), 'Clipboard sentinel')
        w._undo_scratchpad_append()
        self.assertEqual(w._scratchpad_copy_text(), 'Existing notes')
        self.assertEqual(APP.clipboard().text(), 'Clipboard sentinel')

    def test_picker_action_hover_and_disabled_state(self):
        w = self.w
        w.context_picker_button.click()
        d = w._context_picker
        d.timeline.set_selection(d.timeline.selection.select_message(1))
        button = d.copy_button
        self.assertIn(button, w._action_interactions.entries)
        APP.sendEvent(button, QEvent(QEvent.Type.Enter))
        advance(80)
        self.assertGreater(w._action_interactions.entries[button][1], 0)
        d.timeline.set_selection(d.timeline.selection.clear())
        self.assertFalse(button.isEnabled())
        self.assertEqual(w._action_interactions.entries[button][1], 0)
        APP.sendEvent(button, QEvent(QEvent.Type.Enter))
        advance(40)
        self.assertEqual(w._action_interactions.entries[button][1], 0)

    def test_full_source_append_undo_no_scratchpad_window_or_part_mutation(self):
        w = self.w
        before = copy.deepcopy((self.source, w._extracted_conversation, w._parts))
        w.context_picker_button.click()
        d = w._context_picker
        self.assertIs(d.source, self.source)
        self.assertEqual(d.timeline.selection.message_count, 20)
        w.scratchpad.setPlainText("Existing notes")
        APP.clipboard().setText("preserve")
        d.timeline.set_selection(d.timeline.selection.select_display(13, 15))
        d.preview()
        with patch.object(w.scratchpad_dialog, "show") as show, patch.object(w.scratchpad_dialog, "close") as close:
            d.append_button.click()
            self.assertIn(d._preview_text, w._scratchpad_copy_text())
            self.assertTrue(w._scratchpad_copy_text().startswith("Existing notes\n\n--- Selection 13–15"))
            self.assertEqual(APP.clipboard().text(), "preserve")
            self.assertTrue(w.scratchpad_undo_button.isEnabled())
            w.scratchpad_undo_button.click()
            self.assertEqual(w._scratchpad_copy_text(), "Existing notes")
            show.assert_not_called()
            close.assert_not_called()
        self.assertEqual((self.source, w._extracted_conversation, w._parts), before)

    def test_results_copy_append_and_copy_all_unchanged(self):
        w = self.w
        append = w.results_container.findChildren(QPushButton, "AppendPartButton")[0]
        copy_button = w.results_container.findChildren(QPushButton, "CopyPartButton")[1]
        append.click()
        self.assertIn(w._parts[0], w._scratchpad_copy_text())
        copy_button.click()
        self.assertEqual(APP.clipboard().text(), w._parts[1])
        w.copy_all_button.click()
        self.assertEqual(APP.clipboard().text(), "\n\n".join(w._parts))
        w.scratchpad_undo_button.click()
        self.assertEqual(w._scratchpad_copy_text(), "")

    def test_reset_new_extraction_and_closed_picker_session_isolation(self):
        w = self.w
        w.context_picker_button.click()
        d = w._context_picker
        d.timeline.set_selection(d.timeline.selection.replace(15, 19))
        d.close()
        w.context_picker_button.click()
        self.assertIs(w._context_picker, d)
        self.assertEqual(d.timeline.selection.selected_count, 4)
        w._reset_results_session()
        self.assertIsNone(w._context_picker)
        self.assertFalse(d._active)
        self.assertFalse(w.context_picker_button.isEnabled())
        advance(350)
        self.assertIsNone(w._conversation)
        result = {"conversation": conversation(3), "extracted_conversation": conversation(3),
                  "markdown": "new", "parts": ["new"], "mode": "both"}
        w._extraction_finished(result)
        advance(400)
        w.context_picker_button.click()
        self.assertEqual(w._context_picker.timeline.selection, ContextSelection(3))


if __name__ == "__main__":
    unittest.main()
