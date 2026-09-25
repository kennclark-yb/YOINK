import random
from PySide6.QtCore import (
    Property,
    QPropertyAnimation,
    QEasingCurve,
    Qt,
    QTimer,
    QEvent,
)
from PySide6.QtGui import QLinearGradient
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QPushButton
from .loading_messages import LOADING_MESSAGES

from .styles import ACCENT


class ProgressButton(QPushButton):
    def __init__(self, text="EXTRACT"):
        super().__init__(text)

        self._default_text = text
        self._fill_progress = 0.0
        self._hover_progress = 0.0
        self._processing = False
        self._recovery = False
        self._results_press_style = False
        self._pressed = False
        self.pressed.connect(lambda: self._set_pressed(True))
        self.released.connect(lambda: self._set_pressed(False))

        self._loading_messages = LOADING_MESSAGES

        self._loading_text_timer = QTimer(self)
        self._loading_text_timer.setInterval(1400)
        self._loading_text_timer.timeout.connect(
            self._rotate_loading_text
        )

        self._fake_target = 0.0
        self._fake_progress_timer = QTimer(self)
        self._fake_progress_timer.setInterval(80)
        self._fake_progress_timer.timeout.connect(
            self._advance_fake_progress
        )

        self._shimmer_offset = -0.3

        self._shimmer_timer = QTimer(self)
        self._shimmer_timer.setInterval(16)
        self._shimmer_timer.timeout.connect(
            self._advance_shimmer
        )

        self._animation = QPropertyAnimation(
            self,
            b"hoverProgress",
        )

        self._animation.setDuration(250)

        self._animation.setEasingCurve(
            QEasingCurve.Type.Linear
        )

        self._progress_animation = QPropertyAnimation(
            self,
            b"fillProgress",
        )

        self._progress_animation.setDuration(300)

        self._progress_animation.setEasingCurve(
            QEasingCurve.Type.InOutCubic
        )

        self.setFixedHeight(44)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

    def get_fill_progress(self):
        return self._fill_progress

    def set_fill_progress(self, value):
        self._fill_progress = value
        self.update()

    fillProgress = Property(
        float,
        get_fill_progress,
        set_fill_progress,
    )

    def get_hover_progress(self):
        return self._hover_progress

    def set_hover_progress(self, value):
        self._hover_progress = value
        self.update()

    hoverProgress = Property(
        float,
        get_hover_progress,
        set_hover_progress,
    )

    def _rotate_loading_text(self):
        if not self._processing:
            return

        current = self.text()

        choices = [
            message
            for message in self._loading_messages
            if message != current
        ]

        if choices:
            self.setText(
                random.choice(choices)
            )

    def _advance_shimmer(self):
        if not self._processing:
            return

        self._shimmer_offset += 0.025

        if self._shimmer_offset > 1.3:
            self._shimmer_offset = -0.3

        self.update()

    def _advance_fake_progress(self):
        if not self._processing:
            return

        if self._fake_target >= 80.0:
            return

        remaining = 80.0 - self._fake_target

        step = max(
            0.15,
            remaining * 0.025,
        )

        self._fake_target = min(
            self._fake_target + step,
            80.0,
        )

        self._animate_progress_to(
            self._fake_target / 100
        )

    def _animate_progress_to(self, target):
        self._progress_animation.stop()

        self._progress_animation.setStartValue(
            self._fill_progress
        )

        self._progress_animation.setEndValue(
            target
        )

        self._progress_animation.setDuration(
            180
        )

        self._progress_animation.setEasingCurve(
            QEasingCurve.Type.Linear
        )

        self._progress_animation.start()

    def set_processing(self, processing):
        self._processing = processing
        self._set_pressed(False)
        self.setEnabled(not processing)

        if processing:
            self._recovery = False

            self._animation.stop()
            self._progress_animation.stop()

            self._fake_target = 0.0
            self._fill_progress = 0.0

            self._shimmer_offset = -0.3

            self.setText(
                random.choice(self._loading_messages)
            )

            self._loading_text_timer.start()

            self._shimmer_timer.start()
            self._fake_progress_timer.start()

            self.setCursor(
                Qt.CursorShape.ArrowCursor
            )

        else:
            self._shimmer_timer.stop()
            self._fake_progress_timer.stop()
            self._loading_text_timer.stop()

            self._progress_animation.stop()

            self._fill_progress = 0.0
            self._fake_target = 0.0
            self._hover_progress = 0.0

            if self._recovery:
                self.setText("RETRY")
            else:
                self.setText(self._default_text)

            self.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            self.update()

    def set_recovery(self, recovery):
        self._recovery = recovery

        self._animation.stop()
        self._progress_animation.stop()

        self._fill_progress = 0.0

        if recovery:
            self.setText("RETRY")
        else:
            self.setText(self._default_text)

        self.setCursor(
            Qt.CursorShape.PointingHandCursor if self.isEnabled() and not self._processing
            else Qt.CursorShape.ArrowCursor
        )

        self.update()

    def set_results_press_style(self, enabled):
        self._results_press_style = enabled
        self._pressed = False
        self.update()

    def _set_pressed(self, pressed):
        self._pressed = pressed
        self.update()

    def set_progress(self, stage, percentage):
        if not self._processing:
            return

        if percentage >= 100:
            self._loading_text_timer.stop()

            self.setText(
                "[ extraction successful ]"
            )

        if percentage < 100:
            return

        self._fake_progress_timer.stop()
        self._shimmer_timer.stop()

        self._progress_animation.stop()

        self._progress_animation.setStartValue(
            self._fill_progress
        )

        self._progress_animation.setEndValue(
            1.1
        )

        self._progress_animation.setDuration(
            900
        )

        self._progress_animation.setEasingCurve(
            QEasingCurve.Type.InOutCubic
        )

        self._progress_animation.start()

        self._fake_target = 100.0
        self._shimmer_offset = -0.3

        self.update()

    def _animate_to(self, target):
        if self._processing:
            return

        self._animation.stop()

        start = self._hover_progress

        self._animation.setStartValue(start)
        self._animation.setEndValue(target)

        if target == 1.0:
            self._animation.setKeyValueAt(
                0.45,
                start + (target - start) * 0.10,
            )
            self._animation.setKeyValueAt(
                0.70,
                start + (target - start) * 0.40,
            )
            self._animation.setKeyValueAt(
                0.88,
                start + (target - start) * 0.72,
            )
        else:
            self._animation.setKeyValueAt(
                0.45,
                start + (target - start) * 0.40,
            )
            self._animation.setKeyValueAt(
                0.70,
                start + (target - start) * 0.70,
            )
            self._animation.setKeyValueAt(
                0.88,
                start + (target - start) * 0.90,
            )

        self._animation.start()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.EnabledChange:
            if not self.isEnabled():
                self._animation.stop()
                self._hover_progress = 0.0
                self._pressed = False
            self.setCursor(
                Qt.CursorShape.PointingHandCursor
                if self.isEnabled() and not self._processing
                else Qt.CursorShape.ArrowCursor
            )
            self.update()

        super().changeEvent(event)

    def enterEvent(self, event):
        if self.isEnabled() and not self._processing:
            self._animate_to(1.0)

        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.isEnabled() and not self._processing:
            self._animate_to(0.0)

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._processing:
            event.ignore()
            return
        super().mousePressEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._pressed = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        rect = self.rect().adjusted(
            0,
            0,
            -1,
            -1,
        )

        button_path = QPainterPath()

        button_path.addRoundedRect(
            rect,
            10,
            10,
        )

        disabled = not self.isEnabled() and not self._processing
        pressed = self.isEnabled() and (self._pressed or self.isDown())
        progress = 0.0 if disabled else self._fill_progress
        hover_progress = 0.0 if disabled else self._hover_progress
        fill_width = rect.width() * progress
        hover_width = rect.width() * hover_progress

        if disabled:
            base_color = QColor("#25262C")
            accent_color = QColor(ACCENT)
        elif self._recovery:
            base_color = QColor("#D0C58E")
            accent_color = QColor("#B8A56A")
        else:
            base_color = QColor("#E5E5E7")
            accent_color = QColor(ACCENT)

        painter.save()

        painter.setClipPath(button_path)

        # Base button
        painter.fillPath(
            button_path,
            base_color,
        )

        if not self._processing and hover_progress > 0:
            hover_color = QColor(accent_color)
            hover_color.setAlphaF(hover_progress)

            painter.fillPath(
                button_path,
                hover_color,
            )

        # Progress fill
        if fill_width > 0:
            gradient = QLinearGradient(
                rect.left(),
                rect.top(),
                rect.left() + fill_width,
                rect.top(),
            )

            edge_width = min(
                rect.width() * 0.15,
                55,
            )

            edge_start = max(
                0.0,
                fill_width - edge_width,
            )

            gradient.setColorAt(
                0.0,
                accent_color,
            )

            if fill_width < rect.width():
                gradient.setColorAt(
                    edge_start / fill_width,
                    accent_color,
                )

            gradient.setColorAt(
                1.0,
                base_color,
            )

            fill_rect = rect.adjusted(
                0,
                0,
                0,
                0,
            )

            fill_rect.setWidth(
                int(fill_width)
            )

            if progress >= 1.0:
                painter.fillPath(
                    button_path,
                    accent_color,
                )
            else:
                painter.fillRect(
                    fill_rect,
                    gradient,
                )

        # Shimmer
        if (
            self._processing
            and progress > 0
            and not self._recovery
        ):
            shimmer_width = rect.width() * 0.12

            shimmer_x = (
                rect.left()
                + fill_width * self._shimmer_offset
            )

            shimmer_path = QPainterPath()

            shimmer_path.addRoundedRect(
                shimmer_x,
                rect.top(),
                shimmer_width,
                rect.height(),
                8,
                8,
            )

            fill_path = QPainterPath()

            fill_path.addRoundedRect(
                fill_rect,
                10,
                10,
            )

            painter.save()

            painter.setClipPath(fill_path)

            shimmer_gradient = QLinearGradient(
                shimmer_x,
                shimmer_path.boundingRect().top(),
                shimmer_x + shimmer_width,
                shimmer_path.boundingRect().top(),
            )

            shimmer_color = QColor("#FFFFFF")

            shimmer_color.setAlphaF(0.0)
            shimmer_gradient.setColorAt(
                0.0,
                shimmer_color,
            )

            shimmer_color.setAlphaF(0.10)
            shimmer_gradient.setColorAt(
                0.5,
                shimmer_color,
            )

            shimmer_color.setAlphaF(0.0)
            shimmer_gradient.setColorAt(
                1.0,
                shimmer_color,
            )

            painter.fillPath(
                shimmer_path,
                shimmer_gradient,
            )

            painter.restore()

        if pressed:
            painter.fillPath(button_path, accent_color)
            painter.fillPath(
                button_path, QColor(0, 0, 0, 30 if self._results_press_style else 22),
            )

        painter.restore()

        # Border
        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.setPen(
            QPen(
                QColor(ACCENT if self.hasFocus() and self.isEnabled() else
                       "#303137" if disabled else "#555861"),
                2 if self.hasFocus() and self.isEnabled() else 1,
            )
        )

        painter.drawPath(button_path)

        # Text
        painter.setPen(
            QColor("#8A8D96") if disabled else QColor("#FFFFFF")
            if progress > 0.8 or hover_progress > 0.8 or pressed
            else QColor("#111216")
        )

        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            self.text(),
        )
