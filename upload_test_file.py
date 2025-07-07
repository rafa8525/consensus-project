from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = "1HZx8wR05YixBl3s8sYD8IL7QEvsgKnNK"
TEST_FILE_PATH = "ai_test_upload.txt"

# Write a test file to upload
with open(TEST_FILE_PATH, "w") as f:
    f.write("Hello Rafael, file upload successful!")

# Authenticate and build service
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build("drive", "v3", credentials=creds)

# Upload
file_metadata = {"name": "ai_test_upload.txt", "parents": [FOLDER_ID]}
media = MediaFileUpload(TEST_FILE_PATH, mimetype="text/plain")
uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id, name").execute()
print(f"✅ Uploaded: {uploaded_file['name']} (ID: {uploaded_file['id']})")
