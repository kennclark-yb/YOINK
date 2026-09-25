from PySide6.QtCore import QObject, Signal, Slot

from extract import (
    ExtractionError,
    extract_conversation,
    build_filtered_conversation,
)
from formatter import (
    format_markdown,
    split_parts,
    split_parts_by_count,
)


class ExtractionWorker(QObject):
    progress = Signal(str, int)
    finished = Signal(object)
    error = Signal(str)

    def __init__(
        self,
        url,
        mode,
        split_mode,
        split_value,
        preloaded_extraction=None,
    ):
        super().__init__()

        self.url = url
        self.mode = mode
        self.split_mode = split_mode
        self.split_value = split_value
        self.preloaded_extraction = preloaded_extraction

    @Slot()
    def run(self):
        try:
            self.progress.emit(
                "LOADING PAGE",
                10,
            )

            if self.preloaded_extraction is not None:
                full_conversation = self.preloaded_extraction[
                    "full_conversation"
                ]

                conversation = build_filtered_conversation(
                    full_conversation["platform"],
                    full_conversation["title"],
                    full_conversation["url"],
                    full_conversation["messages"],
                    self.mode,
                )
            else:
                extraction = extract_conversation(
                    self.url,
                    self.mode,
                )

                full_conversation = extraction[
                    "full_conversation"
                ]

                conversation = extraction[
                    "conversation"
                ]

            self.progress.emit(
                "EXTRACTING MESSAGES",
                60,
            )

            markdown = format_markdown(
                conversation
            )

            self.progress.emit(
                "FORMATTING",
                80,
            )

            if self.split_mode == "Character Limit":
                max_chars = (
                    int(self.split_value)
                    if self.split_value
                    else 9000
                )

                parts = split_parts(
                    conversation,
                    max_chars=max_chars,
                )

            else:
                if not self.split_value:
                    raise ValueError(
                        "Enter the number of parts."
                    )

                parts = split_parts_by_count(
                    conversation,
                    int(self.split_value),
                )

            self.progress.emit(
                "SPLITTING",
                90,
            )

            self.finished.emit(
                {
                    "conversation": full_conversation,
                    "extracted_conversation": conversation,
                    "markdown": markdown,
                    "parts": parts,
                    "mode": self.mode,
                }
            )

        except (
            ExtractionError,
            ValueError,
            TypeError,
        ) as e:
            self.error.emit(str(e))