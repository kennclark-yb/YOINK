"""Matte two-lobe outline shared by painting and native input clipping."""
from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainterPath


def outer_path(width, height, compact_height, left_edge, right_edge, maximized=False):
    path = QPainterPath()
    rect = QRectF(0, 0, max(1, width), max(1, height))
    if maximized:
        path.addRect(rect)
        return path
    rise = max(0.0, (height - compact_height) / 2)
    if rise < .5:
        path.addRoundedRect(rect, 18, 18)
        return path
    r = 18.0
    left_edge = min(width-r*4, max(r * 2, left_edge))
    right_edge = min(width - r * 2, max(left_edge + 1, right_edge))
    reach = right_edge - left_edge
    bottom = height - rise
    path.moveTo(r, rise)
    path.lineTo(left_edge, rise)
    path.cubicTo(left_edge + reach * .60, rise,
                 right_edge - reach * .18, 0, right_edge, 0)
    path.lineTo(width-r, 0)
    path.quadTo(width, 0, width, r)
    path.lineTo(width, height-r)
    path.quadTo(width, height, width-r, height)
    path.lineTo(right_edge, height)
    path.cubicTo(right_edge - reach * .18, height,
                 left_edge + reach * .60, bottom, left_edge, bottom)
    path.lineTo(r, bottom)
    path.quadTo(0, bottom, 0, bottom-r)
    path.lineTo(0, rise+r)
    path.quadTo(0, rise, r, rise)
    path.closeSubpath()
    return path
