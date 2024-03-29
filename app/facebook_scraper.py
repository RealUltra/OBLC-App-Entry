from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
import time
import string
from bs4 import BeautifulSoup
from subprocess import CREATE_NO_WINDOW

class Facebook:
    def __init__(self, driver=None, headless=False):
        if driver:
            self.driver = driver
        else:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--disable-notifications')

            if headless:
                chrome_options.add_argument('--headless')

            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument('--log-level=3')
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

    def start_login_window(self):
        self.driver.get('https://www.facebook.com/')

        cookies = {}
        try:
            while True:
                cookies = self.driver.get_cookies()
                self.driver.execute_script("return true;")
                time.sleep(1)  # Adjust the sleep time as needed

        except WebDriverException:
            pass

        except Exception as e:
            print(f"An error occurred: {e}")

        return cookies

    def add_cookies(self, cookies):
        self.driver.get('https://www.facebook.com/')

        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def is_logged_in(self):
        response = True

        self.driver.execute_script("window.open('', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

        self.driver.get('https://www.facebook.com/profile')

        s = time.time()
        while time.time() < (s + 3):
            if self.driver.current_url == "https://www.facebook.com/":
                response = False
                break

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])  # Switch back to the original tab

        return response

    def scrape_posts_and_photos(self, url):
        self.driver.get(url)

        first_post = None

        while not first_post:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            posts = soup.find_all('a', {'aria-label': 'Photo album photo'})

            for post in posts:
                href = post['href']

                if href.startswith('/photo'):
                    first_post = post
                    break

        first_post_url = 'https://www.facebook.com' + href

        self.driver.get(first_post_url)

        action_chains = ActionChains(self.driver)

        last_post = None
        counter = 0

        posts_and_photos = []
        while True:
            post_url = str(self.driver.current_url)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            try:
                img = soup.find('img', {'data-visualcompletion': 'media-vc-image'})
                src = img['src']
                image_found = True
            except:
                image_found = False

            if image_found:
                if post_url == last_post:
                    counter += 1

                    if counter >= 20:
                        break

                else:
                    last_post = post_url
                    counter = 0

                    posts_and_photos.append([post_url, src])
                    print('Posts & Photos Scraped:', len(posts_and_photos))

            action_chains.send_keys(Keys.ARROW_RIGHT).perform()
            time.sleep(0.1)

        return posts_and_photos

    def scrape_comments(self, url, remove_no_message_comments=True):
        self.driver.get(url)

        action_chains = ActionChains(self.driver)

        wait = WebDriverWait(self.driver, 5)
        shown_comments_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div[4]/div[1]/div/div')))
        action_chains.move_to_element(shown_comments_button).click().perform()

        wait = WebDriverWait(self.driver, 5)
        menu_div = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div')))
        menu_items = menu_div.find_elements(By.XPATH, "//div[@role='menuitem']")
        time.sleep(3)
        action_chains.move_to_element(menu_items[-1]).click().perform()
        #menu_items[-1].click()

        try:
            wait = WebDriverWait(self.driver, 5)
            show_previous_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div[4]/div[1]/div[1]/div[2]')))
            action_chains.move_to_element(show_previous_button).click().perform()
        except:
            pass

        time.sleep(0.5)

        try:
            ul = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div[4]/ul')
        except:
            return []

        comment_elems = ul.find_elements(By.TAG_NAME, 'li')

        comments = []
        for li in comment_elems:
            try:
                comment_elem = li.find_element(By.CSS_SELECTOR, "div[role='article']")
            except:
                continue

            text = comment_elem.text

            lines = text.split('\n')

            if len(lines) < 2:
                continue

            if 'Like' in lines: lines.remove('Like')
            if 'Reply' in lines: lines.remove('Reply')
            if 'Edited' in lines: lines.remove('Edited')

            sender = lines[0]
            sent_time = lines[-1]

            if len(lines) > 2:
                message = "\n".join(lines[1:-1])
            elif remove_no_message_comments:
                continue
            else:
                message = None

            comments.append([sender, message, sent_time])

        comments.sort(key=lambda x: self.get_seconds(x[2]))

        return comments

    def get_author(self, post_url):
        self.driver.get(post_url)

        wait = WebDriverWait(self.driver, 5)
        poster_elem = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[1]/span/div/h2/span')))
        poster = poster_elem.text

        return poster

    def get_description(self, post_url):
        self.driver.get(post_url)

        try:
            wait = WebDriverWait(self.driver, 1)
            description_elem = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div[2]/span')))
        except:
            return ""

        description = description_elem.text

        return description

    def get_seconds(self, text):
        text = text.lower()
        seconds = 0

        if text[-1] == 'w':
            num = int(text[:-1])
            seconds = num * 7 * 24 * 60 * 60

        elif text[-1] == 'd':
            num = int(text[:-1])
            seconds = num * 24 * 60 * 60

        return seconds

    def get_access_point_and_borrower(self, post, access_points, author=None):
        remove_list = ["return", "borrow", "oblc"] + list(string.punctuation)

        replace_list = [
            "available",
            "to",
            "from",
            "through",
            "by",
            "at",
        ]

        comments = self.scrape_comments(post)

        description = self.get_description(post)
        if description:
            comments.append([author, description, None])

        access_point = None
        access_point_i = -1
        for i, (sender, message, sent_time) in enumerate(comments):
            message = message.lower()
            filtered_words = []

            for word in re.findall(r"[^\s]+", message):
                add = True

                for filter in remove_list:
                    if filter in word:
                        add = False

                if add:
                    filtered_words.append(word)

            for filter in replace_list:
                while filter in filtered_words:
                    filtered_words.remove(filter)

            filtered_msg = " ".join(filtered_words).strip()

            if 'available' in message.lower():
                if "me" in re.findall(r'\S+', filtered_msg):
                    access_point = sender
                else:
                    access_point = filtered_msg
                    print(message)

                access_point_i = i
                break

        borrower = None
        for sender, message, sent_time in reversed(comments[:access_point_i]):
            filtered_words = []

            for word in re.findall(r"[^\s]+", message):
                add = True

                for filter in remove_list:
                    if filter.lower() in word.lower():
                        add = False

                if add:
                    filtered_words.append(word.lower())

            for filter in replace_list:
                while filter.lower() in filtered_words:
                    filtered_words.remove(filter.lower())

            filtered_msg = " ".join(filtered_words).strip()

            if 'borrowed' in message.lower():
                borrower = filtered_msg
            elif 'returned' in message.lower():
                borrower = None

        if access_point:
            for a_p in access_points:
                name = a_p.split('-')[0].strip()

                for word in re.findall(r'\S+', name):
                    if word.lower() in access_point:
                        access_point = a_p
                        break

        return access_point, borrower

    def comment(self, url, message):
        self.driver.get(url)

        wait = WebDriverWait(self.driver, 3)

        try:
            inp = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div[5]/div/div/div[2]/form/div/div[1]/div/div/div[1]')))
            inp.send_keys(message + '\n')
            time.sleep(1)
        except:
            print("[ERROR] Failed to comment!")

if __name__ == "__main__":
    email = ""
    password = ""

    fb = Facebook()
    fb.login(email, password)

    #fb.comment('https://www.facebook.com/photo/?fbid=503792391848528&set=oa.161780706062025', '.')

    post = 'https://www.facebook.com/photo/?fbid=353463226881446&set=oa.229396109093024'
    access_points = ['Anisha - Qurum', 'Reethu - MSQ', 'Eariele Arango  (Eariele) - Sohar', 'Sulaiman - Ghubra, Muscat', 'Nyasha - Al Hail', 'Rajeswari - Al Khuwair', 'Kanvi - Al Hail Greens', 'Shital - Wadi Kabir', 'Jessima - Azaiba', 'Nidhi Negandhi - Wadi Kabir', 'Shijila - Salalah', 'Jiya - Hatat Complex', 'Hansi - Darsait', 'Kunj Thakur  (Riya Thakur) - Darsait', 'Vindhya - Al mabelah', 'Trupti - Seeb', 'Nabila  ', 'Dhanya - Wadi Kabair', 'Ishani Prasobh  (Leena) - Ghala', 'Dr Zainab Ansari - Wadi Kabir', 'Sivasankari - Al Hail Greens', 'Siddhi Khare - Wadi Kabir', 'Abeda  ', 'Farzana  ', 'Remya Maniyath - Ghala', 'Samina - Ghubra, Muscat', 'Sparsha Vyas - Khuwair', 'Swetha Sujith Kumar - Ruwi', 'Thuraiya Al Kindy - Azaiba', 'Shilpa Deshpande - MSQ', 'Vijaylakshmi - Khuwair', 'gomathi Ganesh - Khuwair', 'Sakshi Markan - Ghubra', 'Hanisha Chawla - Ghubra, Al Asallah towers', 'Kripa C Pai - Ghala', 'Sujatha - Ruwi', 'Piya Toprani - Madinat Al Sultan Qaboos', 'Aina Junaid - Qurum', 'Asmi Raniga - Al Ghubra', 'Teny Tony  ', 'Hanane  ', 'Namiya - Wattayah', 'tarun - Bowsher', 'Pavithran  (Pavi) - Wadi Kabir', 'Sharanya - Ruwi', 'Aastha Kakaria - Al Khoud']
    comments = fb.get_access_point_and_borrower(post, access_points, fb.get_author(post))
    print(comments)
    print(len(comments))
    input()

    #posts_and_photos = fb.scrape_posts_and_photos('https://www.facebook.com/media/set/?set=oa.161780706062025&type=3')

    #with open('non-fiction-photos.json', 'w') as f:
    #    json.dump(posts_and_photos, f, indent=1)