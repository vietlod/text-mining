"""
Settings Manager for user preferences and sensitive data.

This module handles:
- User settings storage in Firestore
- API key encryption/decryption
- Theme and language preferences
- Cloud storage credentials
"""

import os
import logging
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)


class SettingsManager:
    """
    Manages user settings and preferences with encryption support.

    Stores data in Firestore with encryption for sensitive values.
    """

    def __init__(self, firestore_client):
        """
        Initialize Settings Manager.

        Args:
            firestore_client: Firestore client instance.
        """
        self.db = firestore_client
        self._encryption_key = None
        self._cipher = None
        self._initialize_encryption()

    def _initialize_encryption(self) -> None:
        """
        Initialize encryption cipher.

        Loads encryption key from environment or generates a new one.
        """
        try:
            # Try to load encryption key from environment
            encryption_key = os.getenv('ENCRYPTION_KEY')

            if not encryption_key:
                # Try to load from .env file
                env_path = os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    '..',
                    'config',
                    '.env'
                )

                if os.path.exists(env_path):
                    from dotenv import load_dotenv
                    load_dotenv(env_path)
                    encryption_key = os.getenv('ENCRYPTION_KEY')

            if not encryption_key:
                # Generate a new key if none exists
                logger.warning("No encryption key found. Generating new key.")
                logger.warning("⚠️ IMPORTANT: Save this key to config/.env as ENCRYPTION_KEY")

                encryption_key = Fernet.generate_key().decode()
                logger.warning(f"Generated encryption key: {encryption_key}")

                # Try to save to .env file
                try:
                    env_path = os.path.join(
                        os.path.dirname(__file__),
                        '..',
                        '..',
                        'config',
                        '.env'
                    )

                    os.makedirs(os.path.dirname(env_path), exist_ok=True)

                    with open(env_path, 'a') as f:
                        f.write(f"\n# Generated encryption key\n")
                        f.write(f"ENCRYPTION_KEY={encryption_key}\n")

                    logger.info(f"Encryption key saved to {env_path}")
                except Exception as e:
                    logger.error(f"Could not save encryption key: {e}")

            # Initialize cipher
            self._encryption_key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
            self._cipher = Fernet(self._encryption_key)

            logger.info("Encryption initialized successfully")

        except Exception as e:
            logger.error(f"Encryption initialization failed: {e}")
            # Use a default key for development (NOT SECURE FOR PRODUCTION)
            logger.warning("⚠️ Using default encryption key. NOT SECURE FOR PRODUCTION!")
            default_key = Fernet.generate_key()
            self._encryption_key = default_key
            self._cipher = Fernet(default_key)

    def _encrypt(self, text: str) -> str:
        """
        Encrypt sensitive text.

        Args:
            text: Plain text to encrypt.

        Returns:
            Encrypted text as base64 string.
        """
        try:
            encrypted_bytes = self._cipher.encrypt(text.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def _decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt encrypted text.

        Args:
            encrypted_text: Encrypted text as base64 string.

        Returns:
            Decrypted plain text.
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode())
            decrypted_bytes = self._cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise

    # ==================== API Key Management ====================

    def save_api_key(self, user_id: str, api_key: str, key_name: str = 'gemini_api_key') -> bool:
        """
        Save encrypted API key to Firestore.

        Args:
            user_id: User ID.
            api_key: API key to encrypt and save.
            key_name: Name of the API key (e.g., 'gemini_api_key', 'openai_api_key').

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Encrypt API key
            encrypted_key = self._encrypt(api_key)

            # Save to Firestore
            from firebase_admin import firestore

            self.db.collection('settings').document(user_id).set({
                key_name: encrypted_key,
                f'{key_name}_updated_at': firestore.SERVER_TIMESTAMP
            }, merge=True)

            logger.info(f"API key '{key_name}' saved for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving API key: {e}")
            return False

    def get_api_key(self, user_id: str, key_name: str = 'gemini_api_key') -> Optional[str]:
        """
        Get and decrypt API key from Firestore.

        Args:
            user_id: User ID.
            key_name: Name of the API key.

        Returns:
            Decrypted API key if found, None otherwise.
        """
        try:
            doc = self.db.collection('settings').document(user_id).get()

            if doc.exists:
                data = doc.to_dict()
                encrypted_key = data.get(key_name)

                if encrypted_key:
                    # Decrypt and return
                    return self._decrypt(encrypted_key)
                else:
                    logger.debug(f"API key '{key_name}' not found for user: {user_id}")
                    return None
            else:
                logger.debug(f"Settings document not found for user: {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error getting API key: {e}")
            return None

    def delete_api_key(self, user_id: str, key_name: str = 'gemini_api_key') -> bool:
        """
        Delete API key from Firestore.

        Args:
            user_id: User ID.
            key_name: Name of the API key.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            from firebase_admin import firestore

            self.db.collection('settings').document(user_id).update({
                key_name: firestore.DELETE_FIELD,
                f'{key_name}_updated_at': firestore.DELETE_FIELD
            })

            logger.info(f"API key '{key_name}' deleted for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting API key: {e}")
            return False

    # ==================== Theme Preferences ====================

    def save_theme_preference(self, user_id: str, theme: str) -> bool:
        """
        Save user theme preference.

        Args:
            user_id: User ID.
            theme: Theme name ('light', 'dark', or 'system').

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if theme not in ['light', 'dark', 'system']:
                logger.warning(f"Invalid theme: {theme}. Using 'system'.")
                theme = 'system'

            from firebase_admin import firestore

            self.db.collection('settings').document(user_id).set({
                'theme': theme,
                'theme_updated_at': firestore.SERVER_TIMESTAMP
            }, merge=True)

            logger.debug(f"Theme preference saved: {theme} for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving theme preference: {e}")
            return False

    def get_theme_preference(self, user_id: str) -> str:
        """
        Get user theme preference.

        Args:
            user_id: User ID.

        Returns:
            Theme name ('light', 'dark', or 'system'). Default: 'system'.
        """
        try:
            doc = self.db.collection('settings').document(user_id).get()

            if doc.exists:
                data = doc.to_dict()
                theme = data.get('theme', 'system')
                return theme
            else:
                return 'system'

        except Exception as e:
            logger.error(f"Error getting theme preference: {e}")
            return 'system'

    # ==================== Language Preferences ====================

    def save_language_preference(self, user_id: str, language: str) -> bool:
        """
        Save user language preference.

        Args:
            user_id: User ID.
            language: Language code ('en' or 'vi').

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if language not in ['en', 'vi']:
                logger.warning(f"Invalid language: {language}. Using 'en'.")
                language = 'en'

            from firebase_admin import firestore

            self.db.collection('settings').document(user_id).set({
                'language': language,
                'language_updated_at': firestore.SERVER_TIMESTAMP
            }, merge=True)

            logger.debug(f"Language preference saved: {language} for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving language preference: {e}")
            return False

    def get_language_preference(self, user_id: str) -> str:
        """
        Get user language preference.

        Args:
            user_id: User ID.

        Returns:
            Language code ('en' or 'vi'). Default: 'en'.
        """
        try:
            doc = self.db.collection('settings').document(user_id).get()

            if doc.exists:
                data = doc.to_dict()
                language = data.get('language', 'en')
                return language
            else:
                return 'en'

        except Exception as e:
            logger.error(f"Error getting language preference: {e}")
            return 'en'

    # ==================== Cloud Storage Credentials ====================

    def save_cloud_credentials(self, user_id: str, provider: str,
                               credentials: Dict[str, Any]) -> bool:
        """
        Save cloud storage credentials (encrypted).

        Args:
            user_id: User ID.
            provider: Provider name ('google_drive' or 'onedrive').
            credentials: Credentials dictionary to encrypt and save.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            import json

            # Convert credentials to JSON and encrypt
            credentials_json = json.dumps(credentials)
            encrypted_credentials = self._encrypt(credentials_json)

            from firebase_admin import firestore

            self.db.collection('settings').document(user_id).set({
                f'{provider}_credentials': encrypted_credentials,
                f'{provider}_credentials_updated_at': firestore.SERVER_TIMESTAMP
            }, merge=True)

            # Log folder info if it's Google Drive
            if provider == 'google_drive':
                folder_id = credentials.get('folder_id', 'Not set')
                folder_name = credentials.get('folder_name', 'Not set')
                logger.info(f"{provider} credentials saved for user: {user_id}, folder_id={folder_id}, folder_name={folder_name}")
            else:
                logger.info(f"{provider} credentials saved for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving cloud credentials: {e}")
            return False

    def get_cloud_credentials(self, user_id: str, provider: str) -> Optional[Dict[str, Any]]:
        """
        Get and decrypt cloud storage credentials.

        Args:
            user_id: User ID.
            provider: Provider name ('google_drive' or 'onedrive').

        Returns:
            Credentials dictionary if found, None otherwise.
        """
        try:
            doc = self.db.collection('settings').document(user_id).get()

            if doc.exists:
                data = doc.to_dict()
                encrypted_credentials = data.get(f'{provider}_credentials')

                if encrypted_credentials:
                    import json

                    # Decrypt and parse JSON
                    credentials_json = self._decrypt(encrypted_credentials)
                    return json.loads(credentials_json)
                else:
                    return None
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting cloud credentials: {e}")
            return None

    def delete_cloud_credentials(self, user_id: str, provider: str) -> bool:
        """
        Delete cloud storage credentials.

        Args:
            user_id: User ID.
            provider: Provider name ('google_drive' or 'onedrive').

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            from firebase_admin import firestore

            self.db.collection('settings').document(user_id).update({
                f'{provider}_credentials': firestore.DELETE_FIELD,
                f'{provider}_credentials_updated_at': firestore.DELETE_FIELD
            })

            logger.info(f"{provider} credentials deleted for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting cloud credentials: {e}")
            return False

    # ==================== General Settings ====================

    def get_all_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get all user settings (excluding encrypted data).

        Args:
            user_id: User ID.

        Returns:
            Dictionary of all settings.
        """
        try:
            doc = self.db.collection('settings').document(user_id).get()

            if doc.exists:
                data = doc.to_dict()

                # Remove encrypted fields from response
                public_data = {}
                for key, value in data.items():
                    if not key.endswith('_credentials') and 'api_key' not in key:
                        public_data[key] = value

                # Add flags for which secrets are configured
                public_data['has_gemini_api_key'] = 'gemini_api_key' in data
                public_data['has_google_drive_credentials'] = 'google_drive_credentials' in data
                public_data['has_onedrive_credentials'] = 'onedrive_credentials' in data

                return public_data
            else:
                return {
                    'has_gemini_api_key': False,
                    'has_google_drive_credentials': False,
                    'has_onedrive_credentials': False
                }

        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return {}

    def delete_all_settings(self, user_id: str) -> bool:
        """
        Delete all user settings.

        Args:
            user_id: User ID.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.db.collection('settings').document(user_id).delete()
            logger.info(f"All settings deleted for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting all settings: {e}")
            return False

    # ==================== OAuth State Management ====================

    def save_oauth_state(self, user_id: str, state: str, oauth_type: str = 'drive') -> bool:
        """
        Save OAuth state to Firestore for persistence across redirects.

        Args:
            user_id: User ID.
            state: OAuth state parameter.
            oauth_type: Type of OAuth flow ('drive' or 'firebase').

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            from firebase_admin import firestore
            import time

            self.db.collection('oauth_states').document(f"{user_id}_{state}").set({
                'user_id': user_id,
                'state': state,
                'oauth_type': oauth_type,
                'created_at': firestore.SERVER_TIMESTAMP,
                'expires_at': time.time() + 600  # Expires in 10 minutes
            })

            logger.info(f"OAuth state saved for user: {user_id}, type: {oauth_type}")
            return True

        except Exception as e:
            logger.error(f"Error saving OAuth state: {e}")
            return False

    def get_oauth_state(self, user_id: str, state: str) -> Optional[Dict[str, Any]]:
        """
        Get OAuth state from Firestore.

        Args:
            user_id: User ID (can be empty string to search by state only).
            state: OAuth state parameter.

        Returns:
            Dictionary with state info if found, None otherwise.
        """
        try:
            import time

            # Try with user_id first (if provided)
            if user_id:
                doc = self.db.collection('oauth_states').document(f"{user_id}_{state}").get()
                if doc.exists:
                    data = doc.to_dict()
                    expires_at = data.get('expires_at', 0)

                    # Check if expired
                    if time.time() > expires_at:
                        logger.warning(f"OAuth state expired for user: {user_id}")
                        # Delete expired state
                        self.db.collection('oauth_states').document(f"{user_id}_{state}").delete()
                        return None

                    return data

            # If not found with user_id, search by state in all documents
            # This is useful when user_id is not known (e.g., before authentication)
            from firebase_admin import firestore
            states_ref = self.db.collection('oauth_states')
            # Use filter keyword argument to avoid warning
            query = states_ref.where(filter=firestore.FieldFilter('state', '==', state)).limit(1)
            docs = query.stream()

            for doc in docs:
                data = doc.to_dict()
                expires_at = data.get('expires_at', 0)

                # Check if expired
                if time.time() > expires_at:
                    logger.warning(f"OAuth state expired")
                    # Delete expired state
                    doc.reference.delete()
                    return None

                return data

            return None

        except Exception as e:
            logger.error(f"Error getting OAuth state: {e}")
            return None

    def delete_oauth_state(self, user_id: str, state: str) -> bool:
        """
        Delete OAuth state from Firestore.

        Args:
            user_id: User ID.
            state: OAuth state parameter.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.db.collection('oauth_states').document(f"{user_id}_{state}").delete()
            logger.debug(f"OAuth state deleted for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting OAuth state: {e}")
            return False
