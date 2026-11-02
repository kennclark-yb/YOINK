"""Session-bound picker with lazily resolved, source-numbered output."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QShortcut, QKeySequence
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout,
                               QLabel, QPushButton, QScrollBar,
                               QScrollArea, QTextBrowser, QVBoxLayout, QWidget)

from .application import ASSETS
from .context_timeline import MessageTimeline


class ContextPicker(QWidget):
    def __init__(self, conversation, append, parent=None, role="both"):
        super().__init__(parent)
        self.output_role = role
        self.source = conversation
        self._append = append
        self._active = True
        self._preview_text = None
        self._background = QPixmap(str(ASSETS / "static_grain_option3.png"))
        self.setWindowTitle("YOINK · Context Picker")
        self.resize(800, min(640, self.screen().availableGeometry().height() - 64))
        self.setMinimumSize(0, 0)
        self.setStyleSheet("""
            QDialog { color: #F2F2F4; }
            QFrame#ContextPanel { background: rgba(21,22,26,214); border: 1px solid #303137;
                                  border-radius: 12px; }
            QLabel { color: #B8BAC2; background: transparent; border: none; }
            QPushButton { background: #1B2340; color: #E5E9F5;
                border: 1px solid #303A53; border-radius: 6px; padding: 7px 10px; }
            QPushButton:hover, QToolButton:hover { background: #253655; }
            QPushButton:pressed, QToolButton:pressed { background: #4D7CFE; color: white; }
            QToolButton { color: #9DB7FF; background: #1B2340; border: 1px solid #303A53; border-radius: 6px; padding: 3px 10px; }
            QToolButton::menu-indicator { image: none; width: 0px; }
            QToolButton:focus { border: 1px solid #8AA9FF; }
            QPushButton:focus { border: 1px solid #8AA9FF; }
            QPushButton:disabled { color: #696E7C; background: #1A1D26; }
            QTextBrowser { background: #0F1012; color: #E5E9F5; border: 1px solid #303A53;
                           border-radius: 6px; padding: 10px; }
            QScrollBar:horizontal { height: 12px; background: #161B28; }
            QScrollBar::handle:horizontal { background: #394A70; min-width: 24px; }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        panel = QFrame()
        panel.setObjectName("ContextPanel")
        self.surface_scroll = QScrollArea()
        self.surface_scroll.setAccessibleName("Context Picker controls and preview")
        self.surface_scroll.setWidgetResizable(True)
        self.surface_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.surface_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.surface_scroll.viewport().setAutoFillBackground(False)
        self.surface_scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.surface_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.surface_scroll.setWidget(panel)
        outer.addWidget(self.surface_scroll)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)
        title = QLabel("CONTEXT PICKER")
        title.setStyleSheet("color: #F2F2F4; font-weight: 700; letter-spacing: 2px;")
        layout.addWidget(title)
        self.summary = QLabel()
        self.summary.setAccessibleName("Selection coverage")
        layout.addWidget(self.summary)
        row = QHBoxLayout()
        row.addWidget(QLabel("A · FIRST MESSAGE"))
        row.addStretch()
        row.addWidget(QLabel("LAST MESSAGE · B"))
        layout.addLayout(row)
        self.timeline = MessageTimeline(len(conversation["messages"]))
        self.timeline.setFixedHeight(68)
        layout.addWidget(self.timeline)
        self.scroll = QScrollBar(Qt.Orientation.Horizontal)
        self.scroll.setAccessibleName("Navigate source messages")
        self.scroll.valueChanged.connect(self.timeline.set_first)
        self.timeline.navigationChanged.connect(self._navigation)
        layout.addWidget(self.scroll)
        row = QHBoxLayout()
        self.cursor_label = QLabel("Cursor · message 1")
        self.timeline.cursorChanged.connect(lambda i: self.cursor_label.setText(f"Cursor · message {i + 1:,}"))
        row.addWidget(self.cursor_label)
        row.addStretch()
        self._button(row, "Fit All", self.fit_all)
        self._button(row, "−", lambda: self.timeline.zoom(-2), "Zoom out timeline")
        self._button(row, "+", lambda: self.timeline.zoom(2), "Zoom in timeline")
        layout.addLayout(row)
        hint = QLabel("Drag to replace · Ctrl+drag to add · Drag the pale upper handles to adjust endpoints.\n"
                      "Arrow keys navigate · Space/Enter selects · Ctrl+Space adds · Wheel scrolls.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #929AAA; font-size: 10px;")
        layout.addWidget(hint)
        row = QHBoxLayout()
        self.presets = {}
        for label, name in (("First half", "first_half"), ("Final quarter", "final_quarter"),
                            ("Final half", "final_half"), ("Final three-quarters", "final_three_quarters")):
            self.presets[name] = self._button(row, label, lambda checked=False, n=name: self._preset(n))
        layout.addLayout(row)
        row = QHBoxLayout()
        self.clear_button = self._button(row, "Clear all", lambda: self.timeline.set_selection(self.timeline.selection.clear()))
        layout.addLayout(row)
        row = QHBoxLayout()

        row.addStretch()
        self.preview_button = self._button(row, "Preview Selection", self.preview)
        layout.addLayout(row)
        self.preview_view = QTextBrowser()
        self.preview_view.setAccessibleName("Selection Preview with original message numbering")
        self.preview_view.setOpenExternalLinks(False)
        self.preview_view.setMinimumHeight(180)
        self.preview_view.hide()
        layout.addWidget(self.preview_view, 1)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setAccessibleName("Selection output status")
        layout.addWidget(self.status)
        row = QHBoxLayout()
        self.copy_button = self._button(row, "Copy Selection", self.copy_selection)
        self.append_button = self._button(row, "Add to Scratchpad", self.append_selection)
        row.addStretch()
        self._button(row, "Close", self.hide)
        layout.addLayout(row)
        # Prefix role counts allow feedback without resolving/copying huge selections per drag.
        self._role_prefix = {}
        for role in ("assistant", "user"):
            prefix = [0]
            for message in conversation["messages"]:
                prefix.append(prefix[-1] + (message["role"] == role))
            self._role_prefix[role] = prefix
        self.timeline.selectionChanged.connect(self._selection_changed)
        self._selection_changed()
        self._navigation()
        self._compact_surface()

    def _compact_surface(self):
        panel = QWidget()
        panel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        panel.setObjectName("PickerSurface")
        panel.setStyleSheet("QWidget#PickerSurface { background: transparent; }")
        widgets = [self.summary,self.timeline,self.scroll,self.cursor_label,
                   self.clear_button,self.preview_button,self.preview_view,
                   self.status,self.copy_button,self.append_button,*self.presets.values()]
        for widget in widgets:widget.setParent(panel)
        old=self.surface_scroll.takeWidget()
        self.surface_scroll.setWidget(panel)
        old.deleteLater()
        self.layout().setContentsMargins(0,0,0,0)
        layout=QVBoxLayout(panel);layout.setContentsMargins(2,2,2,2);layout.setSpacing(3)
        self.summary.hide()
        self.summary_container=QFrame()
        self.summary_container.setObjectName("SelectionSummary")
        self.summary_container.setAccessibleName("Source selection summary")
        self.summary_container.setStyleSheet("QFrame#SelectionSummary { background: rgba(30,40,65,130); border: 1px solid #35415A; border-radius: 8px; }")
        summary_row=QHBoxLayout(self.summary_container)
        summary_row.setContentsMargins(9,5,9,5)
        summary_row.setSpacing(8)
        self.summary_values=[QLabel(),QLabel(),QLabel()]
        for index, value in enumerate(self.summary_values):
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_row.addWidget(value)
            if index < len(self.summary_values) - 1:
                summary_row.addWidget(QLabel('·'))
        layout.addWidget(self.summary_container,0,Qt.AlignmentFlag.AlignHCenter)
        self._update_summary_values()
        layout.addWidget(self.timeline)
        layout.addWidget(self.scroll)
        self.hint=QLabel('[ how to ] : Drag to select \u00b7 Ctrl+drag to add \u00b7 Click selected pill to deselect')
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet('color: #B8BAC2; font-size: 10px;')
        self.hint.setToolTip('Ctrl+0: Fit All; Ctrl+= / Ctrl+-: precision zoom.')
        layout.addWidget(self.hint)
        row=QHBoxLayout()
        for name in ('first_half','final_half'):
            self.presets[name].setText('First Half' if name == 'first_half' else 'Final Half')
            row.addWidget(self.presets[name], 2)
        self.clear_button.setText('Clear Selection')
        self.clear_button.setMaximumWidth(120)
        self.clear_button.setAccessibleName('Clear Selection')
        self.clear_button.setToolTip('Clear selection (Ctrl+Shift+Backspace)')
        self.clear_button.setEnabled(bool(self.timeline.selection.selected_count))
        self.preview_button.hide()
        for name in ('final_quarter','final_three_quarters'):self.presets[name].hide()
        row.addWidget(self.clear_button, 1)
        layout.addLayout(row)
        self.cursor_label.hide()
        self.shortcuts=[]
        for key,callback in (('Ctrl+Shift+Backspace',self.clear_button.click),
                             ('Ctrl+0',self.fit_all),('Ctrl+=',lambda:self.timeline.zoom(2)),
                             ('Ctrl+-',lambda:self.timeline.zoom(-2)),
                             ('Alt+4',lambda:self._preset('final_quarter')),
                             ('Alt+3',lambda:self._preset('final_three_quarters'))):
            shortcut=QShortcut(QKeySequence(key),self)
            shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            shortcut.activated.connect(callback);self.shortcuts.append(shortcut)
        layout.addWidget(self.preview_view,1);self.preview_view.hide()
        self.status.setStyleSheet('color: #B8BAC2; font-size: 10px;')
        layout.addWidget(self.status)
        row=QHBoxLayout();row.addWidget(self.copy_button);row.addWidget(self.append_button);layout.addLayout(row)
        layout.addStretch()
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button.styleSheet()+'QPushButton { padding: 3px 5px; }')

    def _set_status(self, text):
        self.status.setText('[ status ] : '+text.lower())

    def fit_all(self):
        self.timeline.fit_all = True
        self.timeline.set_first(0)
        self.timeline.navigationChanged.emit()
        self.timeline.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            root = self.window()
            if hasattr(root, 'workspace'):
                root.workspace.collapse()
            else:
                self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        if self.parent() is not None:return
        p = QPainter(self)
        p.fillRect(self.rect(), Qt.GlobalColor.black)
        if not self._background.isNull():
            p.drawPixmap(self.rect(), self._background)

    @staticmethod
    def _button(row, text, callback, name=None):
        b = QPushButton(text)
        b.setAutoDefault(False)
        b.setAccessibleName(name or text)
        b.clicked.connect(callback)
        row.addWidget(b)
        return b

    def _navigation(self):
        grouped=self.timeline.fit_all and self.timeline.selection.message_count > max(1,self.timeline.width())
        self.timeline.setFixedHeight(84 if grouped else 68)
        self.scroll.blockSignals(True)
        self.scroll.setRange(0, max(0, self.timeline.selection.message_count - self.timeline.capacity))
        self.scroll.setPageStep(self.timeline.capacity)
        self.scroll.setValue(self.timeline.first)
        self.scroll.blockSignals(False)
        self.scroll.setVisible(self.scroll.maximum() > 0)

    def _update_summary_values(self):
        if hasattr(self, 'summary_values'):
            selection=self.timeline.selection
            for label,text in zip(self.summary_values,(f"{selection.message_count:,} messages",f"{selection.selected_count:,} selected",f"{selection.coverage * 100:.3g}% coverage")):
                label.setText(text)

    def _selection_changed(self, selection=None):
        s = self.timeline.selection
        self.summary.setText(f"{s.message_count:,} messages  ·  {s.selected_count:,} selected  ·  {s.coverage * 100:.3g}% coverage")
        self._update_summary_values()
        self._invalidate()

    def _match_count(self):
        s = self.timeline.selection
        role = self.output_role
        if role == "both":
            return s.selected_count
        prefix = self._role_prefix[role]
        return sum(prefix[r.end] - prefix[r.start] for r in s.ranges)

    def _invalidate(self, *args):
        self._preview_text = None
        self.preview_view.clear()
        self.preview_view.hide()
        self.clear_button.setEnabled(self._active and bool(self.timeline.selection.selected_count))
        count = self._match_count()
        self.copy_button.setEnabled(self._active and bool(count))
        self.append_button.setEnabled(self._active and bool(count))
        self.preview_button.setEnabled(self._active and bool(count))
        if hasattr(self, "preview_action"):
            self.preview_action.setEnabled(self.preview_button.isEnabled())
        if not self.timeline.selection.selected_count:
            self._set_status("No selection")
        elif not count:
            self._set_status("No matching output messages")
        else:
            self._set_status("Selection ready")

    def _preset(self, name):
        self.timeline.set_selection(self.timeline.selection.preset(name))
        if self.timeline.selection.ranges:
            self.timeline.ensure_visible(self.timeline.selection.ranges[0].start)

    def _resolved_text(self):
        if not self._active or not self.timeline.selection.selected_count or not self._match_count():
            return None
        if self._preview_text is None:
            result = self.timeline.selection.resolve(self.source, self.output_role)
            if result.status != "selected":
                return None
            self._preview_text = result.to_markdown()
        return self._preview_text

    def preview(self):
        text = self._resolved_text()
        if text is not None:
            self.preview_view.setPlainText(text)
            self.preview_view.show()
            self._set_status("Selection ready")

    def copy_selection(self):
        text = self._resolved_text()
        if text is not None:
            QApplication.clipboard().setText(text)
            self._set_status("Selection copied")

    def append_selection(self):
        text = self._resolved_text()
        if text is not None:
            ranges = ", ".join(f"{r.start + 1}–{r.end}" for r in self.timeline.selection.ranges)
            appended = self._append(("selection", self.timeline.selection.ranges, self.output_role),
                                    text, f"Selection {ranges} · {self.output_role}")
            self._set_status("Already added. Wait a moment to add again." if appended is False else
                                "Added to Scratchpad")

    def invalidate_session(self):
        self._active = False
        self._preview_text = None
        self.source = None
        self.setEnabled(False)
        self.close()
