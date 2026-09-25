"""Exercise the real spec with collection stubs; never build or touch dist."""
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "playwright/driver/package/.local-browsers/"


class PackagingTests(unittest.TestCase):
    def run_spec(self, directory, entries, qa=False):
        analysis = SimpleNamespace(datas=list(entries), binaries=list(entries),
                                   pure=[], scripts=[])
        collect = Mock()
        with patch("playwright.__file__", str(Path(directory) / "__init__.py")), \
                patch("PyInstaller.utils.hooks.copy_metadata", return_value=[]), \
                patch("PyInstaller.utils.hooks.collect_submodules", return_value=[]):
            runpy.run_path(str(ROOT / ("YOINK-QA.spec" if qa else "YOINK.spec")),
                           init_globals={"SPECPATH": str(ROOT),
                                         "Analysis": Mock(return_value=analysis),
                                         "PYZ": Mock(), "EXE": Mock(), "COLLECT": collect})
        return analysis, collect

    def test_reused_environment_excludes_only_full_chromium(self):
        with TemporaryDirectory() as directory:
            browser_root = Path(directory) / "driver/package/.local-browsers"
            shell = browser_root / "chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe"
            shell.parent.mkdir(parents=True)
            shell.touch()
            stale = browser_root / "chromium-1243/chrome-win64/chrome.exe"
            stale.parent.mkdir(parents=True)
            stale.touch()
            kept = [
                PREFIX + "chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe",
                PREFIX + "chromium_headless_shell-1243/chrome-headless-shell-win64/locales/en-US.pak",
                PREFIX + "ffmpeg-1011/ffmpeg-win64.exe",
                PREFIX + "winldd-1007/winldd.exe",
                "playwright/driver/package/lib/vite/traceViewer/index.html",
                "PySide6/plugins/platforms/qwindows.dll",
                "PySide6/translations/qtbase_en.qm",
                "assets/icon/yoink.ico",
            ]
            removed = [PREFIX + "chromium-1243/chrome-win64/chrome.exe",
                       (PREFIX + "chromium-1200/chrome-win64/chrome.dll").replace("/", "\\")]
            entries = [(name, "unused-source", "DATA") for name in kept + removed]
            for qa in (False, True, False):  # Product, QA, repeated product build.
                with self.subTest(qa=qa):
                    analysis, collect = self.run_spec(directory, entries, qa)
                    self.assertEqual([entry[0] for entry in analysis.datas], kept)
                    self.assertEqual([entry[0] for entry in analysis.binaries], kept)
                    self.assertEqual(collect.call_args.args[1:],
                                     (analysis.binaries, analysis.datas))
                    self.assertTrue(stale.is_file())
                    self.assertTrue(shell.is_file())

    def test_missing_headless_shell_stops_build(self):
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "headless shell is missing"):
                self.run_spec(directory, [])
