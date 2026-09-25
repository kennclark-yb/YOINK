from PySide6.QtCore import (
    QPoint,
    Qt,
    Signal,
    QEvent,
    QPropertyAnimation,
    QEasingCurve,
    Property,
)
from PySide6.QtGui import QCursor, QColor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)

from .styles import ACCENT, INPUT_BG, CARD_BORDER, TEXT


class SplitSelector(QFrame):
    changed = Signal(str)

    def __init__(self, options):
        super().__init__()

        self.options = options
        self._current = options[0]
        self.popup = None
        self._hover_color = QColor(TEXT)
        self._highlight_color = QColor(ACCENT)
        self._hover_button = None

        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(
            f"""
            QFrame {{
                background: {INPUT_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 9px;
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(0)

        self.label = QPushButton(self._current)
        self.label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self.arrow = QPushButton("▾")
        self.arrow.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self.arrow.setFixedWidth(24)

        layout.addWidget(self.label, 1)
        layout.addWidget(self.arrow)

        self._apply_hover_color()

        QApplication.instance().installEventFilter(self)

        # Selector text / arrow hover animation
        self._color_animation = QPropertyAnimation(
            self,
            b"hoverColor",
        )
        self._color_animation.setDuration(250)
        self._color_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

    def currentText(self):
        return self._current

    def changeEvent(self, event):
        if event.type() == QEvent.Type.EnabledChange:
            self._color_animation.stop()
            self._hover_color = QColor(TEXT)
            if not self.isEnabled() and self.popup is not None:
                self.popup_animation.stop()
                self._finish_popup_hide()
            self.setCursor(
                Qt.CursorShape.PointingHandCursor if self.isEnabled()
                else Qt.CursorShape.ArrowCursor
            )
            self._apply_hover_color()
        super().changeEvent(event)

    def enterEvent(self, event):
        if self.isEnabled():
            self._animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.isEnabled():
            self._animate_hover(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:

            if self.popup is not None:
                if self.popup.isVisible():
                    if self.popup_animation.state() == (
                        QPropertyAnimation.State.Running
                    ):
                        self._show_popup()

                    return

            self._show_popup()

        super().mousePressEvent(event)

    def eventFilter(self, watched, event):
        # Popup outside-click handling
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and self.popup is not None
            and self.popup.isVisible()
        ):
            position = QCursor.pos()

            selector_rect = self.rect()
            selector_position = self.mapToGlobal(
                QPoint(0, 0)
            )
            selector_rect.moveTopLeft(selector_position)

            popup_rect = self.popup.rect()
            popup_position = self.popup.mapToGlobal(
                QPoint(0, 0)
            )
            popup_rect.moveTopLeft(popup_position)

            if (
                selector_rect.contains(position)
                or popup_rect.contains(position)
            ):
                return False

            self._hide_popup()

        # Popup option hover handling
        if (
            self.popup is not None
            and event.type() == QEvent.Type.Enter
            and watched in self.popup.findChildren(QPushButton)
        ):
            self._move_highlight(watched)

        # Popup leave handling
        if (
            self.popup is not None
            and event.type() == QEvent.Type.Leave
            and watched is self.popup
        ):
            self._fade_highlight_out()

        return False

    def _animate_hover(self, hovered):
        self._color_animation.stop()

        self._color_animation.setStartValue(
            self._hover_color
        )
        self._color_animation.setEndValue(
            QColor(ACCENT if hovered else TEXT)
        )

        self._color_animation.start()

    def _get_hover_color(self):
        return self._hover_color

    def _set_hover_color(self, color):
        self._hover_color = color
        self._apply_hover_color()

    hoverColor = Property(
        QColor,
        _get_hover_color,
        _set_hover_color,
    )

    def _apply_hover_color(self):
        color = self._hover_color.name() if self.isEnabled() else "#777A84"

        self.label.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: none;
                padding: 0;
                font-size: 13px;
            }}
            """
        )

        self.arrow.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: none;
                padding: 0;
                font-size: 13px;
            }}
            """
        )

    def _create_popup(self):
        self.popup = QFrame(self.window())

        self.popup.setStyleSheet(
            f"""
            QFrame {{
                background: #15171B;
                border: 1px solid {CARD_BORDER};
                border-radius: 9px;
            }}

            QPushButton {{
                background: transparent;
                color: {TEXT};
                border: none;
                border-radius: 6px;
                text-align: center;
                padding: 9px 11px;
            }}

            QPushButton:hover {{
                background: transparent;
                color: #FFFFFF;
            }}
            """
        )

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(5, 5, 5, 5)
        popup_layout.setSpacing(2)

        self.option_buttons = []

        for option in self.options:
            button = QPushButton(option)
            button.setCursor(Qt.CursorShape.PointingHandCursor)

            button.setAttribute(
                Qt.WidgetAttribute.WA_Hover
            )

            button.clicked.connect(
                lambda checked=False, value=option:
                self._select(value)
            )

            popup_layout.addWidget(button)
            self.option_buttons.append(button)

        # Sliding hover highlight
        self.highlight = QFrame(self.popup)
        self.highlight.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self.highlight.setStyleSheet(
            f"""
            QFrame {{
                background: {ACCENT};
                border-radius: 6px;
            }}
            """
        )

        self.highlight.hide()
        self.highlight.lower()

        # Highlight fade
        self.highlight_fade = QPropertyAnimation(
            self,
            b"highlightColor",
        )
        self.highlight_fade.setDuration(200)
        self.highlight_fade.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )
        self.highlight_fade.finished.connect(
            self._finish_highlight_fade
        )

        # Highlight movement
        self.highlight_animation = QPropertyAnimation(
            self.highlight,
            b"geometry",
        )
        self.highlight_animation.setDuration(170)
        self.highlight_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        # Popup fade effect
        self.popup_opacity = QGraphicsOpacityEffect(
            self.popup
        )
        self.popup.setGraphicsEffect(
            self.popup_opacity
        )

        self.popup_animation = QPropertyAnimation(
            self.popup_opacity,
            b"opacity",
        )
        self.popup_animation.setDuration(140)
        self.popup_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self.popup_animation.finished.connect(
            self._finish_popup_hide
        )

    def _get_highlight_color(self):
        return self._highlight_color

    def _set_highlight_color(self, color):
        self._highlight_color = color

        self.highlight.setStyleSheet(
            f"""
            QFrame {{
                background: rgba(
                    {color.red()},
                    {color.green()},
                    {color.blue()},
                    {color.alpha()}
                );
                border-radius: 6px;
            }}
            """
        )

    highlightColor = Property(
        QColor,
        _get_highlight_color,
        _set_highlight_color,
    )

    def _move_highlight(self, button):
        if button not in self.option_buttons:
            return

        target = button.geometry()

        self.highlight_fade.stop()

        # First hover
        if not self.highlight.isVisible():
            self.highlight.setGeometry(target)
            self.highlight.show()
            self.highlight.lower()

            start_color = QColor(ACCENT)
            start_color.setAlpha(0)

            end_color = QColor(ACCENT)
            end_color.setAlpha(255)

            self.highlight_fade.setStartValue(
                start_color
            )
            self.highlight_fade.setEndValue(
                end_color
            )
            self.highlight_fade.start()

        # Move between options
        else:
            self.highlight_animation.stop()
            self.highlight_animation.setStartValue(
                self.highlight.geometry()
            )
            self.highlight_animation.setEndValue(target)
            self.highlight_animation.start()

            full_color = QColor(ACCENT)
            full_color.setAlpha(255)
            self._set_highlight_color(full_color)

        self._hover_button = button

    def _fade_highlight_out(self):
        if (
            self.highlight is None
            or not self.highlight.isVisible()
        ):
            return

        self.highlight_fade.stop()

        start_color = QColor(self._highlight_color)

        end_color = QColor(ACCENT)
        end_color.setAlpha(0)

        self.highlight_fade.setStartValue(
            start_color
        )
        self.highlight_fade.setEndValue(
            end_color
        )
        self.highlight_fade.start()

    def _finish_highlight_fade(self):
        if self._highlight_color.alpha() == 0:
            self.highlight.hide()

    def _show_popup(self):
        if self.popup is None:
            self._create_popup()

        self.popup_animation.stop()
        self.highlight_animation.stop()
        self.highlight_fade.stop()

        self.popup.setFixedWidth(self.width())
        self.popup.adjustSize()

        position = self.mapTo(
            self.window(),
            QPoint(0, self.height() + 4),
        )

        self.popup.move(position)
        self.popup.raise_()

        self.highlight.hide()
        self._hover_button = None

        full_color = QColor(ACCENT)
        full_color.setAlpha(255)
        self._set_highlight_color(full_color)

        self.popup_opacity.setOpacity(1.0)
        self.popup.show()

    def _hide_popup(self):
        if self.popup is None or not self.popup.isVisible():
            return

        self.highlight_animation.stop()
        self.highlight_fade.stop()

        self.popup_animation.stop()

        self.popup_animation.setStartValue(
            self.popup_opacity.opacity()
        )
        self.popup_animation.setEndValue(0.0)

        self.popup_animation.start()

    def _finish_popup_hide(self):
        if self.popup is not None:
            self.popup.hide()
            self.popup_opacity.setOpacity(1.0)
            self.highlight.hide()
            self._hover_button = None

            full_color = QColor(ACCENT)
            full_color.setAlpha(255)
            self._set_highlight_color(full_color)

    def _select(self, value):
        if value == self._current:
            self._hide_popup()
            return
        self._current = value
        self.label.setText(value)

        self._hide_popup()

        self.changed.emit(value)
