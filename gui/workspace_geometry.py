"""Production attached-workspace bounds and matching organic shell."""
from dataclasses import dataclass
from PySide6.QtCore import QRect, QRectF, QSize
from PySide6.QtGui import QPainterPath
from .window_shape import outer_path


@dataclass(frozen=True)
class WorkspaceGeometry:
    window: QRect
    extract: QRect
    results: QRect
    tool: QRect
    fallback: bool


def clamp_window(rect, available):
    """Keep a target within a work area, including negative screen origins."""
    rect = QRect(rect)
    rect.moveLeft(max(available.left(), min(rect.x(), available.right()-rect.width()+1)))
    rect.moveTop(max(available.top(), min(rect.y(), available.bottom()-rect.height()+1)))
    return rect


def centered_window(size, anchor, available):
    """Redistribute growth around the current placement; clamp only as needed."""
    rect = QRect(anchor.topLeft(), size)
    rect.translate((anchor.width()-size.width())//2, (anchor.height()-size.height())//2)
    return clamp_window(rect, available)


def plan_workspace(available, anchor, tool='picker', extract_width=372, results_width=372):
    tw, th = {'picker': (500,300), 'preview': (600,550), 'scratchpad': (600,420)}[tool]
    h = min(anchor.height(), available.height())
    if available.width() < 640 or h < 440:
        raise ValueError('Work area too small for usable Extract and workspace panels')
    # Moderate widths share the reduction; do not collapse at a preferred-size threshold.
    deficit = max(0, 28 + extract_width + results_width + tw + 32 - available.width())
    ew = max(300, extract_width - deficit // 3)
    rw = max(300, results_width - deficit // 3)
    tw = min(tw, available.width() - 28 - ew - rw - 32)
    fallback = tw < 340
    if fallback:
        ew = min(extract_width, (available.width()-44)//2)
        rw = available.width()-44-ew
        tw = rw
    width = 28 + ew + 16 + rw + (0 if fallback else 16+tw)
    window = centered_window(QSize(width,h), anchor, available)
    extract = QRect(14,(h-min(393,h-48))//2,ew,min(393,h-48))
    results = QRect(extract.right()+17,32,rw,h-52)
    rect = QRect(results if fallback else QRect(results.right()+17,(h-min(th,h-84))//2,tw,min(th,h-84)))
    return WorkspaceGeometry(window,extract,results,rect,fallback)


def workspace_path(plan):
    """Trace one exterior: the shoulder curves are never hidden by a union.

    Card gaps do not set the shoulder's reach. The curves sweep *above and
    below* the first part of the tool card, so its content remains covered
    while the exterior can form a broad organic division within a 16 px gap.
    Closed workspaces still use MainWindow's original two-lobe path.
    """
    h = plan.window.height()
    base_width = plan.results.right() + 15
    left = plan.extract.right() - 170
    right = plan.results.left() + 6
    if plan.fallback:
        return outer_path(base_width, h, 440, left, right)

    radius = 18.0
    rise = max(0.0, (h - 440) / 2)
    left = min(base_width - radius * 4, max(radius * 2, left))
    right = min(base_width - radius * 2, max(left + 1, right))
    reach = right - left
    t = QRectF(plan.tool)
    # Start beyond the Results card, but finish well into the tool's width.
    # This replaces the old right wall instead of adding a bridge to it.
    root = plan.results.right() + 10.0
    sweep = min(220.0, t.width() * .45)
    landing = t.left() + sweep
    top, bottom = t.top() - 30.0, t.bottom() + 14.0
    edge = t.right() + 12.0
    bulb_radius = 24.0
    p = QPainterPath()
    p.moveTo(radius, rise)
    p.lineTo(left, rise)
    p.cubicTo(left + reach * .60, rise, right - reach * .18, 0, right, 0)
    p.lineTo(root, 0)
    p.cubicTo(root + 48, 0, landing - sweep * .86, top, landing, top)
    p.lineTo(edge - bulb_radius, top)
    p.quadTo(edge, top, edge, top + bulb_radius)
    p.lineTo(edge, bottom - bulb_radius)
    p.quadTo(edge, bottom, edge - bulb_radius, bottom)
    p.lineTo(landing, bottom)
    p.cubicTo(landing - sweep * .86, bottom, root + 48, h, root, h)
    p.lineTo(right, h)
    p.cubicTo(right - reach * .18, h, left + reach * .60, h - rise, left, h - rise)
    p.lineTo(radius, h - rise)
    p.quadTo(0, h - rise, 0, h - rise - radius)
    p.lineTo(0, rise + radius)
    p.quadTo(0, rise, radius, rise)
    p.closeSubpath()
    return p
