"""Offline selection contracts using synthetic conversations only."""
import copy
from dataclasses import FrozenInstanceError
import time
import tracemalloc
import unittest

from context_selection import ContextSelection, MessageRange
from formatter import format_markdown


def conversation(count):
    return {"title": "Synthetic", "extra": {"source": "fixture"}, "messages": [
        {"id": f"id-{i}", "role": "user" if i % 2 == 0 else "assistant",
         "text": f"Message {i}", "metadata": {"index": i}} for i in range(count)]}


class ContextSelectionTests(unittest.TestCase):
    def test_empty_conversation(self):
        selection = ContextSelection(0)
        result = selection.resolve(conversation(0))
        self.assertEqual(result.status, "empty_selection")
        self.assertEqual((result.selected_count, result.coverage, result.output_coverage), (0, 0, 0))
        self.assertEqual(result.to_markdown(), "")
        self.assertEqual(result.as_conversation()["messages"], [])
        for name in ("final_quarter", "final_half", "final_three_quarters", "first_half"):
            self.assertEqual(selection.preset(name).ranges, ())

    def test_single_message_presets(self):
        for name in ("final_quarter", "final_half", "final_three_quarters", "first_half"):
            self.assertEqual(ContextSelection(1).preset(name).ranges, (MessageRange(0, 1),))

    def test_all_presets_odd_even_boundaries(self):
        # Literal expected endpoints independently specify the rounding contract.
        expected = {
            2: [(1, 2), (1, 2), (0, 2), (0, 1)],
            4: [(3, 4), (2, 4), (1, 4), (0, 2)],
            5: [(3, 5), (2, 5), (1, 5), (0, 3)],
            7: [(5, 7), (3, 7), (1, 7), (0, 4)],
            8: [(6, 8), (4, 8), (2, 8), (0, 4)],
        }
        for count, ranges in expected.items():
            for name, endpoints in zip(
                    ("final_quarter", "final_half", "final_three_quarters", "first_half"), ranges):
                with self.subTest(count=count, name=name):
                    self.assertEqual(ContextSelection(count).preset(name).ranges,
                                     (MessageRange(*endpoints),))

    def test_manual_positions_and_display_conversion(self):
        selection = ContextSelection(6).select_message(4)
        self.assertEqual(selection.ranges, (MessageRange(4, 5),))
        self.assertEqual(selection.select_display(2, 4).ranges, (MessageRange(1, 4),))
        self.assertEqual(MessageRange.from_display(2, 4, 6).to_display(), (2, 4))
        self.assertEqual(selection.select_message(0, add=True).selected_count, 2)
        self.assertEqual(selection.select_display(1, 1, add=True).selected_count, 2)

    def test_replace_versus_add_and_immutability(self):
        original = ContextSelection(10).replace(1, 3)
        self.assertEqual(original.add(7, 9).selected_count, 4)
        self.assertEqual(original.replace(7, 9).ranges, (MessageRange(7, 9),))
        self.assertEqual(original.ranges, (MessageRange(1, 3),))
        with self.assertRaises(FrozenInstanceError):
            original.message_count = 20
        with self.assertRaises(FrozenInstanceError):
            original.ranges[0].end = 9

    def test_remove_split_trim_and_clear(self):
        selection = ContextSelection(10).replace(1, 9)
        self.assertEqual(selection.remove(3, 6).ranges,
                         (MessageRange(1, 3), MessageRange(6, 9)))
        self.assertEqual(selection.remove(0, 4).ranges, (MessageRange(4, 9),))
        self.assertEqual(selection.remove(5, 10).ranges, (MessageRange(1, 5),))
        self.assertEqual(selection.remove(0, 10).ranges, ())
        self.assertEqual(selection.remove(4, 4), selection)
        self.assertEqual(selection.remove(9, 10), selection)
        self.assertEqual(selection.clear().ranges, ())

    def test_merging_overlaps_adjacent_duplicates(self):
        selection = ContextSelection(10).add(5, 8).add(2, 6).add(8, 9).add(2, 6)
        self.assertEqual(selection.ranges, (MessageRange(2, 9),))
        self.assertEqual(selection.selected_count, 7)

    def test_disconnected_reverse_order_and_chronology(self):
        selection = ContextSelection(10).add(8, 10).add(1, 3).add(5, 6).add(1, 2)
        result = selection.resolve(conversation(10))
        self.assertEqual([m.source_position for m in result.messages], [1, 2, 5, 8, 9])
        self.assertEqual([m.source_number for m in result.messages], [2, 3, 6, 9, 10])
        self.assertEqual([m.message["id"] for m in result.messages],
                         ["id-1", "id-2", "id-5", "id-8", "id-9"])
        self.assertEqual((selection.coverage, result.coverage), (0.5, 0.5))

    def test_role_filter_after_preset(self):
        source = conversation(5)
        selection = ContextSelection(5).preset("final_half")
        for role, positions in (("both", [2, 3, 4]), ("assistant", [3]), ("user", [2, 4])):
            with self.subTest(role=role):
                result = selection.resolve(source, role)
                self.assertEqual([m.source_position for m in result.messages], positions)
                self.assertEqual(result.selected_count, len(positions))
                self.assertEqual(result.range_count, 3)
                self.assertEqual(result.coverage, 3 / 5)
                self.assertEqual(result.output_coverage, len(positions) / 5)
                self.assertEqual(result.status, "selected")

    def test_no_role_match_and_empty_selection(self):
        result = ContextSelection(3).select_message(0).resolve(conversation(3), "assistant")
        self.assertEqual(result.status, "no_role_match")
        self.assertEqual(result.selected_count, 0)
        self.assertEqual(result.range_count, 1)
        self.assertEqual(result.to_markdown(), "")
        self.assertEqual(ContextSelection(3).resolve(conversation(3)).status, "empty_selection")

    def test_exact_unicode_multiline_and_long_messages(self):
        text = "  😀 café e\u0301 中文\t\r\n\n```python\npass\n```  \n" + "長" * 1_000_000
        source = conversation(1)
        source["messages"][0]["text"] = text
        for name in ("final_quarter", "final_half", "final_three_quarters", "first_half"):
            result = ContextSelection(1).preset(name).resolve(source)
            self.assertIs(result.messages[0].message["text"], text)
            self.assertEqual(result.to_markdown(), "### [msg 001] The User\n\n" + text)

    def test_metadata_and_source_unchanged(self):
        source = conversation(5)
        before = copy.deepcopy(source)
        result = ContextSelection(5).add(0, 2).add(4, 5).resolve(source)
        output = result.as_conversation()
        self.assertEqual(output["title"], source["title"])
        self.assertEqual(output["extra"], source["extra"])
        self.assertEqual(output["messages"][1], source["messages"][1])
        output["title"] = "Changed"
        output["messages"][0]["text"] = "Changed"
        self.assertEqual(source, before)
        with self.assertRaises(TypeError):
            result.messages[0].message["text"] = "Changed"

    def test_markdown_adapter_retains_gaps_and_v1_compatibility(self):
        source = conversation(6)
        self.assertEqual(ContextSelection(6).replace(0, 6).resolve(source).to_markdown(),
                         format_markdown(source))
        result = ContextSelection(6).add(0, 2).add(4, 6).resolve(source, "assistant")
        self.assertEqual(result.to_markdown(),
                         "### [msg 002] The AI\n\nMessage 1\n\n---\n\n"
                         "### [msg 006] The AI\n\nMessage 5")
        self.assertEqual(format_markdown({"messages": [source["messages"][5]]}),
                         "### [msg 001] The AI\n\nMessage 5")

    def test_duplicate_ids_and_text_do_not_deduplicate_distinct_positions(self):
        source = {"messages": [{"id": "same", "role": "user", "text": "same"}] * 3}
        result = ContextSelection(3).add(0, 3).add(1, 2).resolve(source)
        self.assertEqual([m.source_number for m in result.messages], [1, 2, 3])

    def test_empty_ranges_and_preset_replace(self):
        selection = ContextSelection(5).add(1, 3)
        self.assertEqual(selection.add(5, 5), selection)
        self.assertEqual(selection.replace(2, 2).ranges, ())
        self.assertEqual(selection.preset("final_quarter").ranges, (MessageRange(3, 5),))

    def test_invalid_ranges_and_counts(self):
        for value in (True, False, 1.5, "2", None, -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                ContextSelection(value)
        for start, end in ((-1, 2), (3, 2), (0, 6), (6, 6), (True, 2),
                           (0, False), (0.0, 2), (0, "2"), (None, 2)):
            for method in ("add", "replace", "remove"):
                with self.subTest(start=start, end=end, method=method), self.assertRaises(ValueError):
                    getattr(ContextSelection(5), method)(start, end)
        with self.assertRaises(ValueError):
            ContextSelection(5, ((1, 2),))

    def test_invalid_manual_display_and_preset(self):
        selection = ContextSelection(5)
        for position in (-1, 5, True, 1.5, "1", None):
            with self.assertRaises(ValueError):
                selection.select_message(position)
        for first, last in ((0, 1), (3, 2), (1, 6), (True, 2), (1, "2"), (1.5, 2)):
            with self.assertRaises(ValueError):
                selection.select_display(first, last)
        with self.assertRaises(ValueError):
            MessageRange(1, 1).to_display()
        for name in ("bad", None, []):
            with self.assertRaises(ValueError):
                selection.preset(name)

    def test_invalid_role_and_mismatched_source(self):
        for role in ("all", "", None, []):
            with self.assertRaises(ValueError):
                ContextSelection(2).resolve(conversation(2), role)
        with self.assertRaises(ValueError):
            ContextSelection(3).resolve(conversation(2))

    def test_other_roles_retained_by_both_only(self):
        source = {"messages": [{"id": "tool", "role": "tool", "text": "synthetic"}]}
        self.assertEqual(ContextSelection(1).replace(0, 1).resolve(source).selected_count, 1)
        self.assertEqual(ContextSelection(1).replace(0, 1).resolve(source, "user").status,
                         "no_role_match")

    def test_large_source_runtime_memory_and_text_sharing(self):
        source = conversation(50_000)
        text = "x" * 100_000
        for message in source["messages"]:
            message["text"] = text
        tracemalloc.start()
        try:
            started = time.perf_counter()
            result = ContextSelection(50_000).add(40_000, 50_000).add(0, 10_000).resolve(source)
            elapsed = time.perf_counter() - started
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(result.selected_count, 20_000)
        self.assertEqual(result.messages[-1].source_position, 49_999)
        self.assertTrue(all(m.message["text"] is text for m in result.messages))
        self.assertLess(elapsed, 10, "selection should not scan/copy message text")
        self.assertLess(peak, 32 * 1024 * 1024, "selection should share large text objects")


if __name__ == "__main__":
    unittest.main()
