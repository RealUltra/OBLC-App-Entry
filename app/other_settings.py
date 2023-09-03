from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from . import *

class OtherSettings(QWidget):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.stacked_layout = self.window.stacked_layout

        self.init_ui()

    @pyqtSlot()
    def selected(self):
        self.window.setWindowTitle('OBLC Data Entry | Other Settings')
        self.window.setStyleSheet(self.read_css('other_settings.css'))
        self.window.setFixedSize(450, 100)

        excel_sheet_name = self.window.config.get('excel_sheet_name')
        if excel_sheet_name:
            excel_sheet_i = self.window.wb.sheetnames.index(excel_sheet_name)
            self.sheets_combo_box.setCurrentIndex(excel_sheet_i)

    def init_ui(self):
        layout = QGridLayout()

        self.sheet_label = QLabel("Excel Sheet Name:")
        self.sheets_combo_box = QComboBox()
        self.done_button = QPushButton("Done")

        for sheet_name in self.window.wb.sheetnames:
            self.sheets_combo_box.addItem(sheet_name)

        self.done_button.clicked.connect(self.done_pressed)

        layout.addWidget(self.sheet_label, 0, 0, Qt.AlignCenter)
        layout.addWidget(self.sheets_combo_box, 0, 1)
        layout.addWidget(self.done_button, 2, 0, 1, 2, Qt.AlignBottom)

        self.setLayout(layout)

    def read_css(self, css_filename):
        with open(os.path.join(css_dir, css_filename), 'r') as f:
            return f.read()

    def done_pressed(self):
        excel_sheet_name = self.sheets_combo_box.currentText()

        self.window.config['excel_sheet_name'] = excel_sheet_name

        self.window.update_config()

        self.window.stacked_layout.setCurrentIndex(0)