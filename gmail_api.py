from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailAPI:
    def __init__(self, url=["https://www.googleapis.com/auth/gmail.readonly"]):
        """
            If you are modifying this scope you've to delete the generated token file.

            Here the URL will remain constant
        """
        self.URL = url
        """
            Listing the user's Gmail Label.
        """
        creds = None
        """
        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.
        """
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json", self.URL)
            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                """
                    If our Token has Expired then we are requesting to refresh that token.
                """
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.URL)
                creds = flow.run_local_server(port=0)
                """
                    Now saving the file called credentials for the next run.
                """
            with open("token.json", "w") as token_file:
                token_file.write(creds.to_json())

    def display_api_result(self, user_id="me"):
        self.user_id = user_id
        cerds = Credentials.from_authorized_user_file('token.json', self.URL)
        try:
            service = build('gmail', 'v1', credentials=cerds)
            results = service.users().labels().list(userId=self.user_id).execute()
            labels = results.get('labels', [])
            if not labels:
                print("Labels not found.")
                return
            print("Labels: ")
            for label in labels:
                print(label['name'])
        except HttpError as error:
            print(f"An error occurred: {error}.")

    def set_labels(self, query, max_results=5):
        """
            Set Labels to fetch the messages.
            [
                "inbox",
                "drafts",
                "spam",
                "sent"
            ]
            There are more labels but few examples are given here
        """
        try:
            cerds = Credentials.from_authorized_user_file(
                "token.json", self.URL)
            service = build('gmail', 'v1', credentials=cerds)
            results = service.users().messages().list(
                userId='me', maxResults=max_results, q="in:"+query).execute()
            messages = results.get('messages', [])
            for message in messages:
                load_data = service.users().messages().get(
                    userId='me', id=message['id']).execute()
                payload = load_data['payload']
                headers = payload['headers']
                for header in headers:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    if header['name'] == 'From':
                        sender = header['value']
                    if header['name'] == 'Date':
                        date = header['value']
                # return headers
                print("----------------------------")    
                print(f"{sender}\n{subject}\n{date}")
        except HttpError as error:
            print(f"Cannot fetch the data. Due to {error}!")
    
    def generate_csv(self, filename):
        pass
