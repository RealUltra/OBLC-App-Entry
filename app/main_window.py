from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import warnings
import openpyxl

from . import *
from .gsheets import *
from .main_menu import MainMenu
from .use import Use
from .oblc_settings import OBLCSettings
from .facebook_settings import FacebookSettings
from .other_settings import OtherSettings
from .active_window import ActiveWindow
from .loading_screen import LoadingScreen

warnings.filterwarnings("ignore")

class MainWindow(QWidget):
    START_INDEX = 0

    def __init__(self, app):
        super().__init__()

        self.app = app

        self.setWindowIcon(QIcon(icon_path))

        self.config = self.load_config()

        #self.wb = openpyxl.load_workbook(db_file)
        self.wb = get_workbook()

        self.stacked_layout = QStackedLayout()

        self.main_menu = MainMenu(self)
        self.use = Use(self)
        self.oblc_settings = OBLCSettings(self)
        self.facebook_settings = FacebookSettings(self)
        self.other_settings = OtherSettings(self)
        self.active_window = ActiveWindow(self)
        self.loading_screen = LoadingScreen(self)

        self.stacked_layout.addWidget(self.main_menu) # Main Menu - 0
        self.stacked_layout.addWidget(self.use) # Use - 1
        self.stacked_layout.addWidget(self.oblc_settings) # OBLC Settings - 2
        self.stacked_layout.addWidget(self.facebook_settings) # Facebook Settings - 3
        self.stacked_layout.addWidget(self.other_settings) # Other Settings - 4
        self.stacked_layout.addWidget(self.active_window) # Active Window - 5
        self.stacked_layout.addWidget(self.loading_screen) # Loading Screen - 6

        self.setLayout(self.stacked_layout)

        self.stacked_layout.currentChanged.connect(self.on_widget_selected)

        if self.START_INDEX != 0:
            self.stacked_layout.setCurrentIndex(self.START_INDEX)
        else:
            self.on_widget_selected(self.START_INDEX)

    @pyqtSlot(int)
    def on_widget_selected(self, index):
        selected_widget = self.stacked_layout.widget(index)

        if selected_widget:
            selected_widget.selected()

    def closeEvent(self, event):
        self.hide()

        if self.active_window.oblc:
            self.active_window.running = False
            self.active_window.oblc.driver.quit()

        if self.active_window.facebook:
            self.active_window.running = False
            self.active_window.facebook.driver.quit()

        self.app.quit()

    def load_config(self):
        example_config = {
            "oblc_email": "",
            "oblc_password": "",
            "facebook_email": "",
            "facebook_password": "",
            "album_link": "",
            "excel_sheet_name": "",
            "first_row": "",
            "last_row": "",
            "first_link": ""
        }

        if not os.path.exists(config_file):
            with open(config_file, 'w') as f:
                json.dump(example_config, f, indent=2)

        with open(config_file, 'r') as f:
            config = json.load(f)

        return config

    def dump_config(self, config):
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def update_config(self):
        self.dump_config(self.config)