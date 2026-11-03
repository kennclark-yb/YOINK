import unittest
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QApplication
from gui.bracket_button import draw_brackets
APP=QApplication.instance() or QApplication([])
class Recorder:
    def __init__(self): self.calls=[]
    def fontMetrics(self): return None
    def drawText(self,rect,align,text): self.calls.append((rect,text))
class BracketGeometryTests(unittest.TestCase):
    def test_fixed_anchors_and_centered_labels(self):
        anchors=[]
        for text in ('[ PREVIEW ]','[ PARTS PICKER ]','[ SCRATCHPAD ]','[ COPY ALL ]','[ UNDO APPEND ]'):
            p=Recorder(); draw_brackets(p,QRectF(0,0,98,32),text)
            self.assertEqual([c[1] for c in p.calls],['[',']',text[2:-2]])
            anchors.append((p.calls[0][0].left(),p.calls[1][0].right(),p.calls[2][0].center().x()))
        self.assertEqual(len(set(anchors)),1)
