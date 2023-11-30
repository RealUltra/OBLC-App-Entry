from gphotos import *
import os, re
import json
import time
import random
from facebook_scraper import Facebook

client = GooglePhotosClient.authenticate('client_secrets.json', 'token.json')

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

posts_and_photos_dir = "posts_and_photos"

def upload_to_google_photos(post_link, image_link=None, album_id=None, image_id=None, previous_image_id=None):
    fb_album_id = get_album_id(post_link)
    fb_image_id = get_image_id(post_link)
    album_name = FB_CATEGORIES[ALBUM_IDS.index(fb_album_id)]

    if album_id is None:
        albums = client.list_albums()

        for album in albums:
            if album.get('title').strip().lower() == album_name.strip().lower():
                album_id = album.get('id')

    if not album_id:
        album = client.create_album(album_name)
        album_id = album.get('id')

    if image_id is None:
        album_images = client.list_photos_in_album(album_id)

        image_id = None
        for image in album_images:
            if image.get('description') == fb_image_id:
                image_id = image.get('id')

    if not image_id:
        resp = client.upload_photo_from_url(image_link, album_id=album_id, description=fb_image_id, previous_image_id=previous_image_id)
        return resp.get('newMediaItemResults')[0].get('mediaItem')

    else:
        return client.get_photo_by_id(image_id)

def get_album_id(fb_link):
    r = re.search(r'set=([\d\w\.]+)', fb_link)

    if r:
        return r[1]

def get_image_id(fb_link):
    r = re.search(r'fbid=(\d+)', fb_link)

    if r:
        return r[1]

def fix_album_link(fb_link):
    album_id = get_album_id(fb_link)
    return get_album_link_from_id(album_id)

def get_album_link_from_id(album_id):
    return f'https://www.facebook.com/media/set/?set={album_id}'

def get_gphotos_id_from_link(gphotos_link):
    r = re.search(r'photos/([\w\d]+)', gphotos_link)

    if r:
        return r[1]

def exponential_backoff(func, max_retries, initial_delay=1, max_delay=60):
    retries = 0
    delay = initial_delay

    while retries < max_retries:
        try:
            return func()
        except:
            time.sleep(delay)
            retries += 1
            delay *= 2  # Exponentially increase the delay
            delay = min(delay, max_delay)  # Cap the delay to a maximum value
            delay += random.uniform(0, delay * 0.1)  # Add jitter

    if retries == max_retries:
        raise Exception("Max retries reached")

def get_posts_and_photos(file_path, fb, album_link, album_name):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            posts_and_photos = json.load(f)

        r = requests.get(posts_and_photos[0][1])
        if r.content == b"URL signature expired":
            print(f'"{album_name}" image links expired!')
            os.unlink(file_path)

    if not os.path.exists(file_path):
        print(f'Scraping "{album_name}"...')
        posts_and_photos = fb.scrape_posts_and_photos(album_link)
        with open(file_path, 'w') as f:
            json.dump(posts_and_photos, f)
        print("Scraped!\n")

    else:
        with open(file_path, 'r') as f:
            posts_and_photos = json.load(f)

    return posts_and_photos

def main():
    fb_email = input("[FACEBOOK EMAIL] ").strip()
    fb_password = input("[FACEBOOK PASSWORD] ")

    fb = Facebook()
    fb.login(fb_email, fb_password)

    for album_id in ALBUM_IDS:
        album_name = FB_CATEGORIES[ALBUM_IDS.index(album_id)]
        album_link = get_album_link_from_id(album_id)
        file_path = f'{posts_and_photos_dir}/{album_id}.json'
        get_posts_and_photos(file_path, fb, album_link, album_name)

    failure = True
    while failure:
        failure = False

        for album_id in ALBUM_IDS:
            album_name = FB_CATEGORIES[ALBUM_IDS.index(album_id)]
            album_link = get_album_link_from_id(album_id)
            file_path = f'{posts_and_photos_dir}/{album_id}.json'

            posts_and_photos = get_posts_and_photos(file_path, fb, album_link, album_name)

            while True:
                albums = client.list_albums()
                if albums is not None:
                    break

            gphotos_album_id = None
            for album in albums:
                if album.get('title') == album_name:
                    gphotos_album_id = album.get('id')

            uploaded_photo_ids = {}

            if gphotos_album_id:
                fb_image_ids = list(map(lambda x: get_image_id(x[0]), posts_and_photos))

                while True:
                    photos = client.list_photos_in_album(gphotos_album_id)
                    if photos is not None:
                        break

                for photo in photos:
                    fb_image_id = photo.get('description')
                    image_id = photo.get('id')

                    if fb_image_id in fb_image_ids:
                        uploaded_photo_ids[fb_image_id] = image_id

            for i, (post, photo) in enumerate(posts_and_photos):
                fb_image_id = get_image_id(post)

                if fb_image_id in uploaded_photo_ids:
                    print(f"{i + 1}/{len(posts_and_photos)} of {album_name}: ALREADY UPLOADED")
                    continue

                previous_image_id = None
                if i > 0:
                    previous_post = posts_and_photos[i - 1][0]
                    previous_fb_image_id = get_image_id(previous_post)

                    if previous_fb_image_id in uploaded_photo_ids:
                        previous_image_id = uploaded_photo_ids[previous_fb_image_id]

                try:
                    g_photo = exponential_backoff(lambda: upload_to_google_photos(post, photo, gphotos_album_id, 0, previous_image_id), max_retries=10)
                except:
                    print(f"{i + 1}/{len(posts_and_photos)} of {album_name}: FAILED")
                    failure = True
                    break

                gphotos_link = g_photo.get('productUrl')
                image_id = g_photo.get('id')

                print(f"{i + 1}/{len(posts_and_photos)} of {album_name}: {gphotos_link}")
                uploaded_photo_ids[fb_image_id] = image_id


    fb.driver.quit()
    print("Done!")

if __name__ == '__main__':
    main()