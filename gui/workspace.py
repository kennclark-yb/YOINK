"""One attached workspace and one interruptible geometry animation clock."""
import os
from dataclasses import replace
from PySide6.QtCore import Qt,QRect,QPoint,QSize,QPointF,QVariantAnimation,QEasingCurve
from PySide6.QtGui import QShortcut,QKeySequence,QPixmap,QIcon,QPainter,QPen,QColor
from PySide6.QtWidgets import QFrame,QVBoxLayout,QHBoxLayout,QPushButton,QStackedWidget,QApplication,QLayout,QGraphicsOpacityEffect
from .workspace_geometry import plan_workspace,WorkspaceGeometry,centered_window,clamp_window


class AttachedWorkspace(QFrame):
    def __init__(self, owner):
        super().__init__(owner.background)
        self.owner=owner
        self.plan=None
        self.saved=None
        self.kind=None
        self.phase="closed"
        self._close_callbacks=[]
        self._motion_start=None
        self._motion_end=None
        self.animation=None
        self.animating=False
        self.motion_enabled=QApplication.platformName() != "offscreen" and os.environ.get("YOINK_REDUCED_MOTION") != "1"
        self.setObjectName('AttachedWorkspace')
        self.setStyleSheet('QFrame#AttachedWorkspace { background: rgba(21,22,26,214); border: 1px solid #303137; border-radius: 14px; }')
        layout=QVBoxLayout(self);layout.setContentsMargins(8,6,8,8)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        row=QHBoxLayout()
        self.back=QPushButton()
        arrow=QPixmap(64,36);arrow.setDevicePixelRatio(2);arrow.fill(Qt.GlobalColor.transparent)
        painter=QPainter(arrow);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor('#8AA9FF'),2.4,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
        painter.drawLine(QPointF(4,9),QPointF(28,9))
        painter.drawLine(QPointF(4,9),QPointF(10,3.5));painter.drawLine(QPointF(4,9),QPointF(10,14.5))
        painter.end()
        self.back.setIcon(QIcon(arrow));self.back.setIconSize(QSize(32,18))
        self.back.setFixedSize(42,26)
        self.back.setStyleSheet("""QPushButton { color: #8AA9FF; background: transparent; border: 1px solid transparent; border-radius: 6px; font-size: 21px; font-weight: 700; } QPushButton:hover { background: #253655; } QPushButton:pressed { background: #4D7CFE; color: white; } QPushButton:focus { border-color: #8AA9FF; }""")
        self.back.setToolTip('Back to Results')
        self.back.setAccessibleName('Close workspace and return to Results')
        self.back.clicked.connect(self.collapse)
        row.addWidget(self.back);row.addStretch()
        layout.addLayout(row)
        self.stack=QStackedWidget();layout.addWidget(self.stack,1)
        self.fade=QGraphicsOpacityEffect(self.stack);self.stack.setGraphicsEffect(self.fade)
        self.fade.setOpacity(1)
        self.escape=QShortcut(QKeySequence("Escape"),owner)
        self.escape.activated.connect(self.collapse)
        self.hide()

    def open(self, widget, kind):
        w=self.owner
        if (self.kind==kind and self.phase in ("open","opening")
                and self.stack.currentWidget() is widget and widget.isVisible()):
            return
        self._stop_animation()
        if w._results_animation is not None and w._results_animation.state()==w._results_animation.State.Running:
            w._results_animation.setCurrentTime(w._results_animation.duration())
        starting=self.saved is None
        if starting:
            self.saved=(w.geometry(), w.card.geometry(),w.results_panel.geometry(),w.content_surface.geometry(),w.minimumSize(),w.maximumSize())
        # Saved geometry supplies local dimensions only, never a world position.
        anchor=QRect(w.geometry())
        try:
            plan=plan_workspace(w._results_work_area(),anchor,kind,self.saved[1].width(),self.saved[2].width())
        except ValueError:
            if starting:self.saved=None
            w._show_scratchpad_feedback('Work area too small for the attached workspace.')
            return
        previous=replace(self.plan,window=QRect(w.geometry())) if self.plan else WorkspaceGeometry(QRect(w.geometry()),
            QRect(w.card.mapTo(w.background,QPoint()),w.card.size()),
            QRect(w.results_panel.mapTo(w.background,QPoint()),w.results_panel.size()),
            QRect(plan.tool.x(),plan.tool.y(),0,plan.tool.height()),plan.fallback)
        w.background.layout().setEnabled(False)
        w.content_layout.setEnabled(False)
        self.kind=kind
        self.phase="opening"
        w.setMinimumSize(0,0)
        w.setMaximumSize(16777215,16777215)
        if self.stack.indexOf(widget)<0:
            widget.setParent(self.stack,Qt.WindowType.Widget)
            widget.setMinimumSize(0,0)
            self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
        self.setGeometry(previous.tool)
        if starting:self.fade.setOpacity(0)
        widget.show();self.show();self.raise_()
        def opened():
            self.phase="open"
            widget.setFocus(Qt.FocusReason.TabFocusReason)
        self._transition(previous,plan,opened)

    def _apply(self,plan):
        w=self.owner
        self.plan=plan
        w._geometry_frame_active=True
        try:
            w.setGeometry(plan.window)
            w.background.setGeometry(w.rect())
            w.content_surface.setGeometry(w.rect())
            w.card.setGeometry(plan.extract)
            w.results_panel.setMinimumWidth(0);w.results_panel.setMaximumWidth(16777215)
            w.results_panel.setGeometry(plan.results)
            w.results_panel.setVisible(not plan.fallback)
            self.setGeometry(plan.tool)
            w.title_bar.setGeometry(14,4,plan.results.right()-14,24)
            w.title_bar.raise_()
        finally:
            w._geometry_frame_active=False
        w._update_window_mask()

    def _stop_animation(self):
        if self.animation is not None:
            self.animation.stop()
            self.animation.deleteLater()
            self.animation=None
        self.animating=False
        self._motion_start=None;self._motion_end=None
        self.fade.setOpacity(1)
        self.back.show()

    def _transition(self,start,end,finished,immediate=False):
        self._stop_animation()
        self.owner.setMinimumSize(0,0)
        self.owner.setMaximumSize(16777215,16777215)
        # A responsive mode change replaces an entire area. Keep that bounded
        # rather than interpolating a hidden Results card through Extract.
        if (immediate or not self.motion_enabled or start.fallback or end.fallback
                or not self.owner._results_work_area().contains(start.window)):
            self._apply(end)
            self.owner.setFixedSize(end.window.size())
            finished()
            return
        self.animating=True
        self._motion_start=start;self._motion_end=end
        animation=QVariantAnimation(self)
        self.animation=animation
        animation.setDuration(240)
        animation.setStartValue(0.0);animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        def rect(a,b,t):
            return QRect(*[round(x+(y-x)*t) for x,y in zip(a.getRect(),b.getRect())])
        def frame(t):
            start,end=self._motion_start,self._motion_end
            closing=end.tool.width()==0
            geometry_t=max(0.,(t-.25)/.75) if closing else min(1.,t/.75)
            p=WorkspaceGeometry(*(rect(getattr(start,k),getattr(end,k),geometry_t)
                for k in ('window','extract','results','tool')),False)
            p.results.moveLeft(p.extract.right()+17)
            p.tool.moveLeft(p.results.right()+17)
            p=replace(p,window=clamp_window(p.window,self.owner._results_work_area()))
            self._apply(p)
            # Reveal content only once its real layout has its final dimensions.
            # Closing fades before contraction; no squeezed controls are exposed.
            self.fade.setOpacity(max(0.,1-t/.25) if closing else max(0.,(t-.75)/.25))
            self.back.setVisible(not closing and geometry_t >= 1)
        def done():
            self.animating=False
            self.fade.setOpacity(1)
            self.back.show()
            self._apply(end)
            self.owner.setFixedSize(end.window.size())
            self.animation=None
            self._motion_start=None;self._motion_end=None
            animation.deleteLater()
            finished()
        animation.valueChanged.connect(frame)
        animation.finished.connect(done)
        frame(0.0)
        animation.start()

    def rebase_move(self, delta):
        """Native/manual moves rebase this clock, not the saved layout baseline."""
        if not self.animating or self._motion_start is None:
            return
        area=self.owner._results_work_area()
        for plan in (self._motion_start,self._motion_end):
            plan.window.translate(delta)
            plan.window.moveTopLeft(clamp_window(plan.window,area).topLeft())

    def _closed_target(self):
        area=self.owner._results_work_area()
        size=self.saved[0].size().boundedTo(area.size())
        return centered_window(size,self.owner.geometry(),area)

    def collapse(self, immediate=False, finished=None):
        if finished is not None and finished not in self._close_callbacks:
            self._close_callbacks.append(finished)
        if self.saved is None:
            self._closed_callbacks()
            return
        if self.phase=="closing" and not immediate:
            return
        w=self.owner
        target=self._closed_target()
        if not immediate and self.motion_enabled and self.plan and not self.plan.fallback:
            current=replace(self.plan,window=QRect(w.geometry()))
            extract=QRect(self.saved[1]);extract.translate(self.saved[3].topLeft())
            results=QRect(self.saved[2]);results.translate(self.saved[3].topLeft())
            end=WorkspaceGeometry(target,extract,results,
                QRect(results.right()+17,current.tool.y(),0,current.tool.height()),False)
            self.phase="closing"
            self._transition(current,end,self._restore_closed)
            return
        self._restore_closed()

    def _closed_callbacks(self):
        callbacks,self._close_callbacks=self._close_callbacks,[]
        for callback in callbacks:callback()

    def _restore_closed(self):
        w=self.owner
        saved=self.saved
        target=self._closed_target()
        self._stop_animation()
        self.hide();self.plan=None;self.saved=None;self.kind=None;self.phase="closed"
        w.results_panel.show()
        w.setMaximumSize(16777215,16777215);w.setMinimumSize(0,0)
        w.setGeometry(target)
        w.content_surface.setGeometry(saved[3])
        w.card.setGeometry(saved[1]);w.results_panel.setGeometry(saved[2])
        w.results_panel.setFixedWidth(saved[2].width())
        w.content_layout.setEnabled(True);w.background.layout().setEnabled(True)
        w.background.layout().activate();w.content_layout.activate()
        w.setMinimumSize(saved[4].boundedTo(target.size()));w.setMaximumSize(saved[5])
        w._update_window_mask()
        self._closed_callbacks()
