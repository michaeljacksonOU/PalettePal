import sys
import colour
from colour.models import sRGB_to_XYZ, XYZ_to_Oklab

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QMessageBox, QWidget
from PySide6.QtGui import QPixmap, QImage, QPainter, QCursor
from PySide6.QtCore import Qt, QPoint, QPointF
from PIL import Image, ImageDraw, ImageFont

from frontend import Ui_interface


class ZoomableImageLabel(QWidget):
    #Widget resonsible that displays an image with zoom and pan support
    ZOOM_STEP = 1.15 #Zoom increment percentage 
    ZOOM_MIN  = 0.05
    ZOOM_MAX  = 20.0 #max zoom level

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image       = None #holds the loaded QImage 
        self._zoom       = 1.0 # current zoom level
        self._fit_zoom   = 1.0  # Stores default zoom level to restrict zoom out
        self._offset     = QPointF(0, 0) #the top-level corner position of the image inside the widget 
        self._drag_start = None # stores mouse position when a pan begins 
        self._drag_orig  = None #stores the image offset when a drag begins
        self.setMouseTracking(True)

    def set_image(self, path):
        self.image = QImage(path)

        # Limit resolution (Paul task #2)
        max_w, max_h = 1920, 1080
        if self.image.width() > max_w or self.image.height() > max_h:
            self.image = self.image.scaled(
                max_w, max_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

        self._fit_to_window()
        self.update()

    def _fit_to_window(self):
        if not self.image:
            return
        iw, ih = self.image.width(), self.image.height()
        ww, wh = self.width() or 1, self.height() or 1
        self._zoom = min(ww / iw, wh / ih)
        self._fit_zoom = self._zoom  # Save the default zoom level to use as zoom out limit
        self._center_image()

    def _center_image(self):
        if not self.image:
            return
        iw = self.image.width() * self._zoom
        ih = self.image.height() * self._zoom
        self._offset = QPointF(
            (self.width()  - iw) / 2,
            (self.height() - ih) / 2,
        )

    def resizeEvent(self, event):
        self._fit_to_window()
        super().resizeEvent(event)
    #Draws the image at the current zoom level and offset position 

    def paintEvent(self, event):
        if not self.image:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.translate(self._offset)
        painter.scale(self._zoom, self._zoom)
        painter.drawImage(0, 0, self.image)

    def wheelEvent(self, event):
        if not self.image:
            return

        # Zoom centred on the cursor position
        cursor_pos = QPointF(event.position())
        delta = event.angleDelta().y()
        factor = self.ZOOM_STEP if delta > 0 else 1.0 / self.ZOOM_STEP

        # Use _fit_zoom as minimum so user can't zoom out past the default view
        new_zoom = max(self._fit_zoom, min(self.ZOOM_MAX, self._zoom * factor))
        real_factor = new_zoom / self._zoom

        # Keep the point under the cursor fixed
        self._offset = cursor_pos - real_factor * (cursor_pos - self._offset)
        self._zoom   = new_zoom
        self.update()

    def mousePressEvent(self, event):  # Mouse press event to handle storing color values and color conversion
        if not self.image:
            return

        # Right-click = reset zoom
        if event.button() == Qt.RightButton:
            self._fit_to_window()
            self.update()
            return

        # Eyedropper takes priority over panning
        if self.window().eyedropper_enabled:
            self._pick_color(event.position())
            return

        # Left-drag = pan
        if event.button() == Qt.LeftButton:
            self._drag_start = event.position()
            self._drag_orig  = QPointF(self._offset)
            self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            self._offset = self._drag_orig + delta
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self._drag_orig  = None
            self.setCursor(QCursor(Qt.ArrowCursor))

    def _pick_color(self, widget_pos):
        # Convert widget coords → image pixel coords accounting for zoom and pan
        image_x = int((widget_pos.x() - self._offset.x()) / self._zoom)
        image_y = int((widget_pos.y() - self._offset.y()) / self._zoom)

        # Bounds check
        if not (0 <= image_x < self.image.width() and
                0 <= image_y < self.image.height()):
            return

        color = self.image.pixelColor(image_x, image_y)

        r = color.red()   # Gathers RGB values to make up a color
        g = color.green()
        b = color.blue()

        # Normalize to 0–1
        srgb = [r/255, g/255, b/255]

        # HEX value
        hex_value = color.name().upper()

        # Convert sRGB → XYZ → Oklab
        xyz   = sRGB_to_XYZ(srgb)
        oklab = XYZ_to_Oklab(xyz)
        L, a, b_val = oklab

        print("HEX:", hex_value)   # Prints Hex Color
        print("RGB:", r, g, b)     # Prints RGB values
        print("OKLAB:", L, a, b_val)  # Prints OKLAB converted values

        # Save in parent window
        win = self.window()
        win.selected_hex   = hex_value
        win.selected_rgb   = (r, g, b)
        win.selected_oklab = (L, a, b_val)
        win.update_selected_color_display()
        win.update_palette_from_selected_color()

    


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
        self.dark_mode = True

        # Create zoomable image label inside the frame
        self.image_label = ZoomableImageLabel(self.ui.Image_frame)

        # Put the image label inside the frame layout
        layout = QVBoxLayout(self.ui.Image_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)

        # Connect upload button
        self.ui.upload_btn.clicked.connect(self.open_file_dialog)
        self.ui.copy_button.clicked.connect(self.copy_palette_colors)
        self.ui.Preset_combobox.currentIndexChanged.connect(self.update_palette_from_selected_color)
        self.ui.eyedropper_btn.clicked.connect(self.toggle_eyedropper)
        self.ui.action_toggle_theme.triggered.connect(self.toggle_theme)
        self.ui.export_button.clicked.connect(lambda: self.export_palette(self.generated_palette))

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
    
    def export_palette(self, colors, filename="palette.png"):
        """
        colors: list of HEX strings (e.g. ["#FF5733", "#33FF57", "#3357FF"])
        """
        
        block_width = 200
        block_height = 200

        width = block_width * len(colors)
        height = block_height

        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        for i, color in enumerate(colors):
            x0 = i * block_width
            x1 = x0 + block_width

            draw.rectangle([x0, 0, x1, block_height], fill=color)

            # Optional: add HEX label
            draw.text((x0 + 20, block_height - 30), color, fill="white")

        image.save(filename)
        return filename

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