"""Default static artwork, diagnostic fallback and accepted shape checks."""
import os
import unittest
from unittest.mock import patch
from PySide6.QtCore import QPoint, QRect, QTimer, Qt
from PySide6.QtGui import QImage
from test_phase2a import advance, EXTRACTION
from gui.main_window import MainWindow

class StaticPreviewTests(unittest.TestCase):
    def make_window(self, enabled, opacity="84"):
        env = patch.dict(os.environ, {'YOINK_STATIC_BG_PREVIEW': '3' if enabled else '0', 'YOINK_DITHER_PREVIEW': '1', 'YOINK_PANEL_OPACITY': opacity})
        env.start(); self.addCleanup(env.stop)
        if enabled:
            os.environ.pop('YOINK_STATIC_BG_PREVIEW', None)
            if opacity == '84':
                os.environ.pop('YOINK_PANEL_OPACITY', None)
        check = patch('gui.updates.UpdateChecker.check'); check.start(); self.addCleanup(check.stop)
        w = MainWindow(); w.show(); advance(100)
        self.addCleanup(self.dispose, w)
        return w
    def dispose(self, w):
        w._closing = True; w._finish_shutdown(); w.deleteLater(); advance(20)
    def test_explicit_opt_out_restores_plain_opaque_surfaces(self):
        w = self.make_window(False)
        self.assertFalse(w.background.preview_enabled)
        self.assertTrue(w.background._image.isNull())
        self.assertEqual(w.card.styleSheet(), '')
        self.assertIn('background: #15161A;', w.results_panel.styleSheet())
        self.assertEqual(w.background.findChildren(QTimer, options=Qt.FindChildOption.FindDirectChildrenOnly), [])
    def test_preview_is_static_opaque_and_preserves_layout(self):
        w = self.make_window(True)
        self.assertFalse(w.background._image.isNull())
        self.assertTrue(w.background.preview_enabled)
        self.assertIsNone(w.background.asset_error)
        self.assertEqual(w.background.panel_alpha, 214)
        self.assertEqual(w.background.findChildren(QTimer, options=Qt.FindChildOption.FindDirectChildrenOnly), [])
        self.assertIn('214', w.card.styleSheet())
        self.assertIn('214', w.results_panel.styleSheet())
        w._results_work_area = lambda: QRect(-2000,-1500,6000,4000)
        w._conversation = EXTRACTION['conversation']; w._extracted_conversation = w._conversation
        w._extraction_mode = 'assistant'; w._parts = ['Synthetic']*12; w._markdown = 'Synthetic'
        w._show_results(); advance(420)
        self.assertEqual(w.content_layout.spacing(), 16)
        image = QImage(w.size(), QImage.Format.Format_ARGB32_Premultiplied); image.fill(0); w.render(image)
        self.assertEqual(image.pixelColor(30,30).alpha(), 0)
        for panel in (w.card, w.results_panel):
            point = panel.mapTo(w, QPoint(10, panel.height()//2))
            self.assertEqual(image.pixelColor(point).alpha(), 255)
        w._reset_results_session(); advance(350); self.assertTrue(w.results_panel.isHidden())


    def test_asset_hash_opacity_levels_and_cache_reuse(self):
        import hashlib
        from pathlib import Path
        asset = Path(__file__).resolve().parent.parent / 'assets/static_grain_option3.png'
        self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),
                         'a98613370c6ce6377a9772f278b0470b841008b37f944396004e3d7c8304158b')
        for level in ('78', '84', '90'):
            w = self.make_window(True, level)
            self.assertEqual(w.background.panel_alpha, round(int(level)*255/100))
            w.grab(); key = w.background._cache.cacheKey()
            w.grab(); self.assertEqual(w.background._cache.cacheKey(), key)
            self.assertEqual(w.background._image.size().width(), 2560)
            self.assertEqual(w.background._image.size().height(), 1800)
            self.assertAlmostEqual(w.background._cache.width() / w.devicePixelRatioF(), w.width(), delta=1)

    def test_frozen_layout_resolves_shared_assets_and_loads_accepted_image(self):
        import sys
        import shutil
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from gui.background import Background
        from gui import application
        with TemporaryDirectory() as directory:
            internal = Path(directory) / '_internal'
            assets = internal / 'assets'; assets.mkdir(parents=True)
            shutil.copyfile(application.ASSETS / 'static_grain_option3.png', assets / 'static_grain_option3.png')
            namespace = {'__file__': str(internal / 'gui' / 'application.py'),
                         '__package__': 'gui', '__name__': 'gui.frozen_fixture'}
            exec(compile(Path(application.__file__).read_text(), str(internal / 'gui' / 'application.py'), 'exec'), namespace)
            self.assertEqual(namespace['ASSETS'], assets)
            with patch.object(sys, 'frozen', True, create=True), patch.object(sys, '_MEIPASS', str(internal), create=True), patch('gui.background.ASSETS', namespace['ASSETS']), patch.dict(os.environ):
                os.environ.pop('YOINK_STATIC_BG_PREVIEW', None)
                os.environ.pop('YOINK_PANEL_OPACITY', None)
                background = Background()
                self.addCleanup(background.deleteLater)
                self.assertTrue(background.preview_enabled)
                self.assertIsNone(background.asset_error)
                self.assertEqual(background._image.width(), 2560)
                self.assertEqual(background._image.height(), 1800)
                self.assertEqual(background.panel_alpha, 214)

    def test_missing_asset_is_reported_and_falls_back_to_opaque_plain_panels(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory, patch('gui.background.ASSETS', Path(directory)):
            with self.assertLogs('gui.background', level='ERROR') as logs:
                w = self.make_window(True)
            self.assertIn('Cannot load static background asset', logs.output[0])
            self.assertIsNotNone(w.background.asset_error)
            self.assertFalse(w.background.preview_enabled)
            self.assertTrue(w.background._image.isNull())
            self.assertEqual(w.card.styleSheet(), '')
            self.assertIn('background: #15161A;', w.results_panel.styleSheet())
