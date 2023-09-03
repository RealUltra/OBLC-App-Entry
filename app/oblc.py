import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from subprocess import CREATE_NO_WINDOW

class OBLC:
    url = "https://omanbookloversclub.000webhostapp.com"

    def __init__(self, driver=None, headless=False):
        if driver:
            self.driver = driver
        else:
            chrome_options = webdriver.ChromeOptions()

            if headless:
                chrome_options.add_argument('--headless')

            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            while True:
                try:
                    executable = ChromeDriverManager().install()
                except:
                    print('[ERROR] Failed to install chromedriver!')
                else:
                    print('[SUCCESS] Successfully installed chromedriver!')
                    break

            service = Service(executable_path=executable)
            service.creation_flags = CREATE_NO_WINDOW

            self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.driver.maximize_window()

        self.email = None
        self.password = None

    def login(self, email, password):
        self.driver.get(self.url + "/public/login")

        self.email = email
        self.password = password

        email_input = self.driver.find_element(By.ID, "email")
        password_input = self.driver.find_element(By.ID, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, ".btn")

        email_input.send_keys(email)
        password_input.send_keys(password)
        login_button.click()

    def is_logged_in(self):
        response = True

        self.driver.execute_script("window.open('', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

        self.driver.get(self.url + "/public/home")

        s = time.time()
        while time.time() < (s + 2):
            if "/public/login" in self.driver.current_url:
                response = False
                break

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])  # Switch back to the original tab

        return response

    def add_book(self, isbn=''):
        self.driver.get(self.url + "/public/new-books")
        self.enter_isbn(isbn)

    def enter_isbn(self, isbn):
        isbn_input = self.driver.find_element(By.CSS_SELECTOR, '#isbn')
        isbn_input.send_keys(str(isbn))
        isbn_input.submit()

    def enter_title(self, title):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#title')
        inp.send_keys(title)

    def enter_subtitle(self, subtitle):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#subtitle')
        inp.send_keys(subtitle)

    def enter_authors(self, authors):
        if authors:
            inp = self.driver.find_element(By.CSS_SELECTOR, '#authors')
            inp.send_keys(",".join(authors))

        else:
            checkbox = self.driver.find_element(By.CSS_SELECTOR, '#author_not_available')
            checkbox.click()

    def enter_description(self, description):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#description')
        inp.send_keys(description)

    def enter_isbns(self, isbns):
        if isbns:
            inp = self.driver.find_element(By.CSS_SELECTOR, '#isbn')
            inp.send_keys(",".join(list(map(lambda x: str(x), isbns))))

        else:
            checkbox = self.driver.find_element(By.CSS_SELECTOR, '#isbn_not_available')
            checkbox.click()

    def enter_publisher(self, publisher):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#publisher')
        inp.send_keys(publisher)

    def enter_published_year(self, published_year):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#publishedDate')
        inp.send_keys(str(published_year))

    def enter_genres(self, genres):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#genres')
        inp.send_keys(",".join(genres))

    def enter_sub_genres(self, sub_genres):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#sub_genre')
        inp.send_keys(",".join(sub_genres))

    def set_age_group(self, age_group_index):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#age_group')
        dropdown = Select(dropdown_element)
        dropdown.select_by_index(age_group_index)

    def get_age_groups(self):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#age_group')
        option_elems = dropdown_element.find_elements(By.TAG_NAME, 'option')
        options = list(map(lambda x: x.get_attribute('textContent'), option_elems))
        options = options[1:]
        return options

    def set_language(self, language):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#language')
        dropdown = Select(dropdown_element)
        dropdown.select_by_visible_text(language.title())

    def get_languages(self):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#language')
        option_elems = dropdown_element.find_elements(By.TAG_NAME, 'option')
        options = list(map(lambda x: x.get_attribute('textContent'), option_elems))
        options = options[1:]
        return options

    def enter_page_count(self, page_count):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#page_count')
        inp.send_keys(str(page_count))

    def enter_facebook_link(self, fb_link):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#fb_link')
        inp.send_keys(fb_link)

    def set_facebook_category(self, fb_category_i):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#category')
        dropdown = Select(dropdown_element)
        dropdown.select_by_index(fb_category_i)

    def get_facebook_categories(self):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#category')
        option_elems = dropdown_element.find_elements(By.TAG_NAME, 'option')
        options = list(map(lambda x: x.get_attribute('textContent'), option_elems))
        options = options[1:]
        return options

    def set_lender(self, lender_i):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#lender')
        dropdown = Select(dropdown_element)
        dropdown.select_by_index(lender_i)

    def get_lenders(self):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#lender')
        option_elems = dropdown_element.find_elements(By.TAG_NAME, 'option')
        options = list(map(lambda x: x.get_attribute('textContent'), option_elems))
        options = options[1:]
        return options

    def set_access_point(self, access_point_i):
        try:
            dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#accessPoint')
        except:
            return

        dropdown = Select(dropdown_element)
        dropdown.select_by_index(access_point_i)

    def get_access_points(self):
        try:
            dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#accessPoint')
        except:
            return []

        option_elems = dropdown_element.find_elements(By.TAG_NAME, 'option')
        options = list(map(lambda x: x.get_attribute('textContent'), option_elems))
        options = options[1:]
        return options

    def set_book_status(self, status):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#status')
        dropdown = Select(dropdown_element)
        dropdown.select_by_visible_text(status)

    def get_book_statuses(self):
        dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#status')
        option_elems = dropdown_element.find_elements(By.TAG_NAME, 'option')
        options = list(map(lambda x: x.get_attribute('textContent'), option_elems))
        options = options[1:]
        return options

    def set_borrower(self, borrower_i):
        try:
            dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#borrower_id')
        except:
            return

        dropdown = Select(dropdown_element)
        dropdown.select_by_index(borrower_i)

    def get_borrowers(self):
        try:
            dropdown_element = self.driver.find_element(By.CSS_SELECTOR, '#borrower_id')
        except:
            return []

        option_elems = dropdown_element.find_elements(By.TAG_NAME, 'option')
        options = list(map(lambda x: x.get_attribute('textContent'), option_elems))
        options = options[1:]
        return options

    def enter_cover_photo_link(self, cover_photo_link):
        inp = self.driver.find_element(By.CSS_SELECTOR, '#thumbnail_link')
        inp.send_keys(cover_photo_link)

    def press_add_book_button(self):
        action_chains = ActionChains(self.driver)

        wait = WebDriverWait(self.driver, 1)
        btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#add_book_btn')))
        action_chains.move_to_element(btn).click().perform()

        s = time.time()
        while time.time() < (s + 3):
            try:
                if '/public/new-books' in self.driver.current_url:
                    return True
            except Exception as e:
                print("Error:", e)
                return False

        return False

    def get_search_results(self, query, options):
        results = []

        for i, option in enumerate(options):
            if query.lower().strip() in option.lower().strip():
                results.append(i)

        return results

    def find_best_match(self, query, options):
        q = ''
        result = None

        for i, c in enumerate(query):
            q += c
            results = self.get_search_results(q, options)

            if not results:
                q = q[:-1]
                results = self.get_search_results(q, options)
                result = results[0]
                break

            if i == (len(query) - 1):
                result = results[0]
                break

        return result

    def get_duplicate_links(self):
        oblc = OBLC(headless=True)
        oblc.login(self.email, self.password)

        duplicate_elements = self.driver.find_elements(By.CSS_SELECTOR, '#duplicate_list > label > a')

        duplicate_fb_links = []
        for duplicate in duplicate_elements:
            href = duplicate.get_attribute('href')
            oblc.driver.get(href)
            elem = oblc.driver.find_element(By.CSS_SELECTOR, '#fb_link')
            fb_link = elem.get_attribute('value')
            duplicate_fb_links.append(fb_link)

        return duplicate_fb_links

if __name__ == '__main__':
    oblc = OBLC(headless=True)
    oblc.add_book()
    print(oblc.get_access_points())