# widgets.py
from PySide6.QtWidgets import QLabel, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor

class ClickableLabel(QLabel):
    """
    A QLabel that copies its text to the clipboard when clicked.
    Shows a pointer cursor on hover to indicate it's clickable.
    """
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip("Click to copy HEX value")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            text = self.text()
            if ":" in text:
                hex_value = text.split(":")[1].strip()
            else:
                hex_value = text

            QApplication.clipboard().setText(hex_value)

            original_text = self.text()
            self.setText("Copied!")
            QTimer.singleShot(1000, lambda: self.setText(original_text))