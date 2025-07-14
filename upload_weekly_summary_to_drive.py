from __future__ import print_function
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete token.json
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_folder_id(service, folder_name, parent_id=None):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_to_drive():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # Ensure folder path exists
    root_folder_id = get_folder_id(service, "AI_Consensus_Reports")
    sub_folder_id = get_folder_id(service, "Weekly_Summaries", root_folder_id)

    # Upload PDF
    file_path = "weekly_log_summary.pdf"
    if not os.path.exists(file_path):
        print("❌ PDF not found.")
        return

    file_metadata = {
        'name': f'weekly_log_summary_{file_path[-14:-4]}.pdf',
        'parents': [sub_folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/pdf')
    uploaded = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ Uploaded to Google Drive (ID: {uploaded.get('id')})")

if __name__ == '__main__':
    upload_to_drive()