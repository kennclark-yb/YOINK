"""Native Windows shutdown ownership and z-order regression checks."""
import ctypes
import os
import sys
import unittest
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid

from test_phase2a import APP, advance
from gui.main_window import MainWindow

NATIVE = sys.platform == 'win32' and APP.platformName() == 'windows'
if NATIVE:
    u = ctypes.windll.user32
    u.GetWindow.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    u.GetWindow.restype = ctypes.c_void_p
    u.GetForegroundWindow.restype = ctypes.c_void_p
    u.GetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int]
    u.GetWindowLongW.restype = ctypes.c_long
    u.IsWindow.argtypes = [ctypes.c_void_p]
    u.IsWindowVisible.argtypes = [ctypes.c_void_p]
    u.IsIconic.argtypes = [ctypes.c_void_p]
    u.SetForegroundWindow.argtypes = [ctypes.c_void_p]
    u.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]


def below(hwnd):
    result = []
    cursor = u.GetWindow(hwnd, 2)  # GW_HWNDNEXT, toward the bottom
    while cursor and cursor not in result:
        result.append(cursor)
        cursor = u.GetWindow(cursor, 2)
    return result


@unittest.skipUnless(NATIVE, 'requires native Windows Qt platform')
class NativeShutdownTests(unittest.TestCase):
    def setUp(self):
        self.update = patch('gui.updates.UpdateChecker.check')
        self.update.start()
        self.w = MainWindow()
        self.w.show()
        advance(30)

    def tearDown(self):
        if isValid(self.w):
            self.w._closing = True
            self.w._finish_shutdown()
            self.w.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.update.stop()

    def test_owned_non_topmost_visible_and_disposed(self):
        w = self.w
        self.assertIsNone(w._shutdown_screen)
        w.close()
        screen = w._shutdown_screen
        hwnd, owner = int(screen.winId()), int(w.winId())
        advance(30)
        style = u.GetWindowLongW(hwnd, -20)
        actual_owner = u.GetWindow(hwnd, 4)  # GW_OWNER
        foreground = u.GetForegroundWindow()
        print(f'native owner test: screen={hwnd} owner={owner} actual_owner={actual_owner} exstyle=0x{style & 0xffffffff:08x} foreground={foreground} visible={u.IsWindowVisible(hwnd)} owner_below={owner in below(hwnd)}')
        self.assertEqual(actual_owner, owner)
        self.assertFalse(style & 0x8, 'WS_EX_TOPMOST must be absent')
        self.assertTrue(style & 0x80000, 'translucent CRT must remain layered')
        self.assertTrue(u.IsWindowVisible(hwnd))
        self.assertTrue(w._shutdown_overlay.isVisible())
        self.assertIn(owner, below(hwnd), 'CRT must be above its owner and overlay')
        w.close()
        self.assertFalse(w._shutdown_complete)
        w._finish_shutdown()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.assertFalse(u.IsWindow(hwnd))
        self.assertFalse(isValid(screen))
        self.assertIsNone(w._shutdown_screen)

    def test_minimize_and_restore_preserve_ownership(self):
        w = self.w
        w.close()
        screen = w._shutdown_screen
        hwnd, owner = int(screen.winId()), int(w.winId())
        w.showMinimized()
        advance(80)
        minimized = bool(u.IsIconic(owner))
        minimized_visible = bool(u.IsWindowVisible(hwnd))
        w.showNormal()
        advance(80)
        print(f'native minimize: screen={hwnd} owner={owner} iconic={minimized} screen_visible_minimized={minimized_visible} restored_visible={bool(u.IsWindowVisible(hwnd))} foreground={u.GetForegroundWindow()}')
        self.assertTrue(minimized)
        self.assertFalse(u.IsIconic(owner))
        self.assertEqual(u.GetWindow(hwnd, 4), owner)
        self.assertTrue(u.IsWindowVisible(hwnd))

    def test_existing_external_foreground_is_above_crt(self):
        w = self.w
        w.close()
        hwnd = int(w._shutdown_screen.winId())
        advance(30)
        foreground = u.GetForegroundWindow()
        pid = ctypes.c_ulong()
        u.GetWindowThreadProcessId(foreground, ctypes.byref(pid))
        print(f'native external foreground: screen={hwnd} owner={int(w.winId())} foreground={foreground} foreground_pid={pid.value} foreground_below={foreground in below(hwnd)}')
        if not foreground or pid.value == os.getpid():
            self.skipTest('No independent foreground process available')
        self.assertNotIn(foreground, below(hwnd))
        self.assertIn(hwnd, below(foreground))

    def test_foreground_independent_window_covers_crt(self):
        w = self.w
        w.close()
        screen = w._shutdown_screen
        hwnd = int(screen.winId())
        other = QWidget()
        other.setWindowTitle('Independent shutdown stacking test')
        other.resize(400, 300)
        try:
            other.show()
            other.raise_()
            other.activateWindow()
            ohwnd = int(other.winId())
            u.SetForegroundWindow(ohwnd)
            advance(100)
            foreground = u.GetForegroundWindow()
            print(f'native switch test: screen={hwnd} other={ohwnd} foreground={foreground} exstyle=0x{u.GetWindowLongW(hwnd,-20) & 0xffffffff:08x} other_below={ohwnd in below(hwnd)}')
            if foreground != ohwnd:
                self.skipTest('Windows did not grant foreground to test window')
            self.assertNotIn(ohwnd, below(hwnd), 'CRT is above the unrelated foreground window')
            self.assertIn(hwnd, below(ohwnd))
        finally:
            other.close()
            other.deleteLater()
