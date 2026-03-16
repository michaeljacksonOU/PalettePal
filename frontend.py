from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QFont, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QPushButton, QLabel, QComboBox,
    QGridLayout, QMenuBar, QMenu, QStatusBar
)

class Ui_interface(object):
    # This function places our defined widgets onto the window that is passed as an input
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500,780)




        self.centralwidget = QWidget(MainWindow)

        # IMAGE FRAME
        self.Image_frame = QFrame(self.centralwidget)
        self.Image_frame.setGeometry(QRect(10, 10, 751, 441))
        self.Image_frame.setFrameShape(QFrame.StyledPanel)

        # UPLOAD BUTTON
        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QRect(10, 470, 121, 28))
        self.pushButton_2.setText("Upload Image")

        # EYEDROPPER Button
        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QRect(600, 470, 131, 28))
        self.pushButton_3.setText("EyeDropper : Off")

        # Selected color section
        self.Selected_color_frame_2 = QFrame(self.centralwidget)
        self.Selected_color_frame_2.setGeometry(QRect(10, 550, 751, 211))
        self.Selected_color_frame_2.setFrameShape(QFrame.StyledPanel)

        #Properties for selected color text
        self.label_2 = QLabel(self.Selected_color_frame_2)
        self.label_2.setGeometry(QRect(260, 10, 271, 41))
        font = QFont()
        font.setPointSize(18)
        self.label_2.setFont(font)
        self.label_2.setText("Selected Color")
        self.label_2.setAlignment(Qt.AlignHCenter)
        #Frame responsible for displaying selcted color
        self.Selected_color_frame = QFrame(self.Selected_color_frame_2)
        self.Selected_color_frame.setGeometry(QRect(320, 50, 141, 91))
        self.Selected_color_frame.setFrameShape(QFrame.StyledPanel)
        #text label to display color's HEX value
        self.label_3 = QLabel(self.Selected_color_frame_2)
        self.label_3.setGeometry(QRect(370, 150, 41, 21))
        font = QFont()
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setText("HEX")

        # Preset Frame
        self.Preset_frame = QFrame(self.centralwidget)
        self.Preset_frame.setGeometry(QRect(780, 10, 311, 211))
        self.Preset_frame.setFrameShape(QFrame.StyledPanel)
        #preset ComboBox
        self.Preset_combobox = QComboBox(self.Preset_frame)
        self.Preset_combobox.setGeometry(QRect(0, 0, 311, 31))

        font = QFont()
        font.setPointSize(14)
        self.Preset_combobox.setFont(font)

        self.Preset_combobox.addItems([
            "Natural", "Warm", "Cool", "Moody",
            "Neon", "Patel", "Anime Cel"
        ])

        # Palette Generation frame
        self.Palette_frame = QFrame(self.centralwidget)
        self.Palette_frame.setGeometry(QRect(780, 240, 311, 521))
        self.Palette_frame.setFrameShape(QFrame.StyledPanel)

        self.label_4 = QLabel(self.Palette_frame)
        self.label_4.setGeometry(QRect(10, 10, 311, 31))
        font = QFont()
        font.setPointSize(16)
        font.setUnderline(True)
        self.label_4.setFont(font)
        self.label_4.setText("     Generated Palette     ")

        # GRID LAYOUT HOLDER
        self.gridLayoutWidget = QWidget(self.Palette_frame)
        self.gridLayoutWidget.setGeometry(QRect(19, 50, 271, 441))

        self.gridLayout = QGridLayout(self.gridLayoutWidget)

        # PALETTE INTERNAL FRAME
        self.Palette_frame_2 = QFrame(self.gridLayoutWidget)
        self.Palette_frame_2.setFrameShape(QFrame.StyledPanel)

        self.gridLayout.addWidget(self.Palette_frame_2)

        # COLOR FRAMES
        #lineart frame
        self.Lineart_frame = QFrame(self.Palette_frame_2)
        self.Lineart_frame.setGeometry(QRect(20, 30, 111, 71))
        self.Lineart_frame.setFrameShape(QFrame.StyledPanel)
        #highlight 1 frame
        self.Highlight1_frame = QFrame(self.Palette_frame_2)
        self.Highlight1_frame.setGeometry(QRect(20, 160, 111, 71))
        self.Highlight1_frame.setFrameShape(QFrame.StyledPanel)
        #highlight 2 frame
        self.Shadow1_frame = QFrame(self.Palette_frame_2)
        self.Shadow1_frame.setGeometry(QRect(20, 310, 111, 71))
        self.Shadow1_frame.setFrameShape(QFrame.StyledPanel)
        #Accent frame
        self.Accent_frame = QFrame(self.Palette_frame_2)
        self.Accent_frame.setGeometry(QRect(140, 30, 111, 71))
        self.Accent_frame.setFrameShape(QFrame.StyledPanel)
        #Highlight 2 Frame
        self.Highlight2_frame = QFrame(self.Palette_frame_2)
        self.Highlight2_frame.setGeometry(QRect(140, 160, 111, 71))
        self.Highlight2_frame.setFrameShape(QFrame.StyledPanel)
        #shadow2 Frame
        self.Shadow2_frame = QFrame(self.Palette_frame_2)
        self.Shadow2_frame.setGeometry(QRect(140, 310, 111, 71))
        self.Shadow2_frame.setFrameShape(QFrame.StyledPanel)

        # Palette Buttons
        self.CopyButton = QPushButton(self.centralwidget)
        self.CopyButton.setGeometry(QRect(780, 770, 93, 28))

        self.PopOutButton = QPushButton(self.centralwidget)
        self.PopOutButton.setGeometry(QRect(1010, 770, 93, 28))
        #branding information 
        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QRect(300, 770, 291, 21))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setText("5-Headed Monster 2026")

        MainWindow.setCentralWidget(self.centralwidget)

        # MENU BAR
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 1114, 26))

        self.menuPalettePal = QMenu("PalettePal", self.menubar) #will be updated with our logo for branding once created
        self.menufile = QMenu("file", self.menubar)
        self.menuSettings = QMenu("Settings", self.menubar)
        self.menuWeekly_Challenges = QMenu("Weekly Challenges", self.menubar)
        #menu bar options
        #File button options
        self.actionPlaceholder_1 = QAction("Placeholder 1", MainWindow)
        self.actionPlaceholder_2 = QAction("Placeholder 2", MainWindow)
        #setting button options
        self.actionPlaceholder_3 = QAction("Placeholder 1", MainWindow)
        self.actionPlaceholder_4 = QAction("Placeholder 2", MainWindow)

        self.menufile.addAction(self.actionPlaceholder_1)
        self.menufile.addAction(self.actionPlaceholder_2)
        self.menuSettings.addAction(self.actionPlaceholder_3)
        self.menuSettings.addAction(self.actionPlaceholder_4)

        self.menubar.addMenu(self.menuPalettePal)
        self.menubar.addMenu(self.menufile)
        self.menubar.addMenu(self.menuSettings)
        self.menubar.addMenu(self.menuWeekly_Challenges)

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)