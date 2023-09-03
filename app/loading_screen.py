from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from . import *

class LoadingScreen(QWidget):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.stacked_layout = self.window.stacked_layout

        self.init_ui()

    @pyqtSlot()
    def selected(self):
        self.window.setWindowTitle('OBLC Data Entry | Loading')
        self.window.setStyleSheet(self.read_css('loading_screen.css'))
        self.window.setFixedSize(350, 200)

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.loading_label = QLabel("Loading")
        self.loading_label.setObjectName("loadingLabel")

        self.layout.addWidget(self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)

    def read_css(self, css_filename):
        with open(os.path.join(css_dir, css_filename), 'r') as f:
            return f.read()
