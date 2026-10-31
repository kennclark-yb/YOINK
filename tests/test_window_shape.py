"""Outer contour geometry, alpha, and synthetic lobe composition."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import QPointF, QPoint, QRect, Qt
from PySide6.QtGui import QImage, QPainter, QColor
from gui.window_shape import outer_path
from gui.main_window import MainWindow
from gui.application import configure_application
from test_phase2a import APP, advance, EXTRACTION


class OutlineTests(unittest.TestCase):
    def test_path_cutouts_connected_and_opaque(self):
        path = outer_path(900, 677, 437, 400, 520)
        for point in ((30, 30), (30, 650)):
            self.assertFalse(path.contains(QPointF(*point)))
        for point in ((30, 330), (450, 330), (800, 30), (800, 650)):
            self.assertTrue(path.contains(QPointF(*point)))
        image = QImage(900, 677, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, QColor("#09090B"))
        painter.end()
        self.assertEqual(image.pixelColor(30, 30).alpha(), 0)
        self.assertEqual(image.pixelColor(450, 330).alpha(), 255)

    def test_continuity_and_startup_equivalence(self):
        for step in range(101):
            p = step/100
            path = outer_path(400+500*p, 437+240*p, 437, 400, 400+120*p)
            self.assertEqual(len(path.toSubpathPolygons()), 1)
            self.assertTrue(path.contains(QPointF(200, (437+240*p)/2)))
            self.assertTrue(path.contains(QPointF((400+500*p)-30, (437+240*p)/2)))
        self.assertEqual(outer_path(400, 437, 437, 400, 400), outer_path(400, 437, 437, 400, 528))

    def test_expanded_card_bounds_title_controls_and_reset(self):
        configure_application(APP)
        with patch("gui.updates.UpdateChecker.check"):
            w = MainWindow()
            w.show()
            advance(20)
            try:
                original = w.size()
                card_height = w.card.height()
                w._results_work_area = lambda: QRect(0, 0, 1200, 900)
                w.move(350, 230)
                center = w.geometry().center()
                w._conversation = EXTRACTION["conversation"]
                w._extracted_conversation = w._conversation
                w._extraction_mode = "assistant"
                w._parts = ["Synthetic"] * 12
                w._markdown = "Synthetic"
                w._show_results()
                advance(400)
                self.assertGreater(w.height(), original.height())
                self.assertEqual(w.card.height(), card_height)
                self.assertLessEqual((w.geometry().center()-center).manhattanLength(), 2)
                self.assertEqual(w.content_layout.spacing(), 16)
                path = w._outer_window_path()
                # The cubic shoulder spans much farther than the panel gap.
                start, control1, control2, end = [path.elementAt(i) for i in range(1, 5)]
                self.assertGreater(end.x - start.x, 150)
                self.assertEqual(control1.y, start.y)
                self.assertEqual(control2.y, end.y)
                bottom = [path.elementAt(i) for i in range(13, 17)]
                self.assertEqual(bottom[0].y, bottom[1].y)
                self.assertEqual(bottom[2].y, bottom[3].y)
                def samples(points):
                    values = []
                    for i in range(101):
                        t = i / 100
                        values.append(sum(weight * point.y for weight, point in zip(
                            ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3), points)))
                    return values
                top_y = samples((start, control1, control2, end))
                bottom_y = samples(tuple(reversed(bottom)))
                self.assertTrue(all(a >= b for a, b in zip(top_y, top_y[1:])))
                self.assertTrue(all(a <= b for a, b in zip(bottom_y, bottom_y[1:])))
                self.assertTrue(all(end.y <= y <= start.y for y in top_y))
                self.assertTrue(all(bottom[3].y <= y <= bottom[0].y for y in bottom_y))
                for widget in (w.brand, w.title_bar.close_button, w.card, w.results_panel):
                    point = widget.mapTo(w.background, widget.rect().center())
                    self.assertTrue(path.contains(QPointF(point)))
                    origin = widget.mapTo(w.background, widget.rect().topLeft())
                    for x, y in ((4, 4), (widget.width()-5, 4),
                                 (4, widget.height()-5), (widget.width()-5, widget.height()-5)):
                        self.assertTrue(path.contains(QPointF(origin.x()+x, origin.y()+y)))
                self.assertTrue(w.mask().contains(w.rect().center()))
                self.assertFalse(w.mask().contains(w.rect().topLeft()+QPoint(30, 30)))
                self.assertEqual(w.content_surface.styleSheet(), "")
                w.showMaximized()
                advance(30)
                self.assertTrue(w._outer_window_path().contains(QPointF(5, 5)))
                w.showNormal()
                advance(30)
                self.assertFalse(w._outer_window_path().contains(QPointF(30, 30)))
                w._reset_results_session()
                advance(350)
                self.assertEqual(w.size(), original)
            finally:
                w._closing = True
                w._finish_shutdown()
                w.deleteLater()
                advance(20)

    def test_small_work_area_clamps_offscreen_start(self):
        with patch("gui.updates.UpdateChecker.check"):
            w = MainWindow()
            w.show()
            advance(20)
            try:
                w._results_work_area = lambda: QRect(-800, 40, 800, 600)
                w.move(-1000, -200)
                w._conversation = EXTRACTION["conversation"]
                w._extracted_conversation = w._conversation
                w._extraction_mode = "assistant"
                w._parts = ["Synthetic"] * 12
                w._markdown = "Synthetic"
                w._show_results()
                advance(400)
                self.assertTrue(w._results_work_area().contains(w.geometry()))
                self.assertGreater(w.height(), w._startup_size.height())
                self.assertEqual(w.content_layout.spacing(), 16)
            finally:
                w._closing = True
                w._finish_shutdown()
                w.deleteLater()
                advance(20)
