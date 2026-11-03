"""Shutdown presentation and real caller lifecycle; entirely offline."""
import hashlib
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent, QPoint, Qt
from PySide6.QtGui import QMovie, QFontMetricsF
from PySide6.QtWidgets import QLabel, QWidget
from shiboken6 import isValid

from test_phase2a import APP, EXTRACTION, URL, advance, until
from gui.main_window import MainWindow
from gui.shutdown_screen import EXIT_MESSAGES, ShutdownScreen

ROOT = Path(__file__).resolve().parents[1]


class ShutdownPresentationTests(unittest.TestCase):
    def setUp(self):
        self.screen = ShutdownScreen()
        self.screen.show()
        advance(30)

    def tearDown(self):
        if isValid(self.screen):
            self.screen.close()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def test_transparent_crt_corners_and_production_asset(self):
        s = self.screen
        self.assertEqual(s.size().toTuple(), (220, 140))
        self.assertTrue(s.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        self.assertTrue(s.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertFalse(s.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
        self.assertEqual(Path(s._movie.fileName()).name, 'shutdown_system_optional.gif')
        self.assertEqual(s.TITLE_WORDS, ('SYSTEM', 'SHUTDOWN'))
        self.assertFalse(s.findChildren(QWidget), 'Exactly one composition; no separate message capsule')
        for frame in (0, 1, 2):
            self.assertTrue(s._movie.jumpToFrame(frame))
            image = s.grab().toImage()
            dpr = image.devicePixelRatio()
            self.assertLess(image.pixelColor(0, 0).alpha(), 32)  # antialiased corner coverage
            self.assertEqual(image.pixelColor(round(110*dpr), round(95*dpr)).alpha(), 255)
        self.assertEqual(s._movie.currentPixmap().size().toTuple(), (480, 306))

    def test_all_quips_fit_inside_the_crt_once(self):
        for quip in EXIT_MESSAGES:
            with self.subTest(quip=quip), patch('gui.shutdown_screen.random.choice', return_value=quip) as choose:
                s = ShutdownScreen()
                try:
                    s.show()
                    APP.processEvents()
                    self.assertEqual(s.quip, quip)
                    self.assertEqual(s.accessibleDescription(), quip)
                    metrics = QFontMetricsF(s.terminal_font())
                    self.assertLess(metrics.horizontalAdvance(quip)+1, s.QUIP_RECT.width())
                    self.assertLess(metrics.height(), s.QUIP_RECT.height())
                    self.assertFalse(s.findChildren(QLabel))
                    choose.assert_called_once_with(EXIT_MESSAGES)
                finally:
                    s.close()

    def test_original_asset_identity_and_automatic_movie_disposal(self):
        expected = '9f632946d7162e2720039e204ffc1127901f129315575d1334cad234b5c33c84'
        self.assertEqual(hashlib.sha256((ROOT/'assets/shutdown.gif').read_bytes()).hexdigest(), expected)
        s = self.screen
        movie = s._movie
        stopped = []
        movie.stateChanged.connect(lambda state: stopped.append(state))
        s.close()
        self.assertIn(QMovie.MovieState.NotRunning, stopped)
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.assertFalse(isValid(s))
        self.assertFalse(isValid(movie))

    def test_optional_movie_decodes_advances_and_loops(self):
        movie = QMovie(str(ROOT/'assets/shutdown_system_optional.gif'))
        self.assertTrue(movie.isValid())
        self.assertEqual(movie.loopCount(), -1)
        self.assertGreater(movie.frameCount(), 30)
        frames = []
        movie.frameChanged.connect(frames.append)
        movie.start()
        try:
            until(lambda: len(frames)>movie.frameCount()+2, 6500)
            self.assertEqual(movie.currentPixmap().size().toTuple(), (480, 306))
            self.assertGreaterEqual(frames.count(0), 2)
            self.assertEqual(movie.state(), QMovie.MovieState.Running)
        finally:
            movie.stop()


class ShutdownLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.update_patch = patch('gui.updates.UpdateChecker.check')
        self.update_patch.start()
        self.w = MainWindow()
        self.w.show()
        advance(20)

    def tearDown(self):
        w = self.w
        until(lambda: not w._preload_threads and not w._extraction_threads)
        w._closing = True
        w._finish_shutdown()
        w.deleteLater()
        advance(20)
        self.update_patch.stop()

    def assert_shutdown_disposed(self, screen, overlay):
        until(lambda: self.w._shutdown_complete)
        advance(20)
        self.assertFalse(self.w.isVisible())
        self.assertIsNone(self.w._shutdown_screen)
        self.assertIsNone(self.w._shutdown_overlay)
        self.assertFalse(isValid(screen))
        self.assertFalse(isValid(overlay))
        self.assertFalse(self.w._preload_threads or self.w._extraction_threads)

    def test_shutdown_is_owned_and_not_globally_topmost(self):
        w = self.w
        self.assertIsNone(w._shutdown_screen)
        w.close()
        screen = w._shutdown_screen
        self.assertIs(screen.parentWidget(), w)
        self.assertTrue(screen.isWindow())
        self.assertEqual(screen.windowFlags() & Qt.WindowType.WindowType_Mask, Qt.WindowType.Window)
        self.assertFalse(screen.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
        self.assertTrue(screen.isVisible())
        self.assertTrue(w._shutdown_overlay.isVisible())
        self.assertIs(screen.windowHandle().transientParent(), w.windowHandle())

    def test_idle_timer_centering_and_no_orphans(self):
        w = self.w
        w.close()
        screen, overlay = w._shutdown_screen, w._shutdown_overlay
        center = w.frameGeometry().center()
        self.assertLessEqual(abs(center.x()-screen.geometry().center().x()), 1)
        self.assertLessEqual(abs(center.y()-screen.geometry().center().y()), 1)
        self.assertEqual(overlay.geometry(), w.rect())
        self.assertTrue(overlay.isVisible())
        w.close()
        advance(900)
        self.assertTrue(w.isVisible())
        self.assert_shutdown_disposed(screen, overlay)

    def test_active_preload_and_extraction_gate_shutdown(self):
        w = self.w
        release = threading.Event()
        def delayed(*args):
            if not release.wait(6):
                raise AssertionError('Worker release timed out')
            return EXTRACTION
        w.url_input.setText(URL)
        w.split_value.setText('1')
        with patch('gui.preload_worker.extract_conversation', side_effect=delayed), patch(
            'gui.extraction_worker.extract_conversation', side_effect=delayed
        ), patch.object(w, '_show_results') as results:
            w._extract_conversation()
            w._start_preload(URL)
            try:
                self.assertTrue(w._preload_threads)
                self.assertTrue(w._extraction_threads)
                w.close()
                screen, overlay = w._shutdown_screen, w._shutdown_overlay
                advance(1250)
                self.assertTrue(w.isVisible())
                self.assertTrue(screen.isVisible())
                self.assertFalse(w._shutdown_complete)
                w.close()
            finally:
                release.set()
            self.assert_shutdown_disposed(screen, overlay)
            results.assert_not_called()


if __name__ == '__main__':
    unittest.main()
