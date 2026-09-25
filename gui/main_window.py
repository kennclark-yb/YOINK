import re
from PySide6.QtCore import (
    QEvent,
    QObject,
    QThread,
    Qt,
    QEasingCurve,
    QVariantAnimation,
    QRect,
    QTimer,
    QUrl,
    QPoint,
    QPropertyAnimation,
)
from PySide6.QtGui import (
    QCursor,
    QIntValidator,
    QDesktopServices,
    QKeySequence,
    QShortcut,
    QTextDocument,
)
from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTextBrowser,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from extract import ExtractionError, extract_conversation
from formatter import format_markdown, split_parts, split_parts_by_count
from .shutdown_screen import ShutdownScreen

from .background import Background
from .extraction_worker import ExtractionWorker
from .preload_worker import PreloadWorker
from .progress_button import ProgressButton
from .split_selector import SplitSelector
from .styles import APP_STYLE
from .title_bar import TitleBar
from .application import configure_application
from .updates import UpdateChecker, VERSION
from .update_dialog import UpdateDialog
from .preview import PreviewRoleSelector, render_preview_variants


class ResizeController(QObject):
    MARGIN = 7

    def __init__(self, window):
        super().__init__(window)
        self.window = window

        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() not in (
            QEvent.Type.MouseMove,
            QEvent.Type.MouseButtonPress,
        ):
            return False

        try:
            if not self.window.isVisible():
                return False

            if self.window.isMaximized():
                return False

            global_pos = QCursor.pos()
            local_pos = self.window.mapFromGlobal(
                global_pos
            )

            if not self.window.rect().contains(local_pos):
                self.window.unsetCursor()
                return False

            edges = self._edges_at(local_pos)

            if event.type() == QEvent.Type.MouseMove:
                self.window.setCursor(
                    self._cursor_for_edges(edges)
                )

            elif (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
                and edges
            ):
                handle = self.window.windowHandle()

                if handle:
                    handle.startSystemResize(edges)
                    return True

        except RuntimeError:
            # Qt object may already be destroyed during shutdown.
            return False

        return False

    def _edges_at(self, pos):
        rect = self.window.rect()

        edges = Qt.Edge(0)

        if pos.x() <= self.MARGIN:
            edges |= Qt.Edge.LeftEdge
        elif pos.x() >= rect.width() - self.MARGIN:
            edges |= Qt.Edge.RightEdge

        if pos.y() <= self.MARGIN:
            edges |= Qt.Edge.TopEdge
        elif pos.y() >= rect.height() - self.MARGIN:
            edges |= Qt.Edge.BottomEdge

        return edges

    def _cursor_for_edges(self, edges):
        if edges == (
            Qt.Edge.LeftEdge | Qt.Edge.TopEdge
        ) or edges == (
            Qt.Edge.RightEdge | Qt.Edge.BottomEdge
        ):
            return Qt.CursorShape.SizeFDiagCursor

        if edges == (
            Qt.Edge.RightEdge | Qt.Edge.TopEdge
        ) or edges == (
            Qt.Edge.LeftEdge | Qt.Edge.BottomEdge
        ):
            return Qt.CursorShape.SizeBDiagCursor

        if edges in (
            Qt.Edge.LeftEdge,
            Qt.Edge.RightEdge,
        ):
            return Qt.CursorShape.SizeHorCursor

        if edges in (
            Qt.Edge.TopEdge,
            Qt.Edge.BottomEdge,
        ):
            return Qt.CursorShape.SizeVerCursor

        return Qt.CursorShape.ArrowCursor

class MainWindow(QMainWindow):
    CORNER_RADIUS = 18

    def __init__(self):
        super().__init__()

        self.setWindowTitle("YOINK — The ChatSnatcher")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setStyleSheet(APP_STYLE)

        self._build_ui()
        self.split_selector._select("Number of Parts")

        self.resize_controller = ResizeController(self)

        self._fit_initial_size()

        self._results_animation = None
        self._results_resetting = False
        self._close_after_results = False

        # Permanent startup baseline.
        self._startup_size = self.size()

        # Temporary extraction geometry used for the current result expansion.
        self._current_extraction_geometry = self.geometry()

        self._extraction_card_width = 0

        # Preloading state.
        self._preload_version = 0
        self._preload_thread = None
        self._preload_worker = None
        self._preload_threads = []
        self._preloading_versions = {}
        self._extraction_threads = []
        self._closing = False
        self._shutdown_complete = False
        self._shutdown_screen = None
        self._shutdown_overlay = None
        self._preloaded_extraction = None
        self._preloaded_version = None
        self._waiting_for_preload = False

        self._operation_settings = None

        self.update_checker = UpdateChecker(self)
        self.update_checker.completed.connect(self._update_checked)
        self.update_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        self.update_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.update_shortcut.activated.connect(lambda: self.update_checker.check(manual=True))
        self._update_dialog = None
        QTimer.singleShot(0, self.update_checker.check)

    def _update_checked(self, manual, release, failed):
        if self._closing or self._close_after_results:
            return
        if release is None and not manual:
            return
        if self._update_dialog is not None:
            self._update_dialog.close()
        if release:
            version, url = release
            message = f"YOINK {version} is available."
            actions = [("View Release", lambda: QDesktopServices.openUrl(QUrl(url))),
                       ("Later", None)]
        else:
            message = (
                "Couldn't check for updates. Check your connection and try Ctrl+U again later."
                if failed else f"YOINK is up to date (v{VERSION})."
            )
            actions = [("OK", None)]
        dialog = UpdateDialog(self, message, actions)
        dialog.finished.connect(lambda: setattr(self, "_update_dialog", None))
        self._update_dialog = dialog
        dialog.setModal(False)
        dialog.show()

    def _build_ui(self):
        self.background = Background()
        self.background.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setCentralWidget(self.background)

        # ============================================================
        # WINDOW LAYOUT — outer window padding / spacing
        # ============================================================
        root_layout = QVBoxLayout(self.background)

        # Outside-card/window padding:
        # (left, top, right, bottom)
        root_layout.setContentsMargins(14, 4, 14, 20)

        # Default spacing between items in the window layout.
        root_layout.setSpacing(5)

        # Title bar
        self.title_bar = TitleBar(self)
        root_layout.addWidget(self.title_bar)

        # Main card
        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        # ============================================================
        # CARD LAYOUT — inside-card padding / default spacing
        # ============================================================
        card_layout = QVBoxLayout(self.card)

        # Inside-card padding:
        # (left, top, right, bottom)
        card_layout.setContentsMargins(20, 14, 20, 14)

        # Default spacing between items inside the card.
        # Section-specific spacing is controlled with addSpacing() below.
        card_layout.setSpacing(5)

        # ============================================================
        # URL SECTION — label, input, validation message
        # ============================================================
        url_label = QLabel("SHARED CONVERSATION URL")
        url_label.setStyleSheet(
            "font-size: 9px; font-weight: 700;"
        )

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste a ChatGPT shared conversation URL..."
        )
        self.url_input.setFixedHeight(40)

        self.url_input.setStyleSheet(
            """
            QLineEdit {
                background: #0F1012;
                color: #F2F2F4;
                border: 1px solid #303137;
                border-radius: 9px;
                padding: 0 12px;
                font-size: 13px;
            }

            QLineEdit::placeholder {
                color: #6F717A;
            }

            QLineEdit:focus {
                border: 1px solid #4D7CFE;
            }

            QLineEdit:disabled {
                background: #D5D5D8;
                color: #8A8B91;
                border: 1px solid #B8B9BE;
            }

            QLineEdit[urlValid="false"] {
                border: 1px solid #FF5C5C;
            }
            """
        )

        self.url_error = QLabel(" ")
        self.url_error.setObjectName("UrlError")

        self.url_input.returnPressed.connect(
            self.url_input.clearFocus
        )

        self.url_input.textChanged.connect(
            self._url_changed
        )

        self.url_input.editingFinished.connect(
            self._url_editing_finished
        )

        card_layout.addWidget(url_label)
        card_layout.addSpacing(5)
        card_layout.addWidget(self.url_input)
        card_layout.addWidget(self.url_error)

        # URL SECTION → EXTRACTION MODE spacing
        card_layout.addSpacing(3)

        # ============================================================
        # EXTRACTION MODE SECTION — label + radio buttons
        # ============================================================
        mode_label = QLabel("EXTRACTION MODE")
        mode_label.setStyleSheet(
            "font-size: 9px; font-weight: 700;"
        )

        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(18)

        self.ai_radio = QRadioButton("A.I.")
        self.user_radio = QRadioButton("User")
        self.both_radio = QRadioButton("Both")

        self.ai_radio.setChecked(True)

        mode_layout.addStretch()

        mode_layout.addWidget(self.ai_radio)
        mode_layout.addSpacing(15)
        mode_layout.addWidget(self.user_radio)
        mode_layout.addSpacing(15)
        mode_layout.addWidget(self.both_radio)

        mode_layout.addStretch()

        card_layout.addWidget(mode_label)
        card_layout.addSpacing(5)
        card_layout.addLayout(mode_layout)

        # EXTRACTION MODE → SPLIT OUTPUT spacing
        card_layout.addSpacing(22)

        # ============================================================
        # SPLIT OUTPUT SECTION — label + selector + value
        # ============================================================
        split_label = QLabel("SPLIT OUTPUT")
        split_label.setStyleSheet(
            "font-size: 9px; font-weight: 700;"
        )

        self.split_selector = SplitSelector(
            [
                "Character Limit",
                "Number of Parts",
                "Messages per Part",
            ]
        )

        self.split_value = QLineEdit()
        self.split_value.setFixedHeight(40)
        self.split_value.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.split_value.setPlaceholderText(
            "[ character limit · default 9000 ]"
        )
        self.split_value.setValidator(
            QIntValidator(1, 999999, self)
        )

        self.split_value.returnPressed.connect(
            self.split_value.clearFocus
        )
        self.split_value.textChanged.connect(self._clear_split_error)

        self.split_value.setStyleSheet(
            """
            QLineEdit {
                background: #0F1012;
                color: #F2F2F4;
                border: 1px solid #303137;
                border-radius: 9px;
                padding: 0 12px;
                font-size: 13px;
            }

            QLineEdit::placeholder {
                color: #6F717A;
            }

            QLineEdit:focus {
                border: 1px solid #4D7CFE;
            }
            """
        )

        self.split_value.setStyleSheet(self.split_value.styleSheet() + """
            QLineEdit:disabled {
                color: #777A84;
                background: #17181C;
                border: 1px solid #292B31;
            }
            QLineEdit[splitValid="false"] {
                border: 1px solid #FF5C5C;
            }
        """)

        card_layout.addWidget(split_label)
        card_layout.addSpacing(5)
        card_layout.addWidget(self.split_selector)
        card_layout.addWidget(self.split_value)

        self.split_selector.changed.connect(
            self._reset_split_value
        )

        # ============================================================
        # EXTRACTION ERROR — inline recovery message
        # ============================================================
        self.extraction_error = QLabel("")
        self.extraction_error.setObjectName("ExtractionError")
        self.extraction_error.setWordWrap(True)
        self.extraction_error.hide()

        # ============================================================
        # EXTRACT BUTTON — final action
        # ============================================================
        self.extract_button = ProgressButton("EXTRACT")
        self.extract_button.setEnabled(True)

        self.extract_button.clicked.connect(
            self._extract_conversation
        )

        # SPLIT OUTPUT → EXTRACT BUTTON spacing
        card_layout.addSpacing(50)

        card_layout.addWidget(self.extraction_error)
        card_layout.addWidget(self.extract_button)

        # EXTRACT BUTTON → CARD BOTTOM spacing
        card_layout.addSpacing(5)

        # ============================================================
        # MAIN CONTENT — extraction card + results panel
        # ============================================================
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)

        self.results_panel = QFrame()
        self.results_panel.setObjectName("ResultsPanel")
        self.results_panel.setStyleSheet(
            """
            QFrame#ResultsPanel {
                background: #15161A;
                border-radius: 12px;
            }

            QFrame#ResultsPanel QScrollArea {
                background: transparent;
                border: none;
            }

            QFrame#ResultPartCard {
                background: transparent;
                border: 1px solid #303137;
                border-radius: 9px;
            }

            QFrame#ResultPartCard:hover {
                border: 1px solid #4D7CFE;
            }

            QFrame#ResultPartCard QLabel {
                border: none;
                background: transparent;
                font-size: 10px;
            }

            QFrame#ResultPartCard QPushButton {
                background: transparent;
                color: #B8BAC2;
                border: none;
                border-radius: 6px;
                padding: 0;
            }

            QFrame#ResultPartCard QPushButton:hover {
                background: #252830;
                color: #FFFFFF;
            }
            """
        )
        self.results_panel.hide()

        results_layout = QVBoxLayout(self.results_panel)
        results_layout.setContentsMargins(16, 14, 16, 14)
        results_layout.setSpacing(8)

        results_title = QLabel("RESULTS")
        results_title.setStyleSheet(
            "font-size: 9px; font-weight: 700;"
        )

        self.results_messages = QLabel(
            "Total of 0 messages found"
        )

        self.results_total_characters = QLabel(
            "0 characters in entire conversation"
        )

        self.results_role_breakdown = QLabel(
            "0 AI · 0 User"
        )

        self.results_extraction_mode = QLabel(
            "Extracted: AI only"
        )

        self.results_extracted_characters = QLabel(
            "0 characters"
        )
        
        self.results_parts = QLabel(
            "Split into 0 parts"
        )
        # ------------------------------------------------------------
        # Results summary row + preview button
        # ------------------------------------------------------------

        summary_row = QHBoxLayout()
        summary_row.setContentsMargins(0, 0, 0, 0)
        summary_row.setSpacing(8)

        summary_text_layout = QVBoxLayout()
        summary_text_layout.setContentsMargins(0, 0, 0, 0)
        summary_text_layout.setSpacing(3)

        summary_text_layout.addWidget(
            self.results_messages
        )
        summary_text_layout.addWidget(
            self.results_total_characters
        )
        summary_text_layout.addWidget(
            self.results_role_breakdown
        )
        summary_text_layout.addSpacing(4)
        summary_text_layout.addWidget(
            self.results_extraction_mode
        )
        summary_text_layout.addWidget(
            self.results_extracted_characters
        )

        summary_text_layout.addWidget(
            self.results_parts
        )

        self.preview_button = QPushButton("[ PREVIEW ]")
        self.preview_button.setFixedHeight(32)
        self.preview_button.setMinimumWidth(86)
        self.preview_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.preview_button.setToolTip(
            "Preview entire thread"
        )
        self.preview_button.setStyleSheet(
            """
            QPushButton {
                background: #1B2340;
                color: #B8BAC2;
                border: 1px solid #303137;
                border-radius: 7px;
                padding: 0 10px;
                font-size: 9px;
                font-weight: 700;
            }

            QPushButton:hover {
                background: #252F55;
                color: #FFFFFF;
                border: 1px solid #4D7CFE;
            }

            QPushButton:pressed {
                background: #4D7CFE;
                color: #FFFFFF;
                border: 1px solid #4D7CFE;
            }
            """
        )
        self.preview_button.clicked.connect(
            self._preview_entire_thread
        )

        summary_row.addLayout(
            summary_text_layout
        )
        summary_row.addStretch()
        preview_actions = QVBoxLayout()
        preview_actions.addWidget(self.preview_button)
        self.scratchpad_button = QPushButton("[ SCRATCHPAD ]")
        self.scratchpad_button.setFixedHeight(32)
        self.scratchpad_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scratchpad_button.setStyleSheet(self.preview_button.styleSheet())
        self.scratchpad_button.setToolTip("Open this session's scratchpad")
        self.scratchpad_button.clicked.connect(self._show_scratchpad)
        preview_actions.addWidget(self.scratchpad_button)
        preview_actions.addStretch()
        summary_row.addLayout(preview_actions)

        self.copy_all_button = ProgressButton("COPY ALL")
        self._copy_all_timer = QTimer(self.copy_all_button)
        self._copy_all_timer.setSingleShot(True)
        self._copy_all_timer.setInterval(1000)
        self._copy_all_timer.timeout.connect(self._reset_copy_all_button)
        self.copy_all_button.clicked.connect(
            self._copy_all_parts
        )

        results_layout.addWidget(results_title)
        results_layout.addSpacing(4)
        results_layout.addLayout(summary_row)
        results_layout.addSpacing(4)

        # Keep this dialog in memory: closing it only hides it for this session.
        self.scratchpad_dialog = QDialog(self)
        self.scratchpad_dialog.setWindowTitle("Scratchpad")
        self.scratchpad_dialog.resize(640, 460)
        self.scratchpad_dialog.setStyleSheet("QDialog { background: #0F1012; }")
        scratchpad_layout = QVBoxLayout(self.scratchpad_dialog)
        scratchpad_layout.setContentsMargins(16, 16, 16, 16)
        scratchpad_layout.setSpacing(10)
        scratchpad_label = QLabel("SCRATCHPAD · THIS EXTRACTION SESSION ONLY")
        scratchpad_label.setStyleSheet("color: #F2F2F4; font-size: 10px; font-weight: 700;")
        scratchpad_layout.addWidget(scratchpad_label)
        self.scratchpad_copy = QPushButton("COPY SCRATCHPAD")
        self.scratchpad_copy.setStyleSheet(self.preview_button.styleSheet())
        self.scratchpad_copy.setFixedHeight(36)
        self.scratchpad_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scratchpad_copy.setToolTip("Copy the entire scratchpad")
        self.scratchpad = QPlainTextEdit()
        self.scratchpad.setPlaceholderText(
            "Type or paste the useful bits here.\n\n"
            "Closing this window keeps your notes. Extract Another Thread or closing YOINK clears them."
        )
        self.scratchpad.setStyleSheet("""
            QPlainTextEdit {
                background: #15161A; color: #E7E7EA;
                border: 1px solid #303137; border-radius: 10px;
                padding: 18px; font-size: 12px;
            }
            QPlainTextEdit:focus { border-color: #4D7CFE; }
        """)
        self.scratchpad_copy.clicked.connect(
            lambda: QApplication.clipboard().setText(self.scratchpad.toPlainText())
        )
        scratchpad_layout.addWidget(self.scratchpad, 1)
        scratchpad_layout.addWidget(self.scratchpad_copy)

        # Scrollable result parts area.
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        results_scroll.setFrameShape(QFrame.Shape.NoFrame)
        results_scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea > QWidget {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #303137;
                border-radius: 3px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #555861;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

        self.results_container = QWidget()
        self.results_container.setStyleSheet(
            "background: transparent;"
        )

        self.results_container_layout = QVBoxLayout(self.results_container)
        self.results_container_layout.setContentsMargins(0, 8, 8, 0)
        self.results_container_layout.setSpacing(6)

        results_scroll.setWidget(self.results_container)

        results_layout.addWidget(results_scroll, 1)

        # Create bottom action buttons.
        self.extract_another_button = ProgressButton(
            "EXTRACT ANOTHER THREAD"
        )
        self.extract_another_button.setFixedHeight(32)
        self.extract_another_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.extract_another_button.set_results_press_style(True)
        self.extract_another_button.clicked.connect(
            self._reset_results_session
        )

        # Copy controls stay below the scrollable results area.
        results_layout.addSpacing(4)

        results_layout.addWidget(self.copy_all_button)

        results_layout.addSpacing(4)

        results_layout.addWidget(
            self.extract_another_button
        )

        self.content_layout.addWidget(
            self.card,
            1,
        )
        self.content_layout.addWidget(
            self.results_panel,
            1,
        )

        root_layout.addLayout(self.content_layout)

    def _show_scratchpad(self):
        if (not getattr(self, "_conversation", None) or self._results_resetting
                or self._closing or self._close_after_results):
            return
        self.scratchpad_dialog.show()
        self.scratchpad_dialog.raise_()
        self.scratchpad_dialog.activateWindow()
        self.scratchpad.setFocus()

    def _preview_entire_thread(self):
        if not self._conversation:
            return

        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(
            "Preview Entire Thread"
        )
        preview_dialog.resize(820, 700)

        preview_dialog.setStyleSheet(
            """
            QDialog {
                background: #0F1012;
            }

            QLabel#PreviewTitle {
                color: #F2F2F4;
                font-size: 10px;
                font-weight: 700;
            }

            QTextBrowser {
                background: #15161A;
                color: #E7E7EA;
                border: 1px solid #303137;
                border-radius: 10px;
                padding: 18px;
                font-size: 12px;
            }
            """
        )

        layout = QVBoxLayout(preview_dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("ENTIRE THREAD")
        title.setObjectName("PreviewTitle")

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)

        # --------------------------------------------------------
        # Preview-only styling
        #
        # The actual Markdown remains unchanged.
        # We only make the generated HTML easier to read.
        # --------------------------------------------------------

        preview_css = """
        <style>

            body {
                color: #E7E7EA;
                background: #15161A;
                font-family: "Inter", "Segoe UI", sans-serif;
                font-size: 12px;
                line-height: 1.55;
                margin: 0;
            }

            h1 {
                color: #FFFFFF;
                font-size: 22px;
                margin-top: 4px;
                margin-bottom: 16px;
            }

            h2 {
                color: #FFFFFF;
                font-size: 17px;
                margin-top: 24px;
                margin-bottom: 12px;
            }

            h3 {
                color: #F2F2F4;
                font-size: 15px;
                font-weight: 700;
                margin-top: 24px;
                margin-bottom: 12px;
                padding: 7px 10px;
                border-left: 3px solid #4D7CFE;
                border-bottom: 1px solid #303137;
            }

            p {
                margin-top: 7px;
                margin-bottom: 10px;
            }

            strong {
                color: #FFFFFF;
            }

            em {
                color: #C9CBD2;
            }

            ul,
            ol {
                margin-top: 8px;
                margin-bottom: 12px;
                padding-left: 24px;
            }

            li {
                margin-bottom: 4px;
            }

            code {
                color: #D7D9E0;
                background: #202127;
                padding: 2px 5px;
                border-radius: 4px;
            }

            pre {
                background: #0D0E11;
                border: 1px solid #2C2E35;
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
                margin-bottom: 14px;
            }

            pre code {
                background: transparent;
                padding: 0;
            }

            blockquote {
                border-left: 3px solid #4D7CFE;
                margin-left: 0;
                padding-left: 12px;
                color: #BFC1C9;
            }

            a {
                color: #6F96FF;
            }

            hr {
                border: none;
                border-top: 1px solid #303137;
                margin-top: 18px;
                margin-bottom: 18px;
            }

            table {
                border-collapse: collapse;
                margin-top: 10px;
                margin-bottom: 14px;
            }

            th,
            td {
                border: 1px solid #303137;
                padding: 7px 9px;
            }

            th {
                background: #1B1D23;
                color: #FFFFFF;
            }

            td {
                background: #17181D;
            }

        </style>
        """

        roles = PreviewRoleSelector()
        header = QHBoxLayout()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(roles)
        layout.addLayout(header)
        layout.addWidget(browser, 1)

        # Convert each full-conversation message once per opening. Retain parsed
        # documents too, so clicks do not repeat Qt's HTML parsing/layout work.
        layout.activate()
        documents = {}
        for role, html in render_preview_variants(self._conversation).items():
            document = QTextDocument(preview_dialog)
            document.setDefaultFont(browser.font())
            document.setHtml(preview_css + html)
            browser.setDocument(document)
            document.documentLayout().documentSize()
            documents[role] = document

        def render(role):
            browser.setDocument(documents[role])
            browser.verticalScrollBar().setValue(0)

        roles.changed.connect(render)
        render("all")

        preview_dialog.exec()
        preview_dialog.deleteLater()

    def _copy_all_parts(self):
        if not self._parts:
            return

        QApplication.clipboard().setText(
            "\n\n".join(self._parts)
        )

        self.copy_all_button.setText("COPIED")

        self._copy_all_timer.start()

    def _reset_copy_all_button(self):
        self.copy_all_button.setText("COPY ALL")

    def _build_result_cards(self):
        # Clear any existing result cards.
        while self.results_container_layout.count():
            item = self.results_container_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        # Create one compact card per extracted part.
        for index, part in enumerate(self._parts, start=1):
            card = QFrame()
            card.setObjectName("ResultPartCard")

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(
                12, 8, 8, 8
            )
            card_layout.setSpacing(8)

            part_label = QLabel(
                f"PART {index} · {len(part):,} characters"
            )

            copy_button = QPushButton("⧉")
            copy_button.setFixedSize(30, 30)
            copy_button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            copy_button.setToolTip(f"Copy Part {index}")
            copy_button.setStyleSheet(
                """
                QPushButton {
                    background: transparent;
                    color: #B8BAC2;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    padding: 0;
                }

                QPushButton:hover {
                    background: #1B2340;
                    color: #FFFFFF;
                    border: 1px solid #4D7CFE;
                }

                QPushButton:pressed {
                    background: #4D7CFE;
                    color: #FFFFFF;
                    border: 1px solid #4D7CFE;
                }
                """
            )

            confirmation_timer = QTimer(copy_button)
            confirmation_timer.setSingleShot(True)
            confirmation_timer.setInterval(1000)
            confirmation_timer.timeout.connect(
                lambda button=copy_button: button.setText("⧉")
            )

            def copy_part(
                checked=False,
                text=part,
                button=copy_button,
                timer=confirmation_timer,
            ):
                QApplication.clipboard().setText(text)
                button.setText("✔")

                timer.start()

            copy_button.clicked.connect(copy_part)

            card_layout.addWidget(part_label)
            card_layout.addStretch()
            card_layout.addWidget(copy_button)

            self.results_container_layout.addWidget(card)

        self.results_container_layout.addStretch()

    def _reset_results_session(self):
        if self._results_resetting:
            return
        self._results_resetting = True
        self._stop_input_shake()
        self.scratchpad_dialog.close()
        self.results_panel.setEnabled(False)
        # Invalidate incoming preload data immediately, but keep the displayed
        # results intact until the panel has completely retreated.
        self._preload_version += 1
        self._preloaded_extraction = None
        self._preloaded_version = None
        self._waiting_for_preload = False
        self._operation_settings = None

        # Collapse both together, without leaving empty layout space that
        # would pull the extraction card sideways before the window follows.
        self.setMinimumSize(self._startup_size)
        target_geometry = QRect(self.geometry().topLeft(), self._startup_size)
        target_geometry.moveCenter(self.geometry().center())

        def finish_reset():
            self.results_panel.hide()
            self.scratchpad.clear()
            self._copy_all_timer.stop()
            self._reset_copy_all_button()
            self._conversation = None
            self._extracted_conversation = None
            self._extraction_mode = None
            self._markdown = None
            self._parts = []
            while self.results_container_layout.count():
                item = self.results_container_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.results_panel.setMinimumWidth(0)
            self.results_panel.setMaximumWidth(0)
            self.content_layout.setSpacing(10)
            self.url_input.clear()
            self.split_selector._select("Number of Parts")
            self._reset_split_value("Number of Parts")
            self._operation_settings = None
            self._set_operation_controls_enabled(True)
            self.extract_button.set_processing(False)
            self.extract_button.set_recovery(False)
            self.extraction_error.clear()
            self.extraction_error.hide()
            self._validate_url()
            self._update_window_mask()
            self._results_resetting = False
            if self._close_after_results:
                self._close_after_results = False
                self.close()
            else:
                self.url_input.setFocus(Qt.FocusReason.OtherFocusReason)

        self._animate_results_geometry(
            target_geometry, 0, 300, QEasingCurve.Type.InCubic, finish_reset,
        )

    def _animate_results_geometry(
        self, target_geometry, panel_width, duration, easing, finished,
    ):
        if self._results_animation is not None:
            self._results_animation.stop()
            self._results_animation.deleteLater()

        self.results_panel.setMinimumWidth(0)
        start_geometry = self.geometry()
        start_panel_width = self.results_panel.maximumWidth()
        start_gap = self.content_layout.spacing()
        end_gap = 10 if panel_width else 0

        def update_frame(progress):
            def interpolate(start, end):
                return round(start + (end - start) * progress)

            # One animation clock and shared rounding keep the card stable.
            # Animate the gap too, so hiding the panel adds no final jump.
            gap = interpolate(start_gap, end_gap)
            panel_extent = interpolate(
                start_panel_width + start_gap, panel_width + end_gap,
            )
            self.content_layout.setSpacing(gap)
            self.results_panel.setMaximumWidth(max(0, panel_extent - gap))
            geometry = QRect(start_geometry)
            geometry.setWidth(interpolate(start_geometry.width(), target_geometry.width()))
            geometry.setHeight(interpolate(start_geometry.height(), target_geometry.height()))
            # Use relative offsets rather than QRect.moveCenter(), whose
            # integer rounding can drift on monitors at negative coordinates.
            geometry.moveLeft(
                start_geometry.x() + (start_geometry.width() - geometry.width()) // 2
            )
            geometry.moveTop(
                start_geometry.y() + (start_geometry.height() - geometry.height()) // 2
            )
            self.setGeometry(geometry)

        self._results_animation = QVariantAnimation(self)
        self._results_animation.setDuration(duration)
        self._results_animation.setStartValue(0.0)
        self._results_animation.setEndValue(1.0)
        self._results_animation.setEasingCurve(easing)
        self._results_animation.valueChanged.connect(update_frame)
        self._results_animation.finished.connect(finished)
        self._results_animation.start()

    def _show_results(self):
        self.results_panel.setEnabled(True)
        full_messages = self._conversation["messages"]

        total_messages = len(full_messages)

        total_characters = sum(
            len(message["text"])
            for message in full_messages
        )

        ai_count = sum(
            1
            for message in full_messages
            if message["role"] == "assistant"
        )

        user_count = sum(
            1
            for message in full_messages
            if message["role"] == "user"
        )

        extracted_characters = sum(
            len(message["text"])
            for message in self._extracted_conversation["messages"]
        )

        if self._extraction_mode == "assistant":
            extraction_label = "AI only"
        elif self._extraction_mode == "user":
            extraction_label = "User only"
        else:
            extraction_label = "Entire conversation"

        self.results_messages.setText(
            f"Total of {total_messages:,} messages found"
        )

        self.results_total_characters.setText(
            f"{total_characters:,} characters in entire conversation"
        )

        self.results_role_breakdown.setText(
            f"{ai_count:,} AI · {user_count:,} User"
        )

        self.results_extraction_mode.setText(
            f"Extracted: {extraction_label}"
        )

        self.results_extracted_characters.setText(
            f"{extracted_characters:,} characters"
        )

        self.results_parts.setText(
            f"Split into {len(self._parts):,} parts"
        )

        self._build_result_cards()

        # Capture the current extraction geometry for this result session.
        self._current_extraction_geometry = self.geometry()

        self._extraction_card_width = self.card.width()

        extraction_width = self._extraction_card_width

        expanded_width = (
            self._current_extraction_geometry.width()
            + extraction_width
            + self.content_layout.spacing()
        )

        # Expand equally to either side of the current window center.
        final_geometry = QRect(self._current_extraction_geometry)
        final_geometry.setWidth(expanded_width)
        final_geometry.moveCenter(self._current_extraction_geometry.center())

        self.results_panel.setMinimumWidth(0)
        self.results_panel.setMaximumWidth(0)
        self.content_layout.setSpacing(0)
        self.results_panel.show()

        def finish_results_animation():
            self.results_panel.setMinimumWidth(
                extraction_width
            )
            self.results_panel.setMaximumWidth(
                extraction_width
            )
            self.setMinimumWidth(expanded_width)
            self._update_window_mask()

        self._animate_results_geometry(
            final_geometry, extraction_width, 350,
            QEasingCurve.Type.OutCubic, finish_results_animation,
        )

    def _extract_conversation(self):
        if self._closing or self._close_after_results or not self.url_input.isEnabled():
            return

        url = self.url_input.text().strip()

        self.extraction_error.clear()
        self.extraction_error.hide()
        self.extract_button.set_recovery(False)

        self._stop_input_shake()
        self._validate_url(required=True)
        invalid_field = None if self.url_input.property("urlValid") else self.url_input

        if self.ai_radio.isChecked():
            mode = "assistant"
        elif self.user_radio.isChecked():
            mode = "user"
        else:
            mode = "both"

        split_mode = self.split_selector.currentText()
        split_value = self.split_value.text().strip()
        self._clear_split_error()
        if not split_value and split_mode != "Character Limit":
            self._show_split_error(
                "Enter messages per part." if split_mode == "Messages per Part"
                else "Enter the number of parts."
            )
            invalid_field = invalid_field or self.split_value
        elif split_value:
            try:
                valid = 1 <= int(split_value) <= 999999 and self.split_value.hasAcceptableInput()
            except ValueError:
                valid = False
            if not valid:
                self._show_split_error("Enter a whole number from 1 to 999999.")
                invalid_field = invalid_field or self.split_value

        if invalid_field is not None:
            invalid_field.setFocus(Qt.FocusReason.OtherFocusReason)
            self._shake_input(invalid_field)
            return

        # EXTRACT commits one immutable set of settings, including while
        # waiting for an already-running preload.
        self._operation_settings = (url, mode, split_mode, split_value)
        self._set_operation_controls_enabled(False)
        self.extract_button.set_processing(True)

        if (
            self._preloaded_extraction is None
            and self._preload_version in self._preloading_versions
        ):
            self._waiting_for_preload = True
            return
        self._start_extraction()

    def _stop_input_shake(self):
        if getattr(self, "_input_shake", None) is not None:
            animation, field, origin = self._input_shake
            animation.stop()
            field.move(origin)
            animation.deleteLater()
            self._input_shake = None

    def _shake_input(self, field):
        # One small, local nudge; never move the window or animate several fields.
        self.layout().activate()
        origin = field.pos()
        animation = QPropertyAnimation(field, b"pos", self)
        animation.setDuration(180)
        for step, offset in ((0, 0), (.2, -3), (.4, 3), (.6, -2), (.8, 2), (1, 0)):
            animation.setKeyValueAt(step, origin + QPoint(offset, 0))
        self._input_shake = animation, field, origin
        animation.finished.connect(self._stop_input_shake)
        animation.start()

    def _set_operation_controls_enabled(self, enabled):
        for control in (
            self.url_input, self.ai_radio, self.user_radio, self.both_radio,
            self.split_selector, self.split_value,
        ):
            control.setEnabled(enabled)

    def _start_extraction(self):
        if self._closing or self._close_after_results or self._operation_settings is None:
            return
        url, mode, split_mode, split_value = self._operation_settings
        self._extraction_thread = QThread()
        preloaded_extraction = None

        if (
            self._preloaded_extraction is not None
            and self._preloaded_version == self._preload_version
        ):
            preloaded_extraction = (
                self._preloaded_extraction
            )

        self._extraction_worker = ExtractionWorker(
            url,
            mode,
            split_mode,
            split_value,
            preloaded_extraction,
        )

        self._extraction_worker.moveToThread(
            self._extraction_thread
        )

        self._extraction_thread.started.connect(
            self._extraction_worker.run
        )

        self._extraction_worker.progress.connect(
            self._extraction_progress
        )

        self._extraction_worker.finished.connect(
            self._extraction_finished
        )

        self._extraction_worker.error.connect(
            self._extraction_error
        )

        self._extraction_worker.finished.connect(
            self._extraction_thread.quit
        )

        self._extraction_worker.error.connect(
            self._extraction_thread.quit
        )

        self._extraction_thread.finished.connect(
            self._extraction_worker.deleteLater
        )

        self._extraction_thread.finished.connect(
            self._extraction_thread.deleteLater
        )

        thread = self._extraction_thread
        self._extraction_threads.append(thread)

        def cleanup():
            self._extraction_threads.remove(thread)

        thread.finished.connect(cleanup)
        thread.finished.connect(self._check_shutdown)

        self._extraction_thread.start()

    def _extraction_progress(self, stage, percentage):
        if self._closing or self._close_after_results:
            return
        self.extract_button.set_progress(
            stage,
            percentage,
        )

    def _extraction_finished(self, result):
        if self._closing or self._close_after_results:
            return
        self._conversation = result["conversation"]
        self._extracted_conversation = result[
            "extracted_conversation"
        ]
        self._markdown = result["markdown"]
        self._parts = result["parts"]
        self._extraction_mode = result["mode"]

        self.extract_button.set_progress(
            "DONE",
            100,
        )

        self._show_results()

        print(
            f"Messages: {len(self._conversation['messages'])}"
        )
        print(
            f"Extracted messages: "
            f"{len(self._extracted_conversation['messages'])}"
        )
        print(
            f"Markdown length: "
            f"{len(self._markdown)} characters"
        )
        print(f"Parts: {len(self._parts)}")

    def _extraction_error(self, message):
        if self._closing or self._close_after_results:
            return
        print(f"Error: {message}")

        self.extraction_error.setText(message)
        self.extraction_error.show()

        self._operation_settings = None
        self._waiting_for_preload = False
        self._set_operation_controls_enabled(True)

        self.extract_button.set_processing(False)
        self.extract_button.set_recovery(True)

    def _show_split_error(self, message):
        self.split_value.setProperty("splitValid", False)
        self.split_value.style().unpolish(self.split_value)
        self.split_value.style().polish(self.split_value)
        self.split_value.update()
        self.extraction_error.setProperty("inputError", True)
        self.extraction_error.style().unpolish(self.extraction_error)
        self.extraction_error.style().polish(self.extraction_error)
        self.extraction_error.setText(message)
        self.extraction_error.show()

    def _clear_split_error(self):
        self.split_value.setProperty("splitValid", None)
        self.split_value.style().unpolish(self.split_value)
        self.split_value.style().polish(self.split_value)
        self.split_value.update()
        if self.extraction_error.property("inputError"):
            self.extraction_error.clear()
            self.extraction_error.hide()
            self.extraction_error.setProperty("inputError", None)
            self.extraction_error.style().unpolish(self.extraction_error)
            self.extraction_error.style().polish(self.extraction_error)

    def _reset_split_value(self, mode):
        self.split_value.clear()
        self._clear_split_error()

        if mode == "Character Limit":
            self.split_value.setPlaceholderText(
                "[ character limit · default 9000 ]"
            )
        elif mode == "Messages per Part":
            self.split_value.setPlaceholderText("[ enter messages per part ]")
        else:
            self.split_value.setPlaceholderText(
                "[ enter number of parts ]"
            )

    def _url_changed(self):
        # Any URL edit invalidates the previous preload.
        self._preload_version += 1
        self._preloaded_extraction = None
        self._preloaded_version = None
        # Editing is neutral; validate only when editing finishes. Do not
        # leave an old URL's error on the new text.
        self.url_input.setProperty("urlValid", None)
        self.url_error.setText(" ")
        self.url_input.style().unpolish(self.url_input)
        self.url_input.style().polish(self.url_input)
        self.url_input.update()
        self.extract_button.setEnabled(
            self._operation_settings is None and not self._closing and not self._close_after_results
        )
        if self._operation_settings is None and not self._results_resetting:
            self.extraction_error.clear()
            self.extraction_error.hide()
            self.extract_button.set_recovery(False)

    def _url_editing_finished(self):
        if (
            self._closing or self._close_after_results or self._results_resetting
            or self._operation_settings is not None
        ):
            return
        self._validate_url()

        if not self.url_input.property("urlValid"):
            return

        if not self.split_value.hasAcceptableInput() and not (
            self.split_selector.currentText() == "Character Limit" and not self.split_value.text()
        ):
            return

        self._start_preload(
            self.url_input.text().strip()
        )

    def _start_preload(self, url):
        if self._closing or self._close_after_results:
            return
        version = self._preload_version
        if version in self._preloading_versions:
            return

        print(f"PRELOAD START: version {version}")

        thread = QThread()
        self._preloading_versions[version] = thread
        worker = PreloadWorker(
            version,
            url,
        )

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.finished.connect(self._preload_finished)
        worker.error.connect(self._preload_error)

        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)

        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # Keep every running preload thread alive until it finishes.
        self._preload_threads.append(thread)

        def cleanup():
            if thread in self._preload_threads:
                self._preload_threads.remove(thread)
            if self._preloading_versions.get(version) is thread:
                self._preloading_versions.pop(version)

        thread.finished.connect(cleanup)
        thread.finished.connect(self._check_shutdown)

        # Keep the latest preload references for current-state checks.
        self._preload_thread = thread
        self._preload_worker = worker

        thread.start()

    def _check_shutdown(self):
        if self._closing and not self._preload_threads and not self._extraction_threads:
            self._finish_shutdown()

    def _preload_finished(self, version, extraction):
        self._preloading_versions.pop(version, None)
        if self._closing or self._close_after_results or version != self._preload_version:
            return

        self._preloaded_extraction = extraction
        self._preloaded_version = version

        print("PRELOAD COMPLETE")

        if self._waiting_for_preload:
            self._waiting_for_preload = False
            self._start_extraction()

    def _preload_error(self, version, message):
        # The result is terminal even if QThread teardown is still queued.
        # A Retry must not wait for another result from this finished worker.
        self._preloading_versions.pop(version, None)
        if self._closing or self._close_after_results or version != self._preload_version:
            return

        self._preloaded_extraction = None
        self._preloaded_version = None

        print(f"PRELOAD ERROR: {message}")

        if self._waiting_for_preload:
            self._waiting_for_preload = False
            self._extraction_error(message)

    def _validate_url(self, required=False):
        url = self.url_input.text().strip()

        if not url:
            self.url_input.setProperty("urlValid", False if required else None)
            self.url_error.setText("Enter a shared conversation URL." if required else " ")

        elif not re.match(
            r"^https?://[^\s]+$",
            url,
        ):
            self.url_input.setProperty(
                "urlValid",
                False,
            )
            self.url_error.setText("Invalid URL.")
            self.url_error.show()

        elif re.match(
            r"^https?://(chatgpt\.com|chat\.openai\.com)/?$",
            url,
        ):
            self.url_input.setProperty(
                "urlValid",
                False,
            )
            self.url_error.setText(
                "Incomplete URL."
            )

        elif not re.match(
            r"^https?://(chatgpt\.com|chat\.openai\.com)/share/[^\s]+$",
            url,
        ):
            self.url_input.setProperty(
                "urlValid",
                False,
            )
            self.url_error.setText(
                "Unsupported platform or share format."
            )

        else:
            self.url_input.setProperty("urlValid", True)
            self.url_error.setText(" ")

        self.url_input.style().unpolish(self.url_input)
        self.url_input.style().polish(self.url_input)
        self.url_input.update()

        self.extract_button.setEnabled(
            self._operation_settings is None
            and not self._closing and not self._close_after_results
        )

    def _fit_initial_size(self):
        self.layout().activate()

        height = self.layout().sizeHint().height()

        self.setMinimumWidth(400)
        self.setMinimumHeight(height)

        self.resize(400, height)

        self._update_window_mask()

    def _update_window_mask(self):
        rect = self.rect().adjusted(0, 0, -1, -1)

        path = QPainterPath()
        path.addRoundedRect(
            rect,
            self.CORNER_RADIUS,
            self.CORNER_RADIUS,
        )

        self.setMask(
            QRegion(
                path.toFillPolygon().toPolygon()
            )
        )

    def resizeEvent(self, event):
        self._update_window_mask()
        super().resizeEvent(event)

    def closeEvent(self, event):
        if self._close_after_results:
            event.ignore()
            return

        if self._closing:
            # Repeated close requests must not bypass background teardown.
            if self._shutdown_complete:
                event.accept()
            else:
                event.ignore()
            return

        if not self.results_panel.isHidden():
            event.ignore()
            self._close_after_results = True
            self.background.setEnabled(False)
            # Reuse reset's retreat, including an already-running reset.
            # Its completion requests close again after the panel is hidden.
            self._reset_results_session()
            return

        self._closing = True
        self._stop_input_shake()
        self.scratchpad_dialog.close()
        self.scratchpad.clear()
        self.update_checker.cancel_request()
        self._waiting_for_preload = False
        self.background.setEnabled(False)

        self._shutdown_overlay = QFrame(self)
        self._shutdown_overlay.setStyleSheet(
            """
            QFrame {
                background: rgba(0, 0, 0, 110);
            }
            """
        )
        self._shutdown_overlay.setGeometry(self.rect())
        self._shutdown_overlay.show()
        self._shutdown_overlay.raise_()

        self._shutdown_screen = ShutdownScreen()

        window_center = self.frameGeometry().center()

        x = window_center.x() - self._shutdown_screen.width() // 2
        y = window_center.y() - self._shutdown_screen.height() // 2

        self._shutdown_screen.move(x, y)
        self._shutdown_screen.show()
        self._shutdown_screen.raise_()

        if not self._preload_threads and not self._extraction_threads:
            QTimer.singleShot(1200, self._finish_shutdown)
            event.ignore()
            return

        event.ignore()

    def _finish_shutdown(self):
        if self._preload_threads or self._extraction_threads:
            return
        if self._shutdown_screen is not None:
            self._shutdown_screen.close()
            self._shutdown_screen = None

        if self._shutdown_overlay is not None:
            self._shutdown_overlay.deleteLater()
            self._shutdown_overlay = None

        self._shutdown_complete = True
        self.close()

def run():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    configure_application(app)
    window = MainWindow()
    window.show()

    app.exec()
