from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from urllib.parse import urlparse, unquote
from io import BytesIO
import os
import requests

class GooglePhotosClient:
    def __init__(self, service, credentials):
        self.service = service
        self.credentials = credentials

    @classmethod
    def authenticate(cls, credentials_file, token_file):
        scopes = ['https://www.googleapis.com/auth/photoslibrary']

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        else:
            creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
                creds = flow.run_local_server(port=0)

            with open(token_file, "w") as token:
                token.write(creds.to_json())

        service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)

        return cls(service, creds)

    def list_albums(self):
        try:
            response = self.service.albums().list(pageSize=50).execute()  # Adjust pageSize as needed
            albums = response.get('albums', [])
            nextPageToken = response.get('nextPageToken')

            while nextPageToken:
                response = self.service.albums().list(pageSize=50, pageToken=nextPageToken).execute()
                albums.extend(response.get('albums', []))
                nextPageToken = response.get('nextPageToken')

            return albums

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def create_album(self, title):
        try:
            body = {
                'album': {
                    'title': title
                }
            }

            album = self.service.albums().create(body=body).execute()

            return album

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def list_photos_in_album(self, album_id):
        try:
            response = self.service.mediaItems().search(body={'albumId': album_id, 'pageSize': 100}).execute()
            media_items = response.get('mediaItems', [])
            nextPageToken = response.get('nextPageToken')

            while nextPageToken:
                response = self.service.mediaItems().search(body={'albumId': album_id, 'pageSize': 100, 'pageToken': nextPageToken}).execute()
                media_items.extend(response.get('mediaItems', []))
                nextPageToken = response.get('nextPageToken')

            return media_items

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def upload_photo(self, file_obj, album_id=None, filename=None, description="", previous_image_id=None):
        if not hasattr(file_obj, 'read') and not filename:
            filename = os.path.basename(file_obj)

        upload_token = self.__upload_photo(file_obj, filename)

        if not upload_token:
            return None

        body = {
            "albumId": album_id,

            "newMediaItems": [
                {
                    "description": description,
                    "simpleMediaItem": {
                        "fileName": filename,
                        "uploadToken": upload_token
                    }
                }
            ],

            "albumPosition": {
                "position": "after-media-item",
                "relativeMediaItemId": previous_image_id
            }

        }

        if not album_id:
            body.pop(album_id)

        if not previous_image_id:
            body.pop('albumPosition')

        try:
            response = self.service.mediaItems().batchCreate(body=body).execute()
            return response

        except Exception as e:
            print(f"Failed to upload photo: {e}")
            return None

    def __upload_photo(self, file_obj, filename=None): # This is just for getting the upload token
        if hasattr(file_obj, 'read'):
            file = file_obj

        else:
            file = open(file_obj, 'rb')

            if not filename:
                filename = os.path.basename(file_obj)

        try:
            headers = {
                "Content-type": "application/octet-stream",
                "X-Goog-Upload-File-Name": filename,
                "X-Goog-Upload-Protocol": "raw",
                'Authorization': f'Bearer {self.credentials.token}'
            }

            response = requests.post(
                'https://photoslibrary.googleapis.com/v1/uploads',
                headers=headers,
                data=file
            )

            if not hasattr(file_obj, 'read'):
                file.close()

            return response.content.decode('utf-8')

        except Exception as e:
            print(f"Failed to upload photo: {e}")

            if not hasattr(file_obj, 'read'):
                file.close()

            return None

    def upload_photo_from_url(self, photo_url, album_id=None, filename=None, description="", previous_image_id=None):
        if not filename:
            parsed_url = urlparse(photo_url)
            filename = unquote(parsed_url.path.split('/')[-1])

        content = requests.get(photo_url).content
        file = BytesIO(content)

        return self.upload_photo(file, album_id=album_id, filename=filename, description=description, previous_image_id=None)

    def get_photo_by_id(self, photo_id):
        try:
            response = self.service.mediaItems().get(mediaItemId=photo_id).execute()
            return response

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

