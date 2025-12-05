import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def test_drive_connection():
    """Test Google Drive API connection"""

    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'config/google_oauth_credentials.json',
        scopes=SCOPES
    )

    # This will open browser for authentication
    credentials = flow.run_local_server(port=8501)

    # Build Drive service
    service = build('drive', 'v3', credentials=credentials)

    # Test: List first 10 files
    print("Testing Google Drive API connection...")
    results = service.files().list(
        pageSize=10,
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get('files', [])

    if not files:
        print('No files found in your Google Drive.')
    else:
        print('✅ Successfully connected to Google Drive!')
        print('\nFirst 10 files:')
        for file in files:
            print(f"  - {file['name']} ({file['mimeType']})")

    print("\n🎉 Google Drive API setup verified successfully!")

if __name__ == '__main__':
    test_drive_connection()