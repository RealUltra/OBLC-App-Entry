from PyQt5.QtWidgets import QApplication
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

css_dir = resource_path(f'{data_dir}/css')
icon_path = resource_path(f'{data_dir}/logo.png')
credentials_file = resource_path(f'{data_dir}/credentials.json')
db_file = resource_path(f"{data_dir}/db.xlsx")
posts_and_photos_dir = f'{data_dir}/posts_and_photos'
token_file = f'{data_dir}/token.json'
config_file = f"{data_dir}/config.txt"

ALBUM_IDS = [
    "oa.593757866080803", "oa.268111339203344", "oa.211779284953320",
    "oa.593878089434226", "oa.232754695932177", "oa.1278775029374496",
    "oa.1174950109850009", "oa.170359382009385", "oa.525769706293730",
    "oa.1218873578741412", "oa.1228345307771360", "oa.682343563494767",
    "oa.681550873349205", "oa.353189830228885", "oa.402535325265902",
    "oa.336757238244799", "oa.289383589791983", "oa.4311918308925312",
    "oa.161780706062025", "oa.345804293855070", "oa.1120908834982990",
    "oa.577121506778166", "oa.145074107732807", "oa.229396109093024",
    "oa.333655905121158", "oa.331323592060283", "oa.6882482225115553",
    "oa.351139606335779"
]

FB_CATEGORIES = [
    "Curriculum 2",
    "Knowledge 2 (Light & fun educational and Encyclopedias)",
    "Sohar",
    "Non Fiction 2",
    "Babies / Toddlers / Board Books / Story Books 2",
    "Salalah",
    "Beginner & Young Readers 2",
    "Fiction 3",
    "Young Adult 2",
    "Curriculum / Textbooks",
    "Growing Readers 2",
    "Puzzles, Educational / Bookish Toys & Games",
    "Fiction 2",
    "Professional / Higher Education",
    "Magazines & Hobby",
    "Non-English Books",
    "Young Adult",
    "Miscellaneous",
    "Non-Fiction",
    "Fiction",
    "Encyclopedia / Knowledge / Light & Fun Educational",
    "Poetry",
    "Graphic Novels & Comics",
    "Growing Readers & Young Adult Books",
    "Beginner Readers & Young Readers",
    "Babies & Toddlers, Story Books",
    "Young Adults 3: Books and Borrowing",
    "5 to 10 year olds"
]

GENRES = ['Non-Fiction', 'Non-Fiction', None,
          'Non-Fiction', None, None,
          'Fiction', 'Fiction', 'Fiction',
          'Non-Fiction', 'Fiction', 'Non-Fiction',
          'Fiction', 'Non-Fiction', 'Non-Fiction',
          None, 'Fiction', 'Non-Fiction',
          'Non-Fiction', 'Fiction', 'Non-Fiction',
          None, 'Fiction', 'Fiction',
          'Fiction', None]

os.popen('taskkill /F /im chromedriver.exe').read()

def run_app():
    from .main_window import MainWindow
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec_()
