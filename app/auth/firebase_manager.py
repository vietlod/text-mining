"""
Firebase Manager for authentication and database operations.

This module handles:
- Firebase Admin SDK initialization
- Authentication token verification
- User profile management with Firestore
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, auth, firestore

logger = logging.getLogger(__name__)


class FirebaseManager:
    """
    Manages Firebase Admin SDK operations.

    Provides authentication, user management, and Firestore database access.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern to ensure only one Firebase instance."""
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Firebase Manager (only once)."""
        if not FirebaseManager._initialized:
            self.app = None
            self.db = None
            FirebaseManager._initialized = True

    def initialize_app(self, credentials_path: Optional[str] = None) -> bool:
        """
        Initialize Firebase Admin SDK.

        Args:
            credentials_path: Path to Firebase credentials JSON file.
                            If None, uses environment variable or default path.

        Returns:
            bool: True if initialization successful, False otherwise.

        Raises:
            FileNotFoundError: If credentials file not found.
            ValueError: If credentials file is invalid.
        """
        try:
            # Check if already initialized
            if self.app is not None:
                logger.info("Firebase app already initialized")
                return True

            # Determine credentials path
            if credentials_path is None:
                # Try environment variable
                credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')

                # Try default path
                if credentials_path is None:
                    default_path = Path(__file__).parent.parent.parent / 'config' / 'firebase_config.json'
                    if default_path.exists():
                        credentials_path = str(default_path)

            # Check if credentials file exists
            if credentials_path is None or not os.path.exists(credentials_path):
                logger.error(f"Firebase credentials file not found: {credentials_path}")
                raise FileNotFoundError(
                    f"Firebase credentials not found. Please:\n"
                    f"1. Create Firebase project at https://console.firebase.google.com/\n"
                    f"2. Download service account credentials\n"
                    f"3. Save as config/firebase_config.json\n"
                    f"See SETUP_FIREBASE.md for detailed instructions."
                )

            # Load and validate credentials
            with open(credentials_path, 'r') as f:
                cred_data = json.load(f)

            # Validate required fields
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in cred_data]
            if missing_fields:
                raise ValueError(f"Invalid credentials file. Missing fields: {missing_fields}")

            # Initialize Firebase
            cred = credentials.Certificate(credentials_path)
            self.app = firebase_admin.initialize_app(cred)

            # Initialize Firestore client
            self.db = firestore.client()

            logger.info(f"Firebase initialized successfully for project: {cred_data['project_id']}")
            return True

        except firebase_admin.exceptions.FirebaseError as e:
            logger.error(f"Firebase initialization error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during Firebase initialization: {e}")
            return False

    def get_auth_instance(self):
        """
        Get Firebase Auth instance.

        Returns:
            Firebase Auth module.

        Raises:
            RuntimeError: If Firebase not initialized.
        """
        if self.app is None:
            raise RuntimeError("Firebase not initialized. Call initialize_app() first.")
        return auth

    def get_firestore_client(self):
        """
        Get Firestore database client.

        Returns:
            Firestore client instance.

        Raises:
            RuntimeError: If Firebase not initialized.
        """
        if self.db is None:
            raise RuntimeError("Firestore not initialized. Call initialize_app() first.")
        return self.db

    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token and return decoded token.

        Args:
            id_token: Firebase ID token from client.

        Returns:
            Dict containing user information if valid, None otherwise.
            Example: {'uid': '...', 'email': '...', 'name': '...'}

        Raises:
            RuntimeError: If Firebase not initialized.
        """
        try:
            if self.app is None:
                raise RuntimeError("Firebase not initialized")

            # Verify token
            decoded_token = auth.verify_id_token(id_token)

            # Extract user info
            user_info = {
                'uid': decoded_token.get('uid'),
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name', decoded_token.get('email', '').split('@')[0]),
                'picture': decoded_token.get('picture'),
                'email_verified': decoded_token.get('email_verified', False)
            }

            logger.info(f"Token verified for user: {user_info['email']}")
            return user_info

        except auth.InvalidIdTokenError:
            logger.warning("Invalid ID token")
            return None
        except auth.ExpiredIdTokenError:
            logger.warning("Expired ID token")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by UID from Firebase Auth.

        Args:
            uid: User ID.

        Returns:
            Dict containing user information if found, None otherwise.
        """
        try:
            user_record = auth.get_user(uid)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'photo_url': user_record.photo_url,
                'email_verified': user_record.email_verified,
                'disabled': user_record.disabled,
                'creation_timestamp': user_record.user_metadata.creation_timestamp,
                'last_sign_in_timestamp': user_record.user_metadata.last_sign_in_timestamp
            }
        except auth.UserNotFoundError:
            logger.warning(f"User not found: {uid}")
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def create_user_profile(self, uid: str, email: str, display_name: str,
                           additional_data: Optional[Dict] = None) -> bool:
        """
        Create or update user profile in Firestore.

        Args:
            uid: User ID.
            email: User email.
            display_name: User display name.
            additional_data: Additional user data to store.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if self.db is None:
                raise RuntimeError("Firestore not initialized")

            user_data = {
                'uid': uid,
                'email': email,
                'display_name': display_name,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }

            # Add additional data if provided
            if additional_data:
                user_data.update(additional_data)

            # Create or update user document
            self.db.collection('users').document(uid).set(user_data, merge=True)

            logger.info(f"User profile created/updated: {email}")
            return True

        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            return False

    def get_user_profile(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from Firestore.

        Args:
            uid: User ID.

        Returns:
            Dict containing user profile data if found, None otherwise.
        """
        try:
            if self.db is None:
                raise RuntimeError("Firestore not initialized")

            doc = self.db.collection('users').document(uid).get()

            if doc.exists:
                return doc.to_dict()
            else:
                logger.warning(f"User profile not found: {uid}")
                return None

        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

    def update_user_profile(self, uid: str, data: Dict[str, Any]) -> bool:
        """
        Update user profile in Firestore.

        Args:
            uid: User ID.
            data: Data to update.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if self.db is None:
                raise RuntimeError("Firestore not initialized")

            # Add updated timestamp
            data['updated_at'] = firestore.SERVER_TIMESTAMP

            # Update document
            self.db.collection('users').document(uid).set(data, merge=True)

            logger.info(f"User profile updated: {uid}")
            return True

        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False

    def delete_user_profile(self, uid: str) -> bool:
        """
        Delete user profile from Firestore.

        Args:
            uid: User ID.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if self.db is None:
                raise RuntimeError("Firestore not initialized")

            # Delete user document
            self.db.collection('users').document(uid).delete()

            logger.info(f"User profile deleted: {uid}")
            return True

        except Exception as e:
            logger.error(f"Error deleting user profile: {e}")
            return False

    def is_initialized(self) -> bool:
        """Check if Firebase is initialized."""
        return self.app is not None and self.db is not None


# Global instance
firebase_manager = FirebaseManager()
