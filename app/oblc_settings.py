from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
from . import *

class OBLCSettings(QWidget):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.stacked_layout = self.window.stacked_layout

        self.init_ui()

    @pyqtSlot()
    def selected(self):
        self.window.setWindowTitle('OBLC Data Entry | OBLC Settings')
        self.window.setStyleSheet(self.read_css('oblc_settings.css'))
        self.window.setFixedSize(450, 140)

        self.email_edit.setText(self.window.config.get('oblc_email'))
        self.password_edit.setText(self.window.config.get('oblc_password'))

        self.password_edit.setEchoMode(QLineEdit.Password)
        self.show_password_checkbox.setChecked(False)

    def init_ui(self):
        layout = QGridLayout()

        self.email_label = QLabel("Email:")
        self.email_edit = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.show_password_checkbox = QCheckBox()
        self.done_button = QPushButton("Done")

        self.show_password_checkbox.clicked.connect(self.show_password_pressed)
        self.done_button.clicked.connect(self.done_pressed)

        layout.addWidget(self.email_label, 0, 0, Qt.AlignCenter)
        layout.addWidget(self.email_edit, 0, 1)
        layout.addWidget(self.password_label, 1, 0, Qt.AlignCenter)
        layout.addWidget(self.password_edit, 1, 1)
        layout.addWidget(self.show_password_checkbox, 1, 2)
        layout.addWidget(self.done_button, 3, 0, 1, 3, Qt.AlignBottom)

        self.setLayout(layout)

    def read_css(self, css_filename):
        with open(os.path.join(css_dir, css_filename), 'r') as f:
            return f.read()

    def done_pressed(self):
        email = self.email_edit.text()
        password = self.password_edit.text()

        self.window.config['oblc_email'] = email
        self.window.config['oblc_password'] = password

        self.window.update_config()

        self.window.stacked_layout.setCurrentIndex(0)

    def show_password_pressed(self):
        show = self.show_password_checkbox.checkState()

        if show:
            self.password_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)