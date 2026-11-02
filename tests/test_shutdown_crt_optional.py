"""Reusable production CRT and standalone preview contracts at 220 x 140."""
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtGui import QFontMetricsF, QMovie
from PySide6.QtWidgets import QLabel
from shiboken6 import isValid

from test_phase2a import APP, advance, until
from gui.shutdown_screen import EXIT_MESSAGES, ShutdownScreen
from tools.preview_shutdown_crt import OptionalCrtPreview


class OptionalCrtTests(unittest.TestCase):
    def setUp(self):
        self.preview = OptionalCrtPreview()
        self.preview.show()
        advance(20)

    def tearDown(self):
        if isValid(self.preview):
            self.preview.close()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def test_runtime_selection_uses_existing_collection_once(self):
        for message in EXIT_MESSAGES:
            with self.subTest(message=message), patch('gui.shutdown_screen.random.choice', return_value=message) as choice:
                preview = OptionalCrtPreview()
                self.assertEqual(preview.quip, message)
                choice.assert_called_once_with(EXIT_MESSAGES)
                preview.close()

    def test_all_22_quips_fit_one_line_at_actual_size(self):
        p = self.preview
        self.assertEqual(p.size().toTuple(), (220, 140))
        self.assertEqual(len(EXIT_MESSAGES), 22)
        metrics = QFontMetricsF(p.terminal_font(10))
        for message in EXIT_MESSAGES:
            with self.subTest(message=message):
                self.assertLess(metrics.horizontalAdvance(message)+1, p.QUIP_RECT.width())
                self.assertLessEqual(metrics.height(), p.QUIP_RECT.height())
        self.assertEqual(p.TITLE_WORDS, ('SYSTEM', 'SHUTDOWN'))
        self.assertEqual(len(p._title_paths), 2)
        for face in p._title_paths:
            self.assertTrue(p.rect().contains(face.boundingRect().toAlignedRect()))
        self.assertFalse(hasattr(p, 'STATUS_LINES'))
        self.assertFalse(p.findChildren(QLabel), 'Quip must not be duplicated in a separate floating label')

    def test_movie_has_distinct_surface_frames_and_loops(self):
        movie = self.preview._movie
        movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.assertTrue(movie.isValid())
        self.assertEqual(movie.loopCount(), -1)
        self.assertGreater(movie.frameCount(), 30)
        movie.stop()
        images = []
        for index in (10, 30, 50):
            self.assertTrue(movie.jumpToFrame(index))
            images.append(movie.currentImage())
            self.assertEqual(movie.currentImage().size().toTuple(), (480, 306))
        self.assertNotEqual(images[0], images[1])
        self.assertNotEqual(images[1], images[2])
        # Exercise normal playback on a fresh decoder, independently of seeking.
        movie = QMovie(movie.fileName(), parent=self.preview)
        seen = []
        movie.frameChanged.connect(seen.append)
        movie.start()
        until(lambda: seen.count(0)>=2, 6500)
        self.assertEqual(movie.state(), QMovie.MovieState.Running)
        movie.stop()

    def test_production_uses_reusable_gui_renderer_without_tools(self):
        from gui.shutdown_crt import CrtShutdownSurface
        original = ShutdownScreen()
        try:
            self.assertIsInstance(original, CrtShutdownSurface)
            self.assertIs(OptionalCrtPreview, ShutdownScreen)
            self.assertEqual(Path(original._movie.fileName()).name, 'shutdown_system_optional.gif')
            self.assertFalse(original.findChildren(QLabel))
            runtime = Path('gui/shutdown_crt.py').read_text()
            for obsolete in ('CLOSING OVERLAY SURFACES', 'FLUSHING UI SETTINGS', 'tools.preview_shutdown_crt'):
                self.assertNotIn(obsolete, runtime)
            self.assertNotIn('tools', Path('gui/shutdown_screen.py').read_text())
        finally:
            original.close()

    def test_title_paths_are_large_thick_centered_and_not_cropped(self):
        from PySide6.QtCore import QRectF
        p = self.preview
        for face in p._title_paths:
            bounds = face.boundingRect()
            self.assertAlmostEqual(bounds.center().x(), 110)
            self.assertGreaterEqual(bounds.height(), 24)
            self.assertTrue(QRectF(p.rect()).contains(face.translated(1.5, 2).boundingRect()))
        self.assertGreater(p._title_paths[1].boundingRect().width(), 160)
        self.assertGreater(p.QUIP_RECT.top() - p._title_paths[1].boundingRect().bottom(), 18)
        image = p.grab().toImage()
        dpr = image.devicePixelRatio()
        for top, bottom in ((22, 47), (60, 85)):
            bright = sum(image.pixelColor(x, y).blue()>70
                         for y in range(round(top*dpr), round(bottom*dpr))
                         for x in range(round(20*dpr), round(200*dpr)))
            self.assertGreater(bright, 500*dpr*dpr)

    def test_soft_scan_band_is_broader_without_bright_flashes(self):
        movie = QMovie(self.preview._movie.fileName())
        movie.setCacheMode(QMovie.CacheMode.CacheAll)
        frames = []
        for index in (0, 15, 30, 45, 59):
            self.assertTrue(movie.jumpToFrame(index))
            frames.append(movie.currentImage())
        profile = [frames[2].pixelColor(240, y).blue()-min(im.pixelColor(240, y).blue() for im in frames)
                   for y in range(5, 300)]
        self.assertGreater(sum(delta>=3 for delta in profile), 24)
        self.assertLessEqual(max(profile), 9)

    def test_close_stops_and_disposes_preview_movie(self):
        preview = self.preview
        movie = preview._movie
        states = []
        movie.stateChanged.connect(states.append)
        preview.close()
        self.assertIn(QMovie.MovieState.NotRunning, states)
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.assertFalse(isValid(preview))
        self.assertFalse(isValid(movie))


if __name__ == '__main__':
    unittest.main()
