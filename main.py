import sys
import logging
import colour
from colour.models import sRGB_to_XYZ, XYZ_to_Oklab

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout,
    QMessageBox, QWidget, QGridLayout, QFrame, QScrollArea
)
from PySide6.QtGui import QImage, QPainter, QCursor, QFont,QIcon
from PySide6.QtCore import Qt, QPointF
from PIL import Image, ImageDraw

from frontend import Ui_interface
from logger_config import setup_logger
from init_db import initialize_database
from db_operations import (
    create_project_session,
    save_palette_result,
    link_palette_to_preset
)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )


class ZoomableImageLabel(QWidget):
    ZOOM_STEP = 1.15
    ZOOM_MIN = 0.05
    ZOOM_MAX = 20.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self._zoom = 1.0
        self._fit_zoom = 1.0
        self._offset = QPointF(0, 0)
        self._drag_start = None
        self._drag_orig = None
        self.setMouseTracking(True)

    def set_image(self, path):
        try:
            self.image = QImage(path)

            if self.image.isNull():
                raise ValueError("The selected file could not be loaded as an image.")

            max_w, max_h = 1920, 1080
            if self.image.width() > max_w or self.image.height() > max_h:
                self.image = self.image.scaled(
                    max_w,
                    max_h,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

            self._fit_to_window()
            self.update()

        except Exception:
            logging.exception("Error in set_image")
            raise

    def _fit_to_window(self):
        if not self.image:
            return
        iw, ih = self.image.width(), self.image.height()
        ww, wh = self.width() or 1, self.height() or 1
        self._zoom = min(ww / iw, wh / ih)
        self._fit_zoom = self._zoom
        self._center_image()

    def _center_image(self):
        if not self.image:
            return
        iw = self.image.width() * self._zoom
        ih = self.image.height() * self._zoom
        self._offset = QPointF(
            (self.width() - iw) / 2,
            (self.height() - ih) / 2,
        )

    def resizeEvent(self, event):
        self._fit_to_window()
        super().resizeEvent(event)

    def paintEvent(self, event):
        if not self.image:
            return
        # Creates the painter to repaint the image based on changed made
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        # shifts the entire canvas so the image can be dragged around
        painter.translate(self._offset)
        # scales the image around the origin (0,0) of the translated canvas
        painter.scale(self._zoom, self._zoom)
        # Draw the image at (0,0); translate+scale above position and size it correctly
        painter.drawImage(0, 0, self.image)

    def wheelEvent(self, event):
        if not self.image:
            return

        cursor_pos = QPointF(event.position())
        # Captures wheel up or wheel down
        delta = event.angleDelta().y()
        # if wheel up - zoom in, else - zoom out
        factor = self.ZOOM_STEP if delta > 0 else 1.0 / self.ZOOM_STEP

        new_zoom = max(self._fit_zoom, min(self.ZOOM_MAX, self._zoom * factor))
        real_factor = new_zoom / self._zoom

        self._offset = cursor_pos - real_factor * (cursor_pos - self._offset)
        self._zoom = new_zoom
        self.update()

    def mousePressEvent(self, event):
        if not self.image:
            return
        #Right click will reset the image 
        if event.button() == Qt.RightButton:
            self._fit_to_window()
            self.update()
            return

        if self.window().eyedropper_enabled:
            try:
                self._pick_color(event.position())
            except Exception as e:
                logging.exception("Error while picking color")
                QMessageBox.critical(
                    self.window(),
                    "Color Selection Error",
                    f"An error occurred while selecting a color:\n{e}"
                )
            return

        if event.button() == Qt.LeftButton:
            self._drag_start = event.position()
            self._drag_orig = QPointF(self._offset)
            self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            self._offset = self._drag_orig + delta
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self._drag_orig = None
            self.setCursor(QCursor(Qt.ArrowCursor))

    def _pick_color(self, widget_pos):
        image_x = int((widget_pos.x() - self._offset.x()) / self._zoom)
        image_y = int((widget_pos.y() - self._offset.y()) / self._zoom)

        if not (0 <= image_x < self.image.width() and 0 <= image_y < self.image.height()):
            return

        color = self.image.pixelColor(image_x, image_y)

        r = color.red()
        g = color.green()
        b = color.blue()

        srgb = [r / 255, g / 255, b / 255]
        hex_value = color.name().upper()

        xyz = sRGB_to_XYZ(srgb)
        oklab = XYZ_to_Oklab(xyz)
        L, a, b_val = oklab

        win = self.window()
        win.selected_hex = hex_value
        win.selected_rgb = (r, g, b)
        win.selected_oklab = (L, a, b_val)
        win.update_selected_color_display()
        win.update_palette_from_selected_color()


class PalettePopout(QWidget):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.setWindowTitle("Palette")
        self.setWindowIcon(QIcon("palettepal.ico"))
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(350, 400)

        self.layout = QVBoxLayout(self)
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)

        self.boxes = []
        self.labels = []

        names = ["Lineart", "Accent", "Highlight 1", "Highlight 2", "Shadow 1", "Shadow 2"]

        for i, name in enumerate(names):
            v = QVBoxLayout()

            label = QLabel(name)
            label.setAlignment(Qt.AlignCenter)

            box = QFrame()
            box.setFixedSize(120, 70)
            box.setFrameShape(QFrame.Box)

            hex_label = QLabel("HEX")
            hex_label.setAlignment(Qt.AlignCenter)

            v.addWidget(label)
            v.addWidget(box, alignment=Qt.AlignCenter)
            v.addWidget(hex_label)

            self.grid.addLayout(v, i // 2, i % 2)

            self.boxes.append(box)
            self.labels.append(hex_label)

        self.apply_theme(dark_mode)

    def apply_theme(self, dark_mode):
        if dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: white;
                }
                QLabel {
                    color: white;
                    border: none;
                }
                QFrame {
                    background-color: #353535;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f5f5f5;
                    color: black;
                }
                QLabel {
                    color: black;
                    border: none;
                }
                QFrame {
                    background-color: white;
                    border: none;
                }
            """)

    def update_palette(self, colors):
        for i, c in enumerate(colors):
            if i < len(self.boxes):
                self.boxes[i].setStyleSheet(f"background-color: {c}; border: 1px solid black;")
                self.labels[i].setText(c)

class FAQWindow(QMainWindow):
    """
    A simple window that displays FAQ information about the application.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FAQ")
        self.setWindowIcon(QIcon("palettepal.ico"))
        self.setFixedSize(600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Frequently Asked Questions")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18))

        scroll= QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content= QWidget()
        content_layout = QVBoxLayout(content)

        description = QLabel(
    "Q: How do I upload an image?\n"
    "A: You can go to File > Upload Image or click the Upload Image button\n"
    "near the bottom left corner of the image preview window.\n\n"
    
    "Q: How do I pick colors from my selected image?\n"
    "A: Toggle the eyedropper on/off by clicking the Eyedropper button near\n"
    "the bottom right corner of the image preview window. When the Eyedropper\n"
    "is toggled off, you may drag your selected image around.\n\n"
    
    "Q: Help! My selected image is no longer in-frame of the image preview window!\n"
    "A: Hover your cursor over the image preview window and right-click.\n"
    "Your selected image should snap back to the center of the frame.\n\n"
    
    "Q: How do I zoom in on my selected image?\n"
    "A: Hover your cursor over the image preview window and use the\n"
    "mouse scroll wheel to zoom in/out.\n\n"
    
    "Q: How do I select a palette preset?\n"
    "A: Select a preset from the drop-down menu in the upper right of the window.\n\n"
    
    "Q: What can I use my generated palette(s) for?\n"
    "A: Anything! You can pop out the palette to appear always-on-top of other\n"
    "windows for ease of reference, export the palette as a PNG to reference/\n"
    "colorpick from in your drawing/editing software, or just copy the HEX codes.\n\n"
    
    "Q: Who is PalettePal's target audience?\n"
    "A: PalettePal was designed primarily for beginner/intermediate digital artists\n"
    "to assist them with picking harmonious rendering colors. But its use extends\n"
    "to graphic designers, 3D modelers, UI/web developers, brands, and more!\n\n"
    
    "Q: How does PalettePal work?\n"
    "A: Magic!"
        )
        description.setAlignment(Qt.AlignLeft)
        description.setWordWrap(True)
        description.setFont(QFont("Segoe UI", 10))

        content_layout.addWidget(description)
        scroll.setWidget(content)

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(scroll)
        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

          
        self.setWindowIcon(QIcon("palettepal.ico"))
        self.ui = Ui_interface()
        self.ui.setupUi(self)
        self.popout = None
        self.faq_window = None
        self.ui.pop_out_button.clicked.connect(self.toggle_popout)

        self.selected_hex = None
        self.selected_rgb = None
        self.selected_oklab = None
        self.generated_palette = []
        self.eyedropper_enabled = True
        self.dark_mode = True

        self.current_image_path = None
        self.current_session_id = None

        self.image_label = ZoomableImageLabel(self.ui.Image_frame)

        layout = QVBoxLayout(self.ui.Image_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)

        self.ui.upload_btn.clicked.connect(self.open_file_dialog)
        self.ui.copy_button.clicked.connect(self.copy_palette_colors)
        self.ui.Preset_combobox.currentIndexChanged.connect(self.update_palette_from_selected_color)
        self.ui.eyedropper_btn.clicked.connect(self.toggle_eyedropper)
        self.ui.action_toggle_theme.triggered.connect(self.toggle_theme)
        self.ui.export_button.clicked.connect(lambda: self.export_palette(self.generated_palette))
        self.ui.action_export_palette.triggered.connect(lambda: self.export_palette(self.generated_palette))
        self.ui.upload_image.triggered.connect(self.open_file_dialog)
        self.ui.faq.triggered.connect(self.open_faq_window)


        self.apply_theme()

    def toggle_popout(self):
        if self.popout is None:
            self.popout = PalettePopout(self.dark_mode)
            if self.generated_palette:
                self.popout.update_palette(self.generated_palette)
            self.popout.show()
        else:
            if self.popout.isVisible():
                self.popout.hide()
            else:
                self.popout.apply_theme(self.dark_mode)
                if self.generated_palette:
                    self.popout.update_palette(self.generated_palette)
                self.popout.show()
                self.popout.raise_()
                self.popout.activateWindow()

    def open_file_dialog(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Image",
                "",
                "Images (*.png *.jpg *.jpeg)"
            )

            if not file_path:
                return

            self.current_image_path = file_path
            self.image_label.set_image(file_path)

            preset_name = self.ui.Preset_combobox.currentText()
            self.current_session_id = create_project_session(file_path, preset_name)

            self.statusBar().showMessage(
                f"Image loaded. Session {self.current_session_id} created.",
                5000
            )

        except Exception as e:
            logging.exception("Error while uploading image")
            QMessageBox.critical(
                self,
                "Upload Error",
                f"An error occurred while loading the image:\n{e}"
            )

    def export_palette(self, colors, filename="palette.png"):
        try:
            if not colors:
                QMessageBox.information(self, "No Palette", "Generate a palette first.")
                return

            if not self.current_session_id:
                QMessageBox.information(self, "No Session", "Upload an image first.")
                return

            if not self.selected_hex:
                QMessageBox.information(self, "No Color Selected", "Select a color from the image first.")
                return

            labels = ["Lineart", "Accent", "Highlight 1", "Highlight 2", "Shadow 1", "Shadow 2"]

            block_width = 200
            block_height = 230

            width = block_width * len(colors)
            height = block_height

            image = Image.new("RGB", (width, height), "#3c3c3c")
            draw = ImageDraw.Draw(image)

            for i, color in enumerate(colors):
                x0 = i * block_width
                x1 = x0 + block_width

                label = labels[i] if i < len(labels) else f"Color {i+1}"
                draw.text((x0 + 10, 10), label, fill="white")
                draw.rectangle([x0 + 10, 40, x1 - 10, 180], fill=color)
                draw.text((x0 + 10, 190), f"HEX: {color}", fill="white")

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Palette Image",
                filename,
                "Images (*.png)"
            )

            if not file_path:
                return

            image.save(file_path)

            preset_name = self.ui.Preset_combobox.currentText()

            result_id = save_palette_result(
                session_id=self.current_session_id,
                base_color_hex=self.selected_hex,
                preset_environment=preset_name,
                preset_style="Current UI Palette",
                lineart_hex=colors[0],
                accent_hex=colors[1],
                highlight1_hex=colors[2],
                highlight2_hex=colors[3],
                shadow1_hex=colors[4],
                shadow2_hex=colors[5]
            )

            link_palette_to_preset(result_id, preset_name)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Palette exported and saved to database.\n\n"
                f"PNG: {file_path}\n"
                f"Database Result ID: {result_id}"
            )

        except Exception as e:
            logging.exception("Error while exporting palette")
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export:\n{e}"
            )

    def open_faq_window(self):
        """Opens the FAQ window, or brings it to focus if already open."""
        if self.faq_window is None or not self.faq_window.isVisible():
            self.faq_window = FAQWindow() 
        self.faq_window = FAQWindow()
        self.faq_window.show()
        self.faq_window.raise_()
        self.faq_window.activateWindow()

    def toggle_eyedropper(self):
        self.eyedropper_enabled = not self.eyedropper_enabled

        if self.eyedropper_enabled:
            self.ui.eyedropper_btn.setText("EyeDropper : On")
            self.ui.eyedropper_btn.setToolTip("Use your cursor to select a color inside of an uploaded image")
        else:
            self.ui.eyedropper_btn.setText("EyeDropper : Off")
            self.ui.eyedropper_btn.setToolTip("Use your cursor to drag the image around")

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
                    border: none;
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
                    border: none;
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
                    border: none;
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
                    border: none;
                }
            """)
        if self.popout:
            self.popout.apply_theme(self.dark_mode)

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
            "Pastel":    [(-40, -40, -40), (25, 20, 20), (55, 50, 50), (80, 75, 75), (-20, -20, -20), (-55, -55, -55)],
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
        try:
            if not self.selected_rgb:
                return

            preset_name = self.ui.Preset_combobox.currentText()
            self.generated_palette = self.generate_palette(self.selected_rgb, preset_name)

            for i, hex_color in enumerate(self.generated_palette):
                self.ui.palette_boxes[i].setStyleSheet(
                    f"background-color: {hex_color}; border: 1px solid black;"
                )
                self.ui.palette_labels[i].setText(f"HEX: {hex_color}")

            if self.popout:
                self.popout.update_palette(self.generated_palette)

        except Exception as e:
            logging.exception("Error while updating palette")
            QMessageBox.critical(
                self,
                "Palette Error",
                f"An error occurred while generating the palette:\n{e}"
            )

    def copy_palette_colors(self):
        try:
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

        except Exception as e:
            logging.exception("Error while copying palette colors")
            QMessageBox.critical(
                self,
                "Copy Error",
                f"An error occurred while copying palette colors:\n{e}"
            )


if __name__ == "__main__":
    setup_logger()
    sys.excepthook = handle_exception
    initialize_database()

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()

    app.exec()
