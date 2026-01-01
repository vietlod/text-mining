"""
Google Drive Manager for cloud file operations.

This module handles:
- OAuth2 authentication with Google Drive
- File and folder listing
- File download from Drive
- File upload to Drive
"""

import os
import io
import logging
from typing import List, Dict, Optional, Any, Generator
import json

logger = logging.getLogger(__name__)


class GoogleDriveManager:
    """
    Manages Google Drive API operations.

    Handles OAuth2 flow, file operations, and credential management.
    """

    # OAuth2 scopes for Drive access
    # Using drive scope for full access (read and list files)
    SCOPES = [
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Drive Manager.

        Args:
            credentials_path: Path to OAuth2 credentials JSON file.
                            If None, uses default path.
        """
        self.credentials_path = credentials_path or self._get_default_credentials_path()
        self.flow = None
        self._validate_credentials_file()

    def _get_default_credentials_path(self) -> str:
        """Get default path for OAuth2 credentials."""
        return os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'config',
            'google_oauth_credentials.json'
        )

    def _validate_credentials_file(self) -> bool:
        """
        Validate that credentials file exists and is properly formatted.

        Returns:
            bool: True if valid, raises exception otherwise.
        """
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Google OAuth credentials not found at: {self.credentials_path}\n\n"
                f"Please:\n"
                f"1. Go to https://console.cloud.google.com/\n"
                f"2. Create OAuth2 credentials\n"
                f"3. Download as JSON\n"
                f"4. Save to {self.credentials_path}\n\n"
                f"See SETUP_GOOGLE_CLOUD.md for detailed instructions."
            )

        try:
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)

            # Validate structure
            if 'web' in creds_data:
                required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
                web_data = creds_data['web']

                missing_fields = [f for f in required_fields if f not in web_data]
                if missing_fields:
                    raise ValueError(f"Missing fields in credentials: {missing_fields}")

                logger.info("Google OAuth credentials validated successfully")
                return True
            else:
                raise ValueError("Invalid credentials format. Expected 'web' key.")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in credentials file: {e}")

    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> tuple[str, str]:
        """
        Get OAuth2 authorization URL for user to visit.

        Args:
            redirect_uri: Redirect URI after authorization.
            state: Optional state parameter for CSRF protection.

        Returns:
            Tuple of (authorization_url, state).
        """
        try:
            from google_auth_oauthlib.flow import Flow

            logger.info(f"[GoogleDriveManager] get_authorization_url called")
            logger.info(f"  Redirect URI parameter: {redirect_uri}")
            logger.info(f"  State: {state[:20] if state else 'None'}...")

            # CRITICAL: Ensure redirect_uri is normalized (no trailing slash, exact match)
            redirect_uri = redirect_uri.rstrip('/')
            
            # Create flow
            self.flow = Flow.from_client_secrets_file(
                self.credentials_path,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )

            logger.info(f"  Flow created with redirect_uri: {self.flow.redirect_uri}")
            logger.info(f"  Redirect URI match: {self.flow.redirect_uri == redirect_uri}")

            # Generate authorization URL
            auth_url, flow_state = self.flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',
                state=state
            )

            logger.info(f"  Generated authorization URL")
            logger.info(f"  redirect_uri in URL: {redirect_uri}")
            return auth_url, flow_state

        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {e}")
            raise

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token using manual HTTP request.
        This bypasses the Flow library to have full control over the request.

        Args:
            code: Authorization code from OAuth callback.
            redirect_uri: Redirect URI used in authorization.

        Returns:
            Dictionary containing credentials data.
        """
        try:
            import requests
            import json

            logger.info(f"[GoogleDriveManager] exchange_code_for_token called (MANUAL MODE)")
            
            # CRITICAL: Normalize redirect_uri to match authorization URL
            redirect_uri = redirect_uri.rstrip('/')
            
            logger.info(f"  Redirect URI: {redirect_uri}")
            logger.info(f"  Code length: {len(code)}")
            logger.info(f"  Code (first 30 chars): {code[:30]}...")
            logger.info(f"  Code (last 10 chars): ...{code[-10:]}")

            # Load client credentials
            with open(self.credentials_path, 'r') as f:
                creds = json.load(f)

            client_id = creds['web']['client_id']
            client_secret = creds['web']['client_secret']

            logger.info(f"  Client ID: {client_id[:30]}...")

            # Prepare token exchange request
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }

            logger.info(f"  Token URL: {token_url}")
            logger.info(f"  Request data keys: {list(token_data.keys())}")
            logger.info(f"  Sending POST request...")

            # Make the request
            response = requests.post(token_url, data=token_data)

            logger.info(f"  Response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"  Response body: {response.text}")
                raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")

            # Parse response
            token_response = response.json()
            logger.info(f"  Response keys: {list(token_response.keys())}")

            # Extract credentials
            access_token = token_response.get('access_token')
            refresh_token = token_response.get('refresh_token')
            expires_in = token_response.get('expires_in')
            token_type = token_response.get('token_type')

            if not access_token:
                raise Exception("No access_token in response")

            logger.info(f"  ✅ Got access token!")
            logger.info(f"  ✅ Got refresh token: {bool(refresh_token)}")

            # Calculate expiry
            from datetime import datetime, timedelta
            expiry = None
            if expires_in:
                expiry = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

            # Create credentials dictionary
            creds_dict = {
                'token': access_token,
                'refresh_token': refresh_token,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'client_id': client_id,
                'client_secret': client_secret,
                'scopes': self.SCOPES,
                'expiry': expiry
            }

            logger.info("✅ Successfully exchanged code for Google Drive token (MANUAL MODE)")
            return creds_dict

        except Exception as e:
            logger.error(f"❌ Failed to exchange code for token: {e}", exc_info=True)
            raise

    def get_drive_service(self, credentials_dict: Dict[str, Any]):
        """
        Create Google Drive service from stored credentials.

        Args:
            credentials_dict: Credentials dictionary from storage.

        Returns:
            Google Drive service instance.
        """
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            # Recreate credentials
            credentials = Credentials(
                token=credentials_dict.get('token'),
                refresh_token=credentials_dict.get('refresh_token'),
                token_uri=credentials_dict.get('token_uri'),
                client_id=credentials_dict.get('client_id'),
                client_secret=credentials_dict.get('client_secret'),
                scopes=credentials_dict.get('scopes')
            )

            # Build service
            service = build('drive', 'v3', credentials=credentials)

            logger.info("Google Drive service created successfully")
            return service

        except Exception as e:
            logger.error(f"Failed to create Drive service: {e}")
            raise

    def list_folders(self, service, parent_id: str = 'root') -> List[Dict[str, str]]:
        """
        List folders in Google Drive.

        Args:
            service: Google Drive service instance.
            parent_id: Parent folder ID. Default is 'root'.

        Returns:
            List of folder dictionaries with 'id' and 'name'.
        """
        try:
            # Query for folders only
            query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"

            results = service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, modifiedTime)"
            ).execute()

            folders = results.get('files', [])

            logger.info(f"Found {len(folders)} folders in Drive")
            return folders

        except Exception as e:
            logger.error(f"Failed to list folders: {e}")
            raise

    def list_files_in_folder(self, service, folder_id: str,
                            file_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List files in a specific folder.

        Args:
            service: Google Drive service instance.
            folder_id: Folder ID to list files from.
            file_types: Optional list of file extensions to filter (e.g., ['pdf', 'docx']).

        Returns:
            List of file dictionaries with metadata.
        """
        try:
            if file_types is None:
                file_types = ['pdf', 'docx', 'txt', 'html', 'htm']

            # Build query
            query = f"'{folder_id}' in parents and trashed=false"

            # Add MIME type filters
            mime_type_map = {
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'txt': 'text/plain',
                'html': 'text/html',
                'htm': 'text/html'
            }

            if file_types:
                mime_conditions = []
                for ft in file_types:
                    if ft in mime_type_map:
                        mime_conditions.append(f"mimeType='{mime_type_map[ft]}'")

                if mime_conditions:
                    query += " and (" + " or ".join(mime_conditions) + ")"

            # Execute query
            results = service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, size, modifiedTime)"
            ).execute()

            files = results.get('files', [])
            
            # Ensure size is int (Google Drive API sometimes returns string)
            for file_info in files:
                if 'size' in file_info and file_info['size']:
                    try:
                        file_info['size'] = int(file_info['size'])
                    except (ValueError, TypeError):
                        file_info['size'] = 0

            logger.info(f"Found {len(files)} files in folder {folder_id}")
            return files

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise

    def download_file(self, service, file_id: str, destination_path: str) -> Generator[int, None, None]:
        """
        Download file from Google Drive with progress tracking.

        Args:
            service: Google Drive service instance.
            file_id: File ID to download.
            destination_path: Local path to save file.

        Yields:
            Progress percentage (0-100).
        """
        try:
            from googleapiclient.http import MediaIoBaseDownload

            # Get file metadata
            file_metadata = service.files().get(fileId=file_id, fields='name,size').execute()
            file_name = file_metadata.get('name', 'unknown')
            file_size = int(file_metadata.get('size', 0))

            logger.info(f"Downloading {file_name} ({file_size} bytes) from Drive")

            # Request file content
            request = service.files().get_media(fileId=file_id)

            # Create file handle
            fh = io.FileIO(destination_path, 'wb')

            # Create downloader
            downloader = MediaIoBaseDownload(fh, request)

            # Download with progress
            done = False
            while not done:
                status, done = downloader.next_chunk()

                if status:
                    progress = int(status.progress() * 100)
                    yield progress

            fh.close()
            logger.info(f"Successfully downloaded {file_name} to {destination_path}")

            # Yield 100% at the end
            yield 100

        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise

    def upload_file(self, service, file_path: str, folder_id: str,
                   file_name: Optional[str] = None) -> Dict[str, str]:
        """
        Upload file to Google Drive.

        Args:
            service: Google Drive service instance.
            file_path: Local file path to upload.
            folder_id: Destination folder ID in Drive.
            file_name: Optional custom file name. If None, uses original name.

        Returns:
            Dictionary with uploaded file metadata (id, name, webViewLink).
        """
        try:
            from googleapiclient.http import MediaFileUpload

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            if file_name is None:
                file_name = os.path.basename(file_path)

            # Prepare file metadata
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            # Detect MIME type
            mime_type = self._detect_mime_type(file_path)

            # Create media upload
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            # Upload file
            logger.info(f"Uploading {file_name} to Drive folder {folder_id}")

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()

            logger.info(f"Successfully uploaded {file_name} to Drive")

            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'webViewLink': file.get('webViewLink')
            }

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def _detect_mime_type(self, file_path: str) -> str:
        """
        Detect MIME type from file extension.

        Args:
            file_path: File path.

        Returns:
            MIME type string.
        """
        import mimetypes

        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type:
            return mime_type
        else:
            # Default to octet-stream
            return 'application/octet-stream'

    def test_connection(self, credentials_dict: Dict[str, Any]) -> bool:
        """
        Test Drive connection with stored credentials.

        Args:
            credentials_dict: Credentials dictionary.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            service = self.get_drive_service(credentials_dict)

            # Try to list files (lightweight check)
            results = service.files().list(pageSize=1, fields='files(id)').execute()

            logger.info("Google Drive connection test successful")
            return True

        except Exception as e:
            logger.error(f"Google Drive connection test failed: {e}")
            return False
