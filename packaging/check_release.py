"""Separate QA executable, never shipped as part of the YOINK product."""
import unittest
from gui.application import configure_application
from test_phase2a import APP
import test_phase2a
import test_message_filter
import test_release

configure_application(APP)
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(module)
                           for module in (test_phase2a, test_message_filter, test_release))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
