"""Exercise share readiness and retries without public network access."""
import json
import unittest
from unittest.mock import Mock

from playwright.sync_api import TimeoutError, sync_playwright

from extract import ExtractionError, load_share_page


URL = "https://chatgpt.com/share/loading-test"
UPSTREAM_ERROR = {"type": "error", "error": "Can't load shared conversation test-id"}
UNAVAILABLE = "ChatGPT says nope. This share link's busted."
GENERIC = "ChatGPT page failed to load after 3 attempts."


class ShareLoadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.pages = []

    def tearDown(self):
        for page in self.pages:
            page.close()

    def attempts(self, responses, failure_stage=None):
        responses = iter(responses)

        def new_page():
            response = next(responses)
            page = self.browser.new_page()
            self.pages.append(page)
            state = {"state": {"loaderData": {
                "routes/share.$shareId.($action)": {"serverResponse": response}
            }}}
            html = "<script>window.__reactRouterContext=" + json.dumps(state) + ";</script>"
            page.route(URL, lambda route: route.fulfill(body=html, content_type="text/html"))
            wrapped = Mock(wraps=page)
            if response is None and failure_stage:
                getattr(wrapped, failure_stage).side_effect = TimeoutError("Synthetic timeout")
            return wrapped

        return Mock(new_page=Mock(side_effect=new_page))

    def assert_failure(self, browser, message):
        with self.assertRaises(ExtractionError) as caught:
            load_share_page(browser, URL)
        self.assertEqual(str(caught.exception), message)
        self.assertEqual(browser.new_page.call_count, 3)
        self.assertTrue(all(page.is_closed() for page in self.pages))

    def test_data_returns_open_page_with_original_navigation_and_wait_limits(self):
        browser = self.attempts([{"data": {"mapping": {}}}])
        page = load_share_page(browser, URL)
        self.assertEqual(browser.new_page.call_count, 1)
        self.assertFalse(self.pages[0].is_closed())
        page.goto.assert_called_once_with(URL, wait_until="commit", timeout=10000)
        self.assertEqual(page.wait_for_function.call_args.kwargs, {"timeout": 10000})

    def test_repeated_explicit_errors_retry_three_times_and_report_unavailable(self):
        self.assert_failure(self.attempts([UPSTREAM_ERROR] * 3), UNAVAILABLE)

    def test_explicit_error_retries_and_later_data_succeeds(self):
        browser = self.attempts([UPSTREAM_ERROR, {"data": {"mapping": {}}}])
        load_share_page(browser, URL)
        self.assertEqual(browser.new_page.call_count, 2)
        self.assertTrue(self.pages[0].is_closed())
        self.assertFalse(self.pages[1].is_closed())

    def test_navigation_timeouts_remain_generic_after_three_attempts(self):
        self.assert_failure(self.attempts([None] * 3, "goto"), GENERIC)

    def test_readiness_timeouts_remain_generic_after_three_attempts(self):
        self.assert_failure(self.attempts([None] * 3, "wait_for_function"), GENERIC)

    def test_mixed_explicit_error_and_timeout_remains_generic(self):
        browser = self.attempts([UPSTREAM_ERROR, None, UPSTREAM_ERROR], "goto")
        self.assert_failure(browser, GENERIC)

    def test_data_takes_precedence_over_error_fields(self):
        browser = self.attempts([{**UPSTREAM_ERROR, "data": {"mapping": {}}}])
        load_share_page(browser, URL)
        self.assertEqual(browser.new_page.call_count, 1)
        self.assertFalse(self.pages[0].is_closed())


if __name__ == "__main__":
    unittest.main()
