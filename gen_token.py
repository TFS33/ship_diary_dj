import os
import json
import django
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_diary_dj.settings')
django.setup()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
REDIRECT_PORT = 8060


def main():
    creds = None
    if os.path.exists(settings.GOOGLE_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(settings.GOOGLE_TOKEN_FILE, SCOPES)
        except ValueError as e:
            print(f"Error reading token file: {e}")
            print("Token file contents:")
            with open(settings.GOOGLE_TOKEN_FILE, 'r') as file:
                print(file.read())
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None

        if not creds:
            credentials_path = settings.GOOGLE_TOKEN_ROOT / 'creds.json'
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"creds.json not found at {credentials_path}")

            print(f"Using credentials file: {credentials_path}")
            with open(credentials_path, 'r') as f:
                creds_data = json.load(f)
                print("Credentials file contains these keys:", list(creds_data.keys()))
                if 'installed' in creds_data:
                    print("'installed' key contains these keys:", list(creds_data['installed'].keys()))

            try:
                flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
                creds = flow.run_local_server(port=REDIRECT_PORT)
            except Exception as e:
                print(f"Error during authentication flow: {e}")
                raise

        # Save the credentials for the next run
        with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    print("Token has been generated and saved.")
    return creds


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"GOOGLE_TOKEN_ROOT: {settings.GOOGLE_TOKEN_ROOT}")
        print(f"GOOGLE_TOKEN_FILE: {settings.GOOGLE_TOKEN_FILE}")
