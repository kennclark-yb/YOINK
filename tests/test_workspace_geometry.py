"""Production workspace geometry and real widget session gates."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import QRect,QRectF,QPointF,QPoint,Qt
from PySide6.QtTest import QTest
from test_phase2a import APP,advance
from test_context_selection import conversation
from gui.main_window import MainWindow
from gui.workspace_geometry import plan_workspace,workspace_path


class PlannerTests(unittest.TestCase):
    def test_preferred_proportions_and_exact_gaps(self):
        for name,size in [('picker',(500,300)),('preview',(600,550)),('scratchpad',(600,420))]:
            p=plan_workspace(QRect(0,0,1920,1032),QRect(200,100,788,686),name)
            self.assertEqual((p.tool.width(),p.tool.height()),size)
            self.assertEqual(p.results.left()-p.extract.right()-1,16)
            self.assertEqual(p.tool.left()-p.results.right()-1,16)
            self.assertLess(p.tool.height(),p.results.height())
            self.assertTrue(workspace_path(p).contains(QPointF(p.tool.center())))
            self.assertFalse(workspace_path(p).contains(QPointF(p.window.width()-30,20)))

    def test_negative_and_scaled_available_areas(self):
        for area in (QRect(-800,0,800,688),QRect(0,0,1280,688),QRect(-1920,-100,1920,1032)):
            for name in ('picker','preview','scratchpad'):
                p=plan_workspace(area,QRect(1000,400,788,686),name)
                self.assertTrue(area.contains(p.window))
                self.assertGreaterEqual(p.extract.width(),300)
                self.assertTrue(QRect(0,0,p.window.width(),p.window.height()).contains(p.tool))
        self.assertTrue(plan_workspace(QRect(-800,0,800,688),QRect(100,300,788,686)).fallback)

    def test_refuse_unusable_area(self):
        with self.assertRaises(ValueError):plan_workspace(QRect(0,0,600,400),QRect(0,0,788,686))


class OrganicContourTests(unittest.TestCase):
    @staticmethod
    def boundary(path, x, height, center, upper):
        low, high = (0., center) if upper else (center, float(height))
        for _ in range(32):
            mid = (low + high) / 2
            inside = path.contains(QPointF(x, mid))
            if inside == upper:
                high = mid
            else:
                low = mid
        return (low + high) / 2

    def test_actual_upper_and_lower_shoulders_not_flat_union(self):
        for tool in ('picker','preview','scratchpad'):
            p=plan_workspace(QRect(0,0,1920,1032),QRect(200,100,788,686),tool)
            path=workspace_path(p)
            root=p.results.right()+10
            landing=p.tool.left()+min(220,p.tool.width()*.45)
            xs=[root+(landing-root)*f for f in (.1,.3,.5,.7,.9)]
            upper=[self.boundary(path,x,p.window.height(),p.tool.center().y(),True) for x in xs]
            lower=[self.boundary(path,x,p.window.height(),p.tool.center().y(),False) for x in xs]
            # A wall/rectangle union produces a jump followed by a flat tool edge.
            # A visible shoulder must instead occupy the whole sampled span.
            self.assertTrue(all(b-a>0.5 for a,b in zip(upper,upper[1:])),(tool,upper))
            self.assertTrue(all(a-b>0.5 for a,b in zip(lower,lower[1:])),(tool,lower))
            self.assertGreater(upper[-1]-upper[0],20,tool)
            self.assertGreater(lower[0]-lower[-1],20,tool)
            slopes=[b-a for a,b in zip(upper,upper[1:])]
            self.assertGreater(max(slopes)-min(slopes),3,tool)
            for x,u,l in zip(xs,upper,lower):
                self.assertFalse(path.contains(QPointF(x,u-3)))
                self.assertTrue(path.contains(QPointF(x,u+3)))
                self.assertFalse(path.contains(QPointF(x,l+3)))
                self.assertTrue(path.contains(QPointF(x,l-3)))

    def test_all_card_rectangles_and_connected_interior(self):
        for area in (QRect(0,0,1920,1032),QRect(0,0,1280,688)):
            for tool in ('picker','preview','scratchpad'):
                p=plan_workspace(area,QRect(200,100,788,686),tool)
                path=workspace_path(p)
                for card in (p.extract,p.results,p.tool):
                    self.assertTrue(path.contains(QRectF(card)),(tool,card))
                y=p.tool.center().y()
                for x in range(p.extract.center().x(),p.tool.center().x(),3):
                    self.assertTrue(path.contains(QPointF(x,y)),(tool,x))
                self.assertEqual(len(path.toSubpathPolygons()),1)
                self.assertLessEqual(path.boundingRect().right(),p.window.width())
                self.assertLessEqual(path.boundingRect().bottom(),p.window.height())



class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.check=patch('gui.updates.UpdateChecker.check');self.check.start()
        self.w=MainWindow();self.w.show()
        w=self.w;w._results_work_area=lambda:QRect(0,0,1920,1032)
        w._conversation=conversation(176);w._extracted_conversation=w._conversation
        w._extraction_mode='assistant';w._parts=['Synthetic one','Synthetic two'];w._markdown='Synthetic'
        w._show_results();advance(400)

    def tearDown(self):
        self.w.workspace.collapse();self.w._discard_context_picker()
        self.w._closing=True;self.w._finish_shutdown();self.w.deleteLater();advance(20);self.check.stop()

    def test_actual_stack_gap_shape_switch_close_reopen(self):
        w=self.w;old=w.geometry();w._show_context_picker();advance(20)
        p=w.workspace.plan
        self.assertEqual(w.workspace.x()-w.results_panel.geometry().right()-1,16)
        self.assertFalse(w._context_picker.isWindow())
        self.assertTrue(w._context_picker.timeline.fit_all)
        self.assertEqual(w._context_picker.timeline.capacity,176)
        w._context_picker.timeline.set_selection(w._context_picker.timeline.selection.replace(2,7).add(20,24))
        selected=w._context_picker.timeline.selection
        w._preview_entire_thread();self.assertFalse(w._preview_widget.isWindow())
        w._show_scratchpad();self.assertFalse(w.scratchpad_dialog.isWindow())
        w.scratchpad.setPlainText('Existing notes')
        w._show_context_picker();self.assertEqual(w._context_picker.timeline.selection,selected)
        before=w.geometry()
        w.workspace.collapse();self.assertEqual(w.size(),old.size())
        self.assertEqual(w.x(),before.x()+(before.width()-old.width())//2)
        w._show_scratchpad();self.assertEqual(w.scratchpad.toPlainText(),'Existing notes')

    def test_curve_mask_agreement_and_exact_closed_restoration(self):
        w=self.w
        baseline=w._outer_window_path();mask=w.mask()
        w._show_context_picker();advance(20)
        plan=w.workspace.plan;path=workspace_path(plan)
        self.assertEqual(w._outer_window_path(),path)
        root=plan.results.right()+10
        landing=plan.tool.left()+min(220,plan.tool.width()*.45)
        for f in (.1,.3,.5,.7,.9):
            x=root+(landing-root)*f
            for upper in (True,False):
                y=OrganicContourTests.boundary(path,x,w.height(),plan.tool.center().y(),upper)
                for delta in (-4,4):
                    point=QPoint(round(x),round(y+delta))
                    self.assertEqual(w.mask().contains(point),path.contains(QPointF(point)))
        w.workspace.collapse();advance(20)
        self.assertEqual(w._outer_window_path(),baseline)
        self.assertEqual(w.mask(),mask)

    def test_authoritative_output_copy_append_undo_switch(self):
        w=self.w;w._show_context_picker();d=w._context_picker
        d.timeline.set_selection(d.timeline.selection.replace(0,8).add(12,16));d.preview()
        expected=d.timeline.selection.resolve(w._conversation,'assistant').to_markdown()
        self.assertEqual(d.preview_view.toPlainText(),expected)
        self.assertFalse(hasattr(d,'role'))
        d.copy_selection();self.assertEqual(APP.clipboard().text(),expected)
        w.scratchpad.setPlainText('Notes');d.append_selection()
        w._show_scratchpad();self.assertIn(expected,w._scratchpad_copy_text())
        w._show_context_picker();w._undo_scratchpad_append();self.assertEqual(w._scratchpad_copy_text(),'Notes')

    def test_narrow_fallback_back_bounds(self):
        w=self.w;w._results_work_area=lambda:QRect(-800,0,800,688)
        w._show_context_picker();advance(20)
        self.assertTrue(w.workspace.plan.fallback);self.assertFalse(w.results_panel.isVisible())
        self.assertTrue(w.card.isVisible());self.assertGreater(w.card.width(),300)
        self.assertTrue(w._results_work_area().contains(w.geometry()))
        w.workspace.back.click();advance(20)
        self.assertTrue(w.results_panel.isVisible());self.assertTrue(w._results_work_area().contains(w.geometry()))

    def test_click_deselect_and_grouped_precision(self):
        w=self.w;w._show_context_picker();t=w._context_picker.timeline
        t.set_selection(t.selection.select_message(5))
        rect=t.pill_rect(5);QTest.mouseClick(t,Qt.MouseButton.LeftButton,pos=rect.center().toPoint())
        self.assertEqual(t.selection.selected_count,0)
        from context_selection import ContextSelection
        t.set_selection(ContextSelection(100000));t.repaint()
        self.assertLessEqual(t.last_painted_count,t.width()*2)
        t.zoom(0);t.ensure_visible(99999)
        self.assertIn(99999,t.visible_positions)
