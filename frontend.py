from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QFont, QAction,QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QPushButton, QLabel, QComboBox,
    QGridLayout, QMenuBar, QMenu, QStatusBar,
    QHBoxLayout, QVBoxLayout
)
from widgets import ClickableLabel

class Ui_interface(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 780)
        MainWindow.setWindowTitle("PalettePal")

        self.centralwidget = QWidget(MainWindow)

        self.main_layout = QHBoxLayout(self.centralwidget)
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        self.main_layout.addLayout(self.left_layout, 3)
        self.main_layout.addLayout(self.right_layout, 1)

        self.Image_frame = QFrame()
        self.Image_frame.setFrameShape(QFrame.NoFrame)
        self.Image_frame.setMinimumHeight(500)

        self.button_layout = QHBoxLayout()

        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.setToolTip("Upload an image to interact with.")

        self.clear_btn = QPushButton("Reset Board")
        self.clear_btn.setToolTip("CLick this button to reset the board back to default")

        self.eyedropper_btn = QPushButton("EyeDropper : On")
        self.eyedropper_btn.setToolTip("Use your cursor to select a color inside of an uploaded image")

        self.button_layout.addWidget(self.upload_btn)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.eyedropper_btn)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.clear_btn)

        self.Selected_color_frame_2 = QFrame()
        self.Selected_color_frame_2.setFrameShape(QFrame.NoFrame)

        self.Selected_color_frame_2_layout = QVBoxLayout(self.Selected_color_frame_2)

        self.title = QLabel("Selected Color")
        title_font = QFont()
        title_font.setPointSize(18)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignCenter)

        self.Selected_color_frame = QFrame()
        self.Selected_color_frame.setFrameShape(QFrame.Box)
        self.Selected_color_frame.setFixedSize(120, 80)

        self.hex_label = ClickableLabel("HEX: None")
        self.hex_label.setAlignment(Qt.AlignCenter)

        self.Selected_color_frame_2_layout.addWidget(self.title)
        self.Selected_color_frame_2_layout.addWidget(self.Selected_color_frame, alignment=Qt.AlignCenter)
        self.Selected_color_frame_2_layout.addWidget(self.hex_label, alignment=Qt.AlignCenter)

        self.left_layout.addWidget(self.Image_frame, 3)
        self.left_layout.addLayout(self.button_layout, 0)
        self.left_layout.addWidget(self.Selected_color_frame_2)

        self.Preset_frame = QFrame()
        self.Preset_frame.setFrameShape(QFrame.NoFrame)

        self.Preset_layout = QVBoxLayout(self.Preset_frame)
        self.Preset_frame.setMaximumHeight(50)

        self.Preset_combobox = QComboBox()
        self.Preset_combobox.setFont(QFont("Segoe UI", 14))
        self.Preset_combobox.addItems([
            "Natural", "Warm", "Cool", "Moody",
            "Neon", "Pastel", "Anime Cel"
        ])

        self.Preset_layout.addWidget(self.Preset_combobox)

        self.Palette_frame = QFrame()
        self.Palette_frame.setFrameShape(QFrame.NoFrame)

        self.Palette_layout = QVBoxLayout(self.Palette_frame)

        self.palette_title = QLabel("Generated Palette")
        self.palette_title.setAlignment(Qt.AlignCenter)
        self.palette_title.setFont(QFont("Segoe UI", 20))
        self.palette_title.setStyleSheet("border: none;")

        self.Palette_layout.addWidget(self.palette_title)
        self.Palette_layout.setAlignment(Qt.AlignTop)

        self.grid = QGridLayout()
        frame_names = ["Lineart", "Accent", "Highlight 1", "Highlight 2", "Shadow 1", "Shadow 2"]

        self.palette_boxes = []
        self.palette_labels = []

        self.copy_button = QPushButton("Copy Palette")
        self.copy_button.setToolTip("Copy the HEX values of generated palette")
        self.copy_button.setFixedHeight(35)

        self.pop_out_button = QPushButton("Pop Out")
        self.pop_out_button.setToolTip("Pop Palette out to use in another application")
        self.pop_out_button.setFixedHeight(35)

        self.export_button = QPushButton("Export Palette")
        self.export_button.setToolTip("Export palette as a PNG")
        self.export_button.setFixedHeight(35)

        self.save_button = QPushButton("Save Palette")
        self.save_button.setToolTip("Save the current palette to the database")
        self.save_button.setFixedHeight(35)

        button_row = QHBoxLayout()
        button_row.addWidget(self.pop_out_button)
        button_row.addStretch()
        button_row.addWidget(self.export_button)
        button_row.addStretch()
        button_row.addWidget(self.copy_button)
        button_row.addWidget(self.save_button)

        for i, name in enumerate(frame_names):
            container = QVBoxLayout()
            container.setSpacing(10)

            title = QLabel(name)
            title.setAlignment(Qt.AlignCenter)
            font = QFont()
            font.setPointSize(15)
            title.setFont(font)
            title.setStyleSheet("border: none;")

            box = QFrame()
            box.setFixedSize(130, 80)
            box.setFrameShape(QFrame.NoFrame)

            hex_label = ClickableLabel("HEX:")
            hex_label.setAlignment(Qt.AlignCenter)
            hex_label.setFont(font)
            hex_label.setStyleSheet("border: none;")

            container.addWidget(title)
            container.addWidget(box)
            container.addWidget(hex_label)

            row = i // 2
            col = i % 2

            self.grid.addLayout(container, row, col)

            self.palette_boxes.append(box)
            self.palette_labels.append(hex_label)

            self.grid.setHorizontalSpacing(150)
            self.grid.setVerticalSpacing(50)

        self.Palette_layout.addLayout(self.grid)
        self.Palette_layout.addLayout(button_row)
        self.Palette_layout.addStretch()

        self.right_layout.addWidget(self.Preset_frame, 0)
        self.right_layout.addWidget(self.Palette_frame, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 1114, 26))
        self.menubar.setStyleSheet("QMenuBar { min-height: 40px; }")

        # Logo label instead of QAction
        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("background-color: transparent;")
        logo_pixmap = QPixmap("palettepal.ico").scaled(
            55, 55,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setContentsMargins(5, 2, 5, 0)
        self.menubar.setCornerWidget(self.logo_label, Qt.TopLeftCorner)

        self.menufile = QMenu("File", self.menubar)
        self.menuSettings = QMenu("Tools", self.menubar)

        self.upload_image = QAction("Upload Image", MainWindow)
        self.action_export_palette = QAction("Export Palette", MainWindow)
        self.action_toggle_theme = QAction("Toggle Light/Dark Mode", MainWindow)
        self.faq = QAction("FAQ", MainWindow)
        

        self.menufile.addAction(self.upload_image)
        self.menufile.addAction(self.action_export_palette)
        self.menuSettings.addAction(self.action_toggle_theme)
        self.menuSettings.addAction(self.faq)

        self.menubar.addMenu(self.menufile)
        self.menubar.addMenu(self.menuSettings)

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
