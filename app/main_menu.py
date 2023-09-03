from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from . import *

class MainMenu(QWidget):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.stacked_layout = self.window.stacked_layout

        self.init_ui()

    @pyqtSlot()
    def selected(self):
        self.window.setWindowTitle('OBLC Data Entry | Main Menu')
        self.window.setStyleSheet(self.read_css('main_menu.css'))
        self.window.setFixedSize(400, 200)

    def init_ui(self):
        layout = QVBoxLayout()

        use_button = QPushButton('Use')
        oblc_settings_button = QPushButton('OBLC Settings')
        facebook_settings_button = QPushButton('Facebook Settings')
        other_settings_button = QPushButton('Other Settings')

        use_button.setObjectName('useButton')
        oblc_settings_button.setObjectName('oblcSettingsButton')
        facebook_settings_button.setObjectName('facebookSettingsButton')
        other_settings_button.setObjectName('otherSettingsButton')

        use_button.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(1))
        oblc_settings_button.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(2))
        facebook_settings_button.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(3))
        other_settings_button.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(4))

        layout.addWidget(use_button)
        layout.addWidget(oblc_settings_button)
        layout.addWidget(facebook_settings_button)
        layout.addWidget(other_settings_button)

        self.setLayout(layout)

    def read_css(self, css_filename):
        with open(os.path.join(css_dir, css_filename), 'r') as f:
            return f.read()