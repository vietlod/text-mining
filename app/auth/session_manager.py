"""
Session Manager for Streamlit authentication state.

This module handles:
- User session initialization
- Session state management
- Authentication status tracking
"""

import logging
from typing import Dict, Optional, Any
import streamlit as st

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages user session state in Streamlit.

    Handles authentication state, user data, and session lifecycle.
    """

    # Session state keys
    KEY_AUTHENTICATED = 'authenticated'
    KEY_USER = 'user'
    KEY_ID_TOKEN = 'id_token'
    KEY_FIREBASE_INITIALIZED = 'firebase_initialized'
    # KEY_LANGUAGE removed - language feature removed
    KEY_THEME = 'theme'

    @staticmethod
    def initialize_session() -> None:
        """
        Initialize session state variables.

        Should be called at the start of the Streamlit app.
        Sets default values for all session variables if not already set.
        """
        # Authentication state
        if SessionManager.KEY_AUTHENTICATED not in st.session_state:
            st.session_state[SessionManager.KEY_AUTHENTICATED] = False

        if SessionManager.KEY_USER not in st.session_state:
            st.session_state[SessionManager.KEY_USER] = None

        if SessionManager.KEY_ID_TOKEN not in st.session_state:
            st.session_state[SessionManager.KEY_ID_TOKEN] = None

        if SessionManager.KEY_FIREBASE_INITIALIZED not in st.session_state:
            st.session_state[SessionManager.KEY_FIREBASE_INITIALIZED] = False

        # Language feature removed - using Vietnamese text directly

        if SessionManager.KEY_THEME not in st.session_state:
            st.session_state[SessionManager.KEY_THEME] = 'system'  # Default theme

        logger.debug("Session state initialized")

    @staticmethod
    def set_user(user_data: Dict[str, Any], id_token: Optional[str] = None) -> None:
        """
        Set authenticated user in session.

        Args:
            user_data: Dictionary containing user information.
                      Required keys: 'uid', 'email'
                      Optional keys: 'name', 'picture', 'email_verified'
            id_token: Firebase ID token (optional).
        """
        st.session_state[SessionManager.KEY_USER] = user_data
        st.session_state[SessionManager.KEY_AUTHENTICATED] = True

        if id_token:
            st.session_state[SessionManager.KEY_ID_TOKEN] = id_token

        logger.info(f"User session set: {user_data.get('email', 'unknown')}")

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user.

        Returns:
            Dict containing user information if authenticated, None otherwise.
        """
        return st.session_state.get(SessionManager.KEY_USER)

    @staticmethod
    def get_user_id() -> Optional[str]:
        """
        Get current user ID.

        Returns:
            User ID (UID) if authenticated, None otherwise.
        """
        user = SessionManager.get_current_user()
        return user.get('uid') if user else None

    @staticmethod
    def get_user_email() -> Optional[str]:
        """
        Get current user email.

        Returns:
            User email if authenticated, None otherwise.
        """
        user = SessionManager.get_current_user()
        return user.get('email') if user else None

    @staticmethod
    def get_id_token() -> Optional[str]:
        """
        Get Firebase ID token.

        Returns:
            Firebase ID token if available, None otherwise.
        """
        return st.session_state.get(SessionManager.KEY_ID_TOKEN)

    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if user is authenticated.

        Returns:
            bool: True if authenticated, False otherwise.
        """
        return st.session_state.get(SessionManager.KEY_AUTHENTICATED, False)

    @staticmethod
    def logout() -> None:
        """
        Clear user session and logout.

        Removes all user-related session data and resets authentication state.
        """
        user_email = SessionManager.get_user_email()

        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # Reinitialize session with default values
        SessionManager.initialize_session()

        logger.info(f"User logged out: {user_email}")

    # Language methods removed - language feature removed

    @staticmethod
    def set_theme(theme: str) -> None:
        """
        Set user theme preference.

        Args:
            theme: Theme name ('light', 'dark', or 'system').
        """
        if theme not in ['light', 'dark', 'system']:
            logger.warning(f"Invalid theme: {theme}. Using 'system'.")
            theme = 'system'

        st.session_state[SessionManager.KEY_THEME] = theme
        logger.debug(f"Theme set to: {theme}")

    @staticmethod
    def get_theme() -> str:
        """
        Get current theme preference.

        Returns:
            str: Theme name ('light', 'dark', or 'system').
        """
        return st.session_state.get(SessionManager.KEY_THEME, 'system')

    @staticmethod
    def set_firebase_initialized(initialized: bool) -> None:
        """
        Mark Firebase as initialized.

        Args:
            initialized: Firebase initialization status.
        """
        st.session_state[SessionManager.KEY_FIREBASE_INITIALIZED] = initialized

    @staticmethod
    def is_firebase_initialized() -> bool:
        """
        Check if Firebase is initialized.

        Returns:
            bool: True if initialized, False otherwise.
        """
        return st.session_state.get(SessionManager.KEY_FIREBASE_INITIALIZED, False)

    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """
        Get complete session information for debugging.

        Returns:
            Dict containing all session state data.
        """
        return {
            'authenticated': SessionManager.is_authenticated(),
            'user': SessionManager.get_current_user(),
            'theme': SessionManager.get_theme(),
            'firebase_initialized': SessionManager.is_firebase_initialized()
        }

    @staticmethod
    def require_auth(func):
        """
        Decorator to require authentication for a function.

        Usage:
            @SessionManager.require_auth
            def protected_function():
                # This code only runs if user is authenticated
                pass

        Args:
            func: Function to protect.

        Returns:
            Wrapped function that checks authentication.
        """
        def wrapper(*args, **kwargs):
            if not SessionManager.is_authenticated():
                st.warning("⚠️ Please sign in to access this feature.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper


# Convenience function for quick authentication check
def require_authentication():
    """
    Quick authentication check that stops execution if not authenticated.

    Usage:
        def my_page():
            require_authentication()
            # Rest of the code only runs if authenticated
    """
    if not SessionManager.is_authenticated():
        st.warning("⚠️ Please sign in to access this page.")
        st.stop()
