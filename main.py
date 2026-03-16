import sys
import colour
from colour.models import sRGB_to_XYZ, XYZ_to_Oklab

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel
from PySide6.QtGui import QPixmap, QImage

from frontend import Ui_interface

class ImageLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None

    def set_image(self, path):
        self.image = QImage(path)
        self.setPixmap(QPixmap(path))

    def mousePressEvent(self, event): #Mouse press event to handle storing color values and Color conversion 

        if self.image: #checks if the mouse click is inside the selected image 

            x = int(event.position().x()) #finds the X and Y coordinate of the image 
            y = int(event.position().y())

            color = self.image.pixelColor(x, y) #uses the coordinates to find the color 

            r = color.red() #Gathers RBG values to make up a color
            g = color.green()
            b = color.blue()

            # Normalize to 0–1
            srgb = [r/255, g/255, b/255]

            # HEX value
            hex_value = color.name()

            #  Convert sRGB → XYZ → Oklab
            xyz = sRGB_to_XYZ(srgb)
            oklab = XYZ_to_Oklab(xyz)

            L, a, b_val = oklab

            print("HEX:", hex_value) #prints Hex Color
            print("RGB:", r, g, b) #Prints RBG values
            print("OKLAB:", L, a, b_val) #prints OKLAB converted values 

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

        # Make the image fill the frame
        self.image_label.setGeometry(self.ui.Image_frame.rect())

        # Connect upload button
        self.ui.pushButton_2.clicked.connect(self.open_file_dialog)

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