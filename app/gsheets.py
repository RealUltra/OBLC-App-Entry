from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
import os
import webbrowser
import io
import openpyxl
from . import *
from .messagebox import *

def get_authenticated_service():
    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    creds = None

    # Check if token file exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file)

    # If credentials don't exist or are invalid, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            messagebox.showinfo('Log In', 'You must log into your gmail account to allow access to the database project excel file!')

            while True:
                try:
                    creds = flow.run_local_server(port=0, authorization_prompt_message="", timeout_seconds=300)
                except:
                    creds = None

                if not creds:
                    resp = messagebox.askyesno("Haven't logged in", "You haven't logged into your gmail account. Are you still trying to log in?")

                    if resp:
                        webbrowser.open(flow.redirect_uri)
                    else:
                        return

                else:
                    break

        # Save the credentials for next time
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds, static_discovery=False)

    return service

def get_workbook(spread_id=None):
    if spread_id is None:
        spread_id = DATABASE_PROJECT_EXCEL_FILE_ID

    request = service.files().export_media(fileId=spread_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # Download the content
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    wb = openpyxl.load_workbook(io.BytesIO(fh.getvalue()))

    return wb

service = get_authenticated_service()

if not service:
    sys.exit(0)

DATABASE_PROJECT_EXCEL_FILE_ID = "14u_6G5lts6GGTJUsx2w9l72HG3zSlxzAhDarV1jvQW8"
