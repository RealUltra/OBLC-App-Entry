from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from _thread import start_new_thread
import re
import json
import pyperclip
from . import *
from .facebook_scraper import Facebook
from .messagebox import *

class Use(QWidget):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.stacked_layout = self.window.stacked_layout

        self.facebook = None
        self.facebook_ready = False

        self.init_ui()

    @pyqtSlot()
    def selected(self):
        start_new_thread(self.check_data, ())

        self.window.setWindowTitle('OBLC Data Entry | Use')
        self.window.setStyleSheet(self.read_css('use.css'))
        self.window.setFixedSize(450, 300)

        first_row = self.window.config.get('first_row')
        last_row = self.window.config.get('last_row')

        self.first_row_edit.setText('')
        self.last_row_edit.setText('')
        self.first_row_edit.setText(first_row)
        self.last_row_edit.setText(last_row)
        self.first_link_edit.setText(self.window.config.get('first_link'))

    def init_ui(self):
        layout = QGridLayout()

        self.back_button = QPushButton("Back")
        self.book_name_copy_button = QPushButton("Copy")
        self.book_name_edit = QLineEdit()
        self.book_isbn_copy_button = QPushButton("Copy")
        self.book_isbn_edit = QLineEdit()
        self.first_row_label = QLabel("First Row:")
        self.first_row_edit = QLineEdit()
        self.last_row_label = QLabel("Last Row:")
        self.last_row_edit = QLineEdit()
        self.first_link_label = QLabel("First Facebook Link:")
        self.first_link_edit = QLineEdit()
        self.start_button = QPushButton("Start")

        self.book_name_edit.setEnabled(False)
        self.book_isbn_edit.setEnabled(False)
        self.book_name_edit.setPlaceholderText("Book Name")
        self.book_isbn_edit.setPlaceholderText("Book ISBN")

        self.back_button.setObjectName("backButton")
        self.book_name_copy_button.setObjectName("bookNameCopyButton")
        self.book_name_edit.setObjectName("bookNameEdit")
        self.book_isbn_copy_button.setObjectName('bookIsbnCopyButton')
        self.book_isbn_edit.setObjectName("bookIsbnEdit")
        self.first_row_label.setObjectName("firstRowLabel")
        self.first_row_edit.setObjectName("firstRowEdit")
        self.last_row_label.setObjectName("lastRowLabel")
        self.last_row_edit.setObjectName("lastRowEdit")
        self.first_link_label.setObjectName("firstLinkLabel")
        self.first_link_edit.setObjectName("firstLinkEdit")
        self.start_button.setObjectName("startButton")

        self.back_button.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(0))
        self.book_name_copy_button.clicked.connect(lambda: pyperclip.copy(self.book_name_edit.text()))
        self.book_isbn_copy_button.clicked.connect(lambda: pyperclip.copy(self.book_isbn_edit.text()))
        self.first_row_edit.textChanged.connect(self.on_first_row_changed)
        self.last_row_edit.textChanged.connect(self.on_last_row_changed)
        self.first_link_edit.textChanged.connect(self.on_first_link_changed)
        self.start_button.clicked.connect(self.start_pressed)

        self.start_button.setToolTip("Get started with the app entries!")

        layout.addWidget(self.back_button, 0, 0, 1, 2)
        layout.addWidget(self.book_name_copy_button, 1, 0)
        layout.addWidget(self.book_name_edit, 1, 1)
        layout.addWidget(self.book_isbn_copy_button, 2, 0)
        layout.addWidget(self.book_isbn_edit, 2, 1)
        layout.addWidget(self.first_row_label, 3, 0, Qt.AlignCenter)
        layout.addWidget(self.first_row_edit, 3, 1)
        layout.addWidget(self.last_row_label, 4, 0, Qt.AlignCenter)
        layout.addWidget(self.last_row_edit, 4, 1)
        layout.addWidget(self.first_link_label, 5, 0, Qt.AlignCenter)
        layout.addWidget(self.first_link_edit, 5, 1)
        layout.addWidget(self.start_button, 6, 0, 1, 2, Qt.AlignBottom)

        self.setLayout(layout)

    def check_data(self):
        sheet_name = self.window.config.get('excel_sheet_name')
        if sheet_name not in self.window.wb.sheetnames:
            self.stacked_layout.setCurrentIndex(0)
            showerror("Error", "Please set an excel sheet!")
            return False

        return True

    def read_css(self, css_filename):
        with open(os.path.join(css_dir, css_filename), 'r') as f:
            return f.read()

    def on_first_row_changed(self):
        row_str = self.first_row_edit.text().strip()

        excel_sheet_name = self.window.config.get('excel_sheet_name').strip()
        sheet = self.window.wb[excel_sheet_name]

        if not row_str.isdecimal():
            row_str = ''.join(re.findall('\d+', row_str))
            self.first_row_edit.setText(row_str)

        if row_str:
            row_num = int(row_str.strip())

            if row_num > 1:
                book_name, isbn = self.get_book_name_and_isbn(sheet, row_num)
            else:
                book_name, isbn = "", ""

            if not isbn:
                isbn = ""

            self.book_name_edit.setText(book_name)
            self.book_isbn_edit.setText(isbn)

        else:
            self.book_name_edit.setText("")
            self.book_isbn_edit.setText("")

        self.window.config['first_row'] = row_str
        self.window.update_config()

    def on_last_row_changed(self):
        row_str = self.last_row_edit.text().strip()

        if row_str:
            if not row_str.isdecimal():
                row_str = ''.join(re.findall('\d+', row_str))
                self.last_row_edit.setText(row_str)

        self.window.config['last_row'] = row_str
        self.window.update_config()

    def on_first_link_changed(self):
        first_link = self.first_link_edit.text().strip()
        self.window.config['first_link'] = first_link
        self.window.update_config()

    def start_pressed(self):
        self.stacked_layout.setCurrentIndex(5)

    def get_book_name_and_isbn(self, sheet, row_num):
        try:
            row_cells = tuple(sheet.iter_rows(min_row=row_num, max_row=row_num, values_only=True))[0]
        except ValueError:
            return "", ""

        columns = tuple(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]

        isbn_index = -1
        book_name_index = -1
        for i, col in enumerate(columns):
            if not col:
                continue

            if 'isbn' in col.lower() and isbn_index == -1:
                isbn_index = i

            if 'name' in col.lower() and 'book' in col.lower() and book_name_index == -1:
                book_name_index = i

        book_name = row_cells[book_name_index]
        isbn = row_cells[isbn_index]

        if type(isbn) == float:
            isbn = int(isbn)

        if isbn == None:
            isbn = ""
        else:
            isbn = str(isbn)

        return book_name, isbn

