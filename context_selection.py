"""GUI-independent selection over a complete, already-extracted conversation.

All internal positions are zero-based and ranges are half-open [start, end).
Selections are immutable and initially empty. Presets replace the selection,
rounding lower boundaries down and upper boundaries up using integer arithmetic.
Thus odd halves overlap at the middle message; every nonempty source has at
least one message in every preset. Empty ranges are valid no-ops (replace clears).

Resolution shallow-copies dictionaries, preserving text objects and metadata.
Nested metadata is shared, not recursively frozen: callers must treat it as
read-only. No source dictionaries are mutated. Source positions refer to the
complete extracted messages list, never IDs or a role-filtered list. Callers
must resolve against that same source snapshot (length is checked).
"""
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


def _integer(value, name):
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")


@dataclass(frozen=True, order=True)
class MessageRange:
    start: int
    end: int

    def __post_init__(self):
        _integer(self.start, "start")
        _integer(self.end, "end")
        if not 0 <= self.start <= self.end:
            raise ValueError("range requires 0 <= start <= end")

    @classmethod
    def from_display(cls, first, last, message_count):
        """Convert one-based inclusive numeric UI endpoints; reject empty input."""
        _integer(first, "first")
        _integer(last, "last")
        _count(message_count)
        if not 1 <= first <= last <= message_count:
            raise ValueError("display range must be within 1..message_count")
        return cls(first - 1, last)

    def to_display(self):
        """Return one-based inclusive endpoints; empty ranges have no display."""
        if self.start == self.end:
            raise ValueError("empty range has no inclusive display endpoints")
        return self.start + 1, self.end


def _count(value):
    _integer(value, "message_count")
    if value < 0:
        raise ValueError("message_count must be nonnegative")


@dataclass(frozen=True)
class SelectedMessage:
    source_position: int
    message: Mapping

    @property
    def source_number(self):
        return self.source_position + 1


@dataclass(frozen=True)
class SelectionResult:
    messages: tuple
    source_metadata: Mapping
    source_count: int
    range_count: int
    role: str

    @property
    def selected_count(self):
        """Output count after role filtering."""
        return len(self.messages)

    @property
    def coverage(self):
        """Fraction of source positions selected before role filtering (0..1)."""
        return self.range_count / self.source_count if self.source_count else 0.0

    @property
    def output_coverage(self):
        return self.selected_count / self.source_count if self.source_count else 0.0

    @property
    def status(self):
        if not self.range_count:
            return "empty_selection"
        return "selected" if self.messages else "no_role_match"

    def as_conversation(self):
        """Shallow-copy source metadata/messages; use to_markdown for numbering.

        A plain conversation list cannot encode gaps for the v1 formatter.
        Source positions remain in this result's SelectedMessage wrappers.
        """
        return {**self.source_metadata,
                "messages": [dict(item.message) for item in self.messages]}

    def to_markdown(self):
        """Reuse v1 formatting per message with its original source number."""
        from formatter import format_markdown

        return "\n\n---\n\n".join(
            format_markdown({"messages": [item.message]},
                            start_index=item.source_number)
            for item in self.messages
        )


@dataclass(frozen=True)
class ContextSelection:
    message_count: int
    ranges: tuple = ()

    def __post_init__(self):
        _count(self.message_count)
        normalized = []
        for item in self.ranges:
            if not isinstance(item, MessageRange):
                raise ValueError("ranges must contain MessageRange values")
            self._validate(item)
            if item.start != item.end:
                normalized.append(item)
        merged = []
        for item in sorted(normalized):
            if merged and item.start <= merged[-1].end:
                previous = merged.pop()
                item = MessageRange(previous.start, max(previous.end, item.end))
            merged.append(item)
        object.__setattr__(self, "ranges", tuple(merged))

    def _validate(self, item):
        if item.end > self.message_count:
            raise ValueError("range exceeds source message count")

    @property
    def selected_count(self):
        """Count before role filtering."""
        return sum(item.end - item.start for item in self.ranges)

    @property
    def coverage(self):
        return self.selected_count / self.message_count if self.message_count else 0.0

    def add(self, start, end):
        return ContextSelection(self.message_count,
                                self.ranges + (MessageRange(start, end),))

    def replace(self, start, end):
        return ContextSelection(self.message_count, (MessageRange(start, end),))

    def clear(self):
        return ContextSelection(self.message_count)

    def remove(self, start, end):
        removed = MessageRange(start, end)
        self._validate(removed)
        remaining = []
        for item in self.ranges:
            if removed.end <= item.start or removed.start >= item.end:
                remaining.append(item)
            else:
                if item.start < removed.start:
                    remaining.append(MessageRange(item.start, removed.start))
                if removed.end < item.end:
                    remaining.append(MessageRange(removed.end, item.end))
        return ContextSelection(self.message_count, tuple(remaining))

    def select_message(self, position, *, add=False):
        """Select one zero-based source position, replacing unless add=True."""
        _integer(position, "position")
        return (self.add if add else self.replace)(position, position + 1)

    def select_display(self, first, last, *, add=False):
        item = MessageRange.from_display(first, last, self.message_count)
        return (self.add if add else self.replace)(item.start, item.end)

    def preset(self, name):
        """Replace with a message-count preset; no message text is split."""
        bounds = {"final_quarter": (3, 4), "final_half": (2, 4),
                  "final_three_quarters": (1, 4), "first_half": (0, 2)}
        if not isinstance(name, str) or name not in bounds:
            raise ValueError("unknown fraction preset")
        lower, upper = bounds[name]
        return self.replace(self.message_count * lower // 4,
                            (self.message_count * upper + 3) // 4)

    def resolve(self, conversation, role="both"):
        """Select boundaries first, then filter output by assistant/user/both.

        'both' retains every source role; other values match roles exactly.
        Full extraction is the caller's responsibility. IDs need not be numeric
        or unique: deduplication uses source positions, not IDs or text.
        """
        if role not in ("assistant", "user", "both"):
            raise ValueError("role must be assistant, user or both")
        source = conversation["messages"]
        if len(source) != self.message_count:
            raise ValueError("source length differs from selection message_count")
        messages = tuple(
            SelectedMessage(position, MappingProxyType(dict(source[position])))
            for item in self.ranges for position in range(item.start, item.end)
            if role == "both" or source[position]["role"] == role
        )
        metadata = MappingProxyType({key: value for key, value in conversation.items()
                                     if key != "messages"})
        return SelectionResult(messages, metadata, self.message_count,
                               self.selected_count, role)
