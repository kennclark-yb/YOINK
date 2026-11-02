"""Owner-reported workspace lifecycle, current placement and compact summaries."""
import copy
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt,QRect,QPoint
from PySide6.QtTest import QTest
from test_phase2a import APP,advance,until
from test_context_selection import conversation
from gui.main_window import MainWindow


class WorkspaceStateTests(unittest.TestCase):
    def setUp(self):
        self.update=patch('gui.updates.UpdateChecker.check');self.update.start()
        self.w=MainWindow();w=self.w;w.show()
        w._results_work_area=lambda:QRect(0,0,1920,1032)
        w._conversation=conversation(176);w._extracted_conversation=copy.deepcopy(w._conversation)
        w._extraction_mode='both';w._parts=['Synthetic one','Synthetic two'];w._markdown='Synthetic'
        w._show_results();advance(400)
        w.move(550,100)

    def tearDown(self):
        w=self.w;w.workspace.collapse(immediate=True)
        if w._results_animation:w._results_animation.stop()
        w._close_after_results=False;w._results_resetting=False
        w._closing=True;w._finish_shutdown();w.deleteLater();advance(20);self.update.stop()

    def settle(self):
        until(lambda:not self.w.workspace.animating)

    def test_each_launcher_toggles_and_preserves_state(self):
        w=self.w
        for kind,button in [('picker',w.context_picker_button),('preview',w.preview_button),('scratchpad',w.scratchpad_button)]:
            button.click();self.assertEqual(w.workspace.kind,kind)
            if kind=='picker':w._context_picker.timeline.set_selection(w._context_picker.timeline.selection.replace(2,8))
            if kind=='scratchpad':w.scratchpad.setPlainText('Notes retained')
            widget=w.workspace.stack.currentWidget()
            button.click();self.assertEqual(w.workspace.phase,'closed')
            button.click();self.assertIs(w.workspace.stack.currentWidget(),widget)
            if kind=='picker':self.assertEqual(w._context_picker.timeline.selection.selected_count,6)
            if kind=='scratchpad':self.assertEqual(w.scratchpad.toPlainText(),'Notes retained')
            w.workspace.collapse()

    def test_rapid_toggle_switch_reverse_has_one_clock(self):
        w=self.w;ws=w.workspace;ws.motion_enabled=True
        w.preview_button.click();advance(50);first=ws.animation
        w.preview_button.click();self.assertEqual(ws.phase,'closing')
        self.assertIsNot(ws.animation,first)
        advance(30);w.preview_button.click();self.assertEqual(ws.phase,'opening')
        advance(40);w.context_picker_button.click();advance(40);w.scratchpad_button.click()
        self.settle();self.assertEqual(ws.kind,'scratchpad');self.assertEqual(ws.phase,'open')
        self.assertIsNone(ws.animation)
        w.scratchpad_button.click();self.settle();self.assertEqual(ws.phase,'closed')

    def test_reset_waits_for_third_then_results_no_premature_disposal(self):
        w=self.w;ws=w.workspace;ws.motion_enabled=True
        w._show_context_picker();self.settle();picker=w._context_picker;source=w._conversation
        w.scratchpad.setPlainText('Notes until completion')
        calls=[]
        original=w._retreat_results_for_reset
        def retreat():
            calls.append((ws.phase,ws.plan,w._conversation is source))
            original()
        with patch.object(w,'_retreat_results_for_reset',side_effect=retreat):
            w._reset_results_session();a=ws.animation;w._reset_results_session()
            self.assertIs(ws.animation,a)
            self.assertIs(w._context_picker,picker);self.assertTrue(picker._active)
            self.assertIs(w._conversation,source);self.assertEqual(w.scratchpad.toPlainText(),'Notes until completion')
            self.assertFalse(w.url_input.isEnabled())
            w._extraction_error('Late completion error during teardown')
            self.assertFalse(w.url_input.isEnabled())
            self.assertEqual(w.extraction_error.text(),'')
            a.setCurrentTime(a.duration())
            self.assertEqual(calls,[('closed',None,True)])
            self.assertIsNone(w._context_picker)
            self.assertIs(w._conversation,source)
            self.assertFalse(w.results_panel.isHidden())
            w._results_animation.setCurrentTime(w._results_animation.duration())
            self.assertIsNone(w._conversation);self.assertEqual(w.scratchpad.toPlainText(),'')
            self.assertTrue(w.results_panel.isHidden());self.assertFalse(w._results_resetting)
            self.assertTrue(w.url_input.isEnabled())

    def test_close_chain_each_start_and_repeated_request(self):
        w=self.w;ws=w.workspace;ws.motion_enabled=True
        w._show_scratchpad();advance(60)
        w.close();a=ws.animation
        self.assertEqual(ws.phase,'closing');self.assertIsNone(w._shutdown_screen)
        w.close();self.assertIs(ws.animation,a)
        a.setCurrentTime(a.duration())
        self.assertEqual(ws.phase,'closed');self.assertIsNone(w._shutdown_screen)
        self.assertFalse(w.results_panel.isHidden())
        w._results_animation.setCurrentTime(w._results_animation.duration())
        self.assertTrue(w.results_panel.isHidden());self.assertTrue(w._closing)
        self.assertIsNotNone(w._shutdown_screen);self.assertFalse(w._close_after_results)
        w._finish_shutdown();self.assertFalse(w.isVisible())

    def test_close_joins_back_or_reset_in_progress(self):
        w=self.w;ws=w.workspace;ws.motion_enabled=True;w._show_context_picker();self.settle()
        ws.back.click();a=ws.animation
        w._reset_results_session();w.close();w.close()
        self.assertIs(ws.animation,a);self.assertEqual(len(ws._close_callbacks),1)
        a.setCurrentTime(a.duration())
        w._results_animation.setCurrentTime(w._results_animation.duration())
        self.assertTrue(w._closing);self.assertIsNone(ws.saved)

    def test_current_manual_position_is_anchor_for_switch_and_back(self):
        w=self.w;ws=w.workspace;original_size=w.size()
        w.move(700,150);anchor=w.geometry();w._show_context_picker()
        self.assertEqual(w.x(),anchor.x()+(anchor.width()-w.width())//2)
        w.move(200,250);moved=w.geometry()
        w._preview_entire_thread()
        self.assertEqual(w.x(),moved.x()+(moved.width()-w.width())//2)
        self.assertEqual(w.y(),250)
        self.assertNotEqual(w.x(),ws.saved[0].x())
        current=w.geometry();ws.back.click()
        self.assertEqual(w.size(),original_size)
        self.assertEqual(w.x(),current.x()+(current.width()-w.width())//2)
        self.assertEqual(w.y(),250)

    def test_move_during_animation_rebases_endpoints(self):
        w=self.w;ws=w.workspace;ws.motion_enabled=True;w._show_context_picker();advance(60)
        before=QRect(ws._motion_end.window)
        actual=w.geometry();w.move(actual.x()+80,actual.y()+30)
        self.assertEqual(ws._motion_end.window.topLeft(),before.topLeft()+QPoint(80,30))
        target=QRect(ws._motion_end.window);self.settle()
        self.assertEqual(w.geometry(),target)
        w.move(100,170);current=w.geometry();w._preview_entire_thread();self.settle()
        self.assertEqual(w.x(),max(0,current.x()+(current.width()-w.width())//2))

    def test_edges_negative_narrow_and_reset_bounds(self):
        w=self.w;ws=w.workspace
        for area in (QRect(0,0,1920,1032),QRect(-1920,-100,1920,1032),QRect(0,0,1280,688),QRect(-800,0,800,688)):
            w._results_work_area=lambda area=area:area
            for point in (area.topLeft(),QPoint(area.right()-w.width()+1,area.bottom()-w.height()+1)):
                w.move(point);w._show_context_picker()
                self.assertTrue(area.contains(w.geometry()))
                w._show_scratchpad();self.assertTrue(area.contains(w.geometry()))
                ws.collapse();self.assertTrue(area.contains(w.geometry()))
        w._show_context_picker();w._reset_results_session()
        for ms in (0,30,100,200,299):
            w._results_animation.setCurrentTime(ms)
            self.assertTrue(w._results_work_area().contains(w.geometry()))
        w._results_animation.setCurrentTime(300)
        self.assertTrue(w._results_work_area().contains(w.geometry()))

    def test_picker_clear_alignment_help_status_without_numeric_shortcut(self):
        w=self.w;w._show_context_picker();d=w._context_picker;w.activateWindow();advance(20)
        self.assertFalse(hasattr(d,'more'));self.assertTrue(d.clear_button.isVisible())
        self.assertFalse(d.clear_button.isEnabled());self.assertEqual(d.status.text(),'[ status ] : no selection')
        self.assertTrue(d.hint.text().startswith('[ how to ] :'))
        t=d.timeline
        self.assertEqual(t.height(),68);self.assertEqual(t.pill_rect(0).height(),22)
        self.assertIsNotNone(t.hit_test(QPoint(0,8)));self.assertIsNotNone(t.hit_test(QPoint(t.width()-1,67)))
        for widget in (t,d.hint,d.status,d.copy_button):
            self.assertEqual(widget.mapTo(d,QPoint()).x(),t.mapTo(d,QPoint()).x())
        self.assertEqual(d.append_button.mapTo(d,d.append_button.rect().topRight()).x(),t.mapTo(d,t.rect().topRight()).x())
        self.assertLess(d.presets['first_half'].mapTo(d,QPoint()).y()-t.mapTo(d,t.rect().bottomLeft()).y(),42)
        t.setFocus();QTest.keyClick(t,Qt.Key.Key_G,Qt.KeyboardModifier.ControlModifier)
        self.assertFalse(hasattr(d,'advanced'))
        self.assertIs(APP.focusWidget(),t)
        t.set_selection(t.selection.replace(1,5))
        self.assertEqual(t.selection.selected_count,4);self.assertTrue(d.clear_button.isEnabled())
        self.assertEqual(d.status.text(),'[ status ] : selection ready')
        d.copy_button.click();self.assertEqual(d.status.text(),'[ status ] : selection copied')
        d.clear_button.click();self.assertEqual(t.selection.selected_count,0)

    def test_close_focus_each_tool_back_toggle_and_keyboard(self):
        w=self.w;ws=w.workspace;w.activateWindow();advance(20)
        for kind,button in [('preview',w.preview_button),('picker',w.context_picker_button),('scratchpad',w.scratchpad_button)]:
            for close in ('back','toggle','escape'):
                with self.subTest(kind=kind,close=close):
                    QTest.mouseClick(button,Qt.MouseButton.LeftButton);self.settle()
                    if close=='back':QTest.mouseClick(ws.back,Qt.MouseButton.LeftButton)
                    elif close=='toggle':QTest.mouseClick(button,Qt.MouseButton.LeftButton)
                    else:QTest.keyClick(ws.stack.currentWidget(),Qt.Key.Key_Escape)
                    self.settle()
                    self.assertEqual(ws.phase,'closed')
                    self.assertIsNot(APP.focusWidget(),w.context_picker_button)
                    focus=APP.focusWidget()
                    if focus is not None:
                        self.assertTrue(focus.isVisible())
                        QTest.keyClick(focus,Qt.Key.Key_Tab)
                    else:QTest.keyClick(w,Qt.Key.Key_Tab)
                    self.assertIsNotNone(APP.focusWidget())
                    self.assertTrue(APP.focusWidget().isVisible())
                    self.assertNotEqual(w.context_picker_button.focusPolicy(),Qt.FocusPolicy.NoFocus)
                    # A deliberate keyboard focus remains available on the launcher.
                    w.context_picker_button.setFocus(Qt.FocusReason.TabFocusReason)
                    self.assertIs(APP.focusWidget(),w.context_picker_button)
                    w.url_input.setFocus()

    def test_close_focus_interrupted_transitions_preserves_existing_focus(self):
        w=self.w;ws=w.workspace;ws.motion_enabled=True;w.activateWindow();advance(20)
        for button in (w.preview_button,w.context_picker_button,w.scratchpad_button):
            QTest.mouseClick(button,Qt.MouseButton.LeftButton);advance(40)
            ws.collapse();advance(30)
            QTest.mouseClick(button,Qt.MouseButton.LeftButton);advance(30)
            w.url_input.setFocus()
            ws.collapse();self.settle()
            self.assertEqual(ws.phase,'closed')
            self.assertIs(APP.focusWidget(),w.url_input)

    def test_results_stats_full_source_filtered_output_and_actual_split(self):
        w=self.w
        full=conversation(12)
        for role in ('both','assistant','user'):
            for mode in ('Character Limit','Number of Parts','Messages per Part'):
                w._reset_results_session();advance(350)
                filtered=copy.deepcopy(full)
                filtered['messages']=[m for m in full['messages'] if role=='both' or m['role']==role]
                w._operation_settings=('synthetic',role,mode,'2')
                w._extraction_finished({'conversation':full,'extracted_conversation':filtered,'mode':role,'markdown':'M','parts':['P1','P2']})
                advance(400)
                self.assertEqual(w.results_messages.text(),'12')
                self.assertEqual(w.results_messages.accessibleDescription(),'Full source message count')
                self.assertEqual(w.results_messages.accessibleName(),'')
                self.assertEqual(w.results_total_characters.text(),f"{sum(len(m['text']) for m in full['messages']):,}")
                self.assertIn(f"{sum(len(m['text']) for m in filtered['messages']):,} characters",w.results_extracted_characters.text())
                self.assertIn('6 AI',w.results_role_breakdown.text());self.assertIn('6 User',w.results_role_breakdown.text())
                self.assertIn(mode,w.results_parts.text());self.assertIn('2 parts',w.results_parts.text())
                self.assertIn({'both':'Entire conversation','assistant':'AI only','user':'User only'}[role],w.results_extraction_mode.text())
                w.split_selector._select('Number of Parts' if mode!='Number of Parts' else 'Character Limit')
                self.assertIn(mode,w.results_parts.text())
                self.assertEqual([h.text() for h in w.results_stat_headings],['TOTAL MESSAGES FOUND','CHARACTER\nTOTAL','THREAD','EXTRACTED MESSAGES'])

    def test_reduced_motion_chain_completes_without_workspace_clock(self):
        w=self.w;w._show_context_picker()
        with patch.dict('os.environ',{'YOINK_REDUCED_MOTION':'1'}):
            w._reset_results_session()
        self.assertIsNone(w.workspace.plan);self.assertIsNone(w._conversation)
        self.assertFalse(w._results_resetting)
