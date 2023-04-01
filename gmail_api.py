from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def credentials_token(url):
    """
        Reusable constants   
    """
    return Credentials.from_authorized_user_file(
        "token.json", url)


def process_getter(url, user_id, max_results, query):
    """
        This functions returns the actual behaviour towards the data
    """
    cerds = credentials_token(url)
    service = build('gmail', 'v1', credentials=cerds)
    results = service.users().messages().list(
        userId=user_id, maxResults=max_results, q="in:" + query).execute()
    messages = results.get('messages', [])
    return messages


def build_service(cerds):
    """ Building an api service to fetch the gmail data. """
    return build('gmail', 'v1', credentials=cerds)


class GmailAPI:
    def __init__(self, creds=None, url=None):
        """
            If you are modifying this scope you've to delete the generated token file.

            Here the URL will remain constant
        """
        url = ["https://www.googleapis.com/auth/gmail.readonly"]
        self.URL = url
        """
            Listing the user's Gmail Label.
        """
        # creds by Default is None
        """
        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.
        """
        if os.path.exists("token.json"):
            creds = credentials_token(self.URL)
            """ 
               .-----------------------------------------------------------------------.
               | creds = Credentials.from_authorized_user_file("token.json", self.URL) |
               '-----------------------------------------------------------------------'
               This code can be merged with the function kowns as the credentials_token
               for reusability.
            """
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
        cerds = credentials_token(self.URL)
        try:
            service = build_service(cerds)
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
        self.max_results = max_results
        self.query = query
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
            cerds = credentials_token(self.URL)
            service = build('gmail', 'v1', credentials=cerds)
            results = service.users().messages().list(
                userId=self.user_id, maxResults=self.max_results, q="in:" + self.query).execute()
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
                print("----------------------------")
                print(f"{sender}\n{subject}\n{date}")
            print()

        except HttpError as error:
            print(f"Cannot fetch the data. Due to {error}!")

    def data_getter(self):
        """  Returns the value for the headers """
        service = build_service(cerds=credentials_token(self.URL))
        messages = process_getter(self.URL, self.user_id, self.max_results, self.query)
        csv_data = list()
        for message in messages:
            new_data = service.users().messages().get(
                userId=self.user_id, id=message['id']
            ).execute()
            payload = new_data['payload']
            headers = payload['headers']
            csv_data.append(headers)
        return csv_data
