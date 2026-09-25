"""Exercise the real browser extraction script against synthetic shared-page state."""
import unittest

from playwright.sync_api import sync_playwright

from extract import extract_chat, filter_messages, build_conversation
from formatter import format_markdown, split_parts, split_parts_by_count


PLACEHOLDER = "The output of this plugin was redacted."


class MessageFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def extract(self, messages):
        page = self.browser.new_page()
        try:
            mapping = {
                str(index): {"message": {
                    "author": {"role": role},
                    "content": {"content_type": "text", "parts": parts},
                }}
                for index, (role, parts) in enumerate(messages)
            }
            page.evaluate("""mapping => {
                window.__reactRouterContext = {state: {loaderData: {
                    "routes/share.$shareId.($action)": {serverResponse: {data: {mapping}}}
                }}};
            }""", mapping)
            return extract_chat(page)
        finally:
            page.close()

    def test_omits_only_empty_ai_and_standalone_placeholder(self):
        retained_ai = [
            "  Keep my whitespace.\n\n",
            "This message explains why output was redacted.",
            f"The placeholder says: {PLACEHOLDER}",
            f"```text\n{PLACEHOLDER}\n```",
            "A short reply.",
        ]
        messages = self.extract([
            ("assistant", [""]),
            ("assistant", [" \t\r\n "]),
            ("assistant", ["", "  "]),
            ("assistant", [PLACEHOLDER]),
            ("assistant", [f" \n{PLACEHOLDER}\n "]),
            *[("assistant", [text]) for text in retained_ai],
            ("user", [""]),
            ("user", [PLACEHOLDER]),
            ("user", [" \n "]),
        ])
        self.assertEqual([m["id"] for m in messages], [str(i) for i in range(5, 13)])
        self.assertEqual([m["text"] for m in messages], retained_ai + ["", PLACEHOLDER, " \n "])

    def test_retained_parts_are_not_rewritten(self):
        parts = ["  First\n", "```python\nprint('redacted')\n```  "]
        messages = self.extract([("assistant", parts)])
        self.assertEqual(messages[0]["text"], "\n".join(parts))

    def test_modes_and_formatters_receive_contiguous_filtered_messages(self):
        messages = self.extract([
            ("assistant", [""]), ("user", ["Question"]),
            ("assistant", [PLACEHOLDER]), ("assistant", ["Answer one"]),
            ("assistant", [" \n "]), ("assistant", ["Answer two"]),
        ])
        self.assertEqual(len(filter_messages(messages, "both")), 3)
        self.assertEqual(len(filter_messages(messages, "user")), 1)
        conversation = build_conversation("ChatGPT", "Test", "test", filter_messages(messages, "assistant"))
        expected = "### [msg 001] The AI\n\nAnswer one\n\n---\n\n### [msg 002] The AI\n\nAnswer two"
        self.assertEqual(format_markdown(conversation), expected)
        for parts in (split_parts(conversation, 1), split_parts_by_count(conversation, 2)):
            self.assertEqual(parts, [
                "### [msg 001] The AI\n\nAnswer one",
                "### [msg 002] The AI\n\nAnswer two",
            ])


if __name__ == "__main__":
    unittest.main()
