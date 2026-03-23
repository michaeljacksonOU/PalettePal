import sys
import colour
from colour.models import sRGB_to_XYZ, XYZ_to_Oklab

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout
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

        if self.image:  # checks if the mouse click is inside the selected image

            x = int(event.position().x())  # finds the X and Y coordinate of the image
            y = int(event.position().y())

            color = self.image.pixelColor(x, y)  # uses the coordinates to find the color

            r = color.red()  # Gathers RBG values to make up a color
            g = color.green()
            b = color.blue()

            # Normalize to 0–1
            srgb = [r/255, g/255, b/255]

            # HEX value
            hex_value = color.name()

            # Convert sRGB → XYZ → Oklab
            xyz = sRGB_to_XYZ(srgb)
            oklab = XYZ_to_Oklab(xyz)

            L, a, b_val = oklab

            print("HEX:", hex_value)  # prints Hex Color
            print("RGB:", r, g, b)  # Prints RBG values
            print("OKLAB:", L, a, b_val)  # prints OKLAB converted values

            # Save in parent window
            self.parent().selected_hex = hex_value
            self.parent().selected_rgb = (r, g, b)
            self.parent().selected_oklab = (L, a, b_val)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_interface()
        self.ui.setupUi(self)

        # Variables to store selected color
        self.selected_hex = None
        self.selected_rgb = None
        self.selected_oklab = None

        # Create image label inside the frame
        self.image_label = ImageLabel(self.ui.Image_frame)

        # Put the image label inside the frame layout
        layout = QVBoxLayout(self.ui.Image_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)

        # Connect upload button
        self.ui.upload_btn.clicked.connect(self.open_file_dialog)

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

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()