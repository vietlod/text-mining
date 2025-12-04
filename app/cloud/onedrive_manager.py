"""
OneDrive Manager for Microsoft Graph API operations.

This module handles:
- OAuth2 authentication with Microsoft
- File and folder listing via Graph API
- File download from OneDrive
- File upload to OneDrive
"""

import os
import logging
from typing import List, Dict, Optional, Any, Generator
import json
import requests

logger = logging.getLogger(__name__)


class OneDriveManager:
    """
    Manages OneDrive API operations via Microsoft Graph.

    Handles OAuth2 flow, file operations, and credential management.
    """

    # Microsoft Graph API scopes
    SCOPES = [
        'https://graph.microsoft.com/Files.Read.All',
        'https://graph.microsoft.com/Files.ReadWrite.All',
        'https://graph.microsoft.com/User.Read'
    ]

    # Graph API base URL
    GRAPH_API_URL = 'https://graph.microsoft.com/v1.0'

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize OneDrive Manager.

        Args:
            config_path: Path to Azure config JSON file.
                        If None, uses default path.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = None
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default path for Azure config."""
        return os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'config',
            'azure_config.json'
        )

    def _load_config(self) -> None:
        """
        Load and validate Azure configuration.

        Raises:
            FileNotFoundError: If config file not found.
            ValueError: If config is invalid.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Azure config not found at: {self.config_path}\n\n"
                f"Please:\n"
                f"1. Go to https://portal.azure.com/\n"
                f"2. Register an app in Azure AD\n"
                f"3. Create client secret\n"
                f"4. Save config to {self.config_path}\n\n"
                f"See SETUP_AZURE.md for detailed instructions."
            )

        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

            # Validate required fields
            required_fields = ['client_id', 'client_secret', 'tenant_id']
            missing_fields = [f for f in required_fields if f not in self.config]

            if missing_fields:
                raise ValueError(f"Missing fields in Azure config: {missing_fields}")

            logger.info("Azure config loaded successfully")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Azure config: {e}")

    def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Get OAuth2 authorization URL for user to visit.

        Args:
            redirect_uri: Redirect URI after authorization.

        Returns:
            Authorization URL string.
        """
        try:
            from msal import ConfidentialClientApplication

            tenant_id = self.config.get('tenant_id', 'common')
            authority = f"https://login.microsoftonline.com/{tenant_id}"

            # Create MSAL app
            app = ConfidentialClientApplication(
                client_id=self.config['client_id'],
                client_credential=self.config['client_secret'],
                authority=authority
            )

            # Get authorization URL
            auth_url = app.get_authorization_request_url(
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )

            logger.info("Generated OneDrive authorization URL")
            return auth_url

        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {e}")
            raise

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback.
            redirect_uri: Redirect URI used in authorization.

        Returns:
            Dictionary containing token data.
        """
        try:
            from msal import ConfidentialClientApplication

            tenant_id = self.config.get('tenant_id', 'common')
            authority = f"https://login.microsoftonline.com/{tenant_id}"

            # Create MSAL app
            app = ConfidentialClientApplication(
                client_id=self.config['client_id'],
                client_credential=self.config['client_secret'],
                authority=authority
            )

            # Exchange code for token
            result = app.acquire_token_by_authorization_code(
                code=code,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )

            if 'access_token' in result:
                logger.info("Successfully exchanged code for OneDrive token")
                return result
            else:
                error_desc = result.get('error_description', 'Unknown error')
                raise Exception(f"Token exchange failed: {error_desc}")

        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh expired access token.

        Args:
            refresh_token: Refresh token from previous authentication.

        Returns:
            Dictionary containing new token data.
        """
        try:
            from msal import ConfidentialClientApplication

            tenant_id = self.config.get('tenant_id', 'common')
            authority = f"https://login.microsoftonline.com/{tenant_id}"

            # Create MSAL app
            app = ConfidentialClientApplication(
                client_id=self.config['client_id'],
                client_credential=self.config['client_secret'],
                authority=authority
            )

            # Refresh token
            result = app.acquire_token_by_refresh_token(
                refresh_token=refresh_token,
                scopes=self.SCOPES
            )

            if 'access_token' in result:
                logger.info("Successfully refreshed OneDrive token")
                return result
            else:
                error_desc = result.get('error_description', 'Unknown error')
                raise Exception(f"Token refresh failed: {error_desc}")

        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise

    def _get_headers(self, access_token: str) -> Dict[str, str]:
        """
        Get HTTP headers for Graph API requests.

        Args:
            access_token: OAuth2 access token.

        Returns:
            Headers dictionary.
        """
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get current user information.

        Args:
            access_token: OAuth2 access token.

        Returns:
            User information dictionary.
        """
        try:
            headers = self._get_headers(access_token)
            url = f'{self.GRAPH_API_URL}/me'

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            user_info = response.json()
            logger.info(f"Retrieved user info: {user_info.get('userPrincipalName')}")

            return user_info

        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise

    def list_folders(self, access_token: str, parent_id: str = 'root') -> List[Dict[str, Any]]:
        """
        List folders in OneDrive.

        Args:
            access_token: OAuth2 access token.
            parent_id: Parent folder ID. Default is 'root'.

        Returns:
            List of folder dictionaries.
        """
        try:
            headers = self._get_headers(access_token)

            if parent_id == 'root':
                url = f'{self.GRAPH_API_URL}/me/drive/root/children'
            else:
                url = f'{self.GRAPH_API_URL}/me/drive/items/{parent_id}/children'

            # Filter for folders only
            params = {'$filter': 'folder ne null'}

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            folders = response.json().get('value', [])

            logger.info(f"Found {len(folders)} folders in OneDrive")
            return folders

        except Exception as e:
            logger.error(f"Failed to list folders: {e}")
            raise

    def list_files_in_folder(self, access_token: str, folder_id: str,
                            file_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List files in a specific folder.

        Args:
            access_token: OAuth2 access token.
            folder_id: Folder ID to list files from.
            file_types: Optional list of file extensions to filter.

        Returns:
            List of file dictionaries.
        """
        try:
            headers = self._get_headers(access_token)

            if folder_id == 'root':
                url = f'{self.GRAPH_API_URL}/me/drive/root/children'
            else:
                url = f'{self.GRAPH_API_URL}/me/drive/items/{folder_id}/children'

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            all_items = response.json().get('value', [])

            # Filter files only (not folders)
            files = [item for item in all_items if 'file' in item]

            # Filter by file type if specified
            if file_types:
                supported_extensions = [f'.{ft}' for ft in file_types]
                files = [
                    f for f in files
                    if any(f['name'].lower().endswith(ext) for ext in supported_extensions)
                ]

            logger.info(f"Found {len(files)} files in OneDrive folder {folder_id}")
            return files

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise

    def download_file(self, access_token: str, file_id: str,
                     destination_path: str) -> Generator[int, None, None]:
        """
        Download file from OneDrive with progress tracking.

        Args:
            access_token: OAuth2 access token.
            file_id: File ID to download.
            destination_path: Local path to save file.

        Yields:
            Progress percentage (0-100).
        """
        try:
            headers = self._get_headers(access_token)

            # Get file metadata
            metadata_url = f'{self.GRAPH_API_URL}/me/drive/items/{file_id}'
            metadata_response = requests.get(metadata_url, headers=headers)
            metadata_response.raise_for_status()

            file_metadata = metadata_response.json()
            file_name = file_metadata.get('name', 'unknown')
            file_size = file_metadata.get('size', 0)

            logger.info(f"Downloading {file_name} ({file_size} bytes) from OneDrive")

            # Download file content
            download_url = f'{self.GRAPH_API_URL}/me/drive/items/{file_id}/content'

            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()

            # Write to file with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            yield progress

            logger.info(f"Successfully downloaded {file_name} to {destination_path}")

            # Yield 100% at the end
            yield 100

        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise

    def upload_file(self, access_token: str, file_path: str, folder_id: str,
                   file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload file to OneDrive.

        Args:
            access_token: OAuth2 access token.
            file_path: Local file path to upload.
            folder_id: Destination folder ID in OneDrive.
            file_name: Optional custom file name.

        Returns:
            Dictionary with uploaded file metadata.
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            if file_name is None:
                file_name = os.path.basename(file_path)

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }

            # Build upload URL
            if folder_id == 'root':
                url = f'{self.GRAPH_API_URL}/me/drive/root:/{file_name}:/content'
            else:
                url = f'{self.GRAPH_API_URL}/me/drive/items/{folder_id}:/{file_name}:/content'

            logger.info(f"Uploading {file_name} to OneDrive folder {folder_id}")

            # Upload file
            with open(file_path, 'rb') as f:
                response = requests.put(url, headers=headers, data=f)

            response.raise_for_status()

            file_metadata = response.json()

            logger.info(f"Successfully uploaded {file_name} to OneDrive")

            return {
                'id': file_metadata.get('id'),
                'name': file_metadata.get('name'),
                'webUrl': file_metadata.get('webUrl')
            }

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def test_connection(self, access_token: str) -> bool:
        """
        Test OneDrive connection with access token.

        Args:
            access_token: OAuth2 access token.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            # Try to get user info (lightweight check)
            self.get_user_info(access_token)

            logger.info("OneDrive connection test successful")
            return True

        except Exception as e:
            logger.error(f"OneDrive connection test failed: {e}")
            return False
