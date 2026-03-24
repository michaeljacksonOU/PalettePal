import sys
import colour
from colour.models import sRGB_to_XYZ, XYZ_to_Oklab

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QMessageBox
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

from frontend import Ui_interface

class ImageLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None

    def set_image(self, path):
        self.image = QImage(path)

        # Limit resolution (Paul task #2)
        max_width = 1920
        max_height = 1080

        if self.image.width() > max_width or self.image.height() > max_height:
            self.image = self.image.scaled(
                max_width,
                max_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

        pixmap = QPixmap.fromImage(self.image)

        # Scale to fit label while keeping aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)
        self.setAlignment(Qt.AlignCenter)  # Center image (Paul task #1)

    def resizeEvent(self, event):
        if self.image:
            pixmap = QPixmap.fromImage(self.image)
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        super().resizeEvent(event)

    def mousePressEvent(self, event):  # Mouse press event to handle storing color values and Color conversion

        if not self.window().eyedropper_enabled:
            return

        if self.image:
            pixmap = self.pixmap()
            if not pixmap:
                return

            label_width = self.width()
            label_height = self.height()
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()

            x_offset = (label_width - pixmap_width) / 2
            y_offset = (label_height - pixmap_height) / 2

            click_x = event.position().x()
            click_y = event.position().y()

            if (
                click_x < x_offset or click_x > x_offset + pixmap_width or
                click_y < y_offset or click_y > y_offset + pixmap_height
            ):
                return

            image_x = int((click_x - x_offset) * self.image.width() / pixmap_width)
            image_y = int((click_y - y_offset) * self.image.height() / pixmap_height)

            image_x = max(0, min(self.image.width() - 1, image_x))
            image_y = max(0, min(self.image.height() - 1, image_y))

            color = self.image.pixelColor(image_x, image_y)

            r = color.red()  # Gathers RBG values to make up a color
            g = color.green()
            b = color.blue()

            # Normalize to 0–1
            srgb = [r/255, g/255, b/255]

            # HEX value
            hex_value = color.name().upper()

            # Convert sRGB → XYZ → Oklab
            xyz = sRGB_to_XYZ(srgb)
            oklab = XYZ_to_Oklab(xyz)

            L, a, b_val = oklab

            print("HEX:", hex_value)  # prints Hex Color
            print("RGB:", r, g, b)  # Prints RBG values
            print("OKLAB:", L, a, b_val)  # prints OKLAB converted values

            # Save in parent window
            self.window().selected_hex = hex_value
            self.window().selected_rgb = (r, g, b)
            self.window().selected_oklab = (L, a, b_val)

            self.window().update_selected_color_display()
            self.window().update_palette_from_selected_color()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_interface()
        self.ui.setupUi(self)

        # Variables to store selected color
        self.selected_hex = None
        self.selected_rgb = None
        self.selected_oklab = None
        self.generated_palette = []
        self.eyedropper_enabled = True
        self.dark_mode = False

        # Create image label inside the frame
        self.image_label = ImageLabel(self.ui.Image_frame)

        # Put the image label inside the frame layout
        layout = QVBoxLayout(self.ui.Image_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)

        # Connect upload button
        self.ui.upload_btn.clicked.connect(self.open_file_dialog)
        self.ui.export_button.clicked.connect(self.copy_palette_colors)
        self.ui.Preset_combobox.currentIndexChanged.connect(self.update_palette_from_selected_color)
        self.ui.eyedropper_btn.clicked.connect(self.toggle_eyedropper)
        self.ui.action_toggle_theme.triggered.connect(self.toggle_theme)

        self.apply_theme()

    # Function used to open file explorer to upload an image
    def open_file_dialog(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.image_label.set_image(file_path)
    
    def toggle_eyedropper(self):
        self.eyedropper_enabled = not self.eyedropper_enabled

        if self.eyedropper_enabled:
            self.ui.eyedropper_btn.setText("EyeDropper : On")
        else:
            self.ui.eyedropper_btn.setText("EyeDropper : Off")
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: white;
                }
                QPushButton, QComboBox {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555;
                    padding: 4px;
                }
                QLabel {
                    color: white;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: white;
                }
                QMenuBar::item:selected {
                    background-color: #3a3a3a;
                }
                QMenu {
                    background-color: #2b2b2b;
                    color: white;
                }
                QMenu::item:selected {
                    background-color: #3a3a3a;
                }
                QFrame {
                    background-color: #353535;
                    border: 1px solid #555;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: black;
                }
                QPushButton, QComboBox {
                    background-color: white;
                    color: black;
                    border: 1px solid #999;
                    padding: 4px;
                }
                QLabel {
                    color: black;
                }
                QMenuBar {
                    background-color: #e9e9e9;
                    color: black;
                }
                QMenuBar::item:selected {
                    background-color: #d6d6d6;
                }
                QMenu {
                    background-color: white;
                    color: black;
                }
                QMenu::item:selected {
                    background-color: #d6d6d6;
                }
                QFrame {
                    background-color: white;
                    border: 1px solid #999;
                }
            """)

    def update_selected_color_display(self):
        if not self.selected_hex:
            return

        self.ui.hex_label.setText(f"HEX: {self.selected_hex}")
        self.ui.Selected_color_frame.setStyleSheet(
            f"background-color: {self.selected_hex}; border: 1px solid black;"
        )

    def clamp(self, value):
        return max(0, min(255, int(value)))

    def rgb_to_hex(self, rgb):
        r, g, b = rgb
        return "#{:02X}{:02X}{:02X}".format(
            self.clamp(r),
            self.clamp(g),
            self.clamp(b)
        )

    def generate_palette(self, base_rgb, preset_name):
        r, g, b = base_rgb

        preset_offsets = {
            "Natural":   [(-90, -90, -90), (-30, -10, -10), (35, 35, 35), (65, 65, 65), (-55, -55, -55), (-110, -110, -110)],
            "Warm":      [(-80, -60, -40), (20, 0, -10), (45, 20, 0), (70, 35, 10), (-35, -20, -20), (-75, -45, -35)],
            "Cool":      [(-70, -80, -100), (-20, 0, 15), (10, 30, 45), (25, 50, 70), (-35, -40, -20), (-70, -75, -35)],
            "Moody":     [(-110, -110, -110), (-55, -45, -45), (20, 20, 20), (40, 35, 35), (-85, -70, -70), (-135, -120, -120)],
            "Neon":      [(-120, -120, -120), (40, -10, 40), (80, 50, 0), (100, 80, 35), (-40, -20, 10), (-80, -50, 30)],
            "Pastel":     [(-40, -40, -40), (25, 20, 20), (55, 50, 50), (80, 75, 75), (-20, -20, -20), (-55, -55, -55)],
            "Anime Cel": [(-100, -100, -100), (-20, -20, -20), (30, 30, 30), (65, 65, 65), (-55, -55, -55), (-125, -125, -125)],
        }

        offsets = preset_offsets.get(preset_name, preset_offsets["Natural"])
        palette = []

        for dr, dg, db in offsets:
            new_rgb = (
                self.clamp(r + dr),
                self.clamp(g + dg),
                self.clamp(b + db)
            )
            palette.append(self.rgb_to_hex(new_rgb))

        return palette

    def update_palette_from_selected_color(self):
        if not self.selected_rgb:
            return

        preset_name = self.ui.Preset_combobox.currentText()
        self.generated_palette = self.generate_palette(self.selected_rgb, preset_name)

        for i, hex_color in enumerate(self.generated_palette):
            self.ui.palette_boxes[i].setStyleSheet(
                f"background-color: {hex_color}; border: 1px solid black;"
            )
            self.ui.palette_labels[i].setText(f"HEX: {hex_color}")

    def copy_palette_colors(self):
        if not self.generated_palette:
            QMessageBox.information(
                self,
                "No Palette",
                "Generate a palette first by selecting a color from an image."
            )
            return

        palette_string = ", ".join(self.generated_palette)
        QApplication.clipboard().setText(palette_string)

        QMessageBox.information(
            self,
            "Copied",
            f"Copied palette colors:\n{palette_string}"
        )

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()