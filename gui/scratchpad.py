"""Small provenance map for paragraph breaks lost by Qt plain-text insertion.

Positions are UTF-16 offsets, as used by QTextDocument.contentsChange. Only
lossy breaks need source storage; NBSP, line separators and all other text
are copied from toRawText(), avoiding toPlainText() normalization.
"""
import re

from PySide6.QtCore import QMimeData, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit


class ScratchpadEdit(QPlainTextEdit):
    fidelityBoundaryReached = Signal()

    def __init__(self):
        super().__init__()
        self._source_breaks = {}
        self.document().contentsChange.connect(self._track_edit)

    def _track_edit(self, position, removed, added):
        updated = {}
        lost = False
        for offset, source in self._source_breaks.items():
            if offset < position:
                updated[offset] = source
            elif offset >= position + removed:
                updated[offset + added - removed] = source
            else:
                lost = True
        self._source_breaks = updated
        if lost:
            self.fidelityBoundaryReached.emit()

    def insert_exact(self, cursor, text):
        """Insert source text and remember only breaks Qt cannot distinguish."""
        start = cursor.position()
        cursor.insertText(text)
        normalized = re.sub(r"\r\n|[\r\n\u2029]", "\u2029", text)
        check = QTextCursor(self.document())
        check.setPosition(start)
        check.setPosition(cursor.position(), QTextCursor.MoveMode.KeepAnchor)
        if check.selectedText() != normalized:
            # Fail closed: never substitute source into an unverified range.
            self.fidelityBoundaryReached.emit()
            return False
        offset = start
        previous = 0
        for match in re.finditer(r"\r\n|[\r\n\u2029]", text):
            offset += len(text[previous:match.start()].encode("utf-16-le")) // 2
            self._source_breaks[offset] = match.group()
            offset += 1
            previous = match.end()
        return True

    def createMimeDataFromSelection(self):
        # Qt's lazy selection MIME object can regenerate normalized text even
        # after setText(); use an explicit plain-text payload instead.
        mime = QMimeData()
        cursor = self.textCursor()
        mime.setText(self.exact_text(cursor.selectionStart(), cursor.selectionEnd()))
        return mime

    def exact_text(self, start=0, end=None):
        chunks = []
        offset = 0
        for char in self.document().toRawText():
            if offset >= start and (end is None or offset < end):
                chunks.append(self._source_breaks.get(offset, "\n") if char == "\u2029" else char)
            offset += 2 if ord(char) > 0xffff else 1
        return "".join(chunks)
