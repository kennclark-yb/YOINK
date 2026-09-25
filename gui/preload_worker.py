from PySide6.QtCore import QObject, Signal, Slot

from extract import (
    ExtractionError,
    extract_conversation,
)


class PreloadWorker(QObject):
    finished = Signal(int, object)
    error = Signal(int, str)

    def __init__(self, version, url):
        super().__init__()

        self.version = version
        self.url = url

    @Slot()
    def run(self):
        try:
            extraction = extract_conversation(
                self.url,
                "both",
            )

            self.finished.emit(
                self.version,
                extraction,
            )

        except (
            ExtractionError,
            ValueError,
            TypeError,
        ) as e:
            self.error.emit(
                self.version,
                str(e),
            )