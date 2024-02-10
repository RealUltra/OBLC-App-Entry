from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
from . import *
from .facebook_scraper import Facebook

class FacebookSettings(QWidget):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.stacked_layout = self.window.stacked_layout

        self.init_ui()

    @pyqtSlot()
    def selected(self):
        self.window.setWindowTitle('OBLC Data Entry | Facebook Settings')
        self.window.setStyleSheet(self.read_css('facebook_settings.css'))
        self.window.setFixedSize(450, 180)

        #self.email_edit.setText(self.window.config.get('facebook_email'))
        #self.password_edit.setText(self.window.config.get('facebook_password'))
        self.album_edit.setText(self.window.config.get('facebook_album_link'))

        #self.password_edit.setEchoMode(QLineEdit.Password)
        #self.show_password_checkbox.setChecked(False)

    def init_ui(self):
        layout = QGridLayout()

        #self.email_label = QLabel("Email:")
        #self.email_edit = QLineEdit()
        #self.password_label = QLabel("Password:")
        #self.password_edit = QLineEdit()
        #self.show_password_checkbox = QCheckBox()

        self.login_button = QPushButton("Login to Facebook")
        self.login_button.setObjectName("facebookLoginButton")
        self.login_button.setStyleSheet("""
        #facebookLoginButton {
        background-color: blue;
        color: white;
        }
        
        #facebookLoginButton:hover {
            background-color: #0000b0;
        }
        """)

        self.album_label = QLabel("Album Link:")
        self.album_edit = QLineEdit()
        self.done_button = QPushButton("Done")

        #self.show_password_checkbox.clicked.connect(self.show_password_pressed)
        self.login_button.clicked.connect(self.login_pressed)
        self.done_button.clicked.connect(self.done_pressed)

        #layout.addWidget(self.email_label, 0, 0, Qt.AlignCenter)
        #layout.addWidget(self.email_edit, 0, 1)
        #layout.addWidget(self.password_label, 1, 0, Qt.AlignCenter)
        #layout.addWidget(self.password_edit, 1, 1)
        #layout.addWidget(self.show_password_checkbox, 1, 2)
        layout.addWidget(self.login_button, 1, 1)
        layout.addWidget(self.album_label, 2, 0)
        layout.addWidget(self.album_edit, 2, 1)
        layout.addWidget(self.done_button, 3, 0, 1, 3, Qt.AlignBottom)

        self.setLayout(layout)

    def read_css(self, css_filename):
        with open(os.path.join(css_dir, css_filename), 'r') as f:
            return f.read()

    def login_pressed(self):
        cookies = self.window.config.get('facebook_cookies', '')

        try:
            cookies = json.loads(cookies)
        except:
            cookies = {}

        fb = Facebook(headless=False)
        fb.add_cookies(cookies)
        cookies = fb.start_login_window()

        self.window.config['facebook_cookies'] = json.dumps(cookies)
        self.window.update_config()

    def done_pressed(self):
        album_link = self.album_edit.text()
        self.window.config['facebook_album_link'] = album_link
        self.window.update_config()
        self.window.stacked_layout.setCurrentIndex(0)

    def show_password_pressed(self):
        show = self.show_password_checkbox.checkState()

        if show:
            self.password_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)