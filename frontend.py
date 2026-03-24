from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QFont, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QPushButton, QLabel, QComboBox,
    QGridLayout, QMenuBar, QMenu, QStatusBar,
    QHBoxLayout, QVBoxLayout
)

class Ui_interface(object):
    # This function places our defined widgets onto the window that is passed as an input
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500,780)

        #central widget
        self.centralwidget = QWidget(MainWindow)

        #Main Layout
        self.main_layout = QHBoxLayout(self.centralwidget)
        #Left layout
        self.left_layout = QVBoxLayout()
        #right Layout
        self.right_layout = QVBoxLayout()
       
        #Adds left and right layout to the mainlayout
        self.main_layout.addLayout(self.left_layout,3)
        self.main_layout.addLayout(self.right_layout,1)

        #left content


        # IMAGE FRAME
        self.Image_frame = QFrame()
        self.Image_frame.setFrameShape(QFrame.StyledPanel)
        self.Image_frame.setMinimumHeight(500)

        #button row
        self.button_layout = QHBoxLayout()

        # UPLOAD BUTTON
        self.upload_btn = QPushButton("Upload Image")
        self.eyedropper_btn = QPushButton("EyeDropper : On")
        
        self.button_layout.addWidget(self.upload_btn)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.eyedropper_btn)
        

        # Selected color section
        #*Outer Container for the selected color frame
        self.Selected_color_frame_2 = QFrame()
        self.Selected_color_frame_2.setFrameShape(QFrame.StyledPanel)

        self.Selected_color_frame_2_layout = QVBoxLayout(self.Selected_color_frame_2)
        #Properties for selected color text
        self.title = QLabel("Selected Color")
        title_font = QFont()
        title_font.setPointSize(18)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignCenter)
        #Frame responsible for displaying selcted color

        self.Selected_color_frame = QFrame()
        self.Selected_color_frame.setFrameShape(QFrame.StyledPanel)
        self.Selected_color_frame.setFixedSize(120,80)

        self.hex_label = QLabel("HEX")

        self.Selected_color_frame_2_layout.addWidget(self.title)
        self.Selected_color_frame_2_layout.addWidget(self.Selected_color_frame, alignment=Qt.AlignCenter)
        self.Selected_color_frame_2_layout.addWidget(self.hex_label, alignment=Qt.AlignCenter)
        #adding the widgets to the leftside layout
        self.left_layout.addWidget(self.Image_frame, 3)
        self.left_layout.addLayout(self.button_layout, 0)
        self.left_layout.addWidget(self.Selected_color_frame_2)
        

        #Right side content

        # Preset Frame
        self.Preset_frame = QFrame()
        self.Preset_frame.setFrameShape(QFrame.StyledPanel)

        self.Preset_layout = QVBoxLayout(self.Preset_frame)
        self.Preset_frame.setMaximumHeight(50)
        #preset ComboBox
        self.Preset_combobox = QComboBox()
        self.Preset_combobox.setFont(QFont("",14))

        self.Preset_combobox.addItems([
            "Natural", "Warm", "Cool", "Moody",
            "Neon", "Pastel", "Anime Cel"
        ])

        self.Preset_layout.addWidget(self.Preset_combobox)

        # Palette Generation frame
        self.Palette_frame = QFrame()
        self.Palette_frame.setFrameShape(QFrame.StyledPanel)
        # self.Palette_frame.setFixedHeight(600)

        self.Palette_layout = QVBoxLayout(self.Palette_frame)

        self.palette_title = QLabel("Generated Palette")
        self.palette_title.setAlignment(Qt.AlignCenter)
        self.palette_title.setFont(QFont("", 20))

        self.Palette_layout.addWidget(self.palette_title)
        self.Palette_layout.setAlignment(Qt.AlignTop)

        # GRID LAYOUT HOLDER
        self.grid = QGridLayout()
        frame_names = ["Lineart","Accent","Highlight 1","Highlight 2","Shadow 1","Shadow 2"]

        self.palette_boxes = []
        self.palette_labels = []

        self.export_button = QPushButton("Copy Palette")
        self.export_button.setFixedHeight(35)

        self.pop_out_button = QPushButton("Pop Out")
        self.pop_out_button.setFixedHeight(35)

        button_row = QHBoxLayout()
        button_row.addWidget(self.pop_out_button)
        button_row.addStretch()
        button_row.addWidget(self.export_button)
        
        



        #loop responsible for Creating the indivodual frames 
        for i, name in enumerate(frame_names):

            container = QVBoxLayout()
            container.setSpacing(10)
            

            title= QLabel(name)
            title.setAlignment(Qt.AlignCenter)
            font= QFont()
            font.setPointSize(15)
            title.setFont(font)

             # Color box
            box = QFrame()
            box.setFixedSize(130, 80)
            box.setFrameShape(QFrame.StyledPanel)

            # HEX label
            hex_label = QLabel("HEX:")
            hex_label.setAlignment(Qt.AlignCenter)
            hex_label.setFont(font)

            # Add to vertical container
            container.addWidget(title)
            container.addWidget(box)
            container.addWidget(hex_label)

            # Position in grid
            row = i // 2
            col = i % 2

            self.grid.addLayout(container, row, col)

            # Store references (VERY IMPORTANT)
            self.palette_boxes.append(box)
            self.palette_labels.append(hex_label)
            #applies spacing for each frame
            self.grid.setHorizontalSpacing(150)
            self.grid.setVerticalSpacing(50)
            

        # self.Palette_layout = QVBoxLayout(self.Palette_frame)
        self.Palette_layout.addLayout(self.grid)
        self.Palette_layout.addLayout(button_row)
        self.Palette_layout.addStretch()

       # ADD elements to the right side

        self.right_layout.addWidget(self.Preset_frame,0)
        self.right_layout.addWidget(self.Palette_frame,1)
        
        
        # self.PopOutButton = QPushButton(self.centralwidget)
        
        

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
        self.action_toggle_theme = QAction("Toggle Light/Dark Mode", MainWindow)
        self.actionPlaceholder_4 = QAction("Placeholder 2", MainWindow)

        self.menufile.addAction(self.actionPlaceholder_1)
        self.menufile.addAction(self.actionPlaceholder_2)
        self.menuSettings.addAction(self.action_toggle_theme)
        self.menuSettings.addAction(self.actionPlaceholder_4)

        self.menubar.addMenu(self.menuPalettePal)
        self.menubar.addMenu(self.menufile)
        self.menubar.addMenu(self.menuSettings)
        self.menubar.addMenu(self.menuWeekly_Challenges)

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)