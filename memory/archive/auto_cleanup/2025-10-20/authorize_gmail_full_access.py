from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# Full Gmail read/write scope
SCOPES = ['https://mail.google.com/']

def main():
    creds = None
    token_path = 'token.pickle'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("\n🔐 Starting Gmail OAuth authorization (cloud-safe mode)...")
            print("Copy the link below, open it in your local browser, log in, approve access, and paste the code back here.\n")

            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"👉 Authorization URL:\n{auth_url}\n")

            code = input("🔑 Enter the authorization code here: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

        print("\n✅ Gmail authorization complete. Full access token saved as token.pickle")
    else:
        print("✅ Gmail already authorized. Token is still valid.")

if __name__ == '__main__':
    main()
