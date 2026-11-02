"""Stage 1C owner corrections: real header hit targets and interruptible state."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt,QRect,QPoint,QEvent
from PySide6.QtGui import QFocusEvent
from PySide6.QtTest import QTest
from test_phase2a import APP,advance,until
from test_context_selection import conversation
from gui.main_window import MainWindow


class PolishTests(unittest.TestCase):
    def setUp(self):
        self.check=patch('gui.updates.UpdateChecker.check');self.check.start()
        self.w=MainWindow();w=self.w;w.show()
        w._results_work_area=lambda:QRect(0,0,1920,1032)
        w._conversation=conversation(176);w._extracted_conversation=w._conversation
        w._extraction_mode='both';w._parts=['One','Two'];w._markdown='Synthetic'
        w._show_results();advance(400)

    def tearDown(self):
        w=self.w;w.workspace.collapse(immediate=True)
        w._closing=True;w._finish_shutdown();w.deleteLater();advance(20);self.check.stop()

    def test_close_style_and_hit_target_each_tool(self):
        w=self.w
        self.assertIn('#E33258',w.title_bar.close_button.styleSheet())
        self.assertIn('background: transparent',w.title_bar.close_button.styleSheet())
        for action in (lambda:None,w._show_context_picker,w._preview_entire_thread,w._show_scratchpad):
            action();advance(20)
            b=w.title_bar.close_button;pos=b.mapTo(w,b.rect().center())
            self.assertIs(w.childAt(pos),b)
            self.assertTrue(w.mask().contains(pos))

    def test_left_back_summary_and_single_overflow_affordance(self):
        w=self.w
        for action in (w._show_context_picker,w._preview_entire_thread,w._show_scratchpad):
            action();advance(20)
            self.assertLess(w.workspace.back.x(),w.workspace.width()/2)
            self.assertIn('Results',w.workspace.back.accessibleName())
            self.assertIn('Back',w.workspace.back.toolTip())
            self.assertFalse(w.workspace.back.icon().isNull())
        w._show_context_picker();advance(20);d=w._context_picker
        self.assertEqual(len(d.summary_values),3)
        self.assertLess(d.summary_container.width(),d.width())
        self.assertFalse(hasattr(d,"more"))
        self.assertEqual(d.clear_button.text(),"Clear Selection")

    def test_pointer_focus_has_no_box_keyboard_retains_cursor(self):
        w=self.w;w._show_context_picker();t=w._context_picker.timeline
        APP.sendEvent(t,QFocusEvent(QEvent.Type.FocusIn,Qt.FocusReason.MouseFocusReason))
        self.assertFalse(t._keyboard_focus)
        APP.sendEvent(t,QFocusEvent(QEvent.Type.FocusIn,Qt.FocusReason.TabFocusReason))
        self.assertTrue(t._keyboard_focus)
        QTest.keyClick(t,Qt.Key.Key_Right);QTest.keyClick(t,Qt.Key.Key_Space)
        self.assertEqual(t.selection.selected_count,1)
        self.assertEqual(t.pill_rect(0).height(),22)
        self.assertIsNotNone(t.hit_test(QPoint(0,60)))

    def test_hover_delivery_independent_of_timeline_focus(self):
        w=self.w;w._show_context_picker();d=w._context_picker
        for focus in (w.context_picker_button,d.timeline):
            focus.setFocus();advance(5)
            for b in (w.context_picker_button,d.presets['first_half'],w.workspace.back):
                APP.sendEvent(b,QEvent(QEvent.Type.Enter))
                until(lambda:w._action_interactions.entries[b][1]>0,timeout=1000)
                self.assertGreater(w._action_interactions.entries[b][1],0)
                APP.sendEvent(b,QEvent(QEvent.Type.Leave))
                until(lambda:w._action_interactions.entries[b][1]==0,timeout=1000)
                self.assertEqual(w._action_interactions.entries[b][1],0)

    def test_animation_interrupt_switch_close_reopen(self):
        w=self.w;original=w.geometry();path=w._outer_window_path()
        w.workspace.motion_enabled=True
        w._show_context_picker();advance(60)
        self.assertTrue(w.workspace.animating)
        self.assertTrue(w._results_work_area().contains(w.geometry()))
        w._context_picker.timeline.set_selection(w._context_picker.timeline.selection.replace(2,6))
        w._preview_entire_thread();advance(50);w._show_scratchpad();advance(50)
        w.scratchpad.setPlainText('Preserved notes')
        w._show_context_picker();advance(300)
        self.assertFalse(w.workspace.animating)
        self.assertIsNone(w.workspace.animation)
        self.assertEqual(w._context_picker.timeline.selection.selected_count,4)
        self.assertEqual(w.scratchpad.toPlainText(),'Preserved notes')
        self.assertEqual(w.workspace.x()-w.results_panel.geometry().right()-1,16)
        before=w.geometry()
        w.workspace.collapse();advance(300)
        self.assertEqual(w.size(),original.size())
        self.assertEqual(w.x(),before.x()+(before.width()-original.width())//2)
        self.assertEqual(w._outer_window_path(),path)
        w._show_scratchpad();advance(300)
        self.assertEqual(w.scratchpad.toPlainText(),'Preserved notes')

    def test_animation_every_frame_bounded_and_mask_clipped(self):
        w=self.w;w.workspace.motion_enabled=True;w._show_context_picker()
        a=w.workspace.animation
        for ms in (1,30,80,120,190,239):
            a.setCurrentTime(ms)
            self.assertTrue(w._results_work_area().contains(w.geometry()))
            self.assertTrue(w.rect().contains(w.mask().boundingRect().adjusted(1,1,-1,-1)))
            self.assertEqual(w.childAt(w.title_bar.close_button.mapTo(w,QPoint(14,11))),w.title_bar.close_button)
        advance(300)

    def test_close_during_transition_repeated_uses_shutdown_lifecycle(self):
        w=self.w;w.workspace.motion_enabled=True;w._show_context_picker();advance(70)
        w.close();w.close();until(lambda:w._closing)
        self.assertTrue(w._closing)
        self.assertFalse(w._results_resetting)
        self.assertIsNone(w.workspace.plan)
        self.assertIsNone(w.workspace.animation)
        self.assertIsNone(w._context_picker)
        w._finish_shutdown();self.assertFalse(w.isVisible())

    def test_reduced_motion_and_constrained_mode_are_immediate(self):
        w=self.w;w.workspace.motion_enabled=False;w._show_context_picker()
        self.assertFalse(w.workspace.animating)
        w.workspace.collapse();w.workspace.motion_enabled=True
        w._results_work_area=lambda:QRect(-800,0,800,688)
        w._show_scratchpad()
        self.assertTrue(w.workspace.plan.fallback)
        self.assertFalse(w.workspace.animating)
        self.assertTrue(w._results_work_area().contains(w.geometry()))
        w.workspace.back.click()
        self.assertIsNone(w.workspace.plan)

    def test_close_from_every_mode_and_repeated_requests(self):
        # Every action runs the real reset -> shutdown flow, not a mocked slot.
        for mode in ('results','picker','preview','scratchpad','narrow'):
            with self.subTest(mode=mode):
                w=MainWindow();w.show()
                w._results_work_area=lambda:QRect(0,0,1920,1032)
                w._conversation=conversation(20);w._extracted_conversation=w._conversation
                w._extraction_mode='both';w._parts=['Synthetic'];w._markdown='Synthetic'
                w._show_results();advance(400)
                if mode=='narrow':w._results_work_area=lambda:QRect(-800,0,800,688)
                if mode in ('picker','narrow'):w._show_context_picker()
                elif mode=='preview':w._preview_entire_thread()
                elif mode=='scratchpad':w._show_scratchpad()
                b=w.title_bar.close_button
                self.assertIs(w.childAt(b.mapTo(w,b.rect().center())),b)
                b.click();w.close();advance(400)
                self.assertTrue(w._closing)
                self.assertIsNone(w.workspace.plan)
                self.assertFalse(w._close_after_results)
                w._finish_shutdown();self.assertFalse(w.isVisible())
                w.deleteLater();advance(20)
