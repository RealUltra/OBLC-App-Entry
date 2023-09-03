from selenium.common.exceptions import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from _thread import start_new_thread
import re
import json
import time
from plyer import notification
from . import *
from .messagebox import *
from .facebook_scraper import Facebook
from .oblc import OBLC
from .google_scraper import *

class ActiveWindow(QWidget):
    running = True

    def __init__(self, window):
        super().__init__()

        self.window = window
        self.stacked_layout = self.window.stacked_layout

        self.init_ui()

        self.data_checked = False
        self.facebook = None
        self.sheet = None
        self.fb_category = None
        self.genre = None
        self.posts_and_photos = None
        self.posts_start_index = None
        self.oblc = None
        self.row_i = None
        self.rows = None
        self.first_row = None
        self.last_row = None
        self.book_name_index = None
        self.book_isbn_index = None

    @pyqtSlot()
    def selected(self):
        self.window.setWindowTitle('OBLC Data Entry')
        self.window.setStyleSheet(self.read_css('active_window.css'))
        self.window.setFixedSize(450, 175)

        start_new_thread(self.check_data, ())

    def init_ui(self):
        self.layout = QGridLayout()

        self.row_edit = QLineEdit()
        self.book_name_copy_button = QPushButton("Copy")
        self.book_name_edit = QLineEdit()
        self.book_isbn_copy_button = QPushButton("Copy")
        self.book_isbn_edit = QLineEdit()
        self.add_button = QPushButton("Add")
        self.skip_button = QPushButton("Skip")
        self.repeat_button = QPushButton("Repeat")
        self.back_button = QPushButton("Back")

        self.row_edit.setEnabled(False)
        self.book_name_edit.setEnabled(False)
        self.book_isbn_edit.setEnabled(False)
        self.row_edit.setPlaceholderText("Row Number")
        self.book_name_edit.setPlaceholderText("Book Name")
        self.book_isbn_edit.setPlaceholderText("Book ISBN")

        self.row_edit.setObjectName("rowEdit")
        self.book_name_copy_button.setObjectName("bookNameCopyButton")
        self.book_name_edit.setObjectName("bookNameEdit")
        self.book_isbn_copy_button.setObjectName('bookIsbnCopyButton')
        self.book_isbn_edit.setObjectName("bookIsbnEdit")
        self.add_button.setObjectName("addButton")
        self.skip_button.setObjectName("skipButton")
        self.repeat_button.setObjectName("repeatButton")
        self.back_button.setObjectName("backButton")

        self.add_button.clicked.connect(self.add_pressed)
        self.skip_button.clicked.connect(self.skip_pressed)
        self.repeat_button.clicked.connect(self.repeat_pressed)
        self.back_button.clicked.connect(self.back_pressed)

        self.layout.addWidget(self.row_edit, 0, 1, 1, 3)
        self.layout.addWidget(self.book_name_copy_button, 1, 0)
        self.layout.addWidget(self.book_name_edit, 1, 1, 1, 3)
        self.layout.addWidget(self.book_isbn_copy_button, 2, 0)
        self.layout.addWidget(self.book_isbn_edit, 2, 1, 1, 3)
        self.layout.addWidget(self.add_button, 3, 0, Qt.AlignBottom)
        self.layout.addWidget(self.skip_button, 3, 1, Qt.AlignBottom)
        self.layout.addWidget(self.repeat_button, 3, 2, Qt.AlignBottom)
        self.layout.addWidget(self.back_button, 3, 3, Qt.AlignBottom)

        self.setLayout(self.layout)

    def process(self):
        row_num = self.row_i + self.first_row

        if row_num > self.last_row:
            self.window.close()
            showinfo("Success", "Your task has been completed!")
            return

        self.stacked_layout.setCurrentIndex(6)

        row = self.rows[self.row_i]

        book_name = row[self.book_name_index]
        isbn = row[self.book_isbn_index]
        post, photo = self.posts_and_photos[self.posts_start_index + self.row_i]

        try:
            self.oblc.add_book()
        except:
            pass

        lender = self.facebook.get_author(post)

        if book_name or isbn:
            if isbn and (str(isbn).isnumeric() or type(isbn) in [int, float]):
                if type(isbn) == float:
                    isbn = str(int(isbn))

                book_info = get_book_info(isbn=isbn)

                if not book_info:
                    book_info = get_book_info(name=book_name)

            else:
                book_info = get_book_info(name=book_name)

        else:
            book_info = {}

        access_points = self.oblc.get_access_points()

        access_point, borrower = self.facebook.get_access_point_and_borrower(post, access_points, lender)

        if book_info:
            if not book_info['sub_genres']:
                if self.genre:
                    book_info['sub_genres'] = [self.genre]

            self.oblc.enter_title(book_info['title'])
            self.oblc.enter_subtitle(book_info['subtitle'])

            #print(self.oblc.get_duplicate_links())

            self.oblc.enter_authors(book_info['authors'])
            self.oblc.enter_description(book_info['description'])
            self.oblc.enter_isbns(book_info['isbns'])
            self.oblc.enter_publisher(book_info['publisher'])
            self.oblc.enter_published_year(book_info['published_year'])
            self.oblc.enter_sub_genres(book_info['sub_genres'])
            self.oblc.set_language(book_info['language'])
            self.oblc.enter_page_count(book_info['page_count'])

        if self.genre:
            self.oblc.enter_genres([self.genre])

        self.oblc.set_age_group(0)
        self.oblc.enter_facebook_link(post)
        self.oblc.enter_cover_photo_link(photo)

        lenders = self.oblc.get_lenders()
        lender_i = self.oblc.find_best_match(lender, lenders)
        self.oblc.set_lender(lender_i + 1)

        if not access_point:
            access_point = "Anisha - Qurum"

        print("Access Point:", access_point)
        access_point_i = self.oblc.find_best_match(access_point, access_points)

        try:
            self.oblc.set_access_point(access_point_i + 1)
        except:
            pass

        if not borrower:
            self.oblc.set_book_status("AVAILABLE")

        else:
            self.oblc.set_book_status("BORROWED")

            borrowers = self.oblc.get_borrowers()
            borrower_i = self.oblc.find_best_match(borrower, borrowers)

            try:
                self.oblc.set_borrower(borrower_i + 1)
            except:
                pass

        fb_categories = self.oblc.get_facebook_categories()
        fb_category_i = self.oblc.find_best_match(self.fb_category, fb_categories)
        self.oblc.set_facebook_category(fb_category_i + 1)

        self.row_edit.setText(str(self.row_i + self.first_row))
        self.book_name_edit.setText(book_name)
        self.book_isbn_edit.setText(isbn)

        self.stacked_layout.setCurrentIndex(5)

    def add_pressed(self):
        post, photo = self.posts_and_photos[self.posts_start_index + self.row_i]

        self.row_i += 1

        try:
            success = self.oblc.press_add_book_button()
        except:
            success = True

        if success:
            self.facebook.comment(post, "App Entry Done!")
        else:
            self.row_i -= 1

        self.update_config()
        start_new_thread(self.process, ())

    def skip_pressed(self):
        self.row_i += 1
        self.update_config()
        start_new_thread(self.process, ())

    def repeat_pressed(self):
        self.update_config()
        start_new_thread(self.process, ())

    def back_pressed(self):
        self.row_i -= 1
        self.update_config()
        start_new_thread(self.process, ())

    def update_config(self):
        row_num = self.row_i + self.first_row
        post_link = self.posts_and_photos[self.posts_start_index + self.row_i][0]

        if row_num > self.last_row:
            self.window.config['last_row'] = ''

        self.window.config['first_row'] = str(row_num)
        self.window.config['first_link'] = post_link

        self.window.update_config()

    def check_data(self):
        if self.data_checked:
            return

        self.stacked_layout.setCurrentIndex(6)

        oblc_email = self.window.config.get('oblc_email')
        oblc_password = self.window.config.get('oblc_password')
        facebook_email = self.window.config.get('facebook_email')
        facebook_password = self.window.config.get('facebook_password')
        excel_sheet_name = self.window.config.get('excel_sheet_name')
        first_row = self.window.config.get('first_row')
        last_row = self.window.config.get('last_row')
        first_post_link = self.window.config.get('first_link')

        if not oblc_email:
            showerror("Error", "Please enter your OBLC email address.")
            self.stacked_layout.setCurrentIndex(2)
            return
        elif not oblc_password:
            showerror("Error", "Please enter your OBLC password.")
            self.stacked_layout.setCurrentIndex(2)
            return
        elif not facebook_email:
            showerror("Error", "Please enter your facebook email address.")
            self.stacked_layout.setCurrentIndex(3)
            return
        elif not facebook_password:
            showerror("Error", "Please enter your facebook password.")
            self.stacked_layout.setCurrentIndex(3)
            return
        elif not excel_sheet_name:
            showerror("Error", "Please select an excel sheet.")
            self.stacked_layout.setCurrentIndex(4)
            return
        elif not first_row:
            showerror("Error", "Please enter the first row number.")
            self.stacked_layout.setCurrentIndex(1)
            return
        elif not last_row:
            showerror("Error", "Please enter the last row number.")
            self.stacked_layout.setCurrentIndex(1)
            return
        elif not first_post_link:
            showerror("Error", "Please enter the facebook post link of the first book.")
            self.stacked_layout.setCurrentIndex(1)
            return

        self.sheet = self.window.wb[excel_sheet_name]

        self.window.loading_screen.loading_label.setText("Logging into facebook")

        self.facebook = Facebook()
        self.facebook.login(facebook_email, facebook_password)

        self.window.loading_screen.loading_label.setText("Loading")

        if not self.facebook.is_logged_in():
            self.facebook.driver.quit()
            self.facebook = None
            showerror("Error", "Failed to login to facebook. Please check your credentials and try again!")
            self.stacked_layout.setCurrentIndex(3)
            return

        album_id = self.get_album_id(first_post_link)

        if not album_id:
            showerror("Error", "The facebook post link for the first book that has been entered is invalid. Please try again!")
            self.stacked_layout.setCurrentIndex(1)
            return

        if album_id not in ALBUM_IDS:
            showerror("Error", "The album your facebook post is from is not registered in the system. Please use a different album or try again later!")
            self.stacked_layout.setCurrentIndex(1)
            return

        i = ALBUM_IDS.index(album_id)
        self.fb_category = FB_CATEGORIES[i]
        self.genre = GENRES[i]

        json_path = os.path.join(posts_and_photos_dir, f'{album_id}.json')

        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                self.posts_and_photos = json.load(f)

        else:
            self.window.loading_screen.loading_label.setText('Scraping posts & photos')
            album_link = self.get_album_link(album_id)

            self.posts_and_photos = self.facebook.scrape_posts_and_photos(album_link)

            os.makedirs(posts_and_photos_dir, exist_ok=True)
            with open(json_path, 'w') as f:
                json.dump(self.posts_and_photos, f)

        self.window.loading_screen.loading_label.setText('Loading')

        posts_start_index = -1
        for i, (post, photo) in enumerate(self.posts_and_photos):
            if self.get_image_id(post) == self.get_image_id(first_post_link):
                posts_start_index = i
                break

        if posts_start_index == -1:
            showerror("Error", "The facebook post link for the first book that has been entered is invalid. Please try again!")
            self.stacked_layout.setCurrentIndex(1)
            return

        self.posts_start_index = posts_start_index

        self.oblc = OBLC()
        self.oblc.login(oblc_email, oblc_password)

        self.data_checked = True
        self.row_i = 0
        self.first_row = int(first_row)
        self.last_row = int(last_row)

        columns = tuple(self.sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]

        self.book_isbn_index = -1
        self.book_name_index = -1
        for i, col in enumerate(columns):
            if not col:
                continue

            if 'isbn' in col.lower() and self.book_isbn_index == -1:
                self.book_isbn_index = i

            if 'name' in col.lower() and 'book' in col.lower() and self.book_name_index == -1:
                self.book_name_index = i

        self.rows = list(self.sheet.iter_rows(min_row=self.first_row, max_row=self.last_row, values_only=True))

        start_new_thread(self.handle_browser, ())
        self.process()

        notification.notify(
            title="Ready!",
            message="The OBLC Data Entry application is ready for use!",
            app_name="OBLC Data Entry",
            timeout=5,
            toast=True,
            #app_icon="path/to/icon.png",
        )

        self.stacked_layout.setCurrentIndex(5)

    def handle_browser(self):
        while self.running:
            try:
                self.oblc.driver.current_url
            except NoSuchWindowException:
                self.window.close()
            except:
                pass

    def read_css(self, css_filename):
        with open(os.path.join(css_dir, css_filename), 'r') as f:
            return f.read()

    def get_album_id(self, fb_link):
        r = re.search('set=([\d\w\.]+)', fb_link)

        if r:
            return r[1]

    def get_image_id(self, fb_link):
        r = re.search('fbid=(\d+)', fb_link)

        if r:
            return r[1]

    def get_album_link(self, album_id):
        return f'https://www.facebook.com/media/set/?set={album_id}'