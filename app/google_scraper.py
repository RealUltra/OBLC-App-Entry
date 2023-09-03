import os
import re
import time
import requests
import langcodes

from pprint import pprint

API_KEY = "AIzaSyCGltDhSdvr0xeUflkwmNeeukwJjNnwlUI"
BASE_URL = 'https://www.googleapis.com/books/v1/volumes'

def search_books(query):
    params = {'q': query, 'key': API_KEY}
    response = requests.get(BASE_URL, params=params)
    return response.json()

def get_sub_genres(volume_id):
    details_response = requests.get(f'{BASE_URL}/{volume_id}', params={'key': API_KEY})
    details_data = details_response.json()
    subjects = details_data.get('volumeInfo', {}).get('categories', [])
    return subjects

def get_book_info(isbn=None, name=None):
    if not isbn and not name:
        return

    query = ''

    if isbn is not None:
        query = f'isbn:{isbn}'

    if name is not None:
        query = name

    while True:
        data = search_books(query)

        if data.get('error'):
            if data['error']['code'] == 429:
                print("Delaying")
                time.sleep(60)
        else:
            break

    if not data['totalItems']:
        return

    item = data['items'][0]
    volume = item['volumeInfo']

    title = volume.get('title')
    subtitle = volume.get('subtitle', '')
    isbns = list(map(lambda x: x['identifier'], volume.get('industryIdentifiers', [])))
    authors = volume.get('authors', [])
    description = volume.get('description', '')
    publisher = volume.get('publisher', 'Unknown')
    published_date = volume.get('publishedDate', '0000')
    sub_genres = get_sub_genres(item['id'])
    language = volume.get('language')
    page_count = volume.get('pageCount', 'Unknown')

    r = re.search('\d{4}', published_date)
    published_year = int(r[0])

    sub_genres = split_by(", ".join(sub_genres), ['/', '--', ',', '&'])
    sub_genres = list(map(lambda x: x.strip().title(), sub_genres))
    sub_genres = list(set(sub_genres))
    sub_genres = list(filter(lambda x: x.strip(), sub_genres))
    if 'Etc' in sub_genres:
        sub_genres.remove('Etc')


    language = get_language_name(language)

    return {
        "title": title,
        "subtitle": subtitle,
        "isbns": isbns,
        "authors": authors,
        "description": description,
        "publisher": publisher,
        "published_year": published_year,
        "sub_genres": sub_genres,
        "language": language,
        "page_count": page_count
    }

def split_by(text, splitters):
    split = [text]

    for splitter in splitters:
        temp_split = []

        for text in split:
            temp_split.extend(text.split(splitter))

        split = temp_split[:]

    return split

def get_language_name(language_code):
    try:
        language_name = langcodes.Language.make(language_code).language_name()
        return language_name
    except langcodes.codes.UnknownLanguageError:
        return "Unknown Language"

if __name__ == '__main__':
    book_info = get_book_info(9781851687206)
    #pprint(book_info)