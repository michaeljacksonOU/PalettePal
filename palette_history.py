import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QPushButton,
    QMessageBox, QSizePolicy, QApplication
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, Signal

from db_operations import get_all_project_sessions, get_palette_results_for_session


class PaletteSwatchRow(QFrame):
    """A single row showing one saved palette result with color swatches."""

    def __init__(self, result, dark_mode=False, parent=None):
        super().__init__(parent)
        self.result = result
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(12)

        result_id_label = QLabel(f"Result #{result['result_id']}")
        result_id_label.setFont(QFont("Segoe UI", 9))

        preset_label = QLabel(f"Preset: {result['preset_environment']}")
        preset_label.setFont(QFont("Segoe UI", 9))

        base_label = QLabel(f"Base color: {result['base_color_hex']}")
        base_label.setFont(QFont("Segoe UI", 9))

        time_label = QLabel(result['generated_at'])
        time_label.setFont(QFont("Segoe UI", 9))
        time_label.setAlignment(Qt.AlignRight)

        base_swatch = QFrame()
        base_swatch.setFixedSize(18, 18)
        base_swatch.setStyleSheet(
            f"background-color: {result['base_color_hex']}; border: 1px solid gray; border-radius: 3px;"
        )

        meta_layout.addWidget(result_id_label)
        meta_layout.addWidget(preset_label)
        meta_layout.addWidget(base_swatch)
        meta_layout.addWidget(base_label)
        meta_layout.addStretch()
        meta_layout.addWidget(time_label)

        swatches_layout = QHBoxLayout()
        swatches_layout.setSpacing(8)

        swatch_data = [
            ("Lineart",     result['lineart_hex']),
            ("Accent",      result['accent_hex']),
            ("Highlight 1", result['highlight1_hex']),
            ("Highlight 2", result['highlight2_hex']),
            ("Shadow 1",    result['shadow1_hex']),
            ("Shadow 2",    result['shadow2_hex']),
        ]

        for name, hex_color in swatch_data:
            swatch_container = QVBoxLayout()
            swatch_container.setSpacing(2)
            swatch_container.setAlignment(Qt.AlignCenter)

            swatch = QFrame()
            swatch.setFixedSize(60, 40)
            swatch.setStyleSheet(
                f"background-color: {hex_color}; border: 1px solid gray; border-radius: 4px;"
            )
            swatch.setToolTip(f"Click to copy {hex_color}")
            swatch.setCursor(Qt.PointingHandCursor)
            swatch.mousePressEvent = lambda event, h=hex_color: self._copy_hex(h)

            hex_lbl = QLabel(hex_color)
            hex_lbl.setAlignment(Qt.AlignCenter)
            hex_lbl.setFont(QFont("Segoe UI", 7))
            hex_lbl.setFixedWidth(64)

            name_lbl = QLabel(name)
            name_lbl.setAlignment(Qt.AlignCenter)
            name_lbl.setFont(QFont("Segoe UI", 7))
            name_lbl.setFixedWidth(64)

            swatch_container.addWidget(name_lbl)
            swatch_container.addWidget(swatch, alignment=Qt.AlignCenter)
            swatch_container.addWidget(hex_lbl, alignment=Qt.AlignCenter)

            swatches_layout.addLayout(swatch_container)

        swatches_layout.addStretch()

        layout.addLayout(meta_layout)
        layout.addLayout(swatches_layout)

        self.apply_theme(dark_mode)

    def _copy_hex(self, hex_color):
        QApplication.clipboard().setText(hex_color)

    def apply_theme(self, dark_mode):
        if dark_mode:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2e2e2e;
                    border: 1px solid #444;
                    border-radius: 6px;
                }
                QLabel { color: #cccccc; background: transparent; border: none; }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #fafafa;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                }
                QLabel { color: #333; background: transparent; border: none; }
            """)


class SessionBlock(QFrame):
    """Expandable block showing one session and all its palette results."""

    def __init__(self, session, dark_mode=False, parent=None):
        super().__init__(parent)
        self.session = session
        self.dark_mode = dark_mode
        self.expanded = True

        self.setFrameShape(QFrame.NoFrame)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 8)
        outer.setSpacing(4)

        self.header = QPushButton()
        self.header.setFlat(True)
        self.header.setCursor(Qt.PointingHandCursor)
        self._update_header_text()
        self.header.clicked.connect(self._toggle)
        header_font = QFont("Segoe UI", 10)
        header_font.setBold(True)
        self.header.setFont(header_font)
        self.header.setFixedHeight(32)

        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(12, 0, 0, 0)
        self.results_layout.setSpacing(6)

        results = get_palette_results_for_session(session['session_id'])

        if results:
            for result in results:
                row = PaletteSwatchRow(dict(result), dark_mode=dark_mode)
                self.results_layout.addWidget(row)
        else:
            empty = QLabel("  No saved palettes for this session.")
            empty.setFont(QFont("Segoe UI", 9))
            empty.setStyleSheet("color: gray;")
            self.results_layout.addWidget(empty)

        outer.addWidget(self.header)
        outer.addWidget(self.results_widget)

        self.apply_theme(dark_mode)

    def _update_header_text(self):
        arrow = "v" if self.expanded else ">"
        image = self.session['image_path'] or "Unknown image"
        short_image = image.replace("\\", "/").split("/")[-1]
        preset = self.session['last_used_preset'] or "-"
        created = self.session['created_at'] or ""
        self.header.setText(
            f"{arrow}  Session #{self.session['session_id']}  |  {short_image}  |  Preset: {preset}  |  {created}"
        )

    def _toggle(self):
        self.expanded = not self.expanded
        self.results_widget.setVisible(self.expanded)
        self._update_header_text()

    def apply_theme(self, dark_mode):
        self.dark_mode = dark_mode
        if dark_mode:
            self.header.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 10px;
                }
                QPushButton:hover { background-color: #454545; }
            """)
        else:
            self.header.setStyleSheet("""
                QPushButton {
                    background-color: #e8e8e8;
                    color: #222;
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 10px;
                }
                QPushButton:hover { background-color: #d8d8d8; }
            """)


class PaletteHistoryWindow(QMainWindow):
    """Standalone window that shows all saved palette sessions and results."""

    def __init__(self, dark_mode=False, parent=None):
        super().__init__(parent)
        self.dark_mode = dark_mode

        self.setWindowTitle("Palette History")
        self.setWindowIcon(QIcon("palettepal.ico"))
        self.resize(860, 620)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(10)

        title_row = QHBoxLayout()

        title = QLabel("Palette History")
        title.setFont(QFont("Segoe UI", 18))
        title_row.addWidget(title)
        title_row.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedHeight(30)
        self.refresh_btn.setToolTip("Reload history from the database")
        self.refresh_btn.clicked.connect(self.load_history)

        self.expand_all_btn = QPushButton("Expand all")
        self.expand_all_btn.setFixedHeight(30)
        self.expand_all_btn.clicked.connect(lambda: self._set_all_expanded(True))

        self.collapse_all_btn = QPushButton("Collapse all")
        self.collapse_all_btn.setFixedHeight(30)
        self.collapse_all_btn.clicked.connect(lambda: self._set_all_expanded(False))

        title_row.addWidget(self.expand_all_btn)
        title_row.addWidget(self.collapse_all_btn)
        title_row.addWidget(self.refresh_btn)

        main_layout.addLayout(title_row)

        self.summary_label = QLabel("")
        self.summary_label.setFont(QFont("Segoe UI", 9))
        main_layout.addWidget(self.summary_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)
        self.content_layout.addStretch()

        self.scroll.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll)

        self.session_blocks = []

        self.load_history()
        self.apply_theme(dark_mode)

    def load_history(self):
        for block in self.session_blocks:
            block.setParent(None)
        self.session_blocks.clear()

        item = self.content_layout.takeAt(self.content_layout.count() - 1)
        if item:
            del item

        try:
            sessions = get_all_project_sessions()

            if not sessions:
                empty_label = QLabel("No saved sessions found. Upload an image and save a palette to get started.")
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setFont(QFont("Segoe UI", 11))
                empty_label.setStyleSheet("color: gray; padding: 40px;")
                self.content_layout.addWidget(empty_label)
                self.summary_label.setText("No sessions found.")
            else:
                total_palettes = 0
                for session in sessions:
                    block = SessionBlock(dict(session), dark_mode=self.dark_mode)
                    self.content_layout.addWidget(block)
                    self.session_blocks.append(block)

                    results = get_palette_results_for_session(session['session_id'])
                    total_palettes += len(results)

                self.summary_label.setText(
                    f"{len(sessions)} session(s)  |  {total_palettes} saved palette(s) total  |  "
                    "Click a swatch to copy its HEX value."
                )

        except Exception as e:
            logging.exception("Error loading palette history")
            QMessageBox.critical(self, "Load Error", f"Could not load history:\n{e}")

        self.content_layout.addStretch()

    def _set_all_expanded(self, expanded: bool):
        for block in self.session_blocks:
            if block.expanded != expanded:
                block._toggle()

    def apply_theme(self, dark_mode):
        self.dark_mode = dark_mode
        if dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: white;
                }
                QScrollArea { background-color: #2b2b2b; border: none; }
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: none;
                    padding: 4px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #484848; }
                QLabel { color: white; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: black;
                }
                QScrollArea { background-color: #f5f5f5; border: none; }
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                    padding: 4px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #ebebeb; }
                QLabel { color: black; }
            """)

        for block in self.session_blocks:
            block.apply_theme(dark_mode)
